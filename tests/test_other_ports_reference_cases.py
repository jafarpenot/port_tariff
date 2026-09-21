"""SPEC.md §2's reference case only covers Durban. These four cases,
hand-designed and verified against `calculate()`, extend expected-value
coverage to four more of the eight ports — each one targeting a specific
extraction/implementation risk, not just a random GT.

Unlike SPEC.md's reference case, these numbers do NOT come from an
external answer key — they were computed by hand from the same config
this package ships, as a second, independent check that the formulas
apply the (separately verified) per-port rates correctly. If one of
these ever needs to change, change the test, not the engine, only after
re-deriving the expected value by hand from `config/tariffs_2024_2025.yaml`
— never adjust a case just to make it pass.
"""

import pytest

from tariffs.engine import calculate
from tariffs.models import Port, VesselCall


def _call(port: Port, gt: float, days: float, ops: int = 2) -> VesselCall:
    return VesselCall(port=port, gross_tonnage=gt, number_of_operations=ops, chargeable_period_days=days)


def test_cape_town_low_towage_band_and_054_vts_rate():
    """GT 8,500 sits in towage's lowest band; Cape Town is on the 0.54
    VTS rate (not 0.65, which only Durban/Saldanha get)."""
    result = calculate(_call(Port.CAPE_TOWN, gt=8500, days=2.5))
    totals = result.totals()

    assert totals["light_dues"] == pytest.approx(9951.80, abs=0.01)
    assert totals["vts_dues"] == pytest.approx(4590.00, abs=0.01)
    assert totals["pilotage_dues"] == pytest.approx(14418.78, abs=0.01)
    assert totals["towage_dues"] == pytest.approx(41099.04, abs=0.01)
    assert totals["berthing_services"] == pytest.approx(8641.06, abs=0.01)
    # 28,662.43, not 28,662.42: basic and incremental are rounded to
    # cents SEPARATELY before summing (calculators.port_dues), which is
    # the convention the actual Durban answer key validates — a hand
    # calculation that instead sums first and rounds once lands one cent
    # lower at this exact GT/day combination (16382.05 + 12280.375 =
    # 28662.425, which rounds down to .42 under banker's rounding, vs
    # 16382.05 + round(12280.375, 2) = 16382.05 + 12280.38 = 28662.43).
    assert totals["port_dues"] == pytest.approx(28662.43, abs=0.01)


def test_saldanha_top_towage_band_and_second_065_vts_port():
    """GT 150,000 is in towage's open-ended top band; confirms VTS's
    0.65 rate isn't hardcoded to Durban specifically."""
    result = calculate(_call(Port.SALDANHA, gt=150000, days=4))
    totals = result.totals()

    assert totals["light_dues"] == pytest.approx(175620.00, abs=0.01)
    assert totals["vts_dues"] == pytest.approx(97500.00, abs=0.01)
    assert totals["pilotage_dues"] == pytest.approx(60327.14, abs=0.01)
    assert totals["towage_dues"] == pytest.approx(270975.26, abs=0.01)
    assert totals["berthing_services"] == pytest.approx(58922.68, abs=0.01)
    assert totals["port_dues"] == pytest.approx(635835.00, abs=0.01)


def test_east_london_falls_to_other_column_for_pilotage_and_berthing():
    """East London has its own towage column but no pilotage column (falls
    to "Other": 6,547.45 + 10.49) and no berthing column ("Other Ports").
    A column-alignment mistake would silently substitute a named port's
    rate instead."""
    result = calculate(_call(Port.EAST_LONDON, gt=25000, days=3))
    totals = result.totals()

    assert totals["light_dues"] == pytest.approx(29270.00, abs=0.01)
    assert totals["vts_dues"] == pytest.approx(13500.00, abs=0.01)
    assert totals["pilotage_dues"] == pytest.approx(18339.90, abs=0.01)
    assert totals["towage_dues"] == pytest.approx(75914.82, abs=0.01)
    assert totals["berthing_services"] == pytest.approx(12443.82, abs=0.01)
    assert totals["port_dues"] == pytest.approx(91525.00, abs=0.01)


def test_richards_bay_exact_towage_band_boundary():
    """GT exactly 10,000 — under the lower-exclusive/upper-inclusive
    convention this sits in the 2,001-10,000 band (70,092.54 total). If
    boundary handling were flipped, it would land in the next band
    (79,999.76 base alone) — a ~14% error no other case here reveals."""
    result = calculate(_call(Port.RICHARDS_BAY, gt=10000, days=1.5))
    totals = result.totals()

    assert totals["light_dues"] == pytest.approx(11708.00, abs=0.01)
    assert totals["vts_dues"] == pytest.approx(5400.00, abs=0.01)
    assert totals["pilotage_dues"] == pytest.approx(64106.92, abs=0.01)
    assert totals["towage_dues"] == pytest.approx(70092.54, abs=0.01)
    assert totals["berthing_services"] == pytest.approx(9043.78, abs=0.01)
    assert totals["port_dues"] == pytest.approx(27941.50, abs=0.01)
