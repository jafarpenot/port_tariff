"""SPEC.md §10.3: economic sanity checks that catch shifted-cell
transcription errors — a value copied from the wrong row or column
usually breaks one of these two patterns:

- Within a port, band base fees increase across bands.
- Within a port, per_100t increments decrease across bands.

One documented exception is carved out below rather than "corrected" —
see the note in config/tariffs_2024_2025.yaml (towage.ports.saldanha) and
the comment at KNOWN_ANOMALIES.
"""

from tariffs.schedule import load_schedule

SCHEDULE = load_schedule()
TOWAGE_PORTS = list(SCHEDULE.towage.ports.keys())

# Verified against the source PDF via two independent extraction passes
# (plain-text and layout-preserving) — this is what the book actually
# prints, not a transcription error on our side. Saldanha's per_100t rises
# on the final band instead of falling, breaking the usual pattern.
KNOWN_ANOMALIES = {"saldanha"}


def test_towage_base_fees_increase_across_bands():
    for port in TOWAGE_PORTS:
        values = [b.base for b in SCHEDULE.towage.ports[port].bands if b.base is not None]
        assert values == sorted(values), f"{port}: base fees are not non-decreasing across bands: {values}"


def test_towage_per_100t_decreases_across_bands():
    for port in TOWAGE_PORTS:
        values = [b.per_100t for b in SCHEDULE.towage.ports[port].bands if b.per_100t is not None]
        if port in KNOWN_ANOMALIES:
            continue
        assert values == sorted(values, reverse=True), f"{port}: per_100t is not non-increasing across bands: {values}"


def test_saldanha_anomaly_is_still_present_and_unchanged():
    """If this ever fails, the source data changed (or was "corrected")
    and KNOWN_ANOMALIES above should be revisited — not silently widened."""
    values = [b.per_100t for b in SCHEDULE.towage.ports["saldanha"].bands if b.per_100t is not None]
    assert values[-1] > values[-2], (
        "expected Saldanha's documented per_100t anomaly (rising on the final "
        f"band) to still hold; got {values}"
    )
