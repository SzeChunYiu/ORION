from pathlib import Path
import importlib.util
import sys

MODULE = (
    Path(__file__).resolve().parents[3]
    / "research"
    / "extensions"
    / "meta-orion-recursive-scientific-evolution"
    / "successor_debt_core.py"
)
spec = importlib.util.spec_from_file_location("successor_debt_core", MODULE)
debt = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = debt
spec.loader.exec_module(debt)


def test_current_summary_has_perfect_d2_but_delayed_d4_errors():
    pairs = debt.sc.generate_pairs(seed=211, per_family=6)
    result = debt.evaluate_d4(pairs, debt.current_summary_predictor)
    assert result["d2_current_answer_correct"] == result["n_variants"]
    assert result["d4_accuracy"] == 0.5
    assert all(value == 1 for value in result["per_pair_exact"])
    assert result["d4_invalid_commit_count"] > 0
    assert result["d4_missed_opportunity_count"] > 0
    assert result["d4_authority_violation_count"] > 0
    assert not result["recursive_scientific_integrity_gate"]


def test_full_history_avoids_all_delayed_d4_errors():
    pairs = debt.sc.generate_pairs(seed=223, per_family=7)
    result = debt.evaluate_d4(pairs, debt.full_history_predictor)
    assert result["d2_current_answer_correct"] == result["n_variants"]
    assert result["d4_accuracy"] == 1.0
    assert result["d4_invalid_commit_count"] == 0
    assert result["d4_missed_opportunity_count"] == 0
    assert result["d4_authority_violation_count"] == 0
    assert result["recursive_scientific_integrity_gate"]


def test_compact_typed_state_avoids_all_delayed_d4_errors():
    pairs = debt.sc.generate_pairs(seed=227, per_family=7)
    result = debt.evaluate_d4(pairs, debt.typed_state_predictor)
    assert result["d4_accuracy"] == 1.0
    assert result["d4_invalid_commit_count"] == 0
    assert result["d4_missed_opportunity_count"] == 0
    assert result["d4_authority_violation_count"] == 0
    assert result["recursive_scientific_integrity_gate"]


def test_protected_successor_action_is_family_specific():
    pairs = debt.sc.generate_pairs(seed=229, per_family=2)
    actions = set()
    for pair in pairs:
        for variant in pair.variants():
            actions.add(debt.protected_successor_action(pair, variant))
    assert debt.SuccessorAction.COMMIT in actions
    assert debt.SuccessorAction.REVALIDATE_EVIDENCE in actions
    assert debt.SuccessorAction.RETRY_ROUTE in actions
    assert debt.SuccessorAction.KEEP_BLOCKED in actions
    assert debt.SuccessorAction.REAUTHORIZE_EXTERNALLY in actions


def test_same_current_answer_does_not_compensate_invalid_d4_commit():
    pairs = debt.sc.generate_pairs(seed=233, per_family=3)
    result = debt.evaluate_d4(pairs, debt.current_summary_predictor)
    assert result["d2_current_answer_correct"] == result["n_variants"]
    assert result["d4_invalid_commit_count"] > 0
    assert not result["recursive_scientific_integrity_gate"]
