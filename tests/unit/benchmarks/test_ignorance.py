from orion.benchmarks.ignorance import run_typed_ignorance_known_world


def test_typed_ignorance_routes_distinct_known_unknowns_to_distinct_actions():
    report = run_typed_ignorance_known_world()
    assert report.passed
    metrics = report.metric_dict
    assert metrics["typed_action_accuracy"] == 1.0
    assert metrics["typed_action_accuracy"] > metrics["generic_action_accuracy"]
    assert metrics["retained_independent_source_count"] == 2.0
