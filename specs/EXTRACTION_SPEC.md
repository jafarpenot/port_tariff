# Tariff Extraction Pipeline — Specification

This **replaces** the earlier extraction agent spec entirely. Discard its
architecture.

The pipeline reads a port tariff PDF and **proposes** a rate schedule for the
existing calculator, for human approval. The calculator is extended, not rewritten.

Read in full before writing code. It records decisions already made. Where
something is left to your judgment, it says so. Work stage by stage (§10) and stop
at each checkpoint.

---

## 1. Purpose and position

The calculator computes tariffs from a hand-extracted, hand-verified YAML config.
It won't adapt to a new tariff book without manual rework. This pipeline automates
the extraction, but **does not act autonomously**: its output is a proposal a human
approves before any config is written.

Two reasons, both to be stated in the docs:

1. An extraction model can be wrong, and it cannot be accountable. Someone must
   sign off rates that end up on invoices.
2. Some errors can't be found by reading the document. In the TNPA reference
   case, the answer key's "running of vessel lines" value reconciles to §3.8
   Berthing Services, not §3.9 Running of Vessel Lines. Nothing in the PDF reveals
   that; only reconciliation against known-correct values did.

The product claim: days of manual transcription become a reviewable proposal
someone signs off in minutes.

---

## 2. Design principle

**A known path is a workflow. An unknown path is an agent.**

Reading a document completely is a known path: read every page. That's a
deterministic map-reduce, complete by construction, with no agent deciding what is
worth reading. Hunting for what is wrong with a proposed extraction is an unknown
path: form hypotheses, search, follow references, compare. That's the one place a
ReAct agent is justified.

**Freedom inside nodes, control on the edges.** Whatever an LLM does inside a node,
the decisions that must be guaranteed — is the output valid, is the run sound, is it
approved — are made by Python or by a human, never by a model's self-assessment.

---

## 3. Scope contract

State this in the docs in one line: *the pipeline adapts to new values and new
combinations of the engine's approved calculation stages; it never creates
calculation logic, and anything it cannot represent is escalated for review.*

### 3.1 Charge types

The same six as the calculator, defined **by function, not name** — other
authorities call the same charge differently ("harbour dues" for port dues).

| Canonical type | What it pays for |
|---|---|
| Light dues | National navigation aids (lighthouses, buoys). Usually once per visit to the country, on tonnage. |
| Port dues | Occupying the port. Tonnage-based, usually with a time component. |
| Towage | Tug assistance for manoeuvring, per service. |
| VTS | Vessel traffic service (harbour radar/radio control), per call. |
| Pilotage | A licensed pilot conning the vessel in or out, per service. |
| Berthing | Shore mooring gang making the vessel fast / letting go, per service. |

### 3.2 Outcomes

**Semantic outcomes — emitted by Extract, which owns them:**

| Outcome | Meaning |
|---|---|
| Mapped | Represented with approved stages, with provenance. |
| Bundled | Charged, but included in another charge. Record `included_in: <type>`. Not the same as absent: must never be read as free. |
| Not present | No such charge in this document. A valid outcome; do not force a match. |
| Unmapped | The charge exists and was understood, but its logic cannot be expressed with the approved stages. Quote the source text. |

**Pipeline statuses — set by the workflow, never by a model:**

| Status | Meaning |
|---|---|
| Extraction failed | The model could not produce a valid extraction within the retry budget. Different from Unmapped: "we couldn't read it reliably", not "we read it and the engine can't express it". |
| System error | The application itself failed. See §6.6. |

### 3.3 Everything else in the document

Charge sections outside the six are detected and listed as **out of scope** in the
report. Not extracted. Tariff books contain many irrelevant charges (training
courses, equipment servicing, licences). Listing them shows they were seen, and
makes a future expansion a change to the canonical list, not a redesign.

### 3.4 Hard rules

- No model ever writes Python or modifies calculation logic to make an extraction
  fit.
- The pipeline **proposes, it does not write**. Config is written only after
  approval.

---

