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

## ~~`basis`/`rounding_mode`/`multiplicity` are free strings, not real enums~~ — fixed

Was here as an open item, confirmed on a full TNPA run
(`eval_runs/auto/20260925T175806Z_full-tnpa-linear-pipeline.md`): `port_dues`
oscillated between `basis`/`rounding` and `multiplicity` mistakes across its
whole repair budget without ever getting all three right at once, ending
`EXTRACTION_FAILED`. Same technique as `pricing_params`'s fix:
`ProposedRule.basis`/`.rounding_mode`/`.multiplicity`/`.time_rounding` now use
the real `Basis`/`RoundingMode`/`Multiplicity`/`TimeRounding` enums from
`tariffs/rules.py`, making an invalid value structurally impossible rather
than something Validate has to notice after the fact. Live-verified against
OpenAI: no strict-mode schema issue (unlike the dict-shaped fields before it).

## ~~The `unmapped`/`bundled` escape hatch during a verify-repair round~~ — fixed

Was here as an open item, confirmed live: `pilotage` and `berthing_services`
were both correctly mapped and structurally valid at one point, Verify raised
a narrow concern on each, and the repair re-extraction abandoned the whole
proposal instead of fixing it — Verify then correctly called this out on
both, but nothing had stopped it happening. `pipeline.py`'s `process_charge()`
now tracks whether a charge has ever been mapped this run (sticky, not just
checked at the moment it first flips); any later round that leaves outcome as
anything else is fed back as a HARD validation issue through the existing
repair-budget machinery, so an honest `EXTRACTION_FAILED` is possible but a
silent downgrade isn't. `graph.py` intentionally not updated — only
`pipeline.py` is actively maintained since this session's pivot to a linear
architecture.

## Map/Extract sometimes cite the book's own printed page number instead of the PDF file's page index

Found live on the first full TNPA run through `pipeline.py` after landing
native-PDF input, the page-mapping fix, and the three fixes above
(`eval_runs/auto/20260926T155113Z_full-tnpa-after-0abc.md`). This book packs
two printed pages side-by-side per physical PDF page — confirmed directly by
reading page footers with `pypdf`: PDF page 6's footer literally reads
"...11...12", PDF page 8's reads "...15...16" (a clean `printed ≈
2×pdf_index - 1` relationship, consistent everywhere checked). The
page-mapping fix (`extraction/prompts.py`'s `_page_mapping_note`) tells the
model explicitly "attachment page N = book page M" using M = the real PDF
file index — but when the model can also see a page number visually printed
on the page image itself, it sometimes reports *that* number instead,
ignoring the instruction.

**Confirmed live, not just theorized:** in that run, `vts`'s assembled
context was `pages=[3, 11, 21, 24]` and `towage`'s was
`pages=[3, 12, 15, 16, 17, 18]`. VTS's real content is at PDF page 6 (printed
11) — a standalone test against PDF page 6 directly, earlier the same
session, got a clean, correct `mapped` result. In the full run, VTS's citied
"11" got fed straight into `extract_pdf_pages(pdf_path, [11, ...])`, which
sliced actual PDF page 11 (printed 21/22) — completely unrelated content —
and the charge came back `not_present`, which Verify then correctly flagged
as wrong. Towage's cited pages (15-18) are the *printed* numbers for its real
location (PDF pages 8-9); read as PDF file indices they select printed pages
29-36 instead, and towage ended `EXTRACTION_FAILED` after repeatedly failing
to produce a valid structure from the wrong content. Not universal, though:
`light_dues`'s and `port_dues`'s context pages in the same run were correct,
plausible PDF file indices — this is inconsistent model behavior, not a
deterministic rule, which makes it harder to guard against with a prompt
tweak alone. `pilotage`'s context (`[3, 12, 13, 14]`, PDF pages 12-14 contain
"Section 4, Clause 4.2" language — port_dues territory, not pilotage) and its
`SYSTEM_ERROR` (a `PricingShapes` validation failure exhausting
`structured_call()`'s retries) look plausibly related but weren't
independently confirmed the same way.

**To fix:** the most promising angle is a deterministic code-level check, not
a stronger prompt (prompts alone haven't been reliable against competing
visual evidence): `map_document()`'s `_call()` already knows the true
`(start, end)` PDF-index range it gave the model for that window — any
`WindowSection.page` reported outside that range is provably wrong (whether
from this cause or a hallucination) and could be flagged, clamped, or
dropped before it ever reaches Assemble, rather than trusting the model's
self-report the way `map_document()` already refuses to trust its
`window_start_page`/`window_end_page` echo.

## Other content-quality gaps surfaced by the same run — not investigated further

- `light_dues`: proposal used a flat per-gross-tonnage rate instead of the
  source's "per 100 tons or part thereof" unit, and didn't apply the page's
  stated 15% VAT — the latter is exactly what `modifiers` (above) is for, but
  the model didn't use it here. Worth a live recheck once the page-numbering
  issue is addressed, since a wrong/irrelevant context page could equally
  explain a wrong rate structure.
- `port_dues`: proposal modeled the charge as a single flat per-call rate;
  the source specifies per-metre-of-length-overall-per-day tiers (2.82, 5.56,
  11.14, then 33.45 after 12 months) — likely the same "compositional pricing
  vocabulary gap" already named for towage's discrete per-tug table, not a
  quick fix.

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
