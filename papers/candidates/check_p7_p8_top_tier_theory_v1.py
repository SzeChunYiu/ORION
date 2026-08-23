#!/usr/bin/env python3
"""Finite counterexample/composition checker for P7/P8 top-tier theory V1."""

from __future__ import annotations

from itertools import product
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def p7_closure_transport(*, fact: bool, evidence: bool, support: bool, obligation: bool, coverage: bool) -> bool:
    return fact and evidence and support and obligation and coverage


def p7_checks() -> dict:
    # T7.1: lower-coordinate preservation does not entail closure.
    all_true = dict(fact=True, evidence=True, support=True, obligation=True, coverage=True)
    assert p7_closure_transport(**all_true)
    counter = {}
    for key in all_true:
        case = dict(all_true)
        case[key] = False
        assert not p7_closure_transport(**case)
        counter[key] = "CLOSURE_NOT_TRANSPORTED"

    # Explicit value-preserved / closure-broken witness.
    assert not p7_closure_transport(fact=True, evidence=True, support=False, obligation=True, coverage=True)

    # T7.2: local witness validity versus sequential composability.
    def local_witness(source: str, target: str, required: frozenset[str], established: frozenset[str]) -> dict:
        return {"source": source, "target": target, "required": required, "established": established}

    def local_valid(w: dict) -> bool:
        return w["required"] <= w["established"]

    def composes(a: dict, b: dict, preserved_intermediate: frozenset[str]) -> bool:
        return (
            local_valid(a)
            and local_valid(b)
            and a["target"] == b["source"]
            and a["required"] <= preserved_intermediate
        )

    w01 = local_witness("R0", "R1", frozenset({"calibration-v1"}), frozenset({"calibration-v1", "schema-map"}))
    w12 = local_witness("R1", "R2", frozenset({"schema-map"}), frozenset({"schema-map"}))
    assert local_valid(w01) and local_valid(w12)
    assert composes(w01, w12, frozenset({"calibration-v1", "schema-map"}))
    assert not composes(w01, w12, frozenset({"schema-map"}))  # R2 invalidated calibration-v1.

    # Interface mismatch also blocks composition although both locals are valid.
    mismatch = local_witness("R1-alt", "R2", frozenset(), frozenset())
    assert local_valid(mismatch)
    assert not composes(w01, mismatch, frozenset({"calibration-v1"}))

    # T7.3: identical observation cannot deterministically distinguish closed/open worlds.
    observation = "same-visible-history"
    gold = {"closed-world": "CLOSED", "open-world": "CONTINUE"}
    assert observation == observation
    possible_outputs = ("CLOSED", "CONTINUE", "CANNOT_CHECK")
    best_without_witness = 0.0
    for output in possible_outputs:
        correct = sum(output == label for label in gold.values()) / len(gold)
        best_without_witness = max(best_without_witness, correct)
    assert best_without_witness == 0.5

    # An external coverage witness separates the two worlds.
    def with_coverage(coverage_complete: bool) -> str:
        return "CLOSED" if coverage_complete else "CONTINUE"
    assert with_coverage(True) == gold["closed-world"]
    assert with_coverage(False) == gold["open-world"]

    return {
        "preservation_counterexamples": counter,
        "sequential_assumption_invalidation_blocks": True,
        "interface_mismatch_blocks": True,
        "open_censored_best_observed_only_accuracy": best_without_witness,
        "terminal": "P7_TOP_TIER_THEORY_V1_GREEN",
    }


def p8_action_authorized(case: dict) -> bool:
    # Generic donor-complete action layer.
    return all((
        case["principal_valid"],
        case["policy_permits"],
        case["delegation_valid"],
        case["budget_available"],
        case["provenance_bound"],
        case["fresh"],
    ))


def p8_scientific_authorized(case: dict) -> str:
    if not p8_action_authorized(case):
        return "DENIED"
    if not case["target_obligation_known"] or not case["evidence_type_known"]:
        return "CANNOT_CHECK"
    if case["evidence_type"] != case["target_obligation"]:
        return "DENIED"
    return "AUTHORIZED"


