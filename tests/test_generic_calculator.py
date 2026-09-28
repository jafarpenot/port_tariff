"""tariffs/generic_calculator.py: a data-driven calculator built from
an extracted ProposedRule, instead of tariffs/calculators.py's one
hand-written function per charge. v1, base rate only.
"""

import pytest

from extraction.schemas import (
    BandedShape,
    BasePlusIncrementShape,
    BasePlusIncrementTimesDurationShape,
    CanonicalCharge,
    ChargeReportEntry,
    Modifier,
    PerUnitShape,
    PricingBand,
    PricingShapes,
    ProposedRule,
    SemanticOutcome,
)
from tariffs.generic_calculator import compile_charge, compile_report, compute_base_amount, compute_charge, to_tariff_plan
from tariffs.models import Port, VesselCall

_CALL = VesselCall(port=Port.DURBAN, gross_tonnage=51_255)


def _rule(pricing: PricingShapes, **kwargs) -> ProposedRule:
    return ProposedRule(
        basis=kwargs.pop("basis", "gross_tonnage"),
        rounding_mode=kwargs.pop("rounding_mode", "exact"),
        rounding_unit=kwargs.pop("rounding_unit", None),
        pricing=pricing,
        multiplicity=kwargs.pop("multiplicity", "per_call"),
        **kwargs,
    )


def test_per_unit_shape():
    rule = _rule(PricingShapes(per_unit=PerUnitShape(selected=True, rate=1.0)), rounding_mode="ceil_to_unit", rounding_unit=100)
    # ceil(51255/100) = 513 units x rate 1.0
    assert compute_base_amount(rule, 51_255) == pytest.approx(513.0)


def test_base_plus_increment_shape():
    rule = _rule(PricingShapes(base_plus_increment=BasePlusIncrementShape(selected=True, base=1000.0, rate=2.0)), rounding_mode="ceil_to_unit", rounding_unit=100)
    # base 1000 + ceil(51255/100)=513 x rate 2.0 = 1000 + 1026
    assert compute_base_amount(rule, 51_255) == pytest.approx(2026.0)


def test_banded_shape():
    bands = [
        PricingBand(min_exclusive=0, max_inclusive=100_000, base=500.0, increment_above=0.0, per_unit_rate=3.0),
        PricingBand(min_exclusive=100_000, max_inclusive=None, base=500.0, increment_above=100_000.0, per_unit_rate=5.0),
    ]
    rule = _rule(PricingShapes(banded=BandedShape(selected=True, bands=bands)), rounding_mode="exact")
    # first band: base 500 + ceil((51255 - increment_above=0) / 100) x per_100t 3.0
    assert compute_base_amount(rule, 51_255) == pytest.approx(500.0 + 513 * 3.0)


def test_base_plus_increment_times_duration_shape_requires_days():
    rule = _rule(PricingShapes(base_plus_increment_times_duration=BasePlusIncrementTimesDurationShape(selected=True, basic_rate=10.0, daily_rate=1.0)), rounding_mode="ceil_to_unit", rounding_unit=100)
    with pytest.raises(ValueError, match="requires `days`"):
        compute_base_amount(rule, 51_255)
    # ceil(51255/100)=513 units: basic = 513*10, incremental = 513*1*3.396
    amount = compute_base_amount(rule, 51_255, days=3.396)
    assert amount == pytest.approx(513 * 10.0 + 513 * 1.0 * 3.396)


def test_maximum_caps_the_total_not_each_service():
    rule = _rule(
        PricingShapes(per_unit=PerUnitShape(selected=True, rate=100.0)),
        rounding_mode="exact",
        multiplicity="per_service",
        maximum=150.0,
    )
    call = VesselCall(port=Port.DURBAN, gross_tonnage=1.0, number_of_operations=2)
    result = compute_charge(rule, call, name="test_charge")
    # per-service amount = 1 x 100 = 100; x2 services = 200, capped to 150
    assert result.amount == pytest.approx(150.0)


def test_time_rounding_applied_to_duration_shape():
    rule = _rule(
        PricingShapes(base_plus_increment_times_duration=BasePlusIncrementTimesDurationShape(selected=True, basic_rate=1.0, daily_rate=1.0)),
        rounding_mode="exact",
        time_unit_hours=24.0,
        time_rounding="rounded_up",
    )
    call = VesselCall(port=Port.DURBAN, gross_tonnage=10.0, chargeable_period_days=1.2)
    result = compute_charge(rule, call, name="test_charge")
    # days rounded up from 1.2 to 2.0 whole 24h periods: basic=10, incremental=10*1*2
    assert result.amount == pytest.approx(10.0 + 10.0 * 1.0 * 2.0)


