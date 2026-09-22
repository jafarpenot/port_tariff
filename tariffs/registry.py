"""Schedule registry (specs/EXTRACTION_SPEC.md §5.2): which schedule
file covers a given port, and for what validity period. One entry per
schedule (authority + edition) — a single book can cover many ports.

Deliberately no dependency on tariffs.schedule or tariffs.models: this
module only deals with plain strings and dates, so tariffs.models can
build the Port enum from it (all_registered_ports) without a circular
import — models.py stays the lowest layer that everything else sits on,
this module sits *below* it, not beside it.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import yaml
from pydantic import BaseModel

_REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY_PATH = _REPO_ROOT / "schedules" / "registry.yaml"


class RegistryEntry(BaseModel):
    schedule_file: str
    ports: list[str]
    effective_from: date
    effective_to: date


def load_registry(path: str | Path = DEFAULT_REGISTRY_PATH) -> list[RegistryEntry]:
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or []
    return [RegistryEntry.model_validate(entry) for entry in raw]


def all_registered_ports(path: str | Path = DEFAULT_REGISTRY_PATH) -> list[str]:
    """Every port named by any registry entry, in first-seen order,
    de-duplicated — this is what tariffs.models.Port is built from, so
    a new registry entry with a new port immediately becomes a valid
    `Port` member without editing any Python source."""
    seen: dict[str, None] = {}
    for entry in load_registry(path):
        for port in entry.ports:
            seen.setdefault(port, None)
    return list(seen)


def schedule_path_for(port: str, on_date: date | None = None, path: str | Path = DEFAULT_REGISTRY_PATH) -> Path:
    """Which schedule file covers this port, optionally as of a specific
    date (editions have validity periods). No date given -> match on
    port alone — the most permissive lookup, used when a caller has no
    date to go on (SPEC.md's tri-state "not stated" policy applies to
    VesselCall.arrival too). Raises ValueError with a clear message if
    nothing matches — the hook for "no approved schedule covers this
    port" (specs/EXTRACTION_SPEC.md §5.2), replacing the old fixed
    Port-enum boundary."""
    for entry in load_registry(path):
        if port not in entry.ports:
            continue
        if on_date is not None and not (entry.effective_from <= on_date <= entry.effective_to):
            continue
        return _REPO_ROOT / entry.schedule_file
    if on_date is not None:
        raise ValueError(f"no approved schedule covers port {port!r} on {on_date} — schedules/registry.yaml has no matching entry.")
    raise ValueError(f"no approved schedule covers port {port!r} — schedules/registry.yaml has no matching entry.")
