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
# The transport theorem: a premise the model now carries and decides
# ---------------------------------------------------------------------------


def test_the_shipped_checker_decides_ambiguity_and_reports_pass(theory_closure) -> None:
    """Read off the shipped file: the terminal, the count and the absent premise."""

    shipped = theory_closure.check_support_transport()

    assert shipped.terminal == "PASS"
    assert shipped.checked == premises.SHIPPED_TRANSPORT_CASES == 960
    # A PASS may not name a premise it could not decide, and this one does not.
    assert shipped.undecidable_premise is None
    assert shipped.decided_from is None
    assert "extension_ambiguous" in shipped.detail


def test_the_theory_closure_terminal_is_pass(theory_closure) -> None:
    """The aggregate is the line the reproduction note tells a reader to read."""

    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        theory_closure.main()
    output = buffer.getvalue()

    assert "P7 THEORY CLOSURE V2: PASS" in output
    assert "theory_closure_terminal: PASS" in output
    assert "support_transport: PASS (960 checked)" in output


def test_the_ambiguity_decider_is_now_called_by_the_transport_check() -> None:
    """The regression pin on the repair: ``extension_ambiguous`` is reached.

    While this call was absent the premise was free on every case, so its absence
    is the shape the check must not go back to.
    """

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
    assert "admissible_completion_classes" in functions
    assert "check_support_transport" in callers


def test_the_shipped_transport_space_carries_the_axis_definition_14_reads(
    theory_closure,
) -> None:
    """``admissible_target_completions`` is an axis of the shipped cases now."""

    cases = premises.transport_cases(theory_closure)
    axes = {key for point in cases for key in point}

    assert len(cases) == premises.SHIPPED_TRANSPORT_CASES == 960
    assert len(premises.transport_coordinate_states()) == premises.TRANSPORT_COORDINATE_STATES == 64
    assert set(premises.TARGET_AMBIGUITY.decided_from) <= axes
    assert premises.TARGET_AMBIGUITY.decided_from == ("admissible_target_completions",)


def test_the_completion_classes_are_read_off_the_shipped_checker(theory_closure) -> None:
    """Not a fixture of the audit's own, and not a relabelled boolean."""

    classes = premises.completion_classes(theory_closure)
    ambiguous = [
        name for name, value in classes.items() if theory_closure.extension_ambiguous(value)
    ]

    assert classes == theory_closure.admissible_completion_classes()
    assert len(classes) == 15
    assert len(ambiguous) == 7
    assert len(classes) - len(ambiguous) == 8


def test_the_shipped_transport_check_decides_its_own_ambiguity_premise(
    theory_closure,
) -> None:
    """The premise is decided in the shipped space, not only in a demonstration."""

    constraint = premises.transport_constraint(theory_closure)

    assert constraint.check_id == "check_support_transport"
    assert constraint.premise is premises.TARGET_AMBIGUITY
    assert len(constraint.cases) == 960
    assert constraint.free_case_ids == ()
    assert len(constraint.decided_case_ids) == 960
    assert constraint.admissible_assignments == 1
    assert constraint.reason is DecisionReason.DECIDED_ON_EVERY_CASE
    assert constraint.outcome is Outcome.PASS
    assert constraint.modelled is True
    assert not constraint.blocks


def test_a_supplied_ambiguity_cannot_survive_the_shipped_transport_replay(
    theory_closure,
) -> None:
    """The regression guard: this fails the moment the premise goes back to free.

    A free premise is exactly a replay that accepts a rule other than the
    decision, so every single-case deviation is tried rather than only the two
    constants the pre-repair body passed.
    """

    replay = premises.transport_replay(theory_closure)
    decide = premises.transport_baseline(theory_closure)
    cases = premises.transport_cases(theory_closure)

    assert replay(decide)
    # The constant-false rule is the V1 error the V2 core says it repaired.
    assert not _accepts(replay, lambda point: False)
    assert not _accepts(replay, lambda point: True)
    for point in cases:
        label = case_label(point)

        def flipped(other, label=label):
            value = bool(decide(other))
            return (not value) if case_label(other) == label else value

        assert not _accepts(replay, flipped), f"{label} leaves target_ambiguous_if_missing free"


