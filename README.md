# Port Tariff Calculator

Calculates six Transnet National Ports Authority marine tariffs from a
structured vessel call, against the 23rd Edition (1 April 2024 – 31 March
2025) tariff book. Built to a fixed specification (`SPEC.md`); this README
explains what was built, where the book was ambiguous, and what was
deliberately left out of v1.

All figures in this document and produced by this package are **ex-VAT**
(VAT of 15% is noted on every page of the source book and is never applied
here).

---

## 1. What it does, and how to run it

A Python package with **one entry point**:

```python
from tariffs.engine import calculate
from tariffs.models import VesselCall, Port

call = VesselCall(port=Port.DURBAN, gross_tonnage=51255, ...)
result = calculate(call)
result.totals()     # {"light_dues": 60062.04, ...}
result.trace_df()    # one row per calculation step (needs pandas)
```

It takes a `VesselCall` and returns a `CalculationResult` carrying six
`TariffResult`s (amount, warnings, and a step-by-step trace) plus
convenience methods. There is no CLI, no HTTP layer, and no logging to
stdout inside the engine — a FastAPI layer could wrap `calculate()`
directly in a later version without touching this code.

### Install and run

This project uses [`uv`](https://docs.astral.sh/uv/) for a project-scoped,
reproducible environment (not your system/base Python).

```bash
uv sync              # creates .venv from uv.lock (pydantic + pyyaml only,
                      # plus pytest / pandas / jupyter as dev-only groups)
uv run pytest        # run all tests
uv run jupyter lab    # optional — open notebooks/exploration.ipynb
```

In VS Code: select `.venv/bin/python` as the interpreter, and the
**"Python (port-tariff)"** kernel for the notebook.

### Repository layout

```
config/
    tariffs_2024_2025.yaml       # rate schedule, extracted from the PDF, with source citations
    assignment_mapping.yaml      # benchmark output-name adapter (§3)
tariffs/
    models.py       # VesselCall, RoundingMode, results/trace
    schedule.py      # YAML loader + Pydantic schema for the config
    shapes.py        # the four calculator shapes, each implemented once
    calculators.py   # one function per tariff
    modifiers.py     # reductions, surcharges, exemptions
    engine.py        # the single entry point, calculate()
    adapter.py       # assignment output mapping
tests/               # five layers — see §6
notebooks/exploration.ipynb   # optional; a consumer of the package, not part of the graded path
```

**Principle followed throughout:** anything that varies by port, band, or
tariff edition is *data* (in `config/`); the mathematical mechanism is
*code* (in `tariffs/`). The four calculator shapes in `shapes.py` are each
implemented exactly once and parameterised from config — there is no
`if/elif` cascade over ports anywhere in this package.

---

## 2. Reference case results

**Vessel:** SUDESTADA, bulk carrier, Malta flag, built 2010, at Durban.
Inputs as reconciled below (GT 51,255 and chargeable period 3.396 days —
see §4, "Known deviations").

| Tariff | Computed | Expected (answer key) |
|---|---|---|
| Light dues | 60,062.04 | 60,062.04 ✓ |
| Port dues | 199,549.22 | 199,549.22 ✓ |
| Towage dues | 147,074.38 | 147,074.38 ✓ |
| VTS dues | 33,315.75 | 33,315.75 ✓ |
| Pilotage dues | 47,189.94 | 47,189.94 ✓ |
| Running of vessel lines dues | 19,639.50 | 19,639.50 ✓ |

All six match to the cent. Reproduced by `tests/test_reference_case.py`.

---

## 3. The §3.8 / §3.9 mapping — most important item in this README

The assignment asks for **"running of vessel lines dues."** The tariff
book has a section with exactly that title — **§3.9, "Running of Vessel
Lines,"** page 19. **The answer key does not come from it.**

- §3.9 "Running of Vessel Lines," Other Ports: 1,654.56 per service →
  3,309.12 for two services. **Does not match.**
- §3.8 "Berthing Services," Other Ports:
  `(2,801.91 + 513 × 13.68) × 2 = 19,639.50`. **Exact match.**

**What the two services actually are.** §3.8 is the shore mooring gang who
take the vessel's lines and make them fast to bollards — charged on
essentially every berthing and unberthing. §3.9 is narrower: a launch or
mooring boat used to carry the lines from ship to bollard across the
water, used only where the gang cannot take them directly. They are
**additive, not alternatives** — when a mooring boat is used, both are
billed.

**How this is implemented:**

1. Both services are modelled as separate, correctly-named domain
   calculators (`calculators.berthing_services` and
   `calculators.running_of_vessel_lines`). Nothing in the engine chooses
   between them.
2. `berthing_services` (§3.8) fires on every marine service and is fully
   calculated — this is what produces the 19,639.50 figure above.
3. `running_of_vessel_lines` (§3.9) is **parsed, not calculated**, in v1
   (see §7 below). It is gated on `VesselCall.mooring_boat_used`; if that
   flag is `True`, the result carries an explicit warning that a §3.9
   charge applies but is not computed in this version. It is never
   silently omitted.
4. A thin adapter (`tariffs/adapter.py` + `config/assignment_mapping.yaml`)
   maps the assignment's `running_of_vessel_lines` output slot onto the
   `berthing_services` result, carrying this explanation as a `note` **in
   the output object itself**, not only in this document. The adapter
   never suppresses the real §3.9 calculator — its result is always
   included alongside the mapped slot, under its own name.

---

## 4. Known deviations

Two input-rounding artefacts, both stated in `SPEC.md` and neither a
defect in this implementation.

1. **VTS.** `33,315.75 ÷ 0.65 = 51,255` exactly. The answer key was
   computed on GT 51,255; the vessel sheet says 51,300. VTS is the only
   tariff charged on **exact** GT (`RoundingMode.EXACT`), so it is the
   only one that exposes this — every other tariff rounds up to units of
   100 and both values give `ceil(51255/100) = ceil(51300/100) = 513`.
   Using the sheet's GT 51,300 yields **33,345.00**, a deviation of
   **+ZAR 29.25 (+0.088%)**.
2. **Port dues.** The answer key uses 3.396 days; the vessel sheet shows
   3.39, a truncation of the same figure. Using 3.39 yields **199,371.35**,
   a deviation of **−ZAR 177.87 (−0.089%)**.

`tests/test_reference_case.py` asserts the exact key values (GT 51,255,
3.396 days) **and** documents the deviation when the sheet's rounded
values (51,300 / 3.39) are used instead. The calculators were never
adjusted to absorb the difference.

---

## 5. Interpretations

Decisions made where the book is silent, ambiguous, or where the
supplied input under-specifies a formula input.

**From the spec (settled, not re-derived here):**

- **Port dues chargeable period.** The book defines it as from passing
  the entrance inwards until passing the entrance outwards. No entrance
  timestamps were supplied; arrival-to-departure (7.117 days) yields
  309,853, far from the answer key. Days alongside (3.396 days) is used as
  the closest available proxy, and reconciles exactly. This likely
  understates the true chargeable period by the inbound/outbound transit
  time between the entrance and the anchorage/berth — time at anchorage
  waiting for a berth is correctly excluded, but so is genuine transit
  time inside the entrance. `VesselCall.chargeable_period_basis` records
  which case applies (`entrance_to_entrance` vs. `days_alongside_proxy`);
  entrance timestamps, if ever supplied, take precedence.
- **Band interval convention.** `min_gt_exclusive` is exclusive,
  `max_gt_inclusive` is inclusive. The printed towage table overlaps at
  band edges (e.g. "2 001 to 10 000" followed by "10 000 to 50 000" — GT
  10,000 appears in both rows in the book). This convention resolves that
  overlap; a vessel at exactly a boundary GT falls into the **lower**
  band. Nothing in the source data resolves this either way — it is an
  implementation choice.
- **60% vs. 35% port dues reduction.** The book states the 60% reduction
  "will not be enjoyed in addition to" the 35%, without naming a winner.
  This implementation applies the 60% and drops the 35% — it is the
  narrower, more specific condition and the larger reduction. In
  practice the two rarely co-occur, since a bunkers-only call is already
  not cargo working.
- **15% port dues reduction, applied multiplicatively.** Described as "in
  addition to other reductions that may be enjoyed." Applied to the
  already-reduced figure, not the base: 35% then 15% gives
  `0.65 × 0.85 = 0.5525`, not a flat 50%. No reference value confirms
  this.
- **`number_of_operations` read as `marine_service_count`.** The vessel
  sheet says "Number of Operations: 2," which is not literally "number of
  marine services." The equivalence is inferred from the answer key —
  pilotage, towage and berthing all match only when doubled. This is
  recorded as a benchmark assumption (`VesselCall.resolved_marine_service_count()`),
  not a general rule for future inputs; a future caller could set
  `marine_service_count` directly and bypass the inference entirely.

**Introduced in this implementation, beyond what the spec settles:**

- **10% port dues reduction stacks multiplicatively too.** The book only
  states the multiplicative-stacking rule explicitly for the 15%
  reduction. Nothing suggests the 10% (tanker hull certification) behaves
  differently, so it is treated the same way. Unconfirmed by any
  reference value.
- **Towage surcharges stack additively.** Each is worded in the book as
  "a surcharge of X% is payable" — read as X% of the base fee, added.
  When more than one surcharge condition is met simultaneously (e.g.
  out-of-hours **and** an additional tug), their rates are summed
  (`1 + 0.25 + 0.50`, not `1.25 × 1.50`). Unconfirmed by any reference
  value.
- **Out-of-hours is resolved per call, not per service.** The book's
  surcharge triggers when a *service* starts or ends. `VesselCall` carries
  one arrival and one departure timestamp for the whole call, not one per
  service, so the out-of-hours check looks at whether *either* endpoint
  falls outside ordinary hours, and — when it fires — applies to the
  call's services uniformly rather than to only the affected one.
- **Pilotage's SAPS/SANDF exemption.** The book's wording is inverted
  from every other exemption: SAPS/SANDF vessels are exempt from pilotage
  dues *unless they themselves request pilotage* — normally exempt,
  forfeited only on request. `VesselCall` has no `pilotage_requested`
  field, so that carve-out cannot be evaluated. This implementation
  applies the exemption as a plain, unconditional one whenever
  `exemption_status` is SAPS or SANDF, which will be wrong in the
  (presumably rare) case where such a vessel explicitly requests
  pilotage.
- **The Saldanha towage anomaly is preserved, not corrected.** In the
  printed towage table (§3.6, p.15), Saldanha's `per_100t` rate falls
  across every band except the last, where it rises (27.97 → 47.32).
  Verified against the source PDF via two independent extraction passes
  (plain-text and layout-preserving) — this is what the book prints, not
  a transcription error introduced here. It is left as extracted and
  called out explicitly in `config/tariffs_2024_2025.yaml` and in
  `tests/test_monotonicity.py`, which pins the anomaly rather than
  silently allowing it to pass or fail.
- **"Not undergoing repairs" cannot be confirmed.** The port dues
  long-stay surcharge (§9.2) requires a vessel to be neither engaged in
  cargo working *nor undergoing repairs*. `VesselCall` has no field for
  the latter, so it can never be positively ruled in or out — the
  surcharge can only ever resolve to "applied" or "unresolved," never a
  confident "not applied" on that specific leg.
- **Public holidays are entirely unmodelled**, not merely "left as an
  edge case." §8.3 hints a holiday might sit outside ordinary hours even
  at a 24-hour port, but no calendar exists in v1 to test a date against.
  The out-of-hours derivation is exact for ordinary weekdays and
  Saturdays, and can be wrong specifically on a public holiday.

---

## 6. Assumptions

**Base-case policy** (`VesselCall` resolution, `SPEC.md` §8.2), applied
throughout: *default to the unmodified published tariff; no reduction or
surcharge is applied unless supported by the supplied input.* A tri-state
model is used everywhere a modifier flag matters — `True` (stated),
`False` (stated), and `None` ("not stated"). `None` is never silently
coerced to `False`; every modifier that was *considered* — whether it
fired, was explicitly ruled out, or was left unresolved — is recorded in
`TariffResult.trace`, distinguishing "stated false" from "not stated,
treated as base case" in the trace text itself.

**For the reference case specifically**, every tri-state modifier flag
is unresolved (`None`) — `engaged_in_cargo_working`, `is_bona_fide_coaster`,
`is_passenger_vessel`, `call_purpose_bunkers_stores_water_only`,
`exemption_status`, all five towage event flags, and pilotage/berthing's
cancellation and lateness flags. `mooring_boat_used` is also unresolved
(taken as not used). This is exactly why the base-case engine alone
reproduces all six answer-key values without any modifier ever firing.

The one modifier that *is* derived rather than stated for the reference
case is the out-of-hours check — Durban is a 24-hour port (§8.3), so it
structurally cannot fire there regardless of the timestamps supplied.

---

## 7. Not implemented in v1

Per `SPEC.md` §1 and §7.6, none of the following are built, stubbed with
`NotImplementedError` in the call path, or given a dependency:

- **§3.9 Running of Vessel Lines charge.** The calculator exists and the
  `mooring_boat_used` flag is parsed and carried, but no amount is ever
  computed — only a warning, when the flag is `True` (see §3 above).
- **South African public holiday calendar.** See §5 above.
- **Natural-language parsing of the vessel query** (an LLM call turning a
  free-text description into a `VesselCall`). `VesselCall` is built by
  hand in v1 and in the notebook; its field set is already complete
  enough to carry what a future parser would populate (the event flags in
  particular — see below).
- **Any HTTP/API layer.** `calculate()` is a plain function; a FastAPI
  layer is a v2 concern that should wrap it without modification.
- **Towage's flat late-arrival fee** (per tug, per half-hour) and the
  marine services incentive (§9.4) are calculated nowhere — the former
  needs minutes-late and tug-count data `VesselCall` doesn't carry (warned
  instead, like §3.9); the latter needs shipping-line identity and
  national call-count data that has no field in the model at all, and is
  always reported as "not supported by input," never silently omitted.
