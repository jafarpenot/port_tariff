"""specs/EXTRACTION_SPEC.md §8 eval 1 — extraction accuracy on TNPA.
Runs the pipeline against the real PDF and scores the proposal cell by
cell against the existing hand-verified YAML (the gold standard).

This is evaluation code, not pipeline code — it is expected to know
TNPA-specific things (its port names, its gold values) that the pipeline
itself must never be told (specs/EXTRACTION_SPEC.md §8's cross-cutting
constraint). Keeping it in its own module, separate from prompts.py,
is what keeps that boundary enforceable.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from tariffs.schedule import TariffSchedule, load_schedule
from tariffs.models import Port

from .schemas import CanonicalCharge, ChargeReportEntry, ProposedRule, ReviewReport, SemanticOutcome

_TOLERANCE = 0.01

# Best-effort normalisation from whatever port label the model used
# (a book's own column header — possibly combining two ports, or an
# "Other"/"Other Ports" catch-all) to the canonical Port enum keys this
# evaluator (not the pipeline) knows about.
_PORT_ALIASES: dict[str, list[str]] = {
    "richards_bay": ["richards bay"],
    "durban": ["durban"],
    "east_london": ["east london"],
    "ngqura": ["ngqura"],
    # Deliberately no short alias like "pe" here — "pe" is a substring of
    # "caPE Town" and silently mismatched every Cape Town label to Port
    # Elizabeth (found reviewing the first corrected-scorer live run:
    # every remaining pilotage/berthing_services "miss" traced back to
    # this, not to the extraction). Word-boundary matching below is a
    # second layer of defence against the same class of bug, but the
    # short alias itself was the direct cause and is not coming back.
    "port_elizabeth": ["port elizabeth"],
    "mossel_bay": ["mossel bay"],
    "cape_town": ["cape town"],
    "saldanha": ["saldanha"],
}
_OTHER_LABELS = ["other ports", "other", "all other ports"]


def _normalize(label: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", label.lower()).strip()


def _word_boundary_match(alias: str, normalized_label: str) -> bool:
    """Whole-phrase match at word boundaries, not a raw substring — a
    short or partial alias must not match inside an unrelated word (the
    "pe" bug this replaced)."""
    return re.search(rf"\b{re.escape(alias)}\b", normalized_label) is not None


def match_port_key(label: str) -> str | None:
    """A specific port name, or None if this label doesn't name one
    (e.g. it's an 'Other Ports' catch-all, matched separately)."""
    normalized = _normalize(label)
    for canonical, aliases in _PORT_ALIASES.items():
        if any(_word_boundary_match(alias, normalized) or _word_boundary_match(normalized, alias) for alias in aliases):
            return canonical
    return None


_EXCLUSION_MARKERS = ["excluding", "except", "other than"]


def _is_exclusion_label(normalized_label: str) -> bool:
    """"All ports excluding Durban and Saldanha Bay" (the book's own
    phrasing for VTS) is functionally an 'Other' catch-all — but it
    literally contains the word "Durban", so a naive word-boundary check
    wrongly treats it as *naming* Durban rather than excluding it. Found
    live: this made every VTS cell score as a miss even though the
    extraction was fully correct (Durban's own real 0.65 entry existed
    right alongside it — this label just won the match first)."""
    return any(marker in normalized_label for marker in _EXCLUSION_MARKERS)


def is_other_label(label: str) -> bool:
    normalized = _normalize(label)
    return any(other in normalized for other in _OTHER_LABELS) or _is_exclusion_label(normalized)


def _label_names_port(label: str, port: Port) -> bool:
    """Checks this port's own aliases directly, rather than asking
    match_port_key for its single best guess at a label — a combined
    label like "Port Elizabeth / Ngqura" genuinely names two ports at
    once, and a single-winner resolver can only ever return one of
    them, silently losing the other back to the Other/Other Ports
    fallback (found immediately after fixing the 'pe' alias bug above:
    Ngqura won the tie-break every time, and Port Elizabeth's real value
    disappeared).

    An exclusion-phrased label (see _is_exclusion_label) never counts as
    directly naming a port, even when that port's name literally appears
    in it — it's a catch-all, handled by is_other_label instead."""
    normalized = _normalize(label)
    if _is_exclusion_label(normalized):
        return False
    return any(_word_boundary_match(alias, normalized) for alias in _PORT_ALIASES[port.value])


def resolve_rule_for_port(port: Port, per_port_rules: dict[str, ProposedRule]) -> ProposedRule | None:
    """Direct match first; an 'Other Ports' catch-all only if no direct
    match exists — mirrors how the real book itself is structured
    (SPEC.md §7.6: named columns take priority over the Other fallback)."""
    other_rule = None
    for label, rule in per_port_rules.items():
        if _label_names_port(label, port):
            return rule
        if other_rule is None and is_other_label(label):
            other_rule = rule
    return other_rule


@dataclass
class CellResult:
    charge: str
    cell: str
    gold: float | None
    proposed: float | None
    match: bool


@dataclass
class ChargeScore:
    charge: str
    cells: list[CellResult] = field(default_factory=list)

    @property
    def matched(self) -> int:
        return sum(1 for c in self.cells if c.match)

    @property
    def total(self) -> int:
        return len(self.cells)


def _close(a: float | None, b: float | None) -> bool:
    if a is None or b is None:
        return a is b
    return abs(a - b) < _TOLERANCE


def _cell(charge: str, name: str, gold: float | None, proposed: float | None, out: list[CellResult]) -> None:
    out.append(CellResult(charge=charge, cell=name, gold=gold, proposed=proposed, match=_close(gold, proposed)))


def _find_matching_band(gold_band, proposed_bands: list[dict]) -> dict | None:
    """Match by the band's actual GT boundaries, not list position — a
    proposal's bands aren't guaranteed to be in the same order or count
    as gold's, and comparing by index silently misaligns every band
    after the first mismatch."""
    for pb in proposed_bands:
        if _close(pb.get("min_exclusive"), gold_band.min_gt_exclusive) and _close(pb.get("max_inclusive"), gold_band.max_gt_inclusive):
            return pb
    return None


def _band_field_matches(gold_value: float | None, proposed_value: float | None, gold_base: float | None) -> bool:
    """increment_above/per_unit_rate on a real (non-n/a) flat band mean
    "no increment applies" — the book's null and a mathematically inert
    0 (ceil((gt-0)/100) * 0 == 0 for any gt) produce the identical
    charge, so treat them as equal. This equivalence does NOT apply when
    gold_base is itself None (a genuinely n/a band, SPEC.md §5.3): there,
    a proposed 0 silently charges something instead of correctly
    signalling "no rate published", which is a real miss, not a
    representational choice."""
    if gold_base is None:
        return _close(gold_value, proposed_value)
    gold_is_flat = gold_value is None
    proposed_is_flat = proposed_value is None or proposed_value == 0
    if gold_is_flat and proposed_is_flat:
        return True
    return _close(gold_value, proposed_value)


def score_light_dues(entry: ChargeReportEntry, gold: TariffSchedule) -> ChargeScore:
    cells: list[CellResult] = []
    rule = entry.proposed_rule
    gold_rate = gold.light_dues.foreign_and_other_vessels.rate_per_100t
    _cell("light_dues", "rate_per_100t", gold_rate, rule.pricing_params.get("rate") if rule else None, cells)
    return ChargeScore(charge="light_dues", cells=cells)


def score_port_dues(entry: ChargeReportEntry, gold: TariffSchedule) -> ChargeScore:
    cells: list[CellResult] = []
    rule = entry.proposed_rule
    _cell("port_dues", "basic_rate", gold.port_dues.basic_rate_per_100t, rule.pricing_params.get("basic_rate") if rule else None, cells)
    _cell(
        "port_dues",
        "daily_rate",
        gold.port_dues.incremental_rate_per_100t_per_day,
        rule.pricing_params.get("daily_rate") if rule else None,
        cells,
    )
    return ChargeScore(charge="port_dues", cells=cells)


def score_vts(entry: ChargeReportEntry, gold: TariffSchedule) -> ChargeScore:
    cells: list[CellResult] = []
    for port in Port:
        rule = resolve_rule_for_port(port, entry.per_port_rules)
        gold_rate = gold.vts.ports[port.value].rate_per_gt
        _cell("vts", f"{port.value}.rate", gold_rate, rule.pricing_params.get("rate") if rule else None, cells)
    return ChargeScore(charge="vts", cells=cells)


def score_pilotage(entry: ChargeReportEntry, gold: TariffSchedule) -> ChargeScore:
    cells: list[CellResult] = []
    for port in Port:
        rule = resolve_rule_for_port(port, entry.per_port_rules)
        gold_port = gold.pilotage.ports[port.value]
        _cell("pilotage", f"{port.value}.base", gold_port.base_fee, rule.pricing_params.get("base") if rule else None, cells)
        _cell("pilotage", f"{port.value}.rate", gold_port.per_100t, rule.pricing_params.get("rate") if rule else None, cells)
    return ChargeScore(charge="pilotage", cells=cells)


def score_berthing_services(entry: ChargeReportEntry, gold: TariffSchedule) -> ChargeScore:
    cells: list[CellResult] = []
    for port in Port:
        rule = resolve_rule_for_port(port, entry.per_port_rules)
        gold_port = gold.berthing_services.ports[port.value]
        _cell("berthing_services", f"{port.value}.base", gold_port.base_fee, rule.pricing_params.get("base") if rule else None, cells)
        _cell("berthing_services", f"{port.value}.rate", gold_port.per_100t, rule.pricing_params.get("rate") if rule else None, cells)
    return ChargeScore(charge="berthing_services", cells=cells)


def score_towage(entry: ChargeReportEntry, gold: TariffSchedule) -> ChargeScore:
    cells: list[CellResult] = []
    for port in Port:
        rule = resolve_rule_for_port(port, entry.per_port_rules)
        gold_bands = gold.towage.ports[port.value].bands
        proposed_bands = (rule.pricing_params.get("bands") or []) if rule else []
        for i, gold_band in enumerate(gold_bands):
            proposed_band = _find_matching_band(gold_band, proposed_bands) or {}
            prefix = f"{port.value}.band{i}[{gold_band.min_gt_exclusive:.0f}-{gold_band.max_gt_inclusive}]"
            _cell("towage", f"{prefix}.base", gold_band.base, proposed_band.get("base"), cells)
            cells.append(
                CellResult(
                    charge="towage",
                    cell=f"{prefix}.increment_above",
                    gold=gold_band.increment_above_gt,
                    proposed=proposed_band.get("increment_above"),
                    match=_band_field_matches(gold_band.increment_above_gt, proposed_band.get("increment_above"), gold_band.base),
                )
            )
            cells.append(
                CellResult(
                    charge="towage",
                    cell=f"{prefix}.per_unit_rate",
                    gold=gold_band.per_100t,
                    proposed=proposed_band.get("per_unit_rate"),
                    match=_band_field_matches(gold_band.per_100t, proposed_band.get("per_unit_rate"), gold_band.base),
                )
            )
    return ChargeScore(charge="towage", cells=cells)


_SCORERS = {
    CanonicalCharge.LIGHT_DUES: score_light_dues,
    CanonicalCharge.PORT_DUES: score_port_dues,
    CanonicalCharge.TOWAGE: score_towage,
    CanonicalCharge.VTS: score_vts,
    CanonicalCharge.PILOTAGE: score_pilotage,
    CanonicalCharge.BERTHING_SERVICES: score_berthing_services,
}


def score_report(report: ReviewReport, gold: TariffSchedule | None = None) -> dict[str, ChargeScore]:
    gold = gold or load_schedule()
    scores: dict[str, ChargeScore] = {}
    for entry in report.charges:
        if entry.outcome is not SemanticOutcome.MAPPED:
            scores[entry.charge.value] = ChargeScore(charge=entry.charge.value, cells=[])
            continue
        scorer = _SCORERS[entry.charge]
        scores[entry.charge.value] = scorer(entry, gold)
    return scores


def print_score_report(report: ReviewReport, scores: dict[str, ChargeScore]) -> None:
    total_matched = total_cells = 0
    for entry in report.charges:
        score = scores[entry.charge.value]
        outcome = entry.outcome.value if entry.outcome else entry.status.value if entry.status else "?"
        print(f"{entry.charge.value:20s} outcome={outcome:15s} repair_attempts={entry.repair_attempts}")
        if score.total == 0:
            print("    (no scorable cells)")
            continue
        total_matched += score.matched
        total_cells += score.total
        print(f"    {score.matched}/{score.total} cells matched")
        misses = [c for c in score.cells if not c.match]
        for cell in misses:
            print(f"    MISS {cell.cell:35s} gold={cell.gold!r:>12} proposed={cell.proposed!r}")
        if misses:
            # Raw proposal, for diagnosing a miss the cell-level view can't
            # explain by itself (e.g. a value under a different dict key
            # than the one being scored, or a port label that didn't
            # match any canonical port at all).
            if entry.varies_by_port:
                print(f"    raw per_port_rules keys: {list(entry.per_port_rules.keys())}")
                for label, rule in entry.per_port_rules.items():
                    print(f"      {label!r}: pricing_type={rule.pricing_type!r} params={rule.pricing_params}")
            elif entry.proposed_rule:
                print(f"    raw proposed_rule: pricing_type={entry.proposed_rule.pricing_type!r} params={entry.proposed_rule.pricing_params}")
    if total_cells:
        print(f"\nOVERALL: {total_matched}/{total_cells} cells matched ({100 * total_matched / total_cells:.1f}%)")
