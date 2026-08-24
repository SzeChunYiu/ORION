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




def theorem_t4_t5_discharge() -> list[TheoremResult]:
    rules = (
        DischargeRule(frozenset({"native-proof", "scope-match"}), "local-verified"),
        DischargeRule(frozenset({"local-verified", "promotion-bridge"}), "scientific-claim"),
    )
    seeds = frozenset({"native-proof", "scope-match"})
    neutral_steps = (frozenset({"local-verified"}), frozenset({"native-proof"}))
    no_amp = no_amplification_holds(seeds, rules, neutral_steps)
    bridge_needed = bridge_necessity_holds(
        seeds,
        (rules[0],),
        "scientific-claim",
        neutral_steps,
    )
    return [
        TheoremResult(
            "OSTC-T4",
            "Authority-neutral transformations do not enlarge discharge closure.",
            "LOCAL_PROVED" if no_amp else "COUNTEREXAMPLE",
            ("neutral outputs already lie in the registered least closure",),
            "two neutral materialization steps preserved the fixed point exactly",
        ),
        TheoremResult(
            "OSTC-T5",
            "A target outside closure cannot be reached without new evidence or a bridge.",
            "LOCAL_PROVED" if bridge_needed else "COUNTEREXAMPLE",
            ("finite monotone Horn bridge rules", "authority-neutral intermediate steps"),
            "scientific-claim remained unreachable until promotion-bridge was registered",
        ),
    ]


def theorem_t6_t8_normal_form() -> list[TheoremResult]:
    required = frozenset({"attributable", "occurrence_bound", "content_bound"})
    admitted = 0
    extracted = 0
    validated = 0
    rows: list[dict[str, object]] = []
    for valid, sufficient, entitled, blockers_clear in product((False, True), repeat=4):
        state, judgment = _workflow_state(
            artifact_valid=valid,
            authority=entitled,
            blocker_status=(
                ObligationStatus.DISCHARGED
                if blockers_clear
                else ObligationStatus.UNDETERMINED
            ),
        )
        if sufficient:
            interface = FiniteInterface(
                "promotion-interface",
                {"world-good": "licensed"},
            )
            state_ids = ("world-good",)
            target_map = {"world-good": Terminal.ESTABLISH}
        else:
            interface = FiniteInterface(
                "promotion-interface",
                {"world-good": "same", "world-bad": "same"},
            )
            state_ids = ("world-good", "world-bad")
            target_map = {
                "world-good": Terminal.ESTABLISH,
                "world-bad": Terminal.REOPEN,
            }
        decision = decide_transition(
            state,
            judgment,
            interface,
            state_ids,
            target_map,
            bridge_id="b1",
            authority_id="external-scientific",
            support_family_id="sf1",
            required_integrity=required,
        )
        certificate = extract_normal_form(
            state,
            judgment,
            interface,
            state_ids,
            target_map,
            bridge_id="b1",
            authority_id="external-scientific",
            support_family_id="sf1",
            required_integrity=required,
        )
        expected = valid and sufficient and entitled and blockers_clear
        actual = decision.terminal is Terminal.ESTABLISH
        if actual:
            admitted += 1
        if certificate is not None:
            extracted += 1
            if validate_normal_form(
                state,
                certificate,
                interface,
                state_ids,
                target_map,
                required_integrity=required,
            ):
                validated += 1
        rows.append(
            {
                "V": valid,
                "S": sufficient,
                "E": entitled,
                "B": blockers_clear,
                "terminal": decision.terminal.value,
                "certificate": certificate is not None,
            }
        )
        if actual != expected or (certificate is not None) != actual:
            return [
                TheoremResult(
                    "OSTC-T6",
                    (
                        "Every valid finite normal-form certificate is sound for "
                        "the operational semantics."
                    ),
                    "COUNTEREXAMPLE",
                    ("finite bridge workflow",),
                    f"mismatch at row {rows[-1]}",
                ),
                TheoremResult(
                    "OSTC-T7",
                    (
                        "Every admitted transition in the finite bridge workflow "
                        "yields a normal-form certificate."
                    ),
                    "COUNTEREXAMPLE",
                    ("finite bridge workflow",),
                    f"mismatch at row {rows[-1]}",
                ),
                TheoremResult(
                    "OSTC-T8",
                    (
                        "V, S, E, and B are independently load-bearing in the "
                        "registered workflow class."
                    ),
                    "COUNTEREXAMPLE",
                    ("class-relative minimality only",),
                    f"mismatch at row {rows[-1]}",
                ),
            ]

    factor_rows = {
        factor: next(
            row
            for row in rows
            if all(
                bool(row[name]) == (name != factor)
                for name in ("V", "S", "E", "B")
            )
        )
        for factor in ("V", "S", "E", "B")
    }
    independent = all(row["terminal"] != Terminal.ESTABLISH.value for row in factor_rows.values())
    return [
        TheoremResult(
            "OSTC-T6",
            "Every valid finite normal-form certificate is sound for the operational semantics.",
            "LOCAL_PROVED" if validated == extracted == admitted == 1 else "COUNTEREXAMPLE",
            (
                "finite bridge workflow",
                "registered sound bridge",
                "target-sufficient interface",
                "complete support family",
            ),
            f"16/16 factor worlds checked; admitted={admitted}; validated={validated}",
        ),
        TheoremResult(
            "OSTC-T7",
            (
                "Every admitted transition in the finite bridge workflow yields "
                "a normal-form certificate."
            ),
            "LOCAL_PROVED" if extracted == admitted == 1 else "COUNTEREXAMPLE",
            ("finite bridge workflow", "operational transition admitted"),
            f"16/16 factor worlds checked; extracted={extracted}; admitted={admitted}",
        ),
        TheoremResult(
            "OSTC-T8",
            "V, S, E, and B are independently load-bearing in the registered workflow class.",
            "LOCAL_PROVED" if independent else "COUNTEREXAMPLE",
            ("class-relative minimality only",),
            f"single-factor removals={factor_rows}",
        ),
    ]


