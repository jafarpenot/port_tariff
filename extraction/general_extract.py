"""A standalone, experimental extraction path using general_shapes.py's
more general pricing vocabulary instead of extraction/schemas.py's four
fixed shapes. Not wired into pipeline.py or graph.py — this is deliberately
a separate entry point for one-off, single-charge evaluation, so it can
be compared against the existing path without risking anything already
working. See general_shapes.py's own docstring for the motivation.

Evaluation approach: run extract_charge_general() on the same
(charge, pages) case already tried through the existing extract_charge()
(extraction/extract.py) — first on a case the existing shapes handle
well (TNPA's towage table, to make sure this doesn't regress an already-
solved case), then on a case they don't (RAK's tug-selection-keyed
towage table, which the existing shapes cannot represent at all — see
KNOWN_ISSUES.md). Adopt (fully, or as a fallback when the existing
shapes come back unmapped) only if the comparison favours it.
"""

from __future__ import annotations

import base64
from typing import Any

from .general_shapes import GeneralChargeExtraction
from .llm import structured_call
from .pdf import extract_pdf_pages
from .prompts import SCOPE_CONTRACT

GENERAL_EXTRACT_SYSTEM_PROMPT = (
    SCOPE_CONTRACT + "\n\n"
    "You are extracting a rate rule for exactly one canonical charge type from the pages of "
    "the tariff book attached as a PDF, using a general table-based vocabulary instead of a "
    "small set of fixed formulas. Decide one of four outcomes:\n"
    "- mapped: propose a `GeneralProposedRule` — a table of `bands`, each with a `key` (the "
    "label this book uses for that row, verbatim: a GT range, a tug/vessel/cargo type name, a "
    "port name, a duration bracket — whatever the book's own table is actually organised by) "
    "and a `value` that is either `flat` (set only `flat_amount`; leave `rate` and `base` "
    "unset) or `linear` (set `rate`; set `base` too if there's a fixed component, otherwise "
    "leave it unset — but never set `flat_amount` on a linear value). Set `key_dimension` to "
    "name what the table is keyed by, in plain "
    "language. If the book gives one single rate with no table at all, that is still a table "
    "with exactly one band. If the rate varies by port, the port name is the key — there is no "
    "separate per-port mechanism, a port-keyed table is the same shape as any other. Only set "
    "`basis` if a band's `linear` value multiplies a real vessel-call quantity (tonnage, "
    "length); leave it unset for a purely categorical table of flat amounts.\n"
    "- bundled: this charge is billed, but only as part of another charge — name which one.\n"
    "- not_present: this book has no such charge. Do not force a match to the nearest thing "
    "you can find.\n"
    "- unmapped: the charge exists and you understand it, but even this general table shape "
    "cannot represent it — quote the source text instead of inventing something looser.\n\n"
    "A conditional surcharge, discount, or exemption on top of the base rate is never on its "
    "own a reason to decide 'unmapped' — put it in `modifiers` instead: a structured "
    "`adjustment` (reusing the same flat/linear value shape) or `adjustment_percentage` when "
    "either fits cleanly, or `raw_description` (a verbatim quote) when neither does. Every "
    "modifier must set exactly one of `adjustment`, `adjustment_percentage`, or "
    "`raw_description` — never leave all three unset (quote it verbatim into "
    "`raw_description` rather than dropping it), and never set more than one. Every "
    "numeric value you report must literally appear in the attached pages, on the page you "
    "cite for it. Never invent a value, and never carry one over from any other tariff book."
)


def _charge_content(charge_value: str, pdf_path: str, pages: list[int]) -> str | list:
    text = f"Canonical charge type to extract: {charge_value}\n\nThe relevant pages of this tariff book are attached as a PDF."
    if not pages:
        return f"Canonical charge type to extract: {charge_value}\n\nNo relevant sections were found in this document for this charge."
    listing = ", ".join(f"attachment page {i} = book page {p}" for i, p in enumerate(pages, start=1))
    text += f"\n\nThis attachment's page numbers do not start at 1. Mapping: {listing}. Always cite the book page number shown here."
    pdf_bytes = extract_pdf_pages(pdf_path, pages)
    b64 = base64.b64encode(pdf_bytes).decode()
    return [
        {"type": "text", "text": text},
        {"type": "file", "source_type": "base64", "mime_type": "application/pdf", "data": b64, "filename": f"{charge_value}-context.pdf"},
    ]


def extract_charge_general(charge: Any, pdf_path: str, pages: list[int], llm: Any) -> GeneralChargeExtraction:
    """No tool-loop, no repair machinery — a deliberately minimal,
    single-shot call for evaluating the shape vocabulary itself, not a
    drop-in replacement for extract_charge()'s full behaviour."""
    extraction = structured_call(
        llm, GeneralChargeExtraction, GENERAL_EXTRACT_SYSTEM_PROMPT, _charge_content(charge.value, pdf_path, pages)
    )
    extraction.charge = charge
    return extraction
