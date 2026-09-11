"""SPEC.md §2 and §10.1: the six reference values, to the cent, from the
supplied VesselCall. These numbers come from outside this system and are
NOT to be adjusted — if a test here fails, fix the config or the code.
"""

from datetime import datetime

import pytest

from tariffs.engine import calculate
from tariffs.models import PeriodBasis, Port, VesselCall, VesselType


def _reference_call(*, gross_tonnage: float, chargeable_period_days: float) -> VesselCall:
    return VesselCall(
        vessel_name="SUDESTADA",
        port=Port.DURBAN,
        gross_tonnage=gross_tonnage,
        length_overall_m=229.2,
        vessel_type=VesselType.BULK_CARRIER,
        arrival=datetime(2024, 11, 15, 10, 12),
        departure=datetime(2024, 11, 22, 13, 0),
        chargeable_period_days=chargeable_period_days,
        chargeable_period_basis=PeriodBasis.DAYS_ALONGSIDE_PROXY,
        number_of_operations=2,
    )


def test_reference_case_exact():
    """GT 51,255 and 3.396 days — the answer key's own inputs (SPEC.md §2)."""
    call = _reference_call(gross_tonnage=51255, chargeable_period_days=3.396)
    result = calculate(call)

    assert result.light_dues.amount == pytest.approx(60062.04, abs=0.01)
    assert result.port_dues.amount == pytest.approx(199549.22, abs=0.01)
    assert result.towage_dues.amount == pytest.approx(147074.38, abs=0.01)
    assert result.vts_dues.amount == pytest.approx(33315.75, abs=0.01)
    assert result.pilotage_dues.amount == pytest.approx(47189.94, abs=0.01)
    assert result.berthing_services.amount == pytest.approx(19639.50, abs=0.01)

    # §7.6: the assignment's "running of vessel lines dues" benchmark
    # reconciles to berthing_services, not to the §3.9 calculator.
    assert result.running_of_vessel_lines.amount is None
    assert result.running_of_vessel_lines.warnings == []


def test_reference_case_documented_deviation_with_sheet_rounded_inputs():
    """GT 51,300 and 3.39 days — the vessel sheet's own (rounded/truncated)
    figures. Both deviations are documented input-rounding artefacts
    (SPEC.md §2), not defects. VTS and port dues deviate; the other four
    tariffs are unaffected because ceil(GT/100) is 513 either way.
    """
    call = _reference_call(gross_tonnage=51300, chargeable_period_days=3.39)
    result = calculate(call)

    assert result.vts_dues.amount == pytest.approx(33345.00, abs=0.01)
    assert result.port_dues.amount == pytest.approx(199371.35, abs=0.01)

    assert result.light_dues.amount == pytest.approx(60062.04, abs=0.01)
    assert result.towage_dues.amount == pytest.approx(147074.38, abs=0.01)
    assert result.pilotage_dues.amount == pytest.approx(47189.94, abs=0.01)
    assert result.berthing_services.amount == pytest.approx(19639.50, abs=0.01)
