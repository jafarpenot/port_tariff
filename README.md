# Port Tariff Calculator

Two capabilities, one app:

1. **Calculate** — compute Transnet National Ports Authority (TNPA)
   marine tariffs from a free-text vessel-call request, against a
   hand-verified rate schedule (23rd Edition, 1 Apr 2024 – 31 Mar 2025).
2. **Extract** — upload *any* port authority's tariff PDF, have an LLM
   pipeline propose a structured rate rule per charge for human review,
   and compute against it once approved — no hand-written calculator
   code needed per book.

Both live in the same Streamlit app.

---

## Run it

```bash
export ANTHROPIC_API_KEY=sk-ant-...   # Calculate (or put both in a local .env file)
export OPENAI_API_KEY=sk-...          # Extract (OpenAI GPT-6 Luna, not Claude — a deliberate, extraction-only cost choice)
docker compose up --build
# open http://localhost:8501
```

Pulled new commits? Always `--build` — `docker compose up` alone reuses
whatever image was last built.

**Local, without Docker:**
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[extraction]"   # drop [extraction] to skip the Extract page's dependencies
export ANTHROPIC_API_KEY=sk-ant-... OPENAI_API_KEY=sk-...
streamlit run app.py
```

Run the test suite instead of the app:
```bash
docker compose run --rm app pytest
# or locally: pytest
```
3 tests call a real model directly and are skipped unless
`ANTHROPIC_API_KEY` is set — a plain `pytest` run never spends money or
makes a network call on its own.

A CLI (`python -m tariffs.cli`) and an HTTP API (`tariffs/api.py`, a
second `docker compose` service) also exist for the Calculate side —
see `docs/calculator.md` §9. This README leads with Streamlit only, to
keep one clear path for getting started.

---

## It works — verified two independent ways

**The hand-typed reference case.** A known vessel call (SUDESTADA, GT
51,255, Durban) computed against the hand-verified config matches the
answer key exactly, on all six charges. Details: `docs/calculator.md` §2.

**The same case, from a freshly LLM-extracted copy of the same book.**
Independently — no hand-typed config involved — the Extract pipeline
re-read TNPA's own tariff PDF from scratch, and the generic compute
engine computed the *same reference vessel call* against what it found:

| Charge | Fresh extraction | Reference |
|---|---|---|
| Light dues | 60,062.04 | 60,062.04 ✓ |
| Port dues | 199,549.22 | 199,549.22 ✓ |
| Towage dues | 147,074.38 | 147,074.38 ✓ |
| VTS dues | 33,315.75 | 33,315.75 ✓ |
| Pilotage dues | 47,189.94 | 47,189.94 ✓ |
| Berthing services | 19,639.50 | 19,639.50 ✓ |

**All six match to the cent.** Two completely independent paths — a
human transcribing the book by hand, and an LLM pipeline reading the
same book fresh — arriving at the same numbers. Full writeup:
`docs/extraction.md` §5.

---

## Status and current limitations

- **Extract computes base rates only** — modifiers (surcharges,
  discounts, exemptions) are captured and reported, never silently
  applied.
- **The API doesn't support Extract yet** — computing against a freshly
  extracted report is currently a Streamlit-only capability.
- **TNPA is the only book validated end-to-end** for Extract (upload →
  approve → compute → matches a real reference case). A second book (RAK
  Ports, structurally different from TNPA) was used to stress-test the
  pipeline and surfaced a real gap — see `docs/extraction.md` §6 — fixed
  on a separate branch, not yet merged.
- See `KNOWN_ISSUES.md` for specific, dated findings from live testing.

---

## Where to read more

- **`docs/calculator.md`** — the Calculate side in full: reference case,
  known deviations, interpretations, assumptions, the natural-language
  parsing layer, packaging (CLI/API/Docker).
- **`docs/extraction.md`** — the Extract side in full: pipeline
  architecture, the pricing vocabulary, how to use it, the reference-case
  cross-validation, current limitations.
- **`KNOWN_ISSUES.md`** — specific, dated findings from live testing,
  fixed and open.
- **`specs/SPEC.md`** / **`specs/EXTRACTION_SPEC.md`** — the original
  fixed specifications each side was built against.

---

## Repository layout

```
config/tariffs_2024_2025.yaml   # hand-verified rate schedule, with source citations
tariffs/                        # Calculate: engine, calculators, modifiers, NLP parsing, CLI, API
extraction/                     # Extract: the LLM pipeline (structure scan -> map -> extract -> validate -> verify)
app.py                          # Streamlit entry point (both pages)
pages/1_Extract_New_Tariff.py   # the Extract UI page
extracted_reports/              # approved extraction reports, saved here, gitignored
tests/                          # both sides' test suites
docs/                           # INFERENCE.md, EXTRACTION.md
specs/                          # the two original specifications
notebooks/exploration.ipynb     # optional, not part of the graded path
Dockerfile, docker-compose.yml
```

**Principle followed throughout:** anything that varies by port, band,
or tariff edition is *data*; the mathematical mechanism is *code*.