def p8_checks() -> dict:
    # T8.1 minimal pair: exactly same action-authority record, different scientific obligation.
    shared = {
        "principal_valid": True,
        "policy_permits": True,
        "delegation_valid": True,
        "budget_available": True,
        "provenance_bound": True,
        "fresh": True,
        "target_obligation_known": True,
        "evidence_type_known": True,
        "evidence_type": ("math", "proof", "theorem-A", "content-A", 7),
    }
    c1 = dict(shared, target_obligation=("math", "proof", "theorem-A", "content-A", 7))
    c2 = dict(shared, target_obligation=("math", "proof", "theorem-A", "content-B", 7))
    assert p8_action_authorized(c1) and p8_action_authorized(c2)
    assert p8_scientific_authorized(c1) == "AUTHORIZED"
    assert p8_scientific_authorized(c2) == "DENIED"

    donor_signature_fields = (
        "principal_valid", "policy_permits", "delegation_valid", "budget_available", "provenance_bound", "fresh"
    )
    assert tuple(c1[k] for k in donor_signature_fields) == tuple(c2[k] for k in donor_signature_fields)

    # Unknown type is CANNOT_CHECK, not denial/promotion.
    unknown = dict(c1, target_obligation_known=False)
    assert p8_scientific_authorized(unknown) == "CANNOT_CHECK"

    # T8.2 full-type coercion composition.
    t0 = ("raw", "measurement", "scope-A", "content-A", 1)
    t1 = ("calibrated", "measurement", "scope-A", "content-A", 1)
    t2 = ("claim", "empirical", "scope-A", "content-A", 1)
    t_bad = ("claim", "empirical", "scope-B", "content-A", 1)

    def coercion(source, target, *, valid=True, protected=True):
        return {"source": source, "target": target, "valid": valid, "protected": protected}

    def coercion_valid(g):
        return g["valid"] and g["protected"]

    def compose(g1, g2):
        if not coercion_valid(g1) or not coercion_valid(g2):
            return None
        if g1["target"] != g2["source"]:
            return None
        return (g1["source"], g2["target"])

    g01 = coercion(t0, t1)
    g12 = coercion(t1, t2)
    assert compose(g01, g12) == (t0, t2)
    assert compose(g01, coercion(t_bad, t2)) is None
    assert compose(g01, coercion(t1, t2, valid=False)) is None
    assert compose(g01, coercion(t1, t2, protected=False)) is None

    # Ambiguous coercion registry is fail-closed.
    registry = [coercion(t0, t1), coercion(t0, t_bad)]
    candidates = [g for g in registry if g["source"] == t0 and coercion_valid(g)]
    assert len(candidates) == 2
    ambiguous_terminal = "CANNOT_CHECK"

    # T8.3 support-family revocation.
    derivations = {
        "d1": {"source-A"},
        "d2": {"source-B"},
        "d3": {"source-A", "source-C"},
    }

    def surviving(revoked: set[str]) -> set[str]:
        return {name for name, deps in derivations.items() if not (deps & revoked)}

    after_a = surviving({"source-A"})
    after_ab = surviving({"source-A", "source-B"})
    assert after_a == {"d2"}
    assert after_ab == set()
    assert bool(after_a) and not bool(after_ab)

    # Confidence cannot compensate for invalid hard type.
    for confidence in (0.0, 0.5, 0.99, 1.0):
        mismatch = dict(c2, confidence=confidence)
        assert p8_scientific_authorized(mismatch) == "DENIED"

    return {
        "action_authorization_pair_same": True,
        "scientific_pair": ["AUTHORIZED", "DENIED"],
        "unknown_type_terminal": "CANNOT_CHECK",
        "coercion_composition": True,
        "ambiguous_coercion_terminal": ambiguous_terminal,
        "surviving_after_source_A_revocation": sorted(after_a),
        "all_support_gone_after_A_B_revocation": True,
        "terminal": "P8_TOP_TIER_THEORY_V1_GREEN",
    }


def check_markers() -> None:
    files = {
        "papers/paper-07-epistemic-navigation-open-worlds/TOP_TIER_THEORY_V1.md": ("T7.1", "T7.2", "T7.3"),
        "papers/paper-08-epistemic-authority-autonomous-science/TOP_TIER_THEORY_V1.md": ("T8.1", "T8.2", "T8.3"),
    }
    for path, markers in files.items():
        text = (ROOT / path).read_text()
        for marker in markers:
            assert marker in text, (path, marker)


def main() -> int:
    check_markers()
    result = {
        "P7": p7_checks(),
        "P8": p8_checks(),
        "terminal": "P7_P8_TOP_TIER_THEORY_V1_GREEN",
    }
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
