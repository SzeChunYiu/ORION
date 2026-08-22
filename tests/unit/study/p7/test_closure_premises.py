"""P7's shipped closure checkers, measured against the premises they are handed.

Every number pinned here was read off the shipped artifacts
``papers/paper-07-epistemic-navigation-open-worlds/formal/check_theory_closure_v2.py``,
``research/claim_expansion/p7/check_p7_x2_closure_carrying.py`` and
``research/claim_expansion/p7/P7_X2_CLOSURE_CARRYING_RESULT_V1.json``, or off a
run of the checkers that produced them.
"""

from __future__ import annotations

import ast
import contextlib
import io
import json

import pytest

from orion.programme.decided_premises import (
    Assignment,
    AssertionReplay,
    DecidedResult,
    DecisionReason,
    UndecidedPremise,
    case_label,
    decision_outcome,
    require_decided,
    sample_assignments_accepted,
)
from orion.programme.records import Outcome
from orion.programme.refutation_capacity import (
    axis_sensitivity,
    measure_refutation_capacity,
)
from orion.study.p7 import closure_premises as premises
from orion.study.p7.premise_audit import audit_p7_closure_checkers, main, report_as_json


@pytest.fixture(scope="module")
def theory_closure():
    return premises.theory_closure_module()


@pytest.fixture(scope="module")
def closure_carrying():
    return premises.closure_carrying_module()


@pytest.fixture(scope="module")
def published():
    return json.loads(premises.CLOSURE_CARRYING_RESULT_PATH.read_text())


def _run_shipped_closure_carrying(module) -> dict:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        module.main()
    return json.loads(buffer.getvalue())


def _accepts(replay: AssertionReplay, assignment: Assignment) -> bool:
    """Whether the replayed assertions hold under one deciding rule."""

    try:
        return bool(replay(assignment))
    except AssertionError:
        return False


def test_the_instrument_reproduces_the_published_row_digest(closure_carrying) -> None:
    """Pointed at the shipped artifact, not at a fixture of its own."""

    assert premises.canonical_rows_digest(closure_carrying) == premises.SHIPPED_ROWS_SHA256


def test_the_shipped_checker_reproduces_its_published_counts(closure_carrying, published) -> None:
    result = _run_shipped_closure_carrying(closure_carrying)

    assert result["state_evaluations"] == 320
    assert result["composition_successes"] == published["composition_successes"] == 25
    assert (
        result["composition_bridge_countermodels"]
        == published["composition_bridge_countermodels"]
        == 25
    )
    assert result["canonical_rows_sha256"] == premises.SHIPPED_ROWS_SHA256


# ---------------------------------------------------------------------------
# The transport theorem: a premise its own model cannot express
# ---------------------------------------------------------------------------


def test_the_transport_theorem_never_constrains_its_ambiguity_premise(theory_closure) -> None:
    constraint = premises.transport_constraint(theory_closure)

    assert len(constraint.cases) == premises.SHIPPED_TRANSPORT_CASES == 64
    assert len(constraint.free_case_ids) == 64
    assert constraint.decided_case_ids == ()
    assert constraint.admissible_assignments == 2**64
    assert constraint.reason is DecisionReason.UNDECIDABLE_IN_MODEL
    assert constraint.outcome is Outcome.CANNOT_CHECK
    assert constraint.modelled is False


def test_the_ambiguity_premise_accepts_the_v1_error_the_v2_core_says_it_fixed(
    theory_closure,
) -> None:
    """The constant-false rule is "incompleteness never means ambiguity"."""

    replay = premises.transport_replay(theory_closure)

    assert replay(lambda point: False)
    assert replay(lambda point: True)
    assert replay(lambda point: point["maps_obligation"])


def test_the_transport_check_refutes_every_declared_false_theory_and_still_blocks(
    theory_closure,
) -> None:
    """The two questions are independent: refutation capacity clears this check."""

    capacity = measure_refutation_capacity(
        premises.transport_check(),
        reference=premises.transport_rule(theory_closure),
        reference_id=premises.TRANSPORT_REFERENCE_ID,
        theories=premises.FALSE_TRANSPORT_THEORIES,
        space=premises.transport_theory_space(),
    )

    assert capacity.outcome is Outcome.PASS
    assert len(capacity.refuted) == len(premises.FALSE_TRANSPORT_THEORIES) == 4
    assert capacity.survivors == ()
    assert premises.transport_constraint(theory_closure).blocks


