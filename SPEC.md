# Port Tariff Calculator — Build Specification (v1)

Source document: `Port_Tariff.pdf` — Transnet National Ports Authority Tariff Book,
23rd Edition, 1 April 2024 – 31 March 2025. All section and page references below
are to the **printed page numbers in that book's footer** (your PDF viewer's page
numbers may be offset by one).

This spec is the product of a manual reconciliation of the supplied reference case
against the tariff book. **The formulas, mappings and interpretations below are
settled — do not re-derive them from the PDF.** The PDF is needed only to extract
the per-port rate tables into YAML (see §5.3).

---

## 1. Scope

### In scope for v1

- A Python package that calculates six tariffs from a structured `VesselCall` object.
- A YAML rate schedule extracted from the tariff book, with source citations.
- A test suite (four layers, see §10).
- A `README.md` (contents specified in §11).
- An exploration notebook that imports the package (see §12).

### Explicitly out of scope for v1

Do not build these. Do not stub them with `NotImplementedError` in the call path.
Do not add dependencies for them.

| Item | Status |
|---|---|
| FastAPI / any HTTP layer | v2 |
| Natural-language parsing of the vessel query (LLM call) | v2 |
| PDF ingestion or runtime RAG | Not planned |
| §3.9 Running of Vessel Lines charge | Parsed, not calculated (see §7.6) |
| South African public holiday calendar | v2 (see §8.3) |
| External enrichment (AIS, vessel registries) | Not planned |

### Design constraints this implies

The engine must expose **one clean entry point** — a function taking a `VesselCall`
and returning a result object — with no CLI, transport, logging-to-stdout or
framework concerns inside it. A FastAPI layer must be wrappable around it in v2
without refactoring the engine.

In v1 the `VesselCall` is constructed by hand (in tests and in the notebook). The
v2 parser will produce the same object, so the model must be complete enough to
carry fields v1 does not use.

---

## 2. Reference case

The task supplies one vessel with known correct answers. These six numbers are the
primary acceptance criterion.

**Vessel:** SUDESTADA, bulk carrier, Malta flag, built 2010.
**Port:** Durban.
**GT:** 51,300 · **NT:** 31,192 · **DWT:** 93,274 · **LOA:** 229.2 m
**Cargo:** Exporting iron ore, 40,000 MT
**Arrival:** 15 Nov 2024 10:12 · **Departure:** 22 Nov 2024 13:00
**Days alongside:** 3.39 (see §7.2 — the true value is 3.396)
**Number of operations:** 2

| Tariff | Expected (ZAR, ex-VAT) | Reconciles? |
|---|---|---|
| Light dues | 60,062.04 | exact |
| Port dues | 199,549.22 | exact at 3.396 days |
| Towage dues | 147,074.38 | exact |
| VTS dues | 33,315.75 | exact at GT 51,255 |
| Pilotage dues | 47,189.94 | exact |
| Running of vessel lines dues | 19,639.50 | exact, **via §3.8 not §3.9** |

### Two known input-rounding artefacts

Neither is a defect in this implementation. Both are stated in the README.

1. **VTS.** 33,315.75 ÷ 0.65 = 51,255 exactly. The answer key was computed on
   GT 51,255; the vessel sheet says 51,300. VTS is the only tariff charged on exact
   GT, so it is the only one that exposes this — every other tariff rounds up to
   units of 100 and both values give 513. Using the supplied GT 51,300 yields
   33,345.00, a deviation of +ZAR 29.25 (+0.088%).
2. **Port dues.** The answer key uses 3.396 days; the vessel sheet shows 3.39, a
   truncation of the same figure. Using 3.39 yields 199,371.35, a deviation of
   −ZAR 177.87 (−0.089%).

**Test policy:** the reference-case test asserts the exact key values, using
GT 51,255 and 3.396 days as inputs. A second test documents the deviation when the
sheet's rounded values (51,300 / 3.39) are used instead. Do not fudge the
calculators to absorb the difference.

---

## 3. Domain notes

Needed to read the spec; not needed in code.

- **GT (gross tonnage)** is a dimensionless measure of enclosed volume, not a
  weight. Five of six tariffs derive from it. NT and DWT are on the vessel sheet
  but are **not used** by any tariff in this book.
