# Known issues — to fix later

Found live, not yet fixed. Each entry states what's wrong, where, and why it matters.

## ~~graph.py has no per-charge exception isolation~~ — fixed

Not a new bug, and not caused by today's graph.py work — this is the exact
pre-existing gap `pipeline.py` was originally built to fix (see that
module's own docstring): `node_extract()`'s `extract_all()` call has no
try/except around each charge, so one charge's structured-output parsing
failure (after exhausting `structured_call()`'s retries) propagates and
kills the entire `graph.invoke()` run, discarding every other charge's
already-good progress.

**Confirmed live** while verifying today's Pattern B port (the sticky
"can't reclassify away from mapped" guard, ported from `pipeline.py` —
see the fixed entry above): the guard's own logic ran correctly through
several rounds (a validate-repair resolved `towage`, Verify correctly
flagged 5 of 6 charges, a verify-repair round started) before the run
crashed on `pilotage`'s Durban cancellation-fee modifier hitting the same
"exactly one of adjustment_percentage/adjustment_flat_amount/raw_description"
violation seen elsewhere in this document (pilotage/light_dues SYSTEM_ERRORs
on `pipeline.py`) — a pre-existing structured-output reliability gap, not
something the guard introduced. `pipeline.py`'s own per-charge
try/except correctly isolates this same failure mode to a single
`SYSTEM_ERROR`, confirmed live the same session; `graph.py` has no
equivalent.

**Fixed**: `extract_all()` now wraps each charge's `extract_charge()` call
in its own try/except and returns `(extractions, errors)` instead of a
plain dict; `node_extract()` records `PipelineStatus.SYSTEM_ERROR` per
failed charge (and drops any stale pre-repair extraction for a charge
whose *repair* attempt raises, so it doesn't look like a live answer next
to a SYSTEM_ERROR status) instead of letting the exception propagate —
the same isolation `pipeline.py`'s `process_charge()` already had.
`build_report()` needed no changes — it already handled a missing
extraction gracefully. Covered by a mocked end-to-end graph test that
reproduces this exact scenario (one charge's extraction raising
mid-batch) and confirms the run completes with that charge alone marked
`SYSTEM_ERROR` while the others finish normally.

Also worth noting: the underlying trigger (a modifier failing "exactly
one of adjustment_percentage/adjustment_flat_amount/raw_description")
is separately addressed below — see `structured_call`'s retry-feedback
fix — so this isolation is now a safety net for whatever residual
failure remains, not the primary defense.

## ~~`structured_call` blindly retried a validation failure instead of feeding it back~~ — fixed

Root cause of the modifier "exactly one of adjustment_percentage/
adjustment_flat_amount/raw_description" failures seen throughout this
document (light_dues/towage SYSTEM_ERRORs on `pipeline.py`, the
graph.py crash above, and the general-shapes regression below) — not
three separate bugs, one mechanism showing up in three schemas. On a
`ValidationError`, `structured_call()` retried with the *exact same
messages*, hoping for a different answer by chance, never telling the
model what it got wrong. Confirmed live this session: a fast, targeted
A/B check (bypassing Map/Assemble, calling `extract_charge()` directly
against real Map-assembled context for light_dues/towage/pilotage, 2
reps each) found the model correctly reads and structures the exact
content that crashed before (Durban's 50% cancellation surcharge) most
of the time — the failure is intermittent, not a comprehension gap, and
not caused by `map_notes` (tested with notes stripped too; no
correlation with the crash either way — see the map_notes A/B findings
in this session's transcript if that needs revisiting).

**Fixed**: each retry after a `ValidationError` now appends the exact
error to the conversation before re-asking, so it's a real correction
attempt instead of a re-roll. Paired with spelling out the "exactly one
of" rule explicitly in both `EXTRACT_SYSTEM_PROMPT` and
`GENERAL_EXTRACT_SYSTEM_PROMPT` (neither said so before — the model was
left to infer it from the schema alone). **Live re-verified** on the
one case with a documented, repeatable (2/2) failure rate before today:
`extract_charge_general()` on TNPA's towage table (page 8) now succeeds
cleanly on both reps (`mapped`, 64/39 bands, 5 modifiers each, zero
validation errors) where it failed validation twice independently
before; RAK's tug-table win case re-checked too, still clean (no
regression). Covered by two new stub-based unit tests
(`test_llm.py`) confirming the retry both includes the error text and
still propagates once genuinely exhausted.

## ~~Table-of-contents mentions merged with the real section, exploding a charge's context~~ — fixed

Found live on the window-notes redesign's first full-pipeline run, confirmed
by reproducing it three times: `light_dues`' context ballooned to all 27
pages and every section number in the document. Root cause: Map, reading the
front-matter window, reported a phantom "section 6" sighting for the table
of contents merely *listing* "Section 6 Drydocks...", with no real content
behind it. `merge_sections` (correctly, per its own dedup logic — same
`section_number` is assumed to mean the same real section) merged this
phantom sighting with the *real* Section 6 heading many windows later,
unioning their window bounds into one section spanning most of the
document. `light_dues`' own DEFINITIONS section legitimately references
"Section 6" in its text, and reference-resolution pulled this corrupted,
artificially huge section straight into `light_dues`' context.

Fixed at the source: `MAP_SYSTEM_PROMPT` now says explicitly that a
table-of-contents or index mention naming a section is not a sighting of
that section — only report one when its actual heading and content are on
the attached pages. Live-verified against the exact reproducing conditions:
`light_dues`' context dropped from all 27 pages to 11.

**A smaller residual remains, accepted rather than fixed further**: DEFINITIONS'
own generic cross-reference to "Section 6" still resolves to the real (now
correctly-bounded) Drydocks section and pulls its pages into `light_dues`'
context — the reference-following feature working as designed, not
corruption. A defensible, bounded case of this codebase's own "flag it,
cheap to over-include" bias, not the unbounded explosion this entry
describes. Worth revisiting only if it turns out to meaningfully hurt
extraction quality in practice.

## Five Verify disagreements found on TNPA's first crash-free full run — not schema failures, a different capability gap

With the retry-feedback and per-charge isolation fixes in, a full
`pipeline.py` run through TNPA came back with all 6 charges `mapped`,
zero `SYSTEM_ERROR`, zero `EXTRACTION_FAILED` — the first time this
session every charge cleared structurally. Verify still found 5 material,
unresolved disagreements though — none of them a schema-validation
failure; each is either an incomplete transcription or a misread value.
Grouped by what's actually wrong, with a potential fix noted for each
group (not built yet):

**A. Block-rate billing unit lost (`light_dues`, `berthing_services`).**
Both proposals charge "per gross ton" when the source states a rate per
a *block* of the basis — "R117.08 per 100 tons or part thereof" — the
same shape as the rounding-unit concept this session already added for
partial-unit billing, just not recognised here. Likely cause: the model
reads "per 100 tons" and infers a per-unit rate (dividing by 100) instead
of `rate=117.08` with `rounding_mode=ceil_to_unit, rounding_unit=100`.
**Potential fix**: extend `EXTRACT_SYSTEM_PROMPT`'s existing
partial-unit-rounding paragraph with an explicit example of a rate
quoted *per block* of the basis (not just "or part thereof" as a
rounding trigger, but "per N units" as a `rounding_unit` value in its
own right) — the two are currently one instruction, but the "per N
units" framing isn't spelled out as its own trigger.

**B. A document-wide VAT note not surfaced (`port_dues`, and likely others
unverified).** The book states its rates are subject to 15% VAT once, in
general terms — every charge's context includes those opening pages
(all contexts here start with pages 1-7), so this isn't a locate
problem, but nothing currently prompts the model to check for a
blanket tax/VAT statement and carry it into the proposal (as a modifier
or otherwise). **Potential fix**: add an explicit instruction to check
the general-terms pages for a document-wide tax/VAT statement and
represent it — as a `modifiers` entry, since the existing modifier
mechanism already fits "an adjustment on top of the base rate."

**C. `towage`: Richards Bay's "Above 100 000" band wrong (21.50 vs. the
source's 23.65).** The proposal appears to have carried a neighbouring
port's value into Richards Bay's cell — the same *shape* of error as the
older, already-partially-investigated Pattern D table-misread issue
below, but on a port that entry never actually checked (its own table
only covered East London/Mossel Bay/Durban/Port Elizabeth/Saldanha).
**Potential fix**: an explicit instruction not to assume adjacent ports
share a table value unless the source marks them as such (a merged
cell, "same as X") — read each port's column independently.

**D. `pilotage`: Saldanha's hourly tanker-stay duty captured as a
modifier but the amount (R886.20) dropped.** The condition was
recognised; the number wasn't carried into it — likely a `raw_description`
that paraphrased the rule instead of quoting the figure verbatim.
**Potential fix**: tighten the "verbatim quote" instruction to require
the quote include the actual number, not just describe the condition —
a `raw_description` without its figure is exactly as incomplete as
leaving the field blank.

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

## ~~Map/Extract sometimes cite the book's own printed page number instead of the PDF file's page index~~ — fixed

Was here as an open item, found on the first full TNPA run through
`pipeline.py` after landing native-PDF input and the four fixes above
(`eval_runs/auto/20260926T155113Z_full-tnpa-after-0abc.md`). This book packs
two printed pages side-by-side per physical PDF page — confirmed directly by
reading page footers with `pypdf`: PDF page 6's footer literally reads
"...11...12", PDF page 8's reads "...15...16". The page-mapping fix
(`extraction/prompts.py`'s `_page_mapping_note`) tells the model explicitly
"attachment page N = book page M" using M = the real PDF file index — but
when the model can also see a page number visually printed on the page image
itself, it sometimes reports *that* number instead, inconsistently (not
every charge, not every window).

Fixed with a deterministic check rather than a stronger prompt (prompts
alone weren't reliable against competing visual evidence):
`map_document()`'s `_call()` already knows the true `(start, end)` PDF-index
range it gave the model for that window — `extraction/map_node.py`'s
`_corrected_sections()` now treats any `WindowSection.page` outside that
range as provably wrong and splits it into two sightings at the window's own
start and end, so `merge_sections`' existing min/max union (`assemble.py`)
spans the whole window the section was actually found in, instead of
pointing `extract_pdf_pages()` at a single wrong physical page. Makes no
assumption about this book's specific numbering scheme.

**Live-verified with a clean before/after, same document, same two charges
this broke:** re-ran the full pipeline
(`eval_runs/auto/20260926T170213Z_full-tnpa-after-pagebounds.md`). `vts`
went from wrongly `not_present` to `mapped` and fully resolved clean.
`towage` went from `EXTRACTION_FAILED` (repeatedly invalid structure from
reading the wrong pages) to `mapped` with a genuine content disagreement
instead of structural garbage. `pilotage` went from a `SYSTEM_ERROR` crash to
`mapped`. Across the whole run: zero `SYSTEM_ERROR`, zero
`EXTRACTION_FAILED` — every one of the six charges reached `mapped`, for the
first time this session.

## Widening an uncertain page citation to the whole window trades precision for safety — confirmed real, not just theoretical

Direct side effect of the fix above, found on the same before/after
comparison. Correcting an out-of-range citation to span the whole window
(rather than a single page) means a charge's assembled context can include
several pages that aren't actually relevant, alongside the one that is.
`towage`'s context went from a single correct page in an earlier isolated
test (where every per-port rate matched gold exactly) to
`pages=[3, 6, 8, 9, 11, 13, 14, 15]` in the full run — page 8 (the real
table) is correctly included now, but so are seven others. In that run,
towage's per-port rates regressed to the *same* column-swap errors seen on
the very first pre-fix run months ago (Richards Bay's rate attributed to
Cape Town, Saldanha's to a different port, etc.) — plausibly the wider,
noisier context diluting the model's attention across ports/columns, though
not proven against a controlled comparison.

**To consider:** a tighter fallback than "the whole window" — e.g. clamping
to just the nearer bound (start or end, whichever the out-of-range value is
closer to) rather than always including both — would recover some
precision, at the cost of no longer being provably guaranteed to include the
real page. Not attempted; the current fix prioritizes never silently
dropping real content, which is the more serious failure mode of the two.

## A recurring "per N units or part thereof" rounding-unit gap — confirmed on four separate charges

Found on the same post-fix full run. `port_dues`, `towage`, `pilotage`, and
`berthing_services` **all** had Verify flag the same shape of mistake: the
source states a rate "per 100 tons or part thereof," but the proposal
represents it as a flat per-gross-tonnage rate, silently dropping the 100-ton
unit and the round-up-on-any-remainder rule (`RoundingMode.CEIL_TO_UNIT` with
`rounding_unit=100`, both already available fields per the enum fix above).
Four different charges hitting the identical mistake independently is too
consistent to be charge-specific noise — looks like the model isn't reliably
recognizing "per N units or part thereof" as `ceil_to_unit`, independent of
anything built this session. `berthing_services` also had a real omission of
a separate bespoke tanker-attendance charge (R1,267.83/hour at two named
ports) with nowhere obviously right to put it — a different kind of gap than
a simple surcharge `modifiers` covers.

**To consider:** `EXTRACT_SYSTEM_PROMPT` could be more explicit that "per N
[unit] or part thereof" always means `ceil_to_unit` with that N as
`rounding_unit` — worth trying cheaply, in the same spirit as the earlier
"don't extrapolate past n/a" suggestion, before considering anything more
structural. Not attempted here.

## `port_dues`: time-tiered per-metre rate doesn't fit the four pricing shapes

Confirmed on the same run: the source specifies per-metre-of-length-overall-
per-day tiers (2.82, 5.56, 11.14, then 33.45 after 12 months), but
`port_dues`'s proposal modeled it as a single flat per-call rate. Likely the
same "compositional pricing vocabulary gap" already named for towage's
discrete per-tug table — bigger, structural work, not a quick fix.

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

## Experimental general pricing vocabulary (extraction/general_shapes.py) — regression resolved, still not wired in

Built to close a real, confirmed gap: RAK Ports' towage tariff is keyed by tug
selection (Ghalilah/Hobby/.../Osprey), not any numeric basis range, so none
of the four existing fixed pricing shapes — all keyed on a continuous
numeric basis — can represent it at all (the existing path correctly comes
back `unmapped` on it, with an honest explanation, not a wrong answer).
`GeneralProposedRule`'s `KeyedBand`/`ValueFormula` (flat, or linear =
base + rate × units) generalise `banded`'s GT-only key to any labelled
dimension — a category name, a port, a GT range — without inventing a fully
recursive pricing DSL.

**Live-verified, both directions, same session:**
- **RAK's tug table — a clear win.** `extract_charge_general()` returned
  `mapped`, all 10 tugs correctly priced ($1,569–$6,516), `basis=hours`,
  6 modifiers captured, zero structured-output validation errors. This is
  exactly the case the existing shapes cannot touch, solved cleanly.
- **TNPA's towage table — a regression, twice.** The same function on a case
  the *existing* `extract_charge()` already handles reliably (this book's
  own towage table, page 8) failed structured-output validation on both
  independent attempts: some `flat`-kind bands came back missing
  `flat_amount` entirely, and `GeneralModifier`'s "exactly one of adjustment/
  adjustment_percentage/raw_description" was violated on the same cluster of
  surcharge descriptions (after-hours, additional-tug, no-power, cancellation,
  delay fee) both times — not random noise, a repeatable weak spot.

**Root cause found and fixed, separately** (see `structured_call`'s
retry-feedback entry above): both failures were `structured_call()`
blindly re-rolling a validation failure instead of feeding it back, plus
`GENERAL_EXTRACT_SYSTEM_PROMPT` never spelling out the "exactly one of"
rule or which field goes with `flat` vs. `linear`. Not a deeper
vocabulary problem — the RAK win case never even hit a validation error,
so the mechanism was never exercised there.

**Re-verified live after the fix**: TNPA's towage table (the exact
regression case, same page 8) now returns `mapped` cleanly on both reps
(64 and 39 bands, 5 modifiers each, zero validation errors) instead of
failing twice. RAK's tug table re-checked too — still a clean win, no
regression from the prompt changes.

**Still not wired into pipeline.py/graph.py.** The regression that was
blocking adoption is resolved, but that's one fix verified on one
document pair, not the same depth of live iteration the existing
`EXTRACT_SYSTEM_PROMPT` has had across this whole session. The
recommended integration path is unchanged and still not built: don't run
the general path in place of the existing one — try `extract_charge()`
first, and only retry with `extract_charge_general()` when it returns
`unmapped` specifically because the base calculation doesn't fit any of
the four shapes.