def test_whole_ambiguity_rules_drawn_at_random_are_rejected(theory_closure) -> None:
    """Single-case perturbation counts exactly only if the assertions factorise."""

    assert sample_assignments_accepted(
        premises.TARGET_AMBIGUITY,
        cases=premises.transport_cases(theory_closure),
        replay=premises.transport_replay(theory_closure),
    ) == (0, 5000)


def test_the_terminal_assertions_alone_still_exclude_945_of_the_960(
    theory_closure,
) -> None:
    """The floor under the verdict, with the decision assertion dropped.

    ``transport_replay`` asserts that the rule under test agrees with
    ``extension_ambiguous``, because that is what the shipped body computes. This
    pins how much of the result rests on that assertion: without it, the 15 cases
    pairing the complete witness with a class go free --- Theorem 6 returns
    ``TRANSFER_CLOSURE`` there whatever ambiguity is --- and nothing else does.
    """

    floor = premises.transport_mapping_only_floor(theory_closure)
    replay = premises.transport_mapping_only_replay(theory_closure)

    assert floor["cases"] == 960
    assert floor["cases_excluding_a_value_from_the_terminal_assertions_alone"] == 945
    assert floor["cases_free_under_the_terminal_assertions_alone"] == 15
    assert floor["admissible_ambiguity_rules_under_the_terminal_assertions_alone"] == 2**15
    # Still far from free: the constants do not survive the mapping alone either.
    assert not _accepts(replay, lambda point: True)
    assert not _accepts(replay, lambda point: False)


def test_the_free_cases_under_the_mapping_alone_are_the_complete_witness(
    theory_closure,
) -> None:
    """Not an arbitrary 15: they are the cases Theorem 6 does not read ambiguity on."""

    complete = [
        point
        for point in premises.transport_cases(theory_closure)
        for _ in (0,)
        if all(bool(point[name]) for name in premises.TRANSPORT_COORDINATES)
    ]

    assert len(complete) == len(premises.completion_classes(theory_closure)) == 15
    witness = theory_closure.Transport(*(True,) * 6)
    assert witness.complete
    for value in (False, True):
        assert (
            theory_closure.transfer_terminal(witness, target_ambiguous_if_missing=value)
            == "TRANSFER_CLOSURE"
        )


def test_the_transport_case_count_grew_and_is_a_different_measurement(
    theory_closure,
) -> None:
    """960 is not a bigger 64: the old count stood downstream of the premise."""

    authority = premises.transport_authority(theory_closure)

    assert authority["previously_enumerated_states"] == 64
    assert authority["previously_decided_cases"] == 1
    assert authority["enumerated_cases"] == 960
    assert authority["transport_coordinate_states"] == 64
    assert authority["admissible_completion_classes"] == 15
    assert authority["ambiguous_completion_classes"] == 7
    assert authority["unambiguous_completion_classes"] == 8
    assert authority["cases_whose_terminal_consumes_the_premise"] == 945
    assert authority["cases_whose_terminal_is_fixed_by_completeness"] == 15
    # Read off the shipped file rather than restated here.
    assert authority["shipped_terminal"] == "PASS"
    assert authority["shipped_checked"] == 960
    assert authority["shipped_undecidable_premise"] is None


