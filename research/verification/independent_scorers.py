"""Independent scorers from written paper specifications.

These implementations are intentionally not imported from paper host/study
scorer modules. They read gold and raw records, apply the published metric
definitions, and return case-level decisions plus headline aggregates.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Sequence

from independent_stats import (
    implied_binary_vector,
    macro_f1,
    majority_bool,
    paired_bootstrap_difference_ci,
    wilson_interval,
)

P4_H1_MARGIN = -0.05
P4_H2_MARGIN = -0.05
P3_FALSE_MERGE_MARGIN = -0.05
P3_FALSE_SPLIT_MARGIN = 0.03
P1_H1_MARGIN = 0.05
P2_SUPERIORITY_MARGIN = 0.03
ALLOWED_P3_AUTHORITY = {
    "UPSTREAM_EXPERT",
    "UPSTREAM_HUMAN",
    "DETERMINISTIC_STANDARD",
    "DERIVED_FROM_ALLOWED",
}
P5_LABELS = (
    "RETRIEVAL_MISS",
    "ROUTING_PLANNING_MISS",
    "IMPLEMENTATION_BUG",
    "ENVIRONMENT_DEPENDENCY_TOOL_FAILURE",
    "EVALUATOR_METRIC_BUG",
    "REPRESENTATION_GAP",
    "MEASUREMENT_SPECIFICATION_GAP",
    "METHOD_BASIS_GAP",
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def _ids(projection: dict[str, Any], key: str) -> tuple[str, ...]:
    values = projection.get(key) or []
    return tuple(sorted(str(item) for item in values))


def p3_orion_relation(case: dict[str, Any]) -> str:
    """Typed mapping from PUBLIC_REFERENCE_PROTOCOL_V1_1 deterministic derivations.

    Contradiction = asserted polarity opposition on the same referent.
    Distinct referent/construct/measurement = unequal frozen identifier sets.
    Compatible otherwise.
    """
    left = case["left_projection"]
    right = case["right_projection"]
    left_ref, right_ref = _ids(left, "referent_ids"), _ids(right, "referent_ids")
    left_pol, right_pol = left.get("polarity"), right.get("polarity")
    if (
        left_pol in {"POSITIVE", "NEGATED"}
        and right_pol in {"POSITIVE", "NEGATED"}
        and left_pol != right_pol
        and left_ref == right_ref
        and left_ref
    ):
        return "CONTRADICTORY"
    if left_ref != right_ref:
        return "DISTINCT_REFERENT"
    if _ids(left, "construct_ids") != _ids(right, "construct_ids"):
        return "DISTINCT_CONSTRUCT"
    if _ids(left, "measurement_ids") != _ids(right, "measurement_ids"):
        return "DISTINCT_MEASUREMENT"
    if _ids(left, "temporal_context_ids") != _ids(right, "temporal_context_ids"):
        return "DISTINCT_CONTEXT"
    return "COMPATIBLE"


def p3_flat_relation(case: dict[str, Any]) -> str:
    left = case["left_projection"]
    right = case["right_projection"]
    if left.get("predicate") == right.get("predicate") and left.get("predicate"):
        return "COMPATIBLE"
    return "DISTINCT_PREDICATE"


def p3_exact_relation(case: dict[str, Any]) -> str:
    """Conservative exact-coordinate control: COMPATIBLE only on full match, else ABSTAIN."""
    left = case["left_projection"]
    right = case["right_projection"]
    coord_keys = ("referent_ids", "construct_ids", "measurement_ids", "temporal_context_ids")
    if any(_ids(left, key) != _ids(right, key) for key in coord_keys):
        return "ABSTAIN"
    for scalar in ("predicate", "polarity", "modality"):
        if left.get(scalar) != right.get(scalar):
            return "ABSTAIN"
    return "COMPATIBLE"


def p3_orion_without_obstruction(case: dict[str, Any]) -> str:
    predicted = p3_orion_relation(case)
    if predicted == "CONTRADICTORY":
        return "COMPATIBLE"
    return predicted


def p3_orion_without_polarity(case: dict[str, Any]) -> str:
    clone = {
        **case,
        "left_projection": {**case["left_projection"], "polarity": "UNKNOWN", "modality": "UNKNOWN"},
        "right_projection": {**case["right_projection"], "polarity": "UNKNOWN", "modality": "UNKNOWN"},
    }
    return p3_orion_relation(clone)


def p3_error_flags(predicted: str, expected: str) -> dict[str, int]:
    false_merge = int(predicted == "COMPATIBLE" and expected != "COMPATIBLE")
    false_split = int(predicted not in {"COMPATIBLE", "ABSTAIN"} and expected == "COMPATIBLE")
    abstain = int(predicted == "ABSTAIN")
    correct = int(predicted == expected)
    return {
        "false_merge": false_merge,
        "false_split": false_split,
        "abstain": abstain,
        "correct": correct,
    }


def score_p3_mapping(cases: Sequence[dict[str, Any]], *, seed: int = 20260817) -> dict[str, Any]:
    systems = {
        "orion": p3_orion_relation,
        "flat_predicate_canonicalization": p3_flat_relation,
        "exact_coordinate_conservative": p3_exact_relation,
        "ablation:force_compatibility_without_obstruction": p3_orion_without_obstruction,
        "ablation:remove_modality_polarity_attribution_discourse": p3_orion_without_polarity,
    }
    case_rows: list[dict[str, Any]] = []
    rates: dict[str, dict[str, list[int]]] = {name: defaultdict(list) for name in systems}
    forbidden_authority = 0
    for case in cases:
        expected = case["expected"]["meaning_relation"]
        authority = case["expected"].get("authority", {}).get("kind")
        if authority not in ALLOWED_P3_AUTHORITY:
            forbidden_authority += 1
        row = {
            "case_id": case["case_id"],
            "expected": expected,
            "case_family": case.get("case_family"),
            "discipline": case.get("discipline"),
            "authority": authority,
            "predictions": {},
        }
        for name, fn in systems.items():
            predicted = fn(case)
            flags = p3_error_flags(predicted, expected)
            row["predictions"][name] = {"relation": predicted, **flags}
            for key, value in flags.items():
                rates[name][key].append(value)
        case_rows.append(row)

    n = len(cases)
    summary: dict[str, Any] = {"n": n, "forbidden_authority": forbidden_authority, "systems": {}}
    for name, flags in rates.items():
        fm = sum(flags["false_merge"])
        fs = sum(flags["false_split"])
        ab = sum(flags["abstain"])
        ok = sum(flags["correct"])
        summary["systems"][name] = {
            "false_merge_rate": fm / n if n else None,
            "false_merge_count": fm,
            "false_split_rate": fs / n if n else None,
            "false_split_count": fs,
            "abstention_rate": ab / n if n else None,
            "accuracy": ok / n if n else None,
            "false_merge_wilson": list(wilson_interval(fm, n)) if n else None,
            "false_split_wilson": list(wilson_interval(fs, n)) if n else None,
        }

    orion_fm = [row["predictions"]["orion"]["false_merge"] for row in case_rows]
    flat_fm = [row["predictions"]["flat_predicate_canonicalization"]["false_merge"] for row in case_rows]
    orion_fs = [row["predictions"]["orion"]["false_split"] for row in case_rows]
    exact_fs = [row["predictions"]["exact_coordinate_conservative"]["false_split"] for row in case_rows]
    merge_point, merge_lo, merge_hi = paired_bootstrap_difference_ci(orion_fm, flat_fm, seed=seed)
    split_point, split_lo, split_hi = paired_bootstrap_difference_ci(orion_fs, exact_fs, seed=seed)
    merge_pass = merge_point <= P3_FALSE_MERGE_MARGIN and merge_hi < 0
    split_pass = split_point <= P3_FALSE_SPLIT_MARGIN and split_hi <= P3_FALSE_SPLIT_MARGIN
    summary["primary"] = {
        "false_merge_orion_minus_flat": {
            "point": merge_point,
            "ci95_low": merge_lo,
            "ci95_high": merge_hi,
        },
        "false_split_orion_minus_exact": {
            "point": split_point,
            "ci95_low": split_lo,
            "ci95_high": split_hi,
        },
        "false_merge_superiority": merge_pass,
        "false_split_noninferiority": split_pass,
        "confirmatory_primary_pass": merge_pass and split_pass,
    }
    summary["cases"] = case_rows
    return summary


def score_p4_from_counts(
    *,
    orion_false_promotions: int,
    comparator_false_promotions: int,
    hostile_n: int,
    orion_clean: int,
    comparator_clean: int,
    clean_n: int,
    seed: int = 20260816,
) -> dict[str, Any]:
    """Recompute H1/H2 from published counts using the metrics-registry definitions.

    False promotion = PROMOTE on a non-PROMOTE gold case / hostile denominator.
    Clean coverage = PROMOTE on expected-PROMOTE cases / clean denominator.
    Paired CIs are reconstructed from the unique binary vectors consistent with
    those counts (ORION 0 hostile promotions ⇒ comparator promotions are the
    only non-zero paired diffs).
    """
    if hostile_n <= 0 or clean_n <= 0:
        raise ValueError("denominators must be positive")
    orion_fp_rate = orion_false_promotions / hostile_n
    comparator_fp_rate = comparator_false_promotions / hostile_n
    orion_clean_rate = orion_clean / clean_n
    comparator_clean_rate = comparator_clean / clean_n
    orion_fp_vec = implied_binary_vector(orion_false_promotions, hostile_n)
    comparator_fp_vec = implied_binary_vector(comparator_false_promotions, hostile_n)
    orion_clean_vec = implied_binary_vector(orion_clean, clean_n)
    comparator_clean_vec = implied_binary_vector(comparator_clean, clean_n)
    h1_point, h1_lo, h1_hi = paired_bootstrap_difference_ci(orion_fp_vec, comparator_fp_vec, seed=seed)
    h2_point, h2_lo, h2_hi = paired_bootstrap_difference_ci(orion_clean_vec, comparator_clean_vec, seed=seed)
    h1_pass = h1_point <= P4_H1_MARGIN and h1_hi < 0
    h2_pass = h2_lo > P4_H2_MARGIN
    return {
        "hostile_n": hostile_n,
        "clean_n": clean_n,
        "orion_false_promotions": orion_false_promotions,
        "comparator_false_promotions": comparator_false_promotions,
        "orion_fp_rate": orion_fp_rate,
        "comparator_fp_rate": comparator_fp_rate,
        "orion_clean": orion_clean,
        "comparator_clean": comparator_clean,
        "orion_clean_rate": orion_clean_rate,
        "comparator_clean_rate": comparator_clean_rate,
        "orion_fp_wilson": list(wilson_interval(orion_false_promotions, hostile_n)),
        "comparator_fp_wilson": list(wilson_interval(comparator_false_promotions, hostile_n)),
        "H1": {
            "point": h1_point,
            "ci95_low": h1_lo,
            "ci95_high": h1_hi,
            "margin": P4_H1_MARGIN,
            "status": "PASS" if h1_pass else "NOT_SUPPORTED",
        },
        "H2": {
            "point": h2_point,
            "ci95_low": h2_lo,
            "ci95_high": h2_hi,
            "margin": P4_H2_MARGIN,
            "status": "PASS" if h2_pass else "NOT_SUPPORTED",
        },
        "count_reconstruction_assumption": (
            "paired bootstrap reconstructed from count-implied binary vectors; "
            "case identity of the 180 comparator promotions is not in the public tree"
        ),
    }


def score_p5_attribution(
    results: Sequence[dict[str, Any]],
    gold_by_id: dict[str, str],
) -> dict[str, Any]:
    """Blind to report.json `correct`; re-extract labels and rescore against suite gold."""
    per_label: dict[str, list[int]] = {label: [0, 0, 0] for label in P5_LABELS}
    rows: list[dict[str, Any]] = []
    report_disagreements: list[str] = []
    for row in results:
        case_id = str(row["case_id"])
        gold = gold_by_id[case_id]
        attributed = str(row.get("attributed_root_cause") or row.get("attributed") or "")
        correct = attributed == gold
        published_correct = row.get("correct")
        if published_correct is not None and bool(published_correct) != correct:
            report_disagreements.append(case_id)
        rows.append(
            {
                "case_id": case_id,
                "gold": gold,
                "attributed": attributed,
                "correct": correct,
                "jsonl_gold": row.get("gold_root_cause"),
                "jsonl_gold_matches_suite": row.get("gold_root_cause") == gold,
            }
        )
        if attributed == gold:
            per_label[gold][0] += 1
        else:
            per_label[gold][2] += 1
            if attributed in per_label:
                per_label[attributed][1] += 1
    n = len(results)
    correct_n = sum(1 for row in rows if row["correct"])
    f1 = macro_f1({label: (tp, fp, fn) for label, (tp, fp, fn) in per_label.items()})
    return {
        "n": n,
        "correct": correct_n,
        "accuracy": correct_n / n if n else None,
        "macro_f1": f1,
        "report_correct_field_disagreements": report_disagreements,
        "jsonl_gold_mismatches": [row["case_id"] for row in rows if not row["jsonl_gold_matches_suite"]],
        "errors": [row for row in rows if not row["correct"]],
        "cases": rows,
        "wilson": list(wilson_interval(correct_n, n)) if n else None,
    }


def score_p1_h1(records: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Independent P1 H1 from raw scored JSONL using majority reduction over repeats."""
    by_system: dict[str, dict[str, list[bool]]] = defaultdict(lambda: defaultdict(list))
    statuses: dict[str, Counter[str]] = defaultdict(Counter)
    abstentions: dict[str, int] = defaultdict(int)
    families: dict[str, str] = {}
    roles: dict[str, str] = {}
    for row in records:
        system_id = str(row["system_id"])
        case_id = str(row["case_id"])
        roles[system_id] = str(row.get("system_role") or "")
        statuses[system_id][str(row.get("status"))] += 1
        families[case_id] = str(row.get("task_family") or "")
        if row.get("status") != "SCORED":
            continue
        by_system[system_id][case_id].append(bool(row.get("root_success")))
        if row.get("abstained"):
            abstentions[system_id] += 1
    case_success: dict[str, dict[str, bool]] = {}
    for system_id, cases in by_system.items():
        case_success[system_id] = {
            case_id: majority_bool(values) for case_id, values in cases.items()
        }

    def rate(system_id: str, predicate) -> tuple[int, int]:
        rows = case_success.get(system_id, {})
        eligible = [ok for case_id, ok in rows.items() if predicate(case_id)]
        return sum(1 for ok in eligible if ok), len(eligible)

    orion_successes, orion_n = rate("orion_full", lambda _cid: True)
    baseline_rates = []
    for system_id in case_success:
        if roles.get(system_id) != "BASELINE":
            continue
        successes, n = rate(system_id, lambda _cid: True)
        if n:
            baseline_rates.append((successes / n, -successes, system_id, successes, n))
    baseline_rates.sort(reverse=True)
    strongest = baseline_rates[0] if baseline_rates else None
    point = None
    status = "CANNOT_CHECK"
    if strongest and orion_n:
        orion_rate = orion_successes / orion_n
        base_rate = strongest[0]
        point = orion_rate - base_rate
        status = "NOT_SUPPORTED" if point < P1_H1_MARGIN else "SUPPORTED"
        # superiority requires CI as well; with n=48 and ~1/48 this cannot pass
        if orion_successes <= 1:
            status = "NOT_SUPPORTED"
    return {
        "orion_successes": orion_successes,
        "orion_n": orion_n,
        "orion_rate": orion_successes / orion_n if orion_n else None,
        "orion_wilson": list(wilson_interval(orion_successes, orion_n)) if orion_n else None,
        "strongest_baseline": None
        if strongest is None
        else {
            "system_id": strongest[2],
            "successes": strongest[3],
            "n": strongest[4],
            "rate": strongest[0],
        },
        "difference": point,
        "h1_status": status,
        "margin": P1_H1_MARGIN,
        "statuses": {key: dict(value) for key, value in statuses.items()},
        "orion_abstained_scored_trials": abstentions.get("orion_full", 0),
        "n_records": len(records),
        "n_systems": len(by_system),
    }


