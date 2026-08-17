from __future__ import annotations

from pathlib import Path
import runpy

from orion.study.p5.v2_evidence import (
    V2_SYSTEM_ID,
    content_digest,
    decision_unsigned_payload,
    validate_result_archive,
    validate_run_manifest,
)


_HELPERS = runpy.run_path(str(Path(__file__).with_name("test_p5_v2_evidence.py")))
_protocol = _HELPERS["_protocol"]
_manifest = _HELPERS["_manifest"]
_final_archive = _HELPERS["_final_archive"]


def test_negative_cost_is_invalid_without_crashing_validator() -> None:
    protocol = _protocol()
    manifest = _manifest(protocol)
    archive = _final_archive(manifest, protocol)
    archive["records"][0]["cost"]["wallclock_seconds"] = -1.0

    report = validate_result_archive(archive, manifest, protocol)

    assert report["valid"] is False
    assert report["empirical_authority"] == "CANNOT_CHECK"
    assert any(
        "cost.wallclock_seconds must be non-negative" in error
        for error in report["errors"]
    )


def test_invalid_manifest_report_keeps_explicit_non_authority_marker() -> None:
    protocol = _protocol()
    manifest = _manifest(protocol)
    archive = _final_archive(manifest, protocol)
    del manifest["split_hashes"]["protected"]

    report = validate_result_archive(archive, manifest, protocol)

    assert report["valid"] is False
    assert report["empirical_authority"] == "CANNOT_CHECK"
    assert report["run_manifest_hash"] is None
    assert report["record_count"] == 0
    assert report["candidate_count"] == 0
    assert report["decision_counts"] == {}


def test_boolean_seed_is_rejected_in_manifest_and_archive_identity() -> None:
    protocol = _protocol()
    manifest = _manifest(protocol)
    manifest["seeds"][0] = True

    errors = validate_run_manifest(manifest, protocol)
    assert any("non-boolean integers" in error for error in errors)

    manifest = _manifest(protocol)
    manifest["seeds"][0] = 1
    archive = _final_archive(manifest, protocol)
    archive["records"][0]["seed"] = True

    report = validate_result_archive(archive, manifest, protocol)
    assert report["valid"] is False
    assert any("seed must be a non-boolean integer" in error for error in report["errors"])


def test_early_reject_may_retain_later_hostile_stage_evidence() -> None:
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
            record["verdict"] = "FAIL"
            record["sequence_index"] = 20
        elif (
            record["system_id"] == V2_SYSTEM_ID
            and record["seed"] == seed
            and record["candidate_id"] == candidate_id
            and record["stage"] == "FRESH"
        ):
            record["sequence_index"] = 30
        elif (
            record["system_id"] == V2_SYSTEM_ID
            and record["seed"] == seed
            and record["candidate_id"] == candidate_id
            and record["stage"] == "PROTECTED"
        ):
            record["sequence_index"] = 40

    decision["decision"] = "REJECT"
    decision["decision_sequence_index"] = 25
    decision["decision_artifact_hash"] = content_digest(
        decision_unsigned_payload(decision)
    )

    report = validate_result_archive(archive, manifest, protocol)
    assert report["valid"] is True
    assert not any("predates retained stage evidence" in error for error in report["errors"])
