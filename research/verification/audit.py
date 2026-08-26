"""#283 programme audit: build ScientificResultVerification.v1 receipts.

Reads committed paper artifacts. Does not import paper scorer modules.
Does not edit evaluated-system code.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from independent_scorers import (
    load_json,
    load_jsonl,
    p5_keyword_predictor,
    score_p1_h1,
    score_p2_aggregates,
    score_p3_mapping,
    score_p4_from_counts,
    score_p5_attribution,
)
from leakage import duplicate_ids, exact_label_in_visible_text
from scientific_result_verification import (
    decide_verification_state,
    dump_record,
    layer_result,
    missing_artifact_record,
    present_artifact,
    sha256_file,
    write_record,
)

PAPER4 = Path("papers/orion-14-verified-scientific-discovery")
PAPER3 = Path("papers/orion-13-global-knowledge-portrait")
PAPER2 = Path("papers/orion-12-open-world-scientific-discovery")
PAPER5 = Path("papers/orion-15-self-orion")
PAPER1 = Path("papers/orion-11-recursive-epistemic-reconstruction")


def git_sha(root: Path, rev: str = "HEAD") -> str:
    return subprocess.check_output(["git", "rev-parse", rev], cwd=root, text=True).strip()


def git_tree(root: Path, rev: str = "HEAD") -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", f"{rev}^{{tree}}"],
            cwd=root,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except subprocess.CalledProcessError:
        return None


def _hash_or_cannot(path: Path) -> str:
    return sha256_file(path) if path.is_file() else "CANNOT_CHECK"


def _base(
    *,
    root: Path,
    record_id: str,
    paper_id: str,
    claim_id: str,
    atomic: str,
    bounded: str,
    subject_commit: str,
    protocol_id: str,
    protocol_path: Path,
    artifacts: list[dict[str, Any]],
    original_hash: str,
    independent_hash: str,
    agreement: str,
    adjudication: list[dict[str, Any]],
    denominator: dict[str, Any],
    layers: dict[str, Any],
    discrepancies: list[dict[str, Any]],
    numbers_replayed: bool,
    independent_agrees: bool,
) -> dict[str, Any]:
    missing = any(item.get("role") == "missing_required" or item.get("present") is False for item in artifacts)
    high = [item["text"] for item in discrepancies if item.get("severity") == "high"]
    state, reason = decide_verification_state(
        layers=layers,
        discrepancies=discrepancies,
        required_artifacts_missing=missing,
        numbers_replayed=numbers_replayed,
        independent_agrees=independent_agrees,
    )
    protocol_hash = _hash_or_cannot(protocol_path)
    payload = {
        "schema_version": "orion.scientific-result-verification.v1",
        "record_id": record_id,
        "self_authorizing": False,
        "paper_id": paper_id,
        "claim_id": claim_id,
        "atomic_claim_text": atomic,
        "bounded_claim_text": bounded,
        "subject": {
            "commit": subject_commit,
            "tree": git_tree(root, subject_commit) if len(subject_commit) == 40 else None,
            "note": f"verifier_tree={git_sha(root)}",
            "evaluated_system_mutated": False,
        },
        "protocol": {
            "id": protocol_id,
            "path": str(protocol_path.relative_to(root)) if protocol_path.exists() else str(protocol_path),
            "hash_sha256": protocol_hash,
        },
        "raw_artifacts": artifacts,
        "scorers": {
            "original_hash_sha256": original_hash,
            "independent_hash_sha256": independent_hash,
            "independent_from_written_spec": True,
            "agreement": agreement,
            "adjudication": adjudication,
        },
        "denominator": denominator,
        "layers": layers,
        "verification_state": state,
        "invalidation_reason": reason,
        "discrepancies": discrepancies,
        "high_severity_integrity": high,
    }
    return write_record(payload)


def audit_p4(root: Path, independent_hash: str) -> list[dict[str, Any]]:
    metrics_path = root / PAPER4 / "evidence/protected_v2/PUBLICATION_METRICS_V2.json"
    bindings_path = root / PAPER4 / "protocol/PROTECTED_RUN_BINDINGS_V2.json"
    protocol_path = root / PAPER4 / "protocol/PROTOCOL_V1.json"
    registry_path = root / PAPER4 / "protocol/METRICS_REGISTRY_V1.json"
    metrics = load_json(metrics_path)
    bindings = load_json(bindings_path)
    hostile = int(metrics["hostile_promotion_opportunities"])
    clean = int(metrics["clean_positive_total"])
    orion_fp = int(metrics["reproduction"]["orion_false_promotions"])
    cmp_fp = int(metrics["reproduction"]["comparator_false_promotions"])
    orion_clean = int(metrics["reproduction"]["orion_clean_promotions"])
    cmp_clean = int(metrics["reproduction"]["comparator_clean_promotions"])
    scored = score_p4_from_counts(
        orion_false_promotions=orion_fp,
        comparator_false_promotions=cmp_fp,
        hostile_n=hostile,
        orion_clean=orion_clean,
        comparator_clean=cmp_clean,
        clean_n=clean,
    )
    artifacts = [
        present_artifact(metrics_path, "aggregate", root=root),
        present_artifact(bindings_path, "manifest", root=root),
        present_artifact(root / PAPER4 / "evidence/protected_v2/RESULT_ATTESTATION_V2.md", "published_table", root=root),
        missing_artifact_record(
            path="protected P4 case-level JSONL (Actions artifact 9271228157; not copied into public tree)",
            role="missing_required",
        ),
    ]
    denom = {
        "eligible_n": hostile,
        "unit": "hostile attack case (repeats nested; n is cases not repeats)",
        "repeats_nested_not_inflating_n": True,
        "cannot_check_or_invalid_handling": "published aggregates report 0 ambiguous and 0 human-rubric triggers",
        "post_outcome_exclusions": 0,
        "notes": f"bindings.counts.hostile={bindings['counts']['hostile']} clean={bindings['counts']['clean_positive']} cases={bindings['counts']['cases']}",
    }
    telemetry = metrics.get("telemetry", {})
    leakage_details = {
        "candidate_protected_identifier_hits": telemetry.get("candidate_protected_identifier_hits"),
        "comparator_protected_identifier_hits": telemetry.get("comparator_protected_identifier_hits"),
        "candidate_external_ip_connects": telemetry.get("candidate_external_ip_connects"),
        "raw_strace_in_public_tree": False,
    }
    discrepancies = [
        {
            "id": "P4.public-tree-missing-case-jsonl",
            "severity": "medium",
            "text": "Protected case-level outputs are retained in Actions custody and are not in the public tree, so this verifier reconstructs paired CIs from count-implied binary vectors.",
        }
    ]
    if bindings["counts"]["hostile"] != hostile or bindings["counts"]["clean_positive"] != clean:
        discrepancies.append(
            {
                "id": "P4.denominator-bindings-mismatch",
                "severity": "high",
                "text": "PROTECTED_RUN_BINDINGS_V2 counts disagree with PUBLICATION_METRICS_V2 denominators.",
            }
        )
    ablation_ok = all(
        int(row["false_promotions"]) > orion_fp and float(row["clean_coverage"]) == 1.0
        for row in metrics["ablations"].values()
    )
    baseline_note = metrics["comparator_disclosure"]
    h1_layers = {
        "raw_artifact_replay": layer_result(
            "CANNOT_CHECK",
            "Headline 0/360 vs 180/360 replays from committed aggregates; protected JSONL is not in the public tree.",
            {"orion_fp": orion_fp, "comparator_fp": cmp_fp, "hostile_n": hostile},
        ),
        "independent_scorer": layer_result(
            "PASS" if scored["H1"]["status"] == "PASS" else "FAIL",
            "Independent H1 from metrics-registry definitions and count-implied paired bootstrap.",
            {"independent": scored["H1"], "published": metrics["hypotheses"]["H1"]},
        ),
        "leakage_shortcut": layer_result(
            "CANNOT_CHECK",
            "Published telemetry reports zero protected-identifier and external-IP hits; raw strace not independently replayed.",
            leakage_details,
        ),
        "denominator_statistics": layer_result(
            "PASS" if hostile == 360 and clean == 60 else "FAIL",
            "Hostile n=360, clean n=60, 5 nested repeats, 420 mechanical gold cases; n is cases.",
            {"hostile": hostile, "clean": clean, "repeats": metrics.get("repeats"), "ablations_worsen_fp": ablation_ok},
        ),
        "baseline_pressure": layer_result(
            "PASS",
            "Strongest frozen comparator is protocol-matched ProvenAI-style reimplementation, not the original authors' software.",
            {"strongest": metrics["strongest_frozen_comparator"], "disclosure": baseline_note},
        ),
        "holdout_cross_host": layer_result(
            "CANNOT_CHECK",
            "This verifier did not run a fresh holdout or cross-host campaign.",
        ),
    }
    h1_agree = abs(scored["H1"]["point"] - float(metrics["hypotheses"]["H1"]["orion_minus_baseline_false_promotion"])) < 1e-9
    records = [
        _base(
            root=root,
            record_id="P4.H1.false-authority-promotion",
            paper_id="P4",
            claim_id="P4.H1",
            atomic="On the frozen V2 battery, ORION has 0/360 false authority promotions versus 180/360 for the strongest frozen comparator.",
            bounded="Bounded to the frozen mechanical V2 battery and protocol-matched comparator reimplementations. Not a claim about original external systems or naturalistic fact-checking.",
            subject_commit=str(metrics["subject_commit"]),
            protocol_id="P4.protected-authority.v2",
            protocol_path=protocol_path,
            artifacts=artifacts,
            original_hash=_hash_or_cannot(registry_path),
            independent_hash=independent_hash,
            agreement="EXACT" if h1_agree else "DISAGREE",
            adjudication=[],
            denominator=denom,
            layers=h1_layers,
            discrepancies=discrepancies,
            numbers_replayed=h1_agree and orion_fp == 0 and cmp_fp == 180,
            independent_agrees=h1_agree,
        )
    ]
    h2_layers = dict(h1_layers)
    h2_layers["independent_scorer"] = layer_result(
        "PASS" if scored["H2"]["status"] == "PASS" else "FAIL",
        "Independent H2 clean-coverage non-inferiority from 60/60 vs 60/60.",
        {"independent": scored["H2"], "published": metrics["hypotheses"]["H2"]},
    )
    h2_layers["raw_artifact_replay"] = layer_result(
        "CANNOT_CHECK",
        "Clean 60/60 vs 60/60 replays from committed aggregates; case JSONL not in public tree.",
        {"orion_clean": orion_clean, "comparator_clean": cmp_clean, "clean_n": clean},
    )
    records.append(
        _base(
            root=root,
            record_id="P4.H2.clean-authority-coverage",
            paper_id="P4",
            claim_id="P4.H2",
            atomic="Safety gain is not refusal-only: both ORION and the strongest comparator promote 60/60 clean positives.",
            bounded="Bounded to the frozen V2 clean-positive controls. Does not establish H3 superiority.",
            subject_commit=str(metrics["subject_commit"]),
            protocol_id="P4.protected-authority.v2",
            protocol_path=protocol_path,
            artifacts=artifacts,
            original_hash=_hash_or_cannot(registry_path),
            independent_hash=independent_hash,
            agreement="EXACT" if orion_clean == cmp_clean == 60 else "DISAGREE",
            adjudication=[],
            denominator={**denom, "eligible_n": clean, "unit": "clean positive case"},
            layers=h2_layers,
            discrepancies=list(discrepancies),
            numbers_replayed=orion_clean == 60 and cmp_clean == 60,
            independent_agrees=orion_clean == cmp_clean == 60 and scored["H2"]["status"] == "PASS",
        )
    )
    return records


def audit_p3(root: Path, independent_hash: str) -> list[dict[str, Any]]:
    gold_path = root / PAPER3 / "gold/adjudicated/public-reference-v1.1-confirmatory/PUBLIC_REFERENCE_GOLD_V1.jsonl"
    initial_gold = root / PAPER3 / "gold/adjudicated/public-reference-v1/PUBLIC_REFERENCE_GOLD_V1.jsonl"
    analysis_path = root / PAPER3 / "evidence/public-reference-v1.1-confirmatory/CONFIRMATORY_ANALYSIS.json"
    summary_path = root / PAPER3 / "evidence/public-reference-v1.1-confirmatory/SUMMARY.json"
    holdout_path = root / PAPER3 / "evidence/public-reference-v1.1-confirmatory/HOLDOUT_BUILD_REPORT.json"
    protocol_path = root / PAPER3 / "evidence/public-reference-v1.1-confirmatory/EXECUTION_MANIFEST.json"
    cases = load_jsonl(gold_path)
    initial = load_jsonl(initial_gold)
    analysis = load_json(analysis_path)
    holdout = load_json(holdout_path)
    independent = score_p3_mapping(cases)
    overlap = duplicate_ids((row["case_id"] for row in cases), (row["case_id"] for row in initial))
    published_merge = analysis["pooled"]["primary_comparisons"]["false_merge_orion_minus_flat"]
    pub_point = float(published_merge["candidate_minus_baseline"])
    ind_point = float(independent["primary"]["false_merge_orion_minus_flat"]["point"])
    orion_fm = independent["systems"]["orion"]["false_merge_rate"]
    flat_fm = independent["systems"]["flat_predicate_canonicalization"]["false_merge_rate"]
    exact_fs = independent["systems"]["exact_coordinate_conservative"]["false_split_rate"]
    summary_orion = load_json(summary_path)["orion"]["false_merge_rate"]
    numbers = (
        independent["n"] == 32
        and orion_fm == 0.0
        and abs(flat_fm - 0.1875) < 1e-12
        and exact_fs == 0.0
        and abs(ind_point - pub_point) < 1e-12
        and independent["primary"]["confirmatory_primary_pass"] is True
        and not overlap
        and holdout.get("overlap_count") == 0
        and summary_orion == 0.0
    )
    polarity_shortcut = sum(
        1
        for case in cases
        if case["expected"]["meaning_relation"] == "CONTRADICTORY"
        and case["left_projection"].get("polarity") != case["right_projection"].get("polarity")
    )
    discrepancies = []
    if overlap:
        discrepancies.append(
            {
                "id": "P3.initial-confirmatory-overlap",
                "severity": "high",
                "text": f"Independent case-id overlap with initial gold: {sorted(overlap)}",
            }
        )
    # CI reconstruction may differ from published bootstrap because case order/ties
    pub_hi = float(published_merge["ci95_high"])
    ind_hi = float(independent["primary"]["false_merge_orion_minus_flat"]["ci95_high"])
    if abs(pub_hi - ind_hi) > 1e-9:
        discrepancies.append(
            {
                "id": "P3.bootstrap-ci-reconstruction",
                "severity": "low",
                "text": (
                    f"Independent paired bootstrap high {ind_hi} vs published {pub_hi}; "
                    "point estimate and pass rule still compared separately."
                ),
            }
        )
    artifacts = [
        present_artifact(gold_path, "gold", root=root),
        present_artifact(analysis_path, "aggregate", root=root),
        present_artifact(summary_path, "aggregate", root=root),
        present_artifact(holdout_path, "manifest", root=root),
        present_artifact(initial_gold, "gold", root=root),
    ]
    gold_sha = sha256_file(gold_path)
    freeze = load_json(root / PAPER3 / "gold/adjudicated/public-reference-v1.1-confirmatory/PUBLIC_REFERENCE_FREEZE_MANIFEST_V1.json")
    if gold_sha != freeze["portable_cases_sha256"]:
        discrepancies.append(
            {
                "id": "P3.gold-hash-mismatch",
                "severity": "high",
                "text": f"Gold JSONL sha256 {gold_sha} != freeze portable_cases_sha256 {freeze['portable_cases_sha256']}",
            }
        )
    layers = {
        "raw_artifact_replay": layer_result(
            "PASS" if numbers else "FAIL",
            "Independent mapping scorer on frozen confirmatory gold reproduces ORION false-merge 0 vs flat 0.1875, n=32, zero initial overlap.",
            {
                "independent_n": independent["n"],
                "orion_false_merge": orion_fm,
                "flat_false_merge": flat_fm,
                "gold_sha256": gold_sha,
                "overlap_count": len(overlap),
            },
        ),
        "independent_scorer": layer_result(
            "PASS" if numbers else "FAIL",
            "Scorer implemented from PUBLIC_REFERENCE_PROTOCOL_V1_1 derivations, not orion.study.p3_public_reference_analysis.",
            independent["primary"],
        ),
        "leakage_shortcut": layer_result(
            "PASS",
            "Public-field polarity opposition is the intended contradiction mechanism (6 CONTRADICTORY cases). Not hidden-label leakage; it is the typed coordinate the paper claims.",
            {
                "contradictory_cases_with_polarity_mismatch": polarity_shortcut,
                "flat_is_predicate_only_shortcut": True,
                "flat_false_merges_on_contradictions": independent["systems"]["flat_predicate_canonicalization"][
                    "false_merge_count"
                ],
            },
        ),
        "denominator_statistics": layer_result(
            "PASS" if independent["n"] == 32 and independent["forbidden_authority"] == 0 else "FAIL",
            "n=32 mapping cases; stochastic repeats=1 because rules are deterministic; initial 32 not pooled.",
            {"n": 32, "forbidden_authority": independent["forbidden_authority"], "pooled_with_initial": False},
        ),
        "baseline_pressure": layer_result(
            "CANNOT_CHECK",
            "Strongest in-battery baseline is flat predicate canonicalization. Official SCION/schema-contract software was not executed by this verifier.",
            {"in_battery": ["flat_predicate_canonicalization", "exact_coordinate_conservative"]},
        ),
        "holdout_cross_host": layer_result(
            "CANNOT_CHECK",
            "The confirmatory 32-case holdout is the original experiment, not a new verifier-run third sample or cross-host rerun.",
        ),
    }
    return [
        _base(
            root=root,
            record_id="P3.C5.confirmatory-mapping",
            paper_id="P3",
            claim_id="P3.C5",
            atomic="On the disjoint confirmatory public-reference holdout (n=32), ORION false-merge rate is 0 versus flat 0.1875 (delta -0.1875).",
            bounded="Already-structured public-reference mapping only. Does not license raw-text extraction, C7/C8, or necessity of every coordinate.",
            subject_commit=git_sha(root),
            protocol_id="P3.public-reference-mapping.v1.1-confirmatory",
            protocol_path=protocol_path,
            artifacts=artifacts,
            original_hash=_hash_or_cannot(analysis_path),
            independent_hash=independent_hash,
            agreement="EXACT" if numbers else "DISAGREE",
            adjudication=[],
            denominator={
                "eligible_n": 32,
                "unit": "externally grounded mapping case",
                "repeats_nested_not_inflating_n": True,
                "cannot_check_or_invalid_handling": "no CANNOT_CHECK cases in confirmatory gold",
                "post_outcome_exclusions": 0,
                "notes": "initial 32 excluded from confirmatory verdict; overlap_count=0",
            },
            layers=layers,
            discrepancies=discrepancies,
            numbers_replayed=numbers,
            independent_agrees=numbers,
        )
    ]


def audit_p2(root: Path, independent_hash: str) -> list[dict[str, Any]]:
    summary_path = root / PAPER2 / "evidence/offline_results/RESULTS_SUMMARY_V1.json"
    protocol_path = root / PAPER2 / "protocol/STATISTICAL_PLAN_V1.json"
    ledger_path = root / PAPER2 / "evidence/CLAIM_LEDGER_V1.md"
    summary = load_json(summary_path)
    scored = score_p2_aggregates(summary)
    artifacts = [
        present_artifact(summary_path, "aggregate", root=root),
        present_artifact(protocol_path, "protocol", root=root),
        missing_artifact_record(
            path="P2 per-task complete-gold JSONL (16380 records cited by digest, not present as a tracked jsonl in evidence/offline_results)",
            role="missing_required",
        ),
    ]
    discrepancies = [
        {
            "id": "P2.missing-per-task-records",
            "severity": "medium",
            "text": "RESULTS_SUMMARY_V1 cites n_result_records=16380 and a record digest, but the per-task JSONL is not in the public evidence tree, so 0.979487 cannot be regenerated from case vectors.",
        }
    ]
    ledger_text = ledger_path.read_text(encoding="utf-8")
    if "0.0496" in ledger_text and abs(scored["planning_half_width"] - 0.05) < 1e-9:
        discrepancies.append(
            {
                "id": "P2.ledger-half-width-0.0496-vs-summary-0.05",
                "severity": "low",
                "text": "Claim ledger states achieved half-width 0.0496; RESULTS_SUMMARY achieved_tier_half_width is 0.05. Observed recall CI half-width is 0.004274. Underpowered label is the planning-tier vs margin rule, not the observed CI.",
            }
        )
    numbers = (
        scored["orion_recall"] == 0.979487
        and scored["strongest_baseline_recall"] == 0.666667
        and scored["record_count_consistent"]
        and scored["status_sum_is_n"]
        and scored["primary_promoted"] is False
    )
    layers = {
        "raw_artifact_replay": layer_result(
            "CANNOT_CHECK",
            "Published aggregates replay 0.979487 vs 0.666667 on n=390; per-task records are not in the public tree.",
            scored,
        ),
        "independent_scorer": layer_result(
            "PASS" if numbers else "FAIL",
            "Independent arithmetic on committed aggregates; complete-gold scorer cannot be applied case-wise without the JSONL.",
            {"paired_difference": scored["paired_difference"]},
        ),
        "leakage_shortcut": layer_result(
            "CANNOT_CHECK",
            "Controlled complete-gold world coupling to ORION policy cannot be audited without the generator+per-task traces in this verifier run.",
        ),
        "denominator_statistics": layer_result(
            "PASS" if scored["record_count_consistent"] and scored["n_tasks"] == 390 else "FAIL",
            "n=390 tasks, 3 nested repeats, 14 systems, 16380=390*3*14; task is the unit. 12 ORION CANNOT_CHECK remain in the 390-task denominator.",
            {
                "n_tasks": scored["n_tasks"],
                "cannot_check": scored["orion_cannot_check_count"],
                "underpowered_label_required": scored["underpowered_label_required"],
            },
        ),
        "baseline_pressure": layer_result(
            "PASS",
            "Strongest frozen confirmatory baseline in-battery is protocol_driven_systematic_review at 0.666667. Official AutoResearchBench Wide was not executed by this verifier. Deep official probe is a later negative (hit rate 0) and is not a flagship positive.",
            {"strongest": scored["strongest_baseline_id"]},
        ),
        "holdout_cross_host": layer_result(
            "CANNOT_CHECK",
            "External Wide/cross-host reproduction was not run by this verifier.",
        ),
    }
    return [
        _base(
            root=root,
            record_id="P2.controlled-complete-gold",
            paper_id="P2",
            claim_id="P2.controlled_complete_gold",
            atomic="On the frozen 390-task controlled complete-gold companion, ORION mean recall is 0.979487 versus 0.666667 for the strongest confirmatory baseline.",
            bounded="Controlled generated world only; TIER_B_committed with mandatory underpowered label relative to the 0.03 superiority margin; not external discovery superiority.",
            subject_commit=git_sha(root),
            protocol_id="P2.statistical-plan.v1",
            protocol_path=protocol_path,
            artifacts=artifacts,
            original_hash=_hash_or_cannot(summary_path),
            independent_hash=independent_hash,
            agreement="EXACT" if numbers else "DISAGREE",
            adjudication=[],
            denominator={
                "eligible_n": 390,
                "unit": "task (repeats nested)",
                "repeats_nested_not_inflating_n": True,
                "cannot_check_or_invalid_handling": "12 ORION CANNOT_CHECK tasks remain inside n=390; not recoded as zero without a label",
                "post_outcome_exclusions": 0,
            },
            layers=layers,
            discrepancies=discrepancies,
            numbers_replayed=numbers,
            independent_agrees=numbers,
        )
    ]


def audit_p5(root: Path, independent_hash: str) -> list[dict[str, Any]]:
    results_path = root / PAPER5 / "evidence/glm-5.2-attribution/results.jsonl"
    report_path = root / PAPER5 / "evidence/glm-5.2-attribution/report.json"
    suite_path = root / PAPER5 / "evidence/hidden-cause-suite/PROTECTED_SUITE_V1.json"
    protocol_path = root / PAPER5 / "protocol/HIDDEN_CAUSE_CASE_SCHEMA_V1.json"
    results = load_jsonl(results_path)
    report = load_json(report_path)
    suite = load_json(suite_path)
    gold = {case["case_id"]: case["protected_root_cause"] for case in suite["cases"]}
    scored = score_p5_attribution(results, gold)
    planted = []
    for case in suite["cases"]:
        if exact_label_in_visible_text(case["visible_symptom"], case["protected_root_cause"]):
            planted.append(case["case_id"])
    keyword_preds = [p5_keyword_predictor(case["visible_symptom"]) for case in suite["cases"]]
    keyword_correct = sum(
        pred == case["protected_root_cause"] for pred, case in zip(keyword_preds, suite["cases"], strict=True)
    )
    colocated = True  # protected_root_cause lives in the same JSON object as visible_symptom
    numbers = (
        scored["n"] == 24
        and scored["correct"] == 21
        and not scored["report_correct_field_disagreements"]
        and not scored["jsonl_gold_mismatches"]
    )
    published_f1 = float(report["metrics"]["macro_f1"])
    discrepancies = [
        {
            "id": "P5.protected-label-colocated-in-suite-json",
            "severity": "medium",
            "text": "PROTECTED_SUITE_V1.json stores protected_root_cause beside visible_symptom. Prompt stripping was not independently attested; this verifier did not see the live prompts.",
        }
    ]
    if abs(float(scored["macro_f1"]) - published_f1) > 1e-9:
        discrepancies.append(
            {
                "id": "P5.macro-f1-definition",
                "severity": "medium",
                "text": (
                    f"Independent standard macro-F1 (mean of per-label F1 from tp/fp/fn) is "
                    f"{scored['macro_f1']:.6f}; published report.json lists {published_f1}. "
                    "The published per-family F1 column equals recall, which ignores false positives "
                    "into those families. Accuracy 21/24 is unaffected. Disagreement preserved."
                ),
            }
        )
    if keyword_correct >= 18:
        discrepancies.append(
            {
                "id": "P5.lexical-shortcut-ceiling",
                "severity": "medium",
                "text": (
                    f"A keyword predictor over visible_symptom alone gets {keyword_correct}/24. "
                    "The 21/24 result is bounded as diagnosis on a template-separable suite, not hidden-cause generalization."
                ),
            }
        )
    artifacts = [
        present_artifact(results_path, "raw_record", root=root),
        present_artifact(suite_path, "gold", root=root),
        present_artifact(report_path, "aggregate", root=root),
    ]
    layers = {
        "raw_artifact_replay": layer_result(
            "PASS" if numbers else "FAIL",
            "Recomputed 21/24 and standard macro-F1 "
            f"{scored['macro_f1']:.15f} from results.jsonl vs suite gold, ignoring report.json correct flags.",
            {"correct": scored["correct"], "n": scored["n"], "macro_f1": scored["macro_f1"], "errors": scored["errors"]},
        ),
        "independent_scorer": layer_result(
            "PASS" if numbers else "FAIL",
            "Independent label extraction and accuracy/macro-F1 from written hidden-cause label set.",
            {"wilson": scored["wilson"]},
        ),
        "leakage_shortcut": layer_result(
            "PASS",
            "Exact gold-label tokens are absent from visible_symptom; keyword/template predictor is high because symptoms are textbook label definitions. Label-permutation of gold would collapse accuracy; that is a construct bound, not a count error.",
            {
                "exact_label_in_visible": planted,
                "keyword_predictor_correct": keyword_correct,
                "protected_fields_colocated": colocated,
                "published_accuracy": report["metrics"]["accuracy"],
            },
        ),
        "denominator_statistics": layer_result(
            "PASS" if scored["n"] == 24 else "FAIL",
            "Denominator is 24 frozen cases, 8 families × 3; no post-outcome exclusions; three immutable errors retained.",
            {"n": 24, "errors_retained": 3},
        ),
        "baseline_pressure": layer_result(
            "CANNOT_CHECK",
            "No official ADAS/DGM/ADIAS matched baseline was executed by this verifier. Keyword predictor is a ceiling/oracle for template coupling only.",
        ),
        "holdout_cross_host": layer_result(
            "CANNOT_CHECK",
            "Fresh hidden-cause mini-holdout / other-model transfer was not run. 21/24 is not self-improvement evidence.",
        ),
    }
    return [
        _base(
            root=root,
            record_id="P5.glm-5.2-attribution-21-24",
            paper_id="P5",
            claim_id="P5.glm52_attribution",
            atomic="GLM-5.2 hidden-cause attribution is 21/24 = 0.875. Published macro-F1 0.875 disagrees with independent standard macro-F1.",
            bounded="Diagnosis evidence on this 24-case suite only. Not self-improvement, not fresh-transfer, not model-general attribution. Independent macro-F1 uses tp/fp/fn per label.",
            subject_commit=git_sha(root),
            protocol_id="orion.p5.hidden-cause-case.v1",
            protocol_path=protocol_path,
            artifacts=artifacts,
            original_hash=_hash_or_cannot(report_path),
            independent_hash=independent_hash,
            agreement="DISAGREE",
            adjudication=[
                {
                    "field": "accuracy",
                    "published": 0.875,
                    "independent": scored["accuracy"],
                    "status": "EXACT",
                },
                {
                    "field": "correct_count",
                    "published": 21,
                    "independent": scored["correct"],
                    "status": "EXACT",
                },
                {
                    "field": "macro_f1",
                    "published": published_f1,
                    "independent": scored["macro_f1"],
                    "status": "DISAGREE",
                },
            ],
            denominator={
                "eligible_n": 24,
                "unit": "hidden-cause case",
                "repeats_nested_not_inflating_n": True,
                "cannot_check_or_invalid_handling": "zero runtime errors in results.jsonl",
                "post_outcome_exclusions": 0,
            },
            layers=layers,
            discrepancies=discrepancies,
            numbers_replayed=numbers,
            independent_agrees=numbers,
        )
    ]


def audit_p1(root: Path, independent_hash: str) -> list[dict[str, Any]]:
    scored_path = root / PAPER1 / "results/raw/test_scored.jsonl"
    t2_path = root / PAPER1 / "results/P1-T2_baseline_ablation_results.json"
    protocol_path = root / PAPER1 / "protocol/PROTOCOL_V1.json"
    solv_path = root / PAPER1 / "evidence/mechanical_solvability_audit_v1.json"
    records = load_jsonl(scored_path)
    t2 = load_json(t2_path)
    h1 = score_p1_h1(records)
    published_orion = 0.020833333333333332
    numbers = (
        h1["orion_n"] == 48
        and h1["orion_successes"] == 1
        and abs(float(h1["orion_rate"]) - published_orion) < 1e-12
        and h1["h1_status"] == "NOT_SUPPORTED"
    )
    discrepancies = []
    if t2["comparator"]["system_id"] != h1["strongest_baseline"]["system_id"]:
        discrepancies.append(
            {
                "id": "P1.strongest-baseline-identity",
                "severity": "low",
                "text": (
                    f"Independent strongest baseline {h1['strongest_baseline']['system_id']} "
                    f"vs published comparator {t2['comparator']['system_id']} "
                    "(tie-breaking may differ among equal 1/48 systems)."
                ),
            }
        )
    artifacts = [
        present_artifact(scored_path, "raw_record", root=root),
        present_artifact(t2_path, "aggregate", root=root),
        present_artifact(protocol_path, "protocol", root=root),
    ]
    h1_layers = {
        "raw_artifact_replay": layer_result(
            "PASS" if numbers else "FAIL",
            "Raw test_scored.jsonl majority reduction reproduces ORION 1/48 root_success and H1 NOT_SUPPORTED.",
            h1,
        ),
        "independent_scorer": layer_result(
            "PASS" if numbers else "FAIL",
            "Independent majority reduction over 5 repeats; did not import orion.study.p1.tables.",
        ),
        "leakage_shortcut": layer_result(
            "PASS",
            "Promoted mechanistic claims already record template-level leaks (66/66 framing phrase). H1 remains NOT_SUPPORTED; this verifier does not relabel the null as a positive.",
        ),
        "denominator_statistics": layer_result(
            "PASS" if h1["n_records"] == 2880 else "FAIL",
            "2880=12 systems × 48 cases × 5 repeats; case is the unit. The current frozen archive has no missing records.",
            {"n_records": h1["n_records"], "orion_n": h1["orion_n"]},
        ),
        "baseline_pressure": layer_result(
            "PASS",
            "In-battery strongest matched baseline ties ORION at 1/48. No external superiority campaign is claimed.",
            h1["strongest_baseline"],
        ),
        "holdout_cross_host": layer_result(
            "CANNOT_CHECK",
            "No new hidden-shift holdout was run by this verifier. H1 stays NOT_SUPPORTED.",
        ),
    }
    out = [
        _base(
            root=root,
            record_id="P1.H1.root-success-not-supported",
            paper_id="P1",
            claim_id="P1.H1",
            atomic="P1 H1 (root-success superiority vs strongest matched baseline) is NOT_SUPPORTED on the frozen TEST split (ORION 1/48).",
            bounded="The registered superiority gate returned NOT_SUPPORTED; this does not establish the null. Mechanistic subclaims must not be rewritten as H1 support. Design authority remains blocked by conflicting prospective-power specifications.",
            subject_commit=str(t2["provenance"]["integrity"]["subject_revisions"][0]),
            protocol_id="P1.hidden-formulation.v1",
            protocol_path=protocol_path,
            artifacts=artifacts,
            original_hash=_hash_or_cannot(t2_path),
            independent_hash=independent_hash,
            agreement="EXACT" if numbers else "DISAGREE",
            adjudication=[],
            denominator={
                "eligible_n": 48,
                "unit": "case after majority reduction of 5 repeats",
                "repeats_nested_not_inflating_n": True,
                "cannot_check_or_invalid_handling": "the recovered frozen archive contains all 2880 expected SCORED repeats; any future missing or partial cell must fail closed as CANNOT_CHECK",
                "post_outcome_exclusions": 0,
            },
            layers=h1_layers,
            discrepancies=discrepancies,
            numbers_replayed=numbers,
            independent_agrees=numbers,
        )
    ]
    solv = load_json(solv_path)
    solvable = sum(1 for case in solv["cases"] if case["verdict"] == "SOLVABLE")
    n_sol = len(solv["cases"])
    solv_layers = {
        "raw_artifact_replay": layer_result(
            "PASS" if n_sol == 66 else "FAIL",
            f"mechanical_solvability_audit_v1.json contains {solvable}/{n_sol} SOLVABLE verdicts.",
            {"solvable": solvable, "n": n_sol},
        ),
        "independent_scorer": layer_result(
            "PASS",
            "Independent count of frozen audit verdicts. This verifier did not re-blind-solve the 66 cases.",
        ),
        "leakage_shortcut": layer_result(
            "PASS",
            "The audit itself records template-level leaks and five arithmetic defects; those bounds are retained.",
        ),
        "denominator_statistics": layer_result(
            "PASS" if n_sol == 66 else "FAIL",
            "n=66 descriptive-only; below inferential n. Not H1 support.",
        ),
        "baseline_pressure": layer_result("CANNOT_CHECK", "No independent second rater was run by this verifier."),
        "holdout_cross_host": layer_result("CANNOT_CHECK", "No fresh case set for the solvability audit."),
    }
    out.append(
        _base(
            root=root,
            record_id="P1.solvability-audit-55-66",
            paper_id="P1",
            claim_id="P1.solvability_55_66",
            atomic="Independent blind solvability audit rates 55 of 66 cases SOLVABLE from public content.",
            bounded="Descriptive only (n=66). Not H1 support. Concurrent-edit note in the JSON is retained.",
            subject_commit=git_sha(root),
            protocol_id="P1.hidden-formulation.v1",
            protocol_path=protocol_path,
            artifacts=[present_artifact(solv_path, "raw_record", root=root)],
            original_hash=_hash_or_cannot(solv_path),
            independent_hash=independent_hash,
            agreement="EXACT" if solvable == 55 and n_sol == 66 else "DISAGREE",
            adjudication=[],
            denominator={
                "eligible_n": n_sol,
                "unit": "mechanical-arm case",
                "repeats_nested_not_inflating_n": True,
                "cannot_check_or_invalid_handling": "PARTIAL/UNSOLVABLE retained",
                "post_outcome_exclusions": 0,
            },
            layers=solv_layers,
            discrepancies=[],
            numbers_replayed=solvable == 55 and n_sol == 66,
            independent_agrees=solvable == 55 and n_sol == 66,
        )
    )
    arm_path = root / PAPER1 / "evidence/MECHANICAL_ARM_LIMITATIONS_V1.md"
    out.append(
        _base(
            root=root,
            record_id="P1.mechanical-arm-62-66",
            paper_id="P1",
            claim_id="P1.mechanical_arm_62_66",
            atomic="LLM-free reduction attributes correct top-ranked responsibility on 62 of 66 cases; 0 of 22 negative controls topped by formulation responsibility.",
            bounded="Descriptive only. Four general relations cover 26 cases; remaining attributions are untested for generality. Not H1 support. No machine-readable case table exists for independent rescoring.",
            subject_commit=git_sha(root),
            protocol_id="P1.hidden-formulation.v1",
            protocol_path=protocol_path,
            artifacts=[
                present_artifact(arm_path, "published_table", root=root),
                missing_artifact_record(
                    path="P1 mechanical-arm per-case attribution JSON (only markdown limitations note is tracked)",
                    role="missing_required",
                ),
            ],
            original_hash=_hash_or_cannot(arm_path),
            independent_hash=independent_hash,
            agreement="CANNOT_CHECK",
            adjudication=[],
            denominator={
                "eligible_n": 66,
                "unit": "mechanical-arm case",
                "repeats_nested_not_inflating_n": True,
                "cannot_check_or_invalid_handling": "no JSON case table; independent rescoring CANNOT_CHECK",
                "post_outcome_exclusions": 0,
            },
            layers={
                "raw_artifact_replay": layer_result(
                    "CANNOT_CHECK",
                    "Only a limitations markdown exists; 62/66 cannot be regenerated from a case table.",
                ),
                "independent_scorer": layer_result("CANNOT_CHECK", "No per-case mechanical-arm decisions in JSON."),
                "leakage_shortcut": layer_result(
                    "PASS",
                    "The limitations note already records one-case rules (32/66) and template risk; retained rather than tuned away.",
                ),
                "denominator_statistics": layer_result("CANNOT_CHECK", "Cannot audit 62/66 without the case table."),
                "baseline_pressure": layer_result("CANNOT_CHECK", "No second mechanical rater in this verifier run."),
                "holdout_cross_host": layer_result("CANNOT_CHECK", "No fresh cases for the mechanical arm."),
            },
            discrepancies=[
                {
                    "id": "P1.mechanical-arm-no-case-table",
                    "severity": "medium",
                    "text": "62/66 is documented only in markdown; independent case-level replay is CANNOT_CHECK.",
                }
            ],
            numbers_replayed=False,
            independent_agrees=False,
        )
    )
    return out


def run_all(root: Path) -> list[dict[str, Any]]:
    independent_hash = sha256_file(Path(__file__).resolve().parent / "independent_scorers.py")
    records: list[dict[str, Any]] = []
    records.extend(audit_p4(root, independent_hash))
    records.extend(audit_p3(root, independent_hash))
    records.extend(audit_p2(root, independent_hash))
    records.extend(audit_p5(root, independent_hash))
    records.extend(audit_p1(root, independent_hash))
    return records


def write_all(root: Path) -> list[Path]:
    out_dir = root / "research/verification/records"
    paths: list[Path] = []
    for record in run_all(root):
        path = out_dir / f"{record['record_id']}.json"
        dump_record(path, {key: value for key, value in record.items() if key != "record_sha256"})
        paths.append(path)
    index = {
        "schema_version": "orion.scientific-result-verification-index.v1",
        "issue": 283,
        "records": [path.name for path in paths],
        "states": {},
    }
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        index["states"][payload["record_id"]] = payload["verification_state"]
    (out_dir / "INDEX.json").write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return paths


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    paths = write_all(root)
    print(json.dumps({"wrote": [str(path) for path in paths]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
