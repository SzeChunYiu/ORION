"""Fail-closed projection for the P9 SRE application pilot.

This module deliberately separates candidate-visible incident evidence from evaluator
truth.  ITBench ground-truth files mix observable alerts with injected-fault,
root-cause, propagation and remediation metadata.  A model must never receive the
latter merely because they share one source file.

No function here performs root-cause inference or grants scientific authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
from typing import Mapping, Sequence


class SREView(str, Enum):
    SURFACE = "S0_SURFACE"
    TOPOLOGY = "S1_TOPOLOGY"
    TYPED_EVIDENCE = "S2_TYPED_EVIDENCE"


def _opaque(seed: str, namespace: str, value: str) -> str:
    digest = sha256(f"{seed}|{namespace}|{value}".encode("utf-8")).hexdigest()
    return f"{namespace}_{digest[:16]}"


@dataclass(frozen=True)
class SREAlert:
    source_id: str
    alert_id: str

    def verify(self) -> None:
        if not self.source_id or not self.alert_id:
            raise ValueError("alert source_id and alert_id must be non-empty")


@dataclass(frozen=True)
class SRENode:
    node_id: str
    kind: str

    def verify(self) -> None:
        if not self.node_id or not self.kind:
            raise ValueError("node_id and kind must be non-empty")


@dataclass(frozen=True)
class SRERelation:
    source_id: str
    target_id: str
    relation_type: str

    def verify(self) -> None:
        if not self.source_id or not self.target_id or not self.relation_type:
            raise ValueError("relation fields must be non-empty")
        if self.source_id == self.target_id:
            raise ValueError("self-relations are not admitted in the A1 pilot substrate")


@dataclass(frozen=True)
class SREEvaluatorTruth:
    root_cause_ids: tuple[str, ...]
    propagation_edges: tuple[tuple[str, str], ...]

    def verify(self) -> None:
        if len(set(self.root_cause_ids)) != len(self.root_cause_ids):
            raise ValueError("duplicate root-cause ids")
        if len(set(self.propagation_edges)) != len(self.propagation_edges):
            raise ValueError("duplicate propagation edges")
        for source, target in self.propagation_edges:
            if not source or not target or source == target:
                raise ValueError("invalid propagation edge")


@dataclass(frozen=True)
class SREObservableEvidence:
    alerts: tuple[SREAlert, ...]
    nodes: tuple[SRENode, ...] = ()
    relations: tuple[SRERelation, ...] = ()

    def verify(self) -> None:
        for alert in self.alerts:
            alert.verify()
        for node in self.nodes:
            node.verify()
        for relation in self.relations:
            relation.verify()
        node_ids = {node.node_id for node in self.nodes}
        if len(node_ids) != len(self.nodes):
            raise ValueError("duplicate observable node ids")
        for relation in self.relations:
            if relation.source_id not in node_ids or relation.target_id not in node_ids:
                raise ValueError("relation endpoint missing from observable nodes")

    def model_payload(self, *, view: SREView, remint_seed: str) -> dict[str, object]:
        """Project only candidate-visible evidence into one frozen view.

        The payload intentionally excludes any evaluator truth.  Surface identities are
        reminted so scenario/service names cannot become a reusable answer key.
        """

        self.verify()
        if not remint_seed:
            raise ValueError("remint_seed must be non-empty")

        alert_rows = [
            [
                _opaque(remint_seed, "entity", alert.source_id),
                _opaque(remint_seed, "alert", alert.alert_id),
            ]
            for alert in self.alerts
        ]
        payload: dict[str, object] = {"alerts": sorted(alert_rows)}

        if view is SREView.SURFACE:
            return payload

        topology_rows = [
            [
                _opaque(remint_seed, "entity", relation.source_id),
                _opaque(remint_seed, "entity", relation.target_id),
            ]
            for relation in self.relations
        ]
        payload["topology"] = sorted(topology_rows)

        if view is SREView.TOPOLOGY:
            return payload

        typed_nodes = [
            [_opaque(remint_seed, "entity", node.node_id), node.kind]
            for node in self.nodes
        ]
        typed_relations = [
            [
                _opaque(remint_seed, "entity", relation.source_id),
                _opaque(remint_seed, "entity", relation.target_id),
                relation.relation_type,
            ]
            for relation in self.relations
        ]
        payload["typed_nodes"] = sorted(typed_nodes)
        # The opaque endpoint names intentionally change with ``remint_seed``.
        # Ordering by those names would therefore make the semantic relation
        # sequence change under a surface-only remint.  Keep relation kind as
        # the primary structural coordinate and use endpoints only to make
        # multiple relations of the same kind deterministic.
        payload["typed_relations"] = sorted(
            typed_relations, key=lambda row: (row[2], row[0], row[1])
        )
        return payload


@dataclass(frozen=True)
class SRECase:
    case_id: str
    observable: SREObservableEvidence
    evaluator: SREEvaluatorTruth

    def verify(self) -> None:
        if not self.case_id:
            raise ValueError("case_id must be non-empty")
        self.observable.verify()
        self.evaluator.verify()

    def target_observable(self) -> bool:
        """Whether every protected root-cause entity exists in observable node state."""

        self.verify()
        observable_ids = {node.node_id for node in self.observable.nodes}
        return bool(self.evaluator.root_cause_ids) and all(
            root_cause in observable_ids for root_cause in self.evaluator.root_cause_ids
        )

    def model_payload(self, *, view: SREView, remint_seed: str) -> dict[str, object]:
        self.verify()
        return self.observable.model_payload(view=view, remint_seed=remint_seed)


def _as_sequence(value: object) -> Sequence[object]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return value
    return ()


def _as_mapping(value: object) -> Mapping[str, object]:
    if isinstance(value, Mapping):
        return value
    return {}


def extract_itbench_alerts(raw_groundtruth: Mapping[str, object]) -> tuple[SREAlert, ...]:
    """Extract only minimally observable alert identifiers.

    Alert metadata/descriptions are intentionally discarded because current ITBench
    ground-truth descriptions can contain causal phrases such as ``due to feature
    flag``.  Fault, group/root-cause, propagation and recommendation fields are never
    inspected by this function.
    """

    rows: list[SREAlert] = []
    for raw_alert in _as_sequence(raw_groundtruth.get("alerts")):
        alert = _as_mapping(raw_alert)
        source_id = alert.get("group_id")
        alert_id = alert.get("id")
        if isinstance(source_id, str) and isinstance(alert_id, str):
            rows.append(SREAlert(source_id=source_id, alert_id=alert_id))
    result = tuple(rows)
    for row in result:
        row.verify()
    return result


def extract_itbench_evaluator_truth(
    raw_groundtruth: Mapping[str, object],
) -> SREEvaluatorTruth:
    """Extract evaluator-only root causes and propagation edges.

    This function exists on the evaluator side of the custody boundary.  Its output
    must never be passed to ``SREObservableEvidence.model_payload``.
    """

    root_causes: list[str] = []
    for raw_group in _as_sequence(raw_groundtruth.get("groups")):
        group = _as_mapping(raw_group)
        if group.get("root_cause") is True and isinstance(group.get("id"), str):
            root_causes.append(str(group["id"]))

    propagation_edges: list[tuple[str, str]] = []
    for raw_edge in _as_sequence(raw_groundtruth.get("propagations")):
        edge = _as_mapping(raw_edge)
        source = edge.get("source")
        target = edge.get("target")
        if isinstance(source, str) and isinstance(target, str):
            propagation_edges.append((source, target))

    truth = SREEvaluatorTruth(
        root_cause_ids=tuple(sorted(set(root_causes))),
        propagation_edges=tuple(sorted(set(propagation_edges))),
    )
    truth.verify()
    return truth


__all__ = [
    "SREAlert",
    "SRECase",
    "SREEvaluatorTruth",
    "SRENode",
    "SREObservableEvidence",
    "SRERelation",
    "SREView",
    "extract_itbench_alerts",
    "extract_itbench_evaluator_truth",
]
