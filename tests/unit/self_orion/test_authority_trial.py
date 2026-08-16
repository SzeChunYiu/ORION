import hashlib

from orion.self_orion.authority_trial import (
    AuthorityAttackEvaluationStatus,
    AuthorityAttackExecution,
    AuthorityTrialBinding,
    AuthorityTrialRunner,
    ProtectedAuthorityEvaluation,
)


def _digest(label: str) -> str:
    return hashlib.sha256(label.encode()).hexdigest()


class _Executor:
    def __init__(self, *, authority_increased: bool = False):
        self.authority_increased = authority_increased

    def execute(self, attack, *, binding):
        return AuthorityAttackExecution(
            attack_id=attack.attack_id,
            subject_revision_hash=binding.subject_revision_hash,
            artifact_id=f"execution:{attack.attack_id}",
            artifact_hash=_digest(f"execution:{attack.attack_id}"),
            resource_units=1.0,
            observed_authority_outcome=attack.expected_outcome.value,
            candidate_authority_increased=self.authority_increased,
            note="host execution fixture",
        )


class _Evaluator:
    def __init__(self, *, false_promotion: bool = False):
        self.false_promotion = false_promotion

    def evaluate(self, attack, execution, *, binding):
        return ProtectedAuthorityEvaluation(
            attack_id=attack.attack_id,
            execution_artifact_hash=execution.artifact_hash,
            evaluator_artifact_hash=binding.evaluator_artifact_hash,
            evaluation_epoch_id=binding.evaluation_epoch_id,
            status=AuthorityAttackEvaluationStatus.PASS,
            expected_outcome_observed=True,
            false_promotion_observed=self.false_promotion,
            tamper_or_leakage_detected=attack.attack_id.endswith(("MODIFICATION", "LEAKAGE")),
            evidence_ids=(f"evidence:{attack.attack_id}",),
            note="protected evaluator fixture",
        )


def _binding(*, independent: bool = True):
    producer = _digest("producer")
    evaluator_lineage = _digest("evaluator-lineage") if independent else producer
    return AuthorityTrialBinding(
        subject_revision_hash=_digest("subject"),
        evaluator_artifact_hash=_digest("evaluator"),
        evaluation_epoch_id="epoch:frozen",
        split_id="split:heldout",
        producer_process_lineage_hash=producer,
        evaluator_process_lineage_hash=evaluator_lineage,
        evaluator_frozen_before_candidate=True,
        fresh_split=True,
    )


def test_hostile_authority_runner_executes_exact_frozen_battery_and_never_promotes():
    report = AuthorityTrialRunner(executor=_Executor(), evaluator=_Evaluator()).run(_binding())

    assert report.all_attacks_executed
    assert len(report.results) == 10
    assert report.all_pass
    assert report.correct_cannot_check_passed
    assert report.false_promotion_count == 0
    assert len(report.artifact_hash) == 64
    assert not report.grants_phase2_closure
    assert not report.grants_governed_self_orion


def test_authority_trial_rejects_self_evaluation_even_when_each_attack_says_pass():
    report = AuthorityTrialRunner(executor=_Executor(), evaluator=_Evaluator()).run(
        _binding(independent=False)
    )
    assert not report.all_pass
    assert "authority_trial_self_evaluated" in report.blockers


def test_authority_trial_surfaces_candidate_authority_increase_and_false_promotion():
    report = AuthorityTrialRunner(
        executor=_Executor(authority_increased=True),
        evaluator=_Evaluator(false_promotion=True),
    ).run(_binding())
    assert not report.all_pass
    assert report.false_promotion_count == 10
    assert any("candidate_authority_increased_during_attack" in item for item in report.blockers)
    assert any("false_authority_promotion_observed" in item for item in report.blockers)
