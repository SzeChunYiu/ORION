"""Protected P9 S3 corrective attribution experiment.

The parent D1 result is immutable and already known. S3 does not alter D1; it
adds one prospectively frozen feature/access arm over the existing typed
serialization and asks how much of the historical held-out-domain gap it
recovers.

This module may access the frozen D1 protected test split only because
S3_RESULT_PROTOCOL_V1.json and S3_PRE_ARTIFACT_EXPECTATION_V1.json were
committed first. It fails closed if the inherited D1 result or dataset digest
differs from the registered parent.
"""

from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path
from typing import Sequence

from sklearn.metrics import f1_score

from orion.transfer.v2.canonical import content_digest

# Import the already-frozen parent D1 v1.2 runtime semantics before binding the
# generator/estimator names below. This changes no D1 science: it is exactly the
# execution path that produced the verified parent result.
from . import d1_runtime as _d1_runtime  # noqa: F401
from .d1 import D1Instance, D1Label, D1View, generate_d1_dataset
from .d1_experiment import _estimator, exact_relational_comparator, model_specs
from .s3_access import (
    serialized_exact_generic_comparator,
    serialized_generic_binding_features,
)


_PARENT_RESULT_DIGEST = "sha256:34003fb8ffcecec6ed01654e40c644ff05b7640be56b398a45efc1e52a30141a"
_PARENT_DATASET_DIGEST = "sha256:2775298457b7bdee815b207733507cd27d55719df314ef6352bb601bd709c19c"
_PREPROTECTED_SUBJECT = "2223bba790a3e631d3f40f20bb46b156bce19b72"
_PARENT_RESULT_RELATIVE = Path(
    "research/extensions/p9-structured-neural/results/D1_RESULT_V1_2.json"
)
_PARENT_VERIFICATION_RELATIVE = Path(
    "research/extensions/p9-structured-neural/results/D1_INDEPENDENT_VERIFICATION_V1_2.json"
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _sequence(row: D1Instance) -> list[str]:
    payload = row.model_payload(D1View.TYPED_SERIALIZED)
    sequence = payload["sequence"]
    if not isinstance(sequence, list):
        raise ValueError("D1 typed serialization sequence missing")
    return list(map(str, sequence))


def _metrics(instances: Sequence[D1Instance], predictions: Sequence[str]) -> dict[str, object]:
    if len(instances) != len(predictions):
        raise ValueError("S3 prediction length mismatch")
    labels = [row.label.value for row in instances]
    correct = [p == y for p, y in zip(predictions, labels, strict=True)]
    per_label: dict[str, list[bool]] = defaultdict(list)
    for label, ok in zip(labels, correct, strict=True):
        per_label[label].append(ok)

    double_mask = [len(row.mutation_coordinates) == 2 for row in instances]
    unresolved_mask = [row.label is D1Label.UNRESOLVED for row in instances]

    def masked(mask: Sequence[bool]) -> float | None:
        values = [ok for ok, keep in zip(correct, mask, strict=True) if keep]
        return (sum(values) / len(values)) if values else None

    return {
        "sample_count": len(instances),
        "correct_count": sum(correct),
        "accuracy": sum(correct) / len(instances) if instances else None,
        "macro_f1": f1_score(
            labels,
            list(predictions),
            labels=[item.value for item in D1Label],
            average="macro",
            zero_division=0,
        ) if instances else None,
        "per_label_accuracy": {
            label: sum(values) / len(values) for label, values in sorted(per_label.items())
        },
        "double_corruption_accuracy": masked(double_mask),
        "unresolved_accuracy": masked(unresolved_mask),
    }


def _parent_guard(root: Path) -> dict[str, object]:
    parent_path = root / _PARENT_RESULT_RELATIVE
    verification_path = root / _PARENT_VERIFICATION_RELATIVE
    if not parent_path.exists() or not verification_path.exists():
        raise RuntimeError("frozen parent D1 result/verification is not present")

    parent = json.loads(parent_path.read_text(encoding="utf-8"))
    verification = json.loads(verification_path.read_text(encoding="utf-8"))
    if parent.get("result_digest") != _PARENT_RESULT_DIGEST:
        raise RuntimeError("parent D1 result digest mismatch")
    if parent.get("dataset_manifest_digest") != _PARENT_DATASET_DIGEST:
        raise RuntimeError("parent D1 dataset digest mismatch")
    if verification.get("status") != "BOUNDED_VERIFIED":
        raise RuntimeError("parent D1 result is not bounded-verified")
    if verification.get("official_result_digest") != _PARENT_RESULT_DIGEST:
        raise RuntimeError("parent D1 verification binds a different result digest")
    if verification.get("dataset_manifest_digest") != _PARENT_DATASET_DIGEST:
        raise RuntimeError("parent D1 verification binds a different dataset digest")
    return parent


def _fit_f1(train: Sequence[D1Instance], spec):
    model = _estimator(spec)
    model.fit(
        [serialized_generic_binding_features(_sequence(row)) for row in train],
        [row.label.value for row in train],
    )
    return model


def _predict_f1(model, rows: Sequence[D1Instance]) -> tuple[str, ...]:
    return tuple(
        map(
            str,
            model.predict(
                [serialized_generic_binding_features(_sequence(row)) for row in rows]
            ),
        )
    )


def _select_f1(train: Sequence[D1Instance], dev: Sequence[D1Instance]):
    dev_rows: list[dict[str, object]] = []
    for spec in model_specs():
        model = _fit_f1(train, spec)
        dev_predictions = _predict_f1(model, dev)
        dev_metrics = _metrics(dev, dev_predictions)
        dev_rows.append({
            "config_id": spec.config_id,
            "family": spec.family,
            "params": spec.as_dict(),
            "complexity_rank": spec.complexity_rank,
            "dev": dev_metrics,
        })
    selected_row = sorted(
        dev_rows,
        key=lambda row: (
            -float(row["dev"]["accuracy"]),  # type: ignore[index]
            int(row["complexity_rank"]),
            str(row["config_id"]),
        ),
    )[0]
    selected = next(
        spec for spec in model_specs() if spec.config_id == selected_row["config_id"]
    )
    return selected, tuple(dev_rows)


def run_s3(*, subject_sha: str | None = None) -> dict[str, object]:
    root = _repo_root()
    parent = _parent_guard(root)

    dataset = generate_d1_dataset(
        seed="p9-d1-method-transfer-v1",
        train_instances_per_base_pair=48,
        dev_instances_per_base_pair=16,
        test_instances_per_base_pair=32,
    )
    dataset.verify()
    if dataset.manifest_digest != _PARENT_DATASET_DIGEST:
        raise RuntimeError("regenerated D1 dataset does not match frozen parent digest")

    # Re-run the already-frozen preprotected equivalence check on train/dev before
    # any protected prediction. The comparator on the right is the independent
    # historical D1 exact relational comparator, not a re-expression of F2.
    preprotected_equivalence = all(
        serialized_exact_generic_comparator(_sequence(row))
        == exact_relational_comparator(row)
        for row in (*dataset.train, *dataset.dev)
    )
    if not preprotected_equivalence:
        raise RuntimeError("S3 train/dev comparator equivalence guard failed")

    selected, dev_configs = _select_f1(dataset.train, dataset.dev)
    f1_model = _fit_f1(dataset.train, selected)
    f1_predictions = _predict_f1(f1_model, dataset.test)
    f2_predictions = tuple(
        serialized_exact_generic_comparator(_sequence(row)) for row in dataset.test
    )

    f1_test = _metrics(dataset.test, f1_predictions)
    f2_test = _metrics(dataset.test, f2_predictions)

    historical_serialized = float(
        parent["results"]["TYPED_SERIALIZED_BAG"]["test"]["accuracy"]
    )
    historical_typed = float(
        parent["results"]["TYPED_RELATIONAL"]["test"]["accuracy"]
    )

    hostile_checks = {
        "parent_result_digest_match": parent["result_digest"] == _PARENT_RESULT_DIGEST,
        "dataset_digest_match": dataset.manifest_digest == _PARENT_DATASET_DIGEST,
        "preprotected_train_dev_equivalence": preprotected_equivalence,
        "F2_case_count_matches": f2_test["sample_count"] == len(dataset.test),
    }

    f1_accuracy = float(f1_test["accuracy"])
    f1_unresolved = float(f1_test["unresolved_accuracy"])
    f1_double = float(f1_test["double_corruption_accuracy"])
    f2_accuracy = float(f2_test["accuracy"])

    if not all(hostile_checks.values()):
        terminal = "CANNOT_CHECK"
    elif (
        f2_accuracy == 1.0
        and f1_accuracy >= 0.99
        and f1_unresolved == 1.0
        and f1_double >= 0.99
    ):
        terminal = "EXPLICIT_RELATION_BINDING_SUFFICIENT"
    elif f2_accuracy == 1.0:
        terminal = "LOSSLESS_SERIALIZATION_PLUS_GENERIC_COMPARISON_SUFFICIENT"
    else:
        terminal = "D1_SERIALIZATION_NOT_RECOVERABLE_BY_GENERIC_BINDING"

    result: dict[str, object] = {
        "schema": "P9.S3AccessAttributionResult.v1",
        "protocol": "P9.S3ProtectedResultProtocol.v1.1",
        "subject_sha": subject_sha,
        "preprotected_subject_sha": _PREPROTECTED_SUBJECT,
        "parent_d1_result_digest": _PARENT_RESULT_DIGEST,
        "dataset_manifest_digest": dataset.manifest_digest,
        "selected_F1_model": {
            "config_id": selected.config_id,
            "family": selected.family,
            "params": selected.as_dict(),
            "complexity_rank": selected.complexity_rank,
        },
        "F1_dev_configurations": list(dev_configs),
        "F1_test": f1_test,
        "F2_test": f2_test,
        "historical_controls": {
            "TYPED_SERIALIZED_BAG_accuracy": historical_serialized,
            "TYPED_RELATIONAL_accuracy": historical_typed,
        },
        "gap_recovered": f1_accuracy - historical_serialized,
        "residual_to_typed_relational": historical_typed - f1_accuracy,
        "hostile_checks": hostile_checks,
        "F1_test_predictions": [
            {
                "instance_id": row.instance_id,
                "target": row.label.value,
                "prediction": prediction,
                "correct": prediction == row.label.value,
                "mutation_count": len(row.mutation_coordinates),
            }
            for row, prediction in zip(dataset.test, f1_predictions, strict=True)
        ],
        "F2_test_predictions": [
            {
                "instance_id": row.instance_id,
                "target": row.label.value,
                "prediction": prediction,
                "correct": prediction == row.label.value,
                "mutation_count": len(row.mutation_coordinates),
            }
            for row, prediction in zip(dataset.test, f2_predictions, strict=True)
        ],
        "terminal": terminal,
        "claim_ceiling": "corrective attribution on the unchanged bounded D1 method-transfer benchmark",
        "scientific_authority": "NONE_UNTIL_INDEPENDENT_REPLAY",
    }
    result["result_digest"] = content_digest(result)
    return result


__all__ = ["run_s3"]
