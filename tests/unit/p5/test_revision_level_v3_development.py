from __future__ import annotations

import json
from pathlib import Path

from orion.study.p5.revision_level_v3_development import derive_development_summary

ROOT = Path(__file__).resolve().parents[3]
SUITE = ROOT / "research" / "self-orion-v3" / "development" / "PROTECTED_DEVELOPMENT_SUITE_V1.json"
V1_PROTOCOL = ROOT / "papers" / "orion-15-self-orion" / "protocol" / "PROTOCOL_V1.json"


def test_development_panel_is_evidence_sensitive_but_not_scientific_result() -> None:
    suite = json.loads(SUITE.read_text(encoding="utf-8"))
    summary = derive_development_summary(suite)
    assert summary["terminal"] == "T8_PROSPECTIVE_EXPERIMENT_IMPLEMENTED_CANNOT_CHECK_OUTCOME"
    assert summary["scientific_result"] == "NOT_RUN"
    assert summary["supports_p5_h1_h4"] is False
    assert summary["grants_peer_review_ready"] is False
    assert summary["closes_issue_455"] is False
    normal = summary["full_t7_feedback_sensitivity"]["NORMAL"]["revision_accuracy"]
    no_feedback = summary["full_t7_feedback_sensitivity"]["NONE"]["revision_accuracy"]
    permuted = summary["full_t7_feedback_sensitivity"]["PERMUTED"]["revision_accuracy"]
    assert normal == 1.0
    assert no_feedback < normal
    assert permuted < normal
    assert summary["confirmatory_preflight"]["status"] == "CANNOT_CHECK"


def test_oracle_is_analysis_only_and_generic_diagnosis_is_not_hidden() -> None:
    suite = json.loads(SUITE.read_text(encoding="utf-8"))
    summary = derive_development_summary(suite)
    oracle = summary["policy_scores"]["ORACLE_CEILING"]
    generic = summary["policy_scores"]["GENERIC_CAUSAL_DIAGNOSIS"]
    full = summary["policy_scores"]["FULL_T7"]
    assert oracle["analysis_only"] is True
    assert oracle["eligible_for_superiority_claim"] is False
    assert generic["revision_accuracy"] == full["revision_accuracy"] == 1.0
    # Development instrumentation is deliberately not engineered to manufacture
    # an incremental T7-vs-generic scientific effect.


def test_existing_p5_v1_protocol_remains_original_frozen_design() -> None:
    protocol = json.loads(V1_PROTOCOL.read_text(encoding="utf-8"))
    assert protocol["protocol_id"] == "P5.hidden-cause-fresh-transfer.v1"
    assert protocol["protocol_status"] == "DESIGN_FROZEN"
    assert protocol["outcome_accessed"] is False
    assert protocol["execution_bindings"]["subject_revision"] == "UNBOUND"
