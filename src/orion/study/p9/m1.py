"""P9 M1 classical candidate-relative learning gate.

M1 is diagnostic.  It locates learning/computation residuals before any neural
architecture is permitted to enter the P9 experiment.  It never grants
scientific, model-promotion, or paper-readiness authority.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Mapping, Sequence

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier

from orion.transfer.v2.canonical import content_digest

from .generated_worlds import (
    CorpusSplit,
    GeneratedCorpus,
    GeneratedSplit,
    HostileFamily,
    generate_balanced_split,
    generate_corpus,
)
from .identifiability import analyze_identifiability
from .m0 import M0Baseline, predict_null
from .m0_tasks import GluingTask, MechanicRankingTask, P9Task, TaskKind, build_task
from .m1_features import FeatureFamily, gluing_features, mechanic_features
from .structural_world import P9StructuralWorld, ViewMode


class ModelFamily(str, Enum):
    LOGISTIC = "logistic"
    DECISION_TREE = "decision_tree"
    RANDOM_FOREST = "random_forest"
    KNN = "knn"


@dataclass(frozen=True)
class ModelSpec:
    family: ModelFamily
    config_id: str
    params: tuple[tuple[str, object], ...]
    complexity_rank: int

    def as_dict(self) -> dict[str, object]:
        return {key: value for key, value in self.params}


@dataclass(frozen=True)
class TaskRecord:
    family: HostileFamily
    world: P9StructuralWorld
    task: P9Task


@dataclass(frozen=True)
class PredictionRecord:
    world_id: str
    family: str
    task_kind: str
    target: str
    prediction: str
    correct: bool

    def payload(self) -> dict[str, object]:
        return {
            "world_id": self.world_id,
            "family": self.family,
            "task_kind": self.task_kind,
            "target": self.target,
            "prediction": self.prediction,
            "correct": self.correct,
        }


def frozen_model_specs() -> tuple[ModelSpec, ...]:
    specs: list[ModelSpec] = []
    for index, c_value in enumerate((0.1, 1.0, 10.0)):
        specs.append(
            ModelSpec(
                ModelFamily.LOGISTIC,
                f"logistic-C{c_value:g}",
                (("C", c_value), ("max_iter", 2000), ("random_state", 1701)),
                index,
            )
        )
    for index, depth in enumerate((3, 6, None)):
        specs.append(
            ModelSpec(
                ModelFamily.DECISION_TREE,
                f"tree-depth-{depth if depth is not None else 'none'}",
                (("max_depth", depth), ("min_samples_leaf", 2), ("random_state", 1702)),
                10 + index,
            )
        )
    forest_configs = (
        (200, 4),
        (200, 8),
        (300, None),
    )
    for index, (estimators, depth) in enumerate(forest_configs):
        specs.append(
            ModelSpec(
                ModelFamily.RANDOM_FOREST,
                f"rf-n{estimators}-depth-{depth if depth is not None else 'none'}",
                (
                    ("n_estimators", estimators),
                    ("max_depth", depth),
                    ("min_samples_leaf", 2),
                    ("random_state", 1703),
                    ("n_jobs", 1),
                ),
                30 + index,
            )
        )
    knn_configs = ((3, "uniform"), (7, "distance"), (15, "distance"))
    for index, (neighbors, weights) in enumerate(knn_configs):
        specs.append(
            ModelSpec(
                ModelFamily.KNN,
                f"knn-k{neighbors}-{weights}",
                (("n_neighbors", neighbors), ("weights", weights)),
                20 + index,
            )
        )
    return tuple(specs)


def _make_estimator(spec: ModelSpec) -> Pipeline:
    params = spec.as_dict()
    if spec.family is ModelFamily.LOGISTIC:
        classifier = LogisticRegression(
            C=float(params["C"]),
            max_iter=int(params["max_iter"]),
            random_state=int(params["random_state"]),
            solver="liblinear",
        )
    elif spec.family is ModelFamily.DECISION_TREE:
        classifier = DecisionTreeClassifier(**params)
    elif spec.family is ModelFamily.RANDOM_FOREST:
        classifier = RandomForestClassifier(**params)
    elif spec.family is ModelFamily.KNN:
        classifier = KNeighborsClassifier(**params)
    else:  # pragma: no cover - enum extension guard
        raise ValueError(f"unsupported M1 model family: {spec.family}")
    return Pipeline([("vectorizer", DictVectorizer(sparse=True)), ("classifier", classifier)])


def _feature_families_for(task_kind: TaskKind, mode: ViewMode) -> tuple[FeatureFamily, ...]:
    if task_kind is TaskKind.MECHANIC_RANKING:
        return (FeatureFamily.F0_FIELD_BAG, FeatureFamily.F1_PAIRWISE)
    if task_kind is TaskKind.GLUING:
        if mode in (ViewMode.CURRENT, ViewMode.SEMANTIC):
            return (FeatureFamily.F0_FIELD_BAG, FeatureFamily.F2_CYCLE_NUMERIC)
        return (FeatureFamily.F0_FIELD_BAG,)
    raise ValueError(f"unsupported task kind: {task_kind}")


def _records(split: GeneratedSplit, *, mode: ViewMode, order_seed: str) -> tuple[TaskRecord, ...]:
    split.verify()
    records: list[TaskRecord] = []
    for pair in split.pairs:
        for world in pair.worlds:
            records.append(
                TaskRecord(
                    pair.family,
                    world,
                    build_task(world, mode=mode, order_seed=order_seed),
                )
            )
    return tuple(records)


def _target(task: P9Task) -> str:
    if isinstance(task, MechanicRankingTask):
        return task.target_candidate_id
    if isinstance(task, GluingTask):
        return task.target_label
    raise TypeError(f"unsupported task: {type(task)!r}")


def _training_rows(
    records: Sequence[TaskRecord],
    *,
    task_kind: TaskKind,
    feature_family: FeatureFamily,
    shuffled_labels_seed: int | None = None,
) -> tuple[list[dict[str, object]], list[object]]:
    rows: list[dict[str, object]] = []
    labels: list[object] = []
    for record in records:
        task = record.task
        if task.kind is not task_kind:
            continue
        if isinstance(task, MechanicRankingTask):
            for candidate in task.candidates:
                rows.append(mechanic_features(task, candidate, feature_family))
                labels.append(1 if candidate.candidate_id == task.target_candidate_id else 0)
        elif isinstance(task, GluingTask):
            rows.append(gluing_features(task, feature_family))
            labels.append(task.target_label)
        else:  # pragma: no cover
            raise TypeError(type(task))
    if not rows:
        raise ValueError(f"no training rows for {task_kind.value}/{feature_family.value}")
    if shuffled_labels_seed is not None:
        rng = np.random.default_rng(shuffled_labels_seed)
        permutation = rng.permutation(len(labels))
        labels = [labels[int(index)] for index in permutation]
    return rows, labels


def _positive_score(model: Pipeline, rows: list[dict[str, object]]) -> np.ndarray:
    classifier = model.named_steps["classifier"]
    probabilities = model.predict_proba(rows)
    classes = list(classifier.classes_)
    if 1 not in classes:
        raise ValueError("mechanic scorer was trained without positive class")
    return np.asarray(probabilities[:, classes.index(1)], dtype=float)


def _predict_record(
    model: Pipeline,
    record: TaskRecord,
    *,
    feature_family: FeatureFamily,
) -> PredictionRecord:
    task = record.task
    if isinstance(task, MechanicRankingTask):
        rows = [mechanic_features(task, candidate, feature_family) for candidate in task.candidates]
        scores = _positive_score(model, rows)
        ranked = sorted(
            zip(scores.tolist(), [candidate.candidate_id for candidate in task.candidates], strict=True),
            key=lambda item: (-item[0], item[1]),
        )
        prediction = ranked[0][1]
    elif isinstance(task, GluingTask):
        prediction = str(model.predict([gluing_features(task, feature_family)])[0])
    else:  # pragma: no cover
        raise TypeError(type(task))
    target = _target(task)
    return PredictionRecord(
        world_id=record.world.world_id,
        family=record.family.value,
        task_kind=task.kind.value,
        target=target,
        prediction=prediction,
        correct=prediction == target,
    )


def _evaluate_model(
    model: Pipeline,
    records: Sequence[TaskRecord],
    *,
    task_kind: TaskKind,
    feature_family: FeatureFamily,
) -> tuple[PredictionRecord, ...]:
    return tuple(
        _predict_record(model, record, feature_family=feature_family)
        for record in records
        if record.task.kind is task_kind
    )


def _metrics(predictions: Sequence[PredictionRecord]) -> dict[str, object]:
    total = len(predictions)
    correct = sum(int(item.correct) for item in predictions)
    by_family: dict[str, list[PredictionRecord]] = defaultdict(list)
    for prediction in predictions:
        by_family[prediction.family].append(prediction)
    return {
        "sample_count": total,
        "correct_count": correct,
        "invalid_prediction_count": 0,
        "accuracy": (correct / total) if total else None,
        "per_family_accuracy": {
            family: sum(int(item.correct) for item in rows) / len(rows)
            for family, rows in sorted(by_family.items())
        },
    }


def _fit(
    records: Sequence[TaskRecord],
    *,
    task_kind: TaskKind,
    feature_family: FeatureFamily,
    spec: ModelSpec,
    shuffled_labels_seed: int | None = None,
) -> Pipeline:
    rows, labels = _training_rows(
        records,
        task_kind=task_kind,
        feature_family=feature_family,
        shuffled_labels_seed=shuffled_labels_seed,
    )
    estimator = _make_estimator(spec)
    estimator.fit(rows, labels)
    return estimator


def _candidate_dev_configs(
    train_records: Sequence[TaskRecord],
    dev_records: Sequence[TaskRecord],
    *,
    task_kind: TaskKind,
    mode: ViewMode,
) -> tuple[dict[str, object], ...]:
    configs: list[dict[str, object]] = []
    for feature_family in _feature_families_for(task_kind, mode):
        for spec in frozen_model_specs():
            model = _fit(
                train_records,
                task_kind=task_kind,
                feature_family=feature_family,
                spec=spec,
            )
            predictions = _evaluate_model(
                model,
                dev_records,
                task_kind=task_kind,
                feature_family=feature_family,
            )
            metrics = _metrics(predictions)
            configs.append(
                {
                    "feature_family": feature_family.value,
                    "model_family": spec.family.value,
                    "config_id": spec.config_id,
                    "complexity_rank": spec.complexity_rank,
                    "params": spec.as_dict(),
                    "dev": metrics,
                }
            )
    return tuple(configs)


def _select_config(configs: Sequence[Mapping[str, object]]) -> Mapping[str, object]:
    if not configs:
        raise ValueError("no M1 configurations to select")
    return sorted(
        configs,
        key=lambda item: (
            -float(item["dev"]["accuracy"]),  # type: ignore[index]
            int(item["complexity_rank"]),
            str(item["feature_family"]),
            str(item["config_id"]),
        ),
    )[0]


def _spec_by_id(config_id: str) -> ModelSpec:
    matches = [spec for spec in frozen_model_specs() if spec.config_id == config_id]
    if len(matches) != 1:
        raise ValueError(f"unknown or duplicate M1 config id: {config_id}")
    return matches[0]


def _fit_selected(
    train_records: Sequence[TaskRecord],
    selected: Mapping[str, object],
    *,
    task_kind: TaskKind,
) -> tuple[Pipeline, FeatureFamily, ModelSpec]:
    feature_family = FeatureFamily(str(selected["feature_family"]))
    spec = _spec_by_id(str(selected["config_id"]))
    model = _fit(
        train_records,
        task_kind=task_kind,
        feature_family=feature_family,
        spec=spec,
    )
    return model, feature_family, spec


def _order_invariance(
    model: Pipeline,
    split: GeneratedSplit,
    *,
    mode: ViewMode,
    primary_order_seed: str,
    alternate_order_seed: str,
    feature_family: FeatureFamily,
) -> dict[str, object]:
    first_records = _records(split, mode=mode, order_seed=primary_order_seed)
    second_records = _records(split, mode=mode, order_seed=alternate_order_seed)
    first_predictions = {
        prediction.world_id: prediction.prediction
        for prediction in _evaluate_model(
            model,
            first_records,
            task_kind=TaskKind.MECHANIC_RANKING,
            feature_family=feature_family,
        )
    }
    second_predictions = {
        prediction.world_id: prediction.prediction
        for prediction in _evaluate_model(
            model,
            second_records,
            task_kind=TaskKind.MECHANIC_RANKING,
            feature_family=feature_family,
        )
    }
    common = sorted(set(first_predictions) & set(second_predictions))
    mismatches = [
        world_id
        for world_id in common
        if first_predictions[world_id] != second_predictions[world_id]
    ]
    return {
        "sample_count": len(common),
        "mismatch_count": len(mismatches),
        "invariant": not mismatches,
        "mismatch_world_ids": mismatches,
    }


def _row_permutation_invariance(predictions: Sequence[PredictionRecord]) -> dict[str, object]:
    forward = {item.world_id: item.prediction for item in predictions}
    reverse = {item.world_id: item.prediction for item in reversed(tuple(predictions))}
    return {
        "sample_count": len(forward),
        "invariant": forward == reverse,
    }


def _train_size_curve(
    *,
    corpus_seed: str,
    pairs_per_family: Sequence[int],
    mode: ViewMode,
    order_seed: str,
    dev_records: Sequence[TaskRecord],
    task_kind: TaskKind,
    feature_family: FeatureFamily,
    spec: ModelSpec,
) -> list[dict[str, object]]:
    points: list[dict[str, object]] = []
    for count in pairs_per_family:
        split = generate_balanced_split(
            seed=corpus_seed,
            split=CorpusSplit.TRAIN,
            pairs_per_family=int(count),
        )
        train_records = _records(split, mode=mode, order_seed=order_seed)
        model = _fit(
            train_records,
            task_kind=task_kind,
            feature_family=feature_family,
            spec=spec,
        )
        predictions = _evaluate_model(
            model,
            dev_records,
            task_kind=task_kind,
            feature_family=feature_family,
        )
        points.append({"pairs_per_family": int(count), "dev": _metrics(predictions)})
    return points


def _shuffled_label_sentinel(
    train_records: Sequence[TaskRecord],
    dev_records: Sequence[TaskRecord],
    *,
    task_kind: TaskKind,
    feature_family: FeatureFamily,
    spec: ModelSpec,
) -> dict[str, object]:
    model = _fit(
        train_records,
        task_kind=task_kind,
        feature_family=feature_family,
        spec=spec,
        shuffled_labels_seed=1919,
    )
    predictions = _evaluate_model(
        model,
        dev_records,
        task_kind=task_kind,
        feature_family=feature_family,
    )
    return _metrics(predictions)


def _m0_test_sentinels(records: Sequence[TaskRecord]) -> dict[str, object]:
    candidate_records = [record for record in records if isinstance(record.task, MechanicRankingTask)]
    gluing_records = [record for record in records if isinstance(record.task, GluingTask)]

    def score_candidate(baseline: M0Baseline) -> dict[str, object]:
        predictions: list[PredictionRecord] = []
        for record in candidate_records:
            task = record.task
            assert isinstance(task, MechanicRankingTask)
            prediction = predict_null(task, baseline)
            predictions.append(
                PredictionRecord(
                    record.world.world_id,
                    record.family.value,
                    task.kind.value,
                    task.target_candidate_id,
                    prediction,
                    prediction == task.target_candidate_id,
                )
            )
        return _metrics(predictions)

    return {
        "candidate_position_only": score_candidate(M0Baseline.FIRST_CANDIDATE),
        "opaque_identity_only": score_candidate(M0Baseline.LEXICOGRAPHIC_ID),
        "hash_payload_only": score_candidate(M0Baseline.HASH_PARITY),
        "gluing_always_glue": {
            "accuracy": sum(
                int(record.task.target_label == "GLUE")
                for record in gluing_records
                if isinstance(record.task, GluingTask)
            )
            / len(gluing_records)
            if gluing_records
            else None
        },
    }


def _overall_view_metrics(
    predictions_by_task: Mapping[str, Sequence[PredictionRecord]],
    *,
    split: GeneratedSplit,
    mode: ViewMode,
) -> dict[str, object]:
    combined = tuple(
        prediction
        for task_predictions in predictions_by_task.values()
        for prediction in task_predictions
    )
    metrics = _metrics(combined)
    ceiling = analyze_identifiability(split.worlds, mode).deterministic_accuracy_ceiling
    accuracy = float(metrics["accuracy"] or 0.0)
    metrics["exact_view_deterministic_accuracy_ceiling"] = ceiling
    metrics["ceiling_gap"] = ceiling - accuracy
    metrics["ceiling_violation"] = accuracy > ceiling + 1e-12
    return metrics


def _diagnose(
    view_results: Mapping[str, Mapping[str, object]],
) -> str:
    if any(bool(result["test_overall"]["ceiling_violation"]) for result in view_results.values()):  # type: ignore[index]
        return "M1_LEAKAGE_OR_EVALUATOR_FAILURE"

    semantic = view_results[ViewMode.SEMANTIC.value]
    semantic_accuracy = float(semantic["test_overall"]["accuracy"])  # type: ignore[index]
    semantic_ceiling = float(semantic["test_overall"]["exact_view_deterministic_accuracy_ceiling"])  # type: ignore[index]
    if semantic_accuracy >= semantic_ceiling - 1e-12:
        return "M1_SIMPLE_MODELS_SUFFICIENT_FOR_CURRENT_EXACT_WORLDS"

    transport_accuracy = float(
        semantic["test_overall"]["per_family_accuracy"].get(HostileFamily.TRANSPORT_GLUING.value, 0.0)  # type: ignore[index]
    )
    history_accuracy = float(
        semantic["test_overall"]["per_family_accuracy"].get(HostileFamily.FAILURE_HISTORY.value, 0.0)  # type: ignore[index]
    )
    relation_accuracy = float(
        semantic["test_overall"]["per_family_accuracy"].get(HostileFamily.RELATION_SEMANTICS.value, 0.0)  # type: ignore[index]
    )
    if transport_accuracy + 1e-12 < max(history_accuracy, relation_accuracy):
        return "M1_GLOBAL_COMPOSITION_RESIDUAL"
    if history_accuracy + 1e-12 < relation_accuracy:
        return "M1_HISTORY_OR_BINDING_RESIDUAL"
    return "M1_NONLINEAR_RELATIONAL_RESIDUAL"


def run_m1(
    *,
    corpus_seed: str = "p9-m1-classical-v1",
    train_pairs_per_family: int = 64,
    dev_pairs_per_family: int = 24,
    test_pairs_per_family: int = 48,
    train_size_pairs_per_family: Sequence[int] = (4, 8, 16, 32, 64),
    train_order_seed: str = "p9-m1-order-train-v1",
    dev_order_seed: str = "p9-m1-order-dev-v1",
    test_order_seed: str = "p9-m1-order-test-v1",
    alternate_test_order_seed: str = "p9-m1-order-test-alt-v1",
    subject_sha: str | None = None,
) -> dict[str, object]:
    """Execute the frozen M1 train→dev→single-test diagnostic protocol."""

    corpus: GeneratedCorpus = generate_corpus(
        seed=corpus_seed,
        train_pairs_per_family=train_pairs_per_family,
        dev_pairs_per_family=dev_pairs_per_family,
        test_pairs_per_family=test_pairs_per_family,
    )
    corpus.verify()
    view_results: dict[str, dict[str, object]] = {}

    for mode in ViewMode:
        train_records = _records(corpus.train, mode=mode, order_seed=train_order_seed)
        dev_records = _records(corpus.dev, mode=mode, order_seed=dev_order_seed)
        test_records = _records(corpus.test, mode=mode, order_seed=test_order_seed)
        task_results: dict[str, object] = {}
        test_predictions_by_task: dict[str, tuple[PredictionRecord, ...]] = {}

        for task_kind in (TaskKind.MECHANIC_RANKING, TaskKind.GLUING):
            dev_configs = _candidate_dev_configs(
                train_records,
                dev_records,
                task_kind=task_kind,
                mode=mode,
            )
            selected = _select_config(dev_configs)
            model, feature_family, spec = _fit_selected(
                train_records,
                selected,
                task_kind=task_kind,
            )
            test_predictions = _evaluate_model(
                model,
                test_records,
                task_kind=task_kind,
                feature_family=feature_family,
            )
            test_predictions_by_task[task_kind.value] = test_predictions
            record: dict[str, object] = {
                "selected": dict(selected),
                "test": _metrics(test_predictions),
                "test_predictions": [item.payload() for item in test_predictions],
                "test_row_permutation_invariance": _row_permutation_invariance(test_predictions),
                "train_size_curve_dev": _train_size_curve(
                    corpus_seed=corpus_seed,
                    pairs_per_family=train_size_pairs_per_family,
                    mode=mode,
                    order_seed=train_order_seed,
                    dev_records=dev_records,
                    task_kind=task_kind,
                    feature_family=feature_family,
                    spec=spec,
                ),
                "train_label_shuffle_dev": _shuffled_label_sentinel(
                    train_records,
                    dev_records,
                    task_kind=task_kind,
                    feature_family=feature_family,
                    spec=spec,
                ),
                "dev_configurations": list(dev_configs),
            }
            if task_kind is TaskKind.MECHANIC_RANKING:
                record["candidate_order_invariance_test"] = _order_invariance(
                    model,
                    corpus.test,
                    mode=mode,
                    primary_order_seed=test_order_seed,
                    alternate_order_seed=alternate_test_order_seed,
                    feature_family=feature_family,
                )
            task_results[task_kind.value] = record

        overall = _overall_view_metrics(
            test_predictions_by_task,
            split=corpus.test,
            mode=mode,
        )
        view_results[mode.value] = {
            "tasks": task_results,
            "test_overall": overall,
            "m0_test_sentinels": _m0_test_sentinels(test_records),
        }

    terminal = _diagnose(view_results)
    result: dict[str, object] = {
        "schema": "P9.M1Result.v1",
        "protocol": "P9.M1Protocol.v1",
        "subject_sha": subject_sha,
        "corpus_manifest_digest": corpus.manifest_digest,
        "views": view_results,
        "terminal": terminal,
        "scientific_authority": "NONE_DIAGNOSTIC_ONLY",
        "grants_model_promotion": False,
        "grants_paper_readiness": False,
    }
    result["result_digest"] = content_digest(result)
    return result


__all__ = [
    "ModelFamily",
    "ModelSpec",
    "PredictionRecord",
    "frozen_model_specs",
    "run_m1",
]
