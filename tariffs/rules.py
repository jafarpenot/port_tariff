"""Generalised rate-rule vocabulary (extraction pipeline spec, specs/EXTRACTION_SPEC.md §4).

Restructures what SPEC.md v1 called "shapes" into fixed stages, each a
closed enum:

    basis -> rounding -> pricing -> multiplicity -> time -> min/max

A rate for a tariff this package has never seen before still has to be
one of these. A model proposing `pricing: {type: magical_formula}` gets
rejected by Pydantic before it ever reaches a calculator — that rejection
is the containment boundary the extraction pipeline relies on.

This module only defines the closed vocabulary and the pure functions
that interpret it (rounding, time). It does not decide which tariff uses
which pricing type, or where a value in a `VesselCall` maps to a `Basis`
— that wiring is calculators.py's job, same division of responsibility
as shapes.py before it (SPEC.md §5.1: the mechanism is code, the
selection from it is data).
"""

from __future__ import annotations

import math
from enum import Enum
from typing import Optional

from pydantic import BaseModel, model_validator


class Basis(str, Enum):
    """What a rate is charged on. Only GROSS_TONNAGE is wired to a
    VesselCall field today — SPEC.md §3 notes NT and DWT sit on the
    vessel sheet but are used by no tariff in this book. The others exist
    so a new book's rule can be *represented*; wiring a new basis to an
    actual VesselCall field is separate work, done when a tariff first
    needs it."""

    GROSS_TONNAGE = "gross_tonnage"
    NET_TONNAGE = "net_tonnage"
    LOA = "loa"
    DWT = "dwt"
    CARGO_TONNES = "cargo_tonnes"
    HOURS = "hours"


class RoundingMode(str, Enum):
    EXACT = "exact"
    CEIL_TO_UNIT = "ceil_to_unit"
    PRO_RATA = "pro_rata"


class RoundingSpec(BaseModel):
    """SPEC.md §5.2's rounding modes, generalised: `unit` is a parameter
    instead of `ceil_per_100_t` hardcoding 100. Other books round to 10
    or 50; this represents that without a code change."""

    mode: RoundingMode
    unit: Optional[float] = None

    @model_validator(mode="after")
    def _unit_required_for_ceil(self) -> "RoundingSpec":
        if self.mode is RoundingMode.CEIL_TO_UNIT and not self.unit:
            raise ValueError("RoundingMode.CEIL_TO_UNIT requires a positive `unit`.")
        return self


def round_value(value: float, spec: RoundingSpec) -> float:
    """Apply a RoundingSpec to a basis value (e.g. GT) to get billable
    units. EXACT: as-is (VTS). CEIL_TO_UNIT: ceil(value/unit) — "per N
    tons or part thereof" for whatever N the book prints. PRO_RATA:
    as-is, fractional, never rounded (reserved for time-basis values —
    see round_time below; a basis value is not expected to use this
    mode, but it is not rejected here)."""
    if spec.mode is RoundingMode.EXACT:
        return value
    if spec.mode is RoundingMode.CEIL_TO_UNIT:
        return math.ceil(value / spec.unit)
    if spec.mode is RoundingMode.PRO_RATA:
        return value
    raise ValueError(f"Unhandled RoundingMode: {spec.mode!r}")  # pragma: no cover — closed enum


class Multiplicity(str, Enum):
    """Whether a rate is charged once per marine service (an arrival, a
    departure — SPEC.md §3's "per service" doubling), once per port
    call, or once per year (annual/coastal billing, not modelled by any
    v1 calculator but representable)."""

    PER_SERVICE = "per_service"
    PER_CALL = "per_call"
    PER_YEAR = "per_year"


class TimeRounding(str, Enum):
    PRO_RATA = "pro_rata"
    ROUNDED_UP = "rounded_up"


class TimeSpec(BaseModel):
    """Per 24h / 12h / 1h period, pro rata or rounded up to whole
    periods. Only port dues uses this today (24h periods, pro rata — no
    rounding of the fractional-day chargeable period, SPEC.md §7.2)."""

    unit_hours: float
    rounding: TimeRounding


def round_time(days: float, spec: Optional[TimeSpec]) -> float:
    """Apply a TimeSpec to a duration already expressed in days. No
    spec, or PRO_RATA, means the value passes through unrounded —
    port dues' current behaviour. ROUNDED_UP rounds up to whole
    `unit_hours` periods; unused by any v1 tariff, but representable
    without a code change once a book needs it."""
    if spec is None or spec.rounding is TimeRounding.PRO_RATA:
        return days
    period_days = spec.unit_hours / 24
    return math.ceil(days / period_days) * period_days


class PricingType(str, Enum):
    """SPEC.md §6's four shapes, as a closed, validated label carried in
    config next to the rates themselves. Each of the six v1 tariffs
    already calls a fixed, known shapes.py function (that mapping is
    decided once, in calculators.py, per SPEC.md §5.1 — code, not data);
    this field is what an extraction pipeline validates a NEW tariff's
    proposed shape against, and what a structural test cross-checks the
    existing six against so config and code cannot silently drift apart."""

    PER_UNIT = "per_unit"
    BASE_PLUS_INCREMENT = "base_plus_increment"
    BANDED = "banded"
    BASE_PLUS_INCREMENT_TIMES_DURATION = "base_plus_increment_times_duration"
