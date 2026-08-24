"""Host-owned scoring and oracles for the ORION-P2 offline discovery study.

Custody rule: the candidate never touches anything in here. It does not compute
its own recall, does not classify its own reads, does not decide whether its own
closure was premature, and cannot mutate what this module returns — every
structure handed back is a tuple or a fresh dict.

The verdicts are *replayed* rather than reported. "Did the system stop that route
too early?" is not answerable from the stop decision alone; it needs the state of
the world at the attempt index the decision was taken. The ordered trial timeline
exists so that question has an answer, and `oracle.route_residual_yield` is that
answer written down.

Oracle definitions and constants come from `STATISTICAL_PLAN_V1.json`:

- **O1 route_stop_correctness** — a stop is a false positive when at least
  `MARGINAL_YIELD_THRESHOLD` previously-unfound gold works were still reachable on
  that route and it still held `MIN_REMAINING_BUDGET_UNITS`; a route is a false
  negative when it made more than `EXHAUSTION_GRACE_ATTEMPTS` further attempts
  past the point where nothing remained. The oracle is gold-defined, so changing
  the route-control policy cannot move the truth.
- **O2 premature_task_closure** — declared closure with gold still discoverable
  within remaining budget. Truncated runs never enter the denominator, because
  truncation is not stopping.
- **O3 reread_legitimacy** — rates over *encounters*, not executions. An
  execution-only denominator hides suppression.
- **O4 unavailable_route_obligation** — an open obligation is never exhaustion and
  never evidence of absence; a metric it could bear on is CANNOT_CHECK.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Any

from orion.knowledge.identity import ReadDecision

from .cases import Budget, DiscoveryTask
from .corpus import ROUTE_SPEC_BY_ROUTE, DiscoveryRoute, DiscoveryWorld
from .systems import OBLIGATION_STATUSES, StopScope, SystemTrace, TransportStatus

# O1 constants, verbatim from the plan.
MARGINAL_YIELD_THRESHOLD = 1
MIN_REMAINING_BUDGET_UNITS = 1.0
EXHAUSTION_GRACE_ATTEMPTS = 1

#: O3: reread states that are legitimate rather than duplicated effort.
LEGITIMATE_REREAD_STATES: frozenset[str] = frozenset(
    {
        ReadDecision.CONTENT_CHANGED.value,
        ReadDecision.NEW_SCHEMA.value,
        ReadDecision.NEW_FRAME.value,
    }
)


def evaluator_hash() -> str:
    """B13: the identity of the evaluator that produced a verdict.

    A result is only checkable against the code that scored it, and this module
    is that code. Hashing its own source means a silent change to a threshold
    shows up as a different evaluator rather than as a different result.
    """

    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


@dataclass(frozen=True)
class EvaluationInputs:
    """Everything the evaluator needs. Assembled host-side, never by a candidate."""

    world: DiscoveryWorld
    task: DiscoveryTask
    trace: SystemTrace
    caps: Budget


@dataclass(frozen=True)
class RouteContribution:
    """What one route actually added, separated from what it merely echoed."""

    route_id: str
    backend_identity: str
    query_derivation_identity: str
    attempts: int
    retrieved_merged_source_ids: tuple[str, ...]
    relevant_merged_source_ids: tuple[str, ...]
    unique_relevant_merged_source_ids: tuple[str, ...]
    transport_failures: int

    def as_json(self) -> dict[str, Any]:
        return {
            "route_id": self.route_id,
            "backend_identity": self.backend_identity,
            "query_derivation_identity": self.query_derivation_identity,
            "attempts": self.attempts,
            "retrieved_merged_source_ids": list(self.retrieved_merged_source_ids),
            "relevant_merged_source_ids": list(self.relevant_merged_source_ids),
            "unique_relevant_merged_source_ids": list(self.unique_relevant_merged_source_ids),
            "transport_failures": self.transport_failures,
        }


@dataclass(frozen=True)
class RouteStopAudit:
    """One route stop, replayed against the residual yield at its attempt index."""

    route_id: str
    attempt_index: int
    index: int
    reason: str
    residual_yield_at_stop: int
    remaining_query_budget: int
    open_obligation_ids: tuple[str, ...]
    false_positive: bool
    cannot_check: bool

    def as_json(self) -> dict[str, Any]:
        return {
            "route_id": self.route_id,
            "attempt_index": self.attempt_index,
            "index": self.index,
            "reason": self.reason,
            "residual_yield_at_stop": self.residual_yield_at_stop,
            "remaining_query_budget": self.remaining_query_budget,
            "open_obligation_ids": list(self.open_obligation_ids),
            "false_positive": self.false_positive,
            "cannot_check": self.cannot_check,
        }


@dataclass(frozen=True)
class RouteExhaustionAudit:
    """O1 false negatives: attempts made past the oracle exhaustion point."""

    route_id: str
    exhaustion_attempt_index: int
    attempts_after_exhaustion: int
    false_negative: bool

    def as_json(self) -> dict[str, Any]:
        return {
            "route_id": self.route_id,
            "exhaustion_attempt_index": self.exhaustion_attempt_index,
            "attempts_after_exhaustion": self.attempts_after_exhaustion,
            "false_negative": self.false_negative,
        }


@dataclass(frozen=True)
class Evaluation:
    """The complete host verdict on one run. Every field is immutable."""

    task_id: str
    case_family: str
    system_id: str
    seed: int
    repeat_index: int
    status: str
    failure_class: str | None

    gold_items: tuple[str, ...]
    gold_set_complete: bool
    discovered_gold_ids: tuple[str, ...]
    missed_gold_ids: tuple[str, ...]
    claimed_ids: tuple[str, ...]
    unsupported_claimed_ids: tuple[str, ...]
    false_positive_ids: tuple[str, ...]

    route_contributions: tuple[RouteContribution, ...]
    route_pair_overlap: tuple[tuple[str, str, float, int], ...]
    marginal_relevant_gain: tuple[tuple[str, int], ...]
    route_residual_yield: tuple[tuple[str, tuple[tuple[int, int], ...]], ...]

    route_stop_audits: tuple[RouteStopAudit, ...]
    route_exhaustion_audits: tuple[RouteExhaustionAudit, ...]

    closure_declared: bool
    truncated_at_cap: str
    task_residual_discoverable_within_budget: int
    premature_closure: bool
    closure_cannot_check: bool

    censored_ids: tuple[str, ...]
    unavailable_trial_count: int
    unresolved_obligation_ids: tuple[str, ...]

    encounter_pairs: tuple[tuple[str, str], ...]
    legitimate_encounters: int
    legitimate_executed: int
    already_read_encounters: int
    already_read_executed: int
    unseen_encounters: int

    resources: tuple[tuple[str, float], ...]

    def oracle_block(self) -> dict[str, Any]:
        """The plan's `oracle.*` namespace: B5, B6, B8, B10 under their own names."""

        return {
            "gold_items": list(self.gold_items),
            "gold_set_complete": self.gold_set_complete,
            "route_residual_yield": {
                route_id: {str(attempt): value for attempt, value in entries}
                for route_id, entries in self.route_residual_yield
            },
            "task_residual_discoverable_within_budget": {
                self.task_id: {self.system_id: self.task_residual_discoverable_within_budget}
            },
            "evaluator_hash": evaluator_hash(),
            "constants": {
                "marginal_yield_threshold": MARGINAL_YIELD_THRESHOLD,
                "min_remaining_budget_units": MIN_REMAINING_BUDGET_UNITS,
                "exhaustion_grace_attempts": EXHAUSTION_GRACE_ATTEMPTS,
            },
        }

    def numeric_metrics(self) -> dict[str, float]:
        """The record's `metrics` object: numbers only, per the result-record schema.

        Booleans are 1.0/0.0 because JSON Schema does not accept a boolean where a
        number is required, and a record that fails its own schema is not evidence.
        """

        denominator = float(len(self.gold_items))
        claimed = len(self.claimed_ids)
        stop_events = len(self.route_stop_audits)
        exhausted_routes = [item for item in self.route_exhaustion_audits if item.exhaustion_attempt_index >= 0]
        metrics: dict[str, float] = {
            "complete_gold_recall": (
                len(self.discovered_gold_ids) / denominator if denominator else 0.0
            ),
            # Numerator is what was actually discovered, so a fabricated claim
            # lands in the denominator only.
            "precision": (len(self.discovered_gold_ids) / claimed) if claimed else 0.0,
            "claimed_count": float(claimed),
            "supported_claim_count": float(claimed - len(self.unsupported_claimed_ids)),
            "gold_denominator": denominator,
            "gold_set_complete": float(self.gold_set_complete),
            "discovered_gold_count": float(len(self.discovered_gold_ids)),
            "false_negative_count": float(len(self.missed_gold_ids)),
            "false_positive_count": float(len(self.false_positive_ids)),
            "unsupported_claim_count": float(len(self.unsupported_claimed_ids)),
            "premature_task_closure": float(self.premature_closure),
            "task_closure_declared": float(self.closure_declared),
            "task_residual_discoverable_within_budget": float(
                self.task_residual_discoverable_within_budget
            ),
            "truncated_at_cap": float(bool(self.truncated_at_cap)),
            "route_stop_events": float(stop_events),
            "route_stop_false_positive_count": float(
                sum(1 for item in self.route_stop_audits if item.false_positive)
            ),
            "route_stop_false_positive_rate": (
                sum(1 for item in self.route_stop_audits if item.false_positive) / stop_events
                if stop_events
                else 0.0
            ),
            "routes_reaching_exhaustion": float(len(exhausted_routes)),
            "route_stop_false_negative_count": float(
                sum(1 for item in exhausted_routes if item.false_negative)
            ),
            "route_stop_false_negative_rate": (
                sum(1 for item in exhausted_routes if item.false_negative) / len(exhausted_routes)
                if exhausted_routes
                else 0.0
            ),
            "censored_identity_count": float(len(self.censored_ids)),
            "unavailable_route_event_count": float(self.unavailable_trial_count),
            "unresolved_obligation_count": float(len(self.unresolved_obligation_ids)),
            # O3: encounter denominators, not execution denominators.
            "legitimate_reread_encounters": float(self.legitimate_encounters),
            "legitimate_reread_executed": float(self.legitimate_executed),
            "legitimate_reread_rate": (
                self.legitimate_executed / self.legitimate_encounters
                if self.legitimate_encounters
                else 0.0
            ),
            "already_read_encounters": float(self.already_read_encounters),
            "duplicate_processing_executed": float(self.already_read_executed),
            "duplicate_processing_rate": (
                self.already_read_executed / self.already_read_encounters
                if self.already_read_encounters
                else 0.0
            ),
            "unseen_encounters": float(self.unseen_encounters),
            "routes_used": float(sum(1 for item in self.route_contributions if item.attempts)),
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
            key = contribution.route_id.lower()
            metrics[f"unique_relevant_per_route_{key}"] = float(
                len(contribution.unique_relevant_merged_source_ids)
            )
            metrics[f"attempts_route_{key}"] = float(contribution.attempts)
        return metrics

    def authority_flags(self) -> dict[str, Any]:
        return {
            "closed_task_as_complete": self.closure_declared,
            "closed_over_open_obligation": bool(self.unresolved_obligation_ids)
            and self.closure_declared,
            "closed_over_censored_evidence": bool(self.censored_ids) and self.closure_declared,
            "claims_exceed_retrieval": bool(self.unsupported_claimed_ids),
            "complete_denominator_valid": self.gold_set_complete,
        }

    def as_json(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "case_family": self.case_family,
            "system_id": self.system_id,
            "seed": self.seed,
            "repeat_index": self.repeat_index,
            "status": self.status,
            "failure_class": self.failure_class,
            "gold_items": list(self.gold_items),
            "gold_set_complete": self.gold_set_complete,
            "discovered_gold_ids": list(self.discovered_gold_ids),
            "missed_gold_ids": list(self.missed_gold_ids),
            "claimed_ids": list(self.claimed_ids),
            "unsupported_claimed_ids": list(self.unsupported_claimed_ids),
            "false_positive_ids": list(self.false_positive_ids),
            "route_contributions": [item.as_json() for item in self.route_contributions],
            "route_pair_overlap": [
                {"left": left, "right": right, "jaccard": value, "shared": shared}
                for left, right, value, shared in self.route_pair_overlap
            ],
            "marginal_relevant_gain": [
                {"route_id": route, "added_relevant": count}
                for route, count in self.marginal_relevant_gain
            ],
            "route_stop_audits": [item.as_json() for item in self.route_stop_audits],
            "route_exhaustion_audits": [item.as_json() for item in self.route_exhaustion_audits],
            "closure_declared": self.closure_declared,
            "truncated_at_cap": self.truncated_at_cap,
            "premature_closure": self.premature_closure,
            "closure_cannot_check": self.closure_cannot_check,
            "censored_ids": list(self.censored_ids),
            "unavailable_trial_count": self.unavailable_trial_count,
            "unresolved_obligation_ids": list(self.unresolved_obligation_ids),
            "encounter_pairs": [
                {"merged_source_id": identity, "frame_id": frame}
                for identity, frame in self.encounter_pairs
            ],
            "resources": {name: value for name, value in self.resources},
            "metrics": self.numeric_metrics(),
            "authority_flags": self.authority_flags(),
            "oracle": self.oracle_block(),
        }


def _route_contributions(
    inputs: EvaluationInputs, gold: frozenset[str]
) -> tuple[RouteContribution, ...]:
    """Attribute each relevant work to the routes that reached it.

    "Unique" means *this route and no other reached it*, which is the quantity
    P2.H2 is about. A route that only re-finds what another route already had is
    diversity in name and not in evidence.
    """

    by_route: dict[str, set[str]] = {}
    attempts: dict[str, int] = {}
    failures: dict[str, int] = {}
    routes_of: dict[str, set[str]] = {}
    for trial in inputs.trace.route_trials:
        attempts[trial.route_id] = attempts.get(trial.route_id, 0) + 1
        if trial.transport_status != TransportStatus.OK.value:
            failures[trial.route_id] = failures.get(trial.route_id, 0) + 1
        bucket = by_route.setdefault(trial.route_id, set())
        for capture in trial.captures:
            bucket.add(capture.merged_source_id)
            routes_of.setdefault(capture.merged_source_id, set()).add(trial.route_id)

    contributions: list[RouteContribution] = []
    for route in DiscoveryRoute:
        name = route.value
        retrieved = tuple(sorted(by_route.get(name, set())))
        relevant = tuple(item for item in retrieved if item in gold)
        unique = tuple(item for item in relevant if routes_of.get(item, set()) == {name})
        spec = ROUTE_SPEC_BY_ROUTE[route]
        contributions.append(
            RouteContribution(
                route_id=name,
                backend_identity=spec.backend_identity,
                query_derivation_identity=spec.query_derivation_identity,
                attempts=attempts.get(name, 0),
                retrieved_merged_source_ids=retrieved,
                relevant_merged_source_ids=relevant,
                unique_relevant_merged_source_ids=unique,
                transport_failures=failures.get(name, 0),
            )
        )
    return tuple(contributions)


def _pair_overlap(
    contributions: tuple[RouteContribution, ...]
) -> tuple[tuple[str, str, float, int], ...]:
    """Content-level overlap between route pairs, the input to independence claims."""

    used = [item for item in contributions if item.attempts]
    pairs: list[tuple[str, str, float, int]] = []
    for left, right in combinations(sorted(used, key=lambda item: item.route_id), 2):
        a = set(left.retrieved_merged_source_ids)
        b = set(right.retrieved_merged_source_ids)
        union = a | b
        shared = len(a & b)
        pairs.append((left.route_id, right.route_id, (shared / len(union)) if union else 0.0, shared))
    return tuple(pairs)


def _marginal_gain(
    inputs: EvaluationInputs, gold: frozenset[str]
) -> tuple[tuple[str, int], ...]:
    """Relevant works each route added, in the order the system first used it."""

    seen: set[str] = set()
    order: list[str] = []
    gains: dict[str, int] = {}
    for trial in inputs.trace.route_trials:
        if trial.route_id not in gains:
            order.append(trial.route_id)
            gains[trial.route_id] = 0
        for capture in trial.captures:
            if capture.merged_source_id in gold and capture.merged_source_id not in seen:
                seen.add(capture.merged_source_id)
                gains[trial.route_id] += 1
    return tuple((route, gains[route]) for route in order)


def _residual_yield(
    inputs: EvaluationInputs, gold: frozenset[str]
) -> tuple[tuple[str, tuple[tuple[int, int], ...]], ...]:
    """B8. Gold still reachable on each route at each of its attempt indices.

    Computed from the frozen corpus rather than from what the system happened to
    see, which is what makes it an oracle: a system cannot lower its own residual
    by declining to look.
    """

    task = inputs.task
    found: set[str] = set()
    dead: set[str] = set()
    per_route: dict[str, list[tuple[int, int]]] = {}

    for trial in inputs.trace.route_trials:
        reachable = set(task.protected_gold.reachable_via(DiscoveryRoute(trial.route_id))) & gold
        # Residual *before* this attempt: what the route could still have yielded
        # when the system chose to make (or not make) it.
        residual = 0 if trial.route_id in dead else len(reachable - found)
        per_route.setdefault(trial.route_id, []).append((trial.attempt_index, residual))
        for capture in trial.captures:
            found.add(capture.merged_source_id)
        if trial.transport_status == TransportStatus.UNAVAILABLE.value:
            dead.add(trial.route_id)

    return tuple(
        (route_id, tuple(sorted(entries))) for route_id, entries in sorted(per_route.items())
    )


def _route_audits(
    inputs: EvaluationInputs,
    gold: frozenset[str],
    residual: tuple[tuple[str, tuple[tuple[int, int], ...]], ...],
) -> tuple[tuple[RouteStopAudit, ...], tuple[RouteExhaustionAudit, ...]]:
    """O1. Route-stop false positives and false negatives, gold-defined."""

    residual_map = {route_id: dict(entries) for route_id, entries in residual}
    trials_by_index = {item.index: item for item in inputs.trace.route_trials}
    cap = inputs.caps.query_count

    stops: list[RouteStopAudit] = []
    for decision in inputs.trace.stop_decisions:
        if decision.scope != StopScope.ROUTE.value:
            continue
        used = sum(1 for item in inputs.trace.route_trials if item.index < decision.index)
        remaining = max(0, cap - used)
        yield_at_stop = residual_map.get(decision.route_id, {}).get(decision.attempt_index, 0)
        # Obligations live on this route at the moment it was abandoned, taken
        # from the last trial on it before the stop.
        prior = [
            trials_by_index[index]
            for index in sorted(trials_by_index)
            if index < decision.index and trials_by_index[index].route_id == decision.route_id
        ]
        open_ids = prior[-1].open_obligation_ids if prior else ()
        # O4: an open obligation is never exhaustion, so a stop taken under one
        # cannot be scored as either correct or premature.
        cannot_check = bool(open_ids)
        stops.append(
            RouteStopAudit(
                route_id=decision.route_id,
                attempt_index=decision.attempt_index,
                index=decision.index,
                reason=decision.reason,
                residual_yield_at_stop=yield_at_stop,
                remaining_query_budget=remaining,
                open_obligation_ids=open_ids,
                false_positive=(
                    not cannot_check
                    and yield_at_stop >= MARGINAL_YIELD_THRESHOLD
                    and remaining >= MIN_REMAINING_BUDGET_UNITS
                ),
                cannot_check=cannot_check,
            )
        )

    exhaustion: list[RouteExhaustionAudit] = []
    for route_id, entries in residual:
        point = next((attempt for attempt, value in sorted(entries) if value == 0), -1)
        after = (
            sum(1 for attempt, _ in entries if attempt > point) if point >= 0 else 0
        )
        exhaustion.append(
            RouteExhaustionAudit(
                route_id=route_id,
                exhaustion_attempt_index=point,
                attempts_after_exhaustion=after,
                false_negative=point >= 0 and after > EXHAUSTION_GRACE_ATTEMPTS,
            )
        )
    return tuple(stops), tuple(exhaustion)


def _task_residual(inputs: EvaluationInputs, gold: frozenset[str]) -> int:
    """B10. Gold still discoverable by an admissible route within remaining budget."""

    task = inputs.task
    trace = inputs.trace
    found: set[str] = set()
    dead: set[str] = set()
    for trial in trace.route_trials:
        found.update(item.merged_source_id for item in trial.captures)
        if trial.transport_status == TransportStatus.UNAVAILABLE.value:
            dead.add(trial.route_id)

    remaining = max(0, inputs.caps.query_count - len(trace.route_trials))
    if remaining <= 0:
        # Nothing is discoverable with no budget left, so closing then is not
        # premature — it is truncation, and truncation is accounted separately.
        return 0
    live: set[str] = set()
    for route in DiscoveryRoute:
        if route.value in dead:
            continue
        live.update(task.protected_gold.reachable_via(route))
    return len(((live & gold) - found))


def _status_and_failure(
    inputs: EvaluationInputs,
    *,
    recall: float,
    missed: tuple[str, ...],
    unsupported: tuple[str, ...],
    false_positives: tuple[str, ...],
    premature: bool,
    closure_cannot_check: bool,
    gold_set_complete: bool,
    retrieved: frozenset[str],
) -> tuple[str, str | None]:
    """Assign one status and one failure class, in a fixed precedence."""

    trace = inputs.trace
    caps = inputs.caps

    # Overrun audit first. Python has no hard private attribute, so in-process
    # enforcement can be reached around; what cannot is the host comparing the
    # recorded run against the frozen caps afterwards.
    if (
        len(trace.route_trials) > caps.query_count
        or trace.resources.query_count > caps.query_count
        or trace.resources.tool_calls > caps.tool_calls
        or trace.resources.model_tokens > caps.model_tokens
    ):
        return "INVALID", "harness_tamper"
    if unsupported:
        return "INVALID", "unsupported_claim"
    if not gold_set_complete:
        # B6 is the validity switch for every complete-denominator metric.
        return "CANNOT_CHECK", "incomplete_gold_denominator"
    if trace.error_class:
        return "FAIL", "candidate_error"
    if trace.truncated_at_cap:
        return "FAIL", "TRUNCATED_AT_CAP"
    if premature:
        return "FAIL", "premature_closure"
    if closure_cannot_check:
        # O4: an unresolved obligation could bear on coverage, so the coverage
        # verdict is refused rather than guessed.
        return "CANNOT_CHECK", None
    if trace.report.abstained:
        return "CANNOT_CHECK", None

    if recall >= 1.0 and not false_positives:
        return "PASS", None
    if false_positives:
        return "FAIL", "screening_miss"
    if any(item in retrieved for item in missed):
        return "FAIL", "retrieved_but_unused"
    if any(
        item.transport_status in OBLIGATION_STATUSES and item.probe_admissible
        for item in trace.route_trials
    ):
        return "FAIL", "transport_failure"
    if len({item.route_id for item in trace.route_trials}) <= 1 and missed:
        return "FAIL", "route_starvation"
    return "FAIL", "present_but_missed"


def evaluate(inputs: EvaluationInputs) -> Evaluation:
    """Score one run. The candidate contributed claims; everything else is host-side."""

    task = inputs.task
    trace = inputs.trace
    gold = frozenset(task.protected_gold.gold_content_identities)

    retrieved: set[str] = set()
    unavailable_trials = 0
    for trial in trace.route_trials:
        retrieved.update(item.merged_source_id for item in trial.captures)
        if trial.transport_status in OBLIGATION_STATUSES and trial.probe_admissible:
            unavailable_trials += 1

    claimed = tuple(sorted(set(trace.report.claimed_relevant_merged_source_ids)))
    unsupported = tuple(item for item in claimed if item not in retrieved)
    supported = frozenset(claimed) - frozenset(unsupported)
    discovered = tuple(sorted(supported & gold))
    missed = tuple(sorted(gold - supported))
    false_positives = tuple(sorted(supported - gold))

    contributions = _route_contributions(inputs, gold)
    residual = _residual_yield(inputs, gold)
    stop_audits, exhaustion_audits = _route_audits(inputs, gold, residual)
    task_residual = _task_residual(inputs, gold)

    closure_declared = any(
        item.scope == StopScope.TASK.value and item.declared for item in trace.stop_decisions
    )
    censored = (
        tuple(
            item
            for item in task.protected_gold.censored_content_identities
            if item not in retrieved
        )
        if unavailable_trials
        else ()
    )
    # O2 CANNOT_CHECK: an unresolved obligation could bear on discoverability, so
    # a closure taken under one is neither premature nor safe — it is unscorable.
    closure_cannot_check = bool(trace.unresolved_obligation_ids) or bool(censored)
    premature = closure_declared and not closure_cannot_check and task_residual >= 1

    pairs = tuple(
        sorted({(item.merged_source_id, item.frame_id) for item in trace.read_encounters})
    )
    legitimate = [
        item
        for item in trace.read_encounters
        if item.decision_before_execution in LEGITIMATE_REREAD_STATES
    ]
    already = [
        item
        for item in trace.read_encounters
        if item.decision_before_execution == ReadDecision.ALREADY_READ.value
    ]
    unseen = sum(
        1
        for item in trace.read_encounters
        if item.decision_before_execution == ReadDecision.UNSEEN.value
    )

    recall = (len(discovered) / len(gold)) if gold else 0.0
    status, failure_class = _status_and_failure(
        inputs,
        recall=recall,
        missed=missed,
        unsupported=unsupported,
        false_positives=false_positives,
        premature=premature,
        closure_cannot_check=closure_cannot_check and closure_declared,
        gold_set_complete=task.protected_gold.gold_set_complete,
        retrieved=frozenset(retrieved),
    )

    return Evaluation(
        task_id=task.task_id,
        case_family=task.case_family.value,
        system_id=trace.system_id,
        seed=trace.seed,
        repeat_index=trace.repeat_index,
        status=status,
        failure_class=failure_class,
        gold_items=task.protected_gold.gold_content_identities,
        gold_set_complete=task.protected_gold.gold_set_complete,
        discovered_gold_ids=discovered,
        missed_gold_ids=missed,
        claimed_ids=claimed,
        unsupported_claimed_ids=unsupported,
        false_positive_ids=false_positives,
        route_contributions=contributions,
        route_pair_overlap=_pair_overlap(contributions),
        marginal_relevant_gain=_marginal_gain(inputs, gold),
        route_residual_yield=residual,
        route_stop_audits=stop_audits,
        route_exhaustion_audits=exhaustion_audits,
        closure_declared=closure_declared,
        truncated_at_cap=trace.truncated_at_cap,
        task_residual_discoverable_within_budget=task_residual,
        premature_closure=premature,
        closure_cannot_check=closure_cannot_check,
        censored_ids=censored,
        unavailable_trial_count=unavailable_trials,
        unresolved_obligation_ids=trace.unresolved_obligation_ids,
        encounter_pairs=pairs,
        legitimate_encounters=len(legitimate),
        legitimate_executed=sum(1 for item in legitimate if item.executed),
        already_read_encounters=len(already),
        already_read_executed=sum(1 for item in already if item.executed),
        unseen_encounters=unseen,
        resources=tuple(sorted(trace.resources.as_json().items())),
    )


__all__ = [
    "EXHAUSTION_GRACE_ATTEMPTS",
    "Evaluation",
    "EvaluationInputs",
    "LEGITIMATE_REREAD_STATES",
    "MARGINAL_YIELD_THRESHOLD",
    "MIN_REMAINING_BUDGET_UNITS",
    "RouteContribution",
    "RouteExhaustionAudit",
    "RouteStopAudit",
    "evaluate",
    "evaluator_hash",
]