def theorem_t9_full_abstraction() -> TheoremResult:
    states = ("a", "b", "c", "d")
    target = {
        "a": Terminal.ESTABLISH,
        "b": Terminal.ESTABLISH,
        "c": Terminal.REOPEN,
        "d": Terminal.REOPEN,
    }
    abstract = FiniteInterface("quotient", {"a": 0, "b": 0, "c": 1, "d": 1})
    rich = FiniteInterface("rich", {state: state for state in states})
    passed = is_fully_abstract(states, abstract, target) and not is_fully_abstract(
        states, rich, target
    )
    return TheoremResult(
        "OSTC-T9",
        "A fully abstract interface identifies exactly the target-equivalence classes.",
        "LOCAL_PROVED" if passed else "COUNTEREXAMPLE",
        ("one registered target relation",),
        (
            "minimal quotient is fully abstract; a strictly richer identity interface "
            "is sufficient but not minimal"
        ),
    )


def theorem_t10_t11_composition_revocation() -> list[TheoremResult]:
    first = TransitionContract("local", "scientific", "sha:x", "s", "e", "r", "auth")
    second = TransitionContract("scientific", "publication", "sha:x", "s", "e", "r", "auth")
    bad = TransitionContract("scientific", "publication", "sha:y", "s", "e", "r", "auth")
    composition = contracts_compose(first, second) and not contracts_compose(first, bad)

    state, judgment = _workflow_state()
    alternate = SupportFamily(
        "sf2",
        judgment,
        frozenset({"a2"}),
        frozenset({"b1"}),
        frozenset({"external-scientific"}),
        frozenset({"conflict"}),
    )
    artifact2 = Artifact(
        "a2",
        judgment.target,
        "independent-proof",
        judgment.target.content_identity,
        True,
        "checker-2",
        "prov:2",
        judgment.target.epoch,
        "occ:2",
        "sig:checker-2",
        ExecutionIntegrity(attributable=True, occurrence_bound=True, content_bound=True),
    )
    state = replace(
        state,
        artifacts=state.artifacts + (artifact2,),
        support_families=state.support_families + (alternate,),
    )
    once, retained_once = apply_revocation(state, frozenset({"a1"}))
    _, retained_twice = apply_revocation(once, frozenset({"a2"}))
    revocation = judgment in retained_once and judgment not in retained_twice
    return [
        TheoremResult(
            "OSTC-T10",
            "Transition certificates compose only across exactly matching intermediate contracts.",
            "LOCAL_PROVED" if composition else "COUNTEREXAMPLE",
            ("exact content/scope/epoch/responsibility/authority matching",),
            "clean pair composed; content-mismatched pair was rejected",
        ),
        TheoremResult(
            "OSTC-T11",
            "Revocation removes a judgment iff every complete support family is broken.",
            "LOCAL_PROVED" if revocation else "COUNTEREXAMPLE",
            ("support families are complete and explicitly enumerated",),
            "one independent support survived the first revocation; none survived the second",
        ),
    ]


