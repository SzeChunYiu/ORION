from __future__ import annotations

import pytest

from orion.discovery.episodes import (
    AssertionConfidence,
    AssertionRole,
    FailureStage,
    FailureVisibility,
    HistoricalUseMode,
    SourceKind,
    SourceTemporalRelation,
    build_episode_assertion,
    build_episode_source,
    build_failure_episode,
)


def _source(source_id: str = "pre"):
    return build_episode_source(
        source_id=source_id,
        kind=SourceKind.CONTEMPORANEOUS_RECORD,
        temporal_relation=SourceTemporalRelation.PRE_OR_AT_CUTOFF,
        candidate_visible=True,
        supported_fact_ids=("failed-run",),
    )


def test_failure_chronology_preserves_fixed_stage_order() -> None:
    episode = build_failure_episode(
        episode_id="F1",
        domain="biology",
        cutoff="2000-01-01",
        incumbent_regime_id="R0",
        target_contract_ids=("C",),
        sources=(_source(),),
        assertions=(),
        attempted_trace_ids=("design", "run", "analyze"),
        stage_event_ids={
            FailureStage.OCCURRED: "run-failed",
            FailureStage.BECAME_OBSERVABLE: "negative-readout",
            FailureStage.DETECTED: "analyst-flags",
            FailureStage.RECOGNIZED_MATERIAL: "team-accepts",
        },
        visible_negative_evidence_ids=("negative-readout",),
        contemporaneous_responsibility_hypothesis_ids=("bad-theory", "bad-measurement"),
        retry_patch_replication_ids=("replication-1",),
        visibility=FailureVisibility.PUBLISHED_NULL,
        successor_state_id="NO_SUCCESSOR_YET",
        failure_knowledge_digest=None,
        use_mode=HistoricalUseMode.MECHANISM_EXTRACTION_ONLY,
    )
    assert episode.observed_stage_event_ids == (
        (FailureStage.OCCURRED, "run-failed"),
        (FailureStage.BECAME_OBSERVABLE, "negative-readout"),
        (FailureStage.DETECTED, "analyst-flags"),
        (FailureStage.RECOGNIZED_MATERIAL, "team-accepts"),
    )
    assert episode.attempted_trace_ids == ("design", "run", "analyze")


def test_later_stage_does_not_manufacture_missing_earlier_stage() -> None:
    episode = build_failure_episode(
        episode_id="F2",
        domain="physics",
        cutoff="1990-01-01",
        incumbent_regime_id="R0",
        target_contract_ids=("C",),
        sources=(_source(),),
        assertions=(),
        attempted_trace_ids=("run",),
        stage_event_ids={FailureStage.DETECTED: "later-detection"},
        visible_negative_evidence_ids=("negative",),
        contemporaneous_responsibility_hypothesis_ids=(),
        retry_patch_replication_ids=(),
        visibility=FailureVisibility.UNPUBLISHED_PRIVATE,
        successor_state_id="UNRESOLVED",
        failure_knowledge_digest=None,
        use_mode=HistoricalUseMode.MECHANISM_EXTRACTION_ONLY,
    )
    assert episode.stage_event_id(FailureStage.OCCURRED) is None
    assert episode.stage_event_id(FailureStage.BECAME_OBSERVABLE) is None
    assert episode.stage_event_id(FailureStage.DETECTED) == "later-detection"


def test_failure_stage_input_order_is_canonicalized_to_process_order() -> None:
    episode = build_failure_episode(
        episode_id="F3",
        domain="math",
        cutoff="1970-01-01",
        incumbent_regime_id="R0",
        target_contract_ids=("C",),
        sources=(_source(),),
        assertions=(),
        attempted_trace_ids=("proof", "counterexample"),
        stage_event_ids={
            FailureStage.RECOGNIZED_MATERIAL: "r",
            FailureStage.OCCURRED: "o",
            FailureStage.DETECTED: "d",
        },
        visible_negative_evidence_ids=("counterexample",),
        contemporaneous_responsibility_hypothesis_ids=("lemma-failure",),
        retry_patch_replication_ids=(),
        visibility=FailureVisibility.PUBLISHED_NEGATIVE,
        successor_state_id="REVISED_THEOREM_LATER",
        failure_knowledge_digest=None,
        use_mode=HistoricalUseMode.MECHANISM_EXTRACTION_ONLY,
    )
    assert [stage for stage, _ in episode.observed_stage_event_ids] == [
        FailureStage.OCCURRED,
        FailureStage.DETECTED,
        FailureStage.RECOGNIZED_MATERIAL,
    ]


