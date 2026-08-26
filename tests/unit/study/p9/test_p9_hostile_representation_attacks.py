"""P9's representation-length and format-prior attacks, run against D1 (P9-U-T4).

Every number pinned below either comes from the frozen D1 v1.2 dataset builders
in :mod:`orion.study.p9.d1`, or from the result artifact this lane produced at
``papers/orion-19-structured-epistemic-learning/evidence/
P9_U_T4_HOSTILE_ATTACK_RESULT_2026-08-21.json``. The dataset-digest assertion is
the fidelity anchor: a failure here is about P9, not about a local fixture.

The component-level tests drive each verdict function to all three of its
values on synthetic arm runs, because a component that has only ever returned
one value is not known to be able to return the others.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from orion.programme.records import Outcome
from orion.study.p9 import hostile_representation_attacks as attacks
from orion.study.p9.d1 import D1View

REPO_ROOT = Path(__file__).resolve().parents[4]

RESULT_PATH = (
    REPO_ROOT
    / "papers/orion-19-structured-epistemic-learning/evidence/"
    "P9_U_T4_HOSTILE_ATTACK_RESULT_2026-08-21.json"
)


@pytest.fixture(scope="module")
def datasets() -> dict:
    return attacks.build_datasets()


@pytest.fixture(scope="module")
def result() -> dict:
    return json.loads(RESULT_PATH.read_text(encoding="utf-8"))


def _arm(
    arm_id: str,
    predictions: tuple[str, ...],
    gold: tuple[str, ...],
    *,
    test_features: tuple[tuple[tuple[str, object], ...], ...] | None = None,
    train_features: tuple[tuple[tuple[str, object], ...], ...] = (),
    dev_features: tuple[tuple[tuple[str, object], ...], ...] = (),
) -> attacks.ArmRun:
    if test_features is None:
        test_features = tuple((("f", index),) for index in range(len(predictions)))
    return attacks.ArmRun(
        dataset=attacks.DATASET_BASE,
        arm_id=arm_id,
        config_id="logistic-C1",
        dev_accuracy=1.0,
        predictions=predictions,
        gold=gold,
        train_features=train_features,
        dev_features=dev_features,
        test_features=test_features,
    )


# ---------------------------------------------------------------------------
# Freeze
# ---------------------------------------------------------------------------


def test_the_runner_digest_matches_the_frozen_twin():
    twin = json.loads((REPO_ROOT / attacks.FREEZE_TWIN).read_text(encoding="utf-8"))
    assert twin["parameters_sha256"] == attacks.frozen_digest()
    assert twin["parameters"] == attacks.FROZEN_PARAMETERS
    assert twin["outcome_accessed"] is False
    attacks.verify_against_twin(REPO_ROOT)


def test_the_runner_refuses_to_execute_when_its_constants_have_drifted(tmp_path):
    twin_path = tmp_path / attacks.FREEZE_TWIN
    twin_path.parent.mkdir(parents=True, exist_ok=True)
    twin_path.write_text(json.dumps({"parameters_sha256": "sha256:" + "0" * 64}), encoding="utf-8")
    with pytest.raises(attacks.FreezeViolation):
        attacks.verify_against_twin(tmp_path)


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


def test_the_attacks_run_against_the_dataset_p9_shipped(datasets):
    base = datasets[attacks.DATASET_BASE]
    assert base.manifest_digest == attacks.SHIPPED_DATASET_MANIFEST_DIGEST
    assert (len(base.train), len(base.dev), len(base.test)) == (288, 96, 128)


def test_every_construction_precondition_holds_with_a_real_denominator(datasets):
    checks = attacks.check_preconditions(datasets)
    assert all(item["passed"] for item in checks.values())
    assert checks["PC-2_GOLD_PRESERVATION"]["rows"] == [
        {"variant": "EQUAL_LENGTH", "instances_compared": 512, "labels_changed": 0},
        {"variant": "SEMANTIC_ORBIT", "instances_compared": 512, "labels_changed": 0},
        {"variant": "ORDER_PERMUTATION", "instances_compared": 512, "labels_changed": 0},
    ]
    assert checks["PC-3_CARDINALITY_MATCH"]["corrupted_instances"] == 192
    assert checks["PC-3_CARDINALITY_MATCH"]["coordinate_side_comparisons"] == 1536
    assert checks["PC-3_CARDINALITY_MATCH"]["cardinality_or_presence_mismatches"] == 0
    assert checks["PC-4_ORBIT_BIJECTIVITY"]["atoms"] == 220
    assert checks["PC-4_ORBIT_BIJECTIVITY"]["distinct_images"] == 220
    assert checks["PC-6_LABEL_VARIETY"]["distinct_gold_labels"] == [
        "ALIGNED",
        "OBSTRUCTION",
        "UNRESOLVED",
    ]


def test_the_equal_length_control_replaces_rather_than_appends(datasets):
    base = datasets[attacks.DATASET_BASE]
    control = datasets[attacks.DATASET_EQUAL_LENGTH]
    compared = 0
    for original, controlled in zip(base.test, control.test, strict=True):
        if "preconditions" not in original.mutation_coordinates:
            continue
        compared += 1
        assert len(original.right.preconditions) == len(original.left.preconditions) + 1
        assert len(controlled.right.preconditions) == len(controlled.left.preconditions)
        assert controlled.right.preconditions != controlled.left.preconditions
    assert compared > 0


def test_the_order_remint_is_destroyed_by_the_p1_constructor_so_it_has_no_denominator(datasets):
    """The order-remint control named in the ledger unblock is vacuous on D1.

    ``build_method_realization`` passes every sequence coordinate through
    ``tuple(sorted(set(...)))``, so a permutation never reaches an arm. This is
    the fact the freeze declared in advance; it is measured here rather than
    assumed, and it is why FP-3 reports ``CANNOT_CHECK`` and not "the attack
    failed".
    """

    base = datasets[attacks.DATASET_BASE]
    permuted = datasets[attacks.DATASET_ORDER]
    assert permuted.manifest_digest == base.manifest_digest
    changed = sum(
        1
        for original, rotated in zip(base.test, permuted.test, strict=True)
        if original.model_payload(D1View.TYPED) != rotated.model_payload(D1View.TYPED)
    )
    assert changed == 0


def test_the_semantic_orbit_cannot_reach_the_typed_arm_but_does_reach_the_serialized_arm(datasets):
    base = datasets[attacks.DATASET_BASE]
    orbit = datasets[attacks.DATASET_ORBIT]
    typed_changed = sum(
        1
        for original, reminted in zip(base.test, orbit.test, strict=True)
        if attacks.FEATURE_FUNCTIONS[attacks.ARM_TYPED](original)
        != attacks.FEATURE_FUNCTIONS[attacks.ARM_TYPED](reminted)
    )
    serialized_changed = sum(
        1
        for original, reminted in zip(base.test, orbit.test, strict=True)
        if attacks.FEATURE_FUNCTIONS[attacks.ARM_SERIALIZED](original)
        != attacks.FEATURE_FUNCTIONS[attacks.ARM_SERIALIZED](reminted)
    )
    assert typed_changed == 0
    assert serialized_changed == 128


# ---------------------------------------------------------------------------
# Serialization gates
# ---------------------------------------------------------------------------


def test_the_serialized_view_really_does_carry_the_typed_information(datasets):
    base = datasets[attacks.DATASET_BASE]
    for instance in base.test[:8]:
        tokens = attacks.serialized_tokens(instance)
        assert attacks.decode_typed_serialization(tokens) == instance.model_payload(D1View.TYPED)


def test_a_damaged_token_stream_does_not_decode_to_the_typed_payload(datasets):
    instance = datasets[attacks.DATASET_BASE].test[0]
    tokens = list(attacks.serialized_tokens(instance))
    index = next(
        position
        for position, token in enumerate(tokens)
        if token.startswith("root.left.preconditions[]=")
    )
    tokens[index] = "root.left.preconditions[]=tampered"
    assert attacks.decode_typed_serialization(tokens) != instance.model_payload(D1View.TYPED)


def test_the_reversible_index_removes_every_raw_value_and_restores_it(datasets):
    instance = datasets[attacks.DATASET_BASE].test[0]
    tokens = attacks.serialized_tokens(instance)
    indexed, table = attacks.index_serialization(tokens)
    assert table
    assert attacks.restore_serialization(indexed, table) == tokens
    assert not (set(attacks.string_atoms(tokens)) & set(attacks.string_atoms(indexed)))


def test_the_path_only_reformat_erases_values_but_keeps_cardinality(datasets):
    instance = datasets[attacks.DATASET_BASE].test[0]
    tokens = attacks.serialized_tokens(instance)
    erased = attacks.pathonly_serialization(tokens)
    assert len(erased) == len(tokens)
    assert all(
        token.endswith(f"={attacks.STRING_MARKER}")
        or attacks.LEN_MARKER[:-1] in token
        or token.endswith(f"={attacks.NONE_MARKER}")
        or attacks.split_token(token)[1].lstrip("-").isdigit()
        for token in erased
    )
    assert any(attacks.LEN_MARKER in token for token in erased)


# ---------------------------------------------------------------------------
# Arms
# ---------------------------------------------------------------------------


def test_the_length_only_arm_carries_no_value_identity_and_no_comparison(datasets):
    instance = datasets[attacks.DATASET_BASE].test[0]
    row = attacks.length_only_features(instance)
    assert row
    assert all(
        key.endswith("_present") or key.endswith("_length") for key in row
    ), sorted(row)
    assert not any("equal" in key or "unknown" in key or "same" in key for key in row)


def test_the_length_relational_arm_carries_no_absolute_length(datasets):
    instance = datasets[attacks.DATASET_BASE].test[0]
    row = attacks.length_relational_features(instance)
    assert row
    assert all(
        key.endswith(":present_agree") or key.endswith(":same_length") or key.endswith(":length_diff")
        for key in row
    ), sorted(row)


def test_the_typed_arm_still_scores_one_on_the_frozen_protected_split(datasets):
    run = attacks.run_arm(
        datasets[attacks.DATASET_BASE],
        attacks.DATASET_BASE,
        attacks.ARM_TYPED,
        attacks.FEATURE_FUNCTIONS[attacks.ARM_TYPED],
    )
    assert run.accuracy == 1.0
    assert run.response().distinct_predictions == 3


# ---------------------------------------------------------------------------
# Attack components: each driven to every value it can take
# ---------------------------------------------------------------------------

_GOLD = ("A",) * 4 + ("B",) * 4


@pytest.mark.parametrize("outcome", [Outcome.PASS, Outcome.CANNOT_CHECK])
def test_a_component_cannot_report_a_successful_attack_as_anything_but_fail(outcome):
    with pytest.raises(ValueError):
        attacks.AttackComponent(
            component_id="X",
            hypothesis="H_LEN",
            statement="s",
            outcome=outcome,
            succeeded=True,
            denominator="8",
            detail="d",
            numbers={},
        )


def test_length_sufficiency_fails_the_gate_when_length_reaches_the_typed_arm():
    typed = _arm(attacks.ARM_TYPED, _GOLD, _GOLD)
    challenger = _arm(attacks.ARM_LENGTH_ONLY, _GOLD, _GOLD)
    component = attacks.sufficiency_component(
        component_id="RL-1",
        challenger=challenger,
        typed=typed,
        challenger_label=attacks.ARM_LENGTH_ONLY,
    )
    assert component.succeeded is True
    assert component.outcome is Outcome.FAIL


def test_length_sufficiency_holds_when_length_falls_short():
    typed = _arm(attacks.ARM_TYPED, _GOLD, _GOLD)
    challenger = _arm(attacks.ARM_LENGTH_ONLY, ("A",) * 8, _GOLD)
    component = attacks.sufficiency_component(
        component_id="RL-1",
        challenger=challenger,
        typed=typed,
        challenger_label=attacks.ARM_LENGTH_ONLY,
    )
    assert component.succeeded is False
    assert component.outcome is Outcome.PASS


def test_length_sufficiency_is_decided_at_one_case_not_at_a_wider_tolerance():
    gold = ("A",) * 4 + ("B",) * 4
    typed = _arm(attacks.ARM_TYPED, gold, gold)
    near = _arm(attacks.ARM_LENGTH_ONLY, ("A",) * 5 + ("B",) * 3, gold)
    component = attacks.sufficiency_component(
        component_id="RL-1",
        challenger=near,
        typed=typed,
        challenger_label=attacks.ARM_LENGTH_ONLY,
    )
    assert near.accuracy == 0.875
    assert component.numbers["tolerance"] == attacks.CASE_RESOLUTION
    assert component.succeeded is False
    assert component.outcome is Outcome.PASS


def test_a_contrast_whose_comparator_was_constant_is_not_eligible_to_be_attacked():
    gold = ("A",) * 4 + ("B",) * 4
    typed = _arm(attacks.ARM_TYPED, gold, gold)
    constant = _arm(attacks.ARM_TRANSCRIPT, ("A",) * 8, gold)
    responsive = _arm(attacks.ARM_UNTYPED, ("A", "A", "A", "B", "B", "B", "B", "A"), gold)
    contrasts = {
        "typed_minus_transcript": attacks.measure_contrast_margin(
            "typed_minus_transcript",
            treated=typed.response(),
            comparator=constant.response(),
        ),
        "typed_minus_untyped": attacks.measure_contrast_margin(
            "typed_minus_untyped",
            treated=typed.response(),
            comparator=responsive.response(),
        ),
    }
    assert contrasts["typed_minus_transcript"].outcome is Outcome.CANNOT_CHECK
    assert attacks.eligible_contrasts(contrasts) == ("typed_minus_untyped",)


def test_the_equal_length_control_reports_all_three_of_its_values():
    base = _arm(attacks.ARM_TYPED, _GOLD, _GOLD)
    collapsed = attacks.equal_length_component(
        base_typed=base, control_typed=_arm(attacks.ARM_TYPED, ("A",) * 8, _GOLD)
    )
    assert collapsed.succeeded is True and collapsed.outcome is Outcome.FAIL

    held = attacks.equal_length_component(base_typed=base, control_typed=base)
    assert held.succeeded is False and held.outcome is Outcome.PASS

    partial = attacks.equal_length_component(
        base_typed=base,
        control_typed=_arm(attacks.ARM_TYPED, ("A", "A", "A", "A", "B", "B", "A", "A"), _GOLD),
    )
    assert partial.succeeded is False and partial.outcome is Outcome.CANNOT_CHECK


def test_a_reformat_that_closes_the_gap_fails_the_gate():
    typed = _arm(attacks.ARM_TYPED, _GOLD, _GOLD)
    weak = _arm(attacks.ARM_SERIALIZED, ("A",) * 8, _GOLD)
    strong = _arm(attacks.ARM_SERIALIZED_PATHONLY, ("A", "A", "A", "A", "B", "B", "B", "A"), _GOLD)
    component = attacks.reformat_component(
        component_id="FP-1", typed=typed, base_arm=weak, reformatted=strong
    )
    assert component.succeeded is True
    assert component.outcome is Outcome.FAIL


def test_a_constant_reformatted_arm_is_cannot_check_not_a_refuted_attack():
    typed = _arm(attacks.ARM_TYPED, _GOLD, _GOLD)
    weak = _arm(attacks.ARM_SERIALIZED, ("A",) * 8, _GOLD)
    constant = _arm(attacks.ARM_SERIALIZED_INDEXED, ("B",) * 8, _GOLD)
    component = attacks.reformat_component(
        component_id="FP-1", typed=typed, base_arm=weak, reformatted=constant
    )
    assert component.succeeded is False
    assert component.outcome is Outcome.CANNOT_CHECK


def test_an_invariance_check_with_no_opportunity_is_cannot_check_not_a_pass():
    features = tuple((("f", index),) for index in range(8))
    base = _arm(attacks.ARM_TYPED, _GOLD, _GOLD, test_features=features)
    same = _arm(attacks.ARM_TYPED, _GOLD, _GOLD, test_features=features)
    component = attacks.invariance_component(
        component_id="FP-2", hypothesis="H_FMT", transform="orbit", base=base, transformed=same
    )
    assert component.outcome is Outcome.CANNOT_CHECK
    assert component.succeeded is False
    assert component.numbers["protected_feature_dicts_changed"] == 0


def test_an_invariance_check_that_moves_a_prediction_fails_the_gate():
    before = tuple((("f", index),) for index in range(8))
    after = tuple((("g", index),) for index in range(8))
    base = _arm(attacks.ARM_SERIALIZED, _GOLD, _GOLD, test_features=before)
    moved = _arm(attacks.ARM_SERIALIZED, ("A",) * 8, _GOLD, test_features=after)
    component = attacks.invariance_component(
        component_id="FP-2", hypothesis="H_FMT", transform="orbit", base=base, transformed=moved
    )
    assert component.outcome is Outcome.FAIL
    assert component.succeeded is True
    assert component.numbers["protected_predictions_changed"] == 4


def test_an_invariance_check_that_holds_under_a_real_change_passes():
    before = tuple((("f", index),) for index in range(8))
    after = tuple((("g", index),) for index in range(8))
    base = _arm(attacks.ARM_SERIALIZED, _GOLD, _GOLD, test_features=before)
    steady = _arm(attacks.ARM_SERIALIZED, _GOLD, _GOLD, test_features=after)
    component = attacks.invariance_component(
        component_id="FP-2", hypothesis="H_FMT", transform="orbit", base=base, transformed=steady
    )
    assert component.outcome is Outcome.PASS
    assert component.succeeded is False


# ---------------------------------------------------------------------------
# The artifact this lane produced
# ---------------------------------------------------------------------------


def test_the_result_artifact_records_a_successful_format_prior_attack(result):
    assert result["parameters_sha256"] == attacks.frozen_digest()
    assert result["verdict"] == attacks.VERDICT_ATTACK_SUCCEEDED
    assert result["outcome"] == Outcome.FAIL.value
    assert result["component_census"]["succeeded_ids"] == [
        "FP-2_SEMANTIC_ORBIT_INVARIANCE::TYPED_SERIALIZED_BAG"
    ]


def test_the_serialized_arm_moved_thirty_two_answers_under_a_meaning_preserving_rename(result):
    component = next(
        item
        for item in result["components"]
        if item["component_id"] == "FP-2_SEMANTIC_ORBIT_INVARIANCE::TYPED_SERIALIZED_BAG"
    )
    numbers = component["numbers"]
    assert numbers["protected_predictions_changed"] == 32
    assert numbers["base_accuracy"] == 0.75
    assert numbers["transformed_accuracy"] == 0.5
    assert result["arms"]["SEMANTIC_ORBIT"]["TYPED_SERIALIZED_BAG"]["distinct_predictions"] == 1


def test_the_length_attack_did_not_succeed_and_says_so_with_its_denominator(result):
    by_id = {item["component_id"]: item for item in result["components"]}
    for component_id, accuracy in (
        ("RL-1_LENGTH_ONLY_SUFFICIENT", 0.75),
        ("RL-2_LENGTH_RELATIONAL_SUFFICIENT", 0.875),
    ):
        component = by_id[component_id]
        assert component["attack_succeeded"] is False
        assert component["outcome"] == Outcome.PASS.value
        assert component["denominator"] == "128 protected cases"
        assert component["numbers"]["challenger_accuracy"] == accuracy
    control = by_id["RL-3_EQUAL_LENGTH_CONTROL"]
    assert control["attack_succeeded"] is False
    assert control["numbers"]["control_typed_accuracy"] == 1.0
    assert result["arms"]["EQUAL_LENGTH"]["UNTYPED_PAIR"]["accuracy"] == 0.609375


def test_the_order_remint_component_is_cannot_check_on_every_arm(result):
    order = [
        item
        for item in result["components"]
        if item["component_id"].startswith("FP-3_ORDER_REMINT_INVARIANCE")
    ]
    assert len(order) == len(attacks.ARM_ORDER)
    assert all(item["outcome"] == Outcome.CANNOT_CHECK.value for item in order)
    assert all(item["numbers"]["protected_feature_dicts_changed"] == 0 for item in order)


def test_the_transcript_contrast_is_not_eligible_to_be_attacked(result):
    assert result["contrast_eligibility"]["not_eligible"] == {
        "typed_minus_transcript": "COMPARATOR_CONSTANT"
    }
    assert sorted(result["contrast_eligibility"]["eligible_for_attack"]) == [
        "typed_minus_same_information_serialized",
        "typed_minus_untyped",
    ]


def test_the_artifact_refuses_to_discharge_the_terminal(result):
    assert result["claim_scope"].startswith("BOUNDED_D1_ONLY")
    assert "stays BLOCKED" in result["terminal_disposition"]
    assert result["environment_boundary"]["successor_llm_run_exists"] is False


def test_main_requires_its_argv_and_runs_as_a_subprocess(capsys):
    with pytest.raises(TypeError):
        attacks.main()  # type: ignore[call-arg]
    assert attacks.main(["--print-digest"]) == 0
    assert capsys.readouterr().out.strip() == attacks.frozen_digest()

    completed = subprocess.run(
        [sys.executable, "-m", "orion.study.p9.hostile_representation_attacks", "--print-digest"],
        cwd=str(REPO_ROOT),
        env={
            "PYTHONPATH": str(REPO_ROOT / "src"),
            "PATH": "/usr/bin:/bin:/usr/local/bin",
            # The interpreter binary needs its own runtime loader path. A
            # Python installed outside a default prefix (an HPC module, pyenv,
            # some conda layouts) keeps libpython there, and scrubbing this
            # kills the child with exit 127 before Python starts. Carrying it
            # does not weaken the isolation this env is for: it is the
            # loader's path, not an import path.
            **{
                key: value
                for key, value in os.environ.items()
                if key in ("LD_LIBRARY_PATH", "DYLD_LIBRARY_PATH")
            },
        },
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == attacks.frozen_digest()
