"""SPEC.md §10.4: GT exactly at each band edge, asserting the
lower-exclusive/upper-inclusive convention (SPEC.md §5.4). Also the VTS
minimum fee and the small-vessel port dues minimum.
"""

import math

import pytest

from tariffs.models import RoundingMode
from tariffs.schedule import load_schedule
from tariffs.shapes import banded_base_plus_increment, per_unit_rate

SCHEDULE = load_schedule()
DURBAN_BANDS = SCHEDULE.towage.ports["durban"].bands

# Each row: GT, the band expected to apply (by its base/increment/rate),
# computed from the band definitions themselves rather than hardcoded
# totals, so this test tracks the config rather than duplicating it.
_BOUNDARY_CASES = [
    (2000, 8140.00, None, None),  # exactly on the boundary -> lower band (inclusive)
    (2001, 12633.99, 2000, 268.99),  # just above -> next band
    (10000, 12633.99, 2000, 268.99),  # exactly on the boundary -> still the lower band
    (10001, 38494.51, 10000, 84.95),  # just above -> next band
    (50000, 38494.51, 10000, 84.95),  # exactly on the boundary -> still the lower band
    (50001, 73118.07, 50000, 32.24),  # just above -> next band
    (100000, 73118.07, 50000, 32.24),  # exactly on the boundary -> still the lower band
    (100001, 93548.13, 100000, 23.65),  # just above -> final, open-ended band
]


@pytest.mark.parametrize("gt,band_base,increment_above_gt,rate", _BOUNDARY_CASES)
def test_towage_band_boundaries_durban(gt, band_base, increment_above_gt, rate):
    expected = band_base if increment_above_gt is None else band_base + math.ceil((gt - increment_above_gt) / 100) * rate
    assert banded_base_plus_increment(gt, DURBAN_BANDS) == pytest.approx(expected, abs=0.01)


def test_towage_2000_and_2001_fall_in_different_bands():
    assert banded_base_plus_increment(2000, DURBAN_BANDS) == pytest.approx(8140.00, abs=0.01)
    assert banded_base_plus_increment(2001, DURBAN_BANDS) != pytest.approx(8140.00, abs=0.01)


def test_towage_10000_and_10001_fall_in_different_bands():
    at_10000 = banded_base_plus_increment(10000, DURBAN_BANDS)
    at_10001 = banded_base_plus_increment(10001, DURBAN_BANDS)
    assert at_10000 < at_10001


def test_towage_50000_and_50001_fall_in_different_bands():
    at_50000 = banded_base_plus_increment(50000, DURBAN_BANDS)
    at_50001 = banded_base_plus_increment(50001, DURBAN_BANDS)
    assert at_50000 < at_50001


def test_towage_100000_and_100001_fall_in_different_bands():
    at_100000 = banded_base_plus_increment(100000, DURBAN_BANDS)
    at_100001 = banded_base_plus_increment(100001, DURBAN_BANDS)
    assert at_100000 < at_100001


# ---------------------------------------------------------------------------
# VTS minimum fee (SPEC.md §7.4)
# ---------------------------------------------------------------------------


def test_vts_minimum_fee_applies_for_a_small_vessel():
    rate = SCHEDULE.vts.ports["durban"].rate_per_gt
    minimum = SCHEDULE.vts.minimum_fee
    amount = per_unit_rate(gt=100, rate=rate, rounding=RoundingMode.EXACT, minimum=minimum)
    assert amount == pytest.approx(minimum, abs=0.01)


def test_vts_minimum_fee_does_not_apply_above_threshold():
    rate = SCHEDULE.vts.ports["durban"].rate_per_gt
    minimum = SCHEDULE.vts.minimum_fee
    large_gt = 10000
    amount = per_unit_rate(gt=large_gt, rate=rate, rounding=RoundingMode.EXACT, minimum=minimum)
    assert amount == pytest.approx(large_gt * rate, abs=0.01)
    assert amount > minimum


def test_vts_minimum_fee_threshold_boundary():
    rate = SCHEDULE.vts.ports["durban"].rate_per_gt
    minimum = SCHEDULE.vts.minimum_fee
    threshold_gt = minimum / rate  # exact GT where rate x GT == minimum

    just_below = per_unit_rate(gt=threshold_gt - 1, rate=rate, rounding=RoundingMode.EXACT, minimum=minimum)
    just_above = per_unit_rate(gt=threshold_gt + 1, rate=rate, rounding=RoundingMode.EXACT, minimum=minimum)

    assert just_below == pytest.approx(minimum, abs=0.01)
    assert just_above > minimum


# ---------------------------------------------------------------------------
# Small-vessel port dues minimum (SPEC.md §7.2)
# Out of scope for a commercial vessel call — no calculator applies it in
# v1 — so this is a presence/provenance check, not a calculation boundary.
# ---------------------------------------------------------------------------


def test_small_vessel_port_dues_minimum_fee_is_present_with_provenance():
    fee = SCHEDULE.port_dues.small_vessel_minimum_fee
    assert fee.amount == 470.98
    assert fee.source.section == "4.1.1"
    assert fee.source.page == 21