def test_modifiers_are_reported_but_never_applied():
    rule = _rule(
        PricingShapes(per_unit=PerUnitShape(selected=True, rate=1.0)),
        rounding_mode="exact",
        modifiers=[Modifier(condition="outside ordinary working hours", adjustment_percentage=25.0)],
    )
    result = compute_charge(rule, _CALL, name="test_charge")
    assert result.amount == pytest.approx(51_255.0)  # no modifier applied
    assert any("not applied" in w for w in result.warnings)
    assert "outside ordinary working hours" in result.warnings[0]


def _entry(charge, **kwargs) -> ChargeReportEntry:
    return ChargeReportEntry(charge=charge, **kwargs)


def test_compile_charge_single_rule():
    rule = _rule(PricingShapes(per_unit=PerUnitShape(selected=True, rate=2.0)), rounding_mode="exact")
    entry = _entry(CanonicalCharge.VTS, outcome=SemanticOutcome.MAPPED, proposed_rule=rule)
    fn = compile_charge(CanonicalCharge.VTS, entry)
    result = fn(_CALL)
    assert result.name == "vts_dues"
    assert result.amount == pytest.approx(51_255.0 * 2.0)


def test_compile_charge_varies_by_port_matches_normalized_key():
    rule = _rule(PricingShapes(per_unit=PerUnitShape(selected=True, rate=1.0)), rounding_mode="exact")
    entry = _entry(
        CanonicalCharge.TOWAGE, outcome=SemanticOutcome.MAPPED, varies_by_port=True,
        per_port_rules={"Durban": rule, "Richards Bay": rule},
    )
    fn = compile_charge(CanonicalCharge.TOWAGE, entry)
    result = fn(VesselCall(port=Port.DURBAN, gross_tonnage=10.0))  # Port.DURBAN.value == "durban"
    assert result.amount == pytest.approx(10.0)


def test_compile_charge_varies_by_port_unknown_port_reports_clearly():
    rule = _rule(PricingShapes(per_unit=PerUnitShape(selected=True, rate=1.0)), rounding_mode="exact")
    entry = _entry(CanonicalCharge.TOWAGE, outcome=SemanticOutcome.MAPPED, varies_by_port=True, per_port_rules={"Durban": rule})
    fn = compile_charge(CanonicalCharge.TOWAGE, entry)
    result = fn(VesselCall(port=Port.CAPE_TOWN, gross_tonnage=10.0))
    assert result.amount is None
    assert "no extracted rule matches port" in result.warnings[0]


def test_compile_charge_varies_by_port_exact_match_wins_over_a_negation_key():
    """Found live: VTS's real per_port_rules has a key literally named
    'all ports excluding Durban and Saldanha Bay' sitting next to an
    exact 'Durban' key -- a naive substring check matched "durban"
    against the negation key first (since it contains that word),
    computing the wrong port's rate entirely."""
    other_rule = _rule(PricingShapes(per_unit=PerUnitShape(selected=True, rate=0.54)), rounding_mode="exact")
    durban_rule = _rule(PricingShapes(per_unit=PerUnitShape(selected=True, rate=0.65)), rounding_mode="exact")
    entry = _entry(
        CanonicalCharge.VTS, outcome=SemanticOutcome.MAPPED, varies_by_port=True,
        per_port_rules={
            "all ports excluding Durban and Saldanha Bay": other_rule,
            "Durban": durban_rule,
            "Saldanha Bay": durban_rule,
        },
    )
    fn = compile_charge(CanonicalCharge.VTS, entry)
    result = fn(VesselCall(port=Port.DURBAN, gross_tonnage=51_255))
    assert result.amount == pytest.approx(51_255 * 0.65)


def test_compile_charge_not_mapped_reports_clearly_instead_of_crashing():
    entry = _entry(CanonicalCharge.LIGHT_DUES, outcome=SemanticOutcome.UNMAPPED, unmapped_source_text="some free-form table")
    fn = compile_charge(CanonicalCharge.LIGHT_DUES, entry)
    result = fn(_CALL)
    assert result.amount is None
    assert "not mapped" in result.warnings[0]


