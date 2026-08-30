#!/usr/bin/env python3
"""Structurally separate replay of the frozen ORION-13 mapping result.

This verifier deliberately imports no ORION package code.  It reads the frozen
case records, implements the published coordinate decision rule and both
comparators directly, and recomputes the paired bootstrap intervals.  The
result is a same-repository, same-custody implementation check; it is not an
external or cross-host replication.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from pathlib import Path
from statistics import mean
from typing import Any, Iterable, Sequence


SCRIPT = Path(__file__).resolve()
PAPER = SCRIPT.parents[1]
CONFIRMATORY = (
    PAPER
    / "gold"
    / "adjudicated"
    / "public-reference-v1.1-confirmatory"
    / "PUBLIC_REFERENCE_GOLD_V1.jsonl"
)
INITIAL = (
    PAPER
    / "gold"
    / "adjudicated"
    / "public-reference-v1"
    / "PUBLIC_REFERENCE_GOLD_V1.jsonl"
)
FROZEN_ANALYSIS = (
    PAPER
    / "evidence"
    / "public-reference-v1.1-confirmatory"
    / "CONFIRMATORY_ANALYSIS.json"
)
RECEIPT = PAPER / "editorial" / "INDEPENDENT_CONFIRMATORY_REPLAY.json"

CONFIRMATORY_SHA256 = "13a76c68c149c2552f3543babeca6e1ad5afe23c45ea9c0dc365c1445cf2782b"
INITIAL_SHA256 = "35f9e39b75ff53b7f0ec82cd03ebcaaa82509ee0aea3f5b96aac3fd62c854ed8"
SEED = 20260817
RESAMPLES = 10_000

COMPATIBLE = "COMPATIBLE"
UNRESOLVED = "UNRESOLVED"
NONMERGE = {
    "CONTRADICTORY",
    "CONTEXTUAL_DIFFERENCE",
    "DISTINCT_REFERENT",
    "DISTINCT_CONSTRUCT",
    "DISTINCT_MEASUREMENT",
}

LIST_FIELDS = (
    "argument_roles",
    "referent_ids",
    "construct_ids",
    "measurement_ids",
    "temporal_context_ids",
    "assumption_ids",
    "unresolved_ambiguities",
)
TEXT_FIELDS = ("predicate", "discourse_relation", "attribution_id")


class ReplayError(ValueError):
    """The independent replay cannot establish the frozen result."""


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_json(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def load_jsonl(path: Path, expected_sha256: str) -> list[dict[str, Any]]:
    if not path.is_file():
        raise ReplayError(f"required case archive is missing: {path}")
    digest = sha256_file(path)
    if digest != expected_sha256:
        raise ReplayError(f"case archive digest drifted: {path} ({digest})")
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ReplayError(f"invalid JSON at {path}:{number}") from exc
        if not isinstance(row, dict):
            raise ReplayError(f"case is not an object at {path}:{number}")
        rows.append(row)
    if not rows:
        raise ReplayError(f"case archive is empty: {path}")
    return rows


def as_list(projection: dict[str, Any], field: str) -> tuple[Any, ...]:
    value = projection.get(field, [])
    if not isinstance(value, list):
        raise ReplayError(f"projection field {field} is not an array")
    normalized: list[Any] = []
    for item in value:
        if isinstance(item, list):
            normalized.append(tuple(item))
        else:
            normalized.append(item)
    return tuple(normalized)


def as_text(projection: dict[str, Any], field: str, default: str = "") -> str:
    value = projection.get(field, default)
    if not isinstance(value, str):
        raise ReplayError(f"projection field {field} is not text")
    return value


def coordinate_prediction(case: dict[str, Any]) -> str:
    """Replay the published coordinate ordering without importing generator code."""

    left = case.get("left_projection")
    right = case.get("right_projection")
    if not isinstance(left, dict) or not isinstance(right, dict):
        raise ReplayError("case lacks two projection objects")

    if as_list(left, "unresolved_ambiguities") or as_list(right, "unresolved_ambiguities"):
        return UNRESOLVED
    if as_text(left, "predicate") != as_text(right, "predicate"):
        return UNRESOLVED

    for field, relation in (
        ("referent_ids", "DISTINCT_REFERENT"),
        ("construct_ids", "DISTINCT_CONSTRUCT"),
        ("measurement_ids", "DISTINCT_MEASUREMENT"),
    ):
        lvalue, rvalue = as_list(left, field), as_list(right, field)
        if lvalue and rvalue and lvalue != rvalue:
            return relation

    for field in ("temporal_context_ids", "assumption_ids"):
        lvalue, rvalue = as_list(left, field), as_list(right, field)
        if lvalue and rvalue and lvalue != rvalue:
            return "CONTEXTUAL_DIFFERENCE"
    for field in ("attribution_id", "discourse_relation"):
        lvalue, rvalue = as_text(left, field), as_text(right, field)
        if lvalue and rvalue and lvalue != rvalue:
            return "CONTEXTUAL_DIFFERENCE"

    left_modality = as_text(left, "modality", "UNKNOWN")
    right_modality = as_text(right, "modality", "UNKNOWN")
    if left_modality != right_modality:
        return "CONTEXTUAL_DIFFERENCE"

    left_polarity = as_text(left, "polarity", "UNKNOWN")
    right_polarity = as_text(right, "polarity", "UNKNOWN")
    if (
        left_polarity != "UNKNOWN"
        and right_polarity != "UNKNOWN"
        and left_polarity != right_polarity
    ):
        if left_modality == right_modality == "ASSERTED":
            return "CONTRADICTORY"
        return "CONTEXTUAL_DIFFERENCE"
    return COMPATIBLE


def flat_prediction(case: dict[str, Any]) -> str:
    left, right = case["left_projection"], case["right_projection"]
    if not isinstance(left, dict) or not isinstance(right, dict):
        raise ReplayError("case lacks two projection objects")
    return COMPATIBLE if as_text(left, "predicate") == as_text(right, "predicate") else UNRESOLVED


def normalized_projection(projection: dict[str, Any]) -> tuple[Any, ...]:
    return (
        *(as_text(projection, field) for field in TEXT_FIELDS),
        *(as_list(projection, field) for field in LIST_FIELDS),
        as_text(projection, "polarity", "UNKNOWN"),
        as_text(projection, "modality", "UNKNOWN"),
    )


def exact_prediction(case: dict[str, Any]) -> str:
    left, right = case["left_projection"], case["right_projection"]
    if not isinstance(left, dict) or not isinstance(right, dict):
        raise ReplayError("case lacks two projection objects")
    return COMPATIBLE if normalized_projection(left) == normalized_projection(right) else UNRESOLVED


def expected(case: dict[str, Any]) -> str:
    record = case.get("expected")
    if not isinstance(record, dict):
        raise ReplayError("case lacks expected relation")
    value = record.get("meaning_relation")
    if value not in ({COMPATIBLE, UNRESOLVED} | NONMERGE):
        raise ReplayError(f"unsupported expected relation: {value!r}")
    return str(value)


def binary_vectors(gold: Sequence[str], predictions: Sequence[str]) -> dict[str, list[float]]:
    if len(gold) != len(predictions):
        raise ReplayError("prediction length mismatch")
    return {
        "accuracy": [float(g == p) for g, p in zip(gold, predictions, strict=True)],
        "false_merge": [
            float(g in NONMERGE and p == COMPATIBLE)
            for g, p in zip(gold, predictions, strict=True)
        ],
        "false_split": [
            float(g == COMPATIBLE and p in NONMERGE)
            for g, p in zip(gold, predictions, strict=True)
        ],
        "abstention": [float(p == UNRESOLVED) for p in predictions],
    }


def percentile(values: Sequence[float], q: float) -> float:
    ordered = sorted(values)
    position = q * (len(ordered) - 1)
    low, high = math.floor(position), math.ceil(position)
    if low == high:
        return ordered[low]
    weight = position - low
    return ordered[low] * (1.0 - weight) + ordered[high] * weight


def paired_bootstrap(candidate: Sequence[float], baseline: Sequence[float]) -> list[float]:
    differences = tuple(a - b for a, b in zip(candidate, baseline, strict=True))
    rng = random.Random(SEED)
    resampled = [mean(rng.choices(differences, k=len(differences))) for _ in range(RESAMPLES)]
    return [mean(differences), percentile(resampled, 0.025), percentile(resampled, 0.975)]


def metrics(vectors: dict[str, list[float]]) -> dict[str, float]:
    return {name: mean(values) for name, values in vectors.items()}


def locator_keys(cases: Iterable[dict[str, Any]]) -> set[tuple[str, str, str]]:
    keys: set[tuple[str, str, str]] = set()
    for case in cases:
        records = case.get("source_records")
        if not isinstance(records, list):
            raise ReplayError("case lacks source records")
        for record in records:
            if not isinstance(record, dict):
                raise ReplayError("source record is not an object")
            keys.add((str(record.get("dataset")), str(record.get("locator")), str(record.get("content_hash"))))
    return keys


def frozen_primary() -> dict[str, Any]:
    if not FROZEN_ANALYSIS.is_file():
        raise ReplayError("frozen confirmatory analysis is missing")
    data = json.loads(FROZEN_ANALYSIS.read_text(encoding="utf-8"))
    return data["pooled"]["primary_comparisons"]


def build_receipt() -> dict[str, Any]:
    confirmatory = load_jsonl(CONFIRMATORY, CONFIRMATORY_SHA256)
    initial = load_jsonl(INITIAL, INITIAL_SHA256)
    if len(confirmatory) != 32 or len(initial) != 32:
        raise ReplayError("both frozen sets must contain 32 cases")

    case_ids = [str(case.get("case_id", "")) for case in confirmatory]
    initial_ids = {str(case.get("case_id", "")) for case in initial}
    if not all(case_ids) or len(case_ids) != len(set(case_ids)):
        raise ReplayError("confirmatory case identifiers are missing or duplicated")
    case_overlap = sorted(set(case_ids) & initial_ids)
    if case_overlap:
        raise ReplayError(f"confirmatory case identifiers overlap initial set: {case_overlap}")

    gold = [expected(case) for case in confirmatory]
    predictions = {
        "coordinate_governed": [coordinate_prediction(case) for case in confirmatory],
        "flat_predicate": [flat_prediction(case) for case in confirmatory],
        "exact_coordinate": [exact_prediction(case) for case in confirmatory],
    }
    vectors = {name: binary_vectors(gold, values) for name, values in predictions.items()}
    fm = paired_bootstrap(vectors["coordinate_governed"]["false_merge"], vectors["flat_predicate"]["false_merge"])
    fs = paired_bootstrap(vectors["coordinate_governed"]["false_split"], vectors["exact_coordinate"]["false_split"])
    primary_pass = fm[0] <= -0.05 and fm[2] < 0.0 and fs[0] <= 0.03 and fs[2] <= 0.03

    frozen = frozen_primary()
    expected_fm = frozen["false_merge_orion_minus_flat"]
    expected_fs = frozen["false_split_orion_minus_exact"]
    frozen_match = (
        fm
        == [
            expected_fm["candidate_minus_baseline"],
            expected_fm["ci95_low"],
            expected_fm["ci95_high"],
        ]
        and fs
        == [
            expected_fs["candidate_minus_baseline"],
            expected_fs["ci95_low"],
            expected_fs["ci95_high"],
        ]
    )
    if not primary_pass or not frozen_match:
        raise ReplayError("independent replay did not reproduce the frozen primary result")

    decisions = []
    for index, case in enumerate(confirmatory):
        left, right = case["left_projection"], case["right_projection"]
        observed_differences = sorted(
            field
            for field in (*TEXT_FIELDS, *LIST_FIELDS, "polarity", "modality")
            if normalized_projection({**left, "projection_id": ""})
            and (left.get(field, [] if field in LIST_FIELDS else "") != right.get(field, [] if field in LIST_FIELDS else ""))
        )
        decisions.append(
            {
                "case_id": case_ids[index],
                "case_family": str(case.get("case_family")),
                "expected": gold[index],
                "coordinate_governed": predictions["coordinate_governed"][index],
                "flat_predicate": predictions["flat_predicate"][index],
                "exact_coordinate": predictions["exact_coordinate"][index],
                "observed_coordinate_differences": observed_differences,
            }
        )

    locator_overlap = sorted(locator_keys(confirmatory) & locator_keys(initial))
    payload: dict[str, Any] = {
        "schema_version": "orion.orion13.independent-confirmatory-replay.v1",
        "verdict": "REPRODUCED_BY_STRUCTURALLY_SEPARATE_IMPLEMENTATION",
        "authority_boundary": (
            "Standard-library-only replay with no ORION package imports. Same repository and custody; "
            "not external, cross-host, or independent-author replication."
        ),
        "inputs": {
            "confirmatory_gold_sha256": CONFIRMATORY_SHA256,
            "initial_gold_sha256": INITIAL_SHA256,
            "confirmatory_n": len(confirmatory),
            "initial_n": len(initial),
            "case_id_overlap_count": len(case_overlap),
            "source_locator_hash_overlap_count": len(locator_overlap),
            "source_locator_hash_overlap": [": ".join(item) for item in locator_overlap],
        },
        "implementation": {
            "script": str(SCRIPT.relative_to(PAPER)),
            "script_sha256": sha256_file(SCRIPT),
            "imports_orion_package": False,
            "bootstrap_seed": SEED,
            "bootstrap_resamples": RESAMPLES,
        },
        "systems": {name: metrics(value) for name, value in vectors.items()},
        "primary": {
            "false_merge_coordinate_minus_flat": {
                "difference": fm[0],
                "ci95": fm[1:],
            },
            "false_split_coordinate_minus_exact": {
                "difference": fs[0],
                "ci95": fs[1:],
            },
            "predeclared_rule_pass": primary_pass,
            "exact_match_to_frozen_analysis": frozen_match,
        },
        "case_decisions": decisions,
    }
    payload["receipt_sha256"] = hashlib.sha256(canonical_json(payload)).hexdigest()
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        observed = build_receipt()
    except (KeyError, ReplayError, TypeError, ValueError) as exc:
        print(f"CANNOT_CHECK: {exc}")
        return 3
    if args.write:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(observed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        if not RECEIPT.is_file():
            print(f"CANNOT_CHECK: replay receipt is missing: {RECEIPT}")
            return 3
        committed = json.loads(RECEIPT.read_text(encoding="utf-8"))
        if committed != observed:
            print("CANNOT_CHECK: independent replay receipt drifted")
            return 3
    print(json.dumps(observed, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