def test_the_ambiguity_decider_exists_in_the_same_file_and_is_never_called() -> None:
    """``extension_ambiguous`` is a real rule the transport theorem does not reach."""

    tree = ast.parse(premises.THEORY_CLOSURE_PATH.read_text())
    functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
    callers = {
        name
        for name, node in functions.items()
        if any(
            isinstance(call, ast.Call)
            and isinstance(call.func, ast.Name)
            and call.func.id == "extension_ambiguous"
            for call in ast.walk(node)
        )
    }

    assert "extension_ambiguous" in functions
    assert callers == {"check_stopping_impossibility", "check_certificate_absence_not_ambiguity"}
    assert "check_support_transport" not in callers


def test_the_transport_case_count_is_not_a_count_of_decided_cases(theory_closure) -> None:
    """64 is the size of the enumeration; 1 is what the check decides in-model."""

    authority = premises.transport_authority(theory_closure)

    assert authority["enumerated_states"] == 64
    assert authority["decided_by_the_witness_coordinates"] == 1
    assert authority["downstream_of_the_undecided_premise"] == 63
    # Read off the shipped file rather than restated here.
    assert authority["shipped_terminal"] == "CANNOT_CHECK"
    assert authority["shipped_checked"] == 1
    assert authority["shipped_undecidable_premise"] == "target_ambiguous_if_missing"
    assert authority["shipped_decided_from"] == "admissible_target_completions"


def test_the_reproduction_note_does_not_read_the_64_as_a_result() -> None:
    """The count downstream of the undecided premise is not the paper's headline."""

    note = (
        premises.REPO_ROOT
        / "papers/paper-07-epistemic-navigation-open-worlds/REPRODUCE_V2_1.md"
    ).read_text()

    assert "theory_closure_terminal: CANNOT_CHECK" in note
    assert "including all 64 transport-coordinate combinations" not in note


# ---------------------------------------------------------------------------
# The same premise, in a model that carries what Definition 14 reads
# ---------------------------------------------------------------------------


def test_the_completion_classes_decide_ambiguity_from_structure(theory_closure) -> None:
    """Not a relabelled boolean: ambiguity falls out of the class's own members."""

    classes = premises.completion_classes(theory_closure)
    ambiguous = [
        name for name, value in classes.items() if theory_closure.extension_ambiguous(value)
    ]

    assert len(classes) == 15
    assert len(ambiguous) == 7
    assert len(classes) - len(ambiguous) == 8


def test_the_ambiguity_premise_is_decidable_once_the_model_carries_its_inputs(
    theory_closure,
) -> None:
    """Same premise, same ``decided_from``; only the model differs."""

    extended = premises.extended_transport_constraint(theory_closure)
    shipped = premises.transport_constraint(theory_closure)

    assert extended.premise is shipped.premise is premises.TARGET_AMBIGUITY
    assert premises.TARGET_AMBIGUITY.decided_from == ("admissible_target_completions",)
    assert len(extended.cases) == 64 * 15 == 960
    assert extended.modelled is True
    assert extended.free_case_ids == ()
    assert extended.admissible_assignments == 1
    assert extended.reason is DecisionReason.DECIDED_ON_EVERY_CASE
    assert extended.outcome is Outcome.PASS
    # The shipped model is what cannot answer, not the premise.
    assert shipped.modelled is False
    assert shipped.reason is DecisionReason.UNDECIDABLE_IN_MODEL


def test_the_extended_space_rejects_the_rules_the_shipped_one_accepts(theory_closure) -> None:
    replay = premises.extended_transport_replay(theory_closure)
    baseline = premises.extended_transport_baseline(theory_closure)

    assert replay(baseline)
    assert not _accepts(replay, lambda point: True)
    assert not _accepts(replay, lambda point: False)
    assert sample_assignments_accepted(
        premises.TARGET_AMBIGUITY,
        cases=premises.extended_transport_cases(theory_closure),
        replay=replay,
        trials=200,
    ) == (0, 200)


# ---------------------------------------------------------------------------
# The composition block: a premise the model carries, now decided from it
# ---------------------------------------------------------------------------


def test_the_composition_bridge_is_decided_from_the_donor_pair_and_the_registry(
    closure_carrying,
) -> None:
    constraint = premises.composition_constraint(closure_carrying)
    axes = {key for point in premises.composition_cases(closure_carrying) for key in point}

    assert premises.BRIDGE_MATCH.decided_from == ("left_donor", "right_donor", "registry")
    assert set(premises.BRIDGE_MATCH.decided_from) <= axes
    # 25 ordered pairs, each asserted under the bridging registry and the empty one.
    assert len(constraint.cases) == 50
    assert constraint.free_case_ids == ()
    assert len(constraint.decided_case_ids) == 50
    assert constraint.admissible_assignments == 1
    assert constraint.reason is DecisionReason.DECIDED_ON_EVERY_CASE
    assert constraint.outcome is Outcome.PASS
    assert constraint.modelled is True


