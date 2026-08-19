"""Protected P9 S3 all-domain rotation experiment.

Runs the already-frozen S3 relation-access operator across all three D1 whole-domain
holdout rotations.  No S3 adapter, D1 label rule, model grid, or threshold is
modified here.
"""

from __future__ import annotations

from orion.transfer.v2.canonical import content_digest

# Import the protected S3 runtime first so the same dense compatibility transport
# is used for all same-run learned arms.
from . import s3_runtime as _runtime  # noqa: F401
from .d1 import D1Domain, D1View
from .d1_experiment import D1FeatureFamily, _fit, _metrics, _predict, _select
from .s3_access import serialized_exact_generic_comparator
from .s3_experiment import _fit_s3, _predict_s3, _select_s3
from .s3_rotation import DOMAIN_ORDER, generate_rotation_dataset


def _sequence(row) -> list[str]:
    payload = row.model_payload(D1View.TYPED_SERIALIZED)
    sequence = payload["sequence"]
    if not isinstance(sequence, list):
        raise ValueError("serialized D1 sequence missing")
    return list(map(str, sequence))


def _run_rotation(holdout: D1Domain) -> dict[str, object]:
    dataset = generate_rotation_dataset(holdout)

    f1_selected, f1_dev = _select_s3(dataset.train, dataset.dev)
    f1_model = _fit_s3(dataset.train, f1_selected)
    f1_predictions = _predict_s3(f1_model, dataset.test)
    f1 = _metrics(dataset.test, f1_predictions)

    f2_predictions = tuple(serialized_exact_generic_comparator(_sequence(row)) for row in dataset.test)
    f2 = _metrics(dataset.test, f2_predictions)

    controls: dict[str, object] = {}
    for family in (D1FeatureFamily.TYPED_SERIALIZED_BAG, D1FeatureFamily.TYPED_RELATIONAL):
        selected, dev = _select(dataset.train, dataset.dev, family)
        model = _fit(dataset.train, family, selected)
        predictions = _predict(model, dataset.test, family)
        controls[family.value] = {
            "selected": {
                "config_id": selected.config_id,
                "family": selected.family,
                "params": selected.as_dict(),
                "complexity_rank": selected.complexity_rank,
            },
            "dev_configurations": list(dev),
            "test": _metrics(dataset.test, predictions),
        }

    return {
        "holdout": holdout.value,
        "dataset_manifest_digest": dataset.manifest_digest,
        "f1_serialized_generic_binding": {
            "selected": {
                "config_id": f1_selected.config_id,
                "family": f1_selected.family,
                "params": f1_selected.as_dict(),
                "complexity_rank": f1_selected.complexity_rank,
            },
            "dev_configurations": list(f1_dev),
            "test": f1,
        },
        "f2_serialized_exact_generic_comparator": f2,
        "same_run_dense_controls": controls,
    }


def run_s3_domain_rotations(*, subject_sha: str | None = None) -> dict[str, object]:
    rotations = {holdout.value: _run_rotation(holdout) for holdout in DOMAIN_ORDER}

    all_supported = True
    evaluator_failure = False
    for result in rotations.values():
        f1 = result["f1_serialized_generic_binding"]["test"]  # type: ignore[index]
        f2 = result["f2_serialized_exact_generic_comparator"]  # type: ignore[index]
        f3 = result["same_run_dense_controls"][D1FeatureFamily.TYPED_RELATIONAL.value]["test"]  # type: ignore[index]
        if float(f2["accuracy"]) < 0.999999:
            evaluator_failure = True
        if not (
            float(f1["accuracy"]) >= 0.99
            and float(f1["double_corruption_accuracy"]) >= 0.99
            and float(f1["unresolved_accuracy"]) >= 0.999999
            and abs(float(f1["accuracy"]) - float(f3["accuracy"])) <= 0.01
        ):
            all_supported = False

    if evaluator_failure:
        terminal = "SERIALIZED_ACCESS_EVALUATOR_FAILURE"
    elif all_supported:
        terminal = "EXPLICIT_RELATION_BINDING_ALL_DOMAIN_ROTATIONS_SUPPORTED"
    else:
        terminal = "EXPLICIT_RELATION_BINDING_DOMAIN_LIMITED"

    result: dict[str, object] = {
        "schema": "P9.S3DomainRotationResult.v1",
        "protocol": "P9.S3DomainRotationProtocol.v1",
        "subject_sha": subject_sha,
        "execution_transport": "dense_DictVectorizer_S3_compatibility",
        "immutable_original_workflow_sparse_serialized_bag_accuracy": 0.5,
        "rotations": rotations,
        "terminal": terminal,
        "claim_ceiling": "three bounded authored/procedural D1 domains; relation is coordinate equality/unknownness; no graph or broad relational novelty",
        "scientific_authority": "NONE_UNTIL_INDEPENDENT_VERIFICATION",
    }
    result["result_digest"] = content_digest(result)
    return result


__all__ = ["run_s3_domain_rotations"]
