from __future__ import annotations

import json
from dataclasses import dataclass, replace
from enum import Enum

from orion.self_orion.change_control import ChangeControlResult, ChangeControlVerdict
from orion.self_orion.method_challenger import (
    HostDisposition,
    MethodChallenger,
    assess_method_challenger,
)


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
    challengers: tuple[MethodChallenger, ...] = ()
    challenger_dispositions: tuple[tuple[str, HostDisposition], ...] = ()
    harmful_method_classes: tuple[tuple[str, tuple[str, ...]], ...] = ()


def changelog_recorded(archive: EvolutionArchive, challenger_id: str) -> bool:
    return any(record_id == challenger_id for record_id, _ in archive.challenger_dispositions)


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
    return EvolutionArchive((normalized,), (), normalized.variant_id, harmful_method_classes=())


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
        archive.challengers,
        archive.challenger_dispositions,
        archive.harmful_method_classes,
    )


def register_method_challenger(archive: EvolutionArchive, challenger: MethodChallenger) -> EvolutionArchive:
    """Register a method-level challenger candidate in the evolution archive.

    The challenger is validated for admissible structure; its adoption
    authority remains external.  The challenger record is stored alongside
    the variant archive for cross-reference by issue/obstruction lineage.
    """
    if any(item.challenger_id == challenger.challenger_id for item in archive.challengers):
        raise ValueError("duplicate method challenger id")
    return EvolutionArchive(
        archive.variants,
        archive.trials,
        archive.incumbent_id,
        archive.challengers + (challenger,),
        archive.challenger_dispositions,
        archive.harmful_method_classes,
    )


def record_method_challenger_disposition(
    archive: EvolutionArchive,
    challenger_id: str,
    disposition: HostDisposition,
) -> EvolutionArchive:
    """Record the host disposition for a previously registered method challenger."""
    if not any(item.challenger_id == challenger_id for item in archive.challengers):
        raise ValueError("challenger not registered")
    if changelog_recorded(archive, challenger_id):
        raise ValueError("challenger disposition already recorded")

    # Index the method class if the disposition is harmful
    updated_harmful_classes = archive.harmful_method_classes
    if disposition is HostDisposition.HARMFUL:
        challenger = next(item for item in archive.challengers if item.challenger_id == challenger_id)
        if challenger.method_class:
            existing = dict(archive.harmful_method_classes)
            existing_ids = existing.get(challenger.method_class, ())
            if challenger_id not in existing_ids:
                updated_harmful_classes = tuple(
                    (mc, ids + (challenger_id,) if mc == challenger.method_class else ids)
                    for mc, ids in archive.harmful_method_classes
                )
                if challenger.method_class not in dict(archive.harmful_method_classes):
                    updated_harmful_classes = archive.harmful_method_classes + ((challenger.method_class, (challenger_id,)),)

    return EvolutionArchive(
        archive.variants,
        archive.trials,
        archive.incumbent_id,
        archive.challengers,
        archive.challenger_dispositions + ((challenger_id, disposition),),
        updated_harmful_classes,
    )


def is_known_harmful_class(archive: EvolutionArchive, method_class: str) -> bool:
    """Return True if the given method class has been associated with a harmful disposition."""
    return method_class in dict(archive.harmful_method_classes)


def get_harmful_challengers_for_class(archive: EvolutionArchive, method_class: str) -> tuple[str, ...]:
    """Return challenger IDs that recorded a harmful disposition for the given method class."""
    return dict(archive.harmful_method_classes).get(method_class, ())


def evolution_archive_stats(archive: EvolutionArchive) -> dict[str, int]:
    """Return summary statistics about the evolution archive."""
    disposition_counts: dict[str, int] = {}
    for _, disp in archive.challenger_dispositions:
        disposition_counts[disp.value] = disposition_counts.get(disp.value, 0) + 1
    return {
        "variant_count": len(archive.variants),
        "trial_count": len(archive.trials),
        "challenger_count": len(archive.challengers),
        "disposition_count": len(archive.challenger_dispositions),
        "harmful_class_count": len(archive.harmful_method_classes),
        **disposition_counts,
    }


def _archive_to_dict(archive: EvolutionArchive) -> dict:
    """Serialize an EvolutionArchive to a JSON-compatible dict."""
    return {
        "variants": [
            {
                "variant_id": v.variant_id,
                "revision_hash": v.revision_hash,
                "parent_ids": list(v.parent_ids),
                "capability_tags": list(v.capability_tags),
                "resource_profile": [[n, v] for n, v in v.resource_profile],
                "created_by_episode_ids": list(v.created_by_episode_ids),
                "status": v.status.value,
                "notes": list(v.notes),
            }
            for v in archive.variants
        ],
        "trials": [
            {
                "trial_id": t.trial_id,
                "parent_id": t.parent_id,
                "child_id": t.child_id,
                "proposal_id": t.proposal_id,
                "verdict": t.verdict.value,
                "development_delta": t.development_delta,
                "fresh_assurance_delta": t.fresh_assurance_delta,
                "reasons": list(t.reasons),
            }
            for t in archive.trials
        ],
        "incumbent_id": archive.incumbent_id,
        "challengers": [
            {
                "challenger_id": c.challenger_id,
                "subject_revision": c.subject_revision,
                "generating_failure_ids": list(c.generating_failure_ids),
                "ordinary_causes_challenged": list(c.ordinary_causes_challenged),
                "known_method_routes": list(c.known_method_routes),
                "route_inadequacy_reasons": list(c.route_inadequacy_reasons),
                "assimilated_donor_mechanisms": list(c.assimilated_donor_mechanisms),
                "structural_edit": c.structural_edit,
                "discriminator_prediction": c.discriminator_prediction,
                "stages": [
                    {
                        "stage": s.stage.value,
                        "evidence_id": s.evidence_id,
                        "status": s.status.value,
                        "split_id": s.split_id,
                        "evaluator_id": s.evaluator_id,
                        "result_hash": s.result_hash,
                    }
                    for s in c.stages
                ],
                "negative_history_ids": list(c.negative_history_ids),
                "method_class": c.method_class,
                "host_disposition": c.host_disposition.value,
                "adoption_authority": c.adoption_authority,
                "schema_version": c.schema_version,
                "candidate_controls_authority": c.candidate_controls_authority,
            }
            for c in archive.challengers
        ],
        "challenger_dispositions": [
            [cid, disp.value] for cid, disp in archive.challenger_dispositions
        ],
        "harmful_method_classes": [
            [mc, list(ids)] for mc, ids in archive.harmful_method_classes
        ],
    }


