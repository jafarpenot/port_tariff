# Eval runs

A dated log of meaningful live runs against the real Anthropic/OpenAI APIs —
full pipeline runs, generalisation demos, model comparisons. Not for every
routine live smoke test; for anything whose actual output (numbers, per-charge
outcomes, a bug reproduced live) is worth being able to find again without
digging through a chat transcript or a `/tmp` file that's since been cleared.

One file per run or comparison: `YYYY-MM-DD_short-description.md`.

Template for a new entry:

```markdown
# <title>

**Date:** YYYY-MM-DD
**Model(s):** e.g. Claude Sonnet 5 / GPT-6 Luna
**Command:** the exact command run
**Related commit(s):** short hash + subject

## Summary
One or two sentences: what happened, pass/fail, the one number that matters.

## Details
Per-charge / per-case breakdown, real error text if a failure, whatever a
future reader would need to understand the result without re-running it.
```