- **"Per 100 tons or part thereof"** means `ceil(GT / 100)`. GT 51,300 → 513 units.
- **"Per service"** means charged each time. An arrival plus a departure is two
  services. This is the origin of the ×2 on pilotage, towage and berthing.
- **Alongside** means physically moored at the quay. It excludes time at anchorage
  waiting for a berth, which for large bulk carriers is routinely days.
- All rates in the book are **ex-VAT** (VAT 15% is noted in every page footer).
  The answer key is ex-VAT. Do not apply VAT anywhere.

---

## 4. Repository layout

```
config/
    tariffs_2024_2025.yaml       # rate schedule, with source citations
    assignment_mapping.yaml      # benchmark output-name adapter
tariffs/
    __init__.py
    models.py                    # VesselCall, RoundingMode, results, trace
    schedule.py                  # YAML loader + Pydantic schema for the config
    shapes.py                    # the four calculator shapes (§6)
    calculators.py               # one function per tariff (§7)
    modifiers.py                 # reductions and surcharges (§9)
    engine.py                    # single entry point
    adapter.py                   # assignment output mapping (§7.6)
tests/
    test_reference_case.py
    test_schedule_structure.py
    test_monotonicity.py
    test_boundaries.py
    test_modifiers.py
notebooks/
    exploration.ipynb
README.md
pyproject.toml
```

Python 3.11+. Dependencies: `pydantic` v2, `pyyaml`, `pytest`. Nothing else in v1.
Installable with `pip install -e .`.

---

## 5. Configuration

### 5.1 Principle

**Anything that varies by port, by band, or by tariff edition is data. The
mathematical mechanism is code.** Rates, band boundaries, minimums, per-port
columns and rounding selectors live in YAML. Formulas live in Python.

Do not invent a rule-expression language in YAML. Config selects from a closed set
of named strategies; Python owns their meaning.

### 5.2 Rounding is explicit per rate

The book mixes rounding behaviours and a wrong default silently shifts results.
Define as a Pydantic enum so an unknown string fails at load time, not at runtime:

```python
class RoundingMode(str, Enum):
    EXACT          = "exact"            # use GT as-is (VTS)
    CEIL_PER_100_T = "ceil_per_100_t"   # ceil(GT/100) (everything else)
    PRO_RATA_TIME  = "pro_rata_time"    # fractional days, no rounding (port dues)
```

### 5.3 Extraction instruction

For each tariff below, this spec gives the **Durban column fully worked and
verified against the answer key**. Extract the remaining ports from the PDF into
the identical schema.

Column header order matters and is the most likely source of error. The headers
are given per tariff in §7. Read them carefully: **not every port has its own
column.** Durban has a column in pilotage and towage but falls under "Other Ports"
in berthing and in running of lines. East London has a column in towage but not in
pilotage.

Where the book prints `n/a` for a port/band combination, write an explicit `null`
in the YAML with a comment. A missing key and an unavailable combination are
different states and the structural test distinguishes them.

Every rate block carries provenance:

```yaml
source: {section: "3.6", page: 15}
```

### 5.4 Band interval semantics

The printed towage table overlaps at band edges: it shows `2 001 to 10 000`
followed by `10 000 to 50 000`. A vessel at exactly 10,000 GT appears in both rows.
This is in the source, not an extraction error, and no reference value resolves it.

**Convention: lower bound exclusive, upper bound inclusive.** Encode it explicitly
rather than relying on a `floor_gt` field to imply it:

```yaml
- {min_gt_exclusive: 2000,  max_gt_inclusive: 10000, base: 12633.99, increment_above_gt: 2000,  per_100t: 268.99}
```

So GT 10,000 falls in the 2,001–10,000 band. State this convention in the README.

---

## 6. The four calculator shapes

All six tariffs reduce to these. Implement each once in `shapes.py`, parameterised
from config. Do not write six independent formulas, and do not write an `if/elif`
cascade over ports.

| Shape | Formula | Used by |
|---|---|---|
| `per_unit_rate` | `units × rate`, then apply minimum | Light dues, VTS |
| `base_plus_increment` | `base + units × rate` | Pilotage, Berthing |
| `banded_base_plus_increment` | `band.base + ceil((GT − band.increment_above_gt)/100) × band.per_100t` | Towage |
| `base_plus_increment_times_duration` | `units × basic + units × daily × days` | Port dues |

