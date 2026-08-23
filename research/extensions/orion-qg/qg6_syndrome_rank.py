#!/usr/bin/env python3
"""QG-6 automatic conserved-syndrome rank inference from production ORION-Q DPs."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[3]
ORION_Q = REPO_ROOT / "research" / "extensions" / "orion-q"
sys.path.insert(0, str(ORION_Q))

import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402
import max_r6i_exact_rank2_shared_tag_dp as r6i  # noqa: E402
import max_r6m_exact_three_tare2_shared_factor_dp as r6m  # noqa: E402

BASE = "164462bf7c7f3d3c2e559fa5aaf19726bb6ec388"
PROTOCOL_PATH = (
    REPO_ROOT
    / "development"
    / "orion-qg-regime-geometry"
    / "QG6_SYNDROME_DIMENSION_COMPRESSION_PROTOCOL_V1.md"
)
R6S_PATH = ORION_Q / "MAX_R6S_ALL_N_COMPOSITION_RESULTS.json"
DEFAULT_OUTPUT = REPO_ROOT / "artifacts" / "orion-qg-qg6-syndrome-rank.json"
TOKEN_PREFIX = "ORIONQG_QG6_SYNDROME_RANK="


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def gf2_rank(values: Iterable[int]) -> int:
    basis: dict[int, int] = {}
    for raw in values:
        x = int(raw)
        while x:
            pivot = x.bit_length() - 1
            if pivot in basis:
                x ^= basis[pivot]
            else:
                basis[pivot] = x
                break
    return len(basis)


def _base4_code(values: tuple[int, ...]) -> int:
    code = 0
    for value in values:
        code = (code << 2) | int(value)
    return code


def _span_report(changes: set[int], analytic_basis: tuple[int, ...], width: int) -> dict[str, Any]:
    rank = gf2_rank(changes)
    basis_rank = gf2_rank(analytic_basis)
    joint_rank = gf2_rank(tuple(changes) + analytic_basis)
    return {
        "width": width,
        "unique_change_count": len(changes),
        "rank": rank,
        "analytic_basis": list(analytic_basis),
        "analytic_basis_rank": basis_rank,
        "contained_in_analytic_span": joint_rank == basis_rank,
        "spans_analytic_space": joint_rank == rank == basis_rank,
        "change_vectors": sorted(changes),
        "changed_bit_union": [
            bit for bit in range(width) if any((value >> bit) & 1 for value in changes)
        ],
    }


def infer_r6m() -> dict[str, Any]:
    # Each tuple indexes the production _DELTA array directly; no reimplemented
    # transition formula is used in this analyzer lane.
    slot_names = ("A0", "A1", "B0", "B1", "C0", "C1")
    analytic = {
        "A0": (1 << 0, (1 << 3) | (1 << 4) | (1 << 7)),
        "A1": (1 << 0, (1 << 5) | (1 << 6) | (1 << 8)),
        "B0": (1 << 1, 1 << 3),
        "B1": (1 << 1, 1 << 5),
        "C0": (1 << 2, 1 << 4),
        "C1": (1 << 2, 1 << 6),
    }
    changes = {name: set() for name in slot_names}
    rows = 0
    for values in itertools.product(range(4), repeat=7):
        rows += 1
        old = int(r6m._DELTA[_base4_code(values)])
        for slot, name in enumerate(slot_names):
            rewritten = list(values)
            rewritten[slot] = 0
            new = int(r6m._DELTA[_base4_code(tuple(rewritten))])
            changes[name].add(old ^ new)
    reports = {
        name: _span_report(changes[name], analytic[name], 9) for name in slot_names
    }
    return {
        "production_state_bits": 9,
        "local_option_rows": rows,
        "expected_local_option_rows": 4**7,
        "rewrite": "ZERO_ONE_FRAME_LOCAL_LETTER",
        "slots": reports,
        "all_slot_ranks_2": all(item["rank"] == 2 for item in reports.values()),
        "all_analytic_spans_exact": all(item["spans_analytic_space"] for item in reports.values()),
        "auto_dimension": 2 if all(item["rank"] == 2 for item in reports.values()) else None,
    }


def infer_r6i() -> dict[str, Any]:
    analytic = {
        "A": (
            1 << 0,
            (1 << 2) | (1 << 6),
            (1 << 3) | (1 << 7),
            (1 << 4) | (1 << 8),
            (1 << 5) | (1 << 9),
        ),
        "B": (1 << 1, 1 << 2, 1 << 3, 1 << 4, 1 << 5),
    }
    changes = {"A": set(), "B": set()}
    rows = 0
    for values in itertools.product(range(4), repeat=6):
        rows += 1
        old = int(r6i._DELTA[_base4_code(values)])
        rewrite_a = (0, 0, values[2], values[3], values[4], values[5])
        rewrite_b = (values[0], values[1], 0, 0, values[4], values[5])
        changes["A"].add(old ^ int(r6i._DELTA[_base4_code(rewrite_a)]))
        changes["B"].add(old ^ int(r6i._DELTA[_base4_code(rewrite_b)]))
    reports = {
        name: _span_report(changes[name], analytic[name], 10) for name in ("A", "B")
    }
    return {
        "production_state_bits": 10,
        "local_option_rows": rows,
        "expected_local_option_rows": 4**6,
        "rewrite": "ZERO_BOTH_INDEPENDENT_GENERATORS_OF_ONE_BLOCK",
        "blocks": reports,
        "all_block_ranks_5": all(item["rank"] == 5 for item in reports.values()),
        "all_analytic_spans_exact": all(item["spans_analytic_space"] for item in reports.values()),
        "auto_dimension": 5 if all(item["rank"] == 5 for item in reports.values()) else None,
    }


def production_algebra_binding() -> dict[str, Any]:
    mul_ok = all(
        int(r6i._MUL[a, b]) == int(p10.h.local_mul(a, b))
        and int(r6m._LM[a, b]) == int(p10.h.local_mul(a, b))
        for a in range(4)
        for b in range(4)
    )
    symp_ok = all(
        int(r6i._SYMP[a, b]) == int(p10.h.local_symp(a, b))
        and int(r6m._SY[a, b]) == int(p10.h.local_symp(a, b))
        for a in range(4)
        for b in range(4)
    )
    wt_ok = all(
        int(r6i._LW[a]) == int(p10.h.local_wt(a))
        and int(r6m._LW[a]) == int(p10.h.local_wt(a))
        for a in range(4)
    )
    return {
        "multiplication_exact": mul_ok,
        "symplectic_exact": symp_ok,
        "weight_exact": wt_ok,
        "all_exact": mul_ok and symp_ok and wt_ok,
    }


def corroborate_r6i_local_cost() -> dict[str, Any]:
    count = 0
    violations: list[dict[str, Any]] = []
    max_delta = -10**9
    histogram: Counter[int] = Counter()
    for central in range(3):
        mult = [4, 4, 4]
        mult[central] = 2
        for a, b in itertools.product(range(4), repeat=2):
            if a == 0 and b == 0:
                continue
            r2 = int(r6i._MUL[a, b])
            for p0, p1, p2, s0, s1 in itertools.product(range(4), repeat=5):
                count += 1
                old = (
                    mult[0] * int(r6i._LW[a])
                    + mult[1] * int(r6i._LW[b])
                    + mult[2] * int(r6i._LW[r2])
                    + int(r6i._LW[int(r6i._MUL[p0, a])])
                    + int(r6i._LW[int(r6i._MUL[p1, b])])
                    + int(r6i._LW[int(r6i._MUL[p2, r2])])
                )
                new = int(r6i._LW[p0]) + int(r6i._LW[p1]) + int(r6i._LW[p2])
                delta = new - old
                histogram[delta] += 1
                max_delta = max(max_delta, delta)
                if delta > -4:
                    violations.append(
                        {
                            "central": central,
                            "a": a,
                            "b": b,
                            "p": [p0, p1, p2],
                            "s": [s0, s1],
                            "delta": delta,
                        }
                    )
    return {
        "case_count": count,
        "expected_case_count": 46080,
        "max_delta": max_delta,
        "violations": violations,
        "delta_histogram": {str(k): v for k, v in sorted(histogram.items())},
        "candidate_cost_certificate_pass": count == 46080 and max_delta == -4 and not violations,
        "theorem_authority": "PENDING_QG1_INDEPENDENT_DUAL_HARNESS",
    }


def bind_r6s() -> dict[str, Any]:
    raw = json.loads(R6S_PATH.read_text(encoding="utf-8"))
    gates = raw.get("gates", {})
    checks = {
        "authority_machine_checked": str(raw.get("authority", "")).startswith(
            "MAX_R6S_ALL_N_COMPOSITION_THEOREM_MACHINE_CHECKED"
        ),
        "outcome_theorem_machine_checked": raw.get("outcome") == "THEOREM_MACHINE_CHECKED",
        "lemma_e_zero_violations": gates.get("lemma_e_zero_violations") is True,
        "lemma_b_w3_to_w8_zero_failures": gates.get("lemma_b_w3_to_w8_zero_failures") is True,
        "bindings_exact": gates.get("bindings_exact") is True,
        "no_new_subject_data": gates.get("no_new_subject_data") is True,
        "r6_authority_false": raw.get("r6_authority") is False,
        "novelty_credit_false": raw.get("novelty_credit") is False,
    }
    return {
        "receipt_sha256": sha256_file(R6S_PATH),
        "authority": raw.get("authority"),
        "scope": raw.get("scope"),
        "checks": checks,
        "all_bound": all(checks.values()),
        "reported_class_dimension": 2,
        "reported_support_bound": 2,
    }


def abstract_meta_theorem() -> dict[str, Any]:
    # This is a proof-schema ledger, not a machine proof of linear algebra.
    return {
        "field": "F_2",
        "conditions": [
            "ACTIVE_COORDINATES_HAVE_D_DIMENSIONAL_ADDITIVE_SYNDROME",
            "GLOBAL_REQUIRED_SYNDROME_IS_NONZERO",
            "ZERO_SUM_PROPER_SUBSET_DELETION_PRESERVES_SEMANTICS",
            "DELETION_DOES_NOT_INCREASE_COST",
            "TIES_STRICTLY_DECREASE_WELL_FOUNDED_SUPPORT_MEASURE",
        ],
        "proof_steps": [
            "MORE_THAN_D_ACTIVE_VECTORS_ARE_LINEarly_DEPENDENT",
            "DEPENDENCE_GIVES_NONEMPTY_ZERO_SUM_SUBSET",
            "NONZERO_TOTAL_SYNDROME_MAKES_SUBSET_PROPER",
            "ADMITTED_DELETION_CONTRADICTS_SUPPORT_MINIMAL_OPTIMUM",
        ],
        "support_bound": "d",
        "novelty_credit": False,
    }


def run() -> dict[str, Any]:
    if not PROTOCOL_PATH.is_file():
        raise FileNotFoundError(PROTOCOL_PATH)
    binding = production_algebra_binding()
    r6m_rank = infer_r6m()
    r6i_rank = infer_r6i()
    r6i_cost = corroborate_r6i_local_cost()
    r6s = bind_r6s()

    gates = {
        "production_algebra_exact": binding["all_exact"],
        "r6m_domain_exact": r6m_rank["local_option_rows"] == r6m_rank["expected_local_option_rows"],
        "r6m_auto_rank2": r6m_rank["all_slot_ranks_2"],
        "r6m_analytic_span_exact": r6m_rank["all_analytic_spans_exact"],
        "r6s_theorem_receipt_bound": r6s["all_bound"],
        "r6i_domain_exact": r6i_rank["local_option_rows"] == r6i_rank["expected_local_option_rows"],
        "r6i_auto_rank5": r6i_rank["all_block_ranks_5"],
        "r6i_analytic_span_exact": r6i_rank["all_analytic_spans_exact"],
        "r6i_local_cost_candidate_pass": r6i_cost["candidate_cost_certificate_pass"],
        "no_chemistry_or_protected_subject_read": True,
    }
    positive = all(gates.values())
    terminal = (
        "QG6_PRODUCTION_SYNDROME_RANK_INFERENCE_VERIFIED__R6M_D2_RECOVERS_SUPPORT2__R6I_D5_FOUND_THEOREM_PENDING_QG1"
        if positive
        else "QG6_PRODUCTION_RANK_OR_BINDING_REFUTED"
    )
    result: dict[str, Any] = {
        "schema": "ORION.QG.QG6.SyndromeRank.v1",
        "issue": "SzeChunYiu/ORION#756",
        "base_revision": BASE,
        "protocol_sha256": sha256_file(PROTOCOL_PATH),
        "terminal": terminal,
        "production_algebra": binding,
        "r6m": {
            **r6m_rank,
            "r6s_binding": r6s,
            "support_theorem_status": (
                "RECOVERED_FROM_EXISTING_R6S_CERTIFICATE" if r6s["all_bound"] else "CANNOT_CHECK"
            ),
        },
        "r6i": {
            **r6i_rank,
            "local_cost_corroboration": r6i_cost,
            "support_theorem_status": "PENDING_QG1_INDEPENDENT_DUAL_HARNESS",
        },
        "meta_theorem": abstract_meta_theorem(),
        "search_complexity_corollary": {
            "formula": "sum_{k=0}^d binom(n,k) A^k",
            "fixed_d_asymptotic": "O(n^d A^d)",
            "scope": "CERTIFIED_COMPONENT_ONLY",
        },
        "gates": gates,
        "chemistry_sources_read": False,
        "protected_subject_read": False,
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
    }
    unsigned = canonical(result)
    result["result_digest"] = hashlib.sha256(unsigned.encode("utf-8")).hexdigest()
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args(argv)
    result = run()
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        TOKEN_PREFIX
        + canonical(
            {
                "path": str(out),
                "terminal": result["terminal"],
                "result_digest": result["result_digest"],
                "r6m_d": result["r6m"]["auto_dimension"],
                "r6i_d": result["r6i"]["auto_dimension"],
                "all_gates": all(result["gates"].values()),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
