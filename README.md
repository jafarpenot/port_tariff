# Port Tariff Calculator

Calculates six Transnet National Ports Authority marine tariffs from a
free-text vessel-call request, against the 23rd Edition (1 April 2024 –
31 March 2025) tariff book.

## Run it

**Option A — Docker (recommended)**
```bash
export ANTHROPIC_API_KEY=sk-ant-...   # or put it in a local .env file
docker compose up
# open http://localhost:8501
```
Run the test suite in the same image instead of the app:
```bash
docker compose run --rm app pytest
```

**Option B — local**
```bash
python -m venv .venv && source .venv/bin/activate   # keep this out of your global environment
pip install -e .
export ANTHROPIC_API_KEY=sk-ant-...                   # not needed for --json below
python -m tariffs.cli "your request here"
python -m tariffs.cli --json examples/sudestada.json  # no API key — bypasses the LLM
# Optional: pytest   (verifies the six reference values against the answer key)
```
(Already using `uv`? `uv sync && uv run --env-file .env python -m tariffs.cli "..."`.)

`ANTHROPIC_API_KEY` is the only environment variable required, read at
runtime — never baked into the Docker image or committed (see `.gitignore`).

---

Built to a fixed specification (`SPEC.md`); this README explains what
was built, where the book was ambiguous, and what was deliberately left
out. All figures here, and everything this package produces, are
**ex-VAT** — VAT of 15% is noted on every page of the source book and is
never applied by this system.

---

## 1. What it does

Two functions, two different jobs:

**`parse_vessel_request(text)`** — the real entry point. Turns free text
into either a `Parsed` (a validated `VesselCall`, plus which of the six
tariffs the text supports computing) or a `Rejected` (a reason, not an
exception). This is what the CLI and the Streamlit app use, always.

```python
from tariffs.nlp import parse_vessel_request, Rejected

result = parse_vessel_request("SUDESTADA, bulk carrier, Durban, GT 51,255, Number of Operations: 2.")
if isinstance(result, Rejected):
    print(result.reason)
else:
    print(result.totals())   # per-tariff amount, or None where not computable
```

**`calculate(vessel_call)`** — the lower-level engine underneath it.
Takes a complete, trusted `VesselCall` and computes all six tariffs,
crashing loudly if a required field is missing — no "not computable"
concept. Used directly by `Parsed.tariffs` internally, by the test suite,
by the notebook, and by the CLI's `--json` mode (bypasses the parser
entirely, so the CLI is testable with no API key). **Never call it on a
`VesselCall` that came from an incomplete `Parsed` result** — §9 explains
why that specific combination can silently give a wrong number.

### Repository layout

```
config/tariffs_2024_2025.yaml   # rate schedule, extracted from the PDF, with source citations
config/assignment_mapping.yaml  # benchmark output-name adapter
tariffs/
    models.py, schedule.py, shapes.py, calculators.py, modifiers.py, engine.py, adapter.py   # v1 engine
    nlp.py       # v2 — parse_vessel_request()
    cli.py       # v3 — python -m tariffs.cli
app.py           # v3 — streamlit run app.py
tests/           # v1's five layers (SPEC.md §10) + nlp/cli tests
notebooks/exploration.ipynb   # optional, not part of the graded path
examples/sudestada.json       # sample VesselCall for --json
Dockerfile, docker-compose.yml
```

**Principle followed throughout:** anything that varies by port, band, or
tariff edition is *data* (`config/`); the mathematical mechanism is
*code* (`tariffs/`). No `if/elif` cascade over ports anywhere.

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

1. Both services are separate, correctly-named domain calculators
   (`calculators.berthing_services` and `calculators.running_of_vessel_lines`).
   Nothing in the engine chooses between them.
2. `berthing_services` (§3.8) fires on every marine service and is fully
   calculated — this is what produces the 19,639.50 figure above.
3. `running_of_vessel_lines` (§3.9) is **parsed, not calculated** (§7). It
   is gated on `VesselCall.mooring_boat_used`; if `True`, the result
   carries an explicit warning that a §3.9 charge applies but is not
   computed. Never silently omitted.
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
  at a 24-hour port, but no calendar exists to test a date against. The
  out-of-hours derivation is exact for ordinary weekdays and Saturdays,
  and can be wrong specifically on a public holiday.
