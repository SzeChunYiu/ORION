"""Host-owned scoring for the ORION-P2 offline discovery study.

Custody rule: the candidate never touches anything in here. It does not compute
its own recall, does not classify its own reads, does not decide whether its own
closure was premature, and cannot mutate what this module returns — every
structure handed back is a tuple or a fresh dict.

The verdicts this module reaches are deliberately *replayed* rather than
reported. "Did the system stop that route too early?" is not answerable from the
stop decision alone; it needs the state of the world at the index the decision
was taken — which gold was still unretrieved, and which routes were still alive
at that moment. The ordered event timeline exists so that question has an answer.

Emissions are a superset of the obvious metric needs, because the statistical
plan is being frozen in a sibling lane and will bind fields from this list. New
quantities belong in the rich artifact, which is content-addressed by the result
record's `raw_artifact_hash`; the record's own `metrics` object accepts numbers
only, so nothing structured may be smuggled into it.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Any

from .cases import DiscoveryTask
from .corpus import ROUTE_SPEC_BY_ROUTE, DiscoveryRoute, DiscoveryWorld
from .systems import ReadClassification, StopScope, SystemTrace, TransportStatus


@dataclass(frozen=True)
class EvaluationInputs:
    """Everything the evaluator needs. Assembled host-side, never by a candidate."""

    world: DiscoveryWorld
    task: DiscoveryTask
    trace: SystemTrace


@dataclass(frozen=True)
class RouteContribution:
    """What one route actually added, separated from what it merely echoed."""

    route: str
    backend_identity: str
    query_derivation_identity: str
    calls: int
    retrieved_identities: tuple[str, ...]
    unique_relevant_identities: tuple[str, ...]
    relevant_identities: tuple[str, ...]
    transport_failures: int

    def as_json(self) -> dict[str, Any]:
        return {
            "route": self.route,
            "backend_identity": self.backend_identity,
            "query_derivation_identity": self.query_derivation_identity,
            "calls": self.calls,
            "retrieved_identities": list(self.retrieved_identities),
            "unique_relevant_identities": list(self.unique_relevant_identities),
            "relevant_identities": list(self.relevant_identities),
            "transport_failures": self.transport_failures,
        }


@dataclass(frozen=True)
class StopAudit:
    """A stop decision, replayed against the world state at the index it was taken."""

    index: int
    scope: str
    route: str
    reason: str
    claimed_complete: bool
    still_reachable_count: int
    still_reachable_identities: tuple[str, ...]
    remaining_route_calls: int
    premature: bool

    def as_json(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "scope": self.scope,
            "route": self.route,
            "reason": self.reason,
            "claimed_complete": self.claimed_complete,
            "still_reachable_count": self.still_reachable_count,
            "still_reachable_identities": list(self.still_reachable_identities),
            "remaining_route_calls": self.remaining_route_calls,
            "premature": self.premature,
        }


@dataclass(frozen=True)
class Evaluation:
    """The complete host verdict on one run. Every field is immutable."""

    task_id: str
    case_family: str
    system_id: str
    seed: int
    status: str
    failure_class: str | None

    gold_denominator: int
    discovered_gold_identities: tuple[str, ...]
    missed_gold_identities: tuple[str, ...]
    claimed_identities: tuple[str, ...]
    unsupported_claimed_identities: tuple[str, ...]
    false_positive_identities: tuple[str, ...]

    route_contributions: tuple[RouteContribution, ...]
    route_pair_overlap: tuple[tuple[str, str, float, int], ...]
    marginal_relevant_gain: tuple[tuple[str, int], ...]

    stop_audits: tuple[StopAudit, ...]
    censored_identities: tuple[str, ...]
    unavailable_route_events: tuple[tuple[int, str, str], ...]

    processing_pairs: tuple[tuple[str, str], ...]
    duplicate_processing_count: int
    legitimate_reread_count: int
    first_read_count: int

    resources: dict[str, float]

    def numeric_metrics(self) -> dict[str, float]:
        """The record's `metrics` object: numbers only, per the result-record schema.

        Booleans are emitted as 1.0/0.0 rather than `true`/`false` because JSON
        Schema does not accept a boolean where a number is required, and a record
        that fails its own schema is not evidence of anything.
        """

        denominator = float(self.gold_denominator)
        claimed = len(self.claimed_identities)
        true_positive = claimed - len(self.false_positive_identities)
        metrics: dict[str, float] = {
            "complete_gold_recall": (
                len(self.discovered_gold_identities) / denominator if denominator else 0.0
            ),
            "precision": (true_positive / claimed) if claimed else 0.0,
            "gold_denominator": denominator,
            "discovered_gold_count": float(len(self.discovered_gold_identities)),
            "missed_gold_count": float(len(self.missed_gold_identities)),
            "false_positive_count": float(len(self.false_positive_identities)),
            "unsupported_claim_count": float(len(self.unsupported_claimed_identities)),
            "premature_task_closure": float(
                any(item.premature and item.scope == StopScope.TASK.value for item in self.stop_audits)
            ),
            "route_stop_false_positive_count": float(
                sum(
                    1
                    for item in self.stop_audits
                    if item.scope == StopScope.ROUTE.value and item.premature
                )
            ),
            "censored_identity_count": float(len(self.censored_identities)),
            "unavailable_route_event_count": float(len(self.unavailable_route_events)),
            "duplicate_processing_count": float(self.duplicate_processing_count),
            "legitimate_reread_count": float(self.legitimate_reread_count),
            "first_read_count": float(self.first_read_count),
            "duplicate_processing_rate": (
                self.duplicate_processing_count
                / max(1, self.duplicate_processing_count + self.legitimate_reread_count + self.first_read_count)
            ),
            "routes_used": float(sum(1 for item in self.route_contributions if item.calls)),
            "mean_route_pair_overlap": (
                sum(item[2] for item in self.route_pair_overlap) / len(self.route_pair_overlap)
                if self.route_pair_overlap
                else 0.0
            ),
            "marginal_relevant_gain_after_first_route": float(
                sum(count for _, count in self.marginal_relevant_gain[1:])
            ),
        }
        for contribution in self.route_contributions:
            key = contribution.route.lower()
            metrics[f"unique_relevant_route_{key}"] = float(
                len(contribution.unique_relevant_identities)
            )
            metrics[f"calls_route_{key}"] = float(contribution.calls)
        return metrics

    def authority_flags(self) -> dict[str, Any]:
        """Small structured flags a reader must see without opening the artifact."""

        return {
            "closed_task_as_complete": any(
                item.scope == StopScope.TASK.value and item.claimed_complete
                for item in self.stop_audits
            ),
            "closed_over_censored_evidence": bool(self.censored_identities) and any(
                item.scope == StopScope.TASK.value and item.claimed_complete
                for item in self.stop_audits
            ),
            "claims_exceed_retrieval": bool(self.unsupported_claimed_identities),
        }

    def as_json(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "case_family": self.case_family,
            "system_id": self.system_id,
            "seed": self.seed,
            "status": self.status,
            "failure_class": self.failure_class,
            "gold_denominator": self.gold_denominator,
            "discovered_gold_identities": list(self.discovered_gold_identities),
            "missed_gold_identities": list(self.missed_gold_identities),
            "claimed_identities": list(self.claimed_identities),
            "unsupported_claimed_identities": list(self.unsupported_claimed_identities),
            "false_positive_identities": list(self.false_positive_identities),
            "route_contributions": [item.as_json() for item in self.route_contributions],
            "route_pair_overlap": [
                {"left": left, "right": right, "jaccard": value, "shared": shared}
                for left, right, value, shared in self.route_pair_overlap
            ],
            "marginal_relevant_gain": [
                {"route": route, "added_relevant": count}
                for route, count in self.marginal_relevant_gain
            ],
            "stop_audits": [item.as_json() for item in self.stop_audits],
            "censored_identities": list(self.censored_identities),
            "unavailable_route_events": [
                {"index": index, "route": route, "probe": probe}
                for index, route, probe in self.unavailable_route_events
            ],
            "processing_pairs": [
                {"content_identity": identity, "extraction_question": question}
                for identity, question in self.processing_pairs
            ],
            "duplicate_processing_count": self.duplicate_processing_count,
            "legitimate_reread_count": self.legitimate_reread_count,
            "first_read_count": self.first_read_count,
            "resources": dict(self.resources),
            "metrics": self.numeric_metrics(),
            "authority_flags": self.authority_flags(),
        }


def _route_contributions(
    inputs: EvaluationInputs, gold: frozenset[str]
) -> tuple[RouteContribution, ...]:
    """Attribute each relevant work to the routes that reached it.

    "Unique" means *this route and no other reached it*, which is the quantity
    P2.H2 is about. A route that only re-finds what another route already had is
    diversity in name and not in evidence.
    """

    events = inputs.trace.route_events
    by_route: dict[str, list[str]] = {}
    calls: dict[str, int] = {}
    failures: dict[str, int] = {}
    identity_routes: dict[str, set[str]] = {}
    for event in events:
        calls[event.route] = calls.get(event.route, 0) + 1
        if event.status != TransportStatus.OK.value:
            failures[event.route] = failures.get(event.route, 0) + 1
        bucket = by_route.setdefault(event.route, [])
        for identity in event.retrieved_content_identities:
            bucket.append(identity)
            identity_routes.setdefault(identity, set()).add(event.route)

    contributions: list[RouteContribution] = []
    for route in DiscoveryRoute:
        name = route.value
        retrieved = tuple(sorted(set(by_route.get(name, ()))))
        relevant = tuple(item for item in retrieved if item in gold)
        unique = tuple(
            item for item in relevant if identity_routes.get(item, set()) == {name}
        )
        spec = ROUTE_SPEC_BY_ROUTE[route]
        contributions.append(
            RouteContribution(
                route=name,
                backend_identity=spec.backend_identity,
                query_derivation_identity=spec.query_derivation_identity,
                calls=calls.get(name, 0),
                retrieved_identities=retrieved,
                unique_relevant_identities=unique,
                relevant_identities=relevant,
                transport_failures=failures.get(name, 0),
            )
        )
    return tuple(contributions)


def _pair_overlap(
    contributions: tuple[RouteContribution, ...]
) -> tuple[tuple[str, str, float, int], ...]:
    """Content-level overlap between route pairs, the input to independence claims."""

    used = [item for item in contributions if item.calls]
    pairs: list[tuple[str, str, float, int]] = []
    for left, right in combinations(sorted(used, key=lambda item: item.route), 2):
        a = set(left.retrieved_identities)
        b = set(right.retrieved_identities)
        union = a | b
        shared = len(a & b)
        pairs.append((left.route, right.route, (shared / len(union)) if union else 0.0, shared))
    return tuple(pairs)


def _marginal_gain(
    inputs: EvaluationInputs, gold: frozenset[str]
) -> tuple[tuple[str, int], ...]:
    """Relevant works each route added, in the order the system first used it."""

    seen: set[str] = set()
    order: list[str] = []
    gains: dict[str, int] = {}
    for event in inputs.trace.route_events:
        if event.route not in gains:
            order.append(event.route)
            gains[event.route] = 0
        for identity in event.retrieved_content_identities:
            if identity in gold and identity not in seen:
                seen.add(identity)
                gains[event.route] += 1
    return tuple((route, gains[route]) for route in order)


def _stop_audits(inputs: EvaluationInputs, gold: frozenset[str]) -> tuple[StopAudit, ...]:
    """Replay world state at each stop index and judge prematurity there.

    Two things make a stop *not* premature even with gold outstanding: the budget
    is gone, so nothing was reachable anyway; or the only way to the remainder is
    a route that has already died, in which case the material is censored and the
    correct response is to refuse closure rather than to keep paying.
    """

    task = inputs.task
    trace = inputs.trace
    events = trace.route_events
    audits: list[StopAudit] = []

    for decision in trace.stop_decisions:
        retrieved: set[str] = set()
        dead_routes: set[str] = set()
        calls_used = 0
        for event in events:
            if event.index >= decision.index:
                break
            calls_used += 1
            retrieved.update(event.retrieved_content_identities)
            if event.status == TransportStatus.UNAVAILABLE.value:
                dead_routes.add(event.route)

        live_reach: set[str] = set()
        for route in DiscoveryRoute:
            if route.value in dead_routes:
                continue
            if decision.scope == StopScope.ROUTE.value and route.value == decision.route:
                # Judging *this* route's stop: what could it still have found?
                live_reach.update(task.protected_gold.reachable_via(route))
                continue
            if decision.scope == StopScope.ROUTE.value:
                continue
            live_reach.update(task.protected_gold.reachable_via(route))

        outstanding = tuple(sorted((live_reach & gold) - retrieved))
        remaining_calls = max(0, task.budget.max_route_calls - calls_used)
        premature = bool(outstanding) and remaining_calls > 0
        if decision.scope == StopScope.TASK.value and not decision.claimed_complete:
            # Running out of run without claiming completeness is not a closure
            # error. Prematurity is a property of the *claim*, not of stopping.
            premature = False
        audits.append(
            StopAudit(
                index=decision.index,
                scope=decision.scope,
                route=decision.route,
                reason=decision.reason,
                claimed_complete=decision.claimed_complete,
                still_reachable_count=len(outstanding),
                still_reachable_identities=outstanding,
                remaining_route_calls=remaining_calls,
                premature=premature,
            )
        )
    return tuple(audits)


def _status_and_failure(
    inputs: EvaluationInputs,
    *,
    recall: float,
    missed: tuple[str, ...],
    unsupported: tuple[str, ...],
    false_positives: tuple[str, ...],
    audits: tuple[StopAudit, ...],
    censored: tuple[str, ...],
    retrieved_identities: frozenset[str],
) -> tuple[str, str | None]:
    """Assign one status and one failure class, in a fixed precedence.

    `CANNOT_CHECK` is reserved for the case `ANALYSIS_STANDARD_V1` names: the
    system correctly refuses authority it does not have. Refusing to certify
    completeness while a provider that held relevant material is down is exactly
    that, and grading it as a miss would penalize the safe behaviour the paper
    claims as a contribution.
    """

    trace = inputs.trace
    claimed_complete = any(
        item.scope == StopScope.TASK.value and item.claimed_complete for item in audits
    )

    if unsupported:
        return "INVALID", "unsupported_claim"
    if trace.error_class:
        return "FAIL", "candidate_error"
    if trace.budget_exhausted:
        return "FAIL", "budget_exhausted"
    if any(item.scope == StopScope.TASK.value and item.premature for item in audits):
        return "FAIL", "premature_closure"
    if censored and claimed_complete:
        return "FAIL", "premature_closure"
    if censored and not claimed_complete:
        return "CANNOT_CHECK", None
    if trace.report.abstained:
        return "CANNOT_CHECK", None

    if recall >= 1.0 and not false_positives:
        return "PASS", None
    if false_positives:
        return "FAIL", "screening_miss"
    retrieved_but_unclaimed = tuple(item for item in missed if item in retrieved_identities)
    if retrieved_but_unclaimed:
        return "FAIL", "retrieved_but_unused"
    if any(event.status != TransportStatus.OK.value for event in trace.route_events):
        return "FAIL", "transport_failure"
    used_routes = {event.route for event in trace.route_events}
    if len(used_routes) <= 1 and missed:
        return "FAIL", "route_starvation"
    return "FAIL", "present_but_missed"


def evaluate(inputs: EvaluationInputs) -> Evaluation:
    """Score one run. The candidate contributed claims; everything else is host-side."""

    task = inputs.task
    trace = inputs.trace
    gold = frozenset(task.protected_gold.gold_content_identities)

    retrieved_identities: set[str] = set()
    unavailable_events: list[tuple[int, str, str]] = []
    for event in trace.route_events:
        retrieved_identities.update(event.retrieved_content_identities)
        if event.status == TransportStatus.UNAVAILABLE.value:
            unavailable_events.append((event.index, event.route, event.probe))

    claimed = tuple(sorted(set(trace.report.claimed_relevant_content_identities)))
    # A claim about material the system never retrieved is not a discovery. It
    # would otherwise be possible to score well by naming plausible identifiers.
    unsupported = tuple(item for item in claimed if item not in retrieved_identities)
    supported = frozenset(claimed) - frozenset(unsupported)
    discovered = tuple(sorted(supported & gold))
    missed = tuple(sorted(gold - supported))
    false_positives = tuple(sorted(supported - gold))

    contributions = _route_contributions(inputs, gold)
    audits = _stop_audits(inputs, gold)
    # Censoring is a property of *this run*, not of the task. Material behind a
    # route that died is only censored if this system never got it before the
    # provider went down; whatever it already holds is discovered, not lost.
    censored = (
        tuple(
            item
            for item in task.protected_gold.censored_content_identities
            if item not in retrieved_identities
        )
        if unavailable_events
        else ()
    )

    processing_pairs = tuple(
        sorted({(event.content_identity, event.extraction_question) for event in trace.read_events})
    )
    duplicates = sum(
        1 for event in trace.read_events if event.classification == ReadClassification.DUPLICATE.value
    )
    rereads = sum(
        1
        for event in trace.read_events
        if event.classification
        in {ReadClassification.REVISION_REREAD.value, ReadClassification.NEW_QUESTION_REREAD.value}
    )
    first_reads = sum(
        1 for event in trace.read_events if event.classification == ReadClassification.FIRST_READ.value
    )

    recall = (len(discovered) / len(gold)) if gold else 0.0
    status, failure_class = _status_and_failure(
        inputs,
        recall=recall,
        missed=missed,
        unsupported=unsupported,
        false_positives=false_positives,
        audits=audits,
        censored=censored,
        retrieved_identities=frozenset(retrieved_identities),
    )

    return Evaluation(
        task_id=task.task_id,
        case_family=task.case_family.value,
        system_id=trace.system_id,
        seed=trace.seed,
        status=status,
        failure_class=failure_class,
        gold_denominator=len(gold),
        discovered_gold_identities=discovered,
        missed_gold_identities=missed,
        claimed_identities=claimed,
        unsupported_claimed_identities=unsupported,
        false_positive_identities=false_positives,
        route_contributions=contributions,
        route_pair_overlap=_pair_overlap(contributions),
        marginal_relevant_gain=_marginal_gain(inputs, gold),
        stop_audits=audits,
        censored_identities=censored,
        unavailable_route_events=tuple(unavailable_events),
        processing_pairs=processing_pairs,
        duplicate_processing_count=duplicates,
        legitimate_reread_count=rereads,
        first_read_count=first_reads,
        resources=dict(trace.resources.as_json()),
    )


__all__ = [
    "Evaluation",
    "EvaluationInputs",
    "RouteContribution",
    "StopAudit",
    "evaluate",
]
