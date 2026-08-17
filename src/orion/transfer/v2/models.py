from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from ..types import AlgorithmCell, ProblemSignature, TransferAssessment, TransferStatus, assess_transfer
from .canonical import content_digest

RECEIPT_VERSION = "ORION_TRANSFER_RECEIPT_V2"


def problem_signature_payload(signature: ProblemSignature) -> dict[str, object]:
    return {
        "problem_id": signature.problem_id,
        "source_domain": signature.source_domain,
        "hidden_state": signature.hidden_state,
        "observability": signature.observability,
        "actions": sorted(signature.actions),
        "ground_truth": signature.ground_truth,
        "dependence": signature.dependence,
        "authority_risk": signature.authority_risk,
        "nonstationarity": signature.nonstationarity,
        "reversibility": signature.reversibility,
    }


def problem_signature_from_payload(payload: Mapping[str, object]) -> ProblemSignature:
    required = {
        "problem_id", "source_domain", "hidden_state", "observability", "actions",
        "ground_truth", "dependence", "authority_risk", "nonstationarity", "reversibility",
    }
    if set(payload) != required:
        raise ValueError(f"problem signature fields mismatch: {sorted(set(payload) ^ required)}")
    actions = payload["actions"]
    if not isinstance(actions, list) or not all(isinstance(v, str) for v in actions):
        raise ValueError("actions must be a list of strings")
    return ProblemSignature(
        problem_id=str(payload["problem_id"]),
        source_domain=str(payload["source_domain"]),
        hidden_state=str(payload["hidden_state"]),
        observability=str(payload["observability"]),
        actions=frozenset(actions),
        ground_truth=str(payload["ground_truth"]),
        dependence=float(payload["dependence"]),
        authority_risk=float(payload["authority_risk"]),
        nonstationarity=float(payload["nonstationarity"]),
        reversibility=float(payload["reversibility"]),
    )


def algorithm_cell_payload(cell: AlgorithmCell) -> dict[str, object]:
    return {
        "cell_id": cell.cell_id,
        "source_signature": problem_signature_payload(cell.source_signature),
        "mechanism": cell.mechanism,
        "assumptions": list(cell.assumptions),
        "invariants": list(cell.invariants),
        "stopping_rule": cell.stopping_rule,
        "failure_modes": list(cell.failure_modes),
        "falsifiers": list(cell.falsifiers),
    }


def algorithm_cell_from_payload(payload: Mapping[str, object]) -> AlgorithmCell:
    required = {
        "cell_id", "source_signature", "mechanism", "assumptions", "invariants",
        "stopping_rule", "failure_modes", "falsifiers",
    }
    if set(payload) != required:
        raise ValueError(f"algorithm cell fields mismatch: {sorted(set(payload) ^ required)}")
    source = payload["source_signature"]
    if not isinstance(source, Mapping):
        raise ValueError("source_signature must be an object")
    sequence_fields: dict[str, tuple[str, ...]] = {}
    for name in ("assumptions", "invariants", "failure_modes", "falsifiers"):
        raw = payload[name]
        if not isinstance(raw, list) or not all(isinstance(v, str) for v in raw):
            raise ValueError(f"{name} must be a list of strings")
        if len(raw) != len(set(raw)):
            raise ValueError(f"{name} must not contain duplicates")
        sequence_fields[name] = tuple(raw)
    return AlgorithmCell(
        cell_id=str(payload["cell_id"]),
        source_signature=problem_signature_from_payload(source),
        mechanism=str(payload["mechanism"]),
        assumptions=sequence_fields["assumptions"],
        invariants=sequence_fields["invariants"],
        stopping_rule=str(payload["stopping_rule"]),
        failure_modes=sequence_fields["failure_modes"],
        falsifiers=sequence_fields["falsifiers"],
    )


def _declared_evidence_payload(
    cell: AlgorithmCell,
    assumption_truth: Mapping[str, bool | None],
    falsifier_results: Mapping[str, bool | None],
    provenance: Sequence[str],
) -> dict[str, object]:
    extra_assumptions = set(assumption_truth) - set(cell.assumptions)
    extra_falsifiers = set(falsifier_results) - set(cell.falsifiers)
    if extra_assumptions:
        raise ValueError(f"undeclared assumption evidence: {sorted(extra_assumptions)}")
    if extra_falsifiers:
        raise ValueError(f"undeclared falsifier evidence: {sorted(extra_falsifiers)}")
    if any(v not in (True, False, None) for v in assumption_truth.values()):
        raise ValueError("assumption evidence values must be true/false/null")
    if any(v not in (True, False, None) for v in falsifier_results.values()):
        raise ValueError("falsifier evidence values must be true/false/null")
    if not all(isinstance(item, str) and item for item in provenance):
        raise ValueError("provenance entries must be non-empty strings")
    return {
        "cell_id": cell.cell_id,
        "assumptions": {name: assumption_truth.get(name) for name in cell.assumptions},
        "falsifiers": {name: falsifier_results.get(name) for name in cell.falsifiers},
        "provenance": sorted(set(provenance)),
    }


