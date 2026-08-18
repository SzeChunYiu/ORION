from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
import math
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.linear_model import LogisticRegression
from .types import Experience, CompetenceEstimate, Verdict

@dataclass
class _Model:
    keys: tuple[str, ...]
    scaler: StandardScaler
    clf: LogisticRegression | None
    constant: float | None
    nn: NearestNeighbors
    train_X: np.ndarray
    n_success: int
    n_fail: int

class CompetenceMap:
    """Three-valued competence model: evidence of success, evidence of failure, and unknown.

    Unknown is not encoded as a negative label. It is inferred from distance to admitted
    success/failure evidence and a configurable evidence-support threshold.
    """
    def __init__(self, unknown_quantile: float = 0.95, min_evidence: int = 4) -> None:
        self.unknown_quantile = unknown_quantile
        self.min_evidence = min_evidence
        self.models: dict[str, _Model] = {}
        self.distance_thresholds: dict[str, float] = {}

    @staticmethod
    def _matrix(exps: list[Experience], keys: tuple[str, ...]) -> np.ndarray:
        return np.asarray([[float(e.features.get(k, 0.0)) for k in keys] for e in exps], dtype=float)

    def fit(self, experiences: list[Experience]) -> "CompetenceMap":
        by: dict[str, list[Experience]] = defaultdict(list)
        for e in experiences:
            if e.verdict in (Verdict.SUCCESS, Verdict.FAIL):
                by[e.mechanic_id].append(e)
        self.models.clear(); self.distance_thresholds.clear()
        for mech, rows in by.items():
            keys = tuple(sorted({k for e in rows for k in e.features}))
            X = self._matrix(rows, keys)
            y = np.asarray([1 if e.verdict == Verdict.SUCCESS else 0 for e in rows])
            scaler = StandardScaler().fit(X)
            Z = scaler.transform(X)
            clf = None; const = None
            if len(set(y.tolist())) >= 2:
                clf = LogisticRegression(max_iter=2000, class_weight="balanced", random_state=0).fit(Z, y)
            else:
                const = float(y[0])
            nn = NearestNeighbors(n_neighbors=min(5, len(rows))).fit(Z)
            d, _ = nn.kneighbors(Z)
            # leave-self-in makes first distance zero; use furthest available neighbor.
            local = d[:, -1]
            threshold = max(float(np.quantile(local, self.unknown_quantile)) * 2.0, 0.75)
            self.models[mech] = _Model(keys, scaler, clf, const, nn, Z, int(y.sum()), int((1-y).sum()))
            self.distance_thresholds[mech] = threshold
        return self

    def estimate(self, mechanic_id: str, features: dict[str, float]) -> CompetenceEstimate:
        m = self.models.get(mechanic_id)
        if m is None:
            return CompetenceEstimate(mechanic_id, 0.5, 0.0, Verdict.UNKNOWN, math.inf)
        x = np.asarray([[float(features.get(k, 0.0)) for k in m.keys]], dtype=float)
        z = m.scaler.transform(x)
        d, _ = m.nn.kneighbors(z)
        nearest = float(d[0, 0])
        evidence_mass = float(m.n_success + m.n_fail)
        if evidence_mass < self.min_evidence or nearest > self.distance_thresholds[mechanic_id]:
            return CompetenceEstimate(mechanic_id, 0.5, evidence_mass, Verdict.UNKNOWN, nearest)
        p = m.constant if m.clf is None else float(m.clf.predict_proba(z)[0, 1])
        status = Verdict.SUCCESS if p >= 0.5 else Verdict.FAIL
        return CompetenceEstimate(mechanic_id, float(p), evidence_mass, status, nearest)
