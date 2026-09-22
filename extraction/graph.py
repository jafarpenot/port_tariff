"""The pipeline graph (§6.1) — nodes 1-9. Stage 4 adds node 7 (Verify)
and its repair loop on top of Stage 2's spine.

Map, Extract and Verify's own internal parallelism (ThreadPoolExecutor,
bounded by a concurrency limit) happens inside their node functions —
this graph orchestrates the macro sequence and both repair loops, and
owns what must be guaranteed structurally: every Extract output passes
through Validate before it can reach Verify or the report (§6.2's
invariant) — true for a first-pass extraction, a validate-repair, and a
verify-repair alike, since all three funnel through the same "extract"
node and the same "validate" node before anything downstream can see
the result.

Runtime-only values (the LLM client, window/concurrency/budget settings)
are passed via LangGraph's `config["configurable"]`, never through graph
state — state gets checkpointed (msgpack) to support the human-approval
interrupt/resume, and an LLM client object is not serialisable.
"""

from __future__ import annotations

from typing import Any, Optional, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.types import interrupt

from .assemble import AssembleResult, assemble
from .extract import DEFAULT_CONCURRENCY_LIMIT, extract_all
from .identity import provisional_identity
from .map_node import DEFAULT_WINDOW_OVERLAP, DEFAULT_WINDOW_SIZE, map_document
from .pdf import split_pdf
from .report import build_report
from .schemas import (
    CanonicalCharge,
    ChargeExtraction,
    Disagreement,
    PipelineStatus,
    ReviewReport,
    ValidationResult,
    ValidationSeverity,
    VerifierResult,
    VerifierSeverity,
    WindowMapResult,
    has_material_finding,
)
from .validate import validate_all
from .verify import verify_all

REPAIR_BUDGET = 3  # §6.7, configurable — Validate's structural repair loop
VERIFY_BUDGET = 1  # §6.7, configurable, max 2 — Verify's adversarial repair loop


class PipelineState(TypedDict, total=False):
    pdf_path: str

    page_texts: dict[int, str]
    provisional_identity: Any
    map_results: list[WindowMapResult]
    assemble_result: AssembleResult
    extractions: dict[CanonicalCharge, ChargeExtraction]
    validations: dict[CanonicalCharge, ValidationResult]
    pipeline_statuses: dict[CanonicalCharge, PipelineStatus]
    repair_counts: dict[CanonicalCharge, int]
    verify_results: dict[CanonicalCharge, VerifierResult]
    verify_rounds: dict[CanonicalCharge, int]
    disagreements: list[Disagreement]
    report: ReviewReport
    approved: Optional[bool]


def _cfg(config, key, default=None):
    return (config.get("configurable") or {}).get(key, default)


def node_split(state: PipelineState, config) -> dict:
    if state.get("page_texts"):
        return {}
    return {"page_texts": split_pdf(state["pdf_path"])}


def node_identity(state: PipelineState, config) -> dict:
    llm = _cfg(config, "llm")
    return {"provisional_identity": provisional_identity(state["page_texts"], llm)}


def node_map(state: PipelineState, config) -> dict:
    llm = _cfg(config, "llm")
    results = map_document(
        state["page_texts"],
        llm,
        window_size=_cfg(config, "window_size", DEFAULT_WINDOW_SIZE),
        overlap=_cfg(config, "overlap", DEFAULT_WINDOW_OVERLAP),
        concurrency_limit=_cfg(config, "concurrency_limit", DEFAULT_CONCURRENCY_LIMIT),
    )
    return {"map_results": results}


def node_assemble(state: PipelineState, config) -> dict:
    result = assemble(state["map_results"], state["provisional_identity"], state["page_texts"])
    return {"assemble_result": result}


def _pending_verify_challenges(state: PipelineState, config) -> dict[CanonicalCharge, list]:
    """Charges with an unresolved material finding, still structurally
    valid, still under the verify-repair budget — i.e. due another trip
    through Extract in response to Verify's challenge, not Validate's."""
    budget = _cfg(config, "verify_budget", VERIFY_BUDGET)
    validations = state.get("validations", {})
    verify_results = state.get("verify_results", {})
    verify_rounds = state.get("verify_rounds", {})
    pending = {}
    for charge, result in verify_results.items():
        validation = validations.get(charge)
        if (
            has_material_finding(result)
            and verify_rounds.get(charge, 0) < budget
            and validation is not None
            and validation.valid
        ):
            pending[charge] = [f for f in result.findings if f.severity is VerifierSeverity.MATERIAL]
    return pending


