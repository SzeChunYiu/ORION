from __future__ import annotations

import pytest

from orion.discovery.episodes import (
    AssertionConfidence,
    AssertionRole,
    HistoricalUseMode,
    SourceKind,
    SourceTemporalRelation,
    build_discovery_episode,
    build_episode_assertion,
    build_episode_source,
    project_pre_cutoff_candidate_packet,
)


def _pre_source(source_id: str = "src-pre"):
    return build_episode_source(
        source_id=source_id,
        kind=SourceKind.PRIMARY_ORIGINAL,
        temporal_relation=SourceTemporalRelation.PRE_OR_AT_CUTOFF,
        candidate_visible=True,
        supported_fact_ids=("fact-observation",),
    )


def _post_source(source_id: str = "src-post"):
    return build_episode_source(
        source_id=source_id,
        kind=SourceKind.RETROSPECTIVE_SECONDARY,
        temporal_relation=SourceTemporalRelation.POST_CUTOFF,
        candidate_visible=False,
        supported_fact_ids=("fact-successor",),
    )


def test_post_cutoff_source_cannot_be_candidate_visible() -> None:
    with pytest.raises(ValueError, match="post-cutoff.*candidate-visible"):
        build_episode_source(
            source_id="bad",
            kind=SourceKind.RETROSPECTIVE_SECONDARY,
            temporal_relation=SourceTemporalRelation.POST_CUTOFF,
            candidate_visible=True,
            supported_fact_ids=("x",),
        )


def test_documented_assertion_requires_supporting_source() -> None:
    with pytest.raises(ValueError, match="DOCUMENTED.*source"):
        build_episode_assertion(
            assertion_id="a",
            coordinate_id="incumbent-model",
            value_id="model-v1",
            role=AssertionRole.DOCUMENTED,
            supporting_source_ids=(),
            confidence=AssertionConfidence.HIGH,
        )


def test_cannot_infer_cannot_carry_positive_value() -> None:
    assertion = build_episode_assertion(
        assertion_id="unknown-thought",
        coordinate_id="private-cognitive-step",
        value_id=None,
        role=AssertionRole.CANNOT_INFER,
        supporting_source_ids=(),
        confidence=AssertionConfidence.UNRESOLVED,
    )
    assert assertion.value_id is None
    with pytest.raises(ValueError, match="CANNOT_INFER.*value"):
        build_episode_assertion(
            assertion_id="fake-thought",
            coordinate_id="private-cognitive-step",
            value_id="used-analogy-X",
            role=AssertionRole.CANNOT_INFER,
            supporting_source_ids=(),
            confidence=AssertionConfidence.LOW,
        )


def test_assertion_cannot_cite_unknown_episode_source() -> None:
    source = _pre_source()
    assertion = build_episode_assertion(
        assertion_id="a",
        coordinate_id="observation",
        value_id="obs-1",
        role=AssertionRole.DOCUMENTED,
        supporting_source_ids=(source.source_id, "missing-source"),
        confidence=AssertionConfidence.HIGH,
    )
    with pytest.raises(ValueError, match="unknown source"):
        build_discovery_episode(
            episode_id="D1",
            domain="physics",
            cutoff="1900-01-01",
            incumbent_regime_id="R0",
            target_contract_ids=("C",),
            sources=(source,),
            assertions=(assertion,),
            documented_event_trace_ids=("event-1",),
            transformation_interpretation_assertion_ids=(),
            post_event_result_ids=(),
            successor_context_ids=(),
            use_mode=HistoricalUseMode.MECHANISM_EXTRACTION_ONLY,
        )


