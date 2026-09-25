"""extraction/schemas.py's PricingShapes: a fixed, closed shape per
pricing_type (no free dict) that a model must set selected=true on
exactly one of, fully filled in, leaving the other three untouched.
Replaces the old Validate-level "missing required pricing param" test —
that failure mode is now caught here, at construction, not downstream.
"""

import pytest
from pydantic import ValidationError

from extraction.schemas import BandedShape, BasePlusIncrementShape, PerUnitShape, PricingShapes


def test_a_fully_specified_shape_is_valid():
    shapes = PricingShapes(base_plus_increment=BasePlusIncrementShape(selected=True, base=10.0, rate=1.0))
    assert shapes.pricing_type == "base_plus_increment"
    assert shapes.params == {"base": 10.0, "rate": 1.0}


def test_missing_required_field_on_the_selected_shape_is_rejected():
    with pytest.raises(ValidationError, match="base_plus_increment"):
        PricingShapes(base_plus_increment=BasePlusIncrementShape(selected=True, base=10.0))  # rate missing


def test_no_shape_selected_is_rejected():
    with pytest.raises(ValidationError):
        PricingShapes()


def test_two_shapes_selected_is_rejected():
    with pytest.raises(ValidationError):
        PricingShapes(
            per_unit=PerUnitShape(selected=True, rate=1.0),
            base_plus_increment=BasePlusIncrementShape(selected=True, base=1.0, rate=1.0),
        )


def test_an_unselected_shape_with_fields_set_is_rejected():
    """A model that fills in a shape it didn't select is a real signal
    something's wrong, not something to silently ignore."""
    with pytest.raises(ValidationError, match="per_unit"):
        PricingShapes(
            base_plus_increment=BasePlusIncrementShape(selected=True, base=1.0, rate=1.0),
            per_unit=PerUnitShape(selected=False, rate=5.0),
        )


def test_banded_requires_at_least_one_band():
    with pytest.raises(ValidationError, match="banded"):
        PricingShapes(banded=BandedShape(selected=True, bands=[]))


def test_banded_params_returns_bands_as_plain_dicts():
    shapes = PricingShapes(
        banded=BandedShape(
            selected=True,
            bands=[{"min_exclusive": 0, "max_inclusive": None, "base": 1.0, "increment_above": None, "per_unit_rate": None}],
        )
    )
    assert shapes.params["bands"] == [{"min_exclusive": 0, "max_inclusive": None, "base": 1.0, "increment_above": None, "per_unit_rate": None}]
