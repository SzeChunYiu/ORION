import hashlib

import pytest

from orion.self_orion.authority_live import build_live_authority_trial_runner_from_env
from orion.self_orion.authority_trial import AuthorityTrialBinding


def _digest(label: str) -> str:
    return hashlib.sha256(label.encode()).hexdigest()


def _binding():
    return AuthorityTrialBinding(
        subject_revision_hash=_digest("subject"),
        evaluator_artifact_hash=_digest("evaluator"),
        evaluation_epoch_id="epoch:frozen",
        split_id="split:heldout",
        producer_process_lineage_hash=_digest("producer"),
        evaluator_process_lineage_hash=_digest("evaluator-lineage"),
        evaluator_frozen_before_candidate=True,
        fresh_split=True,
    )


def test_live_authority_runner_env_builder_requires_all_protected_services(monkeypatch):
    names = (
        "ORION_AUTHORITY_ATTACK_EXECUTOR_URL",
        "ORION_AUTHORITY_ATTACK_EXECUTOR_TOKEN",
        "ORION_AUTHORITY_ATTACK_EXECUTOR_ARTIFACT_HASH",
        "ORION_AUTHORITY_EVALUATOR_URL",
        "ORION_AUTHORITY_EVALUATOR_TOKEN",
    )
    for name in names:
        monkeypatch.delenv(name, raising=False)
    with pytest.raises(RuntimeError, match="ORION_AUTHORITY_ATTACK_EXECUTOR_URL"):
        build_live_authority_trial_runner_from_env(binding=_binding())


def test_live_authority_runner_env_builder_binds_frozen_evaluator(monkeypatch):
    monkeypatch.setenv(
        "ORION_AUTHORITY_ATTACK_EXECUTOR_URL",
        "https://authority-executor.example.test/v1/execute",
    )
    monkeypatch.setenv("ORION_AUTHORITY_ATTACK_EXECUTOR_TOKEN", "executor-secret")
    monkeypatch.setenv(
        "ORION_AUTHORITY_ATTACK_EXECUTOR_ARTIFACT_HASH", _digest("executor")
    )
    monkeypatch.setenv(
        "ORION_AUTHORITY_EVALUATOR_URL",
        "https://authority-evaluator.example.test/v1/evaluate",
    )
    monkeypatch.setenv("ORION_AUTHORITY_EVALUATOR_TOKEN", "evaluator-secret")

    binding = _binding()
    runner = build_live_authority_trial_runner_from_env(binding=binding)
    assert runner._evaluator.config.evaluator_artifact_hash == binding.evaluator_artifact_hash
    assert runner._evaluator.config.evaluation_epoch_id == binding.evaluation_epoch_id
    assert runner._executor.config.executor_artifact_hash == _digest("executor")
