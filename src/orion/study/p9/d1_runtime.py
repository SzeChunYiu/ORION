"""Runtime compatibility adapter for the frozen P9 D1 experiment.

The original D1 implementation used a logistic constructor form that is not
accepted by current scikit-learn.  This adapter preserves the frozen model grid
and all scientific logic, replacing only logistic solver plumbing with a current
three-class-capable solver.  The original file remains in history as the
pre-execution implementation failure record.
"""

from __future__ import annotations

from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from . import d1_experiment as _base
from .d1_experiment import D1FeatureFamily, D1ModelSpec, exact_relational_comparator, features, model_specs


_ORIGINAL_ESTIMATOR = _base._estimator


def _compatible_estimator(spec: D1ModelSpec) -> Pipeline:
    if spec.family != "logistic":
        return _ORIGINAL_ESTIMATOR(spec)
    params = spec.as_dict()
    model = LogisticRegression(
        C=float(params["C"]),
        max_iter=2000,
        random_state=2711,
        solver="lbfgs",
    )
    return Pipeline([("vectorizer", _base.DictVectorizer(sparse=True)), ("model", model)])


# Patch only the module-local estimator factory used by the already frozen run_d1
# function. Nothing about data, features, model grid, selection, metrics, or test
# access changes.
_base._estimator = _compatible_estimator
run_d1 = _base.run_d1


__all__ = [
    "D1FeatureFamily",
    "D1ModelSpec",
    "exact_relational_comparator",
    "features",
    "model_specs",
    "run_d1",
]
