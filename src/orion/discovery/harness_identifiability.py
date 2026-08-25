"""Finite theorem-identifiability checks for scientific harnesses.

The core treats a target claim and its registered alternatives as outcome
functions over a frozen case set.  A harness identifies the target only when
its outcome signature differs from every alternative.  These checks are
class-relative and non-authorizing.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Hashable, Mapping, Sequence


def _ordered(values):
    return tuple(sorted(values, key=lambda value: (type(value).__name__, repr(value))))


@dataclass(frozen=True)
class ClaimVariant:
    variant_id: str
    outcomes: Mapping[str, Hashable]
    description: str = ""

    def verify(self, case_ids: Sequence[str]) -> None:
        if not self.variant_id:
            raise ValueError("claim variant requires a non-empty identity")
        expected = set(case_ids)
        actual = set(self.outcomes)
        if actual != expected:
            missing = sorted(expected - actual)
            extra = sorted(actual - expected)
            raise ValueError(
                f"variant {self.variant_id!r} case mismatch: missing={missing}, extra={extra}"
            )

    def signature(self, case_ids: Sequence[str]) -> tuple[Hashable, ...]:
        self.verify(case_ids)
        return tuple(self.outcomes[case_id] for case_id in case_ids)


@dataclass(frozen=True)
class HarnessIdentifiabilityReport:
    target_id: str
    case_ids: tuple[str, ...]
    registered_variant_ids: tuple[str, ...]
    signatures: tuple[tuple[str, tuple[Hashable, ...]], ...]
    separated_alternative_ids: tuple[str, ...]
    equivalent_alternative_ids: tuple[str, ...]
    pairwise_indistinguishable: tuple[tuple[str, str], ...]
    target_identified: bool
    family_injective: bool
    target_outcomes_mixed: bool

    @property
    def grants_theorem_authority(self) -> bool:
        return False


def assess_identifiability(
    variants: Sequence[ClaimVariant],
    *,
    target_id: str,
    case_ids: Sequence[str],
) -> HarnessIdentifiabilityReport:
    ordered_cases = tuple(case_ids)
    if not ordered_cases or len(set(ordered_cases)) != len(ordered_cases):
        raise ValueError("case identities must be non-empty and unique")
    if not variants:
        raise ValueError("at least one claim variant is required")
    by_id: dict[str, ClaimVariant] = {}
    for variant in variants:
        if variant.variant_id in by_id:
            raise ValueError(f"duplicate variant identity: {variant.variant_id}")
        variant.verify(ordered_cases)
        by_id[variant.variant_id] = variant
    if target_id not in by_id:
        raise ValueError("target identity must be one of the registered variants")

    signatures = {
        variant_id: by_id[variant_id].signature(ordered_cases)
        for variant_id in _ordered(by_id)
    }
    target_signature = signatures[target_id]
    equivalent = tuple(
        variant_id
        for variant_id in _ordered(by_id)
        if variant_id != target_id and signatures[variant_id] == target_signature
    )
    separated = tuple(
        variant_id
        for variant_id in _ordered(by_id)
        if variant_id != target_id and signatures[variant_id] != target_signature
    )

    indistinguishable: list[tuple[str, str]] = []
    variant_ids = _ordered(by_id)
    for left, right in combinations(variant_ids, 2):
        if signatures[left] == signatures[right]:
            indistinguishable.append((left, right))

    return HarnessIdentifiabilityReport(
        target_id=target_id,
        case_ids=ordered_cases,
        registered_variant_ids=variant_ids,
        signatures=tuple((variant_id, signatures[variant_id]) for variant_id in variant_ids),
        separated_alternative_ids=separated,
        equivalent_alternative_ids=equivalent,
        pairwise_indistinguishable=tuple(indistinguishable),
        target_identified=not equivalent,
        family_injective=not indistinguishable,
        target_outcomes_mixed=len(set(target_signature)) > 1,
    )


def distinguishing_cases(
    target: ClaimVariant,
    alternative: ClaimVariant,
    case_ids: Sequence[str],
) -> tuple[str, ...]:
    target.verify(case_ids)
    alternative.verify(case_ids)
    return tuple(
        case_id
        for case_id in case_ids
        if target.outcomes[case_id] != alternative.outcomes[case_id]
    )


def clause_witness_map(
    target: ClaimVariant,
    deletion_mutations: Mapping[str, ClaimVariant],
    case_ids: Sequence[str],
) -> dict[str, tuple[str, ...]]:
    result: dict[str, tuple[str, ...]] = {}
    for clause_id in sorted(deletion_mutations):
        result[clause_id] = distinguishing_cases(
            target, deletion_mutations[clause_id], case_ids
        )
    return result


def unattained_clauses(
    target: ClaimVariant,
    deletion_mutations: Mapping[str, ClaimVariant],
    case_ids: Sequence[str],
) -> tuple[str, ...]:
    witnesses = clause_witness_map(target, deletion_mutations, case_ids)
    return tuple(clause_id for clause_id, rows in witnesses.items() if not rows)


@dataclass(frozen=True)
class PreconditionReport:
    eligible_case_ids: tuple[str, ...]
    ineligible_case_ids: tuple[str, ...]

    @property
    def attained(self) -> bool:
        return bool(self.eligible_case_ids)


def assess_precondition(
    case_ids: Sequence[str], eligibility: Mapping[str, bool]
) -> PreconditionReport:
    ordered_cases = tuple(case_ids)
    if set(ordered_cases) != set(eligibility):
        raise ValueError("eligibility map must cover exactly the frozen case set")
    eligible = tuple(case_id for case_id in ordered_cases if eligibility[case_id])
    ineligible = tuple(case_id for case_id in ordered_cases if not eligibility[case_id])
    return PreconditionReport(eligible, ineligible)


def minimal_distinguishing_case_sets(
    variants: Sequence[ClaimVariant],
    *,
    target_id: str,
    case_ids: Sequence[str],
) -> tuple[tuple[str, ...], ...]:
    """Enumerate minimum subsets identifying target against all alternatives.

    Intended for small frozen case families.  An empty result means the full
    harness support is itself non-identifying relative to the registered
    alternatives.
    """

    ordered_cases = tuple(case_ids)
    full = assess_identifiability(variants, target_id=target_id, case_ids=ordered_cases)
    if not full.target_identified:
        return ()
    for size in range(len(ordered_cases) + 1):
        winners: list[tuple[str, ...]] = []
        for subset in combinations(ordered_cases, size):
            report = assess_identifiability(
                variants, target_id=target_id, case_ids=subset
            )
            if report.target_identified:
                winners.append(tuple(subset))
        if winners:
            return tuple(winners)
    raise AssertionError("full case set identified target but no subset did")


def constant_variant(
    variant_id: str, case_ids: Sequence[str], outcome: Hashable
) -> ClaimVariant:
    return ClaimVariant(
        variant_id=variant_id,
        outcomes={case_id: outcome for case_id in case_ids},
        description=f"constant outcome {outcome!r}",
    )


__all__ = [
    "ClaimVariant",
    "HarnessIdentifiabilityReport",
    "PreconditionReport",
    "assess_identifiability",
    "assess_precondition",
    "clause_witness_map",
    "constant_variant",
    "distinguishing_cases",
    "minimal_distinguishing_case_sets",
    "unattained_clauses",
]