`units` is derived from GT by the rate's `RoundingMode`.

---

## 7. The six tariffs

### 7.1 Light dues — §1.1.1, page 09

Shape: `per_unit_rate`. **Not** per service — charged once per South African visit.

Two rates on this page. Read them carefully:

- **24.64 per metre of LOA per financial year** — applies to self-propelled vessels
  *at their registered port*, and to vessels licensed by the Department of
  Environmental Affairs and Tourism. This is the annual rate for locally registered
  vessels, charged on length.
- **117.08 per 100 tons or part thereof** — "All other vessels". This is the one
  that applies to a foreign-flagged vessel calling at an SA port.

Durban / SUDESTADA: `513 × 117.08 = 60,062.04` ✓

Conditions on this page that the engine must model but which do not fire here:

- The single payment covers the whole SA coastal itinerary provided the vessel does
  not pass beyond the SA coastline and does not exceed **60 days** in SA waters.
  Past 60 days the vessel is billed monthly as coastal.
- **Bona fide coaster** status (see §9.1) triggers monthly billing — but a coaster
  arriving from a foreign port pays full light dues at the first SA port anyway, so
  the calculation is unchanged in that case.
- Exemptions: SAPS, SANDF, SAMSA, SA medical/research, non-self-propelled small and
  pleasure vessels not used for gain, vessels remaining at anchorage outside the
  port (unless at a single buoy mooring or similar).

### 7.2 Port dues — §4.1.1, page 21

Shape: `base_plus_increment_times_duration`. Not per service.

```
basic       = ceil(GT/100) × 192.73
incremental = ceil(GT/100) × 57.79 × chargeable_period_days
total       = basic + incremental
```

Durban / SUDESTADA: `98,870.49 + (29,646.27 × 3.396) = 199,549.22` ✓

**The chargeable period.** The book defines it as from passing the entrance inwards
until passing the entrance outwards, with part-periods pro rata. No entrance
timestamps were supplied. Arrival-to-departure is 7.117 days and yields 309,853 —
far from the key. The key uses alongside time (3.396 days).

The likely explanation is that the arrival timestamp is arrival at the port limits
or anchorage, not at the entrance, so the ~3.7-day difference is time at anchor,
which is correctly excluded. Alongside time therefore approximates the chargeable
period, understating it only by the inbound and outbound transit.

**Implementation:** the model field is `chargeable_period_days`, with a
`chargeable_period_basis` enum recording where it came from
(`entrance_to_entrance` | `days_alongside_proxy`). If entrance timestamps are ever
supplied they take precedence. Do not name the field `days_alongside`.

Reductions and the long-stay surcharge attach to this tariff — see §9.
The 20% long-stay surcharge applies to the **incremental component only**, so keep
the two components separate in the result trace.

Also on this page: a minimum fee of 470.98 for small and pleasure vessels visiting
a port other than their registered port. Out of scope for a commercial vessel but
include it in config.

### 7.3 Towage dues — §3.6, page 15

Titled "Tugs/Vessel assistance and/or attendance" in the book. Shape:
`banded_base_plus_increment`. **Per service** (×2 here).

Column headers, in order:
`Richards Bay | Durban | East London | Port Elizabeth/Ngqura | Mossel Bay | Cape Town | Saldanha`

Durban column, verified:

```yaml
Durban:
  bands:
    - {min_gt_exclusive: 0,      max_gt_inclusive: 2000,   base:  8140.00, increment_above_gt: null,   per_100t: null}
    - {min_gt_exclusive: 2000,   max_gt_inclusive: 10000,  base: 12633.99, increment_above_gt: 2000,   per_100t: 268.99}
    - {min_gt_exclusive: 10000,  max_gt_inclusive: 50000,  base: 38494.51, increment_above_gt: 10000,  per_100t:  84.95}
    - {min_gt_exclusive: 50000,  max_gt_inclusive: 100000, base: 73118.07, increment_above_gt: 50000,  per_100t:  32.24}
    - {min_gt_exclusive: 100000, max_gt_inclusive: null,   base: 93548.13, increment_above_gt: 100000, per_100t:  23.65}
```

