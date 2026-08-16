from orion.benchmarks.flagship import current_flagship_evidence_state
from orion.benchmarks.result import BenchmarkStatus


def test_all_local_flagship_falsifiers_pass_but_external_claims_remain_open():
    state = current_flagship_evidence_state()
    assert state.local_all_pass
    assert not state.publication_ready
    assert set(state.cannot_check_papers) == {"P1", "P2", "P3", "P4", "P5"}
    assert all(
        report.status is BenchmarkStatus.CANNOT_CHECK
        for report in state.external_reports
    )
