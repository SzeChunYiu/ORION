"""Execution adapter for P9 M1 protocol v1.1.

The scientific M1 implementation remains in :mod:`m1`.  This adapter changes
only diagnostic train-size-curve failure handling: if a frozen configuration
cannot fit at a small sample size (e.g. kNN with k > n), the point is recorded
rather than changing the model or aborting the protected experiment.
"""

from __future__ import annotations

from typing import Sequence

from orion.transfer.v2.canonical import content_digest

from . import m1 as _base
from .m0_tasks import TaskKind
from .m1 import ModelFamily, ModelSpec, PredictionRecord, frozen_model_specs
from .m1_features import FeatureFamily
from .structural_world import ViewMode


_ORIGINAL_CURVE = _base._train_size_curve
_ORIGINAL_RUN = _base.run_m1


def _safe_train_size_curve(
    *,
    corpus_seed: str,
    pairs_per_family: Sequence[int],
    mode: ViewMode,
    order_seed: str,
    dev_records,
    task_kind: TaskKind,
    feature_family: FeatureFamily,
    spec: ModelSpec,
):
    points: list[dict[str, object]] = []
    for count in pairs_per_family:
        try:
            one = _ORIGINAL_CURVE(
                corpus_seed=corpus_seed,
                pairs_per_family=(int(count),),
                mode=mode,
                order_seed=order_seed,
                dev_records=dev_records,
                task_kind=task_kind,
                feature_family=feature_family,
                spec=spec,
            )
            point = dict(one[0])
            point["status"] = "EVALUATED"
            points.append(point)
        except ValueError as exc:
            # This is diagnostic-only. Never mutate the selected model to make a
            # small curve point runnable.
            points.append(
                {
                    "pairs_per_family": int(count),
                    "status": "CONFIG_NOT_FIT_AT_SIZE",
                    "error_class": type(exc).__name__,
                }
            )
    return points


_base._train_size_curve = _safe_train_size_curve


def run_m1(**kwargs):
    result = _ORIGINAL_RUN(**kwargs)
    result["protocol"] = "P9.M1Protocol.v1.1"
    result.pop("result_digest", None)
    result["result_digest"] = content_digest(result)
    return result


__all__ = [
    "ModelFamily",
    "ModelSpec",
    "PredictionRecord",
    "frozen_model_specs",
    "run_m1",
]