Durban / SUDESTADA: GT 51,300 → band 4. `ceil(1300/100) = 13`.
`73,118.07 + 13 × 32.24 = 73,537.19` per service. `× 2 = 147,074.38` ✓

**Do not multiply by the craft allocation.** The table immediately above the fee
table (page 15) allocates a maximum number of tugs by vessel size — 3 craft for
50,001–100,000 GT. It is operational, not a multiplier: the fee table already
prices the whole job by tonnage. The answer key confirms no ×3. Its actual role in
the calculation is to define the threshold for the "additional tug" surcharge.

Encode the allocation table in config (same interval semantics; it also overlaps at
2,000) and use it only for that surcharge test.

Towage surcharges — see §9.3. East London has no band above 100,000 and Mossel Bay
none above 50,000; the book prints `n/a`. Write explicit nulls.

### 7.4 VTS dues — §2.1.1, page 11

Shape: `per_unit_rate` with `RoundingMode.EXACT`. Not per service — per port call.

- Durban and Saldanha: **0.65 per GT**
- All other ports: **0.54 per GT**
- Minimum fee: **235.52**

Durban / SUDESTADA: `51,255 × 0.65 = 33,315.75` ✓ (see §2 on the GT discrepancy)

This is the only tariff charged on exact GT. Do not apply `ceil(GT/100)` here.

Exemptions: SAPS, SANDF, SAMSA, SA medical/research, vessels returning from
anchorage at the Harbour Master's order, and small/pleasure vessels under §4.2.

### 7.5 Pilotage dues — §3.3, page 13

Shape: `base_plus_increment`. **Per service** (×2 here).

Column headers, in order:
`Richards Bay | Durban | Port Elizabeth/Ngqura | Cape Town | Saldanha | Other`

Note East London does **not** have a column and falls under "Other".

Durban, verified: `base_fee: 18608.61`, `per_100t: 9.72`.

Durban / SUDESTADA: `(18,608.61 + 513 × 9.72) × 2 = 47,189.94` ✓

Compulsory at all eight commercial ports.

**Surcharges (all 50%, all event-driven, none derivable from the vessel sheet):**
service terminating or commencing outside ordinary working hours; vessel not ready
30 minutes after notified time or 30 minutes after the pilot boarded; cancellation
within 30 minutes of notified time with the pilot not yet boarded. Durban only: a
60-minute cancellation window.

Note the out-of-hours trigger cannot fire at Durban (24-hour service, §8.3).

**PLO duties** (Port Liaison Officer, a pilot remaining aboard during the stay):
886.20 per hour, **Saldanha and tankers only**. Structurally out of scope here;
include in config with its port and vessel-type conditions.

Exemptions: SAPS and SANDF, and only when pilotage is not requested.

**Do not conflate with §3.5**, Pilotage Exemption Certificates. That is a separate
annual licence a company buys so its own masters may pilot, priced on LOA. It is
not a discount on pilotage dues. Out of scope for v1; do not model it.

### 7.6 "Running of vessel lines" dues — §3.8 Berthing Services, page 18

**This is the semantic mismatch. Read this section carefully.**

The assignment asks for "running of vessel lines dues". The tariff book has a
section with exactly that title, §3.9 on page 19. **The answer key does not come
from it.**

- §3.9 "Running of Vessel Lines", Other Ports: 1,654.56 per service → 3,309.12 for
  two services. Does not match.
- §3.8 "Berthing Services", Other Ports: `(2,801.91 + 513 × 13.68) × 2 =
  19,639.50` ✓ exact match.

**What the two services actually are.** §3.8 is the shore mooring gang who take the
lines and make them fast to bollards — charged on essentially every berthing and
unberthing. §3.9 is narrower: a launch or mooring boat used to carry the lines from
ship to bollard across the water, used where the gang cannot take them directly.
They are **additive, not alternatives**: when a mooring boat is used, both are
billed.

**Implementation.**

1. The domain model keeps both services correctly named and both calculators
   implemented. Nothing in the engine chooses between them.
2. Berthing (§3.8) fires on every marine service. Shape `base_plus_increment`,
   per service.
