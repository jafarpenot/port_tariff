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

## `basis`/`rounding_mode`/`multiplicity` are free strings, not real enums

Found on a full, uncrashed live run of the real TNPA book through
`extraction/pipeline.py` against GPT-6 Luna (`eval_runs/auto/20260925T175806Z_full-tnpa-linear-pipeline.md`
has the full evidence). `ProposedRule.basis`, `.rounding_mode`, `.multiplicity`
(`extraction/schemas.py`) are plain `str` fields — nothing stops the model from
inventing `"gross tonnage"` instead of `"gross_tonnage"`, `"ceiling"`/`"up"`
instead of `"ceil_to_unit"`, `"once_per_call"` instead of `"per_call"`. Validate's
`_validate_enums()` only catches it after the fact, same shape of bug as the
now-fixed `pricing_params` issue.

**Confirmed to actually break a charge, not just add noise:** `port_dues`'s
validation history in that run shows attempt 1 with a `basis`+`rounding` error;
attempt 2 fixes those but introduces a `multiplicity` error; attempt 3
**regresses back** to the exact same `basis`+`rounding` mistake; attempt 4
regresses back to the `multiplicity` mistake. It never got all three fields
right simultaneously and burned its whole repair budget oscillating —
`port_dues` is the one charge that ended `EXTRACTION_FAILED` in that run.

**To fix:** same technique already proven on `pricing_params` — change
`basis: str` to `basis: Basis` (the enum already defined in `tariffs/rules.py`),
same for `rounding_mode` -> `RoundingMode` and `multiplicity` -> `Multiplicity`.
A native enum field becomes a real `enum: [...]` JSON-schema constraint, so the
model can't produce an invalid value on any attempt — no dict/union shape
involved, so none of the OpenAI strict-mode incompatibilities that
`pricing_params`/`per_port_rules` hit should apply here. Likely the single
highest-leverage fix outstanding: it's implicated in nearly every repair round
across every charge in that run, not just `port_dues`.

## The `unmapped`/`bundled` escape hatch during a verify-repair round — confirmed live, worse than expected

This is the Q1 issue discussed at length earlier in the project (see
`specs/EXTRACTION_SPEC.md`'s Stage 6 write-up) — a validate- or verify-repair
call can reclassify a charge's `outcome` away from `mapped` instead of fixing
its structure/content, since nothing constrains a repair call to keep the
outcome it already committed to.

**Confirmed live, with a clean before/after, on the same full TNPA run named
above:** `pilotage` and `berthing_services` were *both* correctly mapped and
structurally valid at one point in the run. Verify then raised a real but
narrow concern on each (missing surcharges/incentive info). Instead of adding
a caveat, the verify-repair re-extraction abandoned the entire mapped
proposal and declared both charges `unmapped` — and Verify correctly called
this out on both ("the proposal wrongly leaves an extractable charge
unmapped"). Two charges got *worse* because of this, not just failed to
improve — stronger evidence than anything seen before this run.

**To fix:** constrain a repair call (validate- or verify-triggered) so it
cannot change `outcome` away from `mapped` once already committed — it should
only be allowed to fix the structure/content of the proposal it already made.

## ~~No field for conditional surcharges/modifiers on `ProposedRule`~~ — fixed

Was here as an open item: `towage`'s after-hours/additional-tug/late-arrival
surcharges (and, presumably, light dues' 60-day South-African-waters/
coastal-status rule, not independently re-verified) had nowhere to go in the
schema, so a model that read them correctly still had no field to put them
in. `ProposedRule.modifiers` (a `condition` string plus exactly one of
`adjustment_percentage`/`adjustment_flat_amount`/`raw_description`) fixes
this — `raw_description` is the escape hatch for a surcharge that doesn't
fit a plain percentage or flat amount (confirmed needed live: towage's
Saldanha delay fee is priced per half-hour, not as either), so nothing about
this schema forces a surcharge to block the base charge from reaching
`mapped`. Live-verified on `towage`: outcome went from `unmapped` to
`mapped`, with all 6 real surcharges captured.

## ~~Towage: rates extrapolated into cells the source marks "n/a"~~ — resolved (and this doc's own facts were wrong)

Was here as an open item, naming East London, Mossel Bay, Durban, and Port
Elizabeth/Ngqura as affected, and claiming Saldanha's real above-100,000-ton
rate was 38.71. Re-checking those claims directly against the source PDF and
`config/tariffs_2024_2025.yaml` while re-verifying this fix found **two of
those five claims were themselves wrong**, inherited from the original run's
Verify step: Durban is not marked "n/a" above 100,000 tons (it has a real
rate, 23.65 — the original bug was a wrong value there, not extrapolation),
and Port Elizabeth/Ngqura's flagged value (21.50) was already correct, not
"n/a" as claimed. Saldanha's real rate is 47.32, not 38.71 (that figure was
actually Cape Town's rate, misattributed).

Re-verified live on `towage` after switching Map/Extract to native PDF input
(fixes a two-column-layout text-scrambling bug) and adding `modifiers`
(above): every one of the corrected values now comes back exactly right —
East London and Mossel Bay both correctly `n/a` (no band above their real
cutoff), Durban 23.65, Saldanha 47.32, Port Elizabeth/Ngqura still 21.50.
Not fixed by anything targeted at this issue directly — a side effect of the
two other fixes.