def test_the_premise_is_still_undecidable_without_the_completion_class(
    theory_closure,
) -> None:
    """The contrast that says the repair was a missing axis, not a weaker check.

    Same premise, same ``decided_from``, the six coordinates alone: still free on
    every case, still 2**64 admissible ambiguity predicates, still including the
    constant-false one.
    """

    witness_only = premises.witness_only_transport_constraint(theory_closure)
    replay = premises.witness_only_transport_replay(theory_closure)

    assert witness_only.check_id == premises.WITNESS_ONLY_TRANSPORT_CHECK_ID
    assert witness_only.check_id != "check_support_transport"
    assert witness_only.premise is premises.TARGET_AMBIGUITY
    assert len(witness_only.cases) == 64
    assert len(witness_only.free_case_ids) == 64
    assert witness_only.decided_case_ids == ()
    assert witness_only.admissible_assignments == 2**64
    assert witness_only.reason is DecisionReason.UNDECIDABLE_IN_MODEL
    assert witness_only.outcome is Outcome.CANNOT_CHECK
    assert witness_only.modelled is False
    assert replay(lambda point: False)
    assert replay(lambda point: True)
    assert replay(lambda point: point["maps_obligation"])


def test_the_transport_check_refutes_every_declared_false_theory(theory_closure) -> None:
    """Refutation capacity and the premise question stay independent measurements."""

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
    # This passed while the premise was entirely free, which is why it is not the
    # evidence that the premise is decided.
    assert not premises.transport_constraint(theory_closure).blocks
    assert premises.witness_only_transport_constraint(theory_closure).blocks


def test_the_reproduction_note_reports_the_authority_the_check_now_has() -> None:
    """The published figure moved, and the note has to say what it moved to."""

    note = (
        premises.REPO_ROOT
        / "papers/paper-07-epistemic-navigation-open-worlds/REPRODUCE_V2_1.md"
    ).read_text()

    assert "theory_closure_terminal: PASS" in note
    assert "theory_closure_terminal: CANNOT_CHECK" not in note
    assert "960" in note
    assert "The 960 is not a bigger 64." in note
    # What the count does not establish stays in the note beside what it does.
    assert "not every completion class a target model could admit" in note


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
        premises.transport_constraint(theory_closure),
    )
    for constraint in decided:
        assert constraint.reason is DecisionReason.DECIDED_ON_EVERY_CASE
        assert constraint.admissible_assignments == 1
        assert constraint.admissible_assignments < 2 ** len(constraint.cases)

    supplied = premises.witness_only_transport_constraint(theory_closure)
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

    assert diagnosis["verdict_rules_taking_a_donor_argument"] == ()
    assert diagnosis["the_rule_can_read_the_donor"] is False
    assert diagnosis["verdict"] == "THE_RULE_CANNOT_READ_THE_DONOR"
    # Three shipped functions take a donor argument and none is a verdict: the
    # projection, which carries the label into the transform and is what makes the
    # ten donor transforms ten, and the two predicates over that transform, which
    # discard it and are what make those ten carry two distinct verdicts.
    assert diagnosis["functions_taking_a_donor_argument"] == (
        "carry_image_in_donor_language",
        "native_verdict",
        "project_to_donor",
    )
    assert diagnosis["donor_arguments_that_change_the_value"] == ("project_to_donor",)
    # The guard that could not fire is gone, and the detector for it stays armed.
    assert diagnosis["identity_guards"] == ()
    assert premises.DONOR_CONSERVATIVITY_COUNT in multipliers["counts_zero_at_every_stack_size"]

    assert multipliers["counts_at_five_donors"]["state_evaluations"] == 320
    assert multipliers["counts_at_one_donor"]["state_evaluations"] == 64
    assert set(multipliers["counts_multiplied_by_the_donor_loop"]) == {
        "state_evaluations",
        "single_coordinate_separation_witnesses",
        "full_closure_refinement_successes",
        "partial_closure_refinement_failures",
        # The conservativity block visits five copies of two donor transforms for
        # the same reason, and publishes the distinct count beside the total.
        "donor_conservativity_states",
    }
    assert set(multipliers["counts_multiplied_by_the_donor_pair_loop"]) == {
        "composition_successes",
        "composition_bridge_countermodels",
    }
    assert set(multipliers["counts_independent_of_the_donor_loop"]) == {
        "donor_product_nonclosure_countermodels",
        # The assertion-coverage counts are over one copy of the state space by
        # construction, which is the point of publishing them.
        "assertion_covered_states",
        "assertion_covered_states_native_invalid",
        "assertion_state_space",
        "donor_conservativity_distinct_states",
    }


