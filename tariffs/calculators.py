"""One function per tariff (SPEC.md §7). Each calculator looks up its own
config block, calls the relevant shape, and returns a TariffResult carrying
a trace. No formulas live here — only config lookup and trace assembly.

v1 applies no reductions or surcharges (SPEC.md §8.2 base-case default);
that layering happens in modifiers.py / engine.py in a later stage.
"""

from __future__ import annotations

from typing import Optional

from .models import TariffResult, TraceStep, VesselCall
from .rules import Basis, Multiplicity, round_time
from .schedule import TariffSchedule
from .shapes import (
    banded_base_plus_increment,
    base_plus_increment,
    base_plus_increment_times_duration,
    per_unit_rate,
    units_from_gt,
)


def _basis_value(call: VesselCall, basis: Basis) -> float:
    """Which VesselCall field a tariff's declared Basis reads from
    (extraction pipeline spec §4). Only GROSS_TONNAGE is wired — SPEC.md
    §3: NT and DWT are on the vessel sheet but used by no tariff in this
    book, and VesselCall carries no field for them."""
    if basis is Basis.GROSS_TONNAGE:
        return call.gross_tonnage
    raise NotImplementedError(
        f"basis {basis!r} is not wired to a VesselCall field — only "
        "gross_tonnage is used by any tariff in this schedule (SPEC.md §3)."
    )


def _resolved_services(call: VesselCall) -> tuple[int, str]:
    count, note = call.resolved_marine_service_count()
    return (count if count is not None else 1), note


def _services_for(call: VesselCall, multiplicity: Multiplicity) -> tuple[int, Optional[str]]:
    """SPEC.md §3's "per service" doubling, now driven by the tariff's
    declared Multiplicity instead of being implicit in which calculator
    function gets called."""
    if multiplicity is not Multiplicity.PER_SERVICE:
        return 1, None
    return _resolved_services(call)


def _apply_maximum(amount: float, maximum: Optional[float]) -> float:
    return amount if maximum is None else min(amount, maximum)


# ---------------------------------------------------------------------------
# 7.1 Light dues
# ---------------------------------------------------------------------------


def light_dues(call: VesselCall, schedule: TariffSchedule) -> TariffResult:
    cfg = schedule.light_dues
    rate_cfg = cfg.foreign_and_other_vessels
    basis_value = _basis_value(call, cfg.basis)
    amount = round(
        per_unit_rate(basis_value, rate_cfg.rate_per_100t, cfg.rounding, rate_cfg.minimum_fee),
        2,
    )
    amount = _apply_maximum(amount, cfg.maximum)
    units = units_from_gt(basis_value, cfg.rounding)
    trace = [
        TraceStep(
            tariff="Light dues",
            section=cfg.source.section,
            page=cfg.source.page,
            description="ceil(GT/100) x rate_per_100t (foreign/other vessels); charged once per SA visit",
            inputs={
                "gross_tonnage": call.gross_tonnage,
                "units": units,
                "rate_per_100t": rate_cfg.rate_per_100t,
            },
            rounding=cfg.rounding,
            subtotal=amount,
        )
    ]
    return TariffResult(name="light_dues", amount=amount, currency=schedule.schedule_identity.currency, trace=trace)


# ---------------------------------------------------------------------------
# 7.2 Port dues
# ---------------------------------------------------------------------------


