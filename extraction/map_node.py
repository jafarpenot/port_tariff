"""Node 3 — Map (§6.1). LLM, parallel, one call per page window.

Default window: 5 pages, overlapping by 1 — specs/EXTRACTION_SPEC.md §6.1
(the reasoning for windowing over a single whole-document pass is there,
not repeated here). Window size and overlap stay configurable so the
future-work window-size evaluation (§8/§9) can run at other sizes
without a code change (§11).

Each window is sent as a real PDF page range, not flattened text —
found live: a book with a genuine two-column-per-page layout made
pdfplumber's plain text extraction lossy on at least one rate table (a
value silently dropped, not just harder to read), confirmed against
this project's own hand-verified gold config and confirmed fixed by
sending the actual pages instead.
"""

from __future__ import annotations

import base64
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from .llm import structured_call
from .pdf import extract_pdf_pages
from .prompts import MAP_SYSTEM_PROMPT, map_user_prompt
from .schemas import WindowMapResult

DEFAULT_WINDOW_SIZE = 5
DEFAULT_WINDOW_OVERLAP = 1
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


def _window_content(pdf_path: str, start: int, end: int) -> list:
    pdf_bytes = extract_pdf_pages(pdf_path, list(range(start, end + 1)))
    b64 = base64.b64encode(pdf_bytes).decode()
    return [
        {"type": "text", "text": map_user_prompt(start, end)},
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
) -> list[WindowMapResult]:
    n_pages = max(page_texts) if page_texts else 0
    ranges = window_ranges(n_pages, window_size, overlap)

    def _call(page_range: tuple[int, int]) -> WindowMapResult:
        start, end = page_range
        content = _window_content(pdf_path, start, end)
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
