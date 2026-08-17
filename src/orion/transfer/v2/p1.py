from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

from ..diagnosis import DiagnosticProbe, ResponsibilityDiagnoser, ResponsibilityHypothesis
from .canonical import content_digest


class EpistemicAction(str, Enum):
    GATHER_EVIDENCE = "GATHER_EVIDENCE"
    RETRY_EXECUTION = "RETRY_EXECUTION"
    REVISE_REPRESENTATION = "REVISE_REPRESENTATION"
    REFRAME_FORMULATION = "REFRAME_FORMULATION"
    EXPAND_SEARCH_UNIVERSE = "EXPAND_SEARCH_UNIVERSE"
    CHANGE_METHOD = "CHANGE_METHOD"


class P1DecisionStatus(str, Enum):
    LICENSED = "LICENSED"
    BLOCKED = "BLOCKED"
    CANNOT_CHECK = "CANNOT_CHECK"


DEFAULT_LICENSES: Mapping[str, frozenset[EpistemicAction]] = {
    "evidence": frozenset({EpistemicAction.GATHER_EVIDENCE}),
    "execution": frozenset({EpistemicAction.RETRY_EXECUTION}),
    "representation": frozenset({EpistemicAction.REVISE_REPRESENTATION}),
    "formulation": frozenset({EpistemicAction.REFRAME_FORMULATION}),
    "search_universe": frozenset({EpistemicAction.EXPAND_SEARCH_UNIVERSE}),
    "method": frozenset({EpistemicAction.CHANGE_METHOD}),
}


@dataclass(frozen=True)
class P1DiagnosisReceipt:
    requested_action: EpistemicAction
    status: P1DecisionStatus
    reason_code: str
    diagnosable: bool
    best_responsibility: str | None
    best_probability: float | None
    recommended_probe_id: str | None
    posterior: tuple[tuple[str, float], ...]
    information_gain: tuple[tuple[str, float], ...]
    observations: tuple[tuple[str, bool], ...]
    receipt_digest: str

    def unsigned_payload(self) -> dict[str, object]:
        return {
            "receipt_version": "ORION_P1_DIAGNOSIS_RECEIPT_V2",
            "requested_action": self.requested_action.value,
            "status": self.status.value,
            "reason_code": self.reason_code,
            "diagnosable": self.diagnosable,
            "best_responsibility": self.best_responsibility,
            "best_probability": self.best_probability,
            "recommended_probe_id": self.recommended_probe_id,
            "posterior": {key: value for key, value in self.posterior},
            "information_gain": {key: value for key, value in self.information_gain},
            "observations": [{"probe_id": key, "positive": value} for key, value in self.observations],
            "authority_scope": "EPISTEMIC_ACTION_ONLY",
        }

    def to_payload(self) -> dict[str, object]:
        payload = self.unsigned_payload()
        payload["receipt_digest"] = self.receipt_digest
        return payload

    def verify(self) -> None:
        if content_digest(self.unsigned_payload()) != self.receipt_digest:
            raise ValueError("P1 diagnosis receipt digest mismatch")


def diagnose_and_license(
    hypotheses: Sequence[ResponsibilityHypothesis],
    probes: Sequence[DiagnosticProbe],
    *,
    requested_action: EpistemicAction,
    observations: Sequence[tuple[str, bool]] = (),
    threshold: float = 0.8,
    licenses: Mapping[str, frozenset[EpistemicAction]] = DEFAULT_LICENSES,
    cost_weight: float = 0.0,
    risk_weight: float = 0.0,
) -> P1DiagnosisReceipt:
    if not 0.5 <= threshold <= 1.0:
        raise ValueError("threshold must be in [0.5,1]")
    names = [hypothesis.name for hypothesis in hypotheses]
    if len(names) != len(set(names)):
        raise ValueError("responsibility hypothesis names must be unique")
    probe_by_id = {probe.probe_id: probe for probe in probes}
    if len(probe_by_id) != len(probes):
        raise ValueError("probe ids must be unique")
    observation_ids = [probe_id for probe_id, _ in observations]
    if len(observation_ids) != len(set(observation_ids)):
        raise ValueError("the same diagnostic probe cannot be double-counted")

    diagnoser = ResponsibilityDiagnoser(hypotheses, cost_weight=cost_weight, risk_weight=risk_weight)
    gains_before = tuple(sorted((probe.probe_id, diagnoser.information_gain(probe)) for probe in probes))
    diagnosable = any(gain > 1e-12 for _, gain in gains_before)
    if not diagnosable:
        status = P1DecisionStatus.CANNOT_CHECK
        reason = "NON_DIAGNOSABLE"
        best_name = None
        best_probability = None
        recommended = None
    else:
        for probe_id, positive in observations:
            if probe_id not in probe_by_id:
                raise ValueError(f"unknown diagnostic probe: {probe_id}")
            diagnoser.observe(probe_by_id[probe_id], positive=positive)
        recommended_probe = diagnoser.choose_probe(probes)
        recommended = recommended_probe.probe_id if recommended_probe is not None else None
        best_name, best_probability = diagnoser.best_hypothesis()
        if not observations:
            status = P1DecisionStatus.CANNOT_CHECK
            reason = "PROBE_REQUIRED"
        elif best_probability < threshold:
            status = P1DecisionStatus.CANNOT_CHECK
            reason = "LOW_POSTERIOR_CONFIDENCE"
        elif requested_action not in licenses.get(best_name, frozenset()):
            status = P1DecisionStatus.BLOCKED
            reason = "RESPONSIBILITY_SCOPE_MISMATCH"
        else:
            status = P1DecisionStatus.LICENSED
            reason = "RESPONSIBILITY_SUPPORTED_AND_SCOPED"

    posterior = tuple(sorted(diagnoser.posterior.items()))
    unsigned = {
        "receipt_version": "ORION_P1_DIAGNOSIS_RECEIPT_V2",
        "requested_action": requested_action.value,
        "status": status.value,
        "reason_code": reason,
        "diagnosable": diagnosable,
        "best_responsibility": best_name,
        "best_probability": best_probability,
        "recommended_probe_id": recommended,
        "posterior": {key: value for key, value in posterior},
        "information_gain": {key: value for key, value in gains_before},
        "observations": [{"probe_id": key, "positive": value} for key, value in observations],
        "authority_scope": "EPISTEMIC_ACTION_ONLY",
    }
    return P1DiagnosisReceipt(
        requested_action=requested_action,
        status=status,
        reason_code=reason,
        diagnosable=diagnosable,
        best_responsibility=best_name,
        best_probability=best_probability,
        recommended_probe_id=recommended,
        posterior=posterior,
        information_gain=gains_before,
        observations=tuple(observations),
        receipt_digest=content_digest(unsigned),
    )
