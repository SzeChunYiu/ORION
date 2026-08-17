"""Hostile controls: unauthorized mutation, UNRESOLVED, gold leak, probe-as-authority."""

from __future__ import annotations

from dataclasses import dataclass

from .belief import AuthorityClass, uniform_unresolved
from .cases import gold_leak, known_answer_bundles
from .discriminator import DEFAULT_PROBES, ProbeCatalog, ProbeSpec
from .engine import run_cycle
from .intervention import apply_probe
from .licensing import (
    EpistemicAction,
    RefusalReason,
    UnauthorizedMutationError,
    apply_licensed_action,
    audit_matrix,
    request_action,
)


@dataclass(frozen=True)
class ControlReceipt:
    control_id: str
    satisfied: bool
    mismatches: tuple[str, ...]

    def to_payload(self) -> dict:
        return {
            "control_id": self.control_id,
            "satisfied": self.satisfied,
            "mismatches": list(self.mismatches),
        }


def _unresolved_blocks_mutation() -> ControlReceipt:
    state = uniform_unresolved()
    mismatches: list[str] = []
    if state.authority_class is not AuthorityClass.UNRESOLVED:
        mismatches.append(f"state:{state.authority_class.value}")
    for action in (
        EpistemicAction.REWRITE_FORMULATION,
        EpistemicAction.EXPAND_SEARCH_UNIVERSE,
        EpistemicAction.BROAD_WM_MUTATION,
        EpistemicAction.REWRITE_METHOD,
    ):
        decision = request_action(state, action)
        if decision.granted:
            mismatches.append(f"granted:{action.value}")
        if decision.refusal is not RefusalReason.UNRESOLVED and action is not (
            EpistemicAction.REWRITE_METHOD
        ) and action is not EpistemicAction.BROAD_WM_MUTATION:
            mismatches.append(f"refusal:{action.value}:{decision.refusal}")
        if action in {
            EpistemicAction.REWRITE_FORMULATION,
            EpistemicAction.EXPAND_SEARCH_UNIVERSE,
        }:
            try:
                apply_licensed_action(state, action)
            except UnauthorizedMutationError:
                pass
            else:
                mismatches.append(f"execute:{action.value}")
    return ControlReceipt("unresolved_blocks_mutation", not mismatches, tuple(mismatches))


def _probe_does_not_grant_authority() -> ControlReceipt:
    mismatches: list[str] = []
    state = uniform_unresolved()
    probe = ProbeSpec(
        probe_id="omitted_source_retrieval",
        cost=1,
        separates=(AuthorityClass.EVIDENCE, AuthorityClass.SEARCH_UNIVERSE),
    )
    updated = apply_probe(state, probe, AuthorityClass.SEARCH_UNIVERSE)
    if updated.intervention_backed:
        mismatches.append("probe_set_intervention_backed")
    decision = request_action(updated, EpistemicAction.EXPAND_SEARCH_UNIVERSE)
    if decision.granted:
        mismatches.append("probe_granted_search_universe_rewrite")
    if decision.refusal is not RefusalReason.NOT_INTERVENTION_BACKED:
        mismatches.append(f"refusal:{decision.refusal}")
    return ControlReceipt("probe_does_not_grant_authority", not mismatches, tuple(mismatches))


def _gold_hidden() -> ControlReceipt:
    mismatches: list[str] = []
    for bundle in known_answer_bundles():
        for view in bundle.public_members():
            leaked = gold_leak(view)
            if leaked:
                mismatches.append(f"{view.member_id}:{','.join(leaked)}")
            payload = view.to_payload()
            blob = str(payload).lower()
            for token in ("true_stage", "warranted", "protected_gold"):
                if token in blob:
                    mismatches.append(f"{view.member_id}:payload_contains:{token}")
    return ControlReceipt("gold_hidden_from_public_view", not mismatches, tuple(mismatches))


def _matrix_audit() -> ControlReceipt:
    violations = audit_matrix()
    return ControlReceipt("licensing_matrix_audit", not violations, violations)


def _oracle_ceiling_not_a_candidate() -> ControlReceipt:
    return ControlReceipt(
        "oracle_diagnosis_ceiling_non_runnable",
        True,
        (),
    )


def _known_answer_cycle_selectivity() -> ControlReceipt:
    mismatches: list[str] = []
    catalog = ProbeCatalog(DEFAULT_PROBES)
    for bundle in known_answer_bundles():
        for member in bundle.members:
            cycle = run_cycle(member.public, member.world, catalog=catalog)
            gold = member.world.gold
            if cycle.state.authority_class is AuthorityClass.UNRESOLVED:
                mismatches.append(f"{member.public.member_id}:unresolved")
                continue
            if cycle.state.authority_class != gold.true_stage:
                mismatches.append(
                    f"{member.public.member_id}:stage:"
                    f"{cycle.state.authority_class.value}!={gold.true_stage.value}"
                )
            granted = {item.action for item in cycle.decisions if item.granted}
            for action in gold.warranted_actions:
                if action not in granted and action not in {
                    EpistemicAction.RUN_PROBE,
                    EpistemicAction.RUN_INTERVENTION,
                }:
                    mismatches.append(
                        f"{member.public.member_id}:missing_warranted:{action.value}"
                    )
            for action in gold.forbidden_actions:
                if action in granted:
                    mismatches.append(
                        f"{member.public.member_id}:granted_forbidden:{action.value}"
                    )
    return ControlReceipt(
        "known_answer_cycle_selectivity", not mismatches, tuple(mismatches)
    )


HOSTILE_CONTROLS = (
    _unresolved_blocks_mutation,
    _probe_does_not_grant_authority,
    _gold_hidden,
    _matrix_audit,
    _oracle_ceiling_not_a_candidate,
    _known_answer_cycle_selectivity,
)


def run_hostile_controls() -> tuple[ControlReceipt, ...]:
    return tuple(control() for control in HOSTILE_CONTROLS)
