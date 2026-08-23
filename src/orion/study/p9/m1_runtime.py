"""Execution adapter for P9 M1 protocol v1.3.

The frozen M1 data/features/model grid remain in :mod:`m1`.  This adapter
preserves pre-outcome review/execution corrections:

1. diagnostic train-size points that cannot fit the selected configuration are
   recorded instead of mutating the model;
2. row-order invariance is tested by re-running inference on a reversed batch,
   and exact information ceilings are enforced separately per task;
3. scikit-learn 1.9 sparse-index compatibility is kept outside feature semantics
   by making DictVectorizer emit dense numeric arrays.  The prior focused smoke
   test failed before protected protocol execution because liblinear rejected
   int64 CSR index metadata; no corpus, feature, model grid, selection or test
   rule changed.
"""

from __future__ import annotations

from typing import Sequence

from sklearn.feature_extraction import DictVectorizer as _SklearnDictVectorizer

from orion.transfer.v2.canonical import content_digest

from . import m1 as _base
from .generated_worlds import generate_corpus
from .identifiability import analyze_identifiability
from .m0_tasks import TaskKind
from .m1 import ModelFamily, ModelSpec, PredictionRecord, frozen_model_specs
from .m1_features import FeatureFamily
from .structural_world import ViewMode


_ORIGINAL_CURVE = _base._train_size_curve
_ORIGINAL_RUN = _base.run_m1


def _dense_dict_vectorizer(*args, **kwargs):
    """Return the same DictVectorizer feature map without sparse index metadata."""

    kwargs = dict(kwargs)
    kwargs["sparse"] = False
    return _SklearnDictVectorizer(*args, **kwargs)


# Runtime-compatibility amendment only.  m1._make_estimator resolves
# DictVectorizer from its module globals at call time, so this keeps all frozen
# feature construction/model choices intact while avoiding sklearn 1.9's
# liblinear rejection of int64 CSR index arrays.
_base.DictVectorizer = _dense_dict_vectorizer


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
            points.append(
                {
                    "pairs_per_family": int(count),
                    "status": "CONFIG_NOT_FIT_AT_SIZE",
                    "error_class": type(exc).__name__,
                }
            )
    return points


_base._train_size_curve = _safe_train_size_curve


def _prediction_map(predictions) -> dict[str, str]:
    return {prediction.world_id: prediction.prediction for prediction in predictions}


def _augment_corrected_evaluation(result: dict[str, object], *, config: dict[str, object]) -> bool:
    corpus = generate_corpus(
        seed=str(config["corpus_seed"]),
        train_pairs_per_family=int(config["train_pairs_per_family"]),
        dev_pairs_per_family=int(config["dev_pairs_per_family"]),
        test_pairs_per_family=int(config["test_pairs_per_family"]),
    )
    any_violation = False
    views = result["views"]
    assert isinstance(views, dict)

    for mode in ViewMode:
        view_result = views[mode.value]
        assert isinstance(view_result, dict)
        tasks = view_result["tasks"]
        assert isinstance(tasks, dict)
        train_records = _base._records(
            corpus.train,
            mode=mode,
            order_seed=str(config["train_order_seed"]),
        )
        test_records = _base._records(
            corpus.test,
            mode=mode,
            order_seed=str(config["test_order_seed"]),
        )

        for task_kind in (TaskKind.MECHANIC_RANKING, TaskKind.GLUING):
            task_result = tasks[task_kind.value]
            assert isinstance(task_result, dict)
            selected = task_result["selected"]
            assert isinstance(selected, dict)
            model, feature_family, _ = _base._fit_selected(
                train_records,
                selected,
                task_kind=task_kind,
            )
            canonical = _base._evaluate_model(
                model,
                test_records,
                task_kind=task_kind,
                feature_family=feature_family,
            )
            reversed_batch = _base._evaluate_model(
                model,
                tuple(reversed(test_records)),
                task_kind=task_kind,
                feature_family=feature_family,
            )
            canonical_map = _prediction_map(canonical)
            reversed_map = _prediction_map(reversed_batch)
            mismatches = sorted(
                world_id
                for world_id in set(canonical_map) | set(reversed_map)
                if canonical_map.get(world_id) != reversed_map.get(world_id)
            )
            task_result["test_row_permutation_invariance"] = {
                "sample_count": len(canonical_map),
                "mismatch_count": len(mismatches),
                "invariant": not mismatches,
                "mismatch_world_ids": mismatches,
                "method": "REEXECUTED_REVERSED_TEST_BATCH",
            }

            task_worlds = tuple(
                record.world for record in test_records if record.task.kind is task_kind
            )
            ceiling = analyze_identifiability(task_worlds, mode).deterministic_accuracy_ceiling
            test_metrics = task_result["test"]
            assert isinstance(test_metrics, dict)
            accuracy = float(test_metrics["accuracy"])
            violation = accuracy > ceiling + 1e-12
            test_metrics["exact_view_deterministic_accuracy_ceiling"] = ceiling
            test_metrics["ceiling_gap"] = ceiling - accuracy
            test_metrics["ceiling_violation"] = violation
            any_violation = any_violation or violation

        overall = view_result["test_overall"]
        assert isinstance(overall, dict)
        overall["ceiling_violation_any_task"] = any(
            bool(tasks[task.value]["test"]["ceiling_violation"])  # type: ignore[index]
            for task in (TaskKind.MECHANIC_RANKING, TaskKind.GLUING)
        )

    return any_violation


def run_m1(**kwargs):
    config: dict[str, object] = {
        "corpus_seed": "p9-m1-classical-v1",
        "train_pairs_per_family": 64,
        "dev_pairs_per_family": 24,
        "test_pairs_per_family": 48,
        "train_size_pairs_per_family": (4, 8, 16, 32, 64),
        "train_order_seed": "p9-m1-order-train-v1",
        "dev_order_seed": "p9-m1-order-dev-v1",
        "test_order_seed": "p9-m1-order-test-v1",
        "alternate_test_order_seed": "p9-m1-order-test-alt-v1",
        "subject_sha": None,
    }
    config.update(kwargs)
    result = _ORIGINAL_RUN(**kwargs)
    any_violation = _augment_corrected_evaluation(result, config=config)
    if any_violation:
        result["terminal"] = "M1_LEAKAGE_OR_EVALUATOR_FAILURE"
    result["protocol"] = "P9.M1Protocol.v1.3"
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
