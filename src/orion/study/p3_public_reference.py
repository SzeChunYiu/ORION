from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence

from orion.knowledge.semantics import (
    MeaningRelation,
    Modality,
    Polarity,
    ScientificMeaningProjection,
    bridge_compatible,
    compare_meaning,
)

SCHEMA_VERSION = "orion.p3.public-reference-case.v1"
ALLOWED_AUTHORITY = {
    "UPSTREAM_EXPERT",
    "UPSTREAM_HUMAN",
    "DETERMINISTIC_STANDARD",
    "DERIVED_FROM_ALLOWED",
}
FORBIDDEN_AUTHORITY = {
    "LLM_PROPOSAL",
    "HEURISTIC_PROXY",
    "SIMULATED",
    "SELF_LABEL",
}
NONMERGE_RELATIONS = {
    MeaningRelation.CONTRADICTORY,
    MeaningRelation.CONTEXTUAL_DIFFERENCE,
    MeaningRelation.DISTINCT_REFERENT,
    MeaningRelation.DISTINCT_CONSTRUCT,
    MeaningRelation.DISTINCT_MEASUREMENT,
}


class PublicReferenceError(ValueError):
    """A public-reference case is not admissible scientific gold."""


@dataclass(frozen=True)
class CaseOutcome:
    case_id: str
    expected: str
    predicted: str
    correct: bool
    authority: str
    discipline: str
    case_family: str


def canonical_json(payload: object) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def sha256_json(payload: object) -> str:
    return hashlib.sha256(canonical_json(payload)).hexdigest()


def _tuple_strings(value: object) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise PublicReferenceError("projection tuple fields must be JSON arrays")
    return tuple(str(item) for item in value)


