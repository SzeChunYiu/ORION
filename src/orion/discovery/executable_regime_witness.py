"""Executable, non-authorizing regime witness for the bounded #501 benchmark.

A representation proposal is not yet an executable scientific object.  This
module compiles an already-proposed, correspondence-complete Jump proposal into
a small deterministic witness that can:

* replay the incumbent public-domain predictions (preservation),
* expose the introduced representation relation/new opaque object identities,
* derive the proposal's precommitted protected-consequence token.

Compilation does not establish that the move or consequence is scientifically
correct.  Those remain evaluator/authority decisions outside this object.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

from orion.transfer.v2.canonical import content_digest
from orion.discovery.zero_error_jump_benchmark import (
    JumpProposal,
    PublicJumpCase,
    RepresentationMove,
)


def _derived_id(case_id: str, move: RepresentationMove, old_id: str) -> str:
    raw = f"{case_id}|{move.value}|{old_id}|compiled-regime"
    return "new_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:14]


@dataclass(frozen=True)
class ExecutableRegimeWitness:
    case_id: str
    representation_move: RepresentationMove
    executable_axiom_ids: tuple[str, ...]
    old_to_new_object_map: tuple[tuple[str, str], ...]
    satisfied_correspondence_obligation_ids: tuple[str, ...]
    preserved_public_predictions: tuple[tuple[str, str], ...]
    precommitted_consequence_token: str
    validation_interface_ids: tuple[str, ...]
    digest: str

    @property
    def grants_scientific_validity(self) -> bool:
        return False

    @property
    def grants_novelty_authority(self) -> bool:
        return False

    @property
    def grants_adoption_authority(self) -> bool:
        return False

    def replay_public_domain(self) -> tuple[tuple[str, str], ...]:
        return self.preserved_public_predictions

    def derive_precommitted_consequence(self) -> str:
        return self.precommitted_consequence_token

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "ExecutableRegimeWitness.v1",
            "case_id": self.case_id,
            "representation_move": self.representation_move.value,
            "executable_axiom_ids": list(self.executable_axiom_ids),
            "old_to_new_object_map": [list(row) for row in self.old_to_new_object_map],
            "satisfied_correspondence_obligation_ids": list(
                self.satisfied_correspondence_obligation_ids
            ),
            "preserved_public_predictions": [
                list(row) for row in self.preserved_public_predictions
            ],
            "precommitted_consequence_token": self.precommitted_consequence_token,
            "validation_interface_ids": list(self.validation_interface_ids),
            "grants_scientific_validity": False,
            "grants_novelty_authority": False,
            "grants_adoption_authority": False,
        }

    def verify(self) -> None:
        if not self.case_id:
            raise ValueError("executable regime witness requires a case identity")
        if self.representation_move is RepresentationMove.NO_REPRESENTATION_CHANGE:
            raise ValueError("executable Jump witness requires a material representation move")
        if not self.executable_axiom_ids:
            raise ValueError("executable regime witness requires at least one axiom/rule identity")
        if not self.old_to_new_object_map:
            raise ValueError("executable regime witness requires an old/new object correspondence")
        if not self.satisfied_correspondence_obligation_ids:
            raise ValueError("executable regime witness requires correspondence obligations")
        if not self.preserved_public_predictions:
            raise ValueError("executable regime witness must preserve registered public behavior")
        if not self.precommitted_consequence_token:
            raise ValueError("executable regime witness requires a precommitted consequence")
        if not self.validation_interface_ids:
            raise ValueError("executable regime witness requires external validation interfaces")
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("executable regime witness digest mismatch")


def compile_executable_regime(
    public: PublicJumpCase,
    proposal: JumpProposal,
) -> ExecutableRegimeWitness:
    """Compile a correspondence-complete proposal without validating it.

    This function sees only candidate/public proposal material.  It has no gold
    representation move, protected simulator semantics, or evaluator terminal.
    """

    public.verify()
    if proposal.case_id != public.case_id:
        raise ValueError("proposal/public case identity mismatch")
    if not proposal.jump_requested:
        raise ValueError("no-Jump proposal cannot compile a successor regime")
    if proposal.representation_move is RepresentationMove.NO_REPRESENTATION_CHANGE:
        raise ValueError("material representation move is required")
    if not proposal.correspondence_complete:
        raise ValueError("proposal cannot compile before correspondence is complete")
    if not proposal.experiment_outcome or not proposal.protected_consequence_prediction:
        raise ValueError("proposal requires an outcome-bound precommitted consequence")

    object_map = tuple(
        (old_id, _derived_id(public.case_id, proposal.representation_move, old_id))
        for old_id in public.opaque_object_ids
    )
    axiom_ids = (
        f"axiom:{proposal.representation_move.value}",
        "axiom:PRESERVE_REGISTERED_PUBLIC_DOMAIN",
        "axiom:DERIVE_PRECOMMITTED_PROTECTED_CONSEQUENCE",
    )
    payload = {
        "version": "ExecutableRegimeWitness.v1",
        "case_id": public.case_id,
        "representation_move": proposal.representation_move.value,
        "executable_axiom_ids": list(axiom_ids),
        "old_to_new_object_map": [list(row) for row in object_map],
        "satisfied_correspondence_obligation_ids": list(
            public.correspondence_obligation_ids
        ),
        "preserved_public_predictions": [
            list(row) for row in public.incumbent_public_predictions
        ],
        "precommitted_consequence_token": proposal.protected_consequence_prediction,
        "validation_interface_ids": list(public.public_validation_interface_ids),
        "grants_scientific_validity": False,
        "grants_novelty_authority": False,
        "grants_adoption_authority": False,
    }
    witness = ExecutableRegimeWitness(
        case_id=payload["case_id"],
        representation_move=RepresentationMove(payload["representation_move"]),
        executable_axiom_ids=tuple(payload["executable_axiom_ids"]),
        old_to_new_object_map=tuple(
            tuple(row) for row in payload["old_to_new_object_map"]
        ),
        satisfied_correspondence_obligation_ids=tuple(
            payload["satisfied_correspondence_obligation_ids"]
        ),
        preserved_public_predictions=tuple(
            tuple(row) for row in payload["preserved_public_predictions"]
        ),
        precommitted_consequence_token=payload["precommitted_consequence_token"],
        validation_interface_ids=tuple(payload["validation_interface_ids"]),
        digest=content_digest(payload),
    )
    witness.verify()
    return witness


__all__ = ["ExecutableRegimeWitness", "compile_executable_regime"]
