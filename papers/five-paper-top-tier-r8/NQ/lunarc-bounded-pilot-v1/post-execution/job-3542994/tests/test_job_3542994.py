from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path

import jsonschema


JOB_DIR = Path(__file__).resolve().parents[1]
LUNARC_ROOT = JOB_DIR.parents[1]
ENGINE_ROOT = LUNARC_ROOT.parent / "engine-a-bounded-pilot-v1"


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_post_execution_schema_and_record_are_valid() -> None:
    schema = load_json(JOB_DIR / "post-execution-receipt.schema.json")
    record = load_json(JOB_DIR / "POST_EXECUTION_RECEIPT.json")
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(record, schema)


def test_subset_manifest_and_cross_bindings_are_exact() -> None:
    record = load_json(JOB_DIR / "POST_EXECUTION_RECEIPT.json")
    manifest = {}
    for line in (JOB_DIR / "SHA256SUMS").read_text().splitlines():
        digest, path = line.split("  ", 1)
        manifest[path] = digest
    expected_paths = {
        "ACCOUNTING.txt",
        "LUNARC_RUN_METADATA.json",
        "POST_EXECUTION_RECEIPT.json",
        "README.md",
        "SUBMISSION.json",
        "TARGET_RESOURCE_PILOT_RECEIPT.json",
        "TERMINAL.txt",
        "post-execution-receipt.schema.json",
        "tests/test_job_3542994.py",
    }
    assert set(manifest) == expected_paths
    for path, digest in manifest.items():
        assert sha256(JOB_DIR / path) == digest

    bundle = record["bundle"]
    for key in ("accounting", "metadata", "pilot_receipt", "submission", "terminal"):
        binding = bundle[key]
        assert sha256(JOB_DIR / binding["path"]) == binding["sha256"]
    authorization = bundle["authorization_packet"]
    authorization_path = (JOB_DIR / authorization["path"]).resolve()
    assert authorization_path == LUNARC_ROOT / "LUNARC_AUTHORIZATION_PACKET.json"
    assert sha256(authorization_path) == authorization["sha256"]

    frozen = record["frozen_bindings"]
    assert (
        sha256(LUNARC_ROOT / "submit_nq_engine_a_bounded_pilot.sh")
        == frozen["submit_script_sha256"]
    )
    assert sha256(ENGINE_ROOT / "TARGET_RESOURCE_PILOT_PROTOCOL.json") == frozen["protocol_sha256"]
    assert sha256(ENGINE_ROOT / "SOURCE_MANIFEST.json") == frozen["source_manifest_sha256"]


def test_job_receipts_preserve_the_engineering_only_claim_ceiling() -> None:
    record = load_json(JOB_DIR / "POST_EXECUTION_RECEIPT.json")
    submission = load_json(JOB_DIR / "SUBMISSION.json")
    metadata = load_json(JOB_DIR / "LUNARC_RUN_METADATA.json")
    receipt = load_json(JOB_DIR / "TARGET_RESOURCE_PILOT_RECEIPT.json")
    pilot_schema = load_json(ENGINE_ROOT / "schemas/target-resource-pilot-receipt.schema.json")
    jsonschema.validate(receipt, pilot_schema)

    assert (JOB_DIR / "TERMINAL.txt").read_text() == (
        "COMPLETED_ENGINEERING_PILOT_ONLY__CANNOT_CHECK\n"
    )
    assert submission["job_id"] == record["execution"]["job_id"] == "3542994"
    assert (
        submission["authorization_packet_sha256"]
        == record["frozen_bindings"]["authorization_packet_sha256"]
    )
    assert submission["source_commit"] == record["frozen_bindings"]["source_commit"]
    assert submission["source_tree"] == record["frozen_bindings"]["source_tree"]
    assert submission["submit_script_commit"] == record["frozen_bindings"]["submit_script_commit"]
    assert submission["non_duplication_key"] == record["frozen_bindings"]["non_duplication_key"]
    assert metadata["receipt_sha256"] == record["bundle"]["pilot_receipt"]["sha256"]
    assert metadata["protocol_sha256"] == record["frozen_bindings"]["protocol_sha256"]
    assert metadata["full_census_executed"] is False
    assert metadata["two_engine_pass_increment"] == 0
    assert metadata["scientific_terminal"] == "CANNOT_CHECK"
    assert metadata["independence_terminal"] == "CANNOT_CHECK"

    assert receipt["lunarc_submission"] is None
    assert receipt["full_census_executed"] is False
    assert receipt["two_engine_pass_increment"] == 0
    assert receipt["scientific_terminal"] == "CANNOT_CHECK"
    assert receipt["independence_terminal"] == "CANNOT_CHECK"
    assert receipt["exposure_markers"] == record["exposure_markers"]
    statuses = Counter(
        case["kernels"]["exact_two_bin_factorization_dp"]["status"]
        for case in receipt["target_kernel_panel"]["cases"]
    )
    assert statuses == {"NEGATIVE": 16}
    assert record["pilot_observations"]["target_panel"]["status_counts"] == {
        "CANNOT_CHECK_RESOURCE_BOUND": 0,
        "NEGATIVE": 16,
        "POSITIVE": 0,
    }
    checkpoint = receipt["checkpoint_restart"]
    assert record["pilot_observations"]["checkpoint"] == {
        "candidate_edges": checkpoint["candidate_edges"],
        "invocation_count": checkpoint["invocation_count"],
        "output_record_count": checkpoint["output_record_count"],
        "uninterrupted_restart_byte_identical": checkpoint["uninterrupted_restart_byte_identical"],
    }
    assert record["full_census_executed"] is False
    assert record["two_engine_pass_increment"] == 0
    assert record["scientific_terminal"] == "CANNOT_CHECK"
    assert record["independence_terminal"] == "CANNOT_CHECK"