def node_extract(state: PipelineState, config) -> dict:
    llm = _cfg(config, "llm")
    concurrency_limit = _cfg(config, "concurrency_limit", DEFAULT_CONCURRENCY_LIMIT)
    contexts = state["assemble_result"].charge_contexts
    existing = state.get("extractions", {})

    if not existing:
        new_extractions = extract_all(contexts, state["page_texts"], llm, concurrency_limit=concurrency_limit)
        return {"extractions": new_extractions, "repair_counts": {c: 0 for c in contexts}}

    # Priority 1: respond to a verifier challenge (§6.6) — checked first
    # since a charge only reaches this state after already passing
    # Validate; there is nothing structural left to fix on it.
    challenges = _pending_verify_challenges(state, config)
    if challenges:
        to_repair = {c: contexts[c] for c in challenges}
        repaired = extract_all(
            to_repair, state["page_texts"], llm, concurrency_limit=concurrency_limit, verifier_findings_by_charge=challenges
        )
        merged = dict(existing)
        merged.update(repaired)
        return {"extractions": merged}

    # Priority 2: Validate's structural repair loop (§6.5), unchanged from Stage 2.
    budget = _cfg(config, "repair_budget", REPAIR_BUDGET)
    repair_counts = dict(state.get("repair_counts", {}))
    validations = state.get("validations", {})
    to_repair = {}
    issues_by_charge = {}
    for charge, validation in validations.items():
        if not validation.valid and repair_counts.get(charge, 0) < budget:
            to_repair[charge] = contexts[charge]
            issues_by_charge[charge] = [i for i in validation.issues if i.severity is ValidationSeverity.HARD]
            repair_counts[charge] = repair_counts.get(charge, 0) + 1

    repaired = extract_all(
        to_repair, state["page_texts"], llm, concurrency_limit=concurrency_limit, repair_issues_by_charge=issues_by_charge
    )
    merged = dict(existing)
    merged.update(repaired)
    return {"extractions": merged, "repair_counts": repair_counts}


def node_validate(state: PipelineState, config) -> dict:
    return {"validations": validate_all(state["extractions"], state["page_texts"])}


def route_after_validate(state: PipelineState, config) -> str:
    budget = _cfg(config, "repair_budget", REPAIR_BUDGET)
    repair_counts = state.get("repair_counts", {})
    needs_repair = any(
        not validation.valid and repair_counts.get(charge, 0) < budget for charge, validation in state["validations"].items()
    )
    return "extract" if needs_repair else "verify"


def node_verify(state: PipelineState, config) -> dict:
    """Only charges that are currently structurally valid, and either
    never verified yet or just went through a verify-repair cycle, get
    (re-)verified — a charge Validate could never make valid is already
    headed to Extraction failed and gets no adversarial pass at all."""
    llm = _cfg(config, "verifier_llm") or _cfg(config, "llm")
    concurrency_limit = _cfg(config, "concurrency_limit", DEFAULT_CONCURRENCY_LIMIT)
    budget = _cfg(config, "verify_budget", VERIFY_BUDGET)
    validations = state.get("validations", {})
    existing_results = state.get("verify_results", {})
    verify_rounds = dict(state.get("verify_rounds", {}))

    # `verify_rounds` counts repair rounds consumed, not total verify
    # passes — the always-happening first pass on a charge is free, same
    # as `repair_attempts` doesn't count Extract's first-ever attempt.
    # Conflating the two meant a default budget of 1 blocked every
    # repair outright (1 < 1 is false the moment the first pass finds
    # something) — caught by a mocked test expecting a repair to happen
    # and it silently not happening.
    to_verify = []
    is_repair_pass: dict[CanonicalCharge, bool] = {}
    for charge, validation in validations.items():
        if not validation.valid:
            continue
        prior = existing_results.get(charge)
        if prior is None:
            to_verify.append(charge)
            is_repair_pass[charge] = False
        elif has_material_finding(prior) and verify_rounds.get(charge, 0) < budget:
            to_verify.append(charge)
            is_repair_pass[charge] = True

    if not to_verify:
        return {}

    extractions = {c: state["extractions"][c] for c in to_verify}
    new_results = verify_all(extractions, state["page_texts"], llm, concurrency_limit=concurrency_limit)

    results = dict(existing_results)
    results.update(new_results)
    for charge in to_verify:
        if is_repair_pass[charge]:
            verify_rounds[charge] = verify_rounds.get(charge, 0) + 1

    return {"verify_results": results, "verify_rounds": verify_rounds}


