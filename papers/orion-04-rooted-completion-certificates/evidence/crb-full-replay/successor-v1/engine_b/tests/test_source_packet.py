from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

import build_evidence_manifest
import build_manifest
import build_replay_manifest
import engine_b as eb
import verify_receipt


def test_source_allowlist_is_exact_local_and_has_no_live_legacy_authorization() -> None:
    paths = build_manifest.SOURCE_PATHS
    assert paths == tuple(sorted(paths))
    assert len(paths) == len(set(paths))
    assert "engine_b.py" in paths
    assert "symmetry.py" in paths
    assert "PROOF_OF_COMPLETENESS.md" in paths
    assert "EXTERNAL_DRUP_CHECKER_PROTOCOL.json" in paths
    assert "external_drup.py" in paths
    assert "requirements.txt" in paths
    assert "tests/test_engine_b_primitives.py" in paths
    assert "tests/test_external_drup.py" in paths
    assert "replay_custody.py" in paths
    assert "submission_gate.py" in paths
    assert "verify_positive_witnesses.py" in paths
    assert "slurm/job_orion04_crb_full_replay.slurm" in paths
    assert "slurm/submit_orion04_crb_full_replay.sh" in paths
    assert "FULL_REPLAY_AUTHORIZATION.json" not in paths
    assert all(not path.startswith("../") for path in paths)
    assert all("x1f" not in path.lower() and "result" not in path.lower() for path in paths)


def test_source_manifest_is_deterministic_and_tamper_evident(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("a\n")
    (tmp_path / "b.txt").write_text("b\n")
    first = build_manifest.build_source_manifest(tmp_path, ("b.txt", "a.txt"))
    second = build_manifest.build_source_manifest(tmp_path, ("a.txt", "b.txt"))
    assert first == second
    build_manifest.verify_source_manifest(tmp_path, first)
    (tmp_path / "a.txt").write_text("tampered\n")
    with pytest.raises(build_manifest.SourceManifestMismatch, match="a.txt"):
        build_manifest.verify_source_manifest(tmp_path, first)


def test_source_manifest_rejects_symlinks(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside-engine-b.txt"
    outside.write_text("outside\n")
    (tmp_path / "escape.txt").symlink_to(outside)
    with pytest.raises(ValueError, match="symlink"):
        build_manifest.build_source_manifest(tmp_path, ("escape.txt",))


def test_checked_in_evidence_manifest_is_exact_and_tamper_evident() -> None:
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / "EVIDENCE_MANIFEST.json").read_text())
    build_evidence_manifest.verify_evidence_manifest(root, manifest)
    assert tuple(item["path"] for item in manifest["files"]) == (
        build_evidence_manifest.EVIDENCE_PATHS
    )
    assert "SOURCE_MANIFEST.json" in build_evidence_manifest.EVIDENCE_PATHS
    assert all(
        "FULL_REPLAY_AUTHORIZATION" not in path for path in build_evidence_manifest.EVIDENCE_PATHS
    )


def test_checked_in_replay_manifest_binds_successor_without_live_authorization() -> None:
    successor = Path(__file__).resolve().parents[2]
    manifest = json.loads((successor / "REPLAY_SOURCE_MANIFEST_V1.json").read_text())
    build_replay_manifest.verify_replay_manifest(successor, manifest)
    expected_base = "fafe9c2c8ebeffbfde673a8a4d4194d9733cce04"
    assert build_replay_manifest.CURRENT_MAIN_BASE == expected_base
    assert manifest["current_main_base"] == expected_base
    paths = tuple(item["path"] for item in manifest["files"])
    assert paths == build_replay_manifest.REPLAY_PATHS
    assert "AWAITING_NEW_ONE_SHOT_AUTHORIZATION.json" in paths
    assert all(Path(path).name != "ONE_SHOT_AUTHORIZATION.json" for path in paths)


def test_completeness_argument_states_bijection_and_coverage_boundary() -> None:
    root = Path(__file__).resolve().parents[1]
    proof = (root / "PROOF_OF_COMPLETENESS.md").read_text()
    for required in (
        "Soundness",
        "Completeness",
        "primitive `C_5^3` addition",
        "no pruning",
        "input-coverage declaration",
        "does not close `D_4(C_5^3)`",
    ):
        assert required in proof


