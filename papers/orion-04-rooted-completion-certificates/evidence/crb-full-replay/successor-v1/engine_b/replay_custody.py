#!/usr/bin/env python3
"""Durable custody primitives for the ORION-04 CR-B replay successor.

This module deliberately records process and transport facts only.  Its
receipts are not scientific terminals and cannot promote D2, D3, or D4.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import socket
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

import engine_b as eb


class CustodyMismatch(RuntimeError):
    """A durable artifact is missing, corrupt, or structurally unsafe."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _digest(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(eb.canonical_json_bytes(value)).hexdigest()


def _atomic_json(path: Path, value: Mapping[str, Any], *, exclusive: bool = False) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = eb.canonical_json_bytes(value) + b"\n"
    if exclusive:
        try:
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            return False
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        return True
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with temporary.open("wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    return True


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _checkpoint_files(source_root: Path) -> tuple[Path, ...]:
    if not source_root.is_dir() or source_root.is_symlink():
        raise CustodyMismatch(f"phase-1 source is unavailable or unsafe: {source_root}")
    files: list[Path] = []
    for path in sorted(source_root.rglob("*")):
        if path.is_symlink():
            raise CustodyMismatch(f"phase-1 source contains a symlink: {path}")
        if path.is_file():
            files.append(path)
    if not files:
        raise CustodyMismatch("phase-1 source contains no files")
    return tuple(files)


def create_phase1_checkpoint(source_root: Path, destination: Path) -> dict[str, Any]:
    """Copy every phase-1 file durably, hash it, verify it, then publish atomically."""

    source_root = source_root.absolute()
    if source_root.is_symlink():
        raise CustodyMismatch(f"phase-1 source is unavailable or unsafe: {source_root}")
    destination = destination.absolute()
    if destination.exists() or destination.is_symlink():
        raise CustodyMismatch(f"checkpoint destination already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    stage = destination.with_name(f".{destination.name}.{os.getpid()}.tmp")
    if stage.exists() or stage.is_symlink():
        raise CustodyMismatch(f"checkpoint staging path already exists: {stage}")
    stage.mkdir(mode=0o700)
    records: list[dict[str, Any]] = []
    total_bytes = 0
    try:
        for source in _checkpoint_files(source_root):
            relative = source.relative_to(source_root).as_posix()
            target = stage / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            with source.open("rb") as reader, target.open("xb") as writer:
                shutil.copyfileobj(reader, writer, 1 << 20)
                writer.flush()
                os.fsync(writer.fileno())
            size = target.stat().st_size
            digest = _sha256(target)
            if size != source.stat().st_size or digest != _sha256(source):
                raise CustodyMismatch(f"copy verification failed: {relative}")
            records.append({"path": relative, "bytes": size, "sha256": digest})
            total_bytes += size
        core: dict[str, Any] = {
            "schema": "ORION.ORION04.CRB.Phase1Checkpoint.v1",
            "terminal": "ORION04_CRB_PHASE1_CHECKPOINT_DURABLE",
            "scientific_authority_delta": "NONE",
            "file_count": len(records),
            "total_bytes": total_bytes,
            "files": records,
        }
        receipt = {**core, "checkpoint_sha256": _digest(core)}
        _atomic_json(stage / "CHECKPOINT_RECEIPT.json", receipt)
        (stage / "SHA256SUMS").write_text(
            "".join(f"{item['sha256']}  {item['path']}\n" for item in records),
            encoding="ascii",
        )
        with (stage / "SHA256SUMS").open("rb") as stream:
            os.fsync(stream.fileno())
        _fsync_directory(stage)
        os.replace(stage, destination)
        _fsync_directory(destination.parent)
        verify_phase1_checkpoint(destination)
        return receipt
    except BaseException:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def verify_phase1_checkpoint(destination: Path) -> dict[str, Any]:
    if not destination.is_dir() or destination.is_symlink():
        raise CustodyMismatch(f"checkpoint is unavailable or unsafe: {destination}")
    receipt_path = destination / "CHECKPOINT_RECEIPT.json"
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise CustodyMismatch("checkpoint receipt is unavailable or malformed") from error
    if receipt.get("schema") != "ORION.ORION04.CRB.Phase1Checkpoint.v1":
        raise CustodyMismatch("checkpoint receipt schema mismatch")
    if receipt.get("terminal") != "ORION04_CRB_PHASE1_CHECKPOINT_DURABLE":
        raise CustodyMismatch("checkpoint receipt terminal mismatch")
    core = {key: value for key, value in receipt.items() if key != "checkpoint_sha256"}
    if receipt.get("checkpoint_sha256") != _digest(core):
        raise CustodyMismatch("checkpoint receipt digest mismatch")
    records = receipt.get("files")
    if type(records) is not list or any(
        type(item) is not dict or set(item) != {"path", "bytes", "sha256"} for item in records
    ):
        raise CustodyMismatch("checkpoint file ledger is malformed")
    expected_paths = {item["path"] for item in records}
    if len(expected_paths) != len(records):
        raise CustodyMismatch("checkpoint file ledger contains duplicate paths")
    actual_paths = {
        path.relative_to(destination).as_posix()
        for path in destination.rglob("*")
        if path.is_file() and path.name not in {"CHECKPOINT_RECEIPT.json", "SHA256SUMS"}
    }
    if actual_paths != expected_paths:
        raise CustodyMismatch("checkpoint file set mismatch")
    for item in records:
        relative = Path(item["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise CustodyMismatch("checkpoint ledger path is not canonical")
        path = destination / relative
        if path.is_symlink() or path.stat().st_size != item["bytes"]:
            raise CustodyMismatch(f"checkpoint size mismatch: {item['path']}")
        if _sha256(path) != item["sha256"]:
            raise CustodyMismatch(f"checkpoint digest mismatch: {item['path']}")
    expected_ledger = "".join(f"{item['sha256']}  {item['path']}\n" for item in records)
    if (destination / "SHA256SUMS").read_text(encoding="ascii") != expected_ledger:
        raise CustodyMismatch("checkpoint SHA256SUMS mismatch")
    return receipt


def write_environment_receipt(
    durable_root: Path,
    *,
    job_id: str,
    authorized_commit: str,
    source_manifest_sha256: str,
    authorization_sha256: str,
    global_registry_root: str,
) -> dict[str, Any]:
    core: dict[str, Any] = {
        "schema": "ORION.ORION04.CRB.EnvironmentReceipt.v1",
        "captured_at_utc": _utc_now(),
        "job_id": job_id,
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "authorized_commit": authorized_commit,
        "source_manifest_sha256": source_manifest_sha256,
        "authorization_sha256": authorization_sha256,
        "durable_root": str(durable_root.absolute()),
        "global_registry_root": global_registry_root,
        "scientific_authority_delta": "NONE",
    }
    receipt = {**core, "receipt_sha256": _digest(core)}
    _atomic_json(durable_root / "ENVIRONMENT_RECEIPT.json", receipt)
    return receipt


def write_first_failure(
    durable_root: Path,
    *,
    exit_code: int,
    line: int,
    command: str,
    phase: str,
) -> bool:
    core: dict[str, Any] = {
        "schema": "ORION.ORION04.CRB.FirstFailure.v1",
        "captured_at_utc": _utc_now(),
        "exit_code": int(exit_code),
        "line": int(line),
        "command": command,
        "phase": phase,
        "scientific_authority_delta": "NONE",
    }
    receipt = {**core, "receipt_sha256": _digest(core)}
    return _atomic_json(durable_root / "FIRST_FAILURE.json", receipt, exclusive=True)


def write_exit_receipt(durable_root: Path, *, exit_code: int, phase: str) -> dict[str, Any]:
    core: dict[str, Any] = {
        "schema": "ORION.ORION04.CRB.ProcessExitReceipt.v1",
        "captured_at_utc": _utc_now(),
        "exit_code": int(exit_code),
        "phase": phase,
        "terminal": (
            "ORION04_CRB_PROCESS_EXIT_SUCCESS"
            if int(exit_code) == 0
            else "ORION04_CRB_PROCESS_EXIT_FAILURE"
        ),
        "scientific_authority_delta": "NONE",
    }
    receipt = {**core, "receipt_sha256": _digest(core)}
    _atomic_json(durable_root / "EXIT_RECEIPT.json", receipt)
    return receipt


def write_submission_failure(
    durable_root: Path,
    *,
    exit_code: int,
    stage: str,
    command: str,
    nonduplication_key: str,
    job_id: int | None,
    scheduler_reconciliation: str,
    registry_terminalization: str,
) -> dict[str, Any]:
    """Record process custody for a failed post-reservation submit path."""

    core: dict[str, Any] = {
        "schema": "ORION.ORION04.CRB.SubmissionFailure.v1",
        "captured_at_utc": _utc_now(),
        "terminal": "ORION04_SUBMISSION_FAILED_KEY_CONSUMED",
        "exit_code": int(exit_code),
        "stage": stage,
        "command": command,
        "nonduplication_key": nonduplication_key,
        "job_id": job_id,
        "scheduler_reconciliation": scheduler_reconciliation,
        "registry_terminalization": registry_terminalization,
        "operator_attestation": "USER_SUPPLIED_UNVERIFIED_BY_MACHINE",
        "machine_established_externality": False,
        "scientific_authority_delta": "NONE",
    }
    receipt = {**core, "receipt_sha256": _digest(core)}
    _atomic_json(durable_root / "SUBMISSION_FAILURE.json", receipt)
    return receipt


def _git_output(repository: Path, *args: str) -> str:
    return subprocess.run(
        ("git", "-C", str(repository), *args),
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ).stdout.strip()


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    create = subparsers.add_parser("create-phase1-checkpoint")
    create.add_argument("source", type=Path)
    create.add_argument("destination", type=Path)
    verify = subparsers.add_parser("verify-phase1-checkpoint")
    verify.add_argument("destination", type=Path)
    environment = subparsers.add_parser("capture-environment")
    environment.add_argument("durable_root", type=Path)
    environment.add_argument("--job-id", required=True)
    environment.add_argument("--authorized-commit", required=True)
    environment.add_argument("--source-manifest-sha256", required=True)
    environment.add_argument("--authorization-sha256", required=True)
    environment.add_argument("--global-registry-root", required=True)
    failure = subparsers.add_parser("first-failure")
    failure.add_argument("durable_root", type=Path)
    failure.add_argument("--exit-code", type=int, required=True)
    failure.add_argument("--line", type=int, required=True)
    failure.add_argument("--command", required=True)
    failure.add_argument("--phase", required=True)
    exiting = subparsers.add_parser("exit-receipt")
    exiting.add_argument("durable_root", type=Path)
    exiting.add_argument("--exit-code", type=int, required=True)
    exiting.add_argument("--phase", required=True)
    submission_failure = subparsers.add_parser("submission-failure")
    submission_failure.add_argument("durable_root", type=Path)
    submission_failure.add_argument("--exit-code", type=int, required=True)
    submission_failure.add_argument("--stage", required=True)
    submission_failure.add_argument("--command", required=True)
    submission_failure.add_argument("--nonduplication-key", required=True)
    submission_failure.add_argument("--job-id", type=int)
    submission_failure.add_argument("--scheduler-reconciliation", required=True)
    submission_failure.add_argument("--registry-terminalization", required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "create-phase1-checkpoint":
        receipt = create_phase1_checkpoint(args.source, args.destination)
    elif args.command == "verify-phase1-checkpoint":
        receipt = verify_phase1_checkpoint(args.destination)
    elif args.command == "capture-environment":
        receipt = write_environment_receipt(
            args.durable_root,
            job_id=args.job_id,
            authorized_commit=args.authorized_commit,
            source_manifest_sha256=args.source_manifest_sha256,
            authorization_sha256=args.authorization_sha256,
            global_registry_root=args.global_registry_root,
        )
    elif args.command == "first-failure":
        created = write_first_failure(
            args.durable_root,
            exit_code=args.exit_code,
            line=args.line,
            command=args.command,
            phase=args.phase,
        )
        receipt = {"first_failure_created": created}
    elif args.command == "exit-receipt":
        receipt = write_exit_receipt(args.durable_root, exit_code=args.exit_code, phase=args.phase)
    else:
        receipt = write_submission_failure(
            args.durable_root,
            exit_code=args.exit_code,
            stage=args.stage,
            command=args.command,
            nonduplication_key=args.nonduplication_key,
            job_id=args.job_id,
            scheduler_reconciliation=args.scheduler_reconciliation,
            registry_terminalization=args.registry_terminalization,
        )
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
