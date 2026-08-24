#!/usr/bin/env python3
"""Independent verifier for Paper D / D1 stratified authority calculus."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEV = ROOT / "development" / "orion-qg-regime-geometry"
QG = ROOT / "research" / "extensions" / "orion-qg"
PROTOCOL = DEV / "PAPER_D_D1_AUTHORITY_CALCULUS_PROTOCOL_2026-08-24.md"
DEFAULT_INPUT = QG / "PAPER_D_D1_AUTHORITY_CALCULUS_RESULTS_2026-08-24.json"
DEFAULT_OUTPUT = DEV / "PAPER_D_D1_AUTHORITY_CALCULUS_GENERIC_2026-08-24.json"
QG5 = QG / "QG5_CERTIFIED_FORECAST_RESULTS.json"
QG5B = QG / "QG5B_EXACT_FORECASTER_RESULTS.json"
C1 = QG / "PAPER_C_C1_ALL_M_DECISION_RESULTS_2026-08-24.json"
C2 = QG / "PAPER_C_C2_PAIR_GAIN_VALUE_SEPARATION_RESULTS_2026-08-24.json"
C3 = QG / "PAPER_C_C3_RWISE_VALUE_SEPARATION_RESULTS_2026-08-24.json"
POSITIVE = (
    "PAPER_D_D1_STRATIFIED_AUTHORITY_CALCULUS_EXACT_MINIMAL_RETRACTION"
    "__QG5_COUNTEREXAMPLE_LOCALIZED__SIXLCU_NONINTERFERENCE_CORROBORATED"
)
TOKEN = "ORION_PAPER_D_D1_GENERIC="


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_valid(raw: dict[str, Any]) -> bool:
    unsigned = dict(raw)
    observed = unsigned.pop("result_digest", None)
    return observed == hashlib.sha256(canonical(unsigned).encode()).hexdigest()


def graph_parents(node_count: int, edge_mask: int) -> tuple[tuple[int, ...], ...]:
    rows: list[list[int]] = [[] for _ in range(node_count)]
    bit = 0
    for child in range(node_count):
        for parent in range(child):
            if edge_mask & (1 << bit):
                rows[child].append(parent)
            bit += 1
    return tuple(tuple(row) for row in rows)


def ternary_assignment(node_count: int, code: int) -> tuple[set[int], set[int]]:
    seeds: set[int] = set()
    refuted: set[int] = set()
    for node in range(node_count):
        state, code = code % 3, code // 3
        if state == 1:
            seeds.add(node)
        elif state == 2:
            refuted.add(node)
    return seeds, refuted


def topological_evaluate(
    parents: tuple[tuple[int, ...], ...], seeds: set[int], refuted: set[int]
) -> frozenset[int]:
    proved: set[int] = set()
    for node, premises in enumerate(parents):
        if node in refuted:
            continue
        if node in seeds or (premises and all(parent in proved for parent in premises)):
            proved.add(node)
    return frozenset(proved)


def frontier_evaluate(
    parents: tuple[tuple[int, ...], ...], seeds: set[int], refuted: set[int]
) -> frozenset[int]:
    proved = set(seeds - refuted)
    pending = set(range(len(parents))) - proved - refuted
    while True:
        additions = {
            node
            for node in pending
            if parents[node] and set(parents[node]) <= proved
        }
        if not additions:
            break
        proved |= additions
        pending -= additions
    return frozenset(proved)


def ancestor_set(node: int, parents: tuple[tuple[int, ...], ...]) -> set[int]:
    answer: set[int] = set()
    work = list(parents[node])
    while work:
        current = work.pop()
        if current not in answer:
            answer.add(current)
            work.extend(parents[current])
    return answer


def formal_check() -> dict[str, Any]:
    rows = []
    failures = 0
    for node_count in range(1, 6):
        graph_count = 1 << (node_count * (node_count - 1) // 2)
        assignment_count = 3**node_count
        checked = 0
        for edge_mask in range(graph_count):
            parents = graph_parents(node_count, edge_mask)
            for code in range(assignment_count):
                seeds, refuted = ternary_assignment(node_count, code)
                topological = topological_evaluate(parents, seeds, refuted)
                frontier = frontier_evaluate(parents, seeds, refuted)
                baseline = topological_evaluate(parents, seeds, set())
                noninterference = all(
                    node in topological
                    for node in baseline
                    if node not in refuted and not (ancestor_set(node, parents) & refuted)
                )
                failures += int(
                    topological != frontier
                    or not topological <= baseline
                    or not noninterference
                )
                checked += 1
        rows.append(
            {
                "n": node_count,
                "graphs": graph_count,
                "assignments": assignment_count,
                "models": checked,
            }
        )

    def alternative(refuted: set[int]) -> frozenset[int]:
        proved = {0, 1} - refuted
        if 2 not in refuted and (0 in proved or 1 in proved):
            proved.add(2)
        if 3 not in refuted and 2 in proved:
            proved.add(3)
        return frozenset(proved)

    alternatives = {
        "one_path_survives": alternative({0}) == frozenset({1, 2, 3}),
        "all_paths_fail": alternative({0, 1}) == frozenset(),
    }
    return {
        "rows": rows,
        "models": sum(row["models"] for row in rows),
        "failures": failures,
        "alternatives": alternatives,
        "all_checks": failures == 0 and all(alternatives.values()),
    }


def qg5_check() -> dict[str, Any]:
    old = json.loads(QG5.read_text())
    new = json.loads(QG5B.read_text())
    error = old["benchmark"]["fresh_seeded_panel"]["nonzero_errors_verbatim"][0]
    repair = new["panels"]["panel_a_refuting_instance"]
    total = old["benchmark"]["dp_compared_instances_total"]
    errors = old["benchmark"]["nonzero_forecast_errors_total"]
    exact = total - errors
    checks = {
        "counts": (exact, total, errors) == (9545, 9546, 1),
        "falsifier": error["C_DP"] == 10 < error["predicted_C_DP"] == 11,
        "upper": old["gates"]["sandwich_and_borrow_soundness_asserted"] is True
        and error["C_DP"] <= error["predicted_C_DP"],
        "support": repair["C_DP"] == repair["F2_C_Dxx"] == 10,
        "label_refuted": repair["qg5_regime"] == "donor_exact"
        and repair["truth_donor_exact"] is False,
        "repair": repair["f_Bprime"] == repair["F2_C_Dxx"] == repair["C_DP"]
        and new["q1"]["outcome"] == "Q1_ZERO_ERROR"
        and new["q2"]["outcome"] == "Q2_ENLARGED_BORROW_CLOSES",
        "repair_is_not_prospective": new["q1"]["dp_compared_instances_total"] == 9547,
    }
    return {
        "parent_sha256": {"qg5": file_sha256(QG5), "qg5b": file_sha256(QG5B)},
        "counts": {"exact": exact, "total": total, "errors": errors},
        "survivors": [
            "F2_EXACTNESS",
            "FEASIBLE_UPPER_BOUND",
            "REPAIRED_REGIME_LABEL",
            "SUPPORT_TWO_SUFFICIENCY",
        ],
        "retracted": ["ORIGINAL_CLOSED_FORM_EXACTNESS", "ORIGINAL_REGIME_LABEL"],
        "checks": checks,
        "all_checks": all(checks.values()),
    }


def paper_c_check() -> dict[str, Any]:
    c1, c2, c3 = (json.loads(path.read_text()) for path in (C1, C2, C3))
    checks = {
        "decision": c1.get("terminal", "").startswith(
            "PAPER_C_C1_ALL_M_GE_5_FOUR_INDEX_DECISION_THEOREM"
        ),
        "pair_value": c2.get("complete_pair_information_value_sufficient") is False,
        "pair_optimizer": c2.get("complete_pair_information_optimizer_sufficient")
        is False,
        "rwise_value": c3.get("complete_m_minus_2_interaction_value_sufficient")
        is False,
        "parents": all(c1.get("gates", {}).values())
        and all(c2.get("gates", {}).values())
        and all(c3.get("gates", {}).values()),
    }
    return {
        "parent_sha256": {
            "c1": file_sha256(C1),
            "c2": file_sha256(C2),
            "c3": file_sha256(C3),
        },
        "decision_survives": True,
        "paper_d_owns_results": False,
        "checks": checks,
        "all_checks": all(checks.values()),
    }


def run(path: Path) -> dict[str, Any]:
    source = json.loads(path.read_text())
    formal = formal_check()
    qg5 = qg5_check()
    paper_c = paper_c_check()
    checks = {
        "source_schema": source.get("schema") == "ORION.PaperD.D1.StratifiedAuthority.v1",
        "source_terminal": source.get("terminal") == POSITIVE,
        "source_digest": digest_valid(source),
        "protocol_hash": source.get("protocol_sha256") == file_sha256(PROTOCOL),
        "source_gates": all(source.get("gates", {}).values()),
        "formal": formal["all_checks"] and formal["models"] == 254253,
        "qg5": qg5["all_checks"]
        and qg5["retracted"] == source["qg5_instantiation"]["exact_retraction"],
        "paper_c": paper_c["all_checks"],
        "scope": source.get("scientific_authority")
        == "FORMAL_STRATIFIED_CERTIFICATE_CALCULUS_AND_BOUND_PARENT_INSTANTIATIONS_ONLY",
        "no_prospective_relabel": source.get("prospective_repair_authority") is False,
        "no_second_forecaster": source.get("second_independent_forecasting_family") is False,
        "no_framework_integration": source.get("real_static_framework_integration") is False,
        "no_novelty_or_physical": source.get("novelty_authority") is False
        and source.get("physical_quantum_advantage_claim") is False,
    }
    positive = all(checks.values())
    result: dict[str, Any] = {
        "schema": "ORION.PaperD.D1.GenericVerification.v1",
        "decision": "ACCEPT_STRATIFIED_AUTHORITY_CALCULUS"
        if positive
        else "REJECT_STRATIFIED_AUTHORITY_CALCULUS",
        "source_result_digest": source.get("result_digest"),
        "formal": formal,
        "qg5": qg5,
        "paper_c": paper_c,
        "checks": checks,
        "authority_scope": "FORMAL_STRATIFIED_CERTIFICATE_CALCULUS_AND_BOUND_PARENT_INSTANTIATIONS_ONLY",
        "prospective_repair_authority": False,
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
    }
    result["verification_digest"] = hashlib.sha256(canonical(result).encode()).hexdigest()
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    result = run(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        TOKEN
        + canonical(
            {
                "decision": result["decision"],
                "verification_digest": result["verification_digest"],
                "formal_models": result["formal"]["models"],
                "all_checks": all(result["checks"].values()),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
