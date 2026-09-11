"""Domain model: VesselCall, RoundingMode, results, trace (SPEC.md §8).

Kept free of YAML/config concerns (see schedule.py) and of any calculation
logic (see shapes.py / calculators.py) — this module only describes shapes
of data.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class RoundingMode(str, Enum):
    """SPEC.md §5.2. An unknown string fails at config load time, not at
    calculation runtime."""

    EXACT = "exact"  # use GT as-is (VTS)
    CEIL_PER_100_T = "ceil_per_100_t"  # ceil(GT/100) (everything else)
    PRO_RATA_TIME = "pro_rata_time"  # fractional days, no rounding (port dues)


class Port(str, Enum):
    """The eight commercial ports (SPEC.md §8.1). Values match the port keys
    used in config/tariffs_2024_2025.yaml."""

    RICHARDS_BAY = "richards_bay"
    DURBAN = "durban"
    EAST_LONDON = "east_london"
    NGQURA = "ngqura"
    PORT_ELIZABETH = "port_elizabeth"
    MOSSEL_BAY = "mossel_bay"
    CAPE_TOWN = "cape_town"
    SALDANHA = "saldanha"


class VesselType(str, Enum):
    """Not exhaustive in the book — extend as needed. Only bulk_carrier
    (reference case) and tanker (port dues §9.1 10% reduction, PLO duties,
    tanker berthing attendance) are load-bearing for v1 logic."""

    BULK_CARRIER = "bulk_carrier"
    TANKER = "tanker"
    CONTAINER = "container"
    GENERAL_CARGO = "general_cargo"
    PASSENGER = "passenger"
    RO_RO = "ro_ro"
    FISHING = "fishing"
    OTHER = "other"


class HullCert(str, Enum):
    DOUBLE_HULL = "double_hull"
    SEGREGATED_BALLAST = "segregated_ballast"
    GREEN_AWARD = "green_award"


class ExemptionStatus(str, Enum):
    SAPS = "saps"
    SANDF = "sandf"
    SAMSA = "samsa"
    MEDICAL_RESEARCH = "medical_research"


class PeriodBasis(str, Enum):
    """Where chargeable_period_days came from (SPEC.md §7.2). Entrance
    timestamps, if ever supplied, take precedence over the alongside-time
    proxy."""

    ENTRANCE_TO_ENTRANCE = "entrance_to_entrance"
    DAYS_ALONGSIDE_PROXY = "days_alongside_proxy"


# ---------------------------------------------------------------------------
# VesselCall (SPEC.md §8.1)
# ---------------------------------------------------------------------------


class VesselCall(BaseModel):
    # identity and dimensions
    vessel_name: Optional[str] = None
    port: Port
    gross_tonnage: float
    length_overall_m: Optional[float] = None
    vessel_type: Optional[VesselType] = None

    # timing
    arrival: Optional[datetime] = None
    departure: Optional[datetime] = None
    chargeable_period_days: Optional[float] = None
    chargeable_period_basis: Optional[PeriodBasis] = None

    # services
    number_of_operations: Optional[int] = None
    marine_service_count: Optional[int] = None  # derived; see resolved_marine_service_count()

    # tri-state modifier flags — None means "not stated"
    engaged_in_cargo_working: Optional[bool] = None
    is_bona_fide_coaster: Optional[bool] = None
    is_passenger_vessel: Optional[bool] = None
    is_first_sa_port_call: Optional[bool] = None
    days_in_sa_waters: Optional[float] = None
    call_purpose_bunkers_stores_water_only: Optional[bool] = None
    hull_certification: list[HullCert] = Field(default_factory=list)
    exemption_status: Optional[ExemptionStatus] = None
    self_propelled: Optional[bool] = None

    # event flags — not derivable from a vessel sheet
    mooring_boat_used: Optional[bool] = None  # §3.9, v1: warn only
    additional_tug_requested: Optional[bool] = None
    vessel_without_own_power: Optional[bool] = None
    service_cancelled_after_standby: Optional[bool] = None
    late_against_notified_time: Optional[bool] = None

    def resolved_marine_service_count(self) -> tuple[Optional[int], str]:
        """Three-tier resolution (SPEC.md §8.2): stated > derived > unresolved.

        `number_of_operations` is not literally "number of marine services";
        the equivalence is inferred from the answer key (pilotage, towage and
        berthing all match only when doubled). Treating it as such here is a
        recorded benchmark assumption, not a general rule.
        """
        if self.marine_service_count is not None:
            return self.marine_service_count, "stated: marine_service_count supplied directly"
        if self.number_of_operations is not None:
            return (
                self.number_of_operations,
                "derived: number_of_operations treated as marine_service_count "
                "(benchmark assumption, SPEC.md §8.2 — not a general rule)",
            )
        return None, "unresolved: neither marine_service_count nor number_of_operations supplied"


# ---------------------------------------------------------------------------
# Results and trace (SPEC.md §12)
# ---------------------------------------------------------------------------


class TraceStep(BaseModel):
    """One row of the calculation trace: tariff, section reference, inputs
    used, rounding applied, and the subtotal it produced."""

    tariff: str
    section: str
    page: int
    description: str
    inputs: dict[str, Any] = Field(default_factory=dict)
    rounding: Optional[RoundingMode] = None
    modifier: Optional[str] = None
    modifier_resolution: Optional[str] = None
    subtotal: Optional[float] = None


class TariffResult(BaseModel):
    """The outcome of one tariff calculator."""

    name: str
    amount: Optional[float]
    currency: str = "ZAR"
    trace: list[TraceStep] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    # Decomposed subtotals for tariffs whose components a modifier must
    # target individually — e.g. port dues' incremental-only surcharge.
    components: dict[str, float] = Field(default_factory=dict)


class CalculationResult(BaseModel):
    """The single entry point's return value (SPEC.md §1, §12)."""

    vessel_call: VesselCall
    light_dues: TariffResult
    port_dues: TariffResult
    towage_dues: TariffResult
    vts_dues: TariffResult
    pilotage_dues: TariffResult
    berthing_services: TariffResult
    running_of_vessel_lines: TariffResult

    def _all_results(self) -> list[TariffResult]:
        return [
            self.light_dues,
            self.port_dues,
            self.towage_dues,
            self.vts_dues,
            self.pilotage_dues,
            self.berthing_services,
            self.running_of_vessel_lines,
        ]

    def totals(self) -> dict[str, Optional[float]]:
        return {r.name: r.amount for r in self._all_results()}

    def warnings(self) -> list[str]:
        return [w for r in self._all_results() for w in r.warnings]

    def trace_df(self):
        """A pandas DataFrame, one row per trace step, for notebook use
        (SPEC.md §12). pandas is deliberately NOT a dependency of this
        package (see pyproject.toml / SPEC.md §4) — it is imported lazily
        here and only needed if you call this method."""
        rows = []
        for result in self._all_results():
            for step in result.trace:
                rows.append(
                    {
                        "tariff": step.tariff,
                        "section": step.section,
                        "page": step.page,
                        "description": step.description,
                        "inputs": step.inputs,
                        "rounding": step.rounding.value if step.rounding else None,
                        "modifier": step.modifier,
                        "modifier_resolution": step.modifier_resolution,
                        "subtotal": step.subtotal,
                    }
                )
        try:
            import pandas as pd
        except ImportError as exc:  # pragma: no cover - environment-dependent
            raise ImportError(
                "trace_df() requires pandas, which is not a runtime "
                "dependency of the tariffs package. Install it in your "
                "notebook environment to use this method."
            ) from exc
        return pd.DataFrame(rows)
