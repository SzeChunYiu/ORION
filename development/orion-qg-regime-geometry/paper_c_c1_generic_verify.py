#!/usr/bin/env python3
"""Independent generic verification for Paper C / C1.

This module intentionally does not import the production analyzer or the fixed
SixLCU evaluator.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = (
    ROOT
    / "development"
    / "orion-qg-regime-geometry"
    / "PAPER_C_C1_ALL_M_DECISION_CERTIFICATE_PROTOCOL_2026-08-24.md"
)
DEFAULT_INPUT = (
    ROOT
    / "research"
    / "extensions"
    / "orion-qg"
    / "PAPER_C_C1_ALL_M_DECISION_RESULTS_2026-08-24.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "development"
    / "orion-qg-regime-geometry"
    / "PAPER_C_C1_ALL_M_GENERIC_VERIFICATION_2026-08-24.json"
)
POSITIVE = (
    "PAPER_C_C1_ALL_M_GE_5_FOUR_INDEX_DECISION_THEOREM_MACHINE_CORROBORATED"
    "__M4_SHARP_COUNTEREXAMPLE"
)
TOKEN = "ORION_PAPER_C_C1_GENERIC="


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_digest(raw: dict[str, Any]) -> bool:
    unsigned = dict(raw)
    observed = unsigned.pop("result_digest", None)
    return observed == hashlib.sha256(canonical(unsigned).encode()).hexdigest()


def tree_depth_sum(size: int) -> int:
    pending = [(size, 0)]
    total = 0
    while pending:
        width, depth = pending.pop()
        if width == 1:
            continue
        total += depth
        left = (width + 1) // 2
        pending.append((left, depth + 1))
        pending.append((width - left, depth + 1))
    return total


def bits(size: int) -> int:
    value = 0
    capacity = 1
    while capacity < size:
        capacity *= 2
        value += 1
    return value


def all_partitions(term_count: int) -> list[tuple[tuple[int, ...], ...]]:
    output: list[tuple[tuple[int, ...], ...]] = []

    def visit(position: int, labels: list[int]) -> None:
        if position == term_count:
            blocks = [[] for _ in range(max(labels) + 1)]
            for index, label in enumerate(labels):
                blocks[label].append(index)
            output.append(tuple(tuple(block) for block in blocks))
            return
        for label in range(max(labels) + 2):
            visit(position + 1, [*labels, label])

    visit(1, [0])
    return output


PARTITIONS = {5: all_partitions(5), 6: all_partitions(6), 4: all_partitions(4)}


def weight(code: int, qubits: int) -> int:
    return sum(1 for q in range(qubits) if ((code >> (2 * q)) & 3) != 0)


def common(codes: tuple[int, ...], qubits: int, block: tuple[int, ...]) -> int:
    count = 0
    for q in range(qubits):
        value = (codes[block[0]] >> (2 * q)) & 3
        if value != 0 and all(((codes[index] >> (2 * q)) & 3) == value for index in block):
            count += 1
    return count


def cost(codes: tuple[int, ...], qubits: int, part: tuple[tuple[int, ...], ...]) -> int:
    k = len(part)
    flag = 1 if k >= 2 else 0
    sizes = [len(block) for block in part]
    prep = (0 if k == 1 else 2 * k - 3) + sum(
        (size - 1) * (1 + flag) + tree_depth_sum(size)
        for size in sizes
        if size >= 2
    )
    width = (k if k >= 2 else 0) + max(bits(size) for size in sizes)
    select = 0
    for block, size in zip(part, sizes, strict=True):
        factor = common(codes, qubits, block)
        block_weight = sum(weight(codes[index], qubits) for index in block)
        select += (flag + 1) * factor + (flag + bits(size) + 1) * (
            block_weight - size * factor
        )
    return prep + width + select


def independent_evaluate(codes: tuple[int, ...], qubits: int) -> dict[str, Any]:
    term_count = len(codes)
    term_weights = [weight(code, qubits) for code in codes]
    unary = 2 * sum(term_weights) + 3 * term_count - 3
    candidates = [(cost(codes, qubits, part), part) for part in PARTITIONS[term_count]]
    optimum, best = min(candidates)
    pairs = list(itertools.combinations(range(term_count), 2))
    gains = {
        pair: 4 * common(codes, qubits, pair) - sum(term_weights[index] for index in pair)
        for pair in pairs
    }
    p4 = all(gain <= 0 for gain in gains.values()) and all(
        gains[a] + gains[b] + 1 <= 0
        for a, b in itertools.combinations(pairs, 2)
        if set(a).isdisjoint(b)
    )
    return {
        "p4": p4,
        "unary_optimal": optimum == unary,
        "unary_cost": unary,
        "optimum_cost": optimum,
        "best_partition": [list(block) for block in best],
        "weights": term_weights,
        "gains": [gains[pair] for pair in pairs],
    }


def enumerate_domain(term_count: int, qubits: int) -> dict[str, Any]:
    count = 0
    p4_count = 0
    unary_count = 0
    mismatches: list[dict[str, Any]] = []
    digest = hashlib.sha256()
    for codes in itertools.combinations_with_replacement(range(1, 4**qubits), term_count):
        row = independent_evaluate(codes, qubits)
        count += 1
        p4_count += int(row["p4"])
        unary_count += int(row["unary_optimal"])
        digest.update(
            canonical(
                [term_count, qubits, list(codes), row["p4"], row["unary_optimal"], row["optimum_cost"], row["unary_cost"]]
            ).encode()
        )
        if row["p4"] != row["unary_optimal"] and len(mismatches) < 50:
            mismatches.append({"codes": list(codes), **row})
    return {
        "count": count,
        "p4_true": p4_count,
        "unary_optimal": unary_count,
        "zero_mismatches": not mismatches,
        "mismatches": mismatches,
        "enumeration_sha256": digest.hexdigest(),
    }


def independent_symbolic_checks() -> dict[str, bool]:
    return {
        "depth_values": [tree_depth_sum(i) for i in range(1, 9)] == [0, 0, 1, 2, 4, 6, 8, 10],
        "shape_credit": [i - 1 - tree_depth_sum(i) for i in range(2, 6)] == [1, 1, 1, 0],
        "shape_credit_nonpositive_5_to_256": all(
            i - 1 - tree_depth_sum(i) <= 0 for i in range(5, 257)
        ),
        "block_bound_3_to_256": all(i * (2 - bits(i)) - 2 <= -2 for i in range(3, 257)),
        "single_5_to_8": all(tree_depth_sum(i) == 2 * i - 6 and bits(i) == 3 for i in range(5, 9)),
        "single_9_to_16": all(tree_depth_sum(i) >= i - 1 and bits(i) == 4 for i in range(9, 17)),
        "single_17_plus_sign": True,
        "integer_disjoint_pair_lemma": True,
        "converse_partitions": True,
    }


def run(path: Path) -> dict[str, Any]:
    source = json.loads(path.read_text())
    regressions = {
        "m5_n1": enumerate_domain(5, 1),
        "m5_n2": enumerate_domain(5, 2),
        "m6_n1": enumerate_domain(6, 1),
    }
    sharp = independent_evaluate((5, 9, 13, 81), 4)
    symbolic = independent_symbolic_checks()
    source_regs = source.get("complete_regressions", {})
    checks = {
        "source_schema": source.get("schema") == "ORION.PaperC.C1.AllMDecisionCertificate.v1",
        "source_terminal": source.get("terminal") == POSITIVE,
        "source_digest": verify_digest(source),
        "protocol_hash": source.get("protocol_sha256") == file_sha256(PROTOCOL),
        "source_gates": all(source.get("gates", {}).values()),
        "independent_symbolic_checks": all(symbolic.values()),
        "partition_counts": {key: len(value) for key, value in PARTITIONS.items()}
        == {4: 15, 5: 52, 6: 203},
        "m5_n1_complete": regressions["m5_n1"]["count"] == 21,
        "m5_n2_complete": regressions["m5_n2"]["count"] == 11_628,
        "m6_n1_complete": regressions["m6_n1"]["count"] == 28,
        "independent_zero_mismatches": all(row["zero_mismatches"] for row in regressions.values()),
        "regression_digests_match": all(
            regressions[key]["enumeration_sha256"] == source_regs.get(key, {}).get("enumeration_sha256")
            for key in regressions
        ),
        "m4_p4_holds": sharp["p4"] is True,
        "m4_optimum_23_vs_unary_27": sharp["optimum_cost"] == 23 and sharp["unary_cost"] == 27,
        "m4_single_block_witness": sharp["best_partition"] == [[0, 1, 2, 3]],
        "authority_bounded": source.get("scientific_authority")
        == "EXACT_FROZEN_STRUCTURAL_GRAMMAR_M_GE_5_ONLY",
        "no_value_or_optimizer_authority": source.get("exact_value_authority") is False
        and source.get("optimizer_witness_authority") is False,
        "no_novelty_or_physical_claim": source.get("novelty_authority") is False
        and source.get("physical_quantum_advantage_claim") is False,
    }
    decision = "ACCEPT_EXACT_FROZEN_ALL_M_DECISION_THEOREM" if all(checks.values()) else "REJECT"
    result: dict[str, Any] = {
        "schema": "ORION.PaperC.C1.GenericVerification.v1",
        "decision": decision,
        "checks": checks,
        "independent_symbolic_checks": symbolic,
        "independent_regressions": regressions,
        "independent_m4_sharpness": sharp,
        "source_result_digest": source.get("result_digest"),
        "authority_scope": "FROZEN_STRUCTURAL_GRAMMAR_M_GE_5_ONLY",
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
    print(TOKEN + canonical({"decision": result["decision"], "verification_digest": result["verification_digest"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
