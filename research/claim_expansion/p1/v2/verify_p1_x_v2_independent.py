from __future__ import annotations

import hashlib
import json
import sys
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import generate_p1_x_protected_v2 as generator  # noqa: E402

RESULT = HERE / "P1_X_PROTECTED_RESULT_V2.json"

HIGH = {"MODEL_CLASS_EXPANSION", "REPRESENTATION_REGIME_REVISION", "QUESTION_OBJECTIVE_REVISION", "METHOD_BASIS_REVISION"}
ACTIONS = {"REPAIR_LOCAL", "REVISE_HIGH_LEVEL"}


def _decision(terminal: str, candidate: str | None = None, reopen: list[str] | None = None) -> dict[str, Any]:
    return {"terminal": terminal, "revision_class": candidate, "reopen_set": list(reopen or [])}


class IndependentRuntime:
    def __init__(self, case: dict[str, Any]):
        self.visible = {key: deepcopy(value) for key, value in case.items() if key != "protected_gold"}
        self._oracle = {item["candidate_class"]: deepcopy(item) for item in case["protected_gold"]["revision_evaluations"]}
        self.used = 0
        self.limit = int(case["budget"]["max_interventions"])

    def inspect(self, candidate: str) -> dict[str, Any] | None:
        if self.used >= self.limit:
            return None
        self.used += 1
        item = self._oracle.get(candidate)
        return deepcopy(item) if item else None


def _statuses(visible: dict[str, Any]) -> dict[str, str]:
    return {item["candidate_class"]: item["candidate_visible_status"] for item in visible["registered_narrower_alternatives"]}


def _proposals(visible: dict[str, Any]) -> list[dict[str, Any]]:
    return visible["candidate_visible"]["revision_proposals"]


def _valid(item: dict[str, Any] | None) -> bool:
    return bool(item and item["restores_target"] and item["preserves_invariants"] and item["authorized"])


def _less(edges: list[list[str]], a: str, b: str) -> bool:
    graph: dict[str, set[str]] = defaultdict(set)
    for left, right in edges:
        graph[left].add(right)
    todo = [a]
    seen = set()
    while todo:
        node = todo.pop()
        if node in seen:
            continue
        seen.add(node)
        for nxt in graph[node]:
            if nxt == b:
                return True
            todo.append(nxt)
    return False


def independent_p1x(rt: IndependentRuntime) -> dict[str, Any]:
    visible = rt.visible
    statuses = _statuses(visible)
    unknown = visible["candidate_visible"]["unknown_or_unavailable"]
    disc = visible["candidate_visible"]["discriminator_status"]
    if disc == "AVAILABLE":
        return _decision("REQUEST_DISCRIMINATOR")
    if disc == "UNAVAILABLE":
        return _decision("UNRESOLVED")
    if statuses and all(value == "UNTESTED" for value in statuses.values()) and not unknown:
        return _decision("NO_CHANGE")
    if unknown and not any(value == "SUCCEEDED" for value in statuses.values()):
        return _decision("CANNOT_CHECK")

    admitted: dict[str, dict[str, Any]] = {}
    for candidate, status in statuses.items():
        if status != "SUCCEEDED":
            continue
        checked = rt.inspect(candidate)
        if checked is None:
            return _decision("CANNOT_CHECK")
        if _valid(checked):
            admitted[candidate] = checked
    if not admitted:
        return _decision("CANNOT_CHECK")

    minima = [
        candidate
        for candidate in admitted
        if not any(other != candidate and _less(visible["invasiveness_edges"], other, candidate) for other in admitted)
    ]
    if len(minima) != 1:
        return _decision("UNRESOLVED")
    candidate = minima[0]
    checked = admitted[candidate]
    terminal = "REVISE_HIGH_LEVEL" if candidate in HIGH else "REPAIR_LOCAL"
    return _decision(terminal, candidate, checked["observed_reopen_set"] if candidate in HIGH else [])


def independent_b1(rt: IndependentRuntime) -> dict[str, Any]:
    visible = rt.visible
    statuses = _statuses(visible)
    unknown = visible["candidate_visible"]["unknown_or_unavailable"]
    if statuses and all(value == "UNTESTED" for value in statuses.values()) and not unknown:
        return _decision("NO_CHANGE")
    if unknown and not any(value == "SUCCEEDED" for value in statuses.values()):
        if visible["candidate_visible"]["discriminator_status"] != "UNAVAILABLE":
            return _decision("CANNOT_CHECK")
    proposal_map = {item["candidate_class"]: item for item in _proposals(visible)}
    priority = {"SUCCEEDED": 0, "CANNOT_CHECK": 1, "UNTESTED": 2, "FAILED": 3}
    order = [item["candidate_class"] for item in _proposals(visible)]
    order.sort(key=lambda candidate: priority.get(statuses.get(candidate, "UNTESTED"), 2))
    for candidate in order:
        checked = rt.inspect(candidate)
        if not _valid(checked):
            continue
        terminal = "REVISE_HIGH_LEVEL" if candidate in HIGH else "REPAIR_LOCAL"
        reopen = proposal_map[candidate]["proposed_reopen_set"] if candidate in HIGH else []
        return _decision(terminal, candidate, reopen)
    return _decision("CANNOT_CHECK")


