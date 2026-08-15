from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum

from .store import canonical_bytes

GROWTH_COORDINATES: tuple[str, ...] = (
    "verified_closures",
    "evidence_bound_additions",
    "new_evidence_roots",
    "new_route_families",
    "new_residual_kinds",
    "new_mechanic_cells",
    "new_failure_signatures",
)


class SaturationVerdict(str, Enum):
    """Why a run may or may not stop."""

    GROWING = "GROWING"
    INVALID_BASIS = "INVALID_BASIS"
    INSUFFICIENT_FLAT_ROUNDS = "INSUFFICIENT_FLAT_ROUNDS"
    DEPENDENT_FLAT_ROUNDS = "DEPENDENT_FLAT_ROUNDS"
    A_PRIORI_FRAME_FLAT = "A_PRIORI_FRAME_FLAT"
    # Named after Saunders et al. (2018): with the basis frozen, only kinds
    # already inside the frame can be discovered, so this is *a priori*
    # thematic saturation. Calling it inductive or theoretical saturation is
    # the exact conflation that paper was written to name.


@dataclass(frozen=True)
class SaturationBasis:
    """The declared semantics against which flatness is measured.

    Flatness only means something relative to a fixed measuring apparatus. If
    the dimension vocabulary, the selection policy or the registered verifiers
    change, previously flat rounds no longer testify to anything, so the basis
    is fingerprinted and prior rounds carrying a different fingerprint void the
    verdict rather than silently counting toward it.
    """

    root_mechanic_id: str
    dimension_vocabulary: tuple[str, ...]
    priority_order: tuple[str, ...]
    evidence_schemes: tuple[str, ...]
    registered_check_ids: tuple[str, ...]
    selection_limit: int

    @property
    def fingerprint(self) -> str:
        return hashlib.sha256(
            canonical_bytes(
                {
                    "root_mechanic_id": self.root_mechanic_id,
                    "dimension_vocabulary": list(self.dimension_vocabulary),
                    "priority_order": list(self.priority_order),
                    "evidence_schemes": list(self.evidence_schemes),
                    "registered_check_ids": list(self.registered_check_ids),
                    "selection_limit": self.selection_limit,
                }
            )
        ).hexdigest()


@dataclass(frozen=True)
class GrowthVector:
    """One round's movement, in the space where ORION's growth is defined.

    Every coordinate is a non-negative count of something that did not exist
    before this round. Flatness is `sum == 0`: it is non-compensatory, so a
    round cannot look productive by trading knowledge growth against method
    growth.
    """

    round_index: int
    basis_fingerprint: str
    verified_closures: int = 0
    evidence_bound_additions: int = 0
    new_evidence_roots: int = 0
    new_route_families: int = 0
    new_residual_kinds: int = 0
    new_mechanic_cells: int = 0
    new_failure_signatures: int = 0
    evidence_lineage: tuple[str, ...] = ()

    @property
    def coordinates(self) -> tuple[tuple[str, int], ...]:
        return tuple((name, getattr(self, name)) for name in GROWTH_COORDINATES)

    @property
    def magnitude(self) -> int:
        return sum(value for _, value in self.coordinates)

    @property
    def flat(self) -> bool:
        return self.magnitude == 0


@dataclass(frozen=True)
class SaturationReport:
    verdict: SaturationVerdict
    flat_streak: int
    independent_flat_rounds: int
    required_flat_rounds: int
    reasons: tuple[str, ...] = ()
    absolute_complete: bool = False

    @property
    def may_stop(self) -> bool:
        """Whether the run may stop — a budget decision, not a recall claim."""

        return self.verdict is SaturationVerdict.A_PRIORI_FRAME_FLAT

    @property
    def certifies_recall(self) -> bool:
        """Always False. No recall statement is licensed by this verdict.

        The rule implemented here — N consecutive rounds with zero growth under
        a fixed frame — is Francis et al.'s "10+3", Guest/Namey/Chen's
        new-information threshold at 0%, and TAR's IH50. All three literatures
        classify it as a heuristic. Guest et al.'s own bootstrap puts the 0%
        threshold at 87-89% of themes captured; Callaghan et al. (2024) measured
        a 5th-percentile recall of 53% for the consecutive-zero family and
        concluded that arbitrary stopping criteria "have no place in
        high-quality systematic reviews".

        It also fails all three of that paper's stated requirements: it is not
        target-bound, not statistically justified, and not parameter-independent
        (`required_flat_rounds` is exactly the arbitrary X they name).
        """

        return False


