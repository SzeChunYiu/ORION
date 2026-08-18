import json
from pathlib import Path


def _load(name: str):
    path = Path("research/extensions/p9-structured-neural") / name
    return json.loads(path.read_text())


def test_m0_protocol_preserves_failed_v0_and_freezes_pre_execution_amendment():
    original = _load("M0_TASK_HARNESS_PROTOCOL_V0.json")
    amended = _load("M0_TASK_HARNESS_PROTOCOL_V0_1.json")

    assert original["protocol_status"] == "DESIGN_FROZEN"
    assert original["outcome_accessed"] is False
    assert amended["protocol_status"] == "DESIGN_FROZEN_AMENDMENT"
    assert amended["supersedes_for_execution"] == original["schema"]
    assert amended["outcome_accessed"] is False
    assert amended["candidate_order"]["hidden_semantic_order_side_channel_forbidden"] is True
    assert "selected model-visible view fingerprint" in amended["candidate_order"]["frozen_rule"]


def test_m0_protocol_freezes_exact_corpus_and_non_authorizing_terminal():
    amended = _load("M0_TASK_HARNESS_PROTOCOL_V0_1.json")

    assert amended["corpus"] == {
        "seed": "p9-m0-task-harness-v0",
        "train_pairs_per_family": 32,
        "dev_pairs_per_family": 8,
        "test_pairs_per_family": 16,
    }
    assert amended["authority"] == {
        "scientific_authority": False,
        "novelty_authority": False,
        "paper_readiness_authority": False,
        "model_promotion_authority": False,
    }
    assert amended["terminal"] == "M0_TASK_HARNESS_VALIDATED_ONLY"
