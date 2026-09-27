"""Node 4 — Assemble (§6.1). Python, deterministic — no LLM call.

Merges Map's per-window sections into one inventory, resolves explicit
and implicit (chapter/heading-hierarchy) references, and builds each
charge's focused context set — Extract's input, never the whole
document.
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field

from .schemas import (
    AssembledSection,
    CanonicalCharge,
    ChargeContext,
    ProvisionalIdentity,
    SectionType,
    WindowMapResult,
    WindowSection,
)


@dataclass
class AssembleResult:
    sections: list[AssembledSection]
    charge_contexts: dict[CanonicalCharge, ChargeContext]
    identity: ProvisionalIdentity
    out_of_scope_sections: list[AssembledSection] = field(default_factory=list)
    general_terms_found: bool = True


def _section_key(section: WindowSection) -> str:
    if section.section_number:
        return f"num:{section.section_number.strip().lstrip('§').strip().lower()}"
    return f"heading:{' '.join(section.heading.lower().split())}"


def merge_sections(map_results: list[WindowMapResult]) -> list[AssembledSection]:
    """Overlaps produce duplicate sightings of the same section across
    windows: deduplicate by (section_number, or normalised heading if
    none), and where sightings disagree on charge tags, take the union —
    considering one section too many is cheap, missing a modifier is not.

    A section's page range is the union of the *window bounds* it was
    sighted in — never a per-section page citation (WindowSection no
    longer has one; found live, repeatedly unreliable even within a
    window's own valid range). The window call's own start/end is
    ground truth (map_document() overwrites it from the real range
    regardless of what the model echoes)."""
    grouped: dict[str, list[tuple[WindowSection, WindowMapResult]]] = defaultdict(list)
    for window in map_results:
        for section in window.sections:
            grouped[_section_key(section)].append((section, window))

    merged: list[AssembledSection] = []
    for sightings in grouped.values():
        charges: set[CanonicalCharge] = set()
        references: set[str] = set()
        window_pages: set[int] = set()
        for s, window in sightings:
            charges.update(s.affects_charges)
            references.update(s.references)
            window_pages.update(range(window.window_start_page, window.window_end_page + 1))
        window_start_page, window_end_page = min(window_pages), max(window_pages)

        types = {s.section_type for s, _ in sightings}
        if SectionType.CHARGE in types:
            section_type = SectionType.CHARGE
        elif SectionType.GENERAL_TERMS in types:
            section_type = SectionType.GENERAL_TERMS
        else:
            section_type = SectionType.IRRELEVANT

        first_section = sightings[0][0]
        merged.append(
            AssembledSection(
                section_number=first_section.section_number,
                heading=first_section.heading,
                section_type=section_type,
                window_start_page=window_start_page,
                window_end_page=window_end_page,
                affects_charges=sorted(charges, key=lambda c: c.value),
                references=sorted(references),
            )
        )
    return sorted(merged, key=lambda s: s.window_start_page)


def _normalize_ref(text: str) -> str:
    t = text.strip().lower().lstrip("§").strip()
    t = re.sub(r"^(section|clause|annex|appendix)\s*", "", t)
    return t.strip().rstrip(".")


def _resolve_reference(ref: str, by_number: dict[str, AssembledSection]) -> AssembledSection | None:
    target = _normalize_ref(ref)
    for section in by_number.values():
        if section.section_number and _normalize_ref(section.section_number) == target:
            return section
    return None


def _chapter_of(section_number: str | None) -> str | None:
    if not section_number:
        return None
    return section_number.split(".")[0].strip()


def build_charge_contexts(sections: list[AssembledSection], map_results: list[WindowMapResult]) -> dict[CanonicalCharge, ChargeContext]:
    """Each charge's context set (§6.1 node 4): its main section(s), every
    section tagged as affecting it, the general terms its chapter
    inherits, and any explicitly referenced section — plus, additively
    (never a replacement for the section-tag mechanism above, same
    "flag it, cheap to over-include" bias everywhere else in this
    module), every window Map's own per-charge notes (`charge_notes`)
    flagged as `present` for this charge. The two mechanisms can
    disagree — a window with no section explicitly tagged for a charge
    might still have a relevant charge_notes entry it caught only at
    the coarser, whole-window judgment — union rather than pick one."""
    by_number = {s.section_number: s for s in sections if s.section_number}
    general_terms_sections = [s for s in sections if s.section_type is SectionType.GENERAL_TERMS]

    contexts: dict[CanonicalCharge, ChargeContext] = {}
    for charge in CanonicalCharge:
        relevant = [s for s in sections if charge in s.affects_charges]
        section_numbers: list[str] = []
        pages: set[int] = set()
        seen_keys: set[str] = set()

        def _add(section: AssembledSection) -> None:
            key = section.section_number or section.heading
            if key in seen_keys:
                return
            seen_keys.add(key)
            if section.section_number:
                section_numbers.append(section.section_number)
            pages.update(range(section.window_start_page, section.window_end_page + 1))

        for s in relevant:
            _add(s)
            chapter = _chapter_of(s.section_number)
            if chapter:
                for gt in general_terms_sections:
                    if _chapter_of(gt.section_number) == chapter:
                        _add(gt)
            for ref in s.references:
                resolved = _resolve_reference(ref, by_number)
                if resolved is not None:
                    _add(resolved)

        notes: list[str] = []
        for window in map_results:
            for note in window.charge_notes:
                if note.charge is not charge or not note.present:
                    continue
                pages.update(range(window.window_start_page, window.window_end_page + 1))
                notes.append(note.notes)

        contexts[charge] = ChargeContext(
            charge=charge,
            section_numbers=section_numbers,
            pages=sorted(pages),
            notes="\n\n".join(notes),
        )
    return contexts


def finalize_identity(provisional: ProvisionalIdentity, map_results: list[WindowMapResult]) -> ProvisionalIdentity:
    """Node 2's identity, filled in from whatever Map additionally found
    across the whole document — provisional's own fields take priority
    since they come from the pages most likely to state this cleanly."""
    merged = provisional.model_copy()
    for window in map_results:
        found = window.metadata_found
        if not merged.authority and found.authority:
            merged.authority = found.authority
        if not merged.jurisdiction and found.jurisdiction:
            merged.jurisdiction = found.jurisdiction
        if not merged.ports and found.ports:
            merged.ports = found.ports
        if not merged.schedule_name and found.schedule_name:
            merged.schedule_name = found.schedule_name
        if not merged.effective_from and found.effective_from:
            merged.effective_from = found.effective_from
        if not merged.effective_to and found.effective_to:
            merged.effective_to = found.effective_to
        if not merged.currency and found.currency:
            merged.currency = found.currency
    return merged


def assemble(
    map_results: list[WindowMapResult],
    provisional_identity: ProvisionalIdentity,
) -> AssembleResult:
    sections = merge_sections(map_results)
    charge_contexts = build_charge_contexts(sections, map_results)
    identity = finalize_identity(provisional_identity, map_results)
    out_of_scope = [s for s in sections if s.section_type is SectionType.CHARGE and not s.affects_charges]
    general_terms_found = any(s.section_type is SectionType.GENERAL_TERMS for s in sections)
    return AssembleResult(
        sections=sections,
        charge_contexts=charge_contexts,
        identity=identity,
        out_of_scope_sections=out_of_scope,
        general_terms_found=general_terms_found,
    )
