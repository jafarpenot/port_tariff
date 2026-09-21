"""v3+: HTTP API layer — `uvicorn tariffs.api:app`.

Wrapping only, same rule as tariffs/cli.py and app.py: the one endpoint
goes through tariffs.nlp.parse_vessel_request() and returns whatever
ParseResult comes back as JSON. tariffs.engine.calculate() is never
called here, and no calculation or business logic lives in this file.

Two secrets, two different jobs, both read from the environment (never
hardcoded, never committed):
- ANTHROPIC_API_KEY — pays for the LLM extraction (tariffs/nlp.py).
- API_TOKEN — gates who may call *this* API at all, checked as a bearer
  token on every endpoint except /health.
"""

from __future__ import annotations

import os
import secrets
from typing import Any, Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel

from .nlp import Rejected, parse_vessel_request

app = FastAPI(title="Port Tariff Calculator API", version="1.0")


class CalculateRequest(BaseModel):
    request: str


def _require_token(authorization: Optional[str] = Header(default=None)) -> None:
    expected = os.environ.get("API_TOKEN")
    if not expected:
        raise HTTPException(status_code=500, detail="Server misconfigured: API_TOKEN is not set.")
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token.")
    provided = authorization.removeprefix("Bearer ").strip()
    if not secrets.compare_digest(provided, expected):
        raise HTTPException(status_code=401, detail="Invalid token.")


@app.get("/health")
def health() -> dict:
    """Unauthenticated on purpose — for load balancer / uptime checks."""
    return {"status": "ok"}


@app.post("/calculate", dependencies=[Depends(_require_token)])
def calculate_endpoint(payload: CalculateRequest) -> dict[str, Any]:
    try:
        result = parse_vessel_request(payload.request)
    except Exception as exc:  # broken program, not a bad request — see tariffs/nlp.py
        raise HTTPException(status_code=500, detail=f"Parsing failed: {exc}") from exc

    if isinstance(result, Rejected):
        return {
            "status": "rejected",
            "reason": result.reason,
            "parsed_so_far": [e.model_dump() for e in result.parsed_so_far],
            "missing_fields": result.missing_fields,
        }

    return {
        "status": "parsed",
        "vessel_call": result.call.model_dump(mode="json"),
        "evidence": [e.model_dump() for e in result.evidence],
        "tariffs": {
            name: {
                "computed": outcome.computed,
                "amount": outcome.result.amount if outcome.computed and outcome.result else None,
                "reason": outcome.reason,
                "trace": (
                    [step.model_dump() for step in outcome.result.trace]
                    if outcome.computed and outcome.result
                    else []
                ),
                "warnings": outcome.result.warnings if outcome.computed and outcome.result else [],
            }
            # Note: the "berthing_services" key here is what actually
            # answers the assignment's "running of vessel lines dues" —
            # see README §3 for the full §3.8/§3.9 explanation. Unlike
            # tariffs/cli.py, this response attaches no explanatory note
            # for that mapping — a known, documented gap (README §3).
            for name, outcome in result.tariffs.items()
        },
    }
