"""Scoped epistemic licensing — frozen before any V2 outcome.

A probe never grants a mutating license. UNRESOLVED and non-intervention-backed
states issue CANNOT_CHECK / probe requests, never broad W/M mutation.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import Enum

from orion.kernel.store import canonical_bytes

from .belief import MUTATION_BEARING, AuthorityClass, BeliefState


class EpistemicAction(str, Enum):
    ACQUIRE_EVIDENCE = "ACQUIRE_EVIDENCE"
    REPAIR_EXECUTION = "REPAIR_EXECUTION"
    RUN_PROBE = "RUN_PROBE"
    RUN_INTERVENTION = "RUN_INTERVENTION"
    REWRITE_FORMULATION = "REWRITE_FORMULATION"
    EXPAND_SEARCH_UNIVERSE = "EXPAND_SEARCH_UNIVERSE"
    REOPEN_DEPENDENCIES = "REOPEN_DEPENDENCIES"
    REWRITE_METHOD = "REWRITE_METHOD"
    BROAD_WM_MUTATION = "BROAD_WM_MUTATION"


MUTATING_ACTIONS: frozenset[EpistemicAction] = frozenset(
    {
        EpistemicAction.REWRITE_FORMULATION,
        EpistemicAction.EXPAND_SEARCH_UNIVERSE,
        EpistemicAction.REWRITE_METHOD,
        EpistemicAction.BROAD_WM_MUTATION,
    }
)

UNIVERSAL: frozenset[EpistemicAction] = frozenset(
    {EpistemicAction.RUN_PROBE, EpistemicAction.RUN_INTERVENTION}
)


def _row(*actions: EpistemicAction) -> frozenset[EpistemicAction]:
    return UNIVERSAL | frozenset(actions)


LICENSING_MATRIX: dict[AuthorityClass, frozenset[EpistemicAction]] = {
    AuthorityClass.EVIDENCE: _row(EpistemicAction.ACQUIRE_EVIDENCE),
    AuthorityClass.EXECUTION: _row(EpistemicAction.REPAIR_EXECUTION),
    AuthorityClass.FORMULATION: _row(
        EpistemicAction.REWRITE_FORMULATION,
        EpistemicAction.REOPEN_DEPENDENCIES,
    ),
    AuthorityClass.SEARCH_UNIVERSE: _row(
        EpistemicAction.EXPAND_SEARCH_UNIVERSE,
        EpistemicAction.REOPEN_DEPENDENCIES,
    ),
    AuthorityClass.UNRESOLVED: _row(),
}


class RefusalReason(str, Enum):
    UNRESOLVED = "UNRESOLVED"
    NOT_INTERVENTION_BACKED = "NOT_INTERVENTION_BACKED"
    ACTION_NOT_LICENSED = "ACTION_NOT_LICENSED"
    PROTECTED_METHOD = "PROTECTED_METHOD"
    BROAD_MUTATION_FORBIDDEN = "BROAD_MUTATION_FORBIDDEN"
    MATRIX_INVARIANT_BREACH = "MATRIX_INVARIANT_BREACH"


class UnauthorizedMutationError(RuntimeError):
    """Executing a mutating action without a granted license."""


@dataclass(frozen=True)
class LicenseDecision:
    action: EpistemicAction
    granted: bool
    ground: AuthorityClass
    refusal: RefusalReason | None = None
    detail: str = ""
    cannot_check: bool = False

    @property
    def mutates(self) -> bool:
        return self.action in MUTATING_ACTIONS

    def to_payload(self) -> dict:
        return {
            "action": self.action.value,
            "granted": self.granted,
            "ground": self.ground.value,
            "refusal": self.refusal.value if self.refusal else "",
            "detail": self.detail,
            "cannot_check": self.cannot_check,
            "mutates": self.mutates,
        }


def matrix_fingerprint(
    matrix: dict[AuthorityClass, frozenset[EpistemicAction]] | None = None,
) -> str:
    table = LICENSING_MATRIX if matrix is None else matrix
    payload = [
        [item.value, sorted(action.value for action in table[item])]
        for item in AuthorityClass
        if item in table
    ]
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def audit_matrix(
    matrix: dict[AuthorityClass, frozenset[EpistemicAction]] | None = None,
) -> tuple[str, ...]:
    table = LICENSING_MATRIX if matrix is None else matrix
    violations: list[str] = []
    for item in AuthorityClass:
        if item not in table:
            violations.append(f"row_missing:{item.value}")
            continue
        mutating = [action for action in table[item] if action in MUTATING_ACTIONS]
        if item not in MUTATION_BEARING and mutating:
            violations.append(
                "mutation_licensed_by_non_mutation_class:"
                f"{item.value}:{','.join(action.value for action in mutating)}"
            )
        if EpistemicAction.REWRITE_METHOD in table[item]:
            violations.append(f"method_licensed:{item.value}")
        if EpistemicAction.BROAD_WM_MUTATION in table[item]:
            violations.append(f"broad_mutation_licensed:{item.value}")
        if item is AuthorityClass.UNRESOLVED and mutating:
            violations.append("unresolved_licenses_mutation")
    return tuple(violations)


def request_action(
    state: BeliefState,
    action: EpistemicAction,
    *,
    matrix: dict[AuthorityClass, frozenset[EpistemicAction]] | None = None,
) -> LicenseDecision:
    table = LICENSING_MATRIX if matrix is None else matrix
    ground = state.authority_class

    def refuse(reason: RefusalReason, detail: str, *, cannot_check: bool = False) -> LicenseDecision:
        return LicenseDecision(
            action=action,
            granted=False,
            ground=ground,
            refusal=reason,
            detail=detail,
            cannot_check=cannot_check,
        )

    if action is EpistemicAction.REWRITE_METHOD:
        return refuse(RefusalReason.PROTECTED_METHOD, "M.METHOD is a Self-ORION transition")
    if action is EpistemicAction.BROAD_WM_MUTATION:
        return refuse(
            RefusalReason.BROAD_MUTATION_FORBIDDEN,
            "broad W/M mutation after any failure is never licensed",
        )
    if ground is AuthorityClass.UNRESOLVED:
        if action in MUTATING_ACTIONS or action not in UNIVERSAL:
            return refuse(
                RefusalReason.UNRESOLVED,
                "UNRESOLVED issues CANNOT_CHECK / probe request, never mutation",
                cannot_check=True,
            )
        # Probe / intervention requests remain available; they are not licenses
        # to mutate W or M.
    if action in MUTATING_ACTIONS and not state.intervention_backed:
        return refuse(
            RefusalReason.NOT_INTERVENTION_BACKED,
            "a probe or passive diagnosis cannot grant mutating authority",
        )
    permitted = table.get(ground)
    if permitted is None:
        return refuse(RefusalReason.MATRIX_INVARIANT_BREACH, "missing matrix row")
    if action not in permitted:
        return refuse(
            RefusalReason.ACTION_NOT_LICENSED,
            f"{ground.value} does not license {action.value}",
        )
    if action in MUTATING_ACTIONS and ground not in MUTATION_BEARING:
        return refuse(
            RefusalReason.MATRIX_INVARIANT_BREACH,
            "matrix granted mutation from a non-mutation class",
        )
    return LicenseDecision(action=action, granted=True, ground=ground, detail="licensed")


def apply_licensed_action(state: BeliefState, action: EpistemicAction) -> LicenseDecision:
    decision = request_action(state, action)
    if action in MUTATING_ACTIONS and not decision.granted:
        raise UnauthorizedMutationError(
            f"{action.value} blocked: {decision.refusal.value if decision.refusal else 'refused'}"
        )
    return decision
