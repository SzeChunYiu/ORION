from __future__ import annotations

import json
from pathlib import Path

from orion.study.p5.v2_evidence import (
    ARCHIVE_SCHEMA_VERSION,
    PROTOCOL_ID,
    RECORD_SCHEMA_VERSION,
    RUN_SCHEMA_VERSION,
    V2_SYSTEM_ID,
    content_digest,
    result_archive_digest,
    run_manifest_digest,
    validate_result_archive,
    validate_run_manifest,
)


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = (
    ROOT / "papers" / "orion-15-self-orion" / "protocol" / "PROTOCOL_V2.json"
)
RUN_SCHEMA_PATH = (
    ROOT / "papers" / "orion-15-self-orion" / "protocol" / "P5_RUN_MANIFEST_V2_SCHEMA.json"
)
ARCHIVE_SCHEMA_PATH = (
    ROOT / "papers" / "orion-15-self-orion" / "protocol" / "P5_RESULT_ARCHIVE_V2_SCHEMA.json"
)
H64 = "a" * 64
H64_B = "b" * 64
H40 = "c" * 40


def _protocol() -> dict[str, object]:
    return json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))


def _arm(
    system_id: str,
    kind: str,
    *,
    disposition: str = "PROTOCOL_REIMPLEMENTED",
) -> dict[str, object]:
    return {
        "system_id": system_id,
        "kind": kind,
        "config_hash": content_digest(
            {"system_id": system_id, "kind": kind, "revision": 1}
        ),
        "disposition": disposition,
    }


def _manifest(protocol: dict[str, object]) -> dict[str, object]:
    arms = [_arm(V2_SYSTEM_ID, "SUBJECT")]
    arms.extend(_arm(str(item), "BASELINE") for item in protocol["baselines"])
    arms.extend(_arm(str(item), "ABLATION") for item in protocol["ablations"])
    return {
        "schema_version": RUN_SCHEMA_VERSION,
        "paper_id": "P5",
        "protocol_id": PROTOCOL_ID,
        "protocol_digest": content_digest(protocol),
        "created_before_outcome_access": True,
        "subject_revision": H40,
        "hidden_cause_suite_hash": H64,
        "split_hashes": {
            "motivating": content_digest("motivating"),
            "replay": content_digest("replay"),
            "fresh": content_digest("fresh"),
            "protected": content_digest("protected"),
        },
        "episode_ids": ["P5.CASE.001"],
        "seeds": [11, 22, 33, 44, 55],
        "model_provider_revisions": {
            "proposal": "provider/model@revision",
            "baseline": "provider/model@revision",
        },
        "evaluator": {
            "artifact_hash": H64_B,
            "evaluation_epoch": "p5-v2-epoch-001",
            "lineage_id": "external-evaluator-lineage",
        },
        "custody": {
            "candidate_lineage_id": "candidate-lineage",
            "evaluator_lineage_id": "external-evaluator-lineage",
            "host_lineage_id": "host-lineage",
            "evaluator_frozen_before_candidate": True,
            "fresh_frozen_before_candidate": True,
            "candidate_can_read_fresh_labels": False,
            "candidate_can_write_protected_evaluator": False,
            "candidate_can_delete_negative_history": False,
        },
        "pace": {
            "rule_id": "pace-paired-eprocess-v1",
            "config_hash": content_digest({"alpha": 0.05, "rule": "fixture"}),
            "error_budget": 0.05,
            "optional_stopping_allowed": True,
            "anytime_valid": True,
        },
        "resource_limits": {
            "matched_across_arms": True,
            "max_candidates": 4,
            "max_model_tokens": 10000,
            "max_tool_calls": 50,
            "max_wallclock_seconds": 1200,
            "max_evaluator_calls": 20,
        },
        "environment": {
            "python": "3.12.4",
            "dependencies_hash": content_digest({"deps": "fixture"}),
            "runner": "protected-host",
            "hardware": "fixture-hardware",
        },
        "study_arms": arms,
        "access_policy_hash": content_digest({"access": "frozen"}),
        "negative_history_root_hash": content_digest({"history": []}),
        "artifact_root": "/protected/p5-v2",
    }