def test_a_supplied_bridge_cannot_survive_the_composition_replay(closure_carrying) -> None:
    """The regression guard: this fails the moment the premise goes back to free.

    A free premise is exactly a replay that accepts a rule other than the
    decision, so every single-row deviation is tried rather than only the two
    constants the shipped block passed.
    """

    replay = premises.composition_replay(closure_carrying)
    decide = premises.composition_match(closure_carrying)
    cases = premises.composition_cases(closure_carrying)

    assert replay(decide)
    assert replay(premises.composition_baseline)
    assert not _accepts(replay, lambda point: True)
    assert not _accepts(replay, lambda point: False)
    for point in cases:
        label = case_label(point)

        def flipped(other, label=label):
            value = bool(decide(other))
            return (not value) if case_label(other) == label else value

        assert not _accepts(replay, flipped), f"{label} leaves bridge_match free"


def test_the_admissible_rule_count_for_a_decided_premise_is_bounded(
    theory_closure, closure_carrying
) -> None:
    """One is the only count compatible with "the artifact decided it"."""

    decided = (
        premises.composition_constraint(closure_carrying),
        premises.extended_transport_constraint(theory_closure),
    )
    for constraint in decided:
        assert constraint.reason is DecisionReason.DECIDED_ON_EVERY_CASE
        assert constraint.admissible_assignments == 1
        assert constraint.admissible_assignments < 2 ** len(constraint.cases)

    supplied = premises.transport_constraint(theory_closure)
    assert supplied.admissible_assignments == 2 ** len(supplied.cases)


def test_whole_bridge_rules_drawn_at_random_are_rejected(closure_carrying) -> None:
    """Single-case perturbation counts exactly only if the assertions factorise."""

    assert sample_assignments_accepted(
        premises.BRIDGE_MATCH,
        cases=premises.composition_cases(closure_carrying),
        replay=premises.composition_replay(closure_carrying),
    ) == (0, 5000)


def test_deciding_the_bridge_moves_no_published_verdict(closure_carrying, published) -> None:
    """The most important thing to report: the decision agrees with the literals."""

    agreement = premises.composition_agreement(closure_carrying)

    assert agreement["rows"] == 50
    assert agreement["rows_where_the_decision_agrees_with_the_shipped_literal"] == 50
    assert agreement["verdicts_moved"] is False
    assert agreement["composition_successes"] == published["composition_successes"] == 25
    assert (
        agreement["composition_bridge_countermodels"]
        == published["composition_bridge_countermodels"]
        == 25
    )


def test_the_decided_bridge_still_does_not_vary_with_the_donor_pair(closure_carrying) -> None:
    """Deciding a premise and the decision depending on the case are two facts."""

    left, right, registry = premises.composition_handoff_axes(closure_carrying)

    assert (left.axis, right.axis, registry.axis) == ("left_donor", "right_donor", "registry")
    assert left.inert and right.inert
    assert left.multiplier == right.multiplier == 5
    assert not registry.inert
    assert registry.verdict_changing_pairs == registry.comparable_pairs == 25


def test_the_composition_block_evaluates_two_of_eight_argument_triples(closure_carrying) -> None:
    triples = premises.composition_argument_triples(closure_carrying)

    assert triples == ((True, True, False), (True, True, True))
    assert premises.compose_rules_accepted(closure_carrying) == (64, 256)


def test_the_shipped_counts_survive_a_composition_rule_that_ignores_both_operands(
    closure_carrying, published
) -> None:
    """25/25 and the digest are identical under the direct denial of P7.V3.5."""

    module = premises.closure_carrying_module()
    module.compose = lambda left, right, bridge_match: bridge_match
    result = _run_shipped_closure_carrying(module)

    assert result["composition_successes"] == published["composition_successes"]
    assert (
        result["composition_bridge_countermodels"]
        == published["composition_bridge_countermodels"]
    )
    assert result["canonical_rows_sha256"] == published["canonical_rows_sha256"]


# ---------------------------------------------------------------------------
# The inert donor axis
# ---------------------------------------------------------------------------


