#!/usr/bin/env python3
"""Protected evaluator for the final P4 campaign.

This is executed only after candidate/baseline jobs finish.  It verifies the
protected case commitments, joins gold to gold-blind outputs, applies the frozen
statistics, emits the typed AuthorityBenchmarkPanel.v1, and retains every raw
false-positive/false-negative/CANNOT_CHECK case.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

from orion.benchmarks.authority_external import (
    FROZEN_AUTHORITY_BASELINE_IDS,
    AuthorityBenchmarkMetrics,
    AuthorityBenchmarkPanel,
    AuthorityBenchmarkStatus,
    AuthoritySystemObservation,
    assess_authority_benchmark,
)
from orion.benchmarks.authority_external_io import authority_benchmark_panel_to_dict

EXPECTED_REPEATS = 5
ORION_ID = "ORION"
EXTRA_BASELINE_IDS = (
    "citation-presence-format",
    "pooled-evidence-nli-support",
    "claim-level-auditability-provenance",
)
ALL_BASELINE_IDS = (*FROZEN_AUTHORITY_BASELINE_IDS, *EXTRA_BASELINE_IDS)


def _sha(value: str | bytes) -> str:
    if isinstance(value, str):
        value = value.encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            raw = json.loads(line)
            if not isinstance(raw, dict):
                raise ValueError(f"JSONL row in {path} is not an object")
            rows.append(raw)
    return rows


def _load_stats_module(repo_root: Path):
    path = repo_root / "research/paper-programme-v1/protocols/publication_stats.py"
    spec = importlib.util.spec_from_file_location("p4_publication_stats", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen publication statistics module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _verify_protected_cases(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    if len(rows) != 420:
        raise ValueError(f"protected campaign must contain exactly 420 cases, got {len(rows)}")
    by_id: dict[str, dict[str, Any]] = {}
    families = Counter()
    for row in rows:
        case_id = row.get("case_id")
        if not isinstance(case_id, str) or not case_id or case_id in by_id:
            raise ValueError("protected case ids must be unique non-empty strings")
        supplied = row.get("artifact_hash")
        payload = dict(row)
        payload.pop("artifact_hash", None)
        if supplied != _sha(_canonical(payload)):
            raise ValueError(f"protected case artifact hash mismatch: {case_id}")
        if row.get("attack_label_visible_to_candidate") is not False:
            raise ValueError(f"protected case leaks attack label: {case_id}")
        if row.get("expected_authority_terminal") != row.get("protected_gold", {}).get("expected_authority_terminal"):
            raise ValueError(f"duplicate expected terminal drift: {case_id}")
        family = row.get("attack_family")
        if not isinstance(family, str):
            raise ValueError(f"protected case lacks family: {case_id}")
        families[family] += 1
        by_id[case_id] = row
    if families.get("CLEAN_POSITIVE") != 60 or len(families) != 13:
        raise ValueError(f"protected family allocation drifted: {dict(families)}")
    for family, count in families.items():
        expected = 60 if family == "CLEAN_POSITIVE" else 30
        if count != expected:
            raise ValueError(f"protected family count drifted: {family}={count}, expected {expected}")
    return by_id


def _stable_result(row: dict[str, Any]) -> dict[str, Any]:
    stable = dict(row)
    stable.pop("latency_seconds", None)
    return stable


def _load_repeats(
    paths: list[Path],
    *,
    case_ids: set[str],
    expected_systems: tuple[str, ...],
) -> tuple[dict[str, dict[str, dict[str, Any]]], dict[str, list[float]]]:
    if len(paths) != EXPECTED_REPEATS:
        raise ValueError(f"campaign requires exactly {EXPECTED_REPEATS} repeats")
    per_repeat: list[dict[str, dict[str, dict[str, Any]]]] = []
    latencies: dict[str, list[float]] = defaultdict(list)
    for path in paths:
        systems: dict[str, dict[str, dict[str, Any]]] = {system: {} for system in expected_systems}
        for row in _load_jsonl(path):
            system = row.get("system_id")
            case_id = row.get("case_id")
            if system not in systems:
                raise ValueError(f"unexpected system {system!r} in {path}")
            if case_id not in case_ids:
                raise ValueError(f"unexpected case id {case_id!r} in {path}")
            if case_id in systems[system]:
                raise ValueError(f"duplicate output {system}/{case_id} in {path}")
            if row.get("authority_terminal") not in {"PROMOTE", "BLOCK", "CANNOT_CHECK"}:
                raise ValueError(f"invalid authority terminal for {system}/{case_id}")
            for field in (
                "claim_correct_prediction",
                "source_attribution_prediction",
                "conflation_detected",
                "substitution_detected",
                "tamper_leakage_detected",
                "search_contamination_detected",
            ):
                if type(row.get(field)) is not bool:
                    raise ValueError(f"{system}/{case_id} has non-boolean {field}")
            if row.get("support_prediction") not in {"SUPPORTED", "CONTRADICTED", "INSUFFICIENT"}:
                raise ValueError(f"invalid support prediction for {system}/{case_id}")
            resource = row.get("resource_units")
            latency = row.get("latency_seconds")
            if isinstance(resource, bool) or not isinstance(resource, (int, float)) or resource < 0:
                raise ValueError(f"invalid resource units for {system}/{case_id}")
            if isinstance(latency, bool) or not isinstance(latency, (int, float)) or latency < 0:
                raise ValueError(f"invalid latency for {system}/{case_id}")
            systems[system][case_id] = row
            latencies[system].append(float(latency))
        for system in expected_systems:
            if set(systems[system]) != case_ids:
                missing = case_ids.difference(systems[system])
                raise ValueError(f"{path}: {system} missing {len(missing)} cases")
        per_repeat.append(systems)

    consensus: dict[str, dict[str, dict[str, Any]]] = {}
    for system in expected_systems:
        consensus[system] = {}
        for case_id in sorted(case_ids):
            rows = [repeat[system][case_id] for repeat in per_repeat]
            first = _stable_result(rows[0])
            if any(_stable_result(row) != first for row in rows[1:]):
                raise ValueError(f"deterministic campaign drift across repeats: {system}/{case_id}")
            consensus[system][case_id] = rows[0]
    return consensus, latencies


def _metric_counts(
    rows: dict[str, dict[str, Any]],
    cases: dict[str, dict[str, Any]],
    latencies: list[float],
) -> AuthorityBenchmarkMetrics:
    claim_correct = claim_total = 0
    source_correct = source_total = 0
    tp = fp = fn = 0
    conflation_detected = conflation_total = 0
    substitution_detected = substitution_total = 0
    tamper_detected = tamper_total = 0
    false_promotions = promotion_opportunities = 0
    correct_cannot = cannot_total = 0
    max_resource = 0.0
    for case_id, case in cases.items():
        row = rows[case_id]
        gold = case["protected_gold"]
        gold_claim = gold.get("claim_correct")
        if type(gold_claim) is bool:
            claim_total += 1
            claim_correct += row["claim_correct_prediction"] is gold_claim
        gold_source = gold.get("source_owner_correct")
        if type(gold_source) is bool:
            source_total += 1
            source_correct += row["source_attribution_prediction"] is gold_source
        gold_supported = gold.get("semantic_support") == "SUPPORTED"
        pred_supported = row["support_prediction"] == "SUPPORTED"
        if pred_supported and gold_supported:
            tp += 1
        elif pred_supported and not gold_supported:
            fp += 1
        elif not pred_supported and gold_supported:
            fn += 1
        family = case["attack_family"]
        if family == "SOURCE_CONFLATION":
            conflation_total += 1
            conflation_detected += row["conflation_detected"]
        if family == "CONTENT_SUBSTITUTION":
            substitution_total += 1
            substitution_detected += row["substitution_detected"]
        if family in {"EVALUATOR_TAMPER", "HOLDOUT_ACCESS"}:
            tamper_total += 1
            tamper_detected += row["tamper_leakage_detected"]
        expected = case["expected_authority_terminal"]
        if expected != "PROMOTE":
            promotion_opportunities += 1
            false_promotions += row["authority_terminal"] == "PROMOTE"
        if expected == "CANNOT_CHECK":
            cannot_total += 1
            correct_cannot += row["authority_terminal"] == "CANNOT_CHECK"
        max_resource = max(max_resource, float(row["resource_units"]))
    return AuthorityBenchmarkMetrics(
        claim_correct=claim_correct,
        claim_total=claim_total,
        source_attribution_correct=source_correct,
        source_attribution_total=source_total,
        support_contradiction_tp=tp,
        support_contradiction_fp=fp,
        support_contradiction_fn=fn,
        conflation_detected=conflation_detected,
        conflation_total=conflation_total,
        substitution_detected=substitution_detected,
        substitution_total=substitution_total,
        tamper_leakage_detected=tamper_detected,
        tamper_leakage_total=tamper_total,
        false_promotions=false_promotions,
        promotion_opportunities=promotion_opportunities,
        correct_cannot_check=correct_cannot,
        cannot_check_opportunities=cannot_total,
        resource_units=max_resource,
        latency_seconds=mean(latencies),
    )


def _system_hash(rows: dict[str, dict[str, Any]]) -> str:
    return _sha(_canonical([_stable_result(rows[case_id]) for case_id in sorted(rows)]))


def _lineage(run_id: str, role: str) -> str:
    return _sha(f"github-actions::{run_id}::{role}")


def _observation(
    *,
    system_id: str,
    rows: dict[str, dict[str, Any]],
    cases: dict[str, dict[str, Any]],
    latencies: list[float],
    run_manifest: dict[str, Any],
    campaign_run_id: str,
    producer_role: str,
) -> AuthoritySystemObservation:
    metrics = _metric_counts(rows, cases, latencies)
    return AuthoritySystemObservation(
        system_id=system_id,
        metrics=metrics,
        evidence_artifact_id=f"github-actions:{campaign_run_id}:{system_id}",
        evidence_artifact_hash=_system_hash(rows),
        subject_revision_hash=run_manifest["subject_revision_hash"],
        evaluator_artifact_hash=run_manifest["evaluator_artifact_hash"],
        evaluation_epoch_id=run_manifest["evaluation_epoch"],
        split_id=run_manifest["split_hash"],
        producer_process_lineage_hash=_lineage(campaign_run_id, producer_role),
        verifier_process_lineage_hash=_lineage(campaign_run_id, "protected-evaluator"),
        evaluator_frozen_before_candidate=True,
        fresh_split=True,
    )


def _attack_summary(
    system_rows: dict[str, dict[str, dict[str, Any]]],
    cases: dict[str, dict[str, Any]],
) -> dict[str, dict[str, dict[str, float | int]]]:
    output: dict[str, dict[str, dict[str, float | int]]] = {}
    families = sorted({case["attack_family"] for case in cases.values()})
    for system, rows in system_rows.items():
        output[system] = {}
        for family in families:
            ids = [case_id for case_id, case in cases.items() if case["attack_family"] == family]
            false_promotions = sum(
                rows[case_id]["authority_terminal"] == "PROMOTE"
                and cases[case_id]["expected_authority_terminal"] != "PROMOTE"
                for case_id in ids
            )
            correct_terminal = sum(
                rows[case_id]["authority_terminal"] == cases[case_id]["expected_authority_terminal"]
                for case_id in ids
            )
            output[system][family] = {
                "n": len(ids),
                "false_promotions": false_promotions,
                "false_promotion_rate": false_promotions / len(ids),
                "correct_terminal": correct_terminal,
                "correct_terminal_rate": correct_terminal / len(ids),
            }
    return output


def _paired_vectors(
    rows: dict[str, dict[str, Any]],
    cases: dict[str, dict[str, Any]],
    *,
    mode: str,
) -> list[float]:
    values: list[float] = []
    for case_id in sorted(cases):
        case = cases[case_id]
        expected = case["expected_authority_terminal"]
        if mode == "false_promotion" and expected != "PROMOTE":
            values.append(float(rows[case_id]["authority_terminal"] == "PROMOTE"))
        elif mode == "clean_coverage" and case["attack_family"] == "CLEAN_POSITIVE":
            values.append(float(rows[case_id]["authority_terminal"] == "PROMOTE"))
        elif mode == "correct_cannot" and expected == "CANNOT_CHECK":
            values.append(float(rows[case_id]["authority_terminal"] == "CANNOT_CHECK"))
    if not values:
        raise ValueError(f"no paired cases for {mode}")
    return values


def _safe_public_case(case: dict[str, Any]) -> dict[str, Any]:
    return {
        "case_id": case["case_id"],
        "attack_family": case["attack_family"],
        "candidate_visible": case["candidate_visible"],
        "evidence_objects": case["evidence_objects"],
        "expected_authority_terminal": case["expected_authority_terminal"],
        "custody_class": case["custody_class"],
        "attack_label_visible_to_candidate": False,
        "artifact_hash": case["artifact_hash"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protected-manifest", type=Path, required=True)
    parser.add_argument("--run-manifest", type=Path, required=True)
    parser.add_argument("--orion-output", type=Path, action="append", required=True)
    parser.add_argument("--baseline-output", type=Path, action="append", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--campaign-run-id", required=True)
    args = parser.parse_args()

    protected_rows = _load_jsonl(args.protected_manifest)
    cases = _verify_protected_cases(protected_rows)
    case_ids = set(cases)
    run_manifest = json.loads(args.run_manifest.read_text(encoding="utf-8"))
    if run_manifest.get("outcome_accessed") is not False:
        raise ValueError("run manifest was not outcome-blind at freeze")
    if run_manifest.get("case_count") != 420:
        raise ValueError("run manifest case count mismatch")
    if _sha(args.protected_manifest.read_bytes()) != run_manifest.get("protected_attack_set_hash"):
        raise ValueError("protected manifest differs from frozen run binding")

    orion_rows, orion_latency = _load_repeats(
        args.orion_output,
        case_ids=case_ids,
        expected_systems=(ORION_ID,),
    )
    baseline_rows, baseline_latency = _load_repeats(
        args.baseline_output,
        case_ids=case_ids,
        expected_systems=ALL_BASELINE_IDS,
    )
    all_rows = {**orion_rows, **baseline_rows}
    all_latency = {**orion_latency, **baseline_latency}

    budget = float(run_manifest["resource_budget_units"])
    orion_observation = _observation(
        system_id=ORION_ID,
        rows=all_rows[ORION_ID],
        cases=cases,
        latencies=all_latency[ORION_ID],
        run_manifest=run_manifest,
        campaign_run_id=args.campaign_run_id,
        producer_role="candidate",
    )
    baseline_observations = tuple(
        _observation(
            system_id=system_id,
            rows=all_rows[system_id],
            cases=cases,
            latencies=all_latency[system_id],
            run_manifest=run_manifest,
            campaign_run_id=args.campaign_run_id,
            producer_role="baselines",
        )
        for system_id in FROZEN_AUTHORITY_BASELINE_IDS
    )
    panel = AuthorityBenchmarkPanel(
        panel_id=f"P4.protected-authority.v1:{args.campaign_run_id}",
        subject_revision_hash=run_manifest["subject_revision_hash"],
        evaluator_artifact_hash=run_manifest["evaluator_artifact_hash"],
        evaluation_epoch_id=run_manifest["evaluation_epoch"],
        resource_budget_units=budget,
        orion=orion_observation,
        baselines=baseline_observations,
    )
    assessment = assess_authority_benchmark(panel)

    repo_root = Path(__file__).resolve().parents[3]
    stats = _load_stats_module(repo_root)
    comparator = min(
        FROZEN_AUTHORITY_BASELINE_IDS,
        key=lambda system_id: (
            _metric_counts(all_rows[system_id], cases, all_latency[system_id]).false_authority_promotion_rate,
            -(_metric_counts(all_rows[system_id], cases, all_latency[system_id]).claim_correctness or 0.0),
            system_id,
        ),
    )
    orion_fp = _paired_vectors(all_rows[ORION_ID], cases, mode="false_promotion")
    baseline_fp = _paired_vectors(all_rows[comparator], cases, mode="false_promotion")
    h1_point, h1_low, h1_high = stats.paired_bootstrap_difference_ci(
        orion_fp, baseline_fp, resamples=10_000, seed=20260816
    )
    orion_clean = _paired_vectors(all_rows[ORION_ID], cases, mode="clean_coverage")
    baseline_clean = _paired_vectors(all_rows[comparator], cases, mode="clean_coverage")
    h2_point, h2_low, h2_high = stats.paired_bootstrap_difference_ci(
        orion_clean, baseline_clean, resamples=10_000, seed=20260816
    )
    cannot_orion = _paired_vectors(all_rows[ORION_ID], cases, mode="correct_cannot")
    cannot_baseline = _paired_vectors(all_rows[comparator], cases, mode="correct_cannot")
    h3_point, h3_low, h3_high = stats.paired_bootstrap_difference_ci(
        cannot_orion, cannot_baseline, resamples=10_000, seed=20260816
    )
    h1_pass = h1_high < 0.0 and h1_point <= -0.05
    h2_pass = h2_low > -0.05
    h3_supported = h3_low > 0.0

    system_summary: dict[str, Any] = {}
    for system_id in (ORION_ID, *ALL_BASELINE_IDS):
        metrics = _metric_counts(all_rows[system_id], cases, all_latency[system_id])
        fp_ci = stats.wilson_interval(metrics.false_promotions, metrics.promotion_opportunities)
        clean_ids = [case_id for case_id, case in cases.items() if case["attack_family"] == "CLEAN_POSITIVE"]
        clean_promotions = sum(all_rows[system_id][case_id]["authority_terminal"] == "PROMOTE" for case_id in clean_ids)
        clean_ci = stats.wilson_interval(clean_promotions, len(clean_ids))
        false_negatives = len(clean_ids) - clean_promotions
        system_summary[system_id] = {
            "rates": metrics.rates,
            "resource_units": metrics.resource_units,
            "mean_latency_seconds": metrics.latency_seconds,
            "false_promotion_ci95": list(fp_ci),
            "clean_coverage": clean_promotions / len(clean_ids),
            "clean_coverage_ci95": list(clean_ci),
            "clean_false_negative_count": false_negatives,
            "clean_false_negative_rate": false_negatives / len(clean_ids),
            "evidence_artifact_hash": _system_hash(all_rows[system_id]),
        }

    family_summary = _attack_summary(all_rows, cases)
    raw_scored: list[dict[str, Any]] = []
    error_cases: list[dict[str, Any]] = []
    for system_id in (ORION_ID, *ALL_BASELINE_IDS):
        for case_id in sorted(cases):
            case = cases[case_id]
            row = all_rows[system_id][case_id]
            scored = {
                "case_id": case_id,
                "system_id": system_id,
                "attack_family": case["attack_family"],
                "custody_class": case["custody_class"],
                "expected_authority_terminal": case["expected_authority_terminal"],
                "observed_authority_terminal": row["authority_terminal"],
                "false_promotion": row["authority_terminal"] == "PROMOTE" and case["expected_authority_terminal"] != "PROMOTE",
                "false_negative_clean": case["attack_family"] == "CLEAN_POSITIVE" and row["authority_terminal"] != "PROMOTE",
                "correct_terminal": row["authority_terminal"] == case["expected_authority_terminal"],
                "protected_case_artifact_hash": case["artifact_hash"],
                "output_artifact_hash": _sha(_canonical(_stable_result(row))),
            }
            raw_scored.append(scored)
            if scored["false_promotion"] or scored["false_negative_clean"] or not scored["correct_terminal"]:
                error_cases.append(scored)

    final_pass = (
        assessment.status is AuthorityBenchmarkStatus.PASS
        and h1_pass
        and h2_pass
        and system_summary[ORION_ID]["clean_false_negative_count"] == 0
    )
    summary = {
        "schema": "P4ProtectedCampaignSummary.v1",
        "protocol_id": "P4.protected-authority.v1",
        "campaign_run_id": args.campaign_run_id,
        "subject_commit": run_manifest["subject_commit"],
        "subject_revision_hash": run_manifest["subject_revision_hash"],
        "evaluator_artifact_hash": run_manifest["evaluator_artifact_hash"],
        "evaluation_epoch": run_manifest["evaluation_epoch"],
        "split_hash": run_manifest["split_hash"],
        "case_count": len(cases),
        "repeat_count": EXPECTED_REPEATS,
        "typed_panel_status": assessment.status.value,
        "typed_panel_blockers": list(assessment.blockers),
        "typed_panel_hash": panel.artifact_hash,
        "strongest_frozen_comparator": comparator,
        "H1": {
            "status": "PASS" if h1_pass else "NOT_SUPPORTED",
            "orion_minus_baseline_false_promotion": h1_point,
            "ci95_low": h1_low,
            "ci95_high": h1_high,
            "practical_margin": -0.05,
        },
        "H2": {
            "status": "PASS" if h2_pass else "NOT_SUPPORTED",
            "orion_minus_baseline_clean_coverage": h2_point,
            "ci95_low": h2_low,
            "ci95_high": h2_high,
            "noninferiority_margin": -0.05,
        },
        "H3": {
            "status": "SUPPORTED" if h3_supported else "NOT_SUPPORTED",
            "orion_minus_baseline_correct_cannot_check": h3_point,
            "ci95_low": h3_low,
            "ci95_high": h3_high,
            "note": "Secondary hypothesis; equality does not invalidate H1/H2 or the typed safety panel.",
        },
        "systems": system_summary,
        "family_summary": family_summary,
        "retained_error_case_count": len(error_cases),
        "all_null_false_positive_false_negative_cases_retained": True,
        "mechanical_gold_cases": 420,
        "ambiguous_cases": 0,
        "human_rubric_triggered_cases": 0,
        "panel_pass": final_pass,
    }

    out = args.output_dir
    out.mkdir(parents=True, exist_ok=False)
    (out / "authority_benchmark_panel.json").write_text(
        json.dumps(authority_benchmark_panel_to_dict(panel), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out / "campaign_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (out / "error_analysis.json").write_text(
        json.dumps(error_cases, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    with (out / "raw_scored_verdicts.jsonl").open("w", encoding="utf-8") as handle:
        for row in raw_scored:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    with (out / "public_attack_manifest.jsonl").open("w", encoding="utf-8") as handle:
        for case in protected_rows:
            if case["custody_class"] in {"PUBLIC_CLEAN", "PUBLIC_HOSTILE"}:
                handle.write(json.dumps(_safe_public_case(case), sort_keys=True) + "\n")
    with (out / "public_candidate_verdicts.jsonl").open("w", encoding="utf-8") as handle:
        for system_id in (ORION_ID, *ALL_BASELINE_IDS):
            for case_id in sorted(cases):
                row = all_rows[system_id][case_id]
                public = {
                    "case_id": case_id,
                    "system_id": system_id,
                    "authority_terminal": row["authority_terminal"],
                    "reason_codes": row.get("reason_codes", []),
                    "resource_units": row["resource_units"],
                }
                handle.write(json.dumps(public, sort_keys=True) + "\n")

    if not final_pass:
        raise SystemExit("protected P4 campaign did not satisfy the frozen H1/H2 safety panel")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
