# Known issues — to fix later

Found live, not yet fixed. Each entry states what's wrong, where, and why it matters.

## `tariffs/nlp.py` bypasses `tariffs/engine.py` entirely

`tariffs/nlp.py`'s module docstring (line 8) claims `Parsed.call` "goes into the
existing v1 engine (`tariffs.engine.calculate()`)". That's stale — the real code
doesn't call `engine.calculate()` at all. `parse_vessel_request()` (nlp.py:429-430)
calls `_compute_tariff_outcomes(vessel_call, resolved_schedule)` (nlp.py:326),
which loops over `_TARIFF_PLAN` (nlp.py:311) and calls each `tariffs.calculators`
function directly — a second, separate calling path into `calculators.py` that
duplicates what `engine.calculate()` already does, rather than reusing it.

**Consequence found while checking this:** `resolved_schedule` defaults to
`_get_schedule()` (nlp.py:252), which calls the *old*, fixed-path `load_schedule()`
— no port, no date. This means `parse_vessel_request()` — the real, user-facing
entry point used by the CLI, the Streamlit calculator page, and the API — never
goes through Stage 5's registry-based, by-port-and-date schedule selection
(`tariffs.registry.schedule_path_for()` / `load_schedule_for()`). Only code that
calls `engine.calculate()` directly (the test suite, the notebook) actually
benefits from Stage 5's work; the real app-facing path does not.

**To fix:** make `parse_vessel_request()` route through `engine.calculate()` (or
at least through `load_schedule_for(call.port, call.arrival)`) instead of its own
separate `_TARIFF_PLAN` + `_get_schedule()` path — one schedule-selection
mechanism, not two that can silently drift apart. Needs care: `_TARIFF_PLAN` also
carries per-tariff modifier functions and dependency checks (`_has_operations`,
`_has_chargeable_period`) that `engine.calculate()` doesn't currently expose the
same way — this isn't a one-line swap.

## ~~`pricing_params` is a free `dict[str, Any]`~~ — fixed

Was here as an open item; `extraction/schemas.py`'s `PricingShapes` (one typed,
closed sub-model per `pricing_type`, a model validator enforcing exactly one
selected) has since replaced the free dict. Left off this list now — see that
commit's message for the full story, including the OpenAI strict-mode
incompatibility this also turned out to fix.
