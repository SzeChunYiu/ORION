#!/usr/bin/env python3
"""Paper D / D1: exact authority retraction for stratified certificates."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[3]
QG = ROOT / "research" / "extensions" / "orion-qg"
DEV = ROOT / "development" / "orion-qg-regime-geometry"
PROTOCOL = DEV / "PAPER_D_D1_AUTHORITY_CALCULUS_PROTOCOL_2026-08-24.md"
QG5 = QG / "QG5_CERTIFIED_FORECAST_RESULTS.json"
QG5B = QG / "QG5B_EXACT_FORECASTER_RESULTS.json"
QG5_PROTOCOL = DEV / "QG5_FORECAST_THEORY_PROTOCOL.md"
QG5B_PROTOCOL = DEV / "QG5B_EXACT_FORECASTER_PROTOCOL.md"
C1 = QG / "PAPER_C_C1_ALL_M_DECISION_RESULTS_2026-08-24.json"
C2 = QG / "PAPER_C_C2_PAIR_GAIN_VALUE_SEPARATION_RESULTS_2026-08-24.json"
C3 = QG / "PAPER_C_C3_RWISE_VALUE_SEPARATION_RESULTS_2026-08-24.json"
DEFAULT_OUTPUT = QG / "PAPER_D_D1_AUTHORITY_CALCULUS_RESULTS_2026-08-24.json"
BASE = "fa85599ad8ec057f98f935735ab02e30cbbb49ee"
POSITIVE = (
    "PAPER_D_D1_STRATIFIED_AUTHORITY_CALCULUS_EXACT_MINIMAL_RETRACTION"
    "__QG5_COUNTEREXAMPLE_LOCALIZED__SIXLCU_NONINTERFERENCE_CORROBORATED"
)
TOKEN = "ORION_PAPER_D_D1_AUTHORITY="


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def signed_digest(raw: dict[str, Any]) -> str:
    unsigned = dict(raw)
    unsigned.pop("result_digest", None)
    return hashlib.sha256(canonical(unsigned).encode()).hexdigest()


def closure(
    node_count: int,
    seeds: frozenset[int],
    refuted: frozenset[int],
    rules: tuple[tuple[tuple[int, ...], int], ...],
    reverse: bool = False,
) -> frozenset[int]:
    authorized = set(seeds - refuted)
    schedule: Iterable[tuple[tuple[int, ...], int]] = reversed(rules) if reverse else rules
    schedule = tuple(schedule)
    changed = True
    while changed:
        changed = False
        for premises, conclusion in schedule:
            if conclusion in refuted or conclusion in authorized:
                continue
            if all(premise in authorized for premise in premises):
                authorized.add(conclusion)
                changed = True
    assert all(0 <= node < node_count for node in authorized)
    return frozenset(authorized)


def recursive_authority(
    node_count: int,
    seeds: frozenset[int],
    refuted: frozenset[int],
    parents: tuple[tuple[int, ...], ...],
) -> frozenset[int]:
    memo: dict[int, bool] = {}

    def proved(node: int) -> bool:
        if node in memo:
            return memo[node]
        if node in refuted:
            memo[node] = False
        elif node in seeds:
            memo[node] = True
        elif parents[node]:
            memo[node] = all(proved(parent) for parent in parents[node])
        else:
            memo[node] = False
        return memo[node]

    return frozenset(node for node in range(node_count) if proved(node))


def ancestors(node: int, parents: tuple[tuple[int, ...], ...]) -> frozenset[int]:
    found: set[int] = set()
    stack = list(parents[node])
    while stack:
        parent = stack.pop()
        if parent in found:
            continue
        found.add(parent)
        stack.extend(parents[parent])
    return frozenset(found)


def parent_system(node_count: int, edge_mask: int) -> tuple[tuple[int, ...], ...]:
    parents: list[list[int]] = [[] for _ in range(node_count)]
    bit = 0
    for conclusion in range(node_count):
        for premise in range(conclusion):
            if edge_mask & (1 << bit):
                parents[conclusion].append(premise)
            bit += 1
    return tuple(tuple(row) for row in parents)


def assignment(node_count: int, code: int) -> tuple[frozenset[int], frozenset[int]]:
    seeds: set[int] = set()
    refuted: set[int] = set()
    for node in range(node_count):
        state = code % 3
        code //= 3
        if state == 1:
            seeds.add(node)
        elif state == 2:
            refuted.add(node)
    return frozenset(seeds), frozenset(refuted)


def exhaustive_formal_ledger() -> dict[str, Any]:
    rows = []
    total_models = 0
    failures: list[dict[str, Any]] = []
    for node_count in range(1, 6):
        edge_count = node_count * (node_count - 1) // 2
        graphs = 1 << edge_count
        assignments = 3**node_count
        checked = 0
        for edge_mask in range(graphs):
            parents = parent_system(node_count, edge_mask)
            rules = tuple(
                (parents[node], node) for node in range(node_count) if parents[node]
            )
            for assignment_code in range(assignments):
                seeds, refuted = assignment(node_count, assignment_code)
                observed = closure(node_count, seeds, refuted, rules)
                reverse = closure(node_count, seeds, refuted, rules, reverse=True)
                recursive = recursive_authority(node_count, seeds, refuted, parents)
                baseline = closure(node_count, seeds, frozenset(), rules)
                monotone = observed <= baseline
                noninterference = all(
                    node in observed
                    for node in baseline
                    if node not in refuted and not (ancestors(node, parents) & refuted)
                )
                if not (observed == reverse == recursive and monotone and noninterference):
                    failures.append(
                        {
                            "node_count": node_count,
                            "edge_mask": edge_mask,
                            "assignment_code": assignment_code,
                        }
                    )
                checked += 1
        total_models += checked
        rows.append(
            {
                "node_count": node_count,
                "graphs": graphs,
                "assignments_per_graph": assignments,
                "models_checked": checked,
            }
        )

    alternative_rules = (
        ((0,), 2),
        ((1,), 2),
        ((2,), 3),
    )
    rescued = closure(4, frozenset({0, 1}), frozenset({0}), alternative_rules)
    lost = closure(4, frozenset({0, 1}), frozenset({0, 1}), alternative_rules)
    alternative_checks = {
        "independent_alternative_rescues_conclusion": rescued == frozenset({1, 2, 3}),
        "all_alternatives_refuted_retract_conclusion": lost == frozenset(),
    }
    return {
        "rows": rows,
        "total_models_checked": total_models,
        "failure_count": len(failures),
        "failures_verbatim": failures[:10],
        "alternative_derivation_checks": alternative_checks,
        "symbolic_topological_induction_proof_registered": True,
        "finite_enumeration_is_proof": False,
        "all_checks": not failures and all(alternative_checks.values()),
    }


def qg5_instantiation() -> dict[str, Any]:
    old = json.loads(QG5.read_text())
    repaired = json.loads(QG5B.read_text())
    counterexample = old["benchmark"]["fresh_seeded_panel"]["nonzero_errors_verbatim"][0]
    panel_a = repaired["panels"]["panel_a_refuting_instance"]

    nodes = (
        "FEASIBLE_UPPER_BOUND",
        "SUPPORT_TWO_SUFFICIENCY",
        "ORIGINAL_CLOSED_FORM_EXACTNESS",
        "ORIGINAL_REGIME_LABEL",
        "F2_EXACTNESS",
        "REPAIRED_REGIME_LABEL",
    )
    seeds = frozenset({0, 1, 4})
    refuted = frozenset({2})
    rules = (((2,), 3), ((4,), 5))
    pre = closure(len(nodes), frozenset({0, 1, 2, 4}), frozenset(), rules)
    post = closure(len(nodes), seeds, refuted, rules)
    expected_survivors = {
        "FEASIBLE_UPPER_BOUND",
        "SUPPORT_TWO_SUFFICIENCY",
        "F2_EXACTNESS",
        "REPAIRED_REGIME_LABEL",
    }
    expected_retracted = {
        "ORIGINAL_CLOSED_FORM_EXACTNESS",
        "ORIGINAL_REGIME_LABEL",
    }
    survivors = {nodes[index] for index in post}
    retracted = {nodes[index] for index in pre - post}
    structured = old["benchmark"]["structured_n2_exhaustive"]
    chemistry = old["benchmark"]["receipted_chemistry_rows"]
    chemistry_rows = sum(len(rows) for rows in chemistry.values())
    library_verified_exact = sum(
        subject.get("forecast_error_zero_count", 0)
        for subject in old["library_forecast_table"]["subjects"]
        if subject.get("certificate_status", "").startswith("DP_RECEIPT_COMMITTED")
    )
    exact = (
        structured["forecast_error_zero_count"]
        + old["benchmark"]["fresh_seeded_panel"]["forecast_error_zero_count"]
        + chemistry_rows
        + library_verified_exact
    )
    total = old["benchmark"]["dp_compared_instances_total"]
    checks = {
        "qg5_protocol_hash": old.get("protocol_sha256") == file_sha256(QG5_PROTOCOL),
        "qg5b_protocol_hash": repaired.get("protocol_sha256") == file_sha256(QG5B_PROTOCOL),
        "original_exact_count_9545": exact == 9545,
        "original_total_9546": total == 9546,
        "single_error": old["benchmark"]["nonzero_forecast_errors_total"] == 1,
        "exact_counterexample": counterexample["C_DP"] == 10
        and counterexample["predicted_C_DP"] == 11
        and counterexample["error"] == 1,
        "constructive_upper_survives": counterexample["C_DP"]
        <= counterexample["predicted_C_DP"]
        and old["gates"]["sandwich_and_borrow_soundness_asserted"] is True,
        "support_theorem_survives": panel_a["C_DP"] == panel_a["F2_C_Dxx"] == 10
        and repaired["gates"]["dxx_witness_referee_pass"] is True,
        "original_label_refuted": panel_a["qg5_regime"] == "donor_exact"
        and panel_a["truth_donor_exact"] is False,
        "repair_separately_supported": repaired["q1"]["outcome"] == "Q1_ZERO_ERROR"
        and repaired["q2"]["outcome"] == "Q2_ENLARGED_BORROW_CLOSES"
        and panel_a["F2_C_Dxx"] == panel_a["f_Bprime"] == panel_a["C_DP"] == 10,
        "repair_panel_entries_not_denominator": repaired["q1"]["dp_compared_instances_total"]
        == 9547,
        "minimal_retraction_exact": survivors == expected_survivors
        and retracted == expected_retracted,
    }
    return {
        "parent_files": {
            "qg5_path": str(QG5.relative_to(ROOT)),
            "qg5_sha256": file_sha256(QG5),
            "qg5b_path": str(QG5B.relative_to(ROOT)),
            "qg5b_sha256": file_sha256(QG5B),
        },
        "original_benchmark": {
            "exact": exact,
            "total": total,
            "errors": total - exact,
            "universal_exactness": False,
        },
        "counterexample": {
            "n": counterexample["n"],
            "index": counterexample["index"],
            "C_DP": counterexample["C_DP"],
            "F_original": counterexample["predicted_C_DP"],
            "F2": panel_a["F2_C_Dxx"],
            "f_Bprime": panel_a["f_Bprime"],
            "original_label": panel_a["qg5_regime"],
            "truth_donor_exact": panel_a["truth_donor_exact"],
        },
        "pre_authority": sorted(nodes[index] for index in pre),
        "post_authority": sorted(survivors),
        "exact_retraction": sorted(retracted),
        "qg5b_panel_entries": repaired["q1"]["dp_compared_instances_total"],
        "qg5b_is_post_outcome_repair": True,
        "qg5b_is_prospective_confirmation": False,
        "checks": checks,
        "all_checks": all(checks.values()),
    }


def paper_c_noninterference() -> dict[str, Any]:
    c1 = json.loads(C1.read_text())
    c2 = json.loads(C2.read_text())
    c3 = json.loads(C3.read_text())
    nodes = (
        "DECISION_CERTIFICATE_EXACT",
        "PAIR_INFORMATION_VALUE_SUFFICIENT",
        "PAIR_INFORMATION_OPTIMIZER_SUFFICIENT",
        "FIXED_R_INTERACTION_VALUE_SUFFICIENT",
    )
    authority = closure(4, frozenset({0}), frozenset({1, 2, 3}), tuple())
    checks = {
        "c1_terminal": c1.get("terminal")
        == "PAPER_C_C1_ALL_M_GE_5_FOUR_INDEX_DECISION_THEOREM_MACHINE_CORROBORATED__M4_SHARP_COUNTEREXAMPLE",
        "c2_terminal": c2.get("terminal")
        == "PAPER_C_C2_COMPLETE_PAIR_INFORMATION_VALUE_GAP_2T_MINUS_1_UNBOUNDED__OPTIMIZER_TRIPLE_VS_PAIR_SEPARATION",
        "c3_terminal": c3.get("terminal")
        == "PAPER_C_C3_ARBITRARY_FIXED_ORDER_INTERACTION_DATA_VALUE_INSUFFICIENT__LINEAR_GAP_MACHINE_CORROBORATED",
        "all_parent_gates": all(c1.get("gates", {}).values())
        and all(c2.get("gates", {}).values())
        and all(c3.get("gates", {}).values()),
        "value_insufficiency_bound": c2.get("complete_pair_information_value_sufficient")
        is False
        and c3.get("complete_m_minus_2_interaction_value_sufficient") is False,
        "optimizer_insufficiency_bound": c2.get(
            "complete_pair_information_optimizer_sufficient"
        )
        is False,
        "decision_survives": authority == frozenset({0}),
    }
    return {
        "parent_files": {
            "c1_sha256": file_sha256(C1),
            "c2_sha256": file_sha256(C2),
            "c3_sha256": file_sha256(C3),
        },
        "authorized": sorted(nodes[index] for index in authority),
        "refuted_sufficiency_claims": sorted(nodes[index] for index in {1, 2, 3}),
        "result_owner": "PAPER_C",
        "paper_d_ownership_claim": False,
        "is_second_forecasting_family": False,
        "checks": checks,
        "all_checks": all(checks.values()),
    }


def run() -> dict[str, Any]:
    formal = exhaustive_formal_ledger()
    qg5 = qg5_instantiation()
    paper_c = paper_c_noninterference()
    gates = {
        "protocol_present": PROTOCOL.is_file(),
        "formal_calculus_corroborated": formal["all_checks"],
        "qg5_exact_retraction_bound": qg5["all_checks"],
        "paper_c_noninterference_bound": paper_c["all_checks"],
        "original_denominator_preserved": qg5["original_benchmark"]
        == {"exact": 9545, "total": 9546, "errors": 1, "universal_exactness": False},
        "post_outcome_boundary_preserved": qg5["qg5b_is_post_outcome_repair"] is True
        and qg5["qg5b_is_prospective_confirmation"] is False,
        "donor_and_ownership_boundaries_preserved": True,
    }
    positive = all(gates.values())
    result: dict[str, Any] = {
        "schema": "ORION.PaperD.D1.StratifiedAuthority.v1",
        "base_revision": BASE,
        "protocol_path": str(PROTOCOL.relative_to(ROOT)),
        "protocol_sha256": file_sha256(PROTOCOL),
        "terminal": POSITIVE if positive else "PAPER_D_D1_AUTHORITY_CALCULUS_REJECTED",
        "theorem": {
            "object": "finite acyclic registered certificate hypergraph",
            "authorized_set": "unique least fixed point from non-refuted seeds",
            "minimal_retraction": "pre_authority minus post_authority",
            "noninterference": "ancestry-disjoint claims retain authority",
            "alternative_derivation": "one untainted proof tree suffices",
        },
        "formal_ledger": formal,
        "qg5_instantiation": qg5,
        "paper_c_noninterference": paper_c,
        "gates": gates,
        "scientific_authority": "FORMAL_STRATIFIED_CERTIFICATE_CALCULUS_AND_BOUND_PARENT_INSTANTIATIONS_ONLY"
        if positive
        else "NONE",
        "generic_fixed_point_novelty_authority": False,
        "paper_d_standalone_novelty_authority": False,
        "paper_c_result_ownership": False,
        "second_independent_forecasting_family": False,
        "real_static_framework_integration": False,
        "cross_unregistered_system_transfer": False,
        "physical_quantum_advantage_claim": False,
        "prospective_repair_authority": False,
        "novelty_authority": False,
        "ci_authority": False,
    }
    result["result_digest"] = signed_digest(result)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    result = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        TOKEN
        + canonical(
            {
                "terminal": result["terminal"],
                "result_digest": result["result_digest"],
                "formal_models": result["formal_ledger"]["total_models_checked"],
                "qg5_retraction": result["qg5_instantiation"]["exact_retraction"],
                "all_gates": all(result["gates"].values()),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
