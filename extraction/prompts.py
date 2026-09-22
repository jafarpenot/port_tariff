"""Prompt templates for the LLM nodes (identity, Map, Extract).

specs/EXTRACTION_SPEC.md §8's cross-cutting constraint: none of these may
name TNPA, a TNPA port, a TNPA section number, or a TNPA rate value —
doing so would let the TNPA accuracy score (§8 eval 1) and the seeded-error
catch rate (§8 eval 3) measure memorisation of this book instead of
generalisation to a new one. tests/extraction/test_prompts_are_authority_agnostic.py
enforces this with a denylist scan; it is not just a rule stated here.

The six canonical charge definitions below ARE meant to be in every
prompt — they are the scope contract itself (§3.1), generic by
construction ("national navigation aids", not "TNPA light dues"), not a
TNPA fact.
"""

from __future__ import annotations

CANONICAL_CHARGES_TABLE = """\
Canonical charge type | What it pays for
light_dues | National navigation aids (lighthouses, buoys). Usually once per visit to the country, on tonnage.
port_dues | Occupying the port. Tonnage-based, usually with a time component.
towage | Tug assistance for manoeuvring, per service.
vts | Vessel traffic service (harbour radar/radio control), per call.
pilotage | A licensed pilot conning the vessel in or out, per service.
berthing_services | Shore mooring gang making the vessel fast / letting go, per service.
"""

SCOPE_CONTRACT = (
    "You are reading one page-range window of a port authority's tariff book. "
    "These six charge types are defined by function, not by whatever name this "
    "particular book happens to use for them — a different authority may call "
    "port dues 'harbour dues', or use a different section-numbering scheme "
    "entirely. Identify charges by what they actually charge for, never by "
    "matching a title string.\n\n" + CANONICAL_CHARGES_TABLE
)

IDENTITY_SYSTEM_PROMPT = (
    "You identify a tariff book's own metadata from its opening pages: the "
    "issuing authority, jurisdiction, the ports it covers, the schedule's name, "
    "its effective dates, and its currency. Report only what these pages "
    "actually state. Leave a field unset if the opening pages don't say — do "
    "not guess or infer from context, and do not use any tariff book you may "
    "have seen before as a source for this book's values."
)


def identity_user_prompt(opening_pages_text: str) -> str:
    return (
        "Opening pages of a port tariff book:\n\n"
        f"{opening_pages_text}\n\n"
        "Report the authority, jurisdiction, ports covered, schedule name, "
        "effective dates and currency, using only what these pages state."
    )


MAP_SYSTEM_PROMPT = (
    SCOPE_CONTRACT + "\n\n"
    "For the page window you are given, list every section present: its "
    "number (if any), its heading, and its type — 'charge' (it sets a fee "
    "for something), 'general_terms' (definitions, or general conditions at "
    "the head of a chapter), or 'irrelevant' (anything not about a vessel "
    "call charge — training courses, equipment servicing, licences, and "
    "similar). For every section, list every canonical charge type it "
    "affects — not just its own main charge: a section can discount, exempt "
    "or surcharge a charge that isn't its main subject. Also list every "
    "explicit reference you see verbatim (a clause number, a section number, "
    "an annex name) and any of the book's own metadata (authority, "
    "jurisdiction, ports, schedule name, effective dates, currency) this "
    "window happens to state.\n\n"
    "Answer only from the text you are given. If a window's text is empty or "
    "unreadable, return no sections rather than guessing."
)


def map_user_prompt(window_start: int, window_end: int, window_text: str) -> str:
    return f"Pages {window_start}-{window_end} of a port tariff book:\n\n{window_text}"


EXTRACT_SYSTEM_PROMPT = (
    SCOPE_CONTRACT + "\n\n"
    "You are extracting a rate rule for exactly one canonical charge type "
    "from the source text you are given. Decide one of four outcomes:\n"
    "- mapped: the charge exists here and its calculation can be represented "
    "as one of four fixed pricing shapes (per_unit, base_plus_increment, "
    "banded, base_plus_increment_times_duration), each with: what it's "
    "charged on (basis), a rounding rule, whether it multiplies by service "
    "count or is charged once per call/year (multiplicity), an optional time "
    "period, and optional minimum/maximum caps. Propose exactly that. First "
    "decide whether this book gives one rate for this charge everywhere, or "
    "a separate rate per port (a table with one column per port, or a "
    "separate rate quoted for each port by name) — if the latter, propose "
    "one rule per port, keyed by the port name exactly as this book spells "
    "it; do not average or pick just one port's column when the book gives "
    "more than one.\n"
    "- bundled: this charge is billed, but only as part of another charge — "
    "name which one. This is not the same as free or absent.\n"
    "- not_present: this book has no such charge. Do not force a match to "
    "the nearest thing you can find.\n"
    "- unmapped: the charge exists and you understand it, but its "
    "calculation logic does not fit any of the four pricing shapes — quote "
    "the source text instead of inventing a fifth shape.\n\n"
    "Every numeric value you report must be one that literally appears in "
    "the text you were given, on the page you cite for it. Never invent a "
    "value, and never carry over a value from any other tariff book. Cite "
    "the section number and page range your proposal comes from. List every "
    "section in your given context as used or dismissed, with a reason — "
    "this makes your reasoning checkable by a human who has not read the "
    "whole book.\n\n"
    "You have a search tool over the whole document's page texts, to be used "
    "only to follow a lead — an explicit reference in your context pointing "
    "outside it. Do not use it to go looking for a better answer once you "
    "already have one from your given context."
)


def extract_user_prompt(charge: str, context_text: str) -> str:
    return f"Canonical charge type to extract: {charge}\n\nYour context (assembled from the document):\n\n{context_text}"


VERIFY_SYSTEM_PROMPT = (
    SCOPE_CONTRACT + "\n\n"
    "You are an independent, adversarial reviewer checking one proposal made by "
    "someone else. You have not seen how they reached their answer and you "
    "should not assume it is correct — your job is to find what is wrong with "
    "it, not to confirm it. You have whole-document search and read tools; use "
    "them to check the proposal against the source text directly, never against "
    "your own assumptions about what a typical tariff book contains.\n\n"
    "Specifically hunt for: a rate or value that does not match what the source "
    "actually prints, including a value copied from the wrong port's column; a "
    "missing condition, modifier, exemption, surcharge, or minimum/maximum that "
    "the source states but the proposal omits; a semantic outcome that is wrong "
    "— a charge marked not_present that is actually bundled into another "
    "charge, or the reverse, or one marked unmapped that actually fits one of "
    "the four pricing shapes; an overlooked cross-reference to another section "
    "that changes the charge's rate or applicability; an assumption stated as "
    "fact that the source does not actually support.\n\n"
    "Report concrete findings only. Each one must name the specific problem and "
    "cite the page(s) that support your concern — never a vague 'this might be "
    "wrong' and never a confidence score. If you found nothing specific and "
    "checkable, report no findings; do not manufacture one to have something to "
    "say. Mark each finding 'material' if acting on it would change a number a "
    "vessel is actually charged, or 'minor' for anything else (a citation "
    "detail, an omission that does not affect the amount)."
)


def verify_user_prompt(charge: str, proposal_summary: str, extra_context: str = "") -> str:
    text = f"Canonical charge type under review: {charge}\n\nThe proposal to verify:\n{proposal_summary}"
    if extra_context:
        text += f"\n\n---\nWhat you found searching/reading the source directly:\n{extra_context}"
    return text
