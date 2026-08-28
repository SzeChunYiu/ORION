#!/usr/bin/env python3
"""Fail-closed one-shot authorization and global submission registry gate."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, Mapping, Sequence

import engine_b as eb


AUTHORIZATION_SCHEMA = "ORION.ORION04.CRB.OneShotAuthorization.v1"
REGISTRY_SCHEMA = "ORION.ORION04.CRB.GlobalSubmissionRegistry.v1"
REGISTRY_FILENAME = "ORION04_CRB_GLOBAL_SUBMISSION_REGISTRY.json"
LOCK_FILENAME = ".orion04-crb-global-registry.lock"
SOURCE_MANIFEST_PATH = (
    "papers/orion-04-rooted-completion-certificates/evidence/"
    "crb-full-replay/successor-v1/engine_b/SOURCE_MANIFEST.json"
)
SUBJECT_COMMIT = "0c451e862a0eeddac7c673813c4dc499f134b088"
EXPECTED_SCOPES = [
    {"scope": "NQ_D2_NORMALIZED_LENGTH_19", "expected_record_count": 98_622},
    {"scope": "NQ_D3_STRUCTURED_LENGTH_25", "expected_record_count": 230_983},
]
CONSUMED_KEYS = {
    "5bbd43879aedf49bf9ac5e80ee1cc7b5b7f835675c5850e186b2de6b95f62307",
    "07e8b0389f37d2c890cdc050f0f3db2a13d94002dedd94cfcf8a1ce6c0128384",
    "741454d7d6b513ccd80d2aa9a78d2a9f5076fe8075341d0ecc8e95566ecc28ea",
}
SHA256 = re.compile(r"[0-9a-f]{64}")
COMMIT = re.compile(r"[0-9a-f]{40}")
UTC_TIMESTAMP = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z")
FAILURE_STAGE = re.compile(r"[A-Z][A-Z0-9_]{0,63}")
SCHEDULER_RECONCILIATIONS = {
    "NOT_APPLICABLE_NO_JOB_ID",
    "CANCELLED_OR_ABSENT_CONFIRMED",
    "CANCEL_REQUEST_FAILED",
    "CANCEL_REQUESTED_STILL_VISIBLE",
    "CANNOT_CHECK_SCHEDULER",
}


class AuthorizationRefused(RuntimeError):
    """The operator-supplied one-shot request is absent, stale, or malformed."""


class RegistryRefused(RuntimeError):
    """The global registry cannot safely admit a new attempt."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def derive_nonduplication_key(packet: Mapping[str, Any]) -> str:
    payload = {key: value for key, value in packet.items() if key != "nonduplication_key"}
    return hashlib.sha256(eb.canonical_json_bytes(payload)).hexdigest()


def _require_absolute_root(value: object, label: str) -> str:
    if type(value) is not str:
        raise AuthorizationRefused(f"{label} must be an absolute path")
    path = Path(value)
    if not path.is_absolute() or ".." in path.parts:
        raise AuthorizationRefused(f"{label} must be an absolute canonical path")
    return str(path)


def _require_canonical_utc_timestamp(value: object) -> str:
    if type(value) is not str or not UTC_TIMESTAMP.fullmatch(value):
        raise AuthorizationRefused("operator request time is not canonical UTC")
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as error:
        raise AuthorizationRefused("operator request time is invalid") from error
    if parsed.strftime("%Y-%m-%dT%H:%M:%SZ") != value:
        raise AuthorizationRefused("operator request time is not canonical UTC")
    return value


