from __future__ import annotations

import copy
import json
from pathlib import Path

from orion.discovery.failure_atlas_closure import FailureAtlasTerminal
from orion.discovery.failure_atlas_closure_v2 import (
    build_failure_atlas_closure_report_v2,
)


ROOT = Path(__file__).resolve().parents[3]
RESEARCH = ROOT / "research" / "extensions" / "orion-jump-recursive-atoms"
ATLAS = RESEARCH / "failure_atlas"
SCHEMA = RESEARCH / "FAILURE_ATLAS_SCHEMA_V1.json"
MANIFEST = ATLAS / "FAILURE_ATLAS_PILOT_V1.json"
NORMALIZATION = ATLAS / "FAILURE_ATLAS_NORMALIZATION_V1.json"
SATURATION = ATLAS / "FAILURE_ATLAS_SATURATION_V1.json"
EXPECTED = ATLAS / "FAILURE_ATLAS_CLOSURE_EXPECTED_V1.json"
CORRECTIONS = ATLAS / "FAILURE_ATLAS_CORRECTIONS_V2.json"
SHARDS = (
    ATLAS / "FAILURE_ATLAS_PILOT_V1_A.json",
    ATLAS / "FAILURE_ATLAS_PILOT_V1_B.json",
    ATLAS / "FAILURE_ATLAS_PILOT_V1_C.json",
)


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _shards() -> list[dict[str, object]]:
    return [_load(path) for path in SHARDS]


def _episode(shards: list[dict[str, object]], episode_id: str) -> dict[str, object]:
    for shard in shards:
        for episode in shard["episodes"]:
            if episode["episode_id"] == episode_id:
                return episode
    raise AssertionError(episode_id)


def _report(*, shards: list[dict[str, object]] | None = None):
    return build_failure_atlas_closure_report_v2(
        schema=_load(SCHEMA),
        manifest=_load(MANIFEST),
        shards=shards or _shards(),
        normalization=_load(NORMALIZATION),
        saturation=_load(SATURATION),
        expected=_load(EXPECTED),
        corrections=_load(CORRECTIONS),
    )


def test_v2_reviewer_corrections_preserve_schema_stable_terminal() -> None:
    report = _report()

    assert report.corrected_episode_ids == ("F001", "F002", "F003")
    assert report.normalized_pair_rule_count == 0
    assert report.base_report.pair_mismatch_ids == ()
    assert report.base_report.all_checks_passed is True
    assert report.terminal is FailureAtlasTerminal.FAILURE_ATLAS_SCHEMA_STABLE
    assert report.all_checks_passed is True
    assert report.grants_corpus_ready_authority is False
    assert report.grants_issue_closure_authority is False


def test_ai_preserved_success_obligation_is_now_load_bearing() -> None:
    shards = _shards()
    tampered = copy.deepcopy(shards)
    _episode(tampered, "F027")["preserved_success_ids"] = []

    report = _report(shards=tampered)

    assert "AI_FINAL_OR_PROGRAM_SUCCESS_NOT_SCIENTIFIC_VALIDITY" in (
        report.base_report.pair_mismatch_ids
    )
    assert report.all_checks_passed is False
    assert report.terminal is FailureAtlasTerminal.FAILURE_ATLAS_NOT_STABLE


def test_v2_correction_ledger_removes_michelson_morley_from_anomaly_pair() -> None:
    corrections = _load(CORRECTIONS)
    replacements = corrections["episode_field_replacements"]

    assert replacements["F001"] == {
        "paired_case_ids": [],
        "pair_relation_ids": [],
    }
    assert replacements["F002"]["paired_case_ids"] == ["F003", "F008"]
    assert replacements["F003"]["paired_case_ids"] == ["F002", "F008"]


def test_v2_does_not_rewrite_external_review_gate() -> None:
    report = _report()

    assert report.base_report.external_review_agreement_count == 0
    assert report.base_report.external_review_not_obtained_count == 30
    assert report.base_report.corpus_ready_eligible is False
    assert report.base_report.grants_corpus_ready_authority is False
