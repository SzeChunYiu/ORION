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
    DecidedResult,
    DecisionReason,
    UndecidedPremise,
    decision_outcome,
    require_decided,
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


def test_the_transport_theorem_never_constrains_its_ambiguity_premise(theory_closure) -> None:
    constraint = premises.transport_constraint(theory_closure)

    assert len(constraint.cases) == premises.SHIPPED_TRANSPORT_CASES == 64
    assert len(constraint.free_case_ids) == 64
    assert constraint.decided_case_ids == ()
    assert constraint.admissible_assignments == 2**64
    assert constraint.reason is DecisionReason.UNDECIDABLE_IN_MODEL
    assert constraint.outcome is Outcome.CANNOT_CHECK


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


def test_the_composition_block_supplies_its_bridge_on_every_donor_pair(closure_carrying) -> None:
    constraint = premises.composition_constraint(closure_carrying)

    assert len(constraint.cases) == 25
    assert len(constraint.free_case_ids) == 25
    assert constraint.admissible_assignments == 2**25 == 33_554_432
    assert constraint.reason is DecisionReason.PREMISE_SUPPLIED
    assert constraint.outcome is Outcome.FAIL
    # Both donors are axes of the enumerated space, so this one could have been
    # decided here; that is what separates FAIL from the transport CANNOT_CHECK.
    assert constraint.modelled is True


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


def test_the_published_counts_cannot_be_held_as_a_result(theory_closure, closure_carrying) -> None:
    constraints = (
        premises.transport_constraint(theory_closure),
        premises.composition_constraint(closure_carrying),
    )

    assert decision_outcome(constraints) is Outcome.FAIL
    with pytest.raises(UndecidedPremise, match="cannot report"):
        DecidedResult(
            result_id="P7.V3.7",
            reported=(("composition_successes", 25), ("composition_bridge_countermodels", 25)),
            constraints=constraints,
        )
    with pytest.raises(UndecidedPremise) as excinfo:
        require_decided(constraints, label="P7.V3.5 / P7 C4")
    assert "bridge_match" in str(excinfo.value)
    assert "target_ambiguous_if_missing" in str(excinfo.value)


def test_the_audit_runs_against_the_shipped_files_and_blocks() -> None:
    report = audit_p7_closure_checkers()
    payload = report_as_json(report)

    assert payload["canonical_rows_reproduced"] is True
    assert payload["outcome"] == Outcome.FAIL.value
    assert payload["compose_rules_accepted"] == 64
    assert {item["reason"] for item in payload["constraints"]} == {
        DecisionReason.UNDECIDABLE_IN_MODEL.value,
        DecisionReason.PREMISE_SUPPLIED.value,
    }
    assert payload["transport_capacity"]["outcome"] == Outcome.PASS.value
    # Whole ambiguity rules, not only single-case perturbations of one.
    assert payload["sampled_ambiguity_rules"] == [5000, 5000]


def test_the_audit_cli_exits_three(capsys) -> None:
    assert main([]) == 3
    assert "P7 closure premises" in capsys.readouterr().out
    assert main(["--json"]) == 3
    assert json.loads(capsys.readouterr().out)["outcome"] == Outcome.FAIL.value
