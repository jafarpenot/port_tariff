"""Assignment output-name adapter (SPEC.md §7.6, §4).

A thin naming layer over config/assignment_mapping.yaml. It maps the
assignment's output slot names onto domain CalculationResult attributes.
It never suppresses a domain calculator: §3.9 Running of Vessel Lines is
always surfaced too, warnings intact, alongside the mapped slots.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .models import CalculationResult

_REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MAPPING_PATH = _REPO_ROOT / "config" / "assignment_mapping.yaml"


def load_mapping(path: str | Path = DEFAULT_MAPPING_PATH) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return raw["assignment_outputs"]


def to_assignment_output(
    result: CalculationResult,
    mapping: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Render a CalculationResult into the assignment's output slot names."""
    mapping = mapping if mapping is not None else load_mapping()

    output: dict[str, Any] = {}
    for slot_name, spec in mapping.items():
        tariff_result = getattr(result, spec["calculator"])
        entry: dict[str, Any] = {
            "amount": tariff_result.amount,
            "currency": tariff_result.currency,
            "warnings": list(tariff_result.warnings),
        }
        if "note" in spec:
            entry["note"] = spec["note"].strip()
        output[slot_name] = entry

    # §7.6: the adapter must never suppress §3.9 — surface it directly too,
    # under its own name, even though no assignment slot maps to it.
    output["running_of_vessel_lines_section_3_9_not_calculated"] = {
        "amount": result.running_of_vessel_lines.amount,
        "currency": result.running_of_vessel_lines.currency,
        "warnings": list(result.running_of_vessel_lines.warnings),
    }
    return output