def test_the_donor_axis_only_multiplies_the_case_counts(closure_carrying) -> None:
    sensitivity = axis_sensitivity(
        "donor",
        reference=premises.closure_reference(closure_carrying),
        space=premises.closure_model_space(closure_carrying),
    )

    assert sensitivity.comparable_pairs == 640
    assert sensitivity.verdict_changing_pairs == 0
    assert sensitivity.inert
    assert sensitivity.multiplier == 5


def test_the_donor_axis_is_inert_because_no_rule_can_read_it(closure_carrying) -> None:
    """Which kind of inert, decided from the artifact rather than from the shape."""

    diagnosis = premises.donor_axis_diagnosis(closure_carrying)
    multipliers = diagnosis["multipliers"]

    assert diagnosis["functions_taking_a_donor_argument"] == ()
    assert diagnosis["the_rule_can_read_the_donor"] is False
    assert diagnosis["verdict"] == "THE_RULE_CANNOT_READ_THE_DONOR"
    # The one donor-dependent count is guarded by a comparison of a name against
    # the name it was assigned from, so its zero cannot be an observation.
    assert diagnosis["identity_guards"] == ("main: projected_native != native_valid",)
    assert premises.DONOR_CONSERVATIVITY_COUNT in multipliers["counts_zero_at_every_stack_size"]

    assert multipliers["counts_at_five_donors"]["state_evaluations"] == 320
    assert multipliers["counts_at_one_donor"]["state_evaluations"] == 64
    assert set(multipliers["counts_multiplied_by_the_donor_loop"]) == {
        "state_evaluations",
        "single_coordinate_separation_witnesses",
        "full_closure_refinement_successes",
        "partial_closure_refinement_failures",
    }
    assert set(multipliers["counts_multiplied_by_the_donor_pair_loop"]) == {
        "composition_successes",
        "composition_bridge_countermodels",
    }
    assert multipliers["counts_independent_of_the_donor_loop"] == (
        "donor_product_nonclosure_countermodels",
    )


# ---------------------------------------------------------------------------
# The roll-up, and the audit that carries it
# ---------------------------------------------------------------------------


def test_the_published_counts_cannot_be_held_as_a_result(theory_closure, closure_carrying) -> None:
    constraints = (
        premises.transport_constraint(theory_closure),
        premises.composition_constraint(closure_carrying),
    )

    # Non-compensatory: one decided premise does not lift the undecidable one.
    assert decision_outcome(constraints) is Outcome.CANNOT_CHECK
    with pytest.raises(UndecidedPremise, match="cannot report"):
        DecidedResult(
            result_id="P7.V3.7",
            reported=(("composition_successes", 25), ("composition_bridge_countermodels", 25)),
            constraints=constraints,
        )
    with pytest.raises(UndecidedPremise) as excinfo:
        require_decided(constraints, label="P7.V3.5 / P7 C4")
    message = str(excinfo.value)
    assert "target_ambiguous_if_missing" in message
    assert "cannot be decided in this model at all" in message
    # bridge_match is no longer among the premises the check was handed.
    assert "premises are supplied to the check" not in message


def test_the_audit_runs_against_the_shipped_files_and_blocks() -> None:
    report = audit_p7_closure_checkers()
    payload = report_as_json(report)

    assert payload["canonical_rows_reproduced"] is True
    assert payload["outcome"] == Outcome.CANNOT_CHECK.value
    assert payload["compose_rules_accepted"] == 64
    assert {item["reason"] for item in payload["constraints"]} == {
        DecisionReason.UNDECIDABLE_IN_MODEL.value,
        DecisionReason.DECIDED_ON_EVERY_CASE.value,
    }
    assert payload["transport_capacity"]["outcome"] == Outcome.PASS.value
    assert payload["extended_transport"]["outcome"] == Outcome.PASS.value
    assert payload["extended_transport"]["admissible_assignments"] == 1
    assert payload["transport_authority"]["decided_by_the_witness_coordinates"] == 1
    # Whole rules, not only single-case perturbations of one.
    assert payload["sampled_ambiguity_rules"] == [5000, 5000]
    assert payload["sampled_bridge_rules"] == [0, 5000]
    assert payload["sampled_extended_ambiguity_rules"] == [0, 5000]
    assert payload["composition_agreement"]["verdicts_moved"] is False


def test_the_audit_cli_exits_three(capsys) -> None:
    assert main([]) == 3
    assert "P7 closure premises" in capsys.readouterr().out
    assert main(["--json"]) == 3
    assert json.loads(capsys.readouterr().out)["outcome"] == Outcome.CANNOT_CHECK.value
