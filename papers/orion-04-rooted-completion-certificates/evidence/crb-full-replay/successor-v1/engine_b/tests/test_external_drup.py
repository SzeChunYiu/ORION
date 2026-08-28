from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

import batch_engine_b as batch
import engine_b as eb
import external_drup as external


def _git(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ("git", "-C", str(root), *arguments),
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    return completed.stdout.strip()


def _write_tool(root: Path, *, verified: bool = True) -> tuple[Path, str, str]:
    root.mkdir()
    _git(root, "init", "-q")
    _git(root, "config", "user.email", "control@example.invalid")
    _git(root, "config", "user.name", "External control")
    (root / "LICENSE").write_text("MIT control fixture\n")
    checker = root / "drat-trim"
    output = "s VERIFIED" if verified else "s NOT VERIFIED"
    checker.write_text(f"#!/bin/sh\nprintf '%s\\n' '{output}'\n")
    checker.chmod(0o755)
    _git(root, "add", "LICENSE", "drat-trim")
    _git(root, "commit", "-q", "-m", "fixture")
    return checker, _git(root, "rev-parse", "HEAD"), _git(root, "rev-parse", "HEAD^{tree}")


def _write_protocol(path: Path, *, commit: str, tree: str) -> dict[str, object]:
    protocol: dict[str, object] = {
        "schema": "ORION.NQ.EngineB.ExternalDRUPProtocol.v1",
        "tool": {
            "name": "drat-trim",
            "repository": "https://github.com/marijnheule/drat-trim.git",
            "commit": commit,
            "tree": tree,
            "license": "MIT",
            "license_path": "LICENSE",
            "checker_relative_path": "drat-trim",
            "build_command": ["make", "drat-trim"],
            "invocation": ["drat-trim", "INPUT.cnf", "PROOF.drup"],
        },
        "success_contract": {
            "exit_code": 0,
            "marker": "s VERIFIED",
            "timeout_seconds": 5,
        },
        "authority": {
            "full_census_executed": False,
            "independent_replay_authority": "CANNOT_CHECK",
            "scientific_authority_delta": "NONE",
            "paper_authority_delta": "NONE",
            "d4_c5_cubed": "OPEN",
        },
    }
    path.write_text(json.dumps(protocol, indent=2, sort_keys=True) + "\n")
    return protocol


def _write_control(root: Path) -> tuple[Path, Path, Path]:
    record = {
        "schema": "ORION.NQ.EngineB.SequenceRecord.v1",
        "record_id": "negative-batch",
        "scope": "SMALL_CONTROL",
        "sequence": [1, 4, 1],
        "required_bins": 2,
    }
    records = root / "records.jsonl"
    records.write_bytes(eb.canonical_json_bytes(record) + b"\n")
    artifacts = root / "artifacts"
    artifacts.mkdir()
    encoded = eb.build_factorization_cnf(record["sequence"], record["required_bins"])
    cnf_path = artifacts / "negative-batch.cnf"
    batch.write_dimacs(encoded.cnf, cnf_path)
    proof_path = artifacts / "negative-batch.drup"
    proof_path.write_bytes(b"0\n")
    certificate = batch.build_unsat_certificate(
        record_id=record["record_id"],
        encoded=encoded,
        solver_identity="TEST_SOLVER",
        cnf_path=cnf_path,
        proof_path=proof_path,
        artifact_root=artifacts,
    )
    certificate_path = root / "certificate.json"
    certificate_path.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    return records, artifacts, certificate_path


def test_external_checker_receipt_is_source_pinned_and_authority_bounded(
    tmp_path: Path,
) -> None:
    checker, commit, tree = _write_tool(tmp_path / "tool")
    protocol_path = tmp_path / "protocol.json"
    _write_protocol(protocol_path, commit=commit, tree=tree)
    records, artifacts, certificate = _write_control(tmp_path)
    logs = tmp_path / "logs"
    receipt = external.run_external_drup(
        protocol_path=protocol_path,
        record_stream=records,
        record_id="negative-batch",
        certificate_path=certificate,
        artifact_root=artifacts,
        checker=checker,
        checker_source_root=checker.parent,
        log_root=logs,
    )
    assert receipt["execution"]["terminal"] == external.VERIFIED_TERMINAL
    assert receipt["execution"]["verified_marker_seen"] is True
    assert receipt["authority"]["full_census_executed"] is False
    assert receipt["authority"]["independent_replay_authority"] == "CANNOT_CHECK"
    assert receipt["authority"]["d4_c5_cubed"] == "OPEN"
    external.verify_external_drup_receipt(
        receipt,
        protocol_path=protocol_path,
        record_stream=records,
        certificate_path=certificate,
        artifact_root=artifacts,
        checker=checker,
        checker_source_root=checker.parent,
        log_root=logs,
    )


def test_external_checker_rejects_missing_success_marker(tmp_path: Path) -> None:
    checker, commit, tree = _write_tool(tmp_path / "tool", verified=False)
    protocol_path = tmp_path / "protocol.json"
    _write_protocol(protocol_path, commit=commit, tree=tree)
    records, artifacts, certificate = _write_control(tmp_path)
    receipt = external.run_external_drup(
        protocol_path=protocol_path,
        record_stream=records,
        record_id="negative-batch",
        certificate_path=certificate,
        artifact_root=artifacts,
        checker=checker,
        checker_source_root=checker.parent,
        log_root=tmp_path / "logs",
    )
    assert receipt["execution"]["terminal"] == external.REJECTED_TERMINAL
    assert receipt["execution"]["return_code"] == 0
    assert receipt["execution"]["verified_marker_seen"] is False


def test_external_checker_rejects_dirty_or_unpinned_source(tmp_path: Path) -> None:
    checker, commit, tree = _write_tool(tmp_path / "tool")
    protocol_path = tmp_path / "protocol.json"
    _write_protocol(protocol_path, commit=commit, tree=tree)
    records, artifacts, certificate = _write_control(tmp_path)
    (checker.parent / "LICENSE").write_text("tracked tamper\n")
    with pytest.raises(external.ExternalDRUPMismatch, match="tracked source is dirty"):
        external.run_external_drup(
            protocol_path=protocol_path,
            record_stream=records,
            record_id="negative-batch",
            certificate_path=certificate,
            artifact_root=artifacts,
            checker=checker,
            checker_source_root=checker.parent,
            log_root=tmp_path / "logs",
        )


def test_external_receipt_tamper_cannot_promote_science(tmp_path: Path) -> None:
    checker, commit, tree = _write_tool(tmp_path / "tool")
    protocol_path = tmp_path / "protocol.json"
    _write_protocol(protocol_path, commit=commit, tree=tree)
    records, artifacts, certificate = _write_control(tmp_path)
    logs = tmp_path / "logs"
    receipt = external.run_external_drup(
        protocol_path=protocol_path,
        record_stream=records,
        record_id="negative-batch",
        certificate_path=certificate,
        artifact_root=artifacts,
        checker=checker,
        checker_source_root=checker.parent,
        log_root=logs,
    )
    receipt["authority"]["scientific_authority_delta"] = "PASS"
    with pytest.raises(external.ExternalDRUPMismatch, match="digest mismatch"):
        external.verify_external_drup_receipt(
            receipt,
            protocol_path=protocol_path,
            record_stream=records,
            certificate_path=certificate,
            artifact_root=artifacts,
            checker=checker,
            checker_source_root=checker.parent,
            log_root=logs,
        )


def test_protocol_rejects_authority_promotion(tmp_path: Path) -> None:
    _, commit, tree = _write_tool(tmp_path / "tool")
    protocol_path = tmp_path / "protocol.json"
    protocol = _write_protocol(protocol_path, commit=commit, tree=tree)
    protocol["authority"]["full_census_executed"] = True
    protocol_path.write_text(json.dumps(protocol, indent=2, sort_keys=True) + "\n")
    with pytest.raises(external.ExternalDRUPMismatch, match="overstates authority"):
        external.load_protocol(protocol_path)


def test_protocol_rejects_checker_identity_substitution(tmp_path: Path) -> None:
    _, commit, tree = _write_tool(tmp_path / "tool")
    protocol_path = tmp_path / "protocol.json"
    protocol = _write_protocol(protocol_path, commit=commit, tree=tree)
    protocol["tool"]["repository"] = "https://example.invalid/substitute.git"
    protocol_path.write_text(json.dumps(protocol, indent=2, sort_keys=True) + "\n")
    with pytest.raises(external.ExternalDRUPMismatch, match="identity contract"):
        external.load_protocol(protocol_path)


def test_external_receipt_rejects_execution_tamper_even_with_resealed_digest(
    tmp_path: Path,
) -> None:
    checker, commit, tree = _write_tool(tmp_path / "tool")
    protocol_path = tmp_path / "protocol.json"
    _write_protocol(protocol_path, commit=commit, tree=tree)
    records, artifacts, certificate = _write_control(tmp_path)
    logs = tmp_path / "logs"
    receipt = external.run_external_drup(
        protocol_path=protocol_path,
        record_stream=records,
        record_id="negative-batch",
        certificate_path=certificate,
        artifact_root=artifacts,
        checker=checker,
        checker_source_root=checker.parent,
        log_root=logs,
    )
    receipt["execution"]["command"][1] = "different.cnf"
    receipt["receipt_sha256"] = external._receipt_digest(receipt)
    with pytest.raises(external.ExternalDRUPMismatch, match="command mismatch"):
        external.verify_external_drup_receipt(
            receipt,
            protocol_path=protocol_path,
            record_stream=records,
            certificate_path=certificate,
            artifact_root=artifacts,
            checker=checker,
            checker_source_root=checker.parent,
            log_root=logs,
        )