3. Running of lines (§3.9) is gated on a `mooring_boat_used` flag. **In v1 the flag
   is parsed and carried but the charge is not calculated.** If the flag is set
   true, the result must carry a warning: a §3.9 charge applies but is not
   calculated in this version. Do not silently omit it.
4. A thin **adapter** (`config/assignment_mapping.yaml` + `adapter.py`) maps the
   assignment's output slot names onto domain results. The slot named
   `running_of_vessel_lines` is populated by the berthing figure, with a note
   emitted **in the output object**, not only in the README.

```yaml
assignment_outputs:
  running_of_vessel_lines:
    calculator: berthing_services
    note: >
      The supplied benchmark value of ZAR 19,639.50 reconciles exactly to
      Tariff Book §3.8 Berthing Services (Other Ports), not to §3.9 Running of
      Vessel Lines, which would give ZAR 3,309.12 for two services. The benchmark
      figure is reported here; both sections are implemented separately in the
      domain model.
```

The adapter must never suppress §3.9. It is a naming layer only.

Berthing column headers, in order:
`Richards Bay | Port Elizabeth/Ngqura | Cape Town | Saldanha | Other Ports`
(Durban → Other Ports. Verified: `base_fee: 2801.91`, `per_100t: 13.68`.)

Running-of-lines column headers, in order:
`Port Elizabeth/Ngqura | Cape Town | Saldanha | Other Ports`
(Durban → Other Ports, 1,654.56 per service.)

---

## 8. The VesselCall model

### 8.1 Fields

```python
class VesselCall(BaseModel):
    # identity and dimensions
    vessel_name: str | None = None
    port: Port                                  # enum of the eight ports
    gross_tonnage: float
    length_overall_m: float | None = None
    vessel_type: VesselType | None = None       # bulk_carrier, tanker, passenger, ...

    # timing
    arrival: datetime | None = None
    departure: datetime | None = None
    chargeable_period_days: float | None = None
    chargeable_period_basis: PeriodBasis | None = None

    # services
    number_of_operations: int | None = None
    marine_service_count: int | None = None     # derived; see 8.2

    # tri-state modifier flags — None means "not stated"
    engaged_in_cargo_working: bool | None = None
    is_bona_fide_coaster: bool | None = None
    is_passenger_vessel: bool | None = None
    is_first_sa_port_call: bool | None = None
    days_in_sa_waters: float | None = None
    call_purpose_bunkers_stores_water_only: bool | None = None
    hull_certification: list[HullCert] = []     # double_hull, segregated_ballast, green_award
    exemption_status: ExemptionStatus | None = None   # saps, sandf, samsa, medical_research
    self_propelled: bool | None = None

    # event flags — not derivable from a vessel sheet
    mooring_boat_used: bool | None = None       # §3.9, v1: warn only
    additional_tug_requested: bool | None = None
    vessel_without_own_power: bool | None = None
    service_cancelled_after_standby: bool | None = None
    late_against_notified_time: bool | None = None
```

### 8.2 Resolution policy

**Default to the unmodified published tariff.** No reductions, no surcharges, unless
the input supports them. State it in exactly those words in the README — not as
"safest", which begs the question of safe for whom.

Three-tier resolution, applied in order:

1. **Derived** — computed from other supplied fields. `marine_service_count` from
   `number_of_operations`; `days_in_sa_waters` from arrival/departure;
   out-of-hours from timestamps against the port schedule.
2. **Stated** — explicitly supplied.
3. **Unresolved (`None`)** → base case, and the assumption is recorded in the trace.

`None` must never be coerced to `False` silently. The trace distinguishes
"stated false" from "not stated, treated as base case".

**On `number_of_operations`:** the vessel sheet says "Number of Operations: 2",
which is not literally "number of marine services". The equivalence is inferred
from the answer key (pilotage, towage and berthing all match only when doubled).
Normalise it explicitly — keep the raw field, derive `marine_service_count`, and
record the derivation as a benchmark assumption. Do not treat every future
"operation" as a marine movement without that note.

**On bona fide coaster:** the book defines it as carrying cargo exclusively between
SA ports on a regular schedule, subject to approval by application. Flag state is
**not** a criterion — a foreign-flagged vessel could in principle hold the status.
Do not derive `False` from a foreign flag. Leave it `None` → base case.

