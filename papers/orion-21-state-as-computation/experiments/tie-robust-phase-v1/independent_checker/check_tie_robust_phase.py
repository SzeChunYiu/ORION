#!/usr/bin/env python3
"""Independent transcript checker for ORION21.TIE_ROBUST_PHASE.v1.

This checker deliberately does not import the runner or any generator code. It treats the
emitted label/prediction bitstreams as the measurement record, recomputes every candidate
correct count, exact min/max curve, crossing interval, and registered endpoint verdict,
and verifies that the reported equality classes are completely enumerated.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

TAU_NUM = 19
TAU_DEN = 20


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        obj = json.load(fh)
    if not isinstance(obj, dict):
        raise RuntimeError(f"{path}: expected object")
    return obj


def resolve_file(ref: str, result_dir: Path) -> Path:
    path = Path(ref)
    if path.is_absolute():
        return path
    # Runner may be invoked with a relative output directory from another cwd.
    candidates = [result_dir / path, Path.cwd() / path]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def read_bits(meta: dict[str, Any], result_dir: Path) -> np.ndarray:
    path = resolve_file(str(meta["path"]), result_dir)
    encoded = path.read_text(encoding="ascii").strip()
    raw = base64.b64decode(encoded, validate=True)
    digest = hashlib.sha256(raw).hexdigest()
    if digest != meta["packed_sha256"]:
        raise RuntimeError(f"digest mismatch: {path}")
    bits = np.unpackbits(np.frombuffer(raw, dtype=np.uint8), bitorder="little")
    return bits[: int(meta["bit_count"])].astype(np.uint8)


def ranks(values: list[float]) -> list[float]:
    indexed = sorted(enumerate(values), key=lambda x: x[1])
    out = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i + 1
        while j < len(indexed) and indexed[j][1] == indexed[i][1]:
            j += 1
        avg = (i + 1 + j) / 2.0
        for k in range(i, j):
            out[indexed[k][0]] = avg
        i = j
    return out


def spearman(x: list[float], y: list[float]) -> float:
    rx, ry = ranks(x), ranks(y)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry, strict=True))
    dx = math.sqrt(sum((a - mx) ** 2 for a in rx))
    dy = math.sqrt(sum((b - my) ** 2 for b in ry))
    return 0.0 if dx == 0 or dy == 0 else num / (dx * dy)


def n_screen(p: int) -> float:
    return (1.0 + math.sqrt(2.0 * math.log(p))) ** 2 / 0.25


def evaluate(cells: list[dict[str, Any]], key: str) -> dict[str, Any]:
    vals = [(int(c["bank_width_p"]), c[key]) for c in cells]
    if any(n is None for _, n in vals):
        return {"verdict": "C4_INDETERMINATE", "reason": "RIGHT_CENSORED"}
    rows = sorted((p, int(n)) for p, n in vals)
    pvals = [p for p, _ in rows]
    nvals = [n for _, n in rows]
    rel = [abs(n - n_screen(p)) / n_screen(p) for p, n in rows]
    within = sum(v <= 0.25 for v in rel)
    bad = sum(v > 0.25 for v in rel)
    nondecreasing = all(a <= b for a, b in zip(nvals, nvals[1:]))
    rho = spearman([math.log(p) for p in pvals], [float(n) for n in nvals])
    extreme = nvals[pvals.index(42504)] <= nvals[pvals.index(91)] if 91 in pvals and 42504 in pvals else False
    grows = nondecreasing and any(a < b for a, b in zip(nvals, nvals[1:]))
    if within >= 8 and nondecreasing:
        verdict = "C1_LAW_CONFIRMED_REGIME_EXTENDED"
    elif rho <= 0 or extreme:
        verdict = "C2_LAW_FALSIFIED_FLAT"
    elif grows and bad >= 5:
        verdict = "C3_LAW_FALSIFIED_SCALE"
    else:
        verdict = "C4_INDETERMINATE"
    return {
        "verdict": verdict,
        "within_25pct_count": within,
        "outside_25pct_count": bad,
        "nondecreasing_in_p": nondecreasing,
        "spearman_ncross_ln_p": rho,
        "extreme_flat_condition": extreme,
    }


def first_cross(sizes: list[int], nums: list[int], den: int) -> int | None:
    for n, num in zip(sizes, nums, strict=True):
        if TAU_DEN * num >= TAU_NUM * den:
            return n
    return None


def expected_supports(boundary: dict[str, Any]) -> set[tuple[int, ...]]:
    fixed = tuple(int(x) for x in boundary["fixed_above_boundary"])
    tied = tuple(int(x) for x in boundary["boundary_tied"])
    need = int(boundary["need_from_boundary"])
    return {tuple(sorted(fixed + choice)) for choice in itertools.combinations(tied, need)}


def check(result_path: Path, protocol_path: Path, expected_path: Path) -> dict[str, Any]:
    result = load_json(result_path)
    protocol = load_json(protocol_path)
    expected = load_json(expected_path)
    if result.get("terminal") == "T4_CANNOT_CHECK_GENERATOR_UNDERSPECIFIED":
        return {"status": "CANNOT_CHECK", "terminal": result["terminal"], "runner_error": result.get("error")}
    if result.get("protocol_identity") != protocol.get("protocol_identity") or protocol.get("protocol_identity") != expected.get("protocol_identity"):
        raise RuntimeError("protocol identity mismatch")
    sizes = [int(n) for n in protocol["ladder"]["train_sizes"]]
    seeds = [int(s) for s in protocol["ladder"]["seeds"]]
    n_queries = int(protocol["ladder"]["n_queries"])
    n_test = int(protocol["ladder"]["n_test"])
    result_dir = result_path.parent

    checked_cells: list[dict[str, Any]] = []
    separable_count = 0
    tied_count = 0
    candidate_streams = 0

    for cell in result["ladder"]["cells"]:
        if [int(x) for x in cell["cell"]] != [int(x) for x in protocol["ladder"]["cells"][int(cell["cell_index"])]]:
            raise RuntimeError("cell order mismatch")
        seed_rows = cell["seed_rows"]
        if [int(r["seed"]) for r in seed_rows] != seeds:
            raise RuntimeError("seed order mismatch")
        den_seed = n_queries * n_test
        den_mean = den_seed * len(seeds)
        min_curve, max_curve = [], []
        for size_index, n in enumerate(sizes):
            total_min = 0
            total_max = 0
            for seed_row in seed_rows:
                srow = seed_row["sizes"][size_index]
                if int(srow["train_size"]) != n:
                    raise RuntimeError("size order mismatch")
                seed_min = 0
                seed_max = 0
                if len(srow["queries"]) != n_queries:
                    raise RuntimeError("query count mismatch")
                for qrow in srow["queries"]:
                    labels = read_bits(qrow["label_bits"], result_dir)
                    if len(labels) != n_test:
                        raise RuntimeError("label length mismatch")
                    exp_supports = expected_supports(qrow["boundary"])
                    got_supports = {tuple(int(x) for x in c["support_feature_indices"]) for c in qrow["candidates"]}
                    if got_supports != exp_supports:
                        raise RuntimeError("candidate support class incomplete or extra")
                    if int(qrow["boundary"]["candidate_count"]) != len(exp_supports):
                        raise RuntimeError("candidate count mismatch")
                    if len(exp_supports) == 1:
                        separable_count += 1
                        if not qrow["boundary"]["rank_gap_separable"]:
                            raise RuntimeError("singleton class not marked separable")
                    else:
                        tied_count += 1
                        if qrow["boundary"]["rank_gap_separable"]:
                            raise RuntimeError("multi-support class marked separable")
                    counts = []
                    for cand in qrow["candidates"]:
                        pred = read_bits(cand["prediction_bits"], result_dir)
                        if len(pred) != n_test:
                            raise RuntimeError("prediction length mismatch")
                        counts.append(int(np.count_nonzero(pred == labels)))
                        candidate_streams += 1
                    qmin, qmax = min(counts), max(counts)
                    if int(qrow["min_correct"]) != qmin or int(qrow["max_correct"]) != qmax:
                        raise RuntimeError("runner query bound mismatch")
                    seed_min += qmin
                    seed_max += qmax
                if int(srow["seed_min_correct"]) != seed_min or int(srow["seed_max_correct"]) != seed_max:
                    raise RuntimeError("runner seed bound mismatch")
                total_min += seed_min
                total_max += seed_max
            min_curve.append(total_min)
            max_curve.append(total_max)
        n_lo = first_cross(sizes, max_curve, den_mean)
        n_hi = first_cross(sizes, min_curve, den_mean)
        if cell["n_cross_lo"] != n_lo or cell["n_cross_hi"] != n_hi:
            raise RuntimeError("runner n_cross mismatch")
        if bool(cell["identified"]) != (n_lo == n_hi):
            raise RuntimeError("runner identification mismatch")
        checked_cells.append({
            "bank_width_p": int(cell["bank_width_p"]),
            "n_cross_lo": n_lo,
            "n_cross_hi": n_hi,
            "identified": n_lo == n_hi,
        })

    lo = evaluate(checked_cells, "n_cross_lo")
    hi = evaluate(checked_cells, "n_cross_hi")
    all_identified = all(c["identified"] for c in checked_cells)
    terminal = (
        "T1_TIE_ROBUST" if all_identified
        else "T2_TIE_AMBIGUOUS_VERDICT_INVARIANT" if lo["verdict"] == hi["verdict"]
        else "T3_TIE_AMBIGUOUS_VERDICT_CHANGING"
    )
    if result["terminal"] != terminal:
        raise RuntimeError(f"terminal mismatch: runner={result['terminal']} checker={terminal}")
    if result["ladder"]["endpoint_verdict_lo"]["verdict"] != lo["verdict"]:
        raise RuntimeError("low endpoint verdict mismatch")
    if result["ladder"]["endpoint_verdict_hi"]["verdict"] != hi["verdict"]:
        raise RuntimeError("high endpoint verdict mismatch")
    if not result["control"]["synthetic_no_tie"]["passed"] or int(result["control"]["separable_gap_failures"]) != 0:
        raise RuntimeError("runner control failed")

    return {
        "status": "PASS",
        "protocol_identity": protocol["protocol_identity"],
        "terminal": terminal,
        "endpoint_verdict_lo": lo,
        "endpoint_verdict_hi": hi,
        "all_n_cross_point_identified": all_identified,
        "separable_query_points_checked": separable_count,
        "tied_query_points_checked": tied_count,
        "candidate_prediction_streams_checked": candidate_streams,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("result", type=Path)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--expected", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = check(args.result, args.protocol, args.expected)
    except Exception as exc:
        print(json.dumps({"status": "RED", "error": f"{type(exc).__name__}: {exc}"}, indent=2, sort_keys=True))
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 3 if report["status"] == "CANNOT_CHECK" else 0


if __name__ == "__main__":
    raise SystemExit(main())