def test_setlike_fields_are_canonical_but_event_trace_preserves_order() -> None:
    source_a = build_episode_source(
        source_id="s",
        kind=SourceKind.PRIMARY_ORIGINAL,
        temporal_relation=SourceTemporalRelation.PRE_OR_AT_CUTOFF,
        candidate_visible=True,
        supported_fact_ids=("b", "a"),
        limitation_note_ids=("l2", "l1"),
    )
    source_b = build_episode_source(
        source_id="s",
        kind=SourceKind.PRIMARY_ORIGINAL,
        temporal_relation=SourceTemporalRelation.PRE_OR_AT_CUTOFF,
        candidate_visible=True,
        supported_fact_ids=("a", "b"),
        limitation_note_ids=("l1", "l2"),
    )
    assert source_a.digest == source_b.digest

    assertion = build_episode_assertion(
        assertion_id="a",
        coordinate_id="event",
        value_id="v",
        role=AssertionRole.DOCUMENTED,
        supporting_source_ids=("s",),
        confidence=AssertionConfidence.HIGH,
    )
    episode = build_discovery_episode(
        episode_id="D",
        domain="math",
        cutoff="1960-01-01",
        incumbent_regime_id="R",
        target_contract_ids=("C2", "C1"),
        sources=(source_a,),
        assertions=(assertion,),
        documented_event_trace_ids=("observe", "conjecture", "counterexample", "revise"),
        transformation_interpretation_assertion_ids=(),
        post_event_result_ids=("result",),
        successor_context_ids=("later-analysis",),
        use_mode=HistoricalUseMode.MECHANISM_EXTRACTION_ONLY,
    )
    assert episode.target_contract_ids == ("C1", "C2")
    assert episode.documented_event_trace_ids == (
        "observe",
        "conjecture",
        "counterexample",
        "revise",
    )


def test_historical_episode_cannot_be_protected_confirmatory_gold() -> None:
    with pytest.raises(ValueError, match="historical.*confirmatory"):
        build_discovery_episode(
            episode_id="D",
            domain="science",
            cutoff="2000-01-01",
            incumbent_regime_id="R",
            target_contract_ids=("C",),
            sources=(_pre_source(),),
            assertions=(),
            documented_event_trace_ids=("e",),
            transformation_interpretation_assertion_ids=(),
            post_event_result_ids=(),
            successor_context_ids=(),
            use_mode="PROTECTED_CONFIRMATORY_GOLD",
        )


def test_pre_cutoff_projection_strips_post_cutoff_and_evaluator_interpretation() -> None:
    pre = _pre_source()
    post = _post_source()
    observed = build_episode_assertion(
        assertion_id="observed",
        coordinate_id="precutoff-observation",
        value_id="obs",
        role=AssertionRole.DOCUMENTED,
        supporting_source_ids=(pre.source_id,),
        confidence=AssertionConfidence.HIGH,
    )
    interpretation = build_episode_assertion(
        assertion_id="interpretation",
        coordinate_id="transformation",
        value_id="ANALOGY_TRANSFER",
        role=AssertionRole.STRUCTURAL_INTERPRETATION,
        supporting_source_ids=(pre.source_id, post.source_id),
        confidence=AssertionConfidence.MEDIUM,
        evaluator_only=True,
    )
    successor = build_episode_assertion(
        assertion_id="successor-fact",
        coordinate_id="later-successor",
        value_id="R1",
        role=AssertionRole.DOCUMENTED,
        supporting_source_ids=(post.source_id,),
        confidence=AssertionConfidence.HIGH,
        evaluator_only=True,
    )
    episode = build_discovery_episode(
        episode_id="D",
        domain="engineering",
        cutoff="1980-01-01",
        incumbent_regime_id="R0",
        target_contract_ids=("build-function-F",),
        sources=(pre, post),
        assertions=(observed, interpretation, successor),
        documented_event_trace_ids=("problem", "prototype"),
        transformation_interpretation_assertion_ids=(interpretation.assertion_id,),
        post_event_result_ids=("later-success",),
        successor_context_ids=("successor-regime-R1",),
        use_mode=HistoricalUseMode.PRE_CUTOFF_RECONSTRUCTION_DEVELOPMENT,
    )
    packet = project_pre_cutoff_candidate_packet(episode)
    assert packet.source_ids == (pre.source_id,)
    assert packet.assertion_ids == (observed.assertion_id,)
    assert "successor-regime-R1" not in packet.canonical_json()
    assert "ANALOGY_TRANSFER" not in packet.canonical_json()
    assert packet.grants_historical_causal_truth is False
