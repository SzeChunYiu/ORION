"""Operational discharge semantics, normal forms, composition, and revocation."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable, Mapping, Sequence

from .model import (
    Artifact,
    BridgeRule,
    Event,
    EventKind,
    Judgment,
    ObligationStatus,
    ScientificState,
    SupportFamily,
    Terminal,
)
from .sufficiency import FiniteInterface, is_target_sufficient


@dataclass(frozen=True)
class NormalFormCertificate:
    target_judgment: Judgment
    artifact_ids: frozenset[str]
    interface_name: str
    bridge_id: str
    authority_id: str
    support_family_id: str
    cleared_blockers: frozenset[str]


@dataclass(frozen=True)
class DecisionExplanation:
    terminal: Terminal
    failed_factor: str | None
    detail: str


@dataclass(frozen=True)
class DischargeRule:
    premises: frozenset[str]
    conclusion: str


def least_closure(seeds: Iterable[str], rules: Sequence[DischargeRule]) -> frozenset[str]:
    closure = set(seeds)
    changed = True
    while changed:
        changed = False
        for rule in rules:
            if rule.premises.issubset(closure) and rule.conclusion not in closure:
                closure.add(rule.conclusion)
                changed = True
    return frozenset(closure)


def authority_neutral_extension(
    seeds: Iterable[str],
    rules: Sequence[DischargeRule],
    proposed_derived: Iterable[str],
) -> frozenset[str]:
    """A neutral transform may only materialize an already licensed consequence."""

    base = least_closure(seeds, rules)
    derived = frozenset(proposed_derived)
    if not derived.issubset(base):
        missing = sorted(derived - base)
        raise ValueError(f"authority-neutral transform attempted new judgments: {missing}")
    return least_closure(base | derived, rules)


def no_amplification_holds(
    seeds: Iterable[str],
    rules: Sequence[DischargeRule],
    neutral_steps: Sequence[frozenset[str]],
) -> bool:
    base = least_closure(seeds, rules)
    current = base
    for step in neutral_steps:
        current = authority_neutral_extension(current, rules, step)
    return current == base


def bridge_necessity_holds(
    seeds: Iterable[str],
    rules: Sequence[DischargeRule],
    target: str,
    neutral_steps: Sequence[frozenset[str]],
) -> bool:
    base = least_closure(seeds, rules)
    if target in base:
        raise ValueError("target is already inside the authorized closure")
    current = base
    for step in neutral_steps:
        current = authority_neutral_extension(current, rules, step)
    return target not in current


def _artifact_map(state: ScientificState) -> dict[str, Artifact]:
    return {artifact.artifact_id: artifact for artifact in state.artifacts}


def _bridge_map(state: ScientificState) -> dict[str, BridgeRule]:
    return {bridge.bridge_id: bridge for bridge in state.bridge_rules}


def _support_map(state: ScientificState) -> dict[str, SupportFamily]:
    return {family.family_id: family for family in state.support_families}


def decide_transition(
    state: ScientificState,
    target: Judgment,
    interface: FiniteInterface,
    state_ids: Sequence[str],
    target_terminals: Mapping[str, Terminal],
    *,
    bridge_id: str,
    authority_id: str,
    support_family_id: str,
    required_integrity: frozenset[str] = frozenset(),
) -> DecisionExplanation:
    """Operational rule for a finite bridge workflow.

    The rule is written against primitive state objects.  It does not consume a
    preassembled normal-form certificate.  Certificate extraction is a separate
    function used by the normal-form theorem.
    """

    artifacts = _artifact_map(state)
    support = _support_map(state).get(support_family_id)
    if support is None or support.target_judgment != target:
        return DecisionExplanation(Terminal.BLOCK, "B", "no matching complete support family")

    for artifact_id in sorted(support.artifact_ids):
        artifact = artifacts.get(artifact_id)
        if artifact is None:
            return DecisionExplanation(Terminal.DENY, "V", f"missing artifact {artifact_id}")
        if not artifact.native_valid:
            return DecisionExplanation(Terminal.DENY, "V", f"artifact {artifact_id} is invalid")
        if artifact.epoch != target.target.epoch:
            return DecisionExplanation(Terminal.DENY, "V", f"artifact {artifact_id} is stale")
        if not artifact.integrity.satisfies(required_integrity):
            return DecisionExplanation(
                Terminal.CANNOT_CHECK,
                "V",
                f"artifact {artifact_id} lacks required execution integrity",
            )

    if not is_target_sufficient(state_ids, interface, target_terminals):
        return DecisionExplanation(
            Terminal.CANNOT_CHECK,
            "S",
            "target terminal is not constant on an interface fibre",
        )

    bridge = _bridge_map(state).get(bridge_id)
    if bridge is None or not bridge.sound:
        return DecisionExplanation(Terminal.DENY, "E", "missing or unsound target bridge")
    if bridge.target_object != target.target:
        return DecisionExplanation(Terminal.DENY, "E", "bridge targets a different object")
    if bridge.responsibility_id != target.responsibility.responsibility_id:
        return DecisionExplanation(Terminal.DENY, "E", "bridge targets a different responsibility")
    if bridge.scope != target.target.scope or bridge.epoch != target.target.epoch:
        return DecisionExplanation(Terminal.DENY, "E", "bridge scope or epoch mismatch")
    if authority_id not in state.authorities or bridge.required_authority != authority_id:
        return DecisionExplanation(Terminal.DENY, "E", "required target authority is absent")

    for blocker_id in sorted(support.blocker_ids):
        status = state.blockers.get(blocker_id, ObligationStatus.UNDETERMINED)
        if status is ObligationStatus.BLOCKED:
            return DecisionExplanation(Terminal.BLOCK, "B", f"blocker {blocker_id} is established")
        if status is not ObligationStatus.DISCHARGED:
            return DecisionExplanation(
                Terminal.CANNOT_CHECK,
                "B",
                f"blocker {blocker_id} remains {status.value}",
            )

    return DecisionExplanation(Terminal.ESTABLISH, None, "operational transition admitted")


def extract_normal_form(
    state: ScientificState,
    target: Judgment,
    interface: FiniteInterface,
    state_ids: Sequence[str],
    target_terminals: Mapping[str, Terminal],
    *,
    bridge_id: str,
    authority_id: str,
    support_family_id: str,
    required_integrity: frozenset[str] = frozenset(),
) -> NormalFormCertificate | None:
    decision = decide_transition(
        state,
        target,
        interface,
        state_ids,
        target_terminals,
        bridge_id=bridge_id,
        authority_id=authority_id,
        support_family_id=support_family_id,
        required_integrity=required_integrity,
    )
    if decision.terminal is not Terminal.ESTABLISH:
        return None
    support = _support_map(state)[support_family_id]
    cleared = frozenset(
        blocker_id
        for blocker_id in support.blocker_ids
        if state.blockers.get(blocker_id) is ObligationStatus.DISCHARGED
    )
    return NormalFormCertificate(
        target_judgment=target,
        artifact_ids=support.artifact_ids,
        interface_name=interface.name,
        bridge_id=bridge_id,
        authority_id=authority_id,
        support_family_id=support_family_id,
        cleared_blockers=cleared,
    )


def validate_normal_form(
    state: ScientificState,
    certificate: NormalFormCertificate,
    interface: FiniteInterface,
    state_ids: Sequence[str],
    target_terminals: Mapping[str, Terminal],
    *,
    required_integrity: frozenset[str] = frozenset(),
) -> bool:
    if certificate.interface_name != interface.name:
        return False
    support = _support_map(state).get(certificate.support_family_id)
    if support is None or support.artifact_ids != certificate.artifact_ids:
        return False
    decision = decide_transition(
        state,
        certificate.target_judgment,
        interface,
        state_ids,
        target_terminals,
        bridge_id=certificate.bridge_id,
        authority_id=certificate.authority_id,
        support_family_id=certificate.support_family_id,
        required_integrity=required_integrity,
    )
    return decision.terminal is Terminal.ESTABLISH


def certificate_to_event(certificate: NormalFormCertificate) -> Event:
    return Event(
        event_id=f"discharge:{certificate.target_judgment.responsibility.responsibility_id}",
        kind=EventKind.DISCHARGE,
        target_judgment=certificate.target_judgment,
        artifact_ids=certificate.artifact_ids,
        bridge_id=certificate.bridge_id,
        authority_id=certificate.authority_id,
        support_family_id=certificate.support_family_id,
        note="constructed from a validated normal-form certificate",
    )


def apply_revocation(
    state: ScientificState,
    revoked_artifact_ids: frozenset[str],
) -> tuple[ScientificState, frozenset[Judgment]]:
    """Return the new state and judgments retaining at least one complete support family."""

    retained_families = tuple(
        family
        for family in state.support_families
        if not family.artifact_ids.intersection(revoked_artifact_ids)
    )
    retained_judgments = frozenset(family.target_judgment for family in retained_families)
    artifacts = tuple(
        artifact for artifact in state.artifacts if artifact.artifact_id not in revoked_artifact_ids
    )
    history = state.negative_history + tuple(
        f"revoked:{artifact_id}" for artifact_id in sorted(revoked_artifact_ids)
    )
    return (
        replace(
            state,
            artifacts=artifacts,
            support_families=retained_families,
            negative_history=history,
        ),
        retained_judgments,
    )


@dataclass(frozen=True)
class TransitionContract:
    source_type: str
    target_type: str
    content_identity: str
    scope: str
    epoch: str
    responsibility_id: str
    authority_class: str


def contracts_compose(first: TransitionContract, second: TransitionContract) -> bool:
    return (
        first.target_type == second.source_type
        and first.content_identity == second.content_identity
        and first.scope == second.scope
        and first.epoch == second.epoch
        and first.responsibility_id == second.responsibility_id
        and first.authority_class == second.authority_class
    )
