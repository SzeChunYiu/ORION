#!/usr/bin/env python3
"""ORION-02 (FiberGuard C) — C-NBR certified neighborhood executor V1.

Implements CERTIFIED_NEIGHBORHOOD_PROTOCOL_V1.md exactly: freezes the R15
Lipschitz training-anchor neighborhood certificate (Theorem C-R15.9) on
disjoint DEV data and evaluates frozen coverage, certificate validity, and
paid decision value on HELD-OUT scenarios of the live ASlib SAT11-HAND-ALGO
harness subject, against strong baselines, under harness PAR10 accounting.

The frozen harness at papers/paper-xx-executable-research-core/benchmark/ is
imported and reused (digest-verified loader, frozen RF router); it is never
modified. Receipts are content-hash-bound and written in mode 'x'.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
import platform
import sys
from pathlib import Path
from typing import Any

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import sklearn
from sklearn.decomposition import PCA

HERE = Path(__file__).resolve().parent
HARNESS_PATH = (
    HERE.parent.parent
    / "paper-xx-executable-research-core"
    / "benchmark"
    / "run_aslib_v1.py"
)
PROTOCOL_PATH = HERE / "CERTIFIED_NEIGHBORHOOD_PROTOCOL_V1.md"
RESULT_DIR = HERE / "results"
JSON_PATH = RESULT_DIR / "CERTIFIED_NEIGHBORHOOD_RESULT_V1.json"
MARKDOWN_PATH = RESULT_DIR / "CERTIFIED_NEIGHBORHOOD_RESULT_V1.md"


def env_float(name: str, default: float) -> float:
    return float(os.environ.get(name, str(default)))


def env_int(name: str, default: int) -> int:
    return int(os.environ.get(name, str(default)))


SEED = env_int("CNBR_SEED", 20260818)
BOOTSTRAP_SEED = env_int("CNBR_BOOTSTRAP_SEED", 20260819)
BOOTSTRAPS = env_int("CNBR_BOOTSTRAPS", 10000)
INNER_MODULUS = env_int("CNBR_INNER_MODULUS", 5)
SLOPE_QUANTILE = env_float("CNBR_SLOPE_QUANTILE", 0.95)
EPSILON_LEVELS = [
    float(item)
    for item in os.environ.get("CNBR_EPSILON_LEVELS", "500,5000").split(",")
    if item.strip()
]
PRIMARY_EPSILON = env_float("CNBR_PRIMARY_EPSILON", 5000.0)
KNN_K = env_int("CNBR_KNN_K", 16)
RF_TREES = env_int("CNBR_RF_TREES", 300)
PCA_COMPONENTS = env_int("CNBR_PCA_COMPONENTS", 10)
EQ_ROUND = env_int("CNBR_EQ_ROUND", 6)
HOSTILE_FACTOR = env_float("CNBR_HOSTILE_FACTOR", 0.25)
MIN_CAL_PAIRS = env_int("CNBR_MIN_CAL_PAIRS", 100)
SPLIT_A_DEV_FOLDS = {
    int(item)
    for item in os.environ.get("CNBR_SPLIT_A_DEV_FOLDS", "1,2,3,4,5").split(",")
    if item.strip()
}
SPLIT_B_DEV_FRACTION = env_float("CNBR_SPLIT_B_TARGET_DEV_FRACTION", 0.6)
DIST_FLOOR = 1e-9


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_harness() -> Any:
    spec = importlib.util.spec_from_file_location("run_aslib_v1", HARNESS_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import frozen harness at {HARNESS_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["run_aslib_v1"] = module
    spec.loader.exec_module(module)
    return module


def stable_hash(text: str) -> int:
    return int.from_bytes(
        hashlib.sha256(text.encode("utf-8")).digest()[:16], "big"
    )


def inner_calibration(instance_id: str) -> bool:
    return stable_hash(instance_id + ":cnbr-inner") % INNER_MODULUS == 0


def family_of(instance_id: str) -> str:
    parts = instance_id.lstrip("./").split("/")
    return "/".join(parts[:4])


def family_disjoint_split(
    instance_ids: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, dict[str, int]]:
    families = sorted({family_of(item) for item in instance_ids})
    sizes = {
        family: sum(1 for item in instance_ids if family_of(item) == family)
        for family in families
    }
    order = sorted(families, key=lambda family: stable_hash(family + ":cnbr-split-b"))
    dev_count = 0
    held_count = 0
    assignment: dict[str, str] = {}
    for family in order:
        dev_weight = dev_count / max(SPLIT_B_DEV_FRACTION, 1e-9)
        held_weight = held_count / max(1.0 - SPLIT_B_DEV_FRACTION, 1e-9)
        if dev_weight <= held_weight:
            assignment[family] = "DEV"
            dev_count += sizes[family]
        else:
            assignment[family] = "HELD"
            held_count += sizes[family]
    dev = np.asarray(
        [assignment[family_of(item)] == "DEV" for item in instance_ids], dtype=bool
    )
    held = ~dev
    overlap = len(
        {family_of(item) for item in instance_ids[dev]}
        & {family_of(item) for item in instance_ids[held]}
    )
    return dev, held, {
        "family_overlap": overlap,
        "dev_families": len({family_of(item) for item in instance_ids[dev]}),
        "held_families": len({family_of(item) for item in instance_ids[held]}),
    }


def impute_and_standardize(
    x_train: np.ndarray, x_other: list[np.ndarray]
) -> tuple[np.ndarray, list[np.ndarray]]:
    with np.errstate(all="ignore"):
        medians = np.nanmedian(x_train, axis=0)
    medians = np.where(np.isnan(medians), 0.0, medians)
    mean = np.nanmean(np.where(np.isnan(x_train), medians, x_train), axis=0)
    centered = np.where(np.isnan(x_train), medians, x_train) - mean
    std = np.sqrt(np.mean(centered**2, axis=0))
    std = np.where(std < 1e-12, 1.0, std)

    def transform(matrix: np.ndarray) -> np.ndarray:
        filled = np.where(np.isnan(matrix), medians, matrix)
        return (filled - mean) / std

    return transform(x_train), [transform(matrix) for matrix in x_other]


def pairwise_slopes(
    phi: np.ndarray, regret_column: np.ndarray
) -> tuple[np.ndarray, int, int]:
    """Return kept slopes, excluded-pair count, excluded pairs with regret gap."""
    n = len(phi)
    diff_u = np.triu_indices(n, k=1)
    distances = np.linalg.norm(phi[diff_u[0]] - phi[diff_u[1]], axis=1)
    gaps = np.abs(regret_column[diff_u[0]] - regret_column[diff_u[1]])
    keep = distances >= DIST_FLOOR
    excluded = int(np.sum(~keep))
    excluded_gapped = int(np.sum(~keep & (gaps > 0.0)))
    slopes = gaps[keep] / distances[keep]
    return slopes, excluded, excluded_gapped


def certificate_constants(
    phi_cal: np.ndarray, regret_cal: np.ndarray, n_actions: int
) -> tuple[np.ndarray, dict[str, Any]]:
    constants = np.empty(n_actions, dtype=float)
    receipt: dict[str, Any] = {}
    total_pairs = len(phi_cal) * (len(phi_cal) - 1) // 2
    if total_pairs < MIN_CAL_PAIRS:
        raise ValueError(
            f"fail-closed: only {total_pairs} calibration pairs < {MIN_CAL_PAIRS}"
        )
    for action in range(n_actions):
        slopes, excluded, excluded_gapped = pairwise_slopes(
            phi_cal, regret_cal[:, action]
        )
        if slopes.size == 0:
            raise ValueError(f"no usable calibration slopes for action {action}")
        constants[action] = float(np.quantile(slopes, SLOPE_QUANTILE))
        receipt[f"action_{action}"] = {
            "lipschitz_constant": float(constants[action]),
            "excluded_near_duplicate_pairs": excluded,
            "excluded_pairs_with_regret_gap": excluded_gapped,
        }
    receipt["calibration_pairs"] = int(total_pairs)
    receipt["slope_quantile"] = SLOPE_QUANTILE
    return constants, receipt


def certificate_upper_bounds(
    phi_train: np.ndarray,
    regret_train: np.ndarray,
    constants: np.ndarray,
    phi_query: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """U_T(a, x) = min_z [R(a,z) + L_a d(x, z)]; returns (U, a_cert)."""
    distances = np.sqrt(
        np.maximum(
            (
                (phi_query[:, None, :] - phi_train[None, :, :]) ** 2
            ).sum(axis=2),
            0.0,
        )
    )
    upper = np.empty((len(phi_query), regret_train.shape[1]), dtype=float)
    for action in range(regret_train.shape[1]):
        upper[:, action] = (
            regret_train[None, :, action] + constants[action] * distances
        ).min(axis=1)
    action_certificate = np.argmin(upper, axis=1)
    value = upper[np.arange(len(phi_query)), action_certificate]
    return value, action_certificate


def wilson_interval(successes: int, total: int, z: float = 1.959963984540054) -> list[float]:
    if total == 0:
        return [0.0, 1.0]
    p = successes / total
    denominator = 1.0 + z * z / total
    centre = (p + z * z / (2.0 * total)) / denominator
    margin = z * math.sqrt(p * (1.0 - p) / total + z * z / (4.0 * total * total)) / denominator
    return [max(0.0, centre - margin), min(1.0, centre + margin)]


def arm_metrics(
    cost: np.ndarray, solved: np.ndarray, attempt: np.ndarray, vbs_cost: np.ndarray
) -> dict[str, float]:
    par10 = float(protocol_cutoff()) * 10.0
    return {
        "mean_par10": float(np.mean(cost)),
        "solve_rate": float(np.mean(solved)),
        "attempt_coverage": float(np.mean(attempt)),
        "catastrophic_rate": float(np.mean(cost >= par10 - 1e-9)),
        "mean_par10_regret_vs_vbs": float(np.mean(cost - vbs_cost)),
    }


_PROTOCOL_CUTOFF: dict[str, float] = {}


def protocol_cutoff() -> float:
    if "cutoff" not in _PROTOCOL_CUTOFF:
        raise RuntimeError("cutoff not bound")
    return _PROTOCOL_CUTOFF["cutoff"]


def paired_bootstrap(
    cost_a: np.ndarray, cost_b: np.ndarray, seed: int
) -> dict[str, Any]:
    difference = cost_a - cost_b
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, len(difference), size=(BOOTSTRAPS, len(difference)))
    samples = difference[indices].mean(axis=1)
    interval = [float(item) for item in np.quantile(samples, [0.025, 0.975])]
    return {
        "estimate": float(np.mean(difference)),
        "paired_bootstrap_95_percent_interval": interval,
        "resamples": BOOTSTRAPS,
    }


def self_test() -> dict[str, Any]:
    """Synthetic exactly-Lipschitz ground truth; validates the certificate core."""
    rng = np.random.default_rng(20260827)
    n, dims, n_actions = 240, 10, 5
    features = rng.normal(size=(n, dims))
    gradients = rng.normal(size=(n_actions, dims))
    offsets = rng.normal(size=n_actions)
    costs = features @ gradients.T + offsets[None, :]
    best = costs.min(axis=1)
    regret = costs - best[:, None]
    true_constant = np.linalg.norm(gradients, axis=1) + float(
        np.linalg.norm(gradients, axis=1).max()
    )
    train, query = features[:120], features[120:]
    value, action = certificate_upper_bounds(
        train, regret[:120], true_constant, query
    )
    realized = regret[120:, action]
    violations = int(np.sum(realized > value + 1e-9))
    if violations != 0:
        raise AssertionError(
            f"self-test failed: {violations} violations with true constants"
        )
    hostile_value, hostile_action = certificate_upper_bounds(
        train, regret[:120], true_constant * 0.25, query
    )
    hostile_violations = int(
        np.sum(regret[120:, hostile_action] > hostile_value + 1e-9)
    )
    if hostile_violations == 0:
        raise AssertionError(
            "self-test failed: hostile under-estimated constant shows no violations"
        )
    return {
        "true_constant_violations": violations,
        "hostile_underestimated_violations": hostile_violations,
        "n_query": int(len(query)),
        "status": "GREEN",
    }


def evaluate_split(
    data: dict[str, Any],
    harness: Any,
    split_name: str,
    dev_mask: np.ndarray,
    held_mask: np.ndarray,
    split_receipt_extra: dict[str, Any],
) -> dict[str, Any]:
    runtime = data["runtime"]
    solved = data["solved"]
    n_instances, n_actions = runtime.shape
    vbs_solver = np.argmin(runtime, axis=1)
    vbs_cost = runtime[np.arange(n_instances), vbs_solver]
    vbs_solved = np.any(solved, axis=1)

    dev_rows = np.flatnonzero(dev_mask)
    held_rows = np.flatnonzero(held_mask)
    cal_mask = np.asarray(
        [inner_calibration(item) for item in data["instance_ids"][dev_mask]],
        dtype=bool,
    )
    if not cal_mask.any() or cal_mask.all():
        raise ValueError(f"degenerate inner calibration split for {split_name}")
    train_rows = dev_rows[~cal_mask]
    cal_rows = dev_rows[cal_mask]

    x_all = data["x"]
    phi_train, [phi_cal, phi_held] = impute_and_standardize(
        x_all[train_rows], [x_all[cal_rows], x_all[held_rows]]
    )

    regret = runtime - vbs_cost[:, None]

    # frozen fallback: SBS on DEV-TRAIN mean PAR10
    sbs_solver = int(np.argmin(runtime[train_rows].mean(axis=0)))

    # kNN16 selector in the standardized NBR_FULL space
    knn_k = min(KNN_K, len(train_rows))
    distances = np.sqrt(
        ((phi_held[:, None, :] - phi_train[None, :, :]) ** 2).sum(axis=2)
    )
    neighbor_rows = np.argsort(distances, axis=1, kind="stable")[:, :knn_k]
    knn_action = np.argmin(
        runtime[train_rows][neighbor_rows].mean(axis=1), axis=1
    )

    # frozen RF router reused unchanged from the harness, on the harness's own
    # impute-only featurization (median fill, no standardization)
    x_train_imp, x_held_imp = harness.impute(
        x_all[train_rows], x_all[held_rows]
    )
    rf_action, _ = harness.fit_router(
        x_train_imp, runtime[train_rows], solved[train_rows], x_held_imp
    )

    # exact-equality control
    def eq_key(row_values: np.ndarray) -> bytes:
        return np.round(row_values, EQ_ROUND).tobytes()

    train_keys: dict[bytes, list[int]] = {}
    for local_index, row in enumerate(x_all[train_rows]):
        train_keys.setdefault(eq_key(row), []).append(local_index)
    eq_covered = np.asarray(
        [eq_key(row) in train_keys for row in x_all[held_rows]], dtype=bool
    )
    eq_action = np.full(len(held_rows), sbs_solver, dtype=int)
    for index in np.flatnonzero(eq_covered):
        matches = train_keys[eq_key(x_all[held_rows][index])]
        eq_action[index] = int(
            np.argmin(runtime[train_rows][matches].mean(axis=0))
        )

    representations: dict[str, np.ndarray] = {"NBR_FULL": None}
    pca_receipt: dict[str, Any] = {}
    phi_train_pca = phi_train
    phi_cal_pca = phi_cal
    phi_held_pca = phi_held
    if PCA_COMPONENTS > 0 and PCA_COMPONENTS < phi_train.shape[1]:
        pca = PCA(n_components=PCA_COMPONENTS, svd_solver="full")
        pca.fit(phi_train)
        phi_train_pca = pca.transform(phi_train)
        phi_cal_pca = pca.transform(phi_cal)
        phi_held_pca = pca.transform(phi_held)
        pca_receipt = {
            "n_components": int(PCA_COMPONENTS),
            "explained_variance_ratio": [
                float(item) for item in pca.explained_variance_ratio_
            ],
        }
        representations["NBR_PCA10"] = None

    relations: dict[str, dict[str, Any]] = {}
    for relation_name, (train_phi, cal_phi, held_phi) in {
        "NBR_FULL": (phi_train, phi_cal, phi_held),
        "NBR_PCA10": (phi_train_pca, phi_cal_pca, phi_held_pca),
    }.items():
        if relation_name not in representations:
            continue
        constants, constants_receipt = certificate_constants(
            cal_phi, regret[cal_rows], n_actions
        )
        value_cal, action_cal = certificate_upper_bounds(
            train_phi, regret[train_rows], constants, cal_phi
        )
        realized_cal = regret[cal_rows, action_cal]
        cal_violations = int(np.sum(realized_cal > value_cal + 1e-9))

        value_held, action_held = certificate_upper_bounds(
            train_phi, regret[train_rows], constants, held_phi
        )
        realized_held = regret[held_rows, action_held]
        held_violations = int(np.sum(realized_held > value_held + 1e-9))

        hostile_value, hostile_action = certificate_upper_bounds(
            train_phi, regret[train_rows], constants * HOSTILE_FACTOR, held_phi
        )
        hostile_violations = int(
            np.sum(
                regret[held_rows, hostile_action] > hostile_value + 1e-9
            )
        )

        coverage = {
            f"epsilon_{epsilon:g}": float(np.mean(value_held <= epsilon))
            for epsilon in EPSILON_LEVELS
        }
        relations[relation_name] = {
            "lipschitz_constants": constants_receipt,
            "pca": pca_receipt if relation_name == "NBR_PCA10" else {},
            "certificate_calibration_violation_rate": cal_violations / len(cal_rows),
            "certificate_heldout_violation_rate": held_violations / len(held_rows),
            "certificate_heldout_violation_wilson_95": wilson_interval(
                held_violations, len(held_rows)
            ),
            "hostile_underestimated_violation_rate": hostile_violations
            / len(held_rows),
            "heldout_coverage": coverage,
            "value_held": value_held,
            "action_held": action_held,
        }

    primary = relations["NBR_FULL"]
    covered = primary["value_held"] <= PRIMARY_EPSILON
    nbr_action = np.where(
        covered, primary["action_held"], sbs_solver
    ).astype(int)
    pca10 = relations.get("NBR_PCA10")
    if pca10 is not None:
        covered_pca = pca10["value_held"] <= PRIMARY_EPSILON
        nbr_pca_action = np.where(
            covered_pca, pca10["action_held"], sbs_solver
        ).astype(int)

    arms_cost: dict[str, np.ndarray] = {}
    arms_solved: dict[str, np.ndarray] = {}
    arms_attempt: dict[str, np.ndarray] = {}
    arms_cost["SBS"] = runtime[held_rows, sbs_solver]
    arms_solved["SBS"] = solved[held_rows, sbs_solver]
    arms_cost["VBS"] = vbs_cost[held_rows]
    arms_solved["VBS"] = vbs_solved[held_rows]
    arms_cost["RF_ROUTER"] = runtime[held_rows, rf_action]
    arms_solved["RF_ROUTER"] = solved[held_rows, rf_action]
    arms_cost["KNN16"] = runtime[held_rows, knn_action]
    arms_solved["KNN16"] = solved[held_rows, knn_action]
    arms_cost["NBR_CERT_FULL"] = runtime[held_rows, nbr_action]
    arms_solved["NBR_CERT_FULL"] = solved[held_rows, nbr_action]
    arms_attempt["NBR_CERT_FULL"] = covered
    if pca10 is not None:
        arms_cost["NBR_CERT_PCA10"] = runtime[held_rows, nbr_pca_action]
        arms_solved["NBR_CERT_PCA10"] = solved[held_rows, nbr_pca_action]
        arms_attempt["NBR_CERT_PCA10"] = covered_pca
    arms_cost["EXACT_EQ"] = runtime[held_rows, eq_action]
    arms_solved["EXACT_EQ"] = solved[held_rows, eq_action]
    arms_attempt["EXACT_EQ"] = eq_covered
    for name in ["SBS", "VBS", "RF_ROUTER", "KNN16"]:
        arms_attempt[name] = np.ones(len(held_rows), dtype=bool)

    metrics = {
        name: arm_metrics(
            arms_cost[name], arms_solved[name], arms_attempt[name], vbs_cost[held_rows]
        )
        for name in arms_cost
    }

    comparisons = {
        "sbs_minus_nbr_cert": paired_bootstrap(
            arms_cost["SBS"], arms_cost["NBR_CERT_FULL"], BOOTSTRAP_SEED
        ),
        "knn16_minus_nbr_cert": paired_bootstrap(
            arms_cost["KNN16"], arms_cost["NBR_CERT_FULL"], BOOTSTRAP_SEED + 1
        ),
        "rf_router_minus_nbr_cert": paired_bootstrap(
            arms_cost["RF_ROUTER"], arms_cost["NBR_CERT_FULL"], BOOTSTRAP_SEED + 2
        ),
    }

    q = float(np.mean(covered))
    q_eq = float(np.mean(eq_covered))
    v = primary["certificate_heldout_violation_rate"]
    delta = comparisons["sbs_minus_nbr_cert"]
    coverage_producing = q >= 0.10 and q >= 5.0 * q_eq
    certificate_valid = v <= 0.10
    value_over_fallback = (
        delta["estimate"] > 0.0
        and delta["paired_bootstrap_95_percent_interval"][0] > 0.0
    )
    if not certificate_valid:
        verdict = "CERTIFICATE_INVALID"
    elif delta["paired_bootstrap_95_percent_interval"][1] < 0.0:
        verdict = "ADVERSE"
    elif coverage_producing and value_over_fallback:
        verdict = "CERTIFIED_NEIGHBORHOOD_POSITIVE"
    else:
        verdict = "COVERAGE_WITHOUT_VALUE"

    for relation in relations.values():
        relation.pop("value_held")
        relation.pop("action_held")

    return {
        "split": split_name,
        "split_receipt": {
            "dev_instances": int(dev_mask.sum()),
            "heldout_instances": int(held_mask.sum()),
            "dev_train_instances": int(len(train_rows)),
            "dev_calibration_instances": int(len(cal_rows)),
            "sbs_solver": data["algorithms"][sbs_solver],
            "knn_k": int(knn_k),
            "rf_router_featurization": (
                "harness.impute (DEV-TRAIN median fill, no standardization)"
            ),
            **split_receipt_extra,
        },
        "metrics": metrics,
        "relations": relations,
        "exact_equality": {
            "heldout_coverage": q_eq,
            "covered_instances": int(eq_covered.sum()),
        },
        "paired_comparisons": comparisons,
        "gate_inputs": {
            "heldout_coverage_at_primary_epsilon": q,
            "primary_epsilon": PRIMARY_EPSILON,
            "five_times_exact_eq": 5.0 * q_eq,
            "heldout_violation_rate": v,
            "sbs_minus_nbr_cert": delta,
        },
        "verdict": verdict,
    }


def display(value: float | None) -> str:
    return "—" if value is None else f"{value:.4f}"


def render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# ORION-02 C-NBR certified neighborhood result",
        "",
        "> Generated by `experiments/certified_neighborhood.py` from the frozen",
        "> protocol. The JSON file is the machine-readable source of truth.",
        "",
        f"- terminal: `{result['overall_verdict']}`",
        f"- protocol SHA-256: `{result['protocol_sha256']}`",
        f"- self-test: `{result['self_test']['status']}`",
        "",
    ]
    for split in result["splits"]:
        lines += [
            f"## {split['split']}",
            "",
            f"- verdict: `{split['verdict']}`",
            f"- DEV/HELD-OUT instances: {split['split_receipt']['dev_instances']}"
            f"/{split['split_receipt']['heldout_instances']} "
            f"(train {split['split_receipt']['dev_train_instances']}, "
            f"calibration {split['split_receipt']['dev_calibration_instances']})",
            "",
            "| System | Mean PAR10 | Solve rate | Attempt coverage | Catastrophic | Regret vs VBS |",
            "|---|---:|---:|---:|---:|---:|",
        ]
        for name, metric in split["metrics"].items():
            lines.append(
                f"| {name} | {display(metric['mean_par10'])} | "
                f"{display(metric['solve_rate'])} | "
                f"{display(metric['attempt_coverage'])} | "
                f"{display(metric['catastrophic_rate'])} | "
                f"{display(metric['mean_par10_regret_vs_vbs'])} |"
            )
        lines += [
            "",
            "| Relation | Held-out coverage @5000 | Held-out violation rate | Wilson 95% | Hostile violation |",
            "|---|---:|---:|---|---:|",
        ]
        for name, relation in split["relations"].items():
            coverage = relation["heldout_coverage"].get("epsilon_5000")
            wilson = relation["certificate_heldout_violation_wilson_95"]
            lines.append(
                f"| {name} | {display(coverage)} | "
                f"{display(relation['certificate_heldout_violation_rate'])} | "
                f"[{wilson[0]:.4f}, {wilson[1]:.4f}] | "
                f"{display(relation['hostile_underestimated_violation_rate'])} |"
            )
        gates = split["gate_inputs"]
        lines += [
            "",
            f"Exact-equality control coverage: {gates['five_times_exact_eq'] / 5.0:.4f}"
            f" (5x = {gates['five_times_exact_eq']:.4f}); certified coverage"
            f" {gates['heldout_coverage_at_primary_epsilon']:.4f}.",
            f"SBS - NBR_CERT_FULL: {gates['sbs_minus_nbr_cert']['estimate']:.2f}"
            f" {gates['sbs_minus_nbr_cert']['paired_bootstrap_95_percent_interval']}.",
            "",
        ]
    lines += [
        "## Interpretation boundary",
        "",
        "One bounded public scenario; no ASlib-wide, SAT-wide, cross-domain or",
        "selective-prediction superiority claim. The calibrated Lipschitz constant",
        "is probabilistic authority; validity is the audited property above.",
        "Certificate coverage is not action authority.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    _PROTOCOL_CUTOFF["cutoff"] = 5000.0
    self_test_receipt = self_test()

    harness = load_harness()
    harness_protocol = json.loads(harness.PROTOCOL_PATH.read_text(encoding="utf-8"))
    _PROTOCOL_CUTOFF["cutoff"] = float(harness_protocol["cutoff_seconds"])
    data = harness.load_scenario(harness_protocol)

    folds = data["folds"]
    split_a_dev = np.isin(folds, sorted(SPLIT_A_DEV_FOLDS))
    split_b_dev, split_b_held, family_receipt = family_disjoint_split(
        data["instance_ids"]
    )

    result: dict[str, Any] = {
        "schema": "ORION02.CNBR.Result.v1",
        "protocol_sha256": sha256_file(PROTOCOL_PATH),
        "executor_sha256": sha256_file(Path(__file__).resolve()),
        "harness_protocol_sha256": sha256_file(harness.PROTOCOL_PATH),
        "source": {
            "repository": harness_protocol["source"]["repository"],
            "commit": harness_protocol["source"]["commit"],
            "scenario": harness_protocol["source"]["scenario"],
            "git_sha": os.environ.get("CNBR_SOURCE_GIT_SHA", "UNBOUND"),
            "input_sha256": harness_protocol["source"]["files"],
        },
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scikit_learn": sklearn.__version__,
            "platform": platform.platform(),
        },
        "parameters": {
            "seed": SEED,
            "bootstrap_seed": BOOTSTRAP_SEED,
            "bootstraps": BOOTSTRAPS,
            "inner_modulus": INNER_MODULUS,
            "slope_quantile": SLOPE_QUANTILE,
            "epsilon_levels": EPSILON_LEVELS,
            "primary_epsilon": PRIMARY_EPSILON,
            "knn_k": KNN_K,
            "rf_trees": RF_TREES,
            "pca_components": PCA_COMPONENTS,
            "eq_round": EQ_ROUND,
            "hostile_factor": HOSTILE_FACTOR,
            "split_a_dev_folds": sorted(SPLIT_A_DEV_FOLDS),
            "split_b_target_dev_fraction": SPLIT_B_DEV_FRACTION,
        },
        "population": {
            "instances": int(len(data["instance_ids"])),
            "features": int(len(data["feature_names"])),
            "algorithms": int(len(data["algorithms"])),
            "outer_folds": sorted(int(item) for item in np.unique(folds)),
        },
        "self_test": self_test_receipt,
        "disposition": "PENDING_VERDICT",
    }

    splits = [
        evaluate_split(
            data,
            harness,
            "SPLIT_OFFICIAL_FOLD",
            split_a_dev,
            ~split_a_dev,
            {"dev_folds": sorted(SPLIT_A_DEV_FOLDS)},
        ),
        evaluate_split(
            data,
            harness,
            "SPLIT_FAMILY_DISJOINT",
            split_b_dev,
            split_b_held,
            family_receipt,
        ),
    ]
    result["splits"] = splits
    overall = (
        splits[1]["verdict"]
        if splits[0]["verdict"] == splits[1]["verdict"]
        else f"{splits[0]['verdict']}__{splits[1]['verdict']}"
    )
    result["overall_verdict"] = overall
    result["disposition"] = "EXECUTED__FROZEN_PROTOCOL_APPLIED"

    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    with JSON_PATH.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    with MARKDOWN_PATH.open("x", encoding="utf-8") as handle:
        handle.write(render_markdown(result))
    print(f"wrote {JSON_PATH}")
    print(f"wrote {MARKDOWN_PATH}")
    print(json.dumps({"overall_verdict": overall,
                      "split_verdicts": [s["verdict"] for s in splits]},
                     indent=2))


if __name__ == "__main__":
    main()
