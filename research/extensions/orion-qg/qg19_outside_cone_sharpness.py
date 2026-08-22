#!/usr/bin/env python3
"""QG-19: exact finite sharpness probe just outside the QG8 support-two cone.

Independent of Q3 instrument files. The analyzer compares the unrestricted weighted
R6M DP with the exact support-<=2 D++ family on a frozen deterministic panel.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[3]
QG_DIR = REPO_ROOT / "research" / "extensions" / "orion-qg"
sys.path.insert(0, str(QG_DIR))

import qg2_objective_robustness as qg2  # noqa: E402

r6m = qg2.r6m

BASE = "c5ba39fef4f25c46de5fb69bf07f50530f4693ca"
PROTOCOL = REPO_ROOT / "development/orion-qg-regime-geometry/QG19_OUTSIDE_CONE_SHARPNESS_PROTOCOL_V1.md"
DEFAULT_OUTPUT = REPO_ROOT / "artifacts/orion-qg-qg19-outside-cone-sharpness.json"
O19 = qg2.Objective("O19", 4, 3, 2, 2, 0)
SEED = 20260822
RANDOM_PER_N = 24
WITNESS_CAP = 20


def canonical(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evaluate(target_pairs, n: int, source: str, index: Any) -> dict[str, Any]:
    qg2.clear_caches()
    c_dp = qg2.dp_cost_pairs_ob(target_pairs, n, O19)
    c_dxx = qg2.dxx_cost_ob(target_pairs, n, O19)
    if c_dp > c_dxx:
        raise AssertionError({"unrestricted_exceeds_dxx": [n, source, index, c_dp, c_dxx]})
    row = {
        "source": source,
        "index": index,
        "n": n,
        "targets": [[list(a), list(b)] for a, b in target_pairs],
        "C_DP": int(c_dp),
        "C_Dxx": int(c_dxx),
        "gap": int(c_dp - c_dxx),
        "support3_required": bool(c_dp < c_dxx),
    }
    if c_dp < c_dxx:
        w = qg2.dp_witness_ob(target_pairs, n, O19)
        row["dp_witness"] = w
        if int(w["max_frame_support"]) <= 2:
            raise AssertionError({"gap_witness_not_support3": row})
    return row


def n1_brute_gate() -> dict[str, Any]:
    checked = 0
    for name, letter_pairs in sorted(r6m._HOSTILE_N1_PANELS.items()):
        tp = tuple((r6m._N1_LETTER_KEY[a], r6m._N1_LETTER_KEY[b]) for a, b in letter_pairs)
        dp_global = qg2.dp_cost_pairs_ob(tp, 1, O19)
        brute_global = None
        for perm_b in (0, 1):
            for perm_c in (0, 1):
                for centrals in qg2.CENTRALS8:
                    value = qg2.brute_config_n1_ob(tp, perm_b, perm_c, centrals, O19)
                    if value is not None and (brute_global is None or value < brute_global):
                        brute_global = value
        checked += 1
        if brute_global != dp_global:
            raise AssertionError({"o19_n1_brute_mismatch": [name, dp_global, brute_global]})
    return {"hostile_n1_panels_checked": checked, "all_exact": True}


def run() -> dict[str, Any]:
    if not PROTOCOL.is_file():
        raise FileNotFoundError(PROTOCOL)
    # Hard anti-contamination/import gate: this analyzer must not depend on Q3 files.
    source_text = Path(__file__).read_text(encoding="utf-8")
    if "Q-paper-03" in source_text or "LANE_A" in source_text or "LANE_B" in source_text:
        raise AssertionError("QG19 analyzer contains Q3 dependency")

    rows: list[dict[str, Any]] = []
    for name, letter_pairs in sorted(r6m._HOSTILE_N1_PANELS.items()):
        tp = tuple((r6m._N1_LETTER_KEY[a], r6m._N1_LETTER_KEY[b]) for a, b in letter_pairs)
        rows.append(evaluate(tp, 1, "HOSTILE_N1", name))
    for name, tp0 in sorted(r6m._HOSTILE_N2_PANELS.items()):
        tp = tuple((tuple(a), tuple(b)) for a, b in tp0)
        rows.append(evaluate(tp, 2, "HOSTILE_N2", name))

    rng = np.random.default_rng(SEED)
    for n in (2, 3):
        for i in range(RANDOM_PER_N):
            targets = []
            for _ in range(6):
                while True:
                    x = int(rng.integers(0, 2 ** n))
                    z = int(rng.integers(0, 2 ** n))
                    if (x, z) != (0, 0):
                        break
                targets.append((x, z))
            tp = tuple((targets[2*j], targets[2*j+1]) for j in range(3))
            rows.append(evaluate(tp, n, "RANDOM", i))

    gaps = [r for r in rows if r["support3_required"]]
    counts_by_source: dict[str, int] = {}
    gaps_by_source: dict[str, int] = {}
    for r in rows:
        key = f"{r['source']}_n{r['n']}"
        counts_by_source[key] = counts_by_source.get(key, 0) + 1
        gaps_by_source[key] = gaps_by_source.get(key, 0) + int(r["support3_required"])

    terminal = (
        "QG19_SUPPORT3_WITNESS_FOUND_ON_FROZEN_PANEL"
        if gaps else "QG19_ZERO_GAP_ON_FROZEN_PANEL__SHARPNESS_REMAINS_OPEN"
    )
    result: dict[str, Any] = {
        "schema": "ORION.QG.QG19.OutsideConeSharpness.v1",
        "base_revision": BASE,
        "protocol_sha256": sha256_file(PROTOCOL),
        "objective": {"t_nc": 4, "t_c": 3, "t_tag": 2, "t_r": 2, "rho": 0},
        "qg8_margins": {"central": -1, "noncentral": 0},
        "panel": {
            "seed": SEED,
            "random_per_n": RANDOM_PER_N,
            "total_rows": len(rows),
            "counts_by_source": counts_by_source,
        },
        "support3_gap_count": len(gaps),
        "gaps_by_source": gaps_by_source,
        "first_gap_rows": gaps[:WITNESS_CAP],
        "n1_independent_brute_gate": n1_brute_gate(),
        "gates": {
            "all_unrestricted_le_dxx": all(r["C_DP"] <= r["C_Dxx"] for r in rows),
            "all_serialized_gap_witnesses_support_gt2": all(
                int(r["dp_witness"]["max_frame_support"]) > 2 for r in gaps[:WITNESS_CAP]
            ),
            "no_q3_import": True,
            "chemistry_sources_read": False,
            "protected_subject_read": False,
        },
        "terminal": terminal,
        "authority": "EXACT_FROZEN_PANEL_ONLY__NO_ALL_N_SHARPNESS_AUTHORITY__NOT_R6",
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
    }
    digest_payload = dict(result)
    result["result_digest"] = hashlib.sha256(canonical(digest_payload).encode()).hexdigest()
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
