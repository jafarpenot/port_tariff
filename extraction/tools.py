"""Extract's tools (§6.3): keyword search and read-a-page-range over the
whole document's page texts. No embeddings, no vector store — leads are
usually explicit references, which exact matching finds reliably, and
provenance needs exact pages.
"""

from __future__ import annotations

from langchain_core.tools import tool


def make_tools(page_texts: dict[int, str]) -> list:
    @tool
    def search_document(query: str) -> str:
        """Search the whole document for a keyword or phrase — use this
        only to follow a lead (an explicit reference pointing outside
        your given context). Returns matching page numbers and short
        snippets, or "No matches found."."""
        needle = query.lower().strip()
        if not needle:
            return "No matches found."
        hits = []
        for page in sorted(page_texts):
            text = page_texts[page]
            idx = text.lower().find(needle)
            if idx != -1:
                start = max(0, idx - 60)
                end = min(len(text), idx + len(needle) + 60)
                hits.append(f"[page {page}] ...{text[start:end]}...")
        return "\n".join(hits) if hits else "No matches found."

    @tool
    def read_pages(start_page: int, end_page: int) -> str:
        """Read the full text of a page range (inclusive) — use this to
        read a section a lead pointed you to."""
        return "\n\n".join(f"[page {p}]\n{page_texts.get(p, '')}" for p in range(start_page, end_page + 1))

    return [search_document, read_pages]
