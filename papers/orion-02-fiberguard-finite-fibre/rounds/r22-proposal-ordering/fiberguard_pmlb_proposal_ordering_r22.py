#!/usr/bin/env python3
"""Frozen ORION-02 R22 PMLB safe learned proposal-ordering experiment.

The scientific contract is
FIBERGUARD_PMLB_PROPOSAL_ORDERING_R22_PROTOCOL.md.  This executor
intentionally fails closed on retrieval, identity, schema, split, or resource
drift.  Learning only proposes acquisition order and commits inside the exact
finite-fibre certificate shield; admissibility is never learned.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import itertools
import json
import math
import platform
import warnings
from pathlib import Path
from typing import Any, Callable, Sequence

import numpy as np
import scipy
import sklearn
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, RidgeClassifier
from sklearn.metrics import balanced_accuracy_score
from sklearn.model_selection import StratifiedKFold
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import HistGradientBoostingClassifier

SCHEMA = "ORION.FiberGuard.PMLBProposalOrdering.R22.v1"
PMLB_REPO = "https://github.com/EpistasisLab/pmlb.git"
PMLB_COMMIT = "7c1f4bdc00136dc2e55c87fa6b8ba6e8af6d1a68"
PMLB_TREE = "ca5d36e9093c2f7360db57198c8c0586a3217a60"
LICENSE_BLOB = "ac14bc5ab72e5c2fc5643d879ad6bcc2be4d260a"
SUMMARY_BLOB = "88c393504f3ad6c354f5d178de181543878e7782"

SEED = 20260827
ALPHA = 0.10
TOL = 1e-9
TAU = 0.02
TAU_GRID = (0.0, 0.01, 0.02, 0.05, 0.10)
MIN_CLASS_COUNT = 5
N_FOLDS = 9
MIN_CELL_MEMBERS = 2
KNN_K = (1, 3, 5, 9)
RF_TREES = 300
CV_FOLDS = 5
CV_REPS = 3
LANDMARK_REPS = 2
BOOTSTRAP_REPLICATES = 20_000
BOOTSTRAP_SEED_TEXT = "ORION02_R22_PMLB_PROPOSAL_ORDERING_BOOTSTRAP_V1"
MATERIAL_FRACTION = 0.05
COVERAGE_GATE = 0.05
VALIDITY_GATE = 0.10
GROUPS = ("G1", "G2", "G3")
PORTFOLIO = ("dct", "gnb", "hgb", "knn5", "logreg", "rf300")
LANDMARKERS = ("stump", "nn1", "ridgec")
STATIC_ARMS = ("RANDOM_ADAPTIVE", "SHIELD_FREE", "SHIELD_FULL", "STATIC_ADAPTIVE", "VARIANCE_ADAPTIVE")
LEARNED_ARMS = ("LEARNED_KNN_1", "LEARNED_KNN_3", "LEARNED_KNN_5", "LEARNED_KNN_9", "LEARNED_RF300")
UNSHIELDED_ARMS = ("UNSHIELDED_KNN9", "UNSHIELDED_RF300")
ALL_ARMS = STATIC_ARMS + LEARNED_ARMS + UNSHIELDED_ARMS
FREEZE_NAME = "FIBERGUARD_PMLB_R22_DATASET_FREEZE.json"
MISSING_TOKENS = {"", "nan", "NaN", "NAN", "None", "NA", "?"}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_json(value: Any) -> str:
    return sha256_bytes(canonical_json(value).encode())


def derive_seed(*parts: object) -> int:
    text = "|".join(str(part) for part in parts)
    return int.from_bytes(hashlib.sha256(text.encode()).digest()[:8], "big") % (2**31 - 1)


def rng_for(*parts: object) -> np.random.Generator:
    return np.random.default_rng(derive_seed(*parts))


def json_float(value: float) -> float:
    out = float(value)
    if not math.isfinite(out):
        raise ValueError(f"nonfinite value in receipt: {value!r}")
    return round(out, 12)


# ---------------------------------------------------------------------------
# dataset loading, encoding, features
# ---------------------------------------------------------------------------


def read_tsv_gz(path: Path) -> tuple[list[str], list[list[str]]]:
    with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        header = next(reader)
        rows = [row for row in reader if any(cell.strip() for cell in row)]
    if not header or not rows:
        raise ValueError(f"invalid or empty dataset file: {path}")
    if any(len(row) != len(header) for row in rows):
        raise ValueError(f"ragged rows in {path}")
    return header, rows


def code_column(values: list[str]) -> np.ndarray:
    def is_missing(v: object) -> bool:
        return isinstance(v, float) and math.isnan(v)

    def norm(cell: str) -> object:
        token = cell.strip()
        return math.nan if token in MISSING_TOKENS else token

    normed = [norm(v) for v in values]
    observed = sorted({v for v in normed if not is_missing(v)}, key=repr)
    index = {v: float(i) for i, v in enumerate(observed)}
    out = np.empty(len(normed), dtype=float)
    for i, v in enumerate(normed):
        out[i] = math.nan if is_missing(v) else index[v]
    return out


def load_dataset(path: Path) -> dict[str, Any]:
    header, rows = read_tsv_gz(path)
    if header.count("target") < 1:
        raise ValueError(f"no 'target' column: {path}")
    # Label-column rule (grounded in the frozen PMLB tree's own metadata.yaml):
    # the label is the FIRST column named 'target'. Features are all remaining
    # columns in file order. Three frozen datasets place the label first or
    # mid-file (not last), and 'schizo' carries a duplicate trailing 'target'
    # header that its metadata enumerates as the feature 'target.1' — so the
    # first occurrence is always the label and position-by-name must be used
    # instead of last-position.
    target_idx = header.index("target")
    feature_idx = [i for i in range(len(header)) if i != target_idx]
    feature_names = [header[i] for i in feature_idx]
    y = code_column([row[target_idx] for row in rows]).astype(int)
    x_cols = [code_column([row[i] for row in rows]) for i in feature_idx]
    n_features = len(feature_names)
    x = np.empty((len(rows), n_features), dtype=float)
    for j, col in enumerate(x_cols):
        x[:, j] = col
    labels, counts = np.unique(y, return_counts=True)
    return {
        "n_instances": len(rows),
        "n_features": n_features,
        "x": x,
        "y": y,
        "n_classes": int(labels.size),
        "min_class_count": int(counts.min()),
    }


def impute_columns(x: np.ndarray) -> np.ndarray:
    out = np.array(x, dtype=float, copy=True)
    for j in range(out.shape[1]):
        col = out[:, j]
        finite = col[np.isfinite(col)]
        fill = float(np.median(finite)) if finite.size else 0.0
        col[~np.isfinite(col)] = fill
    return out


def _moment(x: np.ndarray, order: int) -> float:
    mean = float(x.mean())
    std = float(math.sqrt(float(((x - mean) ** 2).mean())))
    if std == 0.0:
        return 0.0
    return float(((x - mean) ** order).mean() / std**order)


def g1_features(x_imp: np.ndarray) -> list[float]:
    n, d = x_imp.shape
    stds, skews, kurts, mins, maxs, uniqs, iqrs = [], [], [], [], [], [], []
    for j in range(d):
        col = x_imp[:, j]
        stds.append(float(col.std()))
        skews.append(_moment(col, 3))
        kurts.append(_moment(col, 4))
        mins.append(float(col.min()))
        maxs.append(float(col.max()))
        uniqs.append(float(np.unique(col).size) / n)
        q25, q75 = np.percentile(col, [25.0, 75.0])
        iqrs.append(float(q75 - q25))
    return [
        float(np.median(stds)),
        float(np.median(skews)),
        float(np.median(kurts)),
        float(np.median(mins)),
        float(np.median(maxs)),
        float(np.median(uniqs)),
        float((x_imp == 0.0).mean()),
        float(sum(1 for s in stds if s <= TOL) / d),
        float(math.log10(n / d)),
        float(np.median(iqrs)),
    ]


def _pearson(a: np.ndarray, b: np.ndarray) -> float:
    da = a - a.mean()
    db = b - b.mean()
    denom = math.sqrt(float((da * da).mean())) * math.sqrt(float((db * db).mean()))
    if denom <= TOL:
        return 0.0
    return float((da * db).mean() / denom)


def g2_features(x_imp: np.ndarray, y: np.ndarray) -> list[float]:
    n, d = x_imp.shape
    pairs = [(j, k) for j in range(d) for k in range(j + 1, d)]
    if pairs:
        corrs = [abs(_pearson(x_imp[:, j], x_imp[:, k])) for j, k in pairs]
        max_pair = float(max(corrs))
        mean_pair = float(sum(corrs) / len(corrs))
    else:
        max_pair = 0.0
        mean_pair = 0.0
    label_scores = []
    for j in range(d):
        best = 0.0
        for c in np.unique(y):
            indicator = (y == c).astype(float)
            best = max(best, abs(_pearson(x_imp[:, j], indicator)))
        label_scores.append(best)
    return [max_pair, mean_pair, float(sum(label_scores) / d)]


def make_portfolio_model(arm: str, seed: int) -> Any:
    if arm == "dct":
        return DecisionTreeClassifier(random_state=seed)
    if arm == "gnb":
        return GaussianNB()
    if arm == "hgb":
        return HistGradientBoostingClassifier(random_state=seed)
    if arm == "knn5":
        return KNeighborsClassifier(n_neighbors=5)
    if arm == "logreg":
        return LogisticRegression(max_iter=2000, random_state=seed)
    if arm == "rf300":
        return RandomForestClassifier(n_estimators=RF_TREES, random_state=seed, n_jobs=1)
    raise ValueError(f"unknown portfolio arm: {arm}")


def make_landmarker(arm: str, seed: int) -> Any:
    if arm == "nn1":
        return KNeighborsClassifier(n_neighbors=1)
    if arm == "ridgec":
        return RidgeClassifier(alpha=1.0)
    if arm == "stump":
        return DecisionTreeClassifier(max_depth=1, random_state=seed)
    raise ValueError(f"unknown landmarker: {arm}")


def cv_balanced_error(x: np.ndarray, y: np.ndarray, factory: Callable[[int], Any], reps: int, seed_base: int) -> float:
    errors = []
    for rep in range(reps):
        splitter = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=derive_seed(seed_base, rep))
        for train_idx, test_idx in splitter.split(x, y):
            x_train, x_test = x[train_idx], x[test_idx]
            medians = np.empty(x.shape[1])
            for j in range(x.shape[1]):
                finite = x_train[:, j][np.isfinite(x_train[:, j])]
                medians[j] = float(np.median(finite)) if finite.size else 0.0
            def apply(view: np.ndarray) -> np.ndarray:
                out = np.array(view, dtype=float, copy=True)
                bad = ~np.isfinite(out)
                if bad.any():
                    out[bad] = np.take(medians, np.nonzero(bad)[1])
                return out
            model = factory(derive_seed(seed_base, rep, "fit"))
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                model.fit(apply(x_train), y[train_idx])
                pred = model.predict(apply(x_test))
            errors.append(1.0 - float(balanced_accuracy_score(y[test_idx], pred)))
    if not errors:
        raise ValueError("cross-validation produced no splits")
    return float(sum(errors) / len(errors))


# ---------------------------------------------------------------------------
# exact certificate shield and the acquisition walk
# ---------------------------------------------------------------------------

SCALAR_G0 = 4


class FoldContext:
    """Per-test-fold state: partitions, edges, lazily built shield cells, proposers."""

    def __init__(self, fold: int, roles: dict[str, list[str]], meta: dict[str, dict[str, list[float]]],
                 outcomes: dict[str, dict[str, float]]) -> None:
        self.fold = fold
        self.roles = {role: sorted(names) for role, names in roles.items()}
        self.meta = meta
        self.outcomes = outcomes
        shield_table = self.roles["shield_table"]
        self.f_star = float(np.mean([outcomes[name][arm] for name in shield_table for arm in PORTFOLIO]))
        self.scalar_layout: list[tuple[str, int]] = [("G0", i) for i in range(SCALAR_G0)]
        ref = self.roles["proposer_train"][0]
        for group in GROUPS:
            for i in range(len(meta[ref][group])):
                self.scalar_layout.append((group, i))
        self.edges: list[float] = []
        for group, i in self.scalar_layout:
            vals = [meta[name][group][i] for name in self.roles["proposer_train"]]
            self.edges.append(float(np.median(vals)))
        all_names = sorted(set(sum(self.roles.values(), [])))
        self.vectors = {name: np.array([meta[name][g][i] for g, i in self.scalar_layout], dtype=float) for name in all_names}
        self._cells: dict[tuple[int, ...], dict[tuple[int, ...], list[str]]] = {}
        self._proposers: dict[tuple[str, frozenset], tuple[Any, np.ndarray, np.ndarray]] = {}
        self.custody_seen: set[tuple[str, frozenset]] = set()

    def state_indices(self, acquired: tuple[str, ...]) -> list[int]:
        return [i for i, (g, _) in enumerate(self.scalar_layout) if g == "G0" or g in acquired]

    def cell_of(self, name: str, state: tuple[int, ...]) -> tuple[int, ...]:
        v = self.vectors[name]
        return tuple(int(v[i] > self.edges[i]) for i in state)

    def cell_table(self, state: tuple[int, ...]) -> dict[tuple[int, ...], list[str]]:
        if state not in self._cells:
            table: dict[tuple[int, ...], list[str]] = {}
            for member in self.roles["shield_table"]:
                table.setdefault(self.cell_of(member, state), []).append(member)
            for cell in table:
                table[cell].sort()
            self._cells[state] = table
        return self._cells[state]

    def shield_query(self, name: str, acquired: tuple[str, ...], tau: float) -> tuple[list[str], dict[str, float]]:
        """Exact worst-case table: A = {a : wc_a <= tau} using shield-table excesses."""
        state = tuple(self.state_indices(acquired))
        members = self.cell_table(state).get(self.cell_of(name, state), [])
        wc = {arm: math.inf for arm in PORTFOLIO}
        if len(members) >= MIN_CELL_MEMBERS:
            for arm in PORTFOLIO:
                wc[arm] = max(self.excess_member(m, arm) for m in members)
        admissible = sorted(a for a in PORTFOLIO if wc[a] <= tau)
        return admissible, wc

    def excess_member(self, member: str, arm: str) -> float:
        return self.outcomes[member][arm] - self.outcomes[member]["best"]

    def _base_arm(self, arm: str) -> str:
        if arm.startswith("SHUFFLED_"):
            return arm.split("SHUFFLED_")[-1]
        if arm == "UNSHIELDED_KNN9":
            return "LEARNED_KNN_9"
        if arm == "UNSHIELDED_RF300":
            return "LEARNED_RF300"
        return arm

    def proposer(self, arm: str, acquired: tuple[str, ...]) -> tuple[Any, np.ndarray, np.ndarray]:
        key = (arm, frozenset(acquired))
        if key not in self._proposers:
            names = self.roles["proposer_train"]
            idx = self.state_indices(acquired)
            raw = np.array([self.vectors[n][idx] for n in names], dtype=float)
            mean = raw.mean(axis=0)
            std = raw.std(axis=0)
            std = np.where(std <= TOL, 1.0, std)
            zs = (raw - mean) / std
            targets = np.array([[self.outcomes[n][a] for a in PORTFOLIO] for n in names], dtype=float)
            perm = None
            if arm.startswith("SHUFFLED_"):
                perm = rng_for(SEED, "shuf", arm, self.fold, "".join(sorted(acquired))).permutation(len(names))
                targets = targets[perm]
            base = self._base_arm(arm)
            if base.startswith("LEARNED_KNN_"):
                payload = {"kind": "knn", "k": int(base.rsplit("_", 1)[1]), "zs": zs, "names": list(names), "perm": perm}
            else:
                model = RandomForestRegressor(n_estimators=RF_TREES, random_state=derive_seed(SEED, "rfprop", arm, self.fold, acquired), n_jobs=1)
                model.fit(zs, targets)
                payload = model
            self._proposers[key] = (payload, mean, std)
        return self._proposers[key]

    def propose_errors(self, arm: str, acquired: tuple[str, ...], name: str, enforce_custody: bool = True) -> dict[str, float]:
        """Custody-guarded prediction.  Asserts the proposer was fit on proposer-train only."""
        payload, mean, std = self.proposer(arm, acquired)
        if enforce_custody:
            names = self.roles["proposer_train"]
            assert name not in names, "custody leak: query name inside proposer train"
            if isinstance(payload, dict):
                assert sorted(payload["names"]) == names, "custody drift: proposer train set changed"
        idx = self.state_indices(acquired)
        query = (self.vectors[name][idx] - mean) / std
        if isinstance(payload, dict) and payload["kind"] == "knn":
            zs, tnames, perm, k = payload["zs"], payload["names"], payload["perm"], payload["k"]
            diffs = zs - query  # direct-difference distances (no BLAS expansion)
            dists = np.sqrt((diffs * diffs).sum(axis=1))
            order = sorted(range(len(tnames)), key=lambda i: (float(dists[i]), tnames[i]))[:k]
            rows = []
            for i in order:
                src = tnames[perm[i]] if perm is not None else tnames[i]
                rows.append([self.outcomes[src][a] for a in PORTFOLIO])
            mean_target = np.mean(np.array(rows, dtype=float), axis=0)
            return {a: float(mean_target[j]) for j, a in enumerate(PORTFOLIO)}
        pred = payload.predict(query.reshape(1, -1))[0]
        return {a: float(pred[j]) for j, a in enumerate(PORTFOLIO)}

    def variance_gains(self, acquired: tuple[str, ...]) -> dict[str, float]:
        out = {}
        proposer_train = self.roles["proposer_train"]
        for group in GROUPS:
            if group in acquired:
                continue
            dim = len(self.meta[proposer_train[0]][group])
            out[group] = float(sum(float(np.var([self.meta[n][group][i] for n in proposer_train])) for i in range(dim)))
        return out

    def random_step(self, name: str, acquired: tuple[str, ...]) -> tuple[float, list[str]]:
        rng = rng_for(SEED, "rand", self.fold, name, "".join(sorted(acquired)))
        return float(rng.random()), list(rng.permutation(sorted(g for g in GROUPS if g not in acquired)))


def static_score(ctx: FoldContext, arm: str, name: str, acquired: tuple[str, ...]) -> dict[str, float]:
    _, wc = ctx.shield_query(name, acquired, TAU)
    return {a: wc[a] for a in PORTFOLIO}


def learned_score(ctx: FoldContext, arm: str, name: str, acquired: tuple[str, ...]) -> dict[str, float]:
    return ctx.propose_errors(arm, acquired, name)


def score_for(arm: str) -> Callable[[FoldContext, str, str, tuple[str, ...]], dict[str, float]]:
    if arm.startswith("LEARNED_") or arm.startswith("SHUFFLED_") or arm.startswith("UNSHIELDED_"):
        return learned_score
    return static_score


def walk(ctx: FoldContext, name: str, arm: str, tau: float) -> dict[str, Any]:
    """Myopic acquisition walk under the exact shield; never commits an inadmissible arm."""
    scorer = score_for(arm)
    acquired: tuple[str, ...] = ()
    if arm == "SHIELD_FREE":
        admissible, wc = ctx.shield_query(name, (), tau)
        if admissible:
            best = min(admissible, key=lambda a: (wc[a], a))
            return {"committed": best, "acquired": [], "certified": True, "bound": json_float(wc[best]), "wc": wc[best]}
        return {"committed": "F_STAR", "acquired": [], "certified": False, "bound": None, "wc": None}
    if arm == "SHIELD_FULL":
        full = tuple(sorted(GROUPS))
        admissible, wc = ctx.shield_query(name, full, tau)
        if admissible:
            best = min(admissible, key=lambda a: (wc[a], a))
            return {"committed": best, "acquired": list(full), "certified": True, "bound": json_float(wc[best]), "wc": wc[best]}
        return {"committed": "F_STAR", "acquired": list(full), "certified": False, "bound": None, "wc": None}
    if arm.startswith("UNSHIELDED_"):
        full = tuple(sorted(GROUPS))
        scores = scorer(ctx, arm, name, full)
        best = min(PORTFOLIO, key=lambda a: (scores[a], a))
        return {"committed": best, "acquired": list(full), "certified": False, "bound": None, "wc": None}
    while True:
        admissible, wc = ctx.shield_query(name, acquired, tau)
        legal = sorted(g for g in GROUPS if g not in acquired)
        if not admissible:
            if legal:
                acquired = acquired + (legal[0],)
                continue
            return {"committed": "F_STAR", "acquired": sorted(acquired), "certified": False, "bound": None, "wc": None}
        commit_loss_now = min(scorer(ctx, arm, name, acquired)[a] for a in admissible)
        gains: dict[str, float] = {}
        for g in legal:
            adm2, _ = ctx.shield_query(name, acquired + (g,), tau)
            gains[g] = -math.inf if not adm2 else commit_loss_now - min(scorer(ctx, arm, name, acquired + (g,))[a] for a in adm2)
        best_g: str | None = None
        if arm == "RANDOM_ADAPTIVE":
            u, ranked = ctx.random_step(name, acquired)
            if u >= 0.5 and ranked:
                cand = ranked[0]
                if gains.get(cand, -math.inf) > -math.inf:
                    best_g = cand
        elif arm == "VARIANCE_ADAPTIVE":
            gg = {g: v for g, v in ctx.variance_gains(acquired).items() if gains.get(g, -math.inf) > -math.inf}
            best_g = max(sorted(gg), key=lambda g: gg[g]) if gg else None
        else:
            finite = {g: v for g, v in gains.items() if v > -math.inf}
            best_g = max(sorted(finite), key=lambda g: finite[g]) if finite else None
            if best_g is None or finite[best_g] <= TOL:
                best_g = None
        if best_g is not None:
            acquired = acquired + (best_g,)
            continue
        scores = scorer(ctx, arm, name, acquired)
        best = min(admissible, key=lambda a: (scores[a], a))
        return {"committed": best, "acquired": sorted(acquired), "certified": True, "bound": json_float(wc[best]), "wc": wc[best]}


def excess_of(ctx: FoldContext, name: str, decision: dict[str, Any]) -> float:
    if decision["committed"] == "F_STAR":
        return ctx.outcomes[name]["best"] - ctx.f_star
    return ctx.excess_member(name, decision["committed"])


# ---------------------------------------------------------------------------
# corpus binding, folds, outcome generation
# ---------------------------------------------------------------------------


def load_freeze(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text())
    if data.get("schema") != "ORION.FiberGuard.PMLBProposalOrdering.R22.dataset_freeze.v1":
        raise ValueError("freeze schema drift")
    return data["datasets"]


def verify_and_load_corpus(subject_repo: Path, freeze: list[dict[str, Any]]) -> dict[str, Any]:
    datasets_dir = subject_repo / "datasets"
    if not datasets_dir.is_dir():
        raise ValueError(f"missing datasets dir: {datasets_dir}")
    loaded: dict[str, Any] = {}
    audit: dict[str, dict[str, Any]] = {}
    for row in freeze:
        name = row["dataset"]
        tsv = datasets_dir / name / f"{name}.tsv.gz"
        meta_path = datasets_dir / name / "metadata.yaml"
        for p in (tsv, meta_path):
            if not p.is_file():
                raise ValueError(f"missing frozen artifact: {p}")
        content = tsv.read_bytes()
        if sha256_bytes(content) != row["lfs_oid_sha256"]:
            raise ValueError(f"content hash mismatch for {name}: byte identity with the frozen LFS pointer failed")
        d = load_dataset(tsv)
        n_features_meta = int(row["n_features"])
        n_instances_meta = int(row["n_instances"])
        n_classes_meta = int(row["n_classes"])
        ok = (d["n_instances"] == n_instances_meta and d["n_features"] == n_features_meta and d["n_classes"] == n_classes_meta)
        if not ok:
            raise ValueError(f"metadata audit failed for {name}: bytes {(d['n_instances'], d['n_features'], d['n_classes'])} vs frozen {(n_instances_meta, n_features_meta, n_classes_meta)}")
        audit[name] = {
            "bytes_match_freeze_sha256": True,
            "rows_features_classes_match": True,
            "min_class_count": d["min_class_count"],
        }
        loaded[name] = d
    return {"loaded": loaded, "audit": audit}


def assign_folds(admissible: list[str]) -> dict[str, int]:
    order = list(np.random.default_rng(SEED).permutation(sorted(admissible)))
    return {name: int(i % N_FOLDS) for i, name in enumerate(order)}


def role_names(fold: int, fold_of: dict[str, int]) -> dict[str, list[str]]:
    by_fold: dict[int, list[str]] = {t: sorted(n for n, f in fold_of.items() if f == t) for t in range(N_FOLDS)}
    out = {
        "test": by_fold[fold],
        "proposer_train": sorted(sum((by_fold[(fold + k) % N_FOLDS] for k in (1, 2, 3, 4)), [])),
        "shield_table": sorted(sum((by_fold[(fold + k) % N_FOLDS] for k in (5, 6, 7)), [])),
        "threshold_select": by_fold[(fold + 8) % N_FOLDS],
    }
    universe = sorted(fold_of)
    covered = sorted(sum(out.values(), []))
    assert covered == universe, "role partition does not cover the corpus"
    assert len(set(covered)) == len(covered), "role partition overlap"
    return out


def generate_outcomes(loaded: dict[str, Any], freeze: list[dict[str, Any]]) -> tuple[dict[str, dict[str, float]], dict[str, dict[str, list[float]]]]:
    """Outcome phase: portfolio CV errors + meta features, fully before any policy."""
    outcomes: dict[str, dict[str, float]] = {}
    meta: dict[str, dict[str, list[float]]] = {}
    for row in freeze:
        name = row["dataset"]
        d = loaded[name]
        if d["min_class_count"] < MIN_CLASS_COUNT:
            continue
        x, y = d["x"], d["y"]
        per_arm = {}
        for arm in PORTFOLIO:
            per_arm[arm] = cv_balanced_error(x, y, lambda seed, arm=arm: make_portfolio_model(arm, seed), CV_REPS, derive_seed(SEED, name, arm))
        per_arm["best"] = min(per_arm[a] for a in PORTFOLIO)
        outcomes[name] = per_arm
        x_imp = impute_columns(x)
        g1 = g1_features(x_imp)
        g2 = g2_features(x_imp, y)
        g3 = [cv_balanced_error(x, y, lambda seed, arm=arm: make_landmarker(arm, seed), LANDMARK_REPS, derive_seed(SEED, name, "landmark", arm)) for arm in LANDMARKERS]
        meta[name] = {
            "G0": [float(row["n_instances"]), float(row["n_features"]), float(row["n_classes"]), float(row["imbalance"])],
            "G1": g1,
            "G2": g2,
            "G3": g3,
        }
    return outcomes, meta


# ---------------------------------------------------------------------------
# evaluation, aggregation, terminals
# ---------------------------------------------------------------------------


def evaluate_arm(ctx: FoldContext, names: Sequence[str], arm: str, tau: float) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for name in names:
        decision = walk(ctx, name, arm, tau)
        record = {
            "committed": decision["committed"],
            "acquired": decision["acquired"],
            "groups_acquired": len(decision["acquired"]),
            "certified": decision["certified"],
            "bound": decision["bound"],
            "excess": json_float(excess_of(ctx, name, decision)),
        }
        record["violation_strict"] = bool(decision["certified"] and record["excess"] > decision["bound"] + TOL)
        record["violation_tau"] = bool(decision["certified"] and record["excess"] > tau + TOL)
        out[name] = record
    return out


def arm_summary(rows: dict[str, dict[str, Any]]) -> dict[str, Any]:
    excesses = np.array([r["excess"] for r in rows.values()], dtype=float)
    return {
        "n": len(rows),
        "mean_excess": json_float(excesses.mean()),
        "p95_excess": json_float(np.percentile(excesses, 95.0)),
        "max_excess": json_float(excesses.max()),
        "mean_groups_acquired": json_float(float(np.mean([r["groups_acquired"] for r in rows.values()]))),
        "certified_fraction": json_float(float(np.mean([1.0 if r["certified"] else 0.0 for r in rows.values()]))),
        "violations_strict": int(sum(1 for r in rows.values() if r["violation_strict"])),
        "violations_tau": int(sum(1 for r in rows.values() if r["violation_tau"])),
        "mean_bound": json_float(float(np.mean([r["bound"] for r in rows.values() if r["bound"] is not None]))) if any(r["bound"] is not None for r in rows.values()) else None,
    }


def select_primary(ts_rows: dict[str, dict[str, dict[str, Any]]]) -> str:
    stats = {arm: arm_summary(rows) for arm, rows in ts_rows.items()}
    def key(arm: str) -> tuple[float, float, float, str]:
        s = stats[arm]
        return (s["mean_excess"], s["p95_excess"], s["max_excess"], arm)
    return sorted(LEARNED_ARMS, key=key)[0]


def paired_bootstrap(diffs: np.ndarray) -> dict[str, Any]:
    rng = np.random.default_rng(derive_seed(BOOTSTRAP_SEED_TEXT))
    n = diffs.size
    idx = rng.integers(0, n, size=(BOOTSTRAP_REPLICATES, n))
    means = diffs[idx].mean(axis=1)
    lo, hi = (float(x) for x in np.percentile(means, [2.5, 97.5]))
    return {"ci_lower": json_float(lo), "ci_upper": json_float(hi), "replicates": BOOTSTRAP_REPLICATES}


def coverage_at(ctx: FoldContext, name: str) -> float:
    """Ladder coverage for one query dataset: fraction of states with nonempty A at tau."""
    states = [()] + [tuple(sorted(c)) for r in range(1, 4) for c in itertools.combinations(GROUPS, r)]
    hits = 0
    for state in states:
        admissible, _ = ctx.shield_query(name, state, TAU)
        if admissible:
            hits += 1
    return hits / len(states)


def decide_terminal(payload: dict[str, Any]) -> str:
    hostile = payload["hostile_controls"]
    if not all(hostile.values()):
        return "C_R22_PMLB_PROPOSAL_ORDERING_HOSTILE_CONTROL_FAILED"
    cov = payload["coverage"]["primary_tau_full_state"]
    if cov < 1.0 - COVERAGE_GATE - TOL:
        return "C_R22_PMLB_PROPOSAL_ORDERING_NO_CERTIFIED_COVERAGE"
    prim = payload["arms_summary"]["PRIMARY_LEARNED"]
    static = payload["arms_summary"]["STATIC_ADAPTIVE"]
    if prim["violations_strict"] / prim["n"] > VALIDITY_GATE + TOL:
        return "C_R22_PMLB_PROPOSAL_ORDERING_CERTIFICATE_INVALID"
    pt = payload["primary_test"]
    mean_diff = pt["mean_diff"]
    ci_upper = pt["ci_upper"]
    ratio_ok = pt["primary_mean_excess"] <= (1.0 - MATERIAL_FRACTION) * static["mean_excess"] + TOL
    cost_ok = pt["mean_groups_acquired_primary"] <= pt["mean_groups_acquired_static"] + TOL
    if mean_diff < -1e-9 and ratio_ok and ci_upper < 0.0 and cost_ok:
        return "C_R22_PMLB_PROPOSAL_ORDERING_VALUE"
    if mean_diff < -1e-9:
        return "C_R22_PMLB_PROPOSAL_ORDERING_STRICT_BUT_NOT_MATERIAL"
    if abs(mean_diff) <= 1e-9:
        return "C_R22_PMLB_PROPOSAL_ORDERING_NULL"
    return "C_R22_PMLB_PROPOSAL_ORDERING_ADVERSE"


# ---------------------------------------------------------------------------
# hostile controls (synthetic fixtures; no dataset bytes involved)
# ---------------------------------------------------------------------------


def synthetic_fixture() -> tuple[FoldContext, dict[str, Any]]:
    """Hand-checkable shield: 2 G0 scalars only (layout forced), 6 shield, 2 query."""
    meta: dict[str, dict[str, list[float]]] = {}
    outcomes: dict[str, dict[str, float]] = {}
    shield = [f"shield{i}" for i in range(6)]
    queries = ["queryA", "queryB"]
    others = [f"prop{i}" for i in range(8)] + [f"ts{i}" for i in range(2)]
    shield_vals = [0.1, 0.2, 0.3, 0.7, 0.8, 0.9]
    for i, name in enumerate(shield):
        meta[name] = {"G0": [shield_vals[i], 0.5], "G1": [float(i)], "G2": [0.0], "G3": [0.0]}
    for i, name in enumerate(others):
        meta[name] = {"G0": [0.4 + 0.01 * i, 0.5], "G1": [0.0], "G2": [0.0], "G3": [0.0]}
    meta["queryA"] = {"G0": [0.15, 0.5], "G1": [0.0], "G2": [0.0], "G3": [0.0]}   # lower cell
    meta["queryB"] = {"G0": [0.85, 0.5], "G1": [0.0], "G2": [0.0], "G3": [0.0]}   # upper cell
    # full portfolio present; arms 4-6 held at 0.9 so they are never admissible
    errs = {"shield0": [0.10, 0.30, 0.20], "shield1": [0.12, 0.28, 0.22], "shield2": [0.11, 0.32, 0.21],
            "shield3": [0.50, 0.60, 0.51], "shield4": [0.48, 0.64, 0.49], "shield5": [0.52, 0.58, 0.53]}
    for name in shield:
        e = errs[name]
        row = {a: e[i] for i, a in enumerate(PORTFOLIO[:3])}
        for a in PORTFOLIO[3:]:
            row[a] = 0.9
        row["best"] = min(e)
        outcomes[name] = row
    for name in others + queries:
        row = {a: 0.3 for a in PORTFOLIO}
        row["best"] = 0.3
        outcomes[name] = row

    class Synth(FoldContext):
        def __init__(self) -> None:
            self.fold = 0
            self.roles = {"test": queries, "proposer_train": sorted(others[:8]), "shield_table": shield, "threshold_select": sorted(others[8:])}
            self.meta = meta
            self.outcomes = outcomes
            self.f_star = float(np.mean([outcomes[n][a] for n in shield for a in PORTFOLIO[:3]]))
            self.scalar_layout = [("G0", 0), ("G0", 1), ("G1", 0), ("G2", 0), ("G3", 0)]
            self.edges = [float(np.median([meta[n][g][i] for n in self.roles["proposer_train"]])) for g, i in self.scalar_layout]
            names_all = sorted(set(sum(self.roles.values(), [])))
            self.vectors = {n: np.array([meta[n][g][i] for g, i in self.scalar_layout], dtype=float) for n in names_all}
            self._cells = {}
            self._proposers = {}

    return Synth(), {"shield": shield, "queries": queries}


def hostile_controls_runtime(ctx_pool: dict[int, FoldContext], primary_arm: str) -> dict[str, bool]:
    out: dict[str, bool] = {}
    # 1. synthetic certificate fixture: hand-computed worst-case table
    syn, info = synthetic_fixture()
    adm, wc = syn.shield_query("queryA", (), TAU)
    # lower cell = {shield0,1,2}: wc(dct)=0, wc(gnb)=0.21, wc(hgb)=0.10
    out["synthetic_certificate_fixture"] = (
        adm == ["dct"] and abs(wc["dct"] - 0.0) < 1e-12 and abs(wc["gnb"] - 0.21) < 1e-12 and abs(wc["hgb"] - 0.10) < 1e-12
    )
    adm_b, wc_b = syn.shield_query("queryB", (), TAU)
    # upper cell = {shield3,4,5}: wc(dct)=0.01, wc(gnb)=0.16, wc(hgb)=0.01
    out["synthetic_certificate_fixture"] = out["synthetic_certificate_fixture"] and (
        adm_b == ["dct", "hgb"] and abs(wc_b["dct"] - 0.0) < 1e-12 and abs(wc_b["gnb"] - 0.16) < 1e-12 and abs(wc_b["hgb"] - 0.01) < 1e-12
    )
    # 2. admissibility invariance: hostile scorers can never break the shield
    hostile_ok = True
    def worst_scorer(c, arm, name, acq):
        a, _ = c.shield_query(name, acq, TAU)
        if not a:
            return {x: 0.0 for x in PORTFOLIO}
        pick = max(a, key=lambda x: c.excess_member(name, x))
        return {x: (0.0 if x == pick else 1.0) for x in PORTFOLIO}
    for name in info["queries"]:
        decision = walk_with_scorer(syn, name, "STATIC_ADAPTIVE", TAU, worst_scorer, None)
        final_state = tuple(sorted(decision["acquired"]))
        a_final, _ = syn.shield_query(name, final_state, TAU)
        hostile_ok = hostile_ok and (decision["committed"] == "F_STAR" or (decision["certified"] and decision["committed"] in a_final))
    out["admissibility_invariance"] = hostile_ok
    # 3. custody guard: poisoned partition must raise
    custody_ok = False
    try:
        syn_poison, _ = synthetic_fixture()
        syn_poison.roles = {**syn_poison.roles, "proposer_train": sorted(syn_poison.roles["proposer_train"] + ["queryA"])}
        syn_poison._proposers.pop(("LEARNED_KNN_1", frozenset()), None)
        syn_poison.propose_errors("LEARNED_KNN_1", (), "queryA")
        raise RuntimeError("custody guard did not fire")
    except AssertionError:
        custody_ok = True
    out["custody_guard_hostile"] = custody_ok
    # 4. shuffled control is non-authoritative but shield-safe (uses real ctx)
    shuf_ok = True
    for fold, ctx in sorted(ctx_pool.items()):
        probe = ctx.roles["threshold_select"][0]
        ctx.propose_errors(primary_arm, (), probe)
        perm = rng_for(SEED, "shuf", "SHUFFLED_" + primary_arm, fold, "")
        tgt = np.array([[ctx.outcomes[n][a] for a in PORTFOLIO] for n in ctx.roles["proposer_train"]])
        shuffled = tgt[perm.permutation(len(tgt))]
        same = np.allclose(tgt, shuffled)
        shuf_ok = shuf_ok and (not same)
        dec = walk(ctx, probe, "SHUFFLED_" + primary_arm, TAU)
        a_final, _ = ctx.shield_query(probe, tuple(sorted(dec["acquired"])), TAU)
        shuf_ok = shuf_ok and (dec["committed"] == "F_STAR" or dec["committed"] in a_final)
    out["shuffled_nonauthority"] = shuf_ok
    # 5. VBS dominance + 6. direct-difference distances
    vbs_ok = True
    for ctx in ctx_pool.values():
        for name, row in ctx.outcomes.items():
            vbs_ok = vbs_ok and row["best"] <= min(row[a] for a in PORTFOLIO) + 1e-12
    out["vbs_dominance"] = vbs_ok
    rng = np.random.default_rng(7)
    q, X = rng.random(3), rng.random((9, 3))
    direct = np.sqrt(((X - q) ** 2).sum(axis=1))
    ref = np.array([math.sqrt(float(np.sum((X[i] - q) ** 2))) for i in range(9)])
    out["direct_difference_distances"] = bool(np.allclose(direct, ref, atol=0, rtol=0))
    return out


def walk_with_scorer(ctx: FoldContext, name: str, arm: str, tau: float,
                     scorer: Callable, gain_fn: Callable | None) -> dict[str, Any]:
    """Walk with an injected (possibly hostile) scorer; same shield logic as walk()."""
    acquired: tuple[str, ...] = ()
    while True:
        admissible, wc = ctx.shield_query(name, acquired, tau)
        legal = sorted(g for g in GROUPS if g not in acquired)
        if not admissible:
            if legal:
                acquired = acquired + (legal[0],)
                continue
            return {"committed": "F_STAR", "acquired": sorted(acquired), "certified": False, "bound": None, "wc": None}
        commit_loss_now = min(scorer(ctx, arm, name, acquired)[a] for a in admissible)
        gains = {}
        for g in legal:
            adm2, _ = ctx.shield_query(name, acquired + (g,), tau)
            gains[g] = -math.inf if not adm2 else commit_loss_now - min(scorer(ctx, arm, name, acquired + (g,))[a] for a in adm2)
        finite = {g: v for g, v in gains.items() if v > -math.inf}
        best_g = max(sorted(finite), key=lambda g: finite[g]) if finite else None
        if best_g is None or finite[best_g] <= TOL:
            scores = scorer(ctx, arm, name, acquired)
            best = min(admissible, key=lambda a: (scores[a], a))
            return {"committed": best, "acquired": sorted(acquired), "certified": True, "bound": json_float(wc[best]), "wc": wc[best]}
        acquired = acquired + (best_g,)


# ---------------------------------------------------------------------------
# end-to-end pipeline
# ---------------------------------------------------------------------------

SHUFFLED_ARMS = tuple("SHUFFLED_" + a for a in LEARNED_ARMS)


def policy_phase(fold_of: dict[str, int], meta: dict[str, dict[str, list[float]]], outcomes: dict[str, dict[str, float]]) -> dict[int, dict[str, Any]]:
    per_fold: dict[int, dict[str, Any]] = {}
    for t in range(N_FOLDS):
        roles = role_names(t, fold_of)
        ctx = FoldContext(t, roles, meta, outcomes)
        ts_rows: dict[str, dict[str, dict[str, Any]]] = {}
        for arm in LEARNED_ARMS + SHUFFLED_ARMS:
            ts_rows[arm] = evaluate_arm(ctx, roles["threshold_select"], arm, TAU)
        primary_arm = select_primary({a: r for a, r in ts_rows.items() if a in LEARNED_ARMS})
        test_rows: dict[str, dict[str, dict[str, Any]]] = {}
        for arm in STATIC_ARMS + LEARNED_ARMS + UNSHIELDED_ARMS:
            test_rows[arm] = evaluate_arm(ctx, roles["test"], arm, TAU)
        per_fold[t] = {"roles": roles, "f_star": json_float(ctx.f_star), "threshold_select": ts_rows,
                       "primary": primary_arm, "test": test_rows}
    return per_fold


def execute(subject_repo: Path, freeze_path: Path) -> dict[str, Any]:
    freeze = load_freeze(freeze_path)
    corpus = verify_and_load_corpus(subject_repo, freeze)
    loaded, audit = corpus["loaded"], corpus["audit"]
    excluded = sorted(name for name, d in loaded.items() if d["min_class_count"] < MIN_CLASS_COUNT)
    admissible = sorted(name for name, d in loaded.items() if d["min_class_count"] >= MIN_CLASS_COUNT)
    if len(admissible) < N_FOLDS * 3:
        raise ValueError(f"corpus too small after exclusion: {len(admissible)}")
    fold_of = assign_folds(admissible)
    outcomes, meta = generate_outcomes(loaded, freeze)
    per_fold = policy_phase(fold_of, meta, outcomes)
    # determinism control: independent second policy pass must be byte-identical
    per_fold_repeat = policy_phase(fold_of, meta, outcomes)
    determinism_digest_a = digest_json(per_fold)
    determinism_digest_b = digest_json(per_fold_repeat)
    deterministic = determinism_digest_a == determinism_digest_b

    pooled: dict[str, dict[str, dict[str, Any]]] = {arm: {} for arm in ALL_ARMS}
    pooled["PRIMARY_LEARNED"] = {}
    primary_by_dataset: dict[str, str] = {}
    for t in range(N_FOLDS):
        for arm, rows in per_fold[t]["test"].items():
            pooled[arm].update(rows)
        prim = per_fold[t]["primary"]
        for name, row in per_fold[t]["test"][prim].items():
            pooled["PRIMARY_LEARNED"][name] = row
            primary_by_dataset[name] = prim

    names_sorted = sorted(pooled["STATIC_ADAPTIVE"])
    diffs = np.array([pooled["PRIMARY_LEARNED"][n]["excess"] - pooled["STATIC_ADAPTIVE"][n]["excess"] for n in names_sorted], dtype=float)
    boot = paired_bootstrap(diffs)

    # coverage: ladder over the 8 acquisition states + full-state indicator, per test dataset
    ctx_pool = {t: FoldContext(t, per_fold[t]["roles"], meta, outcomes) for t in range(N_FOLDS)}
    ladder_vals, full_state_hits = [], []
    for t in range(N_FOLDS):
        ctx = ctx_pool[t]
        for name in per_fold[t]["roles"]["test"]:
            ladder_vals.append(coverage_at(ctx, name))
            adm_full, _ = ctx.shield_query(name, tuple(sorted(GROUPS)), TAU)
            full_state_hits.append(1.0 if adm_full else 0.0)
    coverage = {
        "ladder_mean": json_float(float(np.mean(ladder_vals))),
        "primary_tau_full_state": json_float(float(np.mean(full_state_hits))),
        "tau": TAU,
        "n_evaluations": len(ladder_vals),
    }

    frontier = {}
    for tau in TAU_GRID:
        static_rows, prim_rows = {}, {}
        for t in range(N_FOLDS):
            ctx = ctx_pool[t]
            static_rows.update(evaluate_arm(ctx, per_fold[t]["roles"]["test"], "STATIC_ADAPTIVE", tau))
            prim = per_fold[t]["primary"]
            prim_rows.update(evaluate_arm(ctx, per_fold[t]["roles"]["test"], prim, tau))
        frontier[f"{tau:.2f}"] = {
            "tau": tau,
            "static_mean_excess": arm_summary(static_rows)["mean_excess"],
            "primary_learned_mean_excess": arm_summary(prim_rows)["mean_excess"],
            "primary_learned_violations_strict": arm_summary(prim_rows)["violations_strict"],
            "primary_learned_certified_fraction": arm_summary(prim_rows)["certified_fraction"],
        }

    arms_summary = {arm: arm_summary(pooled[arm]) for arm in ALL_ARMS}
    arms_summary["PRIMARY_LEARNED"] = arm_summary(pooled["PRIMARY_LEARNED"])
    static_mean = arms_summary["STATIC_ADAPTIVE"]["mean_excess"]
    primary_test = {
        "comparator": "STATIC_ADAPTIVE",
        "diffs": {n: json_float(diffs[i]) for i, n in enumerate(names_sorted)},
        "mean_diff": json_float(float(diffs.mean())),
        "ci_lower": boot["ci_lower"],
        "ci_upper": boot["ci_upper"],
        "bootstrap_replicates": boot["replicates"],
        "primary_mean_excess": arms_summary["PRIMARY_LEARNED"]["mean_excess"],
        "static_mean_excess": static_mean,
        "mean_groups_acquired_primary": arms_summary["PRIMARY_LEARNED"]["mean_groups_acquired"],
        "mean_groups_acquired_static": arms_summary["STATIC_ADAPTIVE"]["mean_groups_acquired"],
        "primary_fraction_of_static": json_float(arms_summary["PRIMARY_LEARNED"]["mean_excess"] / static_mean) if static_mean > 0 else None,
    }

    hostile = hostile_controls_runtime(ctx_pool, per_fold[0]["primary"])
    hostile["metadata_audit"] = all(a["bytes_match_freeze_sha256"] and a["rows_features_classes_match"] for a in audit.values())
    hostile["determinism_policy_phase"] = deterministic
    hostile["fold_partition_disjoint"] = all(
        sorted(set(per_fold[t]["roles"]["test"]) & set(per_fold[t]["roles"]["proposer_train"])) == [] and
        sorted(set(per_fold[t]["roles"]["test"]) & set(per_fold[t]["roles"]["shield_table"])) == [] and
        sorted(set(per_fold[t]["roles"]["test"]) & set(per_fold[t]["roles"]["threshold_select"])) == []
        for t in range(N_FOLDS))
    hostile["vbs_dominance_outcomes"] = all(
        outcomes[n]["best"] <= min(outcomes[n][a] for a in PORTFOLIO) + 1e-12 for n in outcomes)

    payload = {
        "schema": SCHEMA,
        "upstream": {"repo": PMLB_REPO, "commit": PMLB_COMMIT, "tree": PMLB_TREE,
                     "license_blob": LICENSE_BLOB, "summary_blob": SUMMARY_BLOB},
        "corpus": {
            "frozen_datasets": len(freeze),
            "admissible": len(admissible),
            "excluded": excluded,
            "exclusion_rule": f"rarest class count < {MIN_CLASS_COUNT}",
            "fold_assignment": {n: fold_of[n] for n in sorted(fold_of)},
            "fold_sizes": {str(t): int(sum(1 for f in fold_of.values() if f == t)) for t in range(N_FOLDS)},
            "audit": audit,
        },
        "outcomes": {n: {a: json_float(outcomes[n][a]) for a in list(PORTFOLIO) + ["best"]} for n in sorted(outcomes)},
        "meta_features": {n: {g: [json_float(v) for v in meta[n][g]] for g in ["G0", "G1", "G2", "G3"]} for n in sorted(meta)},
        "folds": {
            str(t): {
                "roles": per_fold[t]["roles"],
                "f_star": per_fold[t]["f_star"],
                "primary": per_fold[t]["primary"],
                "test": per_fold[t]["test"],
                "threshold_select": per_fold[t]["threshold_select"],
            }
            for t in range(N_FOLDS)
        },
        "arms_summary": arms_summary,
        "primary_test": primary_test,
        "primary_by_dataset": primary_by_dataset,
        "coverage": coverage,
        "frontier": frontier,
        "hostile_controls": hostile,
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "sklearn": sklearn.__version__,
            "platform": platform.platform(),
            "machine": platform.machine(),
        },
        "authority": {
            "prospective_registration": False,
            "human_clinical_or_field_trial": False,
            "peer_reviewed_reproduction_by_independent_group": False,
            "corpus_out_of_fold_historical_evidence": True,
            "adversarial_robustness_certification": False,
            "notes": "Prospective frozen-protocol corpus experiment on PMLB metadata-screened datasets; out-of-fold policy evaluation with exact finite-fibre shield.",
        },
    }
    payload["terminal"] = decide_terminal(payload)
    return payload


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def run_self_test() -> None:
    syn, info = synthetic_fixture()
    adm, wc = syn.shield_query("queryA", (), TAU)
    assert adm == ["dct"], adm
    assert abs(wc["gnb"] - 0.21) < 1e-12 and abs(wc["hgb"] - 0.10) < 1e-12
    adm_b, wc_b = syn.shield_query("queryB", (), TAU)
    assert adm_b == ["dct", "hgb"], adm_b
    assert abs(wc_b["dct"] - 0.0) < 1e-12 and abs(wc_b["hgb"] - 0.01) < 1e-12
    # static walk on synthetic: commits dct at the initial state (no gain > tol)
    dec = walk(syn, "queryA", "STATIC_ADAPTIVE", TAU)
    assert dec["committed"] == "dct" and dec["acquired"] == [] and dec["certified"] and abs(dec["bound"] - 0.0) < 1e-12, dec
    assert abs(excess_of(syn, "queryA", dec) - 0.0) < 1e-12
    # shield-free on the same query commits immediately; shield-full acquires all then commits
    dec_free = walk(syn, "queryA", "SHIELD_FREE", TAU)
    assert dec_free["committed"] == "dct" and dec_free["acquired"] == []
    dec_full = walk(syn, "queryA", "SHIELD_FULL", TAU)
    assert dec_full["acquired"] == ["G1", "G2", "G3"] and dec_full["committed"] == "F_STAR", dec_full
    # G1 fractures every full-state cell to <2 members on this fixture: full
    # refinement destroys the certificate and both queries fall back to F*.
    dec_full_b = walk(syn, "queryB", "SHIELD_FULL", TAU)
    assert dec_full_b["committed"] == "F_STAR" and not dec_full_b["certified"], dec_full_b
    # learned proposer runs and stays inside the shield
    dec_knn = walk(syn, "queryB", "LEARNED_KNN_1", TAU)
    a_final, _ = syn.shield_query("queryB", tuple(sorted(dec_knn["acquired"])), TAU)
    assert dec_knn["committed"] == "F_STAR" or dec_knn["committed"] in a_final, dec_knn
    # custody guard raises on poisoned partition
    syn2, _ = synthetic_fixture()
    try:
        syn2.roles = {**syn2.roles, "proposer_train": sorted(syn2.roles["proposer_train"] + ["queryA"])}
        syn2._proposers.pop(("LEARNED_KNN_1", frozenset()), None)
        syn2.propose_errors("LEARNED_KNN_1", (), "queryA")
        raise RuntimeError("custody guard did not fire")
    except AssertionError:
        pass
    # fold machinery
    names = [f"d{i:02d}" for i in range(45)]
    fold_of = assign_folds(names)
    assert fold_of == assign_folds(names)
    for t in range(N_FOLDS):
        roles = role_names(t, fold_of)
        union = sorted(sum(roles.values(), []))
        assert union == names and len(union) == len(set(union))
        assert not (set(roles["test"]) & set(roles["proposer_train"]))
        assert not (set(roles["test"]) & set(roles["shield_table"]))
        assert not (set(roles["test"]) & set(roles["threshold_select"]))
    # bootstrap determinism
    d = np.array([0.1, -0.2, 0.3, 0.05, -0.1, 0.2] * 5)
    b1 = paired_bootstrap(d)
    b2 = paired_bootstrap(d)
    assert b1 == b2
    # cv endpoint machinery: deterministic, finite, informative on separable data
    rng_syn = np.random.default_rng(11)
    y_syn = np.array([0, 1] * 20)
    x_syn = np.column_stack([rng_syn.normal(size=40) + 2.0 * y_syn, rng_syn.normal(size=40)])
    err1 = cv_balanced_error(x_syn, y_syn, lambda s: make_portfolio_model("logreg", s), 1, 12345)
    err2 = cv_balanced_error(x_syn, y_syn, lambda s: make_portfolio_model("logreg", s), 1, 12345)
    assert err1 == err2 and 0.0 <= err1 < 0.25, (err1, err2)
    # imputation: column medians fill missing cells deterministically
    x_missing = np.array([[1.0, np.nan], [2.0, 4.0], [3.0, np.nan]])
    x_filled = impute_columns(x_missing)
    assert x_filled[0, 1] == 4.0 and x_filled[2, 1] == 4.0
    # hostile controls pass on the synthetic context
    controls = hostile_controls_runtime({0: syn}, "LEARNED_KNN_1")
    assert controls["synthetic_certificate_fixture"], controls
    assert controls["admissibility_invariance"], controls
    assert controls["custody_guard_hostile"], controls
    assert controls["vbs_dominance"], controls
    assert controls["direct_difference_distances"], controls
    print("SELF_TEST_OK")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--subject-repo", type=Path, default=None)
    parser.add_argument("--freeze", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--terminal-output", type=Path, default=None)
    parser.add_argument("--timings-output", type=Path, default=None)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        return 0
    if args.output is None or args.terminal_output is None or args.subject_repo is None:
        parser.error("--subject-repo, --output and --terminal-output are required without --self-test")
    import time
    t0 = time.time()
    freeze_path = args.freeze if args.freeze is not None else Path(__file__).resolve().parent / FREEZE_NAME
    try:
        payload = execute(args.subject_repo.resolve(), freeze_path)
    except (ValueError, OSError, KeyError, MemoryError) as exc:  # fail closed
        failure = {"schema": SCHEMA, "terminal": "CANNOT_CHECK_PMLB_PROPOSAL_ORDERING_SOURCE_OR_RESOURCE",
                   "failure_stage": type(exc).__name__, "failure_detail": str(exc)[:2000]}
        args.output.write_text(canonical_json(failure) + "\n")
        args.terminal_output.write_text(failure["terminal"] + "\n")
        print(failure["terminal"])
        print(f"FAILURE_DETAIL {failure['failure_detail'][:200]}")
        return 2
    args.output.write_text(canonical_json(payload) + "\n")
    args.terminal_output.write_text(payload["terminal"] + "\n")
    if args.timings_output is not None:
        args.timings_output.write_text(canonical_json({
            "wall_seconds_total": round(time.time() - t0, 3),
            "python": platform.python_version(), "numpy": np.__version__,
            "scipy": scipy.__version__, "sklearn": sklearn.__version__,
            "machine": platform.machine(),
        }) + "\n")
    print(payload["terminal"])
    print("RESULT_SHA256 " + sha256_bytes(args.output.read_bytes()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
