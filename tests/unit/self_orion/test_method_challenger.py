from __future__ import annotations

import pytest

from orion.self_orion.evolution_archive import (
    EvolutionArchive,
    OrionVariant,
    VariantStatus,
    changelog_recorded,
    initialize_evolution_archive,
    register_challenger,
    register_method_challenger,
    record_method_challenger_disposition,
)
from orion.self_orion.method_challenger import (
    HostDisposition,
    MethodChallenger,
    MethodEvidenceStatus,
    MethodEvolutionStage,
    MethodStageEvidence,
    assess_method_challenger,
    validate_method_challenger,
)


SHA = "a" * 64


def _challenger(**overrides: object) -> MethodChallenger:
    stages = tuple(
        MethodStageEvidence(
            stage,
            f"evidence:{stage.value}",
            MethodEvidenceStatus.PASS,
            split_id="split:fresh" if stage in (MethodEvolutionStage.FRESH, MethodEvolutionStage.PROTECTED) else "",
            evaluator_id="evaluator:protected" if stage in (MethodEvolutionStage.FRESH, MethodEvolutionStage.PROTECTED) else "",
            result_hash=SHA,
        )
        for stage in MethodEvolutionStage
    )
    values: dict[str, object] = {
        "challenger_id": "challenger:1",
        "subject_revision": SHA,
        "generating_failure_ids": ("failure:1",),
        "ordinary_causes_challenged": ("cause:execution", "cause:measurement"),
        "known_method_routes": ("route:literature", "route:transfer"),
        "route_inadequacy_reasons": ("route:literature inadequate", "route:transfer inadequate"),
        "assimilated_donor_mechanisms": ("donor:mechanism:1",),
        "structural_edit": "replace incumbent operator composition",
        "discriminator_prediction": "fresh protected family improves without protected harm",
        "stages": stages,
        "negative_history_ids": ("negative:rejected-1",),
    }
    values.update(overrides)
    return MethodChallenger(**values)


def test_clean_method_candidate_reaches_only_external_host_recommendation() -> None:
    candidate = _challenger()
    assert assess_method_challenger(candidate) == (
        HostDisposition.RECOMMEND,
        ("complete protected method-evolution ladder; host disposition remains external",),
    )
    validate_method_challenger(candidate)
    assert candidate.empirical_authority == "NONE"
    assert not candidate.can_mutate_method_registry


def test_replay_success_cannot_compensate_for_fresh_harm() -> None:
    stages = list(_challenger().stages)
    stages[5] = MethodStageEvidence(
        MethodEvolutionStage.FRESH,
        "evidence:fresh",
        MethodEvidenceStatus.HARMFUL,
        split_id="split:fresh",
        evaluator_id="evaluator:protected",
        result_hash=SHA,
    )
    disposition, reasons = assess_method_challenger(_challenger(stages=tuple(stages)))
    assert disposition is HostDisposition.REJECT
    assert "harmful_outcome_precedence:FRESH" in reasons


def test_missing_protected_evidence_is_blocked_not_adopted() -> None:
    stages = tuple(item for item in _challenger().stages if item.stage is not MethodEvolutionStage.PROTECTED)
    disposition, reasons = assess_method_challenger(_challenger(stages=stages))
    assert disposition is HostDisposition.BLOCK
    assert "missing_stages:PROTECTED" in reasons
    with pytest.raises(ValueError, match="not admissible"):
        validate_method_challenger(_challenger(stages=stages))


def test_candidate_cannot_claim_host_disposition_or_rewrite_authority() -> None:
    with pytest.raises(ValueError, match="external"):
        _challenger(adoption_authority="candidate")
    with pytest.raises(ValueError, match="not authoritative"):
        _challenger(candidate_controls_authority=True)
    with pytest.raises(ValueError, match="not authoritative"):
        _challenger(host_disposition=HostDisposition.RECOMMEND)


def test_register_method_challenger_in_evolution_archive() -> None:
    """Method challenger can be registered in the evolution archive."""
    candidate = _challenger()
    incumbent = OrionVariant(
        variant_id="incumbent:1",
        revision_hash=SHA,
        parent_ids=(),
        capability_tags=("base",),
        resource_profile=(("cpu", 1.0),),
        created_by_episode_ids=(),
        status=VariantStatus.INCUMBENT,
    )
    archive = register_challenger(
        initialize_evolution_archive(incumbent),
        OrionVariant(
            variant_id="challenger:variant:1",
            revision_hash=SHA,
            parent_ids=("incumbent:1",),
            capability_tags=("base", "extended"),
            resource_profile=(("cpu", 1.5),),
            created_by_episode_ids=(),
            status=VariantStatus.CHALLENGER,
        ),
    )
    archive = register_method_challenger(archive, candidate)
    assert any(item.challenger_id == "challenger:1" for item in archive.challengers)
    assert not changelog_recorded(archive, "challenger:1")


def test_record_method_challenger_disposition_persists() -> None:
    """Host disposition for a method challenger is recorded and immutable."""
    candidate = _challenger()
    incumbent = OrionVariant(
        variant_id="incumbent:1",
        revision_hash=SHA,
        parent_ids=(),
        capability_tags=("base",),
        resource_profile=(("cpu", 1.0),),
        created_by_episode_ids=(),
        status=VariantStatus.INCUMBENT,
    )
    archive = initialize_evolution_archive(incumbent)
    archive = register_method_challenger(archive, candidate)
    archive = record_method_challenger_disposition(archive, "challenger:1", HostDisposition.RECOMMEND)
    assert changelog_recorded(archive, "challenger:1")
    assert any(
        rid == "challenger:1" and disp is HostDisposition.RECOMMEND
        for rid, disp in archive.challenger_dispositions
    )


def test_record_method_challenger_disposition_unknown_challenger_rejected() -> None:
    """Disposition for an unregistered challenger is rejected."""
    incumbent = OrionVariant(
        variant_id="incumbent:1",
        revision_hash=SHA,
        parent_ids=(),
        capability_tags=("base",),
        resource_profile=(("cpu", 1.0),),
        created_by_episode_ids=(),
        status=VariantStatus.INCUMBENT,
    )
    archive = initialize_evolution_archive(incumbent)
    with pytest.raises(ValueError, match="not registered"):
        record_method_challenger_disposition(archive, "challenger:unknown", HostDisposition.REJECT)


def test_record_method_challenger_disposition_duplicate_rejected() -> None:
    """Duplicate disposition recording is rejected."""
    candidate = _challenger()
    incumbent = OrionVariant(
        variant_id="incumbent:1",
        revision_hash=SHA,
        parent_ids=(),
        capability_tags=("base",),
        resource_profile=(("cpu", 1.0),),
        created_by_episode_ids=(),
        status=VariantStatus.INCUMBENT,
    )
    archive = initialize_evolution_archive(incumbent)
    archive = register_method_challenger(archive, candidate)
    archive = record_method_challenger_disposition(archive, "challenger:1", HostDisposition.REJECT)
    with pytest.raises(ValueError, match="already recorded"):
        record_method_challenger_disposition(archive, "challenger:1", HostDisposition.RECOMMEND)
