"""The single entry point (SPEC.md §1): a function taking a VesselCall and
returning a result object. No CLI, transport, logging-to-stdout or
framework concerns — a FastAPI layer can wrap `calculate()` in v2 without
refactoring anything here.
"""

from __future__ import annotations

from pathlib import Path

from . import calculators as calc
from .models import CalculationResult, VesselCall
from .schedule import DEFAULT_SCHEDULE_PATH, TariffSchedule, load_schedule

_schedule_cache: TariffSchedule | None = None


def _get_schedule(schedule: TariffSchedule | None, schedule_path: str | Path | None) -> TariffSchedule:
    if schedule is not None:
        return schedule
    if schedule_path is not None:
        return load_schedule(schedule_path)
    global _schedule_cache
    if _schedule_cache is None:
        _schedule_cache = load_schedule(DEFAULT_SCHEDULE_PATH)
    return _schedule_cache


def calculate(
    call: VesselCall,
    schedule: TariffSchedule | None = None,
    schedule_path: str | Path | None = None,
) -> CalculationResult:
    """Calculate all six tariffs for a VesselCall.

    `schedule` lets a caller (e.g. a test) inject an already-loaded
    TariffSchedule; `schedule_path` lets a caller point at a different YAML
    file. With neither, the packaged default config is loaded once and
    cached for the life of the process.
    """
    sched = _get_schedule(schedule, schedule_path)
    return CalculationResult(
        vessel_call=call,
        light_dues=calc.light_dues(call, sched),
        port_dues=calc.port_dues(call, sched),
        towage_dues=calc.towage_dues(call, sched),
        vts_dues=calc.vts_dues(call, sched),
        pilotage_dues=calc.pilotage_dues(call, sched),
        berthing_services=calc.berthing_services(call, sched),
        running_of_vessel_lines=calc.running_of_vessel_lines(call, sched),
    )
