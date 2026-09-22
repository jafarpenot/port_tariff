"""Structured-output schemas for the extraction pipeline's LLM nodes, and
the pure-Python types the deterministic nodes (Assemble, Validate,
Report) pass between each other. Kept separate from state.py so this
module stays pure data shapes, matching the tariffs/models.py
convention — no LLM calls, no LangGraph, no I/O here.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class CanonicalCharge(str, Enum):
    """specs/EXTRACTION_SPEC.md §3.1's six charge types, by function.
    Values match tariffs.schedule.TariffSchedule's field names so a
    Mapped extraction can be written straight into that schema."""

    LIGHT_DUES = "light_dues"
    PORT_DUES = "port_dues"
    TOWAGE = "towage"
    VTS = "vts"
    PILOTAGE = "pilotage"
    BERTHING_SERVICES = "berthing_services"


class SectionType(str, Enum):
    CHARGE = "charge"
    GENERAL_TERMS = "general_terms"
    IRRELEVANT = "irrelevant"


# ---------------------------------------------------------------------------
# Node 2 — provisional schedule identity
# ---------------------------------------------------------------------------


class ProvisionalIdentity(BaseModel):
    """From the opening pages only (§5.1) — finalised later by Assemble,
    which sees the whole document. Every field optional: an opening page
    may not state all of these."""

    authority: Optional[str] = None
    jurisdiction: Optional[str] = None
    ports: list[str] = Field(
        default_factory=list,
        description=(
            "Individual port names, each its own list entry, e.g. ['Durban', 'Cape Town']. "
            "If the text only describes coverage generically ('all South African ports') "
            "without naming them, leave this empty — do not put the generic phrase here."
        ),
    )
    schedule_name: Optional[str] = None
    effective_from: Optional[str] = None
    effective_to: Optional[str] = None
    currency: Optional[str] = Field(
        default=None, description="An ISO 4217 currency code (e.g. 'ZAR', 'USD'), not the spelled-out currency name."
    )


# ---------------------------------------------------------------------------
# Node 3 — Map (one call per page window)
# ---------------------------------------------------------------------------


class WindowSection(BaseModel):
    section_number: Optional[str] = None
    heading: str
    section_type: SectionType
    page: int = Field(description="The page this section's heading appears on — pages in your context are marked '[page N]'.")
    affects_charges: list[CanonicalCharge] = Field(
        default_factory=list,
        description="Every canonical charge this section sets, modifies, exempts, discounts or surcharges — not just its own main charge.",
    )
    references: list[str] = Field(
        default_factory=list, description='Explicit references found in this section, verbatim, e.g. "clause 6.3", "§4.2", "Annex B".'
    )


class WindowMapResult(BaseModel):
    """One Map call's structured output."""

    window_start_page: int
    window_end_page: int
    sections: list[WindowSection] = Field(default_factory=list)
    metadata_found: ProvisionalIdentity = Field(default_factory=ProvisionalIdentity)


# ---------------------------------------------------------------------------
# Node 4 — Assemble (Python; these are its outputs, not an LLM schema)
# ---------------------------------------------------------------------------


class AssembledSection(BaseModel):
    section_number: Optional[str] = None
    heading: str
    section_type: SectionType
    page_start: int
    page_end: int
    affects_charges: list[CanonicalCharge] = Field(default_factory=list)
    references: list[str] = Field(default_factory=list)
    text: str


class ChargeContext(BaseModel):
    """A charge's focused context, assembled from the inventory —
    Extract's input, never the whole document (§6.1 node 5)."""

    charge: CanonicalCharge
    section_numbers: list[str] = Field(default_factory=list)
    combined_text: str


# ---------------------------------------------------------------------------
# Node 5 — Extract (one call per charge)
# ---------------------------------------------------------------------------


class SemanticOutcome(str, Enum):
    """§3.2 — owned by Extract, never by Validate or the workflow."""

    MAPPED = "mapped"
    BUNDLED = "bundled"
    NOT_PRESENT = "not_present"
    UNMAPPED = "unmapped"


class SectionConsideredStatus(str, Enum):
    USED = "used"
    DISMISSED = "dismissed"


class SectionConsidered(BaseModel):
    section_number: Optional[str] = None
    heading: str
    status: SectionConsideredStatus
    reason: str
    found_via_lead: bool = Field(
        default=False, description="True if this section was found by following a lead with the search tool, not present in the assembled context set."
    )


class ProposedRule(BaseModel):
    """An Extract proposal for a Mapped charge, in the closed vocabulary
    from tariffs/rules.py (basis / rounding / pricing / multiplicity /
    time / min-max). `pricing_params` is intentionally a loose dict here
    rather than a second discriminated union duplicating every pricing
    type's parameter shape — the real, strict shape check happens once,
    at Validate, against tariffs.rules/tariffs.schedule directly. This
    schema only has to be strict about the things a model must not
    invent freely: the four closed-enum fields below."""

    basis: str
    rounding_mode: str
    rounding_unit: Optional[float] = None
    pricing_type: str
    pricing_params: dict[str, Any] = Field(default_factory=dict)
    multiplicity: str
    time_unit_hours: Optional[float] = None
    time_rounding: Optional[str] = None
    minimum: Optional[float] = None
    maximum: Optional[float] = None