# ---------------------------------------------------------------------------
# The roll-up, and the audit that carries it
# ---------------------------------------------------------------------------


def test_the_published_counts_can_now_be_held_as_a_result(theory_closure, closure_carrying) -> None:
    """Both premises are decided by the artifacts, so the gate opens for both."""

    constraints = (
        premises.transport_constraint(theory_closure),
        premises.composition_constraint(closure_carrying),
    )

    assert decision_outcome(constraints) is Outcome.PASS
    result = DecidedResult(
        result_id="P7.V3.7",
        reported=(("composition_successes", 25), ("composition_bridge_countermodels", 25)),
        constraints=constraints,
    )
    assert result.as_json()["reported"] == {
        "composition_successes": 25,
        "composition_bridge_countermodels": 25,
    }
    require_decided(constraints, label="P7.V3.5 / P7 C4")


def test_the_gate_still_closes_on_the_model_that_could_not_decide_the_premise(
    theory_closure, closure_carrying
) -> None:
    """Non-compensatory, and still armed: the repair opened it, not a weaker rule."""

    constraints = (
        premises.witness_only_transport_constraint(theory_closure),
        premises.composition_constraint(closure_carrying),
    )

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


def test_the_audit_runs_against_the_shipped_files_and_passes() -> None:
    report = audit_p7_closure_checkers()
    payload = report_as_json(report)

    assert payload["canonical_rows_reproduced"] is True
    assert payload["outcome"] == Outcome.PASS.value
    assert payload["compose_rules_accepted"] == 64
    assert {item["reason"] for item in payload["constraints"]} == {
        DecisionReason.DECIDED_ON_EVERY_CASE.value
    }
    assert {item["check_id"] for item in payload["constraints"]} == {
        "check_support_transport",
        "p7_x2_composition_block",
    }
    assert payload["transport_capacity"]["outcome"] == Outcome.PASS.value
    # The pre-repair model is reported beside the verdict and is not part of it.
    assert payload["witness_only_transport"]["outcome"] == Outcome.CANNOT_CHECK.value
    assert payload["witness_only_transport"]["reason"] == (
        DecisionReason.UNDECIDABLE_IN_MODEL.value
    )
    assert payload["transport_authority"]["enumerated_cases"] == 960
    assert payload["transport_authority"]["previously_decided_cases"] == 1
    assert payload["transport_mapping_floor"][
        "cases_excluding_a_value_from_the_terminal_assertions_alone"
    ] == 945
    # Whole rules, not only single-case perturbations of one.
    assert payload["sampled_ambiguity_rules"] == [0, 5000]
    assert payload["sampled_bridge_rules"] == [0, 5000]
    assert payload["sampled_witness_only_ambiguity_rules"] == [5000, 5000]
    assert payload["composition_agreement"]["verdicts_moved"] is False


def test_the_audit_cli_exits_zero(capsys) -> None:
    assert main([]) == 0
    assert "P7 closure premises" in capsys.readouterr().out
    assert main(["--json"]) == 0
    assert json.loads(capsys.readouterr().out)["outcome"] == Outcome.PASS.value


# ---------------------------------------------------------------------------
# The donor-conservativity count: the guard that could not fire, and its repair
# ---------------------------------------------------------------------------


