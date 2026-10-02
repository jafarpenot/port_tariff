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

from tariffs.models import MODIFIER_COMPATIBLE_VESSEL_FIELDS

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

STRUCTURE_SCAN_SYSTEM_PROMPT = (
    "You are looking at an entire port tariff book for the first time, before any "
    "detailed reading — the same first glance a person would take to orient "
    "themselves before searching for anything specific. Describe, in plain prose:\n"
    "- How the document is organised: its overall structure, chapter/section "
    "layout, and roughly where different kinds of content sit (e.g. definitions "
    "near the front, rate tables in the middle, annexes at the end).\n"
    "- Its table of contents, if it has one — list what it says, but note "
    "explicitly that a table of contents' own page numbers may not match this "
    "PDF's actual page numbers; do not treat them as reliable.\n"
    "- Anything unusual about the layout that could trip up someone reading only "
    "one page or a small range in isolation: multi-column pages, scanned or "
    "image-only pages, inconsistent or duplicated page numbering, tables that "
    "span multiple pages, rotated pages, or anything else out of the ordinary.\n\n"
    "This is a first impression, not a verified fact-check — write it as advisory "
    "orientation for someone about to read specific pages closely, not as a claim "
    "about exact values or section numbers. If nothing is unusual about the "
    "layout, say so briefly rather than inventing a concern."
)


STRUCTURE_SCAN_EXPLORATION_SYSTEM_PROMPT = (
    "You just formed a first-glance impression of a port tariff book (given below), "
    "purely from looking at the whole thing once. That impression is an unverified "
    "guess — table-of-contents page numbers in particular are known to be "
    "unreliable. Your job now is to check it, the way a person would actually "
    "flip through a book to confirm what they think they saw, using the tools "
    "available to you (`read_pages`, `search_document`, `get_page_count`) — not by "
    "reasoning about the impression alone.\n\n"
    "Do two things, in order, each bounded — you do not need to use every "
    "round available, stop as soon as you are confident:\n\n"
    "1. VALIDATE THE PAGE NUMBERING. If the book has its own printed page numbers, "
    "pick 2-3 pages (from different parts of the document, including at least one "
    "section the impression claims comes after the opening pages) and read them "
    "with `read_pages` to see what the book's own printed page number is "
    "alongside each one's real position in this PDF. If every page you check "
    "shows the same consistent offset (e.g. the book's 'page 15' is always this "
    "PDF's page 8), that offset is confirmed. If there's no consistent offset, or "
    "the book has no printed page numbers at all, say so plainly rather than "
    "guessing one.\n\n"
    "2. CONFIRM EACH SECTION. For each section your first-glance impression "
    "claimed, read its first page or two (using the offset you just confirmed, if "
    "any, to find the right PDF pages) and check: is this actually what the "
    "impression said it was? What is its real page range? And — the main "
    "reason for this check — is what you're reading the *base/standard rate "
    "calculation* for a charge, a *modifier, exception, surcharge or condition* "
    "on top of one, general *definitions/terms*, or genuinely *irrelevant* to any "
    "vessel-call charge? A section can contain more than one of these — note "
    "that rather than forcing one label if it's a mix. If a section you read is "
    "general definitions/terms, also note any marine or cargo terminology it "
    "actually defines (a term and its definition, verbatim or close to it) — this "
    "becomes shared background context for every later step, so it's worth "
    "capturing while you're already reading the page.\n\n"
    "Only ever call `read_pages`/`search_document` — do not attempt a calculation "
    "or quote a numeric rate; another step handles that later with the real "
    "pages attached. When you are done checking (or have used your available "
    "rounds), stop calling tools — your final message should summarize what you "
    "confirmed, corrected, and could not confirm."
)