def validate_authorization(
    packet: Mapping[str, Any],
    *,
    expected_commit: str,
    expected_source_manifest_sha256: str,
) -> dict[str, Any]:
    required = {
        "schema",
        "status",
        "paper_id",
        "subject_commit",
        "successor_commit",
        "source_manifest",
        "durable_root",
        "global_registry_root",
        "attempt_limit",
        "declared_scopes",
        "authorization",
        "nonduplication_key",
    }
    if type(packet) is not dict or set(packet) != required:
        raise AuthorizationRefused("authorization fields are not exact")
    key = packet.get("nonduplication_key")
    if key in CONSUMED_KEYS:
        raise AuthorizationRefused("authorization reuses a consumed or terminal key")
    if packet.get("schema") != AUTHORIZATION_SCHEMA:
        raise AuthorizationRefused("authorization schema mismatch")
    if packet.get("status") != "AUTHORIZED_ONE_SHOT":
        raise AuthorizationRefused("authorization status is not a one-shot execution request")
    if packet.get("paper_id") != "ORION-04" or packet.get("subject_commit") != SUBJECT_COMMIT:
        raise AuthorizationRefused("authorization subject mismatch")
    if not COMMIT.fullmatch(expected_commit) or packet.get("successor_commit") != expected_commit:
        raise AuthorizationRefused("authorization successor commit mismatch")
    source = packet.get("source_manifest")
    if type(source) is not dict or set(source) != {"path", "sha256"}:
        raise AuthorizationRefused("authorization source manifest binding is malformed")
    if source.get("path") != SOURCE_MANIFEST_PATH:
        raise AuthorizationRefused("authorization source manifest path mismatch")
    if (
        not SHA256.fullmatch(expected_source_manifest_sha256)
        or source.get("sha256") != expected_source_manifest_sha256
    ):
        raise AuthorizationRefused("authorization source manifest digest mismatch")
    if packet.get("attempt_limit") != 1 or type(packet.get("attempt_limit")) is not int:
        raise AuthorizationRefused("authorization attempt limit must be exactly one")
    if packet.get("declared_scopes") != EXPECTED_SCOPES:
        raise AuthorizationRefused("authorization declared scopes or denominators mismatch")
    durable_root = _require_absolute_root(packet.get("durable_root"), "durable root")
    registry_root = _require_absolute_root(
        packet.get("global_registry_root"), "global registry root"
    )
    durable_path = Path(durable_root)
    registry_path = Path(registry_root)
    if (
        durable_path == registry_path
        or durable_path in registry_path.parents
        or registry_path in durable_path.parents
    ):
        raise AuthorizationRefused("durable and global registry roots are not isolated")
    authorization = packet.get("authorization")
    if type(authorization) is not dict or set(authorization) != {
        "authorized_at_utc",
        "authorized_by",
    }:
        raise AuthorizationRefused("operator request attestation is malformed")
    authorized_by = authorization.get("authorized_by")
    if (
        type(authorized_by) is not str
        or not authorized_by.strip()
        or authorized_by != authorized_by.strip()
        or len(authorized_by) > 256
        or any(
            marker in authorized_by.upper()
            for marker in ("PLACEHOLDER", "REPLACE_WITH", "EXTERNAL_OPERATOR_REQUIRED")
        )
    ):
        raise AuthorizationRefused("operator request label is still a placeholder")
    _require_canonical_utc_timestamp(authorization.get("authorized_at_utc"))
    if not isinstance(key, str) or not SHA256.fullmatch(key):
        raise AuthorizationRefused("authorization nonduplication key is malformed")
    if key != derive_nonduplication_key(packet):
        raise AuthorizationRefused("authorization nonduplication key derivation mismatch")
    return dict(packet)


def authorization_validation_receipt(packet: Mapping[str, Any]) -> dict[str, Any]:
    """Describe structural request validation without asserting external identity.

    ``authorized_by`` is an opaque operator-supplied label.  The gate has no
    trust store and therefore must never turn that text into machine evidence
    of externality, independence, identity, or scientific authority.
    """

    source = packet.get("source_manifest", {})
    return {
        "schema": "ORION.ORION04.CRB.OneShotRequestValidation.v1",
        "terminal": "ORION04_ONE_SHOT_REQUEST_BINDINGS_VALID",
        "paper_id": "ORION-04",
        "nonduplication_key": packet.get("nonduplication_key"),
        "successor_commit": packet.get("successor_commit"),
        "source_manifest_sha256": source.get("sha256"),
        "durable_root": packet.get("durable_root"),
        "global_registry_root": packet.get("global_registry_root"),
        "operator_attestation": "USER_SUPPLIED_UNVERIFIED_BY_MACHINE",
        "machine_established_externality": False,
        "machine_established_identity": False,
        "scientific_authority_delta": "NONE",
    }


def load_authorization(
    path: Path,
    *,
    expected_commit: str,
    expected_source_manifest_sha256: str,
) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        raise AuthorizationRefused(f"authorization is missing or unsafe: {path}")
    try:
        packet = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise AuthorizationRefused("authorization is malformed") from error
    return validate_authorization(
        packet,
        expected_commit=expected_commit,
        expected_source_manifest_sha256=expected_source_manifest_sha256,
    )


