"""specs/EXTRACTION_SPEC.md §5.2: schedules/registry.yaml drives the
Port enum and schedule selection, not a hardcoded list. These tests
guard the registry's structure and the two guarantees the rest of the
codebase relies on: today's registry produces the identical Port enum
shape as the old static definition, and selection is genuinely by port
and date, not just port.
"""

from datetime import date, datetime

import pytest

from tariffs.engine import calculate
from tariffs.models import PeriodBasis, Port, VesselCall, VesselType
from tariffs.registry import all_registered_ports, schedule_path_for
from tariffs.schedule import load_schedule

EXPECTED_PORTS = {
    "richards_bay",
    "durban",
    "east_london",
    "ngqura",
    "port_elizabeth",
    "mossel_bay",
    "cape_town",
    "saldanha",
}


def test_registry_produces_the_expected_eight_ports():
    assert set(all_registered_ports()) == EXPECTED_PORTS


def test_port_enum_matches_the_registry_exactly():
    """If schedules/registry.yaml and tariffs.models.Port ever drift —
    impossible by construction today, since Port is built directly from
    the registry, but worth locking in as a regression guard — this is
    what would catch it."""
    assert {p.value for p in Port} == EXPECTED_PORTS


def test_schedule_path_for_known_port_with_no_date():
    path = schedule_path_for("durban")
    assert path.name == "tariffs_2024_2025.yaml"
    assert path.exists()


def test_schedule_path_for_known_port_within_validity_window():
    path = schedule_path_for("durban", date(2024, 11, 15))
    assert path.exists()


def test_schedule_path_for_known_port_outside_validity_window_raises():
    with pytest.raises(ValueError, match="no approved schedule covers"):
        schedule_path_for("durban", date(2030, 1, 1))


def test_schedule_path_for_unknown_port_raises():
    with pytest.raises(ValueError, match="no approved schedule covers"):
        schedule_path_for("not_a_real_port")


def test_engine_selects_by_port_and_arrival_date_not_a_fixed_default():
    """specs/EXTRACTION_SPEC.md §5.2: the schedule is chosen by port and
    date via the registry, not a single hardcoded file — this proves
    calculate() actually consults schedule_path_for(), not just that the
    only registered schedule happens to be the right answer regardless."""
    call = VesselCall(
        port=Port.DURBAN,
        gross_tonnage=51255,
        arrival=datetime(2024, 11, 15, 10, 12),
        chargeable_period_days=3.396,
        chargeable_period_basis=PeriodBasis.DAYS_ALONGSIDE_PROXY,
        number_of_operations=2,
    )
    result = calculate(call)
    assert result.light_dues.amount == pytest.approx(60062.04, abs=0.01)

    outside_window = call.model_copy(update={"arrival": datetime(2030, 1, 1)})
    with pytest.raises(ValueError, match="no approved schedule covers"):
        calculate(outside_window)


def test_currency_on_every_tariff_result_comes_from_the_selected_schedule_not_a_hardcoded_default():
    """specs/EXTRACTION_SPEC.md §5.2: "currency appears in every output"
    — proven by actually changing it on an injected schedule, not just
    checking it's "ZAR" (which the Pydantic field default is too)."""
    schedule = load_schedule().model_copy(
        update={"schedule_identity": load_schedule().schedule_identity.model_copy(update={"currency": "USD"})}
    )
    call = VesselCall(
        port=Port.DURBAN,
        gross_tonnage=51255,
        vessel_type=VesselType.BULK_CARRIER,
        chargeable_period_days=3.396,
        number_of_operations=2,
    )
    result = calculate(call, schedule=schedule)
    for tariff_result in result._all_results():
        assert tariff_result.currency == "USD", tariff_result.name
