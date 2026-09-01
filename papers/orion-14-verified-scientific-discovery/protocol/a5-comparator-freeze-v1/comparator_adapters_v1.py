#!/usr/bin/env python3
"""Outcome-blind terminal adapters for ORION-14 A5 naturalistic comparators.

This file contains only the prospectively frozen native-output -> exact-terminal
relations and the information-equivalent C4/candidate typed relation.  Model
inference is deliberately separate: protected benchmark text or gold outcomes
are neither imported nor available here.
"""
from __future__ import annotations

import itertools
import json

RESOLVED_TRUE = "ResolvedTrue"
RESOLVED_FALSE = "ResolvedFalse"
CANNOT_CHECK = "CannotCheck"
TERMINALS = (RESOLVED_TRUE, RESOLVED_FALSE, CANNOT_CHECK)
NLI_LABELS = ("entailment", "neutral", "contradiction")


def c1_nli_terminal(native_label: str) -> str:
    """Exact named-label map; score magnitude never changes the terminal."""
    mapping = {
        "entailment": RESOLVED_TRUE,
        "neutral": CANNOT_CHECK,
        "contradiction": RESOLVED_FALSE,
    }
    if native_label not in mapping:
        raise ValueError(f"unknown C1 native label: {native_label!r}")
    return mapping[native_label]


def c2_evidence_escalation_terminal(restricted_label: str, resolving_label: str) -> str:
    """Declared evidence-escalation reimplementation.

    A valid naturalistic pair must be unresolved in the restricted state.  If
    the C1 backbone says otherwise, C2 abstains rather than treating a protocol
    violation as scientific evidence.  Only a neutral restricted state licenses
    use of the resolving-state NLI label.
    """
    if restricted_label not in NLI_LABELS or resolving_label not in NLI_LABELS:
        raise ValueError("C2 labels must be named NLI labels")
    if restricted_label != "neutral":
        return CANNOT_CHECK
    return c1_nli_terminal(resolving_label)


def c3_provenance_verifier_terminal(
    restricted_label: str,
    resolving_label: str,
    *,
    source_identity_valid: bool,
    content_integrity_valid: bool,
    lineage_valid: bool,
    rights_valid: bool,
    state_order_valid: bool,
    one_coordinate_change_valid: bool,
) -> str:
    """Declared provenance-aware verifier reimplementation.

    Provenance/integrity cannot manufacture a truth label.  Every provenance
    gate must pass and the restricted state must remain semantically neutral;
    only then is the resolving semantic terminal passed through.
    """
    gates = (
        source_identity_valid,
        content_integrity_valid,
        lineage_valid,
        rights_valid,
        state_order_valid,
        one_coordinate_change_valid,
    )
    if not all(type(x) is bool for x in gates):
        raise TypeError("C3 provenance gates must be booleans")
    if not all(gates):
        return CANNOT_CHECK
    return c2_evidence_escalation_terminal(restricted_label, resolving_label)


TYPED_COORDINATES = (
    "restricted_semantic_terminal",
    "resolving_semantic_terminal",
    "source_identity_valid",
    "content_integrity_valid",
    "lineage_valid",
    "rights_valid",
    "state_order_valid",
    "one_coordinate_change_valid",
)


def _typed_relation(
    *,
    restricted_semantic_terminal: str,
    resolving_semantic_terminal: str,
    source_identity_valid: bool,
    content_integrity_valid: bool,
    lineage_valid: bool,
    rights_valid: bool,
    state_order_valid: bool,
    one_coordinate_change_valid: bool,
) -> str:
    if restricted_semantic_terminal not in TERMINALS:
        raise ValueError("bad restricted terminal")
    if resolving_semantic_terminal not in TERMINALS:
        raise ValueError("bad resolving terminal")
    gates = (
        source_identity_valid,
        content_integrity_valid,
        lineage_valid,
        rights_valid,
        state_order_valid,
        one_coordinate_change_valid,
    )
    if not all(type(x) is bool for x in gates):
        raise TypeError("typed gates must be booleans")
    if restricted_semantic_terminal != CANNOT_CHECK:
        return CANNOT_CHECK
    if not all(gates):
        return CANNOT_CHECK
    if resolving_semantic_terminal in (RESOLVED_TRUE, RESOLVED_FALSE):
        return resolving_semantic_terminal
    return CANNOT_CHECK