- **"Stay," for reduction/surcharge eligibility, means actual time in
  port — not `chargeable_period_days`.** The book's own wording for the
  60% reduction ("entire stay does not exceed 48 hours"), the 15%
  reduction ("remaining in port for less than 12 hours"), the 35%
  reduction's "first 30 days," and the 20% long-stay surcharge's "longer
  than 30 days" all describe the vessel's actual physical presence —
  arrival to departure — a different figure from `chargeable_period_days`,
  the port dues *billing* figure that (§7.2) is itself often a proxy such
  as days alongside. This implementation computes "stay" from
  `arrival`/`departure`, independent of whatever `chargeable_period_days`
  is set to. Practical consequence: setting
  `call_purpose_bunkers_stores_water_only=True` and only changing
  `chargeable_period_days` to under 48 hours will **not** trigger the 60%
  reduction if `arrival`/`departure` still imply a longer stay — correct
  behaviour, not a bug, but easy to mistake for one.

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
The one modifier that *is* derived rather than stated here is the
out-of-hours check — Durban is a 24-hour port (§8.3), so it structurally
cannot fire there regardless of the timestamps supplied.

---

## 7. Not built / future work

Still not implemented, in any version:

- **§3.9 Running of Vessel Lines charge** — the calculator exists and
  `mooring_boat_used` is parsed, but no amount is computed, only a
  warning when the flag is `True` (§3).
- **South African public holiday calendar** — no calendar exists to test
  a date against (§5).
- **An HTTP/API layer** — only the CLI and Streamlit UI exist (§9); no
  FastAPI endpoint yet.
- **Towage's flat late-arrival fee and the marine services incentive** —
  need data (minutes late/tug count; shipping-line call counts)
  `VesselCall` doesn't carry. Reported as unsupported, never silently
  computed.
- **PLO duties and the small-vessel port dues minimum** — captured in
  config with provenance, wired into no calculator (out of scope for a
  commercial vessel call).
- **External enrichment** (AIS, registries, port-call history) to
  resolve currently-unresolvable flags automatically.
- **Interactive resolution** of fields the parser leaves unresolved —
  the case that would justify introducing LangGraph (§8).

---

## 8. v2: Natural-language parsing layer

`parse_vessel_request()` (§1) turns free text into a `Parsed` or a
`Rejected`. `Parsed.call` can be fed into `calculate()` for the full
engine trace if the request was complete — the v1 engine itself is
untouched by any of this.

### Two categories of failure — only one is an exception

- **A bad request is a normal outcome (`Rejected`), never raised.** Three
  cases: **off-topic** text (reason states what the tool does, with an
  example); a **port outside the book's eight** (named explicitly — never
  a silent fall-through to an "Other" column); or missing the **hard
  floor**, `port`/`gross_tonnage`, without which nothing can be computed.
  `Rejected.parsed_so_far` keeps whatever *was* extracted;
  `missing_fields` names what wasn't.
