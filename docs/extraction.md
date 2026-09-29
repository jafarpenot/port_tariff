# Extraction: reading a new tariff book and computing against it

This is the newer capability, built on top of the calculator described
in `docs/calculator.md`: instead of relying on a hand-typed
`config/*.yaml` schedule, an LLM pipeline reads a tariff book PDF
directly, proposes a structured rate rule per charge, and a generic
compute engine turns that proposal into an actual computed fee — no
hand-written calculator function needed per charge, and no dependence
on the specific book being TNPA's.

The full technical specification is `specs/EXTRACTION_SPEC.md`. This
document is the practical "what it does, how to use it, what it's not
yet" summary. `KNOWN_ISSUES.md` tracks specific open findings from live
testing.

---

## 1. How to use it

1. Run the app (`docker compose up`, or `streamlit run app.py` locally
   — see the top-level `README.md`). Needs `OPENAI_API_KEY` set (this
   pipeline runs on OpenAI's GPT-6 Luna, not Anthropic — a deliberate,
   extraction-only cost choice made after the calculator itself was
   already built and evaluated against Claude; ~20x cheaper per token).
2. Open the **"Extract a New Tariff"** page from the sidebar. Upload any
   port authority's tariff PDF. A **"Charges extracted in parallel"**
   control (default 3) sets how many of the six charges extract at
   once — a book with modest per-charge context (TNPA) is fine at 3–4;
   a larger or more token-heavy book (RAK Ports is one example — single
   extraction calls there used ~150k of a 200k tokens-per-minute
   budget) can hit the LLM provider's rate limit if several such calls
   run concurrently. Lower it toward 1 (fully sequential, slower but
   safest) if a run comes back with "system error" statuses.
3. The pipeline runs — several minutes, many real LLM calls, well under
   a dollar for a book the size of TNPA's. The page streams the live
   run log in place, so you can watch each stage (structure scan, map,
   extract, verify) as it happens rather than staring at a bare spinner.
4. Review the report: authority/currency, per-charge outcome, any
   verifier findings, any unresolved disagreements. **Approve** it, and
   it's saved to `extracted_reports/` (one JSON file per approval).
5. Go to the main calculator page. A **"Tariff book"** selector now
   offers your saved report alongside "TNPA (existing)". Pick it, submit
   a vessel-call request exactly as you would for TNPA, and the computed
   amounts come from your freshly extracted rules instead of the
   hand-typed config.

