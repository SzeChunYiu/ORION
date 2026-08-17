"""P5.causal-repair.v2 acceptance-doctrine scaffolding.

This gate is local engineering infrastructure. It cannot self-merge, cannot
self-certify, and cannot convert missing fresh/protected evidence into
improvement. Replay gain cannot compensate fresh harm.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


PROTOCOL_ID = "P5.causal-repair.v2"
LIVE_CAMPAIGN_ENV_KEYS = ("GLM_API_KEY", "ANTHROPIC_API_KEY")


def live_campaign_preflight() -> dict[str, str]:
    """Report whether a live attribution/repair campaign can run.

    Never returns secret values. Absence is CANNOT_CHECK, not a negative result.
    """

    import os

    present = [key for key in LIVE_CAMPAIGN_ENV_KEYS if os.environ.get(key)]
    if present:
        return {"status": "CREDENTIALS_PRESENT", "authority": "CANNOT_CHECK"}
    return {"status": "CANNOT_CHECK", "authority": "CANNOT_CHECK"}



class CausalRepairStage(str, Enum):
    STATIC = "STATIC"
    DIAGNOSE = "DIAGNOSE"
    DISCRIMINATE = "DISCRIMINATE"
    CANDIDATE = "CANDIDATE"
    REPLAY = "REPLAY"
    FRESH = "FRESH"
    PROTECTED = "PROTECTED"


class StageVerdict(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    CANNOT_CHECK = "CANNOT_CHECK"


class CausalRepairVerdict(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    BLOCK = "BLOCK"
    REJECT = "REJECT"
    CANNOT_CHECK = "CANNOT_CHECK"
    RECOMMEND_HOST_PROMOTION = "RECOMMEND_HOST_PROMOTION"


class ChangeClass(str, Enum):
    RETRIEVAL_ROUTING_REPAIR = "RETRIEVAL_ROUTING_REPAIR"
    IMPLEMENTATION_REPAIR = "IMPLEMENTATION_REPAIR"
    ENVIRONMENT_TOOL_ACCOMMODATION = "ENVIRONMENT_TOOL_ACCOMMODATION"
    REPRESENTATION_REPAIR = "REPRESENTATION_REPAIR"
    MEASUREMENT_SPECIFICATION_REPAIR = "MEASUREMENT_SPECIFICATION_REPAIR"
    METHOD_BASIS_CHANGE = "METHOD_BASIS_CHANGE"


@dataclass(frozen=True)
class StageObservation:
    stage: CausalRepairStage
    verdict: StageVerdict
    score_delta: float = 0.0
    harmful: bool = False


@dataclass
class CausalRepairRecord:
    candidate_id: str
    change_class: ChangeClass
    candidate_fingerprint: str
    discriminator_evidence_bound: bool = False
    lower_causes_ruled_out: bool = False
    greedy_replay_acceptance: bool = False
    observations: dict[CausalRepairStage, StageObservation] = field(default_factory=dict)

    def record(self, observation: StageObservation) -> None:
        if observation.stage in self.observations:
            raise ValueError(f"stage {observation.stage.value} already recorded")
        self.observations[observation.stage] = observation


@dataclass(frozen=True)
class CausalRepairReceipt:
    candidate_id: str
    verdict: CausalRepairVerdict
    blockers: tuple[str, ...]
    missing_stages: tuple[str, ...]
    harmful_stages: tuple[str, ...]
    failed_stages: tuple[str, ...]
    cannot_check_stages: tuple[str, ...]
    terminal_authority: str
    self_merge_authority: bool

    def __post_init__(self) -> None:
        if self.terminal_authority != "HOST_ONLY_RECOMMENDATION":
            raise ValueError("causal-repair receipts cannot grant self-promotion authority")
        if self.self_merge_authority:
            raise ValueError("causal-repair receipts cannot grant self-merge authority")


class NegativeHistory:
    """Append-only store of rejected, blocked, harmful, and null fingerprints."""

    def __init__(self) -> None:
        self._fingerprints: list[str] = []
        self._candidate_ids: list[str] = []

    def retain(self, record: CausalRepairRecord) -> None:
        self._fingerprints.append(record.candidate_fingerprint)
        self._candidate_ids.append(record.candidate_id)

    def contains_fingerprint(self, fingerprint: str) -> bool:
        return fingerprint in self._fingerprints


class CausalRepairGate:
    required_stages = (
        CausalRepairStage.STATIC,
        CausalRepairStage.DIAGNOSE,
        CausalRepairStage.DISCRIMINATE,
        CausalRepairStage.CANDIDATE,
        CausalRepairStage.REPLAY,
        CausalRepairStage.FRESH,
        CausalRepairStage.PROTECTED,
    )

    def evaluate(self, record: CausalRepairRecord, history: NegativeHistory) -> CausalRepairReceipt:
        missing = tuple(stage.value for stage in self.required_stages if stage not in record.observations)
        harmful = tuple(
            sorted(obs.stage.value for obs in record.observations.values() if obs.harmful)
        )
        failed = tuple(
            sorted(obs.stage.value for obs in record.observations.values() if obs.verdict is StageVerdict.FAIL)
        )
        cannot_check = tuple(
            sorted(
                obs.stage.value
                for obs in record.observations.values()
                if obs.verdict is StageVerdict.CANNOT_CHECK
            )
        )
        blockers: list[str] = []
        if history.contains_fingerprint(record.candidate_fingerprint):
            blockers.append("negative_history_recurrence")
        if record.greedy_replay_acceptance:
            blockers.append("greedy_replay_only")
        if CausalRepairStage.FRESH not in record.observations:
            blockers.append("missing_fresh_transfer")
        if CausalRepairStage.PROTECTED not in record.observations:
            blockers.append("missing_protected_evaluator")
        if not record.discriminator_evidence_bound:
            blockers.append("discriminator_not_evidence_bound")
        if record.change_class is ChangeClass.METHOD_BASIS_CHANGE and not record.lower_causes_ruled_out:
            blockers.append("lower_causes_not_ruled_out")
        if record.change_class is ChangeClass.MEASUREMENT_SPECIFICATION_REPAIR:
            blockers.append("measurement_specification_requires_host_authority")

        if harmful or failed:
            verdict = CausalRepairVerdict.REJECT
        elif blockers:
            verdict = CausalRepairVerdict.BLOCK
        elif cannot_check:
            verdict = CausalRepairVerdict.CANNOT_CHECK
        elif missing:
            verdict = CausalRepairVerdict.IN_PROGRESS
        else:
            verdict = CausalRepairVerdict.RECOMMEND_HOST_PROMOTION

        if verdict is not CausalRepairVerdict.RECOMMEND_HOST_PROMOTION:
            history.retain(record)

        return CausalRepairReceipt(
            candidate_id=record.candidate_id,
            verdict=verdict,
            blockers=tuple(blockers),
            missing_stages=missing,
            harmful_stages=harmful,
            failed_stages=failed,
            cannot_check_stages=cannot_check,
            terminal_authority="HOST_ONLY_RECOMMENDATION",
            self_merge_authority=False,
        )
