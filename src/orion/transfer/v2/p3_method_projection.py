from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

from .canonical import content_digest
from .p1_method_realization import MethodRealization


class ProjectionState(str, Enum):
    SUPPORTED = "SUPPORTED"
    PARTIAL = "PARTIAL"
    OBSTRUCTION = "OBSTRUCTION"


class AlignmentState(str, Enum):
    ALIGNED = "ALIGNED"
    RELATED = "RELATED"
    OBSTRUCTION = "OBSTRUCTION"
    UNRESOLVED = "UNRESOLVED"


P1_UNKNOWN_TO_P3 = {
    "progress_measure": "progress",
    "terminal_condition": "termination",
    "reconstruction_map": "reconstruction",
    "failure_modes": "failure",
}


@dataclass(frozen=True)
class MethodStructureProjection:
    projection_id: str
    source_id: str
    source_digest: str
    source_version: str
    source_span_digests: tuple[str, ...]
    realization_digest: str
    target_role: str | None
    initial_obstruction: tuple[str, ...]
    assumptions: tuple[str, ...]
    preconditions: tuple[str, ...]
    representation_changes: tuple[str, ...]
    auxiliary_objects: tuple[str, ...]
    mechanics: tuple[str, ...]
    dependencies: tuple[tuple[str, str], ...]
    invariants: tuple[str, ...]
    progress_semantics: str | None
    termination_semantics: str | None
    reconstruction: str | None
    failure_statements: tuple[str, ...]
    author_rationale: tuple[str, ...]
    unknown_coordinates: tuple[str, ...]
    state: ProjectionState
    digest: str

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "P3.MethodStructureProjection.v1",
            "projection_id": self.projection_id,
            "source_id": self.source_id,
            "source_digest": self.source_digest,
            "source_version": self.source_version,
            "source_span_digests": list(self.source_span_digests),
            "realization_digest": self.realization_digest,
            "target_role": self.target_role,
            "initial_obstruction": list(self.initial_obstruction),
            "assumptions": list(self.assumptions),
            "preconditions": list(self.preconditions),
            "representation_changes": list(self.representation_changes),
            "auxiliary_objects": list(self.auxiliary_objects),
            "mechanics": list(self.mechanics),
            "dependencies": [list(edge) for edge in self.dependencies],
            "invariants": list(self.invariants),
            "progress_semantics": self.progress_semantics,
            "termination_semantics": self.termination_semantics,
            "reconstruction": self.reconstruction,
            "failure_statements": list(self.failure_statements),
            "author_rationale": list(self.author_rationale),
            "unknown_coordinates": list(self.unknown_coordinates),
            "state": self.state.value,
            "authority_scope": "SOURCE_LOCAL_PROJECTION_ONLY",
            "can_claim_method_fibre": False,
        }

    def verify(self) -> None:
        if not self.projection_id or not self.source_id:
            raise ValueError("projection/source identity required")
        if not self.source_digest.startswith("sha256:"):
            raise ValueError("source must be content bound")
        if not self.realization_digest.startswith("sha256:"):
            raise ValueError("realization must be content bound")
        if not self.source_span_digests or any(not x.startswith("sha256:") for x in self.source_span_digests):
            raise ValueError("source spans must be content bound")
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("projection digest mismatch")


def build_projection(
    realization: MethodRealization,
    *,
    projection_id: str,
    source_id: str,
    source_span_digests: Sequence[str],
    initial_obstruction: Sequence[str] = (),
    representation_changes: Sequence[str] = (),
    auxiliary_objects: Sequence[str] = (),
    author_rationale: Sequence[str] = (),
    unknown_coordinates: Sequence[str] = (),
) -> MethodStructureProjection:
    realization.verify()
    inherited_unknown = {P1_UNKNOWN_TO_P3.get(name, name) for name in realization.unknown_coordinates}
    unknown = tuple(sorted(inherited_unknown | set(unknown_coordinates)))
    if not source_span_digests:
        raise ValueError("at least one source span required")
    state = ProjectionState.PARTIAL if unknown else ProjectionState.SUPPORTED
    base = {
        "version": "P3.MethodStructureProjection.v1",
        "projection_id": projection_id,
        "source_id": source_id,
        "source_digest": realization.source_digest,
        "source_version": realization.source_version,
        "source_span_digests": sorted(set(source_span_digests)),
        "realization_digest": realization.digest,
        "target_role": realization.target_role,
        "initial_obstruction": sorted(set(initial_obstruction)),
        "assumptions": list(realization.assumptions),
        "preconditions": list(realization.preconditions),
        "representation_changes": sorted(set(representation_changes)),
        "auxiliary_objects": sorted(set(auxiliary_objects)),
        "mechanics": list(realization.mechanics),
        "dependencies": [list(x) for x in realization.dependencies],
        "invariants": list(realization.invariants),
        "progress_semantics": realization.progress_measure,
        "termination_semantics": realization.terminal_condition,
        "reconstruction": realization.reconstruction_map,
        "failure_statements": list(realization.failure_modes),
        "author_rationale": sorted(set(author_rationale)),
        "unknown_coordinates": list(unknown),
        "state": state.value,
        "authority_scope": "SOURCE_LOCAL_PROJECTION_ONLY",
        "can_claim_method_fibre": False,
    }
    out = MethodStructureProjection(
        projection_id=projection_id,
        source_id=source_id,
        source_digest=realization.source_digest,
        source_version=realization.source_version,
        source_span_digests=tuple(base["source_span_digests"]),
        realization_digest=realization.digest,
        target_role=realization.target_role,
        initial_obstruction=tuple(base["initial_obstruction"]),
        assumptions=realization.assumptions,
        preconditions=realization.preconditions,
        representation_changes=tuple(base["representation_changes"]),
        auxiliary_objects=tuple(base["auxiliary_objects"]),
        mechanics=realization.mechanics,
        dependencies=realization.dependencies,
        invariants=realization.invariants,
        progress_semantics=realization.progress_measure,
        termination_semantics=realization.terminal_condition,
        reconstruction=realization.reconstruction_map,
        failure_statements=realization.failure_modes,
        author_rationale=tuple(base["author_rationale"]),
        unknown_coordinates=unknown,
        state=state,
        digest=content_digest(base),
    )
    out.verify()
    return out


