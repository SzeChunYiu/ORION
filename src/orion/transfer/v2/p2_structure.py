from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

from .canonical import content_digest


class StructuralRouteKind(str, Enum):
    """How a discovery query was derived.

    The first three values are ordinary discovery routes.  The final three are
    structure-conditioned routes introduced by the P2 extension.  A route kind
    describes derivation only; it does not grant route independence, transfer
    validity, novelty, or task-closure authority.
    """

    TOPICAL = "TOPICAL"
    CITATION = "CITATION"
    ENTITY = "ENTITY"
    METHOD_SIGNATURE = "METHOD_SIGNATURE"
    FAILURE_SIGNATURE = "FAILURE_SIGNATURE"
    REPRESENTATION_ANALOGY = "REPRESENTATION_ANALOGY"


class StructuralCandidateStatus(str, Enum):
    CANDIDATE = "CANDIDATE"
    OBSTRUCTION = "OBSTRUCTION"
    CANNOT_CHECK = "CANNOT_CHECK"


class StructuralRouteStop(str, Enum):
    EXHAUSTED = "EXHAUSTED"
    UNAVAILABLE = "UNAVAILABLE"
    CENSORED = "CENSORED"
    BUDGET_STOP = "BUDGET_STOP"


@dataclass(frozen=True)
class StructuralNeed:
    """A bounded structural need exported by an upstream ORION object.

    This is deliberately a small adapter surface.  P1/P3/P6 remain owners of
    method reconstruction, projection and formal equivalence.  P2 receives only
    the coordinates needed to derive candidate-acquisition routes.
    """

    need_id: str
    source_object_id: str
    source_object_digest: str
    assumptions: tuple[str, ...] = ()
    invariants: tuple[str, ...] = ()
    effects: tuple[str, ...] = ()
    failure_signature: tuple[str, ...] = ()
    representation_signature: tuple[str, ...] = ()
    reconstruction: str | None = None

    def __post_init__(self) -> None:
        if not self.need_id or not self.source_object_id:
            raise ValueError("need_id and source_object_id must be non-empty")
        if not self.source_object_digest.startswith("sha256:"):
            raise ValueError("source_object_digest must be sha256-prefixed")
        if not any(
            (
                self.assumptions,
                self.invariants,
                self.effects,
                self.failure_signature,
                self.representation_signature,
                self.reconstruction,
            )
        ):
            raise ValueError("a structural need must retain at least one coordinate")

    def payload(self) -> dict[str, object]:
        return {
            "schema": "StructuralNeed.v1",
            "need_id": self.need_id,
            "source_object_id": self.source_object_id,
            "source_object_digest": self.source_object_digest,
            "assumptions": list(self.assumptions),
            "invariants": list(self.invariants),
            "effects": list(self.effects),
            "failure_signature": list(self.failure_signature),
            "representation_signature": list(self.representation_signature),
            "reconstruction": self.reconstruction,
        }

    @property
    def digest(self) -> str:
        return content_digest(self.payload())

    @classmethod
    def from_mapping(
        cls,
        *,
        need_id: str,
        source_object_id: str,
        source_object_digest: str,
        coordinates: Mapping[str, object],
    ) -> "StructuralNeed":
        """Adapter for versioned P1/P3/P6 payloads without re-owning their schema."""

        def strings(key: str) -> tuple[str, ...]:
            value = coordinates.get(key, ())
            if value is None:
                return ()
            if not isinstance(value, (list, tuple, set, frozenset)):
                raise ValueError(f"{key} must be a sequence")
            return tuple(sorted(str(item) for item in value))

        reconstruction = coordinates.get("reconstruction")
        if reconstruction is not None:
            reconstruction = str(reconstruction)
        return cls(
            need_id=need_id,
            source_object_id=source_object_id,
            source_object_digest=source_object_digest,
            assumptions=strings("assumptions"),
            invariants=strings("invariants"),
            effects=strings("effects"),
            failure_signature=strings("failure_signature"),
            representation_signature=strings("representation_signature"),
            reconstruction=reconstruction,
        )


@dataclass(frozen=True)
class CandidateMethodSignature:
    candidate_id: str
    domain: str
    assumptions: tuple[str, ...] = ()
    invariants: tuple[str, ...] = ()
    effects: tuple[str, ...] = ()
    reconstruction: str | None = None
    provenance_digest: str = ""

    def __post_init__(self) -> None:
        if not self.candidate_id:
            raise ValueError("candidate_id must be non-empty")
        if self.provenance_digest and not self.provenance_digest.startswith("sha256:"):
            raise ValueError("provenance_digest must be sha256-prefixed")