## 4. Prerequisite: generalise the rule representation

Stage 1 of the build, done before any pipeline code. The pipeline can only handle
variation expressed as parameters.

Restructure the current "shapes" into **fixed stages**, each with a **closed enum**
of allowed options:

```
basis → rounding → pricing → multiplicity → time → min/max → modifiers
```

Things currently hardcoded that must become parameters:

- **Basis:** what the rate is charged on — GT, NT, LOA, DWT, cargo tonnes, hours.
- **Rounding:** unit and direction. `ceil_per_100_t` hardcodes the 100; other books
  round to 10 or 50. Something like `{mode: ceil_to_unit, unit: 100}`.
- **Pricing:** the existing formula types (per unit, base plus rate, banded) as enum
  members.
- **Multiplicity:** per service, per call, per year.
- **Time:** per 24h, per 12h period, per hour; pro rata vs rounded up.
- **Minimum and maximum** caps.
- **Schedule metadata:** currency, tax treatment, measurement units.

This is a small constrained rule language, deliberately not a general expression
evaluator. A model cannot invent `pricing: {type: magical_formula}` because
Pydantic rejects it. That rejection is the containment boundary.

Constraints:

- All existing tests stay green. TNPA outputs identical to the cent.
- Migrate the existing YAML to the new structure.
- **Jafar reviews this change himself** — it touches the engine.

Expressiveness check: the TNPA book contains rules the calculator doesn't use —
drydock dues (GT ×2.83 plus cargo mass, per 12h period), tanker fire watch (maximum
caps), hulks (per metre per day). Report which the new stages could express. Do not
implement them as tariffs.

Stated future direction, for the docs only: a fuller compositional representation
(an expression tree over the same closed set of operators). Not now.

---

## 5. Schedule identity and selection

A new PDF is not necessarily an update of TNPA. It may be a new edition of an
existing schedule, or a different authority entirely.

### 5.1 Identity metadata

Every schedule carries:

```yaml
authority:
jurisdiction:
ports: []
schedule_name:
effective_from:
effective_to:
currency:
tax_treatment:
source_document_hash:
supersedes:
```

Identified provisionally from the opening pages (node 2), finalised after the full
read (node 4), since supersession, dates and tax treatment often sit in the general
terms rather than the cover.

The result decides the output: **new edition of an existing schedule** → proposal is
shown as a diff against it. **New authority** → proposal is a new schedule.

### 5.2 Registry and selection

One YAML file per schedule (authority + edition), e.g.
`schedules/tnpa_2024_2025.yaml` — not per port, since one book can cover many ports.
A small registry maps ports to schedule files with validity dates.

Consequences for the calculator and parser (build stage 5, not before):

- The `Port` enum is built from the registry rather than hardcoded.
- The schedule is selected by port **and** arrival date (editions have validity
  periods).
- The out-of-scope port rejection becomes "no approved schedule covers this port".
- Currency appears in every output.

---

## 6. Architecture

A LangGraph graph. Model provider for extraction: Anthropic.

### 6.1 Nodes

**1. Split — Python.** PDF into page texts, with tables preserved as well as the
chosen library allows.

**2. Provisional schedule identity — LLM, once.** From the opening pages: authority,
ports, edition, dates, currency. Marked provisional.

**3. Map — LLM, parallel, one call per page window.** Default window: 5 pages,
overlapping by 1 (pages 1–5, 5–9, 9–13, …) — roughly 14 calls for the 54-page TNPA
book. Window size and overlap are configurable; a window covering the whole
document is the same node with a different setting, not a different architecture.
A narrow question per window, structured output:

- section numbers and headings present
- section type: charge / general terms / irrelevant
- which of the six charges it **sets, modifies, exempts, discounts, surcharges or
  refers to**
- explicit references ("clause 6.3", "Annex B", "§4.2")
- any schedule metadata found

