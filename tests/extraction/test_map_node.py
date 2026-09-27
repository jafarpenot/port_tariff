from extraction.map_node import DEFAULT_WINDOW_OVERLAP, DEFAULT_WINDOW_SIZE, map_document, window_ranges
from extraction.schemas import SectionType, WindowMapResult, WindowSection

from .conftest import StubChatModel, make_blank_pdf, text_of


def test_window_ranges_defaults_cover_a_27_page_document_in_seven_windows():
    # Real page count of Port Tariff.pdf, verified once against the actual
    # file when writing this — locked in here so a pdfplumber/library
    # change that silently altered page count would be caught.
    ranges = window_ranges(27, DEFAULT_WINDOW_SIZE, DEFAULT_WINDOW_OVERLAP)
    assert ranges == [(1, 5), (5, 9), (9, 13), (13, 17), (17, 21), (21, 25), (25, 27)]


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
        return WindowMapResult(window_start_page=999, window_end_page=999, sections=[])

    llm = StubChatModel(respond)
    results = map_document({1: "a", 2: "b", 3: "c"}, llm, pdf_path=make_blank_pdf(), window_size=3, overlap=1)
    assert len(results) == 1
    assert (results[0].window_start_page, results[0].window_end_page) == (1, 3)


def test_map_document_clamps_an_out_of_range_page_citation_to_the_nearer_bound():
    """Found live: a model can cite the book's own printed page number
    (visible on the page image) instead of the attachment-position page
    it was told to use. A citation outside the window's own known range
    is provably wrong -- clamped to whichever of the window's start/end
    it's closer to (not spanning the whole window: confirmed live that a
    wider context measurably hurt a different charge's per-port table
    transcription)."""

    def respond(schema, messages):
        return WindowMapResult(
            window_start_page=999,
            window_end_page=999,
            sections=[
                WindowSection(section_number="3.6", heading="Towage", section_type=SectionType.CHARGE, page=15),  # closer to end (9)
                WindowSection(section_number="3.7", heading="Misc tug", section_type=SectionType.CHARGE, page=1),  # closer to start (5)
                WindowSection(section_number="1.1", heading="Light dues", section_type=SectionType.CHARGE, page=6),  # in range
            ],
        )

    llm = StubChatModel(respond)
    results = map_document({p: f"page {p}" for p in range(1, 10)}, llm, pdf_path=make_blank_pdf(), window_size=5, overlap=1)
    window = next(r for r in results if r.window_start_page == 5 and r.window_end_page == 9)

    by_section = {s.section_number: s.page for s in window.sections}
    assert by_section["3.6"] == 9  # clamped to the nearer bound, not left at the wrong page 15
    assert by_section["3.7"] == 5  # clamped to the nearer bound (start, not end)
    assert by_section["1.1"] == 6  # untouched -- already inside [5, 9]


def test_map_document_routes_each_window_to_its_own_canned_response():
    def respond(schema, messages):
        user_text = text_of(messages[-1].content)
        if "Pages 1-3" in user_text:
            return WindowMapResult(
                window_start_page=1,
                window_end_page=3,
                sections=[WindowSection(section_number="1.1", heading="A", section_type=SectionType.CHARGE, page=1)],
            )
        return WindowMapResult(
            window_start_page=3,
            window_end_page=5,
            sections=[WindowSection(section_number="2.1", heading="B", section_type=SectionType.CHARGE, page=4)],
        )

    llm = StubChatModel(respond)
    results = map_document({p: f"page {p}" for p in range(1, 6)}, llm, pdf_path=make_blank_pdf(), window_size=3, overlap=1, concurrency_limit=2)
    headings = sorted(s.heading for r in results for s in r.sections)
    assert headings == ["A", "B"]
