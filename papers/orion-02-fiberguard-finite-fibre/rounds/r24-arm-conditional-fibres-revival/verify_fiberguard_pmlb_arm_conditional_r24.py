#!/usr/bin/env python3
"""Independent structural and metric verifier for ORION-02 R24 receipts.

The verifier deliberately does not import the R24 executor.  It rebuilds
arm-specific fibres, full-state coverage, stored-decision bounds, summaries,
paired bootstraps, and the terminal from primitive receipt fields.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from math import comb
from pathlib import Path
import sys
from typing import Any, Mapping

import numpy as np


HERE = Path(__file__).resolve().parent
SCHEMA = "ORION.FiberGuard.PMLBArmConditionalBoundaryFibres.R24.Result.v1"
MODE_ARM_CONDITIONAL = "R24_ARM_CONDITIONAL_BOUNDARY_FIBRES"
MODE_LEXICAL_CONTROL = "R24_LEXICAL_GOOD_BOUNDARY_NEGATIVE_CONTROL"
PORTFOLIO = ("dct", "gnb", "hgb", "knn5", "logreg", "rf300")
LEARNED_ARMS = (
    "LEARNED_KNN_1",
    "LEARNED_KNN_3",
    "LEARNED_KNN_5",
    "LEARNED_KNN_9",
    "LEARNED_RF300",
)
TEST_ARMS = ("SHIELD_FREE", "SHIELD_FULL", "STATIC_ADAPTIVE") + LEARNED_ARMS
GROUPS = ("G0", "G1", "G2", "G3")
TAU = 0.02
TOL = 1e-9
POOL_K = 2
COVERAGE_TARGET = 0.95
VALIDITY_TARGET = 0.10
BOOTSTRAP_REPLICATES = 20_000
BOOTSTRAP_SEED_TEXT = "ORION02_R23_PMLB_DENSITY_BACKOFF_BOOTSTRAP_V1"
R23_RESULT_SHA256 = "cf1a0db71ab135278b64c02633f07d05a23604a121f0b62743f4e59c6358fc77"
SERIALIZED_BOUND_ABS_TOL = 1.1e-12


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_float(value: float) -> float:
    out = float(value)
    if not math.isfinite(out):
        raise ValueError("nonfinite verifier value")
    return round(out, 12)


def derive_seed(*parts: object) -> int:
    text = "|".join(str(part) for part in parts)
    return int.from_bytes(hashlib.sha256(text.encode()).digest()[:8], "big") % (2**31 - 1)


def expected_ball_members(n_bits: int, shield_n: int, radius: int) -> float:
    return float(shield_n * sum(comb(n_bits, i) for i in range(radius + 1)) / (2**n_bits))


def minimum_density_radius(n_bits: int, shield_n: int, minimum_expected: float = 2.0) -> int:
    for radius in range(n_bits + 1):
        if expected_ball_members(n_bits, shield_n, radius) >= minimum_expected:
            return radius
    raise ValueError("shield cannot supply the requested expected membership")


def _hamming(left: tuple[int, ...], right: tuple[int, ...]) -> int:
    if len(left) != len(right):
        raise ValueError("Hamming shape mismatch")
    return sum(int(a != b) for a, b in zip(left, right))


def independent_arm_pool(
    query_cell: tuple[int, ...],
    member_cells: Mapping[str, tuple[int, ...]],
    member_excess: Mapping[str, float],
    *,
    tau: float,
    radius: int,
    k: int = POOL_K,
) -> list[str]:
    candidates = sorted(
        (-float(member_excess[name]), _hamming(query_cell, cell), name)
        for name, cell in member_cells.items()
        if float(member_excess[name]) <= tau + TOL and _hamming(query_cell, cell) <= radius
    )
    return [name for _, _, name in candidates[:k]] if len(candidates) >= k else []


def independent_lexical_pool(
    member_excess: Mapping[str, float], *, tau: float, k: int = POOL_K
) -> list[str]:
    candidates = sorted(
        (-float(excess), name)
        for name, excess in member_excess.items()
        if float(excess) <= tau + TOL
    )
    return [name for _, name in candidates[:k]] if len(candidates) >= k else []


def _selected_vector(row: Mapping[str, list[float]], acquired: set[str]) -> tuple[float, ...]:
    return tuple(
        value for group in GROUPS if group == "G0" or group in acquired for value in row[group]
    )


def independent_arm_pools(
    name: str,
    roles: Mapping[str, list[str]],
    meta: Mapping[str, Mapping[str, list[float]]],
    outcomes: Mapping[str, Mapping[str, float]],
    mode: str,
    acquired: list[str] | tuple[str, ...],
) -> tuple[dict[str, list[str]], dict[str, float | None], dict[str, bool]]:
    shield = sorted(roles["shield_table"])
    if name in shield:
        raise AssertionError("query inside shield table")
    acquired_set = set(acquired)
    proposer_vectors = np.asarray(
        [_selected_vector(meta[item], acquired_set) for item in roles["proposer_train"]]
    )
    edges = np.median(proposer_vectors, axis=0)

    def cell(item: str) -> tuple[int, ...]:
        return tuple(
            int(value > edge)
            for value, edge in zip(_selected_vector(meta[item], acquired_set), edges)
        )

    query_cell = cell(name)
    member_cells = {member: cell(member) for member in shield}
    exact = sorted(member for member in shield if member_cells[member] == query_cell)
    radius = minimum_density_radius(len(query_cell), len(shield))
    pools: dict[str, list[str]] = {}
    bounds: dict[str, float | None] = {}
    used: dict[str, bool] = {}
    for arm in PORTFOLIO:
        excess = {member: outcomes[member][arm] - outcomes[member]["best"] for member in shield}
        if len(exact) >= POOL_K and max(excess[member] for member in exact) <= TAU + TOL:
            members = exact
            used_backoff = False
        elif mode == MODE_LEXICAL_CONTROL:
            members = independent_lexical_pool(excess, tau=TAU, k=POOL_K)
            used_backoff = True
        elif mode == MODE_ARM_CONDITIONAL:
            members = independent_arm_pool(
                query_cell,
                member_cells,
                excess,
                tau=TAU,
                radius=radius,
                k=POOL_K,
            )
            used_backoff = True
        else:
            raise ValueError(f"unknown R24 mode: {mode}")
        pools[arm] = members
        bounds[arm] = (
            json_float(max(excess[member] for member in members))
            if len(members) >= POOL_K
            else None
        )
        used[arm] = used_backoff
    return pools, bounds, used


def independent_full_state_record(
    name: str,
    fold: int,
    roles: Mapping[str, list[str]],
    meta: Mapping[str, Mapping[str, list[float]]],
    outcomes: Mapping[str, Mapping[str, float]],
    mode: str,
) -> dict[str, Any]:
    pools, bounds, used = independent_arm_pools(
        name, roles, meta, outcomes, mode, ("G1", "G2", "G3")
    )
    admissible = sorted(arm for arm in PORTFOLIO if pools[arm] and bounds[arm] is not None)
    best_arm = min(admissible, key=lambda arm: (bounds[arm], arm)) if admissible else None
    return {
        "fold": fold,
        "arm_pools": pools,
        "arm_bounds": bounds,
        "arm_used_backoff": used,
        "admissible": admissible,
        "best_arm": best_arm,
        "best_bound": bounds[best_arm] if best_arm is not None else None,
    }


def _bounded_equal(left: Any, right: Any) -> bool:
    if left is None or right is None:
        return left is right
    return math.isclose(float(left), float(right), rel_tol=0.0, abs_tol=SERIALIZED_BOUND_ABS_TOL)


def full_state_records_match(
    rebuilt: Mapping[str, Mapping[str, Any]], stored: Mapping[str, Mapping[str, Any]]
) -> bool:
    if set(rebuilt) != set(stored):
        return False
    for name, left in rebuilt.items():
        right = stored[name]
        if set(left) != set(right):
            return False
        for key in left:
            if key == "best_bound":
                if not _bounded_equal(left[key], right[key]):
                    return False
            elif key == "arm_bounds":
                if set(left[key]) != set(right[key]):
                    return False
                if any(not _bounded_equal(left[key][arm], right[key][arm]) for arm in left[key]):
                    return False
            elif left[key] != right[key]:
                return False
    return True


def independent_arm_summary(rows: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    excesses = np.asarray([float(row["excess"]) for row in rows.values()])
    certified = [row for row in rows.values() if row["certified"]]
    return {
        "n": len(rows),
        "certified_n": len(certified),
        "certified_fraction": json_float(len(certified) / len(rows)),
        "mean_excess": json_float(float(excesses.mean())),
        "p95_excess": json_float(float(np.percentile(excesses, 95.0))),
        "max_excess": json_float(float(excesses.max())),
        "mean_groups_acquired": json_float(
            float(np.mean([row["groups_acquired"] for row in rows.values()]))
        ),
        "violations_strict": sum(bool(row["violation_strict"]) for row in certified),
        "violations_tau": sum(bool(row["violation_tau"]) for row in certified),
        "mean_bound": (
            json_float(float(np.mean([row["bound"] for row in certified]))) if certified else None
        ),
    }


def independent_r23_parent_arm_summary(
    rows: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    """Rebuild the legacy R23 summary schema without importing its executor.

    R23 reports two operational fractions in addition to the common scientific
    summary fields.  R24 deliberately omitted those redundant fields from its
    own summaries.  Keeping the schema distinction explicit prevents an
    exact-dictionary comparison from rejecting a scientifically identical R23
    parent merely because the independent verifier rebuilt only the common
    subset.
    """

    summary = independent_arm_summary(rows)
    summary["fallback_fraction"] = json_float(
        float(np.mean([bool(row["fallback"]) for row in rows.values()]))
    )
    summary["backoff_fraction"] = json_float(
        float(np.mean([bool(row["used_backoff"]) for row in rows.values()]))
    )
    return summary


def pooled_rows(phase: Mapping[str, Any], arm: str) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for fold in sorted(phase, key=int):
        rows.update(phase[fold]["test"][arm])
    return rows


def pooled_primary(phase: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for fold in sorted(phase, key=int):
        rows.update(phase[fold]["test"][phase[fold]["primary"]])
    return rows


def independent_primary(fold_row: Mapping[str, Any]) -> str:
    summaries = {
        arm: independent_arm_summary(fold_row["threshold_select"][arm]) for arm in LEARNED_ARMS
    }
    return min(
        LEARNED_ARMS,
        key=lambda arm: (
            summaries[arm]["mean_excess"],
            summaries[arm]["p95_excess"],
            summaries[arm]["max_excess"],
            arm,
        ),
    )


def independent_comparison(
    left: Mapping[str, Mapping[str, Any]],
    right: Mapping[str, Mapping[str, Any]],
    label: str,
) -> dict[str, Any]:
    names = sorted(left)
    if names != sorted(right):
        raise ValueError("comparison identity mismatch")
    diffs = np.asarray([left[name]["excess"] - right[name]["excess"] for name in names])
    rng = np.random.default_rng(derive_seed(BOOTSTRAP_SEED_TEXT, "R24_" + label))
    indices = rng.integers(0, diffs.size, size=(BOOTSTRAP_REPLICATES, diffs.size))
    means = diffs[indices].mean(axis=1)
    lo, hi = (float(value) for value in np.percentile(means, [2.5, 97.5]))
    return {
        "left_minus_right_by_dataset": {name: json_float(diffs[i]) for i, name in enumerate(names)},
        "mean_diff": json_float(float(diffs.mean())),
        "ci_lower": json_float(lo),
        "ci_upper": json_float(hi),
        "bootstrap_replicates": BOOTSTRAP_REPLICATES,
    }


def derive_terminal(payload: Mapping[str, Any]) -> str:
    if not all(payload["hostile_controls"].values()):
        return "C_R24_ARM_CONDITIONAL_HOSTILE_CONTROL_FAILED"
    coverage = float(payload["coverage"]["r24_primary"])
    parent = float(payload["coverage"]["r23_parent"])
    target = float(payload["coverage"].get("target", COVERAGE_TARGET))
    if coverage <= parent + TOL:
        return "C_R24_ARM_CONDITIONAL_NO_COVERAGE_IMPROVEMENT"
    if coverage < target - TOL:
        return "C_R24_ARM_CONDITIONAL_COVERAGE_IMPROVED_BELOW_GATE"
    certified_n = int(payload["primary"]["certified_n"])
    violations = int(payload["primary"]["violations_strict"])
    rate = violations / certified_n if certified_n else math.inf
    if rate > VALIDITY_TARGET + TOL:
        return "C_R24_ARM_CONDITIONAL_CERTIFICATE_INVALID"
    parent_test = payload.get("matched_parent_test")
    negative_test = payload.get("negative_control_test")
    if (
        parent_test
        and negative_test
        and float(parent_test["mean_diff"]) < -TOL
        and float(parent_test["ci_upper"]) < 0.0
        and float(negative_test["mean_diff"]) < -TOL
        and float(negative_test["ci_upper"]) < 0.0
    ):
        return "C_R24_ARM_CONDITIONAL_VALUE"
    return "C_R24_ARM_CONDITIONAL_COVERAGE_VALIDITY_PASS_VALUE_NOT_MATERIAL"


def _decision_rows_valid(
    phase: Mapping[str, Any],
    meta: Mapping[str, Mapping[str, list[float]]],
    outcomes: Mapping[str, Mapping[str, float]],
    mode: str,
) -> bool:
    for fold in sorted(phase, key=int):
        fold_row = phase[fold]
        roles = fold_row["roles"]
        role_sets = [
            set(roles[key])
            for key in ("test", "proposer_train", "shield_table", "threshold_select")
        ]
        if any(role_sets[i] & role_sets[j] for i in range(4) for j in range(i + 1, 4)):
            return False
        if independent_primary(fold_row) != fold_row["primary"]:
            return False
        fstar = min(
            PORTFOLIO,
            key=lambda arm: (
                float(np.mean([outcomes[name][arm] for name in roles["shield_table"]])),
                arm,
            ),
        )
        if fold_row["f_star_arm"] != fstar:
            return False
        for section in ("threshold_select", "test"):
            for rows in fold_row[section].values():
                for query, row in rows.items():
                    if row["committed"] not in PORTFOLIO:
                        return False
                    expected_excess = json_float(
                        outcomes[query][row["committed"]] - outcomes[query]["best"]
                    )
                    if row["excess"] != expected_excess:
                        return False
                    if row["fallback"]:
                        if (
                            row["certified"]
                            or row["committed"] != fstar
                            or row["bound"] is not None
                        ):
                            return False
                        continue
                    pools, bounds, _ = independent_arm_pools(
                        query, roles, meta, outcomes, mode, row["acquired"]
                    )
                    committed = row["committed"]
                    if row["pool_members"] != pools[committed]:
                        return False
                    if not _bounded_equal(row["bound"], bounds[committed]):
                        return False
                    strict = expected_excess > float(bounds[committed]) + TOL
                    if bool(row["violation_strict"]) != strict:
                        return False
                    if bool(row["violation_tau"]) != (expected_excess > TAU + TOL):
                        return False
    return True


def check(label: str, condition: bool, detail: str = "") -> int:
    suffix = f" :: {detail}" if detail and not condition else ""
    print(("[PASS] " if condition else "[FAIL] ") + label + suffix)
    return 0 if condition else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--terminal", type=Path, required=True)
    parser.add_argument("--r23-parent", type=Path, required=True)
    args = parser.parse_args()
    payload = json.loads(args.result.read_text())
    parent = json.loads(args.r23_parent.read_text())
    failures = 0
    failures += check("result schema", payload.get("schema") == SCHEMA)
    failures += check(
        "R23 parent byte binding", sha256_bytes(args.r23_parent.read_bytes()) == R23_RESULT_SHA256
    )
    failures += check("terminal file", args.terminal.read_text().strip() == payload.get("terminal"))
    failures += check(
        "authority remains none",
        payload["authority"]["scientific_authority_delta"] == "NONE"
        and not payload["authority"]["submission_authorized"]
        and not payload["authority"]["top_tier_gate_pass"]
        and not payload["authority"]["freeze_authorized"],
    )
    outcomes = payload["outcomes"]
    meta = payload["meta_features"]
    for mode in (MODE_ARM_CONDITIONAL, MODE_LEXICAL_CONTROL):
        phase = payload["folds"][mode]
        failures += check(
            "stored decisions " + mode,
            _decision_rows_valid(phase, meta, outcomes, mode),
        )
        rebuilt: dict[str, dict[str, Any]] = {}
        for fold in sorted(phase, key=int):
            roles = phase[fold]["roles"]
            for query in roles["test"]:
                rebuilt[query] = independent_full_state_record(
                    query, int(fold), roles, meta, outcomes, mode
                )
        rebuilt = {name: rebuilt[name] for name in sorted(rebuilt)}
        stored = payload["coverage_records"][mode]
        failures += check(
            "full-state pool replay " + mode,
            full_state_records_match(rebuilt, stored),
        )
        coverage = json_float(
            sum(bool(row["admissible"]) for row in rebuilt.values()) / len(rebuilt)
        )
        key = "r24_primary" if mode == MODE_ARM_CONDITIONAL else "r24_negative_control"
        failures += check("coverage replay " + mode, coverage == payload["coverage"][key])

    geometry = payload["folds"][MODE_ARM_CONDITIONAL]
    negative = payload["folds"][MODE_LEXICAL_CONTROL]
    primary = pooled_primary(geometry)
    static = pooled_rows(geometry, "STATIC_ADAPTIVE")
    parent_phase = parent["folds"]["R23_HAMMING_BACKOFF_K2"]
    parent_primary = pooled_primary(parent_phase)
    negative_primary: dict[str, dict[str, Any]] = {}
    for fold in sorted(geometry, key=int):
        negative_primary.update(negative[fold]["test"][geometry[fold]["primary"]])
    for label, rows in (
        ("R24_PRIMARY_LEARNED", primary),
        ("R24_STATIC_ADAPTIVE", static),
        ("R23_PARENT_PRIMARY_LEARNED", parent_primary),
        ("R24_LEXICAL_MATCHED_PRIMARY", negative_primary),
    ):
        rebuilt_summary = (
            independent_r23_parent_arm_summary(rows)
            if label == "R23_PARENT_PRIMARY_LEARNED"
            else independent_arm_summary(rows)
        )
        failures += check(
            "arm summary " + label,
            rebuilt_summary == payload["arms_summary"][label],
        )

    for label, left, right, stored_key in (
        ("primary-v-r23-primary", primary, parent_primary, "matched_parent_test"),
        ("primary-v-lexical-matched", primary, negative_primary, "negative_control_test"),
        ("primary-v-static", primary, static, "learned_static_test"),
    ):
        rebuilt = independent_comparison(left, right, label)
        for key, value in rebuilt.items():
            failures += check(
                f"comparison {label} {key}",
                payload[stored_key][key] == value,
            )

    failures += check("hostile controls", all(payload["hostile_controls"].values()))
    derived = derive_terminal(payload)
    failures += check(
        "terminal independently derived",
        derived == payload.get("terminal"),
        f"derived={derived} stored={payload.get('terminal')}",
    )
    print("VERIFY_OK" if failures == 0 else f"VERIFY_FAILED failures={failures}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
