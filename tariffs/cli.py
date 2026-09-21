"""v3: command-line entry point — `python -m tariffs.cli "<free-text request>"`.

Wrapping only. No calculation or business logic lives here. Every normal
request goes through `tariffs.nlp.parse_vessel_request()` and renders
whatever `ParseResult` comes back (`Parsed` or `Rejected`) — this module
never calls `tariffs.engine.calculate()` itself, with exactly one
deliberate, explicit exception: `--json` bypasses the LLM parser entirely
to run a hand-built `VesselCall` through the engine directly, precisely
so the CLI is exercisable with no API key.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Optional

from .engine import calculate
from .models import CalculationResult, VesselCall
from .nlp import BERTHING_SERVICES_NOTE, Parsed, ParseResult, Rejected, parse_vessel_request

_TARIFF_ORDER = [
    "light_dues",
    "port_dues",
    "towage_dues",
    "vts_dues",
    "pilotage_dues",
    "berthing_services",
]

_TARIFF_LABELS = {
    "light_dues": "Light dues",
    "port_dues": "Port dues",
    "towage_dues": "Towage dues",
    "vts_dues": "VTS dues",
    "pilotage_dues": "Pilotage dues",
    # "berthing_services" everywhere (the honest domain name), consistent
    # with the API/Streamlit — the §3.8/§3.9 explanation is printed as a
    # separate note line right below it instead (README §3).
    "berthing_services": "Berthing services",
}


# ---------------------------------------------------------------------------
# Rendering — pure formatting, no calculation
# ---------------------------------------------------------------------------


def _print_header(title: str) -> None:
    print()
    print(title)
    print("-" * len(title))


def _format_tariff_line(label: str, amount: Optional[float], reason: Optional[str]) -> str:
    if amount is not None:
        return f"  {label:55s} {amount:>14,.2f} ZAR"
    if reason:
        # `reason` already reads "not computable — ..." (built once, at
        # the source, in tariffs/nlp.py) — don't prepend it again here.
        return f"  {label:55s} {reason}"
    return f"  {label:55s} not computed"


def _print_trace_steps(steps) -> None:
    for step in steps:
        resolution = f" [{step.modifier_resolution}]" if step.modifier_resolution else ""
        subtotal = f" = {step.subtotal:,.2f}" if step.subtotal is not None else ""
        print(f"  [{step.tariff} §{step.section} p.{step.page}] {step.description}{resolution}{subtotal}")


def render_parsed(parsed: Parsed) -> None:
    _print_header("Parsed vessel call")
    evidence_by_field = {e.field: e for e in parsed.evidence}
    for field_name in VesselCall.model_fields:
        if field_name not in evidence_by_field:
            continue  # only show fields actually populated from the request text
        entry = evidence_by_field[field_name]
        value = getattr(parsed.call, field_name)
        flag = "" if entry.verified else "  [UNVERIFIED QUOTE]"
        print(f'  {field_name:35s} = {value!r}    (from: "{entry.evidence}"){flag}')

    _print_header("Tariffs")
    for name in _TARIFF_ORDER:
        outcome = parsed.tariffs.get(name)
        if outcome is None:
            continue
        amount = outcome.result.amount if outcome.computed and outcome.result else None
        print(_format_tariff_line(_TARIFF_LABELS[name], amount, outcome.reason))
        if name == "berthing_services":
            print(f"    note: {BERTHING_SERVICES_NOTE}")

    _print_header("Trace")
    for name in _TARIFF_ORDER:
        outcome = parsed.tariffs.get(name)
        if outcome and outcome.computed and outcome.result:
            _print_trace_steps(outcome.result.trace)

    _print_header("Warnings")
    warnings = [w for outcome in parsed.tariffs.values() if outcome.computed and outcome.result for w in outcome.result.warnings]
    if warnings:
        for w in warnings:
            print(f"  - {w}")
    else:
        print("  (none)")


def render_rejected(rejected: Rejected) -> None:
    # Deliberately just the reason — no stack trace, no other blocks.
    print(rejected.reason)


def render_result(result: ParseResult) -> None:
    if isinstance(result, Rejected):
        render_rejected(result)
    else:
        render_parsed(result)


def render_calculation_result(call: VesselCall, result: CalculationResult) -> None:
    """--json mode's renderer: same shape as render_parsed(), but there is
    no evidence (nothing was extracted from text) and every tariff is
    either computed or not, per the raw engine's own rules — not the
    parser's dependency table."""
    _print_header("Vessel call (from --json — no evidence, nothing was parsed)")
    for field_name in VesselCall.model_fields:
        value = getattr(call, field_name)
        if value in (None, [], False):
            continue
        print(f"  {field_name:35s} = {value!r}")

    _print_header("Tariffs")
    by_name = {
        "light_dues": result.light_dues,
        "port_dues": result.port_dues,
        "towage_dues": result.towage_dues,
        "vts_dues": result.vts_dues,
        "pilotage_dues": result.pilotage_dues,
        "berthing_services": result.berthing_services,
    }
    for name in _TARIFF_ORDER:
        tr = by_name[name]
        print(_format_tariff_line(_TARIFF_LABELS[name], tr.amount, None))
        if name == "berthing_services":
            print(f"    note: {BERTHING_SERVICES_NOTE}")

    _print_header("Trace")
    for tr in by_name.values():
        _print_trace_steps(tr.trace)

    _print_header("Warnings")
    warnings = [w for tr in by_name.values() for w in tr.warnings]
    warnings += list(result.running_of_vessel_lines.warnings)
    if warnings:
        for w in warnings:
            print(f"  - {w}")
    else:
        print("  (none)")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m tariffs.cli",
        description="Parse a free-text vessel port-call request and compute TNPA tariffs.",
    )
    parser.add_argument(
        "request",
        nargs="?",
        help="The free-text vessel request. Required unless --interactive or --json is given.",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Prompt for requests in a loop instead of taking one from the command line.",
    )
    parser.add_argument(
        "--json",
        metavar="FILE",
        help=(
            "Run a pre-built VesselCall (JSON file) through the engine directly, "
            "bypassing the LLM parser entirely. Needs no API key."
        ),
    )
    return parser


def _run_json_mode(path: str) -> None:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    call = VesselCall(**raw)
    result = calculate(call)
    render_calculation_result(call, result)


def _run_single_request(text: str) -> None:
    result = parse_vessel_request(text)
    render_result(result)


def _run_interactive() -> None:
    print("Enter a vessel request (blank line or Ctrl-D to quit).")
    while True:
        try:
            text = input("> ").strip()
        except EOFError:
            print()
            return
        if not text:
            return
        try:
            _run_single_request(text)
        except Exception as exc:  # broken program, not a bad request — see module docstring
            print(f"Error: {exc}", file=sys.stderr)


def main(argv: Optional[list[str]] = None) -> int:
    arg_parser = _build_arg_parser()
    args = arg_parser.parse_args(argv)

    if args.json:
        try:
            _run_json_mode(args.json)
        except Exception as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        return 0

    if args.interactive:
        _run_interactive()
        return 0

    if not args.request:
        arg_parser.print_usage(sys.stderr)
        print("error: a request is required unless --interactive or --json is given", file=sys.stderr)
        return 2

    try:
        _run_single_request(args.request)
    except Exception as exc:  # broken program (API unreachable, a validation error on a
        # field the model DID populate, etc.) — distinct from a Rejected result, and never
        # a raw traceback dumped on the user.
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
