#!/usr/bin/env python3
"""Independent bounded checker for the prospectively frozen P6 ETS V1 study.

The protocol, cases and gold table predate this checker.  This file intentionally
uses only the Python standard library and emits one canonical JSON receipt.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from itertools import product
import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
CASES_PATH = HERE / "ets_cases_v1.jsonl"
GOLD_PATH = HERE / "ets_gold_v1.json"

CASE_TYPES = {
    "clean",
    "evidence_inadmissible",
    "independent_support",
    "stale_epoch",
    "hidden_footprint",
    "authority_obligation_laundering",
}
FAMILIES = {
    "formal-software",
    "agent-memory-tool-state",
    "scientific-evidence-state",
}

DONOR_DECISION_FIELDS = (
    "computational_support",
    "provenance_bound",
    "generic_permission",
    "generic_obligations_clear",
    "footprint_audit_pass",
    "independent_support",
    "preservation_certificate",
)


def load_cases() -> list[dict[str, Any]]:
    cases = [json.loads(line) for line in CASES_PATH.read_text().splitlines() if line.strip()]
    assert len(cases) == 18, len(cases)
    ids = [c["id"] for c in cases]
    assert len(ids) == len(set(ids))
    assert {c["family"] for c in cases} == FAMILIES
    for family in FAMILIES:
        subset = [c for c in cases if c["family"] == family]
        assert len(subset) == 6
        assert {c["case_type"] for c in subset} == CASE_TYPES
    return cases


def load_gold() -> dict[str, str]:
    gold = json.loads(GOLD_PATH.read_text())
    assert set(gold.values()) <= {"ADMISSIBLE", "REOPEN", "DENIED", "CANNOT_CHECK"}
    return gold


def ets_decision(c: dict[str, Any]) -> str:
    # No ID, family or case-type branch is permitted here.
    if not c["footprint_audit_pass"]:
        return "CANNOT_CHECK"
    if not c["provenance_bound"]:
        return "CANNOT_CHECK"
    if not c["computational_support"]:
        return "REOPEN"
    if not c["generic_permission"]:
        return "DENIED"
    if not c["scientific_commit_authority"]:
        return "DENIED"
    if not c["evidence_transport_known"]:
        return "CANNOT_CHECK"
    if not c["evidence_transport_valid"]:
        return "REOPEN"
    if not c["scientific_obligations_clear"]:
        return "REOPEN"
    return "ADMISSIBLE"


def donor_decision(c: dict[str, Any]) -> str:
    # Strong integrated donor product over generic support/policy/provenance/effects.
    # It receives the whole record but intentionally owns only the declared donor
    # semantics; responsibility-scoped scientific discharge is not silently added.
    if not c["footprint_audit_pass"]:
        return "CANNOT_CHECK"
    if not c["provenance_bound"]:
        return "CANNOT_CHECK"
    if not c["computational_support"]:
        return "REOPEN"
    if not c["generic_permission"]:
        return "DENIED"
    if not c["generic_obligations_clear"]:
        return "REOPEN"
    return "ADMISSIBLE"


def audit_no_label_leakage(cases: list[dict[str, Any]]) -> None:
    for c in cases:
        altered = dict(c)
        altered["id"] = "REMINTED-ID"
        altered["family"] = "REMINTED-FAMILY"
        altered["case_type"] = "REMINTED-TYPE"
        assert ets_decision(altered) == ets_decision(c)
        assert donor_decision(altered) == donor_decision(c)


def theorem_t61_factorization() -> dict[str, Any]:
    # Freeze generic transport context as valid and vary the four epistemic factors.
    admissible = []
    for comp, evidence, obligation, authority in product((False, True), repeat=4):
        c = {
            "footprint_audit_pass": True,
            "provenance_bound": True,
            "computational_support": comp,
            "generic_permission": True,
            "scientific_commit_authority": authority,
            "evidence_transport_known": True,
            "evidence_transport_valid": evidence,
            "scientific_obligations_clear": obligation,
        }
        decision = ets_decision(c)
        if decision == "ADMISSIBLE":
            admissible.append((comp, evidence, obligation, authority))
            assert comp and evidence and obligation and authority

    assert admissible == [(True, True, True, True)]

    counterexamples = {}
    names = ("computational_support", "evidence_transport", "scientific_obligation", "scientific_authority")
    for index, name in enumerate(names):
        values = [True, True, True, True]
        values[index] = False
        comp, evidence, obligation, authority = values
        c = {
            "footprint_audit_pass": True,
            "provenance_bound": True,
            "computational_support": comp,
            "generic_permission": True,
            "scientific_commit_authority": authority,
            "evidence_transport_known": True,
            "evidence_transport_valid": evidence,
            "scientific_obligations_clear": obligation,
        }
        result = ets_decision(c)
        assert result != "ADMISSIBLE"
        counterexamples[name] = result

    return {"admissible_assignments": len(admissible), "single_factor_counterexamples": counterexamples}


def local_transition(*, source_epoch: int, target_epoch: int, source_scope: str, target_scope: str,
                     computational_support: bool = True, evidence_transport: bool = True,
                     obligation_clear: bool = True, authority: bool = True) -> dict[str, Any]:
    return {
        "source_epoch": source_epoch,
        "target_epoch": target_epoch,
        "source_scope": source_scope,
        "target_scope": target_scope,
        "computational_support": computational_support,
        "evidence_transport": evidence_transport,
        "obligation_clear": obligation_clear,
        "authority": authority,
    }


def local_admissible(t: dict[str, Any]) -> bool:
    return all((t["computational_support"], t["evidence_transport"], t["obligation_clear"], t["authority"]))


def composed_admissible(a: dict[str, Any], b: dict[str, Any]) -> bool:
    return (
        local_admissible(a)
        and local_admissible(b)
        and a["target_epoch"] == b["source_epoch"]
        and a["target_scope"] == b["source_scope"]
    )


def theorem_t62_composition() -> dict[str, Any]:
    good_a = local_transition(source_epoch=1, target_epoch=2, source_scope="q", target_scope="q")
    good_b = local_transition(source_epoch=2, target_epoch=3, source_scope="q", target_scope="q")
    assert local_admissible(good_a) and local_admissible(good_b)
    assert composed_admissible(good_a, good_b)

    epoch_bad = local_transition(source_epoch=4, target_epoch=5, source_scope="q", target_scope="q")
    scope_bad = local_transition(source_epoch=2, target_epoch=3, source_scope="q-expanded", target_scope="q-expanded")
    obligation_bad = local_transition(
        source_epoch=2, target_epoch=3, source_scope="q", target_scope="q", obligation_clear=False
    )

    assert local_admissible(epoch_bad)
    assert local_admissible(scope_bad)
    assert not composed_admissible(good_a, epoch_bad)
    assert not composed_admissible(good_a, scope_bad)
    assert not local_admissible(obligation_bad)
    assert not composed_admissible(good_a, obligation_bad)

    return {
        "positive_composition": True,
        "counterexamples": ["epoch_mismatch", "scope_mismatch", "open_obligation"],
    }


def theorem_t63_erasure(cases: list[dict[str, Any]], gold: dict[str, str]) -> dict[str, Any]:
    buckets: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for c in cases:
        signature = tuple(c[field] for field in DONOR_DECISION_FIELDS)
        buckets[signature].append(c)

    witnesses = []
    for bucket in buckets.values():
        dispositions = {gold[c["id"]] for c in bucket}
        if len(dispositions) > 1:
            for left in bucket:
                for right in bucket:
                    if left["id"] < right["id"] and gold[left["id"]] != gold[right["id"]]:
                        witnesses.append({
                            "left": left["id"],
                            "right": right["id"],
                            "left_gold": gold[left["id"]],
                            "right_gold": gold[right["id"]],
                        })
    assert witnesses
    return {"witness_count": len(witnesses), "first_witness": witnesses[0]}


def evaluate(cases: list[dict[str, Any]], gold: dict[str, str], decision_fn) -> dict[str, Any]:
    rows = []
    family_correct = Counter()
    family_total = Counter()
    unsafe_false_admissible = 0
    unnecessary_reopen = 0
    laundering_false_admissible = 0

    for c in cases:
        expected = gold[c["id"]]
        predicted = decision_fn(c)
        correct = predicted == expected
        family_total[c["family"]] += 1
        family_correct[c["family"]] += int(correct)
        if predicted == "ADMISSIBLE" and expected != "ADMISSIBLE":
            unsafe_false_admissible += 1
            if c["case_type"] == "authority_obligation_laundering":
                laundering_false_admissible += 1
        if c["case_type"] == "independent_support" and expected == "ADMISSIBLE" and predicted != "ADMISSIBLE":
            unnecessary_reopen += 1
        rows.append({"id": c["id"], "expected": expected, "predicted": predicted, "correct": correct})

    return {
        "accuracy": sum(r["correct"] for r in rows) / len(rows),
        "unsafe_false_admissible": unsafe_false_admissible,
        "unnecessary_reopen": unnecessary_reopen,
        "laundering_false_admissible": laundering_false_admissible,
        "family_accuracy": {f: family_correct[f] / family_total[f] for f in sorted(family_total)},
        "rows": rows,
    }


def canonical_sha(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def main() -> int:
    cases = load_cases()
    gold = load_gold()
    assert set(gold) == {c["id"] for c in cases}
    audit_no_label_leakage(cases)

    t61 = theorem_t61_factorization()
    t62 = theorem_t62_composition()
    t63 = theorem_t63_erasure(cases, gold)
    ets = evaluate(cases, gold, ets_decision)
    donor = evaluate(cases, gold, donor_decision)

    # Frozen primary positive gate: reduce unsafe admission without paying for it by
    # reopening independent-support controls.
    positive = (
        ets["unsafe_false_admissible"] < donor["unsafe_false_admissible"]
        and ets["unnecessary_reopen"] <= donor["unnecessary_reopen"]
        and ets["accuracy"] > donor["accuracy"]
        and ets["unsafe_false_admissible"] == 0
    )

    receipt = {
        "protocol": "P6_ETS_PROTOCOL_V1",
        "case_count": len(cases),
        "case_sha256": hashlib.sha256(CASES_PATH.read_bytes()).hexdigest(),
        "gold_sha256": hashlib.sha256(GOLD_PATH.read_bytes()).hexdigest(),
        "theorems": {"T6.1": t61, "T6.2": t62, "T6.3": t63},
        "ets": ets,
        "donor": donor,
        "positive_gate": positive,
        "terminal": "P6_ETS_BOUNDED_EXECUTABLE_POSITIVE" if positive else "P6_ETS_BOUNDED_GATE_NOT_MET",
    }
    receipt["receipt_sha256"] = canonical_sha(receipt)
    print(json.dumps(receipt, sort_keys=True, indent=2))
    assert positive, receipt
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
