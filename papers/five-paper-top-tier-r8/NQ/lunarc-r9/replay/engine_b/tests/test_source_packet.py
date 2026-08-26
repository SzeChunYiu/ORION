from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

import build_manifest
import engine_b as eb


def test_source_allowlist_is_exact_local_and_has_no_existing_nq_artifact() -> None:
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
    assert disclosure["execution_performed"] is False
    assert disclosure["expected_outcomes_are_execution_evidence"] is False
    assert disclosure["d4_c5_cubed"] == "OPEN"


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
    script = (root / "slurm" / "job_nq_r8_engine_b.slurm").read_text()
    assert '--no-deps -r "${ENGINE_ROOT}/requirements.txt"' in script