STRUCTURE_SCAN_FINAL_SYSTEM_PROMPT = (
    "You are given a first-glance impression of a port tariff book and a record "
    "of what was actually confirmed by reading specific pages (page numbers, "
    "offsets, and section content). Turn this into a final structured answer:\n"
    "- `page_offset_confirmed`/`page_offset`: only set these from what was "
    "actually checked by reading a page — never from the table of contents "
    "alone. Leave `page_offset_confirmed` false if no page was actually read to "
    "verify it.\n"
    "- `sections`: one entry per section that was actually confirmed by reading "
    "it, with its real PDF page range (offset-corrected), its `content_type` "
    "(`base_rate`, `modifier_or_exception`, `general_terms`, or `irrelevant`), "
    "and `confidence` — `high` only for a section whose first page(s) were "
    "actually read and matched the impression; `medium` if read but uncertain, "
    "or boundaries partially inferred; `low` for anything taken on faith from "
    "the table of contents and never actually checked. Never mark `high` for a "
    "section nobody actually looked at.\n"
    "- `glossary`: any marine/cargo terminology definitions actually read during "
    "exploration (a term and its definition, from a general_terms section you "
    "confirmed) — as short 'term: definition' entries. Leave empty if no "
    "general_terms section was read, or none defined anything unusual. Never "
    "invent a definition for a term you did not actually see defined.\n"
    "- `notes`: anything else worth flagging that doesn't fit the above — an "
    "unusual layout, a concern, something the checking round couldn't resolve.\n\n"
    "Be conservative with confidence: an over-confident wrong answer here can "
    "cause a later step to skip pages it should have read, while a correctly "
    "low-confidence answer just falls back to reading everything — the safer "
    "failure mode by far."
)


IDENTITY_SYSTEM_PROMPT = (
    "You identify a tariff book's own metadata from its opening pages: the "
    "issuing authority, jurisdiction, the ports it covers, the schedule's name, "
    "its effective dates, and its currency. Report only what these pages "
    "actually state. Leave a field unset if the opening pages don't say — do "
    "not guess or infer from context, and do not use any tariff book you may "
    "have seen before as a source for this book's values."
)


def _structure_notes_block(structure_notes: str) -> str:
    """Shared framing for the whole-document structure scan's notes,
    wherever a prompt accepts them (Identity, Map, Extract) — always
    advisory, never authoritative, same caution already established for
    ToC page numbers: a description of the document written before
    reading any specific page in detail can be wrong, and the actual
    attached pages are always the real source of truth."""
    if not structure_notes:
        return ""
    return (
        "\n\n---\nNotes from an initial whole-document scan, for context only — "
        "if this disagrees with what you actually see in your attached pages, "
        "trust the attached pages, not these notes:\n" + structure_notes
    )


def _page_mapping_note(pages: list[int]) -> str:
    """A PDF attachment's own internal page count always starts at 1,
    regardless of which book pages it actually contains — found live:
    without this, a model reading an attached slice of pages 5-9 cited
    section locations as "page 1"/"page 4" (the position within the
    attachment), not the book's own page 5/8, silently corrupting every
    downstream page citation. Spelled out explicitly and per-page rather
    than as a single offset, since Extract's attachments are not always
    a contiguous range (ChargeContext.pages can skip pages Map didn't
    flag). Map itself no longer needs this — it doesn't cite pages at
    all any more (see WindowSection/ChargeWindowNote in schemas.py) —
    but Extract still does, for `provenance_pages`."""
    listing = ", ".join(f"attachment page {i} = book page {p}" for i, p in enumerate(pages, start=1))
    return f"This attachment's page numbers do not start at 1. Mapping: {listing}. Always cite the book page number shown here, never the attachment's own page position."


def _map_notes_block(map_notes: str) -> str:
    """Map's own per-window, per-charge paragraphs (ChargeWindowNote),
    concatenated across every window relevant to this charge — advisory
    orientation before reading the attached pages in detail, same
    "trust the attached pages if they disagree" caution as
    structure_notes. Distinct block/wording so it's never confused with
    the whole-document structure scan — this is specifically about the
    one charge being extracted."""
    if not map_notes:
        return ""
    return (
        "\n\n---\nNotes from the mapping pass that selected these pages for this charge, for context "
        "only — if this disagrees with what you actually see in the attached pages, trust the "
        "attached pages, not these notes:\n" + map_notes
    )


def identity_user_prompt(opening_pages_text: str, structure_notes: str = "") -> str:
    return (
        "Opening pages of a port tariff book:\n\n"
        f"{opening_pages_text}\n\n"
        "Report the authority, jurisdiction, ports covered, schedule name, "
        "effective dates and currency, using only what these pages state."
    ) + _structure_notes_block(structure_notes)