def test_the_old_conservativity_guard_compared_a_name_against_itself(tmp_path) -> None:
    """The defect, stated mechanically and kept as a regression.

    ``identity_guards`` walks the shipped file for an ``if x != y`` whose two
    names are related by an assignment in the same function. The closure-carrying
    checker had exactly one --- ``projected_native = native_valid`` immediately
    above ``if projected_native != native_valid`` --- and the audit blocks if one
    ever comes back.
    """

    assert premises.identity_guards(premises.CLOSURE_CARRYING_PATH) == ()

    tree = ast.parse(
        "def main():\n"
        "    total = 0\n"
        "    for native_valid in (False, True):\n"
        "        projected_native = native_valid\n"
        "        if projected_native != native_valid:\n"
        "            total += 1\n"
    )
    scratch = tmp_path / "identity_guard_probe.py"
    scratch.write_text(ast.unparse(tree), encoding="utf-8")
    assert premises.identity_guards(scratch) == ("main: projected_native != native_valid",)


def test_the_repaired_conservativity_count_rejects_the_donor_irrelevant_theory(
    closure_carrying,
) -> None:
    """The count fires, and it is the only claim in the file that does.

    ``closure_carries_without_a_valid_donor`` denies P7.V4.7's conservativity
    outright. Under the old guard the shipped script ran to completion and printed
    ``donor_conservativity_violations: 0``; under the projection it reports 5 --- one
    per donor family whose native verdict is invalid --- and the terminal is FAIL.
    Every measured quantity is unchanged, because their assertion blocks never
    leave ``native_valid=True``.
    """

    capacity = premises.donor_conservativity_capacity(closure_carrying)

    assert capacity["status"] == "CHECKED"
    assert capacity["violations"] == 0
    assert capacity["donor_transforms"] == 10
    assert capacity["distinct_donor_transforms"] == 2
    assert capacity["violations_under_the_donor_irrelevant_theory"] == 5
    assert capacity["terminal_under_the_donor_irrelevant_theory"] == "FAIL"
    assert len(capacity["counts_unchanged_under_the_donor_irrelevant_theory"]) == 7
    assert set(capacity["refuted"]) == {
        "closure_carries_without_a_valid_donor",
        "everything_carries",
        "nothing_carries",
        "donor_family_decides",
    }


def test_the_other_four_claims_still_accept_the_donor_irrelevant_theory(
    closure_carrying,
) -> None:
    """The panel is complete because a new claim covers those states, not an old one.

    Every assertion in the separation, countermodel and refinement blocks still
    evaluates the rule at ``native_valid=True``, so each still accepts a theory
    that drops the donor transform's own verdict. That is the finding, and it is
    what makes the conservativity count load-bearing rather than redundant.
    """

    capacities = premises.closure_carrying_capacities(closure_carrying)

    for check_id in (
        "single_coordinate_separation_witnesses",
        "donor_product_nonclosure_countermodels",
        "selective_closure_refinement",
    ):
        assert "closure_carries_without_a_valid_donor" in capacities[check_id].survivors, check_id
    assert (
        "closure_carries_without_a_valid_donor"
        in capacities[premises.DONOR_CONSERVATIVITY_COUNT].refuted
    )
    for capacity in capacities.values():
        assert capacity.refuted, capacity.check_id
        assert not capacity.blocks


def test_collapsing_the_two_sides_reports_cannot_check_rather_than_a_clean_zero(
    closure_carrying,
) -> None:
    """The durability gate: the repair is only as good as the distinction it made."""

    module = premises.closure_carrying_module()

    def carry_image_in_donor_language(donor_transform):
        _donor, native_valid = donor_transform
        return native_valid

    module.carry_image_in_donor_language = carry_image_in_donor_language
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        module.main()
    collapsed = json.loads(buffer.getvalue())

    assert collapsed["donor_conservativity_status"] == "CANNOT_CHECK"
    assert collapsed[premises.DONOR_CONSERVATIVITY_COUNT] is None
    assert collapsed["terminal"] == "CANNOT_CHECK"
    assert any("cannot refute any theory" in reason for reason in collapsed["cannot_check_reasons"])


