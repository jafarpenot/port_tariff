"""Structured-output schemas for the extraction pipeline's LLM nodes, and
the pure-Python types the deterministic nodes (Assemble, Validate,
Report) pass between each other. Kept separate from state.py so this
module stays pure data shapes, matching the tariffs/models.py
convention — no LLM calls, no LangGraph, no I/O here.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator

from tariffs.models import MODIFIER_COMPATIBLE_VESSEL_FIELDS
from tariffs.rules import Basis, Multiplicity, RoundingMode, TimeRounding


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


class ScanContentType(str, Enum):
    """A `ScannedSection`'s coarse content type — distinct from
    `SectionType` above (which only distinguishes charge/general_terms/
    irrelevant, used by Map's per-window sections): this one separates
    the *base/standard* rate calculation from a *modifier/exception* on
    top of it, the distinction structure-aware Map (Stage 2) is built to
    exploit."""

    BASE_RATE = "base_rate"
    MODIFIER_OR_EXCEPTION = "modifier_or_exception"
    GENERAL_TERMS = "general_terms"
    IRRELEVANT = "irrelevant"


class ScanConfidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ScannedSection(BaseModel):
    """One section of the book, as confirmed (not merely guessed from a
    table of contents) by the structure-scan tool loop actually reading
    at least its first page or two. `start_page`/`end_page` are real PDF
    page numbers, already corrected for any printed-vs-PDF offset —
    never the book's own printed numbers verbatim."""

    heading: str
    section_number: Optional[str] = None
    start_page: int
    end_page: int
    content_type: ScanContentType
    confidence: ScanConfidence = Field(
        description="'high' only if you actually read a page from this section via a tool "
        "call and confirmed it; a boundary taken on faith from the table of contents alone "
        "is 'medium' at most, never 'high'."
    )
    description: str = Field(description="A short description of what's actually here, confirmed by reading the page(s) — not just the ToC title.")
    affects_charges: list[CanonicalCharge] = Field(
        default_factory=list, description="Which canonical charge types this section's content relates to, if any."
    )


class StructureScanResult(BaseModel):
    """Node 1 — Structure scan's output. `notes` is free prose, kept for
    anything that doesn't fit the structured fields below — an unusual
    layout, a concern, anything unanticipated — the same "don't lose
    what wasn't anticipated" reasoning this field always had. `sections`
    and the page-offset fields are new: a verified (tool-read, not
    ToC-guessed) structural map Stage 2's Map node can act on, gated by
    each section's own `confidence`. `glossary` (Stage 4) is a byproduct
    of the same exploration reads, not a separate pass: whenever a
    `general_terms` section is read to confirm it, any marine/cargo
    terminology defined there is worth keeping as shared background
    context for every later node, the same way a human reader carries a
    book's own definitions in mind once they've read them once."""

    notes: str
    page_offset_confirmed: bool = Field(
        default=False, description="True only if you actually read a page via a tool call and compared its own printed page number to its real position in this PDF."
    )
    page_offset: Optional[int] = Field(
        default=None,
        description="printed_page_number + page_offset = pdf_page_number, if a single consistent offset was confirmed across the pages you checked. "
        "Null if not checked, inconsistent across pages, or the book has no printed page numbers to compare.",
    )
    sections: list[ScannedSection] = Field(
        default_factory=list,
        description="Every section you identified, each confirmed by reading at least its first page via a tool call — never a section copied straight from the table of contents without checking it.",
    )
    glossary: str = Field(
        default="",
        description="Marine/cargo terminology definitions actually read in a general_terms section during exploration, as short "
        "term: definition entries — empty if no general_terms section was read, or none defined any unusual terminology.",
    )


# ---------------------------------------------------------------------------
# Node 3 — Map (one call per page window)
# ---------------------------------------------------------------------------


class WindowSection(BaseModel):
    """No `page` field — found live, repeatedly: a model's per-section
    page citation is unreliable even *within* its own window's valid
    range (confirmed on the real TNPA book: one section cited 2 pages
    off, another 1 page off, in the same window, no out-of-range value
    to catch). Downstream (Assemble) now trusts only the window's own
    bounds — ground truth, verified — never a per-section citation. Not
    asking for one at all removes both the failure mode and a field
    that could only ever confuse the model."""

    section_number: Optional[str] = None
    heading: str
    section_type: SectionType
    affects_charges: list[CanonicalCharge] = Field(
        default_factory=list,
        description="Every canonical charge this section sets, modifies, exempts, discounts or surcharges — not just its own main charge.",
    )
    references: list[str] = Field(
        default_factory=list, description='Explicit references found in this section, verbatim, e.g. "clause 6.3", "§4.2", "Annex B".'
    )


class ChargeWindowNote(BaseModel):
    """Per window, per canonical charge — Map's real output, more than
    the section inventory above: not just *whether* a charge is
    discussed here, but a paragraph on *what's here and what kind of
    information it is* (a base rate table, surcharges only, an
    exemption, a cross-reference elsewhere, or nothing at all). This is
    what Extract actually gets handed as orientation before reading the
    attached pages — worth a real paragraph, not a sentence, since it's
    the one summary of this window's content Extract will see before
    diving in."""

    charge: CanonicalCharge
    present: bool = Field(description="Is this charge discussed at all in these pages — a base rate, a surcharge, an exemption, or a cross-reference?")
    notes: str = Field(description="A paragraph on what's here and what kind of information it is. If not present, say so briefly rather than leaving this thin.")
    base_pages: list[int] = Field(
        default_factory=list,
        description="Specific page number(s) actually seen holding this charge's BASE/STANDARD rate calculation — "
        "never guessed or padded with the whole range. Empty if not present or not pinpointable.",
    )
    modifier_pages: list[int] = Field(
        default_factory=list,
        description="Specific page number(s) actually seen holding a MODIFIER/EXCEPTION/SURCHARGE/CONDITION on top "
        "of this charge's base rate. Empty if none, or not pinpointable.",
    )


class WindowMapResult(BaseModel):
    """One Map call's structured output."""

    window_start_page: int
    window_end_page: int
    sections: list[WindowSection] = Field(default_factory=list)
    charge_notes: list[ChargeWindowNote] = Field(default_factory=list)
    metadata_found: ProvisionalIdentity = Field(default_factory=ProvisionalIdentity)

    @model_validator(mode="after")
    def _charge_notes_cover_every_canonical_charge(self) -> "WindowMapResult":
        seen = {note.charge for note in self.charge_notes}
        missing = [c.value for c in CanonicalCharge if c not in seen]
        if missing:
            raise ValueError(f"charge_notes must cover every canonical charge; missing {missing!r}")
        return self


# ---------------------------------------------------------------------------
# Node 4 — Assemble (Python; these are its outputs, not an LLM schema)
# ---------------------------------------------------------------------------


class AssembledSection(BaseModel):
    """`window_start_page`/`window_end_page` name what these actually
    are now: the bounds of the window(s) a section was sighted in, not
    a per-section page range — Assemble no longer derives anything from
    WindowSection's own (removed) page citation, only from the window
    call's own verified bounds."""

    section_number: Optional[str] = None
    heading: str
    section_type: SectionType
    window_start_page: int
    window_end_page: int
    affects_charges: list[CanonicalCharge] = Field(default_factory=list)
    references: list[str] = Field(default_factory=list)


class ChargeContext(BaseModel):
    """A charge's focused context, assembled from the inventory —
    Extract's input, never the whole document (§6.1 node 5). `pages`
    (every page in every window relevant to this charge) is a
    diagnostic, not something Extract reads directly: it exists so a
    run's log can answer "was the page with the value Verify says is
    missing even in Extract's context" directly, instead of guessing
    whether an omission is a Map/Assemble miss or an Extract reasoning
    failure. `notes` is what Extract actually reads as orientation —
    the concatenated per-window ChargeWindowNote paragraphs relevant to
    this charge, advisory only, same as structure_notes.

    `pages` holds the base-rate pages (narrowed to specific `base_pages`
    sightings when Map could pin them down, falling back to the whole
    window/section range otherwise); `modifier_pages` is the same idea
    for modifier/exception content — kept separate so Stage 3's split
    base-rate/modifier Extract calls can each get a tight, targeted
    attachment instead of one broad shared range."""

    charge: CanonicalCharge
    section_numbers: list[str] = Field(default_factory=list)
    pages: list[int] = Field(default_factory=list)
    modifier_pages: list[int] = Field(default_factory=list)
    notes: str = ""


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


class PricingBand(BaseModel):
    """One band row of a `banded` proposal — same shape Validate and the
    evaluator already expect as a dict (`min_exclusive`/`max_inclusive`/
    `base`/`increment_above`/`per_unit_rate`), now a real typed model
    instead of a free dict with those keys hoped-for."""

    min_exclusive: float
    max_inclusive: Optional[float] = None
    base: Optional[float] = None
    increment_above: Optional[float] = None
    per_unit_rate: Optional[float] = None


class PerUnitShape(BaseModel):
    selected: bool = False
    rate: Optional[float] = Field(default=None, description="Required, and only set, if this shape is selected.")


class BasePlusIncrementShape(BaseModel):
    selected: bool = False
    base: Optional[float] = None
    rate: Optional[float] = None


class BandedShape(BaseModel):
    selected: bool = False
    bands: Optional[list[PricingBand]] = None


class BasePlusIncrementTimesDurationShape(BaseModel):
    selected: bool = False
    basic_rate: Optional[float] = None
    daily_rate: Optional[float] = None


class KeyedRateRow(BaseModel):
    """One row of a `keyed_rate` table -- a category label, verbatim as
    this book spells it (a tug/vessel type, a named class -- never a
    continuous numeric range; a table keyed by a range belongs in
    `banded` instead), and its own flat amount or per-basis-unit rate.
    `rate` multiplies the rule's own `basis` value (e.g. hours) --
    there is no separate basis per row, the whole rule shares one."""

    key: str = Field(description="The category label exactly as this book spells it, e.g. a tug name.")
    flat_amount: Optional[float] = None
    rate: Optional[float] = Field(default=None, description="Multiplies the rule's own `basis` value.")

    @model_validator(mode="after")
    def _exactly_one_value(self) -> "KeyedRateRow":
        set_fields = [v for v in (self.flat_amount, self.rate) if v is not None]
        if len(set_fields) != 1:
            raise ValueError("exactly one of flat_amount, rate must be set")
        return self


class KeyedRateShape(BaseModel):
    selected: bool = False
    key_dimension: Optional[str] = Field(default=None, description="What the table is keyed by, in plain language, e.g. 'tug type'.")
    keys: Optional[list[KeyedRateRow]] = None


class TieredUnitRateTier(BaseModel):
    """One tier of a `tiered_unit_rate` table -- a single per-unit rate
    that applies to the WHOLE basis value once it falls in this tier's
    range, never a marginal/incremental rate above a threshold (that's
    `banded`'s job). Confirmed as a genuinely distinct real-world shape:
    Port of Fortaleza's cargo tariff charges one flat rate per tonne for
    the entire shipment, selected by which total-tonnage tier it falls
    into (e.g. up to 25,000t -> R$1.51/t for all of it; 25,000-40,000t
    -> R$1.31/t for all of it) -- not base-plus-increment-above-a-band."""

    min_exclusive: float
    max_inclusive: Optional[float] = None
    rate: float = Field(description="Per-basis-unit rate applied to the ENTIRE basis value once it falls in this tier.")


class TieredUnitRateShape(BaseModel):
    selected: bool = False
    tiers: Optional[list[TieredUnitRateTier]] = None


class DailyRateTier(BaseModel):
    """One escalating day-tier of a `free_period_tiered_daily_rate`
    table -- e.g. Port of Los Angeles' container demurrage: $24.93/day
    for days 1-5 (of the chargeable period), $49.60/day for days 6-10,
    $99.20/day for day 11 onward. `up_to_day` is the day this tier's
    rate stops applying (inclusive, counted from the end of any free
    period) -- null for the last, open-ended tier."""

    up_to_day: Optional[float] = None
    rate_per_unit_per_day: float


class FreePeriodTieredDailyRateShape(BaseModel):
    """A free period before any charge starts, then one or more
    escalating per-day rate tiers on top of the basis -- distinct from
    `base_plus_increment_times_duration`'s single flat daily rate with
    no free period. Confirmed as a genuinely distinct real-world shape:
    PortMiami's wharf demurrage (10 days free, then $1.49/ton/day for
    the next 7 days, $2.35/ton/day from day 8 on) and Port of Tampa's
    container storage (free days, then an escalating per-day rate by
    day-tier) both follow exactly this pattern."""

    selected: bool = False
    free_days: Optional[float] = None
    tiers: Optional[list[DailyRateTier]] = None


class PricingShapes(BaseModel):
    """One field per closed pricing type (tariffs/rules.py's
    `PricingType`), each a fixed, fully-typed shape rather than a free
    `dict[str, Any]` — a model must set `selected=true` on exactly one
    and fill in only that one's fields, leaving the other three
    untouched. Deliberately not a discriminated union: a plain object
    with fixed named fields is the most portable structured-output
    shape across providers, where a `oneOf`/discriminator construct has
    had real, provider-specific rough edges (found live: OpenAI's
    strict structured-output mode rejected this package's old free
    `pricing_params: dict[str, Any]` outright, since every object in a
    strict-mode schema must set `additionalProperties: false` — a free
    dict structurally cannot).

    This closes the actual bug this design replaces: a model could
    previously invent any key name it liked in `pricing_params`, the
    mismatch only surfacing downstream at Validate with a prose
    correction it didn't reliably act on (confirmed recurring
    independently on two different books). Here, an incomplete or
    contradictory answer fails Pydantic validation immediately, inside
    `structured_call()`'s own retry loop — before Validate, before a
    full graph repair round."""

    per_unit: PerUnitShape = Field(default_factory=PerUnitShape)
    base_plus_increment: BasePlusIncrementShape = Field(default_factory=BasePlusIncrementShape)
    banded: BandedShape = Field(default_factory=BandedShape)
    base_plus_increment_times_duration: BasePlusIncrementTimesDurationShape = Field(
        default_factory=BasePlusIncrementTimesDurationShape
    )
    keyed_rate: KeyedRateShape = Field(default_factory=KeyedRateShape)
    tiered_unit_rate: TieredUnitRateShape = Field(default_factory=TieredUnitRateShape)
    free_period_tiered_daily_rate: FreePeriodTieredDailyRateShape = Field(default_factory=FreePeriodTieredDailyRateShape)

    @model_validator(mode="after")
    def _exactly_one_selected_and_complete(self) -> "PricingShapes":
        shapes = {
            "per_unit": self.per_unit,
            "base_plus_increment": self.base_plus_increment,
            "banded": self.banded,
            "base_plus_increment_times_duration": self.base_plus_increment_times_duration,
            "keyed_rate": self.keyed_rate,
            "tiered_unit_rate": self.tiered_unit_rate,
            "free_period_tiered_daily_rate": self.free_period_tiered_daily_rate,
        }
        selected = [name for name, shape in shapes.items() if shape.selected]
        if len(selected) != 1:
            raise ValueError(f"exactly one pricing shape must be selected=true, got {selected!r}")
        chosen = selected[0]
        for name, shape in shapes.items():
            values = shape.model_dump(exclude={"selected"}).values()
            if name == chosen:
                if any(v is None for v in values):
                    raise ValueError(f"selected shape {name!r} is missing required fields: {shape!r}")
                if name == "banded" and not shape.bands:
                    raise ValueError("selected shape 'banded' requires at least one band.")
                if name == "keyed_rate" and not shape.keys:
                    raise ValueError("selected shape 'keyed_rate' requires at least one key.")
                if name == "tiered_unit_rate" and not shape.tiers:
                    raise ValueError("selected shape 'tiered_unit_rate' requires at least one tier.")
                if name == "free_period_tiered_daily_rate" and not shape.tiers:
                    raise ValueError("selected shape 'free_period_tiered_daily_rate' requires at least one tier.")
            elif any(v is not None for v in values):
                raise ValueError(f"unselected shape {name!r} must not have any fields set: {shape!r}")
        return self

    _SHAPE_NAMES = (
        "per_unit",
        "base_plus_increment",
        "banded",
        "base_plus_increment_times_duration",
        "keyed_rate",
        "tiered_unit_rate",
        "free_period_tiered_daily_rate",
    )

    @property
    def pricing_type(self) -> str:
        """Which shape is selected, as a plain string — derived, never a
        second independently-settable field that could disagree with
        what's actually populated."""
        for name in self._SHAPE_NAMES:
            if getattr(self, name).selected:
                return name
        raise AssertionError("unreachable — the model validator guarantees exactly one selection")  # pragma: no cover

    @property
    def params(self) -> dict[str, Any]:
        """The selected shape's own fields as a plain dict, e.g.
        `{"rate": 0.5}` or `{"bands": [...]}` — the same shape
        `pricing_params` used to be, for code that wants a flat view
        (Validate's smoke-calc, the TNPA evaluator) rather than reaching
        into the specific shape object."""
        shape = getattr(self, self.pricing_type)
        dumped = shape.model_dump(exclude={"selected"})
        list_field = {
            "banded": "bands",
            "keyed_rate": "keys",
            "tiered_unit_rate": "tiers",
            "free_period_tiered_daily_rate": "tiers",
        }.get(self.pricing_type)
        if list_field and dumped.get(list_field):
            dumped[list_field] = [item if isinstance(item, dict) else item.model_dump() for item in dumped[list_field]]
        return dumped


class Modifier(BaseModel):
    """A conditional surcharge, discount, or exemption on top of the
    base rate above — a weekend surcharge, a fee per additional tug, a
    delay charge — not something the fixed pricing shapes above are
    meant to express. Every modifier must be captured one way or
    another: `adjustment_percentage`/`adjustment_flat_amount` for the
    common cases, `raw_description` (a verbatim quote) when neither fits
    — e.g. a rate-based delay fee — so a surcharge that doesn't fit a
    clean numeric shape never becomes a reason to leave the whole charge
    unmapped. Confirmed live: towage declined to map specifically
    because its surcharges had nowhere to go (KNOWN_ISSUES.md)."""

    condition: str = Field(
        description="What triggers this modifier, in plain language (e.g. 'outside ordinary working hours', 'per additional tug')."
    )
    adjustment_percentage: Optional[float] = Field(default=None, description="e.g. 25 for a 25% surcharge, -10 for a 10% discount.")
    adjustment_flat_amount: Optional[float] = Field(default=None, description="A flat currency amount, added or subtracted.")
    raw_description: Optional[str] = Field(
        default=None, description="Verbatim source text — use only when the adjustment doesn't fit a plain percentage or flat amount."
    )
    required_vessel_field: Optional[str] = Field(
        default=None,
        description=(
            "Set only if this modifier's condition maps cleanly onto one of a closed set of existing "
            f"vessel-call inputs this tool already asks for: {', '.join(MODIFIER_COMPATIBLE_VESSEL_FIELDS)}. "
            "Leave null for any condition that doesn't match one of these exactly (most will not) — this is "
            "what lets a modifier actually compute when the request states that field, rather than only "
            "ever being reported; it is not worth forcing a loose or approximate match."
        ),
    )

    @model_validator(mode="after")
    def _exactly_one_representation(self) -> "Modifier":
        set_fields = [f for f in (self.adjustment_percentage, self.adjustment_flat_amount, self.raw_description) if f is not None]
        if len(set_fields) != 1:
            raise ValueError("exactly one of adjustment_percentage, adjustment_flat_amount, raw_description must be set")
        return self

    @model_validator(mode="after")
    def _required_vessel_field_is_from_the_closed_set(self) -> "Modifier":
        if self.required_vessel_field is not None and self.required_vessel_field not in MODIFIER_COMPATIBLE_VESSEL_FIELDS:
            raise ValueError(
                f"required_vessel_field {self.required_vessel_field!r} is not one of the supported fields: "
                f"{MODIFIER_COMPATIBLE_VESSEL_FIELDS!r}"
            )
        return self


class ProposedRule(BaseModel):
    """An Extract proposal for a Mapped charge, in the closed vocabulary
    from tariffs/rules.py (basis / rounding / pricing / multiplicity /
    time / min-max / modifiers)."""

    basis: Basis
    rounding_mode: RoundingMode
    rounding_unit: Optional[float] = None
    pricing: PricingShapes
    multiplicity: Multiplicity
    time_unit_hours: Optional[float] = None
    time_rounding: Optional[TimeRounding] = None
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    modifiers: list[Modifier] = Field(default_factory=list)

    @property
    def pricing_type(self) -> str:
        """Read-only, derived from `pricing` — kept so existing code
        that only ever *reads* a rule's shape (Validate's smoke-calc,
        the evaluator, the report/demo printers) didn't need to change
        when `pricing_params` stopped being a free dict."""
        return self.pricing.pricing_type

    @property
    def pricing_params(self) -> dict[str, Any]:
        """Read-only, derived from `pricing`. See `pricing_type` above."""
        return self.pricing.params


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
    unmapped_modifier_notes: list[str] = Field(
        default_factory=list,
        description="Plain-language notes on any modifier/exception/condition that genuinely couldn't be "
        "captured as a Modifier at all (not even raw_description) — flagged here rather than silently dropped.",
    )
    rebuttal: Optional[str] = Field(
        default=None,
        description=(
            "Set only when responding to a verifier challenge (§6.6) and you believe your original "
            "proposal is correct despite it: a specific, evidence-based explanation citing the source "
            "text and pages, with the proposal itself left unchanged. Never set on a first-pass extraction."
        ),
    )


class ModifierExtraction(BaseModel):
    """Stage 3's second, independent call per charge — modifiers only,
    never the base rate or pricing shape (that's the base-rate call's
    job, `ChargeExtraction` above). Best-effort by design: it is fine
    for `modifiers` to come back empty, or for a condition that can't be
    captured even as a verbatim `raw_description` to be noted in
    `unmapped_modifier_notes` instead of forced into the `Modifier`
    shape."""

    modifiers: list[Modifier] = Field(default_factory=list)
    unmapped_modifier_notes: list[str] = Field(default_factory=list)


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

