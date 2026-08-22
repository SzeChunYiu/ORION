from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class ResearchOutcomeKind(str, Enum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    UNRESOLVED = "UNRESOLVED"


class UnresolvedClass(str, Enum):
    CAPABILITY = "CAPABILITY"
    EVIDENCE = "EVIDENCE"
    COVERAGE = "COVERAGE"
    IDENTIFIABILITY = "IDENTIFIABILITY"
    RESOURCE = "RESOURCE"
    AUTHORITY = "AUTHORITY"
    PROTECTED_EXTERNAL = "PROTECTED_EXTERNAL"
    RESPONSIBILITY = "RESPONSIBILITY"
    METHOD = "METHOD"
    REPRESENTATION = "REPRESENTATION"
    UNKNOWN = "UNKNOWN"


class ResolutionState(str, Enum):
    ACTIVE = "ACTIVE"
    BLOCKED_EXTERNAL = "BLOCKED_EXTERNAL"
    CERTIFIED_BOUNDED = "CERTIFIED_BOUNDED"
    RESOLVED = "RESOLVED"


class ResolutionAction(str, Enum):
    RETRY_CAPABILITY = "RETRY_CAPABILITY"
    ACQUIRE_EVIDENCE = "ACQUIRE_EVIDENCE"
    VERIFY_EVIDENCE = "VERIFY_EVIDENCE"
    EXPAND_SEARCH = "EXPAND_SEARCH"
    ORIENT = "ORIENT"
    REFRAME = "REFRAME"
    DIAGNOSE_RESPONSIBILITY = "DIAGNOSE_RESPONSIBILITY"
    REPAIR_REPRESENTATION = "REPAIR_REPRESENTATION"
    ASSESS_OCME = "ASSESS_OCME"
    CHECK_AUTHORITY = "CHECK_AUTHORITY"
    REQUEST_RESOURCE_WIDENING = "REQUEST_RESOURCE_WIDENING"
    REQUEST_PROTECTED_EVIDENCE = "REQUEST_PROTECTED_EVIDENCE"
    TASK_STOP = "TASK_STOP"


class AssimilationDisposition(str, Enum):
    ASSIMILATE_OBSTRUCTION = "ASSIMILATE_OBSTRUCTION"
    CLOSE_HYPOTHESIS_BRANCH = "CLOSE_HYPOTHESIS_BRANCH"
    REOPEN_DEPENDENCY = "REOPEN_DEPENDENCY"
    REFRAME = "REFRAME"
    EXPAND_SEARCH = "EXPAND_SEARCH"
    REGISTER_DONOR_SUBSUMPTION = "REGISTER_DONOR_SUBSUMPTION"
    REVISE_PAPER_CLAIM = "REVISE_PAPER_CLAIM"
    REVISE_FRAMEWORK_MECHANIC = "REVISE_FRAMEWORK_MECHANIC"
    BOUNDED_NEGATIVE_TERMINAL = "BOUNDED_NEGATIVE_TERMINAL"


def _ids(values: Iterable[str], *, name: str, allow_empty: bool = True) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise TypeError(f"{name} must be an iterable of strings")
    out = tuple(str(value).strip() for value in values)
    if not allow_empty and not out:
        raise ValueError(f"{name} cannot be empty")
    if any(not value for value in out):
        raise ValueError(f"{name} entries must be non-empty")
    if len(set(out)) != len(out):
        raise ValueError(f"{name} entries must be unique")
    return out


@dataclass(frozen=True)
class ResearchResolutionObligation:
    obligation_id: str
    subject_id: str
    unresolved_class: UnresolvedClass
    reason_codes: tuple[str, ...]
    required_object_ids: tuple[str, ...]
    next_actions: tuple[ResolutionAction, ...]
    attempt_ids: tuple[str, ...] = ()
    blocker_ids: tuple[str, ...] = ()
    bounded_stop_condition: str = ""
    state: ResolutionState = ResolutionState.ACTIVE
    outcome_kind: ResearchOutcomeKind = ResearchOutcomeKind.UNRESOLVED
    grants_scientific_authority: bool = False
    grants_novelty_authority: bool = False
    grants_promotion_authority: bool = False
    grants_global_task_stop_authority: bool = False

    def __post_init__(self) -> None:
        if not self.obligation_id.strip() or not self.subject_id.strip():
            raise ValueError("resolution obligation requires obligation and subject identity")
        object.__setattr__(self, "reason_codes", _ids(self.reason_codes, name="reason_codes", allow_empty=False))
        object.__setattr__(self, "required_object_ids", _ids(self.required_object_ids, name="required_object_ids"))
        object.__setattr__(self, "attempt_ids", _ids(self.attempt_ids, name="attempt_ids"))
        object.__setattr__(self, "blocker_ids", _ids(self.blocker_ids, name="blocker_ids"))
        if isinstance(self.next_actions, (str, bytes)):
            raise TypeError("next_actions must be an array")
        if not self.next_actions and self.state is ResolutionState.ACTIVE:
            raise ValueError("active resolution obligation requires a next action")
        if ResolutionAction.TASK_STOP in self.next_actions:
            raise ValueError("resolution obligations cannot self-authorize task stop")
        if self.outcome_kind is not ResearchOutcomeKind.UNRESOLVED:
            raise ValueError("resolution obligation outcome kind must remain UNRESOLVED")
        if any(
            (
                self.grants_scientific_authority,
                self.grants_novelty_authority,
                self.grants_promotion_authority,
                self.grants_global_task_stop_authority,
            )
        ):
            raise ValueError("resolution obligation cannot grant authority")

    def as_dict(self) -> dict[str, object]:
        return {
            "schema": "ORION.ResearchResolutionObligation.v1",
            "obligation_id": self.obligation_id,
            "subject_id": self.subject_id,
            "unresolved_class": self.unresolved_class.value,
            "reason_codes": list(self.reason_codes),
            "required_object_ids": list(self.required_object_ids),
            "next_actions": [item.value for item in self.next_actions],
            "attempt_ids": list(self.attempt_ids),
            "blocker_ids": list(self.blocker_ids),
            "bounded_stop_condition": self.bounded_stop_condition,
            "state": self.state.value,
            "outcome_kind": self.outcome_kind.value,
            "grants_scientific_authority": False,
            "grants_novelty_authority": False,
            "grants_promotion_authority": False,
            "grants_global_task_stop_authority": False,
        }


@dataclass(frozen=True)
class ResearchNegativeResult:
    result_id: str
    subject_id: str
    negative_kind: str
    evidence_ids: tuple[str, ...]
    reason_codes: tuple[str, ...]
    dispositions: tuple[AssimilationDisposition, ...]
    outcome_kind: ResearchOutcomeKind = ResearchOutcomeKind.NEGATIVE
    grants_scientific_authority: bool = False
    grants_novelty_authority: bool = False
    grants_promotion_authority: bool = False
    grants_global_task_stop_authority: bool = False

    def __post_init__(self) -> None:
        if not self.result_id.strip() or not self.subject_id.strip() or not self.negative_kind.strip():
            raise ValueError("negative result requires result, subject and kind identities")
        object.__setattr__(self, "evidence_ids", _ids(self.evidence_ids, name="evidence_ids", allow_empty=False))
        object.__setattr__(self, "reason_codes", _ids(self.reason_codes, name="reason_codes", allow_empty=False))
        if isinstance(self.dispositions, (str, bytes)) or not self.dispositions:
            raise ValueError("negative result requires at least one assimilation disposition")
        if self.outcome_kind is not ResearchOutcomeKind.NEGATIVE:
            raise ValueError("negative result outcome kind must remain NEGATIVE")
        if any(
            (
                self.grants_scientific_authority,
                self.grants_novelty_authority,
                self.grants_promotion_authority,
                self.grants_global_task_stop_authority,
            )
        ):
            raise ValueError("negative-result assimilation cannot grant authority")

    def as_dict(self) -> dict[str, object]:
        return {
            "schema": "ORION.ResearchNegativeResult.v1",
            "result_id": self.result_id,
            "subject_id": self.subject_id,
            "negative_kind": self.negative_kind,
            "evidence_ids": list(self.evidence_ids),
            "reason_codes": list(self.reason_codes),
            "dispositions": [item.value for item in self.dispositions],
            "outcome_kind": self.outcome_kind.value,
            "grants_scientific_authority": False,
            "grants_novelty_authority": False,
            "grants_promotion_authority": False,
            "grants_global_task_stop_authority": False,
        }


__all__ = [
    "AssimilationDisposition",
    "ResearchNegativeResult",
    "ResearchOutcomeKind",
    "ResearchResolutionObligation",
    "ResolutionAction",
    "ResolutionState",
    "UnresolvedClass",
]