def _max_disjoint_lineage_subset(lineages: Sequence[frozenset[str]]) -> int:
    """Largest set of rounds whose evidence lineages are pairwise disjoint.

    Rounds that all rest on the same evidence are one observation repeated, not
    independent confirmations of flatness. Greedy smallest-first is a lower
    bound, which can only delay saturation, never manufacture it.
    """

    chosen: list[frozenset[str]] = []
    for lineage in sorted(lineages, key=len):
        if all(not (lineage & taken) for taken in chosen):
            chosen.append(lineage)
    return len(chosen)


def assess_saturation(
    vectors: Sequence[GrowthVector],
    basis: SaturationBasis,
    *,
    required_flat_rounds: int = 2,
) -> SaturationReport:
    """Decide whether repeated challenges are flat enough to stop, and why not.

    This is bounded saturation: flatness under a declared basis and a declared
    number of independent rounds. It never claims the knowledge space is
    exhausted, which is why `absolute_complete` is fixed at False.
    """

    if required_flat_rounds < 1:
        raise ValueError("required_flat_rounds must be positive")
    if not vectors:
        return SaturationReport(
            SaturationVerdict.INSUFFICIENT_FLAT_ROUNDS,
            0,
            0,
            required_flat_rounds,
            ("no rounds have been observed",),
        )

    fingerprint = basis.fingerprint
    stale = tuple(
        item.round_index for item in vectors if item.basis_fingerprint != fingerprint
    )

    streak: list[GrowthVector] = []
    for vector in sorted(vectors, key=lambda item: item.round_index):
        if vector.flat:
            streak.append(vector)
        else:
            streak = []

    if stale and any(item.round_index in stale for item in streak):
        return SaturationReport(
            SaturationVerdict.INVALID_BASIS,
            len(streak),
            0,
            required_flat_rounds,
            tuple(f"round {index} was measured under a different basis" for index in stale),
        )
    if not streak:
        return SaturationReport(
            SaturationVerdict.GROWING,
            0,
            0,
            required_flat_rounds,
            ("the most recent round still produced growth",),
        )
    if len(streak) < required_flat_rounds:
        return SaturationReport(
            SaturationVerdict.INSUFFICIENT_FLAT_ROUNDS,
            len(streak),
            0,
            required_flat_rounds,
            (f"{len(streak)} flat round(s), {required_flat_rounds} required",),
        )

    independent = _max_disjoint_lineage_subset(
        [frozenset(item.evidence_lineage) for item in streak]
    )
    if independent < required_flat_rounds:
        return SaturationReport(
            SaturationVerdict.DEPENDENT_FLAT_ROUNDS,
            len(streak),
            independent,
            required_flat_rounds,
            (
                f"{len(streak)} flat rounds share evidence lineage; only {independent} "
                "are independent",
            ),
        )
    return SaturationReport(
        SaturationVerdict.A_PRIORI_FRAME_FLAT,
        len(streak),
        independent,
        required_flat_rounds,
        (
            f"flat over {len(streak)} rounds under frozen basis "
            f"{fingerprint[:12]}; says nothing about kinds outside the frame",
            f"residual novelty rate <= {3 / max(independent, 1):.3f} at 95% by the "
            "rule of three, and only if those rounds were independent draws",
        ),
    )


def growth_from_round(
    round_index: int,
    basis_fingerprint: str,
    *,
    verified_record_ids: Sequence[str],
    evidence_bound_record_ids: Sequence[str],
    evidence_refs: Sequence[str],
    route_families: Sequence[str],
    residual_kinds: Sequence[str],
    mechanic_ids: Sequence[str],
    failure_signatures: Sequence[tuple[str, ...]],
    seen: Mapping[str, set[str]],
) -> GrowthVector:
    """Score one round against everything previously seen, updating `seen`."""

    def _fresh(key: str, values: Sequence[str]) -> int:
        bucket = seen.setdefault(key, set())
        new = {item for item in values if item not in bucket}
        bucket.update(new)
        return len(new)

    lineage = tuple(sorted(set(evidence_refs)))
    return GrowthVector(
        round_index=round_index,
        basis_fingerprint=basis_fingerprint,
        verified_closures=len(verified_record_ids),
        evidence_bound_additions=len(evidence_bound_record_ids),
        new_evidence_roots=_fresh("evidence", lineage),
        new_route_families=_fresh("routes", route_families),
        new_residual_kinds=_fresh("residuals", residual_kinds),
        new_mechanic_cells=_fresh("mechanics", mechanic_ids),
        new_failure_signatures=_fresh(
            "failures", ["|".join(item) for item in failure_signatures]
        ),
        evidence_lineage=lineage,
    )
