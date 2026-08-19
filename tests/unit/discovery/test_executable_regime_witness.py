from __future__ import annotations

import json
from pathlib import Path

import pytest

from orion.discovery.executable_regime_witness import compile_executable_regime
from orion.discovery.zero_error_jump_benchmark import (
    JumpArm,
    generate_jump_worlds,
    propose,
    public_projection,
)


ROOT = Path(__file__).resolve().parents[3]
PROTOCOL = (
    ROOT
    / "research"
    / "extensions"
    / "orion-jump-recursive-atoms"
    / "zero_error_jump"
    / "ZERO_ERROR_JUMP_PROTOCOL_V2.json"
)


def _protocol() -> dict[str, object]:
    return json.loads(PROTOCOL.read_text(encoding="utf-8"))


def _positive_world():
    protocol = _protocol()
    return next(
        world
        for world in generate_jump_worlds(
            seed=protocol["seeds"]["primary"], split_id="primary"
        )
        if world.is_jump_case
    )


def test_parent_and_orion_compile_same_executable_successor_semantics() -> None:
    world = _positive_world()
    public = public_projection(world)

    parent = compile_executable_regime(
        public,
        propose(world, JumpArm.VERIFIED_REGIME_REVISION_PARENT),
    )
    orion = compile_executable_regime(
        public,
        propose(world, JumpArm.ORION_JUMP),
    )

    assert parent.unsigned() == orion.unsigned()
    assert parent.replay_public_domain() == public.incumbent_public_predictions
    assert parent.derive_precommitted_consequence() == world.protected_novel_consequence_token
    assert parent.old_to_new_object_map
    assert parent.satisfied_correspondence_obligation_ids == public.correspondence_obligation_ids
    assert parent.validation_interface_ids == public.public_validation_interface_ids
    assert parent.grants_scientific_validity is False
    assert parent.grants_novelty_authority is False
    assert parent.grants_adoption_authority is False


def test_correspondence_incomplete_proposal_cannot_compile_successor() -> None:
    world = _positive_world()
    public = public_projection(world)
    proposal = propose(world, JumpArm.ORION_NO_CORRESPONDENCE)

    with pytest.raises(ValueError, match="correspondence"):
        compile_executable_regime(public, proposal)


def test_no_jump_control_does_not_compile_a_successor_regime() -> None:
    protocol = _protocol()
    world = next(
        world
        for world in generate_jump_worlds(
            seed=protocol["seeds"]["primary"], split_id="primary"
        )
        if not world.is_jump_case
    )
    public = public_projection(world)
    proposal = propose(world, JumpArm.ORION_JUMP)

    assert proposal.selected_experiment_id == world.informative_experiment_id
    assert proposal.experiment_outcome == world.informative_outcome
    assert proposal.jump_requested is False
    with pytest.raises(ValueError, match="no-Jump"):
        compile_executable_regime(public, proposal)
