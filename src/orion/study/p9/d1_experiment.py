"""P9 D1 whole-domain and combinatorial transfer experiment.

The experiment is deliberately classical.  It asks whether exact typed method
structure enables transfer across a held-out procedural domain before a neural
model is justified.  Same-information serialized typed data is included to
separate semantic information from an explicit relational comparison bias.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier

from orion.transfer.v2.canonical import content_digest

from .d1 import D1Dataset, D1Instance, D1Label, D1View, COMPARISON_COORDINATES, generate_d1_dataset


class D1FeatureFamily(str, Enum):
    TRANSCRIPT_BAG = "TRANSCRIPT_BAG"
    UNTYPED_PAIR = "UNTYPED_PAIR"
    TYPED_RELATIONAL = "TYPED_RELATIONAL"
    TYPED_SERIALIZED_BAG = "TYPED_SERIALIZED_BAG"


@dataclass(frozen=True)
class D1ModelSpec:
    family: str
    config_id: str
    params: tuple[tuple[str, object], ...]
    complexity_rank: int

    def as_dict(self) -> dict[str, object]:
        return dict(self.params)


def model_specs() -> tuple[D1ModelSpec, ...]:
    return (
        D1ModelSpec("logistic", "logistic-C0.1", (("C", 0.1),), 0),
        D1ModelSpec("logistic", "logistic-C1", (("C", 1.0),), 1),
        D1ModelSpec("logistic", "logistic-C10", (("C", 10.0),), 2),
        D1ModelSpec("tree", "tree-depth3", (("max_depth", 3),), 10),
        D1ModelSpec("tree", "tree-depth6", (("max_depth", 6),), 11),
        D1ModelSpec("rf", "rf-depth6", (("n_estimators", 200), ("max_depth", 6)), 20),
        D1ModelSpec("rf", "rf-none", (("n_estimators", 300), ("max_depth", None)), 21),
    )


def _estimator(spec: D1ModelSpec) -> Pipeline:
    params = spec.as_dict()
    if spec.family == "logistic":
        # Modern scikit-learn infers multiclass handling from the target.  Do not
        # pin the removed `multi_class` constructor argument: that is environment
        # plumbing, not part of the scientific protocol.
        model = LogisticRegression(
            C=float(params["C"]),
            max_iter=2000,
            random_state=2711,
            solver="liblinear",
        )
    elif spec.family == "tree":
        model = DecisionTreeClassifier(
            max_depth=params["max_depth"],
            min_samples_leaf=2,
            random_state=2712,
        )
    elif spec.family == "rf":
        model = RandomForestClassifier(
            n_estimators=int(params["n_estimators"]),
            max_depth=params["max_depth"],
            min_samples_leaf=2,
            random_state=2713,
            n_jobs=1,
        )
    else:  # pragma: no cover
        raise ValueError(spec.family)
    return Pipeline([("vectorizer", DictVectorizer(sparse=True)), ("model", model)])


def _list_len(value: object) -> int | None:
    return len(value) if isinstance(value, list) else None


def _transcript_features(instance: D1Instance) -> dict[str, object]:
    payload = instance.model_payload(D1View.TRANSCRIPT)
    left = payload["left_actions"]
    right = payload["right_actions"]
    assert isinstance(left, list) and isinstance(right, list)
    # Raw reminted tokens may enter this bag; they are disjoint across splits by
    # construction and therefore serve as a direct memorisation/shortcut control.
    # Measured since (``orion.study.p9.transfer_margins.d1_view_collapse_report``):
    # the disjointness is per *instance*, not per split. ``_surface_tokens`` seeds
    # every symbol on the instance that emitted it, so no token occurs twice
    # anywhere in the corpus, 1,152 of the 1,155 fitted keys occur in exactly one
    # training row, and refitting the vocabulary on the protected split's own
    # domain restores none of them. What survives the vectoriser on the protected
    # split is the three arity counts below, which take (2, 2, True) on all 128
    # cases -- so this arm presents one design-matrix row and its protected
    # accuracy is the prior of whichever label the solver emitted.
    features: dict[str, object] = {
        "left_action_count": len(left),
        "right_action_count": len(right),
        "same_action_count": len(left) == len(right),
    }
    for token in left:
        features[f"left_surface:{token}"] = 1.0
    for token in right:
        features[f"right_surface:{token}"] = 1.0
    return features


def _untyped_features(instance: D1Instance) -> dict[str, object]:
    payload = instance.model_payload(D1View.UNTYPED)
    left = payload["left"]
    right = payload["right"]
    assert isinstance(left, Mapping) and isinstance(right, Mapping)
    left_coords = left["coordinates"]
    right_coords = right["coordinates"]
    assert isinstance(left_coords, Mapping) and isinstance(right_coords, Mapping)
    features: dict[str, object] = {}
    for coordinate in COMPARISON_COORDINATES:
        l = left_coords[coordinate]
        r = right_coords[coordinate]
        assert isinstance(l, Mapping) and isinstance(r, Mapping)
        features[f"{coordinate}:left_present"] = bool(l["present"])
        features[f"{coordinate}:right_present"] = bool(r["present"])
        features[f"{coordinate}:left_unknown"] = bool(l["unknown"])
        features[f"{coordinate}:right_unknown"] = bool(r["unknown"])
        if "length" in l:
            features[f"{coordinate}:left_length"] = int(l["length"])
        if "length" in r:
            features[f"{coordinate}:right_length"] = int(r["length"])
        if "length" in l and "length" in r:
            features[f"{coordinate}:same_length"] = int(l["length"]) == int(r["length"])
    features["dependency_same_topology"] = left["dependency_topology"] == right["dependency_topology"]
    return features


def _typed_relational_features(instance: D1Instance) -> dict[str, object]:
    payload = instance.model_payload(D1View.TYPED)
    left = payload["left"]
    right = payload["right"]
    assert isinstance(left, Mapping) and isinstance(right, Mapping)
    unknown_left = set(map(str, left["unknown_coordinates"]))
    unknown_right = set(map(str, right["unknown_coordinates"]))
    features: dict[str, object] = {}
    for coordinate in COMPARISON_COORDINATES:
        left_key = "dependencies" if coordinate == "dependencies" else coordinate
        right_key = left_key
        unknown = coordinate in unknown_left or coordinate in unknown_right
        features[f"{coordinate}:unknown"] = unknown
        features[f"{coordinate}:equal"] = (not unknown) and left[left_key] == right[right_key]
        l_len = _list_len(left[left_key])
        r_len = _list_len(right[right_key])
        if l_len is not None:
            features[f"{coordinate}:left_length"] = l_len
        if r_len is not None:
            features[f"{coordinate}:right_length"] = r_len
    return features


def _serialized_bag_features(instance: D1Instance) -> dict[str, object]:
    payload = instance.model_payload(D1View.TYPED_SERIALIZED)
    sequence = payload["sequence"]
    assert isinstance(sequence, list)
    # Same typed information but without the explicit left-vs-right equality
    # operator provided by TYPED_RELATIONAL.  Values are held-out-domain specific.
    features: dict[str, object] = {"sequence_length": len(sequence)}
    for token in sequence:
        features[f"token:{token}"] = 1.0
    return features


def features(instance: D1Instance, family: D1FeatureFamily) -> dict[str, object]:
    if family is D1FeatureFamily.TRANSCRIPT_BAG:
        return _transcript_features(instance)
    if family is D1FeatureFamily.UNTYPED_PAIR:
        return _untyped_features(instance)
    if family is D1FeatureFamily.TYPED_RELATIONAL:
        return _typed_relational_features(instance)
    if family is D1FeatureFamily.TYPED_SERIALIZED_BAG:
        return _serialized_bag_features(instance)
    raise ValueError(family)


def _fit(instances: Sequence[D1Instance], family: D1FeatureFamily, spec: D1ModelSpec) -> Pipeline:
    model = _estimator(spec)
    model.fit([features(row, family) for row in instances], [row.label.value for row in instances])
    return model


def _predict(model: Pipeline, instances: Sequence[D1Instance], family: D1FeatureFamily) -> tuple[str, ...]:
    return tuple(map(str, model.predict([features(row, family) for row in instances])))


def _metrics(instances: Sequence[D1Instance], predictions: Sequence[str]) -> dict[str, object]:
    if len(instances) != len(predictions):
        raise ValueError("D1 prediction length mismatch")
    labels = [row.label.value for row in instances]
    correct = [prediction == label for prediction, label in zip(predictions, labels, strict=True)]
    per_label: dict[str, list[bool]] = defaultdict(list)
    for label, ok in zip(labels, correct, strict=True):
        per_label[label].append(ok)
    double_mask = [len(row.mutation_coordinates) == 2 for row in instances]
    unresolved_mask = [row.label is D1Label.UNRESOLVED for row in instances]

    def masked_accuracy(mask: Sequence[bool]) -> float | None:
        selected = [ok for ok, keep in zip(correct, mask, strict=True) if keep]
        return (sum(selected) / len(selected)) if selected else None

    return {
        "sample_count": len(instances),
        "correct_count": sum(correct),
        "accuracy": sum(correct) / len(instances) if instances else None,
        "macro_f1": f1_score(labels, list(predictions), labels=[x.value for x in D1Label], average="macro", zero_division=0) if instances else None,
        "per_label_accuracy": {
            label: sum(values) / len(values) for label, values in sorted(per_label.items())
        },
        "double_corruption_accuracy": masked_accuracy(double_mask),
        "unresolved_accuracy": masked_accuracy(unresolved_mask),
    }


def _select(train: Sequence[D1Instance], dev: Sequence[D1Instance], family: D1FeatureFamily) -> tuple[D1ModelSpec, tuple[dict[str, object], ...]]:
    rows: list[dict[str, object]] = []
    for spec in model_specs():
        model = _fit(train, family, spec)
        dev_predictions = _predict(model, dev, family)
        metrics = _metrics(dev, dev_predictions)
        rows.append({
            "config_id": spec.config_id,
            "family": spec.family,
            "params": spec.as_dict(),
            "complexity_rank": spec.complexity_rank,
            "dev": metrics,
        })
    selected_row = sorted(rows, key=lambda row: (-float(row["dev"]["accuracy"]), int(row["complexity_rank"]), str(row["config_id"])))[0]  # type: ignore[index]
    selected = next(spec for spec in model_specs() if spec.config_id == selected_row["config_id"])
    return selected, tuple(rows)


def exact_relational_comparator(instance: D1Instance) -> str:
    """Deterministic ceiling for the typed relational representation."""

    row = _typed_relational_features(instance)
    if any(bool(row[f"{coordinate}:unknown"]) for coordinate in COMPARISON_COORDINATES):
        return D1Label.UNRESOLVED.value
    if any(not bool(row[f"{coordinate}:equal"]) for coordinate in COMPARISON_COORDINATES):
        return D1Label.OBSTRUCTION.value
    return D1Label.ALIGNED.value


def run_d1(
    *,
    seed: str = "p9-d1-method-transfer-v1",
    train_instances_per_base_pair: int = 48,
    dev_instances_per_base_pair: int = 16,
    test_instances_per_base_pair: int = 32,
    subject_sha: str | None = None,
) -> dict[str, object]:
    dataset: D1Dataset = generate_d1_dataset(
        seed=seed,
        train_instances_per_base_pair=train_instances_per_base_pair,
        dev_instances_per_base_pair=dev_instances_per_base_pair,
        test_instances_per_base_pair=test_instances_per_base_pair,
    )
    dataset.verify()
    results: dict[str, object] = {}
    for family in D1FeatureFamily:
        selected, dev_configs = _select(dataset.train, dataset.dev, family)
        model = _fit(dataset.train, family, selected)
        predictions = _predict(model, dataset.test, family)
        results[family.value] = {
            "selected": {
                "config_id": selected.config_id,
                "family": selected.family,
                "params": selected.as_dict(),
                "complexity_rank": selected.complexity_rank,
            },
            "dev_configurations": list(dev_configs),
            "test": _metrics(dataset.test, predictions),
            "test_predictions": [
                {
                    "instance_id": row.instance_id,
                    "target": row.label.value,
                    "prediction": prediction,
                    "correct": prediction == row.label.value,
                    "mutation_count": len(row.mutation_coordinates),
                }
                for row, prediction in zip(dataset.test, predictions, strict=True)
            ],
        }

    oracle_predictions = tuple(exact_relational_comparator(row) for row in dataset.test)
    oracle = _metrics(dataset.test, oracle_predictions)
    typed_accuracy = float(results[D1FeatureFamily.TYPED_RELATIONAL.value]["test"]["accuracy"])  # type: ignore[index]
    transcript_accuracy = float(results[D1FeatureFamily.TRANSCRIPT_BAG.value]["test"]["accuracy"])  # type: ignore[index]
    serialized_accuracy = float(results[D1FeatureFamily.TYPED_SERIALIZED_BAG.value]["test"]["accuracy"])  # type: ignore[index]

    if oracle["accuracy"] != 1.0:
        terminal = "D1_EVALUATOR_FAILURE"
    elif typed_accuracy >= 0.999999 and typed_accuracy > transcript_accuracy + 0.20:
        terminal = "D1_TYPED_STRUCTURE_TRANSFER_SUPPORTED"
    elif typed_accuracy > transcript_accuracy + 0.10:
        terminal = "D1_TYPED_STRUCTURE_TRANSFER_NARROWED"
    else:
        terminal = "D1_NO_TYPED_TRANSFER_ADVANTAGE"

    result: dict[str, object] = {
        "schema": "P9.D1MethodTransferResult.v1",
        "protocol": "P9.D1MethodTransferProtocol.v1.1",
        "subject_sha": subject_sha,
        "dataset_manifest_digest": dataset.manifest_digest,
        "train_domains": ["numerical_methods", "graph_algorithms"],
        "test_domain": "transactional_workflows",
        "results": results,
        "exact_typed_relational_comparator": oracle,
        "typed_minus_transcript": typed_accuracy - transcript_accuracy,
        "typed_minus_same_information_serialized": typed_accuracy - serialized_accuracy,
        "terminal": terminal,
        "claim_ceiling": "exact authored/procedural method-structure transfer across three bounded domains",
        "scientific_authority": "NONE_UNTIL_INDEPENDENT_VERIFICATION",
        "grants_paper_readiness": False,
    }
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