def port_dues(call: VesselCall, schedule: TariffSchedule) -> TariffResult:
    cfg = schedule.port_dues
    if call.chargeable_period_days is None:
        raise ValueError(
            "VesselCall.chargeable_period_days is required for port dues (SPEC.md §7.2)."
        )
    basis_value = _basis_value(call, cfg.basis)
    days = round_time(call.chargeable_period_days, cfg.time)
    result = base_plus_increment_times_duration(
        basis_value,
        cfg.basic_rate_per_100t,
        cfg.incremental_rate_per_100t_per_day,
        days,
        cfg.rounding,
    )
    basic = round(result.basic, 2)
    incremental = round(result.incremental, 2)
    amount = _apply_maximum(round(basic + incremental, 2), cfg.maximum)
    units = units_from_gt(basis_value, cfg.rounding)
    trace = [
        TraceStep(
            tariff="Port dues",
            section=cfg.source.section,
            page=cfg.source.page,
            description="basic = ceil(GT/100) x basic_rate_per_100t",
            inputs={
                "gross_tonnage": call.gross_tonnage,
                "units": units,
                "basic_rate_per_100t": cfg.basic_rate_per_100t,
            },
            rounding=cfg.rounding,
            subtotal=basic,
        ),
        TraceStep(
            tariff="Port dues",
            section=cfg.source.section,
            page=cfg.source.page,
            description=(
                "incremental = ceil(GT/100) x incremental_rate_per_100t_per_day "
                "x chargeable_period_days (pro rata, no rounding of days)"
            ),
            inputs={
                "chargeable_period_days": call.chargeable_period_days,
                "chargeable_period_basis": (
                    call.chargeable_period_basis.value if call.chargeable_period_basis else None
                ),
                "incremental_rate_per_100t_per_day": cfg.incremental_rate_per_100t_per_day,
            },
            rounding=cfg.rounding,
            subtotal=incremental,
        ),
    ]
    return TariffResult(
        name="port_dues",
        amount=amount,
        currency=schedule.schedule_identity.currency,
        trace=trace,
        components={"basic": basic, "incremental": incremental},
    )


# ---------------------------------------------------------------------------
# 7.3 Towage dues
# ---------------------------------------------------------------------------


def towage_dues(call: VesselCall, schedule: TariffSchedule) -> TariffResult:
    cfg = schedule.towage
    port_bands = cfg.ports[call.port.value].bands
    basis_value = _basis_value(call, cfg.basis)
    per_service_amount = banded_base_plus_increment(basis_value, port_bands)
    services, service_note = _services_for(call, cfg.multiplicity)
    amount = _apply_maximum(round(per_service_amount * services, 2), cfg.maximum)
    trace = [
        TraceStep(
            tariff="Towage dues",
            section=cfg.source.section,
            page=cfg.source.page,
            description=(
                f"banded_base_plus_increment(GT, {call.port.value} bands) "
                f"x {services} service(s)"
            ),
            inputs={
                "gross_tonnage": call.gross_tonnage,
                "port": call.port.value,
                "per_service_amount": round(per_service_amount, 2),
                "marine_service_count": services,
            },
            rounding=cfg.rounding,
            subtotal=amount,
        )
    ]
    return TariffResult(name="towage_dues", amount=amount, currency=schedule.schedule_identity.currency, trace=trace, assumptions=[service_note])


# ---------------------------------------------------------------------------
# 7.4 VTS dues
# ---------------------------------------------------------------------------


def vts_dues(call: VesselCall, schedule: TariffSchedule) -> TariffResult:
    cfg = schedule.vts
    rate = cfg.ports[call.port.value].rate_per_gt
    basis_value = _basis_value(call, cfg.basis)
    amount = _apply_maximum(round(per_unit_rate(basis_value, rate, cfg.rounding, cfg.minimum_fee), 2), cfg.maximum)
    trace = [
        TraceStep(
            tariff="VTS dues",
            section=cfg.source.section,
            page=cfg.source.page,
            description="GT x rate_per_gt (RoundingMode.EXACT — no ceil), then apply minimum",
            inputs={
                "gross_tonnage": call.gross_tonnage,
                "port": call.port.value,
                "rate_per_gt": rate,
                "minimum_fee": cfg.minimum_fee,
            },
            rounding=cfg.rounding,
            subtotal=amount,
        )
    ]
    return TariffResult(name="vts_dues", amount=amount, currency=schedule.schedule_identity.currency, trace=trace)


