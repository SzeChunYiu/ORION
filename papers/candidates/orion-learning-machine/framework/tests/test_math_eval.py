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
