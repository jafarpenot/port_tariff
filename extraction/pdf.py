"""Node 1 — Split (§6.1). Python, deterministic: a PDF into page texts.

Table fidelity is whatever pdfplumber's plain text extraction gives —
SPEC.md §11 leaves the extraction library and its limits to judgment.
No LLM call here; there is nothing to check afterwards (every page is
read by construction, once this returns).
"""

from __future__ import annotations

from pathlib import Path

import pdfplumber


def split_pdf(path: str | Path) -> dict[int, str]:
    """1-indexed page number -> extracted text. A blank page yields an
    empty string, not a missing key — Map still receives every page."""
    page_texts: dict[int, str] = {}
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            page_texts[i] = page.extract_text() or ""
    return page_texts
