"""Executable white-box Stage 0 benchmark for Self-ORION V3 (#455).

This is an instrumentation/pilot layer, not a result-bearing protected campaign.  It
makes the pre-freeze case contract executable: candidate-visible state is separated
from protected gold; diagnostic observations can be permuted; policies are scored on
revision-class correctness, false broad revision, preservation, and cost.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Mapping


class RevisionClass(str, Enum):
    NO_SELF_REVISION = "NO_SELF_REVISION"
    CONTAIN = "CONTAIN"
    EVIDENCE = "EVIDENCE"
    MEASUREMENT = "MEASUREMENT"
    PARAMETER = "PARAMETER"
    MODEL_SELECTION = "MODEL_SELECTION"
    M_OPEN = "M_OPEN"
    REPRESENTATION = "REPRESENTATION"
    OBJECTIVE = "OBJECTIVE"
    METHOD_BASIS = "METHOD_BASIS"
    EXECUTION = "EXECUTION"
    EVALUATOR = "EVALUATOR"
    UNRESOLVED = "UNRESOLVED"


BROAD_CLASSES = frozenset(
    {
        RevisionClass.M_OPEN,
        RevisionClass.REPRESENTATION,
        RevisionClass.OBJECTIVE,
        RevisionClass.METHOD_BASIS,
    }
)


@dataclass(frozen=True)
class Diagnostic:
    diagnostic_id: str
    cost: int
    observation_by_class: Mapping[RevisionClass, str]


@dataclass(frozen=True)
class RevisionCase:
    case_id: str
    family_id: str
    visible_residual: str
    candidate_revision_options: tuple[RevisionClass, ...]
    diagnostics: tuple[Diagnostic, ...]
    gold_class: RevisionClass
    minimal_licensed_response: RevisionClass
    forbidden_revision_classes: tuple[RevisionClass, ...] = ()
    unaffected_state_invariants: tuple[str, ...] = ()
    budget: int = 1

    def public_view(self) -> dict[str, object]:
        """Candidate-visible representation; protected gold is deliberately absent."""
        return {
            "case_id": self.case_id,
            "family_id": self.family_id,
            "visible_residual": self.visible_residual,
            "candidate_revision_options": tuple(x.value for x in self.candidate_revision_options),
            "diagnostics": tuple(
                {"diagnostic_id": d.diagnostic_id, "cost": d.cost}
                for d in self.diagnostics
            ),
            "budget": self.budget,
        }


@dataclass(frozen=True)
class PolicyDecision:
    revision_class: RevisionClass
    diagnostic_id: str | None = None


@dataclass(frozen=True)
class Stage0Score:
    n: int
    correct: int
    false_broad_revision: int
    forbidden_revision: int
    unresolved_correct: int
    diagnostic_cost: int

    @property
    def accuracy(self) -> float:
        return self.correct / self.n if self.n else 0.0

    @property
    def false_broad_revision_rate(self) -> float:
        return self.false_broad_revision / self.n if self.n else 0.0


Policy = Callable[[RevisionCase, Mapping[str, str]], PolicyDecision]


def reveal_diagnostics(
    case: RevisionCase,
    *,
    permutation: Mapping[RevisionClass, RevisionClass] | None = None,
) -> dict[str, str]:
    """Reveal only observations licensed by the case budget.

    ``permutation`` supports the fake-adaptivity control: the prompt/case is fixed while
    outcome identities are swapped. A permutation is applied only when the target class
    is a valid outcome of that same diagnostic; unrelated families remain unchanged.
    This preserves the diagnostic's support instead of fabricating an impossible outcome.
    """
    observations: dict[str, str] = {}
    spent = 0
    for diagnostic in case.diagnostics:
        if spent + diagnostic.cost > case.budget:
            continue
        observed_class = case.gold_class
        if permutation is not None:
            candidate = permutation.get(case.gold_class, case.gold_class)
            if candidate in diagnostic.observation_by_class:
                observed_class = candidate
        observations[diagnostic.diagnostic_id] = diagnostic.observation_by_class[observed_class]
        spent += diagnostic.cost
    return observations


def score_policy(
    cases: tuple[RevisionCase, ...],
    policy: Policy,
    *,
    permutation: Mapping[RevisionClass, RevisionClass] | None = None,
) -> Stage0Score:
    correct = false_broad = forbidden = unresolved_correct = cost = 0
    for case in cases:
        observations = reveal_diagnostics(case, permutation=permutation)
        decision = policy(case, observations)
        if decision.revision_class is case.minimal_licensed_response:
            correct += 1
        if (
            decision.revision_class in BROAD_CLASSES
            and case.minimal_licensed_response not in BROAD_CLASSES
        ):
            false_broad += 1
        if decision.revision_class in case.forbidden_revision_classes:
            forbidden += 1
        if (
            decision.revision_class is RevisionClass.UNRESOLVED
            and case.minimal_licensed_response is RevisionClass.UNRESOLVED
        ):
            unresolved_correct += 1
        if decision.diagnostic_id is not None:
            for diagnostic in case.diagnostics:
                if diagnostic.diagnostic_id == decision.diagnostic_id:
                    cost += diagnostic.cost
                    break
    return Stage0Score(
        n=len(cases),
        correct=correct,
        false_broad_revision=false_broad,
        forbidden_revision=forbidden,
        unresolved_correct=unresolved_correct,
        diagnostic_cost=cost,
    )


def responsibility_gated_policy(
    case: RevisionCase, observations: Mapping[str, str]
) -> PolicyDecision:
    """Minimal pilot policy: map discriminating observations to the narrowest response."""
    mapping = {
        "missing-evidence": RevisionClass.EVIDENCE,
        "parameter-fit": RevisionClass.PARAMETER,
        "class-inadequate": RevisionClass.M_OPEN,
        "sensor-bad": RevisionClass.MEASUREMENT,
        "mechanism-missing": RevisionClass.M_OPEN,
        "alignment-sufficient": RevisionClass.PARAMETER,
        "state-inadequate": RevisionClass.REPRESENTATION,
        "exogenous": RevisionClass.NO_SELF_REVISION,
        "self-defect": RevisionClass.PARAMETER,
        "safe-region": RevisionClass.CONTAIN,
        "need-data": RevisionClass.EVIDENCE,
        "evaluator-bad": RevisionClass.EVALUATOR,
        "candidate-bad": RevisionClass.PARAMETER,
        "insufficient": RevisionClass.UNRESOLVED,
    }
    for diagnostic_id, observation in observations.items():
        if observation in mapping:
            return PolicyDecision(mapping[observation], diagnostic_id)
    return PolicyDecision(RevisionClass.UNRESOLVED)


def m_open_only_policy(case: RevisionCase, observations: Mapping[str, str]) -> PolicyDecision:
    del observations
    return PolicyDecision(RevisionClass.M_OPEN)


def always_unresolved_policy(case: RevisionCase, observations: Mapping[str, str]) -> PolicyDecision:
    del case, observations
    return PolicyDecision(RevisionClass.UNRESOLVED)


def direct_update_policy(case: RevisionCase, observations: Mapping[str, str]) -> PolicyDecision:
    del observations
    if RevisionClass.PARAMETER in case.candidate_revision_options:
        return PolicyDecision(RevisionClass.PARAMETER)
    return PolicyDecision(RevisionClass.UNRESOLVED)


def stage0_cases() -> tuple[RevisionCase, ...]:
    """Cause-confusable known-answer pilot families frozen independently of policies."""
    epm = Diagnostic(
        "d:evidence-parameter-model",
        1,
        {
            RevisionClass.EVIDENCE: "missing-evidence",
            RevisionClass.PARAMETER: "parameter-fit",
            RevisionClass.M_OPEN: "class-inadequate",
        },
    )
    measurement = Diagnostic(
        "d:measurement-mechanism",
        1,
        {
            RevisionClass.MEASUREMENT: "sensor-bad",
            RevisionClass.M_OPEN: "mechanism-missing",
        },
    )
    representation = Diagnostic(
        "d:alignment-representation",
        1,
        {
            RevisionClass.PARAMETER: "alignment-sufficient",
            RevisionClass.REPRESENTATION: "state-inadequate",
        },
    )
    stochasticity = Diagnostic(
        "d:stochasticity",
        1,
        {
            RevisionClass.NO_SELF_REVISION: "exogenous",
            RevisionClass.PARAMETER: "self-defect",
            RevisionClass.UNRESOLVED: "insufficient",
        },
    )
    containment = Diagnostic(
        "d:containment",
        1,
        {
            RevisionClass.CONTAIN: "safe-region",
            RevisionClass.EVIDENCE: "need-data",
            RevisionClass.M_OPEN: "class-inadequate",
        },
    )
    evaluator = Diagnostic(
        "d:evaluator-candidate",
        1,
        {
            RevisionClass.EVALUATOR: "evaluator-bad",
            RevisionClass.PARAMETER: "candidate-bad",
            RevisionClass.UNRESOLVED: "insufficient",
        },
    )
    return (
        RevisionCase("v3:evidence", "evidence-vs-model", "prediction residual", (RevisionClass.EVIDENCE, RevisionClass.PARAMETER, RevisionClass.M_OPEN), (epm,), RevisionClass.EVIDENCE, RevisionClass.EVIDENCE, (RevisionClass.OBJECTIVE,)),
        RevisionCase("v3:parameter", "evidence-vs-model", "prediction residual", (RevisionClass.EVIDENCE, RevisionClass.PARAMETER, RevisionClass.M_OPEN), (epm,), RevisionClass.PARAMETER, RevisionClass.PARAMETER, (RevisionClass.OBJECTIVE,)),
        RevisionCase("v3:m-open", "evidence-vs-model", "prediction residual", (RevisionClass.EVIDENCE, RevisionClass.PARAMETER, RevisionClass.M_OPEN), (epm,), RevisionClass.M_OPEN, RevisionClass.M_OPEN),
        RevisionCase("v3:measurement", "measurement-vs-mechanism", "mechanism mismatch", (RevisionClass.MEASUREMENT, RevisionClass.M_OPEN), (measurement,), RevisionClass.MEASUREMENT, RevisionClass.MEASUREMENT),
        RevisionCase("v3:mechanism", "measurement-vs-mechanism", "mechanism mismatch", (RevisionClass.MEASUREMENT, RevisionClass.M_OPEN), (measurement,), RevisionClass.M_OPEN, RevisionClass.M_OPEN),
        RevisionCase("v3:alignment", "alignment-vs-regime", "downstream transfer failure", (RevisionClass.PARAMETER, RevisionClass.REPRESENTATION), (representation,), RevisionClass.PARAMETER, RevisionClass.PARAMETER),
        RevisionCase("v3:regime", "alignment-vs-regime", "downstream transfer failure", (RevisionClass.PARAMETER, RevisionClass.REPRESENTATION), (representation,), RevisionClass.REPRESENTATION, RevisionClass.REPRESENTATION),
        RevisionCase("v3:luck", "stochasticity-vs-self", "bad outcome", (RevisionClass.NO_SELF_REVISION, RevisionClass.PARAMETER, RevisionClass.UNRESOLVED), (stochasticity,), RevisionClass.NO_SELF_REVISION, RevisionClass.NO_SELF_REVISION, (RevisionClass.M_OPEN, RevisionClass.OBJECTIVE)),
        RevisionCase("v3:contain", "contain-investigate-revise", "model uncertainty", (RevisionClass.CONTAIN, RevisionClass.EVIDENCE, RevisionClass.M_OPEN), (containment,), RevisionClass.CONTAIN, RevisionClass.CONTAIN),
        RevisionCase("v3:investigate", "contain-investigate-revise", "model uncertainty", (RevisionClass.CONTAIN, RevisionClass.EVIDENCE, RevisionClass.M_OPEN), (containment,), RevisionClass.EVIDENCE, RevisionClass.EVIDENCE),
        RevisionCase("v3:evaluator", "evaluator-vs-candidate", "FAIL", (RevisionClass.EVALUATOR, RevisionClass.PARAMETER, RevisionClass.UNRESOLVED), (evaluator,), RevisionClass.EVALUATOR, RevisionClass.EVALUATOR),
        RevisionCase("v3:unknown", "evaluator-vs-candidate", "FAIL", (RevisionClass.EVALUATOR, RevisionClass.PARAMETER, RevisionClass.UNRESOLVED), (evaluator,), RevisionClass.UNRESOLVED, RevisionClass.UNRESOLVED),
    )
