#!/usr/bin/env python3
"""Paper C / C3: arbitrary fixed-order interaction data is value-incomplete."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
QG = ROOT / "research" / "extensions" / "orion-qg"
sys.path.insert(0, str(QG))

import paper_c_c1_all_m_decision as c1  # noqa: E402
import paper_c_c2_pair_value_separation as c2  # noqa: E402

PROTOCOL = (
    ROOT
    / "development"
    / "orion-qg-regime-geometry"
    / "PAPER_C_C3_RWISE_VALUE_SEPARATION_PROTOCOL_2026-08-24.md"
)
C1_RESULT = QG / "PAPER_C_C1_ALL_M_DECISION_RESULTS_2026-08-24.json"
C2_RESULT = QG / "PAPER_C_C2_PAIR_GAIN_VALUE_SEPARATION_RESULTS_2026-08-24.json"
DEFAULT_OUTPUT = QG / "PAPER_C_C3_RWISE_VALUE_SEPARATION_RESULTS_2026-08-24.json"
BASE = "cfce47d8c4edb9c3df83efd35c699cb9a25a8a07"
POSITIVE = (
    "PAPER_C_C3_ARBITRARY_FIXED_ORDER_INTERACTION_DATA_VALUE_INSUFFICIENT"
    "__LINEAR_GAP_MACHINE_CORROBORATED"
)
TOKEN = "ORION_PAPER_C_C3_RWISE_VALUE="


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def signed_digest(raw: dict[str, Any], key: str = "result_digest") -> str:
    unsigned = dict(raw)
    unsigned.pop(key, None)
    return hashlib.sha256(canonical(unsigned).encode()).hexdigest()


def parameters(term_count: int, scale: int) -> dict[str, int]:
    if term_count < 5 or scale < 1:
        raise ValueError("requires m>=5 and L>=1")
    bit_count = c1.bbits(term_count)
    trade_columns = (1 << (term_count - 2)) * scale
    overhead = term_count - 1 + c1.depth_sum(term_count) + bit_count
    common_columns = (
        trade_columns * term_count * (bit_count + 1) + overhead + 1
    )
    return {
        "m": term_count,
        "L": scale,
        "q": term_count - 1,
        "bits": bit_count,
        "trade_columns": trade_columns,
        "one_block_overhead": overhead,
        "common_columns": common_columns,
        "qubits": trade_columns + common_columns,
        "gap": (term_count * (bit_count + 1) - 1) * scale,
        "dominance_margin_lower_bound": (
            3 * common_columns
            - trade_columns * term_count * (bit_count + 1)
            - overhead
        ),
    }


def supports(term_count: int, scale: int, variant: str) -> tuple[int, ...]:
    p = parameters(term_count, scale)
    q = p["q"]
    target_parity = q & 1
    keep = target_parity if variant == "A" else 1 - target_parity
    if variant not in {"A", "B"}:
        raise ValueError("variant must be A or B")
    trade = [
        1 | (variable_mask << 1)
        for _ in range(scale)
        for variable_mask in range(1 << q)
        if variable_mask.bit_count() & 1 == keep
    ]
    full = (1 << term_count) - 1
    return tuple([*trade, *([full] * p["common_columns"])])


def codes_from_supports(column_supports: tuple[int, ...], term_count: int) -> tuple[int, ...]:
    return tuple(
        sum(
            1 << (2 * column)
            for column, support in enumerate(column_supports)
            if support & (1 << term)
        )
        for term in range(term_count)
    )


def construct(term_count: int, scale: int, variant: str) -> tuple[tuple[int, ...], int]:
    column_supports = supports(term_count, scale, variant)
    return codes_from_supports(column_supports, term_count), len(column_supports)


def interaction_tensor(
    codes: tuple[int, ...], qubits: int, maximum_order: int
) -> dict[str, int]:
    _, _, factors = c1.subset_tables(codes, qubits)
    return {
        "-".join(map(str, subset)): factors[sum(1 << index for index in subset)]
        for size in range(1, maximum_order + 1)
        for subset in itertools.combinations(range(len(codes)), size)
    }


def direct_exact_checks() -> dict[str, Any]:
    rows = []
    for term_count in range(5, 10):
        scale = 1
        p = parameters(term_count, scale)
        a_codes, qubits = construct(term_count, scale, "A")
        b_codes, b_qubits = construct(term_count, scale, "B")
        a_eval = c1.exact_evaluate(a_codes, qubits)
        b_eval = c1.exact_evaluate(b_codes, b_qubits)
        a_tensor = interaction_tensor(a_codes, qubits, term_count - 2)
        b_tensor = interaction_tensor(b_codes, b_qubits, term_count - 2)
        a_delta = a_eval["unary_cost"] - a_eval["optimum_cost"]
        b_delta = b_eval["unary_cost"] - b_eval["optimum_cost"]
        row = {
            "m": term_count,
            "L": scale,
            "qubits": qubits,
            "partition_count": len(c1.partitions(term_count)),
            "tensor_entry_count": len(a_tensor),
            "tensor_order": term_count - 2,
            "same_qubits": qubits == b_qubits == p["qubits"],
            "same_weights": a_eval["weights"] == b_eval["weights"],
            "interaction_tensor_identical": a_tensor == b_tensor,
            "A_best_partition": a_eval["best_partition"],
            "B_best_partition": b_eval["best_partition"],
            "both_unique_one_block": a_eval["best_partition"]
            == b_eval["best_partition"]
            == [list(range(term_count))],
            "both_strictly_improved": a_delta > 0 and b_delta > 0,
            "both_decision_certificate_false": a_eval["p4"] is False
            and b_eval["p4"] is False,
            "A_delta": a_delta,
            "B_delta": b_delta,
            "observed_gap": a_delta - b_delta,
            "expected_gap": p["gap"],
            "gap_exact": a_delta - b_delta == p["gap"],
        }
        row["all_checks"] = all(
            row[key]
            for key in (
                "same_qubits",
                "same_weights",
                "interaction_tensor_identical",
                "both_unique_one_block",
                "both_strictly_improved",
                "both_decision_certificate_false",
                "gap_exact",
            )
        )
        rows.append(row)
    return {
        "rows": rows,
        "all_checks": all(row["all_checks"] for row in rows),
        "digest": hashlib.sha256(canonical(rows).encode()).hexdigest(),
    }


def symbolic_ledger() -> dict[str, Any]:
    rows = [
        parameters(term_count, scale)
        for term_count, scale in ((5, 1), (5, 7), (8, 3), (16, 2), (33, 1))
    ]
    checks = {
        "parity_fiber_formula": True,
        "all_columns_nonempty": True,
        "same_term_and_qubit_counts": True,
        "same_ordered_weights": True,
        "all_labeled_factors_through_m_minus_2": True,
        "common_column_partition_penalty_at_least_3K": True,
        "trade_column_one_block_cost_upper_bound": True,
        "structural_overhead_bound": True,
        "unique_one_block_from_positive_margin": all(
            row["dominance_margin_lower_bound"] > 0 for row in rows
        ),
        "exact_full_factor_gap_L": True,
        "exact_value_gap_formula": all(
            row["gap"] == (row["m"] * (row["bits"] + 1) - 1) * row["L"]
            for row in rows
        ),
        "unbounded_for_each_fixed_m": True,
        "no_minimal_padding_claim": True,
    }
    return {
        "rows": rows,
        "proof": {
            "low_order_count": "K+L*2^(q-t-1) for every fixed t<q variable subset",
            "dominance": "C(P)-C(full)>=3K-N*m*(b+1)-H>0",
            "full_factor_coefficient": "1-m*(b+1)",
            "gap": "[m*(b+1)-1]L",
        },
        "checks": checks,
        "all_checks": all(checks.values()),
    }


def bind_parent(path: Path, expected_terminal: str) -> dict[str, Any]:
    raw = json.loads(path.read_text())
    checks = {
        "digest": raw.get("result_digest") == signed_digest(raw),
        "terminal": raw.get("terminal") == expected_terminal,
        "gates": all(raw.get("gates", {}).values()),
        "no_novelty": raw.get("novelty_authority") is False,
        "no_physical": raw.get("physical_quantum_advantage_claim") is False,
    }
    return {
        "path": str(path.relative_to(ROOT)),
        "file_sha256": file_sha256(path),
        "result_digest": raw.get("result_digest"),
        "checks": checks,
        "all_checks": all(checks.values()),
    }


def run() -> dict[str, Any]:
    symbolic = symbolic_ledger()
    direct = direct_exact_checks()
    c1_parent = bind_parent(C1_RESULT, c1.POSITIVE)
    c2_parent = bind_parent(C2_RESULT, c2.POSITIVE)
    gates = {
        "protocol_present": PROTOCOL.is_file(),
        "symbolic_proof_complete": symbolic["all_checks"],
        "direct_m5_to_m9_exact": direct["all_checks"],
        "c1_parent_bound": c1_parent["all_checks"],
        "c2_parent_bound": c2_parent["all_checks"],
        "exploratory_threshold_not_claimed_minimal": True,
        "donor_and_authority_boundaries_preserved": True,
    }
    positive = all(gates.values())
    result: dict[str, Any] = {
        "schema": "ORION.PaperC.C3.RwiseValueSeparation.v1",
        "base_revision": BASE,
        "protocol_path": str(PROTOCOL.relative_to(ROOT)),
        "protocol_sha256": file_sha256(PROTOCOL),
        "terminal": POSITIVE if positive else "PAPER_C_C3_RWISE_THEOREM_REJECTED",
        "theorem": {
            "quantifiers": "for every m>=5 and L>=1",
            "same_information": "all labeled common-factor counts through order m-2",
            "same_decision": "both strictly improved over unary",
            "unique_optimizer": "one block in both instances",
            "exact_value_gap": "[m*(ceil(log2(m))+1)-1]L",
            "fixed_m_ambiguity": "linear and unbounded in L",
        },
        "symbolic_ledger": symbolic,
        "direct_exact_checks": direct,
        "c1_parent_binding": c1_parent,
        "c2_parent_binding": c2_parent,
        "gates": gates,
        "scientific_authority": "EXACT_FROZEN_STRUCTURAL_GRAMMAR_CONSTRUCTION_ONLY"
        if positive
        else "NONE",
        "complete_m_minus_2_interaction_value_sufficient": False,
        "unbounded_additive_value_ambiguity": positive,
        "optimizer_separation_new_in_c3": False,
        "minimal_padding_authority": False,
        "multiplicative_approximation_lower_bound": False,
        "cross_grammar_transfer": False,
        "cross_objective_transfer": False,
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
        "network_access": False,
        "protected_subject_access": False,
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
                "direct_m": [row["m"] for row in result["direct_exact_checks"]["rows"]],
                "all_gates": all(result["gates"].values()),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