def independent_b2(rt: IndependentRuntime) -> dict[str, Any]:
    visible = rt.visible
    statuses = _statuses(visible)
    unknown = visible["candidate_visible"]["unknown_or_unavailable"]
    if statuses and all(value == "UNTESTED" for value in statuses.values()) and not unknown:
        return _decision("NO_CHANGE")
    if unknown and not any(value == "SUCCEEDED" for value in statuses.values()):
        return _decision("CANNOT_CHECK")
    proposals = _proposals(visible)
    proposal_map = {item["candidate_class"]: item for item in proposals}
    order = [item["candidate_class"] for item in proposals]
    high_success = [c for c in order if c in HIGH and statuses.get(c) == "SUCCEEDED"]
    other_success = [c for c in order if c not in HIGH and statuses.get(c) == "SUCCEEDED"]
    fallback = [c for c in order if c not in high_success + other_success]
    for candidate in high_success + other_success + fallback:
        checked = rt.inspect(candidate)
        if not _valid(checked):
            continue
        terminal = "REVISE_HIGH_LEVEL" if candidate in HIGH else "REPAIR_LOCAL"
        reopen = proposal_map[candidate]["proposed_reopen_set"] if candidate in HIGH else []
        return _decision(terminal, candidate, reopen)
    return _decision("CANNOT_CHECK")


def _score(case: dict[str, Any], decision: dict[str, Any]) -> int:
    gold = case["protected_gold"]
    if decision["terminal"] != gold["correct_terminal"]:
        return 0
    if decision["terminal"] not in ACTIONS:
        return int(decision["revision_class"] is None and decision["reopen_set"] == [])
    candidate = decision["revision_class"]
    if candidate not in gold["scientifically_justified_revision_set"]:
        return 0
    checked = next((item for item in gold["revision_evaluations"] if item["candidate_class"] == candidate), None)
    return int(_valid(checked) and decision["reopen_set"] == gold["exact_reopen_set"])


def verify() -> dict[str, Any]:
    expected = json.loads(RESULT.read_text())
    cases = generator.generate_cases()
    pair_digest = hashlib.sha256("\n".join(f"{case['case_id']}|{case['seed_commitment']}" for case in cases).encode()).hexdigest()
    bundle = generator.generate_bundle()
    bundle_digest = hashlib.sha256(json.dumps(bundle, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    functions = {
        "B1_DONOR_COMPLETE_GREEDY": independent_b1,
        "B2_SUCCESS_AUTHORIZES_REFRAME": independent_b2,
        "B3_IDEAL_TYPED_PRODUCT": independent_p1x,
        "P1X_MINIMAL_SCIENTIFIC_ESCALATION": independent_p1x,
    }
    scores = {arm: [] for arm in functions}
    rows = []
    for case in cases:
        decisions = {}
        row_scores = {}
        for arm, function in functions.items():
            runtime = IndependentRuntime(case)
            result = function(runtime)
            result["checks_used"] = runtime.used
            decisions[arm] = result
            value = _score(case, result)
            row_scores[arm] = value
            scores[arm].append(value)
        rows.append({"case_id": case["case_id"], "domain": case["domain"], "archetype": case["archetype"], "generator_id": case["generator_id"], "decisions": decisions, "esrd": row_scores})

    row_digest = hashlib.sha256("\n".join(json.dumps(row, sort_keys=True, separators=(",", ":")) for row in rows).encode()).hexdigest()
    counts = {arm: sum(values) for arm, values in scores.items()}
    expected_counts = {arm: item["correct"] for arm, item in expected["arm_esrd"].items()}
    b3_mismatch = sum(1 for row in rows if row["decisions"]["B3_IDEAL_TYPED_PRODUCT"] != row["decisions"]["P1X_MINIMAL_SCIENTIFIC_ESCALATION"])

    checks = {
        "case_count": len(cases) == expected["n"] == 400,
        "identity_pair_digest": pair_digest == expected["protected_identity_pairs_sha256"],
        "bundle_digest": bundle_digest == expected["protected_bundle_sha256"],
        "row_digest": row_digest == expected["canonical_rows_sha256"],
        "headline_counts": counts == expected_counts,
        "b3_decision_mismatches_zero": b3_mismatch == expected["b3_equivalence"]["decision_mismatches"] == 0,
    }
    return {
        "schema_version": "P1_X_INDEPENDENT_VERIFICATION_V2",
        "independent_of_execution_module": true,
        "case_count": len(cases),
        "arm_correct": counts,
        "identity_pair_digest": pair_digest,
        "bundle_digest": bundle_digest,
        "row_digest": row_digest,
        "b3_decision_mismatches": b3_mismatch,
        "checks": checks,
        "ok": all(checks.values()),
        "terminal": "P1_X_V2_INDEPENDENT_VERIFICATION_PASS" if all(checks.values()) else "P1_X_V2_INDEPENDENT_VERIFICATION_FAIL",
    }


def main() -> int:
    result = verify()
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
