from __future__ import annotations

from pathlib import Path
import runpy

from orion.study.p5.v2_evidence import validate_result_archive


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
