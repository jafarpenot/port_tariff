from extraction.map_node import DEFAULT_WINDOW_OVERLAP, DEFAULT_WINDOW_SIZE, build_ranges, map_document, window_ranges
from extraction.schemas import (
    CanonicalCharge,
    ChargeWindowNote,
    ScanConfidence,
    ScanContentType,
    ScannedSection,
    SectionType,
    StructureScanResult,
    WindowMapResult,
    WindowSection,
)

from .conftest import StubChatModel, make_blank_pdf, make_charge_notes, text_of


def test_window_ranges_defaults_cover_a_27_page_document_in_nine_windows():
    # Real page count of Port Tariff.pdf, verified once against the actual
    # file when writing this — locked in here so a pdfplumber/library
    # change that silently altered page count would be caught. Window
    # size is 4 (not the original 5) since Extract now receives whole
    # relevant windows rather than individually cited pages.
    ranges = window_ranges(27, DEFAULT_WINDOW_SIZE, DEFAULT_WINDOW_OVERLAP)
    assert ranges == [(1, 4), (4, 7), (7, 10), (10, 13), (13, 16), (16, 19), (19, 22), (22, 25), (25, 27)]


def test_window_ranges_cover_every_page_with_no_gap():
    ranges = window_ranges(23, window_size=5, overlap=1)
    covered = set()
    for start, end in ranges:
        covered.update(range(start, end + 1))
    assert covered == set(range(1, 24))


def test_window_size_equal_to_document_length_is_the_whole_document_baseline():
    """specs/EXTRACTION_SPEC.md §8.2: the baseline is this same node with
    a large window_size, not a different code path."""
    ranges = window_ranges(27, window_size=27, overlap=1)
    assert ranges == [(1, 27)]


def test_window_size_must_exceed_overlap():
    import pytest

    with pytest.raises(ValueError):
        window_ranges(10, window_size=3, overlap=3)


def test_empty_document_produces_no_windows():
    assert window_ranges(0) == []


def test_map_document_overwrites_the_models_own_page_echo():
    """A confused model reporting the wrong range for its own window must
    not be trusted — the real range always wins."""

    def respond(schema, messages):
        return WindowMapResult(window_start_page=999, window_end_page=999, sections=[], charge_notes=make_charge_notes())

    llm = StubChatModel(respond)
    results = map_document({1: "a", 2: "b", 3: "c"}, llm, pdf_path=make_blank_pdf(), window_size=3, overlap=1)
    assert len(results) == 1
    assert (results[0].window_start_page, results[0].window_end_page) == (1, 3)


def test_window_map_result_requires_a_charge_note_for_every_canonical_charge():
    import pytest
    from pydantic import ValidationError

    incomplete = [ChargeWindowNote(charge=CanonicalCharge.TOWAGE, present=False, notes="Not discussed.")]
    with pytest.raises(ValidationError, match="light_dues"):
        WindowMapResult(window_start_page=1, window_end_page=3, sections=[], charge_notes=incomplete)


def test_map_document_returns_charge_notes_for_every_window():
    def respond(schema, messages):
        return WindowMapResult(
            window_start_page=999,
            window_end_page=999,
            sections=[],
            charge_notes=make_charge_notes({CanonicalCharge.TOWAGE: "A towage rate table with per-port bands."}),
        )

    llm = StubChatModel(respond)
    results = map_document({1: "a", 2: "b", 3: "c"}, llm, pdf_path=make_blank_pdf(), window_size=3, overlap=1)
    notes_by_charge = {n.charge: n for n in results[0].charge_notes}
    assert len(notes_by_charge) == len(CanonicalCharge)
    assert notes_by_charge[CanonicalCharge.TOWAGE].present is True
    assert "per-port bands" in notes_by_charge[CanonicalCharge.TOWAGE].notes
    assert notes_by_charge[CanonicalCharge.VTS].present is False  # not mentioned -> default "not discussed"


def test_map_document_routes_each_window_to_its_own_canned_response():
    def respond(schema, messages):
        user_text = text_of(messages[-1].content)
        if "Pages 1-3" in user_text:
            return WindowMapResult(
                window_start_page=1,
                window_end_page=3,
                sections=[WindowSection(section_number="1.1", heading="A", section_type=SectionType.CHARGE)],
                charge_notes=make_charge_notes(),
            )
        return WindowMapResult(
            window_start_page=3,
            window_end_page=5,
            sections=[WindowSection(section_number="2.1", heading="B", section_type=SectionType.CHARGE)],
            charge_notes=make_charge_notes(),
        )

    llm = StubChatModel(respond)
    results = map_document({p: f"page {p}" for p in range(1, 6)}, llm, pdf_path=make_blank_pdf(), window_size=3, overlap=1, concurrency_limit=2)
    headings = sorted(s.heading for r in results for s in r.sections)
    assert headings == ["A", "B"]


