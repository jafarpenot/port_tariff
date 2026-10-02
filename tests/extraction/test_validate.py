import pytest
from pydantic import ValidationError

from extraction.schemas import (
    BandedShape,
    BasePlusIncrementShape,
    CanonicalCharge,
    ChargeExtraction,
    DailyRateTier,
    FreePeriodTieredDailyRateShape,
    KeyedRateRow,
    KeyedRateShape,
    Modifier,
    PerUnitShape,
    PricingShapes,
    ProposedRule,
    SemanticOutcome,
    TieredUnitRateShape,
    TieredUnitRateTier,
    ValidationSeverity,
)
from extraction.validate import validate_charge

PAGE_TEXTS = {1: "Some opening text.", 2: "Rate 12.5 per unit, minimum 100."}


def _mapped(rule: ProposedRule, pages=None) -> ChargeExtraction:
    return ChargeExtraction(
        charge=CanonicalCharge.LIGHT_DUES,
        outcome=SemanticOutcome.MAPPED,
        proposed_rule=rule,
        provenance_pages=pages or [2],
    )


def _per_unit(rate: float) -> PricingShapes:
    return PricingShapes(per_unit=PerUnitShape(selected=True, rate=rate))


def _banded(bands: list[dict]) -> PricingShapes:
    return PricingShapes(banded=BandedShape(selected=True, bands=bands))


def _keyed_rate(key_dimension: str, keys: list[KeyedRateRow]) -> PricingShapes:
    return PricingShapes(keyed_rate=KeyedRateShape(selected=True, key_dimension=key_dimension, keys=keys))


def _tiered_unit_rate(tiers: list[TieredUnitRateTier]) -> PricingShapes:
    return PricingShapes(tiered_unit_rate=TieredUnitRateShape(selected=True, tiers=tiers))


def _free_period_tiered_daily_rate(free_days: float, tiers: list[DailyRateTier]) -> PricingShapes:
    return PricingShapes(free_period_tiered_daily_rate=FreePeriodTieredDailyRateShape(selected=True, free_days=free_days, tiers=tiers))


def test_valid_per_unit_rule_passes():
    rule = ProposedRule(basis="gross_tonnage", rounding_mode="exact", pricing=_per_unit(12.5), multiplicity="per_call")
    result = validate_charge(_mapped(rule), PAGE_TEXTS)
    assert result.valid is True
    assert result.issues == []


def test_valid_banded_rule_passes():
    rule = ProposedRule(
        basis="gross_tonnage",
        rounding_mode="ceil_to_unit",
        rounding_unit=100,
        pricing=_banded(
            [
                {"min_exclusive": 0, "max_inclusive": 2000, "base": 100.0, "increment_above": None, "per_unit_rate": None},
                {"min_exclusive": 2000, "max_inclusive": None, "base": 200.0, "increment_above": 2000, "per_unit_rate": 5.0},
            ]
        ),
        multiplicity="per_service",
    )
    result = validate_charge(_mapped(rule), PAGE_TEXTS)
    assert result.valid is True


def test_unknown_basis_is_rejected_at_construction_not_at_validate_time():
    """basis/rounding_mode/multiplicity are real enums on ProposedRule
    (extraction/schemas.py) — an invalid value is now structurally
    impossible to construct at all, same technique as pricing_type's own
    closed-shape fix. Validate no longer needs to catch this after the
    fact."""
    with pytest.raises(ValidationError, match="basis"):
        ProposedRule(basis="displacement", rounding_mode="exact", pricing=_per_unit(1.0), multiplicity="per_call")


def test_ceil_to_unit_without_a_unit_is_hard():
    rule = ProposedRule(basis="gross_tonnage", rounding_mode="ceil_to_unit", pricing=_per_unit(1.0), multiplicity="per_call")
    result = validate_charge(_mapped(rule), PAGE_TEXTS)
    assert result.valid is False


def test_band_not_starting_at_zero_is_hard():
    rule = ProposedRule(
        basis="gross_tonnage",
        rounding_mode="ceil_to_unit",
        rounding_unit=100,
        pricing=_banded([{"min_exclusive": 5, "max_inclusive": None, "base": 1.0, "increment_above": None, "per_unit_rate": None}]),
        multiplicity="per_service",
    )
    result = validate_charge(_mapped(rule), PAGE_TEXTS)
    assert result.valid is False


def test_band_gap_between_bands_is_hard():
    rule = ProposedRule(
        basis="gross_tonnage",
        rounding_mode="ceil_to_unit",
        rounding_unit=100,
        pricing=_banded(
            [
                {"min_exclusive": 0, "max_inclusive": 1000, "base": 1.0, "increment_above": None, "per_unit_rate": None},
                {"min_exclusive": 2000, "max_inclusive": None, "base": 2.0, "increment_above": 2000, "per_unit_rate": 1.0},  # gap: 1000 -> 2000
            ]
        ),
        multiplicity="per_service",
    )
    result = validate_charge(_mapped(rule), PAGE_TEXTS)
    assert result.valid is False


