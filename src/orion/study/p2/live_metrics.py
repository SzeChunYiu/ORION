"""Metrics that survive an incomplete denominator — and refusals for the rest.

A live campaign observes an open world. The set of works that exist is unknown,
so any quantity whose denominator is "all relevant works" is not merely hard to
compute here, it is undefined. Recall, false-negative counts and completeness
are all of that shape: they require knowing what we missed, and live, a work we
missed is indistinguishable from a work that does not exist.

The refusal is expressed in code rather than in prose because prose does not
survive a downstream caller in a hurry. Asking this module for recall raises;
asking it for the things a live run can actually measure returns a number.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from itertools import combinations

from orion.knowledge.routes import (
    CoverageEstimate,
    IndependenceVerdict,
    PairIndependence,
    assess_pair,
    estimate_coverage,
)

from .live_campaign import CampaignResult, LiveOutcome, RouteRun


class IncompleteDenominator(RuntimeError):
    """Raised when a metric would need a complete denominator this run lacks.

    Distinct from a failed computation: the quantity is not unavailable, it is
    undefined for an open-world run. Returning ``None`` or zero here would let
    a caller treat "we cannot know" as "we checked and it was fine".
    """


DENOMINATOR_BOUND_METRICS = frozenset(
    {
        "recall",
        "paper_recall",
        "complete_gold_recall",
        "screening_recall",
        "false_negative_count",
        "false_negatives",
        "completeness",
        "coverage_of_literature",
        "miss_rate",
        "sensitivity",
    }
)

DENOMINATOR_FREE_METRICS = frozenset(
    {
        "unique_relevant_per_route",
        "route_overlap_content_digest",
        "marginal_relevant_gain",
        "independence_verdicts",
        "coverage_diagnostic",
        "outcome_census",
        "open_obligation_census",
        "read_state_census",
        "route_stop_census",
        "cost_and_latency",
        "query_count",
    }
)

_WHY = (
    "this metric needs a complete denominator (the set of all relevant works). "
    "A live open-world campaign has none: an unretrieved work is "
    "indistinguishable from a nonexistent one, so the quantity is undefined "
    "rather than merely unmeasured. Report it from the frozen offline "
    "complete-gold world instead."
)


def metric_is_reportable(name: str) -> bool:
    """Whether a named metric may be computed from a live campaign."""

    return name.strip().lower() not in DENOMINATOR_BOUND_METRICS


def require_complete_denominator(name: str) -> None:
    """Refuse, loudly and typed, if the named metric needs a denominator."""

    if not metric_is_reportable(name):
        raise IncompleteDenominator(f"'{name}' is not reportable from a live campaign: {_WHY}")


def denominator_bound_metric(result: CampaignResult, name: str) -> float:
    """Single entry point for every metric this run structurally cannot give."""

    require_complete_denominator(name)
    raise IncompleteDenominator(
        f"'{name}' is not a recognised live-campaign metric; "
        f"reportable metrics are {sorted(DENOMINATOR_FREE_METRICS)}"
    )


def recall(result: CampaignResult) -> float:
    """Always raises. Present so the refusal is discoverable by name."""

    return denominator_bound_metric(result, "recall")


def false_negative_count(result: CampaignResult) -> int:
    """Always raises: a false negative is uncountable without a denominator."""

    return int(denominator_bound_metric(result, "false_negative_count"))


def completeness(result: CampaignResult) -> float:
    """Always raises: completeness is undefined over an open world."""

    return denominator_bound_metric(result, "completeness")


# --- what a live campaign can honestly report ------------------------------


@dataclass(frozen=True)
class RouteContribution:
    route_id: str
    route_kind: str
    backend: str
    query_derivation: str
    retrieved: int
    unique_to_route: int
    attempts: int
    queries: int
    spent_usd: float
    latency_seconds: float
    terminal_action: str
    open_obligations: tuple[str, ...]


def unique_contribution_per_route(
    result: CampaignResult,
) -> tuple[RouteContribution, ...]:
    """Per-route retrieval and the part of it no other route reached.

    Uniqueness is computed over content digests resolved through alias closure,
    so a work reached by two routes under two different identifiers counts once
    and is unique to neither.
    """

    by_route = {run.route.route_id: run.capture.captured for run in result.runs}
    contributions: list[RouteContribution] = []
    for run in result.runs:
        others: set[str] = set()
        for route_id, captured in by_route.items():
            if route_id != run.route.route_id:
                others |= captured
        contributions.append(
            RouteContribution(
                route_id=run.route.route_id,
                route_kind=run.route.route_kind.value,
                backend=run.route.backend,
                query_derivation=run.route.query_derivation,
                retrieved=len(run.capture.captured),
                unique_to_route=len(run.capture.captured - others),
                attempts=len(run.attempts),
                queries=len({item.query.query_id for item in run.attempts}),
                spent_usd=run.spent_usd,
                latency_seconds=round(
                    sum(item.latency_seconds for item in run.attempts), 6
                ),
                terminal_action=run.decision.action.value,
                open_obligations=run.open_obligations,
            )
        )
    return tuple(contributions)


def route_overlap(result: CampaignResult) -> dict[tuple[str, str], int]:
    """Pairwise overlap by content digest, for every ordered route pair."""

    overlap: dict[tuple[str, str], int] = {}
    for left, right in combinations(result.runs, 2):
        key = (left.route.route_id, right.route.route_id)
        overlap[key] = len(left.capture.captured & right.capture.captured)
    return overlap


def independence_verdicts(result: CampaignResult) -> tuple[PairIndependence, ...]:
    """Every pair's verdict, including the ones that fail to earn independence."""

    return tuple(
        assess_pair(left.capture, right.capture)
        for left, right in combinations(result.runs, 2)
    )


