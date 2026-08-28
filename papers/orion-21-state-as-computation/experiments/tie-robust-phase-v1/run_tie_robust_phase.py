#!/usr/bin/env python3
"""Prospective set-valued reconstruction for ORION21.TIE_ROBUST_PHASE.v1.

This file is an engineering implementation of the already-frozen protocol. It does not
change the protocol, run automatically, or grant scientific authority. The scientific
run is required to execute on the registered LUNARC host class.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import itertools
import json
import math
from pathlib import Path
import resource
import time
from typing import Any, Iterable

import numpy as np

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PROTOCOL.json"
EXPECTED = HERE / "EXPECTED_TERMINALS.json"
TAU = 0.95


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        obj = json.load(fh)
    if not isinstance(obj, dict):
        raise RuntimeError(f"{path}: expected object")
    return obj


def bank(x: np.ndarray, subsets: list[tuple[int, ...]]) -> np.ndarray:
    idx = np.asarray(subsets, dtype=np.int16)
    return np.prod(x[:, idx], axis=2, dtype=np.int8)


def rung_stream(seed: int, cell: tuple[int, int, int]) -> np.random.Generator:
    return np.random.default_rng([seed, 0, *cell])


def bit_payload(bits: np.ndarray) -> tuple[bytes, str]:
    arr = np.asarray(bits, dtype=np.uint8)
    raw = np.packbits(arr, bitorder="little").tobytes()
    return raw, hashlib.sha256(raw).hexdigest()


def write_bits(bits: np.ndarray, path: Path, *, record_path: str) -> dict[str, Any]:
    raw, digest = bit_payload(bits)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Base64 keeps the transcript portable through text-only tooling.
    path.write_text(base64.b64encode(raw).decode("ascii") + "\n", encoding="ascii")
    return {
        "path": record_path,
        "encoding": "numpy.packbits/little+base64-file",
        "bit_count": int(np.asarray(bits).size),
        "packed_sha256": digest,
    }


def enumerate_supports(corr: np.ndarray, r: int) -> tuple[list[tuple[int, ...]], dict[str, Any]]:
    """Enumerate the exact top-r equality class from integer correlations.

    Zero correlations are allowed. Their sign is exactly zero in the downstream linear
    score, matching numpy.sign; no tolerance or invented secondary scientific rule is
    introduced. The prospectively registered ascending-index key is used only to name
    the canonical member.
    """
    corr = np.asarray(corr, dtype=np.int64)
    abs_corr = np.abs(corr)
    order = sorted(range(len(corr)), key=lambda i: (-int(abs_corr[i]), i))
    if not 0 < r <= len(order):
        raise RuntimeError("invalid r")
    boundary = int(abs_corr[order[r - 1]])
    fixed = tuple(sorted(i for i in range(len(corr)) if int(abs_corr[i]) > boundary))
    tied = tuple(sorted(i for i in range(len(corr)) if int(abs_corr[i]) == boundary))
    need = r - len(fixed)
    if need < 0 or need > len(tied):
        raise RuntimeError("inconsistent boundary class")
    options = [tuple(sorted(fixed + choice)) for choice in itertools.combinations(tied, need)]
    if not options:
        raise RuntimeError("empty admissible support set")
    canonical = min(options)
    return options, {
        "boundary_abs_correlation_numerator": boundary,
        "fixed_above_boundary": list(fixed),
        "boundary_tied": list(tied),
        "need_from_boundary": need,
        "candidate_count": len(options),
        "canonical_support": list(canonical),
        "rank_gap_separable": len(options) == 1,
    }


def synthetic_no_tie_control() -> dict[str, Any]:
    corr = np.asarray([19, -17, 13, -11, 7, -5], dtype=np.int64)
    options, meta = enumerate_supports(corr, 3)
    ok = len(options) == 1 and meta["rank_gap_separable"]
    if not ok:
        raise RuntimeError("synthetic no-tie control failed")
    return {"passed": True, "correlations": corr.tolist(), "support": list(options[0])}


def exact_fraction(num: int, den: int) -> dict[str, Any]:
    return {"numerator": int(num), "denominator": int(den), "fraction": f"{num}/{den}"}


def candidate_prediction(test_bank: np.ndarray, corr: np.ndarray, support: tuple[int, ...]) -> np.ndarray:
    signs = np.sign(corr[list(support)]).astype(np.int16)
    score = np.sum(test_bank[:, list(support)].astype(np.int16) * signs[None, :], axis=1, dtype=np.int16)
    return (score > 0).astype(np.uint8)


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
    if dx == 0 or dy == 0:
        return 0.0
    return num / (dx * dy)


def n_screen(p: int) -> float:
    rho3 = 0.5
    return (1.0 + math.sqrt(2.0 * math.log(p))) ** 2 / (rho3**2)


def evaluate_registered_criterion(cells: list[dict[str, Any]], key: str) -> dict[str, Any]:
    rows = []
    right_censored = False
    for cell in cells:
        n = cell[key]
        if n is None:
            right_censored = True
        rows.append((int(cell["bank_width_p"]), n))
    if right_censored:
        return {"verdict": "C4_INDETERMINATE", "reason": "RIGHT_CENSORED", "rows": rows}
    rows_sorted = sorted((p, int(n)) for p, n in rows if n is not None)
    pvals = [p for p, _ in rows_sorted]
    nvals = [n for _, n in rows_sorted]
    rel = [abs(n - n_screen(p)) / n_screen(p) for p, n in rows_sorted]
    within = sum(v <= 0.25 for v in rel)
    bad = sum(v > 0.25 for v in rel)
    nondecreasing = all(a <= b for a, b in zip(nvals, nvals[1:]))
    rho = spearman([math.log(p) for p in pvals], [float(n) for n in nvals])
    extremes_flat = None
    if 91 in pvals and 42504 in pvals:
        extremes_flat = nvals[pvals.index(42504)] <= nvals[pvals.index(91)]
    grows = nondecreasing and any(a < b for a, b in zip(nvals, nvals[1:]))
    if within >= 8 and nondecreasing:
        verdict = "C1_LAW_CONFIRMED_REGIME_EXTENDED"
    elif rho <= 0 or bool(extremes_flat):
        verdict = "C2_LAW_FALSIFIED_FLAT"
    elif grows and bad >= 5:
        verdict = "C3_LAW_FALSIFIED_SCALE"
    else:
        verdict = "C4_INDETERMINATE"
    return {
        "verdict": verdict,
        "rows_sorted": rows_sorted,
        "relative_errors": rel,
        "within_25pct_count": within,
        "outside_25pct_count": bad,
        "nondecreasing_in_p": nondecreasing,
        "spearman_ncross_ln_p": rho,
        "extreme_flat_condition": extremes_flat,
    }


def first_cross(sizes: list[int], numerators: list[int], denominator: int) -> int | None:
    # exact comparison to 0.95 = 19/20
    for n, num in zip(sizes, numerators, strict=True):
        if 20 * num >= 19 * denominator:
            return n
    return None


def measure(protocol: dict[str, Any], outdir: Path) -> dict[str, Any]:
    ladder = protocol["ladder"]
    cells = [tuple(map(int, c)) for c in ladder["cells"]]
    seeds = [int(s) for s in ladder["seeds"]]
    sizes = [int(n) for n in ladder["train_sizes"]]
    n_test = int(ladder["n_test"])
    n_queries = int(ladder["n_queries"])
    if float(protocol["primary_quantities"]["tau"]) != TAU:
        raise RuntimeError("protocol tau mismatch")

    control = synthetic_no_tie_control()
    transcript_root = outdir / "transcript"
    cell_rows: list[dict[str, Any]] = []
    total_start = time.perf_counter()
    total_cpu_start = time.process_time()

    for cell_index, cell in enumerate(cells):
        d, s, r = cell
        cell_start = time.perf_counter()
        subsets = list(itertools.combinations(range(d), s))
        p = len(subsets)
        seed_rows: list[dict[str, Any]] = []
        separable_failures = []
        for seed in seeds:
            rng = rung_stream(seed, cell)
            queries = [rng.choice(p, size=r, replace=False).tolist() for _ in range(n_queries)]
            test_x = rng.choice((-1, 1), size=(n_test, d)).astype(np.int8)
            test_bank = bank(test_x, subsets)
            test_labels = [
                (test_bank[:, np.asarray(active, dtype=np.int64)].sum(axis=1) > 0).astype(np.uint8)
                for active in queries
            ]
            label_refs = []
            for qi, label in enumerate(test_labels):
                rel = f"transcript/cell{cell_index}/seed{seed}/q{qi}-labels.bits.b64"
                label_refs.append(write_bits(label, outdir / rel, record_path=rel))

            size_rows = []
            for n in sizes:
                train_x = rng.choice((-1, 1), size=(n, d)).astype(np.int8)
                train_bank = bank(train_x, subsets)
                qrows = []
                seed_min_num = 0
                seed_max_num = 0
                for qi, active in enumerate(queries):
                    train_y = (train_bank[:, np.asarray(active, dtype=np.int64)].sum(axis=1) > 0).astype(np.uint8)
                    y_pm = 2 * train_y.astype(np.int16) - 1
                    corr = np.sum(train_bank.astype(np.int16) * y_pm[:, None], axis=0, dtype=np.int64)
                    options, meta = enumerate_supports(corr, r)
                    candidates = []
                    counts = []
                    for ci, support in enumerate(options):
                        pred = candidate_prediction(test_bank, corr, support)
                        correct = int(np.count_nonzero(pred == test_labels[qi]))
                        counts.append(correct)
                        rel = f"transcript/cell{cell_index}/seed{seed}/n{n}/q{qi}-candidate{ci}-predictions.bits.b64"
                        pred_ref = write_bits(pred, outdir / rel, record_path=rel)
                        candidates.append({
                            "candidate_id": ci,
                            "support_feature_indices": list(support),
                            "correlation_numerators": [int(corr[j]) for j in support],
                            "prediction_bits": pred_ref,
                        })
                    qmin, qmax = min(counts), max(counts)
                    seed_min_num += qmin
                    seed_max_num += qmax
                    if meta["rank_gap_separable"] and len(candidates) != 1:
                        separable_failures.append({"seed": seed, "n": n, "query": qi})
                    qrows.append({
                        "query_id": qi,
                        "label_bits": label_refs[qi],
                        "boundary": meta,
                        "candidates": candidates,
                        "min_correct": qmin,
                        "max_correct": qmax,
                    })
                size_rows.append({
                    "train_size": n,
                    "queries": qrows,
                    "seed_min_correct": seed_min_num,
                    "seed_max_correct": seed_max_num,
                    "denominator": n_queries * n_test,
                })
            seed_rows.append({"seed": seed, "sizes": size_rows})

        if separable_failures:
            raise RuntimeError(f"separable-gap control failed: {separable_failures[:3]}")

        den_seed = n_queries * n_test
        den_mean = den_seed * len(seeds)
        mean_max_nums = []
        mean_min_nums = []
        for size_index, n in enumerate(sizes):
            mean_max_nums.append(sum(row["sizes"][size_index]["seed_max_correct"] for row in seed_rows))
            mean_min_nums.append(sum(row["sizes"][size_index]["seed_min_correct"] for row in seed_rows))
        n_lo = first_cross(sizes, mean_max_nums, den_mean)
        n_hi = first_cross(sizes, mean_min_nums, den_mean)
        cell_rows.append({
            "cell_index": cell_index,
            "cell": list(cell),
            "bank_width_p": p,
            "n_cross_lo": n_lo,
            "n_cross_hi": n_hi,
            "identified": n_lo == n_hi,
            "mean_max_curve": {str(n): exact_fraction(num, den_mean) for n, num in zip(sizes, mean_max_nums, strict=True)},
            "mean_min_curve": {str(n): exact_fraction(num, den_mean) for n, num in zip(sizes, mean_min_nums, strict=True)},
            "seed_rows": seed_rows,
            "resource": {"wall_seconds": time.perf_counter() - cell_start},
        })

    lo_eval = evaluate_registered_criterion(cell_rows, "n_cross_lo")
    hi_eval = evaluate_registered_criterion(cell_rows, "n_cross_hi")
    all_identified = all(row["identified"] for row in cell_rows)
    if all_identified:
        terminal = "T1_TIE_ROBUST"
    elif lo_eval["verdict"] == hi_eval["verdict"]:
        terminal = "T2_TIE_AMBIGUOUS_VERDICT_INVARIANT"
    else:
        terminal = "T3_TIE_AMBIGUOUS_VERDICT_CHANGING"

    return {
        "schema": "orion.orion21.tie-robust-phase.result.v1",
        "protocol_identity": protocol["protocol_identity"],
        "terminal": terminal,
        "scientific_host_requirement": protocol["execution"]["host_class"],
        "control": {"synthetic_no_tie": control, "separable_gap_failures": 0},
        "ladder": {
            "cells": cell_rows,
            "endpoint_verdict_lo": lo_eval,
            "endpoint_verdict_hi": hi_eval,
            "all_n_cross_point_identified": all_identified,
        },
        "resource": {
            "wall_seconds": time.perf_counter() - total_start,
            "cpu_seconds": time.process_time() - total_cpu_start,
            "peak_rss_raw": int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),
        },
        "authority": protocol["authority"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    protocol = load_json(PROTOCOL)
    expected = load_json(EXPECTED)
    if protocol["protocol_identity"] != expected["protocol_identity"]:
        raise RuntimeError("protocol/terminal identity mismatch")
    try:
        result = measure(protocol, args.output_dir)
    except Exception as exc:
        cannot = {
            "schema": "orion.orion21.tie-robust-phase.result.v1",
            "protocol_identity": protocol.get("protocol_identity"),
            "terminal": "T4_CANNOT_CHECK_GENERATOR_UNDERSPECIFIED",
            "error": f"{type(exc).__name__}: {exc}",
            "authority": protocol.get("authority"),
        }
        (args.output_dir / "RESULT.json").write_text(json.dumps(cannot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(cannot, indent=2, sort_keys=True))
        return 3
    (args.output_dir / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"terminal": result["terminal"], "result": str(args.output_dir / 'RESULT.json')}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