### 8.3 Ordinary working hours — §3.1, page 12

Model as a **weekly schedule per port**. Days not listed mean zero ordinary hours.

| Port | Ordinary working hours |
|---|---|
| Mossel Bay | Mon–Fri 06:00–18:00 |
| East London | Mon–Fri 06:00–22:00; Sat 06:00–12:00 |
| Richards Bay, Durban, Ngqura, Port Elizabeth, Cape Town, Saldanha | 00:01–24:00, all days |

Consequences to encode, not to special-case:

- At the six 24-hour ports the out-of-hours surcharge **cannot fire**, including at
  weekends, because there is no time outside ordinary hours.
- At East London, Sunday is not listed, so all of Sunday is outside ordinary hours
  and the surcharge does fire.
- The surcharge clause reads "outside ordinary working hours on weekdays and
  Saturdays or on Sundays and public holidays". The day list describes *when* this
  can occur; the trigger is the hours, not the day. Do not implement day-of-week as
  an independent trigger.
- **Public holidays are not implemented in v1.** The 24-hour ports state that
  marine operations are available "on special request" on public holidays, which
  hints that a holiday may sit outside ordinary hours even at Durban, but the book
  does not say so. Leave the out-of-hours flag `None` when the timestamp falls on a
  date the calendar cannot classify, and document the gap.
- The surcharge triggers on when the **service** starts or ends, not when the vessel
  arrives or departs. Vessel timestamps are a proxy. Record the flag as derived,
  not asserted.

---

## 9. Modifiers

Parameters and applicability metadata in config; evaluation in Python. Each entry
names the tariffs it touches.

### 9.1 Port dues reductions — §4.1.1, pages 21–22

| Reduction | Condition |
|---|---|
| 35% | Not engaged in cargo working, **first 30 days only**; OR bona fide coaster; OR passenger vessel; OR small vessel under §4.2 visiting away from its registered port |
| 60% | Call solely for bunkers and/or stores and/or water, **and** total stay ≤ 48 hours |
| 10% | Liquid bulk tankers only: certified double hull, segregated ballast tanks, or Green Award. Capped at 10% for any one or any combination |
| 15% | Stay under 12 hours |

**Stacking rules:**

- The four conditions inside the 35% group are alternatives, not cumulative. Any one
  qualifies; the reduction is 35% once.
- The book states the 60% "will not be enjoyed in addition to" the 35%. It does not
  name a winner. **Apply the 60% and drop the 35%** — it is the narrower, more
  specific condition and the larger reduction. Record this as an interpretation in
  the README. In practice they rarely co-occur, since a bunkers-only call is
  already not cargo working.
- The 10% is tanker-only and never applies to a bulk carrier. Note that "liquid bulk
  tanker" and "dry bulk carrier" are different vessel classes despite the similar
  names.
- The 15% is described as "in addition to other reductions that may be enjoyed".
  **Apply it multiplicatively to the already-reduced figure**, not to the base:
  35% then 15% gives `0.65 × 0.85 = 0.5525`, not a flat 50%. Record as an
  interpretation — no reference value confirms it.

### 9.2 Port dues surcharge

20% on the **incremental component only** for vessels in port longer than 30 days
that are neither engaged in cargo working nor undergoing repairs.

### 9.3 Towage surcharges — §3.6, page 15

| Surcharge | Condition | Derivable from vessel sheet? |
|---|---|---|
| 25% | Service commencing or terminating outside ordinary working hours | **Yes** — from timestamps + port schedule |
| 50% per tug | A tug provided beyond the craft allocation, at the master's request or the Harbour Master's order | No |
| 50% | Vessel serviced without her own power (100% if an extra tug is also requested for her) | No |
| 25% (as if performed) | Standby cancelled after standby commenced | No |
| 8,050.76 per tug per half hour (Saldanha: 10,152.19) | Vessel 30+ minutes late against notified time. A flat charge, not a percentage | No |

Implement all five. Only the first is derived from input; the rest read explicit
flags defaulting to `None` → not applied.

Note the only ports where the out-of-hours surcharge can ever fire are Mossel Bay
and East London.

