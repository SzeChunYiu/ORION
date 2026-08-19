"""Source-grounded historical/practical episode records for ORION discovery research.

These records exist to prevent retrospective stories from silently becoming
scientific or cognitive ground truth.  They separate source chronology,
documented assertions, ORION structural interpretations, explicit CANNOT_INFER,
and post-cutoff evaluator context.  Historical episodes are mechanism-extraction
or development material only; this V1 schema forbids treating famous historical
content as protected confirmatory gold.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

from orion.transfer.v2.canonical import canonical_json, content_digest


def _sorted_unique(values: Sequence[str]) -> tuple[str, ...]:
    return tuple(sorted({str(value) for value in values}))


def _ordered(values: Sequence[str]) -> tuple[str, ...]:
    return tuple(str(value) for value in values)


class SourceKind(str, Enum):
    PRIMARY_ORIGINAL = "PRIMARY_ORIGINAL"
    CONTEMPORANEOUS_RECORD = "CONTEMPORANEOUS_RECORD"
    ARCHIVAL_SECONDARY = "ARCHIVAL_SECONDARY"
    RETROSPECTIVE_SECONDARY = "RETROSPECTIVE_SECONDARY"
    META_ANALYSIS = "META_ANALYSIS"
    UNKNOWN = "UNKNOWN"


class SourceTemporalRelation(str, Enum):
    PRE_OR_AT_CUTOFF = "PRE_OR_AT_CUTOFF"
    POST_CUTOFF = "POST_CUTOFF"


class AssertionRole(str, Enum):
    DOCUMENTED = "DOCUMENTED"
    STRUCTURAL_INTERPRETATION = "STRUCTURAL_INTERPRETATION"
    CANNOT_INFER = "CANNOT_INFER"


class AssertionConfidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNRESOLVED = "UNRESOLVED"


class HistoricalUseMode(str, Enum):
    MECHANISM_EXTRACTION_ONLY = "MECHANISM_EXTRACTION_ONLY"
    PRE_CUTOFF_RECONSTRUCTION_DEVELOPMENT = "PRE_CUTOFF_RECONSTRUCTION_DEVELOPMENT"


class FailureStage(str, Enum):
    OCCURRED = "OCCURRED"
    BECAME_OBSERVABLE = "BECAME_OBSERVABLE"
    DETECTED = "DETECTED"
    RECOGNIZED_MATERIAL = "RECOGNIZED_MATERIAL"
    RESPONSIBILITY_INVESTIGATED = "RESPONSIBILITY_INVESTIGATED"
    NEGATIVE_KNOWLEDGE_FROZEN = "NEGATIVE_KNOWLEDGE_FROZEN"
    SUCCESSOR_SEARCHED = "SUCCESSOR_SEARCHED"
    SUCCESSOR_VALIDATED = "SUCCESSOR_VALIDATED"


_FAILURE_STAGE_ORDER = {
    stage: index
    for index, stage in enumerate(
        (
            FailureStage.OCCURRED,
            FailureStage.BECAME_OBSERVABLE,
            FailureStage.DETECTED,
            FailureStage.RECOGNIZED_MATERIAL,
            FailureStage.RESPONSIBILITY_INVESTIGATED,
            FailureStage.NEGATIVE_KNOWLEDGE_FROZEN,
            FailureStage.SUCCESSOR_SEARCHED,
            FailureStage.SUCCESSOR_VALIDATED,
        )
    )
}


class FailureVisibility(str, Enum):
    PUBLISHED_NEGATIVE = "PUBLISHED_NEGATIVE"
    PUBLISHED_NULL = "PUBLISHED_NULL"
    UNPUBLISHED_PRIVATE = "UNPUBLISHED_PRIVATE"
    FILE_DRAWER = "FILE_DRAWER"
    CORRECTED = "CORRECTED"
    RETRACTED = "RETRACTED"
    DISPUTED = "DISPUTED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class EpisodeSource:
    source_id: str
    kind: SourceKind
    temporal_relation: SourceTemporalRelation
    candidate_visible: bool
    supported_fact_ids: tuple[str, ...]
    limitation_note_ids: tuple[str, ...]
    digest: str

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "EpisodeSource.v1",
            "source_id": self.source_id,
            "kind": self.kind.value,
            "temporal_relation": self.temporal_relation.value,
            "candidate_visible": self.candidate_visible,
            "supported_fact_ids": list(self.supported_fact_ids),
            "limitation_note_ids": list(self.limitation_note_ids),
        }

    def verify(self) -> None:
        if not self.source_id:
            raise ValueError("episode source identity is required")
        if self.temporal_relation is SourceTemporalRelation.POST_CUTOFF and self.candidate_visible:
            raise ValueError("post-cutoff source cannot be candidate-visible")
        if not self.supported_fact_ids:
            raise ValueError("episode source must bind at least one supported fact/event identity")
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("episode source digest mismatch")


def build_episode_source(
    *,
    source_id: str,
    kind: SourceKind,
    temporal_relation: SourceTemporalRelation,
    candidate_visible: bool,
    supported_fact_ids: Sequence[str],
    limitation_note_ids: Sequence[str] = (),
) -> EpisodeSource:
    payload = {
        "version": "EpisodeSource.v1",
        "source_id": str(source_id),
        "kind": SourceKind(kind).value,
        "temporal_relation": SourceTemporalRelation(temporal_relation).value,
        "candidate_visible": bool(candidate_visible),
        "supported_fact_ids": list(_sorted_unique(supported_fact_ids)),
        "limitation_note_ids": list(_sorted_unique(limitation_note_ids)),
    }
    source = EpisodeSource(
        source_id=payload["source_id"],
        kind=SourceKind(payload["kind"]),
        temporal_relation=SourceTemporalRelation(payload["temporal_relation"]),
        candidate_visible=payload["candidate_visible"],
        supported_fact_ids=tuple(payload["supported_fact_ids"]),
        limitation_note_ids=tuple(payload["limitation_note_ids"]),
        digest=content_digest(payload),
    )
    source.verify()
    return source


@dataclass(frozen=True)
class EpisodeAssertion:
    assertion_id: str
    coordinate_id: str
    value_id: str | None
    role: AssertionRole
    supporting_source_ids: tuple[str, ...]
    competing_interpretation_ids: tuple[str, ...]
    confidence: AssertionConfidence
    evaluator_only: bool
    digest: str

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "EpisodeAssertion.v1",
            "assertion_id": self.assertion_id,
            "coordinate_id": self.coordinate_id,
            "value_id": self.value_id,
            "role": self.role.value,
            "supporting_source_ids": list(self.supporting_source_ids),
            "competing_interpretation_ids": list(self.competing_interpretation_ids),
            "confidence": self.confidence.value,
            "evaluator_only": self.evaluator_only,
            "grants_historical_causal_truth": False,
        }

    def verify(self) -> None:
        if not self.assertion_id or not self.coordinate_id:
            raise ValueError("episode assertion and coordinate identities are required")
        if self.role is AssertionRole.DOCUMENTED:
            if self.value_id is None:
                raise ValueError("DOCUMENTED assertion requires a value/reference identity")
            if not self.supporting_source_ids:
                raise ValueError("DOCUMENTED assertion requires at least one supporting source")
        elif self.role is AssertionRole.STRUCTURAL_INTERPRETATION:
            if self.value_id is None:
                raise ValueError("STRUCTURAL_INTERPRETATION requires an interpretation value/reference")
            if not self.supporting_source_ids:
                raise ValueError("STRUCTURAL_INTERPRETATION requires source lineage")
        elif self.role is AssertionRole.CANNOT_INFER:
            if self.value_id is not None:
                raise ValueError("CANNOT_INFER assertion cannot carry a positive historical value")
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("episode assertion digest mismatch")


def build_episode_assertion(
    *,
    assertion_id: str,
    coordinate_id: str,
    value_id: str | None,
    role: AssertionRole,
    supporting_source_ids: Sequence[str],
    confidence: AssertionConfidence,
    competing_interpretation_ids: Sequence[str] = (),
    evaluator_only: bool = False,
) -> EpisodeAssertion:
    payload = {
        "version": "EpisodeAssertion.v1",
        "assertion_id": str(assertion_id),
        "coordinate_id": str(coordinate_id),
        "value_id": str(value_id) if value_id is not None else None,
        "role": AssertionRole(role).value,
        "supporting_source_ids": list(_sorted_unique(supporting_source_ids)),
        "competing_interpretation_ids": list(_sorted_unique(competing_interpretation_ids)),
        "confidence": AssertionConfidence(confidence).value,
        "evaluator_only": bool(evaluator_only),
        "grants_historical_causal_truth": False,
    }
    assertion = EpisodeAssertion(
        assertion_id=payload["assertion_id"],
        coordinate_id=payload["coordinate_id"],
        value_id=payload["value_id"],
        role=AssertionRole(payload["role"]),
        supporting_source_ids=tuple(payload["supporting_source_ids"]),
        competing_interpretation_ids=tuple(payload["competing_interpretation_ids"]),
        confidence=AssertionConfidence(payload["confidence"]),
        evaluator_only=payload["evaluator_only"],
        digest=content_digest(payload),
    )
    assertion.verify()
    return assertion


def _canonical_sources(sources: Sequence[EpisodeSource]) -> tuple[EpisodeSource, ...]:
    for source in sources:
        source.verify()
    rows = sorted(sources, key=lambda source: source.source_id)
    if len({source.source_id for source in rows}) != len(rows):
        raise ValueError("duplicate episode source identity")
    return tuple(rows)


def _canonical_assertions(
    assertions: Sequence[EpisodeAssertion],
) -> tuple[EpisodeAssertion, ...]:
    for assertion in assertions:
        assertion.verify()
    rows = sorted(assertions, key=lambda assertion: assertion.assertion_id)
    if len({assertion.assertion_id for assertion in rows}) != len(rows):
        raise ValueError("duplicate episode assertion identity")
    return tuple(rows)


def _validate_assertion_sources(
    sources: Sequence[EpisodeSource],
    assertions: Sequence[EpisodeAssertion],
) -> None:
    source_ids = {source.source_id for source in sources}
    for assertion in assertions:
        unknown = set(assertion.supporting_source_ids) - source_ids
        if unknown:
            raise ValueError(
                "episode assertion cites unknown source IDs: " + ",".join(sorted(unknown))
            )


def _parse_historical_use_mode(value: HistoricalUseMode | str) -> HistoricalUseMode:
    if isinstance(value, HistoricalUseMode):
        return value
    raw = str(value)
    if raw == "PROTECTED_CONFIRMATORY_GOLD":
        raise ValueError("historical episode cannot be protected confirmatory gold")
    return HistoricalUseMode(raw)


@dataclass(frozen=True)
class DiscoveryEpisode:
    episode_id: str
    domain: str
    cutoff: str
    incumbent_regime_id: str
    target_contract_ids: tuple[str, ...]
    sources: tuple[EpisodeSource, ...]
    assertions: tuple[EpisodeAssertion, ...]
    documented_event_trace_ids: tuple[str, ...]
    transformation_interpretation_assertion_ids: tuple[str, ...]
    post_event_result_ids: tuple[str, ...]
    successor_context_ids: tuple[str, ...]
    use_mode: HistoricalUseMode
    digest: str

    @property
    def grants_historical_causal_truth(self) -> bool:
        return False

    @property
    def grants_scientific_authority(self) -> bool:
        return False

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "DiscoveryEpisode.v1",
            "episode_id": self.episode_id,
            "domain": self.domain,
            "cutoff": self.cutoff,
            "incumbent_regime_id": self.incumbent_regime_id,
            "target_contract_ids": list(self.target_contract_ids),
            "sources": [source.unsigned() for source in self.sources],
            "assertions": [assertion.unsigned() for assertion in self.assertions],
            "documented_event_trace_ids": list(self.documented_event_trace_ids),
            "transformation_interpretation_assertion_ids": list(
                self.transformation_interpretation_assertion_ids
            ),
            "post_event_result_ids": list(self.post_event_result_ids),
            "successor_context_ids": list(self.successor_context_ids),
            "use_mode": self.use_mode.value,
            "grants_historical_causal_truth": False,
            "grants_scientific_authority": False,
        }

    def verify(self) -> None:
        if not self.episode_id or not self.domain or not self.cutoff or not self.incumbent_regime_id:
            raise ValueError("discovery episode identity/domain/cutoff/regime are required")
        if not self.target_contract_ids:
            raise ValueError("discovery episode requires target contracts")
        if not self.documented_event_trace_ids:
            raise ValueError("discovery episode requires at least one documented event identity")
        if any(not event_id for event_id in self.documented_event_trace_ids):
            raise ValueError("documented event trace identities must be non-empty")
        _validate_assertion_sources(self.sources, self.assertions)
        assertion_map = {a.assertion_id: a for a in self.assertions}
        for assertion_id in self.transformation_interpretation_assertion_ids:
            assertion = assertion_map.get(assertion_id)
            if assertion is None:
                raise ValueError("transformation interpretation references unknown assertion")
            if assertion.role is not AssertionRole.STRUCTURAL_INTERPRETATION:
                raise ValueError("transformation interpretation must reference STRUCTURAL_INTERPRETATION")
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("discovery episode digest mismatch")


def build_discovery_episode(
    *,
    episode_id: str,
    domain: str,
    cutoff: str,
    incumbent_regime_id: str,
    target_contract_ids: Sequence[str],
    sources: Sequence[EpisodeSource],
    assertions: Sequence[EpisodeAssertion],
    documented_event_trace_ids: Sequence[str],
    transformation_interpretation_assertion_ids: Sequence[str],
    post_event_result_ids: Sequence[str],
    successor_context_ids: Sequence[str],
    use_mode: HistoricalUseMode | str,
) -> DiscoveryEpisode:
    source_rows = _canonical_sources(sources)
    assertion_rows = _canonical_assertions(assertions)
    _validate_assertion_sources(source_rows, assertion_rows)
    mode = _parse_historical_use_mode(use_mode)
    payload = {
        "version": "DiscoveryEpisode.v1",
        "episode_id": str(episode_id),
        "domain": str(domain),
        "cutoff": str(cutoff),
        "incumbent_regime_id": str(incumbent_regime_id),
        "target_contract_ids": list(_sorted_unique(target_contract_ids)),
        "sources": [source.unsigned() for source in source_rows],
        "assertions": [assertion.unsigned() for assertion in assertion_rows],
        "documented_event_trace_ids": list(_ordered(documented_event_trace_ids)),
        "transformation_interpretation_assertion_ids": list(
            _sorted_unique(transformation_interpretation_assertion_ids)
        ),
        "post_event_result_ids": list(_sorted_unique(post_event_result_ids)),
        "successor_context_ids": list(_sorted_unique(successor_context_ids)),
        "use_mode": mode.value,
        "grants_historical_causal_truth": False,
        "grants_scientific_authority": False,
    }
    episode = DiscoveryEpisode(
        episode_id=payload["episode_id"],
        domain=payload["domain"],
        cutoff=payload["cutoff"],
        incumbent_regime_id=payload["incumbent_regime_id"],
        target_contract_ids=tuple(payload["target_contract_ids"]),
        sources=source_rows,
        assertions=assertion_rows,
        documented_event_trace_ids=tuple(payload["documented_event_trace_ids"]),
        transformation_interpretation_assertion_ids=tuple(
            payload["transformation_interpretation_assertion_ids"]
        ),
        post_event_result_ids=tuple(payload["post_event_result_ids"]),
        successor_context_ids=tuple(payload["successor_context_ids"]),
        use_mode=mode,
        digest=content_digest(payload),
    )
    episode.verify()
    return episode


@dataclass(frozen=True)
class PreCutoffCandidatePacket:
    episode_id: str
    domain: str
    cutoff: str
    incumbent_regime_id: str
    target_contract_ids: tuple[str, ...]
    sources: tuple[EpisodeSource, ...]
    assertions: tuple[EpisodeAssertion, ...]
    documented_event_trace_ids: tuple[str, ...]
    digest: str

    @property
    def source_ids(self) -> tuple[str, ...]:
        return tuple(source.source_id for source in self.sources)

    @property
    def assertion_ids(self) -> tuple[str, ...]:
        return tuple(assertion.assertion_id for assertion in self.assertions)

    @property
    def grants_historical_causal_truth(self) -> bool:
        return False

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "PreCutoffDiscoveryCandidatePacket.v1",
            "episode_id": self.episode_id,
            "domain": self.domain,
            "cutoff": self.cutoff,
            "incumbent_regime_id": self.incumbent_regime_id,
            "target_contract_ids": list(self.target_contract_ids),
            "sources": [source.unsigned() for source in self.sources],
            "assertions": [assertion.unsigned() for assertion in self.assertions],
            "documented_event_trace_ids": list(self.documented_event_trace_ids),
            "grants_historical_causal_truth": False,
        }

    def canonical_json(self) -> str:
        return canonical_json(self.unsigned())

    def verify(self) -> None:
        if any(
            source.temporal_relation is SourceTemporalRelation.POST_CUTOFF
            or not source.candidate_visible
            for source in self.sources
        ):
            raise ValueError("candidate packet contains non-candidate-visible/post-cutoff source")
        if any(assertion.evaluator_only for assertion in self.assertions):
            raise ValueError("candidate packet contains evaluator-only assertion")
        source_ids = {source.source_id for source in self.sources}
        supported_visible_fact_ids = {
            fact_id for source in self.sources for fact_id in source.supported_fact_ids
        }
        for assertion in self.assertions:
            if set(assertion.supporting_source_ids) - source_ids:
                raise ValueError("candidate assertion depends on stripped source")
            if assertion.role is AssertionRole.STRUCTURAL_INTERPRETATION:
                raise ValueError("structural interpretation must remain evaluator-side in V1 packet")
            if assertion.role is AssertionRole.CANNOT_INFER:
                raise ValueError("CANNOT_INFER placeholder is not candidate evidence")
        if any(event_id not in supported_visible_fact_ids for event_id in self.documented_event_trace_ids):
            raise ValueError("candidate event trace contains event not supported by visible pre-cutoff source")
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("pre-cutoff packet digest mismatch")


def project_pre_cutoff_candidate_packet(
    episode: DiscoveryEpisode,
) -> PreCutoffCandidatePacket:
    episode.verify()
    visible_sources = tuple(
        source
        for source in episode.sources
        if source.candidate_visible
        and source.temporal_relation is SourceTemporalRelation.PRE_OR_AT_CUTOFF
    )
    visible_source_ids = {source.source_id for source in visible_sources}
    visible_fact_ids = {
        fact_id for source in visible_sources for fact_id in source.supported_fact_ids
    }
    visible_assertions = tuple(
        assertion
        for assertion in episode.assertions
        if not assertion.evaluator_only
        and assertion.role is AssertionRole.DOCUMENTED
        and set(assertion.supporting_source_ids).issubset(visible_source_ids)
    )
    visible_event_trace = tuple(
        event_id
        for event_id in episode.documented_event_trace_ids
        if event_id in visible_fact_ids
    )
    payload = {
        "version": "PreCutoffDiscoveryCandidatePacket.v1",
        "episode_id": episode.episode_id,
        "domain": episode.domain,
        "cutoff": episode.cutoff,
        "incumbent_regime_id": episode.incumbent_regime_id,
        "target_contract_ids": list(episode.target_contract_ids),
        "sources": [source.unsigned() for source in visible_sources],
        "assertions": [assertion.unsigned() for assertion in visible_assertions],
        "documented_event_trace_ids": list(visible_event_trace),
        "grants_historical_causal_truth": False,
    }
    packet = PreCutoffCandidatePacket(
        episode_id=episode.episode_id,
        domain=episode.domain,
        cutoff=episode.cutoff,
        incumbent_regime_id=episode.incumbent_regime_id,
        target_contract_ids=episode.target_contract_ids,
        sources=visible_sources,
        assertions=visible_assertions,
        documented_event_trace_ids=visible_event_trace,
        digest=content_digest(payload),
    )
    packet.verify()
    return packet


@dataclass(frozen=True)
class FailureEpisode:
    episode_id: str
    domain: str
    cutoff: str
    incumbent_regime_id: str
    target_contract_ids: tuple[str, ...]
    sources: tuple[EpisodeSource, ...]
    assertions: tuple[EpisodeAssertion, ...]
    attempted_trace_ids: tuple[str, ...]
    observed_stage_event_ids: tuple[tuple[FailureStage, str], ...]
    visible_negative_evidence_ids: tuple[str, ...]
    contemporaneous_responsibility_hypothesis_ids: tuple[str, ...]
    retry_patch_replication_ids: tuple[str, ...]
    visibility: FailureVisibility
    successor_state_id: str
    failure_knowledge_digest: str | None
    use_mode: HistoricalUseMode
    digest: str

    @property
    def grants_scientific_refutation(self) -> bool:
        return False

    @property
    def grants_global_prohibition(self) -> bool:
        return False

    @property
    def scoped_excluded_condition_ids(self) -> tuple[str, ...]:
        # A historical/process record cannot manufacture `FailureKnowledge.v1`.
        return ()

    def stage_event_id(self, stage: FailureStage) -> str | None:
        for row_stage, event_id in self.observed_stage_event_ids:
            if row_stage is stage:
                return event_id
        return None

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "FailureEpisode.v1",
            "episode_id": self.episode_id,
            "domain": self.domain,
            "cutoff": self.cutoff,
            "incumbent_regime_id": self.incumbent_regime_id,
            "target_contract_ids": list(self.target_contract_ids),
            "sources": [source.unsigned() for source in self.sources],
            "assertions": [assertion.unsigned() for assertion in self.assertions],
            "attempted_trace_ids": list(self.attempted_trace_ids),
            "observed_stage_event_ids": [
                [stage.value, event_id] for stage, event_id in self.observed_stage_event_ids
            ],
            "visible_negative_evidence_ids": list(self.visible_negative_evidence_ids),
            "contemporaneous_responsibility_hypothesis_ids": list(
                self.contemporaneous_responsibility_hypothesis_ids
            ),
            "retry_patch_replication_ids": list(self.retry_patch_replication_ids),
            "visibility": self.visibility.value,
            "successor_state_id": self.successor_state_id,
            "failure_knowledge_digest": self.failure_knowledge_digest,
            "use_mode": self.use_mode.value,
            "grants_scientific_refutation": False,
            "grants_global_prohibition": False,
        }

    def verify(self) -> None:
        if not self.episode_id or not self.domain or not self.cutoff or not self.incumbent_regime_id:
            raise ValueError("failure episode identity/domain/cutoff/regime are required")
        if not self.target_contract_ids or not self.attempted_trace_ids:
            raise ValueError("failure episode requires target contracts and attempted trace")
        if any(not step for step in self.attempted_trace_ids):
            raise ValueError("failure attempted trace identities must be non-empty")
        if not self.visible_negative_evidence_ids:
            raise ValueError("failure episode requires at least one visible negative evidence identity")
        if not self.successor_state_id:
            raise ValueError("failure episode requires explicit successor/no-successor state")
        _validate_assertion_sources(self.sources, self.assertions)
        stages = [stage for stage, _ in self.observed_stage_event_ids]
        if len(stages) != len(set(stages)):
            raise ValueError("failure stage may appear at most once")
        if stages != sorted(stages, key=lambda stage: _FAILURE_STAGE_ORDER[stage]):
            raise ValueError("failure chronology stages must be stored in fixed process order")
        if any(not event_id for _, event_id in self.observed_stage_event_ids):
            raise ValueError("failure chronology event identities must be non-empty")
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("failure episode digest mismatch")


def build_failure_episode(
    *,
    episode_id: str,
    domain: str,
    cutoff: str,
    incumbent_regime_id: str,
    target_contract_ids: Sequence[str],
    sources: Sequence[EpisodeSource],
    assertions: Sequence[EpisodeAssertion],
    attempted_trace_ids: Sequence[str],
    stage_event_ids: Mapping[FailureStage, str],
    visible_negative_evidence_ids: Sequence[str],
    contemporaneous_responsibility_hypothesis_ids: Sequence[str],
    retry_patch_replication_ids: Sequence[str],
    visibility: FailureVisibility,
    successor_state_id: str,
    failure_knowledge_digest: str | None,
    use_mode: HistoricalUseMode | str,
) -> FailureEpisode:
    source_rows = _canonical_sources(sources)
    assertion_rows = _canonical_assertions(assertions)
    _validate_assertion_sources(source_rows, assertion_rows)
    mode = _parse_historical_use_mode(use_mode)
    stage_rows = tuple(
        sorted(
            ((FailureStage(stage), str(event_id)) for stage, event_id in stage_event_ids.items()),
            key=lambda row: _FAILURE_STAGE_ORDER[row[0]],
        )
    )
    payload = {
        "version": "FailureEpisode.v1",
        "episode_id": str(episode_id),
        "domain": str(domain),
        "cutoff": str(cutoff),
        "incumbent_regime_id": str(incumbent_regime_id),
        "target_contract_ids": list(_sorted_unique(target_contract_ids)),
        "sources": [source.unsigned() for source in source_rows],
        "assertions": [assertion.unsigned() for assertion in assertion_rows],
        "attempted_trace_ids": list(_ordered(attempted_trace_ids)),
        "observed_stage_event_ids": [[stage.value, event_id] for stage, event_id in stage_rows],
        "visible_negative_evidence_ids": list(_sorted_unique(visible_negative_evidence_ids)),
        "contemporaneous_responsibility_hypothesis_ids": list(
            _sorted_unique(contemporaneous_responsibility_hypothesis_ids)
        ),
        "retry_patch_replication_ids": list(_ordered(retry_patch_replication_ids)),
        "visibility": FailureVisibility(visibility).value,
        "successor_state_id": str(successor_state_id),
        "failure_knowledge_digest": (
            str(failure_knowledge_digest) if failure_knowledge_digest is not None else None
        ),
        "use_mode": mode.value,
        "grants_scientific_refutation": False,
        "grants_global_prohibition": False,
    }
    episode = FailureEpisode(
        episode_id=payload["episode_id"],
        domain=payload["domain"],
        cutoff=payload["cutoff"],
        incumbent_regime_id=payload["incumbent_regime_id"],
        target_contract_ids=tuple(payload["target_contract_ids"]),
        sources=source_rows,
        assertions=assertion_rows,
        attempted_trace_ids=tuple(payload["attempted_trace_ids"]),
        observed_stage_event_ids=stage_rows,
        visible_negative_evidence_ids=tuple(payload["visible_negative_evidence_ids"]),
        contemporaneous_responsibility_hypothesis_ids=tuple(
            payload["contemporaneous_responsibility_hypothesis_ids"]
        ),
        retry_patch_replication_ids=tuple(payload["retry_patch_replication_ids"]),
        visibility=FailureVisibility(payload["visibility"]),
        successor_state_id=payload["successor_state_id"],
        failure_knowledge_digest=payload["failure_knowledge_digest"],
        use_mode=mode,
        digest=content_digest(payload),
    )
    episode.verify()
    return episode


__all__ = [
    "AssertionConfidence",
    "AssertionRole",
    "DiscoveryEpisode",
    "EpisodeAssertion",
    "EpisodeSource",
    "FailureEpisode",
    "FailureStage",
    "FailureVisibility",
    "HistoricalUseMode",
    "PreCutoffCandidatePacket",
    "SourceKind",
    "SourceTemporalRelation",
    "build_discovery_episode",
    "build_episode_assertion",
    "build_episode_source",
    "build_failure_episode",
    "project_pre_cutoff_candidate_packet",
]
