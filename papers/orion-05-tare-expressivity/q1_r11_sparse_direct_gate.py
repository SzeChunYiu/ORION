#!/usr/bin/env python3
"""Hostile executable gate for the ORION-05 R11 sparse-direct theorem candidate.

The candidate solver is imported from the paper directory and is source-audited
for dependency isolation.  This harness alone imports the frozen R6M DP as an
oracle on the protocol-specified hostile panels.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import itertools
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
Q = ROOT / "research/extensions/orion-q"
QG = ROOT / "research/extensions/orion-qg"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(Q))

import q1_r11_sparse_direct_solver as sparse_solver  # noqa: E402
import max_r6m_exact_three_tare2_shared_factor_dp as r6m  # noqa: E402

PROTOCOL = HERE / "Q1_R11_SPARSE_DIRECT_EXECUTABLE_PROTOCOL_V1.md"
PAIR_CHECK = HERE / "q1_r11_pair_count_independent.py"
SOLVER = HERE / "q1_r11_sparse_direct_solver.py"
QG7 = QG / "QG7_BPRIME_COMPLETENESS_RESULTS.json"
TERMINAL_PASS = "Q1_R11_EXACT_O_N9_DIRECT_SOLVER_THEOREM"
TERMINAL_COUNTEREXAMPLE = "Q1_R11_RUNTIME_THEOREM_COUNTEREXAMPLE"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def source_isolation_gate() -> dict:
    source = SOLVER.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    forbidden_modules = [
        name
        for name in imported
        if name.startswith("orion")
        or "max_r6m" in name
        or "max_r6p" in name
        or "max_r6o" in name
    ]
    forbidden_text = {
        "global_4_pow_n_tag_sweep": "product(range(4), repeat=n)" in source.replace(" ", ""),
        "pattern_table_4_pow_2n": "4**(2*n)" in source.replace(" ", ""),
        "historical_dp_symbol": "exact_r6m_matching(" in source,
    }
    return {
        "imports": imported,
        "forbidden_modules": forbidden_modules,
        "forbidden_text": forbidden_text,
        "pass": not forbidden_modules and not any(forbidden_text.values()),
    }


def run_pair_checker() -> dict:
    proc = subprocess.run(
        [sys.executable, str(PAIR_CHECK)],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    return {
        "returncode": proc.returncode,
        "terminal_present": "Q1_R11_INDEPENDENT_FINITE_CHECK_PASS" in proc.stdout,
        "stdout_sha256": hashlib.sha256(proc.stdout.encode()).hexdigest(),
        "stdout_tail": proc.stdout[-2000:],
        "pass": proc.returncode == 0 and "Q1_R11_INDEPENDENT_FINITE_CHECK_PASS" in proc.stdout,
    }


# Independent one-qubit brute grammar: full 4^7 local option enumeration is
# prefiltered once, then every one of the 729 target sextuples is scored.
LETTER_BITS = sparse_solver.LETTER_BITS
NONZERO = sparse_solver.NONZERO


def sy(a: int, b: int) -> int:
    return sparse_solver.local_symp(a, b)


def mul(a: int, b: int) -> int:
    return sparse_solver.local_mul(a, b)


def f3(a: int, b: int, c: int) -> int:
    return sparse_solver.f3(a, b, c)


def feasible_n1_options():
    rows = []
    for option in itertools.product(range(4), repeat=7):
        ra0, ra1, rb0, rb1, rc0, rc1, tag = option
        if not (sy(ra0, ra1) and sy(rb0, rb1) and sy(rc0, rc1)):
            continue
        labels = (sy(tag, ra0), sy(tag, ra1))
        if labels[0] == labels[1]:
            continue
        if (sy(tag, rb0), sy(tag, rb1)) != labels:
            continue
        if (sy(tag, rc0), sy(tag, rc1)) != labels:
            continue
        rows.append((option, 2 * int(tag != 0)))
    if not rows:
        raise AssertionError("n1 brute option set empty")
    return tuple(rows)


N1_OPTIONS = feasible_n1_options()


def brute_n1_cost(targets: tuple[int, ...]) -> int:
    best = sparse_solver.INF
    for option, tag_cost in N1_OPTIONS:
        ra0, ra1, rb0, rb1, rc0, rc1, _tag = option
        frames = (ra0, ra1, rb0, rb1, rc0, rc1)
        for perm_b, perm_c in itertools.product((0, 1), repeat=2):
            ordered = (
                targets[0], targets[1],
                targets[2 + perm_b], targets[3 - perm_b],
                targets[4 + perm_c], targets[5 - perm_c],
            )
            cost = tag_cost
            for k in (0, 1):
                cost += f3(
                    mul(ordered[k], frames[k]),
                    mul(ordered[2 + k], frames[2 + k]),
                    mul(ordered[4 + k], frames[4 + k]),
                )
            if cost < best:
                best = cost
    return int(best)


def local_letter_global(letter: int) -> tuple[int, int]:
    x, z = LETTER_BITS[letter]
    return x, z


def sextuple_to_pairs(targets: tuple[int, ...]):
    keys = tuple(local_letter_global(letter) for letter in targets)
    return ((keys[0], keys[1]), (keys[2], keys[3]), (keys[4], keys[5]))


def complete_n1_gate() -> dict:
    mismatches = []
    count = 0
    start = time.perf_counter()
    max_wall = 0.0
    max_active = 0
    support2_improvements = 0
    for targets in itertools.product(NONZERO, repeat=6):
        pairs = sextuple_to_pairs(tuple(targets))
        result = sparse_solver.solve(pairs, 1)
        brute = brute_n1_cost(tuple(targets))
        count += 1
        max_wall = max(max_wall, float(result["stats"]["wall_seconds"]))
        max_active = max(max_active, int(result["stats"]["support2"]["max_active_union"]))
        support2_improvements += int(result["strict_support2_improvement"])
        if result["C_sparse"] != brute or not all(result["witness"]["checks"].values()):
            mismatches.append({
                "targets": list(targets),
                "sparse": result["C_sparse"],
                "brute": brute,
                "checks": result["witness"]["checks"],
            })
            if len(mismatches) >= 10:
                break
    return {
        "denominator": count,
        "expected_denominator": 729,
        "mismatches": mismatches,
        "max_single_solve_seconds": max_wall,
        "max_active_union": max_active,
        "strict_support2_improvements": support2_improvements,
        "wall_seconds": time.perf_counter() - start,
        "pass": count == 729 and not mismatches,
    }


def to_global_n1_panel(letter_pairs):
    key = {"X": (1, 0), "Z": (0, 1), "Y": (1, 1)}
    return tuple((key[a], key[b]) for a, b in letter_pairs)


def dp_cost(target_pairs, n: int):
    terms = r6m._synthetic_terms(tuple((tuple(a), tuple(b)) for a, b in target_pairs))
    witness = r6m.exact_r6m_matching(terms, r6m._SYNTHETIC_MATCHING, n, list(range(6)))
    if not all(witness.get("checks", {}).values()):
        raise AssertionError({"dp_witness_checks": witness.get("checks")})
    return int(witness["C_R6M"]), witness


def frozen_dp_panels_gate() -> dict:
    rows = []
    for name, letter_pairs in r6m._HOSTILE_N1_PANELS.items():
        target_pairs = to_global_n1_panel(letter_pairs)
        sparse = sparse_solver.solve(target_pairs, 1)
        dp, _ = dp_cost(target_pairs, 1)
        rows.append({
            "id": name,
            "n": 1,
            "sparse": sparse["C_sparse"],
            "dp": dp,
            "support1": sparse["support1_incumbent"],
            "max_frame_support": max(max(b["support"]) for b in sparse["witness"]["blocks"]),
            "wall_seconds": sparse["stats"]["wall_seconds"],
            "pass": sparse["C_sparse"] == dp and all(sparse["witness"]["checks"].values()),
        })
    for name, target_pairs in r6m._HOSTILE_N2_PANELS.items():
        target_pairs = tuple((tuple(a), tuple(b)) for a, b in target_pairs)
        sparse = sparse_solver.solve(target_pairs, 2)
        dp, _ = dp_cost(target_pairs, 2)
        rows.append({
            "id": name,
            "n": 2,
            "sparse": sparse["C_sparse"],
            "dp": dp,
            "support1": sparse["support1_incumbent"],
            "max_frame_support": max(max(b["support"]) for b in sparse["witness"]["blocks"]),
            "wall_seconds": sparse["stats"]["wall_seconds"],
            "pass": sparse["C_sparse"] == dp and all(sparse["witness"]["checks"].values()),
        })
    return {"rows": rows, "pass": all(row["pass"] for row in rows)}


def qg7_support2_gate() -> dict:
    qg7 = json.loads(QG7.read_text(encoding="utf-8"))
    candidates = qg7["arm1_hostile_search"]["fourth_regime_candidates_verbatim"]
    selected = []
    for local_index in (2, 5):
        row = next(r for r in candidates if r.get("panel") == "H1_n3" and r.get("local_index") == local_index)
        target_pairs = tuple((tuple(a), tuple(b)) for a, b in row["target_pairs"])
        sparse = sparse_solver.solve(target_pairs, 3)
        dp, _ = dp_cost(target_pairs, 3)
        selected.append({
            "panel": row["panel"],
            "local_index": local_index,
            "recorded_C_DP": row["C_DP"],
            "recorded_C_Dplus": row["C_Dplus"],
            "recorded_C_Dxx": row["C_Dxx"],
            "sparse": sparse["C_sparse"],
            "support1": sparse["support1_incumbent"],
            "dp_replay": dp,
            "strict_support2_improvement": sparse["strict_support2_improvement"],
            "max_frame_support": max(max(b["support"]) for b in sparse["witness"]["blocks"]),
            "stats": sparse["stats"],
            "witness": sparse["witness"],
            "pass": (
                sparse["C_sparse"] == dp == int(row["C_DP"])
                and sparse["support1_incumbent"] > sparse["C_sparse"]
                and sparse["strict_support2_improvement"] is True
                and all(sparse["witness"]["checks"].values())
            ),
        })
    return {"rows": selected, "pass": all(row["pass"] for row in selected)}


def pair_generation_gate() -> dict:
    rows = []
    expected = [6, 120, 666, 1968, 4350, 8136]
    for n, expected_count in enumerate(expected, 1):
        pairs = sparse_solver.generate_pairs(n)
        rows.append({
            "n": n,
            "count": len(pairs),
            "expected": expected_count,
            "max_pair_union": max(len(pair.active) for pair in pairs),
            "all_anticommuting": all(sparse_solver.sp_symp(pair.r0, pair.r1) == 1 for pair in pairs),
            "all_support_le_2": all(1 <= sparse_solver.sp_wt(frame) <= 2 for pair in pairs for frame in (pair.r0, pair.r1)),
        })
    return {"rows": rows, "pass": all(row["count"] == row["expected"] and row["max_pair_union"] <= 3 and row["all_anticommuting"] and row["all_support_le_2"] for row in rows)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    source_gate = source_isolation_gate()
    pair_checker = run_pair_checker()
    generated_pairs = pair_generation_gate()
    n1 = complete_n1_gate()
    dp_panels = frozen_dp_panels_gate()
    qg7 = qg7_support2_gate()

    gates = {
        "protocol_exists": PROTOCOL.is_file(),
        "source_isolation": source_gate["pass"],
        "independent_pair_checker": pair_checker["pass"],
        "constructive_pair_generation": generated_pairs["pass"],
        "complete_n1_729": n1["pass"],
        "frozen_dp_n1_n2_panels": dp_panels["pass"],
        "qg7_support2_rows": qg7["pass"],
    }
    positive = all(gates.values())
    result = {
        "schema": "ORION.Q1.R11.SparseDirectExecutableGate.v1",
        "date": "2026-08-27",
        "terminal": TERMINAL_PASS if positive else TERMINAL_COUNTEREXAMPLE,
        "protocol_sha256": sha256(PROTOCOL),
        "solver_sha256": sha256(SOLVER),
        "pair_checker_sha256": sha256(PAIR_CHECK),
        "qg7_sha256": sha256(QG7),
        "gates": gates,
        "source_isolation": source_gate,
        "independent_pair_checker": pair_checker,
        "pair_generation": generated_pairs,
        "complete_n1": n1,
        "frozen_dp_panels": dp_panels,
        "qg7_support2": qg7,
        "authority": {
            "algorithmic_theorem": positive,
            "scope": "frozen R6M six-slot grammar and declared objective only",
            "production_runtime_value": False,
            "physical_quantum_resource_authority": False,
            "novelty_authority": False,
            "submission_authority": False,
        },
    }
    result["result_digest"] = hashlib.sha256(canonical(result).encode()).hexdigest()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(canonical({"terminal": result["terminal"], "gates": gates, "result_digest": result["result_digest"]}))
    return 0 if positive else 1


if __name__ == "__main__":
    raise SystemExit(main())
