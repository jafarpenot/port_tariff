"""Reductions, surcharges and exemptions (SPEC.md §9).

Parameters and applicability metadata live in config (rates, conditions,
thresholds); this module only evaluates them against a VesselCall.

Default policy (SPEC.md §8.2): **no reduction or surcharge is applied
unless the input explicitly supports it.** `None` is never coerced to
`False` — every modifier considered is recorded in the trace, whether it
fired, was explicitly ruled out, or was left unresolved.

Interpretations recorded here (see README for the full list):
- 60% port dues reduction beats 35% (mutually exclusive; §9.1).
- 10% and 15% port dues reductions stack multiplicatively onto whatever
  reduction (0%, 35% or 60%) already applied — the book only states this
  explicitly for the 15%, but nothing suggests 10% behaves differently.
- Multiple towage surcharges that co-occur stack additively (each is "a
  surcharge of X%" on the base fee), not multiplicatively.
- The out-of-hours check is per *call* (arrival/departure), not per
  *service* — VesselCall carries one timestamp pair, not one per service.
- The towage late-arrival flat fee and the §3.9 mooring-boat charge are
  both flagged with a warning rather than computed — both need data
  (minutes late, tug count) that VesselCall does not carry.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time
from typing import Optional

from .models import Port, TariffResult, TraceStep, VesselCall, VesselType
from .schedule import Source, TariffSchedule

_DAY_KEYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


# ---------------------------------------------------------------------------
# Tri-state boolean algebra (True / False / None="unresolved")
# ---------------------------------------------------------------------------


def _not3(v: Optional[bool]) -> Optional[bool]:
    return None if v is None else (not v)


def _or3(*vals: Optional[bool]) -> Optional[bool]:
    """True wins; else None wins over False (can't rule it out)."""
    if any(v is True for v in vals):
        return True
    if any(v is None for v in vals):
        return None
    return False


def _and3(*vals: Optional[bool]) -> Optional[bool]:
    """False wins; else None wins over True (can't confirm it)."""
    if any(v is False for v in vals):
        return False
    if any(v is None for v in vals):
        return None
    return True


# ---------------------------------------------------------------------------
# Small shared derivations
# ---------------------------------------------------------------------------


def _stay_hours(call: VesselCall) -> Optional[float]:
    if call.arrival is None or call.departure is None:
        return None
    return (call.departure - call.arrival).total_seconds() / 3600


def _parse_hhmm(value: str) -> time:
    hh, mm = value.split(":")
    return time(int(hh), int(mm))


def is_out_of_hours(ts: Optional[datetime], port: Port, schedule: TariffSchedule) -> Optional[bool]:
    """Derived-by-proxy, never asserted (SPEC.md §8.3). `None` if `ts` is
    missing.

    `ts` (the vessel's arrival or departure timestamp) is used as a proxy
    for the inbound/outbound *service* time the book's surcharge actually
    triggers on — the two are not the same instant. The vessel may have
    waited at anchorage before berthing, so in particular the arrival
    timestamp is only an approximation of when the inbound service
    (pilotage/towage/berthing) actually occurred; it can be earlier than
    the true service time by however long the vessel sat at anchor.

    Public holidays are also not modelled — no calendar exists in v1 — so
    this can be wrong specifically on a public holiday; otherwise exact
    for the timestamp it was given.
    """
    if ts is None:
        return None
    cfg = schedule.ordinary_working_hours.ports[port.value]
    if cfg.is_24_hour:
        return False
    day_hours = cfg.hours.get(_DAY_KEYS[ts.weekday()])
    if day_hours is None:
        return True
    return not (_parse_hhmm(day_hours.start) <= ts.time() <= _parse_hhmm(day_hours.end))


def _call_out_of_hours(call: VesselCall, schedule: TariffSchedule) -> Optional[bool]:
    """Whether either endpoint of the call (arrival or departure) fell
    outside ordinary working hours — a per-call, derived-by-proxy stand-in
    for the book's per-service trigger (see is_out_of_hours docstring and
    the module docstring)."""
    flags = [
        is_out_of_hours(call.arrival, call.port, schedule),
        is_out_of_hours(call.departure, call.port, schedule),
    ]
    resolved = [f for f in flags if f is not None]
    if not resolved:
        return None
    return any(resolved)


def _out_of_hours_or_readiness_reason(
    overall: Optional[bool], out_of_hours: Optional[bool], flag_b: Optional[bool], flag_c: Optional[bool]
) -> str:
    """Shared reason text for pilotage/berthing's single OR'd surcharge,
    naming which leg actually fired — and, when it was the out-of-hours
    leg, marking it derived-by-proxy rather than asserted (see
    is_out_of_hours docstring)."""
    if overall is not True:
        return "no triggering condition stated"
    if out_of_hours is True:
        return (
            "derived-by-proxy from arrival/departure timestamp (not asserted — vessel may have "
            "waited at anchorage, so arrival approximates rather than confirms the inbound service time)"
        )
    if flag_b is True or flag_c is True:
        return "readiness/lateness or cancellation condition stated true"
    return "triggering condition met"  # pragma: no cover - defensive; overall is True implies one leg is True


# ---------------------------------------------------------------------------
# ModifierOutcome — the uniform shape every resolver returns
# ---------------------------------------------------------------------------


@dataclass
class ModifierOutcome:
    name: str
    applied: Optional[bool]  # True / False / None = unresolved
    reason: str
    rate: Optional[float] = None


def _trace_step(source: Source, tariff_label: str, outcome: ModifierOutcome) -> TraceStep:
    if outcome.applied is True:
        resolution = f"applied — {outcome.reason}"
    elif outcome.applied is False:
        resolution = f"not applied — {outcome.reason}"
    else:
        resolution = f"unresolved, base case (no modifier applied) — {outcome.reason}"
    return TraceStep(
        tariff=tariff_label,
        section=source.section,
        page=source.page,
        description=f"modifier: {outcome.name}",
        modifier=outcome.name,
        modifier_resolution=resolution,
        subtotal=None,
    )


# ---------------------------------------------------------------------------
# Exemptions (100% off) — SPEC.md §7, per-tariff exemption lists
# ---------------------------------------------------------------------------


def resolve_exemption(call: VesselCall, exemptions: list[str]) -> ModifierOutcome:
    if call.exemption_status is None:
        return ModifierOutcome("exemption", applied=None, reason="exemption_status not stated")
    stated = call.exemption_status.value
    if stated in exemptions:
        return ModifierOutcome("exemption", applied=True, reason=f"{stated} — 100% exemption", rate=1.0)
    return ModifierOutcome("exemption", applied=False, reason=f"{stated} is not listed as exempt for this tariff")


def _apply_exemption_only(
    result: TariffResult, call: VesselCall, source: Source, exemptions: list[str], tariff_label: str
) -> TariffResult:
    outcome = resolve_exemption(call, exemptions)
    trace = [*result.trace, _trace_step(source, tariff_label, outcome)]
    amount = 0.0 if outcome.applied is True else result.amount
    return result.model_copy(update={"amount": amount, "trace": trace})


def apply_to_light_dues(result: TariffResult, call: VesselCall, schedule: TariffSchedule) -> TariffResult:
    cfg = schedule.light_dues
    return _apply_exemption_only(result, call, cfg.source, cfg.exemptions, "Light dues")


def apply_to_vts(result: TariffResult, call: VesselCall, schedule: TariffSchedule) -> TariffResult:
    cfg = schedule.vts
    return _apply_exemption_only(result, call, cfg.source, cfg.exemptions, "VTS dues")


# ---------------------------------------------------------------------------
# Port dues (§9.1, §9.2)
# ---------------------------------------------------------------------------


def resolve_port_dues_reductions(call: VesselCall, cfg) -> dict[str, ModifierOutcome]:
    stay_hours = _stay_hours(call)
    stay_days = None if stay_hours is None else stay_hours / 24

    not_cargo_working = _not3(call.engaged_in_cargo_working)
    thirty_five_extra_reason = None
    if not_cargo_working is True and stay_days is not None and stay_days > 30:
        # "first 30 days only" — this leg stops qualifying once the stay is
        # confirmed to exceed 30 days (coaster/passenger legs are unaffected).
        not_cargo_working = False
        thirty_five_extra_reason = "stay exceeds the first-30-days window"

    thirty_five_flag = _or3(not_cargo_working, call.is_bona_fide_coaster, call.is_passenger_vessel)

    within_48h = None if stay_hours is None else (stay_hours <= 48)
    sixty_flag = _and3(call.call_purpose_bunkers_stores_water_only, within_48h)
    sixty_applies = sixty_flag is True

    # §9.1: 60% is not enjoyed in addition to 35% — apply 60% and drop 35%.
    thirty_five_effective = False if sixty_applies else thirty_five_flag
    thirty_five_reason = (
        "superseded by the 60% reduction"
        if sixty_applies
        else thirty_five_extra_reason
        or ("not engaged in cargo working, bona fide coaster, or passenger vessel" if thirty_five_flag else "condition not met / not stated")
    )

    is_tanker = None if call.vessel_type is None else (call.vessel_type is VesselType.TANKER)
    has_hull_cert = len(call.hull_certification) > 0
    ten_flag = _and3(is_tanker, has_hull_cert)

    fifteen_flag = None if stay_hours is None else (stay_hours < 12)

    return {
        "reduction_60pct": ModifierOutcome(
            "port_dues_reduction_60pct",
            sixty_flag,
            rate=cfg.reductions["bunkers_stores_water_only_stay_le_48h"].rate,
            reason="bunkers/stores/water-only call, stay <=48h" if sixty_flag else "condition not met / not stated",
        ),
        "reduction_35pct": ModifierOutcome(
            "port_dues_reduction_35pct",
            thirty_five_effective,
            rate=cfg.reductions["not_cargo_working_or_coaster_or_passenger_or_small_vessel_away_from_home_port"].rate,
            reason=thirty_five_reason,
        ),
        "reduction_10pct": ModifierOutcome(
            "port_dues_reduction_10pct",
            ten_flag,
            rate=cfg.reductions["liquid_bulk_tanker_hull_certification"].rate,
            reason="liquid bulk tanker with qualifying hull certification" if ten_flag else "not a certified tanker / not stated",
        ),
        "reduction_15pct": ModifierOutcome(
            "port_dues_reduction_15pct",
            fifteen_flag,
            rate=cfg.reductions["stay_under_12_hours"].rate,
            reason="stay under 12 hours" if fifteen_flag else "stay not under 12h / not stated",
        ),
    }


def resolve_port_dues_surcharge(call: VesselCall, cfg) -> ModifierOutcome:
    stay_hours = _stay_hours(call)
    stay_days = None if stay_hours is None else stay_hours / 24
    over_30_days = None if stay_days is None else (stay_days > 30)
    not_cargo_working = _not3(call.engaged_in_cargo_working)
    # "not undergoing repairs" has no corresponding VesselCall field, so it
    # can never be positively confirmed — only "over 30 days and not cargo
    # working" is checkable here.
    flag = _and3(over_30_days, not_cargo_working)
    return ModifierOutcome(
        "port_dues_long_stay_surcharge_20pct",
        flag,
        rate=cfg.long_stay_surcharge.rate,
        reason="in port >30 days, not engaged in cargo working" if flag else "condition not met / not stated",
    )


def apply_to_port_dues(result: TariffResult, call: VesselCall, schedule: TariffSchedule) -> TariffResult:
    cfg = schedule.port_dues
    trace = list(result.trace)

    exemption = resolve_exemption(call, cfg.exemptions)
    trace.append(_trace_step(cfg.source, "Port dues", exemption))
    if exemption.applied is True:
        return result.model_copy(
            update={"amount": 0.0, "trace": trace, "components": {"basic": 0.0, "incremental": 0.0}}
        )

    basic = result.components["basic"]
    incremental = result.components["incremental"]

    reductions = resolve_port_dues_reductions(call, cfg)
    reduction_multiplier = 1.0
    for key in ("reduction_60pct", "reduction_35pct", "reduction_10pct", "reduction_15pct"):
        outcome = reductions[key]
        trace.append(_trace_step(cfg.source, "Port dues", outcome))
        if outcome.applied is True:
            reduction_multiplier *= 1 - outcome.rate

    adjusted_basic = round(basic * reduction_multiplier, 2)
    adjusted_incremental = round(incremental * reduction_multiplier, 2)

    surcharge = resolve_port_dues_surcharge(call, cfg)
    trace.append(_trace_step(cfg.source, "Port dues", surcharge))
    if surcharge.applied is True:
        adjusted_incremental = round(adjusted_incremental * (1 + surcharge.rate), 2)

    amount = round(adjusted_basic + adjusted_incremental, 2)
    return result.model_copy(
        update={
            "amount": amount,
            "trace": trace,
            "components": {"basic": adjusted_basic, "incremental": adjusted_incremental},
        }
    )


# ---------------------------------------------------------------------------
# Marine services incentive (§9.4) — always "not supported by input"
# ---------------------------------------------------------------------------


def _marine_incentive_outcome() -> ModifierOutcome:
    return ModifierOutcome(
        "marine_services_incentive",
        applied=False,
        reason="not supported by the supplied input — VesselCall carries no shipping-line identity or national call-count field",
    )


# ---------------------------------------------------------------------------
# Towage surcharges (§9.3)
# ---------------------------------------------------------------------------


def resolve_towage_surcharges(call: VesselCall, schedule: TariffSchedule) -> dict[str, ModifierOutcome]:
    cfg = schedule.towage.surcharges
    out_of_hours = _call_out_of_hours(call, schedule)
    additional_tug_rate = (
        cfg.vessel_without_own_power.additional_tug_requested_rate
        if call.additional_tug_requested
        else cfg.vessel_without_own_power.rate
    )
    return {
        "out_of_hours_25pct": ModifierOutcome(
            "towage_out_of_hours_25pct",
            out_of_hours,
            rate=cfg.out_of_hours.rate,
            reason=(
                "derived-by-proxy from arrival/departure timestamp (not asserted — vessel may have "
                "waited at anchorage, so arrival approximates rather than confirms the inbound service time)"
                if out_of_hours
                else "within ordinary working hours per arrival/departure timestamp, or timestamps not stated"
            ),
        ),
        "additional_tug_50pct": ModifierOutcome(
            "towage_additional_tug_beyond_allocation_50pct",
            call.additional_tug_requested,
            rate=cfg.additional_tug_beyond_allocation.rate,
            reason="additional_tug_requested stated true" if call.additional_tug_requested else "not stated",
        ),
        "without_own_power": ModifierOutcome(
            "towage_vessel_without_own_power",
            call.vessel_without_own_power,
            rate=additional_tug_rate,
            reason="vessel_without_own_power stated true" if call.vessel_without_own_power else "not stated",
        ),
        "cancelled_after_standby_25pct": ModifierOutcome(
            "towage_cancelled_after_standby_25pct",
            call.service_cancelled_after_standby,
            rate=cfg.cancelled_after_standby_commenced.rate,
            reason="service_cancelled_after_standby stated true" if call.service_cancelled_after_standby else "not stated",
        ),
        "late_flat_fee": ModifierOutcome(
            "towage_late_against_notified_time",
            call.late_against_notified_time,
            rate=None,
            reason="late_against_notified_time stated true — flat fee per tug per half-hour, not a percentage" if call.late_against_notified_time else "not stated",
        ),
    }


def apply_to_towage(result: TariffResult, call: VesselCall, schedule: TariffSchedule) -> TariffResult:
    cfg = schedule.towage
    outcomes = resolve_towage_surcharges(call, schedule)
    trace = list(result.trace)
    warnings = list(result.warnings)

    multiplier = 1.0
    for key in ("out_of_hours_25pct", "additional_tug_50pct", "without_own_power", "cancelled_after_standby_25pct"):
        outcome = outcomes[key]
        trace.append(_trace_step(cfg.source, "Towage dues", outcome))
        if outcome.applied is True and outcome.rate is not None:
            multiplier += outcome.rate

    late = outcomes["late_flat_fee"]
    trace.append(_trace_step(cfg.source, "Towage dues", late))
    if late.applied is True:
        warnings.append(
            "Towage late-arrival/departure flat fee (§3.6) applies but is not computed — "
            "it requires minutes-late and tug count, which VesselCall does not carry."
        )

    incentive = _marine_incentive_outcome()
    trace.append(_trace_step(schedule.marine_services_incentive.source, "Towage dues", incentive))

    amount = round(result.amount * multiplier, 2)
    return result.model_copy(update={"amount": amount, "trace": trace, "warnings": warnings})


# ---------------------------------------------------------------------------
# Pilotage surcharge (§7.5) — single 50%, several OR'd triggers
# ---------------------------------------------------------------------------


def resolve_pilotage_surcharge(call: VesselCall, schedule: TariffSchedule) -> ModifierOutcome:
    cfg = schedule.pilotage.surcharges
    out_of_hours = _call_out_of_hours(call, schedule)
    # Durban's 60-minute (vs. the standard 30-minute) cancellation window
    # isn't separately modelled: VesselCall only carries a boolean
    # service_cancelled_after_standby, not minutes-until-notified-time, so
    # the two windows are indistinguishable at this level of input detail.
    flag = _or3(out_of_hours, call.late_against_notified_time, call.service_cancelled_after_standby)
    return ModifierOutcome(
        "pilotage_surcharge_50pct",
        flag,
        rate=cfg.standard_50pct.rate,
        reason=_out_of_hours_or_readiness_reason(flag, out_of_hours, call.late_against_notified_time, call.service_cancelled_after_standby),
    )


def apply_to_pilotage(result: TariffResult, call: VesselCall, schedule: TariffSchedule) -> TariffResult:
    cfg = schedule.pilotage
    trace = list(result.trace)

    exemption = resolve_exemption(call, cfg.exemptions)
    trace.append(_trace_step(cfg.source, "Pilotage dues", exemption))
    if exemption.applied is True:
        return result.model_copy(update={"amount": 0.0, "trace": trace})

    outcome = resolve_pilotage_surcharge(call, schedule)
    trace.append(_trace_step(cfg.source, "Pilotage dues", outcome))

    incentive = _marine_incentive_outcome()
    trace.append(_trace_step(schedule.marine_services_incentive.source, "Pilotage dues", incentive))

    amount = result.amount
    if outcome.applied is True:
        amount = round(amount * (1 + outcome.rate), 2)
    return result.model_copy(update={"amount": amount, "trace": trace})


# ---------------------------------------------------------------------------
# Berthing services surcharge (§3.8) — single 50%, several OR'd triggers
# ---------------------------------------------------------------------------


def resolve_berthing_surcharge(call: VesselCall, schedule: TariffSchedule) -> ModifierOutcome:
    cfg = schedule.berthing_services.surcharges
    out_of_hours = _call_out_of_hours(call, schedule)
    flag = _or3(out_of_hours, call.service_cancelled_after_standby, call.late_against_notified_time)
    return ModifierOutcome(
        "berthing_surcharge_50pct",
        flag,
        rate=cfg.standard_50pct.rate,
        reason=_out_of_hours_or_readiness_reason(flag, out_of_hours, call.service_cancelled_after_standby, call.late_against_notified_time),
    )


def apply_to_berthing(result: TariffResult, call: VesselCall, schedule: TariffSchedule) -> TariffResult:
    cfg = schedule.berthing_services
    outcome = resolve_berthing_surcharge(call, schedule)
    trace = [*result.trace, _trace_step(cfg.source, "Berthing services (§3.8)", outcome)]

    incentive = _marine_incentive_outcome()
    trace.append(_trace_step(schedule.marine_services_incentive.source, "Berthing services (§3.8)", incentive))

    amount = result.amount
    if outcome.applied is True:
        amount = round(amount * (1 + outcome.rate), 2)
    return result.model_copy(update={"amount": amount, "trace": trace})