A narrow per-window question is more likely to catch a single qualifying sentence
than a whole-document pass — long-context models are good at *finding* things,
weaker at *exhaustively listing* every sentence touching one of six charges across
80 pages, and that output tends to be silently incomplete. Every page is read by
construction; there is nothing to check afterwards. Windowing does not resend
content wastefully either: with 1-page overlap each page is sent about twice total,
versus once per charge for a whole-document approach.

Windows are weaker at connecting distant pages (e.g. "except vessels under clause
4.7", twenty pages later) — by design, not a gap: Map only records the reference,
Assemble resolves it, and Extract receives both sections together in its focused
context. Global reasoning happens at Extract, not Map. An agentic discovery node
choosing what to read was considered and rejected again here: a coverage check that
only verifies labels is exactly the weakness this design exists to remove.

**4. Assemble — Python.**

- Merge windows into sections. Overlaps produce duplicates: deduplicate, and where
  two windows disagree on charge tags, **take the union**. Considering one section
  too many is cheap; missing a modifier is not.
- Resolve explicit references by section number.
- Implicit references: every section inherits its chapter's general conditions via
  the heading hierarchy. (TNPA §3.6 towage never cites §3.1, but depends on its
  working hours.)
- Build each charge's **context set**: its main section(s), every section tagged as
  affecting it, the general terms, referenced sections.
- A charge no window tagged as a main section is a not-present candidate.
- Other charge sections become the out-of-scope list.
- Finalise schedule metadata.

General terms always come from **the document being processed**, never from an
existing config. If none are found, the report says so and states the assumptions
made.

**5. Extract — LLM, parallel, one per charge.** Focused context from Assemble, not
the whole document. Has read and search tools (§6.3), used only to **follow a lead**
— a reference pointing outside its context. Anything found that way is flagged,
because it means Map/Assemble missed a link.

Output per charge:

- a semantic outcome (§3.2)
- for Mapped: the proposed block in the staged representation
- **provenance:** section and page range per charge; page per rate block
- **sections considered:** every section in its context plus any lead-found ones,
  each *used* or *dismissed* with a reason

**6. Validate — Python.** See §6.4 and §6.5.

**7. Verify — ReAct agent.** See §6.6.

**8. Review report — assemble.** See §7.

**9. Human approval — LangGraph interrupt.** Approve → write the schedule (new file
or new edition) and run the full test suite. Reject → stop, keep the report.

### 6.2 Invariant

**Every output of Extract passes through Validate. No exceptions** — whether it came
from the first pass, a validation repair, or a verifier challenge. It must be
impossible for an unvalidated extraction to reach Verify or the report.

```
Extract → Validate → Verify → Report
   ↑         │          │
   └─ repair ┘          │
   ↑                    │
   └───── finding ──────┘   (then Validate again, then Verify again)
```

### 6.3 Tools

Keyword and pattern search over the page texts, returning page numbers and short
snippets. Read a page range. No embeddings, no vector store: leads are usually
explicit references, which exact matching finds reliably, and provenance needs
exact pages.

### 6.4 Validation checks

**Hard — failure routes back to Extract:**

- schema valid; every stage option is an allowed enum member
- required parameters present
- band structure valid: ordered, contiguous under the interval convention, final
  band open or explicit null
- cited pages exist
- smoke calculation: the engine computes each mapped charge for a few synthetic
  vessels (small, medium, large) without error, non-negative

**Warnings — forwarded to the report, never block:**

- a numeric value not found verbatim on its cited page (PDF formatting varies too
  much for this to be a gate)
- non-monotonic band pricing (true for every TNPA port, but an economic pattern in
  one book, not a law)

### 6.5 Validation routing

- **Valid** → Verify.
- **Invalid extraction** → back to Extract, for **that charge only**, with
  structured errors, including the list of allowed options where an invalid one was
  used. Validate never decides a charge is Unmapped: an invalid option may be a
  misreading of a representable rule. Only Extract declares Unmapped.
- **Budget exhausted** → status Extraction failed, with the attempts shown in the
  report.
- **System error** → abort the run (§6.7).

### 6.6 Verifier

The one genuinely agentic node.

- **Independent reasoning path:** fresh context, no access to the extractor's
  reasoning, whole-document access through the tools.
- **Preferably a different model or provider** from extraction, where available.
  Configurable. Diversity catches different errors; it is a preference, not a hard
  dependency.
- **Adversarial objective:** assume the proposal may be wrong. Find missing
  conditions, wrong rates, wrong mappings, overlooked references, modifiers,
  exemptions, minimums or maximums, unsupported assumptions, bundling mistakes.
- **Concrete findings, no confidence scores:** each finding names the charge,
  severity, the problem, and the source pages.

Routing:

- **No material finding** → report.
- **Findings** → back to Extract with the findings. Extract either accepts and
  corrects, or rebuts with evidence. Then Validate, then Verify once more.
- **Still disagreeing after the budget** → both positions go to the report as an
  unresolved disagreement:

```yaml
disagreement:
  charge: pilotage
  extractor: {interpretation: ..., pages: [12, 13]}
  verifier: {concern: ..., pages: [8, 21]}
  status: unresolved
```

A disagreement is information for the reviewer, not a pipeline failure. Never loop
until the models agree.

### 6.7 Retry budgets and system errors

Separate per-charge budgets, so one failure mode can't consume the other:

- validation repairs: 3 (configurable)
- verifier rounds: 1 (configurable, max 2)

A **system error** is a failure of the application itself: the schema cannot be
loaded, the validator crashes, a configured option has no implementation, a version
mismatch. In this version, **any system error aborts the whole run**, since a report
built on a broken validator makes false claims. Document in the docs that per-charge
isolation — abort only when shared machinery fails, isolate a charge when the
failure is confined to its code path — is the intended refinement.

### 6.8 State

A typed state carrying: page texts, provisional and final schedule identity, window
map outputs, assembled sections and context sets, per-charge extractions with
outcomes, validation errors and warnings, verifier findings, disagreements,
per-charge retry counters for each budget, pipeline statuses, the report.

---

## 7. Review report

- schedule identity, and whether this is a new edition (with diff) or a new schedule
- per charge: outcome, proposed block, provenance, sections considered, lead-found
  sections
- warnings
- verifier findings and how each was resolved
- unresolved disagreements, both positions
- Extraction failed items with their attempts
- not-present, bundled, unmapped and out-of-scope lists
- coverage: pages read, charges mapped
- assumptions made where general terms were missing

It is written for a business reviewer. It must be readable without opening the
code.

---

## 8. Evaluation

All results go in the docs.

**Cross-cutting constraint: authority-agnostic prompts.** No prompt used by Map,
Assemble, Extract or Verify may reference TNPA-specific facts — port names, section
numbers (§3.2, §3.8, §3.9), or cited rate values from this book. If TNPA facts leak
into a prompt, the accuracy score in (1) and the catch rate in (3) measure
memorisation, not generalisation — and this spec is itself full of TNPA examples, so
the leak risk is the default path, not a hypothetical. **Enforced, not just stated:**
a test scans every prompt template against a denylist of TNPA-specific strings (port
names, the §3.2/§3.8/§3.9 section numbers, cited rate values) and fails the build if
any appear. The seeded-error evaluation (3) additionally must not tell the verifier
which errors were seeded, directly or through prompt structure.

1. **Extraction accuracy on TNPA.** Run the pipeline on the TNPA PDF. Score the
   proposal cell by cell against the existing hand-verified YAML, the gold standard.
   Per charge and overall. Also score Map's tagging directly: §3.2 must be tagged
   towage, pilotage and berthing.
2. **Baseline comparison.** Not a separate build: one graph behind two config
   flags — `context: assembled | whole_document` (whole-document skips Map and
   Assemble; Extract gets the full text instead of its focused context) and
   `verifier: on | off`. Scoring code is shared across all three runs. The naive
   baseline (`whole_document`, `verifier: off`) still gets the same Validate node
   and the same repair budget as the full pipeline — score it the same way. This
   gives a clean three-way comparison — baseline, spine (stage 2, `assembled` /
   `off`), spine plus verifier (stage 4, `assembled` / `on`) — where each step
   isolates exactly one contribution: Map/Assemble structure, then the verifier.
   Without the shared Validate node and budget, a score difference would conflate
   "the pipeline structure helps" with "having any validation helps."
3. **Verifier catch rate.** Take the gold TNPA config, inject known errors, and give
   each mutated version to the verifier as if it were a proposal. Seed at least: a
   rate shifted into the wrong port column; a surcharge removed; a band boundary
   moved; the §3.2 incentive dropped; a bundled charge marked not present. Report
   the proportion caught.
4. **Generalisation demo.** One other authority's tariff book. The report should
   show naming reconciliation, a different currency, a new-schedule rather than a
   diff, and correct handling of not-present, bundled and unmapped charges.

---

## 9. Packaging and docs

- Package `extraction/` beside `tariffs/`. Imports the schema, loader and
  validators from `tariffs`; duplicates nothing.
- Dependencies in an optional extra: `pip install -e .[extraction]`.
- Map issues one LLM call per page window; run these under a **configurable
  concurrency limit** (default e.g. 5), not unbounded parallel calls.
- Tests for the pipeline must not require network access or API keys: mock model
  calls with recorded responses.
- `docs/extraction.md` covers: the scope contract, the human-gate rationale with the
  §3.8 example, the design principle, the outcomes and statuses, the architecture,
  evaluation results, known limitations (system errors abort the run; the future
  compositional representation), and **typical run cost** — call count,
  approximate $ and wall-clock time for a TNPA-sized book.
- `docs/extraction.md` also states the Map window-size default was chosen as a
  reasonable balance, not tuned. Future work: evaluate Map at several window sizes
  — including a single whole-document window, 10-page and 2-page windows — scoring
  the resulting inventory on TNPA (known charge sections, modifiers,
  cross-references, and the §3.2 tagging), and set the default from the results.

---

## 10. Build stages

Stop after each for review.

1. **Rule representation generalisation** (§4). Checkpoint: all existing tests
   green, TNPA outputs unchanged, expressiveness report.
2. **Pipeline spine without verifier:** nodes 1–6, 8, 9. Checkpoint: TNPA accuracy
   score.
3. **Baseline** and its score — the `whole_document` flag on the stage-2 graph
   (§8.2), not new code beyond that flag. **Most droppable stage under time
   pressure:** stage 2's score is the required proof the pipeline works, stage 4's
   seeded-error catch rate is the strongest demo; if time runs out, skip stage 3 and
   document it as future work, the same way as Map window-size tuning (§8/§9).
4. **Verifier** and the seeded-error evaluation. Checkpoint: catch rate, and whether
   accuracy improved over stage 2.
5. **Schedule registry and selection** (§5.2) in the calculator and parser.
6. **Generalisation demo** on a second tariff book.
7. **Docs restructure:** top-level README as entry point, detailed material in
   `docs/calculator.md` and `docs/extraction.md`.

---

## 11. Specified vs left to judgment

**Specified — do not deviate:** the design principle, scope contract, outcomes and
statuses, stage structure and closed enums, node roles and outputs, the invariant,
hard vs warning checks, routing rules, retry budgets, verifier independence and
objective, system-error handling, evaluation method, build order, the Map
window-size *default value* (5 pages / 1-page overlap) — window size and overlap
themselves must stay configurable, not hardcoded, since the future-work evaluation
in §8/§9 requires running Map at other sizes without a code change.

**Left to your judgment:** PDF and table extraction library, prompt wording, tool
implementations, state class details, report format, file layout inside
`extraction/`, test organisation, how model calls are mocked.

**Reviewed by Jafar:** the rule representation change (stage 1), and every
evaluation number.

---

## 12. Out of scope

- Charge types beyond the six.
- New calculation operators — flagged as Unmapped only.
- Autonomous config writes.
- A UI for uploading PDFs (later).
- Per-charge isolation of system errors (documented as future work).
