"""Runtime compatibility adapter for the frozen P9 D1 experiment.

Execution protocol v1.2 composes two pre-outcome implementation corrections:

1. dependency mutations reverse the existing stored dependency edges and fail
   closed if topology is unchanged (`d1_data_runtime`);
2. current scikit-learn logistic plumbing uses a three-class-capable solver.

Data, features, model grid, train->dev selection, protected test, metrics and
scientific terminal rules remain frozen.
"""

from __future__ import annotations

from orion.transfer.v2.canonical import content_digest
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

# Import for side effect before d1_experiment binds/uses the generator functions.
from . import d1_data_runtime as _data_runtime  # noqa: F401
from . import d1_experiment as _base
from .d1_experiment import D1FeatureFamily, D1ModelSpec, exact_relational_comparator, features, model_specs


_ORIGINAL_ESTIMATOR = _base._estimator
_ORIGINAL_RUN = _base.run_d1


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


_base._estimator = _compatible_estimator


def run_d1(**kwargs):
    result = _ORIGINAL_RUN(**kwargs)
    result["protocol"] = "P9.D1MethodTransferProtocol.v1.2"
    result.pop("result_digest", None)
    result["result_digest"] = content_digest(result)
    return result


__all__ = [
    "D1FeatureFamily",
    "D1ModelSpec",
    "exact_relational_comparator",
    "features",
    "model_specs",
    "run_d1",
]
