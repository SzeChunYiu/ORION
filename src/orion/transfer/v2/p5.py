from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Mapping

from ..staging import CandidateRecord, CandidateVerdict, MultiStageCandidateGate, Stage, StageResult, StageVerdict
from .canonical import content_digest


def stage_result_payload(result: StageResult) -> dict[str, object]:
    return {
        "stage": result.stage.value,
        "verdict": result.verdict.value,
        "score_delta": result.score_delta,
        "cost": result.cost,
        "harmful": result.harmful,
    }


def candidate_record_payload(record: CandidateRecord) -> dict[str, object]:
    if not record.candidate_id:
        raise ValueError("candidate_id must be non-empty")
    return {
        "candidate_id": record.candidate_id,
        "results": {
            stage.value: stage_result_payload(result)
            for stage, result in sorted(record.results.items(), key=lambda item: item[0].value)
        },
        "total_cost": record.total_cost,
    }


class AppendOnlyCandidateHistory:
    """Retains every unique candidate-state revision; there is intentionally no delete API."""

    def __init__(self) -> None:
        self._history: dict[str, list[tuple[str, dict[str, object]]]] = {}

    def append(self, record: CandidateRecord) -> str:
        payload = candidate_record_payload(record)
        digest = content_digest(payload)
        revisions = self._history.setdefault(record.candidate_id, [])
        if not any(prior_digest == digest for prior_digest, _ in revisions):
            revisions.append((digest, deepcopy(payload)))
        return digest

    def revisions(self, candidate_id: str) -> tuple[tuple[str, Mapping[str, object]], ...]:
        return tuple((digest, deepcopy(payload)) for digest, payload in self._history.get(candidate_id, ()))

    def to_payload(self) -> dict[str, object]:
        return {
            candidate_id: [
                {"digest": digest, "payload": deepcopy(payload)}
                for digest, payload in revisions
            ]
            for candidate_id, revisions in sorted(self._history.items())
        }

    @property
    def digest(self) -> str:
        return content_digest(self.to_payload())


@dataclass(frozen=True)
class P5GateReceipt:
    candidate_id: str
    candidate_digest: str
    archive_digest: str
    verdict: CandidateVerdict
    failed_stages: tuple[str, ...]
    harmful_stages: tuple[str, ...]
    cannot_check_stages: tuple[str, ...]
    missing_stages: tuple[str, ...]
    terminal_authority: str
    receipt_digest: str

    def __post_init__(self) -> None:
        if self.terminal_authority != "HOST_ONLY_RECOMMENDATION":
            raise ValueError("P5 gate cannot grant self-promotion authority")

    def unsigned_payload(self) -> dict[str, object]:
        return {
            "receipt_version": "ORION_P5_GATE_RECEIPT_V2",
            "candidate_id": self.candidate_id,
            "candidate_digest": self.candidate_digest,
            "archive_digest": self.archive_digest,
            "verdict": self.verdict.value,
            "failed_stages": list(self.failed_stages),
            "harmful_stages": list(self.harmful_stages),
            "cannot_check_stages": list(self.cannot_check_stages),
            "missing_stages": list(self.missing_stages),
            "terminal_authority": self.terminal_authority,
        }

    def to_payload(self) -> dict[str, object]:
        payload = self.unsigned_payload()
        payload["receipt_digest"] = self.receipt_digest
        return payload

    def verify(self) -> None:
        if content_digest(self.unsigned_payload()) != self.receipt_digest:
            raise ValueError("P5 gate receipt digest mismatch")


def evaluate_and_archive(
    record: CandidateRecord,
    history: AppendOnlyCandidateHistory,
) -> P5GateReceipt:
    gate = MultiStageCandidateGate()
    verdict = gate.evaluate(record)
    candidate_digest = history.append(record)
    failed = tuple(sorted(result.stage.value for result in record.results.values() if result.verdict is StageVerdict.FAIL))
    harmful = tuple(sorted(result.stage.value for result in record.results.values() if result.harmful))
    cannot_check = tuple(sorted(result.stage.value for result in record.results.values() if result.verdict is StageVerdict.CANNOT_CHECK))
    missing = tuple(stage.value for stage in gate.required_stages if stage not in record.results)
    unsigned = {
        "receipt_version": "ORION_P5_GATE_RECEIPT_V2",
        "candidate_id": record.candidate_id,
        "candidate_digest": candidate_digest,
        "archive_digest": history.digest,
        "verdict": verdict.value,
        "failed_stages": list(failed),
        "harmful_stages": list(harmful),
        "cannot_check_stages": list(cannot_check),
        "missing_stages": list(missing),
        "terminal_authority": "HOST_ONLY_RECOMMENDATION",
    }
    return P5GateReceipt(
        candidate_id=record.candidate_id,
        candidate_digest=candidate_digest,
        archive_digest=history.digest,
        verdict=verdict,
        failed_stages=failed,
        harmful_stages=harmful,
        cannot_check_stages=cannot_check,
        missing_stages=missing,
        terminal_authority="HOST_ONLY_RECOMMENDATION",
        receipt_digest=content_digest(unsigned),
    )
