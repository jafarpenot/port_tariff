"""v3+: tests for tariffs.api — the HTTP layer, wrapping only.

No real Anthropic API calls: parse_vessel_request is monkeypatched at
the module level tariffs.api imports it into, same idea as the stub LLM
used in tests/test_nlp_parser.py, one level further out.
"""

from fastapi.testclient import TestClient

import tariffs.api as api_module
from tariffs.models import Port, VesselCall
from tariffs.nlp import ExtractionTraceEntry, Parsed, Rejected, TariffOutcome

client = TestClient(api_module.app)

TOKEN = "test-token-123"


def _reference_parsed() -> Parsed:
    call = VesselCall(port=Port.DURBAN, gross_tonnage=51255, number_of_operations=2)
    return Parsed(
        call=call,
        evidence=[ExtractionTraceEntry(field="port", value="durban", evidence="Durban")],
        tariffs={
            "light_dues": TariffOutcome(computed=True, result=_fake_result(60062.04)),
            "berthing_services": TariffOutcome(computed=True, result=_fake_result(19639.50)),
            "pilotage_dues": TariffOutcome(computed=False, reason="not computable — missing number_of_operations"),
        },
    )


def _fake_result(amount: float):
    from tariffs.models import TariffResult

    return TariffResult(name="light_dues", amount=amount, trace=[], warnings=[])


# ---------------------------------------------------------------------------
# /health — unauthenticated
# ---------------------------------------------------------------------------


def test_health_requires_no_token():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# /calculate — auth
# ---------------------------------------------------------------------------


def test_calculate_without_token_is_rejected(monkeypatch):
    monkeypatch.setenv("API_TOKEN", TOKEN)
    response = client.post("/calculate", json={"request": "..."})
    assert response.status_code == 401


def test_calculate_with_wrong_token_is_rejected(monkeypatch):
    monkeypatch.setenv("API_TOKEN", TOKEN)
    response = client.post(
        "/calculate", json={"request": "..."}, headers={"Authorization": "Bearer wrong-token"}
    )
    assert response.status_code == 401


def test_calculate_with_no_server_token_configured_is_a_server_error(monkeypatch):
    monkeypatch.delenv("API_TOKEN", raising=False)
    response = client.post(
        "/calculate", json={"request": "..."}, headers={"Authorization": "Bearer anything"}
    )
    assert response.status_code == 500


# ---------------------------------------------------------------------------
# /calculate — happy path and rejection, with parse_vessel_request stubbed
# ---------------------------------------------------------------------------


def test_calculate_parsed_result_shape(monkeypatch):
    monkeypatch.setenv("API_TOKEN", TOKEN)
    monkeypatch.setattr(api_module, "parse_vessel_request", lambda text: _reference_parsed())

    response = client.post(
        "/calculate", json={"request": "..."}, headers={"Authorization": f"Bearer {TOKEN}"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "parsed"
    assert body["vessel_call"]["port"] == "durban"
    assert body["tariffs"]["light_dues"]["computed"] is True
    assert body["tariffs"]["light_dues"]["amount"] == 60062.04
    assert body["tariffs"]["pilotage_dues"]["computed"] is False
    assert body["tariffs"]["pilotage_dues"]["amount"] is None  # never a silent zero
    assert "number_of_operations" in body["tariffs"]["pilotage_dues"]["reason"]


def test_calculate_attaches_berthing_services_note_only_to_that_tariff(monkeypatch):
    monkeypatch.setenv("API_TOKEN", TOKEN)
    monkeypatch.setattr(api_module, "parse_vessel_request", lambda text: _reference_parsed())

    response = client.post(
        "/calculate", json={"request": "..."}, headers={"Authorization": f"Bearer {TOKEN}"}
    )
    body = response.json()
    assert body["tariffs"]["berthing_services"]["note"] is not None
    assert "§3.8" in body["tariffs"]["berthing_services"]["note"]
    assert body["tariffs"]["light_dues"]["note"] is None
    assert body["tariffs"]["pilotage_dues"]["note"] is None


def test_calculate_rejected_result_shape(monkeypatch):
    monkeypatch.setenv("API_TOKEN", TOKEN)
    rejected = Rejected(reason="This tool calculates TNPA port tariffs...", parsed_so_far=[], missing_fields=["port"])
    monkeypatch.setattr(api_module, "parse_vessel_request", lambda text: rejected)

    response = client.post(
        "/calculate", json={"request": "..."}, headers={"Authorization": f"Bearer {TOKEN}"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "rejected"
    assert body["reason"] == "This tool calculates TNPA port tariffs..."
    assert body["missing_fields"] == ["port"]


def test_calculate_broken_program_returns_clean_500_not_a_traceback(monkeypatch):
    monkeypatch.setenv("API_TOKEN", TOKEN)

    def _boom(text):
        raise ValueError("upstream exploded")

    monkeypatch.setattr(api_module, "parse_vessel_request", _boom)

    response = client.post(
        "/calculate", json={"request": "..."}, headers={"Authorization": f"Bearer {TOKEN}"}
    )
    assert response.status_code == 500
    assert "upstream exploded" in response.json()["detail"]
    assert "Traceback" not in response.text
