from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

pytest.importorskip("pysat.solvers")

import batch_engine_b as batch
import batch_external_drup as batch_drup
import engine_b as eb
import external_drup as drup


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


CONTROL_SPEC = (
    ("neg-batch-a", [1, 4, 1]),
    ("sat-batch-b", [1, 4, 1, 4]),
    ("neg-batch-c", [1, 4, 1]),
    ("neg-batch-d", [1, 4, 1]),
)


def _write_control(root: Path) -> tuple[Path, Path]:
    """Emit the exact execution-phase contract: one certificate per record.

    Three two-bin-negative records interleaved with one satisfiable record,
    produced by the real solver path so the SAT certificate is genuine.
    """

    records_path = root / "records.jsonl"
    certificates_path = root / "certificates.jsonl"
    artifacts = root / "artifacts"
    artifacts.mkdir()
    with records_path.open("wb") as records, certificates_path.open("wb") as certificates:
        for record_id, sequence in CONTROL_SPEC:
            record = {
                "schema": "ORION.NQ.EngineB.SequenceRecord.v1",
                "record_id": record_id,
                "scope": "SMALL_CONTROL",
                "sequence": sequence,
                "required_bins": 2,
            }
            records.write(eb.canonical_json_bytes(record) + b"\n")
            parsed = batch._parse_record_object(record)
            certificate = batch.solve_record_with_pysat(parsed, proof_root=artifacts)
            certificates.write(eb.canonical_json_bytes(certificate) + b"\n")
    return records_path, certificates_path


def _verify_arguments(root: Path) -> dict[str, object]:
    return dict(
        protocol_path=root / "protocol.json",
        record_stream=root / "records.jsonl",
        certificates_path=root / "certificates.jsonl",
        artifact_root=root / "artifacts",
        checker=root / "tool" / "drat-trim",
        checker_source_root=root / "tool",
        receipts_path=root / "receipts.jsonl",
    )


def _run_arguments(root: Path, *, receipts_name: str = "receipts.jsonl"):
    arguments = _verify_arguments(root)
    arguments["receipts_path"] = root / receipts_name
    return arguments


def _run(root: Path, *, verified: bool = True, **overrides) -> dict[str, object]:
    checker, commit, tree = _write_tool(root / "tool", verified=verified)
    _write_protocol(root / "protocol.json", commit=commit, tree=tree)
    records, certificates = _write_control(root)
    arguments = dict(
        protocol_path=root / "protocol.json",
        record_stream=records,
        certificates_path=certificates,
        artifact_root=root / "artifacts",
        checker=checker,
        checker_source_root=checker.parent,
        receipts_path=root / "receipts.jsonl",
    )
    arguments.update(overrides)
    return batch_drup.run_batch(**arguments)


def test_batch_verifies_every_unsat_certificate_and_skips_sat(tmp_path: Path) -> None:
    receipt = _run(tmp_path, threads=2, chunk_size=1)
    assert receipt["terminal"] == batch_drup.BATCH_TERMINAL
    assert receipt["counts"]["unsat_certificates"] == 3
    assert receipt["counts"]["sat_certificates_skipped"] == 1
    assert receipt["counts"]["verified"] == 3
    assert receipt["counts"]["rejected"] == 0
    assert receipt["counts"]["partial_batch"] is False
    lines = [json.loads(line) for line in (tmp_path / "receipts.jsonl").read_text().splitlines()]
    assert [line["record_id"] for line in lines] == [
        "neg-batch-a",
        "neg-batch-c",
        "neg-batch-d",
    ]
    assert "sat-batch-b" not in {line["record_id"] for line in lines}
    batch_drup.verify_batch_receipt(receipt, **_verify_arguments(tmp_path))


def test_batch_partial_run_cannot_claim_the_complete_terminal(tmp_path: Path) -> None:
    receipt = _run(tmp_path, max_records=2)
    # the truncated prefix holds one UNSAT certificate and the SAT record
    assert receipt["counts"]["unsat_certificates"] == 1
    assert receipt["counts"]["verified"] == 1
    assert receipt["counts"]["partial_batch"] is True
    assert receipt["terminal"] == batch_drup.BATCH_INCOMPLETE
    batch_drup.verify_batch_receipt(receipt, **_verify_arguments(tmp_path))


def test_batch_rejects_when_the_checker_rejects_any_certificate(tmp_path: Path) -> None:
    receipt = _run(tmp_path, verified=False)
    assert receipt["terminal"] == batch_drup.BATCH_REJECTED
    assert receipt["counts"]["rejected"] == 3


def test_batch_rejects_certificate_stream_out_of_lockstep(tmp_path: Path) -> None:
    _run(tmp_path)
    certificates = tmp_path / "certificates.jsonl"
    lines = certificates.read_bytes().splitlines(keepends=True)
    lines[0], lines[1] = lines[1], lines[0]
    certificates.write_bytes(b"".join(lines))
    with pytest.raises(batch_drup.ExternalDRUPBatchMismatch, match="lockstep"):
        batch_drup.run_batch(**_run_arguments(tmp_path))


def test_batch_rejects_record_stream_beyond_certificate_stream(tmp_path: Path) -> None:
    _run(tmp_path)
    certificates = tmp_path / "certificates.jsonl"
    lines = certificates.read_bytes().splitlines(keepends=True)
    certificates.write_bytes(b"".join(lines[:-1]))
    with pytest.raises(batch_drup.ExternalDRUPBatchMismatch, match="beyond"):
        batch_drup.run_batch(**_run_arguments(tmp_path))


def test_batch_rejects_dirty_checker_source(tmp_path: Path) -> None:
    _run(tmp_path)
    (tmp_path / "tool" / "LICENSE").write_text("tracked tamper\n")
    with pytest.raises(drup.ExternalDRUPMismatch, match="dirty"):
        batch_drup.run_batch(**_run_arguments(tmp_path))


def test_batch_receipt_tamper_cannot_promote_authority(tmp_path: Path) -> None:
    receipt = _run(tmp_path)
    receipt["authority"]["scientific_authority_delta"] = "PASS"
    with pytest.raises(batch_drup.ExternalDRUPBatchMismatch, match="digest mismatch"):
        batch_drup.verify_batch_receipt(receipt, **_verify_arguments(tmp_path))


def _reseal(receipt: dict[str, object]) -> None:
    receipt["batch_receipt_sha256"] = hashlib.sha256(
        eb.canonical_json_bytes(
            {key: value for key, value in receipt.items() if key != "batch_receipt_sha256"}
        )
    ).hexdigest()


def test_batch_receipt_rejects_resealed_partial_overclaim(tmp_path: Path) -> None:
    receipt = _run(tmp_path, max_records=2)
    receipt["counts"]["partial_batch"] = False
    _reseal(receipt)
    with pytest.raises(batch_drup.ExternalDRUPBatchMismatch, match="partial flag disagrees"):
        batch_drup.verify_batch_receipt(receipt, **_verify_arguments(tmp_path))


def test_batch_receipt_rejects_resealed_verified_overcount(tmp_path: Path) -> None:
    receipt = _run(tmp_path)
    receipt["counts"]["verified"] = 4
    _reseal(receipt)
    with pytest.raises(
        batch_drup.ExternalDRUPBatchMismatch, match="counts disagree with its lines"
    ):
        batch_drup.verify_batch_receipt(receipt, **_verify_arguments(tmp_path))


def test_batch_verify_resamples_against_the_reference_instrument(tmp_path: Path) -> None:
    receipt = _run(tmp_path)
    batch_drup.verify_batch_receipt(receipt, **_verify_arguments(tmp_path), resample=2)
