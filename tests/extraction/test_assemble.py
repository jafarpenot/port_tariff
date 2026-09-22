"""Node 4 (Assemble) is pure Python — no LLM, no mocking needed. Tests
build synthetic WindowMapResult objects directly."""

from extraction.assemble import assemble, build_charge_contexts, merge_sections
from extraction.schemas import (
    CanonicalCharge,
    ProvisionalIdentity,
    SectionType,
    WindowMapResult,
    WindowSection,
)

PAGE_TEXTS = {
    1: "1.1 General conditions. Ordinary hours apply throughout.",
    2: "1.2 Light dues. Rate per 100 tons.",
    3: "1.3 Cross-referenced surcharge clause.",
    4: "1.4 Staff training courses (irrelevant to a vessel call).",
}


def _window(start, end, sections):
    return WindowMapResult(window_start_page=start, window_end_page=end, sections=sections)


def test_overlapping_windows_deduplicate_and_union_charge_tags():
    # Same section (1.2) seen in two overlapping windows, tagged with a
    # different (but real) charge in each — union, not last-write-wins.
    window_a = _window(
        1,
        2,
        [
            WindowSection(section_number="1.1", heading="General conditions", section_type=SectionType.GENERAL_TERMS, page=1),
            WindowSection(
                section_number="1.2",
                heading="Light dues",
                section_type=SectionType.CHARGE,
                page=2,
                affects_charges=[CanonicalCharge.LIGHT_DUES],
            ),
        ],
    )
    window_b = _window(
        2,
        3,
        [
            WindowSection(
                section_number="1.2",
                heading="Light dues",
                section_type=SectionType.CHARGE,
                page=2,
                affects_charges=[CanonicalCharge.LIGHT_DUES, CanonicalCharge.PORT_DUES],
                references=["1.3"],
            ),
            WindowSection(section_number="1.3", heading="Surcharge clause", section_type=SectionType.CHARGE, page=3),
        ],
    )
    sections = merge_sections([window_a, window_b], PAGE_TEXTS)
    by_number = {s.section_number: s for s in sections}

    assert len(by_number) == 3  # 1.1, 1.2, 1.3 — deduplicated, not 4 sightings
    assert set(by_number["1.2"].affects_charges) == {CanonicalCharge.LIGHT_DUES, CanonicalCharge.PORT_DUES}


def test_charge_context_includes_chapter_general_terms_and_references():
    window = _window(
        1,
        3,
        [
            WindowSection(section_number="1.1", heading="General conditions", section_type=SectionType.GENERAL_TERMS, page=1),
            WindowSection(
                section_number="1.2",
                heading="Light dues",
                section_type=SectionType.CHARGE,
                page=2,
                affects_charges=[CanonicalCharge.LIGHT_DUES],
                references=["§1.3"],
            ),
            WindowSection(section_number="1.3", heading="Surcharge clause", section_type=SectionType.CHARGE, page=3),
        ],
    )
    sections = merge_sections([window], PAGE_TEXTS)
    contexts = build_charge_contexts(sections)
    light_dues_context = contexts[CanonicalCharge.LIGHT_DUES]

    assert "1.2" in light_dues_context.section_numbers
    assert "1.1" in light_dues_context.section_numbers  # implicit: same chapter's general terms
    assert "1.3" in light_dues_context.section_numbers  # explicit reference resolved
    assert "General conditions" in light_dues_context.combined_text


def test_charge_never_mentioned_gets_an_empty_context_not_an_error():
    window = _window(
        1,
        2,
        [WindowSection(section_number="1.1", heading="General conditions", section_type=SectionType.GENERAL_TERMS, page=1)],
    )
    sections = merge_sections([window], PAGE_TEXTS)
    contexts = build_charge_contexts(sections)
    assert contexts[CanonicalCharge.TOWAGE].combined_text == ""
    assert contexts[CanonicalCharge.TOWAGE].section_numbers == []


def test_charge_section_matching_no_canonical_type_is_out_of_scope():
    window = _window(
        4,
        4,
        [WindowSection(section_number="1.4", heading="Staff training courses", section_type=SectionType.CHARGE, page=4)],
    )
    result = assemble([window], ProvisionalIdentity(), PAGE_TEXTS)
    assert [s.section_number for s in result.out_of_scope_sections] == ["1.4"]


def test_general_terms_found_flag():
    with_general_terms = assemble(
        [_window(1, 1, [WindowSection(section_number="1.1", heading="General", section_type=SectionType.GENERAL_TERMS, page=1)])],
        ProvisionalIdentity(),
        PAGE_TEXTS,
    )
    assert with_general_terms.general_terms_found is True

    without_general_terms = assemble(
        [_window(4, 4, [WindowSection(section_number="1.4", heading="Training", section_type=SectionType.CHARGE, page=4)])],
        ProvisionalIdentity(),
        PAGE_TEXTS,
    )
    assert without_general_terms.general_terms_found is False


def test_finalize_identity_prefers_provisional_and_fills_gaps_from_map():
    provisional = ProvisionalIdentity(authority="Acme Port Authority", currency=None)
    window = _window(
        1,
        1,
        [],
    )
    window.metadata_found = ProvisionalIdentity(authority="Should not override", currency="ZAR")
    result = assemble([window], provisional, PAGE_TEXTS)
    assert result.identity.authority == "Acme Port Authority"  # provisional wins
    assert result.identity.currency == "ZAR"  # gap filled from Map