def test_blinding_disclosure_records_exposed_values_as_expectations_only() -> None:
    root = Path(__file__).resolve().parents[1]
    disclosure = json.loads((root / "BLINDING_DISCLOSURE.json").read_text())
    assert disclosure["blinded_independence"] == "NOT_CLAIMED"
    assert disclosure["execution_attempted"] is True
    assert disclosure["valid_d2_d3_execution"] is False
    assert disclosure["failed_job"] == 3544056
    assert disclosure["expected_outcomes_are_execution_evidence"] is False
    assert disclosure["d4_c5_cubed"] == "OPEN"


def test_checked_non_outcome_receipt_is_post_failure_local_only_and_current_bound() -> None:
    root = Path(__file__).resolve().parents[1]
    successor = root.parent
    source = json.loads((root / "SOURCE_MANIFEST.json").read_text())
    receipt = json.loads((root / "NON_OUTCOME_VALIDATION.json").read_text())
    failure_binding = successor / "PRESERVED_FAILURE_BINDING_V1.json"
    assert receipt["bindings"]["source_manifest_sha256"] == source["manifest_sha256"]
    assert (
        receipt["bindings"]["preserved_failure_binding_sha256"]
        == hashlib.sha256(failure_binding.read_bytes()).hexdigest()
    )
    assert receipt["schema"] == "ORION.ORION04.CRB.PostFailureLocalFixtureValidation.v1"
    assert receipt["terminal"] == ("ORION04_POST_FAILURE_LOCAL_FIXTURES_VALIDATED_NO_SCIENCE_DELTA")
    assert receipt["validation_context"] == "POST_FAILURE_LOCAL_FIXTURES_ONLY"
    assert receipt["local_fixture_lunarc_submission"] == "NOT_SUBMITTED_LOCAL_ONLY"
    assert receipt["lunarc_submission"] == "HISTORICAL_JOB_3544056_SUBMITTED_AND_FAILED"
    assert receipt["historical_job"] == {
        "job_id": 3544056,
        "scheduler_state": "FAILED",
        "valid_d2_outcome": False,
        "valid_d3_outcome": False,
        "d2_authority": "CANNOT_CHECK",
        "d3_authority": "CANNOT_CHECK",
        "failure_terminal": (
            "NQ_CRB_FULL_REPLAY_JOB_3544056_FAILED_CENSUS_RECEIPT_SERIALIZATION__"
            "D2_D3_AUTHORITY_CANNOT_CHECK"
        ),
    }
    assert receipt["full_strata_closed"] is False
    assert receipt["authority"]["scientific_authority_delta"] == "NONE"
    core = {key: value for key, value in receipt.items() if key != "receipt_sha256"}
    assert receipt["receipt_sha256"] == hashlib.sha256(eb.canonical_json_bytes(core)).hexdigest()
    verify_receipt.verify_receipt(
        receipt["local_fixture_receipt"],
        expected_manifest_sha256=source["manifest_sha256"],
    )


def test_protocol_never_promotes_partial_strata_or_resource_limit() -> None:
    root = Path(__file__).resolve().parents[1]
    protocol = json.loads((root / "SOURCE_PROTOCOL.json").read_text())
    assert protocol["subject_commit"] == eb.SUBJECT_COMMIT
    assert protocol["d4_policy"]["default"] == "OPEN"
    assert protocol["d4_policy"]["resource_exhaustion"] == "CANNOT_CHECK_RESOURCE_BOUND"
    assert protocol["d4_policy"]["partial_stratum"] == "OPEN"
    assert protocol["architecture"]["existing_nq_algorithm_read_or_imported"] is False


def test_input_schema_hash_is_stable_and_declares_exact_record_fields() -> None:
    root = Path(__file__).resolve().parents[1]
    raw = (root / "INPUT_SCHEMA.json").read_bytes()
    schema = json.loads(raw)
    assert schema["$id"] == "ORION.NQ.EngineB.InputSchemas.v1"
    required = schema["$defs"]["sequence_record"]["required"]
    assert set(required) == {
        "schema",
        "record_id",
        "scope",
        "sequence",
        "required_bins",
    }
    assert schema["sha256_policy"] == "canonical JSONL records plus byte-exact file manifests"
    assert hashlib.sha256(raw).hexdigest() != "0" * 64


def test_solver_runtime_is_local_and_exactly_pinned() -> None:
    root = Path(__file__).resolve().parents[1]
    requirements = (root / "requirements.txt").read_text().splitlines()
    assert requirements == ["python-sat==1.9.dev15", "six==1.17.0"]
    script = (root / "slurm" / "job_orion04_crb_full_replay.slurm").read_text()
    assert '--no-deps -r "${ENGINE_ROOT}/requirements.txt"' in script