MAP_SYSTEM_PROMPT = (
    SCOPE_CONTRACT + "\n\n"
    "Your goal: find everything in this page range that could affect what a vessel is "
    "actually charged for one of the six canonical charges above. This is the only pass "
    "that will ever see these pages in full — a charge you don't flag here is invisible "
    "to every later step, even if it's the one place a real surcharge or exemption is "
    "stated. When genuinely unsure whether something is relevant, flag it; flagging "
    "something dismissed later costs nothing, missing something entirely is gone for "
    "good.\n\n"
    "You have two things to report, and the second is the one that matters most:\n\n"
    "1. Every section whose actual heading and content appears in the attached pages — "
    "never one merely *mentioned* here, such as a table of contents entry, an index "
    "listing, or a cross-reference naming a section that lives elsewhere. A table of "
    "contents naming 'Section 6' is not a sighting of Section 6; only report Section 6 "
    "when its own heading and substance are actually on one of these pages. This matters: "
    "found live, treating a contents-page mention the same as a real sighting caused two "
    "unrelated sections that happen to share a number to be wrongly merged into one, "
    "corrupting what pages got attached downstream. For each real section: its number (if "
    "any), its heading, and its type — 'charge' (it sets a fee for something), "
    "'general_terms' (definitions, or general conditions at the head of a chapter), or "
    "'irrelevant' (anything not about a vessel call charge — training courses, equipment "
    "servicing, licences, and similar). For every section, list every canonical charge "
    "type it affects — not just its own main charge: a section can discount, exempt or "
    "surcharge a charge that isn't its main subject. Also list every explicit reference "
    "you see verbatim (a clause number, a section number, an annex name) and any of the "
    "book's own metadata (authority, jurisdiction, ports, schedule name, effective dates, "
    "currency) this window happens to state. Do not report a page number for a section — "
    "you are not asked for one, and guessing one is worse than not trying: found live, a "
    "model's own per-section page citation is unreliable even for a page within the pages "
    "it was actually given.\n\n"
    "2. For EACH of the six canonical charge types above, one paragraph: is it discussed "
    "at all in these pages, and if so, what's here and what kind of information it is — a "
    "base rate table, surcharges only, an exemption, a cross-reference to elsewhere in the "
    "book, or nothing at all. This is what the extraction step actually reads before "
    "looking at these pages itself, so make it a real paragraph, not a one-line label: "
    "name the sections involved, describe roughly what the numbers/rules cover, and flag "
    "anything that looks incomplete on its own (e.g. 'the base rate is here, but it "
    "references a table that may be elsewhere'). If a charge genuinely isn't discussed "
    "here, say so briefly rather than leaving this thin — every one of the six charges "
    "needs an entry, present or not.\n\n"
    "Also, for each charge that IS present, pinpoint exactly which attached page number(s) "
    "hold the BASE/STANDARD rate calculation (`base_pages`) versus which page number(s) "
    "hold a MODIFIER, EXCEPTION, SURCHARGE, or CONDITION on top of that base rate "
    "(`modifier_pages`) — the two are often not the same page. This is a real, expected "
    "part of the task, not an optional extra — you are only looking at a handful of pages "
    "here, so pinpointing which one(s) actually carry the content you just described in "
    "your own paragraph should usually be straightforward; make a genuine effort before "
    "leaving a list empty. A charge can have both, either, or (rarely) neither pinned to "
    "specific pages. Only list a page number you actually saw the relevant content on — "
    "never guess a page you didn't look at, and never pad a list with every page in the "
    "window just to be safe. Leave a list empty only when you truly cannot tell which "
    "specific page(s) carry it even after trying — not merely because narrowing it down "
    "takes a little more care than reporting the whole window. An empty list is a weaker, "
    "more expensive fallback for everything downstream, not a free default.\n\n"
    "Answer only from the attached pages. If they're blank or unreadable, return no "
    "sections and say so in each charge's notes rather than guessing."
)


def map_user_prompt(window_start: int, window_end: int, structure_notes: str = "") -> str:
    text = f"Pages {window_start}-{window_end} of a port tariff book are attached as a PDF."
    return text + _structure_notes_block(structure_notes)


