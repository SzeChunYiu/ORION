from orion.benchmarks.formal_engine import (
    FormalEngineStatus,
    assess_formal_engine_readiness,
)


def test_recursive_engine_has_contracts_but_is_not_formally_closed_yet():
    report = assess_formal_engine_readiness()
    assert report.structurally_sound
    assert report.status is FormalEngineStatus.INDEPENDENT_VERIFICATION_OPEN
    assert report.operator_contract_count == 9
    assert all(check.passed for check in report.proof_checks)
    assert report.metrics.open_question_count > 0
    assert report.metrics.ready_mechanic_count < report.metrics.mechanic_count
    assert report.blockers