def _dict_to_archive(d: dict) -> EvolutionArchive:
    """Deserialize a dict back to an EvolutionArchive."""
    from orion.self_orion.method_challenger import (
        HostDisposition,
        MethodChallenger,
        MethodEvidenceStatus,
        MethodEvolutionStage,
        MethodStageEvidence,
    )
    from orion.self_orion.change_control import ChangeControlVerdict

    variants = tuple(
        OrionVariant(
            variant_id=v["variant_id"],
            revision_hash=v["revision_hash"],
            parent_ids=tuple(v["parent_ids"]),
            capability_tags=tuple(v["capability_tags"]),
            resource_profile=tuple((n, vv) for n, vv in v["resource_profile"]),
            created_by_episode_ids=tuple(v["created_by_episode_ids"]),
            status=VariantStatus(v["status"]),
            notes=tuple(v["notes"]),
        )
        for v in d["variants"]
    )
    trials = tuple(
        EvolutionTrialRecord(
            trial_id=t["trial_id"],
            parent_id=t["parent_id"],
            child_id=t["child_id"],
            proposal_id=t["proposal_id"],
            verdict=ChangeControlVerdict(t["verdict"]),
            development_delta=t["development_delta"],
            fresh_assurance_delta=t["fresh_assurance_delta"],
            reasons=tuple(t["reasons"]),
        )
        for t in d["trials"]
    )
    challengers = tuple(
        MethodChallenger(
            challenger_id=c["challenger_id"],
            subject_revision=c["subject_revision"],
            generating_failure_ids=tuple(c["generating_failure_ids"]),
            ordinary_causes_challenged=tuple(c["ordinary_causes_challenged"]),
            known_method_routes=tuple(c["known_method_routes"]),
            route_inadequacy_reasons=tuple(c["route_inadequacy_reasons"]),
            assimilated_donor_mechanisms=tuple(c["assimilated_donor_mechanisms"]),
            structural_edit=c["structural_edit"],
            discriminator_prediction=c["discriminator_prediction"],
            stages=tuple(
                MethodStageEvidence(
                    stage=MethodEvolutionStage(s["stage"]),
                    evidence_id=s["evidence_id"],
                    status=MethodEvidenceStatus(s["status"]),
                    split_id=s["split_id"],
                    evaluator_id=s["evaluator_id"],
                    result_hash=s["result_hash"],
                )
                for s in c["stages"]
            ),
            negative_history_ids=tuple(c["negative_history_ids"]),
            method_class=c["method_class"],
            host_disposition=HostDisposition(c["host_disposition"]),
            adoption_authority=c["adoption_authority"],
            schema_version=c["schema_version"],
            candidate_controls_authority=c["candidate_controls_authority"],
        )
        for c in d["challengers"]
    )
    challenger_dispositions = tuple(
        (cid, HostDisposition(disp)) for cid, disp in d["challenger_dispositions"]
    )
    harmful_method_classes = tuple(
        (mc, tuple(ids)) for mc, ids in d["harmful_method_classes"]
    )
    return EvolutionArchive(
        variants=variants,
        trials=trials,
        incumbent_id=d["incumbent_id"],
        challengers=challengers,
        challenger_dispositions=challenger_dispositions,
        harmful_method_classes=harmful_method_classes,
    )


def evolution_archive_to_json(archive: EvolutionArchive) -> str:
    """Serialize an EvolutionArchive to a JSON string."""
    return json.dumps(_archive_to_dict(archive), indent=2, sort_keys=True)


def evolution_archive_from_json(data: str) -> EvolutionArchive:
    """Deserialize an EvolutionArchive from a JSON string."""
    return _dict_to_archive(json.loads(data))


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
        ChangeControlVerdict.META_OVERFIT: VariantStatus.REJECTED,
        ChangeControlVerdict.CANDIDATE_ONLY: VariantStatus.CHALLENGER,
        ChangeControlVerdict.RECOMMEND_HOST_PROMOTION: VariantStatus.ASSURED,
    }[result.verdict]
    notes = ()
    if result.verdict is ChangeControlVerdict.META_OVERFIT:
        notes = ("META_OVERFIT: development gain accompanied by fresh-assurance regression",)
    variants = tuple(
        replace(item, status=next_status, notes=(*item.notes, *notes))
        if item.variant_id == child_variant_id
        else item
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
    return EvolutionArchive(variants, archive.trials + (trial,), archive.incumbent_id, archive.challengers, archive.challenger_dispositions, archive.harmful_method_classes)


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
    "changelog_recorded",
    "evolution_archive_from_json",
    "evolution_archive_stats",
    "evolution_archive_to_json",
    "get_harmful_challengers_for_class",
    "initialize_evolution_archive",
    "is_known_harmful_class",
    "recommend_host_promotion",
    "record_change_control_result",
    "record_method_challenger_disposition",
    "register_challenger",
    "register_method_challenger",
]