**Port names are still TNPA's, regardless of which book you selected.**
The free-text request parser only recognizes the eight ports in
`schedules/registry.yaml` (TNPA's) — that list isn't derived from
whichever report you picked. So to test a freshly extracted non-TNPA
book (e.g. RAK Ports), name one of TNPA's eight ports in the request
(e.g. "Durban") anyway; it's just used to satisfy the parser; the rates
computed still come entirely from the extracted book, not from TNPA.

---

## 2. Architecture

One pipeline, two entry points: `extraction/pipeline.py` (a plain,
sequential linear pipeline — easiest to read and debug) and
`extraction/graph.py` (the same logic as a LangGraph state machine, with
an explicit human-approval interrupt — this is what the Streamlit page
runs). Both call the same underlying node functions, so a fix to one
applies to both automatically; only entry-point-specific control flow
(like the graph's repair-loop routing) needs porting by hand between
them.

**The pipeline, in order:**

1. **Structure scan** — a whole-document pass noting the book's own
   table of contents / section layout, advisory context for later steps.
2. **Split** — deterministic, no LLM: the PDF into per-page text.
3. **Identity** — which authority, which currency, from the opening
   pages.
4. **Map** — the whole document, read in page windows, to find which
   pages discuss which of the six canonical charges (light dues, port
   dues, towage, VTS, pilotage, berthing services) and what's said about
   each — not page citations (found live, repeatedly, to be unreliable;
   see `KNOWN_ISSUES.md`), but a paragraph of notes per charge per
   window.
5. **Assemble** — merges Map's findings into one focused page range and
   note-set per charge.
6. **Extract** — one call per charge: propose a structured rule (basis,
   rounding, pricing shape, modifiers) from its assembled pages, sent as
   real PDF pages, not flattened text (table fidelity matters — see
   `KNOWN_ISSUES.md` for why that switch happened).
7. **Validate** — deterministic: does the proposed rule's structure make
   sense (a smoke calculation against synthetic vessel sizes, band
   contiguity, cited pages in range)? Invalid triggers a repair round —
   Extract runs again for that charge with the specific problem folded
   into the prompt.
8. **Verify** — an independent, adversarial LLM pass, checking the
   proposal against the source directly, with no visibility into
   Extract's own reasoning. A material finding triggers a repair round
   too. A finding that survives the repair budget becomes a recorded,
   unresolved disagreement in the final report — never forced to
   resolve, never silently dropped.
9. **Human approval** — the graph interrupts here; nothing is saved
   until a human approves.

---

## 3. The pricing vocabulary

Four fixed shapes, closed and validated (not a free-form formula the
model could invent): `per_unit` (rate × units), `base_plus_increment`
(a flat base plus rate × units), `banded` (the above, but the base and
rate change across GT bands), `base_plus_increment_times_duration` (a
basic component plus a per-unit-per-day incremental one — port dues'
shape). A charge that varies by port gets one full rule *per port*, not
an average or a single column picked arbitrarily.

**Modifiers** (a surcharge, discount, or exemption on top of the base
rate) are always captured — as a plain percentage, a flat amount, or a
verbatim quote when neither fits — never a reason to leave the whole
charge unmapped. **They are not applied by the compute engine (§4)** —
every modifier is reported (visible in the UI as a warning: "N
modifier(s) not applied") rather than silently ignored or guessed at.

If a charge's *base* calculation genuinely doesn't fit any of the four
shapes — RAK Ports' towage table, keyed by which tug is requested rather
than any numeric measurement, is the clearest example found so far —
the pipeline correctly reports it `unmapped` with the source quoted,
rather than forcing a wrong fit. A fifth, category-keyed shape to cover
this case has been designed and prototyped on a separate,
**not-yet-merged** branch; `main` (what this document describes) still
has only the four shapes above.

---

## 4. Computing from an extracted rule

`tariffs/generic_calculator.py` is a small, data-driven engine: given
one extracted `ProposedRule` and a vessel call, it dispatches on the
rule's own `pricing_type` to the same underlying math
(`tariffs/shapes.py`) the hand-written `tariffs/calculators.py`
functions use — real multiplicity, real rounding, `maximum` applied to
the total. No hand-written function is needed per charge; a newly
extracted charge from any book is computable the moment it's approved.

**v1 scope, explicitly: base rate only.** Modifiers are reported, never
applied — a result is never presented as complete when a modifier might
actually change it. This is the main functional gap versus the
hand-written `tariffs/calculators.py` path, which does apply TNPA's own
modifiers (`tariffs/modifiers.py`).

**Not yet wired up:** `tariffs/api.py` (the HTTP API) still only
supports the original calculation path — computing against a freshly
extracted report is currently a Streamlit-only capability.

---

## 5. Reference-case cross-validation

The same reference vessel call used throughout `docs/calculator.md` (GT
51,255, Durban, 3.396 days, 2 operations) was run against TNPA's tariff
book **re-extracted fresh by this pipeline** — an independent LLM
extraction, not the hand-typed `config/tariffs_2024_2025.yaml` — and
computed through the generic engine above.

| Charge | Compiled (fresh extraction) | Reference (hand-typed config) |
|---|---|---|
| Light dues | 60,062.04 | 60,062.04 ✓ |
| Port dues | 199,549.22 | 199,549.22 ✓ |
| Towage dues | 147,074.38 | 147,074.38 ✓ |
| VTS dues | 33,315.75 | 33,315.75 ✓ |
| Pilotage dues | 47,189.94 | 47,189.94 ✓ |
| Berthing services | 19,639.50 | 19,639.50 ✓ |

**All six match to the cent** — two entirely independent paths (a human
transcribing the book by hand into config; an LLM pipeline reading the
same book fresh) arriving at the same numbers. This cross-validates both
the hand-typed config *and* the extraction pipeline at once.

**Reproduced end-to-end through the actual app, not just as a
standalone script**: uploading `Port Tariff.pdf` on the "Extract a New
Tariff" page, approving the resulting report (saved to
`extracted_reports/`), selecting it from the main calculator's "Tariff
book" dropdown, and submitting the same reference vessel-call request —
the computed amounts matched this same table exactly. That confirms the
*whole* user-facing path (extract → approve → save → select → compute),
not just the underlying compute function called directly.

---

## 6. What's evaluated but not merged

RAK Ports' tariff book was used to stress-test the pipeline against a
book structurally unlike TNPA's — confirmed live that its towage table
(keyed by tug selection) cannot be represented by the four shapes above,
and that a more general, category-keyed shape can represent it cleanly.
That work (a fifth pricing shape, a generic categorical-key input on
`VesselCall`, a corresponding UI selector) exists on a separate branch,
deliberately not merged into `main` yet — it surfaced its own open
question (the model occasionally reaches for the new shape even when a
simpler existing one already fits) that needs another iteration before
it's ready. See `KNOWN_ISSUES.md` for the live findings.

---

## 7. Known limitations, stated plainly

- **Base rate only** — modifiers are reported, never applied (§4).
- **API not wired up** — extraction/compute is Streamlit-only (§4).
- **TNPA is the only book validated end-to-end** (extract → approve →
  compute → matches a real reference case). RAK was evaluated for
  extraction feasibility only, on the vocabulary side, not carried
  through to a live compute+UI test.
- **Reports are not versioned or diffed** — approving a second extraction
  of the same book just adds another file to `extracted_reports/`; there
  is no merge/compare-against-previous mechanism.
- **The request parser only accepts TNPA's eight port names**, no matter
  which book you selected for compute (§1) — there's no port registry
  per extracted book.
- See `KNOWN_ISSUES.md` for specific, dated findings from live testing
  (page-citation reliability, table-of-contents merge bugs, a
  retry-feedback fix, a port-matching bug, and others) — most already
  fixed and documented there, some still open.
