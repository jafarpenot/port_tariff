# RAK Ports generalisation demo: GPT-6 Luna vs Claude Sonnet 5

**Date:** 2026-09-25
**Model(s):** GPT-6 Luna (OpenAI) vs Claude Sonnet 5 (Anthropic), same book, same test
**Command:** `uv run --env-file .env python3 -m pytest tests/extraction/test_live_generalization_demo.py -q -s`
**Book:** `new_tariff_pdf/RAK-Ports-Tariff-2026.pdf` (RAK Ports, UAE, 58 pages)
**Related commits:** `9942e41` (switch to Luna), `2bb098d` (pricing-shape + OpenAI-compat fixes)

## Summary

Switching extraction's LLM from Claude Sonnet 5 to GPT-6 Luna (~20x cheaper per
token) took five live attempts to get running at all — two distinct OpenAI
strict-structured-output incompatibilities, then a rate limit, before a clean
run. Once running, GPT-6 Luna's extraction *quality* on this book was clearly
worse than Sonnet 5's: every one of the 6 charges came back either
misclassified, disputed by Verify, or carrying a flatly wrong value, versus
Sonnet 5's cleaner run on the same book (see `specs/EXTRACTION_SPEC.md`'s
Stage 6 section for that earlier run's own write-up).

## What it took to get a clean run (infrastructure, now fixed)

1. **Schema rejection #1** — `ProposedRule.pricing_params: dict[str, Any]` (a
   free dict) was rejected outright by OpenAI's default strict
   structured-output mode: `"'additionalProperties' is required to be
   supplied and to be false"`. Fixed by replacing the free dict with
   `PricingShapes` — a fixed, closed shape per `pricing_type` (commit `2bb098d`).
2. **Schema rejection #2** — after fixing (1), `ChargeExtraction.per_port_rules`
   (also a dynamically-keyed dict) hit the same class of rejection:
   `"'required' is required to be supplied and to be an array including
   every key in properties. Extra required key 'per_port_rules' supplied."`
   Fixed by switching `structured_call()` to `method="function_calling"`
   (OpenAI's older, looser mode — already Claude's own default) instead of
   relying on strict mode at all.
3. **Rate limit** — 6 charges extracting in parallel (`concurrency_limit=5`,
   then `3`) burst past the account's 200,000 TPM limit on GPT-6 Luna twice in
   a row (`Used 193786, Requested 50743`, then `Used 179148, Requested
   156775` even with a 15/30/60s retry-backoff added). Fixed for this run by
   dropping to `concurrency_limit=1` (fully sequential) — slower, but no
   rate-limit errors at all.

## Quality comparison, same book

| Charge | Sonnet 5 | GPT-6 Luna |
|---|---|---|
| `vts` | mapped, clean, correct bands (222/390 by GT) | **unmapped** — balked at a boundary ambiguity ("thresholds overlap at exactly 500 GT") |
| `light_dues` | bundled into `port_dues`; Verify disputed the bundling | bundled into `port_dues`; Verify did not flag it this run |
| `port_dues` | `EXTRACTION_FAILED` (exhausted repair budget, still invalid) | **unmapped** — Verify: "incorrectly labels Harbour Dues as unmapped... assessed by gross tonnage" |
| `towage` | unmapped, disputed (per-tug rate table present) | unmapped, disputed again — same failure mode recurring |
| `pilotage` | mapped; Verify found 2 material omissions | **unmapped** — Verify: "has an express per-vessel-GT-band rate in Annex C... fits a GT-based pricing shape" |
| `berthing_services` | `EXTRACTION_FAILED` | "mapped" with **rate = AED 0.0** — Verify: "does not match the tariff. Page 48 lists... AED 552, 624, 784, 943, 1,176, or 1,342" |

Net: on the Luna run, all 6 charges ended up either misclassified, disputed,
or holding a clearly wrong value (a literal `0.0` rate that passed Validate's
structural check, since `0.0` is a syntactically valid float). Sonnet 5's run
at least got `vts` fully right and had only 2 hard failures rather than 4
wrong `unmapped` calls.

## Takeaway

The infrastructure fixes (pricing shapes, `function_calling` mode, lower
concurrency, rate-limit retry) are real and durable — they'd apply to any
OpenAI model, not just Luna, and they also close a real recurring bug
(wrong `pricing_params` key names) independent of provider. The quality gap is
a separate, open question: GPT-6 Luna appears more prone to the `unmapped`
escape hatch (see the Q1 discussion this session — a repair round can silently
reclassify a charge instead of fixing its structure) than Sonnet 5 was on this
same book. Not fixed here. Reasonable next steps, not yet decided: try GPT-6
Sol (the non-"Luna", presumably stronger tier) for a fairer quality
comparison at a still-lower cost than Claude, or invest in the repair-round
outcome-lock (Q1) and the compositional pricing vocabulary (the
drydock/towage-table gap) before trusting a cheaper model's output at review
quality.
