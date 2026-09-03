#!/usr/bin/env python3
"""Frozen A3 candidate policy: three-valued premise-support transport (v1).

Exact executable identity frozen by A3_CANDIDATE_POLICY_FREEZE_V1.json before
any protected prediction or gold. The policy is the transport law of
ORION23.EXTERNAL_RESPONSIBILITY_TRANSPORT.v1 applied to a WorkflowHub frozen
version pair, with no free parameters and nothing resolved at run time.

Premise universe P(c): every normalized member-manifest entry of the BEFORE
RO-Crate of the cluster's frozen version pair -- the certificate's issuance
state. Members present only in the AFTER crate are not premises of the
certificate (Theorem P1 speaks only over P(c)) and do not enter the decision.

Status assignment is mechanical and total over P(c):
- UNCHANGED    member path present in AFTER with an identical normalized entry
- CONTRADICTED member path present in AFTER with a differing normalized entry
- UNKNOWN      member path absent from the AFTER crate
ENTAILED is never assigned by extractor v1: no mechanical entailment receipt
exists in the frozen substrate, so the extractor is strictly conservative.

Decision (the transport law's three-valued rule; the law's REVOKE is spelled
REOPEN in the A3 terminal alphabet frozen by EXECUTION_AND_ANALYSIS_FREEZE_V1):
- any CONTRADICTED premise -> REOPEN
- else any UNKNOWN premise   -> CANNOT_CHECK
- else                       -> REUSE
"""
from __future__ import annotations

import json
from typing import Any

REUSE = "REUSE"
REOPEN = "REOPEN"
CANNOT_CHECK = "CANNOT_CHECK"
TERMINALS = (REUSE, REOPEN, CANNOT_CHECK)
STATUSES = ("UNCHANGED", "ENTAILED", "CONTRADICTED", "UNKNOWN")

VISIBLE_SCHEMA = "ORION.A3.CandidateVisibleMemberManifests.v1"
ENTRY_FIELDS = ("path", "bytes", "sha256", "kind", "executable")
FORBIDDEN_VISIBLE_FIELDS = (
    "gold", "reuse_gold", "adjudicated_target", "reuse_reopen_target",
    "candidate_prediction", "baseline_prediction", "outcome", "protected_outcome",
)
POLICY_ID = "A3_TRANSPORT_THREE_VALUED_V1"


def _entry_is_wellformed(entry: Any) -> bool:
    if not isinstance(entry, dict) or set(entry) != set(ENTRY_FIELDS):
        return False
    if not isinstance(entry["path"], str) or not entry["path"]:
        return False
    if type(entry["bytes"]) is not int or entry["bytes"] < 0:
        return False
    if not isinstance(entry["sha256"], str) or len(entry["sha256"]) != 64:
        return False
    if not isinstance(entry["kind"], str) or not entry["kind"]:
        return False
    if type(entry["executable"]) is not bool:
        return False
    return True


def normalized_member_map(manifest: Any) -> dict[str, dict[str, Any]]:
    """Map member path -> normalized entry, rejecting malformed manifests."""
    if not isinstance(manifest, list):
        raise ValueError("member manifest must be a list of normalized entries")
    out: dict[str, dict[str, Any]] = {}
    for entry in manifest:
        if not _entry_is_wellformed(entry):
            raise ValueError(f"member entry is not a frozen normalized entry: {entry!r}")
        path = entry["path"]
        if path in out:
            raise ValueError(f"duplicate member path: {path}")
        out[path] = entry
    return out


def premise_status(before_entry: dict[str, Any], after_map: dict[str, dict[str, Any]]) -> str:
    after_entry = after_map.get(before_entry["path"])
    if after_entry is None:
        return "UNKNOWN"
    for field in ENTRY_FIELDS:
        if field == "path":
            continue
        if before_entry[field] != after_entry[field]:
            return "CONTRADICTED"
    return "UNCHANGED"