class ChargeExtraction(BaseModel):
    charge: CanonicalCharge
    outcome: SemanticOutcome
    varies_by_port: bool = Field(
        default=False,
        description=(
            "True if this book gives a different rate for this charge per port (a table with one "
            "column per port). False if it's a single rate that applies everywhere."
        ),
    )
    proposed_rule: Optional[ProposedRule] = Field(
        default=None, description="Set if and only if outcome is 'mapped' and varies_by_port is false."
    )
    per_port_rules: dict[str, ProposedRule] = Field(
        default_factory=dict,
        description=(
            "Set if and only if outcome is 'mapped' and varies_by_port is true — one entry per port, "
            "keyed by the port name exactly as this book spells it (e.g. 'Durban', not a code)."
        ),
    )
    included_in: Optional[CanonicalCharge] = Field(default=None, description="Set if and only if outcome is 'bundled'.")
    unmapped_source_text: Optional[str] = Field(default=None, description="Set if and only if outcome is 'unmapped' — the quoted source text.")
    provenance_sections: list[str] = Field(default_factory=list)
    provenance_pages: list[int] = Field(default_factory=list)
    sections_considered: list[SectionConsidered] = Field(default_factory=list)
    rebuttal: Optional[str] = Field(
        default=None,
        description=(
            "Set only when responding to a verifier challenge (§6.6) and you believe your original "
            "proposal is correct despite it: a specific, evidence-based explanation citing the source "
            "text and pages, with the proposal itself left unchanged. Never set on a first-pass extraction."
        ),
    )


# ---------------------------------------------------------------------------
# Node 6 — Validate
# ---------------------------------------------------------------------------


class ValidationSeverity(str, Enum):
    HARD = "hard"
    WARNING = "warning"


class ValidationIssue(BaseModel):
    severity: ValidationSeverity
    message: str
    allowed_options: Optional[list[str]] = None


class ValidationResult(BaseModel):
    charge: CanonicalCharge
    valid: bool
    issues: list[ValidationIssue] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# §3.2 — pipeline statuses, set by the workflow, never by a model
# ---------------------------------------------------------------------------


class PipelineStatus(str, Enum):
    EXTRACTION_FAILED = "extraction_failed"
    SYSTEM_ERROR = "system_error"


# ---------------------------------------------------------------------------
# Node 7 — Verify (§6.6). The one genuinely agentic node: independent
# context, adversarial objective, concrete findings, no confidence scores.
# ---------------------------------------------------------------------------


class VerifierSeverity(str, Enum):
    MATERIAL = "material"  # would change a number a vessel is actually charged — drives a repair round
    MINOR = "minor"  # recorded in the report, does not trigger a repair round


class VerifierFinding(BaseModel):
    severity: VerifierSeverity
    problem: str = Field(description="A specific, checkable problem — never a vague 'this might be wrong'.")
    pages: list[int] = Field(default_factory=list, description="The page(s) that support this concern.")


class VerifierResult(BaseModel):
    charge: CanonicalCharge
    findings: list[VerifierFinding] = Field(default_factory=list)


def has_material_finding(result: Optional["VerifierResult"]) -> bool:
    return result is not None and any(f.severity is VerifierSeverity.MATERIAL for f in result.findings)


class Disagreement(BaseModel):
    """§6.6: still disagreeing after the verify-repair budget is
    exhausted. Information for the reviewer, not a pipeline failure —
    never looped until the models agree."""

    charge: CanonicalCharge
    extractor_interpretation: str
    extractor_pages: list[int] = Field(default_factory=list)
    verifier_concern: str
    verifier_pages: list[int] = Field(default_factory=list)
    status: str = "unresolved"


# ---------------------------------------------------------------------------
# Node 8 — review report (§7). Written for a business reviewer; must be
# readable without opening the code.
# ---------------------------------------------------------------------------


class ChargeReportEntry(BaseModel):
    charge: CanonicalCharge
    outcome: Optional[SemanticOutcome] = None
    status: Optional[PipelineStatus] = None
    varies_by_port: bool = False
    proposed_rule: Optional[ProposedRule] = None
    per_port_rules: dict[str, ProposedRule] = Field(default_factory=dict)
    included_in: Optional[CanonicalCharge] = None
    unmapped_source_text: Optional[str] = None
    provenance_sections: list[str] = Field(default_factory=list)
    provenance_pages: list[int] = Field(default_factory=list)
    sections_considered: list[SectionConsidered] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    repair_attempts: int = 0
    verifier_findings: list[VerifierFinding] = Field(default_factory=list)
    verify_rounds: int = 0


class ReviewReport(BaseModel):
    identity: ProvisionalIdentity
    is_new_edition: bool
    matched_existing_authority: Optional[str] = None
    charges: list[ChargeReportEntry] = Field(default_factory=list)
    out_of_scope_sections: list[str] = Field(default_factory=list)
    coverage_pages_read: int = 0
    coverage_total_pages: int = 0
    general_terms_found: bool = True
    assumptions: list[str] = Field(default_factory=list)
    disagreements: list[Disagreement] = Field(default_factory=list)

