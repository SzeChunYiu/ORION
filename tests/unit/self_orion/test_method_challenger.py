from __future__ import annotations

import pytest

from orion.self_orion.evolution_archive import (
    EvolutionArchive,
    OrionVariant,
    VariantStatus,
    changelog_recorded,
    evolution_archive_from_json,
    evolution_archive_stats,
    evolution_archive_to_json,
    initialize_evolution_archive,
    is_known_harmful_class,
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
    pre_assess_known_harmful_class,
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


def test_pre_assess_known_harmful_class_returns_harmful_on_recurrence() -> None:
    """A challenger whose method class was previously harmful is pre-assessed
    as HARMFUL with a recurrence reason, before the evidence ladder is evaluated."""
    candidate = _challenger(method_class="operator_replacement")
    prior = _challenger(challenger_id="challenger:harmful:prior", method_class="operator_replacement")
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
    archive = register_method_challenger(archive, prior)
    archive = record_method_challenger_disposition(archive, "challenger:harmful:prior", HostDisposition.HARMFUL)

    disposition, reasons = pre_assess_known_harmful_class(candidate, archive)
    assert disposition is HostDisposition.HARMFUL
    assert any("known_harmful_method_class_recurrence" in r for r in reasons)


def test_pre_assess_known_harmful_class_returns_candidate_only_for_unknown_class() -> None:
    """A challenger with a method class not previously associated with harm
    is not pre-assessed as harmful."""
    candidate = _challenger(method_class="novel_mechanism")
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
    disposition, reasons = pre_assess_known_harmful_class(candidate, archive)
    assert disposition is HostDisposition.CANDIDATE_ONLY
    assert not reasons


def test_pre_assess_known_harmful_class_skips_empty_method_class() -> None:
    """A challenger with no method class is not pre-assessed."""
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
    disposition, reasons = pre_assess_known_harmful_class(candidate, archive)
    assert disposition is HostDisposition.CANDIDATE_ONLY
    assert not reasons


def test_archive_retains_rejected_challengers() -> None:
    """Rejected challengers are retained in the archive after recording dispositions."""
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
    # Reject it
    archive = record_method_challenger_disposition(archive, "challenger:1", HostDisposition.REJECT)
    # The challenger must still be in archive.challengers
    assert any(c.challenger_id == "challenger:1" for c in archive.challengers)
    # The disposition must be recorded
    assert any(rid == "challenger:1" and disp is HostDisposition.REJECT for rid, disp in archive.challenger_dispositions)


def test_archive_retains_harmful_challengers() -> None:
    """Harmful-disposition challengers are retained in the archive."""
    candidate = _challenger(method_class="operator_replacement")
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
    archive = record_method_challenger_disposition(archive, "challenger:1", HostDisposition.HARMFUL)
    # The challenger must still be in archive.challengers
    assert any(c.challenger_id == "challenger:1" for c in archive.challengers)
    # The harmful method class must be indexed
    assert is_known_harmful_class(archive, "operator_replacement")


def test_evolution_archive_stats() -> None:
    """evolution_archive_stats returns correct summary counts."""
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
    stats = evolution_archive_stats(archive)
    assert stats["variant_count"] == 1
    assert stats["challenger_count"] == 1
    assert stats["disposition_count"] == 1
    assert stats["trial_count"] == 0


def test_evolution_archive_round_trip_json() -> None:
    """EvolutionArchive serializes to JSON and deserializes identically."""
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
    json_str = evolution_archive_to_json(archive)
    restored = evolution_archive_from_json(json_str)
    assert restored.variants == archive.variants
    assert restored.challengers == archive.challengers
    assert restored.challenger_dispositions == archive.challenger_dispositions
    assert restored.incumbent_id == archive.incumbent_id