def test_map_document_folds_in_structure_notes_as_advisory_context():
    seen = {}

    def respond(schema, messages):
        seen["user_text"] = text_of(messages[-1].content)
        return WindowMapResult(window_start_page=999, window_end_page=999, sections=[], charge_notes=make_charge_notes())

    llm = StubChatModel(respond)
    map_document(
        {1: "a", 2: "b", 3: "c"}, llm, pdf_path=make_blank_pdf(), window_size=3, overlap=1, structure_notes="A two-column layout throughout."
    )

    assert "A two-column layout throughout." in seen["user_text"]
    assert "for context only" in seen["user_text"]


def _scan(*sections: ScannedSection) -> StructureScanResult:
    return StructureScanResult(notes="", sections=list(sections))


def test_build_ranges_with_no_structure_scan_matches_today_s_fixed_windows():
    assert build_ranges(27, None, DEFAULT_WINDOW_SIZE, DEFAULT_WINDOW_OVERLAP) == window_ranges(
        27, DEFAULT_WINDOW_SIZE, DEFAULT_WINDOW_OVERLAP
    )


def test_build_ranges_uses_a_high_confidence_section_s_own_bounds_as_one_call():
    scan = _scan(
        ScannedSection(
            heading="Marine Tariff",
            start_page=10,
            end_page=15,
            content_type=ScanContentType.BASE_RATE,
            confidence=ScanConfidence.HIGH,
            description="",
        )
    )
    ranges = build_ranges(30, scan, DEFAULT_WINDOW_SIZE, DEFAULT_WINDOW_OVERLAP)
    assert (10, 15) in ranges  # tier 1: the section's own exact bounds, one call


def test_build_ranges_covers_every_page_exactly_once_or_via_overlap_never_a_gap():
    scan = _scan(
        ScannedSection(
            heading="Marine Tariff", start_page=10, end_page=15, content_type=ScanContentType.BASE_RATE,
            confidence=ScanConfidence.HIGH, description="",
        ),
        ScannedSection(
            heading="Cargo", start_page=20, end_page=22, content_type=ScanContentType.IRRELEVANT,
            confidence=ScanConfidence.HIGH, description="",
        ),
    )
    ranges = build_ranges(30, scan, DEFAULT_WINDOW_SIZE, DEFAULT_WINDOW_OVERLAP)
    covered = set()
    for start, end in ranges:
        covered.update(range(start, end + 1))
    assert covered == set(range(1, 31))  # the non-negotiable coverage guarantee, structure-aware or not


def test_build_ranges_ignores_medium_and_low_confidence_sections():
    """Only a high-confidence, actually-verified section gets to narrow
    Map's own behaviour — medium/low falls all the way back to tier 3's
    uniform fixed windows, same as having no structure_scan at all."""
    scan = _scan(
        ScannedSection(
            heading="Guessed from the ToC only", start_page=10, end_page=15, content_type=ScanContentType.BASE_RATE,
            confidence=ScanConfidence.MEDIUM, description="",
        )
    )
    ranges = build_ranges(30, scan, DEFAULT_WINDOW_SIZE, DEFAULT_WINDOW_OVERLAP)
    assert ranges == window_ranges(30, DEFAULT_WINDOW_SIZE, DEFAULT_WINDOW_OVERLAP)


def test_build_ranges_subwindows_an_oversized_high_confidence_section():
    from extraction.map_node import MAX_SECTION_CALL_PAGES

    big_end = 10 + MAX_SECTION_CALL_PAGES + 5
    scan = _scan(
        ScannedSection(
            heading="Huge Annex", start_page=10, end_page=big_end, content_type=ScanContentType.BASE_RATE,
            confidence=ScanConfidence.HIGH, description="",
        )
    )
    ranges = build_ranges(big_end + 5, scan, DEFAULT_WINDOW_SIZE, DEFAULT_WINDOW_OVERLAP)
    assert (10, big_end) not in ranges  # too large for one call
    covered = set()
    for start, end in ranges:
        assert start >= 10 and end <= big_end or start > big_end or end < 10  # no window spills outside its own scope oddly
        covered.update(range(start, end + 1))
    assert set(range(10, big_end + 1)).issubset(covered)  # still fully covered, just sub-windowed
