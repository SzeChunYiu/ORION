from __future__ import annotations

from typing import Iterable, Mapping

from orion.core.research_resolution import (
    AssimilationDisposition,
    ResearchNegativeResult,
    ResearchResolutionObligation,
    ResolutionAction,
    ResolutionState,
    UnresolvedClass,
)

from .protocol import content_digest


def _tuple(values: Iterable[str]) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise TypeError("expected an iterable of strings")
    return tuple(str(value) for value in values)


def _resolution_policy(
    unresolved_class: UnresolvedClass,
) -> tuple[ResolutionState, tuple[ResolutionAction, ...], str]:
    if unresolved_class is UnresolvedClass.CAPABILITY:
        return ResolutionState.ACTIVE, (ResolutionAction.RETRY_CAPABILITY,), ""
    if unresolved_class is UnresolvedClass.EVIDENCE:
        return (
            ResolutionState.ACTIVE,
            (ResolutionAction.ACQUIRE_EVIDENCE, ResolutionAction.VERIFY_EVIDENCE),
            "",
        )
    if unresolved_class is UnresolvedClass.COVERAGE:
        return (
            ResolutionState.ACTIVE,
            (ResolutionAction.EXPAND_SEARCH, ResolutionAction.ORIENT),
            "",
        )
    if unresolved_class is UnresolvedClass.IDENTIFIABILITY:
        return (
            ResolutionState.ACTIVE,
            (ResolutionAction.EXPAND_SEARCH, ResolutionAction.REFRAME),
            "a formally certified non-identifiability result should be assimilated as NEGATIVE rather than left as CANNOT_CHECK",
        )
    if unresolved_class is UnresolvedClass.RESOURCE:
        return (
            ResolutionState.ACTIVE,
            (ResolutionAction.REQUEST_RESOURCE_WIDENING, ResolutionAction.REFRAME),
            "if the frozen protocol forbids further resource widening, preserve the unresolved obligation without task-stop authority",
        )
    if unresolved_class is UnresolvedClass.AUTHORITY:
        return ResolutionState.ACTIVE, (ResolutionAction.CHECK_AUTHORITY,), ""
    if unresolved_class is UnresolvedClass.PROTECTED_EXTERNAL:
        return (
            ResolutionState.BLOCKED_EXTERNAL,
            (ResolutionAction.REQUEST_PROTECTED_EVIDENCE,),
            "required protected/external evidence is not released under the current protocol",
        )
    if unresolved_class is UnresolvedClass.RESPONSIBILITY:
        return ResolutionState.ACTIVE, (ResolutionAction.DIAGNOSE_RESPONSIBILITY,), ""
    if unresolved_class is UnresolvedClass.METHOD:
        return ResolutionState.ACTIVE, (ResolutionAction.ASSESS_OCME,), ""
    if unresolved_class is UnresolvedClass.REPRESENTATION:
        return (
            ResolutionState.ACTIVE,
            (ResolutionAction.REPAIR_REPRESENTATION, ResolutionAction.REFRAME),
            "",
        )
    return ResolutionState.ACTIVE, (ResolutionAction.DIAGNOSE_RESPONSIBILITY,), ""


def build_resolution_obligation(
    *,
    subject_id: str,
    unresolved_class: UnresolvedClass,
    reason_codes: Iterable[str],
    required_object_ids: Iterable[str] = (),
    attempt_ids: Iterable[str] = (),
    blocker_ids: Iterable[str] = (),
) -> ResearchResolutionObligation:
    reasons = _tuple(reason_codes)
    required = _tuple(required_object_ids)
    attempts = _tuple(attempt_ids)
    blockers = _tuple(blocker_ids)
    state, next_actions, stop_condition = _resolution_policy(unresolved_class)
    identity = {
        "subject_id": subject_id,
        "unresolved_class": unresolved_class.value,
        "reason_codes": list(reasons),
        "required_object_ids": list(required),
        "attempt_ids": list(attempts),
        "blocker_ids": list(blockers),
    }
    return ResearchResolutionObligation(
        obligation_id="resolution:" + content_digest(identity)[:24],
        subject_id=subject_id,
        unresolved_class=unresolved_class,
        reason_codes=reasons,
        required_object_ids=required,
        next_actions=next_actions,
        attempt_ids=attempts,
        blocker_ids=blockers,
        bounded_stop_condition=stop_condition,
        state=state,
    )


