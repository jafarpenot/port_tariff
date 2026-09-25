"""Regression tests for the two scorer bugs found reviewing the first
live run's results: band comparison by list position instead of actual
GT boundaries, and 0-vs-null not being recognised as the same charge on
a flat band. Both are pure logic, no LLM involved.
"""

from tariffs.models import Port
from tariffs.schedule import load_schedule

from extraction.evaluate import (
    _band_field_matches,
    _find_matching_band,
    match_port_key,
    resolve_rule_for_port,
    score_towage,
    score_vts,
)
from extraction.schemas import BandedShape, CanonicalCharge, ChargeReportEntry, PerUnitShape, PricingShapes, ProposedRule, SemanticOutcome

GOLD = load_schedule()


class _FakeBand:
    def __init__(self, min_gt_exclusive, max_gt_inclusive, base):
        self.min_gt_exclusive = min_gt_exclusive
        self.max_gt_inclusive = max_gt_inclusive
        self.base = base


def test_find_matching_band_ignores_list_order():
    gold_band = _FakeBand(2000, 10000, 12633.99)
    proposed_bands = [
        {"min_exclusive": 10000, "max_inclusive": 50000, "base": 999},  # a different band, listed first
        {"min_exclusive": 2000, "max_inclusive": 10000, "base": 12633.99},  # the actual match, listed second
    ]
    match = _find_matching_band(gold_band, proposed_bands)
    assert match["base"] == 12633.99


def test_find_matching_band_returns_none_when_no_boundary_matches():
    gold_band = _FakeBand(2000, 10000, 12633.99)
    proposed_bands = [{"min_exclusive": 0, "max_inclusive": 2000, "base": 1.0}]
    assert _find_matching_band(gold_band, proposed_bands) is None


def test_zero_and_null_are_equivalent_on_a_real_flat_band():
    # gold_base is a real number (not None) -> the "no increment" case
    assert _band_field_matches(None, 0, gold_base=8140.0) is True
    assert _band_field_matches(None, None, gold_base=8140.0) is True


def test_zero_and_null_are_not_equivalent_on_an_na_band():
    # gold_base is itself None -> a genuinely n/a band; 0 silently
    # charges something instead of signalling "not published"
    assert _band_field_matches(None, 0, gold_base=None) is False


def test_nonzero_mismatch_is_still_a_real_miss_on_a_flat_band():
    assert _band_field_matches(None, 5.0, gold_base=8140.0) is False


def test_cape_town_does_not_collide_with_port_elizabeths_short_alias():
    """Found on a live run: 'pe' as a Port Elizabeth alias is a substring
    of 'caPE Town', so every Cape Town label matched Port Elizabeth
    instead — this was purely a scorer bug, not an extraction one."""
    assert match_port_key("Cape Town") == "cape_town"
    assert match_port_key("Port Elizabeth") == "port_elizabeth"
    assert match_port_key("Port Elizabeth / Ngqura") in {"port_elizabeth", "ngqura"}  # combined column, either is fine


def test_combined_column_label_resolves_correctly_for_both_ports_it_names():
    """Found immediately after fixing the 'pe' bug: a single-winner
    resolver could only ever return one port for a combined label like
    "Port Elizabeth / Ngqura" — Ngqura won the tie-break every time and
    Port Elizabeth's real value silently fell back to Other."""
    combined = ProposedRule(basis="gross_tonnage", rounding_mode="exact", pricing=PricingShapes(per_unit=PerUnitShape(selected=True, rate=14.33)), multiplicity="per_call")
    other = ProposedRule(basis="gross_tonnage", rounding_mode="exact", pricing=PricingShapes(per_unit=PerUnitShape(selected=True, rate=10.49)), multiplicity="per_call")
    per_port_rules = {"Port Elizabeth / Ngqura": combined, "Other": other}
    assert resolve_rule_for_port(Port.PORT_ELIZABETH, per_port_rules) is combined
    assert resolve_rule_for_port(Port.NGQURA, per_port_rules) is combined


def _rate_rule(rate):
    return ProposedRule(basis="gross_tonnage", rounding_mode="exact", pricing=PricingShapes(per_unit=PerUnitShape(selected=True, rate=rate)), multiplicity="per_call")


def test_exclusion_phrased_label_does_not_hijack_the_named_port_it_excludes():
    """Real data from a live run: the book's own VTS phrasing is "0.54 at
    all ports excluding Durban and Saldanha Bay; 0.65 at Durban and
    Saldanha Bay" — the model extracted this faithfully, but the
    exclusion label literally contains the word "Durban", so it used to
    win the match before ever reaching Durban's own entry."""
    per_port_rules = {
        "All ports excluding Durban and Saldanha Bay": _rate_rule(0.54),
        "Durban": _rate_rule(0.65),
        "Saldanha Bay": _rate_rule(0.65),
    }
    assert resolve_rule_for_port(Port.DURBAN, per_port_rules).pricing_params["rate"] == 0.65
    assert resolve_rule_for_port(Port.SALDANHA, per_port_rules).pricing_params["rate"] == 0.65
    for port in [Port.RICHARDS_BAY, Port.EAST_LONDON, Port.NGQURA, Port.PORT_ELIZABETH, Port.MOSSEL_BAY, Port.CAPE_TOWN]:
        assert resolve_rule_for_port(port, per_port_rules).pricing_params["rate"] == 0.54


def test_score_vts_real_live_data_scores_100_percent_once_exclusion_label_is_handled():
    entry = ChargeReportEntry(
        charge=CanonicalCharge.VTS,
        outcome=SemanticOutcome.MAPPED,
        varies_by_port=True,
        per_port_rules={
            "All ports excluding Durban and Saldanha Bay": _rate_rule(0.54),
            "Durban": _rate_rule(0.65),
            "Saldanha Bay": _rate_rule(0.65),
        },
    )
    score = score_vts(entry, GOLD)
    assert score.matched == score.total == 8


def test_score_towage_perfect_durban_proposal_scores_100_percent_with_reordered_and_zeroed_bands():
    durban_bands = GOLD.towage.ports["durban"].bands
    # Deliberately reordered (last band first) and using 0 instead of
    # null for band 0's "no increment" fields — both should now score as
    # correct, per the two fixes above.
    proposed_bands = [
        {
            "min_exclusive": b.min_gt_exclusive,
            "max_inclusive": b.max_gt_inclusive,
            "base": b.base,
            "increment_above": b.increment_above_gt if b.increment_above_gt is not None else 0,
            "per_unit_rate": b.per_100t if b.per_100t is not None else 0,
        }
        for b in reversed(durban_bands)
    ]
    rule = ProposedRule(
        basis="gross_tonnage",
        rounding_mode="ceil_to_unit",
        rounding_unit=100,
        pricing=PricingShapes(banded=BandedShape(selected=True, bands=proposed_bands)),
        multiplicity="per_service",
    )
    entry = ChargeReportEntry(
        charge=CanonicalCharge.TOWAGE,
        outcome=SemanticOutcome.MAPPED,
        varies_by_port=True,
        per_port_rules={p.value: rule for p in Port},  # same (correct) bands for every port, for this test
    )
    score = score_towage(entry, GOLD)
    durban_cells = [c for c in score.cells if c.cell.startswith("durban.")]
    assert all(c.match for c in durban_cells), [c for c in durban_cells if not c.match]
