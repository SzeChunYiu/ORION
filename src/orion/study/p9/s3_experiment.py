"""Protected P9 S3 corrective access-attribution experiment.

This experiment runs only after the V1.2 pre-protected gate is green. It reuses
D1's frozen dataset, split, model grid, dev-only selection, and metrics. The only
new learned arm is a generic comparison feature map derived solely from the
existing serialized typed token sequence.
"""

from __future__ import annotations

from typing import Sequence

from orion.transfer.v2.canonical import content_digest

from .d1 import D1Instance, D1View, generate_d1_dataset
from .d1_experiment import (
    D1FeatureFamily,
    D1ModelSpec,
    _estimator,
    _fit,
    _metrics,
    _predict,
    _select,
    exact_relational_comparator,
    model_specs,
)
from .s3_access import (
    serialized_exact_generic_comparator,
    serialized_generic_binding_features,
)


def _sequence(instance: D1Instance) -> list[str]:
    payload = instance.model_payload(D1View.TYPED_SERIALIZED)
    sequence = payload["sequence"]
    if not isinstance(sequence, list):
        raise ValueError("D1 serialized sequence missing")
    return list(map(str, sequence))


def _fit_s3(instances: Sequence[D1Instance], spec: D1ModelSpec):
    model = _estimator(spec)
    model.fit(
        [serialized_generic_binding_features(_sequence(row)) for row in instances],
        [row.label.value for row in instances],
    )
    return model


def _predict_s3(model, instances: Sequence[D1Instance]) -> tuple[str, ...]:
    return tuple(
        map(
            str,
            model.predict(
                [serialized_generic_binding_features(_sequence(row)) for row in instances]
            ),
        )
    )


def _select_s3(
    train: Sequence[D1Instance], dev: Sequence[D1Instance]
) -> tuple[D1ModelSpec, tuple[dict[str, object], ...]]:
    rows: list[dict[str, object]] = []
    for spec in model_specs():
        model = _fit_s3(train, spec)
        dev_predictions = _predict_s3(model, dev)
        metrics = _metrics(dev, dev_predictions)
        rows.append(
            {
                "config_id": spec.config_id,
                "family": spec.family,
                "params": spec.as_dict(),
                "complexity_rank": spec.complexity_rank,
                "dev": metrics,
            }
        )
    selected_row = sorted(
        rows,
        key=lambda row: (
            -float(row["dev"]["accuracy"]),  # type: ignore[index]
            int(row["complexity_rank"]),
            str(row["config_id"]),
        ),
    )[0]
    selected = next(
        spec for spec in model_specs() if spec.config_id == selected_row["config_id"]
    )
    return selected, tuple(rows)


def run_s3_access_attribution(
    *,
    seed: str = "p9-d1-method-transfer-v1",
    train_instances_per_base_pair: int = 48,
    dev_instances_per_base_pair: int = 16,
    test_instances_per_base_pair: int = 32,
    subject_sha: str | None = None,
) -> dict[str, object]:
    dataset = generate_d1_dataset(
        seed=seed,
        train_instances_per_base_pair=train_instances_per_base_pair,
        dev_instances_per_base_pair=dev_instances_per_base_pair,
        test_instances_per_base_pair=test_instances_per_base_pair,
    )
    dataset.verify()

    # Pre-protected invariant is recomputed here and remains explicit in the result.
    train_dev_equivalence = all(
        serialized_exact_generic_comparator(_sequence(row))
        == exact_relational_comparator(row)
        for row in (*dataset.train, *dataset.dev)
    )
    if not train_dev_equivalence:
        raise ValueError("S3 train/dev exact-comparator equivalence failed")

    selected, dev_configs = _select_s3(dataset.train, dataset.dev)
    f1_model = _fit_s3(dataset.train, selected)
    f1_predictions = _predict_s3(f1_model, dataset.test)
    f1_metrics = _metrics(dataset.test, f1_predictions)

    f2_predictions = tuple(
        serialized_exact_generic_comparator(_sequence(row)) for row in dataset.test
    )
    f2_metrics = _metrics(dataset.test, f2_predictions)

    # Historical controls are replayed unchanged with the original D1 feature maps
    # and exact same frozen model-selection policy.
    historical: dict[str, object] = {}
    for family in (
        D1FeatureFamily.TYPED_SERIALIZED_BAG,
        D1FeatureFamily.TYPED_RELATIONAL,
    ):
        h_selected, h_dev_configs = _select(dataset.train, dataset.dev, family)
        h_model = _fit(dataset.train, family, h_selected)
        h_predictions = _predict(h_model, dataset.test, family)
        historical[family.value] = {
            "selected": {
                "config_id": h_selected.config_id,
                "family": h_selected.family,
                "params": h_selected.as_dict(),
                "complexity_rank": h_selected.complexity_rank,
            },
            "dev_configurations": list(h_dev_configs),
            "test": _metrics(dataset.test, h_predictions),
        }

    serialized_accuracy = float(
        historical[D1FeatureFamily.TYPED_SERIALIZED_BAG.value]["test"]["accuracy"]  # type: ignore[index]
    )
    typed_accuracy = float(
        historical[D1FeatureFamily.TYPED_RELATIONAL.value]["test"]["accuracy"]  # type: ignore[index]
    )
    f1_accuracy = float(f1_metrics["accuracy"])
    f2_accuracy = float(f2_metrics["accuracy"])
    f1_unresolved = float(f1_metrics["unresolved_accuracy"])
    f1_double = float(f1_metrics["double_corruption_accuracy"])

    if f2_accuracy < 0.999999:
        terminal = "S3_EVALUATOR_OR_SERIALIZATION_DISCREPANCY"
    elif (
        f1_accuracy >= 0.99
        and f1_unresolved >= 0.999999
        and f1_double >= 0.99
    ):
        terminal = "EXPLICIT_RELATION_BINDING_SUFFICIENT"
    else:
        terminal = "LOSSLESS_SERIALIZATION_PLUS_GENERIC_COMPARISON_SUFFICIENT"

    result: dict[str, object] = {
        "schema": "P9.S3AccessAttributionResult.v1",
        "protocol": "P9.S3AccessAttributionProtocol.v1.2",
        "subject_sha": subject_sha,
        "dataset_manifest_digest": dataset.manifest_digest,
        "train_dev_exact_equivalence": train_dev_equivalence,
        "f1_serialized_generic_binding": {
            "selected": {
                "config_id": selected.config_id,
                "family": selected.family,
                "params": selected.as_dict(),
                "complexity_rank": selected.complexity_rank,
            },
            "dev_configurations": list(dev_configs),
            "test": f1_metrics,
            "test_predictions": [
                {
                    "instance_id": row.instance_id,
                    "target": row.label.value,
                    "prediction": prediction,
                    "correct": prediction == row.label.value,
                    "mutation_count": len(row.mutation_coordinates),
                }
                for row, prediction in zip(dataset.test, f1_predictions, strict=True)
            ],
        },
        "f2_serialized_exact_generic_comparator": f2_metrics,
        "historical_controls": historical,
        "f1_minus_historical_serialized_bag": f1_accuracy - serialized_accuracy,
        "historical_typed_relational_minus_f1": typed_accuracy - f1_accuracy,
        "terminal": terminal,
        "claim_ceiling": "post-result attribution of D1 access/inductive bias only",
        "scientific_authority": "NONE_UNTIL_INDEPENDENT_VERIFICATION",
    }
    result["result_digest"] = content_digest(result)
    return result


__all__ = ["run_s3_access_attribution"]
