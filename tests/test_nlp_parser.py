"""v2: tests for tariffs.nlp.parse_vessel_request().

No real Anthropic API calls here — a stub LLM stands in for
`.with_structured_output(schema).invoke(messages)`, so these tests run
offline and don't need ANTHROPIC_API_KEY. One live smoke test at the
bottom is skipped unless that key is set.
"""

import os

import pytest
from pydantic import ValidationError

from tariffs.models import Port, VesselCall, VesselType
from tariffs.nlp import VesselCallExtraction, parse_vessel_request


class _StubStructuredLLM:
    def __init__(self, canned_output):
        self._canned_output = canned_output
        self.received_messages = None

    def invoke(self, messages):
        self.received_messages = messages
        return self._canned_output


class _StubChatModel:
    """Stands in for a LangChain chat model: `.with_structured_output(schema)`
    returns something with `.invoke(messages)` — exactly the surface
    parse_vessel_request() relies on, nothing more."""

    def __init__(self, canned_output):
        self._canned_output = canned_output
        self.structured = None

    def with_structured_output(self, schema):
        self.structured = _StubStructuredLLM(self._canned_output)
        return self.structured


def _extraction(**slots) -> VesselCallExtraction:
    """Build a VesselCallExtraction with only the given fields populated,
    each as {"value": ..., "evidence": "..."}."""
    return VesselCallExtraction(**slots)


# ---------------------------------------------------------------------------
# Schema shape
# ---------------------------------------------------------------------------


def test_extraction_schema_mirrors_every_vessel_call_field():
    assert set(VesselCallExtraction.model_fields.keys()) == set(VesselCall.model_fields.keys())


def test_extraction_schema_fields_are_all_optional_at_top_level():
    ext = VesselCallExtraction()  # no arguments at all — every slot must default to None
    for name in VesselCall.model_fields:
        assert getattr(ext, name) is None


# ---------------------------------------------------------------------------
# Happy path: populated fields flow through, with evidence
# ---------------------------------------------------------------------------


def test_populated_fields_become_a_valid_vessel_call():
    canned = _extraction(
        port={"value": "durban", "evidence": "at the Port of Durban"},
        gross_tonnage={"value": 51255.0, "evidence": "GT 51,255"},
        vessel_type={"value": "bulk_carrier", "evidence": "bulk carrier"},
    )
    result = parse_vessel_request("A bulk carrier, GT 51,255, calling at the Port of Durban.", llm=_StubChatModel(canned))

    assert result.vessel_call.port == Port.DURBAN
    assert result.vessel_call.gross_tonnage == 51255.0
    assert result.vessel_call.vessel_type == VesselType.BULK_CARRIER


def test_unpopulated_fields_stay_none_not_guessed():
    canned = _extraction(
        port={"value": "durban", "evidence": "Durban"},
        gross_tonnage={"value": 51255.0, "evidence": "51,255 GT"},
    )
    result = parse_vessel_request("Durban, 51,255 GT.", llm=_StubChatModel(canned))

    call = result.vessel_call
    assert call.vessel_name is None
    assert call.length_overall_m is None
    assert call.chargeable_period_days is None
    assert call.mooring_boat_used is None
    assert call.hull_certification == []  # VesselCall's own default, not a guessed value


def test_evidence_is_recorded_per_populated_field_and_visible_in_trace():
    canned = _extraction(
        port={"value": "durban", "evidence": "at the Port of Durban"},
        gross_tonnage={"value": 51255.0, "evidence": "GT 51,255"},
    )
    result = parse_vessel_request("...", llm=_StubChatModel(canned))

    by_field = {entry.field: entry.evidence for entry in result.trace}
    assert by_field == {
        "port": "at the Port of Durban",
        "gross_tonnage": "GT 51,255",
    }
    # Only populated fields appear in the trace — nothing for the 23 unset ones.
    assert len(result.trace) == 2


def test_raw_request_text_is_preserved():
    canned = _extraction(port={"value": "durban", "evidence": "Durban"}, gross_tonnage={"value": 1000.0, "evidence": "1000 GT"})
    text = "Vessel at Durban, 1000 GT."
    result = parse_vessel_request(text, llm=_StubChatModel(canned))
    assert result.raw_request_text == text


