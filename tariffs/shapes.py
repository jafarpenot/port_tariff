"""The four calculator shapes (SPEC.md §6). Each is implemented exactly
once and parameterised from config — no per-port branching and no
duplicated formulas live here or anywhere else in the package.

| Shape                               | Used by                |
|--------------------------------------|-------------------------|
| per_unit_rate                       | Light dues, VTS         |
| base_plus_increment                 | Pilotage, Berthing      |
| banded_base_plus_increment           | Towage                  |
| base_plus_increment_times_duration   | Port dues               |
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

from .rules import RoundingSpec, round_value
from .schedule import Band


class RateNotPublished(ValueError):
    """A specific GT/port combination has no published rate — the source
    book prints an explicit "n/a" there (SPEC.md §5.3), not a gap in our
    config. Deliberately distinct from a plain ValueError: this is a
    known, expected case a caller may want to handle gracefully (report
    "not computable" for just this one tariff), unlike a GT matching no
    band at all, which signals an actual config bug and should keep
    crashing loudly.
    """


def units_from_gt(gt: float, rounding: RoundingSpec) -> float:
    """Derive the billable 'units' quantity from a basis value (e.g. GT)
    per the rate's RoundingSpec (extraction pipeline spec §4 — the unit
    is a parameter, not hardcoded to 100). PRO_RATA is reserved for
    time-based rounding (see round_time in tariffs.rules) and is not
    expected here, but is not rejected — round_value passes it through
    unrounded like EXACT."""
    return round_value(gt, rounding)


def per_unit_rate(
    gt: float,
    rate: float,
    rounding: RoundingSpec,
    minimum: float | None = None,
) -> float:
    """units x rate, then apply minimum. Used by light dues, VTS."""
    units = units_from_gt(gt, rounding)
    amount = units * rate
    if minimum is not None:
        amount = max(amount, minimum)
    return amount


def base_plus_increment(
    gt: float,
    base: float,
    rate: float,
    rounding: RoundingSpec,
) -> float:
    """base + units x rate. Used by pilotage, berthing."""
    units = units_from_gt(gt, rounding)
    return base + units * rate


def _select_band(gt: float, bands: Sequence[Band]) -> Band:
    """Lower bound exclusive, upper bound inclusive (SPEC.md §5.4)."""
    for band in bands:
        lower_ok = gt > band.min_gt_exclusive
        upper_ok = band.max_gt_inclusive is None or gt <= band.max_gt_inclusive
        if lower_ok and upper_ok:
            return band
    raise ValueError(f"GT {gt} does not fall into any configured band.")


def banded_base_plus_increment(gt: float, bands: Sequence[Band]) -> float:
    """band.base + ceil((GT - band.increment_above_gt)/100) x band.per_100t.
    Used by towage."""
    band = _select_band(gt, bands)
    if band.base is None:
        raise RateNotPublished(
            f"no rate published for GT {gt} at this port — the source prints n/a for this band"
        )
    if band.increment_above_gt is None:
        return band.base
    extra_units = math.ceil((gt - band.increment_above_gt) / 100)
    return band.base + extra_units * band.per_100t


@dataclass(frozen=True)
class DurationChargeResult:
    """Port dues' basic and incremental components, kept separate because
    the long-stay surcharge (SPEC.md §9.2) applies to the incremental
    component only."""

    basic: float
    incremental: float

    @property
    def total(self) -> float:
        return self.basic + self.incremental


def base_plus_increment_times_duration(
    gt: float,
    basic_rate: float,
    daily_rate: float,
    days: float,
    rounding: RoundingSpec,
) -> DurationChargeResult:
    """units x basic + units x daily x days. Used by port dues.

    `units` comes from `rounding` (SPEC.md §7.2: ceil(GT/100) in this
    book — extraction pipeline spec §4 makes the 100 a parameter rather
    than hardcoding it here). `days` is a separate axis, governed by the
    tariff's `time` spec (tariffs.rules.round_time) — pro rata in this
    book, i.e. never rounded or truncated.
    """
    units = units_from_gt(gt, rounding)
    basic = units * basic_rate
    incremental = units * daily_rate * days
    return DurationChargeResult(basic=basic, incremental=incremental)
