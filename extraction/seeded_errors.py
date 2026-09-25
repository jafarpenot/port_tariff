"""specs/EXTRACTION_SPEC.md §8 eval 3 — the verifier's seeded-error
catch rate. Evaluation code, not pipeline code: it is expected to know
TNPA-specific facts (its real gold values) the pipeline itself must
never be told — same boundary as evaluate.py.

Each case takes an otherwise-correct, plausible-looking proposal (using
real gold values everywhere except the one seeded mistake) and gives it
to the real Verify LLM as if it were a genuine extraction. Nothing here
hints that an error was seeded, or which kind — the proposal looks like
any other confident proposal (§8's constraint: the verifier must not be
told which errors were seeded, directly or through prompt structure).
"""

from __future__ import annotations

import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any, Callable

from tariffs.schedule import load_schedule

from .schemas import (
    BandedShape,
    BasePlusIncrementShape,
    CanonicalCharge,
    ChargeExtraction,
    PerUnitShape,
    PricingShapes,
    ProposedRule,
    SemanticOutcome,
    has_material_finding,
)
from .verify import verify_charge


@dataclass
class SeededCase:
    name: str
    description: str
    build: Callable[[], ChargeExtraction]


def _rate_shifted_to_wrong_port_column() -> ChargeExtraction:
    """VTS: Durban's real rate is 0.65; propose Cape Town's rate (0.54)
    for Durban instead — a value genuinely printed in this book, just in
    the wrong column."""
    gold = load_schedule()
    per_port = {}
    for port, rate_cfg in gold.vts.ports.items():
        rate = gold.vts.ports["cape_town"].rate_per_gt if port == "durban" else rate_cfg.rate_per_gt
        per_port[port] = ProposedRule(
            basis="gross_tonnage",
            rounding_mode="exact",
            pricing=PricingShapes(per_unit=PerUnitShape(selected=True, rate=rate)),
            multiplicity="per_call",
            minimum=gold.vts.minimum_fee,
        )
    return ChargeExtraction(charge=CanonicalCharge.VTS, outcome=SemanticOutcome.MAPPED, varies_by_port=True, per_port_rules=per_port, provenance_sections=["2.1.1"], provenance_pages=[6])


def _surcharge_removed() -> ChargeExtraction:
    """Towage: correct base rates for every port and band, but the
    proposal cites only the rate-table page, never the surcharges
    described in the same section (out-of-hours, additional tug, vessel
    without power, cancellation, late arrival)."""
    gold = load_schedule()
    per_port = {}
    for port, port_bands in gold.towage.ports.items():
        bands = [
            {"min_exclusive": b.min_gt_exclusive, "max_inclusive": b.max_gt_inclusive, "base": b.base, "increment_above": b.increment_above_gt, "per_unit_rate": b.per_100t}
            for b in port_bands.bands
        ]
        per_port[port] = ProposedRule(
            basis="gross_tonnage",
            rounding_mode="ceil_to_unit",
            rounding_unit=100,
            pricing=PricingShapes(banded=BandedShape(selected=True, bands=bands)),
            multiplicity="per_service",
        )
    return ChargeExtraction(charge=CanonicalCharge.TOWAGE, outcome=SemanticOutcome.MAPPED, varies_by_port=True, per_port_rules=per_port, provenance_sections=["3.6"], provenance_pages=[15])


def _band_boundary_moved() -> ChargeExtraction:
    """Towage, Durban only (other ports correct): the real 2,000/10,000
    boundary between bands 1 and 2 moved to 9,000."""
    gold = load_schedule()
    per_port = {}
    for port, port_bands in gold.towage.ports.items():
        bands = []
        for i, b in enumerate(port_bands.bands):
            min_exclusive, max_inclusive, increment_above = b.min_gt_exclusive, b.max_gt_inclusive, b.increment_above_gt
            if port == "durban" and i == 1:  # band [2000, 10000] -> [2000, 9000]
                max_inclusive = 9000.0
            elif port == "durban" and i == 2:  # band [10000, 50000] -> [9000, 50000]
                min_exclusive, increment_above = 9000.0, 9000.0
            bands.append({"min_exclusive": min_exclusive, "max_inclusive": max_inclusive, "base": b.base, "increment_above": increment_above, "per_unit_rate": b.per_100t})
        per_port[port] = ProposedRule(
            basis="gross_tonnage",
            rounding_mode="ceil_to_unit",
            rounding_unit=100,
            pricing=PricingShapes(banded=BandedShape(selected=True, bands=bands)),
            multiplicity="per_service",
        )
    return ChargeExtraction(charge=CanonicalCharge.TOWAGE, outcome=SemanticOutcome.MAPPED, varies_by_port=True, per_port_rules=per_port, provenance_sections=["3.6"], provenance_pages=[15])


def _marine_services_incentive_dropped() -> ChargeExtraction:
    """Pilotage: correct Durban rate, but the proposal cites only the
    core pilotage section, never §3.2's marine services incentive, which
    explicitly discounts pilotage."""
    gold = load_schedule()
    rate_cfg = gold.pilotage.ports["durban"]
    rule = ProposedRule(
        basis="gross_tonnage",
        rounding_mode="ceil_to_unit",
        rounding_unit=100,
        pricing=PricingShapes(base_plus_increment=BasePlusIncrementShape(selected=True, base=rate_cfg.base_fee, rate=rate_cfg.per_100t)),
        multiplicity="per_service",
    )
    return ChargeExtraction(charge=CanonicalCharge.PILOTAGE, outcome=SemanticOutcome.MAPPED, varies_by_port=False, proposed_rule=rule, provenance_sections=["3.3"], provenance_pages=[13])


def _bundled_charge_marked_not_present() -> ChargeExtraction:
    """TNPA has no charge among the six that is naturally bundled into
    another (adapted from the spec's literal wording, §8 eval 3): this
    tests the same underlying capability — catching a charge wrongly
    called not_present — using berthing_services, a real, independently
    billed §3.8 charge, claimed absent from a book that plainly has it."""
    return ChargeExtraction(charge=CanonicalCharge.BERTHING_SERVICES, outcome=SemanticOutcome.NOT_PRESENT)


SEEDED_CASES: list[SeededCase] = [
    SeededCase("rate_wrong_port_column", "VTS: Durban given Cape Town's rate", _rate_shifted_to_wrong_port_column),
    SeededCase("surcharge_removed", "Towage: correct rates, surcharges never cited", _surcharge_removed),
    SeededCase("band_boundary_moved", "Towage/Durban: 10,000 boundary moved to 9,000", _band_boundary_moved),
    SeededCase("incentive_dropped", "Pilotage: correct rate, §3.2 incentive never cited", _marine_services_incentive_dropped),
    SeededCase("bundled_marked_not_present", "Berthing services wrongly claimed not present", _bundled_charge_marked_not_present),
]


def run_seeded_error_eval(page_texts: dict[int, str], llm: Any, *, concurrency_limit: int = 5) -> dict[str, dict]:
    def _run_one(case: SeededCase) -> tuple[str, dict]:
        print(f"[seeded-error eval] starting {case.name}...", file=sys.stderr, flush=True)
        extraction = case.build()
        result = verify_charge(extraction.charge, extraction, page_texts, llm)
        print(f"[seeded-error eval] finished {case.name}", file=sys.stderr, flush=True)
        return case.name, {
            "description": case.description,
            "caught": has_material_finding(result),
            "findings": [f.model_dump() for f in result.findings],
        }

    with ThreadPoolExecutor(max_workers=max(1, concurrency_limit)) as pool:
        return dict(pool.map(_run_one, SEEDED_CASES))
