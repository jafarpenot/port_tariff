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

from .conftest import make_charge_notes


def _window(start, end, sections, charge_notes=None):
    return WindowMapResult(window_start_page=start, window_end_page=end, sections=sections, charge_notes=charge_notes or make_charge_notes())


def test_overlapping_windows_deduplicate_and_union_charge_tags():
    # Same section (1.2) seen in two overlapping windows, tagged with a
    # different (but real) charge in each — union, not last-write-wins.
    window_a = _window(
        1,
        2,
        [
            WindowSection(section_number="1.1", heading="General conditions", section_type=SectionType.GENERAL_TERMS),
            WindowSection(
                section_number="1.2",
                heading="Light dues",
                section_type=SectionType.CHARGE,
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
                affects_charges=[CanonicalCharge.LIGHT_DUES, CanonicalCharge.PORT_DUES],
                references=["1.3"],
            ),
            WindowSection(section_number="1.3", heading="Surcharge clause", section_type=SectionType.CHARGE),
        ],
    )
    sections = merge_sections([window_a, window_b])
    by_number = {s.section_number: s for s in sections}

    assert len(by_number) == 3  # 1.1, 1.2, 1.3 — deduplicated, not 4 sightings
    assert set(by_number["1.2"].affects_charges) == {CanonicalCharge.LIGHT_DUES, CanonicalCharge.PORT_DUES}
    assert (by_number["1.2"].window_start_page, by_number["1.2"].window_end_page) == (1, 3)  # union of both sightings' windows


def test_charge_context_includes_chapter_general_terms_and_references():
    window = _window(
        1,
        3,
        [
            WindowSection(section_number="1.1", heading="General conditions", section_type=SectionType.GENERAL_TERMS),
            WindowSection(
                section_number="1.2",
                heading="Light dues",
                section_type=SectionType.CHARGE,
                affects_charges=[CanonicalCharge.LIGHT_DUES],
                references=["§1.3"],
            ),
            WindowSection(section_number="1.3", heading="Surcharge clause", section_type=SectionType.CHARGE),
        ],
    )
    sections = merge_sections([window])
    contexts = build_charge_contexts(sections, [window])
    light_dues_context = contexts[CanonicalCharge.LIGHT_DUES]

    assert "1.2" in light_dues_context.section_numbers
    assert "1.1" in light_dues_context.section_numbers  # implicit: same chapter's general terms
    assert "1.3" in light_dues_context.section_numbers  # explicit reference resolved
    assert light_dues_context.pages == [1, 2, 3]  # the whole window behind every relevant section


def test_charge_context_pages_covers_the_whole_relevant_window():
    """A section is only ever attributed the window(s) it was sighted
    in — never a per-section page (WindowSection has none) — so a
    window spanning 2-4 always contributes all of 2, 3, 4, not just
    whichever page a citation might have named."""
    window = _window(
        2,
        4,
        [WindowSection(section_number="2.1", heading="Towage", section_type=SectionType.CHARGE, affects_charges=[CanonicalCharge.TOWAGE])],
    )
    sections = merge_sections([window])
    contexts = build_charge_contexts(sections, [window])
    assert contexts[CanonicalCharge.TOWAGE].pages == [2, 3, 4]


def test_charge_notes_additively_extend_pages_and_concatenate_into_context_notes():
    """charge_notes is a second, independent signal from the section-tag
    mechanism — a window can flag a charge present even with no section
    explicitly tagged for it, and that must still pull the window's
    pages in and surface the note text to Extract."""
    window = _window(
        5,
        7,
        [],  # no sections at all tagged for towage
        charge_notes=make_charge_notes({CanonicalCharge.TOWAGE: "A surcharge table for towage, no base rate here."}),
    )
    sections = merge_sections([window])
    contexts = build_charge_contexts(sections, [window])
    towage_context = contexts[CanonicalCharge.TOWAGE]

    assert towage_context.pages == [5, 6, 7]
    assert "A surcharge table for towage, no base rate here." in towage_context.notes


def test_charge_never_mentioned_gets_an_empty_context_not_an_error():
    window = _window(
        1,
        2,
        [WindowSection(section_number="1.1", heading="General conditions", section_type=SectionType.GENERAL_TERMS)],
    )
    sections = merge_sections([window])
    contexts = build_charge_contexts(sections, [window])
    assert contexts[CanonicalCharge.TOWAGE].notes == ""
    assert contexts[CanonicalCharge.TOWAGE].section_numbers == []


def test_charge_section_matching_no_canonical_type_is_out_of_scope():
    window = _window(4, 4, [WindowSection(section_number="1.4", heading="Staff training courses", section_type=SectionType.CHARGE)])
    result = assemble([window], ProvisionalIdentity())
    assert [s.section_number for s in result.out_of_scope_sections] == ["1.4"]


def test_general_terms_found_flag():
    with_general_terms = assemble(
        [_window(1, 1, [WindowSection(section_number="1.1", heading="General", section_type=SectionType.GENERAL_TERMS)])],
        ProvisionalIdentity(),
    )
    assert with_general_terms.general_terms_found is True

    without_general_terms = assemble(
        [_window(4, 4, [WindowSection(section_number="1.4", heading="Training", section_type=SectionType.CHARGE)])],
        ProvisionalIdentity(),
    )
    assert without_general_terms.general_terms_found is False


def test_finalize_identity_prefers_provisional_and_fills_gaps_from_map():
    provisional = ProvisionalIdentity(authority="Acme Port Authority", currency=None)
    window = _window(1, 1, [])
    window.metadata_found = ProvisionalIdentity(authority="Should not override", currency="ZAR")
    result = assemble([window], provisional)
    assert result.identity.authority == "Acme Port Authority"  # provisional wins
    assert result.identity.currency == "ZAR"  # gap filled from Map
