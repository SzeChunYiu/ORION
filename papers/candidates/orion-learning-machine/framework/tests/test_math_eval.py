import pytest
from orion_learning_machine import *


def _fixture():
    t=FrozenMathTask('T1','theorem T : True := by trivial','bench','abc123','solved')
    a=MathAttempt('T1',t.statement_sha256,'orion-p10','by trivial')
    r=VerifierReceipt('T1',t.statement_sha256,a.attempt_sha256,'lean-kernel','4.25.0',Verdict.SUCCESS)
    return t,a,r


def test_exact_verifier_receipt_binding():
    t,a,r=_fixture(); b=bind_verifier_receipt(t,a,r)
    assert b.verified_success


def test_receipt_replay_or_attempt_tamper_rejected():
    t,a,r=_fixture()
    changed=MathAttempt('T1',t.statement_sha256,'orion-p10','by simp')
    with pytest.raises(ValueError): bind_verifier_receipt(t,changed,r)


def test_statement_misbinding_rejected():
    t,a,r=_fixture()
    other=FrozenMathTask('T1','theorem T : False := by sorry','bench','abc123','solved')
    with pytest.raises(ValueError): bind_verifier_receipt(other,a,r)


def test_cannot_check_never_counts_as_verified_success():
    t,a,r=_fixture()
    r2=VerifierReceipt('T1',t.statement_sha256,a.attempt_sha256,'lean-kernel','4.25.0',Verdict.CANNOT_CHECK)
    assert not bind_verifier_receipt(t,a,r2).verified_success


def _native_fixture(source_revision: str = "abc123"):
    environment = MathEvaluationEnvironment(
        repository="https://github.com/leanprover-community/mathlib4",
        source_revision=source_revision,
        lean_toolchain="leanprover/lean4:v4.34.0-rc1",
        dependency_manifest_sha256="1" * 64,
        source_path="Mathlib/Algebra/Group/Basic.lean",
        source_sha256="2" * 64,
        branch="master",
    )
    task = FrozenMathTask(
        "T-native",
        "theorem T : True := by trivial",
        "mathlib4",
        source_revision,
        "solved",
        environment=environment,
    )
    attempt = MathAttempt(
        "T-native",
        task.statement_sha256,
        "orion-p10",
        "by trivial",
        environment_sha256=environment.environment_sha256,
    )
    receipt = VerifierReceipt(
        "T-native",
        task.statement_sha256,
        attempt.attempt_sha256,
        "lean-kernel",
        "4.34.0-rc1",
        Verdict.SUCCESS,
        environment_sha256=environment.environment_sha256,
    )
    return task, attempt, receipt


def test_source_revision_substitution_invalidates_native_subject():
    task, attempt, receipt = _native_fixture()
    substituted_task, _, _ = _native_fixture("different-revision")
    with pytest.raises(ValueError):
        bind_verifier_receipt(substituted_task, attempt, receipt)


def test_unbound_task_id_control_silently_reuses_a_stale_result():
    """Minimal conventional control: a task-id-only result cannot see drift."""

    task, _, _ = _native_fixture()
    substituted_task, _, _ = _native_fixture("different-revision")
    unbound_results = {task.task_id: {"verdict": "SUCCESS"}}
    assert unbound_results[substituted_task.task_id]["verdict"] == "SUCCESS"
    assert substituted_task.statement_sha256 != task.statement_sha256


def test_source_byte_substitution_invalidates_native_subject():
    task, attempt, receipt = _native_fixture()
    substituted_environment = MathEvaluationEnvironment(
        repository=task.environment.repository,
        source_revision=task.environment.source_revision,
        lean_toolchain=task.environment.lean_toolchain,
        dependency_manifest_sha256=task.environment.dependency_manifest_sha256,
        source_path=task.environment.source_path,
        source_sha256="3" * 64,
        branch=task.environment.branch,
    )
    substituted_task = FrozenMathTask(
        task.task_id,
        task.statement,
        task.source,
        task.source_revision,
        task.status_at_freeze,
        environment=substituted_environment,
    )
    with pytest.raises(ValueError):
        bind_verifier_receipt(substituted_task, attempt, receipt)


def test_native_rejection_cannot_be_recorded_as_success():
    assert verdict_from_native_exit(0) == Verdict.SUCCESS
    assert verdict_from_native_exit(1) == Verdict.FAIL
    assert verdict_from_native_exit(137) == Verdict.FAIL