# ---------------------------------------------------------------------------
# 7.5 Pilotage dues
# ---------------------------------------------------------------------------


def pilotage_dues(call: VesselCall, schedule: TariffSchedule) -> TariffResult:
    cfg = schedule.pilotage
    rate_cfg = cfg.ports[call.port.value]
    basis_value = _basis_value(call, cfg.basis)
    per_service_amount = base_plus_increment(
        basis_value, rate_cfg.base_fee, rate_cfg.per_100t, cfg.rounding
    )
    services, service_note = _services_for(call, cfg.multiplicity)
    amount = _apply_maximum(round(per_service_amount * services, 2), cfg.maximum)
    trace = [
        TraceStep(
            tariff="Pilotage dues",
            section=cfg.source.section,
            page=cfg.source.page,
            description=f"(base_fee + ceil(GT/100) x per_100t) x {services} service(s)",
            inputs={
                "gross_tonnage": call.gross_tonnage,
                "port": call.port.value,
                "base_fee": rate_cfg.base_fee,
                "per_100t": rate_cfg.per_100t,
                "marine_service_count": services,
            },
            rounding=cfg.rounding,
            subtotal=amount,
        )
    ]
    return TariffResult(name="pilotage_dues", amount=amount, currency=schedule.schedule_identity.currency, trace=trace, assumptions=[service_note])


# ---------------------------------------------------------------------------
# 7.6 Berthing services (§3.8) — this is what the reference case's
# "running of vessel lines dues" benchmark figure actually reconciles to.
# ---------------------------------------------------------------------------


def berthing_services(call: VesselCall, schedule: TariffSchedule) -> TariffResult:
    cfg = schedule.berthing_services
    rate_cfg = cfg.ports[call.port.value]
    basis_value = _basis_value(call, cfg.basis)
    per_service_amount = base_plus_increment(
        basis_value, rate_cfg.base_fee, rate_cfg.per_100t, cfg.rounding
    )
    services, service_note = _services_for(call, cfg.multiplicity)
    amount = _apply_maximum(round(per_service_amount * services, 2), cfg.maximum)
    trace = [
        TraceStep(
            tariff="Berthing services (§3.8)",
            section=cfg.source.section,
            page=cfg.source.page,
            description=f"(base_fee + ceil(GT/100) x per_100t) x {services} service(s)",
            inputs={
                "gross_tonnage": call.gross_tonnage,
                "port": call.port.value,
                "base_fee": rate_cfg.base_fee,
                "per_100t": rate_cfg.per_100t,
                "marine_service_count": services,
            },
            rounding=cfg.rounding,
            subtotal=amount,
        )
    ]
    return TariffResult(name="berthing_services", amount=amount, currency=schedule.schedule_identity.currency, trace=trace, assumptions=[service_note])


# ---------------------------------------------------------------------------
# §3.9 Running of vessel lines — parsed, not calculated in v1
# (SPEC.md §7.6 item 3). Never conflate with berthing_services() above.
# ---------------------------------------------------------------------------


def running_of_vessel_lines(call: VesselCall, schedule: TariffSchedule) -> TariffResult:
    cfg = schedule.running_of_vessel_lines
    trace = [
        TraceStep(
            tariff="Running of vessel lines (§3.9)",
            section=cfg.source.section,
            page=cfg.source.page,
            description="Parsed, not calculated in v1 (SPEC.md §7.6).",
            inputs={"mooring_boat_used": call.mooring_boat_used},
            rounding=None,
            subtotal=None,
        )
    ]
    warnings: list[str] = []
    if call.mooring_boat_used:
        warnings.append(
            "A §3.9 Running of Vessel Lines charge applies (mooring_boat_used=True) "
            "but is not calculated in this version — see SPEC.md §7.6 / README."
        )
    return TariffResult(name="running_of_vessel_lines", amount=None, currency=schedule.schedule_identity.currency, trace=trace, warnings=warnings)
