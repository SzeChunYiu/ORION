#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

from sklearn.feature_extraction import DictVectorizer as _DictVectorizer

HERE = Path(__file__).resolve().parent
VERIFIER = HERE / "verify_s3_independent.py"


def _load_verifier():
    spec = importlib.util.spec_from_file_location("p9_s3_frozen_verifier", VERIFIER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen S3 verifier")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Execution-only amendment: preserve feature dictionaries but avoid the
    # current sklearn sparse-index incompatibility.
    module.DictVectorizer = lambda sparse=True: _DictVectorizer(sparse=False)
    return module


def _project_official(raw: dict[str, object], verifier) -> tuple[dict[str, object], bool]:
    f1 = raw["f1_serialized_generic_binding"]
    f2 = raw["f2_serialized_exact_generic_comparator"]
    dataset = verifier.generate_d1_dataset(
        seed="p9-d1-method-transfer-v1",
        train_instances_per_base_pair=48,
        dev_instances_per_base_pair=16,
        test_instances_per_base_pair=32,
    )
    dataset.verify()

    # Official F2 archive has aggregate 128/128 but not per-case rows. With every
    # case correct, each prediction is logically fixed to its immutable target.
    f2_perfect = (
        int(f2["correct_count"]) == int(f2["sample_count"]) == len(dataset.test)
        and float(f2["accuracy"]) == 1.0
    )
    if not f2_perfect:
        raise RuntimeError("cannot reconstruct absent F2 case-level rows from a non-perfect aggregate")
    f2_rows = [
        {
            "instance_id": row.instance_id,
            "target": row.label.value,
            "prediction": row.label.value,
        }
        for row in dataset.test
    ]

    projected = {
        "dataset_manifest_digest": raw["dataset_manifest_digest"],
        "selected_F1_model": f1["selected"],
        "F1_test": f1["test"],
        "F2_test": f2,
        "F1_test_predictions": f1["test_predictions"],
        "F2_test_predictions": f2_rows,
        "terminal": raw["terminal"],
    }
    return projected, True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("official", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    verifier = _load_verifier()
    raw = json.loads(args.official.read_text(encoding="utf-8"))
    projected, reconstructed = _project_official(raw, verifier)
    reproduced = verifier.reproduce()
    result = verifier.compare(projected, reproduced)
    result["schema"] = "P9.S3IndependentVerification.v1.1"
    result["execution_amendment"] = "DENSE_DICT_VECTORIZER_ONLY"
    result["official_result_digest"] = raw["result_digest"]
    result["official_historical_serialized_accuracy"] = raw["historical_controls"]["TYPED_SERIALIZED_BAG"]["test"]["accuracy"]
    result["f2_case_level_rows_reconstructed_from_perfect_aggregate"] = reconstructed
    if result["status"] == "BOUNDED_VERIFIED":
        result["status"] = "BOUNDED_VERIFIED_WITH_F2_CASE_LEVEL_SCHEMA_LIMITATION"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "material_discrepancies": result["discrepancy_counts"]["material"],
        "independent_terminal": result["independent_terminal"],
        "independent_F1_accuracy": result["independent_F1_accuracy"],
        "independent_F2_accuracy": result["independent_F2_accuracy"],
    }, sort_keys=True))
    return 0 if result["discrepancy_counts"]["material"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
