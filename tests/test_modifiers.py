"""SPEC.md §9, §10: modifier behavior — exemptions, reductions,
surcharges, and the "None is never coerced to False" resolution policy.

None of these inputs come from the reference case (SUDESTADA triggers no
modifier at all); these tests exist to lock in the interpretations made in
tariffs/modifiers.py, not to reproduce an external answer key.
"""

from datetime import datetime

import pytest

from tariffs import modifiers as mod
from tariffs.engine import calculate
from tariffs.models import ExemptionStatus, HullCert, PeriodBasis, Port, VesselCall, VesselType
from tariffs.schedule import load_schedule

SCHEDULE = load_schedule()


def _call(**overrides) -> VesselCall:
    defaults = dict(
        port=Port.EAST_LONDON,
        gross_tonnage=51255,
        number_of_operations=2,
        chargeable_period_days=1.0,
        chargeable_period_basis=PeriodBasis.DAYS_ALONGSIDE_PROXY,
    )
    defaults.update(overrides)
    return VesselCall(**defaults)


# ---------------------------------------------------------------------------
# Tri-state boolean algebra
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "vals,expected",
    [
        ((True, False), True),
        ((False, False), False),
        ((False, None), None),
        ((True, None), True),
    ],
)
def test_or3(vals, expected):
    assert mod._or3(*vals) is expected


@pytest.mark.parametrize(
    "vals,expected",
    [
        ((True, True), True),
        ((True, False), False),
        ((True, None), None),
        ((False, None), False),
    ],
)
def test_and3(vals, expected):
    assert mod._and3(*vals) is expected


@pytest.mark.parametrize("val,expected", [(True, False), (False, True), (None, None)])
def test_not3(val, expected):
    assert mod._not3(val) is expected


# ---------------------------------------------------------------------------
# is_out_of_hours (SPEC.md §8.3)
# ---------------------------------------------------------------------------


def test_out_of_hours_none_when_timestamp_missing():
    assert mod.is_out_of_hours(None, Port.DURBAN, SCHEDULE) is None


def test_24_hour_port_never_out_of_hours():
    ts = datetime(2024, 11, 17, 3, 0)  # Sunday 03:00
    assert mod.is_out_of_hours(ts, Port.DURBAN, SCHEDULE) is False


def test_east_london_sunday_is_out_of_hours():
    ts = datetime(2024, 11, 17, 9, 0)  # Sunday — not listed, zero hours
    assert mod.is_out_of_hours(ts, Port.EAST_LONDON, SCHEDULE) is True


def test_east_london_within_weekday_hours():
    ts = datetime(2024, 11, 15, 10, 0)  # Friday, within 06:00-22:00
    assert mod.is_out_of_hours(ts, Port.EAST_LONDON, SCHEDULE) is False


def test_east_london_before_weekday_hours():
    ts = datetime(2024, 11, 15, 5, 0)  # Friday 05:00, before 06:00 opening
    assert mod.is_out_of_hours(ts, Port.EAST_LONDON, SCHEDULE) is True


def test_mossel_bay_saturday_is_out_of_hours():
    ts = datetime(2024, 11, 16, 10, 0)  # Saturday — not listed for Mossel Bay
    assert mod.is_out_of_hours(ts, Port.MOSSEL_BAY, SCHEDULE) is True


# ---------------------------------------------------------------------------
# Exemptions (SPEC.md §7 exemption lists — 100% off, only when stated)
# ---------------------------------------------------------------------------


def test_saps_exemption_zeroes_light_port_vts_pilotage():
    result = calculate(_call(exemption_status=ExemptionStatus.SAPS))
    assert result.light_dues.amount == 0.0
    assert result.port_dues.amount == 0.0
    assert result.vts_dues.amount == 0.0
    assert result.pilotage_dues.amount == 0.0


def test_no_exemption_stated_is_unresolved_not_false():
    result = calculate(_call())
    step = next(s for s in result.light_dues.trace if s.modifier == "exemption")
    assert step.modifier_resolution.startswith("unresolved")
    assert result.light_dues.amount > 0


def test_exemption_not_in_list_does_not_zero_amount():
    # SAMSA is stated but towage has no exemptions list at all in config —
    # only light dues, port dues, VTS and pilotage carry one (SPEC.md §7).
    result = calculate(_call(exemption_status=ExemptionStatus.SAMSA))
    assert result.towage_dues.amount > 0


# ---------------------------------------------------------------------------
# Port dues reductions and surcharge (SPEC.md §9.1, §9.2)
# ---------------------------------------------------------------------------


def test_35pct_reduction_not_engaged_in_cargo_working():
    base = calculate(_call()).port_dues.amount
    reduced = calculate(_call(engaged_in_cargo_working=False)).port_dues.amount
    assert reduced == pytest.approx(base * 0.65, abs=0.01)