# ---------------------------------------------------------------------------
# to_tariff_plan() / parse_vessel_request(tariff_plan=...) integration
# ---------------------------------------------------------------------------


def test_to_tariff_plan_matches_nlp_s_expected_shape():
    rule = _rule(PricingShapes(per_unit=PerUnitShape(selected=True, rate=1.0)), rounding_mode="exact")
    entries = {
        CanonicalCharge.LIGHT_DUES: _entry(CanonicalCharge.LIGHT_DUES, outcome=SemanticOutcome.MAPPED, proposed_rule=rule),
        CanonicalCharge.VTS: _entry(CanonicalCharge.VTS, outcome=SemanticOutcome.MAPPED, proposed_rule=rule),
    }
    plan = to_tariff_plan(compile_report(entries))
    assert set(plan) == {"light_dues", "vts_dues"}
    calc_fn, mod_fn, dependency_met, missing_field = plan["light_dues"]
    assert dependency_met(_CALL) is True  # light dues needs nothing beyond port+GT
    assert mod_fn(calc_fn(_CALL, None), _CALL, None).amount == pytest.approx(51_255.0)


def test_parse_vessel_request_treats_an_unmapped_compiled_charge_as_not_computed():
    """Found live: a charge whose extraction outcome isn't 'mapped'
    compiles to a closure returning amount=None with an explanatory
    warning instead of raising -- _compute_tariff_outcomes() only ever
    checked for a raised RateNotPublished, so this was unconditionally
    treated as computed=True, and app.py crashed formatting None as a
    number. Must come back computed=False with the compiled warning as
    the reason, same shape as any other not-computable charge."""
    from tariffs.nlp import Parsed, VesselCallExtraction, parse_vessel_request

    class _StubStructuredLLM:
        def __init__(self, canned):
            self._canned = canned

        def invoke(self, messages):
            return self._canned

    class _StubChatModel:
        def __init__(self, canned):
            self._canned = canned

        def with_structured_output(self, schema):
            return _StubStructuredLLM(self._canned)

    canned = VesselCallExtraction(
        port={"value": "durban", "evidence": "Durban"},
        gross_tonnage={"value": 51_255.0, "evidence": "51255 GT"},
    )
    entries = {CanonicalCharge.LIGHT_DUES: _entry(CanonicalCharge.LIGHT_DUES, outcome=SemanticOutcome.UNMAPPED, unmapped_source_text="a free-form table")}
    plan = to_tariff_plan(compile_report(entries))

    result = parse_vessel_request("GT 51,255 at Durban", llm=_StubChatModel(canned), tariff_plan=plan)

    assert isinstance(result, Parsed)
    outcome = result.tariffs["light_dues"]
    assert outcome.computed is False
    assert outcome.result is None
    assert "not mapped" in outcome.reason


def test_parse_vessel_request_uses_the_compiled_tariff_plan_not_calculators_py():
    from tariffs.nlp import Parsed, VesselCallExtraction, parse_vessel_request

    class _StubStructuredLLM:
        def __init__(self, canned):
            self._canned = canned

        def invoke(self, messages):
            return self._canned

    class _StubChatModel:
        def __init__(self, canned):
            self._canned = canned

        def with_structured_output(self, schema):
            return _StubStructuredLLM(self._canned)

    canned = VesselCallExtraction(
        port={"value": "durban", "evidence": "Durban"},
        gross_tonnage={"value": 51_255.0, "evidence": "51255 GT"},
    )
    # A deliberately distinctive rate -- TNPA's real light_dues rate is
    # nowhere near this, so a match here can only come from the compiled
    # plan, never from an accidental fall-through to calculators.py.
    rule = _rule(PricingShapes(per_unit=PerUnitShape(selected=True, rate=999.0)), rounding_mode="exact")
    entries = {CanonicalCharge.LIGHT_DUES: _entry(CanonicalCharge.LIGHT_DUES, outcome=SemanticOutcome.MAPPED, proposed_rule=rule)}
    plan = to_tariff_plan(compile_report(entries))

    result = parse_vessel_request("GT 51,255 at Durban", llm=_StubChatModel(canned), tariff_plan=plan)

    assert isinstance(result, Parsed)
    assert set(result.tariffs) == {"light_dues"}  # only the one charge in the compiled plan
    outcome = result.tariffs["light_dues"]
    assert outcome.computed is True
    assert outcome.result.amount == pytest.approx(51_255.0 * 999.0)
