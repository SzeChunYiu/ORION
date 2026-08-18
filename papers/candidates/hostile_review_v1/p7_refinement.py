"""P7 hostile checks: non-vacuous representation refinement and proof transport."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping

from .common import ReviewResult, Status


REVIEWED_SNAPSHOT = "999abd4899f3fed906ba024ae8ecd775a69b6560"


class StopDecision(str, Enum):
    TASK_STOP = "TASK_STOP"
    ROUTE_STOP = "ROUTE_STOP"
    CONTINUE = "CONTINUE"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class LatentFrame:
    states: frozenset[str]
    edges: frozenset[tuple[str, str, str]]
    goals: frozenset[str]
    retained_features: Mapping[str, str]

    def step(self, state: str, action: str) -> str | None:
        matches = [target for source, label, target in self.edges if source == state and label == action]
        if len(matches) > 1:
            raise ValueError("deterministic fragment requires at most one target")
        return matches[0] if matches else None


@dataclass(frozen=True)
class Chart:
    observation: Mapping[str, str]


@dataclass(frozen=True)
class LegalRefinement:
    old: Chart
    new: Chart
    feature_support: Mapping[str, str]

    def is_legal_for(self, frame: LatentFrame) -> bool:
        if set(self.old.observation) != set(frame.states):
            return False
        if set(self.new.observation) != set(frame.states):
            return False
        if dict(self.feature_support) != dict(frame.retained_features):
            return False
        states = tuple(sorted(frame.states))
        for left in states:
            for right in states:
                if self.old.observation[left] != self.old.observation[right]:
                    if self.new.observation[left] == self.new.observation[right]:
                        return False
                if self.new.observation[left] != self.new.observation[right]:
                    if (
                        self.old.observation[left],
                        self.feature_support[left],
                    ) == (
                        self.old.observation[right],
                        self.feature_support[right],
                    ):
                        return False
        return True


def policy_success_for_all(
    frame: LatentFrame,
    starts: tuple[str, ...],
    chart: Chart,
    policy: Mapping[str, str],
) -> bool:
    for start in starts:
        action = policy.get(chart.observation[start])
        if action is None:
            return False
        target = frame.step(start, action)
        if target not in frame.goals:
            return False
    return True


def check_unconstrained_chart_injection() -> ReviewResult:
    old_nodes = frozenset({"start", "dead"})
    old_goals = frozenset()
    new_nodes = frozenset({"start", "dead", "new-goal"})
    new_goals = frozenset({"new-goal"})
    witness_passes = not old_goals and bool(new_goals) and new_nodes > old_nodes
    if not witness_passes:
        return ReviewResult(
            "P7",
            "H1 unconstrained chart-injection witness",
            Status.FAIL,
            1,
            "The underconstrained expressivity witness was not reproduced.",
            REVIEWED_SNAPSHOT,
        )
    return ReviewResult(
        "P7",
        "H1 unconstrained chart-injection witness",
        Status.COUNTEREXAMPLE_CONFIRMED,
        1,
        "Allowing T' to add a new goal state proves only that a larger model is more expressive; it does not isolate representation-only reframing.",
        REVIEWED_SNAPSHOT,
        {"old_nodes": sorted(old_nodes), "new_nodes": sorted(new_nodes), "added_goal": "new-goal"},
        "Counterexample to the theorem's discriminating strength, not to the existential statement itself.",
    )


def _aliasing_fixture() -> tuple[LatentFrame, Chart, Chart, LegalRefinement, tuple[str, ...]]:
    frame = LatentFrame(
        states=frozenset({"start-left", "start-right", "goal", "dead"}),
        edges=frozenset(
            {
                ("start-left", "take-left", "goal"),
                ("start-left", "take-right", "dead"),
                ("start-right", "take-left", "dead"),
                ("start-right", "take-right", "goal"),
            }
        ),
        goals=frozenset({"goal"}),
        retained_features={
            "start-left": "left-context",
            "start-right": "right-context",
            "goal": "goal",
            "dead": "dead",
        },
    )
    old = Chart(
        {
            "start-left": "ambiguous",
            "start-right": "ambiguous",
            "goal": "goal",
            "dead": "dead",
        }
    )
    new = Chart(
        {
            "start-left": "ambiguous:left-context",
            "start-right": "ambiguous:right-context",
            "goal": "goal",
            "dead": "dead",
        }
    )
    refinement = LegalRefinement(old, new, frame.retained_features)
    return frame, old, new, refinement, ("start-left", "start-right")


def check_representation_only_strictness() -> ReviewResult:
    frame, old, new, refinement, starts = _aliasing_fixture()
    fixed_policies = (
        {"ambiguous": "take-left", "goal": "take-left", "dead": "take-left"},
        {"ambiguous": "take-right", "goal": "take-right", "dead": "take-right"},
    )
    cases = 0
    for policy in fixed_policies:
        cases += 1
        if policy_success_for_all(frame, starts, old, policy):
            return ReviewResult(
                "P7",
                "H2 representation-only strictness",
                Status.FAIL,
                cases,
                "A policy over the aliased chart solved both latent starts.",
                REVIEWED_SNAPSHOT,
            )
    if not refinement.is_legal_for(frame):
        return ReviewResult(
            "P7",
            "H2 representation-only strictness",
            Status.FAIL,
            cases + 1,
            "The retained-feature refinement was rejected.",
            REVIEWED_SNAPSHOT,
        )
    refined_policy = {
        "ambiguous:left-context": "take-left",
        "ambiguous:right-context": "take-right",
        "goal": "take-left",
        "dead": "take-left",
    }
    cases += 2
    if not policy_success_for_all(frame, starts, new, refined_policy):
        return ReviewResult(
            "P7",
            "H2 representation-only strictness",
            Status.FAIL,
            cases,
            "The refined policy failed on a latent start.",
            REVIEWED_SNAPSHOT,
        )
    return ReviewResult(
        "P7",
        "H2 representation-only strictness",
        Status.PASS,
        cases,
        "With latent states, transitions, goals and retained information fixed, no old-quotient policy solved both starts while a legal observation refinement did.",
        REVIEWED_SNAPSHOT,
        {"old_class": ["start-left", "start-right"], "retained_feature": ["left-context", "right-context"]},
        "Strictness relative to stationary observation-based policies over the old quotient; no new sensing or latent state is added.",
    )


def check_missing_proof_needs_richness_premise() -> ReviewResult:
    # A singleton admissible target class can preserve a closure even when no
    # proof object is supplied.  Therefore proof absence alone does not imply
    # a falsifying completion exists; fail-closed reopening is a policy unless
    # a richness/ambiguity premise is added.
    admissible_targets = ({"support_preserved": True},)
    proof_supplied = False
    ambiguity = len({target["support_preserved"] for target in admissible_targets}) > 1
    if proof_supplied or ambiguity:
        return ReviewResult(
            "P7",
            "H3 negative transport premise",
            Status.FAIL,
            1,
            "The singleton target-class counterexample was not constructed.",
            REVIEWED_SNAPSHOT,
        )
    return ReviewResult(
        "P7",
        "H3 negative transport premise",
        Status.COUNTEREXAMPLE_CONFIRMED,
        1,
        "Absence of a replacement proof does not logically create two target completions in every model class; the negative direction needs a richness premise or must be stated as a fail-closed rule.",
        REVIEWED_SNAPSHOT,
        {"admissible_target_count": 1, "support_preserved": True, "proof_supplied": False},
    )


def stop_decision(
    required: frozenset[str],
    discharged: frozenset[str],
    unknown_or_censored: bool,
    route_exhausted: bool,
) -> StopDecision:
    if unknown_or_censored:
        return StopDecision.CANNOT_CHECK
    if required <= discharged:
        return StopDecision.TASK_STOP
    if route_exhausted:
        return StopDecision.ROUTE_STOP
    return StopDecision.CONTINUE


def check_fail_closed_stop_terminals() -> ReviewResult:
    required = frozenset({"coverage-a", "coverage-b"})
    actual = (
        stop_decision(required, required, False, True),
        stop_decision(required, frozenset({"coverage-a"}), False, True),
        stop_decision(required, required, True, True),
        stop_decision(required, frozenset(), False, False),
    )
    expected = (
        StopDecision.TASK_STOP,
        StopDecision.ROUTE_STOP,
        StopDecision.CANNOT_CHECK,
        StopDecision.CONTINUE,
    )
    if actual != expected:
        return ReviewResult(
            "P7",
            "H4 fail-closed stop terminals",
            Status.FAIL,
            len(actual),
            "Stopping-terminal lattice mismatch.",
            REVIEWED_SNAPSHOT,
            {"actual": [item.value for item in actual]},
        )
    return ReviewResult(
        "P7",
        "H4 fail-closed stop terminals",
        Status.PASS,
        len(actual),
        "Known complete coverage permitted task stop; local incompleteness yielded route stop; unknown/censored coverage yielded CANNOT_CHECK.",
        REVIEWED_SNAPSHOT,
    )


def run_checks() -> list[ReviewResult]:
    return [
        check_unconstrained_chart_injection(),
        check_representation_only_strictness(),
        check_missing_proof_needs_richness_premise(),
        check_fail_closed_stop_terminals(),
    ]