def _record(
    manifest: dict[str, object],
    *,
    result_id: str,
    system_id: str,
    arm_kind: str,
    candidate_id: str,
    seed: int,
    stage: str,
    verdict: str = "PASS",
    harmful: bool = False,
    sequence_index: int | None = None,
) -> dict[str, object]:
    return {
        "schema_version": RECORD_SCHEMA_VERSION,
        "protocol_id": PROTOCOL_ID,
        "run_manifest_hash": content_digest(manifest),
        "result_id": result_id,
        "system_id": system_id,
        "arm_kind": arm_kind,
        "episode_id": "P5.CASE.001",
        "task_family": "implementation_bug",
        "candidate_id": candidate_id,
        "candidate_revision_hash": content_digest(
            {"system_id": system_id, "candidate_id": candidate_id}
        ),
        "seed": seed,
        "stage": stage,
        "sequence_index": (
            sequence_index
            if sequence_index is not None
            else {"STATIC": 10, "REPLAY": 20, "FRESH": 30, "PROTECTED": 40}[stage]
        ),
        "verdict": verdict,
        "score_delta": 0.1,
        "harmful": harmful,
        "subject_revision": H40,
        "evaluator_hash": H64_B,
        "evaluation_epoch": "p5-v2-epoch-001",
        "raw_artifact_hash": content_digest(
            {"result_id": result_id, "stage": stage}
        ),
        "negative_history_digest": content_digest(
            {"system_id": system_id, "candidate_id": candidate_id, "stage": stage}
        ),
        "cost": {
            "wallclock_seconds": 1.0,
            "model_tokens": 10,
            "tool_calls": 1,
            "evaluator_calls": 1,
        },
        "metrics": {"fixture_metric": 1.0},
    }


def _decision(
    manifest: dict[str, object],
    *,
    system_id: str,
    candidate_id: str,
    seed: int,
    decision: str,
    decision_sequence_index: int = 50,
) -> dict[str, object]:
    payload = {
        "run_manifest_hash": content_digest(manifest),
        "system_id": system_id,
        "episode_id": "P5.CASE.001",
        "seed": seed,
        "candidate_id": candidate_id,
        "decision": decision,
        "decision_sequence_index": decision_sequence_index,
    }
    return {
        **payload,
        "decision_artifact_hash": content_digest(payload),
    }


def _final_archive(
    manifest: dict[str, object],
    protocol: dict[str, object],
) -> dict[str, object]:
    records: list[dict[str, object]] = []
    decisions: list[dict[str, object]] = []
    result_index = 0
    for arm in manifest["study_arms"]:
        system_id = str(arm["system_id"])
        arm_kind = str(arm["kind"])
        if arm["disposition"] == "NOT_EXECUTABLE_WITH_JUSTIFICATION":
            continue
        for seed in manifest["seeds"]:
            candidate_id = f"{system_id}-{seed}"
            for stage in ("STATIC", "REPLAY", "FRESH", "PROTECTED"):
                result_index += 1
                records.append(
                    _record(
                        manifest,
                        result_id=f"r-{result_index}",
                        system_id=system_id,
                        arm_kind=arm_kind,
                        candidate_id=candidate_id,
                        seed=int(seed),
                        stage=stage,
                    )
                )
            decisions.append(
                _decision(
                    manifest,
                    system_id=system_id,
                    candidate_id=candidate_id,
                    seed=int(seed),
                    decision="ACCEPT",
                )
            )
    return {
        "schema_version": ARCHIVE_SCHEMA_VERSION,
        "protocol_id": PROTOCOL_ID,
        "run_manifest_hash": content_digest(manifest),
        "finalized": True,
        "final_negative_history_hash": content_digest(
            {"final": "negative-history-fixture"}
        ),
        "records": records,
        "decisions": decisions,
    }


def test_valid_run_manifest_binds_protocol_and_execution_identities() -> None:
    protocol = _protocol()
    manifest = _manifest(protocol)
    assert validate_run_manifest(manifest, protocol) == []
    assert run_manifest_digest(manifest, protocol) == content_digest(manifest)


