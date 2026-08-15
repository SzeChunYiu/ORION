import pytest

from orion.development.protocol import (
    BasisChallenge,
    DevelopmentAtom,
    DevelopmentImpact,
    DevelopmentPacket,
    assert_ready_to_implement,
)
from orion.engine.operators.saturate import SaturationAssessment, SaturationStatus


def _saturated():
    return SaturationAssessment(
        status=SaturationStatus.BOUNDED_SATURATED,
        semantic_flat_rounds=2,
        search_universe_flat_rounds=2,
        formulation_flat_rounds=2,
        covered_route_kind_ids=("CURRENT_VOCABULARY",),
        missing_route_kind_ids=(),
        reasons=(),
    )


def _challenge():
    return BasisChallenge(
        challenge_id="basis:1",
        saturation_could_be_false_if=("a parent discipline remains outside W",),
        potentially_missing_parent_domains=("unknown",),
        prior_miss_hypotheses=("routing stayed inside incumbent vocabulary",),
        reopen_triggers=("new domain changes the decomposition",),
    )


def test_high_impact_development_fails_without_saturation():
    packet = DevelopmentPacket(
        task_id="dev:1",
        impact=DevelopmentImpact.HIGH,
        atoms=(DevelopmentAtom("atom:1", "what is the correct mechanic?"),),
        saturation=None,
        basis_challenge=_challenge(),
        implementation_hypothesis="implement a typed operator",
    )
    with pytest.raises(ValueError, match="requires bounded"):
        assert_ready_to_implement(packet)


def test_high_impact_development_requires_basis_challenge():
    packet = DevelopmentPacket(
        task_id="dev:2",
        impact=DevelopmentImpact.HIGH,
        atoms=(DevelopmentAtom("atom:1", "what is the correct mechanic?"),),
        saturation=_saturated(),
        basis_challenge=None,
        implementation_hypothesis="implement a typed operator",
    )
    with pytest.raises(ValueError, match="basis challenge"):
        assert_ready_to_implement(packet)


def test_saturated_atomized_packet_can_implement():
    packet = DevelopmentPacket(
        task_id="dev:3",
        impact=DevelopmentImpact.HIGH,
        atoms=(DevelopmentAtom("atom:1", "what is the correct mechanic?"),),
        saturation=_saturated(),
        basis_challenge=_challenge(),
        implementation_hypothesis="implement a typed operator",
    )
    assert_ready_to_implement(packet)