EXTRACT_SYSTEM_PROMPT = (
    SCOPE_CONTRACT + "\n\n"
    "You are extracting a rate rule for exactly one canonical charge type "
    "from the pages of the tariff book attached as a PDF. Decide one of four outcomes:\n"
    "- mapped: the charge exists here and its calculation can be represented "
    "as one of seven fixed pricing shapes (per_unit, base_plus_increment, "
    "banded, base_plus_increment_times_duration, keyed_rate, tiered_unit_rate, "
    "free_period_tiered_daily_rate). Your `pricing` field always "
    "has all seven shapes present — set `selected: true` on exactly the one "
    "that fits and fill in only that shape's own fields; leave the other "
    "six shapes completely untouched (selected: false, every field null).\n\n"
    "Three of these shapes are easy to confuse with a near neighbor — when a table could "
    "plausibly be more than one, ask the specific question below rather than guessing:\n"
    "- `keyed_rate` vs `banded`: is this table keyed by a genuine category you could count and "
    "list by name — a named tug, vessel, or service type, each with its own rate (`keyed_rate`) "
    "— or by a sequence of numeric thresholds, such as bands of gross tonnage or length "
    "(`banded`)? A numeric range printed as a table with one row per range is still `banded`, "
    "never `keyed_rate`. `keyed_rate` also requires at least two genuinely different "
    "categories — a table with only one row/category is not a meaningful keyed table; use "
    "whichever simpler shape actually fits instead (usually `per_unit` or "
    "`base_plus_increment`), never `keyed_rate` with a single key.\n"
    "- `tiered_unit_rate` vs `banded`: does the table give a base amount PLUS a marginal rate "
    "charged only on the portion of the value ABOVE a threshold (`banded` — progressive "
    "pricing, like an income-tax bracket), or does it give a SINGLE flat per-unit rate that "
    "applies to the ENTIRE basis value once that value falls into a tier (`tiered_unit_rate` — "
    "slab pricing, e.g. 'R1.51/tonne for shipments up to 25,000t, R1.31/tonne for shipments "
    "25,000-40,000t', where the whole shipment is charged at ONE of these rates, never a mix)? "
    "If crossing a threshold changes the rate on the WHOLE quantity rather than just the "
    "portion above it, that is `tiered_unit_rate`, not `banded`.\n"
    "- `free_period_tiered_daily_rate` vs `base_plus_increment_times_duration`: does the "
    "per-day rate stay the same flat amount from day one, with no free period "
    "(`base_plus_increment_times_duration`), or is there a free period before any charge "
    "starts, and/or does the daily rate itself change at different day-count thresholds — "
    "e.g. 'first 10 days free, then $1.49/ton/day for the next 7 days, $2.35/ton/day "
    "thereafter' (`free_period_tiered_daily_rate`)? A single constant daily rate with zero "
    "free days is `base_plus_increment_times_duration`, even if this book also charges a "
    "separate basic/admin fee alongside it.\n\n"
    "Also propose: what it's charged on (basis), a rounding rule, whether it "
    "multiplies by service count or is charged once per call/year "
    "(multiplicity), an optional time period, and optional minimum/maximum "
    "caps.\n"
    "Watch specifically for a rule that bills any partial unit as a full "
    "one — an incomplete or fractional measurement rounds up to the next "
    "whole unit, never charged proportionally or ignored. This can apply to "
    "the charging basis itself (a physical quantity measured in fixed-size "
    "blocks) or to a time period (a service billed per hour, per day, or "
    "some other fixed duration). Books phrase this many different ways — "
    "\"or part thereof\", \"or fraction thereof\", \"rounded up to the next "
    "complete [unit]\", a table column simply labelled \"(rounded up)\" — do "
    "not look for one specific wording; recognise the underlying rule "
    "regardless of how a given book phrases it. When you find it: if it "
    "applies to the basis, set `rounding_mode` to `ceil_to_unit` with the "
    "block size as `rounding_unit`; if it applies to a time period, set "
    "`time_rounding` to `rounded_up` with that duration as `time_unit_hours`. "
    "Never represent this kind of rule as a flat/exact rate — that silently "
    "misstates the charge for any partial unit.\n"
    "First "
    "decide whether this book gives one rate for this charge everywhere, or "
    "a separate rate per port (a table with one column per port, or a "
    "separate rate quoted for each port by name) — if the latter, propose "
    "one rule per port, keyed by the port name exactly as this book spells "
    "it; do not average or pick just one port's column when the book gives "
    "more than one. A conditional surcharge, discount, or exemption on top "
    "of the base rate (an after-hours fee, a per-additional-unit charge, a "
    "delay fee, a coastal-status exemption) is never on its own a reason to "
    "decide 'unmapped' or to leave the whole charge unrepresented — put the "
    "base rate in `pricing` as above and leave `modifiers` empty here; a "
    "separate pass extracts those, you only need the base calculation. Only "
    "decide 'unmapped' "
    "if the *base* calculation itself — not a modifier on top of it — "
    "doesn't fit any of the seven pricing shapes.\n"
    "- bundled: this charge is billed, but only as part of another charge — "
    "name which one. This is not the same as free or absent.\n"
    "- not_present: this book has no such charge. Do not force a match to "
    "the nearest thing you can find.\n"
    "- unmapped: the charge exists and you understand it, but its *base* "
    "calculation logic does not fit any of the seven pricing shapes — quote "
    "the source text instead of inventing an eighth shape.\n\n"
    "Every numeric value you report must be one that literally appears in "
    "the attached pages, on the page you cite for it. Never invent a "
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


MODIFIER_SYSTEM_PROMPT = (
    SCOPE_CONTRACT + "\n\n"
    "You are extracting ONLY the modifiers — conditional surcharges, discounts, or "
    "exemptions — for one canonical charge type, from the pages attached as a PDF. A "
    "separate pass already handles this charge's base/standard rate calculation; do not "
    "decide a pricing shape or a semantic outcome here, and do not report the base rate "
    "itself as a modifier.\n\n"
    "A modifier is any condition that changes the base amount on top of itself — an "
    "after-hours fee, a per-additional-unit charge, a delay fee, a coastal-status "
    "exemption, a tanker surcharge, and similar. For each one, set exactly one of "
    "`adjustment_percentage`, `adjustment_flat_amount`, or `raw_description` (a verbatim "
    "quote, for anything that doesn't reduce to a plain percentage or flat amount) — never "
    "leave all three unset, and never set more than one.\n\n"
    "Also set `required_vessel_field` whenever — and only whenever — a modifier's "
    "condition maps cleanly onto one of this closed list of existing vessel-call inputs: "
    f"{', '.join(MODIFIER_COMPATIBLE_VESSEL_FIELDS)}. For example, a condition reading "
    "'if a tug beyond the standard allocation was requested' maps exactly to "
    "`additional_tug_requested`; a condition that doesn't match one of these fields at all "
    "(most will not — this list is short and specific) should leave `required_vessel_field` "
    "null. Setting this correctly is what lets a modifier actually compute later, when the "
    "request states that field, instead of only ever being reported — do not force a loose "
    "or approximate match just to set it.\n\n"
    "If a condition genuinely cannot be captured as a `Modifier` at all — not even as a "
    "verbatim `raw_description` — note it in plain language in `unmapped_modifier_notes` "
    "instead of dropping it silently. It is completely normal for `modifiers` to come back "
    "empty if this charge genuinely has none in the attached pages; do not invent one to "
    "avoid an empty list.\n\n"
    "Every numeric value you report must literally appear in the attached pages. Never "
    "invent a value, and never carry one over from any other tariff book."
)


def extract_user_prompt(
    charge: str,
    pages: list[int] | None = None,
    notes: str = "",
    pages_attached: bool = True,
    structure_notes: str = "",
    map_notes: str = "",
) -> str:
    text = f"Canonical charge type to extract: {charge}\n\n"
    if pages_attached:
        text += "The relevant pages of this tariff book are attached as a PDF.\n\n" + _page_mapping_note(pages or [])
    else:
        text += "No relevant sections were found in this document for this charge."
    text += _structure_notes_block(structure_notes)
    text += _map_notes_block(map_notes)
    if notes:
        text += "\n\n---\n" + notes
    return text


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
    "the seven pricing shapes; an overlooked cross-reference to another section "
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
