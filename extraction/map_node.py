"""Node 3 — Map (§6.1). LLM, parallel, one call per page window.

Default window: 4 pages, overlapping by 1 — narrower than the original
5 (specs/EXTRACTION_SPEC.md §6.1's reasoning for windowing at all is
there, not repeated here), because Extract now receives whole relevant
windows rather than individual cited pages (see below) — a smaller
window keeps that bound reasonable. Window size and overlap stay
configurable so the future-work window-size evaluation (§8/§9) can run
at other sizes without a code change (§11).

Each window is sent as a real PDF page range, not flattened text —
found live: a book with a genuine two-column-per-page layout made
pdfplumber's plain text extraction lossy on at least one rate table (a
value silently dropped, not just harder to read), confirmed against
this project's own hand-verified gold config and confirmed fixed by
sending the actual pages instead.

WindowSection no longer carries a page citation — found live,
repeatedly: a model's per-section page number is unreliable even
*within* its own window's valid range (two different sections in the
same window, off by different, non-uniform amounts, no out-of-range
value for a clamp to catch). Assemble now trusts only the window's own
verified bounds for a charge's page range, and Map's real per-charge
output is `charge_notes` — a paragraph per canonical charge on whether
and how it's discussed in this window — not a page number at all.
"""

from __future__ import annotations

import base64
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from .llm import structured_call
from .pdf import extract_pdf_pages
from .prompts import MAP_SYSTEM_PROMPT, map_user_prompt
from .schemas import ScanConfidence, StructureScanResult, WindowMapResult

DEFAULT_WINDOW_SIZE = 4
DEFAULT_WINDOW_OVERLAP = 1
MAX_SECTION_CALL_PAGES = 12  # a confirmed section larger than this falls back to sub-windowing
# within its own bounds (tier 2) instead of one native-PDF attachment -- keeps any single
# call's attachment size bounded, same reasoning DEFAULT_WINDOW_SIZE already follows.
DEFAULT_CONCURRENCY_LIMIT = 3  # see extraction/extract.py's DEFAULT_CONCURRENCY_LIMIT — same
# reasoning, only relevant when this module is called directly, not through the graph.


def window_ranges(n_pages: int, window_size: int = DEFAULT_WINDOW_SIZE, overlap: int = DEFAULT_WINDOW_OVERLAP) -> list[tuple[int, int]]:
    """1-indexed, inclusive (start, end) page ranges covering 1..n_pages.
    A window_size >= n_pages collapses to a single whole-document window
    — the baseline (specs/EXTRACTION_SPEC.md §8.2) is this same function
    with a large window_size, not a different code path."""
    if n_pages <= 0:
        return []
    if window_size <= overlap:
        raise ValueError("window_size must be greater than overlap.")
    stride = window_size - overlap
    ranges: list[tuple[int, int]] = []
    start = 1
    while start <= n_pages:
        end = min(start + window_size - 1, n_pages)
        ranges.append((start, end))
        if end >= n_pages:
            break
        start += stride
    return ranges


def _contiguous_runs(pages: list[int]) -> list[tuple[int, int]]:
    """Group a sorted, deduplicated list of page numbers into maximal
    contiguous (start, end) runs."""
    if not pages:
        return []
    runs: list[tuple[int, int]] = []
    start = prev = pages[0]
    for p in pages[1:]:
        if p == prev + 1:
            prev = p
            continue
        runs.append((start, prev))
        start = prev = p
    runs.append((start, prev))
    return runs


def _offset_window_ranges(start: int, end: int, window_size: int, overlap: int) -> list[tuple[int, int]]:
    """window_ranges() scoped to an arbitrary (start, end) range instead
    of always starting at page 1 — tier 2's sub-windowing within one
    oversized confirmed section, and tier 3's fallback windows over a
    gap the structure scan had no confidence about."""
    n = end - start + 1
    return [(s + start - 1, e + start - 1) for s, e in window_ranges(n, window_size, overlap)]


def build_ranges(
    n_pages: int,
    structure_scan: StructureScanResult | None = None,
    window_size: int = DEFAULT_WINDOW_SIZE,
    overlap: int = DEFAULT_WINDOW_OVERLAP,
) -> list[tuple[int, int]]:
    """The three-tier hierarchy (specs/EXTRACTION_SPEC.md §6.1's original
    design extended, not replaced): one call over a confirmed
    high-confidence section's own real bounds if it's small enough to
    attach whole (tier 1 — the new default unit of work, replacing an
    arbitrary fixed window with the document's own structure), the same
    section sub-windowed within its own bounds if too large for one call
    (tier 2), and today's original uniform fixed windows over anything a
    structure scan had no high confidence about at all — including
    having no structure_scan at all — (tier 3, unchanged, the
    non-negotiable fallback carrying over §6.1's "every page is read by
    construction" guarantee). `structure_scan=None` collapses this back
    to exactly today's single-tier behaviour."""
    sections = []
    if structure_scan is not None:
        sections = [s for s in structure_scan.sections if s.confidence == ScanConfidence.HIGH]

    ranges: list[tuple[int, int]] = []
    covered: set[int] = set()
    for s in sorted(sections, key=lambda s: s.start_page):
        start, end = max(1, s.start_page), min(n_pages, s.end_page)
        if start > end or all(p in covered for p in range(start, end + 1)):
            continue
        if end - start + 1 <= MAX_SECTION_CALL_PAGES:
            ranges.append((start, end))  # tier 1
        else:
            ranges.extend(_offset_window_ranges(start, end, window_size, overlap))  # tier 2
        covered.update(range(start, end + 1))

    gap_pages = sorted(p for p in range(1, n_pages + 1) if p not in covered)
    for gap_start, gap_end in _contiguous_runs(gap_pages):
        ranges.extend(_offset_window_ranges(gap_start, gap_end, window_size, overlap))  # tier 3

    return ranges


def _window_content(pdf_path: str, start: int, end: int, structure_notes: str = "") -> list:
    pdf_bytes = extract_pdf_pages(pdf_path, list(range(start, end + 1)))
    b64 = base64.b64encode(pdf_bytes).decode()
    return [
        {"type": "text", "text": map_user_prompt(start, end, structure_notes)},
        {"type": "file", "source_type": "base64", "mime_type": "application/pdf", "data": b64, "filename": f"pages-{start}-{end}.pdf"},
    ]


def map_document(
    page_texts: dict[int, str],
    llm: Any,
    *,
    pdf_path: str,
    window_size: int = DEFAULT_WINDOW_SIZE,
    overlap: int = DEFAULT_WINDOW_OVERLAP,
    concurrency_limit: int = DEFAULT_CONCURRENCY_LIMIT,
    structure_notes: str = "",
    structure_scan: StructureScanResult | None = None,
) -> list[WindowMapResult]:
    n_pages = max(page_texts) if page_texts else 0
    ranges = build_ranges(n_pages, structure_scan, window_size, overlap)

    def _call(page_range: tuple[int, int]) -> WindowMapResult:
        start, end = page_range
        content = _window_content(pdf_path, start, end, structure_notes)
        result = structured_call(llm, WindowMapResult, MAP_SYSTEM_PROMPT, content)
        # The model's own echo of the range it covered is not trusted for
        # anything downstream — overwrite with the real range so a
        # confused model can't misreport which pages it actually saw.
        result.window_start_page = start
        result.window_end_page = end
        return result

    if not ranges:
        return []
    with ThreadPoolExecutor(max_workers=max(1, concurrency_limit)) as pool:
        return list(pool.map(_call, ranges))