def _negative_dispositions(negative_kind: str) -> tuple[AssimilationDisposition, ...]:
    key = negative_kind.strip().upper()
    if key in {"DONOR_SUBSUMED", "OCME_DONOR_SUBSUMED"}:
        return (
            AssimilationDisposition.REGISTER_DONOR_SUBSUMPTION,
            AssimilationDisposition.CLOSE_HYPOTHESIS_BRANCH,
            AssimilationDisposition.REVISE_PAPER_CLAIM,
        )
    if key in {
        "VERIFIED_OBSTRUCTION",
        "EXACT_FINITE_NONREACHABILITY",
        "MACHINE_CHECKED_LOWER_BOUND",
    }:
        return (
            AssimilationDisposition.ASSIMILATE_OBSTRUCTION,
            AssimilationDisposition.REFRAME,
            AssimilationDisposition.REOPEN_DEPENDENCY,
        )
    if key in {"NON_IDENTIFIABLE", "FORMAL_NON_IDENTIFIABILITY"}:
        return (
            AssimilationDisposition.BOUNDED_NEGATIVE_TERMINAL,
            AssimilationDisposition.REVISE_PAPER_CLAIM,
        )
    if key in {"IMPOSSIBILITY_BOUNDARY", "OCME_IMPOSSIBILITY_BOUNDARY"}:
        return (
            AssimilationDisposition.ASSIMILATE_OBSTRUCTION,
            AssimilationDisposition.BOUNDED_NEGATIVE_TERMINAL,
            AssimilationDisposition.REVISE_FRAMEWORK_MECHANIC,
        )
    if key in {"FAILED_TRANSFER", "FALSIFIED_HYPOTHESIS", "NEGATIVE_EXPERIMENT"}:
        return (
            AssimilationDisposition.CLOSE_HYPOTHESIS_BRANCH,
            AssimilationDisposition.REFRAME,
            AssimilationDisposition.EXPAND_SEARCH,
        )
    return (
        AssimilationDisposition.CLOSE_HYPOTHESIS_BRANCH,
        AssimilationDisposition.REVISE_PAPER_CLAIM,
    )


def assimilate_negative_result(
    *,
    result_id: str,
    subject_id: str,
    negative_kind: str,
    evidence_ids: Iterable[str],
    reason_codes: Iterable[str],
) -> ResearchNegativeResult:
    return ResearchNegativeResult(
        result_id=result_id,
        subject_id=subject_id,
        negative_kind=negative_kind,
        evidence_ids=_tuple(evidence_ids),
        reason_codes=_tuple(reason_codes),
        dispositions=_negative_dispositions(negative_kind),
    )


def resolution_plan_from_mapping(raw: Mapping[str, object]) -> dict[str, object]:
    outcome_kind = str(raw.get("outcome_kind", "UNRESOLVED")).strip().upper()
    subject_id = str(raw.get("subject_id", "")).strip()
    if not subject_id:
        raise ValueError("subject_id is required")
    reason_codes_raw = raw.get("reason_codes", ())
    if isinstance(reason_codes_raw, (str, bytes)) or not isinstance(reason_codes_raw, (list, tuple)):
        raise TypeError("reason_codes must be an array")

    if outcome_kind == "NEGATIVE":
        evidence_raw = raw.get("evidence_ids", ())
        if isinstance(evidence_raw, (str, bytes)) or not isinstance(evidence_raw, (list, tuple)):
            raise TypeError("evidence_ids must be an array")
        result = assimilate_negative_result(
            result_id=str(raw.get("result_id") or ("negative:" + content_digest(dict(raw))[:24])),
            subject_id=subject_id,
            negative_kind=str(raw.get("negative_kind", "NEGATIVE_RESULT")),
            evidence_ids=tuple(str(item) for item in evidence_raw),
            reason_codes=tuple(str(item) for item in reason_codes_raw),
        )
        return result.as_dict()

    unresolved_raw = str(raw.get("unresolved_class", "UNKNOWN")).strip().upper()
    try:
        unresolved_class = UnresolvedClass(unresolved_raw)
    except ValueError as exc:
        raise ValueError(f"unsupported unresolved_class: {unresolved_raw!r}") from exc

    def rows(name: str) -> tuple[str, ...]:
        value = raw.get(name, ())
        if isinstance(value, (str, bytes)) or not isinstance(value, (list, tuple)):
            raise TypeError(f"{name} must be an array")
        return tuple(str(item) for item in value)

    obligation = build_resolution_obligation(
        subject_id=subject_id,
        unresolved_class=unresolved_class,
        reason_codes=tuple(str(item) for item in reason_codes_raw),
        required_object_ids=rows("required_object_ids"),
        attempt_ids=rows("attempt_ids"),
        blocker_ids=rows("blocker_ids"),
    )
    return obligation.as_dict()


__all__ = [
    "assimilate_negative_result",
    "build_resolution_obligation",
    "resolution_plan_from_mapping",
]
