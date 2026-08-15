from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from orion.self_orion.change_control import ChangeControlResult, ChangeControlVerdict


class VariantStatus(str, Enum):
    INCUMBENT = "INCUMBENT"
    CHALLENGER = "CHALLENGER"
    ASSURED = "ASSURED"
    REJECTED = "REJECTED"
    RETIRED = "RETIRED"


@dataclass(frozen=True)
class OrionVariant:
    variant_id: str
    revision_hash: str
    parent_ids: tuple[str, ...]
    capability_tags: tuple[str, ...]
    resource_profile: tuple[tuple[str, float], ...]
    created_by_episode_ids: tuple[str, ...]
    status: VariantStatus
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.variant_id.strip() or not self.revision_hash.strip():
            raise ValueError("variant identity/revision are required")
        if len(self.revision_hash) != 64 or any(ch not in "0123456789abcdef" for ch in self.revision_hash):
            raise ValueError("variant revision hash must be SHA-256")
        names = [name for name, _ in self.resource_profile]
        if len(set(names)) != len(names) or any(value < 0 for _, value in self.resource_profile):
            raise ValueError("variant resource profile must be unique and non-negative")


@dataclass(frozen=True)
class EvolutionTrialRecord:
    trial_id: str
    parent_id: str
    child_id: str
    proposal_id: str
    verdict: ChangeControlVerdict
    development_delta: float
    fresh_assurance_delta: float
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class EvolutionArchive:
    variants: tuple[OrionVariant, ...]
    trials: tuple[EvolutionTrialRecord, ...] = ()
    incumbent_id: str = ""


@dataclass(frozen=True)
class HostPromotionRecommendation:
    variant_id: str
    incumbent_id: str
    supporting_trial_ids: tuple[str, ...]
    reasons: tuple[str, ...]

    @property
    def authorizes_promotion(self) -> bool:
        return False


def initialize_evolution_archive(incumbent: OrionVariant) -> EvolutionArchive:
    normalized = incumbent if incumbent.status is VariantStatus.INCUMBENT else replace(incumbent, status=VariantStatus.INCUMBENT)
    return EvolutionArchive((normalized,), (), normalized.variant_id)


def register_challenger(archive: EvolutionArchive, challenger: OrionVariant) -> EvolutionArchive:
    if any(item.variant_id == challenger.variant_id for item in archive.variants):
        raise ValueError("duplicate variant id")
    known = {item.variant_id for item in archive.variants}
    if not challenger.parent_ids or not set(challenger.parent_ids).issubset(known):
        raise ValueError("challenger must reference registered parent variants")
    return EvolutionArchive(
        archive.variants + (replace(challenger, status=VariantStatus.CHALLENGER),),
        archive.trials,
        archive.incumbent_id,
    )


def record_change_control_result(
    archive: EvolutionArchive,
    *,
    trial_id: str,
    parent_variant_id: str,
    child_variant_id: str,
    result: ChangeControlResult,
) -> EvolutionArchive:
    if not trial_id.strip():
        raise ValueError("trial id is required")
    if any(item.trial_id == trial_id for item in archive.trials):
        raise ValueError("duplicate evolution trial id")
    by_id = {item.variant_id: item for item in archive.variants}
    child = by_id.get(child_variant_id)
    if child is None or parent_variant_id not in child.parent_ids:
        raise ValueError("trial child/parent must match a registered challenger lineage")
    expected_revision = result.execution.candidate_revision_hash
    if child.revision_hash != expected_revision:
        raise ValueError("candidate execution revision does not match registered challenger")
    next_status = {
        ChangeControlVerdict.REJECT: VariantStatus.REJECTED,
        ChangeControlVerdict.CANDIDATE_ONLY: VariantStatus.CHALLENGER,
        ChangeControlVerdict.RECOMMEND_HOST_PROMOTION: VariantStatus.ASSURED,
    }[result.verdict]
    variants = tuple(
        replace(item, status=next_status) if item.variant_id == child_variant_id else item
        for item in archive.variants
    )
    trial = EvolutionTrialRecord(
        trial_id=trial_id,
        parent_id=parent_variant_id,
        child_id=child_variant_id,
        proposal_id=result.proposal.proposal_id,
        verdict=result.verdict,
        development_delta=result.assurance.development_delta,
        fresh_assurance_delta=result.assurance.fresh_assurance_delta,
        reasons=result.reasons,
    )
    return EvolutionArchive(variants, archive.trials + (trial,), archive.incumbent_id)


def recommend_host_promotion(archive: EvolutionArchive, variant_id: str) -> HostPromotionRecommendation:
    target = next((item for item in archive.variants if item.variant_id == variant_id), None)
    if target is None:
        raise ValueError("variant does not exist")
    supporting = tuple(
        item.trial_id
        for item in archive.trials
        if item.child_id == variant_id and item.verdict is ChangeControlVerdict.RECOMMEND_HOST_PROMOTION
    )
    reasons: list[str] = []
    if target.status is not VariantStatus.ASSURED:
        reasons.append("variant_not_assured")
    if not supporting:
        reasons.append("no_protected_assurance_trial")
    if variant_id == archive.incumbent_id:
        reasons.append("variant_already_incumbent")
    return HostPromotionRecommendation(
        variant_id=variant_id,
        incumbent_id=archive.incumbent_id,
        supporting_trial_ids=supporting,
        reasons=tuple(reasons) if reasons else ("assured challenger may be presented to an external host/governance promotion action",),
    )


__all__ = [
    "EvolutionArchive",
    "EvolutionTrialRecord",
    "HostPromotionRecommendation",
    "OrionVariant",
    "VariantStatus",
    "initialize_evolution_archive",
    "record_change_control_result",
    "recommend_host_promotion",
    "register_challenger",
]