def route_after_verify(state: PipelineState, config) -> str:
    budget = _cfg(config, "verify_budget", VERIFY_BUDGET)
    verify_results = state.get("verify_results", {})
    verify_rounds = state.get("verify_rounds", {})
    needs_repair = any(
        has_material_finding(result) and verify_rounds.get(charge, 0) < budget for charge, result in verify_results.items()
    )
    return "extract" if needs_repair else "finalize_statuses"


def node_finalize_statuses(state: PipelineState, config) -> dict:
    """§3.2: a pipeline status is set by the workflow, never by a model —
    a charge still invalid once its repair budget is exhausted becomes
    Extraction failed here, distinct from Extract's own Unmapped. A
    charge Verify still has a material finding on, once the verify
    budget is exhausted, becomes an unresolved disagreement (§6.6) —
    information for the reviewer, never looped until the models agree."""
    statuses = dict(state.get("pipeline_statuses", {}))
    for charge, validation in state["validations"].items():
        if not validation.valid:
            statuses[charge] = PipelineStatus.EXTRACTION_FAILED

    budget = _cfg(config, "verify_budget", VERIFY_BUDGET)
    verify_results = state.get("verify_results", {})
    verify_rounds = state.get("verify_rounds", {})
    extractions = state.get("extractions", {})
    disagreements = list(state.get("disagreements", []))
    for charge, result in verify_results.items():
        if has_material_finding(result) and verify_rounds.get(charge, 0) >= budget:
            extraction = extractions.get(charge)
            material = [f for f in result.findings if f.severity is VerifierSeverity.MATERIAL]
            disagreements.append(
                Disagreement(
                    charge=charge,
                    extractor_interpretation=(
                        extraction.rebuttal if extraction and extraction.rebuttal else "(no rebuttal given — proposal unchanged after review)"
                    ),
                    extractor_pages=extraction.provenance_pages if extraction else [],
                    verifier_concern="; ".join(f.problem for f in material),
                    verifier_pages=sorted({p for f in material for p in f.pages}),
                )
            )
    return {"pipeline_statuses": statuses, "disagreements": disagreements}


def node_report(state: PipelineState, config) -> dict:
    total_pages = max(state["page_texts"]) if state["page_texts"] else 0
    report = build_report(
        state["assemble_result"].identity,
        state["assemble_result"],
        state["extractions"],
        state["validations"],
        state.get("pipeline_statuses", {}),
        state.get("repair_counts", {}),
        total_pages,
        verify_results=state.get("verify_results", {}),
        verify_rounds=state.get("verify_rounds", {}),
        disagreements=state.get("disagreements", []),
    )
    return {"report": report}


def node_human_approval(state: PipelineState, config) -> dict:
    """Approve -> stage 5+ writes the schedule file and runs the test
    suite (not wired up yet: no schedule registry exists to write into —
    see specs/EXTRACTION_SPEC.md §5.2, build stage 5). Reject -> stop,
    keep the report. Either way this graph's only responsibility is to
    pause and record the decision; the caller acts on `approved` in the
    returned state."""
    decision = interrupt({"report": state["report"]})
    return {"approved": bool(decision.get("approved"))}


def build_graph():
    graph = StateGraph(PipelineState)
    graph.add_node("split", node_split)
    graph.add_node("identity", node_identity)
    graph.add_node("map", node_map)
    graph.add_node("assemble", node_assemble)
    graph.add_node("extract", node_extract)
    graph.add_node("validate", node_validate)
    graph.add_node("verify", node_verify)
    graph.add_node("finalize_statuses", node_finalize_statuses)
    graph.add_node("report", node_report)
    graph.add_node("human_approval", node_human_approval)

    graph.set_entry_point("split")
    graph.add_edge("split", "identity")
    graph.add_edge("identity", "map")
    graph.add_edge("map", "assemble")
    graph.add_edge("assemble", "extract")
    graph.add_edge("extract", "validate")
    graph.add_conditional_edges("validate", route_after_validate, {"extract": "extract", "verify": "verify"})
    graph.add_conditional_edges("verify", route_after_verify, {"extract": "extract", "finalize_statuses": "finalize_statuses"})
    graph.add_edge("finalize_statuses", "report")
    graph.add_edge("report", "human_approval")
    graph.add_edge("human_approval", END)

    return graph.compile(checkpointer=MemorySaver())
