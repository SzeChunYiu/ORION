"""Architecture-neutral P9 M0 task adapters.

The adapter separates evaluator-only target/identity from model-visible context.
Mechanic selection is candidate-relative: a system must rank mechanics supplied
in the current world rather than predict a global mechanic-id class.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
from typing import Mapping

from orion.transfer.v2.canonical import content_digest

from .structural_world import (
    GluingVerdict,
    GoldKind,
    MechanicView,
    P9StructuralWorld,
    ViewMode,
)


class TaskKind(str, Enum):
    MECHANIC_RANKING = "MECHANIC_RANKING"
    GLUING = "GLUING"


@dataclass(frozen=True)
class CandidateInput:
    candidate_id: str
    payload: Mapping[str, object]

    def verify(self) -> None:
        if not self.candidate_id:
            raise ValueError("candidate id is required")
        if self.payload.get("candidate_id") != self.candidate_id:
            raise ValueError("candidate payload identity mismatch")


@dataclass(frozen=True)
class MechanicRankingTask:
    task_id: str
    kind: TaskKind
    mode: ViewMode
    context: Mapping[str, object]
    candidates: tuple[CandidateInput, ...]
    target_candidate_id: str

    def verify(self) -> None:
        if self.kind is not TaskKind.MECHANIC_RANKING:
            raise ValueError("mechanic task has wrong task kind")
        if not self.task_id:
            raise ValueError("task id is required")
        if not self.candidates:
            raise ValueError("mechanic task requires candidates")
        candidate_ids = [candidate.candidate_id for candidate in self.candidates]
        if len(candidate_ids) != len(set(candidate_ids)):
            raise ValueError("duplicate candidate id")
        for candidate in self.candidates:
            candidate.verify()
        if self.target_candidate_id not in set(candidate_ids):
            raise ValueError("target candidate is not present in current example")

    def model_payload(self) -> dict[str, object]:
        """Model-visible input only; excludes task id and target."""

        self.verify()
        return {
            "schema": "P9.MechanicRankingInput.v0",
            "kind": self.kind.value,
            "view_mode": self.mode.value,
            "context": dict(self.context),
            "candidates": [dict(candidate.payload) for candidate in self.candidates],
        }


@dataclass(frozen=True)
class GluingTask:
    task_id: str
    kind: TaskKind
    mode: ViewMode
    context: Mapping[str, object]
    target_label: str
    allowed_labels: tuple[str, ...] = tuple(verdict.value for verdict in GluingVerdict)

    def verify(self) -> None:
        if self.kind is not TaskKind.GLUING:
            raise ValueError("gluing task has wrong task kind")
        if not self.task_id:
            raise ValueError("task id is required")
        if self.target_label not in self.allowed_labels:
            raise ValueError("gluing target is outside fixed vocabulary")

    def model_payload(self) -> dict[str, object]:
        """Model-visible input only; excludes task id and target."""

        self.verify()
        return {
            "schema": "P9.GluingInput.v0",
            "kind": self.kind.value,
            "view_mode": self.mode.value,
            "context": dict(self.context),
            "allowed_labels": list(self.allowed_labels),
        }


P9Task = MechanicRankingTask | GluingTask


def _incidence_payload(mechanic: MechanicView) -> dict[str, object]:
    return {
        "read_atom_ids": list(sorted(set(mechanic.read_atom_ids))),
        "write_atom_ids": list(sorted(set(mechanic.write_atom_ids))),
    }


def _candidate_payload(mechanic: MechanicView, mode: ViewMode) -> dict[str, object]:
    incidence = _incidence_payload(mechanic)
    if mode is ViewMode.SURFACE:
        return {
            "candidate_id": mechanic.mechanic_id,
            "surface_label": mechanic.surface_label,
            **incidence,
        }
    if mode is ViewMode.TOPOLOGY:
        return {
            "candidate_id": mechanic.mechanic_id,
            **incidence,
        }
    if mode in (ViewMode.TYPED, ViewMode.CURRENT, ViewMode.SEMANTIC):
        return {
            "candidate_id": mechanic.mechanic_id,
            **incidence,
            "preconditions": list(sorted(set(mechanic.preconditions))),
            "effects": list(sorted(set(mechanic.effects))),
            "failure_modes": list(sorted(set(mechanic.failure_modes))),
            "cost": mechanic.cost,
        }
    raise ValueError(f"unsupported view mode: {mode}")


def _context_payload(world: P9StructuralWorld, mode: ViewMode) -> dict[str, object]:
    """Project one world while moving mechanic fields into candidate payloads.

    For SURFACE, the original world view carries mechanic incidence inside the
    nested topology object.  That incidence is removed from context and restored
    in each candidate payload so the adapter preserves the view's information
    while keeping candidates example-local.
    """

    payload = dict(world.view_payload(mode))
    payload.pop("mechanics", None)
    payload.pop("mechanic_incidence", None)
    topology = payload.get("topology")
    if isinstance(topology, dict):
        clean_topology = dict(topology)
        clean_topology.pop("mechanic_incidence", None)
        payload["topology"] = clean_topology
    return payload


def _candidate_order_key(
    *,
    order_seed: str,
    visible_view_fingerprint: str,
    candidate_id: str,
) -> str:
    """Order candidates using only information admitted by the declared view.

    A previous pre-execution design used the full SEMANTIC fingerprint here,
    which would leak hidden relation/transport/history coordinates into candidate
    presentation for weaker views.  Protocol V0.1 forbids that side channel.
    """

    material = f"{order_seed}|{visible_view_fingerprint}|{candidate_id}"
    return sha256(material.encode("utf-8")).hexdigest()


def _ordered_candidates(
    world: P9StructuralWorld,
    *,
    mode: ViewMode,
    order_seed: str,
) -> tuple[CandidateInput, ...]:
    if not order_seed:
        raise ValueError("candidate order seed is required")
    visible_view_fingerprint = world.fingerprint(mode)
    mechanics = sorted(
        world.mechanics,
        key=lambda mechanic: _candidate_order_key(
            order_seed=order_seed,
            visible_view_fingerprint=visible_view_fingerprint,
            candidate_id=mechanic.mechanic_id,
        ),
    )
    return tuple(
        CandidateInput(
            candidate_id=mechanic.mechanic_id,
            payload=_candidate_payload(mechanic, mode),
        )
        for mechanic in mechanics
    )


def build_task(
    world: P9StructuralWorld,
    *,
    mode: ViewMode,
    order_seed: str,
) -> P9Task:
    """Create one evaluator task from a verified world.

    `order_seed` is mandatory only for mechanic ranking.  It is accepted but not
    model-visible for gluing so callers may use one uniform adapter signature.
    """

    world.verify()
    context = _context_payload(world, mode)

    if world.gold.kind is GoldKind.MECHANIC_SELECTION:
        candidates = _ordered_candidates(world, mode=mode, order_seed=order_seed)
        task = MechanicRankingTask(
            task_id=content_digest(
                {
                    "schema": "P9.MechanicRankingTaskIdentity.v0.1",
                    "semantic_fingerprint": world.fingerprint(ViewMode.SEMANTIC),
                    "mode": mode.value,
                    "order_seed_digest": content_digest(order_seed),
                }
            ),
            kind=TaskKind.MECHANIC_RANKING,
            mode=mode,
            context=context,
            candidates=candidates,
            target_candidate_id=world.gold.value,
        )
        task.verify()
        return task

    if world.gold.kind is GoldKind.GLUING:
        task = GluingTask(
            task_id=content_digest(
                {
                    "schema": "P9.GluingTaskIdentity.v0.1",
                    "semantic_fingerprint": world.fingerprint(ViewMode.SEMANTIC),
                    "mode": mode.value,
                }
            ),
            kind=TaskKind.GLUING,
            mode=mode,
            context=context,
            target_label=world.gold.value,
        )
        task.verify()
        return task

    raise ValueError(f"unsupported P9 gold kind: {world.gold.kind}")


__all__ = [
    "CandidateInput",
    "GluingTask",
    "MechanicRankingTask",
    "P9Task",
    "TaskKind",
    "build_task",
]
