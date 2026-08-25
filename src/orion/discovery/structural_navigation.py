"""Responsibility-aware structural navigation for cross-domain donor search.

The reference implementation deliberately keeps a vector-valued comparison.
No arbitrary scalar score is used to declare one route scientifically superior.
The result is a finite search aid and does not grant transfer validity or novelty.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from orion.transfer.v2.canonical import content_digest


def _sorted_unique(values: Sequence[str]) -> tuple[str, ...]:
    return tuple(sorted({str(value) for value in values}))


@dataclass(frozen=True)
class StructuralAddress:
    address_id: str
    domain_id: str
    role_ids: tuple[str, ...]
    relation_signature_ids: tuple[str, ...]
    invariant_ids: tuple[str, ...]
    obstruction_ids: tuple[str, ...]
    validation_kind: str
    interface_ids: tuple[str, ...]

    def verify(self) -> None:
        if not self.address_id or not self.domain_id or not self.validation_kind:
            raise ValueError("structural address requires identity/domain/validation")
        if not self.role_ids or not self.relation_signature_ids:
            raise ValueError("structural address requires roles and relations")
        if any(
            not item
            for item in (
                self.role_ids
                + self.relation_signature_ids
                + self.invariant_ids
                + self.obstruction_ids
                + self.interface_ids
            )
        ):
            raise ValueError("structural address identities must be non-empty")


@dataclass(frozen=True)
class StructuralCorrespondence:
    correspondence_id: str
    source_address_id: str
    target_address_id: str
    mapped_target_role_ids: tuple[str, ...]
    mapped_target_relation_ids: tuple[str, ...]
    mapped_target_invariant_ids: tuple[str, ...]
    mapped_target_obstruction_ids: tuple[str, ...]
    mapped_target_interface_ids: tuple[str, ...]
    validation_correspondence: bool

    def verify(self) -> None:
        if not self.correspondence_id:
            raise ValueError("correspondence identity is required")
        if not self.source_address_id or not self.target_address_id:
            raise ValueError("correspondence requires source and target addresses")


@dataclass(frozen=True)
class StructuralDistortion:
    missing_role_ids: tuple[str, ...]
    missing_relation_ids: tuple[str, ...]
    missing_invariant_ids: tuple[str, ...]
    missing_obstruction_ids: tuple[str, ...]
    missing_interface_ids: tuple[str, ...]
    validation_mismatch: bool

    @property
    def exact(self) -> bool:
        return not (
            self.missing_role_ids
            or self.missing_relation_ids
            or self.missing_invariant_ids
            or self.missing_obstruction_ids
            or self.missing_interface_ids
            or self.validation_mismatch
        )

    @property
    def vector(self) -> tuple[int, int, int, int, int, int]:
        return (
            len(self.missing_role_ids),
            len(self.missing_relation_ids),
            len(self.missing_invariant_ids),
            len(self.missing_obstruction_ids),
            len(self.missing_interface_ids),
            int(self.validation_mismatch),
        )


def evaluate_structural_correspondence(
    source: StructuralAddress,
    target: StructuralAddress,
    correspondence: StructuralCorrespondence,
) -> StructuralDistortion:
    source.verify()
    target.verify()
    correspondence.verify()
    if correspondence.source_address_id != source.address_id:
        raise ValueError("source address identity mismatch")
    if correspondence.target_address_id != target.address_id:
        raise ValueError("target address identity mismatch")
    return StructuralDistortion(
        missing_role_ids=tuple(
            sorted(set(target.role_ids) - set(correspondence.mapped_target_role_ids))
        ),
        missing_relation_ids=tuple(
            sorted(
                set(target.relation_signature_ids)
                - set(correspondence.mapped_target_relation_ids)
            )
        ),
        missing_invariant_ids=tuple(
            sorted(set(target.invariant_ids) - set(correspondence.mapped_target_invariant_ids))
        ),
        missing_obstruction_ids=tuple(
            sorted(
                set(target.obstruction_ids)
                - set(correspondence.mapped_target_obstruction_ids)
            )
        ),
        missing_interface_ids=tuple(
            sorted(set(target.interface_ids) - set(correspondence.mapped_target_interface_ids))
        ),
        validation_mismatch=not correspondence.validation_correspondence,
    )


@dataclass(frozen=True)
class NavigationOption:
    option_id: str
    reachable_contract_ids: tuple[str, ...]
    distortion_vector: tuple[int, ...]
    resource_vector: tuple[int, ...]
    authority_debt: int
    origin_trace_id: str

    def verify(self) -> None:
        if not self.option_id or not self.origin_trace_id:
            raise ValueError("navigation option requires identity and origin trace")
        if not self.reachable_contract_ids:
            raise ValueError("navigation option requires at least one reachable contract")
        if any(value < 0 for value in self.distortion_vector + self.resource_vector):
            raise ValueError("distortion/resource coordinates must be non-negative")
        if self.authority_debt < 0:
            raise ValueError("authority debt cannot be negative")


def _componentwise_le(left: tuple[int, ...], right: tuple[int, ...]) -> bool:
    if len(left) != len(right):
        raise ValueError("navigation vectors must have matching dimensions")
    return all(a <= b for a, b in zip(left, right, strict=True))


def dominates(left: NavigationOption, right: NavigationOption) -> bool:
    """Return whether left weakly improves every registered coordinate."""

    left.verify()
    right.verify()
    reach_superset = set(left.reachable_contract_ids).issuperset(right.reachable_contract_ids)
    distortion_le = _componentwise_le(left.distortion_vector, right.distortion_vector)
    resources_le = _componentwise_le(left.resource_vector, right.resource_vector)
    debt_le = left.authority_debt <= right.authority_debt
    strict = (
        set(left.reachable_contract_ids) != set(right.reachable_contract_ids)
        or left.distortion_vector != right.distortion_vector
        or left.resource_vector != right.resource_vector
        or left.authority_debt != right.authority_debt
    )
    return reach_superset and distortion_le and resources_le and debt_le and strict


def pareto_navigation_frontier(
    options: Sequence[NavigationOption],
) -> tuple[NavigationOption, ...]:
    rows = tuple(options)
    if not rows:
        raise ValueError("navigation frontier requires at least one option")
    for row in rows:
        row.verify()
    if len({row.option_id for row in rows}) != len(rows):
        raise ValueError("duplicate navigation option identity")
    frontier = [
        row
        for row in rows
        if not any(other.option_id != row.option_id and dominates(other, row) for other in rows)
    ]
    return tuple(sorted(frontier, key=lambda row: row.option_id))


@dataclass(frozen=True)
class NavigationReceipt:
    problem_address_id: str
    option_ids: tuple[str, ...]
    frontier_option_ids: tuple[str, ...]
    exact_correspondence_ids: tuple[str, ...]
    partial_correspondence_ids: tuple[str, ...]
    digest: str

    @property
    def grants_scientific_validity(self) -> bool:
        return False

    @property
    def grants_novelty_authority(self) -> bool:
        return False

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "StructuralNavigationReceipt.v1",
            "problem_address_id": self.problem_address_id,
            "option_ids": list(self.option_ids),
            "frontier_option_ids": list(self.frontier_option_ids),
            "exact_correspondence_ids": list(self.exact_correspondence_ids),
            "partial_correspondence_ids": list(self.partial_correspondence_ids),
            "grants_scientific_validity": False,
            "grants_novelty_authority": False,
        }

    def verify(self) -> None:
        if not self.problem_address_id:
            raise ValueError("navigation receipt requires a problem address")
        if not set(self.frontier_option_ids).issubset(self.option_ids):
            raise ValueError("frontier contains an unregistered option")
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("navigation receipt digest mismatch")


def build_navigation_receipt(
    *,
    problem_address_id: str,
    options: Sequence[NavigationOption],
    correspondence_results: Sequence[tuple[str, StructuralDistortion]],
) -> NavigationReceipt:
    frontier = pareto_navigation_frontier(options)
    exact_ids = sorted(
        correspondence_id
        for correspondence_id, distortion in correspondence_results
        if distortion.exact
    )
    partial_ids = sorted(
        correspondence_id
        for correspondence_id, distortion in correspondence_results
        if not distortion.exact
    )
    payload = {
        "version": "StructuralNavigationReceipt.v1",
        "problem_address_id": str(problem_address_id),
        "option_ids": sorted(row.option_id for row in options),
        "frontier_option_ids": sorted(row.option_id for row in frontier),
        "exact_correspondence_ids": exact_ids,
        "partial_correspondence_ids": partial_ids,
        "grants_scientific_validity": False,
        "grants_novelty_authority": False,
    }
    receipt = NavigationReceipt(
        problem_address_id=payload["problem_address_id"],
        option_ids=tuple(payload["option_ids"]),
        frontier_option_ids=tuple(payload["frontier_option_ids"]),
        exact_correspondence_ids=tuple(payload["exact_correspondence_ids"]),
        partial_correspondence_ids=tuple(payload["partial_correspondence_ids"]),
        digest=content_digest(payload),
    )
    receipt.verify()
    return receipt


__all__ = [
    "NavigationOption",
    "NavigationReceipt",
    "StructuralAddress",
    "StructuralCorrespondence",
    "StructuralDistortion",
    "build_navigation_receipt",
    "dominates",
    "evaluate_structural_correspondence",
    "pareto_navigation_frontier",
]
