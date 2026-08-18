"""Pre-confirmatory v2.2.1 world amendment for P1 mutation necessity.

The v2.2.0 generator remains untouched as design history.  This successor makes
all interventions one budget unit and plants high-level target-flip traps: on
half of hidden-shift worlds the highest-confidence high-level proposal restores
the motivating target but violates a protected sibling, while the second
high-level proposal is the valid mutation.  Gold is recomputed from the hidden
response matrix, never from a candidate policy.
"""

from __future__ import annotations

from dataclasses import replace
import hashlib

from .necessity_cases import (
    LEVEL_ORDER,
    NecessityProtectedWorld,
    NecessityWorld,
    PublicRepair,
    RepairLevel,
    RepairResponse,
    generate_necessity_worlds,
)


def _parity(task_id: str) -> int:
    return int(hashlib.sha256(task_id.encode()).hexdigest()[-1], 16) % 2


def _unit_cost(repair: PublicRepair) -> PublicRepair:
    return replace(repair, declared_cost=1.0)


def _amend_world(world: NecessityWorld) -> NecessityWorld:
    repairs = tuple(_unit_cost(item) for item in world.public.repairs)
    public = replace(world.public, repairs=repairs)
    protected = world.protected
    responses = dict(protected.response_by_repair)

    if protected.hidden_shift:
        high = sorted(
            (
                item
                for item in repairs
                if item.level in {RepairLevel.FORMULATION, RepairLevel.SEARCH_UNIVERSE}
            ),
            key=lambda item: (-item.proposal_confidence, item.repair_id),
        )
        if len(high) != 2:
            raise AssertionError("registered hidden world must expose two high-level proposals")
        safe = high[_parity(public.task_id)]
        for item in high:
            previous = responses[item.repair_id]
            responses[item.repair_id] = RepairResponse(
                target_success=True,
                protected_sibling_ok=item.repair_id == safe.repair_id,
                observed_invalidated_ids=previous.observed_invalidated_ids,
            )

    successful = [
        item
        for item in repairs
        if responses[item.repair_id].target_success
        and responses[item.repair_id].protected_sibling_ok
    ]
    if not successful:
        raise AssertionError("every registered world must have at least one valid repair")
    min_level = min(LEVEL_ORDER[item.level] for item in successful)
    minimal_ids = tuple(
        sorted(item.repair_id for item in successful if LEVEL_ORDER[item.level] == min_level)
    )
    gold_impact: tuple[str, ...] = ()
    if protected.hidden_shift:
        gold_impact = responses[minimal_ids[0]].observed_invalidated_ids

    protected_v2 = NecessityProtectedWorld(
        family_id=protected.family_id,
        true_level=protected.true_level,
        response_by_repair=tuple(
            (item.repair_id, responses[item.repair_id]) for item in repairs
        ),
        response_by_probe=protected.response_by_probe,
        gold_minimal_repair_ids=minimal_ids,
        gold_dependency_impact_ids=gold_impact,
        hidden_shift=protected.hidden_shift,
        negative_control=protected.negative_control,
    )
    return NecessityWorld(public, protected_v2)


def generate_necessity_worlds_v2(
    *,
    seed: int,
    hidden_shift_n: int = 480,
    control_n: int = 2400,
) -> tuple[NecessityWorld, ...]:
    return tuple(
        _amend_world(item)
        for item in generate_necessity_worlds(
            seed=seed,
            hidden_shift_n=hidden_shift_n,
            control_n=control_n,
        )
    )


__all__ = ["generate_necessity_worlds_v2"]
