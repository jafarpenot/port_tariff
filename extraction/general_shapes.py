"""An alternative, more general pricing vocabulary for a proposed rate
rule — built alongside extraction/schemas.py's four fixed shapes
(per_unit, base_plus_increment, banded, base_plus_increment_times_duration),
not replacing them. New, isolated file: nothing in extraction/schemas.py,
extraction/extract.py, or anything they touch is modified by this module.

Motivation, confirmed live: RAK Ports' towage tariff is keyed by tug
selection (Ghalilah/Hobby/Hulaylah/...), not by any numeric basis range
at all — none of the four existing shapes, all keyed on a continuous
numeric basis, can represent a rate that varies by a named category
instead. Real-world port tariff research (searched while building this)
confirms this is a common, recurring pattern, not a RAK-specific
quirk — tug type, vessel type, and cargo type are all commonly used as
the keying dimension in real tariff schedules, the same way `banded`
already keys on a GT range.

Deliberately not a fully general/recursive pricing DSL — two primitives
only (a keyed lookup, and a flat-or-linear value per key), covering the
concrete gaps found so far without trying to anticipate every possible
future structure. `varies_by_port` needs no separate representation
here the way ChargeExtraction/ProposedRule needs it: a port name is
just another key, so a port-varying rate is a KeyedTable with
key_dimension="port", the same shape as a tug-varying or GT-banded one.

Experimental and not yet wired into the pipeline: adopt only if a
side-by-side evaluation against TNPA and RAK shows this performs at
least as well as the existing shapes on cases they already handle, and
better on cases they don't (extraction/general_extract.py's own
docstring has the evaluation approach).
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator

from tariffs.rules import Basis, Multiplicity, RoundingMode

from .schemas import CanonicalCharge, SemanticOutcome


class ValueFormula(BaseModel):
    """A flat amount, or a linear function of the charging basis
    (base + rate * units) — subsumes per_unit (base absent/zero) and
    base_plus_increment (base present) as the same shape. Deliberately
    not itself keyed or nested further — see KeyedBand for that."""

    kind: Literal["flat", "linear"]
    flat_amount: Optional[float] = None
    base: Optional[float] = None
    rate: Optional[float] = None

    @model_validator(mode="after")
    def _fields_match_kind(self) -> "ValueFormula":
        if self.kind == "flat":
            if self.flat_amount is None or self.rate is not None:
                raise ValueError("kind='flat' requires flat_amount only, not base/rate")
        else:
            if self.rate is None or self.flat_amount is not None:
                raise ValueError("kind='linear' requires rate (base optional, defaults to 0), not flat_amount")
        return self


class KeyedBand(BaseModel):
    """One row of a keyed lookup table — the key can be a numeric range
    spelled out as text ("50,001-100,000 GT") or a named category
    ("Ocean tug", "Container vessel", a port name). Real tariffs key
    rate tables on both; treating them uniformly as a labelled key with
    a value avoids needing to know in advance which kind a given book
    uses."""

    key: str = Field(description="The label for this row exactly as the book states it -- a GT range, a tug/vessel/cargo type name, a port name, etc.")
    value: ValueFormula


class GeneralModifier(BaseModel):
    """Same escape-hatch philosophy as extraction/schemas.py's Modifier,
    but its structured adjustment reuses ValueFormula instead of being
    limited to percentage/flat — a modifier can itself be rate-based
    (e.g. a delay fee priced per half hour, confirmed live on TNPA's
    towage section as a real case a flat/percentage-only modifier
    couldn't cleanly represent)."""

    condition: str
    adjustment: Optional[ValueFormula] = None
    adjustment_percentage: Optional[float] = None
    raw_description: Optional[str] = None

    @model_validator(mode="after")
    def _exactly_one_representation(self) -> "GeneralModifier":
        set_fields = [f for f in (self.adjustment, self.adjustment_percentage, self.raw_description) if f is not None]
        if len(set_fields) != 1:
            raise ValueError("exactly one of adjustment, adjustment_percentage, raw_description must be set")
        return self


class GeneralProposedRule(BaseModel):
    """An alternative to ProposedRule (extraction/schemas.py) for a
    charge whose rate varies by a dimension none of the four fixed
    pricing shapes can key on. `basis` is set only if a band's linear
    value multiplies a real vessel-call quantity (leave unset for a
    purely categorical table with flat values per key)."""

    key_dimension: str = Field(description="What the table is keyed by, in plain language, e.g. 'tug type', 'vessel category', 'port', 'gross tonnage band'.")
    bands: list[KeyedBand]
    basis: Optional[Basis] = None
    rounding_mode: Optional[RoundingMode] = None
    rounding_unit: Optional[float] = None
    multiplicity: Multiplicity
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    modifiers: list[GeneralModifier] = Field(default_factory=list)

    @model_validator(mode="after")
    def _at_least_one_band(self) -> "GeneralProposedRule":
        if not self.bands:
            raise ValueError("bands must not be empty")
        return self


class GeneralChargeExtraction(BaseModel):
    """Parallel to ChargeExtraction (extraction/schemas.py) — same
    outcome vocabulary, but `proposed_rule` uses the shape above
    instead. No separate varies_by_port/per_port_rules split: a
    port-keyed GeneralProposedRule already covers that case."""

    charge: CanonicalCharge
    outcome: SemanticOutcome
    proposed_rule: Optional[GeneralProposedRule] = Field(default=None, description="Set if and only if outcome is 'mapped'.")
    unmapped_source_text: Optional[str] = Field(default=None, description="Set if and only if outcome is 'unmapped' -- verbatim quote of the source.")
    included_in: Optional[CanonicalCharge] = Field(default=None, description="Set if and only if outcome is 'bundled'.")
    provenance_sections: list[str] = Field(default_factory=list)
    provenance_pages: list[int] = Field(default_factory=list)
