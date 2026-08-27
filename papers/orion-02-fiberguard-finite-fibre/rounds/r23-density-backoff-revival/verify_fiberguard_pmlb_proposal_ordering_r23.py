#!/usr/bin/env python3
"""Independent structural and metric verifier for ORION-02 R23 receipts.

This verifier does not import the R23 executor.  It independently rebuilds
full-state exact/backoff pools, F* arms, summaries, paired bootstraps, and the
terminal from stored primitive outcomes, meta-features, and custody roles.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
SCHEMA = "ORION.FiberGuard.PMLBProposalOrdering.R23.v1"
PARENT_SCHEMA = "ORION.FiberGuard.PMLBProposalOrdering.R22CorrectedExact.v1"
MODE_EXACT = "R22C_EXACT_CELL"
MODE_BACKOFF = "R23_HAMMING_BACKOFF_K2"
MODE_LEXICAL = "R23_LEXICAL_BACKOFF_K2_NEGATIVE_CONTROL"
R22_RESULT_SHA256 = "39f47c7806ba77b94a495851f5d51fa111e551db983aa7a31607d5b4bc4f2623"
R22_TERMINAL = "C_R22_PMLB_PROPOSAL_ORDERING_NO_CERTIFIED_COVERAGE"
PORTFOLIO = ("dct", "gnb", "hgb", "knn5", "logreg", "rf300")
LEARNED_ARMS = ("LEARNED_KNN_1", "LEARNED_KNN_3", "LEARNED_KNN_5", "LEARNED_KNN_9", "LEARNED_RF300")
GROUPS = ("G0", "G1", "G2", "G3")
TAU = 0.02
TOL = 1e-9
BACKOFF_K = 2
COVERAGE_TARGET = 0.95
VALIDITY_GATE = 0.10
MATERIAL_FRACTION = 0.05
BOOTSTRAP_REPLICATES = 20_000
BOOTSTRAP_SEED_TEXT = "ORION02_R23_PMLB_DENSITY_BACKOFF_BOOTSTRAP_V1"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest_json(value: Any) -> str:
    return sha256_bytes(canonical_json(value).encode())


def derive_seed(*parts: object) -> int:
    text = "|".join(str(part) for part in parts)
    return int.from_bytes(hashlib.sha256(text.encode()).digest()[:8], "big") % (2**31 - 1)


def json_float(value: float) -> float:
    out = float(value)
    if not math.isfinite(out):
        raise ValueError("nonfinite verifier value")
    return round(out, 12)


def independent_f_star(shield: list[str], outcomes: dict[str, dict[str, float]], portfolio: tuple[str, ...]) -> str:
    return min(portfolio, key=lambda arm: (float(np.mean([outcomes[name][arm] for name in shield])), arm))


def independent_members(query_cell: tuple[int, ...], member_cells: dict[str, tuple[int, ...]],
                        mode: str, k: int = BACKOFF_K) -> tuple[list[str], bool]:
    exact = sorted(name for name, cell in member_cells.items() if cell == query_cell)
    if mode in {"exact", MODE_EXACT} or len(exact) >= k:
        return exact, False
    names = sorted(member_cells)
    if len(names) < k:
        return [], True
    if mode in {"lexical", MODE_LEXICAL}:
        return names[:k], True
    if mode not in {"backoff", MODE_BACKOFF}:
        raise ValueError(f"unknown independent pool mode: {mode}")
    ranked = sorted(
        names,
        key=lambda name: (
            sum(int(a != b) for a, b in zip(member_cells[name], query_cell)),
            name,
        ),
    )
    return ranked[:k], True


def flatten_meta(row: dict[str, list[float]]) -> np.ndarray:
    return np.asarray([value for group in GROUPS for value in row[group]], dtype=float)


def full_state_pool_record(name: str, roles: dict[str, list[str]], meta: dict[str, dict[str, list[float]]],
                           outcomes: dict[str, dict[str, float]], mode: str) -> dict[str, Any]:
    proposer = roles["proposer_train"]
    shield = sorted(roles["shield_table"])
    if name in shield:
        raise AssertionError("query inside shield table")
    raw = np.asarray([flatten_meta(meta[member]) for member in proposer], dtype=float)
    edges = np.median(raw, axis=0)
    def cell(member: str) -> tuple[int, ...]:
        return tuple(int(value > edge) for value, edge in zip(flatten_meta(meta[member]), edges))
    query_cell = cell(name)
    cells = {member: cell(member) for member in shield}
    members, used = independent_members(query_cell, cells, mode, BACKOFF_K)
    wc = {arm: math.inf for arm in PORTFOLIO}
    if len(members) >= BACKOFF_K:
        for arm in PORTFOLIO:
            wc[arm] = max(outcomes[member][arm] - outcomes[member]["best"] for member in members)
    admissible = sorted(arm for arm in PORTFOLIO if wc[arm] <= TAU)
    return {
        "fold": None,
        "members": members,
        "used_backoff": used,
        "admissible": admissible,
        "best_bound": json_float(min(wc[arm] for arm in admissible)) if admissible else None,
    }


def independent_arm_summary(rows: dict[str, dict[str, Any]]) -> dict[str, Any]:
    excesses = np.asarray([row["excess"] for row in rows.values()], dtype=float)
    certified = [row for row in rows.values() if row["certified"]]
    return {
        "n": len(rows),
        "mean_excess": json_float(float(excesses.mean())),
        "p95_excess": json_float(float(np.percentile(excesses, 95.0))),
        "max_excess": json_float(float(excesses.max())),
        "mean_groups_acquired": json_float(float(np.mean([row["groups_acquired"] for row in rows.values()]))),
        "certified_n": len(certified),
        "certified_fraction": json_float(float(len(certified) / len(rows))),
        "fallback_fraction": json_float(float(np.mean([row["fallback"] for row in rows.values()]))),
        "backoff_fraction": json_float(float(np.mean([row["used_backoff"] for row in rows.values()]))),
        "violations_strict": sum(row["violation_strict"] for row in certified),
        "violations_tau": sum(row["violation_tau"] for row in certified),
        "mean_bound": json_float(float(np.mean([row["bound"] for row in certified]))) if certified else None,
    }


def pooled_rows(phase: dict[str, Any], arm: str) -> dict[str, dict[str, Any]]:
    rows = {}
    for fold in sorted(phase, key=int):
        rows.update(phase[fold]["test"][arm])
    return rows


def pooled_primary(phase: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = {}
    for fold in sorted(phase, key=int):
        arm = phase[fold]["primary"]
        rows.update(phase[fold]["test"][arm])
    return rows


def independent_primary(fold_row: dict[str, Any]) -> str:
    summaries = {arm: independent_arm_summary(fold_row["threshold_select"][arm]) for arm in LEARNED_ARMS}
    return min(
        LEARNED_ARMS,
        key=lambda arm: (
            summaries[arm]["mean_excess"],
            summaries[arm]["p95_excess"],
            summaries[arm]["max_excess"],
            arm,
        ),
    )


def independent_comparison(left: dict[str, dict[str, Any]], right: dict[str, dict[str, Any]], label: str) -> dict[str, Any]:
    names = sorted(left)
    if names != sorted(right):
        raise ValueError("comparison identity mismatch")
    diffs = np.asarray([left[name]["excess"] - right[name]["excess"] for name in names], dtype=float)
    rng = np.random.default_rng(derive_seed(BOOTSTRAP_SEED_TEXT, label))
    indices = rng.integers(0, diffs.size, size=(BOOTSTRAP_REPLICATES, diffs.size))
    means = diffs[indices].mean(axis=1)
    lo, hi = (float(x) for x in np.percentile(means, [2.5, 97.5]))
    return {
        "left_minus_right_by_dataset": {name: json_float(diffs[i]) for i, name in enumerate(names)},
        "mean_diff": json_float(float(diffs.mean())),
        "ci_lower": json_float(lo),
        "ci_upper": json_float(hi),
        "bootstrap_replicates": BOOTSTRAP_REPLICATES,
    }


def independent_terminal(payload: dict[str, Any]) -> str:
    if not all(payload["hostile_controls"].values()):
        return "C_R23_PMLB_BACKOFF_HOSTILE_CONTROL_FAILED"
    parent_cov = payload["coverage"]["r22c_exact_full_state"]
    coverage = payload["coverage"]["r23_backoff_full_state"]
    if coverage <= parent_cov + TOL:
        return "C_R23_PMLB_BACKOFF_NO_COVERAGE_IMPROVEMENT"
    if coverage < COVERAGE_TARGET - TOL:
        return "C_R23_PMLB_BACKOFF_COVERAGE_IMPROVED_BELOW_GATE"
    primary = payload["arms_summary"]["R23_BACKOFF_PRIMARY_LEARNED"]
    certified_n = primary["certified_n"]
    violation_rate = primary["violations_strict"] / certified_n if certified_n else math.inf
    if violation_rate > VALIDITY_GATE + TOL:
        return "C_R23_PMLB_BACKOFF_CERTIFICATE_INVALID"
    static = payload["arms_summary"]["R23_BACKOFF_STATIC_ADAPTIVE"]
    test = payload["primary_test"]
    ratio_ok = test["primary_mean_excess"] <= (1.0 - MATERIAL_FRACTION) * static["mean_excess"] + TOL
    cost_ok = test["mean_groups_acquired_primary"] <= test["mean_groups_acquired_static"] + TOL
    if test["mean_diff"] < -TOL and ratio_ok and test["ci_upper"] < 0.0 and cost_ok:
        return "C_R23_PMLB_BACKOFF_VALUE"
    if test["mean_diff"] < -TOL:
        return "C_R23_PMLB_BACKOFF_COVERAGE_RESTORED_VALUE_NOT_MATERIAL"
    if abs(test["mean_diff"]) <= TOL:
        return "C_R23_PMLB_BACKOFF_COVERAGE_RESTORED_VALUE_NULL"
    return "C_R23_PMLB_BACKOFF_COVERAGE_RESTORED_VALUE_ADVERSE"


def check(label: str, condition: bool, detail: str = "") -> int:
    suffix = f" :: {detail}" if detail and not condition else ""
    print(("[PASS] " if condition else "[FAIL] ") + label + suffix)
    return 0 if condition else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result", type=Path, default=HERE / "FIBERGUARD_PMLB_PROPOSAL_ORDERING_R23_RESULTS.json")
    parser.add_argument("--corrected-parent", type=Path, default=HERE / "FIBERGUARD_PMLB_R22_CORRECTED_EXACT_RECEIPT.json")
    parser.add_argument("--terminal", type=Path, default=HERE / "FIBERGUARD_PMLB_PROPOSAL_ORDERING_R23_TERMINAL.txt")
    parser.add_argument("--r22-result", type=Path, default=HERE.parent / "r22-proposal-ordering" / "FIBERGUARD_PMLB_PROPOSAL_ORDERING_R22_RESULTS.json")
    args = parser.parse_args()
    payload = json.loads(args.result.read_text())
    parent = json.loads(args.corrected_parent.read_text())
    failures = 0

    failures += check("result schema", payload.get("schema") == SCHEMA)
    failures += check("parent schema", parent.get("schema") == PARENT_SCHEMA)
    failures += check("terminal file", args.terminal.read_text().strip() == payload.get("terminal"))
    failures += check("R22 result byte binding", sha256_bytes(args.r22_result.read_bytes()) == R22_RESULT_SHA256)
    failures += check("R22 terminal preserved", payload["original_r22"]["terminal"] == R22_TERMINAL and payload["original_r22"]["preserved_unchanged"])
    failures += check("corrected parent digest", digest_json(parent) == payload["corrected_parent_receipt_sha256"])
    failures += check("parent exact folds match main", parent["folds"] == payload["folds"][MODE_EXACT])
    failures += check("parent outcome binding", parent["outcomes_sha256"] == digest_json(payload["outcomes"]))
    failures += check("parent meta binding", parent["meta_features_sha256"] == digest_json(payload["meta_features"]))
    failures += check("authority remains none", payload["authority"]["scientific_authority_delta"] == "NONE" and not payload["authority"]["submission_authorized"] and not payload["authority"]["top_tier_gate_pass"] and not payload["authority"]["freeze_authorized"])

    outcomes = payload["outcomes"]
    meta = payload["meta_features"]
    for mode in (MODE_EXACT, MODE_BACKOFF):
        phase = payload["folds"][mode]
        for fold in sorted(phase, key=int):
            row = phase[fold]
            expected_fstar = independent_f_star(row["roles"]["shield_table"], outcomes, PORTFOLIO)
            failures += check(f"F* fold {fold} {mode}", row["f_star_arm"] == expected_fstar)
            failures += check(f"primary fold {fold} {mode}", row["primary"] == independent_primary(row))
            role_sets = [set(row["roles"][key]) for key in ("test", "proposer_train", "shield_table", "threshold_select")]
            failures += check(f"custody disjoint fold {fold} {mode}", all(not (role_sets[i] & role_sets[j]) for i in range(4) for j in range(i + 1, 4)))

    for mode, independent_mode in ((MODE_EXACT, "exact"), (MODE_BACKOFF, "backoff"), (MODE_LEXICAL, "lexical")):
        phase = payload["folds"][mode]
        stored_records = payload["coverage_records"][mode]
        rebuilt = {}
        for fold in sorted(phase, key=int):
            roles = phase[fold]["roles"]
            for name in roles["test"]:
                row = full_state_pool_record(name, roles, meta, outcomes, independent_mode)
                row["fold"] = int(fold)
                rebuilt[name] = row
        rebuilt = {name: rebuilt[name] for name in sorted(rebuilt)}
        failures += check(f"full-state pool replay {mode}", rebuilt == stored_records)
        coverage = json_float(float(np.mean([bool(row["admissible"]) for row in rebuilt.values()])))
        expected_cov = {
            MODE_EXACT: payload["coverage"]["r22c_exact_full_state"],
            MODE_BACKOFF: payload["coverage"]["r23_backoff_full_state"],
            MODE_LEXICAL: payload["coverage"]["negative_control_full_state"],
        }[mode]
        failures += check(f"coverage replay {mode}", coverage == expected_cov)

    exact = payload["folds"][MODE_EXACT]
    backoff = payload["folds"][MODE_BACKOFF]
    exact_static = pooled_rows(exact, "STATIC_ADAPTIVE")
    exact_primary = pooled_primary(exact)
    backoff_static = pooled_rows(backoff, "STATIC_ADAPTIVE")
    backoff_primary = pooled_primary(backoff)
    for label, rows in (
        ("R22C_EXACT_STATIC_ADAPTIVE", exact_static),
        ("R22C_EXACT_PRIMARY_LEARNED", exact_primary),
        ("R23_BACKOFF_STATIC_ADAPTIVE", backoff_static),
        ("R23_BACKOFF_PRIMARY_LEARNED", backoff_primary),
    ):
        failures += check("arm summary " + label, independent_arm_summary(rows) == payload["arms_summary"][label])
        failures += check("nonnegative excess " + label, all(row["excess"] >= -TOL for row in rows.values()))

    primary_cmp = independent_comparison(backoff_primary, backoff_static, "learned-v-static")
    for key, value in primary_cmp.items():
        failures += check("primary comparison " + key, payload["primary_test"][key] == value)
    matched_cmp = independent_comparison(backoff_static, exact_static, "backoff-static-v-exact-static")
    for key, value in matched_cmp.items():
        failures += check("matched comparison " + key, payload["matched_parent_test"][key] == value)

    failures += check("hostile controls", all(payload["hostile_controls"].values()))
    derived_terminal = independent_terminal(payload)
    failures += check("terminal independently derived", derived_terminal == payload["terminal"], f"derived={derived_terminal} stored={payload.get('terminal')}")
    print("VERIFY_OK" if failures == 0 else f"VERIFY_FAILED failures={failures}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