def _argument_roles(value: object) -> tuple[tuple[str, str], ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise PublicReferenceError("argument_roles must be an array")
    roles: list[tuple[str, str]] = []
    for pair in value:
        if not isinstance(pair, list) or len(pair) != 2:
            raise PublicReferenceError("argument_roles entries must be [role, value]")
        roles.append((str(pair[0]), str(pair[1])))
    return tuple(roles)


def projection_from_dict(payload: object) -> ScientificMeaningProjection:
    if not isinstance(payload, dict):
        raise PublicReferenceError("projection must be an object")
    try:
        polarity = Polarity(str(payload.get("polarity", "UNKNOWN")))
        modality = Modality(str(payload.get("modality", "UNKNOWN")))
    except ValueError as exc:
        raise PublicReferenceError(f"invalid projection enum: {exc}") from exc
    return ScientificMeaningProjection(
        projection_id=str(payload.get("projection_id", "")),
        source_id=str(payload.get("source_id", "")),
        source_span=str(payload.get("source_span", "")),
        predicate=str(payload.get("predicate", "")),
        argument_roles=_argument_roles(payload.get("argument_roles")),
        referent_ids=_tuple_strings(payload.get("referent_ids")),
        construct_ids=_tuple_strings(payload.get("construct_ids")),
        measurement_ids=_tuple_strings(payload.get("measurement_ids")),
        temporal_context_ids=_tuple_strings(payload.get("temporal_context_ids")),
        discourse_relation=str(payload.get("discourse_relation", "")),
        attribution_id=str(payload.get("attribution_id", "")),
        polarity=polarity,
        modality=modality,
        assumption_ids=_tuple_strings(payload.get("assumption_ids")),
        unresolved_ambiguities=_tuple_strings(payload.get("unresolved_ambiguities")),
    )


def validate_case(case: object) -> dict[str, object]:
    if not isinstance(case, dict):
        raise PublicReferenceError("case must be a JSON object")
    required = {
        "schema_version",
        "case_id",
        "discipline",
        "case_family",
        "source_records",
        "left_projection",
        "right_projection",
        "expected",
    }
    missing = sorted(required - set(case))
    if missing:
        raise PublicReferenceError(f"case missing required keys: {', '.join(missing)}")
    if case["schema_version"] != SCHEMA_VERSION:
        raise PublicReferenceError(f"unsupported schema_version: {case['schema_version']!r}")

    source_records = case["source_records"]
    if not isinstance(source_records, list) or not source_records:
        raise PublicReferenceError("source_records must be a non-empty array")
    for source in source_records:
        if not isinstance(source, dict):
            raise PublicReferenceError("source record must be an object")
        for key in ("dataset", "revision", "locator", "content_hash"):
            if not str(source.get(key, "")).strip():
                raise PublicReferenceError(f"source record missing {key}")
        if "text" in source:
            raise PublicReferenceError(
                "source_records may not vendor upstream text; store a locator and hash instead"
            )

    projection_from_dict(case["left_projection"])
    projection_from_dict(case["right_projection"])

    expected = case["expected"]
    if not isinstance(expected, dict):
        raise PublicReferenceError("expected must be an object")
    try:
        MeaningRelation(str(expected.get("meaning_relation", "")))
    except ValueError as exc:
        raise PublicReferenceError("expected meaning_relation is invalid") from exc
    authority = expected.get("authority")
    if not isinstance(authority, dict):
        raise PublicReferenceError("expected.authority must be an object")
    kind = str(authority.get("kind", ""))
    if kind in FORBIDDEN_AUTHORITY:
        raise PublicReferenceError(f"forbidden gold authority: {kind}")
    if kind not in ALLOWED_AUTHORITY:
        raise PublicReferenceError(f"unknown/non-authoritative gold kind: {kind}")
    evidence = authority.get("evidence")
    if not isinstance(evidence, list) or not evidence or not all(str(x).strip() for x in evidence):
        raise PublicReferenceError("gold authority requires at least one evidence locator")
    if kind == "DERIVED_FROM_ALLOWED":
        derivation = authority.get("derivation")
        if not isinstance(derivation, dict) or not str(derivation.get("rule", "")).strip():
            raise PublicReferenceError("derived gold requires a machine-readable derivation rule")
        rule = str(derivation["rule"]).lower()
        if rule.startswith("llm:") or rule.startswith("heuristic:"):
            raise PublicReferenceError("LLM/heuristic derivation cannot create final gold authority")
    return case


def _authority_kind(case: dict[str, object]) -> str:
    expected = case["expected"]
    assert isinstance(expected, dict)
    authority = expected["authority"]
    assert isinstance(authority, dict)
    return str(authority["kind"])


def _expected_relation(case: dict[str, object]) -> MeaningRelation:
    expected = case["expected"]
    assert isinstance(expected, dict)
    return MeaningRelation(str(expected["meaning_relation"]))


def evaluate_case(case: dict[str, object]) -> CaseOutcome:
    validate_case(case)
    left = projection_from_dict(case["left_projection"])
    right = projection_from_dict(case["right_projection"])
    predicted = compare_meaning(left, right).relation
    expected = _expected_relation(case)
    return CaseOutcome(
        case_id=str(case["case_id"]),
        expected=expected.value,
        predicted=predicted.value,
        correct=predicted is expected,
        authority=_authority_kind(case),
        discipline=str(case["discipline"]),
        case_family=str(case["case_family"]),
    )


def evaluate_bridge_case(case: dict[str, object]) -> CaseOutcome:
    validate_case(case)
    pivot = str(case.get("pivot_referent_id", ""))
    if not pivot:
        raise PublicReferenceError("bridge case requires pivot_referent_id")
    left = projection_from_dict(case["left_projection"])
    right = projection_from_dict(case["right_projection"])
    predicted = bridge_compatible(left, right, pivot_referent_id=pivot).relation
    expected = _expected_relation(case)
    return CaseOutcome(
        case_id=str(case["case_id"]),
        expected=expected.value,
        predicted=predicted.value,
        correct=predicted is expected,
        authority=_authority_kind(case),
        discipline=str(case["discipline"]),
        case_family=str(case["case_family"]),
    )


def flat_predicate_baseline(case: dict[str, object]) -> MeaningRelation:
    """Naive canonicalization: equal normalized predicate implies merge."""
    validate_case(case)
    left = projection_from_dict(case["left_projection"])
    right = projection_from_dict(case["right_projection"])
    if left.predicate == right.predicate:
        return MeaningRelation.COMPATIBLE
    return MeaningRelation.UNRESOLVED


def exact_coordinate_baseline(case: dict[str, object]) -> MeaningRelation:
    """Conservative baseline: merge only if every exposed coordinate is exactly equal."""
    validate_case(case)
    left = projection_from_dict(case["left_projection"])
    right = projection_from_dict(case["right_projection"])
    ignored = {"projection_id", "source_id", "source_span"}
    ldict = {k: v for k, v in asdict(left).items() if k not in ignored}
    rdict = {k: v for k, v in asdict(right).items() if k not in ignored}
    if ldict == rdict:
        return MeaningRelation.COMPATIBLE
    return MeaningRelation.UNRESOLVED


def _rates(expected: Sequence[MeaningRelation], predicted: Sequence[MeaningRelation]) -> dict[str, float]:
    if len(expected) != len(predicted):
        raise ValueError("expected and predicted lengths differ")
    n = len(expected)
    if not n:
        return {
            "accuracy": 0.0,
            "false_merge_rate": 0.0,
            "false_split_rate": 0.0,
            "abstention_rate": 0.0,
        }
    false_merge = sum(
        1 for gold, pred in zip(expected, predicted, strict=True)
        if gold in NONMERGE_RELATIONS and pred is MeaningRelation.COMPATIBLE
    )
    false_split = sum(
        1 for gold, pred in zip(expected, predicted, strict=True)
        if gold is MeaningRelation.COMPATIBLE and pred in NONMERGE_RELATIONS
    )
    abstain = sum(1 for pred in predicted if pred is MeaningRelation.UNRESOLVED)
    correct = sum(1 for gold, pred in zip(expected, predicted, strict=True) if gold is pred)
    return {
        "accuracy": correct / n,
        "false_merge_rate": false_merge / n,
        "false_split_rate": false_split / n,
        "abstention_rate": abstain / n,
    }


def summarize(cases: Sequence[dict[str, object]]) -> dict[str, object]:
    if not cases:
        raise PublicReferenceError("atlas is empty")
    for case in cases:
        validate_case(case)
    expected = [_expected_relation(case) for case in cases]
    orion = [MeaningRelation(evaluate_case(case).predicted) for case in cases]
    flat = [flat_predicate_baseline(case) for case in cases]
    exact = [exact_coordinate_baseline(case) for case in cases]
    disciplines = Counter(str(case["discipline"]) for case in cases)
    families = Counter(str(case["case_family"]) for case in cases)
    authorities = Counter(_authority_kind(case) for case in cases)
    return {
        "schema_version": "orion.p3.public-reference-summary.v1",
        "case_count": len(cases),
        "atlas_sha256": sha256_json(cases),
        "discipline_counts": dict(sorted(disciplines.items())),
        "case_family_counts": dict(sorted(families.items())),
        "authority_counts": dict(sorted(authorities.items())),
        "orion": _rates(expected, orion),
        "flat_predicate_canonicalization": _rates(expected, flat),
        "exact_coordinate_conservative": _rates(expected, exact),
    }


def load_jsonl(path: str | Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for line_number, raw in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            payload = json.loads(raw)
            records.append(validate_case(payload))
        except (json.JSONDecodeError, PublicReferenceError) as exc:
            raise PublicReferenceError(f"{path}:{line_number}: {exc}") from exc
    if not records:
        raise PublicReferenceError(f"{path}: no cases")
    return records


def run_atlas(cases_path: str | Path, output_path: str | Path) -> dict[str, object]:
    cases = load_jsonl(cases_path)
    report = summarize(cases)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate ORION-P3 public-reference atlas")
    parser.add_argument("--cases", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        report = run_atlas(args.cases, args.output)
    except PublicReferenceError as exc:
        print(f"CANNOT_CHECK: {exc}")
        return 3
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