@dataclass(frozen=True)
class StructuralCandidateReceipt:
    need_digest: str
    candidate_id: str
    status: StructuralCandidateStatus
    reason_codes: tuple[str, ...]
    matched_coordinates: tuple[str, ...]
    authority_terminal: str
    receipt_digest: str

    def unsigned_payload(self) -> dict[str, object]:
        return {
            "receipt_version": "ORION_P2_STRUCTURAL_CANDIDATE_RECEIPT_V1",
            "need_digest": self.need_digest,
            "candidate_id": self.candidate_id,
            "status": self.status.value,
            "reason_codes": list(self.reason_codes),
            "matched_coordinates": list(self.matched_coordinates),
            "authority_scope": "CANDIDATE_ACQUISITION_ONLY",
            "can_certify_transfer": False,
            "can_claim_novelty": False,
            "can_close_task": False,
            "authority_terminal": self.authority_terminal,
        }

    def verify(self) -> None:
        if self.authority_terminal != "NONE":
            raise ValueError("P2 structural candidate cannot grant scientific authority")
        if content_digest(self.unsigned_payload()) != self.receipt_digest:
            raise ValueError("P2 structural candidate receipt digest mismatch")


def assess_structural_candidate(
    need: StructuralNeed,
    candidate: CandidateMethodSignature,
) -> StructuralCandidateReceipt:
    missing_assumptions = sorted(set(need.assumptions) - set(candidate.assumptions))
    missing_invariants = sorted(set(need.invariants) - set(candidate.invariants))
    missing_effects = sorted(set(need.effects) - set(candidate.effects))
    reasons: list[str] = []
    matched: list[str] = []

    if missing_assumptions:
        reasons.extend(f"ASSUMPTION_MISMATCH:{item}" for item in missing_assumptions)
    elif need.assumptions:
        matched.append("assumptions")
    if missing_invariants:
        reasons.extend(f"INVARIANT_MISMATCH:{item}" for item in missing_invariants)
    elif need.invariants:
        matched.append("invariants")
    if missing_effects:
        reasons.extend(f"EFFECT_MISMATCH:{item}" for item in missing_effects)
    elif need.effects:
        matched.append("effects")

    if reasons:
        status = StructuralCandidateStatus.OBSTRUCTION
    elif need.reconstruction is not None and candidate.reconstruction is None:
        status = StructuralCandidateStatus.CANNOT_CHECK
        reasons.append("RECONSTRUCTION_UNKNOWN")
    elif need.reconstruction is not None and candidate.reconstruction != need.reconstruction:
        status = StructuralCandidateStatus.OBSTRUCTION
        reasons.append("RECONSTRUCTION_MISMATCH")
    else:
        status = StructuralCandidateStatus.CANDIDATE
        if need.reconstruction is not None:
            matched.append("reconstruction")
        if not candidate.provenance_digest:
            status = StructuralCandidateStatus.CANNOT_CHECK
            reasons.append("PROVENANCE_UNKNOWN")

    unsigned = {
        "receipt_version": "ORION_P2_STRUCTURAL_CANDIDATE_RECEIPT_V1",
        "need_digest": need.digest,
        "candidate_id": candidate.candidate_id,
        "status": status.value,
        "reason_codes": sorted(reasons),
        "matched_coordinates": sorted(matched),
        "authority_scope": "CANDIDATE_ACQUISITION_ONLY",
        "can_certify_transfer": False,
        "can_claim_novelty": False,
        "can_close_task": False,
        "authority_terminal": "NONE",
    }
    return StructuralCandidateReceipt(
        need_digest=need.digest,
        candidate_id=candidate.candidate_id,
        status=status,
        reason_codes=tuple(sorted(reasons)),
        matched_coordinates=tuple(sorted(matched)),
        authority_terminal="NONE",
        receipt_digest=content_digest(unsigned),
    )


@dataclass(frozen=True)
class StructuralDiscoveryRoute:
    route_id: str
    derivation_kind: StructuralRouteKind
    need_digest: str
    source_object_digest: str
    backend_identity: str
    query_derivation_identity: str
    capture_identity: str
    query_terms: tuple[str, ...]
    receipt_digest: str

    def unsigned_payload(self) -> dict[str, object]:
        return {
            "receipt_version": "StructuralDiscoveryRoute.v1",
            "route_id": self.route_id,
            "derivation_kind": self.derivation_kind.value,
            "need_digest": self.need_digest,
            "source_object_digest": self.source_object_digest,
            "backend_identity": self.backend_identity,
            "query_derivation_identity": self.query_derivation_identity,
            "capture_identity": self.capture_identity,
            "query_terms": list(self.query_terms),
            "authority_scope": "CANDIDATE_ACQUISITION_ONLY",
            "can_certify_independence_by_label": False,
            "can_certify_transfer": False,
            "can_close_task": False,
        }

    def verify(self) -> None:
        if content_digest(self.unsigned_payload()) != self.receipt_digest:
            raise ValueError("P2 structural route receipt digest mismatch")


def _derived_terms(need: StructuralNeed, kind: StructuralRouteKind) -> tuple[str, ...]:
    if kind is StructuralRouteKind.METHOD_SIGNATURE:
        values = (*need.assumptions, *need.invariants, *need.effects)
        if need.reconstruction:
            values = (*values, need.reconstruction)
    elif kind is StructuralRouteKind.FAILURE_SIGNATURE:
        values = (*need.failure_signature, *need.invariants, *need.effects)
    elif kind is StructuralRouteKind.REPRESENTATION_ANALOGY:
        values = (*need.representation_signature, *need.invariants, *need.effects)
    else:
        raise ValueError("ordinary topical/citation/entity routes require their native derivation path")
    terms = tuple(sorted({value.strip() for value in values if value and value.strip()}))
    if not terms:
        raise ValueError("selected structural derivation has no supported coordinates")
    return terms


