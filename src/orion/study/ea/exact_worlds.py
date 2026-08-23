"""Exact causal-belief-surgery worlds for ORION-EA EA-1A.

The module freezes deterministic epistemic-update semantics before any learned
model is trained.  The exact kernel is evaluator infrastructure and grants no
scientific, novelty, execution, or adoption authority.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from hashlib import sha256
import json
from typing import Iterable


class NodeKind(str, Enum):
    EVIDENCE = "EVIDENCE"
    CLAIM = "CLAIM"
    METHOD = "METHOD"
    FAILURE = "FAILURE"
    OBLIGATION = "OBLIGATION"


class NodeStatus(str, Enum):
    ACTIVE = "ACTIVE"
    RETRACTED = "RETRACTED"
    BLOCKED = "BLOCKED"
    UNKNOWN = "UNKNOWN"
    STALE = "STALE"


class EdgeKind(str, Enum):
    SUPPORTS = "SUPPORTS"
    REQUIRES = "REQUIRES"
    DEFEATS = "DEFEATS"


class InterventionKind(str, Enum):
    RETRACT = "RETRACT"
    ACTIVATE = "ACTIVATE"
    MARK_UNKNOWN = "MARK_UNKNOWN"
    CHANGE_REPRESENTATION = "CHANGE_REPRESENTATION"


class DeltaKind(str, Enum):
    SET_STATUS = "SET_STATUS"
    SET_REPRESENTATION = "SET_REPRESENTATION"


class ViewMode(str, Enum):
    """Evaluator-controlled model views.

    TYPED hides representation semantic keys and failure/obligation scope.
    FULL exposes every EA-1A state coordinate except evaluator family/gold.
    """

    SURFACE = "SURFACE"
    TOPOLOGY = "TOPOLOGY"
    TYPED = "TYPED"
    FULL = "FULL"


class ExactFamily(str, Enum):
    SPARSE_RETRACTION = "SPARSE_RETRACTION"
    INDEPENDENT_SUPPORT = "INDEPENDENT_SUPPORT"
    ACTIVE_DEFEATER = "ACTIVE_DEFEATER"
    FAILURE_REOPEN_MATERIAL = "FAILURE_REOPEN_MATERIAL"
    FAILURE_REOPEN_REMINT = "FAILURE_REOPEN_REMINT"
    OBLIGATION_NONTRANSPORT = "OBLIGATION_NONTRANSPORT"
    OBLIGATION_TRANSPORT = "OBLIGATION_TRANSPORT"
    UNKNOWN_PROPAGATION = "UNKNOWN_PROPAGATION"
    IRRELEVANT_RETRACTION = "IRRELEVANT_RETRACTION"


def _digest(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return sha256(payload.encode("utf-8")).hexdigest()


def _opaque(prefix: str, material: str, *, length: int = 16) -> str:
    if len(prefix) != 1 or not prefix.islower() or not prefix.isalpha():
        raise ValueError("opaque prefix must be one lowercase letter")
    if not material:
        raise ValueError("opaque material is required")
    return prefix + sha256(material.encode("utf-8")).hexdigest()[:length]


def _tok(seed: str, namespace: str, slot: str, prefix: str) -> str:
    return _opaque(prefix, f"{seed}|{namespace}|{slot}")


@dataclass(frozen=True)
class Representation:
    representation_id: str
    semantic_key: str

    def verify(self) -> None:
        if not self.representation_id or not self.semantic_key:
            raise ValueError("representation id and semantic key are required")


@dataclass(frozen=True)
class EpistemicNode:
    node_id: str
    kind: NodeKind
    status: NodeStatus
    surface_label: str

    def verify(self) -> None:
        if not self.node_id or not self.surface_label:
            raise ValueError("node id and surface label are required")


@dataclass(frozen=True)
class EpistemicEdge:
    edge_id: str
    source_id: str
    target_id: str
    kind: EdgeKind
    surface_label: str

    def verify(self) -> None:
        if not self.edge_id or not self.source_id or not self.target_id:
            raise ValueError("edge identity/endpoints are required")
        if not self.surface_label:
            raise ValueError("edge surface label is required")


@dataclass(frozen=True)
class FailureScope:
    failure_id: str
    required_semantic_key: str
    reopen_on_semantic_change: bool = True


@dataclass(frozen=True)
class ObligationScope:
    obligation_id: str
    required_semantic_key: str
    transportable: bool = False


@dataclass(frozen=True)
class EpistemicIntervention:
    kind: InterventionKind
    target_id: str | None = None
    new_representation: Representation | None = None

    def verify(self) -> None:
        if self.kind is InterventionKind.CHANGE_REPRESENTATION:
            if self.target_id is not None or self.new_representation is None:
                raise ValueError("representation change requires only new_representation")
            self.new_representation.verify()
        elif not self.target_id or self.new_representation is not None:
            raise ValueError("node intervention requires only target_id")


@dataclass(frozen=True, order=True)
class DeltaOp:
    kind: DeltaKind
    target_id: str
    value: str

    def verify(self) -> None:
        if not self.target_id or not self.value:
            raise ValueError("delta target/value are required")
        if self.kind is DeltaKind.SET_STATUS:
            NodeStatus(self.value)


@dataclass(frozen=True)
class EpistemicWorld:
    world_id: str
    representation: Representation
    nodes: tuple[EpistemicNode, ...]
    edges: tuple[EpistemicEdge, ...]
    failure_scopes: tuple[FailureScope, ...] = ()
    obligation_scopes: tuple[ObligationScope, ...] = ()

    def verify(self) -> None:
        if not self.world_id:
            raise ValueError("world id is required")
        self.representation.verify()
        node_ids = [node.node_id for node in self.nodes]
        edge_ids = [edge.edge_id for edge in self.edges]
        if len(node_ids) != len(set(node_ids)):
            raise ValueError("duplicate node id")
        if len(edge_ids) != len(set(edge_ids)):
            raise ValueError("duplicate edge id")
        by_id = {node.node_id: node for node in self.nodes}
        for node in self.nodes:
            node.verify()
        for edge in self.edges:
            edge.verify()
            if edge.source_id not in by_id or edge.target_id not in by_id:
                raise ValueError("edge references unknown node")
        for scope in self.failure_scopes:
            node = by_id.get(scope.failure_id)
            if node is None or node.kind is not NodeKind.FAILURE:
                raise ValueError("failure scope must reference FAILURE node")
            if not scope.required_semantic_key:
                raise ValueError("failure scope semantic key is required")
        for scope in self.obligation_scopes:
            node = by_id.get(scope.obligation_id)
            if node is None or node.kind is not NodeKind.OBLIGATION:
                raise ValueError("obligation scope must reference OBLIGATION node")
            if not scope.required_semantic_key:
                raise ValueError("obligation scope semantic key is required")

    def node_map(self) -> dict[str, EpistemicNode]:
        self.verify()
        return {node.node_id: node for node in self.nodes}

    def view_payload(self, mode: ViewMode) -> dict[str, object]:
        self.verify()
        if mode is ViewMode.SURFACE:
            return {
                "schema": "EA.EpistemicWorld.surface.v0",
                "nodes": [
                    [node.node_id, node.surface_label]
                    for node in sorted(self.nodes, key=lambda item: item.node_id)
                ],
                "edges": [
                    [edge.source_id, edge.target_id, edge.surface_label]
                    for edge in sorted(self.edges, key=lambda item: item.edge_id)
                ],
                "representation_id": self.representation.representation_id,
            }
        if mode is ViewMode.TOPOLOGY:
            return {
                "schema": "EA.EpistemicWorld.topology.v0",
                "nodes": [node.node_id for node in sorted(self.nodes, key=lambda item: item.node_id)],
                "edges": [
                    [edge.source_id, edge.target_id]
                    for edge in sorted(self.edges, key=lambda item: item.edge_id)
                ],
                "representation_id": self.representation.representation_id,
            }
        typed = {
            "nodes": [
                [node.node_id, node.kind.value, node.status.value]
                for node in sorted(self.nodes, key=lambda item: item.node_id)
            ],
            "edges": [
                [edge.source_id, edge.target_id, edge.kind.value]
                for edge in sorted(self.edges, key=lambda item: item.edge_id)
            ],
            "representation_id": self.representation.representation_id,
        }
        if mode is ViewMode.TYPED:
            return {"schema": "EA.EpistemicWorld.typed.v0", **typed}
        if mode is ViewMode.FULL:
            return {
                "schema": "EA.EpistemicWorld.full.v0",
                **typed,
                "representation_semantic_key": self.representation.semantic_key,
                "failure_scopes": [
                    [scope.failure_id, scope.required_semantic_key, scope.reopen_on_semantic_change]
                    for scope in sorted(self.failure_scopes, key=lambda item: item.failure_id)
                ],
                "obligation_scopes": [
                    [scope.obligation_id, scope.required_semantic_key, scope.transportable]
                    for scope in sorted(self.obligation_scopes, key=lambda item: item.obligation_id)
                ],
            }
        raise ValueError(f"unsupported view mode: {mode}")

    def fingerprint(self, mode: ViewMode) -> str:
        return _digest(self.view_payload(mode))


@dataclass(frozen=True)
class ExactCase:
    family: ExactFamily
    case_id: str
    pre_state: EpistemicWorld
    intervention: EpistemicIntervention
    post_state: EpistemicWorld
    gold_delta: tuple[DeltaOp, ...]

    def verify(self) -> None:
        if not self.case_id:
            raise ValueError("case id is required")
        self.pre_state.verify()
        self.intervention.verify()
        self.post_state.verify()
        for op in self.gold_delta:
            op.verify()
        replay_post, replay_delta = execute_intervention(self.pre_state, self.intervention)
        if replay_post != self.post_state or replay_delta != self.gold_delta:
            raise ValueError("case gold does not replay through exact kernel")
        if self.intervention.new_representation is None:
            replayed = apply_delta(self.pre_state, self.gold_delta)
        else:
            replayed = apply_delta_with_representation(
                self.pre_state,
                self.gold_delta,
                self.intervention.new_representation,
            )
        if replayed != self.post_state:
            raise ValueError("gold delta does not reconstruct post-state")

    def model_payload(self, mode: ViewMode) -> dict[str, object]:
        """Return pre-state + intervention without evaluator family/case/gold."""
        self.verify()
        intervention: dict[str, object] = {"kind": self.intervention.kind.value}
        if self.intervention.target_id is not None:
            intervention["target_id"] = self.intervention.target_id
        if self.intervention.new_representation is not None:
            intervention["new_representation_id"] = self.intervention.new_representation.representation_id
            if mode is ViewMode.FULL:
                intervention["new_representation_semantic_key"] = (
                    self.intervention.new_representation.semantic_key
                )
        return {
            "schema": f"EA.ExactCase.{mode.value.lower()}.v0",
            "pre_state": self.pre_state.view_payload(mode),
            "intervention": intervention,
        }

    def fingerprint(self, mode: ViewMode) -> str:
        return _digest(self.model_payload(mode))

    def manifest(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "EA.ExactCase.evaluator.v0",
            "family": self.family.value,
            "case_id": self.case_id,
            "gold_delta": [[op.kind.value, op.target_id, op.value] for op in self.gold_delta],
            "full_fingerprint": self.fingerprint(ViewMode.FULL),
        }


def _propagate(
    nodes: dict[str, EpistemicNode],
    edges: tuple[EpistemicEdge, ...],
) -> dict[str, EpistemicNode]:
    nodes = dict(nodes)
    changed = True
    while changed:
        changed = False
        for target_id in sorted(nodes):
            target = nodes[target_id]
            if target.kind not in {NodeKind.CLAIM, NodeKind.METHOD}:
                continue
            incoming = [edge for edge in edges if edge.target_id == target_id]
            active_defeaters = [
                edge
                for edge in incoming
                if edge.kind is EdgeKind.DEFEATS
                and nodes[edge.source_id].status is NodeStatus.ACTIVE
            ]
            requirements = [edge for edge in incoming if edge.kind is EdgeKind.REQUIRES]
            supports = [edge for edge in incoming if edge.kind is EdgeKind.SUPPORTS]
            new_status = target.status
            if active_defeaters:
                new_status = NodeStatus.BLOCKED if target.kind is NodeKind.METHOD else NodeStatus.RETRACTED
            elif any(
                nodes[edge.source_id].status in {NodeStatus.RETRACTED, NodeStatus.BLOCKED}
                for edge in requirements
            ):
                new_status = NodeStatus.RETRACTED
            elif any(nodes[edge.source_id].status is NodeStatus.UNKNOWN for edge in requirements):
                new_status = NodeStatus.UNKNOWN
            elif supports:
                support_statuses = [nodes[edge.source_id].status for edge in supports]
                if NodeStatus.ACTIVE in support_statuses:
                    new_status = NodeStatus.ACTIVE
                elif NodeStatus.UNKNOWN in support_statuses:
                    new_status = NodeStatus.UNKNOWN
                else:
                    new_status = NodeStatus.RETRACTED
            elif target.kind is NodeKind.METHOD and target.status is NodeStatus.BLOCKED:
                new_status = NodeStatus.ACTIVE
            if new_status is not target.status:
                nodes[target_id] = replace(target, status=new_status)
                changed = True
    return nodes


def execute_intervention(
    world: EpistemicWorld,
    intervention: EpistemicIntervention,
) -> tuple[EpistemicWorld, tuple[DeltaOp, ...]]:
    """Apply evaluator intervention and exact V0 fixed-point revision semantics."""
    world.verify()
    intervention.verify()
    before = world.node_map()
    nodes = dict(before)
    representation = world.representation

    if intervention.kind is InterventionKind.RETRACT:
        node = nodes[intervention.target_id]
        nodes[intervention.target_id] = replace(node, status=NodeStatus.RETRACTED)
    elif intervention.kind is InterventionKind.ACTIVATE:
        node = nodes[intervention.target_id]
        nodes[intervention.target_id] = replace(node, status=NodeStatus.ACTIVE)
    elif intervention.kind is InterventionKind.MARK_UNKNOWN:
        node = nodes[intervention.target_id]
        nodes[intervention.target_id] = replace(node, status=NodeStatus.UNKNOWN)
    elif intervention.kind is InterventionKind.CHANGE_REPRESENTATION:
        assert intervention.new_representation is not None
        old_representation = representation
        representation = intervention.new_representation
        semantic_changed = old_representation.semantic_key != representation.semantic_key
        if semantic_changed:
            for scope in world.failure_scopes:
                if (
                    scope.reopen_on_semantic_change
                    and scope.required_semantic_key == old_representation.semantic_key
                ):
                    node = nodes[scope.failure_id]
                    nodes[scope.failure_id] = replace(node, status=NodeStatus.STALE)
            for scope in world.obligation_scopes:
                if (
                    scope.required_semantic_key == old_representation.semantic_key
                    and not scope.transportable
                ):
                    node = nodes[scope.obligation_id]
                    nodes[scope.obligation_id] = replace(node, status=NodeStatus.UNKNOWN)
    else:  # pragma: no cover
        raise ValueError(f"unsupported intervention: {intervention.kind}")

    nodes = _propagate(nodes, world.edges)
    post_state = replace(
        world,
        representation=representation,
        nodes=tuple(nodes[node.node_id] for node in world.nodes),
    )
    post_state.verify()

    delta: list[DeltaOp] = []
    if representation != world.representation:
        delta.append(DeltaOp(DeltaKind.SET_REPRESENTATION, "representation", representation.representation_id))
    for node_id in sorted(before):
        if before[node_id].status != nodes[node_id].status:
            delta.append(DeltaOp(DeltaKind.SET_STATUS, node_id, nodes[node_id].status.value))
    return post_state, tuple(sorted(delta))


def apply_delta(world: EpistemicWorld, delta: Iterable[DeltaOp]) -> EpistemicWorld:
    """Apply a delta that contains no representation-semantic change."""
    world.verify()
    nodes = world.node_map()
    representation = world.representation
    for op in tuple(delta):
        op.verify()
        if op.kind is DeltaKind.SET_STATUS:
            node = nodes[op.target_id]
            nodes[op.target_id] = replace(node, status=NodeStatus(op.value))
        elif op.kind is DeltaKind.SET_REPRESENTATION:
            if op.value != representation.representation_id:
                raise ValueError("representation semantics require evaluator binding")
    return replace(world, nodes=tuple(nodes[node.node_id] for node in world.nodes))


def apply_delta_with_representation(
    world: EpistemicWorld,
    delta: Iterable[DeltaOp],
    representation: Representation,
) -> EpistemicWorld:
    """Apply a delta with evaluator-bound target representation semantics."""
    world.verify()
    representation.verify()
    nodes = world.node_map()
    rep = world.representation
    for op in tuple(delta):
        op.verify()
        if op.kind is DeltaKind.SET_STATUS:
            node = nodes[op.target_id]
            nodes[op.target_id] = replace(node, status=NodeStatus(op.value))
        elif op.kind is DeltaKind.SET_REPRESENTATION:
            if op.value != representation.representation_id:
                raise ValueError("delta representation id does not match supplied representation")
            rep = representation
    out = replace(world, representation=rep, nodes=tuple(nodes[node.node_id] for node in world.nodes))
    out.verify()
    return out


def _case(
    family: ExactFamily,
    material: str,
    world: EpistemicWorld,
    intervention: EpistemicIntervention,
) -> ExactCase:
    post_state, delta = execute_intervention(world, intervention)
    case = ExactCase(
        family=family,
        case_id=_tok(material, "case", family.value, "c"),
        pre_state=world,
        intervention=intervention,
        post_state=post_state,
        gold_delta=delta,
    )
    case.verify()
    return case


def _base(seed: str, slot: str) -> str:
    if not seed:
        raise ValueError("seed is required")
    return _digest({"schema": "EA.seed.v0", "seed": seed, "slot": slot})


def _node(material: str, slot: str, kind: NodeKind, status: NodeStatus = NodeStatus.ACTIVE) -> EpistemicNode:
    return EpistemicNode(
        _tok(material, "node", slot, "n"),
        kind,
        status,
        _tok(material, "surface-node", slot, "s"),
    )


def _edge(material: str, slot: str, source: str, target: str, kind: EdgeKind) -> EpistemicEdge:
    return EpistemicEdge(
        _tok(material, "edge", slot, "e"),
        source,
        target,
        kind,
        _tok(material, "surface-edge", slot, "s"),
    )


def _representation(material: str, slot: str, semantic_slot: str) -> Representation:
    return Representation(
        _tok(material, "representation", slot, "r"),
        _tok(material, "semantic", semantic_slot, "k"),
    )


def generate_case(family: ExactFamily, seed: str) -> ExactCase:
    material = _base(seed, family.value)

    if family is ExactFamily.SPARSE_RETRACTION:
        e1 = _node(material, "e1", NodeKind.EVIDENCE)
        c1 = _node(material, "c1", NodeKind.CLAIM)
        c2 = _node(material, "c2", NodeKind.CLAIM)
        e2 = _node(material, "e2", NodeKind.EVIDENCE)
        c3 = _node(material, "c3", NodeKind.CLAIM)
        world = EpistemicWorld(
            _tok(material, "world", "0", "w"),
            _representation(material, "old", "A"),
            (e1, c1, c2, e2, c3),
            (
                _edge(material, "0", e1.node_id, c1.node_id, EdgeKind.SUPPORTS),
                _edge(material, "1", c1.node_id, c2.node_id, EdgeKind.REQUIRES),
                _edge(material, "2", e2.node_id, c3.node_id, EdgeKind.SUPPORTS),
            ),
        )
        return _case(family, material, world, EpistemicIntervention(InterventionKind.RETRACT, e1.node_id))

    if family is ExactFamily.INDEPENDENT_SUPPORT:
        e1 = _node(material, "e1", NodeKind.EVIDENCE)
        e2 = _node(material, "e2", NodeKind.EVIDENCE)
        c1 = _node(material, "c1", NodeKind.CLAIM)
        c2 = _node(material, "c2", NodeKind.CLAIM)
        world = EpistemicWorld(
            _tok(material, "world", "0", "w"),
            _representation(material, "old", "A"),
            (e1, e2, c1, c2),
            (
                _edge(material, "0", e1.node_id, c1.node_id, EdgeKind.SUPPORTS),
                _edge(material, "1", e2.node_id, c1.node_id, EdgeKind.SUPPORTS),
                _edge(material, "2", c1.node_id, c2.node_id, EdgeKind.REQUIRES),
            ),
        )
        return _case(family, material, world, EpistemicIntervention(InterventionKind.RETRACT, e1.node_id))

    if family is ExactFamily.ACTIVE_DEFEATER:
        e1 = _node(material, "e1", NodeKind.EVIDENCE)
        d1 = _node(material, "d1", NodeKind.EVIDENCE, NodeStatus.RETRACTED)
        c1 = _node(material, "c1", NodeKind.CLAIM)
        c2 = _node(material, "c2", NodeKind.CLAIM)
        world = EpistemicWorld(
            _tok(material, "world", "0", "w"),
            _representation(material, "old", "A"),
            (e1, d1, c1, c2),
            (
                _edge(material, "0", e1.node_id, c1.node_id, EdgeKind.SUPPORTS),
                _edge(material, "1", d1.node_id, c1.node_id, EdgeKind.DEFEATS),
                _edge(material, "2", c1.node_id, c2.node_id, EdgeKind.REQUIRES),
            ),
        )
        return _case(family, material, world, EpistemicIntervention(InterventionKind.ACTIVATE, d1.node_id))

    if family in {ExactFamily.FAILURE_REOPEN_MATERIAL, ExactFamily.FAILURE_REOPEN_REMINT}:
        f1 = _node(material, "f1", NodeKind.FAILURE)
        m1 = _node(material, "m1", NodeKind.METHOD, NodeStatus.BLOCKED)
        old = _representation(material, "old", "A")
        semantic_slot = "B" if family is ExactFamily.FAILURE_REOPEN_MATERIAL else "A"
        new = Representation(
            _tok(material, "representation", "new", "r"),
            _tok(material, "semantic", semantic_slot, "k"),
        )
        world = EpistemicWorld(
            _tok(material, "world", "0", "w"),
            old,
            (f1, m1),
            (_edge(material, "0", f1.node_id, m1.node_id, EdgeKind.DEFEATS),),
            failure_scopes=(FailureScope(f1.node_id, old.semantic_key, True),),
        )
        return _case(
            family,
            material,
            world,
            EpistemicIntervention(InterventionKind.CHANGE_REPRESENTATION, new_representation=new),
        )

    if family in {ExactFamily.OBLIGATION_NONTRANSPORT, ExactFamily.OBLIGATION_TRANSPORT}:
        o1 = _node(material, "o1", NodeKind.OBLIGATION)
        c1 = _node(material, "c1", NodeKind.CLAIM)
        old = _representation(material, "old", "A")
        new = _representation(material, "new", "B")
        world = EpistemicWorld(
            _tok(material, "world", "0", "w"),
            old,
            (o1, c1),
            (_edge(material, "0", o1.node_id, c1.node_id, EdgeKind.REQUIRES),),
            obligation_scopes=(
                ObligationScope(
                    o1.node_id,
                    old.semantic_key,
                    family is ExactFamily.OBLIGATION_TRANSPORT,
                ),
            ),
        )
        return _case(
            family,
            material,
            world,
            EpistemicIntervention(InterventionKind.CHANGE_REPRESENTATION, new_representation=new),
        )

    if family is ExactFamily.UNKNOWN_PROPAGATION:
        e1 = _node(material, "e1", NodeKind.EVIDENCE)
        c1 = _node(material, "c1", NodeKind.CLAIM)
        c2 = _node(material, "c2", NodeKind.CLAIM)
        world = EpistemicWorld(
            _tok(material, "world", "0", "w"),
            _representation(material, "old", "A"),
            (e1, c1, c2),
            (
                _edge(material, "0", e1.node_id, c1.node_id, EdgeKind.REQUIRES),
                _edge(material, "1", c1.node_id, c2.node_id, EdgeKind.REQUIRES),
            ),
        )
        return _case(family, material, world, EpistemicIntervention(InterventionKind.MARK_UNKNOWN, e1.node_id))

    if family is ExactFamily.IRRELEVANT_RETRACTION:
        e1 = _node(material, "e1", NodeKind.EVIDENCE)
        c1 = _node(material, "c1", NodeKind.CLAIM)
        e2 = _node(material, "e2", NodeKind.EVIDENCE)
        world = EpistemicWorld(
            _tok(material, "world", "0", "w"),
            _representation(material, "old", "A"),
            (e1, c1, e2),
            (_edge(material, "0", e1.node_id, c1.node_id, EdgeKind.SUPPORTS),),
        )
        return _case(family, material, world, EpistemicIntervention(InterventionKind.RETRACT, e2.node_id))

    raise ValueError(f"unsupported family: {family}")


def generate_representation_hostile_pair(seed: str) -> tuple[ExactCase, ExactCase]:
    """Construct typed-view collision: remint vs material semantic change."""
    material = _base(seed, "representation-hostile-pair")
    f1 = _node(material, "f1", NodeKind.FAILURE)
    m1 = _node(material, "m1", NodeKind.METHOD, NodeStatus.BLOCKED)
    old = _representation(material, "old", "A")
    new_id = _tok(material, "representation", "new", "r")
    world = EpistemicWorld(
        _tok(material, "world", "0", "w"),
        old,
        (f1, m1),
        (_edge(material, "0", f1.node_id, m1.node_id, EdgeKind.DEFEATS),),
        failure_scopes=(FailureScope(f1.node_id, old.semantic_key, True),),
    )
    remint = _case(
        ExactFamily.FAILURE_REOPEN_REMINT,
        material + "|remint",
        world,
        EpistemicIntervention(
            InterventionKind.CHANGE_REPRESENTATION,
            new_representation=Representation(new_id, old.semantic_key),
        ),
    )
    material_change = _case(
        ExactFamily.FAILURE_REOPEN_MATERIAL,
        material + "|material",
        world,
        EpistemicIntervention(
            InterventionKind.CHANGE_REPRESENTATION,
            new_representation=Representation(new_id, _tok(material, "semantic", "B", "k")),
        ),
    )
    return remint, material_change


def generate_obligation_hostile_pair(seed: str) -> tuple[ExactCase, ExactCase]:
    """Construct typed-view collision: hidden obligation transportability changes gold."""
    material = _base(seed, "obligation-hostile-pair")
    o1 = _node(material, "o1", NodeKind.OBLIGATION)
    c1 = _node(material, "c1", NodeKind.CLAIM)
    old = _representation(material, "old", "A")
    new = _representation(material, "new", "B")
    edge = _edge(material, "0", o1.node_id, c1.node_id, EdgeKind.REQUIRES)
    common = {
        "world_id": _tok(material, "world", "0", "w"),
        "representation": old,
        "nodes": (o1, c1),
        "edges": (edge,),
    }
    nontransport_world = EpistemicWorld(
        **common,
        obligation_scopes=(ObligationScope(o1.node_id, old.semantic_key, False),),
    )
    transport_world = EpistemicWorld(
        **common,
        obligation_scopes=(ObligationScope(o1.node_id, old.semantic_key, True),),
    )
    intervention = EpistemicIntervention(
        InterventionKind.CHANGE_REPRESENTATION,
        new_representation=new,
    )
    return (
        _case(ExactFamily.OBLIGATION_NONTRANSPORT, material + "|nontransport", nontransport_world, intervention),
        _case(ExactFamily.OBLIGATION_TRANSPORT, material + "|transport", transport_world, intervention),
    )


def generate_suite(seed: str) -> tuple[ExactCase, ...]:
    if not seed:
        raise ValueError("suite seed is required")
    return tuple(generate_case(family, f"{seed}|{family.value}") for family in ExactFamily)
