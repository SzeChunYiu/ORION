"""Exact model-independent hostile worlds for P9 structural learning.

This module deliberately contains no neural-network code.  It exists to freeze
information distinctions before model tuning, so later text / graph / sheaf /
neural-algorithmic / latent models can be compared on worlds where a restricted
view is provably non-identifying.

No object in this module grants scientific, novelty, adoption, or execution
authority.  Gold targets are evaluator-side only and are excluded from every
model-view fingerprint.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from hashlib import sha256
import math
from typing import Iterable, Sequence

from orion.transfer.v2.canonical import content_digest


class AtomType(str, Enum):
    CLAIM = "CLAIM"
    OBSERVATION = "OBSERVATION"
    REPRESENTATION = "REPRESENTATION"
    METHOD = "METHOD"
    EVIDENCE = "EVIDENCE"
    FAILURE = "FAILURE"
    UNKNOWN = "UNKNOWN"


class RelationType(str, Enum):
    SUPPORTS = "SUPPORTS"
    DEFEATS = "DEFEATS"
    DEPENDS_ON = "DEPENDS_ON"
    MAPS_TO = "MAPS_TO"
    PRODUCES = "PRODUCES"
    PRESERVES = "PRESERVES"


class GluingVerdict(str, Enum):
    GLUE = "GLUE"
    OBSTRUCTION = "OBSTRUCTION"
    UNKNOWN = "UNKNOWN"


class GoldKind(str, Enum):
    GLUING = "GLUING"
    MECHANIC_SELECTION = "MECHANIC_SELECTION"


class ViewMode(str, Enum):
    """Evaluator-controlled projections exposed to model families.

    `SURFACE` intentionally omits semantic types.
    `TOPOLOGY` retains only identities/connectivity/read-write incidence.
    `TYPED` adds atom/relation/mechanic semantics but not transport values/history.
    `CURRENT` adds full local transport values but excludes historical failures.
    `SEMANTIC` adds history while still excluding human-readable surface labels.

    Every view excludes `gold` and `world_id`.
    """

    SURFACE = "SURFACE"
    TOPOLOGY = "TOPOLOGY"
    TYPED = "TYPED"
    CURRENT = "CURRENT"
    SEMANTIC = "SEMANTIC"


def _unique(values: Iterable[str], *, what: str) -> None:
    seen: set[str] = set()
    for value in values:
        if not value:
            raise ValueError(f"empty {what} id")
        if value in seen:
            raise ValueError(f"duplicate {what} id: {value}")
        seen.add(value)


def _sorted_unique(values: Sequence[str]) -> tuple[str, ...]:
    return tuple(sorted({str(value) for value in values}))


@dataclass(frozen=True)
class Atom:
    atom_id: str
    atom_type: AtomType
    surface_label: str

    def verify(self) -> None:
        if not self.atom_id:
            raise ValueError("atom id is required")
        if not self.surface_label:
            raise ValueError("atom surface label is required")


@dataclass(frozen=True)
class Relation:
    relation_id: str
    source_id: str
    target_id: str
    relation_type: RelationType
    surface_label: str

    def verify(self) -> None:
        if not self.relation_id:
            raise ValueError("relation id is required")
        if not self.source_id or not self.target_id:
            raise ValueError("relation endpoints are required")
        if not self.surface_label:
            raise ValueError("relation surface label is required")


@dataclass(frozen=True)
class AffineTransport:
    """One-dimensional exact local-chart transport used by tranche-0 countermodels.

    The affine form is intentionally tiny.  It is not a claim that P9's eventual
    learned representation should be one-dimensional or affine; it merely creates
    exact cycle-consistency worlds where topology/types are held fixed while the
    local transport data changes.
    """

    transport_id: str
    source_chart_id: str
    target_chart_id: str
    scale: float
    offset: float

    def verify(self) -> None:
        if not self.transport_id:
            raise ValueError("transport id is required")
        if not self.source_chart_id or not self.target_chart_id:
            raise ValueError("transport endpoints are required")
        if not math.isfinite(self.scale) or not math.isfinite(self.offset):
            raise ValueError("transport values must be finite")


@dataclass(frozen=True)
class MechanicView:
    """Non-authorizing projection of a reusable mechanic for learning/evaluation."""

    mechanic_id: str
    surface_label: str
    read_atom_ids: tuple[str, ...] = ()
    write_atom_ids: tuple[str, ...] = ()
    preconditions: tuple[str, ...] = ()
    effects: tuple[str, ...] = ()
    failure_modes: tuple[str, ...] = ()
    cost: float = 0.0
    can_authorize: bool = False

    def verify(self) -> None:
        if not self.mechanic_id:
            raise ValueError("mechanic id is required")
        if not self.surface_label:
            raise ValueError("mechanic surface label is required")
        if self.cost < 0 or not math.isfinite(self.cost):
            raise ValueError("mechanic cost must be finite and non-negative")
        if self.can_authorize:
            raise ValueError("P9 mechanic view cannot authorize scientific or adoption state")


@dataclass(frozen=True)
class FailureRecord:
    record_id: str
    mechanic_id: str
    reason: str
    context_atom_ids: tuple[str, ...] = ()

    def verify(self) -> None:
        if not self.record_id:
            raise ValueError("failure record id is required")
        if not self.mechanic_id:
            raise ValueError("failure mechanic id is required")
        if not self.reason:
            raise ValueError("failure reason is required")


@dataclass(frozen=True)
class GoldTarget:
    """Evaluator-only target.  Never included in a model-view fingerprint."""

    kind: GoldKind
    value: str

    def verify(self) -> None:
        if not self.value:
            raise ValueError("gold target value is required")


@dataclass(frozen=True)
class P9StructuralWorld:
    world_id: str
    atoms: tuple[Atom, ...]
    relations: tuple[Relation, ...]
    transports: tuple[AffineTransport, ...]
    mechanics: tuple[MechanicView, ...]
    history: tuple[FailureRecord, ...]
    gold: GoldTarget

    def verify(self) -> None:
        if not self.world_id:
            raise ValueError("world id is required")
        self.gold.verify()

        _unique((atom.atom_id for atom in self.atoms), what="atom")
        _unique((relation.relation_id for relation in self.relations), what="relation")
        _unique((transport.transport_id for transport in self.transports), what="transport")
        _unique((mechanic.mechanic_id for mechanic in self.mechanics), what="mechanic")
        _unique((record.record_id for record in self.history), what="failure record")

        atom_by_id = {atom.atom_id: atom for atom in self.atoms}
        mechanic_by_id = {mechanic.mechanic_id: mechanic for mechanic in self.mechanics}

        for atom in self.atoms:
            atom.verify()

        for relation in self.relations:
            relation.verify()
            if relation.source_id not in atom_by_id:
                raise ValueError(f"relation references unknown source: {relation.source_id}")
            if relation.target_id not in atom_by_id:
                raise ValueError(f"relation references unknown target: {relation.target_id}")

        for transport in self.transports:
            transport.verify()
            source = atom_by_id.get(transport.source_chart_id)
            target = atom_by_id.get(transport.target_chart_id)
            if source is None:
                raise ValueError(
                    f"transport references unknown source chart: {transport.source_chart_id}"
                )
            if target is None:
                raise ValueError(
                    f"transport references unknown target chart: {transport.target_chart_id}"
                )
            if source.atom_type is not AtomType.REPRESENTATION:
                raise ValueError("transport source must be a REPRESENTATION atom")
            if target.atom_type is not AtomType.REPRESENTATION:
                raise ValueError("transport target must be a REPRESENTATION atom")

        for mechanic in self.mechanics:
            mechanic.verify()
            for atom_id in (*mechanic.read_atom_ids, *mechanic.write_atom_ids):
                if atom_id not in atom_by_id:
                    raise ValueError(
                        f"mechanic {mechanic.mechanic_id} references unknown atom: {atom_id}"
                    )

        for record in self.history:
            record.verify()
            if record.mechanic_id not in mechanic_by_id:
                raise ValueError(
                    f"failure history references unknown mechanic: {record.mechanic_id}"
                )
            for atom_id in record.context_atom_ids:
                if atom_id not in atom_by_id:
                    raise ValueError(
                        f"failure history references unknown context atom: {atom_id}"
                    )

        if self.gold.kind is GoldKind.MECHANIC_SELECTION:
            if self.gold.value not in mechanic_by_id:
                raise ValueError("mechanic-selection gold references unknown mechanic")
        elif self.gold.kind is GoldKind.GLUING:
            if self.gold.value not in {verdict.value for verdict in GluingVerdict}:
                raise ValueError("invalid gluing gold target")
        else:  # pragma: no cover - future enum extension guard
            raise ValueError(f"unsupported gold kind: {self.gold.kind}")

    def view_payload(self, mode: ViewMode) -> dict[str, object]:
        """Return one model-visible projection; evaluator gold is always excluded."""

        self.verify()

        atoms_surface = [
            [atom.atom_id, atom.surface_label]
            for atom in sorted(self.atoms, key=lambda item: item.atom_id)
        ]
        relations_surface = [
            [relation.source_id, relation.target_id, relation.surface_label]
            for relation in sorted(self.relations, key=lambda item: item.relation_id)
        ]
        mechanics_surface = [
            [mechanic.mechanic_id, mechanic.surface_label]
            for mechanic in sorted(self.mechanics, key=lambda item: item.mechanic_id)
        ]

        topology = {
            "atoms": [atom.atom_id for atom in sorted(self.atoms, key=lambda item: item.atom_id)],
            "relations": [
                [relation.source_id, relation.target_id]
                for relation in sorted(self.relations, key=lambda item: item.relation_id)
            ],
            "transport_endpoints": [
                [transport.source_chart_id, transport.target_chart_id]
                for transport in sorted(self.transports, key=lambda item: item.transport_id)
            ],
            "mechanic_incidence": [
                [
                    mechanic.mechanic_id,
                    list(_sorted_unique(mechanic.read_atom_ids)),
                    list(_sorted_unique(mechanic.write_atom_ids)),
                ]
                for mechanic in sorted(self.mechanics, key=lambda item: item.mechanic_id)
            ],
        }

        if mode is ViewMode.SURFACE:
            return {
                "version": "P9StructuralWorld.surface.v0",
                "atoms": atoms_surface,
                "relations": relations_surface,
                "mechanics": mechanics_surface,
                "topology": topology,
            }

        if mode is ViewMode.TOPOLOGY:
            return {"version": "P9StructuralWorld.topology.v0", **topology}

        typed = {
            "atoms": [
                [atom.atom_id, atom.atom_type.value]
                for atom in sorted(self.atoms, key=lambda item: item.atom_id)
            ],
            "relations": [
                [
                    relation.source_id,
                    relation.target_id,
                    relation.relation_type.value,
                ]
                for relation in sorted(self.relations, key=lambda item: item.relation_id)
            ],
            "transport_endpoints": topology["transport_endpoints"],
            "mechanics": [
                [
                    mechanic.mechanic_id,
                    list(_sorted_unique(mechanic.read_atom_ids)),
                    list(_sorted_unique(mechanic.write_atom_ids)),
                    list(_sorted_unique(mechanic.preconditions)),
                    list(_sorted_unique(mechanic.effects)),
                    list(_sorted_unique(mechanic.failure_modes)),
                    mechanic.cost,
                    False,
                ]
                for mechanic in sorted(self.mechanics, key=lambda item: item.mechanic_id)
            ],
        }
        if mode is ViewMode.TYPED:
            return {"version": "P9StructuralWorld.typed.v0", **typed}

        current = {
            **typed,
            "transports": [
                [
                    transport.source_chart_id,
                    transport.target_chart_id,
                    transport.scale,
                    transport.offset,
                ]
                for transport in sorted(self.transports, key=lambda item: item.transport_id)
            ],
        }
        if mode is ViewMode.CURRENT:
            return {"version": "P9StructuralWorld.current.v0", **current}

        if mode is ViewMode.SEMANTIC:
            return {
                "version": "P9StructuralWorld.semantic.v0",
                **current,
                "history": [
                    [
                        record.mechanic_id,
                        record.reason,
                        list(_sorted_unique(record.context_atom_ids)),
                    ]
                    for record in sorted(self.history, key=lambda item: item.record_id)
                ],
            }

        raise ValueError(f"unsupported view mode: {mode}")

    def fingerprint(self, mode: ViewMode) -> str:
        return content_digest(self.view_payload(mode))

    def permute_surface(self, *, seed: str) -> P9StructuralWorld:
        """Deterministically permute human-readable labels while preserving semantics."""

        self.verify()
        if not seed:
            raise ValueError("surface permutation seed is required")

        def rotate(labels: list[str], namespace: str) -> list[str]:
            if len(labels) <= 1:
                return labels[:]
            digest = sha256(f"{seed}:{namespace}".encode("utf-8")).hexdigest()
            offset = 1 + (int(digest[:8], 16) % (len(labels) - 1))
            return labels[offset:] + labels[:offset]

        atom_sorted = sorted(self.atoms, key=lambda item: item.atom_id)
        atom_labels = rotate([item.surface_label for item in atom_sorted], "atoms")
        atom_map = {
            item.atom_id: replace(item, surface_label=label)
            for item, label in zip(atom_sorted, atom_labels, strict=True)
        }

        relation_sorted = sorted(self.relations, key=lambda item: item.relation_id)
        relation_labels = rotate(
            [item.surface_label for item in relation_sorted], "relations"
        )
        relation_map = {
            item.relation_id: replace(item, surface_label=label)
            for item, label in zip(relation_sorted, relation_labels, strict=True)
        }

        mechanic_sorted = sorted(self.mechanics, key=lambda item: item.mechanic_id)
        mechanic_labels = rotate(
            [item.surface_label for item in mechanic_sorted], "mechanics"
        )
        mechanic_map = {
            item.mechanic_id: replace(item, surface_label=label)
            for item, label in zip(mechanic_sorted, mechanic_labels, strict=True)
        }

        out = replace(
            self,
            world_id=f"{self.world_id}:surface-permutation",
            atoms=tuple(atom_map[item.atom_id] for item in self.atoms),
            relations=tuple(relation_map[item.relation_id] for item in self.relations),
            mechanics=tuple(mechanic_map[item.mechanic_id] for item in self.mechanics),
        )
        out.verify()
        return out


def classify_cycle_gluing(
    world: P9StructuralWorld,
    cycle: Sequence[str],
    *,
    atol: float = 1e-9,
) -> GluingVerdict:
    """Classify one directed affine transport cycle.

    Missing or ambiguous local maps return `UNKNOWN`; a complete cycle glues only
    if its affine composition is identity within the declared numerical tolerance.
    """

    world.verify()
    if len(cycle) < 2 or cycle[0] != cycle[-1]:
        raise ValueError("cycle must contain at least one edge and return to its start")
    if atol < 0 or not math.isfinite(atol):
        raise ValueError("atol must be finite and non-negative")

    by_edge: dict[tuple[str, str], list[AffineTransport]] = {}
    for transport in world.transports:
        by_edge.setdefault(
            (transport.source_chart_id, transport.target_chart_id), []
        ).append(transport)

    scale = 1.0
    offset = 0.0
    for source, target in zip(cycle[:-1], cycle[1:], strict=True):
        candidates = by_edge.get((source, target), [])
        if len(candidates) != 1:
            return GluingVerdict.UNKNOWN
        transport = candidates[0]
        scale = transport.scale * scale
        offset = transport.scale * offset + transport.offset

    if math.isclose(scale, 1.0, abs_tol=atol, rel_tol=0.0) and math.isclose(
        offset, 0.0, abs_tol=atol, rel_tol=0.0
    ):
        return GluingVerdict.GLUE
    return GluingVerdict.OBSTRUCTION


def _verified(world: P9StructuralWorld) -> P9StructuralWorld:
    world.verify()
    return world


def relation_semantics_pair() -> tuple[P9StructuralWorld, P9StructuralWorld]:
    """Same labels/topology, different relation semantics and correct mechanic."""

    atoms = (
        Atom("problem", AtomType.CLAIM, "target statement"),
        Atom("evidence", AtomType.EVIDENCE, "observed result"),
    )
    mechanics = (
        MechanicView(
            mechanic_id="m_integrate",
            surface_label="combine available information",
            read_atom_ids=("problem", "evidence"),
            write_atom_ids=("problem",),
            preconditions=("evidence_relevant",),
            effects=("integrate_evidence",),
            failure_modes=("mapping_invalid",),
            cost=1.0,
        ),
        MechanicView(
            mechanic_id="m_reopen",
            surface_label="inspect the current conclusion",
            read_atom_ids=("problem", "evidence"),
            write_atom_ids=("problem",),
            preconditions=("evidence_relevant",),
            effects=("reopen_claim",),
            failure_modes=("defeater_not_material",),
            cost=1.0,
        ),
    )
    support = P9StructuralWorld(
        world_id="relation-support",
        atoms=atoms,
        relations=(
            Relation(
                "r_evidence_claim",
                "evidence",
                "problem",
                RelationType.SUPPORTS,
                "linked to",
            ),
        ),
        transports=(),
        mechanics=mechanics,
        history=(),
        gold=GoldTarget(GoldKind.MECHANIC_SELECTION, "m_integrate"),
    )
    defeat = replace(
        support,
        world_id="relation-defeat",
        relations=(
            Relation(
                "r_evidence_claim",
                "evidence",
                "problem",
                RelationType.DEFEATS,
                "linked to",
            ),
        ),
        gold=GoldTarget(GoldKind.MECHANIC_SELECTION, "m_reopen"),
    )
    return _verified(support), _verified(defeat)


def transport_gluing_pair() -> tuple[P9StructuralWorld, P9StructuralWorld]:
    """Same typed graph, different local transport values and global consistency."""

    atoms = (
        Atom("chart_a", AtomType.REPRESENTATION, "view alpha"),
        Atom("chart_b", AtomType.REPRESENTATION, "view beta"),
        Atom("chart_c", AtomType.REPRESENTATION, "view gamma"),
    )
    relations = (
        Relation("r_ab", "chart_a", "chart_b", RelationType.MAPS_TO, "translates"),
        Relation("r_bc", "chart_b", "chart_c", RelationType.MAPS_TO, "translates"),
        Relation("r_ca", "chart_c", "chart_a", RelationType.MAPS_TO, "translates"),
    )
    compatible = P9StructuralWorld(
        world_id="transport-compatible",
        atoms=atoms,
        relations=relations,
        transports=(
            AffineTransport("t_ab", "chart_a", "chart_b", 2.0, 1.0),
            AffineTransport("t_bc", "chart_b", "chart_c", 0.5, -0.5),
            AffineTransport("t_ca", "chart_c", "chart_a", 1.0, 0.0),
        ),
        mechanics=(),
        history=(),
        gold=GoldTarget(GoldKind.GLUING, GluingVerdict.GLUE.value),
    )
    obstructed = replace(
        compatible,
        world_id="transport-obstructed",
        transports=(
            AffineTransport("t_ab", "chart_a", "chart_b", 2.0, 1.0),
            AffineTransport("t_bc", "chart_b", "chart_c", 0.5, -0.5),
            AffineTransport("t_ca", "chart_c", "chart_a", 1.0, 1.0),
        ),
        gold=GoldTarget(GoldKind.GLUING, GluingVerdict.OBSTRUCTION.value),
    )
    return _verified(compatible), _verified(obstructed)


def failure_history_pair() -> tuple[P9StructuralWorld, P9StructuralWorld]:
    """Same current state/mechanics, different admitted negative history."""

    atoms = (
        Atom("problem", AtomType.CLAIM, "problem state"),
        Atom("observation", AtomType.OBSERVATION, "latest observation"),
    )
    mechanics = (
        MechanicView(
            mechanic_id="m_primary",
            surface_label="primary transformation",
            read_atom_ids=("problem", "observation"),
            write_atom_ids=("problem",),
            preconditions=("local_precondition",),
            effects=("candidate_progress",),
            failure_modes=("precondition_failed",),
            cost=1.0,
        ),
        MechanicView(
            mechanic_id="m_fallback",
            surface_label="fallback transformation",
            read_atom_ids=("problem", "observation"),
            write_atom_ids=("problem",),
            preconditions=("fallback_supported",),
            effects=("candidate_progress",),
            failure_modes=("fallback_failed",),
            cost=1.2,
        ),
    )
    clean = P9StructuralWorld(
        world_id="history-clean",
        atoms=atoms,
        relations=(
            Relation(
                "r_observation_problem",
                "observation",
                "problem",
                RelationType.DEPENDS_ON,
                "associated with",
            ),
        ),
        transports=(),
        mechanics=mechanics,
        history=(),
        gold=GoldTarget(GoldKind.MECHANIC_SELECTION, "m_primary"),
    )
    learned_failure = replace(
        clean,
        world_id="history-negative",
        history=(
            FailureRecord(
                "f_primary_precondition",
                "m_primary",
                "precondition_failed",
                ("problem", "observation"),
            ),
        ),
        gold=GoldTarget(GoldKind.MECHANIC_SELECTION, "m_fallback"),
    )
    return _verified(clean), _verified(learned_failure)