def build_structural_route(
    need: StructuralNeed,
    *,
    derivation_kind: StructuralRouteKind,
    backend_identity: str,
    query_derivation_identity: str,
    capture_identity: str,
) -> StructuralDiscoveryRoute:
    for label, value in (
        ("backend_identity", backend_identity),
        ("query_derivation_identity", query_derivation_identity),
        ("capture_identity", capture_identity),
    ):
        if not value:
            raise ValueError(f"{label} must be non-empty")
    terms = _derived_terms(need, derivation_kind)
    identity_payload = {
        "kind": derivation_kind.value,
        "need_digest": need.digest,
        "backend_identity": backend_identity,
        "query_derivation_identity": query_derivation_identity,
        "capture_identity": capture_identity,
        "query_terms": list(terms),
    }
    route_id = f"structural:{content_digest(identity_payload).split(':', 1)[1][:20]}"
    unsigned = {
        "receipt_version": "StructuralDiscoveryRoute.v1",
        "route_id": route_id,
        "derivation_kind": derivation_kind.value,
        "need_digest": need.digest,
        "source_object_digest": need.source_object_digest,
        "backend_identity": backend_identity,
        "query_derivation_identity": query_derivation_identity,
        "capture_identity": capture_identity,
        "query_terms": list(terms),
        "authority_scope": "CANDIDATE_ACQUISITION_ONLY",
        "can_certify_independence_by_label": False,
        "can_certify_transfer": False,
        "can_close_task": False,
    }
    return StructuralDiscoveryRoute(
        route_id=route_id,
        derivation_kind=derivation_kind,
        need_digest=need.digest,
        source_object_digest=need.source_object_digest,
        backend_identity=backend_identity,
        query_derivation_identity=query_derivation_identity,
        capture_identity=capture_identity,
        query_terms=terms,
        receipt_digest=content_digest(unsigned),
    )


def routes_are_earned_independent(
    left: StructuralDiscoveryRoute,
    right: StructuralDiscoveryRoute,
) -> bool:
    """Strict P2 independence: labels/kinds alone never count as another route."""

    return (
        left.backend_identity != right.backend_identity
        and left.query_derivation_identity != right.query_derivation_identity
        and left.capture_identity != right.capture_identity
    )


@dataclass(frozen=True)
class StructuralRouteStopReceipt:
    route_id: str
    route_digest: str
    route_terminal: StructuralRouteStop
    task_terminal: str
    reason: str
    receipt_digest: str

    def unsigned_payload(self) -> dict[str, object]:
        return {
            "receipt_version": "ORION_P2_STRUCTURAL_ROUTE_STOP_V1",
            "route_id": self.route_id,
            "route_digest": self.route_digest,
            "route_terminal": self.route_terminal.value,
            "task_terminal": self.task_terminal,
            "reason": self.reason,
            "can_close_task": False,
        }

    def verify(self) -> None:
        if self.task_terminal != "OPEN":
            raise ValueError("structural route stop cannot close the scientific task")
        if content_digest(self.unsigned_payload()) != self.receipt_digest:
            raise ValueError("P2 structural stop receipt digest mismatch")


def stop_structural_route(
    route: StructuralDiscoveryRoute,
    *,
    terminal: StructuralRouteStop,
    reason: str,
) -> StructuralRouteStopReceipt:
    route.verify()
    if not reason:
        raise ValueError("route stop reason must be non-empty")
    unsigned = {
        "receipt_version": "ORION_P2_STRUCTURAL_ROUTE_STOP_V1",
        "route_id": route.route_id,
        "route_digest": route.receipt_digest,
        "route_terminal": terminal.value,
        "task_terminal": "OPEN",
        "reason": reason,
        "can_close_task": False,
    }
    return StructuralRouteStopReceipt(
        route_id=route.route_id,
        route_digest=route.receipt_digest,
        route_terminal=terminal,
        task_terminal="OPEN",
        reason=reason,
        receipt_digest=content_digest(unsigned),
    )


def structural_match_score(
    need: StructuralNeed,
    candidate: CandidateMethodSignature,
) -> float:
    """Bounded acquisition score; never a transfer/validity/novelty score."""

    receipt = assess_structural_candidate(need, candidate)
    if receipt.status is StructuralCandidateStatus.OBSTRUCTION:
        return -1.0
    total = sum(
        1
        for values in (need.assumptions, need.invariants, need.effects)
        if values
    ) + (1 if need.reconstruction is not None else 0)
    if total == 0:
        return 0.0
    score = len(receipt.matched_coordinates) / total
    if receipt.status is StructuralCandidateStatus.CANNOT_CHECK:
        score -= 0.25
    return score
