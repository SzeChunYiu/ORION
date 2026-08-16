from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from ..lenses import AffineLens
from .canonical import content_digest


class ScientificCoordinateType(str, Enum):
    REFERENT = "REFERENT"
    CONSTRUCT = "CONSTRUCT"
    MEASUREMENT = "MEASUREMENT"
    CONTEXT = "CONTEXT"
    MODALITY = "MODALITY"
    ATTRIBUTION = "ATTRIBUTION"


class P3ConsistencyOutcome(str, Enum):
    GLUE = "GLUE"
    OBSTRUCTION = "OBSTRUCTION"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class TypedLensEdge:
    source_view: str
    target_view: str
    coordinate_type: ScientificCoordinateType
    lens: AffineLens
    bidirectional_validated: bool = True
    provenance_digest: str = ""

    def __post_init__(self) -> None:
        if not self.source_view or not self.target_view or self.source_view == self.target_view:
            raise ValueError("typed lens edge requires distinct non-empty views")
        if self.provenance_digest and not self.provenance_digest.startswith("sha256:"):
            raise ValueError("provenance_digest must be sha256-prefixed")


def typed_edge_payload(edge: TypedLensEdge) -> dict[str, object]:
    return {
        "source_view": edge.source_view,
        "target_view": edge.target_view,
        "coordinate_type": edge.coordinate_type.value,
        "scale": edge.lens.scale,
        "offset": edge.lens.offset,
        "bidirectional_validated": edge.bidirectional_validated,
        "provenance_digest": edge.provenance_digest,
    }


@dataclass(frozen=True)
class P3ConsistencyReceipt:
    coordinate_type: ScientificCoordinateType
    cycle: tuple[str, ...]
    outcome: P3ConsistencyOutcome
    reason_code: str
    worst_error: float | None
    mapping_digest: str
    anchors_digest: str
    receipt_digest: str

    def unsigned_payload(self) -> dict[str, object]:
        return {
            "receipt_version": "ORION_P3_CONSISTENCY_RECEIPT_V2",
            "coordinate_type": self.coordinate_type.value,
            "cycle": list(self.cycle),
            "outcome": self.outcome.value,
            "reason_code": self.reason_code,
            "worst_error": self.worst_error,
            "mapping_digest": self.mapping_digest,
            "anchors_digest": self.anchors_digest,
            "merge_authority": "CONSISTENCY_GATE_ONLY",
        }

    def to_payload(self) -> dict[str, object]:
        payload = self.unsigned_payload()
        payload["receipt_digest"] = self.receipt_digest
        return payload

    def verify(self) -> None:
        if content_digest(self.unsigned_payload()) != self.receipt_digest:
            raise ValueError("P3 consistency receipt digest mismatch")


