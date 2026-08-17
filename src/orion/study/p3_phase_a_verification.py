"""Phase A verification scaffolding for the frozen P3 confirmatory result.

Independent scoring, leakage/construction tests, and stronger secondary
baseline *stubs* run on the frozen confirmatory cases. New post-outcome
baselines remain secondary and cannot rewrite the frozen confirmatory claim.
Gold absence is ``CANNOT_CHECK``.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Mapping, Sequence

from orion.study.p3_confirmatory_receipt import (
    GoldUnavailableError,
    PAPER03,
    RECEIPT_DIR,
    load_confirmatory_gold,
    load_primary_gold,
    overlap_report,
    sha256_json,
)
from orion.study.p3_independent_evaluator import DEFAULT_INDEPENDENT_EVALUATOR, IndependentScore
from orion.study.p3_public_reference import (
    exact_coordinate_baseline,
    flat_predicate_baseline,
    evaluate_case,
)

SOURCE_REGISTRY = PAPER03 / "gold" / "PUBLIC_REFERENCE_SOURCE_REGISTRY_V1.json"
PHASE_A_PATH = RECEIPT_DIR / "PHASE_A_VERIFICATION.json"
FORBIDDEN_REGISTRY_TERMINAL_KEYS = {
    "expected",
    "expected_terminal",
    "meaning_relation",
    "gold_label",
    "integration_verdict",
}


@dataclass(frozen=True)
class BaselineResult:
    system_id: str
    status: str
    predicted: str | None
    reason: str = ""


def fail_closed_load_confirmatory() -> list[dict[str, object]]:
    return load_confirmatory_gold()


def independent_scores(
    cases: Sequence[Mapping[str, object]] | None = None,
) -> list[IndependentScore]:
    loaded = list(cases) if cases is not None else fail_closed_load_confirmatory()
    return [DEFAULT_INDEPENDENT_EVALUATOR.score(case) for case in loaded]


def scorer_agreement(
    cases: Sequence[Mapping[str, object]] | None = None,
) -> dict[str, object]:
    loaded = list(cases) if cases is not None else fail_closed_load_confirmatory()
    disagreements: list[dict[str, object]] = []
    for case in loaded:
        incumbent = evaluate_case(dict(case))
        independent = DEFAULT_INDEPENDENT_EVALUATOR.score(case)
        if incumbent.predicted != independent.meaning_relation:
            disagreements.append(
                {
                    "case_id": incumbent.case_id,
                    "incumbent": incumbent.predicted,
                    "independent": independent.meaning_relation,
                    "independent_reasons": list(independent.reasons),
                }
            )
    return {
        "n": len(loaded),
        "agreed": len(loaded) - len(disagreements),
        "disagreements": disagreements,
        "unanimous": not disagreements,
    }


def exact_conservative_control(case: Mapping[str, object]) -> BaselineResult:
    predicted = exact_coordinate_baseline(dict(case))
    return BaselineResult(
        system_id="exact_coordinate_conservative",
        status="SCORED",
        predicted=predicted.value,
        reason="merge only if every exposed coordinate is exactly equal; otherwise UNRESOLVED",
    )


def flat_canonicalization_baseline(case: Mapping[str, object]) -> BaselineResult:
    predicted = flat_predicate_baseline(dict(case))
    return BaselineResult(
        system_id="flat_predicate_canonicalization",
        status="SCORED",
        predicted=predicted.value,
        reason="equal normalized predicate implies merge; otherwise UNRESOLVED",
    )


def scion_like_baseline(_case: Mapping[str, object]) -> BaselineResult:
    return BaselineResult(
        system_id="scion_like_conservative_schema_fusion",
        status="CANNOT_CHECK",
        predicted=None,
        reason="SCION-like evidence-linked fusion is not faithfully implemented; stub only",
    )


def executable_schema_contract_baseline(_case: Mapping[str, object]) -> BaselineResult:
    return BaselineResult(
        system_id="executable_schema_contracts_like",
        status="CANNOT_CHECK",
        predicted=None,
        reason="provenance-aware schema-contract baseline is not faithfully implemented; stub only",
    )


def provenance_world_baseline(_case: Mapping[str, object]) -> BaselineResult:
    return BaselineResult(
        system_id="provenance_world_attributed_statements",
        status="CANNOT_CHECK",
        predicted=None,
        reason="provenance-world/attributed-statement reasoning is not faithfully implemented; stub only",
    )


SECONDARY_BASELINES: dict[str, Callable[[Mapping[str, object]], BaselineResult]] = {
    "exact_coordinate_conservative": exact_conservative_control,
    "flat_predicate_canonicalization": flat_canonicalization_baseline,
    "scion_like_conservative_schema_fusion": scion_like_baseline,
    "executable_schema_contracts_like": executable_schema_contract_baseline,
    "provenance_world_attributed_statements": provenance_world_baseline,
}


def score_secondary_baselines(
    cases: Sequence[Mapping[str, object]] | None = None,
) -> dict[str, object]:
    loaded = list(cases) if cases is not None else fail_closed_load_confirmatory()
    per_system: dict[str, dict[str, object]] = {}
    for name, fn in SECONDARY_BASELINES.items():
        results = [fn(case) for case in loaded]
        statuses = Counter(item.status for item in results)
        predicted = [item.predicted for item in results if item.predicted is not None]
        per_system[name] = {
            "status_counts": dict(statuses),
            "n_scored": len(predicted),
            "n_cannot_check": statuses.get("CANNOT_CHECK", 0),
            "reason": results[0].reason if results else "empty",
        }
    return {
        "n_cases": len(loaded),
        "systems": per_system,
        "note": (
            "Secondary baselines cannot rewrite the frozen confirmatory claim. "
            "Unimplemented stronger baselines remain CANNOT_CHECK."
        ),
    }


def source_registry_terminal_leakage(path: Path = SOURCE_REGISTRY) -> dict[str, object]:
    if not path.is_file():
        raise GoldUnavailableError(f"source registry missing: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    leaked: list[str] = []

    def walk(value: object, prefix: str) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                lowered = str(key).lower()
                here = f"{prefix}.{key}" if prefix else str(key)
                if lowered in FORBIDDEN_REGISTRY_TERMINAL_KEYS:
                    leaked.append(here)
                walk(child, here)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, f"{prefix}[{index}]")

    walk(payload, "")
    return {"leaked_fields": leaked, "clean": not leaked}


def metadata_majority_predictor(
    cases: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    """Leave-one-out majority label from case_family/discipline/dataset only."""

    records: list[tuple[str, str, str]] = []
    for case in cases:
        expected = case["expected"]
        assert isinstance(expected, dict)
        sources = case["source_records"]
        assert isinstance(sources, list) and sources
        dataset = str(sources[0]["dataset"]) if isinstance(sources[0], dict) else ""
        key = f"{case['case_family']}|{case['discipline']}|{dataset}"
        records.append((str(case["case_id"]), key, str(expected["meaning_relation"])))

    correct = 0
    for index, (_case_id, key, label) in enumerate(records):
        others = [item[2] for j, item in enumerate(records) if j != index and item[1] == key]
        if not others:
            others = [item[2] for j, item in enumerate(records) if j != index]
        majority = Counter(others).most_common(1)[0][0] if others else ""
        if majority == label:
            correct += 1
    n = len(records)
    return {
        "n": n,
        "leave_one_out_accuracy": correct / n if n else 0.0,
        "features": "case_family|discipline|dataset",
        "note": (
            "A metadata predictor is a construction diagnostic. High accuracy does not "
            "rewrite confirmatory PASS; it constrains how much of the result could be "
            "read from public fields rather than projections."
        ),
    }


def permutation_diagnostics(cases: Sequence[Mapping[str, object]]) -> dict[str, object]:
    from orion.study.p3_public_reference import summarize

    original = summarize(list(cases))
    reversed_cases = list(reversed(cases))
    reversed_summary = summarize(reversed_cases)
    order_invariant = (
        original["orion"] == reversed_summary["orion"]
        and original["flat_predicate_canonicalization"]
        == reversed_summary["flat_predicate_canonicalization"]
        and original["exact_coordinate_conservative"]
        == reversed_summary["exact_coordinate_conservative"]
    )

    labels = [str(case["expected"]["meaning_relation"]) for case in cases]  # type: ignore[index]
    rotated = labels[1:] + labels[:1]
    shuffled: list[dict[str, object]] = []
    for case, new_label in zip(cases, rotated, strict=True):
        clone = json.loads(json.dumps(case))
        clone["expected"]["meaning_relation"] = new_label
        shuffled.append(clone)
    try:
        permuted = summarize(shuffled)
        perm_changed = permuted["orion"] != original["orion"]
        perm_status = "SCORED"
    except Exception as exc:  # validation may fail on illegal relations for authority
        permuted = None
        perm_changed = True
        perm_status = f"CANNOT_CHECK:{exc}"
    return {
        "case_order_invariant_rates": order_invariant,
        "label_permutation_changes_orion_rates": perm_changed,
        "label_permutation_status": perm_status,
    }


def construction_report(
    cases: Sequence[Mapping[str, object]] | None = None,
) -> dict[str, object]:
    loaded = list(cases) if cases is not None else fail_closed_load_confirmatory()
    primary = load_primary_gold()
    return {
        "source_registry": source_registry_terminal_leakage(),
        "metadata_predictor": metadata_majority_predictor(loaded),
        "permutation": permutation_diagnostics(loaded),
        "overlap_with_primary": overlap_report(list(loaded), primary),
        "source_hash_and_locator_complete": all(
            str(source.get("content_hash", "")).strip()
            and str(source.get("locator", "")).strip()
            and str(source.get("revision", "")).strip()
            for case in loaded
            for source in case["source_records"]  # type: ignore[union-attr]
        ),
    }


def phase_a_report(*, write: bool = False) -> dict[str, object]:
    cases = fail_closed_load_confirmatory()
    report: dict[str, object] = {
        "schema_version": "orion.p3.phase-a-verification.v1",
        "gold_status": "BOUND",
        "independent_evaluator": scorer_agreement(cases),
        "secondary_baselines": score_secondary_baselines(cases),
        "construction": construction_report(cases),
        "frozen_claim_not_rewritten": True,
        "v2_experiment_executed": False,
        "note": (
            "Phase A verifies the frozen confirmatory result. It is not a V2 experiment archive."
        ),
    }
    report["report_sha256"] = sha256_json({k: v for k, v in report.items() if k != "report_sha256"})
    if write:
        RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
        PHASE_A_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> int:
    try:
        report = phase_a_report(write=True)
    except GoldUnavailableError as exc:
        print(str(exc))
        return 3
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
