from __future__ import annotations

import json
from pathlib import Path

from orion.study.p9.m1_runtime import run_m1


PROTOCOL = Path("research/extensions/p9-structured-neural/M1_PROTOCOL_V1_2.json")
AMENDMENT = Path("research/extensions/p9-structured-neural/M1_PROTOCOL_V1_3_AMENDMENT.json")


def test_m1_v12_protocol_is_pre_outcome_and_v13_is_runtime_only():
    protocol = json.loads(PROTOCOL.read_text())
    amendment = json.loads(AMENDMENT.read_text())
    assert protocol["schema"] == "P9.M1Protocol.v1.2"
    assert protocol["outcome_accessed"] is False
    assert protocol["supersedes_for_execution"] == "P9.M1Protocol.v1.1"
    assert "task-specific ceiling" in protocol["terminal_rule_addition"]

    assert amendment["schema"] == "P9.M1ProtocolAmendment.v1.3"
    assert amendment["supersedes_execution_protocol"] == "P9.M1Protocol.v1.2"
    assert amendment["outcome_accessed"] is False
    assert amendment["execution_protocol"] == "P9.M1Protocol.v1.3"
    assert amendment["amendment"]["feature_semantics_changed"] is False
    assert amendment["amendment"]["corpus_or_split_changed"] is False
    assert amendment["amendment"]["model_grid_changed"] is False
    assert amendment["amendment"]["selection_rule_changed"] is False
    assert amendment["amendment"]["protected_test_rule_changed"] is False


def test_m1_v12_corrections_reexecute_under_superseding_v13_runtime():
    result = run_m1(
        corpus_seed="p9-m1-v12-smoke",
        train_pairs_per_family=8,
        dev_pairs_per_family=3,
        test_pairs_per_family=4,
        train_size_pairs_per_family=(2, 4, 8),
        train_order_seed="v12-train",
        dev_order_seed="v12-dev",
        test_order_seed="v12-test",
        alternate_test_order_seed="v12-test-alt",
        subject_sha="smoke",
    )
    assert result["protocol"] == "P9.M1Protocol.v1.3"
    for view in result["views"].values():
        assert "ceiling_violation_any_task" in view["test_overall"]
        for task in view["tasks"].values():
            sentinel = task["test_row_permutation_invariance"]
            assert sentinel["method"] == "REEXECUTED_REVERSED_TEST_BATCH"
            assert sentinel["invariant"] is True
            assert "exact_view_deterministic_accuracy_ceiling" in task["test"]
            assert "ceiling_violation" in task["test"]