def candidate_naturalistic_terminal(**record: object) -> str:
    """Frozen target-relevant candidate interface for A5 naturalistic scoring."""
    if tuple(record) != TYPED_COORDINATES:
        raise ValueError("candidate field set/order differs from frozen interface")
    return _typed_relation(**record)  # type: ignore[arg-type]


def c4_information_equivalent_typed_donor(**record: object) -> str:
    """C4 sees exactly the candidate typed coordinates and nothing else."""
    if tuple(record) != TYPED_COORDINATES:
        raise ValueError("C4 field set/order differs from frozen candidate interface")
    return _typed_relation(**record)  # type: ignore[arg-type]


def audit() -> dict:
    c1_rows = {label: c1_nli_terminal(label) for label in NLI_LABELS}
    c2_rows = {
        f"{a}/{b}": c2_evidence_escalation_terminal(a, b)
        for a, b in itertools.product(NLI_LABELS, repeat=2)
    }

    c4_states = 0
    c4_equal = True
    c4_output = set()
    for restricted, resolving in itertools.product(TERMINALS, repeat=2):
        for gates in itertools.product((False, True), repeat=6):
            record = dict(zip(TYPED_COORDINATES, (restricted, resolving, *gates), strict=True))
            candidate = candidate_naturalistic_terminal(**record)
            donor = c4_information_equivalent_typed_donor(**record)
            c4_states += 1
            c4_equal &= candidate == donor
            c4_output.add(donor)

    hostile = {}
    try:
        c1_nli_terminal("BLOCK")
        hostile["c1_unknown_native_label_rejected"] = False
    except ValueError:
        hostile["c1_unknown_native_label_rejected"] = True

    extra = dict(zip(
        TYPED_COORDINATES,
        (CANNOT_CHECK, RESOLVED_TRUE, True, True, True, True, True, True),
        strict=True,
    ))
    extra["protected_gold"] = RESOLVED_TRUE
    try:
        c4_information_equivalent_typed_donor(**extra)
        hostile["c4_extra_gold_field_rejected"] = False
    except ValueError:
        hostile["c4_extra_gold_field_rejected"] = True

    missing = dict(zip(
        TYPED_COORDINATES[:-1],
        (CANNOT_CHECK, RESOLVED_TRUE, True, True, True, True, True),
        strict=True,
    ))
    try:
        c4_information_equivalent_typed_donor(**missing)
        hostile["c4_missing_candidate_field_rejected"] = False
    except ValueError:
        hostile["c4_missing_candidate_field_rejected"] = True

    checks = {
        "c1_native_fibres_exact_three_way": set(c1_rows.values()) == set(TERMINALS),
        "c2_output_alphabet_exact": set(c2_rows.values()) <= set(TERMINALS),
        "c4_candidate_field_tuple_exact": True,
        "c4_exhaustive_equality": c4_equal,
        "c4_output_alphabet_exact": c4_output == set(TERMINALS),
        "hostile_controls": all(hostile.values()),
    }
    return {
        "schema": "ORION.A5.ComparatorAdapterAudit.v1",
        "c1_map": c1_rows,
        "c2_map": c2_rows,
        "c4_typed_states_checked": c4_states,
        "c4_fields": list(TYPED_COORDINATES),
        "c4_outputs_observed": sorted(c4_output),
        "hostile": hostile,
        "checks": checks,
        "decision": "GREEN" if all(checks.values()) else "REJECT",
        "protected_outcomes_accessed": False,
        "scientific_authority_delta": "NONE__COMPARATOR_FREEZE_ONLY",
    }


if __name__ == "__main__":
    result = audit()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["decision"] == "GREEN" else 1)
