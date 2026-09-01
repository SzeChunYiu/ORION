from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

import batch_engine_b as batch
import engine_b as eb
import run_engine_b
import verify_receipt


def _write_bundle(root: Path, *, complete: bool = True) -> tuple[Path, Path]:
    records = (
        {
            "schema": "ORION.NQ.EngineB.SequenceRecord.v1",
            "record_id": "r0",
            "scope": "SMALL_CONTROL",
            "sequence": [0],
            "required_bins": 1,
        },
        {
            "schema": "ORION.NQ.EngineB.SequenceRecord.v1",
            "record_id": "r1",
            "scope": "SMALL_CONTROL",
            "sequence": [1, 4],
            "required_bins": 1,
        },
    )
    stream = root / "records.jsonl"
    stream.write_bytes(b"".join(eb.canonical_json_bytes(record) + b"\n" for record in records))
    coverage = root / "coverage.json"
    coverage.write_text(
        json.dumps(
            {
                "schema": "ORION.NQ.EngineB.CoverageDeclaration.v1",
                "subject_commit": eb.SUBJECT_COMMIT,
                "scope": "SMALL_CONTROL",
                "declared_complete": complete,
                "expected_record_count": len(records),
                "coverage_argument_sha256": "a" * 64,
                "generator_identity": "test-independent-generator",
                "normalization_identity": "test-no-quotient",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    return stream, coverage


def test_input_manifest_binds_canonical_stream_and_coverage(tmp_path: Path) -> None:
    stream, coverage = _write_bundle(tmp_path)
    manifest = batch.build_input_manifest(
        tmp_path,
        stream_path=stream.name,
        coverage_path=coverage.name,
    )
    bundle = batch.verify_input_manifest(tmp_path, manifest)
    assert bundle.record_count == 2
    assert bundle.scope == "SMALL_CONTROL"
    assert [record.record_id for record in batch.iter_records(bundle.stream_path)] == [
        "r0",
        "r1",
    ]
    assert len(manifest["manifest_sha256"]) == 64


def test_input_gate_rejects_incomplete_coverage_and_tamper(tmp_path: Path) -> None:
    stream, coverage = _write_bundle(tmp_path, complete=False)
    manifest = batch.build_input_manifest(
        tmp_path, stream_path=stream.name, coverage_path=coverage.name
    )
    with pytest.raises(batch.CoverageIncomplete, match="declared complete"):
        batch.verify_input_manifest(tmp_path, manifest)

    stream, coverage = _write_bundle(tmp_path, complete=True)
    manifest = batch.build_input_manifest(
        tmp_path, stream_path=stream.name, coverage_path=coverage.name
    )
    stream.write_text("tampered\n")
    with pytest.raises(batch.InputManifestMismatch, match="records.jsonl"):
        batch.verify_input_manifest(tmp_path, manifest)


def test_record_parser_rejects_noncanonical_lines_and_duplicate_ids(
    tmp_path: Path,
) -> None:
    record = {
        "schema": "ORION.NQ.EngineB.SequenceRecord.v1",
        "record_id": "same",
        "scope": "SMALL_CONTROL",
        "sequence": [0],
        "required_bins": 1,
    }
    noncanonical = tmp_path / "noncanonical.jsonl"
    noncanonical.write_text(json.dumps(record, indent=2) + "\n")
    with pytest.raises(batch.InputRecordMismatch, match="canonical"):
        tuple(batch.iter_records(noncanonical))

    duplicates = tmp_path / "duplicates.jsonl"
    line = eb.canonical_json_bytes(record) + b"\n"
    duplicates.write_bytes(line + line)
    with pytest.raises(batch.InputRecordMismatch, match="duplicate"):
        tuple(batch.iter_records(duplicates))


def test_fixture_receipt_preserves_open_and_imperfect_blinding_boundaries() -> None:
    receipt = run_engine_b.build_fixture_receipt(source_manifest_sha256="b" * 64)
    assert receipt["payload"]["terminal"] == "NQ_ENGINE_B_NON_OUTCOME_FIXTURES_VALIDATED"
    assert receipt["payload"]["d4_c5_cubed"] == "OPEN"
    assert receipt["payload"]["blinded_independence"] == "NOT_CLAIMED"
    assert receipt["payload"]["full_strata_closed"] is False
    assert receipt["payload"]["lunarc_submission"] == "NOT_SUBMITTED"
    verify_receipt.verify_receipt(receipt, expected_manifest_sha256="b" * 64)


def test_resource_limit_maps_only_to_cannot_check_resource_bound() -> None:
    receipt = batch.build_resource_bound_receipt(
        source_manifest_sha256="c" * 64,
        input_manifest_sha256="d" * 64,
        processed_records=17,
        total_records=100,
        reason="wall clock guard reached",
    )
    assert receipt["payload"]["terminal"] == "CANNOT_CHECK_RESOURCE_BOUND"
    assert receipt["payload"]["d4_c5_cubed"] == "OPEN"
    assert receipt["payload"]["processed_records"] == 17
    assert receipt["payload"]["unprocessed_records"] == 83


def test_missing_solver_maps_only_to_cannot_check_environment() -> None:
    receipt = batch.build_environment_receipt(
        source_manifest_sha256="c" * 64,
        input_manifest_sha256="d" * 64,
        total_records=100,
        reason="python-sat unavailable",
    )
    assert receipt["payload"]["terminal"] == "CANNOT_CHECK_ENVIRONMENT"
    assert receipt["payload"]["processed_records"] == 0
    assert receipt["payload"]["unprocessed_records"] == 100
    assert receipt["payload"]["d4_c5_cubed"] == "OPEN"
    verify_receipt.verify_receipt(receipt, expected_manifest_sha256="c" * 64)


def test_unsat_certificate_binds_proof_without_claiming_it_was_checked(
    tmp_path: Path,
) -> None:
    encoded = eb.build_factorization_cnf((1, 4, 1), 2)
    cnf_path = tmp_path / "r1.cnf"
    batch.write_dimacs(encoded.cnf, cnf_path)
    proof = b"0\n"
    proof_path = tmp_path / "r1.drup"
    proof_path.write_bytes(proof)
    certificate = batch.build_unsat_certificate(
        record_id="r1",
        encoded=encoded,
        solver_identity="TEST_SOLVER",
        cnf_path=cnf_path,
        proof_path=proof_path,
        artifact_root=tmp_path,
    )
    assert certificate["schema"] == "ORION.NQ.EngineB.UNSATCertificate.v2"
    assert certificate["status"] == "UNSAT_PROOF_EMITTED_REQUIRES_EXTERNAL_CHECK"
    assert certificate["cnf"]["format"] == "DIMACS_CNF"
    assert certificate["proof"]["externally_checked"] is False
    batch.verify_unsat_certificate_bindings(
        certificate,
        sequence=encoded.sequence,
        required_bins=2,
        artifact_root=tmp_path,
    )
    proof_path.write_bytes(b"tampered\n")
    with pytest.raises(eb.CertificateMismatch, match="proof"):
        batch.verify_unsat_certificate_bindings(
            certificate,
            sequence=encoded.sequence,
            required_bins=2,
            artifact_root=tmp_path,
        )


def test_unsat_certificate_rejects_semantically_different_dimacs(
    tmp_path: Path,
) -> None:
    encoded = eb.build_factorization_cnf((1, 4, 1), 2)
    cnf_path = tmp_path / "r1.cnf"
    cnf_path.write_bytes(batch.dimacs_bytes(encoded.cnf))
    proof_path = tmp_path / "r1.drup"
    proof_path.write_bytes(b"0\n")
    certificate = batch.build_unsat_certificate(
        record_id="r1",
        encoded=encoded,
        solver_identity="TEST_SOLVER",
        cnf_path=cnf_path,
        proof_path=proof_path,
        artifact_root=tmp_path,
    )
    cnf_path.write_bytes(b"p cnf 1 1\n1 0\n")
    with pytest.raises(eb.CertificateMismatch, match="cnf content"):
        batch.verify_unsat_certificate_bindings(
            certificate,
            sequence=encoded.sequence,
            required_bins=2,
            artifact_root=tmp_path,
        )


def test_unsat_certificate_cannot_promote_its_status(tmp_path: Path) -> None:
    encoded = eb.build_factorization_cnf((1, 4, 1), 2)
    cnf_path = tmp_path / "r1.cnf"
    batch.write_dimacs(encoded.cnf, cnf_path)
    proof_path = tmp_path / "r1.drup"
    proof_path.write_bytes(b"0\n")
    certificate = batch.build_unsat_certificate(
        record_id="r1",
        encoded=encoded,
        solver_identity="TEST_SOLVER",
        cnf_path=cnf_path,
        proof_path=proof_path,
        artifact_root=tmp_path,
    )
    certificate["status"] = "UNSAT_EXTERNALLY_VERIFIED"
    certificate["certificate_sha256"] = batch._certificate_digest(certificate)
    with pytest.raises(eb.CertificateMismatch, match="status mismatch"):
        batch.verify_unsat_certificate_bindings(
            certificate,
            sequence=encoded.sequence,
            required_bins=2,
            artifact_root=tmp_path,
        )


def test_slurm_script_uses_frozen_smallest_adequate_envelope() -> None:
    script = (
        Path(__file__).resolve().parents[1] / "slurm" / "job_nq_r8_engine_b.slurm"
    ).read_text()
    assert "#SBATCH --cpus-per-task=32" in script
    assert "#SBATCH --mem=128G" in script
    assert "#SBATCH --time=24:00:00" in script
    assert "#SBATCH --partition" not in script
    assert "--subject-commit " + eb.SUBJECT_COMMIT in script
    assert "NQ_ENGINE_B_AUTHORIZED_COMMIT" in script
    assert "NQ/lunarc-r9/replay/engine_b" in script
    assert "CANNOT_CHECK_RESOURCE_BOUND" in script


def test_manifest_builder_rejects_symlink_input(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside-nq.txt"
    outside.write_text("outside\n")
    (tmp_path / "records.jsonl").symlink_to(outside)
    coverage = tmp_path / "coverage.json"
    coverage.write_text("{}\n")
    with pytest.raises(ValueError, match="symlink"):
        batch.build_input_manifest(
            tmp_path,
            stream_path="records.jsonl",
            coverage_path="coverage.json",
        )


def test_receipt_digest_is_tamper_evident() -> None:
    receipt = run_engine_b.build_fixture_receipt(source_manifest_sha256="e" * 64)
    digest = receipt["receipt_sha256"]
    assert (
        digest
        == hashlib.sha256(
            eb.canonical_json_bytes({k: v for k, v in receipt.items() if k != "receipt_sha256"})
        ).hexdigest()
    )
    receipt["payload"]["d4_c5_cubed"] = "CLOSED"
    with pytest.raises(verify_receipt.ReceiptMismatch):
        verify_receipt.verify_receipt(receipt, expected_manifest_sha256="e" * 64)


def test_receipt_rejects_issue_level_pass_and_incomplete_internal_completion() -> None:
    promoted = batch.seal_receipt(
        {
            "terminal": "NQ_D2_D3_INDEPENDENT_REPLAY_PASS",
            "d4_c5_cubed": "OPEN",
            "full_strata_closed": False,
        },
        {"source_manifest_sha256": "f" * 64},
    )
    with pytest.raises(verify_receipt.ReceiptMismatch, match="allowed Engine B"):
        verify_receipt.verify_receipt(promoted, expected_manifest_sha256="f" * 64)

    incomplete = batch.seal_receipt(
        {
            "terminal": "NQ_ENGINE_B_STRUCTURAL_EXECUTION_COMPLETE",
            "processed_records": 9,
            "total_records": 10,
            "unsat_proofs_requiring_external_check": 0,
            "d4_c5_cubed": "OPEN",
            "full_strata_closed": False,
        },
        {
            "source_manifest_sha256": "f" * 64,
            "input_manifest_sha256": "a" * 64,
        },
    )
    with pytest.raises(verify_receipt.ReceiptMismatch, match="incomplete denominator"):
        verify_receipt.verify_receipt(incomplete, expected_manifest_sha256="f" * 64)


def test_parallel_dispatch_is_bounded_into_deterministic_chunks() -> None:
    assert batch.chunk_records(tuple(range(5)), 2) == ((0, 1), (2, 3), (4,))
    with pytest.raises(ValueError, match="positive"):
        batch.chunk_records((1,), 0)


def test_input_parsing_does_not_build_a_sat_formula(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    record = {
        "schema": "ORION.NQ.EngineB.SequenceRecord.v1",
        "record_id": "lightweight",
        "scope": "SMALL_CONTROL",
        "sequence": [0, 1, 2],
        "required_bins": 2,
    }
    stream = tmp_path / "records.jsonl"
    stream.write_bytes(eb.canonical_json_bytes(record) + b"\n")

    def forbidden(*args: object, **kwargs: object) -> object:
        raise AssertionError("input parsing must not materialize a SAT formula")

    monkeypatch.setattr(batch.eb, "build_factorization_cnf", forbidden)
    parsed = tuple(batch.iter_records(stream))
    assert parsed[0].sequence == (0, 1, 2)
    assert parsed[0].required_bins == 2
