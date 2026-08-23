from pathlib import Path
import importlib.util
import json
import sys

MODULE = (
    Path(__file__).resolve().parents[3]
    / "research"
    / "extensions"
    / "meta-orion-recursive-scientific-evolution"
    / "rssi_exact_core.py"
)
spec = importlib.util.spec_from_file_location("rssi_exact_core", MODULE)
rssi = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = rssi
spec.loader.exec_module(rssi)


def test_deterministic_generation():
    a = rssi.generate_pilot(seed=7, per_family=5)
    b = rssi.generate_pilot(seed=7, per_family=5)
    assert rssi.public_jsonl(a) == rssi.public_jsonl(b)
    assert rssi.gold_jsonl(a) == rssi.gold_jsonl(b)


def test_public_payload_has_no_family_or_gold():
    cases = rssi.generate_pilot(seed=9, per_family=2)
    for case in cases:
        payload = case.public.payload()
        assert "family_id" not in payload
        text = json.dumps(payload)
        assert "correct_task_answer" not in text
        assert "affected_object_ids" not in text


def test_rule_policy_perfect_on_pilot():
    cases = rssi.generate_pilot(seed=11, per_family=6)
    result = rssi.evaluate(cases, rssi.rule_policy)
    assert result["all_gates_pass"]
    assert result["migration_exact"] == result["n"]
    assert result["invalid_promotions"] == 0


def test_hostile_policies_fail():
    cases = rssi.generate_pilot(seed=13, per_family=5)
    assert not rssi.evaluate(cases, rssi.always_preserve)["all_gates_pass"]
    assert not rssi.evaluate(cases, rssi.always_reopen)["all_gates_pass"]
    assert not rssi.evaluate(cases, rssi.answer_only)["all_gates_pass"]


def test_same_answer_can_have_different_scientific_standing():
    cases = rssi.generate_pilot(seed=17, per_family=3)
    pair = [c for c in cases if c.public.task_answer == "SAME"]
    assert pair
    outputs = [
        (c.gold.correct_task_answer, c.gold.migrations[0].to_standing.value)
        for c in pair
    ]
    assert {answer for answer, _ in outputs} == {"SAME"}
    assert {standing for _, standing in outputs} == {"AUTHORIZED", "REOPENED"}


def test_donor_union_closes_current_pilot():
    cases = rssi.generate_pilot(seed=19, per_family=7)
    result = rssi.evaluate(cases, rssi.donor_union_policy)
    assert result["all_gates_pass"]
    assert result["migration_exact"] == result["n"]


def test_individual_parents_do_not_solve_all_families():
    cases = rssi.generate_pilot(seed=23, per_family=5)
    assert not rssi.evaluate(cases, rssi.semantic_change_parent)["all_gates_pass"]
    assert not rssi.evaluate(cases, rssi.negative_applicability_parent)["all_gates_pass"]
    assert not rssi.evaluate(cases, rssi.authority_drift_parent)["all_gates_pass"]


def test_naive_donor_union_fails_interaction_pilot():
    cases = rssi.generate_interaction_pilot(seed=29, per_family=5)
    result = rssi.evaluate(cases, rssi.donor_union_policy)
    assert not result["all_gates_pass"]
    assert result["task_correct"] == result["n"]
    assert result["migration_exact"] < result["n"]


def test_coordinated_interaction_policy_passes_interaction_pilot():
    cases = rssi.generate_interaction_pilot(seed=31, per_family=6)
    result = rssi.evaluate(cases, rssi.interaction_policy)
    assert result["all_gates_pass"]
    assert result["migration_exact"] == result["n"]
