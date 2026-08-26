"""Q1-B independently attacks the bounded shared-Tag finite grammar."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LANE = ROOT / "papers/five-paper-top-tier-r8/Q1/q1_b_finite_attack_r9"
sys.path.insert(0, str(LANE))

from q1_b_semantic_evaluator_r9 import evaluate_witness  # noqa: E402
from q1_b_solver_r9 import (  # noqa: E402
    RESOURCE_EXHAUSTED,
    apply_block_permutation,
    apply_coordinate_permutation,
    apply_letter_relabeling,
    broken_two_tag_support_control,
    declared_n3_instances,
    lower_control_instance,
    pauli_product,
    perfect_matchings,
    simple_support_one_instance,
    solve_instance,
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_direct_pauli_grammar_has_no_registered_implementation_dependency() -> None:
    assert pauli_product("XI", "IZ") == "XZ"
    assert pauli_product("XY", "YZ") == "ZX"
    solver_text = (LANE / "q1_b_solver_r9.py").read_text(encoding="utf-8")
    forbidden = (
        "MAX_R6S",
        "MAX_R6O",
        "support_two_checker",
        "witness_generator",
        "orion.study",
    )
    assert not any(name in solver_text for name in forbidden)


def test_smallest_support_three_capable_domain_is_complete_over_matchings() -> None:
    instances = declared_n3_instances()
    target_sets = {tuple(sorted(p for block in i.blocks for p in block)) for i in instances}
    assert len(instances) == 15
    assert len(target_sets) == 1
    assert len(next(iter(target_sets))) == 6
    assert len(set(perfect_matchings(tuple(range(6))))) == 15
    assert all(i.n == 3 for i in instances)


def test_support_one_and_independently_generated_support_two_lower_controls() -> None:
    support_one = solve_instance(simple_support_one_instance(), timeout_ms=30_000)
    assert support_one["terminal"] == "EXACT_OPTIMUM"
    assert support_one["minimum_support_among_optima"] == 1
    assert evaluate_witness(
        simple_support_one_instance(), support_one["witness"]
    )["valid"]

    lower = solve_instance(lower_control_instance(), timeout_ms=30_000)
    assert lower["terminal"] == "EXACT_OPTIMUM"
    assert lower["support_bounded_objectives"] == {"1": 8, "2": 7}
    assert lower["exact_optimum"] == 7
    assert lower["minimum_support_among_optima"] == 2
    assert evaluate_witness(lower_control_instance(), lower["witness"])["valid"]


def test_broken_shared_tag_control_really_requires_support_three() -> None:
    control = broken_two_tag_support_control()
    assert control["scope"] == "OUTSIDE_R6M_BROKEN_SHARED_ONE_TAG"
    assert control["minimum_support"] == 3
    assert control["support_two_feasible"] is False
    assert control["witness"] == "ZZZ"


def test_relabel_coordinate_and_block_orbits_preserve_the_lower_result() -> None:
    base = lower_control_instance()
    variants = (
        apply_letter_relabeling(base, {"I": "I", "X": "Z", "Y": "Y", "Z": "X"}),
        apply_coordinate_permutation(base, (1, 0)),
        apply_block_permutation(base, (2, 0, 1)),
    )
    for variant in variants:
        result = solve_instance(variant, timeout_ms=30_000)
        assert result["terminal"] == "EXACT_OPTIMUM"
        assert result["support_bounded_objectives"] == {"1": 8, "2": 7}
        assert result["minimum_support_among_optima"] == 2


def test_resource_exhaustion_is_preserved_not_coerced_to_a_result() -> None:
    result = solve_instance(declared_n3_instances()[0], timeout_ms=1)
    assert result["terminal"] == RESOURCE_EXHAUSTED
    assert result["exact_optimum"] is None
    assert result["witness"] is None


def test_committed_receipt_retains_bounded_terminal_and_authority_ceiling() -> None:
    receipt = json.loads((LANE / "Q1_B_FINITE_ATTACK_RECEIPT_R9.json").read_text())
    assert receipt["terminal"] == "NO_SUPPORT3_COUNTEREXAMPLE_IN_DECLARED_FINITE_DOMAIN"
    assert receipt["typed_terminal"] == (
        "Q1_B_NO_SUPPORT3_COUNTEREXAMPLE_IN_DECLARED_FINITE_DOMAIN__"
        "BOUNDED_CORROBORATION_ONLY"
    )
    assert receipt["results"]["instances_checked"] == 15
    assert receipt["results"]["support_three_counterexamples"] == []
    assert receipt["results"]["semantic_evaluator_disagreements"] == []
    assert receipt["results"]["solver_disagreements"] == []
    assert receipt["results"]["symmetry_leakage_cases"] == []
    assert receipt["authority"]["same_program_independence"] == "CANNOT_CHECK"
    assert receipt["authority"]["journal_authority"] == "CANNOT_CHECK"
    assert receipt["authority"]["finite_domain_only"] is True
    assert receipt["authority"]["proves_all_size_theorem"] is False


def test_receipt_manifests_and_every_stored_witness_are_machine_checkable() -> None:
    receipt = json.loads((LANE / "Q1_B_FINITE_ATTACK_RECEIPT_R9.json").read_text())
    for key, name in {
        "source_manifest_sha256": "Q1_B_SOURCE_MANIFEST_R9.json",
        "result_manifest_sha256": "Q1_B_RESULT_MANIFEST_R9.json",
        "environment_manifest_sha256": "Q1_B_ENVIRONMENT_MANIFEST_R9.json",
        "negative_control_manifest_sha256": "Q1_B_NEGATIVE_CONTROL_MANIFEST_R9.json",
    }.items():
        assert receipt["manifests"][key] == _sha(LANE / name)

    result = json.loads((LANE / "Q1_B_RESULT_R9.json").read_text())
    by_id = {instance.instance_id: instance for instance in declared_n3_instances()}
    assert set(by_id) == {row["instance_id"] for row in result["instances"]}
    for row in result["instances"]:
        evaluation = evaluate_witness(by_id[row["instance_id"]], row["witness"])
        assert evaluation["valid"], evaluation
        assert evaluation["objective"] == row["exact_optimum"]
        assert row["minimum_support_among_optima"] <= 2

