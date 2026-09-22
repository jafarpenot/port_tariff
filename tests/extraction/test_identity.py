from extraction.identity import OPENING_PAGES_COUNT, provisional_identity
from extraction.schemas import ProvisionalIdentity

from .conftest import StubChatModel


def test_provisional_identity_only_sees_opening_pages():
    seen = {}

    def respond(schema, messages):
        seen["user_text"] = messages[-1].content
        return ProvisionalIdentity(authority="Acme Port Authority", currency="XYZ")

    llm = StubChatModel(respond)
    page_texts = {1: "cover page", 2: "more cover", 3: "still opening", 4: "definitely not opening", 20: "deep in the book"}
    result = provisional_identity(page_texts, llm)

    assert result.authority == "Acme Port Authority"
    assert "deep in the book" not in seen["user_text"]
    assert "definitely not opening" not in seen["user_text"]  # beyond OPENING_PAGES_COUNT
    assert OPENING_PAGES_COUNT == 3
    assert "cover page" in seen["user_text"]
