from extraction.schemas import StructureScanResult
from extraction.structure_scan import scan_structure

from .conftest import StubChatModel, make_blank_pdf, text_of


def test_scan_structure_attaches_the_whole_document_and_returns_free_text():
    seen = {}

    def respond(schema, messages):
        seen["content"] = messages[-1].content
        return StructureScanResult(notes="A straightforward single-column layout, no anomalies found.")

    llm = StubChatModel(respond)
    notes = scan_structure(make_blank_pdf(), llm)

    assert notes == "A straightforward single-column layout, no anomalies found."
    content = seen["content"]
    assert isinstance(content, list)  # the whole PDF was attached, not flattened text
    file_block = next(b for b in content if b["type"] == "file")
    assert file_block["filename"] == "document.pdf"