def test_final_band_not_open_ended_is_hard():
    rule = ProposedRule(
        basis="gross_tonnage",
        rounding_mode="ceil_to_unit",
        rounding_unit=100,
        pricing=_banded([{"min_exclusive": 0, "max_inclusive": 1000, "base": 1.0, "increment_above": None, "per_unit_rate": None}]),
        multiplicity="per_service",
    )
    result = validate_charge(_mapped(rule), PAGE_TEXTS)
    assert result.valid is False


def test_cited_page_out_of_range_is_hard():
    rule = ProposedRule(basis="gross_tonnage", rounding_mode="exact", pricing=_per_unit(1.0), multiplicity="per_call")
    result = validate_charge(_mapped(rule, pages=[999]), PAGE_TEXTS)
    assert result.valid is False
    assert any("999" in i.message for i in result.issues)


def test_negative_smoke_calculation_result_is_hard():
    rule = ProposedRule(basis="gross_tonnage", rounding_mode="exact", pricing=_per_unit(-5.0), multiplicity="per_call")
    result = validate_charge(_mapped(rule), PAGE_TEXTS)
    assert result.valid is False
    assert any("negative" in i.message for i in result.issues)


def test_valid_keyed_rate_rule_passes():
    rule = ProposedRule(
        basis="hours",
        rounding_mode="exact",
        pricing=_keyed_rate("tug type", [KeyedRateRow(key="Ghalilah", rate=1569.0), KeyedRateRow(key="Osprey", rate=6516.0)]),
        multiplicity="per_call",
    )
    result = validate_charge(_mapped(rule), PAGE_TEXTS)
    assert result.valid is True
    assert result.issues == []


def test_keyed_rate_duplicate_key_is_hard():
    rule = ProposedRule(
        basis="hours",
        rounding_mode="exact",
        pricing=_keyed_rate("tug type", [KeyedRateRow(key="Ghalilah", rate=1569.0), KeyedRateRow(key="Ghalilah", rate=2000.0)]),
        multiplicity="per_call",
    )
    result = validate_charge(_mapped(rule), PAGE_TEXTS)
    assert result.valid is False
    assert any("duplicate" in i.message for i in result.issues)


def test_keyed_rate_negative_value_is_hard():
    rule = ProposedRule(
        basis="hours",
        rounding_mode="exact",
        pricing=_keyed_rate("tug type", [KeyedRateRow(key="Ghalilah", rate=-1.0)]),
        multiplicity="per_call",
    )
    result = validate_charge(_mapped(rule), PAGE_TEXTS)
    assert result.valid is False
    assert any("negative" in i.message for i in result.issues)


def test_keyed_rate_row_requires_exactly_one_value():
    with pytest.raises(ValidationError):
        KeyedRateRow(key="Ghalilah")
    with pytest.raises(ValidationError):
        KeyedRateRow(key="Ghalilah", flat_amount=1.0, rate=2.0)


def test_valid_tiered_unit_rate_rule_passes():
    rule = ProposedRule(
        basis="cargo_tonnes",
        rounding_mode="exact",
        pricing=_tiered_unit_rate(
            [
                TieredUnitRateTier(min_exclusive=0, max_inclusive=25000, rate=1.51),
                TieredUnitRateTier(min_exclusive=25000, max_inclusive=40000, rate=1.31),
                TieredUnitRateTier(min_exclusive=40000, max_inclusive=None, rate=0.74),
            ]
        ),
        multiplicity="per_call",
    )
    result = validate_charge(_mapped(rule), PAGE_TEXTS)
    assert result.valid is True
    assert result.issues == []


def test_tiered_unit_rate_gap_between_tiers_is_hard():
    rule = ProposedRule(
        basis="cargo_tonnes",
        rounding_mode="exact",
        pricing=_tiered_unit_rate(
            [
                TieredUnitRateTier(min_exclusive=0, max_inclusive=1000, rate=1.0),
                TieredUnitRateTier(min_exclusive=2000, max_inclusive=None, rate=2.0),  # gap: 1000 -> 2000
            ]
        ),
        multiplicity="per_call",
    )
    result = validate_charge(_mapped(rule), PAGE_TEXTS)
    assert result.valid is False


def test_tiered_unit_rate_negative_rate_is_hard():
    rule = ProposedRule(
        basis="cargo_tonnes",
        rounding_mode="exact",
        pricing=_tiered_unit_rate([TieredUnitRateTier(min_exclusive=0, max_inclusive=None, rate=-1.0)]),
        multiplicity="per_call",
    )
    result = validate_charge(_mapped(rule), PAGE_TEXTS)
    assert result.valid is False
    assert any("negative" in i.message for i in result.issues)


