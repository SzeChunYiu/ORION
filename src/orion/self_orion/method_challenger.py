"""Fail-closed governance records for P5 method-space challengers.

A method challenger is an inspectable candidate, not an invention claim or an
adoption authority.  This module deliberately keeps candidate generation,
assurance, and host disposition separate: a candidate can only receive a host
recommendation after the complete non-compensatory ladder has been evidenced.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


SCHEMA_VERSION = "orion.p5.method-challenger.v1"


class MethodEvolutionStage(str, Enum):
    DIAGNOSE = "DIAGNOSE"
    SEARCH_ABSORB = "SEARCH/ABSORB"
    CHALLENGER = "CHALLENGER"
    ISOLATED_RUN = "ISOLATED_RUN"
    REPLAY = "REPLAY"
    FRESH = "FRESH"
    PROTECTED = "PROTECTED"


class MethodEvidenceStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    HARMFUL = "HARMFUL"
    MISSING = "MISSING"
    BLOCK = "BLOCK"
    NOT_RUN = "NOT_RUN"


class HostDisposition(str, Enum):
    RECOMMEND = "RECOMMEND_HOST_DISPOSITION"
    REJECT = "REJECT"
    BLOCK = "CANNOT_CHECK/BLOCK"
    CANDIDATE_ONLY = "CANDIDATE_ONLY"


@dataclass(frozen=True)
class MethodStageEvidence:
    stage: MethodEvolutionStage
    evidence_id: str
    status: MethodEvidenceStatus
    split_id: str = ""
    evaluator_id: str = ""
    result_hash: str = ""

    def __post_init__(self) -> None:
        if not self.evidence_id.strip():
            raise ValueError("method-stage evidence id is required")
        if self.status is MethodEvidenceStatus.PASS and not self.result_hash.strip():
            raise ValueError("passing method-stage evidence requires a result identity")
        if self.stage in (MethodEvolutionStage.FRESH, MethodEvolutionStage.PROTECTED):
            if not self.split_id.strip() or not self.evaluator_id.strip():
                raise ValueError("fresh/protected evidence requires split and evaluator identities")


@dataclass(frozen=True)
class MethodChallenger:
    """Versioned method candidate whose adoption authority remains external."""

    challenger_id: str
    subject_revision: str
    generating_failure_ids: tuple[str, ...]
    ordinary_causes_challenged: tuple[str, ...]
    known_method_routes: tuple[str, ...]
    route_inadequacy_reasons: tuple[str, ...]
    assimilated_donor_mechanisms: tuple[str, ...]
    structural_edit: str
    discriminator_prediction: str
    stages: tuple[MethodStageEvidence, ...]
    negative_history_ids: tuple[str, ...]
    host_disposition: HostDisposition = HostDisposition.CANDIDATE_ONLY
    adoption_authority: str = "EXTERNAL_HOST"
    schema_version: str = SCHEMA_VERSION
    candidate_controls_authority: bool = False

    def __post_init__(self) -> None:
        if not self.challenger_id.strip() or not self.subject_revision.strip():
            raise ValueError("challenger and subject identities are required")
        if len(self.subject_revision) != 64 or any(c not in "0123456789abcdef" for c in self.subject_revision):
            raise ValueError("subject revision must be SHA-256")
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError("unsupported method challenger schema")
        required = (
            (self.generating_failure_ids, "generating failure records"),
            (self.ordinary_causes_challenged, "ordinary-cause challenge records"),
            (self.known_method_routes, "known method search routes"),
            (self.route_inadequacy_reasons, "known method inadequacy reasons"),
            (self.assimilated_donor_mechanisms, "donor assimilation records"),
            (self.negative_history_ids, "negative history"),
        )
        if any(not values for values, _ in required):
            missing = next(label for values, label in required if not values)
            raise ValueError(f"{missing} are required")
        if not self.structural_edit.strip() or not self.discriminator_prediction.strip():
            raise ValueError("structural edit and frozen discriminator prediction are required")
        if self.adoption_authority != "EXTERNAL_HOST":
            raise ValueError("method adoption authority must remain external to the candidate")
        if self.candidate_controls_authority:
            raise ValueError("candidate cannot control adoption authority; not authoritative")
        if self.host_disposition is not HostDisposition.CANDIDATE_ONLY:
            raise ValueError("candidate host disposition is not authoritative")
        seen = {stage.stage for stage in self.stages}
        if len(seen) != len(self.stages):
            raise ValueError("method stages must be unique")

    @property
    def empirical_authority(self) -> str:
        return "NONE"

    @property
    def can_mutate_method_registry(self) -> bool:
        return False


_EXPECTED_STAGES = tuple(MethodEvolutionStage)


def assess_method_challenger(challenger: MethodChallenger) -> tuple[HostDisposition, tuple[str, ...]]:
    """Return the only disposition justified by the immutable candidate record.

    Harm and missing protected evidence are evaluated before gains.  Thus a
    positive replay cannot compensate for fresh harm, and no stage can be
    skipped by a candidate claiming success at a later stage.
    """

    by_stage = {item.stage: item for item in challenger.stages}
    reasons: list[str] = []
    missing = tuple(stage.value for stage in _EXPECTED_STAGES if stage not in by_stage)
    if missing:
        reasons.append("missing_stages:" + ",".join(missing))
    harmful = tuple(item.stage.value for item in challenger.stages if item.status is MethodEvidenceStatus.HARMFUL)
    if harmful:
        reasons.append("harmful_outcome_precedence:" + ",".join(harmful))
    failed = tuple(item.stage.value for item in challenger.stages if item.status in (MethodEvidenceStatus.FAIL, MethodEvidenceStatus.BLOCK))
    if failed:
        reasons.append("failed_stage:" + ",".join(failed))
    unavailable = tuple(item.stage.value for item in challenger.stages if item.status in (MethodEvidenceStatus.MISSING, MethodEvidenceStatus.NOT_RUN))
    if unavailable:
        reasons.append("unavailable_stage:" + ",".join(unavailable))
    if challenger.host_disposition is not HostDisposition.CANDIDATE_ONLY:
        reasons.append("candidate_disposition_is_not_authoritative")
    if reasons:
        if harmful or failed:
            return HostDisposition.REJECT, tuple(reasons)
        return HostDisposition.BLOCK, tuple(reasons)
    return HostDisposition.RECOMMEND, ("complete protected method-evolution ladder; host disposition remains external",)


def validate_method_challenger(challenger: MethodChallenger) -> None:
    """Raise on records that cannot be admitted to the P5 challenger archive."""

    disposition, reasons = assess_method_challenger(challenger)
    if disposition is not HostDisposition.RECOMMEND:
        raise ValueError("method challenger is not admissible: " + "; ".join(reasons))


__all__ = [
    "HostDisposition",
    "MethodChallenger",
    "MethodEvidenceStatus",
    "MethodEvolutionStage",
    "MethodStageEvidence",
    "SCHEMA_VERSION",
    "assess_method_challenger",
    "validate_method_challenger",
]
