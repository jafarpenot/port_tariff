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

from .models import RoundingMode
from .schedule import Band


def ceil_per_100t(gt: float) -> int:
    """"Per 100 tons or part thereof" (SPEC.md §3) — ceil(GT/100)."""
    return math.ceil(gt / 100)


def units_from_gt(gt: float, rounding: RoundingMode) -> float:
    """Derive the billable 'units' quantity from GT per the rate's
    RoundingMode (SPEC.md §6). Only EXACT and CEIL_PER_100_T describe a
    GT-based unit; PRO_RATA_TIME is reserved for port dues' time-based
    rounding (see base_plus_increment_times_duration below) and is never
    passed here."""
    if rounding is RoundingMode.EXACT:
        return gt
    if rounding is RoundingMode.CEIL_PER_100_T:
        return ceil_per_100t(gt)
    raise ValueError(
        f"{rounding!r} does not describe a GT-based unit rounding "
        "(SPEC.md §5.2)."
    )


def per_unit_rate(
    gt: float,
    rate: float,
    rounding: RoundingMode,
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
    rounding: RoundingMode,
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
        raise ValueError(
            f"GT {gt} falls into a band that is n/a for this port in the source."
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
) -> DurationChargeResult:
    """units x basic + units x daily x days. Used by port dues.

    `units` is ceil(GT/100) — the book's formula bakes this in explicitly
    (SPEC.md §7.2) independent of the tariff's own `rounding` field, which
    for port dues (`pro_rata_time`) instead asserts that `days` is used as
    a raw fraction, never rounded or truncated.
    """
    units = ceil_per_100t(gt)
    basic = units * basic_rate
    incremental = units * daily_rate * days
    return DurationChargeResult(basic=basic, incremental=incremental)
