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

def theorem_t12_open_world() -> TheoremResult:
    worlds = (
        OpenWorldCompletion("closed", ("route-a-stop",), True),
        OpenWorldCompletion("open", ("route-a-stop",), False),
    )
    probabilities = {"closed": Fraction(1, 2), "open": Fraction(1, 2)}
    risk = best_deterministic_closure_error(worlds, probabilities)
    return TheoremResult(
        "OSTC-T12",
        (
            "Equal-history open and closed completions force deterministic closure "
            "error at least one half."
        ),
        "LOCAL_PROVED" if risk == Fraction(1, 2) else "COUNTEREXAMPLE",
        ("two equal-prior admissible completions", "history-only deterministic policy"),
        f"minimax/equal-prior error={risk}",
    )


def theorem_t13_transport() -> TheoremResult:
    first = RegimeTransport("t1", "r0", "r1", {"o0": "o1"}, True, True, True)
    good = RegimeTransport("t2", "r1", "r2", {"o1": "o2"}, True, True, True)
    bad = RegimeTransport("t3", "r1", "r2", {"o1": "o2"}, True, False, True)
    alternate_first = RegimeTransport(
        "u1", "r0", "r1b", {"o0": "o1b"}, True, True, True
    )
    alternate_second = RegimeTransport(
        "u2", "r1b", "r2", {"o1b": "o2-prime"}, True, True, True
    )
    direct_path = compose_transport(first, good)
    alternate_path = compose_transport(alternate_first, alternate_second)
    path_dependent = direct_path.obligation_map != alternate_path.obligation_map
    passed = first.sound and good.sound and not bad.sound and path_dependent
    return TheoremResult(
        "OSTC-T13",
        "Regime transport requires continuity at each hop and may remain path-dependent.",
        "LOCAL_PROVED" if passed else "COUNTEREXAMPLE",
        ("registered finite obligation maps",),
        (
            "objective mismatch blocks one hop; two locally sound paths induce "
            "different final obligations"
        ),
        {
            "direct": dict(direct_path.obligation_map),
            "alternate": dict(alternate_path.obligation_map),
        },
    )


def theorem_t14_diagnosis() -> TheoremResult:
    model = DiagnosticModel(
        causes=("information", "access", "compute", "method", "formulation"),
        interventions=("acquire", "reencode", "scale", "expand", "reframe"),
        signatures={
            "information": (1, 0, 0, 0, 0),
            "access": (0, 1, 0, 0, 0),
            "compute": (0, 0, 1, 0, 0),
            "method": (0, 0, 0, 1, 0),
            "formulation": (0, 0, 0, 0, 1),
        },
    )
    minimal = model.minimal_intervention_set()
    ambiguous = model.compatible_causes({})
    passed = model.identifiable() and minimal is not None and len(ambiguous) == 5
    return TheoremResult(
        "OSTC-T14",
        "Failure causes are identifiable exactly when intervention signatures separate them.",
        "LOCAL_PROVED" if passed else "COUNTEREXAMPLE",
        ("deterministic registered response signatures",),
        f"minimal separating interventions={minimal}; no-observation ambiguity={sorted(ambiguous)}",
    )


def theorem_t15_method_expansion() -> TheoremResult:
    old = MethodLanguage(
        "affine",
        frozenset({"x", "1"}),
        (
            MethodRule(frozenset({"x", "1"}), "ax+b"),
        ),
    )
    extended = MethodLanguage(
        "affine+square",
        old.seeds | frozenset({"square"}),
        old.rules
        + (
            MethodRule(frozenset({"square", "x", "1"}), "x^2+ax+b"),
            MethodRule(frozenset({"square", "x", "1"}), "(x+1)^2"),
        ),
    )
    obstruction = certify_obstruction(old, "x^2+ax+b")
    expansion = certify_expansion(
        old,
        extended,
        "square",
        "x^2+ax+b",
        ("(x+1)^2",),
    )
    passed = obstruction.valid and expansion.valid
    return TheoremResult(
        "OSTC-T15",
        "A finite semantic expansion requires old-closure obstruction and new held-out reach.",
        "LOCAL_PROVED" if passed else "COUNTEREXAMPLE",
        ("exact finite registered closure", "extension supplied prospectively"),
        "square is outside affine closure and enables the origin plus a held-out shifted square",
    )


def theorem_t16_placement() -> TheoremResult:
    law = PlacementLaw(Fraction(100), Fraction(10), Fraction(2), Fraction(20))
    break_even = law.break_even_horizon()
    recovered_break_even = law.break_even_horizon(include_recovery=True)
    passed = (
        break_even == 13
        and recovered_break_even == 15
        and not law.compiled_is_cheaper(12)
        and law.compiled_is_cheaper(13)
    )
    return TheoremResult(
        "OSTC-T16",
        "Compiled state is cheaper exactly beyond the fixed-cost break-even horizon.",
        "LOCAL_PROVED" if passed else "COUNTEREXAMPLE",
        ("constant per-query costs", "declared recovery charge"),
        f"break-even={break_even}; with recovery={recovered_break_even}",
    )


def theorem_t17_allocation() -> TheoremResult:
    worlds = (
        AllocationWorld("cheap-state", "coarse", "STATE"),
        AllocationWorld("cheap-reason", "coarse", "REASON"),
    )
    sufficient = len({world.optimal_action for world in worlds}) == 1
    known_certificate_selects = {
        "cheap-state": "STATE",
        "cheap-reason": "REASON",
    }
    exact_when_revealed = all(
        known_certificate_selects[world.world_id] == world.optimal_action for world in worlds
    )
    passed = not sufficient and exact_when_revealed
    return TheoremResult(
        "OSTC-T17",
        (
            "Exact allocation is possible with a sufficient certificate and impossible "
            "on an optimal-action collision fibre."
        ),
        "LOCAL_PROVED" if passed else "COUNTEREXAMPLE",
        ("two worlds share one coarse certificate", "full certificate reveals the cost state"),
        "coarse certificate collides; full certificate selects the exact action in both worlds",
    )


def theorem_t18_responsibility() -> TheoremResult:
    states = ("s0", "s1", "s2", "s3")
    targets = {
        "predict": {
            "s0": Terminal.ESTABLISH,
            "s1": Terminal.ESTABLISH,
            "s2": Terminal.REOPEN,
            "s3": Terminal.REOPEN,
        },
        "verify": {
            "s0": Terminal.ESTABLISH,
            "s1": Terminal.CANNOT_CHECK,
            "s2": Terminal.REOPEN,
            "s3": Terminal.BLOCK,
        },
    }
    model = ResponsibilityModel(states, targets)
    prediction_state = FiniteInterface("prediction-state", {"s0": 0, "s1": 0, "s2": 1, "s3": 1})
    join_state = FiniteInterface("join-state", model.join_labels(("predict", "verify")))
    passed = (
        model.refines("verify", "predict")
        and model.interface_supports("predict", prediction_state)
        and not model.interface_supports("verify", prediction_state)
        and model.interface_supports("verify", join_state)
    )
    return TheoremResult(
        "OSTC-T18",
        (
            "State sufficiency is responsibility-relative; the responsibility join "
            "restores all required distinctions."
        ),
        "LOCAL_PROVED" if passed else "COUNTEREXAMPLE",
        ("finite responsibility target maps",),
        "prediction quotient is insufficient for verification; joint labels are sufficient",
    )


