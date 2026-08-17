from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path
from typing import Iterable, Sequence

from orion.knowledge.semantics import MeaningRelation, Modality, Polarity, compare_meaning
from orion.study import statistics as stats
from orion.study.p3_public_reference import (
    NONMERGE_RELATIONS,
    PublicReferenceError,
    exact_coordinate_baseline,
    flat_predicate_baseline,
    load_jsonl,
    projection_from_dict,
    validate_case,
)

ABLATIONS = (
    "remove_referent",
    "remove_construct",
    "remove_measurement",
    "remove_temporal_context",
    "remove_modality_polarity_attribution_discourse",
    "force_compatibility_without_obstruction",
)


def _expected(case: dict[str, object]) -> MeaningRelation:
    expected = case["expected"]
    assert isinstance(expected, dict)
    return MeaningRelation(str(expected["meaning_relation"]))


def ablated_relation(case: dict[str, object], ablation: str) -> MeaningRelation:
    validate_case(case)
    if ablation not in ABLATIONS:
        raise PublicReferenceError(f"unknown ablation: {ablation}")
    left = projection_from_dict(case["left_projection"])
    right = projection_from_dict(case["right_projection"])
    if ablation == "remove_referent":
        left, right = replace(left, referent_ids=()), replace(right, referent_ids=())
    elif ablation == "remove_construct":
        left, right = replace(left, construct_ids=()), replace(right, construct_ids=())
    elif ablation == "remove_measurement":
        left, right = replace(left, measurement_ids=()), replace(right, measurement_ids=())
    elif ablation == "remove_temporal_context":
        left, right = (
            replace(left, temporal_context_ids=()),
            replace(right, temporal_context_ids=()),
        )
    elif ablation == "remove_modality_polarity_attribution_discourse":
        left, right = (
            replace(
                left,
                modality=Modality.UNKNOWN,
                polarity=Polarity.UNKNOWN,
                attribution_id="",
                discourse_relation="",
            ),
            replace(
                right,
                modality=Modality.UNKNOWN,
                polarity=Polarity.UNKNOWN,
                attribution_id="",
                discourse_relation="",
            ),
        )
    elif ablation == "force_compatibility_without_obstruction":
        if left.predicate == right.predicate:
            return MeaningRelation.COMPATIBLE
    return compare_meaning(left, right).relation


def _prediction(case: dict[str, object], system: str) -> MeaningRelation:
    if system == "orion":
        left = projection_from_dict(case["left_projection"])
        right = projection_from_dict(case["right_projection"])
        return compare_meaning(left, right).relation
    if system == "flat_predicate_canonicalization":
        return flat_predicate_baseline(case)
    if system == "exact_coordinate_conservative":
        return exact_coordinate_baseline(case)
    if system.startswith("ablation:"):
        return ablated_relation(case, system.split(":", 1)[1])
    raise PublicReferenceError(f"unknown system: {system}")


def _binary_vectors(
    expected: Sequence[MeaningRelation], predicted: Sequence[MeaningRelation]
) -> dict[str, list[float]]:
    vectors: dict[str, list[float]] = {
        "accuracy": [],
        "false_merge": [],
        "false_split": [],
        "abstention": [],
    }
    for gold, pred in zip(expected, predicted, strict=True):
        vectors["accuracy"].append(float(gold is pred))
        vectors["false_merge"].append(
            float(gold in NONMERGE_RELATIONS and pred is MeaningRelation.COMPATIBLE)
        )
        vectors["false_split"].append(
            float(gold is MeaningRelation.COMPATIBLE and pred in NONMERGE_RELATIONS)
        )
        vectors["abstention"].append(float(pred is MeaningRelation.UNRESOLVED))
    return vectors


def _rate_summary(values: Sequence[float]) -> dict[str, float]:
    if not values:
        raise PublicReferenceError("cannot summarize empty vector")
    successes = int(sum(values))
    low, high = stats.wilson_interval(successes, len(values))
    return {
        "rate": successes / len(values),
        "n": float(len(values)),
        "ci95_low": low,
        "ci95_high": high,
    }


def _paired_difference(
    candidate: Sequence[float], baseline: Sequence[float]
) -> dict[str, float]:
    diff, low, high = stats.paired_bootstrap_difference_ci(
        candidate,
        baseline,
        resamples=10_000,
        seed=20260817,
    )
    return {
        "candidate_minus_baseline": diff,
        "ci95_low": low,
        "ci95_high": high,
        "n": float(len(candidate)),
    }


def analyze(cases: Sequence[dict[str, object]]) -> dict[str, object]:
    if not cases:
        raise PublicReferenceError("atlas is empty")
    for case in cases:
        validate_case(case)
    expected = [_expected(case) for case in cases]

    systems = [
        "orion",
        "flat_predicate_canonicalization",
        "exact_coordinate_conservative",
        *[f"ablation:{name}" for name in ABLATIONS],
    ]
    vectors: dict[str, dict[str, list[float]]] = {}
    summaries: dict[str, dict[str, dict[str, float]]] = {}
    for system in systems:
        predicted = [_prediction(case, system) for case in cases]
        vec = _binary_vectors(expected, predicted)
        vectors[system] = vec
        summaries[system] = {
            metric: _rate_summary(values) for metric, values in vec.items()
        }

    fm_diff = _paired_difference(
        vectors["orion"]["false_merge"],
        vectors["flat_predicate_canonicalization"]["false_merge"],
    )
    fs_diff = _paired_difference(
        vectors["orion"]["false_split"],
        vectors["exact_coordinate_conservative"]["false_split"],
    )
    primary = {
        "false_merge_orion_minus_flat": fm_diff,
        "false_split_orion_minus_exact": fs_diff,
        "superiority_margin": -0.05,
        "noninferiority_margin": 0.03,
        "false_merge_margin_met_point_estimate": (
            fm_diff["candidate_minus_baseline"] <= -0.05
        ),
        "false_split_margin_met_point_estimate": (
            fs_diff["candidate_minus_baseline"] <= 0.03
        ),
        "note": (
            "Point-estimate margin flags are descriptive. Publication inference must "
            "also report the paired confidence intervals and the frozen protocol."
        ),
    }

    ablation_deltas: dict[str, dict[str, dict[str, float]]] = {}
    for name in ABLATIONS:
        system = f"ablation:{name}"
        ablation_deltas[name] = {
            "accuracy_ablation_minus_full": _paired_difference(
                vectors[system]["accuracy"], vectors["orion"]["accuracy"]
            ),
            "false_merge_ablation_minus_full": _paired_difference(
                vectors[system]["false_merge"], vectors["orion"]["false_merge"]
            ),
            "false_split_ablation_minus_full": _paired_difference(
                vectors[system]["false_split"], vectors["orion"]["false_split"]
            ),
        }

    return {
        "schema_version": "orion.p3.public-reference-analysis.v1",
        "case_count": len(cases),
        "systems": summaries,
        "primary_comparisons": primary,
        "ablation_deltas": ablation_deltas,
        "statistics": {
            "rate_interval": "Wilson 95%",
            "paired_interval": "paired percentile bootstrap, 10000 resamples",
            "bootstrap_seed": 20260817,
            "unit": "externally grounded mapping case",
        },
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Analyze frozen ORION-P3 public-reference mapping cases"
    )
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        report = analyze(load_jsonl(args.cases))
    except PublicReferenceError as exc:
        print(f"CANNOT_CHECK: {exc}")
        return 3
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
