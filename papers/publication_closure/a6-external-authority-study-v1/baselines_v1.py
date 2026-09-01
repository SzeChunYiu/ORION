#!/usr/bin/env python3
"""Typed A6 donor baselines for the external authority/discharge study.

Coordinates are three-valued PASS / FAIL / UNKNOWN and are assumed to be visible
before scientific gold. The information-equivalent donor and candidate relation
are intentionally extensionally identical; any later implementation mismatch is
an invalid comparison, not a performance opportunity.
"""
from __future__ import annotations

import json
from typing import Any

PASS = "PASS"
FAIL = "FAIL"
UNKNOWN = "UNKNOWN"
STATES = (PASS, FAIL, UNKNOWN)
ADMIT = "ADMIT"
DENY = "DENY"
CANNOT_CHECK = "CANNOT_CHECK"
TERMINALS = (ADMIT, DENY, CANNOT_CHECK)

COORDS = (
    "authorization",
    "provenance",
    "verification",
    "scientific_discharge",
)


def _state(record: dict[str, Any], key: str) -> str:
    value = record.get(key)
    if value not in STATES:
        raise ValueError(f"{key} must be PASS/FAIL/UNKNOWN")
    return value


def one_coordinate(record: dict[str, Any], key: str) -> str:
    value = _state(record, key)
    if value == PASS:
        return ADMIT
    if value == FAIL:
        return DENY
    return CANNOT_CHECK


def authorization_only(record: dict[str, Any]) -> str:
    return one_coordinate(record, "authorization")


def provenance_only(record: dict[str, Any]) -> str:
    return one_coordinate(record, "provenance")


def verification_only(record: dict[str, Any]) -> str:
    return one_coordinate(record, "verification")


def strongest_combined_incomplete(record: dict[str, Any]) -> str:
    values = [_state(record, key) for key in ("authorization", "provenance", "verification")]
    if FAIL in values:
        return DENY
    if all(v == PASS for v in values):
        return ADMIT
    return CANNOT_CHECK


def typed_full_relation(record: dict[str, Any]) -> str:
    if set(record) != set(COORDS):
        raise ValueError("typed full relation requires exactly the four target-relevant coordinates")
    values = [_state(record, key) for key in COORDS]
    if FAIL in values:
        return DENY
    if all(v == PASS for v in values):
        return ADMIT
    return CANNOT_CHECK


def merged_candidate(record: dict[str, Any]) -> str:
    return typed_full_relation(record)


def information_equivalent_typed_donor(record: dict[str, Any]) -> str:
    return typed_full_relation(record)


BASELINES = {
    "AUTHORIZATION_ONLY": authorization_only,
    "PROVENANCE_ONLY": provenance_only,
    "VERIFICATION_ONLY": verification_only,
    "STRONGEST_COMBINED_DONOR_WITHOUT_SCIENTIFIC_DISCHARGE": strongest_combined_incomplete,
    "MERGED_CANDIDATE": merged_candidate,
    "INFORMATION_EQUIVALENT_TYPED_DONOR": information_equivalent_typed_donor,
}


def evaluate(record: dict[str, Any]) -> dict[str, str]:
    return {name: fn(record) for name, fn in BASELINES.items()}


def exhaustive_tie_audit() -> dict[str, Any]:
    import itertools
    rows = 0
    outputs = set()
    for vals in itertools.product(STATES, repeat=len(COORDS)):
        record = dict(zip(COORDS, vals, strict=True))
        cand = merged_candidate(record)
        ideal = information_equivalent_typed_donor(record)
        assert cand == ideal
        outputs.add(cand)
        rows += 1
    return {"typed_states": rows, "candidate_ideal_exact_tie": True, "output_alphabet": sorted(outputs)}


def self_test() -> dict[str, Any]:
    audit = exhaustive_tie_audit()
    assert audit["typed_states"] == 81
    assert set(audit["output_alphabet"]) == set(TERMINALS)
    all_pass = {k: PASS for k in COORDS}
    assert evaluate(all_pass)["MERGED_CANDIDATE"] == ADMIT
    unknown_science = dict(all_pass, scientific_discharge=UNKNOWN)
    out = evaluate(unknown_science)
    assert out["STRONGEST_COMBINED_DONOR_WITHOUT_SCIENTIFIC_DISCHARGE"] == ADMIT
    assert out["MERGED_CANDIDATE"] == CANNOT_CHECK
    failed_prov = dict(all_pass, provenance=FAIL)
    assert evaluate(failed_prov)["MERGED_CANDIDATE"] == DENY
    extra = dict(all_pass, protected_gold=ADMIT)
    try:
        merged_candidate(extra)
    except ValueError as exc:
        assert "exactly" in str(exc)
    else:
        raise AssertionError("extra protected field was accepted")
    return {"decision": "GREEN", "audit": audit, "protected_gold_consumed": False}


if __name__ == "__main__":
    print(json.dumps(self_test(), indent=2, sort_keys=True))
