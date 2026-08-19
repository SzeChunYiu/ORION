"""Non-authorizing closure checks for the #509 failure-atlas pilot.

The checker validates a source-grounded 30-episode pilot against the schema that
was frozen before annotation, an explicit non-structural normalization layer,
and two post-schema saturation rounds.  It can support only the bounded
``FAILURE_ATLAS_SCHEMA_STABLE`` terminal.

It deliberately cannot self-certify ``FAILURE_MORPHOLOGY_CORPUS_READY``:
independent domain-expert review is an external evidence gate and is absent in
this pilot.  A green report therefore grants neither scientific refutation nor
corpus/issue-closure authority.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

from orion.transfer.v2.canonical import content_digest


class FailureAtlasTerminal(str, Enum):
    FAILURE_ATLAS_SCHEMA_STABLE = "FAILURE_ATLAS_SCHEMA_STABLE"
    FAILURE_MORPHOLOGY_CORPUS_READY = "FAILURE_MORPHOLOGY_CORPUS_READY"
    FAILURE_ATLAS_NOT_STABLE = "FAILURE_ATLAS_NOT_STABLE"
    CANNOT_CHECK = "CANNOT_CHECK"


_REQUIRED_PRIVATE_COGNITION = "CANNOT_INFER"
_REQUIRED_HISTORICAL_USE = "MECHANISM_EXTRACTION_ONLY"
_REQUIRED_REVIEW_STATUS = "NOT_OBTAINED"


def _mapping(value: object, *, label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be an object")
    return value


def _sequence(value: object, *, label: str) -> Sequence[object]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise ValueError(f"{label} must be an array")
    return value


def _string_tuple(value: object, *, label: str) -> tuple[str, ...]:
    return tuple(str(item) for item in _sequence(value, label=label))


def _allowed(schema: Mapping[str, object], enum_name: str) -> set[str]:
    enums = _mapping(schema.get("enums", {}), label="schema enums")
    return set(_string_tuple(enums.get(enum_name, ()), label=f"enum {enum_name}"))


def _normalize(
    value: str,
    *,
    field_name: str,
    normalization: Mapping[str, object],
) -> str:
    aliases = _mapping(normalization.get("aliases", {}), label="normalization aliases")
    field_aliases = _mapping(aliases.get(field_name, {}), label=f"aliases for {field_name}")
    return str(field_aliases.get(value, value))


@dataclass(frozen=True)
class FailureAtlasClosureReport:
    episode_count: int
    shard_count: int
    domain_counts: tuple[tuple[str, int], ...]
    malformed_episode_ids: tuple[str, ...]
    enum_violation_episode_ids: tuple[str, ...]
    source_boundary_violation_episode_ids: tuple[str, ...]
    pair_mismatch_ids: tuple[str, ...]
    formal_scope_violation_episode_ids: tuple[str, ...]
    external_review_agreement_count: int
    external_review_not_obtained_count: int
    corpus_ready_eligible: bool
    normalization_material_schema_change: bool
    post_schema_round_count: int
    post_schema_primary_source_count: int
    material_change_round_ids: tuple[str, ...]
    terminal: FailureAtlasTerminal
    all_checks_passed: bool
    digest: str

    @property
    def grants_scientific_refutation(self) -> bool:
        return False

    @property
    def grants_global_prohibition(self) -> bool:
        return False

    @property
    def grants_historical_causal_truth(self) -> bool:
        return False

    @property
    def grants_corpus_ready_authority(self) -> bool:
        return False

    @property
    def grants_issue_closure_authority(self) -> bool:
        return False

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "FailureAtlasClosureReport.v1",
            "episode_count": self.episode_count,
            "shard_count": self.shard_count,
            "domain_counts": [list(item) for item in self.domain_counts],
            "malformed_episode_ids": list(self.malformed_episode_ids),
            "enum_violation_episode_ids": list(self.enum_violation_episode_ids),
            "source_boundary_violation_episode_ids": list(
                self.source_boundary_violation_episode_ids
            ),
            "pair_mismatch_ids": list(self.pair_mismatch_ids),
            "formal_scope_violation_episode_ids": list(
                self.formal_scope_violation_episode_ids
            ),
            "external_review_agreement_count": self.external_review_agreement_count,
            "external_review_not_obtained_count": self.external_review_not_obtained_count,
            "corpus_ready_eligible": self.corpus_ready_eligible,
            "normalization_material_schema_change": self.normalization_material_schema_change,
            "post_schema_round_count": self.post_schema_round_count,
            "post_schema_primary_source_count": self.post_schema_primary_source_count,
            "material_change_round_ids": list(self.material_change_round_ids),
            "terminal": self.terminal.value,
            "all_checks_passed": self.all_checks_passed,
            "grants_scientific_refutation": False,
            "grants_global_prohibition": False,
            "grants_historical_causal_truth": False,
            "grants_corpus_ready_authority": False,
            "grants_issue_closure_authority": False,
        }

    def verify(self) -> None:
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("failure atlas closure digest mismatch")


def _validate_episode(
    episode: Mapping[str, object],
    *,
    schema: Mapping[str, object],
    normalization: Mapping[str, object],
    minimum_sources: int,
    minimum_interpretations: int,
) -> tuple[list[str], list[str], list[str], str, str]:
    episode_id = str(episode.get("episode_id", "")) or "<missing-id>"
    malformed: list[str] = []
    enum_violations: list[str] = []
    source_violations: list[str] = []

    required_scalar_fields = (
        "episode_id",
        "title",
        "domain_bucket",
        "knowledge_cutoff_date",
        "incumbent_target_id",
        "incumbent_regime_id",
        "protocol_summary",
        "attempt_summary",
        "first_negative_evidence_summary",
        "first_negative_outcome_class",
        "first_negative_decisive_status",
        "failure_detection_status",
        "recognition_delay_class",
        "materiality_class",
        "responsibility_resolution_class",
        "successor_state_id",
        "successor_transition_class",
        "visibility_status",
        "private_cognition",
        "historical_use",
        "independent_domain_expert_review_status",
    )
    if any(not str(episode.get(field, "")) for field in required_scalar_fields):
        malformed.append(episode_id)

    required_array_fields = (
        "source_records",
        "response_type_ids",
        "patch_or_replication_records",
        "responsibility_hypothesis_ids",
        "excluded_scope_ids",
        "still_live_alternative_ids",
        "preserved_success_ids",
        "misstep_class_ids",
        "post_cutoff_source_ids",
        "paired_case_ids",
        "pair_relation_ids",
        "alternative_interpretations",
    )
    try:
        arrays = {
            field: _sequence(episode.get(field, ()), label=f"{field} for {episode_id}")
            for field in required_array_fields
        }
    except ValueError:
        malformed.append(episode_id)
        arrays = {field: () for field in required_array_fields}

    if len(arrays["source_records"]) < minimum_sources:
        malformed.append(episode_id)
    interpretations = tuple(str(item) for item in arrays["alternative_interpretations"])
    if (
        len(interpretations) < minimum_interpretations
        or len(set(interpretations)) < minimum_interpretations
        or any(not item for item in interpretations)
    ):
        malformed.append(episode_id)

    if episode.get("private_cognition") != _REQUIRED_PRIVATE_COGNITION:
        malformed.append(episode_id)
    if episode.get("historical_use") != _REQUIRED_HISTORICAL_USE:
        malformed.append(episode_id)
    if episode.get("protected_confirmatory_gold") is not False:
        malformed.append(episode_id)

    # Validate source identity/cutoff bookkeeping.  Later sources may live in the
    # evaluator-side atlas, but every post-cutoff source must be named explicitly.
    source_ids: set[str] = set()
    post_cutoff_ids: set[str] = set()
    pre_cutoff_source_count = 0
    for raw_source in arrays["source_records"]:
        if not isinstance(raw_source, Mapping):
            source_violations.append(episode_id)
            continue
        source_id = str(raw_source.get("source_id", ""))
        locator = str(raw_source.get("locator", ""))
        source_kind = str(raw_source.get("source_kind", ""))
        temporal = str(raw_source.get("temporal_relation", ""))
        support = raw_source.get("supported_coordinate_ids", ())
        if (
            not source_id
            or source_id in source_ids
            or not locator
            or source_kind not in _allowed(schema, "source_kind")
            or temporal not in _allowed(schema, "temporal_relation")
            or not isinstance(support, Sequence)
            or isinstance(support, (str, bytes))
            or not support
        ):
            source_violations.append(episode_id)
        source_ids.add(source_id)
        if temporal == "POST_CUTOFF":
            post_cutoff_ids.add(source_id)
        elif temporal == "PRE_OR_AT_CUTOFF":
            pre_cutoff_source_count += 1
    declared_post = set(str(item) for item in arrays["post_cutoff_source_ids"])
    if declared_post != post_cutoff_ids or pre_cutoff_source_count < 1:
        source_violations.append(episode_id)

    # Enum checks occur after the explicitly recorded non-structural aliases.
    scalar_enums = (
        "domain_bucket",
        "first_negative_outcome_class",
        "first_negative_decisive_status",
        "failure_detection_status",
        "materiality_class",
        "responsibility_resolution_class",
        "recognition_delay_class",
        "successor_transition_class",
        "visibility_status",
        "independent_domain_expert_review_status",
    )
    for field in scalar_enums:
        raw = str(episode.get(field, ""))
        canonical = _normalize(raw, field_name=field, normalization=normalization)
        if canonical not in _allowed(schema, field):
            enum_violations.append(episode_id)
    for field in ("response_type_ids", "misstep_class_ids"):
        for raw in (str(item) for item in arrays[field]):
            canonical = _normalize(raw, field_name=field, normalization=normalization)
            if canonical not in _allowed(schema, field):
                enum_violations.append(episode_id)

    decisive = str(episode.get("first_negative_decisive_status", ""))
    excluded = tuple(str(item) for item in arrays["excluded_scope_ids"])
    still_live = tuple(str(item) for item in arrays["still_live_alternative_ids"])
    if decisive == "DECISIVE_FOR_REGISTERED_CLAIM" and not excluded:
        malformed.append(episode_id)
    if not still_live:
        malformed.append(episode_id)

    review = str(episode.get("independent_domain_expert_review_status", ""))
    return (
        malformed,
        enum_violations,
        source_violations,
        review,
        episode_id,
    )


def _validate_pair_families(
    *,
    manifest: Mapping[str, object],
    by_id: Mapping[str, Mapping[str, object]],
) -> tuple[str, ...]:
    mismatches: list[str] = []
    families = _sequence(
        manifest.get("required_pair_families", ()),
        label="required pair families",
    )
    for raw_family in families:
        family = _mapping(raw_family, label="pair family")
        relation = str(family.get("pair_relation_id", ""))
        required = _string_tuple(
            family.get("required_episode_ids", ()),
            label=f"required ids for {relation}",
        )
        if not relation or not required:
            mismatches.append(relation or "<missing-pair-relation>")
            continue
        episodes: list[Mapping[str, object]] = []
        for episode_id in required:
            episode = by_id.get(episode_id)
            if episode is None:
                mismatches.append(relation)
                continue
            episodes.append(episode)
            relations = set(_string_tuple(episode.get("pair_relation_ids", ()), label="pair ids"))
            if relation not in relations:
                mismatches.append(relation)

        if family.get("require_distinct_responsibility_signatures") is True and episodes:
            signatures = {
                tuple(sorted(_string_tuple(ep.get("responsibility_hypothesis_ids", ()), label="responsibility")))
                for ep in episodes
            }
            if len(signatures) < 2:
                mismatches.append(relation)
        if family.get("require_preserved_success") is True:
            if any(not _string_tuple(ep.get("preserved_success_ids", ()), label="preserved") for ep in episodes):
                mismatches.append(relation)
        if family.get("require_nonempty_still_live_alternatives") is True:
            if any(not _string_tuple(ep.get("still_live_alternative_ids", ()), label="alternatives") for ep in episodes):
                mismatches.append(relation)
        required_detection = family.get("require_failure_detection_status")
        if required_detection:
            if any(ep.get("failure_detection_status") != required_detection for ep in episodes):
                mismatches.append(relation)

    return tuple(sorted(set(mismatches)))


def _validate_formal_scope(
    *,
    manifest: Mapping[str, object],
    by_id: Mapping[str, Mapping[str, object]],
) -> tuple[str, ...]:
    rule = _mapping(manifest.get("formal_scope_rule", {}), label="formal scope rule")
    violations: list[str] = []
    counterexample_ids = _string_tuple(
        rule.get("counterexample_episode_ids", ()),
        label="formal counterexample ids",
    )
    required_decisive = str(rule.get("required_decisive_status", ""))
    for episode_id in counterexample_ids:
        episode = by_id.get(episode_id)
        if episode is None:
            violations.append(episode_id)
            continue
        if episode.get("first_negative_outcome_class") != "FORMAL_COUNTEREXAMPLE":
            violations.append(episode_id)
        if episode.get("first_negative_decisive_status") != required_decisive:
            violations.append(episode_id)
        if not _string_tuple(episode.get("excluded_scope_ids", ()), label="formal excluded scope"):
            violations.append(episode_id)

    failed_proof_id = str(rule.get("failed_proof_episode_id", ""))
    failed_proof = by_id.get(failed_proof_id)
    if failed_proof is None:
        violations.append(failed_proof_id or "<failed-proof-id>")
    else:
        if failed_proof.get("first_negative_outcome_class") != rule.get("failed_proof_required_outcome"):
            violations.append(failed_proof_id)
        if not _string_tuple(failed_proof.get("preserved_success_ids", ()), label="failed-proof preserved"):
            violations.append(failed_proof_id)
        alternatives = set(
            _string_tuple(failed_proof.get("still_live_alternative_ids", ()), label="failed-proof alternatives")
        )
        if not any("FOUR_COLOUR_THEOREM" in item for item in alternatives):
            violations.append(failed_proof_id)
    return tuple(sorted(set(violations)))


def _analyze_saturation(
    saturation: Mapping[str, object],
) -> tuple[int, int, tuple[str, ...]]:
    rounds = _sequence(saturation.get("rounds", ()), label="saturation rounds")
    source_count = 0
    material: list[str] = []
    seen: set[str] = set()
    for raw_round in rounds:
        row = _mapping(raw_round, label="saturation round")
        round_id = str(row.get("round_id", ""))
        if not round_id or round_id in seen:
            material.append(round_id or "<duplicate-or-missing-round>")
        seen.add(round_id)
        sources = _sequence(row.get("primary_sources", ()), label=f"sources for {round_id}")
        source_count += len(sources)
        if not sources:
            material.append(round_id)
        for raw_source in sources:
            source = _mapping(raw_source, label=f"source for {round_id}")
            if not str(source.get("source_id", "")) or not str(source.get("locator", "")):
                material.append(round_id)
            if not _sequence(source.get("mapped_fields", ()), label="saturation mapped fields"):
                material.append(round_id)
        if row.get("material_change") is not False or row.get("result") != "NO_MATERIAL_CHANGE":
            material.append(round_id)
        if _sequence(row.get("new_schema_coordinate_ids", ()), label="new schema coords"):
            material.append(round_id)
    return len(rounds), source_count, tuple(sorted(set(material)))


def build_failure_atlas_closure_report(
    *,
    schema: Mapping[str, object],
    manifest: Mapping[str, object],
    shards: Sequence[Mapping[str, object]],
    normalization: Mapping[str, object],
    saturation: Mapping[str, object],
    expected: Mapping[str, object],
) -> FailureAtlasClosureReport:
    expected_pilot = _mapping(expected.get("pilot", {}), label="expected pilot")
    expected_normalization = _mapping(
        expected.get("normalization", {}), label="expected normalization"
    )
    expected_saturation = _mapping(
        expected.get("post_schema_saturation", {}), label="expected saturation"
    )

    if schema.get("version") != "FailureAtlasSchema.v1":
        raise ValueError("unexpected failure-atlas schema version")
    if manifest.get("version") != "FailureAtlasPilot.v1":
        raise ValueError("unexpected failure-atlas manifest version")
    if normalization.get("version") != "FailureAtlasNormalization.v1":
        raise ValueError("unexpected normalization version")
    if saturation.get("version") != "FailureAtlasSaturation.v1":
        raise ValueError("unexpected saturation version")

    minimum_sources = int(expected_pilot.get("minimum_source_records_per_episode", 2))
    minimum_interpretations = int(
        expected_pilot.get("minimum_alternative_interpretations_per_episode", 2)
    )

    episodes: list[Mapping[str, object]] = []
    for shard in shards:
        if shard.get("version") != "FailureAtlasPilotShard.v1":
            raise ValueError("unexpected failure-atlas shard version")
        raw_episodes = _sequence(shard.get("episodes", ()), label="shard episodes")
        episodes.extend(_mapping(raw, label="atlas episode") for raw in raw_episodes)

    ids = [str(ep.get("episode_id", "")) for ep in episodes]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate failure-atlas episode id")
    by_id = {str(ep.get("episode_id", "")): ep for ep in episodes}

    malformed: list[str] = []
    enum_violations: list[str] = []
    source_violations: list[str] = []
    reviews: Counter[str] = Counter()
    for episode in episodes:
        bad, enum_bad, source_bad, review, _ = _validate_episode(
            episode,
            schema=schema,
            normalization=normalization,
            minimum_sources=minimum_sources,
            minimum_interpretations=minimum_interpretations,
        )
        malformed.extend(bad)
        enum_violations.extend(enum_bad)
        source_violations.extend(source_bad)
        reviews[review] += 1

    pair_mismatches = _validate_pair_families(manifest=manifest, by_id=by_id)
    formal_violations = _validate_formal_scope(manifest=manifest, by_id=by_id)

    domain_counts = Counter(str(ep.get("domain_bucket", "")) for ep in episodes)
    expected_domains = {
        str(key): int(value)
        for key, value in _mapping(
            expected_pilot.get("domain_counts", {}), label="expected domain counts"
        ).items()
    }

    normalization_material_change = bool(
        normalization.get("material_schema_change", True)
    )
    alias_map = _mapping(normalization.get("aliases", {}), label="normalization alias map")
    response_alias_count = len(
        _mapping(alias_map.get("response_type_ids", {}), label="response aliases")
    )
    successor_alias_count = len(
        _mapping(
            alias_map.get("successor_transition_class", {}), label="successor aliases"
        )
    )

    round_count, saturation_source_count, material_rounds = _analyze_saturation(saturation)

    agreement_count = reviews.get("OBTAINED_AGREEMENT", 0)
    not_obtained_count = reviews.get(_REQUIRED_REVIEW_STATUS, 0)
    corpus_ready_eligible = agreement_count > 0 and not_obtained_count < len(episodes)

    all_checks_passed = (
        len(episodes) == int(expected_pilot.get("episodes", -1))
        and len(shards) == int(expected_pilot.get("shards", -1))
        and dict(domain_counts) == expected_domains
        and not malformed
        and not enum_violations
        and not source_violations
        and not pair_mismatches
        and not formal_violations
        and agreement_count
        == int(expected_pilot.get("independent_domain_expert_agreements", -1))
        and not_obtained_count
        == int(expected_pilot.get("independent_domain_expert_not_obtained", -1))
        and corpus_ready_eligible is False
        and normalization_material_change
        is bool(expected_normalization.get("material_schema_change", True))
        and normalization_material_change is False
        and response_alias_count == int(expected_normalization.get("response_aliases", -1))
        and successor_alias_count == int(expected_normalization.get("successor_aliases", -1))
        and round_count == int(expected_saturation.get("rounds", -1))
        and saturation_source_count == int(expected_saturation.get("primary_sources", -1))
        and len(material_rounds)
        == int(expected_saturation.get("material_change_rounds", -1))
        and manifest.get("candidate_terminal")
        == expected.get("candidate_terminal")
        == schema.get("candidate_terminal")
        == FailureAtlasTerminal.FAILURE_ATLAS_SCHEMA_STABLE.value
        and expected.get("forbidden_terminal_without_external_review")
        == schema.get("forbidden_self_terminal")
        == FailureAtlasTerminal.FAILURE_MORPHOLOGY_CORPUS_READY.value
    )

    terminal = (
        FailureAtlasTerminal.FAILURE_ATLAS_SCHEMA_STABLE
        if all_checks_passed
        else FailureAtlasTerminal.FAILURE_ATLAS_NOT_STABLE
    )

    payload = {
        "version": "FailureAtlasClosureReport.v1",
        "episode_count": len(episodes),
        "shard_count": len(shards),
        "domain_counts": [list(item) for item in sorted(domain_counts.items())],
        "malformed_episode_ids": sorted(set(malformed)),
        "enum_violation_episode_ids": sorted(set(enum_violations)),
        "source_boundary_violation_episode_ids": sorted(set(source_violations)),
        "pair_mismatch_ids": list(pair_mismatches),
        "formal_scope_violation_episode_ids": list(formal_violations),
        "external_review_agreement_count": agreement_count,
        "external_review_not_obtained_count": not_obtained_count,
        "corpus_ready_eligible": corpus_ready_eligible,
        "normalization_material_schema_change": normalization_material_change,
        "post_schema_round_count": round_count,
        "post_schema_primary_source_count": saturation_source_count,
        "material_change_round_ids": list(material_rounds),
        "terminal": terminal.value,
        "all_checks_passed": all_checks_passed,
        "grants_scientific_refutation": False,
        "grants_global_prohibition": False,
        "grants_historical_causal_truth": False,
        "grants_corpus_ready_authority": False,
        "grants_issue_closure_authority": False,
    }
    report = FailureAtlasClosureReport(
        episode_count=payload["episode_count"],
        shard_count=payload["shard_count"],
        domain_counts=tuple(tuple(item) for item in payload["domain_counts"]),
        malformed_episode_ids=tuple(payload["malformed_episode_ids"]),
        enum_violation_episode_ids=tuple(payload["enum_violation_episode_ids"]),
        source_boundary_violation_episode_ids=tuple(
            payload["source_boundary_violation_episode_ids"]
        ),
        pair_mismatch_ids=tuple(payload["pair_mismatch_ids"]),
        formal_scope_violation_episode_ids=tuple(
            payload["formal_scope_violation_episode_ids"]
        ),
        external_review_agreement_count=payload["external_review_agreement_count"],
        external_review_not_obtained_count=payload[
            "external_review_not_obtained_count"
        ],
        corpus_ready_eligible=payload["corpus_ready_eligible"],
        normalization_material_schema_change=payload[
            "normalization_material_schema_change"
        ],
        post_schema_round_count=payload["post_schema_round_count"],
        post_schema_primary_source_count=payload["post_schema_primary_source_count"],
        material_change_round_ids=tuple(payload["material_change_round_ids"]),
        terminal=FailureAtlasTerminal(payload["terminal"]),
        all_checks_passed=payload["all_checks_passed"],
        digest=content_digest(payload),
    )
    report.verify()
    return report


__all__ = [
    "FailureAtlasClosureReport",
    "FailureAtlasTerminal",
    "build_failure_atlas_closure_report",
]