@dataclass(frozen=True)
class CoordinateComparison:
    coordinate: str
    state: str
    left_value: object
    right_value: object
    reason: str

    def payload(self) -> dict[str, object]:
        return {
            "coordinate": self.coordinate,
            "state": self.state,
            "left_value": self.left_value,
            "right_value": self.right_value,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class MethodAlignment:
    alignment_id: str
    purpose: str
    left_projection_digest: str
    right_projection_digest: str
    comparisons: tuple[CoordinateComparison, ...]
    unmatched_assumptions: tuple[str, ...]
    state: AlignmentState
    reasons: tuple[str, ...]
    digest: str

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "P3.MethodAlignment.v1",
            "alignment_id": self.alignment_id,
            "purpose": self.purpose,
            "left_projection_digest": self.left_projection_digest,
            "right_projection_digest": self.right_projection_digest,
            "comparisons": [x.payload() for x in self.comparisons],
            "unmatched_assumptions": list(self.unmatched_assumptions),
            "state": self.state.value,
            "reasons": list(self.reasons),
            "authority_scope": "CANDIDATE_ALIGNMENT_ONLY",
            "can_claim_equivalence": False,
            "can_claim_method_fibre": False,
        }

    def verify(self) -> None:
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("alignment digest mismatch")


def align_projections(
    left: MethodStructureProjection,
    right: MethodStructureProjection,
    *,
    alignment_id: str,
    purpose: str,
    required_coordinates: Sequence[str],
) -> MethodAlignment:
    left.verify(); right.verify()
    values: Mapping[str, tuple[object, object]] = {
        "preconditions": (left.preconditions, right.preconditions),
        "assumptions": (left.assumptions, right.assumptions),
        "invariants": (left.invariants, right.invariants),
        "progress": (left.progress_semantics, right.progress_semantics),
        "termination": (left.termination_semantics, right.termination_semantics),
        "reconstruction": (left.reconstruction, right.reconstruction),
        "failure": (left.failure_statements, right.failure_statements),
    }
    unknown = set(left.unknown_coordinates) | set(right.unknown_coordinates)
    comparisons: list[CoordinateComparison] = []
    reasons: list[str] = []
    obstruction = False
    unresolved = False
    for coordinate in required_coordinates:
        if coordinate not in values:
            raise ValueError(f"unsupported alignment coordinate: {coordinate}")
        lv, rv = values[coordinate]
        if coordinate in unknown:
            state = "UNRESOLVED"; reason = "SOURCE_EVIDENCE_INSUFFICIENT"; unresolved = True
        elif lv == rv:
            state = "SUPPORTED"; reason = "SOURCE_LOCAL_VALUES_AGREE"
        else:
            state = "OBSTRUCTION"; reason = "LOAD_BEARING_VALUES_DIFFER"; obstruction = True
            reasons.append(f"{coordinate.upper()}_MISMATCH")
        comparisons.append(CoordinateComparison(coordinate, state, lv, rv, reason))
    unmatched = tuple(sorted(set(left.assumptions) ^ set(right.assumptions)))
    if obstruction:
        overall = AlignmentState.OBSTRUCTION
    elif unresolved:
        overall = AlignmentState.UNRESOLVED
    else:
        overall = AlignmentState.ALIGNED
    base = {
        "version": "P3.MethodAlignment.v1",
        "alignment_id": alignment_id,
        "purpose": purpose,
        "left_projection_digest": left.digest,
        "right_projection_digest": right.digest,
        "comparisons": [x.payload() for x in comparisons],
        "unmatched_assumptions": list(unmatched),
        "state": overall.value,
        "reasons": sorted(reasons),
        "authority_scope": "CANDIDATE_ALIGNMENT_ONLY",
        "can_claim_equivalence": False,
        "can_claim_method_fibre": False,
    }
    out = MethodAlignment(
        alignment_id, purpose, left.digest, right.digest, tuple(comparisons), unmatched,
        overall, tuple(base["reasons"]), content_digest(base)
    )
    out.verify()
    return out


def obstruction_certificate(alignment: MethodAlignment) -> dict[str, object]:
    alignment.verify()
    return {
        "version": "P3.MethodAlignmentObstruction.v1",
        "alignment_digest": alignment.digest,
        "state": alignment.state.value,
        "obstructed_coordinates": [x.coordinate for x in alignment.comparisons if x.state == "OBSTRUCTION"],
        "unresolved_coordinates": [x.coordinate for x in alignment.comparisons if x.state == "UNRESOLVED"],
        "source_projection_digests": [alignment.left_projection_digest, alignment.right_projection_digest],
        "authority_scope": "OBSTRUCTION_EVIDENCE_ONLY",
    }
