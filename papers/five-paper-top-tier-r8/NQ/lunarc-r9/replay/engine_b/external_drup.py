#!/usr/bin/env python3
"""Run a source-pinned external DRUP checker over one Engine-B certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import subprocess
from pathlib import Path
from typing import Any, Mapping, Sequence

import batch_engine_b as batch
import engine_b as eb


class ExternalDRUPMismatch(RuntimeError):
    """Raised when an external-checker binding or receipt is invalid."""


VERIFIED_TERMINAL = "NQ_ENGINE_B_EXTERNAL_DRUP_CONTROL_VERIFIED"
REJECTED_TERMINAL = "NQ_ENGINE_B_EXTERNAL_DRUP_CONTROL_REJECTED"
TIMEOUT_TERMINAL = "CANNOT_CHECK_EXTERNAL_DRUP_TIMEOUT"
ALLOWED_TERMINALS = {VERIFIED_TERMINAL, REJECTED_TERMINAL, TIMEOUT_TERMINAL}
GIT_OBJECT = re.compile(r"[0-9a-f]{40}")
PROTOCOL_AUTHORITY = {
    "full_census_executed": False,
    "independent_replay_authority": "CANNOT_CHECK",
    "scientific_authority_delta": "NONE",
    "paper_authority_delta": "NONE",
    "d4_c5_cubed": "OPEN",
}
RECEIPT_AUTHORITY = {
    "scope": "ONE_UNSAT_ENGINEERING_CONTROL",
    **PROTOCOL_AUTHORITY,
}


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _file_binding(path: Path, *, display_path: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ExternalDRUPMismatch(f"bound file is unavailable or a symlink: {path}")
    data = path.read_bytes()
    return {"path": display_path, "bytes": len(data), "sha256": _sha256(data)}


def _run_text(command: Sequence[str]) -> str:
    completed = subprocess.run(
        list(command),
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, "LC_ALL": "C", "LANG": "C"},
    )
    if completed.returncode != 0:
        raise ExternalDRUPMismatch(
            f"identity command failed with exit {completed.returncode}: {' '.join(command)}"
        )
    try:
        return completed.stdout.decode("utf-8").strip()
    except UnicodeDecodeError as error:
        raise ExternalDRUPMismatch("identity command returned non-UTF-8 output") from error


def load_protocol(path: Path) -> dict[str, Any]:
    try:
        protocol = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ExternalDRUPMismatch("external DRUP protocol cannot be parsed") from error
    if type(protocol) is not dict or set(protocol) != {
        "schema",
        "tool",
        "success_contract",
        "authority",
    }:
        raise ExternalDRUPMismatch("external DRUP protocol fields are not exact")
    if protocol["schema"] != "ORION.NQ.EngineB.ExternalDRUPProtocol.v1":
        raise ExternalDRUPMismatch("external DRUP protocol schema mismatch")
    tool = protocol["tool"]
    if type(tool) is not dict or set(tool) != {
        "name",
        "repository",
        "commit",
        "tree",
        "license",
        "license_path",
        "checker_relative_path",
        "build_command",
        "invocation",
    }:
        raise ExternalDRUPMismatch("external DRUP tool fields are not exact")
    if type(tool["commit"]) is not str or not GIT_OBJECT.fullmatch(tool["commit"]):
        raise ExternalDRUPMismatch("external DRUP source commit is malformed")
    if type(tool["tree"]) is not str or not GIT_OBJECT.fullmatch(tool["tree"]):
        raise ExternalDRUPMismatch("external DRUP source tree is malformed")
    expected_identity = {
        "name": "drat-trim",
        "repository": "https://github.com/marijnheule/drat-trim.git",
        "license": "MIT",
        "license_path": "LICENSE",
        "checker_relative_path": "drat-trim",
        "build_command": ["make", "drat-trim"],
        "invocation": ["drat-trim", "INPUT.cnf", "PROOF.drup"],
    }
    if any(tool[field] != value for field, value in expected_identity.items()):
        raise ExternalDRUPMismatch("external DRUP tool identity contract mismatch")
    for field in ("license_path", "checker_relative_path"):
        relative = Path(tool[field])
        if relative.is_absolute() or ".." in relative.parts or relative.as_posix() != tool[field]:
            raise ExternalDRUPMismatch(f"external DRUP tool {field} is not canonical")
    success = protocol["success_contract"]
    if type(success) is not dict or set(success) != {
        "exit_code",
        "marker",
        "timeout_seconds",
    }:
        raise ExternalDRUPMismatch("external DRUP success contract fields are not exact")
    if success["exit_code"] != 0 or success["marker"] != "s VERIFIED":
        raise ExternalDRUPMismatch("external DRUP success contract is not fail closed")
    if type(success["timeout_seconds"]) is not int or not 1 <= success["timeout_seconds"] <= 600:
        raise ExternalDRUPMismatch("external DRUP timeout is outside the bounded scope")
    if protocol["authority"] != PROTOCOL_AUTHORITY:
        raise ExternalDRUPMismatch("external DRUP protocol overstates authority")
    return protocol


def _verified_marker_seen(data: bytes, marker: str) -> bool:
    expected = marker.encode("ascii")
    return any(line.strip() == expected for line in data.splitlines())


def _tool_binding(
    protocol: Mapping[str, Any], *, checker: Path, source_root: Path
) -> dict[str, Any]:
    root = source_root.resolve()
    checker_path = checker.resolve()
    tool = protocol["tool"]
    if source_root.is_symlink() or checker.is_symlink():
        raise ExternalDRUPMismatch("external checker source or binary is a symlink")
    if not checker_path.is_relative_to(root):
        raise ExternalDRUPMismatch("external checker binary is outside its source root")
    expected_checker = root / tool["checker_relative_path"]
    if checker_path != expected_checker.resolve() or not checker_path.is_file():
        raise ExternalDRUPMismatch("external checker binary path mismatch")
    if not os.access(checker_path, os.X_OK):
        raise ExternalDRUPMismatch("external checker binary is not executable")
    commit = _run_text(("git", "-C", str(root), "rev-parse", "HEAD"))
    tree = _run_text(("git", "-C", str(root), "rev-parse", "HEAD^{tree}"))
    tracked_status = _run_text(
        ("git", "-C", str(root), "status", "--porcelain", "--untracked-files=no")
    )
    if commit != tool["commit"] or tree != tool["tree"]:
        raise ExternalDRUPMismatch("external checker source identity mismatch")
    if tracked_status:
        raise ExternalDRUPMismatch("external checker tracked source is dirty")
    license_path = root / tool["license_path"]
    return {
        "name": tool["name"],
        "repository": tool["repository"],
        "source_commit": commit,
        "source_tree": tree,
        "tracked_source_status": "CLEAN",
        "license": tool["license"],
        "license_file": _file_binding(license_path, display_path=tool["license_path"]),
        "binary": _file_binding(checker_path, display_path=tool["checker_relative_path"]),
    }


def _load_record(path: Path, record_id: str) -> batch.SequenceRecord:
    matches = [record for record in batch.iter_records(path) if record.record_id == record_id]
    if len(matches) != 1:
        raise ExternalDRUPMismatch("external DRUP record id is absent or duplicated")
    return matches[0]


def _load_certificate(path: Path) -> dict[str, Any]:
    try:
        certificate = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ExternalDRUPMismatch("UNSAT certificate cannot be parsed") from error
    if type(certificate) is not dict:
        raise ExternalDRUPMismatch("UNSAT certificate is not a JSON object")
    return certificate


def _receipt_digest(receipt: Mapping[str, Any]) -> str:
    payload = {key: value for key, value in receipt.items() if key != "receipt_sha256"}
    return _sha256(eb.canonical_json_bytes(payload))


def _write_log(root: Path, name: str, data: bytes) -> dict[str, Any]:
    root.mkdir(parents=True, exist_ok=True)
    destination = root / name
    temporary = destination.with_name(f".{destination.name}.{os.getpid()}.tmp")
    temporary.write_bytes(data)
    os.replace(temporary, destination)
    return _file_binding(destination, display_path=name)


def run_external_drup(
    *,
    protocol_path: Path,
    record_stream: Path,
    record_id: str,
    certificate_path: Path,
    artifact_root: Path,
    checker: Path,
    checker_source_root: Path,
    log_root: Path,
) -> dict[str, Any]:
    protocol = load_protocol(protocol_path)
    record = _load_record(record_stream, record_id)
    certificate = _load_certificate(certificate_path)
    if certificate.get("record_id") != record_id:
        raise ExternalDRUPMismatch("UNSAT certificate record id mismatch")
    batch.verify_unsat_certificate_bindings(
        certificate,
        sequence=record.sequence,
        required_bins=record.required_bins,
        artifact_root=artifact_root,
    )
    tool_binding = _tool_binding(protocol, checker=checker, source_root=checker_source_root)
    root = artifact_root.resolve()
    cnf_path = root / certificate["cnf"]["path"]
    proof_path = root / certificate["proof"]["path"]
    command = (str(checker.resolve()), str(cnf_path), str(proof_path))
    timed_out = False
    try:
        completed = subprocess.run(
            command,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=protocol["success_contract"]["timeout_seconds"],
            env={**os.environ, "LC_ALL": "C", "LANG": "C"},
        )
        return_code: int | None = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
    except subprocess.TimeoutExpired as error:
        timed_out = True
        return_code = None
        stdout = error.stdout or b""
        stderr = error.stderr or b""
    marker = protocol["success_contract"]["marker"]
    marker_seen = _verified_marker_seen(stdout, marker) or _verified_marker_seen(stderr, marker)
    if timed_out:
        terminal = TIMEOUT_TERMINAL
    elif return_code == protocol["success_contract"]["exit_code"] and marker_seen:
        terminal = VERIFIED_TERMINAL
    else:
        terminal = REJECTED_TERMINAL
    receipt: dict[str, Any] = {
        "schema": "ORION.NQ.EngineB.ExternalDRUPReceipt.v1",
        "subject_commit": eb.SUBJECT_COMMIT,
        "record_id": record_id,
        "protocol": _file_binding(protocol_path, display_path=protocol_path.name),
        "input": {
            "record_stream": _file_binding(record_stream, display_path=record_stream.name),
            "certificate": _file_binding(certificate_path, display_path=certificate_path.name),
            "certificate_sha256": certificate["certificate_sha256"],
            "cnf_semantic_sha256": certificate["cnf_sha256"],
            "cnf_file_sha256": certificate["cnf"]["sha256"],
            "proof_sha256": certificate["proof"]["sha256"],
        },
        "checker": tool_binding,
        "execution": {
            "command": [
                tool_binding["binary"]["path"],
                certificate["cnf"]["path"],
                certificate["proof"]["path"],
            ],
            "return_code": return_code,
            "verified_marker_seen": marker_seen,
            "stdout": _write_log(log_root, f"{record_id}.drat-trim.stdout", stdout),
            "stderr": _write_log(log_root, f"{record_id}.drat-trim.stderr", stderr),
            "terminal": terminal,
        },
        "runtime": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "machine": platform.machine(),
        },
        "authority": dict(RECEIPT_AUTHORITY),
    }
    receipt["receipt_sha256"] = _receipt_digest(receipt)
    return receipt


def verify_external_drup_receipt(
    receipt: Mapping[str, Any],
    *,
    protocol_path: Path,
    record_stream: Path,
    certificate_path: Path,
    artifact_root: Path,
    checker: Path,
    checker_source_root: Path,
    log_root: Path,
) -> None:
    if type(receipt) is not dict or set(receipt) != {
        "schema",
        "subject_commit",
        "record_id",
        "protocol",
        "input",
        "checker",
        "execution",
        "runtime",
        "authority",
        "receipt_sha256",
    }:
        raise ExternalDRUPMismatch("external DRUP receipt fields are not exact")
    if receipt["schema"] != "ORION.NQ.EngineB.ExternalDRUPReceipt.v1":
        raise ExternalDRUPMismatch("external DRUP receipt schema mismatch")
    if receipt["subject_commit"] != eb.SUBJECT_COMMIT:
        raise ExternalDRUPMismatch("external DRUP receipt subject mismatch")
    if receipt["receipt_sha256"] != _receipt_digest(receipt):
        raise ExternalDRUPMismatch("external DRUP receipt digest mismatch")
    protocol = load_protocol(protocol_path)
    if receipt["protocol"] != _file_binding(protocol_path, display_path=protocol_path.name):
        raise ExternalDRUPMismatch("external DRUP receipt protocol binding mismatch")
    record = _load_record(record_stream, receipt["record_id"])
    certificate = _load_certificate(certificate_path)
    if certificate.get("record_id") != receipt["record_id"]:
        raise ExternalDRUPMismatch("UNSAT certificate record id mismatch")
    batch.verify_unsat_certificate_bindings(
        certificate,
        sequence=record.sequence,
        required_bins=record.required_bins,
        artifact_root=artifact_root,
    )
    if receipt["checker"] != _tool_binding(
        protocol, checker=checker, source_root=checker_source_root
    ):
        raise ExternalDRUPMismatch("external DRUP checker binding mismatch")
    expected_input = {
        "record_stream": _file_binding(record_stream, display_path=record_stream.name),
        "certificate": _file_binding(certificate_path, display_path=certificate_path.name),
        "certificate_sha256": certificate["certificate_sha256"],
        "cnf_semantic_sha256": certificate["cnf_sha256"],
        "cnf_file_sha256": certificate["cnf"]["sha256"],
        "proof_sha256": certificate["proof"]["sha256"],
    }
    if receipt["input"] != expected_input:
        raise ExternalDRUPMismatch("external DRUP receipt input binding mismatch")
    execution = receipt["execution"]
    if type(execution) is not dict or set(execution) != {
        "command",
        "return_code",
        "verified_marker_seen",
        "stdout",
        "stderr",
        "terminal",
    }:
        raise ExternalDRUPMismatch("external DRUP execution fields are not exact")
    if execution["terminal"] not in ALLOWED_TERMINALS:
        raise ExternalDRUPMismatch("external DRUP receipt terminal is invalid")
    expected_command = [
        receipt["checker"]["binary"]["path"],
        certificate["cnf"]["path"],
        certificate["proof"]["path"],
    ]
    if execution["command"] != expected_command:
        raise ExternalDRUPMismatch("external DRUP execution command mismatch")
    if type(execution["verified_marker_seen"]) is not bool:
        raise ExternalDRUPMismatch("external DRUP marker flag is not Boolean")
    if execution["return_code"] is not None and type(execution["return_code"]) is not int:
        raise ExternalDRUPMismatch("external DRUP return code is invalid")
    log_bytes: dict[str, bytes] = {}
    for stream_name in ("stdout", "stderr"):
        binding = execution[stream_name]
        expected_path = f"{receipt['record_id']}.drat-trim.{stream_name}"
        if type(binding) is not dict or binding.get("path") != expected_path:
            raise ExternalDRUPMismatch(f"external DRUP {stream_name} path mismatch")
        log_path = log_root / expected_path
        if binding != _file_binding(log_path, display_path=expected_path):
            raise ExternalDRUPMismatch(f"external DRUP {stream_name} binding mismatch")
        log_bytes[stream_name] = log_path.read_bytes()
    marker_seen = _verified_marker_seen(
        log_bytes["stdout"], protocol["success_contract"]["marker"]
    ) or _verified_marker_seen(log_bytes["stderr"], protocol["success_contract"]["marker"])
    if execution["verified_marker_seen"] is not marker_seen:
        raise ExternalDRUPMismatch("external DRUP marker flag disagrees with bound logs")
    if execution["terminal"] == VERIFIED_TERMINAL and not (
        execution["return_code"] == protocol["success_contract"]["exit_code"]
        and execution["verified_marker_seen"] is True
    ):
        raise ExternalDRUPMismatch("external DRUP success terminal lacks success evidence")
    if execution["terminal"] == TIMEOUT_TERMINAL and execution["return_code"] is not None:
        raise ExternalDRUPMismatch("external DRUP timeout terminal has a return code")
    if execution["terminal"] == REJECTED_TERMINAL and (
        execution["return_code"] is None
        or (
            execution["return_code"] == protocol["success_contract"]["exit_code"]
            and execution["verified_marker_seen"] is True
        )
    ):
        raise ExternalDRUPMismatch("external DRUP rejection terminal is inconsistent")
    if receipt["authority"] != RECEIPT_AUTHORITY:
        raise ExternalDRUPMismatch("external DRUP receipt overstates authority")


def write_receipt(path: Path, receipt: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    os.replace(temporary, path)


def _add_common_arguments(parser: argparse.ArgumentParser, root: Path) -> None:
    parser.add_argument(
        "--protocol", type=Path, default=root / "EXTERNAL_DRUP_CHECKER_PROTOCOL.json"
    )
    parser.add_argument(
        "--record-stream",
        type=Path,
        default=root / "controls" / "batch_input" / "records.jsonl",
    )
    parser.add_argument("--record-id", default="negative-batch")
    parser.add_argument(
        "--certificate",
        type=Path,
        default=root / "controls" / "external_drup" / "UNSAT_CONTROL_CERTIFICATE_V2.json",
    )
    parser.add_argument("--artifact-root", type=Path, default=root / "controls" / "batch_proofs")
    parser.add_argument("--checker", type=Path, required=True)
    parser.add_argument("--checker-source-root", type=Path, required=True)
    parser.add_argument("--log-root", type=Path, required=True)


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    run = subparsers.add_parser("run")
    _add_common_arguments(run, root)
    run.add_argument("--output", type=Path, required=True)
    verify = subparsers.add_parser("verify")
    _add_common_arguments(verify, root)
    verify.add_argument("--receipt", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    common = {
        "protocol_path": args.protocol,
        "record_stream": args.record_stream,
        "certificate_path": args.certificate,
        "artifact_root": args.artifact_root,
        "checker": args.checker,
        "checker_source_root": args.checker_source_root,
        "log_root": args.log_root,
    }
    if args.command == "run":
        receipt = run_external_drup(record_id=args.record_id, **common)
        write_receipt(args.output, receipt)
        print(receipt["execution"]["terminal"])
        return 0 if receipt["execution"]["terminal"] == VERIFIED_TERMINAL else 2
    receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
    verify_external_drup_receipt(receipt, **common)
    print("NQ_ENGINE_B_EXTERNAL_DRUP_RECEIPT_VERIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
