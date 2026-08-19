"""Execution-only compatibility adapter for frozen P9 S3.

This module preserves S3/D1 feature semantics and model hyperparameters while
forcing dense DictVectorizer output to avoid scikit-learn 1.9's int64 sparse-index
rejection.  It also inherits D1 v1.2's logistic-regression compatibility choice.
"""

from __future__ import annotations

from sklearn.feature_extraction import DictVectorizer
from sklearn.pipeline import Pipeline

from . import d1_experiment as _base
from . import d1_runtime as _d1_runtime  # applies D1 v1.2 estimator/data compatibility


def _dense_compatible_estimator(spec):
    template = _d1_runtime._compatible_estimator(spec)
    return Pipeline(
        [
            ("vectorizer", DictVectorizer(sparse=False)),
            ("model", template.named_steps["model"]),
        ]
    )


# Patch before importing S3 experiment so both F1 and historical D1 replay use
# the same dense execution transport while keeping feature dictionaries/models.
_base._estimator = _dense_compatible_estimator

from .s3_experiment import run_s3_access_attribution  # noqa: E402

__all__ = ["run_s3_access_attribution"]
