from __future__ import annotations

from orion.discovery.episodes import (
    HistoricalUseMode,
    SourceKind,
    SourceTemporalRelation,
    build_discovery_episode,
    build_episode_source,
    project_pre_cutoff_candidate_packet,
)


def test_candidate_packet_keeps_only_precutoff_supported_event_subsequence() -> None:
    pre = build_episode_source(
        source_id="pre",
        kind=SourceKind.CONTEMPORANEOUS_RECORD,
        temporal_relation=SourceTemporalRelation.PRE_OR_AT_CUTOFF,
        candidate_visible=True,
        supported_fact_ids=("problem-visible", "attempt-visible"),
    )
    post = build_episode_source(
        source_id="post",
        kind=SourceKind.RETROSPECTIVE_SECONDARY,
        temporal_relation=SourceTemporalRelation.POST_CUTOFF,
        candidate_visible=False,
        supported_fact_ids=("later-analogy-attribution", "successor-validation"),
    )
    episode = build_discovery_episode(
        episode_id="D-cutoff",
        domain="science",
        cutoff="1950-01-01",
        incumbent_regime_id="R0",
        target_contract_ids=("C",),
        sources=(pre, post),
        assertions=(),
        documented_event_trace_ids=(
            "problem-visible",
            "later-analogy-attribution",
            "attempt-visible",
            "successor-validation",
        ),
        transformation_interpretation_assertion_ids=(),
        post_event_result_ids=("successor-validation",),
        successor_context_ids=("R1",),
        use_mode=HistoricalUseMode.PRE_CUTOFF_RECONSTRUCTION_DEVELOPMENT,
    )
    packet = project_pre_cutoff_candidate_packet(episode)
    assert packet.documented_event_trace_ids == (
        "problem-visible",
        "attempt-visible",
    )
    assert "later-analogy-attribution" not in packet.canonical_json()
    assert "successor-validation" not in packet.canonical_json()