- **PLO duties** (§3.3) and the **small-vessel port dues minimum** (§4.1.1)
  are captured in config with full provenance but wired into no
  calculator — both are explicitly out of scope for a commercial vessel
  call in v1.

---

## 8. Outputs are ex-VAT

Every rate in the source book is ex-VAT (VAT 15%, noted in every page
footer); this package never applies VAT anywhere. All figures quoted in
this document, and every `TariffResult.amount`, are ex-VAT ZAR.

---

## 9. Production extensions (brief)

Sketched, not built, for v2:

- **LLM parsing layer** turning a free-text vessel/voyage description
  into a `VesselCall` — the model's tri-state event flags
  (`mooring_boat_used`, `additional_tug_requested`,
  `service_cancelled_after_standby`, `late_against_notified_time`, etc.)
  exist specifically so such a parser has somewhere to put what it finds,
  without any change to the engine.
- **A FastAPI endpoint** wrapping `tariffs.engine.calculate()` directly.
- **External enrichment** (AIS, vessel registries, port-call history) to
  resolve currently-unresolvable flags automatically — e.g. confirming
  bona fide coaster status, hull certification, or a vessel's registered
  port, instead of requiring them as explicit input.

---

## 10. Manual verification obligation (not automated)

Roughly a hundred numbers were extracted from `Port_Tariff.pdf` into
`config/tariffs_2024_2025.yaml`, and only a handful are exercised by the
reference case or the automated tests. **The towage table on page 15 in
particular should be checked cell-by-cell against the source PDF by
hand** before this config is trusted for any port/GT combination beyond
what's tested here. This is not re-verified by any automated test, and
should be repeated if the config is ever hand-edited.

**Status: done, twice, independently, on 2026-09-12.** First via two
independent text-extraction passes during the build (plain-text and
layout-preserving), which is what caught the Saldanha anomaly noted in
§5. Then via an actual rendered page image of printed page 15, read cell
by cell against every value in `towage.ports` and `towage.craft_allocation`
— confirming all of it, including that the Saldanha anomaly is genuinely
printed that way and not an artifact of text extraction. **The repo
owner also independently checked page 15 against the config by hand**,
separately from the two passes above.

---

## Notebook

`notebooks/exploration.ipynb` is optional and not part of the graded
path — the tests are. It imports and calls the package; it defines no
formulas, rate values, or logic of its own.
