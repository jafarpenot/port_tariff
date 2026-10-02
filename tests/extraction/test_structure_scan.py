from extraction.schemas import ScanConfidence, ScanContentType, ScannedSection, StructureScanResult
from extraction.structure_scan import notes_with_glossary, scan_structure

from .conftest import StubChatModel, make_blank_pdf


def test_notes_with_glossary_appends_when_present():
    result = StructureScanResult(notes="A straightforward layout.", glossary="laytime: time allowed for loading/discharging.")
    combined = notes_with_glossary(result)
    assert combined.startswith("A straightforward layout.")
    assert "laytime: time allowed for loading/discharging." in combined


def test_notes_with_glossary_is_a_no_op_when_empty():
    result = StructureScanResult(notes="A straightforward layout.")
    assert notes_with_glossary(result) == "A straightforward layout."


def test_scan_structure_attaches_the_whole_document_for_its_first_pass():
    seen = {}

    def respond(schema, messages):
        if "content" not in seen:
            seen["content"] = messages[-1].content
        return StructureScanResult(notes="A straightforward single-column layout, no anomalies found.")

    llm = StubChatModel(respond)
    result = scan_structure(make_blank_pdf(), llm)

    assert isinstance(result, StructureScanResult)
    assert result.notes == "A straightforward single-column layout, no anomalies found."
    content = seen["content"]
    assert isinstance(content, list)  # the whole PDF was attached, not flattened text
    file_block = next(b for b in content if b["type"] == "file")
    assert file_block["filename"] == "document.pdf"


def test_scan_structure_with_no_tool_calls_returns_low_confidence_result():
    """The stub's default tool_respond never calls a tool — scan_structure
    must still return cleanly (no crash on an empty exploration round),
    and nothing it never actually checked should claim high confidence."""

    def respond(schema, messages):
        return StructureScanResult(
            notes="ok",
            sections=[
                ScannedSection(
                    heading="Marine Tariff",
                    start_page=1,
                    end_page=5,
                    content_type=ScanContentType.BASE_RATE,
                    confidence=ScanConfidence.LOW,
                    description="Taken from the table of contents, never actually read.",
                )
            ],
        )

    llm = StubChatModel(respond)
    result = scan_structure(make_blank_pdf(), llm)

    assert result.sections[0].confidence is ScanConfidence.LOW


def test_scan_structure_uses_a_bounded_tool_loop_to_check_pages():
    """A tool call (read_pages) is actually issued and its result makes
    it into the final call's context — the exploration round isn't a
    no-op wrapper around the same single call as before."""
    calls = {"tool_rounds": 0}

    def tool_respond(tools, messages):
        calls["tool_rounds"] += 1
        if calls["tool_rounds"] == 1:
            read_pages = next(t for t in tools if t.name == "read_pages")
            return _FakeAIMessage([{"name": "read_pages", "args": {"start_page": 1, "end_page": 1}, "id": "call_1"}])
        return _NoToolCalls()

    seen_final_transcript = {}

    def respond(schema, messages):
        content = messages[-1].content
        if isinstance(content, str) and "read_pages" in content:
            seen_final_transcript["saw_tool_result"] = True
        return StructureScanResult(notes="ok")

    llm = StubChatModel(respond, tool_respond)
    result = scan_structure(make_blank_pdf(), llm)

    assert calls["tool_rounds"] >= 1
    assert seen_final_transcript.get("saw_tool_result") is True
    assert isinstance(result, StructureScanResult)


class _NoToolCalls:
    tool_calls: list = []


class _FakeAIMessage:
    def __init__(self, tool_calls):
        self.tool_calls = tool_calls
        self.content = ""
