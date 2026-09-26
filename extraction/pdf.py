"""Node 1 — Split (§6.1). Python, deterministic: a PDF into page texts.

Table fidelity is whatever pdfplumber's plain text extraction gives —
SPEC.md §11 leaves the extraction library and its limits to judgment.
No LLM call here; there is nothing to check afterwards (every page is
read by construction, once this returns).

`page_texts` (from `split_pdf`) still backs page-count, Validate's
citation checks, and Verify's search tools — but Map and Extract's own
LLM calls send `extract_pdf_pages`' native PDF slices as their main
content instead of this flattened text (found live: a real book's
two-column-per-page layout made pdfplumber's plain extraction
genuinely lossy on a rate table — a real number went missing from a
row, not just harder to read — confirmed by comparing against this
project's own hand-verified gold config, and confirmed fixed by
sending the actual PDF page instead).
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pdfplumber
from pypdf import PdfReader, PdfWriter


def split_pdf(path: str | Path) -> dict[int, str]:
    """1-indexed page number -> extracted text. A blank page yields an
    empty string, not a missing key — Map still receives every page."""
    page_texts: dict[int, str] = {}
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            page_texts[i] = page.extract_text() or ""
    return page_texts


def extract_pdf_pages(path: str | Path, pages: list[int]) -> bytes:
    """A new, standalone PDF's bytes containing exactly the given
    1-indexed pages, in the order given — not necessarily contiguous
    (a charge's context can span a main section plus a referenced one
    pages apart). Used to attach real PDF pages to a Map/Extract call
    instead of their flattened text."""
    reader = PdfReader(str(path))
    writer = PdfWriter()
    for page_number in pages:
        writer.add_page(reader.pages[page_number - 1])
    buf = BytesIO()
    writer.write(buf)
    return buf.getvalue()
