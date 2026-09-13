"""v3: tests for tariffs.cli — rendering and argument handling only.

No real Anthropic API calls: normal-mode tests exercise the rendering
functions directly against hand-built Parsed/Rejected objects (the same
pattern as tests/test_nlp_parser.py's stub LLM, one level up), and
--json mode needs no API key by construction.
"""

from datetime import datetime

import pytest

from tariffs.calculators import light_dues
from tariffs.cli import main, render_parsed, render_rejected
from tariffs.engine import calculate
from tariffs.models import Port, VesselCall
from tariffs.modifiers import apply_to_light_dues
from tariffs.nlp import ExtractionTraceEntry, Parsed, Rejected, TariffOutcome
from tariffs.schedule import load_schedule

SCHEDULE = load_schedule()


def _reference_call() -> VesselCall:
    return VesselCall(
        vessel_name="SUDESTADA",
        port=Port.DURBAN,
        gross_tonnage=51255,
        number_of_operations=2,
        chargeable_period_days=3.396,
    )


def _computed_outcome(call: VesselCall):
    result = apply_to_light_dues(light_dues(call, SCHEDULE), call, SCHEDULE)
    return TariffOutcome(computed=True, result=result)


# ---------------------------------------------------------------------------
# render_parsed / render_rejected
# ---------------------------------------------------------------------------


def test_render_parsed_shows_vessel_call_evidence_tariffs_trace_warnings(capsys):
    call = _reference_call()
    parsed = Parsed(
        call=call,
        evidence=[
            ExtractionTraceEntry(field="port", value="durban", evidence="at Durban"),
            ExtractionTraceEntry(field="gross_tonnage", value=51255.0, evidence="GT 51,255"),
        ],
        tariffs={
            "light_dues": _computed_outcome(call),
            "pilotage_dues": TariffOutcome(computed=False, reason="not computable — missing number_of_operations"),
        },
    )
    render_parsed(parsed)
    out = capsys.readouterr().out

    assert "Parsed vessel call" in out
    assert 'at Durban' in out
    assert "Tariffs" in out
    assert "60,062.04" in out  # light dues, computed
    assert "not computable — missing number_of_operations" in out  # never shown as zero
    assert "Trace" in out
    assert "Warnings" in out
    assert "(none)" in out


def test_render_parsed_never_shows_a_zero_for_not_computable():
    call = _reference_call()
    parsed = Parsed(
        call=call,
        evidence=[],
        tariffs={"towage_dues": TariffOutcome(computed=False, reason="not computable — missing number_of_operations")},
    )
    # Capture via a real run rather than string-search alone: assert there is
    # no numeric amount rendered for the uncomputed tariff.
    import io
    import contextlib

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        render_parsed(parsed)
    out = buf.getvalue()
    assert "0.00 ZAR" not in out
    assert "not computable" in out


def test_render_rejected_prints_reason_only_no_traceback(capsys):
    rejected = Rejected(reason="This tool calculates TNPA port tariffs...", parsed_so_far=[], missing_fields=[])
    render_rejected(rejected)
    out = capsys.readouterr().out
    assert out.strip() == "This tool calculates TNPA port tariffs..."
    assert "Traceback" not in out


# ---------------------------------------------------------------------------
# main() — argument handling and --json mode (no API key needed)
# ---------------------------------------------------------------------------


def test_main_requires_request_unless_flag_given(capsys):
    exit_code = main([])
    err = capsys.readouterr().err
    assert exit_code == 2
    assert "request is required" in err


def test_main_json_mode_reproduces_the_reference_case(capsys, tmp_path):
    json_file = tmp_path / "call.json"
    json_file.write_text(
        """
        {
            "vessel_name": "SUDESTADA",
            "port": "durban",
            "gross_tonnage": 51255,
            "chargeable_period_days": 3.396,
            "number_of_operations": 2
        }
        """
    )
    exit_code = main(["--json", str(json_file)])
    out = capsys.readouterr().out

    assert exit_code == 0
    assert "60,062.04" in out  # light dues
    assert "199,549.22" in out  # port dues
    assert "147,074.38" in out  # towage dues
    assert "33,315.75" in out  # VTS dues
    assert "47,189.94" in out  # pilotage dues
    assert "19,639.50" in out  # berthing services / running of vessel lines dues


def test_main_json_mode_missing_file_prints_clean_error_not_traceback(capsys):
    exit_code = main(["--json", "/definitely/not/a/real/file.json"])
    err = capsys.readouterr().err
    assert exit_code == 1
    assert err.startswith("Error:")
    assert "Traceback" not in err


def test_main_json_mode_invalid_vessel_call_raises_cleanly_not_a_traceback(capsys, tmp_path):
    json_file = tmp_path / "bad.json"
    json_file.write_text('{"port": "durban", "gross_tonnage": -5}')  # violates gt=0
    exit_code = main(["--json", str(json_file)])
    err = capsys.readouterr().err
    assert exit_code == 1
    assert err.startswith("Error:")
    assert "Traceback" not in err
