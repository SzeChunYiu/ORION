"""Reviewer-corrected operational closure for the #509 failure-atlas pilot.

V1 remains immutable research history. This V2 adapter applies a tiny, explicit
annotation correction ledger before delegating to the frozen V1 closure checker.
The AI preserved-success obligation is now repaired directly in the manifest;
V2 only removes Michelson--Morley from the unexpected-physical-signal pair
family. No source, scientific terminal, external-review status, or authority
boundary is changed by this adapter.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Mapping, Sequence

from orion.discovery.failure_atlas_closure import (
    FailureAtlasClosureReport,
    FailureAtlasTerminal,
    build_failure_atlas_closure_report,
)
from orion.transfer.v2.canonical import content_digest


@dataclass(frozen=True)
class FailureAtlasClosureReportV2:
    base_report: FailureAtlasClosureReport
    corrected_episode_ids: tuple[str, ...]
    normalized_pair_rule_count: int
    terminal: FailureAtlasTerminal
    all_checks_passed: bool
    digest: str

    @property
    def grants_corpus_ready_authority(self) -> bool:
        return False

    @property
    def grants_issue_closure_authority(self) -> bool:
        return False

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "FailureAtlasClosureReport.v2",
            "base_report_digest": self.base_report.digest,
            "corrected_episode_ids": list(self.corrected_episode_ids),
            "normalized_pair_rule_count": self.normalized_pair_rule_count,
            "terminal": self.terminal.value,
            "all_checks_passed": self.all_checks_passed,
            "grants_corpus_ready_authority": False,
            "grants_issue_closure_authority": False,
        }

    def verify(self) -> None:
        self.base_report.verify()
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("failure atlas V2 closure digest mismatch")


def _apply_corrections(
    *,
    manifest: Mapping[str, object],
    shards: Sequence[Mapping[str, object]],
    corrections: Mapping[str, object],
) -> tuple[dict[str, object], list[dict[str, object]], tuple[str, ...], int]:
    if corrections.get("version") != "FailureAtlasCorrections.v2":
        raise ValueError("unexpected failure-atlas correction version")
    if corrections.get("outcome_accessed") is not False:
        raise ValueError("failure-atlas corrections must be pre-outcome/reviewer-driven")

    corrected_manifest = copy.deepcopy(dict(manifest))
    corrected_shards = [copy.deepcopy(dict(shard)) for shard in shards]

    replacements = corrections.get("episode_field_replacements", {})
    if not isinstance(replacements, Mapping):
        raise ValueError("episode_field_replacements must be an object")

    by_id: dict[str, dict[str, object]] = {}
    for shard in corrected_shards:
        episodes = shard.get("episodes", [])
        if not isinstance(episodes, list):
            raise ValueError("shard episodes must be a list")
        for episode in episodes:
            if not isinstance(episode, dict):
                raise ValueError("episode must be an object")
            episode_id = str(episode.get("episode_id", ""))
            if episode_id:
                by_id[episode_id] = episode

    corrected_ids: list[str] = []
    for raw_episode_id, raw_fields in replacements.items():
        episode_id = str(raw_episode_id)
        episode = by_id.get(episode_id)
        if episode is None:
            raise ValueError(f"correction references unknown episode {episode_id}")
        if not isinstance(raw_fields, Mapping):
            raise ValueError("episode correction fields must be an object")
        for field_name, value in raw_fields.items():
            episode[str(field_name)] = copy.deepcopy(value)
        corrected_ids.append(episode_id)

    aliases = corrections.get("pair_family_rule_aliases", {})
    if not isinstance(aliases, Mapping):
        raise ValueError("pair_family_rule_aliases must be an object")
    normalized_count = 0
    families = corrected_manifest.get("required_pair_families", [])
    if not isinstance(families, list):
        raise ValueError("required_pair_families must be a list")
    for family in families:
        if not isinstance(family, dict):
            raise ValueError("pair family must be an object")
        for source_key, target_key in aliases.items():
            source = str(source_key)
            target = str(target_key)
            if source in family:
                family[target] = family[source]
                normalized_count += 1

    corrected_manifest["version"] = "FailureAtlasPilot.v1"
    return corrected_manifest, corrected_shards, tuple(sorted(corrected_ids)), normalized_count


def build_failure_atlas_closure_report_v2(
    *,
    schema: Mapping[str, object],
    manifest: Mapping[str, object],
    shards: Sequence[Mapping[str, object]],
    normalization: Mapping[str, object],
    saturation: Mapping[str, object],
    expected: Mapping[str, object],
    corrections: Mapping[str, object],
) -> FailureAtlasClosureReportV2:
    corrected_manifest, corrected_shards, corrected_ids, normalized_count = _apply_corrections(
        manifest=manifest,
        shards=shards,
        corrections=corrections,
    )
    expected_corrections = corrections.get("expected_corrections", {})
    if not isinstance(expected_corrections, Mapping):
        raise ValueError("expected_corrections must be an object")

    base = build_failure_atlas_closure_report(
        schema=schema,
        manifest=corrected_manifest,
        shards=corrected_shards,
        normalization=normalization,
        saturation=saturation,
        expected=expected,
    )

    all_checks_passed = (
        base.all_checks_passed
        and len(corrected_ids) == int(expected_corrections.get("episode_rows_touched", -1))
        and normalized_count == int(expected_corrections.get("pair_rule_aliases", -1))
        and corrected_ids == ("F001", "F002", "F003")
        and normalized_count == 0
    )
    terminal = (
        FailureAtlasTerminal.FAILURE_ATLAS_SCHEMA_STABLE
        if all_checks_passed
        else FailureAtlasTerminal.FAILURE_ATLAS_NOT_STABLE
    )
    payload = {
        "version": "FailureAtlasClosureReport.v2",
        "base_report_digest": base.digest,
        "corrected_episode_ids": list(corrected_ids),
        "normalized_pair_rule_count": normalized_count,
        "terminal": terminal.value,
        "all_checks_passed": all_checks_passed,
        "grants_corpus_ready_authority": False,
        "grants_issue_closure_authority": False,
    }
    report = FailureAtlasClosureReportV2(
        base_report=base,
        corrected_episode_ids=corrected_ids,
        normalized_pair_rule_count=normalized_count,
        terminal=terminal,
        all_checks_passed=all_checks_passed,
        digest=content_digest(payload),
    )
    report.verify()
    return report


__all__ = [
    "FailureAtlasClosureReportV2",
    "build_failure_atlas_closure_report_v2",
]
