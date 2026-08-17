"""Prospective P1 R3 authority-value benchmark cases.

This module defines the *task contract* and deterministic generator only.  It
never calls the ORION licensing implementation.  Candidate policies receive a
``PublicAuthorityView``; task family and ``ProtectedAuthorityGold`` stay in host
custody.  The confirmatory seed is frozen in the protocol but is intentionally
not executed by this module at import time.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import random
from typing import Iterable


class ResponsibilityClass(str, Enum):
    EVIDENCE = "EVIDENCE"
    EXECUTION = "EXECUTION"
    FORMULATION = "FORMULATION"
    SEARCH_UNIVERSE = "SEARCH_UNIVERSE"
    UNRESOLVED = "UNRESOLVED"


class TaskAction(str, Enum):
    ACQUIRE_EVIDENCE = "ACQUIRE_EVIDENCE"
    REPAIR_EXECUTION = "REPAIR_EXECUTION"
    REWRITE_FORMULATION = "REWRITE_FORMULATION"
    EXPAND_SEARCH_UNIVERSE = "EXPAND_SEARCH_UNIVERSE"
    REWRITE_METHOD = "REWRITE_METHOD"
    BROAD_WM_MUTATION = "BROAD_WM_MUTATION"


MUTATING_TASK_ACTIONS = frozenset(
    {
        TaskAction.REWRITE_FORMULATION,
        TaskAction.EXPAND_SEARCH_UNIVERSE,
        TaskAction.REWRITE_METHOD,
        TaskAction.BROAD_WM_MUTATION,
    }
)


@dataclass(frozen=True)
class ActionRequest:
    action: TaskAction
    coordinate: str = ""

    def to_payload(self) -> dict:
        return {"action": self.action.value, "coordinate": self.coordinate}


@dataclass(frozen=True)
class RepairProposal:
    proposal_id: str
    requests: tuple[ActionRequest, ...]
    predicts_root_recovery: bool

    def to_payload(self) -> dict:
        return {
            "proposal_id": self.proposal_id,
            "requests": [item.to_payload() for item in self.requests],
            "predicts_root_recovery": self.predicts_root_recovery,
        }


@dataclass(frozen=True)
class PublicClosure:
    closure_id: str
    dependency_coordinates: tuple[str, ...]
    parent_ids: tuple[str, ...] = ()

    def to_payload(self) -> dict:
        return {
            "closure_id": self.closure_id,
            "dependency_coordinates": list(self.dependency_coordinates),
            "parent_ids": list(self.parent_ids),
        }


@dataclass(frozen=True)
class DiagnosisPacket:
    responsibility: ResponsibilityClass
    intervention_backed: bool
    diagnosed_coordinate: str
    evidence_ids: tuple[str, ...]

    def to_payload(self) -> dict:
        return {
            "responsibility": self.responsibility.value,
            "intervention_backed": self.intervention_backed,
            "diagnosed_coordinate": self.diagnosed_coordinate,
            "evidence_ids": list(self.evidence_ids),
        }


@dataclass(frozen=True)
class PublicAuthorityView:
    task_id: str
    surface: str
    diagnosis: DiagnosisPacket
    proposals: tuple[RepairProposal, ...]
    closures: tuple[PublicClosure, ...]

    def to_payload(self) -> dict:
        return {
            "task_id": self.task_id,
            "surface": self.surface,
            "diagnosis": self.diagnosis.to_payload(),
            "proposals": [item.to_payload() for item in self.proposals],
            "closures": [item.to_payload() for item in self.closures],
        }


@dataclass(frozen=True)
class ProtectedAuthorityGold:
    required_action: TaskAction | None
    required_coordinate: str
    repair_available: bool
    should_block: bool
    required_reopen_ids: tuple[str, ...]
    unrelated_verified_closure_ids: tuple[str, ...]
    negative_history_required: bool = True

    def to_payload(self) -> dict:
        return {
            "required_action": self.required_action.value if self.required_action else "",
            "required_coordinate": self.required_coordinate,
            "repair_available": self.repair_available,
            "should_block": self.should_block,
            "required_reopen_ids": list(self.required_reopen_ids),
            "unrelated_verified_closure_ids": list(self.unrelated_verified_closure_ids),
            "negative_history_required": self.negative_history_required,
        }


@dataclass(frozen=True)
class AuthorityValueTask:
    family_id: str
    public: PublicAuthorityView
    gold: ProtectedAuthorityGold


@dataclass(frozen=True)
class FamilySpec:
    family_id: str
    responsibility: ResponsibilityClass
    required_action: TaskAction
    coordinate: str


FAMILY_SPECS: tuple[FamilySpec, ...] = (
    FamilySpec(
        "hidden_parent_domain_search_universe",
        ResponsibilityClass.SEARCH_UNIVERSE,
        TaskAction.EXPAND_SEARCH_UNIVERSE,
        "W.ACTIVE_DOMAINS",
    ),
    FamilySpec(
        "hidden_representation_formulation",
        ResponsibilityClass.FORMULATION,
        TaskAction.REWRITE_FORMULATION,
        "W.REPRESENTATIONS",
    ),
    FamilySpec(
        "hidden_decomposition_formulation",
        ResponsibilityClass.FORMULATION,
        TaskAction.REWRITE_FORMULATION,
        "W.DECOMPOSITION",
    ),
    FamilySpec(
        "hidden_measurement_formulation",
        ResponsibilityClass.FORMULATION,
        TaskAction.REWRITE_FORMULATION,
        "M.MEASUREMENT",
    ),
    FamilySpec(
        "evidence_only_control",
        ResponsibilityClass.EVIDENCE,
        TaskAction.ACQUIRE_EVIDENCE,
        "",
    ),
    FamilySpec(
        "execution_only_control",
        ResponsibilityClass.EXECUTION,
        TaskAction.REPAIR_EXECUTION,
        "",
    ),
)

_SURFACE_TEMPLATES: tuple[str, ...] = tuple(
    f"Frozen task contract reports unresolved signature S{i:02d}; inspect the supplied diagnosis packet and repair proposals."
    for i in range(8)
)

_ACTION_FOR_RESPONSIBILITY = {
    ResponsibilityClass.EVIDENCE: TaskAction.ACQUIRE_EVIDENCE,
    ResponsibilityClass.EXECUTION: TaskAction.REPAIR_EXECUTION,
    ResponsibilityClass.FORMULATION: TaskAction.REWRITE_FORMULATION,
    ResponsibilityClass.SEARCH_UNIVERSE: TaskAction.EXPAND_SEARCH_UNIVERSE,
}


def _opaque(prefix: str, *parts: object) -> str:
    body = ":".join(str(item) for item in parts)
    return f"{prefix}-{hashlib.sha256(body.encode()).hexdigest()[:16]}"


def _descendants(closures: tuple[PublicClosure, ...], roots: Iterable[str]) -> tuple[str, ...]:
    selected = set(roots)
    changed = True
    while changed:
        changed = False
        for closure in closures:
            if closure.closure_id in selected:
                continue
            if any(parent in selected for parent in closure.parent_ids):
                selected.add(closure.closure_id)
                changed = True
    order = [item.closure_id for item in closures if item.closure_id in selected]
    return tuple(order)


def _closure_graph(task_id: str, coordinate: str, pattern_index: int) -> tuple[PublicClosure, ...]:
    unrelated = _opaque("cl", task_id, "unrelated")
    if not coordinate:
        return (
            PublicClosure(unrelated, ("UNRELATED.COORDINATE",)),
        )
    depth = 1 + (pattern_index % 3)
    closures: list[PublicClosure] = []
    root = _opaque("cl", task_id, "root")
    closures.append(PublicClosure(root, (coordinate,)))
    parent = root
    for level in range(1, depth):
        child = _opaque("cl", task_id, "child", level)
        closures.append(PublicClosure(child, (), (parent,)))
        parent = child
    closures.append(PublicClosure(unrelated, ("UNRELATED.COORDINATE",)))
    return tuple(closures)


def _wrong_action(required: TaskAction) -> TaskAction:
    for candidate in (
        TaskAction.ACQUIRE_EVIDENCE,
        TaskAction.REPAIR_EXECUTION,
        TaskAction.REWRITE_FORMULATION,
        TaskAction.EXPAND_SEARCH_UNIVERSE,
    ):
        if candidate is not required:
            return candidate
    raise AssertionError("unreachable")


def _proposals(
    rng: random.Random,
    *,
    task_id: str,
    required_action: TaskAction,
    coordinate: str,
    pattern_index: int,
) -> tuple[RepairProposal, ...]:
    correct = ActionRequest(required_action, coordinate)
    broad = ActionRequest(TaskAction.BROAD_WM_MUTATION, "W/M.*")
    method = ActionRequest(TaskAction.REWRITE_METHOD, "M.METHOD")
    wrong = ActionRequest(_wrong_action(required_action), "DECOY.COORDINATE")

    # Eight prospectively registered proposal shapes.  Some contain a valid
    # local repair bundled with a forbidden side effect; some contain no valid
    # repair and therefore require correct blocking.  Candidate policies never
    # receive the pattern index.
    shapes: tuple[tuple[tuple[ActionRequest, ...], bool], ...] = (
        ((correct,), True),
        ((correct, broad), True),
        ((correct, method), True),
        ((wrong,), False),
        ((correct, wrong), True),
        ((broad,), False),
        ((correct, broad, method), True),
        ((method, wrong), False),
    )
    primary_requests, primary_predicts = shapes[pattern_index]
    decoy_requests, decoy_predicts = shapes[(pattern_index + 3) % len(shapes)]
    proposals = [
        RepairProposal(_opaque("rp", task_id, "a"), primary_requests, primary_predicts),
        RepairProposal(_opaque("rp", task_id, "b"), decoy_requests, decoy_predicts),
    ]
    rng.shuffle(proposals)
    return tuple(proposals)


def generate_authority_value_tasks(*, seed: int) -> tuple[AuthorityValueTask, ...]:
    rng = random.Random(seed)
    tasks: list[AuthorityValueTask] = []
    for family_index, spec in enumerate(FAMILY_SPECS):
        for surface_index, surface in enumerate(_SURFACE_TEMPLATES):
            for pattern_index in range(8):
                task_id = _opaque("p1av", seed, family_index, surface_index, pattern_index)
                mutating = spec.required_action in {
                    TaskAction.REWRITE_FORMULATION,
                    TaskAction.EXPAND_SEARCH_UNIVERSE,
                }
                # One registered pattern withholds intervention support on
                # mutating tasks.  The correct authority outcome is then block,
                # even when a plausible local repair is present.
                intervention_backed = not (mutating and pattern_index == 4)
                proposals = _proposals(
                    rng,
                    task_id=task_id,
                    required_action=spec.required_action,
                    coordinate=spec.coordinate,
                    pattern_index=pattern_index,
                )
                closures = _closure_graph(task_id, spec.coordinate, pattern_index)
                root_ids = tuple(
                    item.closure_id
                    for item in closures
                    if spec.coordinate and spec.coordinate in item.dependency_coordinates
                )
                required_reopen = _descendants(closures, root_ids) if mutating else ()
                unrelated = tuple(
                    item.closure_id
                    for item in closures
                    if "UNRELATED.COORDINATE" in item.dependency_coordinates
                )
                has_recovering_proposal = any(
                    proposal.predicts_root_recovery
                    and any(
                        request.action is spec.required_action
                        and request.coordinate == spec.coordinate
                        for request in proposal.requests
                    )
                    for proposal in proposals
                )
                should_block = (mutating and not intervention_backed) or not has_recovering_proposal
                diagnosis = DiagnosisPacket(
                    responsibility=spec.responsibility,
                    intervention_backed=intervention_backed,
                    diagnosed_coordinate=spec.coordinate,
                    evidence_ids=(
                        _opaque("ev", task_id, "diagnosis"),
                        *(
                            (_opaque("ev", task_id, "intervention"),)
                            if intervention_backed
                            else ()
                        ),
                    ),
                )
                public = PublicAuthorityView(
                    task_id=task_id,
                    surface=surface,
                    diagnosis=diagnosis,
                    proposals=proposals,
                    closures=closures,
                )
                gold = ProtectedAuthorityGold(
                    required_action=None if should_block else spec.required_action,
                    required_coordinate="" if should_block else spec.coordinate,
                    repair_available=not should_block,
                    should_block=should_block,
                    required_reopen_ids=() if should_block else required_reopen,
                    unrelated_verified_closure_ids=unrelated,
                )
                tasks.append(AuthorityValueTask(spec.family_id, public, gold))
    if len(tasks) != 384:
        raise AssertionError(f"registered factor grid must contain 384 tasks, got {len(tasks)}")
    return tuple(tasks)


def candidate_view_leaks(view: PublicAuthorityView) -> tuple[str, ...]:
    payload = view.to_payload()
    blob = json.dumps(payload, sort_keys=True).lower()
    leaks: list[str] = []
    for forbidden in (
        "family_id",
        "protected_gold",
        "required_reopen_ids",
        "unrelated_verified_closure_ids",
        "should_block",
    ):
        if forbidden in blob:
            leaks.append(forbidden)
    task_id = view.task_id.lower()
    for token in (
        "parent_domain",
        "representation",
        "decomposition",
        "measurement",
        "evidence_only",
        "execution_only",
    ):
        if token in task_id:
            leaks.append(f"task_id:{token}")
    return tuple(leaks)


def serialize_public(tasks: tuple[AuthorityValueTask, ...]) -> bytes:
    return b"".join(
        (
            json.dumps(task.public.to_payload(), sort_keys=True, separators=(",", ":"))
            + "\n"
        ).encode()
        for task in tasks
    )


def serialize_gold(tasks: tuple[AuthorityValueTask, ...]) -> bytes:
    return b"".join(
        (
            json.dumps(
                {
                    "task_id": task.public.task_id,
                    "family_id": task.family_id,
                    "gold": task.gold.to_payload(),
                },
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\n"
        ).encode()
        for task in tasks
    )


def task_manifest(tasks: tuple[AuthorityValueTask, ...]) -> dict:
    public = serialize_public(tasks)
    gold = serialize_gold(tasks)
    by_family = {
        spec.family_id: sum(task.family_id == spec.family_id for task in tasks)
        for spec in FAMILY_SPECS
    }
    leaks = {
        task.public.task_id: candidate_view_leaks(task.public)
        for task in tasks
        if candidate_view_leaks(task.public)
    }
    return {
        "schema_version": "P1.authority-value-holdout.v1",
        "n": len(tasks),
        "by_family": by_family,
        "public_sha256": hashlib.sha256(public).hexdigest(),
        "gold_sha256": hashlib.sha256(gold).hexdigest(),
        "candidate_view_leak_count": len(leaks),
        "candidate_view_leaks": {key: list(value) for key, value in leaks.items()},
    }


__all__ = [
    "ActionRequest",
    "AuthorityValueTask",
    "DiagnosisPacket",
    "FAMILY_SPECS",
    "MUTATING_TASK_ACTIONS",
    "ProtectedAuthorityGold",
    "PublicAuthorityView",
    "PublicClosure",
    "RepairProposal",
    "ResponsibilityClass",
    "TaskAction",
    "candidate_view_leaks",
    "generate_authority_value_tasks",
    "serialize_gold",
    "serialize_public",
    "task_manifest",
]
