from __future__ import annotations

import re
from dataclasses import dataclass


_TOKEN = re.compile(r"[a-z0-9]+")


def _norm(values: tuple[str, ...]) -> frozenset[str]:
    tokens: set[str] = set()
    for value in values:
        tokens.update(_TOKEN.findall(value.lower()))
    return frozenset(tokens)


@dataclass(frozen=True)
class FunctionalOperationSignature:
    """Name-independent description of an atomic research operation.

    Discipline labels are intentionally absent. The object says what the
    operation consumes/produces, what it must preserve, and how it fails. This
    is the bridge from an ORION mechanic to mature fields that study the same
    function under different vocabulary.
    """

    signature_id: str
    operation_terms: tuple[str, ...]
    object_terms: tuple[str, ...] = ()
    failure_terms: tuple[str, ...] = ()
    invariant_terms: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.signature_id.strip() or not self.operation_terms:
            raise ValueError("functional signature identity and operation terms are required")
        if any(not item.strip() for item in (*self.operation_terms, *self.object_terms, *self.failure_terms, *self.invariant_terms)):
            raise ValueError("functional signature terms must be non-empty")

    @property
    def all_tokens(self) -> frozenset[str]:
        return _norm(
            (*self.operation_terms, *self.object_terms, *self.failure_terms, *self.invariant_terms)
        )


@dataclass(frozen=True)
class ParentDisciplineProfile:
    """Externally sourced functional profile for a mature discipline.

    `discipline_id` is output metadata, never a feature used for matching. The
    match is driven only by mechanism/object/failure/invariant terms with source
    evidence attached, preventing a hidden-name benchmark from succeeding by
    leaking the answer label into the query signature.
    """

    profile_id: str
    discipline_id: str
    mechanism_terms: tuple[str, ...]
    object_terms: tuple[str, ...] = ()
    failure_terms: tuple[str, ...] = ()
    invariant_terms: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.profile_id.strip() or not self.discipline_id.strip() or not self.mechanism_terms:
            raise ValueError("parent-discipline profile identity/name/mechanisms are required")
        if not self.evidence_ids:
            raise ValueError("parent-discipline profiles require source evidence")


@dataclass(frozen=True)
class ParentDisciplineCandidate:
    profile_id: str
    discipline_id: str
    score: float
    matched_terms: tuple[str, ...]
    lexically_independent: bool
    evidence_ids: tuple[str, ...]


_WEIGHTS = {
    "operation": 4.0,
    "object": 2.0,
    "failure": 2.0,
    "invariant": 1.0,
}


def _weighted_overlap(signature: FunctionalOperationSignature, profile: ParentDisciplineProfile) -> tuple[float, tuple[str, ...]]:
    groups = (
        (_norm(signature.operation_terms), _norm(profile.mechanism_terms), _WEIGHTS["operation"]),
        (_norm(signature.object_terms), _norm(profile.object_terms), _WEIGHTS["object"]),
        (_norm(signature.failure_terms), _norm(profile.failure_terms), _WEIGHTS["failure"]),
        (_norm(signature.invariant_terms), _norm(profile.invariant_terms), _WEIGHTS["invariant"]),
    )
    numerator = 0.0
    denominator = 0.0
    matched: set[str] = set()
    for left, right, weight in groups:
        if not left:
            continue
        denominator += weight * len(left)
        intersection = left & right
        numerator += weight * len(intersection)
        matched.update(intersection)
    return (0.0 if denominator == 0 else numerator / denominator, tuple(sorted(matched)))


def discover_parent_disciplines(
    signature: FunctionalOperationSignature,
    profiles: tuple[ParentDisciplineProfile, ...],
    *,
    minimum_score: float = 0.12,
) -> tuple[ParentDisciplineCandidate, ...]:
    """Rank mature fields from functional correspondence without label leakage."""

    candidates: list[ParentDisciplineCandidate] = []
    signature_tokens = signature.all_tokens
    for profile in profiles:
        score, matched = _weighted_overlap(signature, profile)
        if score < minimum_score or not matched:
            continue
        label_tokens = _norm((profile.discipline_id,))
        candidates.append(
            ParentDisciplineCandidate(
                profile_id=profile.profile_id,
                discipline_id=profile.discipline_id,
                score=score,
                matched_terms=matched,
                lexically_independent=not bool(signature_tokens & label_tokens),
                evidence_ids=profile.evidence_ids,
            )
        )
    return tuple(
        sorted(candidates, key=lambda item: (-item.score, item.discipline_id, item.profile_id))
    )


def top_parent_discipline(
    signature: FunctionalOperationSignature,
    profiles: tuple[ParentDisciplineProfile, ...],
    *,
    minimum_score: float = 0.12,
) -> ParentDisciplineCandidate | None:
    ranked = discover_parent_disciplines(signature, profiles, minimum_score=minimum_score)
    return ranked[0] if ranked else None


def named_basis_mentions(
    named_routes: tuple[str, ...],
    discipline_id: str,
) -> bool:
    """Historical diagnostic only: does a frozen named basis explicitly name a field?"""

    discipline_tokens = _norm((discipline_id,))
    basis_tokens = _norm(named_routes)
    return bool(discipline_tokens) and discipline_tokens.issubset(basis_tokens)


__all__ = [
    "FunctionalOperationSignature",
    "ParentDisciplineCandidate",
    "ParentDisciplineProfile",
    "discover_parent_disciplines",
    "named_basis_mentions",
    "top_parent_discipline",
]
