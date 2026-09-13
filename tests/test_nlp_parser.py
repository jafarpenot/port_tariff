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
from tariffs.nlp import Parsed, Rejected, VesselCallExtraction, parse_vessel_request


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
    each as {"value": ..., "evidence": "..."}. off_topic/unrecognized_port
    are passed through as plain values, not {value, evidence} slots."""
    return VesselCallExtraction(**slots)


# ---------------------------------------------------------------------------
# Schema shape
# ---------------------------------------------------------------------------


def test_extraction_schema_covers_every_vessel_call_field_plus_two_meta_fields():
    extra = set(VesselCallExtraction.model_fields.keys()) - set(VesselCall.model_fields.keys())
    assert set(VesselCall.model_fields.keys()) <= set(VesselCallExtraction.model_fields.keys())
    assert extra == {"off_topic", "unrecognized_port"}


def test_extraction_schema_fields_are_all_optional_at_top_level():
    ext = VesselCallExtraction()  # no arguments at all — every slot must default to None
    for name in VesselCall.model_fields:
        assert getattr(ext, name) is None
    assert ext.off_topic is None
    assert ext.unrecognized_port is None


# ---------------------------------------------------------------------------
# Happy path: populated fields flow through, with evidence
# ---------------------------------------------------------------------------


def test_populated_fields_become_a_parsed_result_with_valid_vessel_call():
    canned = _extraction(
        port={"value": "durban", "evidence": "at the Port of Durban"},
        gross_tonnage={"value": 51255.0, "evidence": "GT 51,255"},
        vessel_type={"value": "bulk_carrier", "evidence": "bulk carrier"},
    )
    result = parse_vessel_request("A bulk carrier, GT 51,255, calling at the Port of Durban.", llm=_StubChatModel(canned))

    assert isinstance(result, Parsed)
    assert result.call.port == Port.DURBAN
    assert result.call.gross_tonnage == 51255.0
    assert result.call.vessel_type == VesselType.BULK_CARRIER


def test_unpopulated_fields_stay_none_not_guessed():
    canned = _extraction(
        port={"value": "durban", "evidence": "Durban"},
        gross_tonnage={"value": 51255.0, "evidence": "51,255 GT"},
    )
    result = parse_vessel_request("Durban, 51,255 GT.", llm=_StubChatModel(canned))

    assert isinstance(result, Parsed)
    call = result.call
    assert call.vessel_name is None
    assert call.length_overall_m is None
    assert call.chargeable_period_days is None
    assert call.mooring_boat_used is None
    assert call.hull_certification == []  # VesselCall's own default, not a guessed value


def test_evidence_is_recorded_per_populated_field():
    canned = _extraction(
        port={"value": "durban", "evidence": "at the Port of Durban"},
        gross_tonnage={"value": 51255.0, "evidence": "GT 51,255"},
    )
    result = parse_vessel_request("...", llm=_StubChatModel(canned))

    assert isinstance(result, Parsed)
    by_field = {entry.field: entry.evidence for entry in result.evidence}
    assert by_field == {
        "port": "at the Port of Durban",
        "gross_tonnage": "GT 51,255",
    }
    assert len(result.evidence) == 2


def test_trace_df_returns_one_row_per_populated_field():
    pytest.importorskip("pandas")
    canned = _extraction(port={"value": "durban", "evidence": "Durban"}, gross_tonnage={"value": 1000.0, "evidence": "1000 GT"})
    result = parse_vessel_request("...", llm=_StubChatModel(canned))
    assert isinstance(result, Parsed)
    df = result.trace_df()
    assert len(df) == 2
    assert set(df["field"]) == {"port", "gross_tonnage"}


# ---------------------------------------------------------------------------
# Bad requests: normal outcomes (Rejected), never exceptions
# ---------------------------------------------------------------------------


def test_off_topic_request_is_rejected_with_helpful_reason():
    canned = _extraction(off_topic=True)
    result = parse_vessel_request("What's the weather like in Cape Town today?", llm=_StubChatModel(canned))

    assert isinstance(result, Rejected)
    assert "TNPA" in result.reason or "port tariffs" in result.reason
    assert "SUDESTADA" in result.reason  # the example request is present
    assert result.missing_fields == []


def test_missing_gross_tonnage_is_rejected_not_raised():
    canned = _extraction(
        vessel_name={"value": "SUDESTADA", "evidence": "SUDESTADA"},
        port={"value": "durban", "evidence": "Durban"},
    )
    result = parse_vessel_request("The vessel SUDESTADA arrived at Durban.", llm=_StubChatModel(canned))

    assert isinstance(result, Rejected)
    assert "gross_tonnage" in result.missing_fields
    assert "port" not in result.missing_fields
    # Whatever WAS extracted is still visible, not thrown away.
    assert {e.field for e in result.parsed_so_far} == {"vessel_name", "port"}


def test_missing_port_and_gross_tonnage_is_rejected_not_raised():
    canned = _extraction(vessel_name={"value": "SUDESTADA", "evidence": "SUDESTADA"})
    result = parse_vessel_request("The vessel SUDESTADA sailed.", llm=_StubChatModel(canned))

    assert isinstance(result, Rejected)
    assert set(result.missing_fields) == {"port", "gross_tonnage"}


def test_unrecognized_port_is_rejected_with_reason_naming_it():
    canned = _extraction(
        gross_tonnage={"value": 20000.0, "evidence": "20,000 GT"},
        unrecognized_port="Walvis Bay",
    )
    result = parse_vessel_request("A vessel, 20,000 GT, called at Walvis Bay.", llm=_StubChatModel(canned))

    assert isinstance(result, Rejected)
    assert "Walvis Bay" in result.reason
    assert "Durban" in result.reason  # names the actual eight ports supported


# ---------------------------------------------------------------------------
# Incomplete but not rejected: partial computability, never a silent zero
# ---------------------------------------------------------------------------


def test_partial_request_missing_operation_count_reports_three_tariffs_not_computable():
    # GT, port, and an explicit chargeable period are given (so light
    # dues, VTS and port dues all have what they need); number_of_operations
    # is not. pilotage/towage/berthing all depend on it — nothing else does.
    canned = _extraction(
        port={"value": "durban", "evidence": "Durban"},
        gross_tonnage={"value": 51255.0, "evidence": "GT 51,255"},
        chargeable_period_days={"value": 3.396, "evidence": "alongside for 3.396 days"},
    )
    result = parse_vessel_request("...", llm=_StubChatModel(canned))

    assert isinstance(result, Parsed)
    computed = {name for name, outcome in result.tariffs.items() if outcome.computed}
    not_computed = {name for name, outcome in result.tariffs.items() if not outcome.computed}

    assert computed == {"light_dues", "vts_dues", "port_dues"}
    assert not_computed == {"pilotage_dues", "towage_dues", "berthing_services"}
    assert len(not_computed) == 3

    for name in not_computed:
        outcome = result.tariffs[name]
        assert outcome.result is None
        assert "number_of_operations" in outcome.reason

    totals = result.totals()
    assert totals["light_dues"] is not None
    assert totals["pilotage_dues"] is None  # never a silent zero


def test_number_of_operations_is_never_defaulted_to_two():
    """The reference case happens to use 2 — that must not become a rule
    the parser applies when the count is simply missing."""
    canned = _extraction(
        port={"value": "durban", "evidence": "Durban"},
        gross_tonnage={"value": 51255.0, "evidence": "GT 51,255"},
    )
    result = parse_vessel_request("...", llm=_StubChatModel(canned))
    assert isinstance(result, Parsed)
    assert result.call.number_of_operations is None
    assert result.tariffs["towage_dues"].computed is False


def test_missing_chargeable_period_only_blocks_port_dues():
    canned = _extraction(
        port={"value": "durban", "evidence": "Durban"},
        gross_tonnage={"value": 51255.0, "evidence": "GT 51,255"},
        number_of_operations={"value": 2, "evidence": "Number of Operations: 2"},
    )
    result = parse_vessel_request("...", llm=_StubChatModel(canned))

    assert isinstance(result, Parsed)
    assert result.tariffs["port_dues"].computed is False
    assert "chargeable_period_days" in result.tariffs["port_dues"].reason
    for name in ("light_dues", "vts_dues", "pilotage_dues", "towage_dues", "berthing_services"):
        assert result.tariffs[name].computed is True


def test_fully_complete_request_computes_all_six_tariffs():
    canned = _extraction(
        port={"value": "durban", "evidence": "Durban"},
        gross_tonnage={"value": 51255.0, "evidence": "GT 51,255"},
        number_of_operations={"value": 2, "evidence": "Number of Operations: 2"},
        chargeable_period_days={"value": 3.396, "evidence": "alongside for 3.396 days"},
    )
    result = parse_vessel_request("...", llm=_StubChatModel(canned))

    assert isinstance(result, Parsed)
    assert all(outcome.computed for outcome in result.tariffs.values())
    totals = result.totals()
    assert totals["light_dues"] == pytest.approx(60062.04, abs=0.01)
    assert totals["towage_dues"] == pytest.approx(147074.38, abs=0.01)
    assert totals["port_dues"] == pytest.approx(199549.22, abs=0.01)


# ---------------------------------------------------------------------------
# Broken program vs. bad request: validation errors on POPULATED fields
# still raise — never caught, never downgraded to a rejection or a None.
# ---------------------------------------------------------------------------


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

    assert isinstance(result_a, Parsed) and isinstance(result_b, Parsed)
    assert result_a.call.port == Port.DURBAN
    assert result_b.call.port == Port.SALDANHA
    assert result_a.call.gross_tonnage == 1000.0
    assert result_b.call.gross_tonnage == 2000.0


def test_system_prompt_and_request_text_are_both_sent_to_the_model():
    canned = _extraction(port={"value": "durban", "evidence": "Durban"}, gross_tonnage={"value": 1000.0, "evidence": "1000 GT"})
    stub = _StubChatModel(canned)
    parse_vessel_request("a very specific request", llm=stub)

    roles = [m[0] for m in stub.structured.received_messages]
    texts = [m[1] for m in stub.structured.received_messages]
    assert roles == ["system", "human"]
    assert "a very specific request" in texts


# ---------------------------------------------------------------------------
# Live smoke tests — skipped unless ANTHROPIC_API_KEY is set
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not os.environ.get("ANTHROPIC_API_KEY"), reason="requires a real ANTHROPIC_API_KEY")
def test_live_parse_of_the_reference_case_narrative():
    text = (
        "SUDESTADA, a bulk carrier, is calling at the Port of Durban. "
        "GT 51,255. Number of Operations: 2."
    )
    result = parse_vessel_request(text)
    assert isinstance(result, Parsed)
    assert result.call.port == Port.DURBAN
    assert result.call.gross_tonnage == 51255
    assert result.call.number_of_operations == 2
    assert len(result.evidence) >= 3


@pytest.mark.skipif(not os.environ.get("ANTHROPIC_API_KEY"), reason="requires a real ANTHROPIC_API_KEY")
def test_live_off_topic_request_is_rejected():
    result = parse_vessel_request("What's a good recipe for banana bread?")
    assert isinstance(result, Rejected)


@pytest.mark.skipif(not os.environ.get("ANTHROPIC_API_KEY"), reason="requires a real ANTHROPIC_API_KEY")
def test_live_unsupported_port_is_rejected():
    result = parse_vessel_request("A bulk carrier, GT 40,000, called at the Port of Walvis Bay.")
    assert isinstance(result, Rejected)