def _load_registry(path: Path) -> dict[str, Any]:
    try:
        registry = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RegistryRefused("global registry is unavailable or malformed") from error
    if type(registry) is not dict or set(registry) != {"schema", "submissions"}:
        raise RegistryRefused("global registry fields are not exact")
    if registry.get("schema") != REGISTRY_SCHEMA or type(registry.get("submissions")) is not list:
        raise RegistryRefused("global registry schema mismatch")
    entries = registry["submissions"]
    keys = [entry.get("nonduplication_key") for entry in entries if type(entry) is dict]
    if len(entries) != len(keys) or len(keys) != len(set(keys)):
        raise RegistryRefused("global registry contains malformed or duplicate entries")
    return registry


def _atomic_registry(path: Path, registry: Mapping[str, Any]) -> None:
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    data = json.dumps(registry, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    with temporary.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


@contextmanager
def _locked_registry(
    global_root: Path, prebind_path: Path
) -> Iterator[tuple[Path, dict[str, Any]]]:
    if not global_root.is_dir() or global_root.is_symlink():
        raise RegistryRefused(f"global registry path is unavailable or unsafe: {global_root}")
    if not os.access(global_root, os.R_OK | os.W_OK | os.X_OK):
        raise RegistryRefused(f"global registry path is unavailable or not writable: {global_root}")
    if not prebind_path.is_file() or prebind_path.is_symlink():
        raise RegistryRefused("global registry prebind packet is unavailable")
    seed = _load_registry(prebind_path)
    seed_keys = {entry["nonduplication_key"] for entry in seed["submissions"]}
    if not CONSUMED_KEYS.issubset(seed_keys):
        raise RegistryRefused("global registry prebind omits a terminal or consumed key")
    lock_path = global_root / LOCK_FILENAME
    with lock_path.open("a+", encoding="ascii") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        registry_path = global_root / REGISTRY_FILENAME
        if registry_path.exists():
            if registry_path.is_symlink():
                raise RegistryRefused("global registry file is a symlink")
            registry = _load_registry(registry_path)
        else:
            registry = seed
            _atomic_registry(registry_path, registry)
        registry_keys = {entry["nonduplication_key"] for entry in registry["submissions"]}
        if not seed_keys.issubset(registry_keys):
            raise RegistryRefused("global registry lost a prebound terminal key")
        yield registry_path, registry


def reserve_submission(
    global_root: Path, prebind_path: Path, packet: Mapping[str, Any]
) -> dict[str, Any]:
    key = packet.get("nonduplication_key")
    if not isinstance(key, str) or not SHA256.fullmatch(key):
        raise RegistryRefused("submission key is malformed")
    if key in CONSUMED_KEYS:
        raise RegistryRefused("submission key is terminal or consumed")
    with _locked_registry(global_root, prebind_path) as (path, registry):
        entries = registry["submissions"]
        if any(entry.get("nonduplication_key") == key for entry in entries):
            raise RegistryRefused("duplicate nonduplication key refused")
        if any(entry.get("status") in {"RESERVED", "SUBMITTED"} for entry in entries):
            raise RegistryRefused("another ORION-04 replay attempt is active")
        reservation: dict[str, Any] = {
            "paper_id": "ORION-04",
            "nonduplication_key": key,
            "status": "RESERVED",
            "job_id": None,
            "successor_commit": packet.get("successor_commit"),
            "source_manifest_sha256": packet.get("source_manifest", {}).get("sha256"),
            "durable_root": packet.get("durable_root"),
            "reserved_at_utc": _utc_now(),
        }
        entries.append(reservation)
        _atomic_registry(path, registry)
        return reservation


def update_submission(
    global_root: Path,
    prebind_path: Path,
    *,
    key: str,
    status: str,
    job_id: int | None,
) -> dict[str, Any]:
    if status != "SUBMITTED":
        raise RegistryRefused("invalid registry transition")
    with _locked_registry(global_root, prebind_path) as (path, registry):
        matches = [
            entry for entry in registry["submissions"] if entry.get("nonduplication_key") == key
        ]
        if len(matches) != 1 or matches[0].get("status") != "RESERVED":
            raise RegistryRefused("registry reservation is missing or not mutable")
        entry = matches[0]
        entry["status"] = status
        entry["job_id"] = job_id
        entry["updated_at_utc"] = _utc_now()
        _atomic_registry(path, registry)
        return entry


def terminalize_submission(
    global_root: Path,
    prebind_path: Path,
    *,
    key: str,
    job_id: int | None,
    failure_stage: str,
    failure_exit_code: int,
    failure_command: str,
    scheduler_reconciliation: str,
) -> dict[str, Any]:
    """Consume a reserved key after any post-reservation submission failure."""

    if not isinstance(key, str) or not SHA256.fullmatch(key):
        raise RegistryRefused("submission key is malformed")
    if type(job_id) is not int and job_id is not None:
        raise RegistryRefused("terminal job id is malformed")
    if isinstance(job_id, int) and (isinstance(job_id, bool) or job_id <= 0):
        raise RegistryRefused("terminal job id is malformed")
    if type(failure_stage) is not str or not FAILURE_STAGE.fullmatch(failure_stage):
        raise RegistryRefused("submission failure stage is malformed")
    if (
        type(failure_exit_code) is not int
        or isinstance(failure_exit_code, bool)
        or failure_exit_code == 0
    ):
        raise RegistryRefused("submission failure exit code is malformed")
    if type(failure_command) is not str or not failure_command or len(failure_command) > 4096:
        raise RegistryRefused("submission failure command is malformed")
    if scheduler_reconciliation not in SCHEDULER_RECONCILIATIONS:
        raise RegistryRefused("scheduler reconciliation is malformed")
    with _locked_registry(global_root, prebind_path) as (path, registry):
        matches = [
            entry for entry in registry["submissions"] if entry.get("nonduplication_key") == key
        ]
        if len(matches) != 1 or matches[0].get("status") not in {"RESERVED", "SUBMITTED"}:
            raise RegistryRefused("registry reservation is missing or already terminal")
        entry = matches[0]
        existing_job_id = entry.get("job_id")
        if existing_job_id is not None and job_id is not None and existing_job_id != job_id:
            raise RegistryRefused("terminal job id differs from the bound held job")
        entry["status"] = "SUBMISSION_FAILED_KEY_CONSUMED"
        entry["job_id"] = existing_job_id if existing_job_id is not None else job_id
        entry["updated_at_utc"] = _utc_now()
        entry["failure"] = {
            "stage": failure_stage,
            "exit_code": failure_exit_code,
            "command": failure_command,
            "scheduler_reconciliation": scheduler_reconciliation,
        }
        entry["scientific_authority_delta"] = "NONE"
        _atomic_registry(path, registry)
        return dict(entry)


def terminalize_started_submission(
    global_root: Path,
    prebind_path: Path,
    *,
    key: str,
    job_id: int,
    successor_commit: str,
    process_exit_code: int,
    phase: str,
) -> dict[str, Any]:
    """Consume a submitted key when its bound job exits, without adjudicating science."""

    if not isinstance(key, str) or not SHA256.fullmatch(key):
        raise RegistryRefused("submission key is malformed")
    if type(job_id) is not int or isinstance(job_id, bool) or job_id <= 0:
        raise RegistryRefused("terminal job id is malformed")
    if type(successor_commit) is not str or not COMMIT.fullmatch(successor_commit):
        raise RegistryRefused("terminal successor commit is malformed")
    if (
        type(process_exit_code) is not int
        or isinstance(process_exit_code, bool)
        or not 0 <= process_exit_code <= 255
    ):
        raise RegistryRefused("process exit code is malformed")
    if type(phase) is not str or not FAILURE_STAGE.fullmatch(phase):
        raise RegistryRefused("process exit phase is malformed")
    with _locked_registry(global_root, prebind_path) as (path, registry):
        matches = [
            entry for entry in registry["submissions"] if entry.get("nonduplication_key") == key
        ]
        if len(matches) != 1 or matches[0].get("status") != "SUBMITTED":
            raise RegistryRefused("submitted attempt is missing or already terminal")
        entry = matches[0]
        if entry.get("job_id") != job_id or entry.get("successor_commit") != successor_commit:
            raise RegistryRefused("submitted attempt job identity mismatch")
        outcome = "SUCCESS" if process_exit_code == 0 else "FAILURE"
        entry["status"] = f"PROCESS_EXIT_{outcome}_KEY_CONSUMED"
        entry["updated_at_utc"] = _utc_now()
        entry["process_exit"] = {
            "terminal": f"ORION04_CRB_PROCESS_EXIT_{outcome}",
            "exit_code": process_exit_code,
            "phase": phase,
        }
        entry["scientific_authority_delta"] = "NONE"
        _atomic_registry(path, registry)
        return dict(entry)


def assert_submitted_attempt(
    global_root: Path,
    prebind_path: Path,
    *,
    key: str,
    job_id: int,
    successor_commit: str,
) -> dict[str, Any]:
    """Rebind the running allocation to its globally registered submission."""

    with _locked_registry(global_root, prebind_path) as (_path, registry):
        matches = [
            entry for entry in registry["submissions"] if entry.get("nonduplication_key") == key
        ]
        if len(matches) != 1:
            raise RegistryRefused("submitted attempt is absent or duplicate")
        entry = matches[0]
        if (
            entry.get("status") != "SUBMITTED"
            or entry.get("job_id") != job_id
            or entry.get("successor_commit") != successor_commit
        ):
            raise RegistryRefused("submitted attempt job identity mismatch")
        return dict(entry)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "reserve"):
        sub = subparsers.add_parser(name)
        sub.add_argument("--authorization", type=Path, required=True)
        sub.add_argument("--expected-commit", required=True)
        sub.add_argument("--source-manifest-sha256", required=True)
        if name == "reserve":
            sub.add_argument("--global-root", type=Path, required=True)
            sub.add_argument("--prebind", type=Path, required=True)
    for name in ("commit",):
        sub = subparsers.add_parser(name)
        sub.add_argument("--global-root", type=Path, required=True)
        sub.add_argument("--prebind", type=Path, required=True)
        sub.add_argument("--key", required=True)
        sub.add_argument("--job-id", type=int, required=True)
    terminalize = subparsers.add_parser("terminalize")
    terminalize.add_argument("--global-root", type=Path, required=True)
    terminalize.add_argument("--prebind", type=Path, required=True)
    terminalize.add_argument("--key", required=True)
    terminalize.add_argument("--job-id", type=int)
    terminalize.add_argument("--failure-stage", required=True)
    terminalize.add_argument("--failure-exit-code", type=int, required=True)
    terminalize.add_argument("--failure-command", required=True)
    terminalize.add_argument("--scheduler-reconciliation", required=True)
    started = subparsers.add_parser("terminalize-started")
    started.add_argument("--global-root", type=Path, required=True)
    started.add_argument("--prebind", type=Path, required=True)
    started.add_argument("--key", required=True)
    started.add_argument("--job-id", type=int, required=True)
    started.add_argument("--successor-commit", required=True)
    started.add_argument("--process-exit-code", type=int, required=True)
    started.add_argument("--phase", required=True)
    asserted = subparsers.add_parser("assert-submitted")
    asserted.add_argument("--global-root", type=Path, required=True)
    asserted.add_argument("--prebind", type=Path, required=True)
    asserted.add_argument("--key", required=True)
    asserted.add_argument("--job-id", type=int, required=True)
    asserted.add_argument("--successor-commit", required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command in {"validate", "reserve"}:
        packet = load_authorization(
            args.authorization,
            expected_commit=args.expected_commit,
            expected_source_manifest_sha256=args.source_manifest_sha256,
        )
        if args.command == "validate":
            result: Mapping[str, Any] = authorization_validation_receipt(packet)
        else:
            if str(args.global_root) != packet["global_registry_root"]:
                raise RegistryRefused("global registry root differs from authorization")
            result = reserve_submission(args.global_root, args.prebind, packet)
    elif args.command == "commit":
        result = update_submission(
            args.global_root,
            args.prebind,
            key=args.key,
            status="SUBMITTED",
            job_id=args.job_id,
        )
    elif args.command == "terminalize":
        result = terminalize_submission(
            args.global_root,
            args.prebind,
            key=args.key,
            job_id=args.job_id,
            failure_stage=args.failure_stage,
            failure_exit_code=args.failure_exit_code,
            failure_command=args.failure_command,
            scheduler_reconciliation=args.scheduler_reconciliation,
        )
    elif args.command == "terminalize-started":
        result = terminalize_started_submission(
            args.global_root,
            args.prebind,
            key=args.key,
            job_id=args.job_id,
            successor_commit=args.successor_commit,
            process_exit_code=args.process_exit_code,
            phase=args.phase,
        )
    else:
        result = assert_submitted_attempt(
            args.global_root,
            args.prebind,
            key=args.key,
            job_id=args.job_id,
            successor_commit=args.successor_commit,
        )
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
