"""v2: the natural-language parsing layer.

Scope, deliberately narrow: `parse_vessel_request()` is one pure function
that takes free-text and returns a `ParseResult` — either `Parsed` (a
validated `VesselCall`, plus which of the six tariffs its fields support
computing) or `Rejected` (the request cannot be turned into a tariff
calculation at all, with a human-readable reason). `Parsed.call` then
goes into the existing v1 engine (`tariffs.engine.calculate()`)
completely unchanged if the caller wants the full engine's trace/
modifiers too — nothing here changes the calculation engine itself.

Two categories of failure, deliberately distinguished:

- **A bad request is a normal outcome, not an exception.** Off-topic
  text, a port outside the eight this book covers, or a request missing
  the hard floor (port and/or gross tonnage, without which nothing can
  be computed) — all of these come back as `Rejected`, for the caller to
  inspect and act on.
- **A broken program is still an exception.** The API being unreachable,
  a malformed model response, or a validation error on a field the model
  *did* populate (e.g. a stated GT that's negative) — none of these are
  caught. A bad but populated field must fail loudly, not be silently
  downgraded to `None`.

Division of labour, strictly enforced:

- **The LLM extracts, it never infers or calculates.** Every field is
  either read from something explicitly present in the request text, or
  left `None`. In particular, a duration is never computed from two dates
  here — `chargeable_period_days` is only populated if the text states a
  duration directly, never derived from `arrival`/`departure`.
- **Every populated field carries evidence** — the short, verbatim
  fragment of the request text it was read from — so a populated value
  can be told apart from an invented one. This is carried in
  `Parsed.evidence` / `Rejected.parsed_so_far`, and the quote itself is
  checked, not just trusted: `ExtractionTraceEntry.verified` records
  whether that fragment genuinely appears in the request text.
- **Incomplete is not the same as invalid.** A request missing
  `number_of_operations` or a chargeable period is still `Parsed` — the
  tariffs that need what's missing are reported as not computable
  (naming the missing field), never silently computed with a defaulted
  or assumed value, and never reported as zero.

Kept as a single pure function, not a LangGraph node: with one
extraction step there is no branching, no loop, and no shared state to
justify a graph. See README "Why LangGraph was not used in v2" for what
would change that (interactive resolution of unknown fields, external
enrichment).
"""

from __future__ import annotations

from typing import Any, Callable, Optional, Union

from pydantic import BaseModel, Field, create_model

from . import calculators, modifiers
from .models import TariffResult, VesselCall
from .schedule import TariffSchedule, load_schedule

_SUPPORTED_PORTS_TEXT = (
    "Richards Bay, Durban, East London, Ngqura, Port Elizabeth, Mossel Bay, Cape Town, or Saldanha"
)

_SYSTEM_PROMPT = f"""\
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
correct to leave a field null; it is never correct to guess.

Two additional classification fields, always answer both:
- `off_topic`: true if this request text has nothing to do with a vessel \
or a port call at all — an unrelated question or statement. false if it \
describes a vessel or a port call in any way, even partially.
- `unrecognized_port`: if the text names a specific port that is NOT one \
of {_SUPPORTED_PORTS_TEXT}, put that port's name here verbatim (do not \
also populate `port` in that case). Leave null if no port is named, or \
if the named port IS one of those eight — in that case populate `port` \
as normal instead.\
"""