class TypedScientificLensNetwork:
    def __init__(self, edges: Sequence[TypedLensEdge]) -> None:
        self._edges: dict[tuple[ScientificCoordinateType, str, str], TypedLensEdge] = {}
        self._pair_types: dict[tuple[str, str], set[ScientificCoordinateType]] = {}
        for edge in edges:
            key = (edge.coordinate_type, edge.source_view, edge.target_view)
            prior = self._edges.get(key)
            if prior is not None and typed_edge_payload(prior) != typed_edge_payload(edge):
                raise ValueError(f"conflicting typed lens edge: {key}")
            self._edges[key] = edge
            self._pair_types.setdefault((edge.source_view, edge.target_view), set()).add(edge.coordinate_type)
            inverse = TypedLensEdge(
                source_view=edge.target_view,
                target_view=edge.source_view,
                coordinate_type=edge.coordinate_type,
                lens=edge.lens.inverse(),
                bidirectional_validated=edge.bidirectional_validated,
                provenance_digest=edge.provenance_digest,
            )
            inverse_key = (inverse.coordinate_type, inverse.source_view, inverse.target_view)
            self._edges.setdefault(inverse_key, inverse)
            self._pair_types.setdefault((inverse.source_view, inverse.target_view), set()).add(edge.coordinate_type)

    def assess_cycle(
        self,
        coordinate_type: ScientificCoordinateType,
        cycle: Sequence[str],
        anchors: Sequence[float],
        *,
        tolerance: float = 1e-9,
    ) -> P3ConsistencyReceipt:
        if tolerance < 0:
            raise ValueError("tolerance must be non-negative")
        if len(cycle) < 3 or cycle[0] != cycle[-1]:
            raise ValueError("cycle must return to its start")
        relevant: list[TypedLensEdge] = []
        for source, target in zip(cycle, cycle[1:]):
            edge = self._edges.get((coordinate_type, source, target))
            if edge is None:
                pair_types = self._pair_types.get((source, target), set())
                if pair_types:
                    return self._receipt(
                        coordinate_type, cycle, anchors, [], P3ConsistencyOutcome.OBSTRUCTION,
                        "COORDINATE_TYPE_MISMATCH", None,
                    )
                return self._receipt(
                    coordinate_type, cycle, anchors, [], P3ConsistencyOutcome.CANNOT_CHECK,
                    "MAPPING_MISSING", None,
                )
            relevant.append(edge)
        if any(not edge.bidirectional_validated for edge in relevant):
            return self._receipt(
                coordinate_type, cycle, anchors, relevant, P3ConsistencyOutcome.CANNOT_CHECK,
                "BIDIRECTIONAL_VALIDATION_MISSING", None,
            )
        if any(not edge.provenance_digest for edge in relevant):
            return self._receipt(
                coordinate_type, cycle, anchors, relevant, P3ConsistencyOutcome.CANNOT_CHECK,
                "PROVENANCE_ANCHOR_MISSING", None,
            )
        if not anchors:
            return self._receipt(
                coordinate_type, cycle, anchors, relevant, P3ConsistencyOutcome.CANNOT_CHECK,
                "VALIDATION_ANCHORS_MISSING", None,
            )
        composed = AffineLens(1.0, 0.0)
        for edge in relevant:
            composed = composed.then(edge.lens)
        worst = max(abs(composed.forward(anchor) - anchor) for anchor in anchors)
        if worst <= tolerance:
            return self._receipt(
                coordinate_type, cycle, anchors, relevant, P3ConsistencyOutcome.GLUE,
                "ROUND_TRIP_WITHIN_TOLERANCE", worst,
            )
        return self._receipt(
            coordinate_type, cycle, anchors, relevant, P3ConsistencyOutcome.OBSTRUCTION,
            "CYCLE_INCONSISTENT", worst,
        )

    def _receipt(
        self,
        coordinate_type: ScientificCoordinateType,
        cycle: Sequence[str],
        anchors: Sequence[float],
        edges: Sequence[TypedLensEdge],
        outcome: P3ConsistencyOutcome,
        reason: str,
        worst_error: float | None,
    ) -> P3ConsistencyReceipt:
        mapping_payload = sorted((typed_edge_payload(edge) for edge in edges), key=lambda item: (str(item["source_view"]), str(item["target_view"])))
        mapping_digest = content_digest(mapping_payload)
        anchors_digest = content_digest(list(anchors))
        unsigned = {
            "receipt_version": "ORION_P3_CONSISTENCY_RECEIPT_V2",
            "coordinate_type": coordinate_type.value,
            "cycle": list(cycle),
            "outcome": outcome.value,
            "reason_code": reason,
            "worst_error": worst_error,
            "mapping_digest": mapping_digest,
            "anchors_digest": anchors_digest,
            "merge_authority": "CONSISTENCY_GATE_ONLY",
        }
        return P3ConsistencyReceipt(
            coordinate_type=coordinate_type,
            cycle=tuple(cycle),
            outcome=outcome,
            reason_code=reason,
            worst_error=worst_error,
            mapping_digest=mapping_digest,
            anchors_digest=anchors_digest,
            receipt_digest=content_digest(unsigned),
        )
