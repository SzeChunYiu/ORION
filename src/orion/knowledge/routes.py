from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum
from itertools import combinations

from orion.core.search import SearchRouteKind


class IndependenceVerdict(str, Enum):
    """Whether a pair of routes may be treated as independent capture occasions."""

    INDEPENDENT = "INDEPENDENT"
    SHARED_BACKEND = "SHARED_BACKEND"
    SHARED_QUERY_DERIVATION = "SHARED_QUERY_DERIVATION"
    SAME_ROUTE_KIND = "SAME_ROUTE_KIND"


@dataclass(frozen=True)
class RouteCapture:
    """What one route family actually caught, and what makes it its own occasion.

    `captured` holds content digests, never retrieval identifiers. A source that
    re-mints ids would otherwise make two routes look disjoint when they found
    the same paper, inflating every coverage estimate built on their overlap.

    `backend` and `query_derivation` are the independence claim. Capture-recapture
    needs occasions whose capture probabilities are not driven by a shared cause,
    and two routes hitting one index with queries derived the same way share both.
    """

    route_kind: SearchRouteKind
    backend: str
    query_derivation: str
    captured: frozenset[str]

    def __post_init__(self) -> None:
        if not self.backend.strip() or not self.query_derivation.strip():
            raise ValueError(
                "a route capture must declare its backend and query derivation; "
                "independence is constructed, not assumed"
            )


@dataclass(frozen=True)
class PairIndependence:
    left: SearchRouteKind
    right: SearchRouteKind
    verdict: IndependenceVerdict
    overlap: int

    @property
    def independent(self) -> bool:
        return self.verdict is IndependenceVerdict.INDEPENDENT


def assess_pair(left: RouteCapture, right: RouteCapture) -> PairIndependence:
    """Judge one pair, refusing independence on any shared cause.

    The order matters only for the reported reason. Any shared cause is
    disqualifying, and the check is deliberately conservative: positive
    dependence biases unseen-mass estimates *downward*, so a wrongly-accepted
    pair produces false confidence that the search is nearly exhausted.
    """

    overlap = len(left.captured & right.captured)
    if left.route_kind is right.route_kind:
        verdict = IndependenceVerdict.SAME_ROUTE_KIND
    elif left.backend == right.backend:
        verdict = IndependenceVerdict.SHARED_BACKEND
    elif left.query_derivation == right.query_derivation:
        verdict = IndependenceVerdict.SHARED_QUERY_DERIVATION
    else:
        verdict = IndependenceVerdict.INDEPENDENT
    return PairIndependence(left.route_kind, right.route_kind, verdict, overlap)


@dataclass(frozen=True)
class CoverageEstimate:
    """A diagnostic estimate of how much remains unfound, or a refusal.

    `population_estimate` is never a stopping authority. Confidence intervals on
    a class count are necessarily one-sided in the unhelpful direction — "at
    least this many exist", never "no more than this many remain" — and missing
    mass is provably unlearnable in relative error without distributional
    assumptions ORION cannot make.
    """

    observed: int
    population_estimate: float | None
    independent_pairs: int
    refusal_reason: str = ""
    diagnostic_only: bool = True

    @property
    def estimated_unseen(self) -> float | None:
        if self.population_estimate is None:
            return None
        return max(0.0, self.population_estimate - self.observed)

    @property
    def coverage_fraction(self) -> float | None:
        if not self.population_estimate:
            return None
        return min(1.0, self.observed / self.population_estimate)


@dataclass(frozen=True)
class EnsembleReport:
    captures: tuple[RouteCapture, ...]
    pairs: tuple[PairIndependence, ...]
    union: frozenset[str]
    estimate: CoverageEstimate

    @property
    def route_kinds(self) -> tuple[SearchRouteKind, ...]:
        return tuple(item.route_kind for item in self.captures)

    @property
    def singletons(self) -> int:
        """Items found by exactly one route — the f1 of this frequency spectrum."""

        return sum(1 for item in self.union if self._found_by(item) == 1)

    @property
    def doubletons(self) -> int:
        return sum(1 for item in self.union if self._found_by(item) == 2)

    def _found_by(self, item: str) -> int:
        return sum(1 for capture in self.captures if item in capture.captured)


def lincoln_petersen(left: int, right: int, overlap: int) -> float | None:
    """Two-source population estimate `N = n1*n2/m12`.

    Undefined at zero overlap: two routes that found nothing in common place no
    upper bound on the population at all, and returning a huge number there
    would read as a measurement rather than as the absence of one.
    """

    if overlap <= 0 or left <= 0 or right <= 0:
        return None
    return (left * right) / overlap


def estimate_coverage(captures: Sequence[RouteCapture]) -> CoverageEstimate:
    """Estimate population size from independent route overlap, or refuse.

    Refusal is the common case and the correct one. An adaptive searcher that
    follows up on what it just found converts singletons into doubletons, which
    deflates every unseen-mass estimator in the direction of "nearly done", so
    an estimate produced from dependent occasions is worse than no estimate.
    """

    union: set[str] = set()
    for capture in captures:
        union |= capture.captured
    observed = len(union)

    if len(captures) < 2:
        return CoverageEstimate(
            observed, None, 0, "capture-recapture needs at least two occasions"
        )

    pairs = [assess_pair(a, b) for a, b in combinations(captures, 2)]
    independent = [item for item in pairs if item.independent]
    if not independent:
        reasons = sorted({item.verdict.value for item in pairs})
        return CoverageEstimate(
            observed,
            None,
            0,
            "no independent pair of capture occasions: " + ", ".join(reasons),
        )

    by_kind = {item.route_kind: item for item in captures}
    usable: list[float] = []
    for pair in independent:
        estimate = lincoln_petersen(
            len(by_kind[pair.left].captured),
            len(by_kind[pair.right].captured),
            pair.overlap,
        )
        if estimate is not None:
            usable.append(estimate)
    if not usable:
        return CoverageEstimate(
            observed,
            None,
            len(independent),
            "independent routes share no captures, so the population is unbounded above",
        )

    # The most conservative independent estimate: the largest population implies
    # the most still unfound, which is the direction that fails safe.
    return CoverageEstimate(observed, max(usable), len(independent))


def build_ensemble(captures: Sequence[RouteCapture]) -> EnsembleReport:
    union: set[str] = set()
    for capture in captures:
        union |= capture.captured
    return EnsembleReport(
        captures=tuple(captures),
        pairs=tuple(assess_pair(a, b) for a, b in combinations(captures, 2)),
        union=frozenset(union),
        estimate=estimate_coverage(captures),
    )
