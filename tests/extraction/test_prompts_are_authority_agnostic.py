"""specs/EXTRACTION_SPEC.md §8's cross-cutting constraint, enforced: no
prompt sent to Map, Extract or the identity node may contain a
TNPA-specific fact. If one leaked in, the TNPA accuracy score and the
seeded-error catch rate would measure memorisation, not generalisation
— and the spec itself is full of TNPA examples, so this is the default
failure mode of editing these prompts carelessly, not a hypothetical.

Scans the rendered prompt STRINGS (not the .py source), so a mention in
a docstring or comment — like this one — is not a false positive.
"""

from extraction.prompts import (
    EXTRACT_SYSTEM_PROMPT,
    IDENTITY_SYSTEM_PROMPT,
    MAP_SYSTEM_PROMPT,
    VERIFY_SYSTEM_PROMPT,
    extract_user_prompt,
    identity_user_prompt,
    map_user_prompt,
    verify_user_prompt,
)

# Port names, the authority's own name, the specific sections behind the
# §3.8/§3.9 semantic mismatch, and a sample of reference-case rate/answer
# figures. Not exhaustive by design — a regression guard on the prompts
# that exist today, not a general secrets scanner.
_DENYLIST = [
    "transnet",
    "tnpa",
    "richards bay",
    "durban",
    "east london",
    "ngqura",
    "port elizabeth",
    "mossel bay",
    "cape town",
    "saldanha",
    "§3.8",
    "§3.9",
    "berthing services",  # the book's own section TITLE — "berthing_services" (the canonical key) is exempt
    "running of vessel lines",
    "sudestada",
    "117.08",
    "19,639.50",
    "51,255",
    "51,300",
    "60,062.04",
    "199,549.22",
    "147,074.38",
    "33,315.75",
    "47,189.94",
]

_RENDERED_PROMPTS = {
    "IDENTITY_SYSTEM_PROMPT": IDENTITY_SYSTEM_PROMPT,
    "identity_user_prompt": identity_user_prompt("placeholder opening pages text"),
    "MAP_SYSTEM_PROMPT": MAP_SYSTEM_PROMPT,
    "map_user_prompt": map_user_prompt(1, 5, "placeholder window text"),
    "EXTRACT_SYSTEM_PROMPT": EXTRACT_SYSTEM_PROMPT,
    "extract_user_prompt": extract_user_prompt("light_dues", "placeholder context text"),
    "VERIFY_SYSTEM_PROMPT": VERIFY_SYSTEM_PROMPT,
    "verify_user_prompt": verify_user_prompt("light_dues", "placeholder proposal summary", "placeholder tool findings"),
}


def test_no_prompt_contains_a_tnpa_specific_fact():
    violations = []
    for name, rendered in _RENDERED_PROMPTS.items():
        lowered = rendered.lower()
        for term in _DENYLIST:
            if term.lower() in lowered:
                violations.append(f"{name} contains denylisted term {term!r}")
    assert not violations, "\n".join(violations)


def test_canonical_charge_keys_are_still_present():
    """The denylist must not have collided with the legitimate, generic
    vocabulary every prompt is supposed to carry (§3.1)."""
    for key in ["light_dues", "port_dues", "towage", "vts", "pilotage", "berthing_services"]:
        assert key in MAP_SYSTEM_PROMPT
        assert key in EXTRACT_SYSTEM_PROMPT
        assert key in VERIFY_SYSTEM_PROMPT
