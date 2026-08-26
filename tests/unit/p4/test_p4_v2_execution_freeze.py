from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
P4 = ROOT / "papers" / "orion-14-verified-scientific-discovery"
BINDINGS = P4 / "protocol" / "PROTECTED_RUN_BINDINGS_V2.json"
WORKFLOW = ROOT / ".github" / "workflows" / "p4_protected_campaign_v2.yml"
TRIGGER = P4 / "host" / "CAMPAIGN_TRIGGER_V2.txt"
CONFIG = P4 / "host" / "BASELINE_CONFIGS_V2.json"


def test_v2_execution_bindings_are_concrete_and_outcome_blind() -> None:
    b = json.loads(BINDINGS.read_text())
    assert b["schema"] == "P4ProtectedRunBindings.v2"
    assert b["campaign_id"] == "P4.protected-authority.v2"
    assert b["base_protocol_id"] == "P4.protected-authority.v1"
    assert b["status"] == "EXECUTION_FROZEN"
    assert b["outcome_accessed"] is False
    assert b["campaign_execution_authorized"] is False
    assert b["subject_commit"] == "f6e51b5c8f905382b8e2f5568d9035fc14241aa1"
    assert b["subject_archive_sha256"] == "a617a30ba8ebce5f7f89ceca77dbde793a7c43f85b8b01300e8ec1ef40a1e0e4"
    assert b["host_preparation"]["run_id"] == "31975937488"
    assert b["dataset_revisions"]["protected_attack_set_sha256"] == "6b8b6243040163dfa582dbeb8896e2c68d6b263e3227b64e7bab199d8599897c"
    assert b["dataset_revisions"]["split_sha256"] == "3fe91b669643fa158f2f64c1e6ab70837afbb9b0582e297f1da6e1c3c696fcd9"
    assert b["baseline_config_sha256"] == "df389938f0bf1d6ef9312c82c5cadeba9af60c9a8ce7c602c10996f73f85fd9e"
    assert b["harness_sha256"] == "094f43cb320f8e8e3196049269b20ac22e7e94fa9890b80f27f38ef49f7c82ea"
    assert b["evaluation_epoch"] == "2026-08-16T22:17:32Z"
    assert b["counts"]["cases"] == 420
    assert b["counts"]["clean_positive"] == 60
    assert b["counts"]["hostile"] == 360
    assert b["counts"]["ambiguous"] == 0


def test_v2_config_matches_repaired_panel_and_ablations() -> None:
    cfg = json.loads(CONFIG.read_text())
    assert cfg["schema"] == "P4BaselineConfigs.v2"
    assert len(cfg["panel_baseline_ids"]) == 7
    assert cfg["panel_baseline_ids"][-1] == "deepsciverify-abstract-to-full-escalation"
    assert len(cfg["baselines"]) == 10
    assert len(cfg["ablations"]) == 8
    assert all(row["resource_units"] == 9.0 for row in cfg["ablations"])


def test_v2_workflow_is_protected_and_lifecycle_aware() -> None:
    text = WORKFLOW.read_text()
    assert "CAMPAIGN_TRIGGER_V2.txt" in text
    assert "verification']['verified'] is True" in text
    assert "verification']['reason'] == 'valid'" in text
    assert "git diff --exit-code \"$FREEZE_SHA\"" in text
    assert "run_baselines_v2.py" in text
    assert "evaluate_campaign_v2.py" in text
    assert "independent_reproduce_v2.py" in text
    assert "Download protected V2 gold only after scored jobs complete" in text
    assert "candidate_external_ip_connects" in text
    assert "comparator_external_ip_connects" in text

    if TRIGGER.exists():
        trigger = TRIGGER.read_text()
        assert "outcome_accessed_before_launch=false" in trigger
        assert "freeze_merge=" in trigger
        assert "freeze_exact_main_ci_run=" in trigger
    else:
        b = json.loads(BINDINGS.read_text())
        assert b["campaign_execution_authorized"] is False
