from orion.benchmarks.reconstruction import (
    frozen_reconstruction_suite,
    run_hidden_shift_case,
)


def test_recursive_reconstruction_suite_passes_and_blocks_false_reframes():
    reports = tuple(run_hidden_shift_case(case) for case in frozen_reconstruction_suite())
    assert len(reports) == 4
    assert all(report.passed for report in reports)
    by_case = {report.case_id: report for report in reports}
    assert by_case["missing-evidence-only"].metric_dict["unnecessary_reframe"] == 0.0
    assert by_case["execution-bug-only"].metric_dict["unnecessary_reframe"] == 0.0
    assert by_case["hidden-parent-domain"].metric_dict["closure_staled"] == 1.0
    assert by_case["hidden-representation"].metric_dict["closure_staled"] == 1.0
