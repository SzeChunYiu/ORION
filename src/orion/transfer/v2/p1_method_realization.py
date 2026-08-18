from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

from .canonical import content_digest


class RealizationState(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    INVALID = "INVALID"


class PairDecision(str, Enum):
    SUBSTITUTABLE_FOR_CLAIM = "SUBSTITUTABLE_FOR_CLAIM"
    NOT_SUBSTITUTABLE = "NOT_SUBSTITUTABLE"
    UNRESOLVED = "UNRESOLVED"


COORDINATES = (
    "target_role",
    "preconditions",
    "assumptions",
    "resources",
    "representation_in",
    "representation_out",
    "mechanics",
    "dependencies",
    "invariants",
    "progress_measure",
    "effects",
    "terminal_condition",
    "reconstruction_map",
    "failure_modes",
    "lineage",
    "authority_boundary",
)

MANDATORY_COORDINATES = frozenset(
    {
        "target_role",
        "preconditions",
        "mechanics",
        "dependencies",
        "invariants",
        "effects",
        "terminal_condition",
        "reconstruction_map",
        "failure_modes",
        "lineage",
        "authority_boundary",
    }
)


@dataclass(frozen=True)
class MethodRealization:
    method_id: str
    source_digest: str
    source_version: str
    target_role: str | None
    preconditions: tuple[str, ...]
    assumptions: tuple[str, ...]
    resources: tuple[str, ...]
    representation_in: str | None
    representation_out: str | None
    mechanics: tuple[str, ...]
    dependencies: tuple[tuple[str, str], ...]
    invariants: tuple[str, ...]
    progress_measure: str | None
    effects: tuple[str, ...]
    terminal_condition: str | None
    reconstruction_map: str | None
    failure_modes: tuple[str, ...]
    lineage: tuple[str, ...]
    authority_boundary: str | None
    unknown_coordinates: tuple[str, ...]
    digest: str

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "P1.MethodRealization.v1",
            "method_id": self.method_id,
            "source_digest": self.source_digest,
            "source_version": self.source_version,
            "target_role": self.target_role,
            "preconditions": list(self.preconditions),
            "assumptions": list(self.assumptions),
            "resources": list(self.resources),
            "representation_in": self.representation_in,
            "representation_out": self.representation_out,
            "mechanics": list(self.mechanics),
            "dependencies": [list(edge) for edge in self.dependencies],
            "invariants": list(self.invariants),
            "progress_measure": self.progress_measure,
            "effects": list(self.effects),
            "terminal_condition": self.terminal_condition,
            "reconstruction_map": self.reconstruction_map,
            "failure_modes": list(self.failure_modes),
            "lineage": list(self.lineage),
            "authority_boundary": self.authority_boundary,
            "unknown_coordinates": list(self.unknown_coordinates),
        }

    def verify(self) -> None:
        if not self.method_id:
            raise ValueError("method_id required")
        if not self.source_digest.startswith("sha256:"):
            raise ValueError("source_digest must be content bound")
        if not self.source_version:
            raise ValueError("source_version required")
        if not set(self.unknown_coordinates) <= set(COORDINATES):
            raise ValueError("unknown coordinate name")
        if len(set(self.unknown_coordinates)) != len(self.unknown_coordinates):
            raise ValueError("duplicate unknown coordinate")
        if any(len(edge) != 2 for edge in self.dependencies):
            raise ValueError("dependency edges must be binary")
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("method realization digest mismatch")

    @property
    def state(self) -> RealizationState:
        errors = completeness_errors(self)
        if any(code.startswith("INVALID:") for code in errors):
            return RealizationState.INVALID
        return RealizationState.COMPLETE if not errors else RealizationState.PARTIAL


def _tuple(values: Sequence[str] | None) -> tuple[str, ...]:
    return tuple(sorted({str(x) for x in (values or ())}))


def build_method_realization(
    *,
    method_id: str,
    source_digest: str,
    source_version: str,
    target_role: str | None,
    preconditions: Sequence[str] = (),
    assumptions: Sequence[str] = (),
    resources: Sequence[str] = (),
    representation_in: str | None = None,
    representation_out: str | None = None,
    mechanics: Sequence[str] = (),
    dependencies: Sequence[tuple[str, str]] = (),
    invariants: Sequence[str] = (),
    progress_measure: str | None = None,
    effects: Sequence[str] = (),
    terminal_condition: str | None = None,
    reconstruction_map: str | None = None,
    failure_modes: Sequence[str] = (),
    lineage: Sequence[str] = (),
    authority_boundary: str | None = "REPRESENTATION_ONLY",
    unknown_coordinates: Sequence[str] = (),
) -> MethodRealization:
    dep = tuple(sorted({(str(a), str(b)) for a, b in dependencies}))
    payload = {
        "version": "P1.MethodRealization.v1",
        "method_id": method_id,
        "source_digest": source_digest,
        "source_version": source_version,
        "target_role": target_role,
        "preconditions": list(_tuple(preconditions)),
        "assumptions": list(_tuple(assumptions)),
        "resources": list(_tuple(resources)),
        "representation_in": representation_in,
        "representation_out": representation_out,
        "mechanics": list(_tuple(mechanics)),
        "dependencies": [list(edge) for edge in dep],
        "invariants": list(_tuple(invariants)),
        "progress_measure": progress_measure,
        "effects": list(_tuple(effects)),
        "terminal_condition": terminal_condition,
        "reconstruction_map": reconstruction_map,
        "failure_modes": list(_tuple(failure_modes)),
        "lineage": list(_tuple(lineage)),
        "authority_boundary": authority_boundary,
        "unknown_coordinates": list(_tuple(unknown_coordinates)),
    }
    out = MethodRealization(
        method_id=method_id,
        source_digest=source_digest,
        source_version=source_version,
        target_role=target_role,
        preconditions=tuple(payload["preconditions"]),
        assumptions=tuple(payload["assumptions"]),
        resources=tuple(payload["resources"]),
        representation_in=representation_in,
        representation_out=representation_out,
        mechanics=tuple(payload["mechanics"]),
        dependencies=dep,
        invariants=tuple(payload["invariants"]),
        progress_measure=progress_measure,
        effects=tuple(payload["effects"]),
        terminal_condition=terminal_condition,
        reconstruction_map=reconstruction_map,
        failure_modes=tuple(payload["failure_modes"]),
        lineage=tuple(payload["lineage"]),
        authority_boundary=authority_boundary,
        unknown_coordinates=tuple(payload["unknown_coordinates"]),
        digest=content_digest(payload),
    )
    out.verify()
    return out


