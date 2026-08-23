#!/usr/bin/env python3
"""NR-12 step 1: verify the cell-level concentration attribution from the FROZEN
P11_QUERY_FAMILY_PHASE_V1 primary receipt (read-only; no battery re-execution).

Questions, pre-stated:
  A1. Is compile-tolerance concentrated in specific (responsibility x access-class)
      cells rather than being a family-wide property? Quantify: per-cell QS matrix,
      per-responsibility tolerant-class counts, and a two-way variance partition
      of the delta table (responsibility main effect vs access-class main effect
      vs interaction vs residual).
  A2. Does the delta track UNIVERSAL difficulty (the receipt's mechanism claim)?
      Pearson + Spearman of delta vs universal_mean per access class, and pooled.

Output: nr12_attribution_verification_v1.json + printed summary.
"""
from __future__ import annotations
import hashlib, json
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
SRC = HERE / "p11_query_family_phase_primary_v1.json"
OUT = HERE / "nr12_attribution_verification_v1.json"
ARMS = ("LINEAR", "RBF", "KNN")
QS = list(range(10))


def main() -> int:
    d = json.loads(SRC.read_text())
    qr = d["query_results"]
    # A1: QS matrix and per-responsibility tolerant-class counts
    qs_matrix = {a: [bool(qr[f"{a}:{q}"]["quality_supported"]) for q in QS] for a in ARMS}
    tol_classes = {q: sum(qs_matrix[a][q] for a in ARMS) for q in QS}
    cells_qs = sum(sum(row) for row in qs_matrix.values())
    # A1: two-way partition of delta_{q,a} with no replication:
    #   delta = grand + resp_effect + access_effect + interaction (exact, no residual
    #   when interaction is kept; residual=0). Report share of sum-squares.
    delta = np.array([[qr[f"{a}:{q}"]["delta"] for a in ARMS] for q in QS])  # q x a
    grand = delta.mean()
    resp_eff = np.repeat(delta.mean(axis=1, keepdims=True) - grand, 3, axis=1)  # (10,3)
    acc_eff = np.repeat(delta.mean(axis=0, keepdims=True) - grand, 10, axis=0)  # (10,3)
    inter = delta - grand - resp_eff - acc_eff                    # (10,3)
    ss = lambda m: float((np.asarray(m, dtype=float) ** 2).sum())
    ss_total = ss(delta - grand)
    shares = (ss(resp_eff) / ss_total, ss(acc_eff) / ss_total, ss(inter) / ss_total)
    assert abs(sum(shares) - 1.0) < 1e-9, shares  # balanced design: exact partition
    partition = {
        "total_ss": ss_total,
        "responsibility_share": shares[0],
        "access_share": shares[1],
        "interaction_share": shares[2],
    }
    # A2: difficulty tracking
    uni = {a: np.array([qr[f"{a}:{q}"]["universal_mean"] for q in QS]) for a in ARMS}
    dl = {a: np.array([qr[f"{a}:{q}"]["delta"] for q in QS]) for a in ARMS}

    def corr(x, y):
        pr = float(np.corrcoef(x, y)[0, 1])
        rx = np.argsort(np.argsort(x)); ry = np.argsort(np.argsort(y))
        sp = float(np.corrcoef(rx, ry)[0, 1])
        return {"pearson": pr, "spearman": sp}

    difficulty = {a: corr(uni[a], dl[a]) for a in ARMS}
    pooled = corr(
        np.concatenate([uni[a] for a in ARMS]),
        np.concatenate([dl[a] for a in ARMS]),
    )
    out = {
        "schema": "P11.NR12.AttributionVerification.v1",
        "source_sha256": hashlib.sha256(SRC.read_bytes()).hexdigest(),
        "source_terminal": d["terminal"],
        "qs_matrix": qs_matrix,
        "cells_qs_of_30": cells_qs,
        "tolerant_class_count_per_responsibility": tol_classes,
        "responsibilities_with_zero_tolerant_class": [q for q in QS if tol_classes[q] == 0],
        "responsibilities_with_all_three_tolerant": [q for q in QS if tol_classes[q] == 3],
        "delta_two_way_partition": partition,
        "difficulty_correlation": {**{f"{a}": difficulty[a] for a in ARMS}, "pooled": pooled},
    }
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True))
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