### 9.4 Marine services incentive — §3.2, page 12

A volume discount per shipping line, based on national call counts, applying to
pilotage, craft assistance and berthing services. The input supplies no line
identity or call count.

**Do not claim it does not apply** — say it is not supported by the supplied input
and therefore not applied. Include the thresholds in config for completeness.

---

## 10. Tests

Four layers. The first is the only one with an external source of truth; the others
guard the extraction.

### 10.1 `test_reference_case.py`

All six values to the cent, from the reference `VesselCall`. Plus the documented-
deviation test using the sheet's rounded GT and days.

These six numbers come from outside the system. **They are not to be adjusted.**

### 10.2 `test_schedule_structure.py`

Validates the config's integrity, not its values:

- Every port referenced by the `Port` enum has an entry in every tariff that is
  port-specific.
- Band lists are ordered and contiguous under the exclusive/inclusive convention:
  each band's `min_gt_exclusive` equals the previous band's `max_gt_inclusive`.
- The final band in each list has `max_gt_inclusive: null`, or is explicitly null
  if the port has no band at that size.
- `n/a` combinations are explicit `null`, never missing keys.
- Every rate block carries a `source` with a section and page.
- Every `rounding` value parses to the enum.

### 10.3 `test_monotonicity.py`

Economic sanity checks that catch shifted-cell transcription errors:

- Within a port, band base fees increase across bands.
- Within a port, `per_100t` increments **decrease** across bands.

Both hold across all seven ports in the towage table. A value copied from the wrong
row or column usually breaks one of them. This will not catch a digit transposition
inside a plausible range — hence §10.5.

### 10.4 `test_boundaries.py`

GT exactly at each band edge, asserting the exclusive/inclusive convention. Cover
2,000 / 10,000 / 50,000 / 100,000 for towage. Also the VTS minimum fee and the
small-vessel port dues minimum.

### 10.5 Manual verification (not automated)

Roughly a hundred numbers are extracted from the PDF and only a handful are
exercised by the reference case. After the build, the towage table on page 15 must
be checked cell by cell against the source by hand. Note this obligation in the
README.

---

## 11. README contents

Required sections:

1. **What it does** and how to install and run it.
2. **Reference case results** — the six values, matched.
3. **The §3.8 / §3.9 mapping** — the full explanation from §7.6 above, with both
   figures shown. This is the most important item in the README.
4. **Known deviations** — the two input-rounding artefacts from §2, quantified.
5. **Interpretations** — decisions made where the book is silent or ambiguous:
   - Port dues chargeable period: entrance-to-entrance is the rule; days alongside
     is used as the closest available proxy; what that omits.
   - Band interval convention (lower exclusive, upper inclusive) and the printed
     overlap it resolves.
   - 60% takes precedence over 35%.
   - 15% applied multiplicatively.
   - `number_of_operations` read as marine service count.
6. **Assumptions** — the base-case policy, stated as: *default to the unmodified
   published tariff; no reduction or surcharge is applied unless supported by the
   supplied input.* List which flags were unresolved for the reference case.
7. **Not implemented in v1** — §3.9 charge, public holidays, NL parsing, API.
8. **Outputs are ex-VAT.**
9. **Production extensions** (brief): LLM parsing layer, FastAPI endpoint, external
   enrichment from AIS/registries/port-call history for unresolved flags.

Keep the deviations and the mapping factual and short. Do not frame the submission
as a critique of the benchmark.

---

## 12. Notebook

`notebooks/exploration.ipynb` is a **consumer** of the package. No formulas, no rate
values, no logic defined in cells.

```python
%load_ext autoreload
%autoreload 2

from tariffs.engine import calculate
from tariffs.models import VesselCall

call = VesselCall(port="Durban", gross_tonnage=51255, ...)
result = calculate(call)
result.trace_df()
```

The result object must expose a **trace**: one row per calculation step, with the
tariff, the section reference, the inputs used, the rounding applied, any modifier
considered and how it resolved, and the subtotal. This is what makes the notebook
useful for verification rather than just a call site, and it is also what a reviewer
reads to confirm the engine is doing what it claims.

The notebook is not part of the graded path — reviewers run the tests. Mention it in
the README as optional.
