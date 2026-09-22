# Stage 1 expressiveness report

specs/EXTRACTION_SPEC.md §4 asks for a check of whether the generalised rule
vocabulary (`tariffs/rules.py`) can express three TNPA rules the calculator
doesn't use, without implementing them as tariffs. All three are drawn from
the TNPA book itself, not a hypothetical second authority.

## 1. Drydock dues — GT × 2.83 plus cargo mass, per 12-hour period

**Not cleanly expressible.** The time axis is fine — `TimeSpec(unit_hours=12,
rounding=...)` covers "per 12-hour period" exactly as designed. The blocker is
the pricing shape: this rate sums two *independent* bases (GT and cargo mass)
in one formula. `Basis` is a single value per rule, and none of the four
`PricingType` members represent "rate_a × basis_a + rate_b × basis_b" — only
`BASE_PLUS_INCREMENT_TIMES_DURATION` combines two components, and both of
those are on the *same* basis (GT), not two different ones.

Gap: a fifth pricing type covering a rate that's the sum of two single-basis
components, each independently rounded — or, more generally, treating a rate
as *two stacked rules whose amounts are added*, which would need no new
`PricingType` at all but does need a place in the schema to say "these two
rules compose." Not designed here; flagged as a real gap, not implemented.

## 2. Tanker fire watch — maximum caps

**Fully expressible.** The `maximum` field added in this stage
(`_apply_maximum` in `tariffs/calculators.py`) is applied generically to
the final computed amount regardless of pricing type — assuming fire watch's
underlying formula is one of the four known shapes (most plausibly
`per_unit` or `base_plus_increment`), adding a cap is a config value, not a
code change. This is the cleanest of the three — it's exactly the gap §4
named explicitly, and it's now closed.

## 3. Hulks — per metre per day

**Expressible, but only via a degenerate case, not a clean fit.** `Basis.LOA`
already exists in the closed enum, so "per metre" is covered. "Per day" has
no clean pricing type of its own, though: none of the four `PricingType`
members is a plain "units × rate × duration" with no base/incremental split.
It *can* be represented today by forcing it through
`BASE_PLUS_INCREMENT_TIMES_DURATION` with `basic_rate_per_100t: 0` — the
`basic` component zeroes out and only `incremental = units × daily_rate ×
days` survives, which is arithmetically correct. But a reviewer reading that
config would have to know the zero is a deliberate no-op, not a missing
value. A cleaner fix would be a `PER_UNIT_TIMES_DURATION` pricing type
(no base/incremental split); not added here, since nothing in the current
six tariffs needs it and the workaround is correct, if not self-documenting.

## Summary

| Rule | Basis | Time | Pricing shape | Verdict |
|---|---|---|---|---|
| Drydock dues | needs two bases at once | ✓ (12h) | ✗ no shape sums two bases | Not expressible |
| Tanker fire watch | ✓ | n/a | ✓ (existing shape + new `maximum`) | Fully expressible |
| Hulks | ✓ (LOA) | ✓ (per day) | ⚠ degenerate case (`basic_rate: 0`) | Expressible, not clean |

None of these three are implemented as tariffs — per §4, this check is
informational only, to size the gap before a second real tariff book might
need one of them.