def test_the_repaired_checker_publishes_the_same_counts_and_digest(
    closure_carrying, published
) -> None:
    """The repair changed what the checker claims, not what it found."""

    result = _run_shipped_closure_carrying(closure_carrying)

    for key in (
        "state_evaluations",
        "donor_conservativity_violations",
        "single_coordinate_separation_witnesses",
        "donor_product_nonclosure_countermodels",
        "full_closure_refinement_successes",
        "partial_closure_refinement_failures",
        "composition_successes",
        "composition_bridge_countermodels",
        "ideal_product_mismatches",
        "canonical_rows_sha256",
    ):
        assert result[key] == published[key], key
    assert result["canonical_rows_sha256"] == premises.SHIPPED_ROWS_SHA256
    assert result["terminal"] == published["terminal"] == "PASS"
    assert result["assertion_coverage_status"] == "COMPLETE"
    assert result["assertion_covered_states"] == result["assertion_state_space"] == 64
    assert result["assertion_covered_states_native_invalid"] == 32


def test_every_published_count_is_reported_with_its_multiplicity(closure_carrying) -> None:
    """320 is 64 observed five times, and the artifact has to say so.

    Measured by running the shipped checker at one donor family and at five, not
    read off the loop's shape.
    """

    table = premises.published_count_multiplicity(closure_carrying)
    rows = {row["count"]: row for row in table["rows"]}

    assert (rows["state_evaluations"]["published"], rows["state_evaluations"]["distinct"]) == (
        320,
        64,
    )
    assert rows["single_coordinate_separation_witnesses"]["published"] == 25
    assert rows["single_coordinate_separation_witnesses"]["distinct"] == 5
    assert rows["full_closure_refinement_successes"]["distinct"] == 31
    assert rows["partial_closure_refinement_failures"]["distinct"] == 211
    assert rows["composition_successes"]["distinct"] == 1
    assert rows["composition_bridge_countermodels"]["distinct"] == 1
    assert rows["composition_successes"]["factor"] == 25
    # The one count the donor loop does not touch.
    assert rows["donor_product_nonclosure_countermodels"]["factor"] == 1
    assert rows["donor_product_nonclosure_countermodels"]["distinct"] == 31

    published = json.loads(premises.CLOSURE_CARRYING_RESULT_PATH.read_text())
    axis = published["donor_axis"]
    assert axis["multiplier"] == 5
    assert axis["pair_multiplier"] == 25
    assert axis["read_by_carries_or_compose"] is False
    assert axis["distinct_state_evaluations"] == 64
    assert axis["distinct_separation_witnesses"] == 5
    assert axis["distinct_full_refinement_successes"] == 31
    assert axis["distinct_partial_refinement_failures"] == 211
    assert axis["distinct_composition_successes"] == 1
    assert axis["distinct_composition_bridge_countermodels"] == 1


def test_the_undecidable_premise_is_undecidable_by_construction(theory_closure) -> None:
    """Why, not only that. The proof the audit prints beside the CANNOT_CHECK.

    Definition 14 is one-to-many over the six transport coordinates: every one of
    the 64 coordinate states is paired with all 15 admissible completion classes,
    7 ambiguous and 8 not. So no rule over those coordinates alone reproduces the
    shipped decision, and the best one is wrong on 7 x 64 = 448 of the 960 cases.
    """

    proof = premises.witness_only_transport_undecidability(theory_closure)

    assert proof["check_id"] == premises.WITNESS_ONLY_TRANSPORT_CHECK_ID
    assert proof["cases"] == 960
    assert proof["coordinate_states"] == 64
    assert proof["coordinate_states_carrying_both_values"] == 64
    assert proof["ambiguous_classes_per_state"] == 7
    assert proof["unambiguous_classes_per_state"] == 8
    assert proof["minimum_cases_a_coordinate_rule_gets_wrong"] == 448
    assert proof["best_possible_agreement"] == 512
    assert proof["decidable_in_the_witness_only_model"] is False
    assert proof["decidable_in_the_shipped_space"] is True
