#!/usr/bin/env python3
"""ORION-02 (FiberGuard C) — C-NBR2 conformal certified neighborhood executor V1.

Implements CERTIFIED_NEIGHBORHOOD_CONFORMAL_PROTOCOL_V1.md exactly: replaces
the C-NBR V1 pairwise-slope-quantile Lipschitz calibration (CERTIFICATE_INVALID,
LUNARC job 3544034) with split-conformal per-instance calibration of the
neighborhood certificate, frozen on the identical V1 splits, and evaluates
bound validity, certified coverage (including on family-disjoint untouched
scenarios), and paid decision value over the frozen fallback, under harness
PAR10 accounting, against the V1 comparators.

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
PROTOCOL_PATH = HERE / "CERTIFIED_NEIGHBORHOOD_CONFORMAL_PROTOCOL_V1.md"
RESULT_DIR = HERE / "results"
JSON_PATH = RESULT_DIR / "CERTIFIED_NEIGHBORHOOD_CONFORMAL_RESULT_V2.json"
MARKDOWN_PATH = RESULT_DIR / "CERTIFIED_NEIGHBORHOOD_CONFORMAL_RESULT_V2.md"


def env_float(name: str, default: float) -> float:
    return float(os.environ.get(name, str(default)))


def env_int(name: str, default: int) -> int:
    return int(os.environ.get(name, str(default)))


SEED = env_int("CNBR2_SEED", 20260818)
BOOTSTRAP_SEED = env_int("CNBR2_BOOTSTRAP_SEED", 20260819)
BOOTSTRAPS = env_int("CNBR2_BOOTSTRAPS", 10000)
ALPHA = env_float("CNBR2_ALPHA", 0.10)
MU_K = env_int("CNBR2_MU_K", 16)
SIGMA_OFFSET = env_float("CNBR2_SIGMA_OFFSET", 1.0)
EPSILON_LEVELS = [
    float(item)
    for item in os.environ.get("CNBR2_EPSILON_LEVELS", "500,5000").split(",")
    if item.strip()
]
PRIMARY_EPSILON = env_float("CNBR2_PRIMARY_EPSILON", 5000.0)
MONDRIAN_STRATA = env_int("CNBR2_MONDRIAN_STRATA", 3)
HOSTILE_ALPHA_FACTOR = env_float("CNBR2_HOSTILE_ALPHA_FACTOR", 4.0)
KNN_K = env_int("CNBR2_KNN_K", 16)
RF_TREES = env_int("CNBR2_RF_TREES", 300)
PCA_COMPONENTS = env_int("CNBR2_PCA_COMPONENTS", 10)
EQ_ROUND = env_int("CNBR2_EQ_ROUND", 6)
MIN_CAL = env_int("CNBR2_MIN_CAL", 20)
SPLIT_A_DEV_FOLDS = {
    int(item)
    for item in os.environ.get("CNBR2_SPLIT_A_DEV_FOLDS", "1,2,3,4,5").split(",")
    if item.strip()
}
SPLIT_B_DEV_FRACTION = env_float("CNBR2_SPLIT_B_TARGET_DEV_FRACTION", 0.6)


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
    return stable_hash(instance_id + ":cnbr-inner") % 5 == 0


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


def pairwise_distances(query: np.ndarray, anchors: np.ndarray) -> np.ndarray:
    return np.sqrt(
        np.maximum(
            ((query[:, None, :] - anchors[None, :, :]) ** 2).sum(axis=2),
            0.0,
        )
    )


def neighborhood_predictor(
    phi_train: np.ndarray,
    regret_train: np.ndarray,
    phi_query: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """m_a (mu-neighbour mean regret), d1 (nearest-anchor distance), a_base."""
    mu = min(MU_K, len(phi_train))
    distances = pairwise_distances(phi_query, phi_train)
    neighbour_rows = np.argsort(distances, axis=1, kind="stable")[:, :mu]
    m = regret_train[neighbour_rows].mean(axis=1)
    d1 = np.take_along_axis(distances, neighbour_rows[:, :1], axis=1).ravel()
    a_base = np.argmin(m, axis=1)
    return m, d1, a_base


def conformal_quantile(scores: np.ndarray, level: float) -> tuple[float, dict[str, Any]]:
    """Finite-sample split-conformal upper quantile of `scores` at `level`.

    k = ceil((n + 1) * level); k > n => +inf (never certifies).
    Returns (quantile, receipt).
    """
    ordered = np.sort(np.asarray(scores, dtype=float))
    n = len(ordered)
    k = int(math.ceil((n + 1) * level))
    if k > n:
        return math.inf, {
            "calibration_count": n,
            "order_statistic_k": k,
            "fail_closed_infinite": True,
        }
    value = float(ordered[k - 1])
    return value, {
        "calibration_count": n,
        "order_statistic_k": k,
        "fail_closed_infinite": False,
    }


def normalized_scores(
    m_cal: np.ndarray, d1_cal: np.ndarray, a_base_cal: np.ndarray, regret_cal: np.ndarray
) -> np.ndarray:
    rows = np.arange(len(a_base_cal))
    realized = regret_cal[rows, a_base_cal]
    predicted = m_cal[rows, a_base_cal]
    return (realized - predicted) / (SIGMA_OFFSET + d1_cal)


def mondrian_cut_points(d1_train: np.ndarray) -> list[float]:
    quantiles = [
        (index + 1) / MONDRIAN_STRATA for index in range(MONDRIAN_STRATA - 1)
    ]
    return [float(item) for item in np.quantile(d1_train, quantiles)]


def mondrian_assign(d1: np.ndarray, cuts: list[float]) -> np.ndarray:
    return np.searchsorted(np.asarray(cuts, dtype=float), d1, side="right")


def wilson_interval(
    successes: int, total: int, z: float = 1.959963984540054
) -> list[float]:
    if total == 0:
        return [0.0, 1.0]
    p = successes / total
    denominator = 1.0 + z * z / total
    centre = (p + z * z / (2.0 * total)) / denominator
    margin = (
        z * math.sqrt(p * (1.0 - p) / total + z * z / (4.0 * total * total))
        / denominator
    )
    return [max(0.0, centre - margin), min(1.0, centre + margin)]


_PROTOCOL_CUTOFF: dict[str, float] = {}


def protocol_cutoff() -> float:
    if "cutoff" not in _PROTOCOL_CUTOFF:
        raise RuntimeError("cutoff not bound")
    return _PROTOCOL_CUTOFF["cutoff"]


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
    """Synthetic exchangeable ground truth; validates the conformal core.

    The pooled bound's empirical violation rate on 2000 fresh instances must
    stay within a three-sigma tolerance of the marginal alpha, and the hostile
    (over-confident, 4x alpha) bound must violate strictly more.
    """
    rng = np.random.default_rng(20260827)
    n_train, n_cal, n_test, dims, n_actions = 200, 200, 2000, 10, 5
    features = rng.normal(size=(n_train + n_cal + n_test, dims))
    gradients = rng.normal(size=(n_actions, dims))
    offsets = rng.normal(size=n_actions)
    costs = features @ gradients.T + offsets[None, :] + rng.normal(
        scale=0.5, size=(n_train + n_cal + n_test, n_actions)
    )
    regret = costs - costs.min(axis=1)[:, None]
    train, cal, test = (
        features[:n_train],
        features[n_train : n_train + n_cal],
        features[n_train + n_cal :],
    )
    regret_train, regret_cal, regret_test = (
        regret[:n_train],
        regret[n_train : n_train + n_cal],
        regret[n_train + n_cal :],
    )

    m_cal, d1_cal, a_base_cal = neighborhood_predictor(
        train, regret_train, cal
    )
    m_test, d1_test, a_base_test = neighborhood_predictor(
        train, regret_train, test
    )
    scores = normalized_scores(m_cal, d1_cal, a_base_cal, regret_cal)
    q_hat, q_receipt = conformal_quantile(scores, 1.0 - ALPHA)
    bound = m_test[np.arange(n_test), a_base_test] + q_hat * (
        SIGMA_OFFSET + d1_test
    )
    realized = regret_test[np.arange(n_test), a_base_test]
    violations = int(np.sum(realized > bound + 1e-9))

    q_hostile, _ = conformal_quantile(
        scores, 1.0 - HOSTILE_ALPHA_FACTOR * ALPHA
    )
    hostile_bound = m_test[np.arange(n_test), a_base_test] + q_hostile * (
        SIGMA_OFFSET + d1_test
    )
    hostile_violations = int(np.sum(realized > hostile_bound + 1e-9))

    tolerance = ALPHA + 3.0 * math.sqrt(ALPHA * (1.0 - ALPHA) / n_test)
    if violations > tolerance * n_test:
        raise AssertionError(
            f"self-test failed: conformal violation rate "
            f"{violations / n_test:.4f} exceeds tolerance {tolerance:.4f}"
        )
    if hostile_violations <= violations:
        raise AssertionError(
            f"self-test failed: hostile control ({hostile_violations}) does "
            f"not exceed honest bound violations ({violations})"
        )

    # Hostile anchor-order control (issue #1495 repair gate): every recorded
    # d1 / q_hat / coverage value must be invariant to the ORDER of the
    # anchor rows. Protocol §4 defines d1(x) as the distance to the single
    # NEAREST anchor; a `distances[:, 0]` regression (distance to anchor
    # row 0) changes d1 under any non-identity anchor permutation and must
    # fail here, before any receipt is written.
    eps_check = float(np.median(bound))
    covered = bound <= eps_check
    invariance_orders = {
        "random": np.random.default_rng(20260828).permutation(n_train),
        "reversed": np.arange(n_train)[::-1],
    }
    for label, order in invariance_orders.items():
        m_cal_o, d1_cal_o, a_base_cal_o = neighborhood_predictor(
            train[order], regret_train[order], cal
        )
        m_test_o, d1_test_o, a_base_test_o = neighborhood_predictor(
            train[order], regret_train[order], test
        )
        if not (
            np.array_equal(d1_cal, d1_cal_o)
            and np.array_equal(d1_test, d1_test_o)
            and np.allclose(m_cal, m_cal_o, rtol=0.0, atol=1e-9)
            and np.allclose(m_test, m_test_o, rtol=0.0, atol=1e-9)
            and np.array_equal(a_base_cal, a_base_cal_o)
            and np.array_equal(a_base_test, a_base_test_o)
        ):
            raise AssertionError(
                "self-test failed: anchor-row permutation "
                f"({label}) changed d1/m/a_base — d1 is not the "
                "nearest-anchor distance"
            )
        scores_o = normalized_scores(
            m_cal_o, d1_cal_o, a_base_cal_o, regret_cal
        )
        q_hat_o, _ = conformal_quantile(scores_o, 1.0 - ALPHA)
        bound_o = m_test_o[np.arange(n_test), a_base_test_o] + q_hat_o * (
            SIGMA_OFFSET + d1_test_o
        )
        covered_o = bound_o <= eps_check
        if not (
            math.isclose(q_hat_o, q_hat, rel_tol=1e-12, abs_tol=1e-12)
            and np.allclose(bound, bound_o, rtol=0.0, atol=1e-9)
            and np.array_equal(covered, covered_o)
            and int(np.sum(realized > bound_o + 1e-9)) == violations
        ):
            raise AssertionError(
                "self-test failed: anchor-row permutation "
                f"({label}) changed q_hat/coverage/violations — recorded "
                "values must be anchor-order invariant"
            )
    return {
        "conformal_violations": violations,
        "conformal_violation_rate": violations / n_test,
        "tolerance": tolerance,
        "hostile_violations": hostile_violations,
        "q_hat": q_hat,
        "quantile_receipt": q_receipt,
        "n_test": n_test,
        "anchor_order_invariance": {
            "permutations": sorted(invariance_orders),
            "status": "GREEN",
        },
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
    if len(cal_rows) < MIN_CAL:
        raise ValueError(
            f"fail-closed: calibration count {len(cal_rows)} < {MIN_CAL}"
        )

    x_all = data["x"]
    phi_train, [phi_cal, phi_held] = impute_and_standardize(
        x_all[train_rows], [x_all[cal_rows], x_all[held_rows]]
    )

    regret = runtime - vbs_cost[:, None]
    regret_train = regret[train_rows]
    regret_cal = regret[cal_rows]

    sbs_solver = int(np.argmin(runtime[train_rows].mean(axis=0)))

    # KNN16 comparator (identical to V1: mean PAR10 over 16 neighbours)
    knn_k = min(KNN_K, len(train_rows))
    distances_full = pairwise_distances(phi_held, phi_train)
    neighbor_rows = np.argsort(distances_full, axis=1, kind="stable")[:, :knn_k]
    knn_action = np.argmin(
        runtime[train_rows][neighbor_rows].mean(axis=1), axis=1
    )

    # frozen RF router reused unchanged (harness impute-only featurization)
    x_train_imp, x_held_imp = harness.impute(
        x_all[train_rows], x_all[held_rows]
    )
    rf_action, _ = harness.fit_router(
        x_train_imp, runtime[train_rows], solved[train_rows], x_held_imp
    )

    # exact-equality control (identical to V1)
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

    # representations: NBR_FULL primary, NBR_PCA10 coarsening
    pca_receipt: dict[str, Any] = {}
    representations: dict[str, tuple[np.ndarray, np.ndarray, np.ndarray]] = {
        "NBR_FULL": (phi_train, phi_cal, phi_held)
    }
    if PCA_COMPONENTS > 0 and PCA_COMPONENTS < phi_train.shape[1]:
        pca = PCA(n_components=PCA_COMPONENTS, svd_solver="full")
        pca.fit(phi_train)
        representations["NBR_PCA10"] = (
            pca.transform(phi_train),
            pca.transform(phi_cal),
            pca.transform(phi_held),
        )
        pca_receipt = {
            "n_components": int(PCA_COMPONENTS),
            "explained_variance_ratio": [
                float(item) for item in pca.explained_variance_ratio_
            ],
        }

    # Mondrian cut points frozen on TRAIN nearest-other-anchor distances
    train_self = pairwise_distances(phi_train, phi_train)
    np.fill_diagonal(train_self, math.inf)
    cuts = mondrian_cut_points(train_self.min(axis=1))

    conformal_arms: dict[str, dict[str, Any]] = {}
    for representation_name, (train_phi, cal_phi, held_phi) in representations.items():
        m_cal, d1_cal, a_base_cal = neighborhood_predictor(
            train_phi, regret_train, cal_phi
        )
        m_held, d1_held, a_base_held = neighborhood_predictor(
            train_phi, regret_train, held_phi
        )
        scores = normalized_scores(m_cal, d1_cal, a_base_cal, regret_cal)
        q_hat, q_receipt = conformal_quantile(scores, 1.0 - ALPHA)
        q_hostile, hostile_receipt = conformal_quantile(
            scores, 1.0 - HOSTILE_ALPHA_FACTOR * ALPHA
        )
        sigma_held = SIGMA_OFFSET + d1_held
        base_held = m_held[np.arange(len(held_rows)), a_base_held]
        bound_held = base_held + q_hat * sigma_held
        bound_cal = (
            m_cal[np.arange(len(cal_rows)), a_base_cal]
            + q_hat * (SIGMA_OFFSET + d1_cal)
        )
        realized_cal = regret_cal[np.arange(len(cal_rows)), a_base_cal]
        realized_held = regret[held_rows, a_base_held]
        hostile_bound = base_held + q_hostile * sigma_held
        suffix = "" if representation_name == "NBR_FULL" else "_PCA10"
        conformal_arms[f"CNF_POOLED{suffix}"] = {
            "representation": representation_name,
            "action": a_base_held,
            "bound": bound_held,
            "receipt": {
                "q_hat_par10_per_distance_unit": q_hat,
                "q_hat_receipt": q_receipt,
                "q_hostile_par10_per_distance_unit": q_hostile,
                "q_hostile_receipt": hostile_receipt,
                "calibration_violation_rate": float(
                    np.mean(realized_cal > bound_cal + 1e-9)
                ),
                "heldout_violation_rate": float(
                    np.mean(realized_held > bound_held + 1e-9)
                ),
                "heldout_violation_wilson_95": wilson_interval(
                    int(np.sum(realized_held > bound_held + 1e-9)), len(held_rows)
                ),
                "hostile_violation_rate": float(
                    np.mean(realized_held > hostile_bound + 1e-9)
                ),
                "pca": pca_receipt if representation_name == "NBR_PCA10" else {},
                "covered_median_d1": None,
                "uncovered_median_d1": None,
            },
        }

    # Mondrian-by-distance arm on NBR_FULL
    m_cal, d1_cal, a_base_cal = neighborhood_predictor(
        phi_train, regret_train, phi_cal
    )
    m_held, d1_held, a_base_held = neighborhood_predictor(
        phi_train, regret_train, phi_held
    )
    strata_cal = mondrian_assign(d1_cal, cuts)
    strata_held = mondrian_assign(d1_held, cuts)
    scores = normalized_scores(m_cal, d1_cal, a_base_cal, regret_cal)
    mondrian_q: list[float] = []
    mondrian_receipt: dict[str, Any] = {"cut_points": cuts, "strata": {}}
    for stratum in range(MONDRIAN_STRATA):
        stratum_scores = scores[strata_cal == stratum]
        q_s, q_s_receipt = conformal_quantile(
            stratum_scores if len(stratum_scores) else np.asarray([math.inf]),
            1.0 - ALPHA,
        )
        mondrian_q.append(q_s)
        mondrian_receipt["strata"][f"stratum_{stratum}"] = {
            **q_s_receipt,
            "q_hat": q_s,
        }
    q_mondrian_held = np.asarray(mondrian_q)[strata_held]
    bound_mondrian_held = m_held[np.arange(len(held_rows)), a_base_held] + (
        SIGMA_OFFSET + d1_held
    ) * q_mondrian_held
    realized_held = regret[held_rows, a_base_held]
    conformal_arms["CNF_MONDRIAN3"] = {
        "representation": "NBR_FULL",
        "action": a_base_held,
        "bound": bound_mondrian_held,
        "receipt": {
            **mondrian_receipt,
            "heldout_violation_rate": float(
                np.mean(realized_held > bound_mondrian_held + 1e-9)
            ),
            "heldout_violation_wilson_95": wilson_interval(
                int(np.sum(realized_held > bound_mondrian_held + 1e-9)),
                len(held_rows),
            ),
        },
    }

    for arm in conformal_arms.values():
        covered = arm["bound"] <= PRIMARY_EPSILON
        arm["covered"] = covered
        nearest = pairwise_distances(
            representations[arm["representation"]][2],
            representations[arm["representation"]][0],
        ).min(axis=1)
        arm["receipt"]["covered_median_d1"] = (
            float(np.median(nearest[covered])) if covered.any() else None
        )
        arm["receipt"]["uncovered_median_d1"] = (
            float(np.median(nearest[~covered])) if (~covered).any() else None
        )
        arm["receipt"]["heldout_coverage"] = {
            f"epsilon_{epsilon:g}": float(np.mean(arm["bound"] <= epsilon))
            for epsilon in EPSILON_LEVELS
        }

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
    for arm_name, arm in conformal_arms.items():
        action = np.where(arm["covered"], arm["action"], sbs_solver).astype(int)
        arms_cost[arm_name] = runtime[held_rows, action]
        arms_solved[arm_name] = solved[held_rows, action]
        arms_attempt[arm_name] = arm["covered"]
    arms_cost["EXACT_EQ"] = runtime[held_rows, eq_action]
    arms_solved["EXACT_EQ"] = solved[held_rows, eq_action]
    arms_attempt["EXACT_EQ"] = eq_covered
    for name in ["SBS", "VBS", "RF_ROUTER", "KNN16"]:
        arms_attempt[name] = np.ones(len(held_rows), dtype=bool)

    metrics = {
        name: arm_metrics(
            arms_cost[name],
            arms_solved[name],
            arms_attempt[name],
            vbs_cost[held_rows],
        )
        for name in arms_cost
    }

    comparisons = {
        "sbs_minus_cnf_pooled": paired_bootstrap(
            arms_cost["SBS"], arms_cost["CNF_POOLED"], BOOTSTRAP_SEED
        ),
        "knn16_minus_cnf_pooled": paired_bootstrap(
            arms_cost["KNN16"], arms_cost["CNF_POOLED"], BOOTSTRAP_SEED + 1
        ),
        "rf_router_minus_cnf_pooled": paired_bootstrap(
            arms_cost["RF_ROUTER"], arms_cost["CNF_POOLED"], BOOTSTRAP_SEED + 2
        ),
    }

    primary = conformal_arms["CNF_POOLED"]
    q = float(np.mean(primary["covered"]))
    q_eq = float(np.mean(eq_covered))
    v = primary["receipt"]["heldout_violation_rate"]
    delta = comparisons["sbs_minus_cnf_pooled"]
    coverage_producing = q >= 0.10 and q >= 5.0 * q_eq
    bound_valid = v <= ALPHA
    value_over_fallback = (
        delta["estimate"] > 0.0
        and delta["paired_bootstrap_95_percent_interval"][0] > 0.0
    )
    if not bound_valid:
        verdict = "CONFORMAL_INVALID"
    elif delta["paired_bootstrap_95_percent_interval"][1] < 0.0:
        verdict = "ADVERSE"
    elif coverage_producing and value_over_fallback:
        verdict = "CONFORMAL_NEIGHBORHOOD_REVIVED"
    else:
        verdict = "VALID_WITHOUT_COVERAGE_OR_VALUE"

    relations_receipt = {
        name: arm["receipt"] for name, arm in conformal_arms.items()
    }
    for arm in conformal_arms.values():
        arm.pop("covered", None)

    return {
        "split": split_name,
        "split_receipt": {
            "dev_instances": int(dev_mask.sum()),
            "heldout_instances": int(held_mask.sum()),
            "dev_train_instances": int(len(train_rows)),
            "dev_calibration_instances": int(len(cal_rows)),
            "sbs_solver": data["algorithms"][sbs_solver],
            "knn_k": int(knn_k),
            "mu_k": int(min(MU_K, len(train_rows))),
            "rf_router_featurization": (
                "harness.impute (DEV-TRAIN median fill, no standardization)"
            ),
            **split_receipt_extra,
        },
        "metrics": metrics,
        "relations": relations_receipt,
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
            "alpha": ALPHA,
            "sbs_minus_cnf_pooled": delta,
        },
        "verdict": verdict,
    }


def display(value: float | None) -> str:
    return "—" if value is None else f"{value:.4f}"


def render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# ORION-02 C-NBR2 conformal certified neighborhood result",
        "",
        "> Generated by `experiments/certified_neighborhood_conformal.py` from",
        "> the frozen protocol. The JSON file is the machine-readable source of",
        "> truth.",
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
            "| Relation | Coverage @5000 | Violation rate | Wilson 95% | q_hat (PAR10/unit) | Hostile violation | covered/uncovered median d1 |",
            "|---|---:|---:|---|---:|---:|---|",
        ]
        for name, relation in split["relations"].items():
            coverage = relation.get("heldout_coverage", {}).get("epsilon_5000")
            wilson = relation["heldout_violation_wilson_95"]
            q_hat = relation.get("q_hat_par10_per_distance_unit")
            if q_hat is None and "strata" in relation:
                q_hat = min(
                    item["q_hat"] for item in relation["strata"].values()
                )
            lines.append(
                f"| {name} | {display(coverage)} | "
                f"{display(relation['heldout_violation_rate'])} | "
                f"[{wilson[0]:.4f}, {wilson[1]:.4f}] | "
                f"{display(q_hat)} | "
                f"{display(relation.get('hostile_violation_rate'))} | "
                f"{display(relation.get('covered_median_d1'))} / "
                f"{display(relation.get('uncovered_median_d1'))} |"
            )
        gates = split["gate_inputs"]
        lines += [
            "",
            f"Exact-equality control coverage: {gates['five_times_exact_eq'] / 5.0:.4f}"
            f" (5x = {gates['five_times_exact_eq']:.4f}); certified coverage"
            f" {gates['heldout_coverage_at_primary_epsilon']:.4f}.",
            f"SBS - CNF_POOLED: {gates['sbs_minus_cnf_pooled']['estimate']:.2f}"
            f" {gates['sbs_minus_cnf_pooled']['paired_bootstrap_95_percent_interval']}.",
            "",
        ]
    lines += [
        "## Interpretation boundary",
        "",
        "One bounded public scenario; no ASlib-wide, SAT-wide, cross-domain or",
        "selective-prediction superiority claim. The conformal bound carries a",
        "finite-sample marginal guarantee under exchangeability, not",
        "conditional-on-covariates validity. Certificate coverage is not action",
        "authority.",
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
        "schema": "ORION02.CNBR2.Result.v1",
        "protocol_sha256": sha256_file(PROTOCOL_PATH),
        "executor_sha256": sha256_file(Path(__file__).resolve()),
        "harness_protocol_sha256": sha256_file(harness.PROTOCOL_PATH),
        "source": {
            "repository": harness_protocol["source"]["repository"],
            "commit": harness_protocol["source"]["commit"],
            "scenario": harness_protocol["source"]["scenario"],
            "git_sha": os.environ.get("CNBR2_SOURCE_GIT_SHA", "UNBOUND"),
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
            "alpha": ALPHA,
            "mu_k": MU_K,
            "sigma_offset": SIGMA_OFFSET,
            "epsilon_levels": EPSILON_LEVELS,
            "primary_epsilon": PRIMARY_EPSILON,
            "mondrian_strata": MONDRIAN_STRATA,
            "hostile_alpha_factor": HOSTILE_ALPHA_FACTOR,
            "knn_k": KNN_K,
            "rf_trees": RF_TREES,
            "pca_components": PCA_COMPONENTS,
            "eq_round": EQ_ROUND,
            "min_cal": MIN_CAL,
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
    if splits[0]["verdict"] == splits[1]["verdict"]:
        overall = splits[0]["verdict"]
    else:
        overall = splits[1]["verdict"]
        result["overall_verdict_note"] = (
            "splits disagree; SPLIT_FAMILY_DISJOINT governs per protocol §8 "
            f"(fold: {splits[0]['verdict']}, family-disjoint: {splits[1]['verdict']})"
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
    print(
        json.dumps(
            {
                "overall_verdict": overall,
                "split_verdicts": [s["verdict"] for s in splits],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