def _reason_codes(assessment: TransferAssessment) -> tuple[str, ...]:
    reasons: list[str] = []
    reasons.extend(f"ASSUMPTION_FALSE:{name}" for name in assessment.failed_assumptions)
    reasons.extend(f"ASSUMPTION_UNKNOWN:{name}" for name in assessment.missing_assumptions)
    reasons.extend(f"FALSIFIER_FAILED:{name}" for name in assessment.failed_falsifiers)
    reasons.extend(f"FALSIFIER_UNKNOWN:{name}" for name in assessment.unknown_falsifiers)
    if not reasons and assessment.status is TransferStatus.ADMISSIBLE:
        reasons.append("ALL_DECLARED_CONDITIONS_PASSED")
    return tuple(reasons)


@dataclass(frozen=True)
class TransferReceipt:
    target_id: str
    target_digest: str
    cell_id: str
    cell_digest: str
    evidence_digest: str
    source_domain: str
    mechanism: str
    status: TransferStatus
    structural_score: float
    reason_codes: tuple[str, ...]
    provenance: tuple[str, ...]
    receipt_digest: str
    receipt_version: str = RECEIPT_VERSION

    def unsigned_payload(self) -> dict[str, object]:
        return {
            "receipt_version": self.receipt_version,
            "target_id": self.target_id,
            "target_digest": self.target_digest,
            "cell_id": self.cell_id,
            "cell_digest": self.cell_digest,
            "evidence_digest": self.evidence_digest,
            "source_domain": self.source_domain,
            "mechanism": self.mechanism,
            "status": self.status.value,
            "structural_score": self.structural_score,
            "reason_codes": list(self.reason_codes),
            "provenance": list(self.provenance),
        }

    def to_payload(self) -> dict[str, object]:
        payload = self.unsigned_payload()
        payload["receipt_digest"] = self.receipt_digest
        return payload

    def verify(self) -> None:
        if self.receipt_version != RECEIPT_VERSION:
            raise ValueError("unsupported transfer receipt version")
        expected = content_digest(self.unsigned_payload())
        if expected != self.receipt_digest:
            raise ValueError("transfer receipt digest mismatch")


def build_transfer_receipt(
    target: ProblemSignature,
    cell: AlgorithmCell,
    *,
    assumption_truth: Mapping[str, bool | None],
    falsifier_results: Mapping[str, bool | None],
    provenance: Sequence[str] = (),
) -> TransferReceipt:
    evidence = _declared_evidence_payload(cell, assumption_truth, falsifier_results, provenance)
    assessment = assess_transfer(
        target,
        cell,
        assumption_truth=evidence["assumptions"],  # type: ignore[arg-type]
        falsifier_results=evidence["falsifiers"],  # type: ignore[arg-type]
    )
    unsigned = {
        "receipt_version": RECEIPT_VERSION,
        "target_id": target.problem_id,
        "target_digest": content_digest(problem_signature_payload(target)),
        "cell_id": cell.cell_id,
        "cell_digest": content_digest(algorithm_cell_payload(cell)),
        "evidence_digest": content_digest(evidence),
        "source_domain": cell.source_signature.source_domain,
        "mechanism": cell.mechanism,
        "status": assessment.status.value,
        "structural_score": assessment.structural_score,
        "reason_codes": list(_reason_codes(assessment)),
        "provenance": evidence["provenance"],
    }
    return TransferReceipt(
        target_id=target.problem_id,
        target_digest=unsigned["target_digest"],  # type: ignore[arg-type]
        cell_id=cell.cell_id,
        cell_digest=unsigned["cell_digest"],  # type: ignore[arg-type]
        evidence_digest=unsigned["evidence_digest"],  # type: ignore[arg-type]
        source_domain=cell.source_signature.source_domain,
        mechanism=cell.mechanism,
        status=assessment.status,
        structural_score=assessment.structural_score,
        reason_codes=_reason_codes(assessment),
        provenance=tuple(evidence["provenance"]),  # type: ignore[arg-type]
        receipt_digest=content_digest(unsigned),
    )