def test_35pct_does_not_apply_past_first_30_days():
    call = _call(
        engaged_in_cargo_working=False,
        is_bona_fide_coaster=False,
        is_passenger_vessel=False,
        arrival=datetime(2024, 5, 1),
        departure=datetime(2024, 6, 30),  # 60 days
        chargeable_period_days=60.0,
    )
    result = calculate(call)
    step = next(s for s in result.port_dues.trace if s.modifier == "port_dues_reduction_35pct")
    assert step.modifier_resolution.startswith("not applied")
    assert "first-30-days" in step.modifier_resolution


def test_60pct_beats_35pct():
    plain = calculate(_call(chargeable_period_days=1.5)).port_dues.amount
    call = _call(
        engaged_in_cargo_working=False,  # would qualify for 35% alone
        call_purpose_bunkers_stores_water_only=True,
        arrival=datetime(2024, 5, 1, 0, 0),
        departure=datetime(2024, 5, 2, 12, 0),  # 36h, within 48h
        chargeable_period_days=1.5,
    )
    result = calculate(call)
    assert result.port_dues.amount == pytest.approx(plain * 0.40, abs=0.01)
    thirty_five = next(s for s in result.port_dues.trace if s.modifier == "port_dues_reduction_35pct")
    assert "superseded by the 60%" in thirty_five.modifier_resolution


def test_60pct_requires_stay_under_48h():
    call = _call(
        call_purpose_bunkers_stores_water_only=True,
        arrival=datetime(2024, 5, 1, 0, 0),
        departure=datetime(2024, 5, 4, 0, 0),  # 72h, over 48h
        chargeable_period_days=3.0,
    )
    plain = calculate(_call(chargeable_period_days=3.0)).port_dues.amount
    result = calculate(call).port_dues.amount
    assert result == pytest.approx(plain, abs=0.01)


def test_10pct_tanker_with_hull_certification():
    base = calculate(_call()).port_dues.amount
    call = _call(vessel_type=VesselType.TANKER, hull_certification=[HullCert.DOUBLE_HULL])
    result = calculate(call).port_dues.amount
    assert result == pytest.approx(base * 0.90, abs=0.01)


def test_10pct_does_not_apply_to_non_tanker():
    base = calculate(_call()).port_dues.amount
    call = _call(vessel_type=VesselType.BULK_CARRIER, hull_certification=[HullCert.DOUBLE_HULL])
    result = calculate(call).port_dues.amount
    assert result == pytest.approx(base, abs=0.01)


def test_15pct_stacks_multiplicatively_on_35pct():
    base = calculate(_call(chargeable_period_days=8 / 24)).port_dues.amount
    call = _call(
        engaged_in_cargo_working=False,
        arrival=datetime(2024, 5, 1, 0, 0),
        departure=datetime(2024, 5, 1, 8, 0),  # 8h stay: <30 days and <12h
        chargeable_period_days=8 / 24,
    )
    result = calculate(call).port_dues.amount
    assert result == pytest.approx(base * 0.65 * 0.85, abs=0.01)


def test_long_stay_surcharge_hits_incremental_component_only():
    common = dict(arrival=datetime(2024, 5, 1), departure=datetime(2024, 7, 14), chargeable_period_days=74.0)
    plain = calculate(_call(engaged_in_cargo_working=True, **common)).port_dues
    surcharged = calculate(_call(engaged_in_cargo_working=False, **common)).port_dues

    assert surcharged.components["basic"] == pytest.approx(plain.components["basic"], abs=0.01)
    assert surcharged.components["incremental"] == pytest.approx(plain.components["incremental"] * 1.20, abs=0.01)


def test_port_dues_unresolved_flags_leave_base_case_unchanged():
    result = calculate(_call())
    assert result.port_dues.amount == pytest.approx(
        calculate(_call(engaged_in_cargo_working=None)).port_dues.amount, abs=0.01
    )
    for step in result.port_dues.trace:
        if step.modifier:
            assert step.modifier_resolution.startswith("unresolved") or step.modifier_resolution.startswith("not applied")


# ---------------------------------------------------------------------------
# Towage surcharges (SPEC.md §9.3)
# ---------------------------------------------------------------------------


def test_towage_out_of_hours_surcharge_is_derivable():
    base = calculate(_call()).towage_dues.amount
    result = calculate(
        _call(arrival=datetime(2024, 11, 15, 10, 0), departure=datetime(2024, 11, 17, 9, 0))  # Sun, EL closed
    ).towage_dues.amount
    assert result == pytest.approx(base * 1.25, abs=0.01)


def test_towage_additional_tug_surcharge():
    base = calculate(_call()).towage_dues.amount
    result = calculate(_call(additional_tug_requested=True)).towage_dues.amount
    assert result == pytest.approx(base * 1.50, abs=0.01)


