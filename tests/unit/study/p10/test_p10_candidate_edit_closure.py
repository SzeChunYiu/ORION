"""Candidate edits against P10's frozen method-language closure.

The check that matters is the false closure: an edit using a token the grammar
does not contain while claiming to be inside it. That is method-language
escalation, and it is the failure the paper exists to detect.
"""

from __future__ import annotations

import pytest

from orion.study.p10.a0_control import ControllerArm, ProposalKind, Responsibility
from orion.study.p10.candidate_edit_closure import (
    EXIT_CANNOT_CHECK,
    EXIT_EXPANSION_UNNAMED,
    EXIT_FALSE_CLOSURE,
    EXIT_PASS,
    EXIT_UNDECLARED_EXPANSION,
    IN_CLOSURE,
    OUTSIDE_CLOSURE,
    check_candidate_edit,
    frozen_grammar,
    grammar_digest,
)


def test_the_grammar_is_read_from_the_live_enums_not_restated():
    """A restated grammar drifts; a derived one cannot."""

    g = frozen_grammar()
    assert set(g["responsibility"]) == {m.value for m in Responsibility}
    assert set(g["proposal_kind"]) == {m.value for m in ProposalKind}
    assert set(g["controller_arm"]) == {m.value for m in ControllerArm}


def test_the_grammar_digest_is_stable_and_order_independent():
    a = grammar_digest()
    shuffled = {k: tuple(reversed(v)) for k, v in frozen_grammar().items()}
    assert grammar_digest(shuffled) == a
    assert len(a) == 64


def test_a_widened_grammar_changes_the_digest():
    g = frozen_grammar()
    widened = dict(g)
    widened["proposal_kind"] = g["proposal_kind"] + ("INVENT_NEW_MOVE",)
    assert grammar_digest(widened) != grammar_digest(g)


# --- in closure ------------------------------------------------------------


@pytest.mark.parametrize("kind", [m.value for m in ProposalKind])
def test_every_frozen_proposal_kind_is_in_closure(kind):
    verdict = check_candidate_edit({"declared_position": IN_CLOSURE, "proposal_kind": kind})
    assert verdict.exit_code == EXIT_PASS
    assert verdict.position == IN_CLOSURE


@pytest.mark.parametrize("arm", [m.value for m in ControllerArm])
def test_every_frozen_controller_arm_is_in_closure(arm):
    assert check_candidate_edit({"declared_position": IN_CLOSURE, "controller_arm": arm}).exit_code == EXIT_PASS


def test_an_edit_touching_several_axes_at_once_passes():
    verdict = check_candidate_edit({
        "declared_position": IN_CLOSURE,
        "responsibility": "LOCAL_REPAIR",
        "proposal_kind": "LOCAL_REPAIR",
        "controller_arm": "ORION_RESPONSIBILITY_CONTROL",
    })
    assert verdict.exit_code == EXIT_PASS


# --- false closure: the failure the paper is about -------------------------


def test_an_out_of_grammar_token_claimed_in_closure_is_refused():
    verdict = check_candidate_edit({
        "declared_position": IN_CLOSURE,
        "proposal_kind": "INVENT_NEW_MOVE",
    })
    assert verdict.exit_code == EXIT_FALSE_CLOSURE
    assert verdict.terminal == "P10_FALSE_CLOSURE"
    assert ("proposal_kind", "INVENT_NEW_MOVE") in verdict.out_of_grammar


def test_a_false_closure_on_the_responsibility_axis_is_refused():
    verdict = check_candidate_edit({
        "declared_position": IN_CLOSURE,
        "responsibility": "ESCALATE_TO_OPERATOR",
    })
    assert verdict.exit_code == EXIT_FALSE_CLOSURE


def test_a_near_miss_spelling_is_still_out_of_grammar():
    """Closure is membership, not resemblance."""

    verdict = check_candidate_edit({"declared_position": IN_CLOSURE, "proposal_kind": "act"})
    assert verdict.exit_code == EXIT_FALSE_CLOSURE


# --- declared expansion ----------------------------------------------------


def test_a_declared_expansion_that_names_its_token_passes():
    verdict = check_candidate_edit({
        "declared_position": OUTSIDE_CLOSURE,
        "proposal_kind": "INVENT_NEW_MOVE",
        "expansion_tokens": ["INVENT_NEW_MOVE"],
    })
    assert verdict.exit_code == EXIT_PASS
    assert verdict.terminal == "P10_DECLARED_EXPANSION"
    assert verdict.position == OUTSIDE_CLOSURE


def test_an_expansion_naming_no_token_is_refused():
    """An expansion nobody can name cannot be witnessed."""

    verdict = check_candidate_edit({
        "declared_position": OUTSIDE_CLOSURE,
        "proposal_kind": "INVENT_NEW_MOVE",
    })
    assert verdict.exit_code == EXIT_EXPANSION_UNNAMED


def test_an_expansion_naming_the_wrong_token_is_refused():
    verdict = check_candidate_edit({
        "declared_position": OUTSIDE_CLOSURE,
        "proposal_kind": "INVENT_NEW_MOVE",
        "expansion_tokens": ["SOMETHING_ELSE"],
    })
    assert verdict.exit_code == EXIT_EXPANSION_UNNAMED
    assert "omits" in verdict.problems[0]


def test_declaring_an_expansion_that_is_not_one_is_refused():
    """Claiming OCME on ordinary vocabulary would inflate the OCME count."""

    verdict = check_candidate_edit({"declared_position": OUTSIDE_CLOSURE, "proposal_kind": "ACT"})
    assert verdict.exit_code == EXIT_UNDECLARED_EXPANSION
    assert verdict.terminal == "P10_SPURIOUS_EXPANSION"


# --- cannot check ----------------------------------------------------------


@pytest.mark.parametrize("bad", [None, "edit", 7, [], {}, {"proposal_kind": "ACT"},
                                 {"declared_position": "MAYBE"}])
def test_a_malformed_edit_cannot_be_checked_and_never_passes(bad):
    verdict = check_candidate_edit(bad)
    assert verdict.exit_code == EXIT_CANNOT_CHECK
    assert not verdict.passed


def test_a_non_string_token_cannot_be_checked():
    assert check_candidate_edit(
        {"declared_position": IN_CLOSURE, "proposal_kind": 5}
    ).exit_code == EXIT_CANNOT_CHECK


def test_each_failure_mode_has_its_own_exit_code():
    assert len({EXIT_PASS, EXIT_FALSE_CLOSURE, EXIT_UNDECLARED_EXPANSION,
                EXIT_EXPANSION_UNNAMED, EXIT_CANNOT_CHECK}) == 5