def earned_independent_pairs(result: CampaignResult) -> tuple[PairIndependence, ...]:
    return tuple(item for item in independence_verdicts(result) if item.independent)


def coverage_diagnostic(result: CampaignResult) -> CoverageEstimate:
    """Delegate to the shared estimator, which refuses more often than not.

    Reported as a diagnostic only. It never authorises stopping, and on this
    campaign's route set it will frequently refuse — two routes on one backend
    are not two capture occasions however different their queries look.
    """

    return estimate_coverage(result.captures)


def marginal_gain(result: CampaignResult) -> tuple[tuple[str, int, int], ...]:
    """Cumulative union after each route, in the order the routes ran.

    The second element is the union size, the third the gain that route added.
    This is the honest live analogue of a recall curve: it says how much new
    material each additional route bought, without claiming what fraction of
    the world that is.
    """

    union: set[str] = set()
    curve: list[tuple[str, int, int]] = []
    for run in result.runs:
        before = len(union)
        union |= run.capture.captured
        curve.append((run.route.route_id, len(union), len(union) - before))
    return tuple(curve)


def outcome_census(result: CampaignResult) -> dict[str, int]:
    """How many attempts ended in each typed outcome.

    Every outcome is retained, including the deferrals and failures. A census
    that silently dropped them would make a half-executed campaign look like a
    complete one.
    """

    census: dict[str, int] = {item.value: 0 for item in LiveOutcome}
    for attempt in result.attempts:
        census[attempt.outcome.value] += 1
    return census


def open_obligation_census(result: CampaignResult) -> dict[str, tuple[str, ...]]:
    """Per route, the looks it still owes."""

    return {
        run.route.route_id: run.open_obligations
        for run in result.runs
        if run.open_obligations
    }


def read_state_census(result: CampaignResult) -> dict[str, int]:
    """Duplicate processing versus legitimate reread, by read decision.

    ``ALREADY_READ`` is duplicate processing avoided; the other decisions are
    rereads a changed rendition, schema or frame made necessary. Collapsing
    them would hide the distinction the read-state design exists to make.
    """

    census: dict[str, int] = {}
    for attempt in result.attempts:
        for _, decision in attempt.read_decisions:
            census[decision] = census.get(decision, 0) + 1
    return census


def route_stop_census(result: CampaignResult) -> dict[str, str]:
    """The terminal action each route reached, and nothing about the task."""

    return {run.route.route_id: run.decision.action.value for run in result.runs}


def cost_and_latency(result: CampaignResult) -> dict[str, float]:
    """Resource use: queries issued, requests made, dollars and seconds."""

    attempts = result.attempts
    return {
        "attempts": float(len(attempts)),
        "queries": float(len({item.query.query_id for item in attempts})),
        "transport_requests": float(sum(len(item.trace_refs) for item in attempts)),
        "spent_usd": round(sum(run.spent_usd for run in result.runs), 6),
        "wallclock_seconds": round(
            sum(item.latency_seconds for item in attempts), 6
        ),
    }


def campaign_report(result: CampaignResult) -> dict:
    """Every denominator-free metric, in one auditable structure."""

    estimate = coverage_diagnostic(result)
    return {
        "campaign_id": result.campaign_id,
        "question_id": result.question.question_id,
        "policy_id": result.policy_id,
        "denominator": "INCOMPLETE_OPEN_WORLD",
        "recall_reportable": False,
        "observed_union": len(result.union_digests),
        "unique_relevant_per_route": [
            {
                "route_id": item.route_id,
                "route_kind": item.route_kind,
                "backend": item.backend,
                "query_derivation": item.query_derivation,
                "retrieved": item.retrieved,
                "unique_to_route": item.unique_to_route,
                "attempts": item.attempts,
                "queries": item.queries,
                "spent_usd": item.spent_usd,
                "latency_seconds": item.latency_seconds,
                "terminal_action": item.terminal_action,
                "open_obligations": list(item.open_obligations),
            }
            for item in unique_contribution_per_route(result)
        ],
        "route_overlap_content_digest": {
            f"{left}|{right}": value for (left, right), value in route_overlap(result).items()
        },
        "independence_verdicts": [
            {
                "left": item.left.value,
                "right": item.right.value,
                "verdict": item.verdict.value,
                "overlap": item.overlap,
                "independent": item.independent,
            }
            for item in independence_verdicts(result)
        ],
        "marginal_relevant_gain": [
            {"route_id": route_id, "union": union, "gain": gain}
            for route_id, union, gain in marginal_gain(result)
        ],
        "coverage_diagnostic": {
            "observed": estimate.observed,
            "population_estimate": estimate.population_estimate,
            "independent_pairs": estimate.independent_pairs,
            "refusal_reason": estimate.refusal_reason,
            "diagnostic_only": estimate.diagnostic_only,
        },
        "outcome_census": outcome_census(result),
        "open_obligation_census": {
            key: list(value) for key, value in open_obligation_census(result).items()
        },
        "read_state_census": read_state_census(result),
        "route_stop_census": route_stop_census(result),
        "cost_and_latency": cost_and_latency(result),
    }


__all__ = [
    "DENOMINATOR_BOUND_METRICS",
    "DENOMINATOR_FREE_METRICS",
    "IncompleteDenominator",
    "RouteContribution",
    "campaign_report",
    "completeness",
    "cost_and_latency",
    "coverage_diagnostic",
    "denominator_bound_metric",
    "earned_independent_pairs",
    "false_negative_count",
    "independence_verdicts",
    "marginal_gain",
    "metric_is_reportable",
    "open_obligation_census",
    "outcome_census",
    "read_state_census",
    "recall",
    "require_complete_denominator",
    "route_overlap",
    "route_stop_census",
    "unique_contribution_per_route",
]
