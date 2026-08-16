from __future__ import annotations

import pytest

from orion.kernel.checks import claude_lane
from orion.kernel.gate import (
    CheckOutcome,
    DiscriminatingCheck,
    run_discriminating_check,
)
from orion.kernel.registry import CheckRegistryError, load_registered_checks
from orion.mechanics.model import MechanicCell, MechanicDimension
from orion.mechanics.program import current_program_cells


def _bare(mechanic_id: str, **fields) -> MechanicCell:
    return MechanicCell(mechanic_id=mechanic_id, purpose="p", scope="s", **fields)


def _target() -> MechanicCell:
    return next(
        cell
        for cell in current_program_cells()
        if cell.mechanic_id == "SEARCH.ROUTE_STOP.v0"
    )


def _check(predicate, negatives=()) -> DiscriminatingCheck:
    return DiscriminatingCheck(
        check_id="adv.check.v0",
        dimension=MechanicDimension.TRANSITION_MODEL,
        lane="adv",
        predicate=predicate,
        positive_fixture=_bare(
            "fixture.adv",
            transition_semantics=("typed outcomes GO_ON | STOP_HERE; deterministic in declared inputs",),
        ),
        negative_fixtures=tuple(negatives),
        frozen_at_round=0,
    )


def test_identity_keyed_predicate_is_inadmissible():
    """The attack demonstrated on the pre-hardening gate: separate battery from
    target by mechanic id, ignore content entirely. Target-derived members share
    the target's identity, so at least one is accepted and admission fails."""

    check = _check(lambda cell: not cell.mechanic_id.startswith(("battery.", "nearmiss.")))
    outcome, reasons = run_discriminating_check(check, _target())
    assert outcome is CheckOutcome.NOT_DISCRIMINATING, reasons


def test_fixture_prose_keyed_predicate_is_inadmissible():
    check = _check(lambda cell: "adversarial negative" not in cell.purpose and bool(cell.transition_semantics))
    outcome, reasons = run_discriminating_check(check, _target())
    assert outcome is CheckOutcome.NOT_DISCRIMINATING, reasons


def test_unrelated_field_keyed_predicate_is_inadmissible():
    """A TRANSITION_MODEL check keying on verification content: the emptied and
    junked members keep the target's verification field verbatim, so they are
    accepted and the check is refused."""

    # The positive fixture must satisfy the predicate, or soundness fires first
    # and the battery never gets a turn — the attack would go untested.
    check = DiscriminatingCheck(
        check_id="adv.check.v0",
        dimension=MechanicDimension.TRANSITION_MODEL,
        lane="adv",
        predicate=lambda cell: bool(cell.verification_contracts),
        positive_fixture=_bare(
            "fixture.adv",
            transition_semantics=("typed outcomes; deterministic in declared inputs",),
            verification_contracts=("an independent replay reproduces the transition",),
        ),
        frozen_at_round=0,
    )
    outcome, reasons = run_discriminating_check(check, _target())
    assert outcome is CheckOutcome.NOT_DISCRIMINATING, reasons


def test_registered_checks_remain_admissible_on_real_targets():
    """The no-alarm case: hardening must not reject the honest checks."""

    target_by_dimension = {
        MechanicDimension.TRANSITION_MODEL: _target(),
        MechanicDimension.MATHEMATICS: _target(),
        MechanicDimension.STATE: _target(),
        MechanicDimension.OBSERVABILITY: _target(),
        MechanicDimension.VERIFICATION: _target(),
        MechanicDimension.FAILURE: _target(),
    }
    for check in load_registered_checks().values():
        target = target_by_dimension.get(check.dimension, check.positive_fixture)
        outcome, reasons = run_discriminating_check(check, target)
        # An honest check may PASS or FAIL on a raw target (its content is seed
        # only), but it must never be refused as unsound or non-discriminating.
        assert outcome in (CheckOutcome.PASSED, CheckOutcome.FAILED), (
            check.check_id,
            outcome,
            reasons,
        )


def test_registry_rejects_checks_without_negative_fixtures(monkeypatch):
    stripped = tuple(
        DiscriminatingCheck(
            check_id=item.check_id,
            dimension=item.dimension,
            lane=item.lane,
            predicate=item.predicate,
            positive_fixture=item.positive_fixture,
            negative_fixtures=(),
            frozen_at_round=item.frozen_at_round,
        )
        for item in claude_lane.CHECKS[:1]
    )
    monkeypatch.setattr(claude_lane, "CHECKS", stripped)
    with pytest.raises(CheckRegistryError, match="failable"):
        load_registered_checks()
