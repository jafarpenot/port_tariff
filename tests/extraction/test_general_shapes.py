"""general_shapes.py -- pure schema tests, no LLM. Mirrors
test_schemas.py's style for the existing PricingShapes/Modifier."""

import pytest
from pydantic import ValidationError

from extraction.general_shapes import GeneralModifier, GeneralProposedRule, KeyedBand, ValueFormula


def test_flat_value_formula_is_valid():
    ValueFormula(kind="flat", flat_amount=100.0)


def test_linear_value_formula_is_valid():
    ValueFormula(kind="linear", rate=0.5, base=10.0)


def test_linear_value_formula_without_base_is_valid():
    ValueFormula(kind="linear", rate=0.5)  # base defaults to absent -- subsumes per_unit


def test_flat_value_formula_with_rate_is_rejected():
    with pytest.raises(ValidationError):
        ValueFormula(kind="flat", flat_amount=100.0, rate=0.5)


def test_linear_value_formula_without_rate_is_rejected():
    with pytest.raises(ValidationError):
        ValueFormula(kind="linear", base=10.0)


def test_keyed_table_can_represent_a_categorical_dimension():
    """The actual gap this module exists to close: RAK's towage table
    is keyed by tug name, not any numeric GT range -- a case the
    existing banded shape (extraction/schemas.py) cannot represent."""
    rule = GeneralProposedRule(
        key_dimension="tug type",
        bands=[
            KeyedBand(key="Ghalilah 9.6t Bollard Pull", value=ValueFormula(kind="flat", flat_amount=1569.0)),
            KeyedBand(key="Hobby 14t Bollard Pull", value=ValueFormula(kind="flat", flat_amount=1663.0)),
        ],
        multiplicity="per_service",
    )
    assert rule.key_dimension == "tug type"
    assert len(rule.bands) == 2


def test_keyed_table_can_still_represent_a_gt_banded_dimension():
    """The existing case the general shape must not regress -- a GT
    range as the key, linear value with a basis."""
    rule = GeneralProposedRule(
        key_dimension="gross tonnage band",
        bands=[
            KeyedBand(key="0-2,000 GT", value=ValueFormula(kind="flat", flat_amount=100.0)),
            KeyedBand(key="2,001+ GT", value=ValueFormula(kind="linear", base=100.0, rate=5.0)),
        ],
        basis="gross_tonnage",
        multiplicity="per_call",
    )
    assert rule.basis.value == "gross_tonnage"


def test_empty_bands_is_rejected():
    with pytest.raises(ValidationError):
        GeneralProposedRule(key_dimension="tug type", bands=[], multiplicity="per_service")


def test_modifier_with_a_linear_adjustment_is_valid():
    """The other real gap found live: TNPA's Saldanha delay fee is
    priced per half-hour, not a flat amount or a percentage -- the
    existing Modifier (extraction/schemas.py) has no way to represent
    this structurally, only via raw_description."""
    GeneralModifier(condition="delay after standby commences", adjustment=ValueFormula(kind="linear", rate=8050.76))


def test_modifier_with_percentage_is_valid():
    GeneralModifier(condition="after-hours surcharge", adjustment_percentage=25.0)


def test_modifier_with_raw_description_is_valid():
    GeneralModifier(condition="unusual case", raw_description="some verbatim quote")


def test_modifier_with_none_set_is_rejected():
    with pytest.raises(ValidationError):
        GeneralModifier(condition="after-hours surcharge")


def test_modifier_with_more_than_one_set_is_rejected():
    with pytest.raises(ValidationError):
        GeneralModifier(condition="after-hours surcharge", adjustment_percentage=25.0, raw_description="also this")
