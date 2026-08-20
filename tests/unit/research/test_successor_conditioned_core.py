from pathlib import Path
import importlib.util
import json
import sys

MODULE = (
    Path(__file__).resolve().parents[3]
    / "research"
    / "extensions"
    / "meta-orion-recursive-scientific-evolution"
    / "successor_conditioned_core.py"
)
spec = importlib.util.spec_from_file_location("successor_conditioned_core", MODULE)
sc = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = sc
spec.loader.exec_module(sc)


def test_deterministic_pair_generation():
    a = sc.generate_pairs(seed=101, per_family=5)
    b = sc.generate_pairs(seed=101, per_family=5)
    assert sc.candidate_jsonl(a) == sc.candidate_jsonl(b)
    assert sc.protected_jsonl(a) == sc.protected_jsonl(b)


def test_every_pair_is_current_identical_future_identical_gold_different():
    pairs = sc.generate_pairs(seed=103, per_family=4)
    report = sc.nonidentifiability_report(pairs)
    assert report["identical_candidate_input_pairs"] == report["n_pairs"]
    assert report["same_future_transition_pairs"] == report["n_pairs"]
    assert report["different_protected_future_standing_pairs"] == report["n_pairs"]
    assert report["deterministic_current_summary_accuracy_ceiling"] == 0.5


def test_candidate_payload_excludes_lineage_and_future_gold():
    pairs = sc.generate_pairs(seed=107, per_family=3)
    for pair in pairs:
        assert pair.left.candidate_payload() == pair.right.candidate_payload()
        payload = json.dumps(pair.left.candidate_payload(), sort_keys=True)
        assert "history" not in payload
        assert "lineage_kind" not in payload
        assert "protected_future_standing" not in payload
        assert "variant_id" not in payload


def test_current_summary_policy_hits_exact_information_ceiling():
    pairs = sc.generate_pairs(seed=109, per_family=7)
    result = sc.evaluate_current_summary(pairs)
    assert result["accuracy"] == 0.5
    assert all(value == 1 for value in result["per_pair_exact"])


def test_full_history_policy_recovers_all_future_standing():
    pairs = sc.generate_pairs(seed=113, per_family=6)
    result = sc.evaluate_full_history(pairs)
    assert result["accuracy"] == 1.0
    assert result["exact"] == result["n_variants"]


def test_compact_typed_lineage_state_recovers_all_future_standing():
    pairs = sc.generate_pairs(seed=127, per_family=6)
    result = sc.evaluate_typed_state(pairs)
    assert result["accuracy"] == 1.0
    assert result["exact"] == result["n_variants"]


def test_current_answer_and_standing_are_identical_within_pairs():
    pairs = sc.generate_pairs(seed=131, per_family=5)
    for pair in pairs:
        assert pair.left.current.current_answer == pair.right.current.current_answer
        assert pair.left.current.current_standing == pair.right.current.current_standing
        assert pair.left.current.proposition == pair.right.current.proposition
