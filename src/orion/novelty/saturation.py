from __future__ import annotations

from dataclasses import dataclass

from orion.novelty.types import NoveltySearchRoute, REQUIRED_SEARCH_ROUTES


@dataclass(frozen=True)
class SearchRoundRecord:
    round_index: int
    route: NoveltySearchRoute
    queries: tuple[str, ...]
    finding_ids: tuple[str, ...]
    changed_residual_or_disposition: bool

    def __post_init__(self) -> None:
        if self.round_index < 1:
            raise ValueError("round_index must be positive")
        if not isinstance(self.route, NoveltySearchRoute):
            object.__setattr__(self, "route", NoveltySearchRoute(self.route))
        if not self.queries or any(not query.strip() for query in self.queries):
            raise ValueError("each search round requires at least one non-empty query")

    @property
    def empty_for_stop_rule(self) -> bool:
        return not self.changed_residual_or_disposition


@dataclass(frozen=True)
class SaturationStopReport:
    stop_rule_satisfied: bool
    consecutive_empty_rounds: int
    required_consecutive_empty_rounds: int
    covered_routes: tuple[NoveltySearchRoute, ...]
    missing_routes: tuple[NoveltySearchRoute, ...]
    reasons: tuple[str, ...]


def assess_saturation(
    rounds: tuple[SearchRoundRecord, ...],
    required_routes: tuple[NoveltySearchRoute, ...] = REQUIRED_SEARCH_ROUTES,
    required_consecutive_empty_rounds: int = 2,
) -> SaturationStopReport:
    covered = tuple(dict.fromkeys(record.route for record in rounds))
    missing = tuple(route for route in required_routes if route not in covered)
    consecutive = 0
    for record in reversed(rounds):
        if record.empty_for_stop_rule:
            consecutive += 1
        else:
            break
    reasons: list[str] = []
    if missing:
        reasons.append("required novelty search routes are incomplete")
    if consecutive < required_consecutive_empty_rounds:
        reasons.append("two consecutive empty rounds have not been observed")
    stop = not missing and consecutive >= required_consecutive_empty_rounds
    if stop:
        reasons = ("two consecutive empty rounds after all seven required routes",)
    return SaturationStopReport(
        stop_rule_satisfied=stop,
        consecutive_empty_rounds=consecutive,
        required_consecutive_empty_rounds=required_consecutive_empty_rounds,
        covered_routes=covered,
        missing_routes=missing,
        reasons=tuple(reasons),
    )


@dataclass(frozen=True)
class SearchSaturationProtocol:
    rounds: tuple[SearchRoundRecord, ...]
    required_routes: tuple[NoveltySearchRoute, ...] = REQUIRED_SEARCH_ROUTES
    required_consecutive_empty_rounds: int = 2

    def __post_init__(self) -> None:
        if self.required_consecutive_empty_rounds < 1:
            raise ValueError("required_consecutive_empty_rounds must be positive")
        if tuple(self.required_routes) != tuple(REQUIRED_SEARCH_ROUTES) and set(self.required_routes) != set(
            REQUIRED_SEARCH_ROUTES
        ):
            missing = tuple(route for route in REQUIRED_SEARCH_ROUTES if route not in self.required_routes)
            if missing:
                raise ValueError(f"novelty saturation cannot drop required routes: {missing}")

    @classmethod
    def from_rounds(cls, rounds: tuple[SearchRoundRecord, ...] | list[SearchRoundRecord]) -> SearchSaturationProtocol:
        return cls(rounds=tuple(rounds))

    def report(self) -> SaturationStopReport:
        return assess_saturation(
            self.rounds,
            self.required_routes,
            self.required_consecutive_empty_rounds,
        )

    @property
    def stop_rule_satisfied(self) -> bool:
        return self.report().stop_rule_satisfied
