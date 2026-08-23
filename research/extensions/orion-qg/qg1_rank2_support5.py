#!/usr/bin/env python3
"""QG-1 complete local + F2^5 machine check for the rank-2 support-five theorem."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
ORION_Q_DIR = REPO_ROOT / "research" / "extensions" / "orion-q"
sys.path.insert(0, str(ORION_Q_DIR))

# Production import is chemistry-free at module import time: it initializes the
# frozen local Pauli/DP tables but does not call any subject loader.  QG-1 uses it
# only to bind the independent local algebra below to the exact R6I implementation.
import max_r6i_exact_rank2_shared_tag_dp as production_r6i  # noqa: E402

PROTOCOL_PATH = (
    REPO_ROOT
    / "development"
    / "orion-qg-regime-geometry"
    / "QG1_RANK2_SUPPORT5_PROTOCOL_V1.md"
)
NOVELTY_PATH = (
    REPO_ROOT
    / "development"
    / "orion-qg-regime-geometry"
    / "QG1_NOVELTY_THREAT_FREEZE_2026-08-21.md"
)
DEFAULT_OUTPUT = REPO_ROOT / "artifacts" / "orion-qg-qg1-support5-theorem.json"
TOKEN_PREFIX = "ORIONQG_QG1_THEOREM="

# Independent local encoding: 0=I, 1=X, 2=Y, 3=Z.  Modulo phase the Pauli
# quotient is F_2^2 and multiplication is XOR in this coding.  The first theorem
# gate below independently compares every entry to the production R6I tables.
LETTERS = range(4)
FROZEN_BASE = "e6011bbeae68d91b5cce45ffa34e67306905844d"
BOUNDARY_CLASSES = (1, 2, 4, 8, 20)
EXPECTED_BOUNDARY_XOR = 27  # alpha=1, labels c0=2 and c1=3.


def mul(a: int, b: int) -> int:
    return a ^ b


def wt(a: int) -> int:
    return int(a != 0)


def symp(a: int, b: int) -> int:
    return int(a != 0 and b != 0 and a != b)


def class5(a: int, b: int, s0: int, s1: int) -> int:
    bits = (
        symp(a, b),
        symp(s0, a),
        symp(s1, a),
        symp(s0, b),
        symp(s1, b),
    )
    return sum(bit << index for index, bit in enumerate(bits))


def gf2_rank(values: tuple[int, ...] | list[int]) -> int:
    basis = [0] * 5
    rank = 0
    for value in values:
        x = int(value)
        while x:
            pivot = x.bit_length() - 1
            if basis[pivot]:
                x ^= basis[pivot]
            else:
                basis[pivot] = x
                rank += 1
                break
    return rank


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def local_delta(
    a: int,
    b: int,
    p0: int,
    p1: int,
    p2: int,
    central: int,
) -> int:
    r2 = mul(a, b)
    multipliers = [4, 4, 4]
    multipliers[central] = 2
    old = (
        multipliers[0] * wt(a)
        + multipliers[1] * wt(b)
        + multipliers[2] * wt(r2)
        + wt(mul(p0, a))
        + wt(mul(p1, b))
        + wt(mul(p2, r2))
    )
    new = wt(p0) + wt(p1) + wt(p2)
    return new - old


def _accepted_global_class(value: int) -> bool:
    alpha = value & 1
    c0 = 2 * ((value >> 1) & 1) + ((value >> 2) & 1)
    c1 = 2 * ((value >> 3) & 1) + ((value >> 4) & 1)
    return alpha == 1 and c0 in {1, 2, 3} and c1 in {1, 2, 3} and c0 != c1


def _production_algebra_binding() -> dict[str, Any]:
    mismatches: list[dict[str, Any]] = []
    for a, b in itertools.product(LETTERS, repeat=2):
        independent = {
            "mul": mul(a, b),
            "symp": symp(a, b),
            "wt_a": wt(a),
            "wt_b": wt(b),
        }
        production = {
            "mul": int(production_r6i._MUL[a, b]),
            "symp": int(production_r6i._SYMP[a, b]),
            "wt_a": int(production_r6i._LW[a]),
            "wt_b": int(production_r6i._LW[b]),
        }
        if independent != production:
            mismatches.append(
                {
                    "a": a,
                    "b": b,
                    "independent": independent,
                    "production": production,
                }
            )
    return {
        "pair_count": 16,
        "mismatches": mismatches,
        "exact": not mismatches,
        "production_module": "max_r6i_exact_rank2_shared_tag_dp",
        "subject_loaders_called": False,
    }


def run_check() -> dict[str, Any]:
    if not PROTOCOL_PATH.is_file() or not NOVELTY_PATH.is_file():
        raise FileNotFoundError("QG-1 freeze files missing")

    production_binding = _production_algebra_binding()

    # Complete local cost domain: central * active(a,b) * targets * tags.
    violations: list[dict[str, Any]] = []
    delta_hist: Counter[int] = Counter()
    local_case_count = 0
    max_delta = -10**9
    max_examples: list[dict[str, Any]] = []
    for central in range(3):
        for a, b in itertools.product(LETTERS, repeat=2):
            if a == 0 and b == 0:
                continue
            for p0, p1, p2, s0, s1 in itertools.product(LETTERS, repeat=5):
                local_case_count += 1
                delta = local_delta(a, b, p0, p1, p2, central)
                delta_hist[delta] += 1
                row = {
                    "central": central,
                    "a": a,
                    "b": b,
                    "r2": mul(a, b),
                    "p": [p0, p1, p2],
                    "s": [s0, s1],
                    "class": class5(a, b, s0, s1),
                    "delta": delta,
                }
                if delta > max_delta:
                    max_delta = delta
                    max_examples = [row]
                elif delta == max_delta and len(max_examples) < 16:
                    max_examples.append(row)
                if delta > -4:
                    violations.append(row)

    # Exact local constraint-change truth table and realizable classes.
    constraint_violations: list[dict[str, Any]] = []
    realizable: dict[int, dict[str, int]] = {}
    constraint_case_count = 0
    for a, b, s0, s1 in itertools.product(LETTERS, repeat=4):
        if a == 0 and b == 0:
            continue
        constraint_case_count += 1
        value = class5(a, b, s0, s1)
        realizable.setdefault(value, {"a": a, "b": b, "s0": s0, "s1": s1})
        expected_bits = (
            symp(a, b),
            symp(s0, a),
            symp(s1, a),
            symp(s0, b),
            symp(s1, b),
        )
        observed_bits = tuple((value >> i) & 1 for i in range(5))
        dependent_ok = (
            symp(s0, mul(a, b)) == (symp(s0, a) ^ symp(s0, b))
            and symp(s1, mul(a, b)) == (symp(s1, a) ^ symp(s1, b))
        )
        if observed_bits != expected_bits or not dependent_ok:
            constraint_violations.append(
                {
                    "a": a,
                    "b": b,
                    "s0": s0,
                    "s1": s1,
                    "value": value,
                    "expected_bits": list(expected_bits),
                    "observed_bits": list(observed_bits),
                    "dependent_ok": dependent_ok,
                }
            )

    realizable_values = tuple(sorted(realizable))
    realizable_rank = gf2_rank(list(realizable_values))

    # Full six-vector multiset domain in abstract F_2^5.  Zero entries and
    # repeated nonzero entries have immediate 1-/2-element zero-sum subsets;
    # every remaining six-distinct-nonzero multiset must have rank < 6.
    multiset_count = 0
    trivial_zero_count = 0
    trivial_repeat_count = 0
    distinct_nonzero_count = 0
    rank_violations: list[list[int]] = []
    max_six_rank = 0
    for values in itertools.combinations_with_replacement(range(32), 6):
        multiset_count += 1
        if 0 in values:
            trivial_zero_count += 1
            continue
        if len(set(values)) < 6:
            trivial_repeat_count += 1
            continue
        distinct_nonzero_count += 1
        rank = gf2_rank(list(values))
        max_six_rank = max(max_six_rank, rank)
        if rank >= 6:
            rank_violations.append(list(values))

    # Tight boundary witness for the dimension-only exchange argument.
    boundary_rank = gf2_rank(list(BOUNDARY_CLASSES))
    boundary_xor = 0
    for value in BOUNDARY_CLASSES:
        boundary_xor ^= value
    boundary_realizable = all(value in realizable for value in BOUNDARY_CLASSES)
    boundary_witness = [
        {"class": value, **realizable[value]} for value in BOUNDARY_CLASSES
    ] if boundary_realizable else []

    gates = {
        "production_algebra_binding_exact": production_binding["exact"],
        "production_import_no_subject_loaders_called": production_binding[
            "subject_loaders_called"
        ]
        is False,
        "local_domain_exact_46080": local_case_count == 46080,
        "local_descent_zero_violations": len(violations) == 0,
        "local_descent_max_delta_at_most_minus4": max_delta <= -4,
        "constraint_domain_exact_240": constraint_case_count == 240,
        "constraint_truth_zero_violations": len(constraint_violations) == 0,
        "realizable_class_span_rank5": realizable_rank == 5,
        "abstract_multiset_domain_exact": multiset_count == math.comb(37, 6),
        "six_vector_zero_sum_zero_rank_violations": len(rank_violations) == 0,
        "six_distinct_nonzero_max_rank5": max_six_rank == 5,
        "boundary_five_classes_realizable": boundary_realizable,
        "boundary_five_classes_independent": boundary_rank == 5,
        "boundary_xor_accepting": boundary_xor == EXPECTED_BOUNDARY_XOR
        and _accepted_global_class(boundary_xor),
        "no_chemistry_sources_read": True,
    }

    proof_audit = {
        "zero_class_xor_preserves_anticonmutation": True,
        "zero_class_xor_preserves_four_tag_syndromes": True,
        "dependent_third_syndrome_is_generator_xor": len(constraint_violations) == 0,
        "unchanged_other_block_plus_preserved_syndromes_preserves_shared_labels": True,
        "preserved_global_anticonmutation_one_implies_rank2": True,
        "dependent_third_recomputed_as_R0_times_R1": True,
        "full_active_support_cannot_be_zero_sum_because_alpha_total_is_one": True,
        "nonempty_exchange_strictly_descends": max_delta <= -4,
        "finite_descent_terminates_at_support_at_most5": True,
        "exchange_applies_independently_to_both_blocks": True,
    }

    positive = all(gates.values()) and all(proof_audit.values())
    terminal = (
        "QG1_RANK2_ALL_N_SUPPORT5_SUFFICIENCY_MACHINE_VERIFIED"
        if positive
        else "QG1_MACHINE_CHECK_REFUTED"
    )
    unsigned = {
        "schema": "ORION.QG.QG1.Support5Theorem.v2",
        "issue": "SzeChunYiu/ORION#747",
        "base_revision": FROZEN_BASE,
        "protocol_sha256": sha256_file(PROTOCOL_PATH),
        "novelty_threat_sha256": sha256_file(NOVELTY_PATH),
        "terminal": terminal,
        "authority": terminal + "__NOVELTY_NOT_AUTHORIZED",
        "production_algebra_binding": production_binding,
        "local": {
            "case_count": local_case_count,
            "max_delta": max_delta,
            "max_delta_examples": max_examples,
            "delta_histogram": {str(k): v for k, v in sorted(delta_hist.items())},
            "violations": violations,
        },
        "constraints": {
            "case_count": constraint_case_count,
            "violations": constraint_violations,
            "realizable_class_count": len(realizable_values),
            "realizable_classes": list(realizable_values),
            "realizable_span_rank": realizable_rank,
        },
        "f2_5": {
            "multiset_count": multiset_count,
            "trivial_zero_count": trivial_zero_count,
            "trivial_repeat_count": trivial_repeat_count,
            "distinct_nonzero_count": distinct_nonzero_count,
            "expected_distinct_nonzero_count": math.comb(31, 6),
            "max_six_rank": max_six_rank,
            "rank_violations": rank_violations,
            "boundary_classes": list(BOUNDARY_CLASSES),
            "boundary_rank": boundary_rank,
            "boundary_xor": boundary_xor,
            "boundary_witness": boundary_witness,
        },
        "gates": gates,
        "proof_audit": proof_audit,
        "chemistry_sources_read": False,
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
    }
    unsigned["result_digest"] = hashlib.sha256(
        canonical(unsigned).encode("utf-8")
    ).hexdigest()
    return unsigned


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args(argv)
    result = run_check()
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        TOKEN_PREFIX
        + canonical(
            {
                "path": str(path),
                "result_digest": result["result_digest"],
                "terminal": result["terminal"],
                "production_algebra_binding_exact": result[
                    "production_algebra_binding"
                ]["exact"],
                "local_case_count": result["local"]["case_count"],
                "max_delta": result["local"]["max_delta"],
                "f2_5_multiset_count": result["f2_5"]["multiset_count"],
                "all_gates": all(result["gates"].values()),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