def test_manifest_rejects_missing_split_and_unbound_identity() -> None:
    protocol = _protocol()
    manifest = _manifest(protocol)
    del manifest["split_hashes"]["protected"]
    manifest["model_provider_revisions"]["proposal"] = "UNBOUND"

    errors = validate_run_manifest(manifest, protocol)
    assert any("missing P5 V2 split hashes: protected" in error for error in errors)
    assert any("UNBOUND" in error for error in errors)


def test_manifest_rejects_custody_collapse_and_unmatched_resources() -> None:
    protocol = _protocol()
    manifest = _manifest(protocol)
    manifest["custody"]["host_lineage_id"] = manifest["custody"][
        "evaluator_lineage_id"
    ]
    manifest["resource_limits"]["matched_across_arms"] = False

    errors = validate_run_manifest(manifest, protocol)
    assert any("custody lineages must be distinct" in error for error in errors)
    assert any("matched_across_arms must be true" in error for error in errors)


def test_manifest_rejects_optional_stopping_without_anytime_valid_rule() -> None:
    protocol = _protocol()
    manifest = _manifest(protocol)
    manifest["pace"]["anytime_valid"] = False

    errors = validate_run_manifest(manifest, protocol)
    assert "pace.anytime_valid must be true" in errors


def test_manifest_requires_every_frozen_arm_and_mandatory_baseline() -> None:
    protocol = _protocol()
    manifest = _manifest(protocol)
    manifest["study_arms"] = [
        arm
        for arm in manifest["study_arms"]
        if arm["system_id"] != "replay_only"
    ]
    for arm in manifest["study_arms"]:
        if arm["system_id"] == "pace_anytime_valid_acceptance":
            arm["disposition"] = "NOT_EXECUTABLE_WITH_JUSTIFICATION"
            arm["justification_hash"] = H64

    errors = validate_run_manifest(manifest, protocol)
    assert any("missing required P5 V2 study arms: replay_only" in error for error in errors)
    assert any("mandatory baseline pace_anytime_valid_acceptance" in error for error in errors)


def test_final_archive_is_content_bound_and_complete() -> None:
    protocol = _protocol()
    manifest = _manifest(protocol)
    archive = _final_archive(manifest, protocol)

    report = validate_result_archive(archive, manifest, protocol)
    assert report["valid"] is True
    assert report["errors"] == []
    assert report["false_acceptance_count"] == 0
    assert report["fresh_harm_count"] == 0
    assert report["empirical_authority"] == "CANNOT_CHECK"


def test_archive_rejects_result_binding_mismatch() -> None:
    protocol = _protocol()
    manifest = _manifest(protocol)
    archive = _final_archive(manifest, protocol)
    archive["records"][0]["subject_revision"] = "d" * 40

    report = validate_result_archive(archive, manifest, protocol)
    assert report["valid"] is False
    assert any("subject_revision mismatch" in error for error in report["errors"])


def test_v2_decision_must_match_non_compensatory_gate() -> None:
    protocol = _protocol()
    manifest = _manifest(protocol)
    archive = _final_archive(manifest, protocol)

    v2_key = next(
        decision
        for decision in archive["decisions"]
        if decision["system_id"] == V2_SYSTEM_ID
    )
    seed = int(v2_key["seed"])
    candidate_id = str(v2_key["candidate_id"])
    for record in archive["records"]:
        if (
            record["system_id"] == V2_SYSTEM_ID
            and record["seed"] == seed
            and record["candidate_id"] == candidate_id
            and record["stage"] == "FRESH"
        ):
            record["harmful"] = True
            break

    report = validate_result_archive(archive, manifest, protocol)
    assert report["valid"] is False
    assert report["fresh_harm_count"] >= 1
    assert any("V2 candidate decision mismatch" in error for error in report["errors"])


def test_baseline_false_acceptance_is_measured_not_dropped() -> None:
    protocol = _protocol()
    manifest = _manifest(protocol)
    archive = _final_archive(manifest, protocol)

    baseline = "greedy_accept_if_score_up"
    decision = next(
        item
        for item in archive["decisions"]
        if item["system_id"] == baseline
    )
    seed = int(decision["seed"])
    candidate_id = str(decision["candidate_id"])
    for record in archive["records"]:
        if (
            record["system_id"] == baseline
            and record["seed"] == seed
            and record["candidate_id"] == candidate_id
            and record["stage"] == "PROTECTED"
        ):
            record["verdict"] = "FAIL"
            record["harmful"] = True
            break

    report = validate_result_archive(archive, manifest, protocol)
    assert report["valid"] is True
    assert report["false_acceptance_count"] == 1