def test_trace_df_returns_one_row_per_populated_field():
    pd = pytest.importorskip("pandas")
    canned = _extraction(port={"value": "durban", "evidence": "Durban"}, gross_tonnage={"value": 1000.0, "evidence": "1000 GT"})
    result = parse_vessel_request("...", llm=_StubChatModel(canned))
    df = result.trace_df()
    assert len(df) == 2
    assert set(df["field"]) == {"port", "gross_tonnage"}


# ---------------------------------------------------------------------------
# Hard-error validation (never fall through to None / base case)
# ---------------------------------------------------------------------------


def test_missing_required_fields_raise_validation_error():
    canned = _extraction(vessel_name={"value": "SUDESTADA", "evidence": "SUDESTADA"})  # no port, no GT
    with pytest.raises(ValidationError):
        parse_vessel_request("The vessel SUDESTADA arrived.", llm=_StubChatModel(canned))


def test_non_positive_gross_tonnage_raises_validation_error():
    canned = _extraction(
        port={"value": "durban", "evidence": "Durban"},
        gross_tonnage={"value": -100.0, "evidence": "-100 GT"},
    )
    with pytest.raises(ValidationError):
        parse_vessel_request("...", llm=_StubChatModel(canned))


def test_negative_number_of_operations_raises_validation_error():
    canned = _extraction(
        port={"value": "durban", "evidence": "Durban"},
        gross_tonnage={"value": 1000.0, "evidence": "1000 GT"},
        number_of_operations={"value": -1, "evidence": "-1 operations"},
    )
    with pytest.raises(ValidationError):
        parse_vessel_request("...", llm=_StubChatModel(canned))


def test_negative_chargeable_period_days_raises_validation_error():
    canned = _extraction(
        port={"value": "durban", "evidence": "Durban"},
        gross_tonnage={"value": 1000.0, "evidence": "1000 GT"},
        chargeable_period_days={"value": -3.0, "evidence": "-3 days"},
    )
    with pytest.raises(ValidationError):
        parse_vessel_request("...", llm=_StubChatModel(canned))


# ---------------------------------------------------------------------------
# Pure function: no shared state between calls
# ---------------------------------------------------------------------------


def test_parser_is_a_pure_function_no_shared_state_between_calls():
    canned_a = _extraction(port={"value": "durban", "evidence": "Durban"}, gross_tonnage={"value": 1000.0, "evidence": "1000 GT"})
    canned_b = _extraction(port={"value": "saldanha", "evidence": "Saldanha"}, gross_tonnage={"value": 2000.0, "evidence": "2000 GT"})

    result_a = parse_vessel_request("first request", llm=_StubChatModel(canned_a))
    result_b = parse_vessel_request("second request", llm=_StubChatModel(canned_b))

    assert result_a.vessel_call.port == Port.DURBAN
    assert result_b.vessel_call.port == Port.SALDANHA
    assert result_a.vessel_call.gross_tonnage == 1000.0
    assert result_b.vessel_call.gross_tonnage == 2000.0


def test_system_prompt_and_request_text_are_both_sent_to_the_model():
    canned = _extraction(port={"value": "durban", "evidence": "Durban"}, gross_tonnage={"value": 1000.0, "evidence": "1000 GT"})
    stub = _StubChatModel(canned)
    parse_vessel_request("a very specific request", llm=stub)

    roles = [m[0] for m in stub.structured.received_messages]
    texts = [m[1] for m in stub.structured.received_messages]
    assert roles == ["system", "human"]
    assert "a very specific request" in texts


# ---------------------------------------------------------------------------
# Live smoke test — skipped unless ANTHROPIC_API_KEY is set
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not os.environ.get("ANTHROPIC_API_KEY"), reason="requires a real ANTHROPIC_API_KEY")
def test_live_parse_of_the_reference_case_narrative():
    text = (
        "SUDESTADA, a bulk carrier, is calling at the Port of Durban. "
        "GT 51,255. Number of Operations: 2."
    )
    result = parse_vessel_request(text)
    assert result.vessel_call.port == Port.DURBAN
    assert result.vessel_call.gross_tonnage == 51255
    assert result.vessel_call.number_of_operations == 2
    assert len(result.trace) >= 3
