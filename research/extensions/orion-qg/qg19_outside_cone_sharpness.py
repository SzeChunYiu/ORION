#!/usr/bin/env python3
"""QG-19: exact finite sharpness probe just outside the QG8 support-two cone.

The analyzer is scientifically independent of the benchmark instruments: it imports only
scientific/runtime modules and compares the unrestricted weighted R6M DP with the exact
support-<=2 D++ family on the prospectively frozen panel.
"""
from __future__ import annotations

import argparse
import ast
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


def anti_instrument_import_gate() -> dict[str, Any]:
    """Inspect actual Python imports rather than prose/comments for instrument dependencies."""
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    forbidden = [name for name in imported if "q3_replacement" in name.lower() or "dual_instrument" in name.lower()]
    return {"imports": sorted(set(imported)), "forbidden_imports": forbidden, "pass": not forbidden}


def evaluate(target_pairs, n: int, source: str, index: Any) -> dict[str, Any]:
    qg2.clear_caches()
    c_dp = qg2.dp_cost_pairs_ob(target_pairs, n, O19)
    c_dxx = qg2.dxx_cost_ob(target_pairs, n, O19)
    if c_dp > c_dxx:
        raise AssertionError({"unrestricted_exceeds_dxx": [n, source, index, c_dp, c_dxx]})
    row: dict[str, Any] = {
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
        witness = qg2.dp_witness_ob(target_pairs, n, O19)
        row["dp_witness"] = witness
        if int(witness["max_frame_support"]) <= 2:
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
    import_gate = anti_instrument_import_gate()
    if not import_gate["pass"]:
        raise AssertionError({"instrument_import_dependency": import_gate})

    rows: list[dict[str, Any]] = []
    for name, letter_pairs in sorted(r6m._HOSTILE_N1_PANELS.items()):
        tp = tuple((r6m._N1_LETTER_KEY[a], r6m._N1_LETTER_KEY[b]) for a, b in letter_pairs)
        rows.append(evaluate(tp, 1, "HOSTILE_N1", name))
    for name, raw in sorted(r6m._HOSTILE_N2_PANELS.items()):
        tp = tuple((tuple(a), tuple(b)) for a, b in raw)
        rows.append(evaluate(tp, 2, "HOSTILE_N2", name))

    rng = np.random.default_rng(SEED)
    for n in (2, 3):
        for i in range(RANDOM_PER_N):
            targets = []
            for _ in range(6):
                while True:
                    x = int(rng.integers(0, 2**n))
                    z = int(rng.integers(0, 2**n))
                    if (x, z) != (0, 0):
                        break
                targets.append((x, z))
            tp = tuple((targets[2*j], targets[2*j+1]) for j in range(3))
            rows.append(evaluate(tp, n, "RANDOM", i))

    gaps = [row for row in rows if row["support3_required"]]
    counts_by_source: dict[str, int] = {}
    gaps_by_source: dict[str, int] = {}
    for row in rows:
        key = f"{row['source']}_n{row['n']}"
        counts_by_source[key] = counts_by_source.get(key, 0) + 1
        gaps_by_source[key] = gaps_by_source.get(key, 0) + int(row["support3_required"])

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
        "panel": {"seed": SEED, "random_per_n": RANDOM_PER_N, "total_rows": len(rows), "counts_by_source": counts_by_source},
        "support3_gap_count": len(gaps),
        "gaps_by_source": gaps_by_source,
        "first_gap_rows": gaps[:WITNESS_CAP],
        "n1_independent_brute_gate": n1_brute_gate(),
        "anti_instrument_import_gate": import_gate,
        "gates": {
            "all_unrestricted_le_dxx": all(row["C_DP"] <= row["C_Dxx"] for row in rows),
            "all_serialized_gap_witnesses_support_gt2": all(int(row["dp_witness"]["max_frame_support"]) > 2 for row in gaps[:WITNESS_CAP]),
            "no_instrument_import": import_gate["pass"],
            "chemistry_sources_read": False,
            "protected_subject_read": False,
        },
        "terminal": terminal,
        "authority": "EXACT_FROZEN_PANEL_ONLY__NO_ALL_N_SHARPNESS_AUTHORITY__NOT_R6",
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
    }
    result["result_digest"] = hashlib.sha256(canonical(result).encode()).hexdigest()
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(canonical(result))


if __name__ == "__main__":
    main()
