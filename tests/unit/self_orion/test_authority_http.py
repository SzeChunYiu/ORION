import hashlib
import json

import pytest

from orion.self_orion.authority_http import (
    ProtectedAuthorityEvaluatorHTTPConfig,
    ProtectedAuthorityExecutorHTTPConfig,
    ProtectedAuthorityHTTPEvaluator,
    ProtectedAuthorityHTTPExecutor,
)
from orion.self_orion.authority_trial import (
    AuthorityAttackEvaluationStatus,
    AuthorityTrialBinding,
    FROZEN_AUTHORITY_ATTACKS,
)


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


def test_remote_authority_executor_binds_frozen_attack_subject_and_executor_artifact():
    attack = FROZEN_AUTHORITY_ATTACKS[0]
    binding = _binding()
    artifact_hash = _digest("execution")

    def transport(request, timeout):
        payload = json.loads(request.data)
        return json.dumps(
            {
                "request_hash": payload["request_hash"],
                "executor_artifact_hash": _digest("executor"),
                "attack_id": attack.attack_id,
                "subject_revision_hash": binding.subject_revision_hash,
                "artifact_id": "artifact:execution",
                "artifact_hash": artifact_hash,
                "resource_units": 2.0,
                "observed_authority_outcome": attack.expected_outcome.value,
                "candidate_authority_increased": False,
                "note": "executed against protected subject",
            }
        ).encode()

    config = ProtectedAuthorityExecutorHTTPConfig(
        endpoint="https://authority-executor.example.test/v1/execute",
        bearer_token="executor-secret",
        executor_artifact_hash=_digest("executor"),
    )
    execution = ProtectedAuthorityHTTPExecutor(config, transport=transport).execute(
        attack, binding=binding
    )
    assert execution.attack_id == attack.attack_id
    assert execution.artifact_hash == artifact_hash
    assert not execution.candidate_authority_increased
    assert "executor-secret" not in repr(config)


def test_remote_authority_evaluator_binds_execution_and_frozen_evaluator():
    attack = FROZEN_AUTHORITY_ATTACKS[-1]
    binding = _binding()
    execution = ProtectedAuthorityHTTPExecutor(
        ProtectedAuthorityExecutorHTTPConfig(
            endpoint="https://authority-executor.example.test/v1/execute",
            bearer_token="executor-secret",
            executor_artifact_hash=_digest("executor"),
        ),
        transport=lambda request, timeout: json.dumps(
            {
                "request_hash": json.loads(request.data)["request_hash"],
                "executor_artifact_hash": _digest("executor"),
                "attack_id": attack.attack_id,
                "subject_revision_hash": binding.subject_revision_hash,
                "artifact_id": "artifact:a10",
                "artifact_hash": _digest("a10-execution"),
                "resource_units": 1.0,
                "observed_authority_outcome": "CANNOT_CHECK",
                "candidate_authority_increased": False,
                "note": "insufficient evidence case",
            }
        ).encode(),
    ).execute(attack, binding=binding)

    def evaluator_transport(request, timeout):
        payload = json.loads(request.data)
        return json.dumps(
            {
                "request_hash": payload["request_hash"],
                "attack_id": attack.attack_id,
                "execution_artifact_hash": execution.artifact_hash,
                "evaluator_artifact_hash": binding.evaluator_artifact_hash,
                "evaluation_epoch_id": binding.evaluation_epoch_id,
                "status": "PASS",
                "expected_outcome_observed": True,
                "false_promotion_observed": False,
                "tamper_or_leakage_detected": False,
                "evidence_ids": ["evidence:a10:protected"],
                "note": "correct CANNOT_CHECK verified",
            }
        ).encode()

    config = ProtectedAuthorityEvaluatorHTTPConfig(
        endpoint="https://authority-evaluator.example.test/v1/evaluate",
        bearer_token="evaluator-secret",
        evaluator_artifact_hash=binding.evaluator_artifact_hash,
        evaluation_epoch_id=binding.evaluation_epoch_id,
    )
    evaluation = ProtectedAuthorityHTTPEvaluator(
        config, transport=evaluator_transport
    ).evaluate(attack, execution, binding=binding)
    assert evaluation.status is AuthorityAttackEvaluationStatus.PASS
    assert evaluation.expected_outcome_observed
    assert not evaluation.false_promotion_observed
    assert "evaluator-secret" not in repr(config)


def test_remote_authority_services_reject_binding_mismatch():
    attack = FROZEN_AUTHORITY_ATTACKS[0]
    binding = _binding()
    executor = ProtectedAuthorityHTTPExecutor(
        ProtectedAuthorityExecutorHTTPConfig(
            endpoint="https://authority-executor.example.test/v1/execute",
            bearer_token="secret",
            executor_artifact_hash=_digest("executor"),
        ),
        transport=lambda request, timeout: json.dumps(
            {
                "request_hash": "0" * 64,
                "executor_artifact_hash": _digest("executor"),
                "attack_id": attack.attack_id,
                "subject_revision_hash": binding.subject_revision_hash,
                "artifact_id": "artifact:x",
                "artifact_hash": _digest("x"),
                "resource_units": 0.0,
                "observed_authority_outcome": "REJECT",
                "candidate_authority_increased": False,
                "note": "replayed response",
            }
        ).encode(),
    )
    with pytest.raises(RuntimeError, match="request binding mismatch"):
        executor.execute(attack, binding=binding)

    wrong_evaluator = ProtectedAuthorityHTTPEvaluator(
        ProtectedAuthorityEvaluatorHTTPConfig(
            endpoint="https://authority-evaluator.example.test/v1/evaluate",
            bearer_token="secret",
            evaluator_artifact_hash=_digest("different-evaluator"),
            evaluation_epoch_id=binding.evaluation_epoch_id,
        )
    )
    with pytest.raises(ValueError, match="does not match trial binding"):
        wrong_evaluator.evaluate(
            attack,
            type("Execution", (), {"artifact_hash": _digest("execution")})(),
            binding=binding,
        )
