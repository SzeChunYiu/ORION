#!/usr/bin/env python3
"""QG-20: complete n=1/n=2 SixLCU census under O20=2*SELECT+PREP+WIDTH.

Independent of Q3 instrument files. Tests the original QG12 P0 predicate unchanged
against exact reweighted incumbent labels on the frozen complete domains.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
QG_DIR = REPO_ROOT / "research" / "extensions" / "orion-qg"
sys.path.insert(0, str(QG_DIR))

import qg4_second_family as qg4  # noqa: E402

BASE = "c5ba39fef4f25c46de5fb69bf07f50530f4693ca"
PROTOCOL = REPO_ROOT / "development/orion-qg-regime-geometry/QG20_SIXLCU_OBJECTIVE_SCOPE_PROTOCOL_V1.md"
DEFAULT_OUTPUT = REPO_ROOT / "artifacts/orion-qg-qg20-sixlcu-objective-scope.json"
W_SELECT = 2
W_PREP = 1
W_WIDTH = 1
MISMATCH_CAP = 50


def canonical(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reweighted_from_rec(codes, n: int, rec: dict[str, Any]) -> dict[str, Any]:
    W = int(rec["W"])
    wF = rec["wF"]
    sw = rec["sw"]
    best = qg4.INF
    bestidx = -1
    for idx, static in enumerate(qg4.PSTAT):
        select = 0
        for mask, A, B in static["coeffs"]:
            select += int(A) * int(wF[mask]) + int(B) * int(sw[mask])
        cost = W_SELECT * select + W_PREP * int(static["prep"]) + W_WIDTH * int(static["width_shared"])
        if cost < best:
            best = cost
            bestidx = idx
    c_u = 4 * W + 15
    c_b = 8 * W + 14
    if not c_u < c_b:
        raise AssertionError({"o20_unary_not_incumbent": [list(codes), n, W, c_u, c_b]})
    p0 = bool(rec["P"][0])
    label = int(best) == int(c_u)
    return {
        "P0": p0,
        "incumbent_exact_O20": label,
        "C_F_O20": int(best),
        "C_U_O20": int(c_u),
        "C_B_O20": int(c_b),
        "best_partition_index_O20": int(bestidx),
        "W": W,
    }


def direct_member_min(codes, n: int) -> int:
    best = qg4.INF
    for part in qg4.PARTITIONS:
        phi = (1,) * len(part)
        sel, prep, width = qg4.member_components(codes, n, part, phi, True)
        value = W_SELECT * int(sel) + W_PREP * int(prep) + W_WIDTH * int(width)
        if value < best:
            best = value
    return int(best)


def run() -> dict[str, Any]:
    if not PROTOCOL.is_file():
        raise FileNotFoundError(PROTOCOL)
    source_text = Path(__file__).read_text(encoding="utf-8")
    if "Q-paper-03" in source_text or "LANE_A" in source_text or "LANE_B" in source_text:
        raise AssertionError("QG20 analyzer contains Q3 dependency")

    mismatch_count = 0
    false_positive = 0  # P0 true, O20 label false
    false_negative = 0  # P0 false, O20 label true
    mismatch_rows: list[dict[str, Any]] = []
    digest = hashlib.sha256()
    counts = {"n1": 0, "n2": 0, "n1_p0": 0, "n2_p0": 0, "n1_label": 0, "n2_label": 0}
    direct_checks = 0

    def consume(codes, n: int, index: int) -> None:
        nonlocal mismatch_count, false_positive, false_negative, direct_checks
        rec = qg4.eval_instance(codes, n)
        rw = reweighted_from_rec(codes, n, rec)
        key = f"n{n}"
        counts[key] += 1
        counts[f"{key}_p0"] += int(rw["P0"])
        counts[f"{key}_label"] += int(rw["incumbent_exact_O20"])
        digest.update(canonical([n, list(codes), rw]).encode())
        mismatch = rw["P0"] != rw["incumbent_exact_O20"]
        if mismatch:
            mismatch_count += 1
            false_positive += int(rw["P0"] and not rw["incumbent_exact_O20"])
            false_negative += int((not rw["P0"]) and rw["incumbent_exact_O20"])
            if len(mismatch_rows) < MISMATCH_CAP:
                mismatch_rows.append({"n": n, "index": index, "codes": list(codes), **rw})
        # Different implementation path: direct member_components over all 203 partitions.
        if (n == 1 and index % 97 == 0) or (n == 2 and index % 2500 == 0):
            direct = direct_member_min(codes, n)
            direct_checks += 1
            if direct != rw["C_F_O20"]:
                raise AssertionError({"o20_direct_member_mismatch": [n, index, direct, rw["C_F_O20"]]})

    for i, codes in enumerate(itertools.product((1, 2, 3), repeat=6)):
        consume(codes, 1, i)
    for i, codes in enumerate(itertools.combinations_with_replacement(range(1, 16), 6)):
        consume(codes, 2, i)

    if counts["n1"] != 729 or counts["n2"] != 38760:
        raise AssertionError({"domain_count_drift": counts})

    terminal = (
        "QG20_P0_REWEIGHTED_BOUNDARY_REFUTED"
        if mismatch_count else "QG20_P0_ZERO_MISMATCH_ON_COMPLETE_N1_N2"
    )
    result: dict[str, Any] = {
        "schema": "ORION.QG.QG20.SixLCUObjectiveScope.v1",
        "base_revision": BASE,
        "protocol_sha256": sha256_file(PROTOCOL),
        "objective": {"SELECT": W_SELECT, "PREP": W_PREP, "WIDTH": W_WIDTH},
        "domain": {"n1": counts["n1"], "n2": counts["n2"], "total": counts["n1"] + counts["n2"]},
        "boundary_counts": counts,
        "mismatch_count": mismatch_count,
        "p0_true_label_false": false_positive,
        "p0_false_label_true": false_negative,
        "first_mismatches": mismatch_rows,
        "enumeration_digest": digest.hexdigest(),
        "direct_member_crosscheck_rows": direct_checks,
        "gates": {
            "domain_exact_729_38760": counts["n1"] == 729 and counts["n2"] == 38760,
            "unary_incumbent_remains_incumbent": True,
            "direct_member_crosschecks_pass": True,
            "no_q3_import": True,
        },
        "terminal": terminal,
        "authority": "COMPLETE_FROZEN_N1_N2_DOMAIN_ONLY__NO_ALL_N_WEIGHTED_THEOREM__NOT_R6",
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
    }
    result["result_digest"] = hashlib.sha256(canonical(result).encode()).hexdigest()
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    ns = ap.parse_args()
    result = run()
    ns.output.parent.mkdir(parents=True, exist_ok=True)
    ns.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(canonical(result))


if __name__ == "__main__":
    main()
