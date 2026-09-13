"""v2: the natural-language parsing layer.

Scope, deliberately narrow: `parse_vessel_request()` is one pure function
that takes free-text and returns a validated `VesselCall`. That object
then goes into the existing v1 engine (`tariffs.engine.calculate()`)
completely unchanged — nothing here is imported by, or changes the
behaviour of, the calculation engine.

Division of labour, strictly enforced:

- **The LLM extracts, it never infers or calculates.** Every field is
  either read from something explicitly present in the request text, or
  left `None`. In particular, a duration is never computed from two dates
  here — `chargeable_period_days` is only populated if the text states a
  duration directly, never derived from `arrival`/`departure`.
- **Every populated field carries evidence** — the short, verbatim
  fragment of the request text it was read from — so a populated value
  can be told apart from an invented one. This is carried in
  `ParsedVesselCall.trace`.
- **Validation is a hard error.** Converting the draft extraction into a
  real `VesselCall` runs full Pydantic validation (including the
  gt/ge constraints on `VesselCall` itself). A failure raises
  `pydantic.ValidationError` — it is never caught and downgraded to a
  `None` field that would silently resolve to the engine's base case.

Kept as a single pure function, not a LangGraph node: with one
extraction step there is no branching, no loop, and no shared state to
justify a graph. See README "Why LangGraph was not used in v2" for what
would change that (interactive resolution of unknown fields, external
enrichment).
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field, create_model

from .models import VesselCall

_SYSTEM_PROMPT = """\
You extract a structured vessel port-call record from a free-text request. \
You are an EXTRACTOR, not an analyst: populate a field only if the request \
text explicitly and unambiguously states it. Never infer a value from \
context, typical values, or vessel type. Never calculate anything — in \
particular, never derive a duration (e.g. days alongside, days in port, \
chargeable period) from two dates you were given; only populate a \
duration field if the text states that duration directly, in those terms. \
If you are not confident a piece of text maps onto one of an enum field's \
allowed values, leave that field null rather than choosing the closest one.

For every field you DO populate, also provide, in that field's `evidence` \
slot, the shortest exact fragment of the request text that supports it. \
If you do not populate a field, leave its `evidence` null too.

Leave every field you cannot ground in the text as null. It is always \
correct to leave a field null; it is never correct to guess.\
"""


def _build_extraction_schema() -> type[BaseModel]:
    """Build a structured-output schema mirroring VesselCall field-for-
    field, where each field becomes an optional `{value, evidence}` slot.

    Generated from `VesselCall.model_fields` rather than hand-duplicated,
    so it can never silently drift out of sync with the real model.
    """
    slots: dict[str, Any] = {}
    for name, field in VesselCall.model_fields.items():
        slot_model = create_model(
            "".join(part.capitalize() for part in name.split("_")) + "Slot",
            value=(Optional[field.annotation], Field(default=None, description=field.description)),
            evidence=(
                Optional[str],
                Field(default=None, description="Shortest verbatim fragment of the request text supporting `value`."),
            ),
        )
        slots[name] = (Optional[slot_model], Field(default=None, description=field.description))
    return create_model("VesselCallExtraction", **slots)


VesselCallExtraction = _build_extraction_schema()


class ExtractionTraceEntry(BaseModel):
    """One populated field: what was read, and the text it came from."""

    field: str
    value: Any
    evidence: str


class ParsedVesselCall(BaseModel):
    """The result of `parse_vessel_request()`: the validated `VesselCall`
    the request text supports, plus the per-field evidence trace."""

    vessel_call: VesselCall
    trace: list[ExtractionTraceEntry] = Field(default_factory=list)
    raw_request_text: str

    def trace_df(self):
        """A pandas DataFrame, one row per populated field. Mirrors
        CalculationResult.trace_df()'s convention: pandas is imported
        lazily here and is not a dependency of this module or the
        `nlp` dependency group."""
        try:
            import pandas as pd
        except ImportError as exc:  # pragma: no cover - environment-dependent
            raise ImportError(
                "trace_df() requires pandas, which is not installed by the "
                "nlp dependency group — install it separately to use this method."
            ) from exc
        return pd.DataFrame([entry.model_dump() for entry in self.trace])


def _default_llm(model: str) -> Any:
    from langchain_anthropic import ChatAnthropic

    # No `temperature` argument: newer Claude models (e.g. claude-sonnet-5)
    # reject it outright ("temperature is deprecated for this model")
    # rather than ignoring it, so passing 0 here fails every real call.
    return ChatAnthropic(model=model)


def parse_vessel_request(
    request_text: str,
    *,
    llm: Any = None,
    model: str = "claude-sonnet-5",
) -> ParsedVesselCall:
    """Parse a free-text vessel-call request into a validated VesselCall.

    Pure function: every dependency (the model) is either passed in or
    constructed fresh from the given arguments — nothing module-level is
    read or mutated, and no state carries over between calls. `llm` can
    be any object exposing LangChain's
    `.with_structured_output(schema).invoke(messages)` surface — pass a
    stub here in tests instead of calling a real model.

    Raises `pydantic.ValidationError` if the extracted fields do not
    satisfy `VesselCall`'s validation (a missing required field, a
    negative GT, an unrecognised port, etc.) — deliberately: a bad field
    must fail loudly here, not fall through to `None` and silently
    resolve to the engine's base case.
    """
    resolved_llm = llm if llm is not None else _default_llm(model)
    structured_llm = resolved_llm.with_structured_output(VesselCallExtraction)

    extraction = structured_llm.invoke(
        [
            ("system", _SYSTEM_PROMPT),
            ("human", request_text),
        ]
    )

    draft_values: dict[str, Any] = {}
    trace: list[ExtractionTraceEntry] = []
    for field_name in VesselCall.model_fields:
        slot = getattr(extraction, field_name, None)
        if slot is None or slot.value is None:
            continue
        draft_values[field_name] = slot.value
        trace.append(ExtractionTraceEntry(field=field_name, value=slot.value, evidence=slot.evidence or ""))

    # Hard error on anything VesselCall itself rejects — never caught and
    # downgraded to a None field (module docstring, "Validation is a hard error").
    vessel_call = VesselCall(**draft_values)

    return ParsedVesselCall(vessel_call=vessel_call, trace=trace, raw_request_text=request_text)