def premise_statuses(
    before_manifest: list[dict[str, Any]], after_manifest: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """One status per premise of P(c), deterministically ordered by path."""
    after_map = normalized_member_map(after_manifest)
    before_map = normalized_member_map(before_manifest)
    return [
        {"path": path, "status": premise_status(before_map[path], after_map)}
        for path in sorted(before_map)
    ]


def decide(statuses: list[dict[str, Any]]) -> str:
    values = [row["status"] for row in statuses]
    if "CONTRADICTED" in values:
        return REOPEN
    if "UNKNOWN" in values:
        return CANNOT_CHECK
    return REUSE


def evaluate(visible_record: dict[str, Any]) -> dict[str, Any]:
    """Map one candidate-visible record to the frozen prediction.

    The visible record carries only the two normalized member manifests of the
    frozen version pair. Any gold- or prediction-bearing field is rejected.
    """
    bad = set(FORBIDDEN_VISIBLE_FIELDS) & set(visible_record)
    if bad:
        raise ValueError(f"candidate-visible record carries forbidden fields: {sorted(bad)}")
    if visible_record.get("schema") != VISIBLE_SCHEMA:
        raise ValueError("visible record schema mismatch")
    for key in ("workflow_id", "version_before", "version_after"):
        if key not in visible_record:
            raise ValueError(f"visible record missing {key}")
    premises = premise_statuses(visible_record["before_manifest"], visible_record["after_manifest"])
    counts = {status: 0 for status in STATUSES}
    for row in premises:
        counts[row["status"]] += 1
    return {
        "policy_id": POLICY_ID,
        "workflow_id": visible_record["workflow_id"],
        "premises": premises,
        "premise_status_counts": counts,
        "decision": decide(premises),
    }


def _permuted(manifest: list[dict[str, Any]], shift: int) -> list[dict[str, Any]]:
    n = len(manifest)
    return [manifest[(i + shift) % n] for i in range(n)] if n else list(manifest)


def self_test() -> dict[str, Any]:
    entry_a = {"path": "ro-crate-metadata.json", "bytes": 2, "sha256": "a" * 64, "kind": "regular", "executable": False}
    entry_b = {"path": "workflow.cwl", "bytes": 18, "sha256": "b" * 64, "kind": "regular", "executable": False}
    entry_c = {"path": "tools/trim.py", "bytes": 100, "sha256": "c" * 64, "kind": "regular", "executable": True}

    def visible(before: list[dict[str, Any]], after: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "schema": VISIBLE_SCHEMA,
            "workflow_id": "self-test",
            "version_before": 1,
            "version_after": 2,
            "before_manifest": before,
            "after_manifest": after,
        }

    all_unchanged = evaluate(visible([entry_a, entry_b], [dict(entry_a), dict(entry_b)]))
    assert all_unchanged["decision"] == REUSE, all_unchanged
    assert all_unchanged["premise_status_counts"] == {"UNCHANGED": 2, "ENTAILED": 0, "CONTRADICTED": 0, "UNKNOWN": 0}

    changed_b = dict(entry_b, sha256="d" * 64, bytes=19)
    one_contradicted = evaluate(visible([entry_a, entry_b, entry_c], [dict(entry_a), changed_b, dict(entry_c)]))
    assert one_contradicted["decision"] == REOPEN, one_contradicted

    removed_c = evaluate(visible([entry_a, entry_b, entry_c], [dict(entry_a), dict(entry_b)]))
    assert removed_c["decision"] == CANNOT_CHECK, removed_c

    added_after = dict(entry_c, path="tools/new.py")
    addition_only = evaluate(visible([entry_a, entry_b], [dict(entry_a), dict(entry_b), added_after]))
    assert addition_only["decision"] == REUSE, addition_only

    executable_flip = dict(entry_c, executable=False)
    mode_change = evaluate(visible([entry_c], [executable_flip]))
    assert mode_change["decision"] == REOPEN, mode_change

    # Determinism and manifest-order invariance.
    first = evaluate(visible([entry_a, entry_b, entry_c], [changed_b, dict(entry_a), dict(entry_c)]))
    second = evaluate(visible(_permuted([entry_a, entry_b, entry_c], 1), _permuted([changed_b, dict(entry_a), dict(entry_c)], 2)))
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)

    # Gold-bearing visible records are rejected.
    for field in ("gold", "adjudicated_target", "candidate_prediction"):
        poisoned = visible([entry_a], [dict(entry_a)])
        poisoned[field] = "REOPEN"
        try:
            evaluate(poisoned)
        except ValueError as exc:
            assert "forbidden" in str(exc)
        else:
            raise AssertionError(f"gold-bearing visible record accepted: {field}")

    # Malformed manifests are rejected.
    for bad_manifest in (["not-an-entry"], [{"path": "x"}], [dict(entry_a, path="dup"), dict(entry_b, path="dup")]):
        try:
            premise_statuses(bad_manifest, [dict(entry_a)])
        except ValueError:
            pass
        else:
            raise AssertionError(f"malformed manifest accepted: {bad_manifest!r}")

    # Transport-law exhaustive conformance at the decision layer.
    import itertools
    for k in (1, 2, 3):
        for combo in itertools.product(STATUSES, repeat=k):
            statuses = [{"path": f"p{i}", "status": s} for i, s in enumerate(combo)]
            expected = "REOPEN" if "CONTRADICTED" in combo else ("CANNOT_CHECK" if "UNKNOWN" in combo else REUSE)
            assert decide(statuses) == expected, combo

    return {
        "decision": "GREEN",
        "policy_id": POLICY_ID,
        "free_parameters": [],
        "terminals": list(TERMINALS),
        "all_unchanged_reuses": True,
        "contradicted_reopens": True,
        "removed_premise_cannot_checks": True,
        "after_only_member_ignored": True,
        "deterministic_and_order_invariant": True,
        "gold_fields_rejected": True,
        "malformed_manifests_rejected": True,
        "transport_law_decision_conformance": True,
    }


if __name__ == "__main__":
    print(json.dumps(self_test(), indent=2, sort_keys=True))