def test_failure_visibility_is_not_scientific_validity() -> None:
    source = _source()
    assertion = build_episode_assertion(
        assertion_id="execution-defect",
        coordinate_id="failure-responsibility",
        value_id="EXECUTION_DEFECT_POSSIBLE",
        role=AssertionRole.DOCUMENTED,
        supporting_source_ids=(source.source_id,),
        confidence=AssertionConfidence.MEDIUM,
    )
    episode = build_failure_episode(
        episode_id="F4",
        domain="science",
        cutoff="2020-01-01",
        incumbent_regime_id="R0",
        target_contract_ids=("C",),
        sources=(source,),
        assertions=(assertion,),
        attempted_trace_ids=("experiment",),
        stage_event_ids={FailureStage.OCCURRED: "fail"},
        visible_negative_evidence_ids=("fail",),
        contemporaneous_responsibility_hypothesis_ids=("execution-defect",),
        retry_patch_replication_ids=(),
        visibility=FailureVisibility.RETRACTED,
        successor_state_id="UNRESOLVED",
        failure_knowledge_digest=None,
        use_mode=HistoricalUseMode.MECHANISM_EXTRACTION_ONLY,
    )
    assert episode.visibility is FailureVisibility.RETRACTED
    assert episode.grants_scientific_refutation is False


def test_failure_episode_cannot_manufacture_scoped_exclusions() -> None:
    episode = build_failure_episode(
        episode_id="F5",
        domain="engineering",
        cutoff="2010-01-01",
        incumbent_regime_id="R0",
        target_contract_ids=("C",),
        sources=(_source(),),
        assertions=(),
        attempted_trace_ids=("prototype", "test"),
        stage_event_ids={FailureStage.OCCURRED: "break"},
        visible_negative_evidence_ids=("break",),
        contemporaneous_responsibility_hypothesis_ids=("material", "geometry"),
        retry_patch_replication_ids=(),
        visibility=FailureVisibility.PUBLISHED_NEGATIVE,
        successor_state_id="UNRESOLVED",
        failure_knowledge_digest=None,
        use_mode=HistoricalUseMode.MECHANISM_EXTRACTION_ONLY,
    )
    assert episode.failure_knowledge_digest is None
    assert episode.scoped_excluded_condition_ids == ()
    assert episode.grants_global_prohibition is False


def test_failure_episode_rejects_unknown_assertion_sources() -> None:
    source = _source()
    assertion = build_episode_assertion(
        assertion_id="a",
        coordinate_id="cause",
        value_id="x",
        role=AssertionRole.STRUCTURAL_INTERPRETATION,
        supporting_source_ids=("not-present",),
        confidence=AssertionConfidence.LOW,
    )
    with pytest.raises(ValueError, match="unknown source"):
        build_failure_episode(
            episode_id="F6",
            domain="science",
            cutoff="2020-01-01",
            incumbent_regime_id="R0",
            target_contract_ids=("C",),
            sources=(source,),
            assertions=(assertion,),
            attempted_trace_ids=("run",),
            stage_event_ids={FailureStage.OCCURRED: "fail"},
            visible_negative_evidence_ids=("fail",),
            contemporaneous_responsibility_hypothesis_ids=(),
            retry_patch_replication_ids=(),
            visibility=FailureVisibility.UNKNOWN,
            successor_state_id="UNRESOLVED",
            failure_knowledge_digest=None,
            use_mode=HistoricalUseMode.MECHANISM_EXTRACTION_ONLY,
        )
