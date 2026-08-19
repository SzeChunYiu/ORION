#!/usr/bin/env python3
"""Independent verifier for P9 S3 access attribution.

This implementation is frozen before the official S3 artifact exists.  It does
not import `s3_access` or `s3_result`.  It independently parses the D1 typed
serialization, reconstructs the generic comparison features, rebuilds the
registered classical model grid, and compares its predictions to an official
result JSON supplied later.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
from typing import Iterable, Sequence

from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier

# Parent D1 v1.2 runtime side effects are part of the frozen parent dataset.
from orion.study.p9 import d1_runtime as _d1_runtime  # noqa: F401
from orion.study.p9.d1 import (
    COMPARISON_COORDINATES,
    D1Instance,
    D1Label,
    D1View,
    generate_d1_dataset,
)


PARENT_RESULT_DIGEST = "sha256:34003fb8ffcecec6ed01654e40c644ff05b7640be56b398a45efc1e52a30141a"
DATASET_DIGEST = "sha256:2775298457b7bdee815b207733507cd27d55719df314ef6352bb601bd709c19c"


def _sequence(row: D1Instance) -> list[str]:
    payload = row.model_payload(D1View.TYPED_SERIALIZED)
    sequence = payload["sequence"]
    if not isinstance(sequence, list):
        raise ValueError("typed serialization missing")
    return list(map(str, sequence))


def _path(token: str) -> str:
    if ":LEN=" in token:
        return token.split(":LEN=", 1)[0]
    if "=" in token:
        return token.split("=", 1)[0]
    raise ValueError(f"bad serialized token: {token!r}")


def _unknowns(tokens: Iterable[str], side: str) -> frozenset[str]:
    prefix = f"root.{side}.unknown_coordinates[]="
    values = {
        token[len(prefix) :]
        for token in tokens
        if token.startswith(prefix)
    }
    if any(value not in COMPARISON_COORDINATES for value in values):
        raise ValueError("serialization contains unknown coordinate name")
    return frozenset(values)


def independent_features(sequence: list[str]) -> dict[str, object]:
    """Independent V1.2 parser: preserve within-coordinate token order."""

    tokens = tuple(map(str, sequence))
    left_unknown = _unknowns(tokens, "left")
    right_unknown = _unknowns(tokens, "right")
    groups: dict[tuple[str, str], list[str]] = defaultdict(list)

    for token in tokens:
        path = _path(token)
        for side in ("left", "right"):
            prefix = f"root.{side}."
            if not path.startswith(prefix):
                continue
            remainder = path[len(prefix) :]
            for coordinate in COMPARISON_COORDINATES:
                if remainder == coordinate or remainder.startswith(f"{coordinate}["):
                    groups[(side, coordinate)].append(
                        "root.side." + token[len(prefix) :]
                    )
                    break
            break

    out: dict[str, object] = {}
    for coordinate in COMPARISON_COORDINATES:
        left = tuple(groups.get(("left", coordinate), ()))
        right = tuple(groups.get(("right", coordinate), ()))
        if not left or not right:
            raise ValueError(f"coordinate missing from serialization: {coordinate}")
        unknown = coordinate in left_unknown or coordinate in right_unknown
        out[f"{coordinate}:unknown"] = unknown
        out[f"{coordinate}:equal"] = (not unknown) and left == right
    return out


def independent_exact(sequence: list[str]) -> str:
    row = independent_features(sequence)
    if any(bool(row[f"{coordinate}:unknown"]) for coordinate in COMPARISON_COORDINATES):
        return D1Label.UNRESOLVED.value
    if any(not bool(row[f"{coordinate}:equal"]) for coordinate in COMPARISON_COORDINATES):
        return D1Label.OBSTRUCTION.value
    return D1Label.ALIGNED.value


def _specs() -> tuple[dict[str, object], ...]:
    return (
        {"family": "logistic", "config_id": "logistic-C0.1", "C": 0.1, "complexity_rank": 0},
        {"family": "logistic", "config_id": "logistic-C1", "C": 1.0, "complexity_rank": 1},
        {"family": "logistic", "config_id": "logistic-C10", "C": 10.0, "complexity_rank": 2},
        {"family": "tree", "config_id": "tree-depth3", "max_depth": 3, "complexity_rank": 10},
        {"family": "tree", "config_id": "tree-depth6", "max_depth": 6, "complexity_rank": 11},
        {"family": "rf", "config_id": "rf-depth6", "n_estimators": 200, "max_depth": 6, "complexity_rank": 20},
        {"family": "rf", "config_id": "rf-none", "n_estimators": 300, "max_depth": None, "complexity_rank": 21},
    )


def _model(spec: dict[str, object]) -> Pipeline:
    family = spec["family"]
    if family == "logistic":
        estimator = LogisticRegression(
            C=float(spec["C"]),
            max_iter=2000,
            random_state=2711,
            solver="lbfgs",
        )
    elif family == "tree":
        estimator = DecisionTreeClassifier(
            max_depth=spec["max_depth"],
            min_samples_leaf=2,
            random_state=2712,
        )
    elif family == "rf":
        estimator = RandomForestClassifier(
            n_estimators=int(spec["n_estimators"]),
            max_depth=spec["max_depth"],
            min_samples_leaf=2,
            random_state=2713,
            n_jobs=1,
        )
    else:
        raise ValueError(family)
    return Pipeline([("vectorizer", DictVectorizer(sparse=True)), ("model", estimator)])


def _metrics(rows: Sequence[D1Instance], predictions: Sequence[str]) -> dict[str, object]:
    labels = [row.label.value for row in rows]
    correct = [p == y for p, y in zip(predictions, labels, strict=True)]
    double = [len(row.mutation_coordinates) == 2 for row in rows]
    unresolved = [row.label is D1Label.UNRESOLVED for row in rows]

    def masked(mask):
        values = [ok for ok, keep in zip(correct, mask, strict=True) if keep]
        return sum(values) / len(values) if values else None

    return {
        "sample_count": len(rows),
        "correct_count": sum(correct),
        "accuracy": sum(correct) / len(rows),
        "macro_f1": f1_score(
            labels,
            list(predictions),
            labels=[item.value for item in D1Label],
            average="macro",
            zero_division=0,
        ),
        "double_corruption_accuracy": masked(double),
        "unresolved_accuracy": masked(unresolved),
    }


def reproduce() -> dict[str, object]:
    dataset = generate_d1_dataset(
        seed="p9-d1-method-transfer-v1",
        train_instances_per_base_pair=48,
        dev_instances_per_base_pair=16,
        test_instances_per_base_pair=32,
    )
    dataset.verify()
    if dataset.manifest_digest != DATASET_DIGEST:
        raise RuntimeError("independent verifier dataset digest mismatch")

    dev_table: list[dict[str, object]] = []
    fitted: dict[str, Pipeline] = {}
    for spec in _specs():
        model = _model(spec)
        model.fit(
            [independent_features(_sequence(row)) for row in dataset.train],
            [row.label.value for row in dataset.train],
        )
        pred = tuple(map(str, model.predict([independent_features(_sequence(row)) for row in dataset.dev])))
        metrics = _metrics(dataset.dev, pred)
        dev_table.append({**spec, "dev": metrics})
        fitted[str(spec["config_id"])] = model

    selected = sorted(
        dev_table,
        key=lambda row: (
            -float(row["dev"]["accuracy"]),
            int(row["complexity_rank"]),
            str(row["config_id"]),
        ),
    )[0]
    model = fitted[str(selected["config_id"])]
    f1_predictions = tuple(map(str, model.predict([independent_features(_sequence(row)) for row in dataset.test])))
    f2_predictions = tuple(independent_exact(_sequence(row)) for row in dataset.test)

    return {
        "dataset_manifest_digest": dataset.manifest_digest,
        "selected_config_id": selected["config_id"],
        "F1_test": _metrics(dataset.test, f1_predictions),
        "F2_test": _metrics(dataset.test, f2_predictions),
        "F1_predictions": [
            {"instance_id": row.instance_id, "target": row.label.value, "prediction": prediction}
            for row, prediction in zip(dataset.test, f1_predictions, strict=True)
        ],
        "F2_predictions": [
            {"instance_id": row.instance_id, "target": row.label.value, "prediction": prediction}
            for row, prediction in zip(dataset.test, f2_predictions, strict=True)
        ],
    }


def compare(official: dict[str, object], reproduced: dict[str, object]) -> dict[str, object]:
    discrepancies: list[dict[str, object]] = []

    def check(name: str, left, right, *, material: bool = True):
        if left != right:
            discrepancies.append({
                "field": name,
                "official": left,
                "independent": right,
                "material": material,
            })

    check("dataset_manifest_digest", official.get("dataset_manifest_digest"), reproduced["dataset_manifest_digest"])
    check("selected_config_id", official["selected_F1_model"]["config_id"], reproduced["selected_config_id"])
    for section in ("F1_test", "F2_test"):
        for field in ("sample_count", "correct_count", "accuracy", "macro_f1", "double_corruption_accuracy", "unresolved_accuracy"):
            check(f"{section}.{field}", official[section][field], reproduced[section][field])

    official_f1 = [
        {"instance_id": row["instance_id"], "target": row["target"], "prediction": row["prediction"]}
        for row in official["F1_test_predictions"]
    ]
    official_f2 = [
        {"instance_id": row["instance_id"], "target": row["target"], "prediction": row["prediction"]}
        for row in official["F2_test_predictions"]
    ]
    check("F1_predictions", official_f1, reproduced["F1_predictions"])
    check("F2_predictions", official_f2, reproduced["F2_predictions"])

    f1 = float(reproduced["F1_test"]["accuracy"])
    f1_double = float(reproduced["F1_test"]["double_corruption_accuracy"])
    f1_unresolved = float(reproduced["F1_test"]["unresolved_accuracy"])
    f2 = float(reproduced["F2_test"]["accuracy"])
    expected_terminal = (
        "EXPLICIT_RELATION_BINDING_SUFFICIENT"
        if f2 == 1.0 and f1 >= 0.99 and f1_double >= 0.99 and f1_unresolved == 1.0
        else "LOSSLESS_SERIALIZATION_PLUS_GENERIC_COMPARISON_SUFFICIENT"
        if f2 == 1.0
        else "D1_SERIALIZATION_NOT_RECOVERABLE_BY_GENERIC_BINDING"
    )
    check("terminal", official.get("terminal"), expected_terminal)

    material = sum(1 for item in discrepancies if item["material"])
    return {
        "schema": "P9.S3IndependentVerification.v1",
        "preartifact_verifier": True,
        "parent_d1_result_digest": PARENT_RESULT_DIGEST,
        "discrepancies": discrepancies,
        "discrepancy_counts": {
            "total": len(discrepancies),
            "material": material,
            "non_material": len(discrepancies) - material,
        },
        "status": "BOUNDED_VERIFIED" if material == 0 else "DISAGREEMENT_BLOCKS_PROMOTION",
        "independent_terminal": expected_terminal,
        "independent_F1_accuracy": f1,
        "independent_F2_accuracy": f2,
        "authority": "INDEPENDENT_DIAGNOSTIC_ONLY",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("official", type=Path)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    official = json.loads(args.official.read_text(encoding="utf-8"))
    reproduced = reproduce()
    result = compare(official, reproduced)
    encoded = json.dumps(result, sort_keys=True, indent=2)
    print(encoded)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded + "\n", encoding="utf-8")
    return 0 if result["status"] == "BOUNDED_VERIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
