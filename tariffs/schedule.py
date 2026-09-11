"""YAML loader + Pydantic schema for config/tariffs_2024_2025.yaml.

Anything that varies by port, band or tariff edition is data (SPEC.md §5.1)
and is validated here. An unknown `rounding` string fails at load time
(Pydantic enum coercion), not at calculation time.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel

from .models import RoundingMode

_REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEDULE_PATH = _REPO_ROOT / "config" / "tariffs_2024_2025.yaml"


class Source(BaseModel):
    section: str
    page: int


# ---------------------------------------------------------------------------
# Shared band shapes
# ---------------------------------------------------------------------------


class Band(BaseModel):
    """A towage / berthing-band row. `base`, `increment_above_gt` and
    `per_100t` are explicit `null` for n/a port/band combinations
    (SPEC.md §5.3), never missing keys."""

    min_gt_exclusive: float
    max_gt_inclusive: Optional[float]
    base: Optional[float]
    increment_above_gt: Optional[float]
    per_100t: Optional[float]


class PortBands(BaseModel):
    bands: list[Band]


class CraftBand(BaseModel):
    min_gt_exclusive: float
    max_gt_inclusive: Optional[float]
    max_craft: float


# ---------------------------------------------------------------------------
# 7.1 Light dues
# ---------------------------------------------------------------------------


class LightDuesForeignRate(BaseModel):
    rate_per_100t: float
    minimum_fee: Optional[float]


class LightDuesRegisteredRate(BaseModel):
    rate_per_metre_loa_per_financial_year: float
    minimum_fee: Optional[float]


class CoastalBilling(BaseModel):
    max_days_in_sa_waters: int
    note: str


class LightDues(BaseModel):
    source: Source
    rounding: RoundingMode
    per_service: bool
    scope: str
    foreign_and_other_vessels: LightDuesForeignRate
    self_propelled_at_registered_port: LightDuesRegisteredRate
    coastal_billing: CoastalBilling
    exemptions: list[str]


# ---------------------------------------------------------------------------
# 7.2 Port dues
# ---------------------------------------------------------------------------


class SmallVesselMinimumFee(BaseModel):
    amount: float
    source: Source
    note: str


class Reduction(BaseModel):
    rate: float
    source: Source
    note: str


class LongStaySurcharge(BaseModel):
    rate: float
    applies_to: str
    condition: str
    source: Source


class PortDues(BaseModel):
    source: Source
    rounding: RoundingMode
    per_service: bool
    basic_rate_per_100t: float
    incremental_rate_per_100t_per_day: float
    small_vessel_minimum_fee: SmallVesselMinimumFee
    reductions: dict[str, Reduction]
    long_stay_surcharge: LongStaySurcharge
    exemptions: list[str]


# ---------------------------------------------------------------------------
# 7.3 Towage
# ---------------------------------------------------------------------------


class CraftAllocation(BaseModel):
    source: Source
    note: str
    bands: list[CraftBand]


class TowageOutOfHoursSurcharge(BaseModel):
    rate: float
    condition: str
    derivable_from_input: bool


class TowageAdditionalTugSurcharge(BaseModel):
    rate: float
    per: str
    condition: str
    derivable_from_input: bool


class TowageWithoutOwnPowerSurcharge(BaseModel):
    rate: float
    additional_tug_requested_rate: float
    condition: str
    derivable_from_input: bool


class TowageCancelledSurcharge(BaseModel):
    rate: float
    note: str
    derivable_from_input: bool


class TowageLateSurcharge(BaseModel):
    unit: str
    all_ports_except_saldanha: float
    saldanha: float
    derivable_from_input: bool


class TowageSurcharges(BaseModel):
    source: Source
    out_of_hours: TowageOutOfHoursSurcharge
    additional_tug_beyond_allocation: TowageAdditionalTugSurcharge
    vessel_without_own_power: TowageWithoutOwnPowerSurcharge
    cancelled_after_standby_commenced: TowageCancelledSurcharge
    late_against_notified_time: TowageLateSurcharge


class Towage(BaseModel):
    source: Source
    rounding: RoundingMode
    per_service: bool
    ports: dict[str, PortBands]
    craft_allocation: CraftAllocation
    surcharges: TowageSurcharges


# ---------------------------------------------------------------------------
# 7.4 VTS
# ---------------------------------------------------------------------------


class VTSPortRate(BaseModel):
    rate_per_gt: float


class VTS(BaseModel):
    source: Source
    rounding: RoundingMode
    per_service: bool
    minimum_fee: float
    ports: dict[str, VTSPortRate]
    exemptions: list[str]


# ---------------------------------------------------------------------------
# 7.5 Pilotage
# ---------------------------------------------------------------------------


class PilotagePortRate(BaseModel):
    base_fee: float
    per_100t: float


class PilotageStandardSurcharge(BaseModel):
    rate: float
    conditions: list[str]
    note: str


class PilotageDurbanCancellationWindow(BaseModel):
    source: Source
    rate: float
    condition: str


class PilotageSurcharges(BaseModel):
    source: Source
    standard_50pct: PilotageStandardSurcharge
    durban_cancellation_window: PilotageDurbanCancellationWindow


class PLODuties(BaseModel):
    source: Source
    rate_per_hour: float
    applicability: str


class Pilotage(BaseModel):
    source: Source
    rounding: RoundingMode
    per_service: bool
    ports: dict[str, PilotagePortRate]
    surcharges: PilotageSurcharges
    plo_duties: PLODuties
    exemptions: list[str]


# ---------------------------------------------------------------------------
# 7.6 Berthing services (§3.8) and Running of vessel lines (§3.9)
# ---------------------------------------------------------------------------


class BerthingPortRate(BaseModel):
    base_fee: float
    per_100t: float


class BerthingSurcharge(BaseModel):
    rate: float
    conditions: list[str]


class BerthingSurcharges(BaseModel):
    source: Source
    standard_50pct: BerthingSurcharge


class BerthingServices(BaseModel):
    source: Source
    rounding: RoundingMode
    per_service: bool
    ports: dict[str, BerthingPortRate]
    surcharges: BerthingSurcharges
    tanker_attendance_mossel_bay_saldanha_per_hour: float


class RunningOfLinesPortRate(BaseModel):
    per_service: float
    outside_hours_minimum: float


class CancelledAfterStandby(BaseModel):
    minimum_hours: int
    per_hour_or_part_thereof: float


class RunningOfVesselLines(BaseModel):
    source: Source
    rounding: RoundingMode
    per_service: bool
    status: str
    note: str
    ports: dict[str, RunningOfLinesPortRate]
    late_arrival_departure_per_hour: dict[str, RunningOfLinesPortRate]
    cancelled_after_standby_commenced: CancelledAfterStandby
    saldanha_remooring_without_tug_or_pilot_per_service: float


# ---------------------------------------------------------------------------
# 9.4 Marine services incentive
# ---------------------------------------------------------------------------


class IncentiveThreshold(BaseModel):
    vessel_cargo_type: str
    threshold_calls: int
    discount_per_step: float
    calls_per_step: int
    max_calls_for_discount: int


class MarineServicesIncentive(BaseModel):
    source: Source
    status: str
    applies_to: list[str]
    thresholds: list[IncentiveThreshold]


# ---------------------------------------------------------------------------
# Top-level schedule
# ---------------------------------------------------------------------------


class TariffSchedule(BaseModel):
    light_dues: LightDues
    port_dues: PortDues
    towage: Towage
    vts: VTS
    pilotage: Pilotage
    berthing_services: BerthingServices
    running_of_vessel_lines: RunningOfVesselLines
    marine_services_incentive: MarineServicesIncentive


def load_schedule(path: str | Path = DEFAULT_SCHEDULE_PATH) -> TariffSchedule:
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return TariffSchedule.model_validate(raw)
