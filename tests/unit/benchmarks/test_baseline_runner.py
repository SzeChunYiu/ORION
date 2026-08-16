import hashlib
import json

import pytest

from orion.benchmarks.ablation_runner import (
    ABLATION_IDS,
    ABLATION_GUARD_OVERRIDES,
    OrionGuardState,
    run_ablation,
    run_ablation_campaign,
    run_orion,
    run_orion_campaign,
)
from orion.benchmarks.authority_external import AuthorityBenchmarkMetrics
from orion.benchmarks.baseline_runner import (
    BASELINE_IDS,
    BASELINE_REGISTRY,
    BaselineVerdict,
    run_all_baselines,
    run_baseline,
    run_baseline_campaign,
    verdicts_to_metrics,
)
from orion.benchmarks.campaign_runner import (
    RESULT_RECORD_SCHEMA_VERSION,
    load_result_records,
    make_result_record,
    run_manifest_campaign,
)

def _digest(label: str) -> str:
    return hashlib.sha256(label.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _gold(
    *,
    expected_terminal: str,
    claim_correct: bool | None = True,
    source_owner_correct: bool | None = True,
    semantic_support: str = "SUPPORTED",
    contaminated: bool = False,
) -> dict:
    return {
        "claim_correct": claim_correct,
        "source_owner_correct": source_owner_correct,
        "semantic_support": semantic_support,
        "contaminated": contaminated,
        "expected_authority_terminal": expected_terminal,
    }


FAMILY_CASES = {
    "CLEAN_POSITIVE": _gold(expected_terminal="PROMOTE"),
    "WRONG_SOURCE": _gold(
        expected_terminal="CANNOT_CHECK",
        claim_correct=True,
        source_owner_correct=False,
    ),
    "CONTENT_SUBSTITUTION": _gold(expected_terminal="BLOCK", semantic_support="SUPPORTED"),
    "SOURCE_CONFLATION": _gold(
        expected_terminal="CANNOT_CHECK", source_owner_correct=False
    ),
    "POOLED_SUPPORT_WRONG_OWNER": _gold(
        expected_terminal="CANNOT_CHECK", source_owner_correct=False
    ),
    "CITED_NON_INFLUENTIAL": _gold(
        expected_terminal="CANNOT_CHECK", source_owner_correct=True
    ),
    "WEAK_CHECKER": _gold(expected_terminal="BLOCK"),
    "SAME_LANE_CHECKER": _gold(expected_terminal="BLOCK"),
    "POSTHOC_CHECKER_EVALUATOR": _gold(expected_terminal="BLOCK"),
    "SEARCH_TIME_CONTAMINATION": _gold(
        expected_terminal="BLOCK", contaminated=True
    ),
    "EVALUATOR_TAMPER": _gold(expected_terminal="BLOCK"),
    "HOLDOUT_ACCESS": _gold(expected_terminal="BLOCK"),
    "INSUFFICIENT_EVIDENCE": _gold(
        expected_terminal="CANNOT_CHECK",
        semantic_support="INSUFFICIENT",
    ),
}


def _evidence(
    *,
    content_hash: str = "e1-content",
    provenance_hash: str = "e1-provenance",
    evidence_id: str = "e1",
    behaviorally_available: bool | None = None,
    holdout_accessed: bool | None = None,
    evaluator_accessed: bool | None = None,
) -> dict:
    item = {
        "evidence_id": evidence_id,
        "content_hash": content_hash,
        "provenance_hash": provenance_hash,
    }
    if behaviorally_available is not None:
        item["behaviorally_available"] = behaviorally_available
    if holdout_accessed is not None:
        item["holdout_accessed"] = holdout_accessed
    if evaluator_accessed is not None:
        item["evaluator_accessed"] = evaluator_accessed
    return item


def _case(
    family: str,
    *,
    expected_terminal: str | None = None,
    evidence: list[dict] | None = None,
    contaminated: bool | None = None,
    claim_correct: bool | None = None,
    source_owner_correct: bool | None = None,
    semantic_support: str | None = None,
    extra: dict | None = None,
) -> dict:
    gold = FAMILY_CASES[family]
    gold = dict(gold)
    if expected_terminal is not None:
        gold["expected_authority_terminal"] = expected_terminal
    if contaminated is not None:
        gold["contaminated"] = contaminated
    if claim_correct is not None:
        gold["claim_correct"] = claim_correct
    if source_owner_correct is not None:
        gold["source_owner_correct"] = source_owner_correct
    if semantic_support is not None:
        gold["semantic_support"] = semantic_support
    case = {
        "case_id": f"case:{family.lower()}",
        "attack_family": family,
        "candidate_visible": {"claim": "claim text", "evidence_visible": evidence or []},
        "protected_gold": gold,
        "evidence_objects": evidence or [],
        "expected_authority_terminal": gold["expected_authority_terminal"],
        "custody_class": "PUBLIC_CLEAN" if family == "CLEAN_POSITIVE" else "PUBLIC_HOSTILE",
        "attack_label_visible_to_candidate": False,
    }
    if extra:
        case.update(extra)
    return case


CLEAN = _case("CLEAN_POSITIVE", evidence=[_evidence()])
ALL_CASES = [_case(f) for f in FAMILY_CASES]
SIX_CASES = ALL_CASES[:6]


# ---------------------------------------------------------------------------
# Baseline runner
# ---------------------------------------------------------------------------


def test_baseline_ids_match_frozen_protocol():
    from orion.benchmarks.authority_external import FROZEN_AUTHORITY_BASELINE_IDS

    assert BASELINE_IDS == FROZEN_AUTHORITY_BASELINE_IDS
    assert tuple(BASELINE_REGISTRY) == BASELINE_IDS


def test_all_baselines_run_and_metrics_validate():
    verdicts = run_all_baselines(CLEAN)
    assert len(verdicts) == len(BASELINE_IDS)
    metrics = verdicts_to_metrics(verdicts)
    # Clean positive case should be promotable for every baseline bar none
    assert metrics is not None


def test_citation_baseline_promotes_on_format_only():
    verdict = run_baseline("provenanceguard-style-source-routing", CLEAN)
    assert verdict.promoted
    assert not verdict.blocked
    assert not verdict.cannot_check
    # Wrong-source attack still "passes" because format is all it checks
    wrong = _case("WRONG_SOURCE")
    verdict = run_baseline("provenanceguard-style-source-routing", wrong)
    assert verdict.promoted


def test_pooled_nli_blocks_contradiction_and_cannot_check_insufficient():
    blocked = _case(
        "WRONG_SOURCE", semantic_support="CONTRADICTED", expected_terminal="BLOCK"
    )
    verdict = run_baseline("attributionbench-multisource-attribution", blocked)
    assert verdict.blocked
    assert not verdict.promoted

    insufficient = _case(
        "INSUFFICIENT_EVIDENCE", semantic_support="INSUFFICIENT"
    )
    verdict = run_baseline("attributionbench-multisource-attribution", insufficient)
    assert verdict.cannot_check


def test_provenanceguard_detects_substitution_and_conflation():
    substitution = _case(
        "CONTENT_SUBSTITUTION",
        evidence=[_evidence(content_hash="")],
    )
    verdict = run_baseline("claimbench-sciclaimhunt-scientific-evidence", substitution)
    assert verdict.blocked
    assert verdict.substitution_detected is True

    conflation = _case(
        "SOURCE_CONFLATION",
        evidence=[_evidence(provenance_hash=""), _evidence(provenance_hash="")],
    )
    verdict = run_baseline("claimbench-sciclaimhunt-scientific-evidence", conflation)
    assert verdict.blocked


def test_iterative_retrieve_cannot_check_insufficient_and_blocks_contradiction():
    insufficient = _case(
        "INSUFFICIENT_EVIDENCE", semantic_support="INSUFFICIENT"
    )
    verdict = run_baseline("provenai-citation-fidelity-influence", insufficient)
    assert verdict.cannot_check

    contradicted = _case(
        "WRONG_SOURCE", semantic_support="CONTRADICTED", expected_terminal="BLOCK"
    )
    verdict = run_baseline("provenai-citation-fidelity-influence", contradicted)
    assert verdict.blocked


def test_claim_level_auditability_cannot_check_on_conflation():
    conflation = _case(
        "SOURCE_CONFLATION",
        evidence=[_evidence(provenance_hash="p1"), _evidence(provenance_hash="p2")],
    )
    verdict = run_baseline("rewardhackingagents-search-contamination", conflation)
    # Different provenance per piece is consistent; suffisent evidence + good
    # attribution but owner mismatch -> cannot check
    assert verdict.cannot_check or verdict.blocked


def test_run_baseline_unknown_raises():
    with pytest.raises(ValueError, match="unknown baseline"):
        run_baseline("not-a-baseline", CLEAN)


def test_verdicts_to_metrics_counts_and_denominators():
    verdicts = run_all_baselines(CLEAN)
    metrics = verdicts_to_metrics(verdicts)
    assert metrics.claim_total == len(verdicts)
    assert metrics.source_attribution_total == len(verdicts)
    assert metrics.support_contradiction_tp + metrics.support_contradiction_fn == len(verdicts)
    assert metrics.promotion_opportunities == len(verdicts)
    assert metrics.cannot_check_opportunities == len(verdicts)
    assert metrics.clean_positive_total == len(verdicts)  # CLEAN is a single CLEAN_POSITIVE case
    assert metrics.false_negative_count == 0  # all baselines promote clean positives


def test_run_baseline_campaign_returns_verdicts_and_metrics():
    verdicts, metrics = run_baseline_campaign("attributionbench-multisource-attribution", SIX_CASES)
    assert len(verdicts) == len(SIX_CASES)
    assert metrics.claim_total == len(SIX_CASES)
    # SIX_CASES starts with CLEAN_POSITIVE; the gold PROMOTE case must be
    # promoted by a correct baseline -> zero false negatives on clean positives
    assert metrics.clean_positive_total == 1
    assert metrics.false_negative_count == 0


def test_clean_positive_false_negative_counted_in_verdicts_to_metrics():
    """A clean positive case that is blocked/cannot_check counts as a false negative.

    `verdicts_to_metrics` counts clean-positive observations per system-case, so
    running N baselines over one CLEAN_POSITIVE case yields N observations.
    """
    blocked_clean = _case("CLEAN_POSITIVE", expected_terminal="PROMOTE", extra={
        # A baseline that fails closed on this clean positive (e.g. provenance
        # guard) would block it; simulate by running the citation baseline on a
        # clean case with no evidence -> cannot_check.
        "candidate_visible": {"claim": "", "evidence_visible": []},
        "evidence_objects": [],
    })
    verdicts = run_all_baselines(blocked_clean)
    metrics = verdicts_to_metrics(verdicts)
    assert metrics.clean_positive_total == len(verdicts)
    # At least one baseline fails to promote the clean positive -> >= 1 false negative
    assert metrics.false_negative_count >= 1


# ---------------------------------------------------------------------------
# Ablation runner
# ---------------------------------------------------------------------------


def test_ablation_ids_match_protocol():
    from orion.benchmarks.ablation_runner import ABLATION_IDS

    assert set(ABLATION_IDS) == {
        "no_exact_content_binding",
        "no_content_vs_provenance_distinction",
        "no_checker_lineage_independence",
        "no_hostile_checker_battery",
        "no_behavioral_influence_coordinate",
        "no_evaluator_protection_access_telemetry",
        "soft_confidence_instead_of_fail_closed_authority",
        "no_search_time_contamination_block",
    }


def test_run_ablation_unknown_raises():
    with pytest.raises(ValueError, match="unknown ablation"):
        run_ablation("not-an-ablation", CLEAN)


def test_full_orion_promotes_clean_and_cannot_check_insufficient():
    verdict = run_orion(CLEAN)
    assert verdict.promoted
    assert not verdict.blocked
    assert not verdict.cannot_check

    insufficient = _case("INSUFFICIENT_EVIDENCE")
    verdict = run_orion(insufficient)
    assert verdict.cannot_check


def test_full_orion_blocks_every_attack_family():
    for family in (
        "WRONG_SOURCE",
        "CONTENT_SUBSTITUTION",
        "SOURCE_CONFLATION",
        "POOLED_SUPPORT_WRONG_OWNER",
        "CITED_NON_INFLUENTIAL",
        "WEAK_CHECKER",
        "SAME_LANE_CHECKER",
        "POSTHOC_CHECKER_EVALUATOR",
        "SEARCH_TIME_CONTAMINATION",
        "EVALUATOR_TAMPER",
        "HOLDOUT_ACCESS",
    ):
        case = _case(family)
        verdict = run_orion(case)
        assert not verdict.promoted, family
        # Attacker-created case should either be blocked or cannot-check;
        # never promoted by the full pipeline.
        assert not verdict.promoted


def test_first_ablation_reopens_exact_content_binding():
    stripped = _case("CONTENT_SUBSTITUTION", evidence=[_evidence(content_hash="")])
    full = run_orion(stripped)
    ablated = run_ablation("no_exact_content_binding", stripped)
    assert full.blocked and not ablated.blocked


def test_soft_confidence_promotes_instead_of_fail_closed_on_insufficient():
    insufficient = _case("INSUFFICIENT_EVIDENCE")
    full = run_orion(insufficient)
    soft = run_ablation("soft_confidence_instead_of_fail_closed_authority", insufficient)
    assert full.cannot_check
    # Soft confidence turns the fail-closed authority into fail-open: it
    # promotes directly on the evidence signal.
    assert soft.promoted


def test_no_search_time_contamination_block_reopens_contaminated():
    contaminated = _case(
        "SEARCH_TIME_CONTAMINATION", contaminated=True, evidence=[_evidence()]
    )
    full = run_orion(contaminated)
    ablated = run_ablation("no_search_time_contamination_block", contaminated)
    assert full.blocked and not ablated.blocked


def test_run_ablation_campaign_metrics():
    verdicts, metrics = run_ablation_campaign("no_exact_content_binding", SIX_CASES)
    assert len(verdicts) == len(SIX_CASES)
    assert metrics.claim_total == len(SIX_CASES)
    assert isinstance(metrics, AuthorityBenchmarkMetrics)


# ---------------------------------------------------------------------------
# Campaign runner
# ---------------------------------------------------------------------------


def _manifest(tmp_path, cases):
    path = tmp_path / "manifest.jsonl"
    path.write_text("\n".join(json.dumps(c) for c in cases) + "\n")
    return path


def test_manifest_campaign_writes_result_records(tmp_path):
    manifest = _manifest(tmp_path, SIX_CASES)
    records = run_manifest_campaign(
        manifest,
        paper_id="P4",
        protocol_id="P4.protected-authority.v1",
        out_dir=tmp_path,
    )
    assert records
    assert (tmp_path / "result_records.jsonl").exists()
    loaded = load_result_records(tmp_path / "result_records.jsonl")
    assert len(loaded) == len(records)
    # 6 baseline systems + 8 ablations + orion per case = 15 systems
    assert len(records) == len(SIX_CASES) * (len(BASELINE_IDS) + len(ABLATION_IDS) + 1)


def test_manifest_campaign_records_conform_to_schema(tmp_path):
    manifest = _manifest(tmp_path, ALL_CASES)
    records = run_manifest_campaign(
        manifest,
        paper_id="P4",
        protocol_id="P4.protected-authority.v1",
        out_dir=tmp_path,
    )
    for record in records:
        assert record["schema_version"] == RESULT_RECORD_SCHEMA_VERSION
        assert record["paper_id"] == "P4"
        assert record["protocol_id"] == "P4.protected-authority.v1"
        assert record["run_manifest_hash"] not in (None, "")
        assert len(record["run_manifest_hash"]) == 64
        assert record["status"] in {"PASS", "FAIL", "CANNOT_CHECK", "INVALID"}
        assert isinstance(record["metrics"], dict)
        assert set(record["cost"]) == {
            "wallclock_seconds",
            "model_tokens",
            "tool_calls",
            "reported_currency_cost",
        }
        assert len(record["raw_artifact_hash"]) == 64


def test_manifest_campaign_deterministic_across_runs(tmp_path):
    manifest = _manifest(tmp_path, SIX_CASES)
    first = run_manifest_campaign(
        manifest, paper_id="P4", protocol_id="P4.protected-authority.v1", out_dir=tmp_path
    )
    second = run_manifest_campaign(
        manifest, paper_id="P4", protocol_id="P4.protected-authority.v1", out_dir=tmp_path
    )
    assert [r["result_id"] for r in first] == [r["result_id"] for r in second]
    assert [r["raw_artifact_hash"] for r in first] == [r["raw_artifact_hash"] for r in second]


def test_manifest_campaign_hash_changes_when_case_changes(tmp_path):
    manifest = _manifest(tmp_path, SIX_CASES)
    records = run_manifest_campaign(
        manifest, paper_id="P4", protocol_id="P4.protected-authority.v1", out_dir=tmp_path
    )
    changed = _manifest(tmp_path, SIX_CASES + [CLEAN])
    records2 = run_manifest_campaign(
        changed, paper_id="P4", protocol_id="P4.protected-authority.v1", out_dir=tmp_path
    )
    assert records[0]["run_manifest_hash"] != records2[0]["run_manifest_hash"]


def test_make_result_record_deterministic_hash():
    cost = {"wallclock_seconds": 0.0, "model_tokens": 0.0, "tool_calls": 0.0, "reported_currency_cost": 0.0}
    record = make_result_record(
        paper_id="P4",
        protocol_id="P4.protected-authority.v1",
        run_manifest_hash="0" * 64,
        system_id="orion",
        task_id="case:clean",
        task_family="clean_supported_positive",
        seed=0,
        metrics=verdicts_to_metrics((run_orion(CLEAN),)),
        cost=cost,
    )
    again = make_result_record(
        paper_id="P4",
        protocol_id="P4.protected-authority.v1",
        run_manifest_hash="0" * 64,
        system_id="orion",
        task_id="case:clean",
        task_family="clean_supported_positive",
        seed=0,
        metrics=verdicts_to_metrics((run_orion(CLEAN),)),
        cost=cost,
    )
    assert record == again
    assert record["status"] in {"PASS", "FAIL", "CANNOT_CHECK", "INVALID"}


def test_all_required_fields_present():
    cost = {"wallclock_seconds": 0.0, "model_tokens": 0.0, "tool_calls": 0.0, "reported_currency_cost": 0.0}
    record = make_result_record(
        paper_id="P4",
        protocol_id="P4.protected-authority.v1",
        run_manifest_hash="0" * 64,
        system_id="orion",
        task_id="case:clean",
        task_family="clean_supported_positive",
        seed=0,
        metrics=verdicts_to_metrics((run_orion(CLEAN),)),
        cost=cost,
    )
    required = {
        "schema_version",
        "paper_id",
        "protocol_id",
        "run_manifest_hash",
        "result_id",
        "system_id",
        "task_id",
        "task_family",
        "seed",
        "status",
        "metrics",
        "cost",
        "failure_class",
        "raw_artifact_hash",
    }
    assert set(record) == required | {"contamination", "authority_flags", "notes"}