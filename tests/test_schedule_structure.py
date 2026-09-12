"""SPEC.md §10.2: validates the config's integrity, not its values.

These tests guard the extraction — they'd catch a port silently dropped
from a table, a missing source citation, or an unparseable rounding mode,
none of which the reference case would necessarily expose.
"""

import copy

import pytest
import yaml
from pydantic import ValidationError

from tariffs.models import Port, RoundingMode
from tariffs.schedule import DEFAULT_SCHEDULE_PATH, TariffSchedule, load_schedule

SCHEDULE = load_schedule()

with open(DEFAULT_SCHEDULE_PATH, encoding="utf-8") as f:
    RAW = yaml.safe_load(f)

ALL_PORTS = {p.value for p in Port}

# Tariffs/blocks with a per-port `ports: {...}` mapping — every Port enum
# member must have an entry, even if it's a duplicate of a shared column
# (e.g. Ngqura/Port Elizabeth) or an "Other"/"Other Ports" fallback value.
PORT_SPECIFIC_BLOCKS = [
    "towage",
    "vts",
    "pilotage",
    "berthing_services",
    "running_of_vessel_lines",
    "ordinary_working_hours",
]

# Top-level tariff blocks, each expected to carry its own source citation.
TOP_LEVEL_TARIFFS = [
    "light_dues",
    "port_dues",
    "towage",
    "vts",
    "pilotage",
    "berthing_services",
    "running_of_vessel_lines",
    "marine_services_incentive",
    "ordinary_working_hours",
]

# Tariffs whose `rounding` field is meaningful (marine_services_incentive
# and ordinary_working_hours have none — they aren't rate calculators).
RATED_TARIFFS = ["light_dues", "port_dues", "towage", "vts", "pilotage", "berthing_services", "running_of_vessel_lines"]


# ---------------------------------------------------------------------------
# Every port referenced by the Port enum has an entry
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("block_name", PORT_SPECIFIC_BLOCKS)
def test_every_port_has_an_entry(block_name):
    cfg = getattr(SCHEDULE, block_name)
    configured = set(cfg.ports.keys())
    missing = ALL_PORTS - configured
    extra = configured - ALL_PORTS
    assert not missing, f"{block_name}: missing ports {missing}"
    assert not extra, f"{block_name}: unexpected port keys {extra}"


# ---------------------------------------------------------------------------
# Band lists: ordered, contiguous, final band open-ended
# ---------------------------------------------------------------------------


def test_towage_bands_are_ordered_and_contiguous():
    for port, port_bands in SCHEDULE.towage.ports.items():
        bands = port_bands.bands
        assert bands[0].min_gt_exclusive == 0, f"{port}: first band must start at 0"
        for prev, curr in zip(bands, bands[1:]):
            assert curr.min_gt_exclusive == prev.max_gt_inclusive, (
                f"{port}: band boundary mismatch between {prev} and {curr} "
                "(min_gt_exclusive must equal the previous band's max_gt_inclusive)"
            )


def test_towage_final_band_has_null_upper_bound():
    for port, port_bands in SCHEDULE.towage.ports.items():
        assert port_bands.bands[-1].max_gt_inclusive is None, f"{port}: final band must be open-ended"


def test_craft_allocation_bands_are_ordered_and_contiguous():
    bands = SCHEDULE.towage.craft_allocation.bands
    assert bands[0].min_gt_exclusive == 0
    for prev, curr in zip(bands, bands[1:]):
        assert curr.min_gt_exclusive == prev.max_gt_inclusive
    assert bands[-1].max_gt_inclusive is None


# ---------------------------------------------------------------------------
# n/a combinations are explicit null (SPEC.md §5.3, §7.3)
# ---------------------------------------------------------------------------


def test_east_london_has_no_band_above_100000():
    top_band = SCHEDULE.towage.ports["east_london"].bands[-1]
    assert top_band.base is None
    assert top_band.increment_above_gt is None
    assert top_band.per_100t is None


def test_mossel_bay_has_no_bands_above_50000():
    bands = SCHEDULE.towage.ports["mossel_bay"].bands
    for band in bands[-2:]:  # 50,000-100,000 and >100,000
        assert band.base is None
        assert band.increment_above_gt is None
        assert band.per_100t is None


def test_missing_band_key_fails_at_load_time():
    """A missing key (as opposed to an explicit null) must fail validation
    — SPEC.md §5.3 distinguishes the two."""
    bad = copy.deepcopy(RAW)
    del bad["towage"]["ports"]["durban"]["bands"][0]["per_100t"]
    with pytest.raises(ValidationError):
        TariffSchedule.model_validate(bad)


# ---------------------------------------------------------------------------
# Every rate block carries a source with a section and a page
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("tariff_name", TOP_LEVEL_TARIFFS)
def test_top_level_blocks_carry_source(tariff_name):
    cfg = getattr(SCHEDULE, tariff_name)
    assert cfg.source.section
    assert cfg.source.page > 0


def test_port_dues_reduction_blocks_carry_source():
    for name, reduction in SCHEDULE.port_dues.reductions.items():
        assert reduction.source.section, name
        assert reduction.source.page > 0, name


def test_port_dues_small_vessel_minimum_fee_carries_source():
    fee = SCHEDULE.port_dues.small_vessel_minimum_fee
    assert fee.source.section
    assert fee.source.page > 0


def test_towage_surcharges_and_craft_allocation_carry_source():
    assert SCHEDULE.towage.surcharges.source.section
    assert SCHEDULE.towage.surcharges.source.page > 0
    assert SCHEDULE.towage.craft_allocation.source.section
    assert SCHEDULE.towage.craft_allocation.source.page > 0


def test_pilotage_plo_duties_and_surcharges_carry_source():
    assert SCHEDULE.pilotage.plo_duties.source.section
    assert SCHEDULE.pilotage.plo_duties.source.page > 0
    assert SCHEDULE.pilotage.surcharges.source.section
    assert SCHEDULE.pilotage.surcharges.source.page > 0


# ---------------------------------------------------------------------------
# Every `rounding` value parses to the enum
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("tariff_name", RATED_TARIFFS)
def test_rounding_parses_to_enum(tariff_name):
    cfg = getattr(SCHEDULE, tariff_name)
    assert isinstance(cfg.rounding, RoundingMode)


def test_unknown_rounding_value_fails_at_load_time():
    bad = copy.deepcopy(RAW)
    bad["light_dues"]["rounding"] = "made_up_mode"
    with pytest.raises(ValidationError):
        TariffSchedule.model_validate(bad)