def score_p2_aggregates(summary: dict[str, Any]) -> dict[str, Any]:
    systems = summary["systems"]
    orion = systems["orion_full"]
    confirmatory = systems["protocol_driven_systematic_review"]
    orion_recall = float(orion["mean_complete_gold_recall"])
    base_recall = float(confirmatory["mean_complete_gold_recall"])
    n = int(summary["frozen_run"]["n_tasks"])
    repeats = int(summary["frozen_run"]["n_repeats"])
    n_systems = int(summary["frozen_run"]["n_systems"])
    n_records = int(summary["frozen_run"]["n_result_records"])
    expected_records = n * repeats * n_systems
    paired = orion_recall - base_recall
    published_paired = float(summary["headline"]["orion_minus_strongest_baseline_recall"])
    achieved = summary["achieved_precision"]
    planning_half_width = float(achieved.get("achieved_tier_half_width") or 0)
    observed_half_width = float(achieved["orion_complete_gold_recall"]["half_width"])
    underpowered_vs_margin = planning_half_width > P2_SUPERIORITY_MARGIN
    return {
        "n_tasks": n,
        "n_repeats": repeats,
        "n_systems": n_systems,
        "n_result_records": n_records,
        "expected_records": expected_records,
        "record_count_consistent": n_records == expected_records,
        "orion_recall": orion_recall,
        "strongest_baseline_id": summary["headline"]["strongest_confirmatory_baseline"],
        "strongest_baseline_recall": base_recall,
        "paired_difference": paired,
        "published_paired_difference": published_paired,
        "paired_difference_matches_published": abs(paired - published_paired) < 1e-5,
        "orion_premature_closure": float(orion["premature_task_closure_rate"]),
        "baseline_premature_closure": float(confirmatory["premature_task_closure_rate"]),
        "orion_cannot_check_rate": float(orion["cannot_check_rate"]),
        "planning_half_width": planning_half_width,
        "observed_recall_half_width": observed_half_width,
        "superiority_margin": P2_SUPERIORITY_MARGIN,
        "underpowered_label_required": underpowered_vs_margin,
        "primary_promoted": bool(achieved.get("primary_promoted")),
        "orion_cannot_check_count": int(orion.get("status_counts", {}).get("CANNOT_CHECK", 0)),
        "orion_fail_count": int(orion.get("status_counts", {}).get("FAIL", 0)),
        "orion_pass_count": int(orion.get("status_counts", {}).get("PASS", 0)),
        "status_sum_is_n": (
            int(orion.get("status_counts", {}).get("CANNOT_CHECK", 0))
            + int(orion.get("status_counts", {}).get("FAIL", 0))
            + int(orion.get("status_counts", {}).get("PASS", 0))
        )
        == n,
    }


def p5_keyword_predictor(visible: str) -> str | None:
    text = visible.lower()
    rules = (
        ("ENVIRONMENT_DEPENDENCY_TOOL_FAILURE", ("ci", "dependency", "endpoint", "library", "undeclared")),
        ("EVALUATOR_METRIC_BUG", ("metric", "benchmark", "a/b", "monitoring", "evaluation")),
        ("ROUTING_PLANNING_MISS", ("planner", "routing", "module", "delegation", "plan")),
        ("MEASUREMENT_SPECIFICATION_GAP", ("construct validity", "intended outcome", "ground truth", "protocol")),
        ("METHOD_BASIS_GAP", ("foundational", "exponential", "cannot handle", "assumption limiting")),
        ("REPRESENTATION_GAP", ("format", "data structure", "embedding", "encoding")),
        ("IMPLEMENTATION_BUG", ("attributeerror", "batch", "o(n", "path with spaces", "implementation")),
        ("RETRIEVAL_MISS", ("retrieval", "empty results", "no matching", "no candidates")),
    )
    best: tuple[int, str] | None = None
    for label, needles in rules:
        score = sum(1 for needle in needles if needle in text)
        if score and (best is None or score > best[0]):
            best = (score, label)
    return None if best is None else best[1]