def test_towage_without_own_power_50pct():
    base = calculate(_call()).towage_dues.amount
    result = calculate(_call(vessel_without_own_power=True)).towage_dues.amount
    assert result == pytest.approx(base * 1.50, abs=0.01)


def test_towage_without_own_power_100pct_when_extra_tug_also_requested():
    base = calculate(_call()).towage_dues.amount
    result = calculate(
        _call(vessel_without_own_power=True, additional_tug_requested=True)
    ).towage_dues.amount
    # +50% (additional tug) and +100% (no own power, w/ extra tug) stack additively.
    assert result == pytest.approx(base * (1 + 0.50 + 1.00), abs=0.01)


def test_towage_cancelled_after_standby_25pct():
    base = calculate(_call()).towage_dues.amount
    result = calculate(_call(service_cancelled_after_standby=True)).towage_dues.amount
    assert result == pytest.approx(base * 1.25, abs=0.01)


def test_towage_surcharges_stack_additively_not_multiplicatively():
    base = calculate(_call()).towage_dues.amount
    result = calculate(
        _call(
            arrival=datetime(2024, 11, 15, 10, 0),
            departure=datetime(2024, 11, 17, 9, 0),
            additional_tug_requested=True,
        )
    ).towage_dues.amount
    assert result == pytest.approx(base * (1 + 0.25 + 0.50), abs=0.01)
    assert result != pytest.approx(base * 1.25 * 1.50, abs=0.01)


def test_towage_late_fee_warns_but_does_not_change_amount():
    base = calculate(_call()).towage_dues.amount
    result = calculate(_call(late_against_notified_time=True))
    assert result.towage_dues.amount == pytest.approx(base, abs=0.01)
    assert any("not computed" in w for w in result.towage_dues.warnings)


def test_towage_unresolved_flags_are_recorded_not_silently_false():
    result = calculate(_call())
    for step in result.towage_dues.trace:
        if step.modifier and step.modifier != "marine_services_incentive":
            assert step.modifier_resolution.startswith("unresolved")


# ---------------------------------------------------------------------------
# Pilotage / berthing surcharges
# ---------------------------------------------------------------------------


def test_pilotage_surcharge_out_of_hours():
    plain = calculate(_call()).pilotage_dues.amount
    result = calculate(
        _call(arrival=datetime(2024, 11, 15, 10, 0), departure=datetime(2024, 11, 17, 9, 0))
    ).pilotage_dues.amount
    assert result == pytest.approx(plain * 1.50, abs=0.01)


def test_pilotage_surcharge_cannot_fire_via_hours_at_24h_port():
    plain = calculate(_call(port=Port.DURBAN)).pilotage_dues.amount
    result = calculate(
        _call(port=Port.DURBAN, arrival=datetime(2024, 11, 17, 3, 0), departure=datetime(2024, 11, 17, 5, 0))
    ).pilotage_dues.amount
    assert result == pytest.approx(plain, abs=0.01)


def test_pilotage_saps_exemption():
    result = calculate(_call(exemption_status=ExemptionStatus.SAPS))
    assert result.pilotage_dues.amount == 0.0


def test_berthing_surcharge_late_against_notified_time():
    plain = calculate(_call()).berthing_services.amount
    result = calculate(_call(late_against_notified_time=True)).berthing_services.amount
    assert result == pytest.approx(plain * 1.50, abs=0.01)


def test_berthing_surcharge_cancelled_after_standby():
    plain = calculate(_call()).berthing_services.amount
    result = calculate(_call(service_cancelled_after_standby=True)).berthing_services.amount
    assert result == pytest.approx(plain * 1.50, abs=0.01)


# ---------------------------------------------------------------------------
# Marine services incentive — always "not supported by input" (SPEC.md §9.4)
# ---------------------------------------------------------------------------


def test_marine_incentive_always_reported_not_applied():
    result = calculate(_call())
    for res in (result.towage_dues, result.pilotage_dues, result.berthing_services):
        step = next(s for s in res.trace if s.modifier == "marine_services_incentive")
        assert step.modifier_resolution.startswith("not applied")


# ---------------------------------------------------------------------------
# §3.9 — parsed, not calculated (SPEC.md §7.6 item 3)
# ---------------------------------------------------------------------------


def test_mooring_boat_used_warns_but_never_computes_an_amount():
    result = calculate(_call(mooring_boat_used=True))
    assert result.running_of_vessel_lines.amount is None
    assert any("mooring_boat_used=True" in w for w in result.running_of_vessel_lines.warnings)
    # §3.8 berthing services is unaffected — it is a separate calculator.
    assert result.berthing_services.amount == pytest.approx(calculate(_call()).berthing_services.amount, abs=0.01)