- **A broken program still raises.** An unreachable API, a malformed
  response, or — importantly — **a validation error on a field the model
  did populate** (a stated GT that's negative) are never caught. Only a
  field's *absence* becomes a `Rejected`/"not computable" outcome; its
  *invalidity* is always an exception.

### Incomplete is not rejected — it's partial

A request with only `port` and `gross_tonnage` is `Parsed`, not
`Rejected` — light dues and VTS need nothing more. `Parsed.tariffs`
reports each tariff's own dependency:

| Tariffs | Also need |
|---|---|
| light dues, VTS | nothing beyond port + GT |
| pilotage, towage, berthing | number of operations |
| port dues | chargeable period |

A missing dependency is reported `computed=False` with a reason —
**never an assumed value, never zero.** `number_of_operations` is never
defaulted to 2 (the reference case's own figure, not a rule).

### The extraction contract

- **Extraction, not inference.** A field is populated only if the text
  states it explicitly; nothing is calculated — most importantly, a
  duration (`chargeable_period_days`, `days_in_sa_waters`) is never
  derived from two dates.
- **Evidence per field.** Every populated field carries the verbatim
  text fragment it came from (`Parsed.evidence` / `Rejected.parsed_so_far`)
  — the check that a value was read, not invented.
- **Validation is a hard error, but only for populated fields.**
  Converting the draft into a real `VesselCall` runs full Pydantic
  validation, including constraints added to `VesselCall` for this
  purpose (`gross_tonnage > 0`, counts `>= 0`, durations `>= 0`). A
  failure raises and is never caught. Missing *required* fields are
  checked *before* this step and become `Rejected` instead — so "missing"
  and "invalid" are never the same outcome.
- **The schema is generated from `VesselCall`**, not hand-duplicated
  (`_build_extraction_schema()` walks `VesselCall.model_fields`), so it
  can't drift out of sync. Two fixed fields with no `VesselCall`
  counterpart — `off_topic`, `unrecognized_port` — exist purely to make
  the rejection cases above distinguishable from an ordinary unpopulated
  field.

### Why an LLM for parsing, not for calculation

Extraction is language work — identifying which of ~25 possible facts a
request states, in whatever phrasing was used. Calculation is
deterministic and must be exactly, auditably reproducible every time.
Keeping them separate also gives the right failure mode: a fact absent
from the request comes back *absent*, not guessed.

### Why not LangGraph

One call in, one call out — no branching, no loop, no state to justify a
graph. `parse_vessel_request()` is a stateless pure function specifically
so it *can* become a graph node later without changing its contract.
What would justify it: **interactive resolution** of fields left `None`
(a loop with state — which fields are still open) or **external
enrichment** (AIS/registries, a second step with its own failure modes)
(§7) — both multi-step, conditional flows a single function isn't.

### Two timestamp decisions

1. **Out-of-hours surcharge** — `arrival`/`departure` are proxies for the
   actual service time, recorded in the trace as **derived-by-proxy, not
   asserted**. The vessel may have waited at anchorage, so arrival only
   approximates the true inbound service time.
2. **Port dues chargeable period** — days alongside is used (§2, §4);
   entrance-to-entrance is `chargeable_period_basis`'s other value,
   supplied instead whenever real entrance timestamps exist. Not a
   config toggle — a different *value* for the same field.

---

## 9. v3: Packaging and delivery

Wrapping only — `tariffs/cli.py`, `app.py`, `Dockerfile`,
`docker-compose.yml`. The engine, calculators, modifiers, and parsing
layer are untouched.

Both `python -m tariffs.cli` and `streamlit run app.py` go through
`parse_vessel_request()` and render whichever result comes back — the
same four blocks, same order: vessel call + evidence, tariff values
(never zero for one that's not computable), trace, warnings. Neither
calls `calculate()` in its normal path. The one exception: the CLI's
`--json <file>` loads a hand-built `VesselCall` and calls `calculate()`
directly, bypassing the parser so the CLI is exercisable with no API key
(`examples/sudestada.json` reproduces the reference case exactly).

Both entry points catch broken-program exceptions at the top level only,
printing/showing one clean message — never a raw traceback, never
conflated with a `Rejected` result's calm reason.

**Known inconsistency, not yet fixed:** `calculators.py` still defaults
an unresolved marine service count to 1 for pilotage/towage/berthing
when `calculate()` is called directly (v1's original §8.2 base-case
decision) — `parse_vessel_request()` never does this; it reports those
as not computable instead. This is exactly why `calculate()` must never
be called on a `VesselCall` that came from an incomplete `Parsed` result:
`port_dues` would raise on a missing chargeable period, but
pilotage/towage/berthing would silently return a plausible-looking,
wrong number instead. Neither the CLI nor Streamlit ever does this.

**Packaging:** plain `pip install -e .` is sufficient — `langchain-anthropic`,
`streamlit`, and `pytest` are core `[project.dependencies]` alongside
`pydantic`/`pyyaml`; only notebook exploration (`pandas`, `jupyter`) is a
separate, optional `uv` group. `Dockerfile` installs with plain `pip` (no
`uv` inside the image) and runs the Streamlit app by default;
`docker-compose.yml` passes `ANTHROPIC_API_KEY` through from the
environment (or a local `.env`, read automatically) — never baked into
the image. The same image runs the test suite via
`docker compose run --rm app pytest`.

---

## 10. Data extraction verification

Roughly a hundred numbers were extracted from `Port_Tariff.pdf` into
`config/tariffs_2024_2025.yaml`; only a handful are exercised by the
reference case or the automated tests. The towage table (page 15) was
checked cell-by-cell against the source by hand — via two independent
text extractions (catching the Saldanha anomaly, §5) and a rendered page
image, both confirming every value, plus an independent check by the
repo owner. Not re-verified by any automated test — repeat this check if
the config is ever hand-edited.

---

## Notebook

`notebooks/exploration.ipynb` is optional and not part of the graded
path — the tests are. It imports and calls the package; it defines no
formulas, rate values, or logic of its own.
