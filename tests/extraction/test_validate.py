from extraction.schemas import (
    BandedShape,
    BasePlusIncrementShape,
    CanonicalCharge,
    ChargeExtraction,
    PerUnitShape,
    PricingShapes,
    ProposedRule,
    SemanticOutcome,
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


def test_unknown_basis_is_hard_and_lists_allowed_options():
    rule = ProposedRule(basis="displacement", rounding_mode="exact", pricing=_per_unit(1.0), multiplicity="per_call")
    result = validate_charge(_mapped(rule), PAGE_TEXTS)
    assert result.valid is False
    issue = next(i for i in result.issues if "basis" in i.message.lower())
    assert issue.severity is ValidationSeverity.HARD
    assert "gross_tonnage" in issue.allowed_options


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


def test_numeric_value_not_on_cited_page_is_a_warning_not_a_block():
    rule = ProposedRule(basis="gross_tonnage", rounding_mode="exact", pricing=_per_unit(999999.99), multiplicity="per_call")
    result = validate_charge(_mapped(rule), PAGE_TEXTS)
    assert result.valid is True  # warning, not hard
    assert any(i.severity is ValidationSeverity.WARNING for i in result.issues)


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
        per_port_rules={"Durban": _rate_rule(0.65), "Cape Town": ProposedRule(basis="displacement", rounding_mode="exact", pricing=_per_unit(1.0), multiplicity="per_call")},
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
