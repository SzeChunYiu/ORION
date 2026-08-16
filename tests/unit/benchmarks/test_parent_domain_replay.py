from orion.benchmarks.parent_domain_replay import (
    HistoricalCausalVerdict,
    run_parent_domain_replay,
)


def test_parent_domain_replay_recovers_hidden_historical_and_fresh_domains():
    result = run_parent_domain_replay()
    assert result.local_report.passed
    assert result.named_basis_omissions == (
        "computational linguistics",
        "psychometrics",
    )
    assert result.fresh_transfer_accuracy == 1.0
    assert result.rules_out_required_method_basis_change


def test_historical_cause_remains_partially_identified_without_original_trace():
    result = run_parent_domain_replay(original_query_trace_available=False)
    assert result.historical_causal_verdict is HistoricalCausalVerdict.PARTIALLY_IDENTIFIED
    assert result.historical_blockers


def test_trace_claim_fails_closed_until_a_bound_replay_artifact_exists():
    result = run_parent_domain_replay(original_query_trace_available=True)
    assert result.historical_causal_verdict is HistoricalCausalVerdict.CANNOT_CHECK
    assert result.historical_blockers
