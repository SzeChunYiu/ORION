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

def _object() -> ScientificObject:
    return ScientificObject("claim-1", "science", "claim", "global", "sha:claim", "epoch-1")


def _responsibility(target: ScientificObject) -> Responsibility:
    return Responsibility(
        "r-promote",
        target,
        "may the claim be established?",
        "exact terminal",
        "zero false promotion",
        "external-scientific",
    )


def _workflow_state(
    *,
    artifact_valid: bool = True,
    authority: bool = True,
    blocker_status: ObligationStatus = ObligationStatus.DISCHARGED,
    integrity: bool = True,
) -> tuple[ScientificState, Judgment]:
    target = _object()
    responsibility = _responsibility(target)
    judgment = Judgment(target, responsibility, Terminal.ESTABLISH)
    execution = ExecutionIntegrity(
        attributable=integrity,
        occurrence_bound=integrity,
        content_bound=integrity,
        environment_bound=integrity,
        chronology_valid=integrity,
    )
    artifact = Artifact(
        "a1",
        target,
        "native-proof",
        target.content_identity,
        artifact_valid,
        "checker",
        "prov:1",
        target.epoch,
        "occ:1",
        "sig:checker",
        execution,
    )
    bridge = BridgeRule(
        "b1",
        frozenset({"native:a1"}),
        "judgment:claim-1",
        target,
        responsibility.responsibility_id,
        "external-scientific",
        target.scope,
        target.epoch,
    )
    support = SupportFamily(
        "sf1",
        judgment,
        frozenset({"a1"}),
        frozenset({"b1"}),
        frozenset({"external-scientific"}),
        frozenset({"conflict"}),
    )
    state = ScientificState(
        "world-good",
        regime="epoch-1",
        responsibilities=frozenset({responsibility.responsibility_id}),
        artifacts=(artifact,),
        support_families=(support,),
        bridge_rules=(bridge,),
        authorities=(frozenset({"external-scientific"}) if authority else frozenset()),
        blockers={"conflict": blocker_status},
        execution=execution,
    )
    return state, judgment




def theorem_t0_non_tautological() -> TheoremResult:
    interface = FiniteInterface("one-state", {"world-good": "visible"})
    target_map = {"world-good": Terminal.ESTABLISH}
    state, judgment = _workflow_state()
    wrong_object = replace(judgment.target, content_identity="sha:other")
    bad_bridge = replace(state.bridge_rules[0], target_object=wrong_object)
    bad_state = replace(state, bridge_rules=(bad_bridge,))

    coarse_factors = {"V": True, "S": True, "E": True, "B": True}
    operational = decide_transition(
        bad_state,
        judgment,
        interface,
        ("world-good",),
        target_map,
        bridge_id="b1",
        authority_id="external-scientific",
        support_family_id="sf1",
    )
    passed = all(coarse_factors.values()) and operational.terminal is Terminal.DENY
    return TheoremResult(
        "OSTC-T0",
        "Operational admission is not the bare conjunction of four unbound booleans.",
        "LOCAL_PROVED" if passed else "COUNTEREXAMPLE",
        ("typed primitive bridge semantics",),
        "all coarse factors are true, but exact target-content binding rejects the transition",
        {"coarse_factors": coarse_factors, "operational_terminal": operational.terminal.value},
    )


def theorem_t1_native_conservativity() -> TheoremResult:
    interface = FiniteInterface("one-state", {"world-good": "visible"})
    state, judgment = _workflow_state()
    before = state.artifacts[0].native_valid
    _ = decide_transition(
        state,
        judgment,
        interface,
        ("world-good",),
        {"world-good": Terminal.ESTABLISH},
        bridge_id="b1",
        authority_id="external-scientific",
        support_family_id="sf1",
    )
    after = state.artifacts[0].native_valid
    passed = before is True and after is True
    return TheoremResult(
        "OSTC-T1",
        "Scientific transition evaluation preserves donor-native verdicts on their own subjects.",
        "LOCAL_PROVED" if passed else "COUNTEREXAMPLE",
        ("immutable donor artifact record",),
        f"native verdict before={before}; after={after}",
    )


def theorem_t2_fibre() -> TheoremResult:
    states = ("s0", "s1", "s2")
    checked = 0
    first_collision = None
    for observations in product((0, 1), repeat=len(states)):
        interface = FiniteInterface(
            "candidate",
            dict(zip(states, observations, strict=True)),
        )
        for terminals in product(
            (Terminal.ESTABLISH, Terminal.REOPEN),
            repeat=len(states),
        ):
            target = dict(zip(states, terminals, strict=True))
            sufficient = is_target_sufficient(states, interface, target)
            collision = minimal_collision(states, interface, target)
            if sufficient:
                rule = synthesise_decision_rule(states, interface, target)
                if not verifies_factorisation(states, interface, target, rule):
                    return TheoremResult(
                        "OSTC-T2",
                        (
                            "A finite target factors through an interface iff it is "
                            "constant on every fibre."
                        ),
                        "COUNTEREXAMPLE",
                        ("finite nonempty state space", "deterministic target terminal"),
                        "constructed rule failed on an allegedly sufficient interface",
                    )
            elif collision is None:
                return TheoremResult(
                    "OSTC-T2",
                    (
            "A finite target factors through an interface iff it is constant "
            "on every fibre."
        ),
                    "COUNTEREXAMPLE",
                    ("finite nonempty state space", "deterministic target terminal"),
                    "insufficiency was reported without an incompatible fibre pair",
                )
            elif first_collision is None:
                first_collision = collision
            checked += 1
    return TheoremResult(
        "OSTC-T2",
        (
            "A finite target factors through an interface iff it is constant "
            "on every fibre."
        ),
        "LOCAL_PROVED",
        ("finite nonempty state space", "deterministic target terminal"),
        f"exhaustively checked {checked} binary three-state interface/target pairs",
        None if first_collision is None else asdict(first_collision),
    )


def theorem_t3_risk() -> TheoremResult:
    states = ("s0", "s1", "s2", "s3")
    target = {
        "s0": Terminal.ESTABLISH,
        "s1": Terminal.ESTABLISH,
        "s2": Terminal.REOPEN,
        "s3": Terminal.REOPEN,
    }
    probability = {state: Fraction(1, 4) for state in states}
    fine = FiniteInterface("fine", {"s0": 0, "s1": 0, "s2": 1, "s3": 1})
    coarse = FiniteInterface("coarse", {state: 0 for state in states})
    fine_risk = bayes_risk(states, fine, target, probability)
    coarse_risk = bayes_risk(states, coarse, target, probability)
    passed = fine_risk == 0 and coarse_risk == Fraction(1, 2) and data_processing_holds(
        states, fine, coarse, target, probability
    )
    return TheoremResult(
        "OSTC-T3",
        "Coarsening cannot reduce finite Bayes target risk.",
        "LOCAL_PROVED" if passed else "COUNTEREXAMPLE",
        ("known finite probability mass function", "0-1 target loss"),
        f"fine risk={fine_risk}; coarse risk={coarse_risk}",
    )