def test_final_archive_rejects_coverage_drop() -> None:
    protocol = _protocol()
    manifest = _manifest(protocol)
    archive = _final_archive(manifest, protocol)

    dropped_system = "replay_only"
    dropped_seed = manifest["seeds"][0]
    archive["records"] = [
        record
        for record in archive["records"]
        if not (
            record["system_id"] == dropped_system
            and record["seed"] == dropped_seed
        )
    ]
    archive["decisions"] = [
        decision
        for decision in archive["decisions"]
        if not (
            decision["system_id"] == dropped_system
            and decision["seed"] == dropped_seed
        )
    ]

    report = validate_result_archive(archive, manifest, protocol)
    assert report["valid"] is False
    assert any("missing arm/episode/seed coverage" in error for error in report["errors"])


def test_accepted_candidate_requires_fresh_and_protected_audit() -> None:
    protocol = _protocol()
    manifest = _manifest(protocol)
    archive = _final_archive(manifest, protocol)

    baseline = "evaluator_only_acceptance"
    decision = next(
        item
        for item in archive["decisions"]
        if item["system_id"] == baseline
    )
    seed = int(decision["seed"])
    candidate_id = str(decision["candidate_id"])
    archive["records"] = [
        record
        for record in archive["records"]
        if not (
            record["system_id"] == baseline
            and record["seed"] == seed
            and record["candidate_id"] == candidate_id
            and record["stage"] == "PROTECTED"
        )
    ]

    report = validate_result_archive(archive, manifest, protocol)
    assert report["valid"] is False
    assert any("lacks a PROTECTED evaluation" in error for error in report["errors"])


def test_machine_readable_v2_evidence_schemas_are_bound() -> None:
    run_schema = json.loads(RUN_SCHEMA_PATH.read_text(encoding="utf-8"))
    archive_schema = json.loads(ARCHIVE_SCHEMA_PATH.read_text(encoding="utf-8"))

    assert run_schema["$id"] == RUN_SCHEMA_VERSION
    assert archive_schema["$id"] == ARCHIVE_SCHEMA_VERSION
    assert (
        run_schema["properties"]["protocol_id"]["const"]
        == archive_schema["properties"]["protocol_id"]["const"]
        == PROTOCOL_ID
    )


def test_v2_acceptance_requires_frozen_stage_chronology() -> None:
    protocol = _protocol()
    manifest = _manifest(protocol)
    archive = _final_archive(manifest, protocol)

    decision = next(
        item for item in archive["decisions"] if item["system_id"] == V2_SYSTEM_ID
    )
    seed = int(decision["seed"])
    candidate_id = str(decision["candidate_id"])
    for record in archive["records"]:
        if (
            record["system_id"] == V2_SYSTEM_ID
            and record["seed"] == seed
            and record["candidate_id"] == candidate_id
            and record["stage"] == "REPLAY"
        ):
            record["sequence_index"] = 35
        elif (
            record["system_id"] == V2_SYSTEM_ID
            and record["seed"] == seed
            and record["candidate_id"] == candidate_id
            and record["stage"] == "FRESH"
        ):
            record["sequence_index"] = 25

    report = validate_result_archive(archive, manifest, protocol)
    assert report["valid"] is False
    assert any("violates frozen stage chronology" in error for error in report["errors"])


def test_decision_artifact_hash_is_content_bound() -> None:
    protocol = _protocol()
    manifest = _manifest(protocol)
    archive = _final_archive(manifest, protocol)
    archive["decisions"][0]["decision"] = "REJECT"

    report = validate_result_archive(archive, manifest, protocol)
    assert report["valid"] is False
    assert any("decision_artifact_hash mismatch" in error for error in report["errors"])


def test_valid_archive_has_stable_content_digest() -> None:
    protocol = _protocol()
    manifest = _manifest(protocol)
    archive = _final_archive(manifest, protocol)

    assert result_archive_digest(archive, manifest, protocol) == content_digest(archive)
