"""LLM-free, proof-carrying graph search for compiled ORION problems.

This module is intentionally additive.  It does not replace ``OrionSolver`` and
does not turn raw prose into facts.  A caller must first freeze a typed problem
snapshot and provide an exact transition-certificate provider.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from enum import Enum
from heapq import heappop, heappush
from itertools import count
from typing import TypeAlias

from orion.core.residuals import Residual
from orion.core.search import SearchRouteKind
from orion.core.solution import SolutionStatus
from orion.kernel.support import (
    DependencyStatusEvent,
    SupportSet,
    SupportVerdict,
    evaluate_support,
)
from orion.kernel.transition import canonical_digest
from orion.knowledge.backward_multiseed import WaypointSeed, assess_seed_diversity
from orion.knowledge.route_control import (
    RouteControlAction,
    RouteControlDecision,
)
from orion.knowledge.route_family_health import RouteHealthState


_HEX = frozenset("0123456789abcdef")


def _identifier(value: str, name: str) -> None:
    if not value.strip():
        raise ValueError(f"{name} must be nonblank")


def _sha256(value: str, name: str) -> None:
    if len(value) != 64 or any(item not in _HEX for item in value):
        raise ValueError(f"{name} must be a lowercase SHA-256 digest")


def _state_digest(facts: frozenset[str]) -> str:
    return canonical_digest(
        tuple(sorted(facts)), domain="orion-mechanical-fact-state-v1"
    )


def _support_payload(support: SupportSet) -> tuple[str, tuple[str, ...]]:
    return support.support_set_id, support.dependency_ids


class VerificationVerdict(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    CANNOT_CHECK = "CANNOT_CHECK"


class AssuranceBasis(str, Enum):
    """Where a receipt's assurance claim comes from.

    DECLARED means whoever compiled the problem asserted the mode; the
    certificate chain makes that auditable after the fact, since every checker
    binary, policy and authority root is content-bound, but nothing cross-checks
    it during the solve. DERIVED means the mode was computed from the per-checker
    attestations of the checkers that actually ran. Only DECLARED exists today;
    the enum names the repair rather than describing it in a comment.
    """

    DECLARED = "DECLARED"
    DERIVED = "DERIVED"


class AssuranceMode(str, Enum):
    EXACT = "EXACT"
    APPROXIMATE = "APPROXIMATE"


@dataclass(frozen=True)
class CheckerPolicy:
    """Frozen consumer-side checker and authority policy identity."""

    checker_id: str
    checker_lineage_id: str
    checker_binary_digest: str
    policy_digest: str
    authority_root_digest: str
    version: int
    valid_from: int
    valid_until: int
    revocation_epoch: int

    def __post_init__(self) -> None:
        _identifier(self.checker_id, "checker_id")
        _identifier(self.checker_lineage_id, "checker_lineage_id")
        for value, name in (
            (self.checker_binary_digest, "checker_binary_digest"),
            (self.policy_digest, "policy_digest"),
            (self.authority_root_digest, "authority_root_digest"),
        ):
            _sha256(value, name)
        if self.version < 1:
            raise ValueError("checker policy version must be positive")
        if self.valid_from < 0 or self.valid_until < self.valid_from:
            raise ValueError("checker policy validity window is invalid")
        if self.revocation_epoch < 0:
            raise ValueError("checker policy revocation epoch must be nonnegative")

    @property
    def digest(self) -> str:
        return canonical_digest(
            (
                self.checker_id,
                self.checker_lineage_id,
                self.checker_binary_digest,
                self.policy_digest,
                self.authority_root_digest,
                self.version,
                self.valid_from,
                self.valid_until,
                self.revocation_epoch,
            ),
            domain="orion-checker-policy-v1",
        )

    def is_valid_at(self, status_time: int) -> bool:
        return self.valid_from <= status_time <= self.valid_until


@dataclass(frozen=True)
class GoalClause:
    clause_id: str
    required_facts: frozenset[str]

    def __post_init__(self) -> None:
        _identifier(self.clause_id, "clause_id")
        if not self.required_facts:
            raise ValueError("a goal clause requires at least one fact")
        if any(not item.strip() for item in self.required_facts):
            raise ValueError("goal fact identifiers must be nonblank")


@dataclass(frozen=True)
class TransitionRule:
    rule_id: str
    route_id: str
    route_kind: SearchRouteKind
    preconditions: frozenset[str]
    add_effects: frozenset[str]
    delete_effects: frozenset[str]
    support_sets: tuple[SupportSet, ...]
    cost_units: int
    checker_policy: CheckerPolicy
    checker_registered_before_run: bool
    representation: str
    structural_signature: tuple[str, ...] = ()
    semantic_tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for value, name in (
            (self.rule_id, "rule_id"),
            (self.route_id, "route_id"),
            (self.representation, "representation"),
        ):
            _identifier(value, name)
        if self.cost_units <= 0:
            raise ValueError(
                "transition cost must be strictly positive unless a separate "
                "zero-cost rank-witness contract is implemented"
            )
        if not self.add_effects and not self.delete_effects:
            raise ValueError("a transition must declare at least one effect")
        if self.add_effects & self.delete_effects:
            raise ValueError("one fact cannot be both added and deleted")
        if any(
            not item.strip()
            for item in self.preconditions | self.add_effects | self.delete_effects
        ):
            raise ValueError("fact identifiers must be nonblank")
        support_ids = tuple(item.support_set_id for item in self.support_sets)
        if len(support_ids) != len(set(support_ids)):
            raise ValueError("support set identities must be unique within a rule")
        environments = tuple(
            frozenset(item.dependency_ids) for item in self.support_sets
        )
        if len(environments) != len(set(environments)) or any(
            environment > other
            for environment in environments
            for other in environments
        ):
            raise ValueError(
                "support environments must be unique and subset-minimal DNF terms"
            )
        if len(self.structural_signature) != len(set(self.structural_signature)):
            raise ValueError("structural signature tags must be unique")
        if len(self.semantic_tags) != len(set(self.semantic_tags)):
            raise ValueError("semantic tags must be unique")

    @property
    def digest(self) -> str:
        payload = {
            "rule_id": self.rule_id,
            "route_id": self.route_id,
            "route_kind": self.route_kind.value,
            "preconditions": tuple(sorted(self.preconditions)),
            "add_effects": tuple(sorted(self.add_effects)),
            "delete_effects": tuple(sorted(self.delete_effects)),
            "support_sets": tuple(_support_payload(item) for item in self.support_sets),
            "cost_units": self.cost_units,
            "checker_policy_digest": self.checker_policy.digest,
            "checker_registered_before_run": self.checker_registered_before_run,
            "representation": self.representation,
            "structural_signature": self.structural_signature,
            "semantic_tags": self.semantic_tags,
        }
        return canonical_digest(payload, domain="orion-mechanical-transition-rule-v1")

    def applies_to(self, facts: frozenset[str]) -> bool:
        return self.preconditions.issubset(facts)

    def apply(self, facts: frozenset[str]) -> frozenset[str]:
        return frozenset((facts - self.delete_effects) | self.add_effects)


@dataclass(frozen=True)
class TransitionCheckRequest:
    problem_snapshot_digest: str
    rule_id: str
    rule_digest: str
    source_state_digest: str
    target_state_digest: str
    checker_id: str
    checker_lineage_id: str
    checker_policy_digest: str


@dataclass(frozen=True)
class TransitionCertificate:
    problem_snapshot_digest: str
    rule_id: str
    rule_digest: str
    source_state_digest: str
    target_state_digest: str
    checker_id: str
    checker_lineage_id: str
    checker_policy_digest: str
    artifact_id: str
    artifact_digest: str
    verdict: VerificationVerdict

    def __post_init__(self) -> None:
        for value, name in (
            (self.rule_id, "rule_id"),
            (self.checker_id, "checker_id"),
            (self.checker_lineage_id, "checker_lineage_id"),
            (self.artifact_id, "artifact_id"),
        ):
            _identifier(value, name)
        for value, name in (
            (self.problem_snapshot_digest, "problem_snapshot_digest"),
            (self.rule_digest, "rule_digest"),
            (self.source_state_digest, "source_state_digest"),
            (self.target_state_digest, "target_state_digest"),
            (self.checker_policy_digest, "checker_policy_digest"),
            (self.artifact_digest, "artifact_digest"),
        ):
            _sha256(value, name)

    def mismatch(self, request: TransitionCheckRequest) -> tuple[str, ...]:
        fields = (
            "problem_snapshot_digest",
            "rule_id",
            "rule_digest",
            "source_state_digest",
            "target_state_digest",
            "checker_id",
            "checker_lineage_id",
            "checker_policy_digest",
        )
        return tuple(
            field_name
            for field_name in fields
            if getattr(self, field_name) != getattr(request, field_name)
        )


@dataclass(frozen=True)
class CompiledProblem:
    problem_id: str
    snapshot_id: str
    initial_facts: frozenset[str]
    goals: tuple[GoalClause, ...]
    rules: tuple[TransitionRule, ...]
    dependency_history: tuple[DependencyStatusEvent, ...]
    status_time: int
    admissible_checker_lineage_ids: tuple[str, ...]
    residuals: tuple[Residual, ...] = ()
    waypoint_seeds: tuple[WaypointSeed, ...] = ()
    route_health: tuple[tuple[str, RouteHealthState], ...] = ()
    route_decisions: tuple[RouteControlDecision, ...] = ()
    assurance_mode: AssuranceMode = AssuranceMode.EXACT

    def __post_init__(self) -> None:
        _identifier(self.problem_id, "problem_id")
        _identifier(self.snapshot_id, "snapshot_id")
        if not self.goals:
            raise ValueError("a compiled problem requires at least one goal clause")
        if self.status_time < 0:
            raise ValueError("status_time must be nonnegative")
        if not self.admissible_checker_lineage_ids:
            raise ValueError("at least one admissible checker lineage is required")
        if any(not item.strip() for item in self.admissible_checker_lineage_ids):
            raise ValueError("checker lineage identities must be nonblank")
        if len(self.admissible_checker_lineage_ids) != len(
            set(self.admissible_checker_lineage_ids)
        ):
            raise ValueError("admissible checker lineage identities must be unique")
        rule_ids = tuple(item.rule_id for item in self.rules)
        if len(rule_ids) != len(set(rule_ids)):
            raise ValueError("transition rule identities must be unique")
        goal_ids = tuple(item.clause_id for item in self.goals)
        if len(goal_ids) != len(set(goal_ids)):
            raise ValueError("goal clause identities must be unique")
        health_ids = tuple(item[0] for item in self.route_health)
        if len(health_ids) != len(set(health_ids)):
            raise ValueError("route health identities must be unique")
        decision_ids = tuple(item.route_id for item in self.route_decisions)
        if len(decision_ids) != len(set(decision_ids)):
            raise ValueError("route decision identities must be unique")

    @property
    def digest(self) -> str:
        payload = {
            "problem_id": self.problem_id,
            "snapshot_id": self.snapshot_id,
            "initial_facts": tuple(sorted(self.initial_facts)),
            "goals": tuple(
                (item.clause_id, tuple(sorted(item.required_facts)))
                for item in self.goals
            ),
            "rules": tuple(
                item.digest
                for item in sorted(self.rules, key=lambda rule: rule.rule_id)
            ),
            "dependency_history": tuple(
                (
                    item.event_id,
                    item.dependency_id,
                    item.status.value,
                    item.observed_at,
                    item.reason,
                )
                for item in self.dependency_history
            ),
            "status_time": self.status_time,
            "assurance_mode": self.assurance_mode.value,
            "admissible_checker_lineage_ids": tuple(
                sorted(self.admissible_checker_lineage_ids)
            ),
            "residuals": tuple(
                (
                    item.residual_id,
                    item.kind.value,
                    item.description,
                    item.material,
                    tuple(value.value for value in item.candidate_responsibilities),
                    item.metadata,
                )
                for item in self.residuals
            ),
            "waypoint_seeds": tuple(
                (
                    item.seed_id,
                    item.family.value,
                    item.structural_signature,
                    item.artifact_hash,
                )
                for item in self.waypoint_seeds
            ),
            "route_health": tuple(
                (key, value.value) for key, value in self.route_health
            ),
            "route_decisions": tuple(
                (
                    item.route_id,
                    item.route_kind.value,
                    item.policy_id,
                    item.action.value,
                    item.reasons,
                    tuple(trigger.value for trigger in item.reopen_triggers),
                )
                for item in self.route_decisions
            ),
        }
        return canonical_digest(payload, domain="orion-compiled-mechanical-problem-v1")


@dataclass(frozen=True)
class StepReceipt:
    index: int
    rule_id: str
    rule_digest: str
    route_id: str
    source_facts: tuple[str, ...]
    target_facts: tuple[str, ...]
    source_state_digest: str
    target_state_digest: str
    live_support_set_ids: tuple[str, ...]
    support_dependency_ids: tuple[str, ...]
    certificate: TransitionCertificate
    cost_units: int

    def payload(self) -> tuple[object, ...]:
        certificate = self.certificate
        return (
            self.index,
            self.rule_id,
            self.rule_digest,
            self.route_id,
            self.source_facts,
            self.target_facts,
            self.source_state_digest,
            self.target_state_digest,
            self.live_support_set_ids,
            self.support_dependency_ids,
            (
                certificate.problem_snapshot_digest,
                certificate.rule_id,
                certificate.rule_digest,
                certificate.source_state_digest,
                certificate.target_state_digest,
                certificate.checker_id,
                certificate.checker_lineage_id,
                certificate.checker_policy_digest,
                certificate.artifact_id,
                certificate.artifact_digest,
                certificate.verdict.value,
            ),
            self.cost_units,
        )


@dataclass(frozen=True)
class MechanicalSolveReceipt:
    problem_id: str
    problem_snapshot_digest: str
    assurance_mode: AssuranceMode
    status: SolutionStatus
    goal_clause_id: str | None
    final_facts: tuple[str, ...]
    steps: tuple[StepReceipt, ...]
    total_cost_units: int
    expanded_states: int
    residuals: tuple[str, ...]
    negative_history: tuple[str, ...]
    shortcut_hits: int
    shortcut_misses: int
    seed_diversity_count: int
    seed_diversity_reasons: tuple[str, ...]
    assurance_basis: AssuranceBasis = AssuranceBasis.DECLARED
    previous_receipt_hash: str | None = None
    reopened_from_step: int | None = None
    matched_prefix_rule_ids: tuple[str, ...] = ()

    @property
    def hash(self) -> str:
        payload = {
            "problem_id": self.problem_id,
            "problem_snapshot_digest": self.problem_snapshot_digest,
            "assurance_mode": self.assurance_mode.value,
            "status": self.status.value,
            "goal_clause_id": self.goal_clause_id,
            "final_facts": self.final_facts,
            "steps": tuple(item.payload() for item in self.steps),
            "total_cost_units": self.total_cost_units,
            "expanded_states": self.expanded_states,
            "residuals": self.residuals,
            "negative_history": self.negative_history,
            "shortcut_hits": self.shortcut_hits,
            "shortcut_misses": self.shortcut_misses,
            "seed_diversity_count": self.seed_diversity_count,
            "seed_diversity_reasons": self.seed_diversity_reasons,
            "assurance_basis": self.assurance_basis.value,
            "previous_receipt_hash": self.previous_receipt_hash,
            "reopened_from_step": self.reopened_from_step,
            "matched_prefix_rule_ids": self.matched_prefix_rule_ids,
        }
        return canonical_digest(payload, domain="orion-mechanical-solve-receipt-v1")


@dataclass(frozen=True)
class MechanicalSolveResult:
    status: SolutionStatus
    answer: str
    evidence_ids: tuple[str, ...]
    receipt: MechanicalSolveReceipt


@dataclass(frozen=True)
class DeterministicSolverConfig:
    max_expansions: int = 10_000
    minimum_seed_families: int = 3

    def __post_init__(self) -> None:
        if self.max_expansions < 0:
            raise ValueError("max_expansions must be nonnegative")
        if self.minimum_seed_families < 1:
            raise ValueError("minimum_seed_families must be positive")


CertificateProvider: TypeAlias = Callable[
    [TransitionCheckRequest], TransitionCertificate
]


_HEALTH_ORDER = {
    RouteHealthState.PROGRESSIVE_SIGNAL: 0,
    RouteHealthState.LOCALLY_PROGRESSIVE_ROOT_STALLED: 1,
    RouteHealthState.RESTRUCTURING_SIGNAL: 2,
    RouteHealthState.INSUFFICIENT_HISTORY: 3,
    RouteHealthState.CANNOT_CHECK: 4,
    RouteHealthState.PATCH_ACCUMULATION_SIGNAL: 5,
    RouteHealthState.STAGNANT_SIGNAL: 6,
    RouteHealthState.EXTERNALLY_BLOCKED: 7,
}


def _append_unique(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)


def _residual_tags(residuals: Iterable[Residual]) -> frozenset[str]:
    values: set[str] = set()
    for residual in residuals:
        values.add(residual.kind.value)
        values.update(item.value for item in residual.candidate_responsibilities)
        for key, value in residual.metadata:
            values.add(key)
            values.add(value)
    return frozenset(values)


class DeterministicProblemSolver:
    """Uniform-cost ORION navigation over a frozen proof-carrying graph."""

    def __init__(
        self,
        certificate_provider: CertificateProvider,
        *,
        config: DeterministicSolverConfig | None = None,
    ) -> None:
        self._certificate_provider = certificate_provider
        self._config = config or DeterministicSolverConfig()

    @staticmethod
    def _goal(
        facts: frozenset[str], goals: tuple[GoalClause, ...]
    ) -> GoalClause | None:
        return next(
            (item for item in goals if item.required_facts.issubset(facts)), None
        )

    def _rule_order(
        self,
        problem: CompiledProblem,
        rules: Iterable[TransitionRule],
    ) -> tuple[TransitionRule, ...]:
        health = dict(problem.route_health)
        residual_tags = _residual_tags(problem.residuals)
        seed_tags = frozenset(
            tag for seed in problem.waypoint_seeds for tag in seed.structural_signature
        )

        def key(rule: TransitionRule) -> tuple[object, ...]:
            shortcut = len(residual_tags.intersection(rule.semantic_tags))
            seed = len(seed_tags.intersection(rule.structural_signature))
            health_rank = _HEALTH_ORDER.get(
                health.get(rule.route_id, RouteHealthState.INSUFFICIENT_HISTORY), 3
            )
            return (health_rank, -shortcut, -seed, rule.route_id, rule.rule_id)

        return tuple(sorted(rules, key=key))

    @staticmethod
    def _reopen_metadata(
        prior: MechanicalSolveReceipt | None,
        changed_dependency_ids: tuple[str, ...],
    ) -> tuple[str | None, int | None]:
        if prior is None:
            return None, None
        changed = set(changed_dependency_ids)
        if not changed:
            return prior.hash, len(prior.steps)
        for index, step in enumerate(prior.steps):
            if changed.intersection(step.support_dependency_ids):
                return prior.hash, index
        return prior.hash, len(prior.steps)

    def solve(
        self,
        problem: CompiledProblem,
        *,
        prior_receipt: MechanicalSolveReceipt | None = None,
        changed_dependency_ids: tuple[str, ...] = (),
    ) -> MechanicalSolveResult:
        previous_hash, reopened_from = self._reopen_metadata(
            prior_receipt, changed_dependency_ids
        )
        seed_report = assess_seed_diversity(
            problem.waypoint_seeds,
            min_distinct_families=self._config.minimum_seed_families,
        )
        residuals: list[str] = []
        negative_history: list[str] = []
        shortcut_hits = 0
        shortcut_misses = 0
        expanded = 0

        initial_goal = self._goal(problem.initial_facts, problem.goals)
        if initial_goal is not None:
            _append_unique(residuals, "initial_goal_authority_unbound")
            return self._finish(
                problem,
                SolutionStatus.CANNOT_CHECK,
                "The goal is present initially but its external authority is not bound.",
                problem.initial_facts,
                (),
                None,
                expanded,
                residuals,
                negative_history,
                shortcut_hits,
                shortcut_misses,
                seed_report,
                previous_hash,
                reopened_from,
                prior_receipt,
            )

        if self._config.max_expansions == 0:
            _append_unique(residuals, "resource_bound")
            return self._finish(
                problem,
                SolutionStatus.BLOCKED,
                "The frozen expansion resource bound prevented graph search.",
                problem.initial_facts,
                (),
                None,
                expanded,
                residuals,
                negative_history,
                shortcut_hits,
                shortcut_misses,
                seed_report,
                previous_hash,
                reopened_from,
                prior_receipt,
            )

        decisions = {item.route_id: item for item in problem.route_decisions}
        residual_tag_values = _residual_tags(problem.residuals)
        ticket = count()
        queue: list[
            tuple[
                int, int, int, tuple[str, ...], frozenset[str], tuple[StepReceipt, ...]
            ]
        ] = []
        heappush(
            queue,
            (0, 0, next(ticket), (), problem.initial_facts, ()),
        )
        best_cost: dict[frozenset[str], int] = {problem.initial_facts: 0}
        last_facts = problem.initial_facts

        while queue:
            cost, depth, _, path_ids, facts, steps = heappop(queue)
            if cost != best_cost.get(facts):
                continue
            if expanded >= self._config.max_expansions:
                _append_unique(residuals, "resource_bound")
                return self._finish(
                    problem,
                    SolutionStatus.BLOCKED,
                    "The frozen expansion resource bound was reached before closure.",
                    facts,
                    steps,
                    None,
                    expanded,
                    residuals,
                    negative_history,
                    shortcut_hits,
                    shortcut_misses,
                    seed_report,
                    previous_hash,
                    reopened_from,
                    prior_receipt,
                )
            expanded += 1
            last_facts = facts
            goal = self._goal(facts, problem.goals)
            if goal is not None:
                result_status = SolutionStatus.SOLVED_VERIFIED
                answer = (
                    f"Verified transition chain satisfies goal clause {goal.clause_id}."
                )
                if problem.assurance_mode is AssuranceMode.APPROXIMATE:
                    result_status = SolutionStatus.PROVISIONAL
                    answer = (
                        f"A checked candidate chain satisfies goal clause "
                        f"{goal.clause_id}, but approximate assurance cannot "
                        "grant a verified terminal."
                    )
                    _append_unique(residuals, "approximate_assurance_no_closure")
                return self._finish(
                    problem,
                    result_status,
                    answer,
                    facts,
                    steps,
                    goal,
                    expanded,
                    residuals,
                    negative_history,
                    shortcut_hits,
                    shortcut_misses,
                    seed_report,
                    previous_hash,
                    reopened_from,
                    prior_receipt,
                )

            applicable = tuple(item for item in problem.rules if item.applies_to(facts))
            if residual_tag_values:
                if any(
                    residual_tag_values.intersection(item.semantic_tags)
                    for item in applicable
                ):
                    shortcut_hits += 1
                elif applicable:
                    shortcut_misses += 1

            for rule in self._rule_order(problem, applicable):
                decision = decisions.get(rule.route_id)
                if decision is not None and decision.action in {
                    RouteControlAction.STOP,
                    RouteControlAction.SUSPEND,
                }:
                    local_state = (
                        "stopped"
                        if decision.action is RouteControlAction.STOP
                        else "suspended"
                    )
                    _append_unique(
                        residuals,
                        f"route_locally_{local_state}:{rule.route_id}",
                    )
                    continue
                support = evaluate_support(
                    rule.support_sets,
                    problem.dependency_history,
                    status_time=problem.status_time,
                )
                if support.verdict is SupportVerdict.FAIL:
                    _append_unique(negative_history, f"support_fail:{rule.rule_id}")
                    continue
                if support.verdict is SupportVerdict.CANNOT_CHECK:
                    _append_unique(residuals, f"support_cannot_check:{rule.rule_id}")
                    continue
                if not rule.checker_registered_before_run:
                    _append_unique(
                        residuals, f"checker_chronology_invalid:{rule.rule_id}"
                    )
                    continue
                if not rule.checker_policy.is_valid_at(problem.status_time):
                    _append_unique(
                        residuals,
                        f"checker_policy_not_valid:{rule.rule_id}",
                    )
                    continue
                if (
                    rule.checker_policy.checker_lineage_id
                    not in problem.admissible_checker_lineage_ids
                ):
                    _append_unique(
                        residuals,
                        "checker_lineage_not_admissible:"
                        f"{rule.rule_id}:{rule.checker_policy.checker_lineage_id}",
                    )
                    continue

                target = rule.apply(facts)
                if target == facts:
                    _append_unique(negative_history, f"no_state_change:{rule.rule_id}")
                    continue
                request = TransitionCheckRequest(
                    problem_snapshot_digest=problem.digest,
                    rule_id=rule.rule_id,
                    rule_digest=rule.digest,
                    source_state_digest=_state_digest(facts),
                    target_state_digest=_state_digest(target),
                    checker_id=rule.checker_policy.checker_id,
                    checker_lineage_id=rule.checker_policy.checker_lineage_id,
                    checker_policy_digest=rule.checker_policy.digest,
                )
                try:
                    certificate = self._certificate_provider(request)
                except Exception as error:  # noqa: BLE001 - failure becomes typed residual
                    _append_unique(
                        residuals,
                        f"certificate_provider_error:{rule.rule_id}:{type(error).__name__}",
                    )
                    continue
                mismatches = certificate.mismatch(request)
                if mismatches:
                    _append_unique(
                        residuals,
                        f"certificate_mismatch:{rule.rule_id}:{','.join(mismatches)}",
                    )
                    continue
                if certificate.verdict is VerificationVerdict.FAIL:
                    _append_unique(negative_history, f"certificate_fail:{rule.rule_id}")
                    continue
                if certificate.verdict is VerificationVerdict.CANNOT_CHECK:
                    _append_unique(
                        residuals, f"certificate_cannot_check:{rule.rule_id}"
                    )
                    continue

                support_dependencies = tuple(
                    dict.fromkeys(
                        dependency_id
                        for support_set in rule.support_sets
                        if support_set.support_set_id in support.live_support_set_ids
                        for dependency_id in support_set.dependency_ids
                    )
                )
                new_cost = cost + rule.cost_units
                if new_cost >= best_cost.get(target, 2**63 - 1):
                    continue
                best_cost[target] = new_cost
                step = StepReceipt(
                    index=len(steps),
                    rule_id=rule.rule_id,
                    rule_digest=rule.digest,
                    route_id=rule.route_id,
                    source_facts=tuple(sorted(facts)),
                    target_facts=tuple(sorted(target)),
                    source_state_digest=request.source_state_digest,
                    target_state_digest=request.target_state_digest,
                    live_support_set_ids=support.live_support_set_ids,
                    support_dependency_ids=support_dependencies,
                    certificate=certificate,
                    cost_units=rule.cost_units,
                )
                heappush(
                    queue,
                    (
                        new_cost,
                        depth + 1,
                        next(ticket),
                        (*path_ids, rule.rule_id),
                        target,
                        (*steps, step),
                    ),
                )

        _append_unique(residuals, "verified_graph_exhausted_without_goal_proof")
        return self._finish(
            problem,
            SolutionStatus.CANNOT_CHECK,
            "The frozen verified graph was exhausted without a goal proof; this is not an impossibility result.",
            last_facts,
            (),
            None,
            expanded,
            residuals,
            negative_history,
            shortcut_hits,
            shortcut_misses,
            seed_report,
            previous_hash,
            reopened_from,
            prior_receipt,
        )

    @staticmethod
    def _finish(
        problem: CompiledProblem,
        status: SolutionStatus,
        answer: str,
        facts: frozenset[str],
        steps: tuple[StepReceipt, ...],
        goal: GoalClause | None,
        expanded: int,
        residuals: list[str],
        negative_history: list[str],
        shortcut_hits: int,
        shortcut_misses: int,
        seed_report,
        previous_hash: str | None,
        reopened_from: int | None,
        prior_receipt: MechanicalSolveReceipt | None,
    ) -> MechanicalSolveResult:
        matched_prefix: tuple[str, ...] = ()
        if prior_receipt is not None and reopened_from is not None:
            limit = min(reopened_from, len(steps), len(prior_receipt.steps))
            values: list[str] = []
            for index in range(limit):
                if prior_receipt.steps[index].rule_id != steps[index].rule_id:
                    break
                values.append(steps[index].rule_id)
            matched_prefix = tuple(values)
        receipt = MechanicalSolveReceipt(
            problem_id=problem.problem_id,
            problem_snapshot_digest=problem.digest,
            assurance_mode=problem.assurance_mode,
            status=status,
            goal_clause_id=goal.clause_id if goal else None,
            final_facts=tuple(sorted(facts)),
            steps=steps,
            total_cost_units=sum(item.cost_units for item in steps),
            expanded_states=expanded,
            residuals=tuple(residuals),
            negative_history=tuple(negative_history),
            shortcut_hits=shortcut_hits,
            shortcut_misses=shortcut_misses,
            seed_diversity_count=seed_report.distinct_family_count,
            seed_diversity_reasons=seed_report.reasons,
            previous_receipt_hash=previous_hash,
            reopened_from_step=reopened_from,
            matched_prefix_rule_ids=matched_prefix,
        )
        evidence_ids = tuple(
            dict.fromkeys(item.certificate.artifact_id for item in steps)
        )
        return MechanicalSolveResult(status, answer, evidence_ids, receipt)


__all__ = [
    "AssuranceMode",
    "CertificateProvider",
    "CheckerPolicy",
    "CompiledProblem",
    "DeterministicProblemSolver",
    "DeterministicSolverConfig",
    "GoalClause",
    "MechanicalSolveReceipt",
    "MechanicalSolveResult",
    "StepReceipt",
    "TransitionCertificate",
    "TransitionCheckRequest",
    "TransitionRule",
    "VerificationVerdict",
]
