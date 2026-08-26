"""Issue #279 one-stage attribution, Wide freeze, and V2 discriminator.

These tests exercise the taxonomy on synthetic traces and the committed Deep/Wide
archives. They do not call arXiv, do not mutate PROTOCOL_V1, and do not treat a
rate-limit as a scientific zero.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from orion.study.p2.one_stage_attribution import (
    FailureStage,
    ItemTrace,
    aggregate_stages,
    classify_item,
    ledger_from_artifacts,
    query_is_plausible,
)

ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "papers" / "orion-12-open-world-scientific-discovery"
EMIT = PAPER / "scripts" / "emit_issue279_revival_receipts.py"
PROTOCOL_V1 = PAPER / "protocol" / "PROTOCOL_V1.json"
PROTOCOL_V2 = PAPER / "protocol" / "P2_V2_CANDIDATE_GENERATION_DISCRIMINATOR_V1.json"
RECEIPT = PAPER / "evidence" / "external_results" / "OFFLINE_390_REPRODUCTION_RECEIPT_V1.json"
WIDE_FREEZE = PAPER / "evidence" / "external_results" / "WIDE_MATCHED_CAMPAIGN_FREEZE_V1.json"
LEDGER = PAPER / "evidence" / "external_results" / "ONE_STAGE_FAILURE_ATTRIBUTION_LEDGER_V1.json"
DEEP_ATTR = PAPER / "evidence" / "external_results" / "DEEP_ZERO_HIT_STAGE_ATTRIBUTION_2026-08-17.json"
DEEP_ARCHIVE = PAPER / "evidence" / "external_results" / "DEEP_OFFICIAL_ARCHIVE_V1.json"
WIDE_PROBE = PAPER / "evidence" / "external_results" / "AUTORESEARCHBENCH_WIDE_KEYLESS_PROBE_V1.json"
SUMMARY = (
    PAPER
    / "evidence"
    / "offline_results"
    / "RESULTS_SUMMARY_PRE_CANONICAL_VOCABULARY_2026-08-25.json"
)

ALPHAFOLD = "AlphaFold protein structure prediction"


def _trace(**overrides) -> ItemTrace:
    base = dict(
        task_id="wide-test",
        gold_ids=("2501.00001",),
        gold_titles=(ALPHAFOLD,),
        queries=("AlphaFold protein structure",),
        candidates=(),
        provider_statuses=("OK",),
    )
    base.update(overrides)
    return ItemTrace(**base)


def test_plausible_query_requires_shared_content_tokens() -> None:
    assert query_is_plausible(
        ("AlphaFold protein structure",),
        gold_ids=("2501.00001",),
        gold_titles=(ALPHAFOLD,),
    )
    assert not query_is_plausible(
        ("climate change models",),
        gold_ids=("2501.00001",),
        gold_titles=(ALPHAFOLD,),
    )


def test_hit_is_none() -> None:
    assert (
        classify_item(_trace(candidates=("2501.00001 The AlphaFold paper",), gold_recovered=True))
        is FailureStage.NONE
    )


def test_missing_gold_labels_cannot_check() -> None:
    assert (
        classify_item(
            ItemTrace(task_id="empty", queries=("anything",), provider_statuses=("OK",))
        )
        is FailureStage.CANNOT_CHECK
    )


def test_implausible_query_is_query_derivation_miss() -> None:
    assert (
        classify_item(_trace(queries=("climate change models",)))
        is FailureStage.QUERY_DERIVATION_MISS
    )


def test_plausible_query_without_gold_in_candidates_is_generation_miss() -> None:
    assert (
        classify_item(_trace(candidates=("A completely different paper about optics",)))
        is FailureStage.CANDIDATE_GENERATION_MISS
    )


def test_semantic_scholar_429_is_censored_route_not_generation_miss() -> None:
    """The named open-obligation case: HTTP 429 is never a silent drop."""

    stage = classify_item(
        _trace(
            queries=("AlphaFold protein structure",),
            candidates=(),
            provider_statuses=("RATE_LIMITED",),
        )
    )
    assert stage is FailureStage.CENSORED_ROUTE
    assert stage is not FailureStage.CANDIDATE_GENERATION_MISS


def test_unobserved_index_is_censored_even_when_queries_look_reasonable() -> None:
    for status in ("UNAVAILABLE", "SERVICE_ERROR", "RATE_LIMIT_DEFERRED", "KEY_REQUIRED"):
        assert classify_item(_trace(provider_statuses=(status,), candidates=())) is (
            FailureStage.CENSORED_ROUTE
        )


def test_gold_beyond_cutoff_is_ranking_miss() -> None:
    assert (
        classify_item(
            _trace(
                candidates=("2401.99999",),
                candidate_pool_ranked=("2401.99999", "2501.00001"),
                ranking_cutoff=1,
            )
        )
        is FailureStage.RANKING_MISS
    )


def test_retrieved_then_rejected_is_screening_miss() -> None:
    assert (
        classify_item(
            _trace(
                candidates=("2501.00001",),
                gold_recovered=False,
                screened_out=("2501.00001",),
            )
        )
        is FailureStage.SCREENING_MISS
    )


def test_identity_route_task_budget_and_unresolved() -> None:
    pool = ("2501.00001",)
    assert (
        classify_item(_trace(candidates=pool, identity_conflated=True, gold_recovered=False))
        is FailureStage.IDENTITY_DEDUP_ERROR
    )
    assert (
        classify_item(
            _trace(
                candidates=pool,
                gold_recovered=False,
                route_stop_while_gain_possible=True,
            )
        )
        is FailureStage.ROUTE_STOP_ERROR
    )
    assert (
        classify_item(
            _trace(
                candidates=pool,
                gold_recovered=False,
                task_closed_with_open_routes=True,
            )
        )
        is FailureStage.TASK_STOP_ERROR
    )
    assert (
        classify_item(
            _trace(candidates=pool, gold_recovered=False, budget_exhausted=True)
        )
        is FailureStage.BUDGET_EXHAUSTION
    )
    assert (
        classify_item(_trace(candidates=pool, gold_recovered=False))
        is FailureStage.OTHER_UNRESOLVED
    )


def test_aggregate_dominance_ignores_hits_and_breaks_ties_by_pipeline_order() -> None:
    summary = aggregate_stages(
        (
            FailureStage.NONE,
            FailureStage.CANDIDATE_GENERATION_MISS,
            FailureStage.CANDIDATE_GENERATION_MISS,
            FailureStage.QUERY_DERIVATION_MISS,
            FailureStage.QUERY_DERIVATION_MISS,
            FailureStage.CANNOT_CHECK,
        )
    )
    assert summary["dominant_earliest_stage"] == FailureStage.QUERY_DERIVATION_MISS.value
    assert summary["counts"][FailureStage.NONE.value] == 1


def test_deep_zero_hit_archive_is_candidate_generation() -> None:
    ledger = ledger_from_artifacts(
        deep_attribution=json.loads(DEEP_ATTR.read_text(encoding="utf-8")),
        deep_archive=json.loads(DEEP_ARCHIVE.read_text(encoding="utf-8")),
        wide_probe=json.loads(WIDE_PROBE.read_text(encoding="utf-8")),
    )
    assert ledger["dominant_earliest_stage"] == FailureStage.CANDIDATE_GENERATION_MISS.value
    assert ledger["deep"]["official_hits"] == 0
    assert ledger["deep"]["exact_title_recoveries"] == 0
    assert ledger["deep"]["substring_recoveries"] == 0
    assert ledger["deep"]["judge_control_passed"] is True
    assert ledger["deep"]["item_level_computable"] is True
    assert ledger["wide"]["item_level_stage"] == FailureStage.CANNOT_CHECK.value
    assert ledger["wide"]["censored_route_census"]["RATE_LIMITED"] == 52
    assert ledger["wide"]["censored_route_census"]["SERVICE_ERROR"] == 2
    assert ledger["close_issue"] is False
    assert ledger["p2_v1_mutation"] == "forbidden"
    assert ledger["allocator_architecture"] == "not_licensed_before_external_test"


def test_committed_receipts_exist_and_bind_the_historical_390_task_summary() -> None:
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    freeze = json.loads(WIDE_FREEZE.read_text(encoding="utf-8"))
    protocol = json.loads(PROTOCOL_V2.read_text(encoding="utf-8"))
    v1 = json.loads(PROTOCOL_V1.read_text(encoding="utf-8"))

    assert receipt["bindings"]["n_tasks"] == 390
    assert receipt["bindings"]["n_result_records"] == 16380
    assert receipt["bindings"]["orion_complete_gold_recall"] == 0.979487
    assert receipt["bindings"]["baseline_complete_gold_recall"] == 0.666667
    assert receipt["bindings"]["orion_premature_task_closure_rate"] == 0.0
    assert receipt["bindings"]["achieved_precision_tier"] == "TIER_B_committed"
    assert receipt["bindings"]["primary_promoted"] is False
    assert receipt["content_hashes"]["record_digest_sha256"] == summary["frozen_run"][
        "record_digest_sha256"
    ]
    assert receipt["content_hashes"]["results_summary_file_sha256"] == hashlib.sha256(
        SUMMARY.read_bytes()
    ).hexdigest()
    assert receipt["artifact"] == "evidence/offline_results/RESULTS_SUMMARY_V1.json"
    assert receipt["regeneration"]["match"] is True
    assert receipt["close_issue"] is False

    assert freeze["status"] == "BLOCKED_NOT_EXECUTED"
    assert freeze["expected_n"] == 399
    assert freeze["outputs_dir"] == "/tmp/p2-wide-matched"
    assert any(item["id"] == "ARXIV_API_FORBIDDEN" for item in freeze["blockers"])
    assert "run_autoresearchbench_wide_comparison.py" in freeze["run_command"]
    assert freeze["p2_v1_mutation"] == "forbidden"

    assert protocol["rewrites_parent"] is False
    assert protocol["parent_protocol_id"] == v1["protocol_id"]
    assert protocol["allocator_architecture"] == "not_implemented"
    assert protocol["official_implementations"]["SAGE"] == "CANNOT_CHECK"
    assert protocol["official_implementations"]["AgentSLR"] == "CANNOT_CHECK"
    assert "fixed_v1_allocation" in protocol["baselines_and_ablations_if_allocator_later"]
    assert "treat_censoring_as_zero_reward" in protocol["baselines_and_ablations_if_allocator_later"]
    assert protocol["backends"]["semantic_scholar_429"] == "open_obligation_never_silent_drop"


def test_emit_script_check_matches_committed_receipts() -> None:
    result = subprocess.run(
        [sys.executable, str(EMIT), "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr + result.stdout
    assert "match committed artifacts" in result.stdout


def test_protocol_v1_is_untouched_by_this_lane() -> None:
    """A V2 discriminator that rewrote V1 would be an issue-#279 constraint violation."""

    v1 = json.loads(PROTOCOL_V1.read_text(encoding="utf-8"))
    v2 = json.loads(PROTOCOL_V2.read_text(encoding="utf-8"))
    assert v1["protocol_id"] == "P2.open-world-discovery.v1"
    assert v1["protocol_status"] == "DESIGN_FROZEN"
    assert v2["rewrites_parent"] is False
    assert v2["protocol_id"] != v1["protocol_id"]
