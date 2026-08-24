"""Deterministic local theorem and countermodel suite for issue #1220."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from enum import Enum
from fractions import Fraction
from itertools import product
from typing import Any, Callable

from .capability import (
    AllocationWorld,
    DiagnosticModel,
    MethodLanguage,
    MethodRule,
    PlacementLaw,
    ResponsibilityModel,
    certify_expansion,
    certify_obstruction,
)
from .discharge import (
    DischargeRule,
    TransitionContract,
    apply_revocation,
    bridge_necessity_holds,
    contracts_compose,
    decide_transition,
    extract_normal_form,
    no_amplification_holds,
    validate_normal_form,
)
from .integrity import (
    AdoptionWorld,
    EvolutionCertificate,
    AdvanceCase,
    ExecutionScienceCase,
    black_box_synthesis_verification_gap,
    candidate_only_adoption_is_identifying,
    coupled_advance_separations,
    integrity_does_not_identify_science,
    protected_adoption_is_identifying,
)
from .model import (
    Artifact,
    BridgeRule,
    ExecutionIntegrity,
    Judgment,
    ObligationStatus,
    Responsibility,
    ScientificObject,
    ScientificState,
    SupportFamily,
    Terminal,
)
from .open_world import (
    OpenWorldCompletion,
    RegimeTransport,
    best_deterministic_closure_error,
    compose_transport,
)
from .sufficiency import (
    FiniteInterface,
    bayes_risk,
    data_processing_holds,
    is_fully_abstract,
    is_target_sufficient,
    minimal_collision,
    synthesise_decision_rule,
    verifies_factorisation,
)


from .theorem_types import TheoremResult

def theorem_t19_self_promotion() -> TheoremResult:
    worlds = (
        AdoptionWorld("genuine", "visible-pass", "fresh-pass", True),
        AdoptionWorld("gaming", "visible-pass", "fresh-fail", False),
    )
    candidate = candidate_only_adoption_is_identifying(worlds)
    protected = protected_adoption_is_identifying(worlds)
    passed = not candidate and protected
    return TheoremResult(
        "OSTC-T19",
        "Candidate-controlled evidence cannot identify safe adoption on a gaming collision pair.",
        "LOCAL_PROVED" if passed else "COUNTEREXAMPLE",
        ("candidate sees the same record in both worlds", "protected record is external"),
        "external fresh evidence separates the genuine and gaming worlds",
    )


def theorem_t20_integrity() -> TheoremResult:
    integrity = ExecutionIntegrity(
        attributable=True,
        occurrence_bound=True,
        content_bound=True,
        environment_bound=True,
        chronology_valid=True,
        replayable=True,
        cross_implementation_agreement=True,
        attested=True,
        custody_bound=True,
        freshness_bound=True,
    )
    cases = (
        ExecutionScienceCase("valid", integrity, Terminal.ESTABLISH),
        ExecutionScienceCase("invalid", integrity, Terminal.BLOCK),
    )
    passed = integrity_does_not_identify_science(cases)
    return TheoremResult(
        "OSTC-T20",
        "Even complete execution integrity does not identify scientific validity or authority.",
        "LOCAL_PROVED" if passed else "COUNTEREXAMPLE",
        ("same integrity vector", "different scientific gold"),
        "minimal integrity-fibre collision contains one valid and one blocked scientific case",
    )


def theorem_t21_governed_evolution() -> TheoremResult:
    complete = EvolutionCertificate(
        issue_identity="issue-1",
        diagnosis_and_discriminator="cause separated by hidden test",
        candidate_intervention="patch-1",
        isolation_record="sandbox:1",
        replay_record="replay:green",
        fresh_transfer_record="fresh:green",
        protected_assurance_record="assurance:green",
        negative_history_update="history:appended",
        external_adoption_record="host:approved",
    )
    self_promoted = replace(complete, external_adoption_record="")
    passed = complete.valid and not self_promoted.valid
    return TheoremResult(
        "OSTC-T21",
        "Governed recursive evolution requires a complete protected record and external adoption.",
        "LOCAL_PROVED" if passed else "COUNTEREXAMPLE",
        ("finite evolution-certificate schema",),
        "complete record validates; deleting external adoption blocks promotion",
    )


def theorem_t22_synthesis_checking_gap() -> TheoremResult:
    search_queries, verification_queries = black_box_synthesis_verification_gap(16)
    passed = search_queries == 16 and verification_queries == 1
    return TheoremResult(
        "OSTC-T22",
        (
            "In a unique-witness black-box family, deterministic synthesis may require "
            "N queries while checking a supplied witness requires one."
        ),
        "LOCAL_PROVED" if passed else "COUNTEREXAMPLE",
        ("unique marked candidate", "deterministic black-box search"),
        f"worst-case synthesis queries={search_queries}; certificate checks={verification_queries}",
    )


def theorem_t23_coupled_advance() -> TheoremResult:
    cases = (
        AdvanceCase("advance", True, True),
        AdvanceCase("reachable-unauthorized", True, False),
        AdvanceCase("authorized-unreachable", False, True),
        AdvanceCase("neither", False, False),
    )
    passed = coupled_advance_separations(cases)
    return TheoremResult(
        "OSTC-T23",
        (
            "Scientific advance is the conjunction of reachability and admissibility; "
            "neither substitutes for the other."
        ),
        "LOCAL_PROVED" if passed else "COUNTEREXAMPLE",
        ("four logically possible finite cases",),
        "all four truth-table cells are nonempty",
    )


def answer_laundering_control() -> TheoremResult:
    states = ("s0", "s1")
    target = {"s0": Terminal.ESTABLISH, "s1": Terminal.REOPEN}
    leaked = FiniteInterface(
        "answer-coded",
        {"s0": Terminal.ESTABLISH.value, "s1": Terminal.REOPEN.value},
        protected_target_reads=frozenset({"gold_terminal"}),
    )
    passed = is_target_sufficient(states, leaked, target) and not leaked.admissible
    return TheoremResult(
        "OSTC-GUARD-NO-ANSWER-LAUNDERING",
        "Mathematical sufficiency does not imply admissible scientific construction.",
        "LOCAL_PROVED" if passed else "COUNTEREXAMPLE",
        ("protected target reads are declared",),
        "answer-coded interface is sufficient but rejected as inadmissible",
    )