def _build_extraction_schema() -> type[BaseModel]:
    """Build a structured-output schema mirroring VesselCall field-for-
    field, where each field becomes an optional `{value, evidence}` slot,
    plus two fixed classification fields (`off_topic`, `unrecognized_port`)
    that have no VesselCall counterpart.

    The per-VesselCall-field part is generated from `VesselCall.model_fields`
    rather than hand-duplicated, so it can never silently drift out of
    sync with the real model.
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

    slots["off_topic"] = (
        Optional[bool],
        Field(default=None, description="True if the request text has nothing to do with a vessel or a port call at all."),
    )
    slots["unrecognized_port"] = (
        Optional[str],
        Field(
            default=None,
            description=(
                "Verbatim name of a port mentioned in the text that is NOT one of the "
                f"eight this tool supports ({_SUPPORTED_PORTS_TEXT}). Null if no such "
                "out-of-scope port is named."
            ),
        ),
    )
    return create_model("VesselCallExtraction", **slots)


VesselCallExtraction = _build_extraction_schema()


class ExtractionTraceEntry(BaseModel):
    """One populated field: what was read, and the text it came from.

    `verified` is a cheap, deterministic check — does `evidence` actually
    appear (case/whitespace-insensitive) in the raw request text? It is
    **not** a guarantee the extracted `value` is correct, only that the
    model isn't quoting something that was never in the text. This is
    reported, not enforced: an unverified field is surfaced here, never
    silently rejected or dropped — a fuller accuracy evaluation (a
    labeled test set, or an LLM-as-judge second pass) is a larger,
    separate piece of work, deliberately not done here.
    """

    field: str
    value: Any
    evidence: str
    verified: bool = False


# Single source of truth for the §3.8/§3.9 explanation (README §3) — used
# by every delivery layer (tariffs/cli.py, tariffs/api.py, app.py) that
# surfaces the "berthing_services" tariff, so the wording can't drift
# between them.
BERTHING_SERVICES_NOTE = (
    "This is what 'running of vessel lines dues' actually reconciles to — "
    "Tariff Book §3.8 Berthing Services, not §3.9 Running of Vessel Lines "
    "(which is parsed but not calculated in this version). See README §3."
)


class TariffOutcome(BaseModel):
    """Whether one tariff could be computed from what was extracted.

    Never a silent zero: a tariff whose dependencies are missing has
    `computed=False` and a `reason` naming what's missing, not an
    `amount` of 0.
    """

    computed: bool
    result: Optional[TariffResult] = None
    reason: Optional[str] = None


class Parsed(BaseModel):
    """A request with enough information to compute at least the hard-
    floor tariffs (light dues, VTS — the only two that need nothing
    beyond port and gross tonnage). Tariffs whose extra dependencies
    (number of operations; chargeable period) are missing are reported
    in `tariffs` as not computable, never defaulted and never zero.
    """

    call: VesselCall
    evidence: list[ExtractionTraceEntry] = Field(default_factory=list)
    tariffs: dict[str, TariffOutcome] = Field(default_factory=dict)

    def totals(self) -> dict[str, Optional[float]]:
        """Computed amount per tariff, or None where not computable."""
        return {name: (o.result.amount if o.computed and o.result else None) for name, o in self.tariffs.items()}

    def trace_df(self):
        """A pandas DataFrame, one row per populated field. Mirrors
        CalculationResult.trace_df()'s convention: pandas is imported
        lazily here and is not a dependency of this module or the
        `nlp` dependency group."""
        return _entries_to_df(self.evidence)


class Rejected(BaseModel):
    """A request that cannot be turned into any tariff computation at
    all — off-topic, naming a port outside the book's eight, or missing
    the hard floor (port and/or gross tonnage). This is a normal
    outcome, not an exception: the caller inspects `reason`.
    """

    reason: str
    parsed_so_far: list[ExtractionTraceEntry] = Field(default_factory=list)
    missing_fields: list[str] = Field(default_factory=list)

    def trace_df(self):
        return _entries_to_df(self.parsed_so_far)


ParseResult = Union[Parsed, Rejected]


def _entries_to_df(entries: list[ExtractionTraceEntry]):
    try:
        import pandas as pd
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise ImportError(
            "trace_df() requires pandas, which is not installed by the "
            "nlp dependency group — install it separately to use this method."
        ) from exc
    return pd.DataFrame([entry.model_dump() for entry in entries])


def _default_llm(model: str) -> Any:
    from langchain_anthropic import ChatAnthropic

    # No `temperature` argument: newer Claude models (e.g. claude-sonnet-5)
    # reject it outright ("temperature is deprecated for this model")
    # rather than ignoring it, so passing 0 here fails every real call.
    return ChatAnthropic(model=model)


_schedule_cache: Optional[TariffSchedule] = None


def _get_schedule() -> TariffSchedule:
    global _schedule_cache
    if _schedule_cache is None:
        _schedule_cache = load_schedule()
    return _schedule_cache


def _evidence_is_verifiable(evidence: str, request_text: str) -> bool:
    """Case/whitespace-insensitive substring check: does `evidence` appear
    in `request_text` at all? Deliberately simple — no fuzzy matching, no
    extra dependency. Catches outright fabricated quotes; does not catch
    a paraphrased-but-genuine one, or confirm the *value* itself is right.
    """
    if not evidence.strip():
        return False
    normalize = lambda s: " ".join(s.split()).lower()
    return normalize(evidence) in normalize(request_text)


def _collect_populated_fields(
    extraction: BaseModel, request_text: str
) -> tuple[dict[str, Any], list[ExtractionTraceEntry]]:
    draft_values: dict[str, Any] = {}
    trace: list[ExtractionTraceEntry] = []
    for field_name in VesselCall.model_fields:
        slot = getattr(extraction, field_name, None)
        if slot is None or slot.value is None:
            continue
        draft_values[field_name] = slot.value
        evidence = slot.evidence or ""
        trace.append(
            ExtractionTraceEntry(
                field=field_name,
                value=slot.value,
                evidence=evidence,
                verified=_evidence_is_verifiable(evidence, request_text),
            )
        )
    return draft_values, trace


def _has_operations(call: VesselCall) -> bool:
    return call.marine_service_count is not None or call.number_of_operations is not None


def _has_chargeable_period(call: VesselCall) -> bool:
    return call.chargeable_period_days is not None


def _always(call: VesselCall) -> bool:
    return True


# Field-dependency table (SPEC.md v2 addendum): which of the six tariffs
# need more than the hard floor (port + GT, already guaranteed by the
# time this is consulted), and which existing calculator+modifier pair
# to call when they're satisfied. Deliberately does NOT default
# `number_of_operations` — a tariff whose dependency is missing is
# reported not computable, never computed with an assumed count.
_TARIFF_PLAN: dict[str, tuple[Callable, Callable, Callable[[VesselCall], bool], str]] = {
    "light_dues": (calculators.light_dues, modifiers.apply_to_light_dues, _always, ""),
    "vts_dues": (calculators.vts_dues, modifiers.apply_to_vts, _always, ""),
    "pilotage_dues": (calculators.pilotage_dues, modifiers.apply_to_pilotage, _has_operations, "number_of_operations"),
    "towage_dues": (calculators.towage_dues, modifiers.apply_to_towage, _has_operations, "number_of_operations"),
    "berthing_services": (
        calculators.berthing_services,
        modifiers.apply_to_berthing,
        _has_operations,
        "number_of_operations",
    ),
    "port_dues": (calculators.port_dues, modifiers.apply_to_port_dues, _has_chargeable_period, "chargeable_period_days"),
}


def _compute_tariff_outcomes(call: VesselCall, schedule: TariffSchedule) -> dict[str, TariffOutcome]:
    outcomes: dict[str, TariffOutcome] = {}
    for name, (calc_fn, mod_fn, dependency_met, missing_field) in _TARIFF_PLAN.items():
        if dependency_met(call):
            result = mod_fn(calc_fn(call, schedule), call, schedule)
            outcomes[name] = TariffOutcome(computed=True, result=result)
        else:
            outcomes[name] = TariffOutcome(
                computed=False,
                reason=f"not computable — missing {missing_field}",
            )
    return outcomes


_OFF_TOPIC_REASON = (
    "This tool calculates Transnet National Ports Authority (TNPA) port tariffs for a "
    "vessel call at a South African port — it can't help with that request. Example of "
    "what it expects: \"The bulk carrier SUDESTADA, GT 51,300, called at the Port of "
    "Durban. Arrived 15 Nov 2024, departed 22 Nov 2024. Number of Operations: 2.\""
)


def parse_vessel_request(
    request_text: str,
    *,
    llm: Any = None,
    model: str = "claude-sonnet-5",
    schedule: Optional[TariffSchedule] = None,
) -> ParseResult:
    """Parse a free-text vessel-call request into a `ParseResult`.

    Pure function: every dependency (the model, the rate schedule) is
    either passed in or constructed fresh from the given arguments —
    nothing module-level is mutated, and no state carries over between
    calls. `llm` can be any object exposing LangChain's
    `.with_structured_output(schema).invoke(messages)` surface — pass a
    stub here in tests instead of calling a real model.

    Returns `Rejected` (not an exception) for a bad request: off-topic
    text, a port outside the book's eight, or a request missing the hard
    floor (port and/or gross tonnage).

    Raises (does not catch) `pydantic.ValidationError` if a field the
    model DID populate fails validation (a negative GT, a negative
    count, etc.) — that is a broken response, not a bad request, and
    must fail loudly rather than being silently downgraded to `None`.
    """
    resolved_llm = llm if llm is not None else _default_llm(model)
    structured_llm = resolved_llm.with_structured_output(VesselCallExtraction)

    extraction = structured_llm.invoke(
        [
            ("system", _SYSTEM_PROMPT),
            ("human", request_text),
        ]
    )

    draft_values, trace = _collect_populated_fields(extraction, request_text)

    if getattr(extraction, "off_topic", None) is True:
        return Rejected(reason=_OFF_TOPIC_REASON, parsed_so_far=trace, missing_fields=[])

    unrecognized_port = getattr(extraction, "unrecognized_port", None)
    if unrecognized_port:
        return Rejected(
            reason=(
                f"'{unrecognized_port}' is not one of the eight ports this tool covers: "
                f"{_SUPPORTED_PORTS_TEXT}."
            ),
            parsed_so_far=trace,
            missing_fields=[],
        )

    missing_hard_floor = [f for f in ("port", "gross_tonnage") if f not in draft_values]
    if missing_hard_floor:
        return Rejected(
            reason=(
                "Not enough information to calculate any tariff — missing "
                f"{' and '.join(missing_hard_floor)}. Port and gross tonnage (GT) are "
                "both structurally required; nothing can be computed without them."
            ),
            parsed_so_far=trace,
            missing_fields=missing_hard_floor,
        )

    # Hard error on anything VesselCall itself rejects on a field that WAS
    # populated — a broken response, not a bad request. Never caught here
    # (module docstring, "A broken program is still an exception").
    vessel_call = VesselCall(**draft_values)

    resolved_schedule = schedule if schedule is not None else _get_schedule()
    tariffs = _compute_tariff_outcomes(vessel_call, resolved_schedule)

    return Parsed(call=vessel_call, evidence=trace, tariffs=tariffs)
