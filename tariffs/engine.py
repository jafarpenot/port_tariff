"""The single entry point (SPEC.md §1): a function taking a VesselCall and
returning a result object. No CLI, transport, logging-to-stdout or
framework concerns — a FastAPI layer can wrap `calculate()` in v2 without
refactoring anything here.
"""

from __future__ import annotations

from pathlib import Path

from . import calculators as calc
from . import modifiers as mod
from .models import CalculationResult, VesselCall
from .registry import schedule_path_for
from .schedule import TariffSchedule, load_schedule

_schedule_cache: dict[str, TariffSchedule] = {}


def _get_schedule(call: VesselCall, schedule: TariffSchedule | None, schedule_path: str | Path | None) -> TariffSchedule:
    if schedule is not None:
        return schedule
    if schedule_path is not None:
        return load_schedule(schedule_path)
    # Selected by port and arrival date via schedules/registry.yaml
    # (specs/EXTRACTION_SPEC.md §5.2) — not a single fixed default file.
    # No date stated -> match on port alone, same tri-state "not stated"
    # policy SPEC.md §8.2 already applies to every other optional field.
    on_date = call.arrival.date() if call.arrival else None
    path = str(schedule_path_for(call.port.value, on_date))
    if path not in _schedule_cache:
        _schedule_cache[path] = load_schedule(path)
    return _schedule_cache[path]


def calculate(
    call: VesselCall,
    schedule: TariffSchedule | None = None,
    schedule_path: str | Path | None = None,
) -> CalculationResult:
    """Calculate all six tariffs for a VesselCall.

    `schedule` lets a caller (e.g. a test) inject an already-loaded
    TariffSchedule; `schedule_path` lets a caller point at a different YAML
    file. With neither, the schedule is selected via schedules/registry.yaml
    by `call.port` and `call.arrival` (§5.2) and cached per resolved file
    for the life of the process.
    """
    sched = _get_schedule(call, schedule, schedule_path)
    return CalculationResult(
        vessel_call=call,
        light_dues=mod.apply_to_light_dues(calc.light_dues(call, sched), call, sched),
        port_dues=mod.apply_to_port_dues(calc.port_dues(call, sched), call, sched),
        towage_dues=mod.apply_to_towage(calc.towage_dues(call, sched), call, sched),
        vts_dues=mod.apply_to_vts(calc.vts_dues(call, sched), call, sched),
        pilotage_dues=mod.apply_to_pilotage(calc.pilotage_dues(call, sched), call, sched),
        berthing_services=mod.apply_to_berthing(calc.berthing_services(call, sched), call, sched),
        # §3.9: parsed, not calculated — no modifiers apply to an
        # amount that is never computed in v1.
        running_of_vessel_lines=calc.running_of_vessel_lines(call, sched),
    )