def test_valid_free_period_tiered_daily_rate_rule_passes():
    rule = ProposedRule(
        basis="gross_tonnage",
        rounding_mode="exact",
        pricing=_free_period_tiered_daily_rate(
            10,
            [
                DailyRateTier(up_to_day=5, rate_per_unit_per_day=24.93),
                DailyRateTier(up_to_day=10, rate_per_unit_per_day=49.60),
                DailyRateTier(up_to_day=None, rate_per_unit_per_day=99.20),
            ],
        ),
        multiplicity="per_call",
    )
    result = validate_charge(_mapped(rule), PAGE_TEXTS)
    assert result.valid is True
    assert result.issues == []


def test_free_period_tiered_daily_rate_negative_free_days_is_hard():
    rule = ProposedRule(
        basis="gross_tonnage",
        rounding_mode="exact",
        pricing=_free_period_tiered_daily_rate(-1, [DailyRateTier(up_to_day=None, rate_per_unit_per_day=1.0)]),
        multiplicity="per_call",
    )
    result = validate_charge(_mapped(rule), PAGE_TEXTS)
    assert result.valid is False


def test_free_period_tiered_daily_rate_final_tier_not_open_ended_is_hard():
    rule = ProposedRule(
        basis="gross_tonnage",
        rounding_mode="exact",
        pricing=_free_period_tiered_daily_rate(0, [DailyRateTier(up_to_day=5, rate_per_unit_per_day=1.0)]),
        multiplicity="per_call",
    )
    result = validate_charge(_mapped(rule), PAGE_TEXTS)
    assert result.valid is False



def test_bundled_without_included_in_is_hard():
    extraction = ChargeExtraction(charge=CanonicalCharge.VTS, outcome=SemanticOutcome.BUNDLED, provenance_pages=[2])
    result = validate_charge(extraction, PAGE_TEXTS)
    assert result.valid is False


def test_bundled_with_included_in_is_valid():
    extraction = ChargeExtraction(
        charge=CanonicalCharge.VTS, outcome=SemanticOutcome.BUNDLED, included_in=CanonicalCharge.PORT_DUES, provenance_pages=[2]
    )
    result = validate_charge(extraction, PAGE_TEXTS)
    assert result.valid is True


def test_unmapped_without_source_text_is_hard():
    extraction = ChargeExtraction(charge=CanonicalCharge.TOWAGE, outcome=SemanticOutcome.UNMAPPED, provenance_pages=[2])
    result = validate_charge(extraction, PAGE_TEXTS)
    assert result.valid is False


def test_not_present_needs_nothing_else_and_is_valid():
    extraction = ChargeExtraction(charge=CanonicalCharge.PILOTAGE, outcome=SemanticOutcome.NOT_PRESENT)
    result = validate_charge(extraction, PAGE_TEXTS)
    assert result.valid is True


def _rate_rule(rate=1.0):
    return ProposedRule(basis="gross_tonnage", rounding_mode="exact", pricing=_per_unit(rate), multiplicity="per_call")


def test_varies_by_port_with_all_valid_rules_is_valid():
    extraction = ChargeExtraction(
        charge=CanonicalCharge.VTS,
        outcome=SemanticOutcome.MAPPED,
        varies_by_port=True,
        per_port_rules={"Durban": _rate_rule(0.65), "Cape Town": _rate_rule(0.54)},
        provenance_pages=[2],
    )
    result = validate_charge(extraction, PAGE_TEXTS)
    assert result.valid is True


def test_varies_by_port_with_empty_per_port_rules_is_hard():
    extraction = ChargeExtraction(charge=CanonicalCharge.VTS, outcome=SemanticOutcome.MAPPED, varies_by_port=True)
    result = validate_charge(extraction, PAGE_TEXTS)
    assert result.valid is False


def test_varies_by_port_one_bad_port_fails_and_names_the_port():
    extraction = ChargeExtraction(
        charge=CanonicalCharge.VTS,
        outcome=SemanticOutcome.MAPPED,
        varies_by_port=True,
        per_port_rules={
            "Durban": _rate_rule(0.65),
            "Cape Town": ProposedRule(basis="gross_tonnage", rounding_mode="ceil_to_unit", pricing=_per_unit(1.0), multiplicity="per_call"),  # missing rounding_unit
        },
        provenance_pages=[2],
    )
    result = validate_charge(extraction, PAGE_TEXTS)
    assert result.valid is False
    assert any(i.message.startswith("[Cape Town]") and i.severity is ValidationSeverity.HARD for i in result.issues)
    assert not any(
        i.message.startswith("[Durban]") and i.severity is ValidationSeverity.HARD for i in result.issues
    )  # Durban's own rule was structurally fine (a citation warning may still fire — PAGE_TEXTS is a fixture, not the real book)


def test_varies_by_port_false_ignores_per_port_rules_and_needs_proposed_rule():
    extraction = ChargeExtraction(
        charge=CanonicalCharge.LIGHT_DUES, outcome=SemanticOutcome.MAPPED, varies_by_port=False, per_port_rules={"Durban": _rate_rule()}
    )
    result = validate_charge(extraction, PAGE_TEXTS)
    assert result.valid is False  # proposed_rule missing — per_port_rules doesn't count when varies_by_port is false
