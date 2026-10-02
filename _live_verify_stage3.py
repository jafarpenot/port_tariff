import sys
import time

from dotenv import load_dotenv

load_dotenv("/tmp/port_tariff_wt/.env")

from extraction.llm import default_llm
from extraction.pipeline import run_pipeline
from tariffs.generic_calculator import compile_report, to_tariff_plan
from tariffs.models import Port, VesselCall
from tariffs.nlp import parse_vessel_request

PDF = "/tmp/port_tariff_wt/Port Tariff.pdf"

t0 = time.time()
llm = default_llm()
report = run_pipeline(PDF, llm, map_concurrency_limit=3)
print(f"[done] pipeline took {time.time() - t0:.0f}s", file=sys.stderr, flush=True)

charges_by_key = {e.charge: e for e in report.charges}
for e in report.charges:
    mods = []
    rule = e.proposed_rule or (next(iter(e.per_port_rules.values()), None) if e.varies_by_port else None)
    if rule:
        mods = [(m.condition, m.required_vessel_field) for m in rule.modifiers]
    print(f"{e.charge.value}: outcome={e.outcome.value} varies_by_port={e.varies_by_port} modifiers={mods}", file=sys.stderr)

compiled = compile_report(charges_by_key, currency=report.identity.currency or "ZAR")
plan = to_tariff_plan(compiled)

REQUEST = (
    "SUDESTADA, a bulk carrier of 51,255 GT, called at Durban. Number of operations: 2."
)
result = parse_vessel_request(REQUEST, tariff_plan=plan)
print("=== REFERENCE CASE (no modifier fields stated) ===", file=sys.stderr)
if hasattr(result, "tariffs"):
    for name, outcome in result.tariffs.items():
        amt = outcome.result.amount if outcome.computed and outcome.result else None
        print(f"{name}: computed={outcome.computed} amount={amt} warnings={outcome.result.warnings if outcome.computed and outcome.result else outcome.reason}", file=sys.stderr)
else:
    print("REJECTED:", result, file=sys.stderr)

report.identity_report_path = None
import json
with open("/tmp/port_tariff_wt/_tnpa_report.json", "w") as f:
    f.write(report.model_dump_json())
print("[saved] /tmp/port_tariff_wt/_tnpa_report.json", file=sys.stderr)
