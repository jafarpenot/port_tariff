"""Node 1 — Structure scan (new). LLM, once, before anything else runs.

The same first glance a person takes before searching a book for
anything specific — the whole document, attached natively (not
windowed, not flattened text), asked to describe its own organisation,
table of contents (if any), and any layout oddity a reader should know
about before trusting a single page or small range in isolation. Runs
before Split/Identity, since it makes no assumption about where a
book's metadata or structure actually lives — the opposite of
Identity's own hardcoded "read the first few pages" assumption.

Purely advisory: its output is folded into Identity's, Map's, and
Extract's prompts as background context, never as ground truth — a
description written before reading any specific page closely can be
wrong, and the actual attached pages always win if they disagree.
"""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

from .llm import structured_call
from .prompts import STRUCTURE_SCAN_SYSTEM_PROMPT
from .schemas import StructureScanResult


def scan_structure(pdf_path: str, llm: Any) -> str:
    pdf_bytes = Path(pdf_path).read_bytes()
    b64 = base64.b64encode(pdf_bytes).decode()
    content = [
        {"type": "text", "text": "The full port tariff book is attached as a PDF."},
        {"type": "file", "source_type": "base64", "mime_type": "application/pdf", "data": b64, "filename": "document.pdf"},
    ]
    result = structured_call(llm, StructureScanResult, STRUCTURE_SCAN_SYSTEM_PROMPT, content)
    return result.notes