def completeness_errors(realization: MethodRealization) -> tuple[str, ...]:
    realization.verify()
    errors: list[str] = []
    unknown = set(realization.unknown_coordinates)
    for coordinate in sorted(MANDATORY_COORDINATES):
        if coordinate in unknown:
            errors.append(f"UNKNOWN:{coordinate}")
            continue
        value = getattr(realization, coordinate)
        if value is None or value == () or value == "":
            errors.append(f"MISSING:{coordinate}")
    nodes = set(realization.mechanics)
    for left, right in realization.dependencies:
        if left not in nodes or right not in nodes:
            errors.append(f"INVALID:dependency:{left}->{right}")
    if realization.authority_boundary not in {"REPRESENTATION_ONLY", "FORMAL_STRUCTURE_ONLY"}:
        errors.append("INVALID:authority_boundary")
    return tuple(errors)


def material_differences(left: MethodRealization, right: MethodRealization) -> tuple[str, ...]:
    left.verify(); right.verify()
    fields = (
        "preconditions", "assumptions", "dependencies", "invariants", "effects",
        "terminal_condition", "reconstruction_map", "failure_modes", "lineage",
        "authority_boundary", "unknown_coordinates",
    )
    return tuple(name for name in fields if getattr(left, name) != getattr(right, name))


def assess_substitutability(
    left: MethodRealization,
    right: MethodRealization,
    *,
    required_coordinates: Sequence[str],
) -> PairDecision:
    left.verify(); right.verify()
    required = set(required_coordinates)
    if not required <= set(COORDINATES):
        raise ValueError("unknown required coordinate")
    if required & (set(left.unknown_coordinates) | set(right.unknown_coordinates)):
        return PairDecision.UNRESOLVED
    for coordinate in required:
        if getattr(left, coordinate) != getattr(right, coordinate):
            return PairDecision.NOT_SUBSTITUTABLE
    return PairDecision.SUBSTITUTABLE_FOR_CLAIM


def from_mapping(payload: Mapping[str, object]) -> MethodRealization:
    def seq(name: str) -> tuple[str, ...]:
        raw = payload.get(name, ()) or ()
        if not isinstance(raw, (list, tuple, set, frozenset)):
            raise ValueError(name)
        return tuple(str(x) for x in raw)

    deps_raw = payload.get("dependencies", ()) or ()
    deps: list[tuple[str, str]] = []
    if not isinstance(deps_raw, (list, tuple)):
        raise ValueError("dependencies")
    for edge in deps_raw:
        if not isinstance(edge, (list, tuple)) or len(edge) != 2:
            raise ValueError("dependency edge")
        deps.append((str(edge[0]), str(edge[1])))
    return build_method_realization(
        method_id=str(payload["method_id"]),
        source_digest=str(payload["source_digest"]),
        source_version=str(payload["source_version"]),
        target_role=None if payload.get("target_role") is None else str(payload["target_role"]),
        preconditions=seq("preconditions"), assumptions=seq("assumptions"), resources=seq("resources"),
        representation_in=None if payload.get("representation_in") is None else str(payload["representation_in"]),
        representation_out=None if payload.get("representation_out") is None else str(payload["representation_out"]),
        mechanics=seq("mechanics"), dependencies=deps, invariants=seq("invariants"),
        progress_measure=None if payload.get("progress_measure") is None else str(payload["progress_measure"]),
        effects=seq("effects"),
        terminal_condition=None if payload.get("terminal_condition") is None else str(payload["terminal_condition"]),
        reconstruction_map=None if payload.get("reconstruction_map") is None else str(payload["reconstruction_map"]),
        failure_modes=seq("failure_modes"), lineage=seq("lineage"),
        authority_boundary=None if payload.get("authority_boundary") is None else str(payload["authority_boundary"]),
        unknown_coordinates=seq("unknown_coordinates"),
    )
