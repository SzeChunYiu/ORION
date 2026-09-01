"""Batch external DRUP verification of every UNSAT certificate in a stream.

The single-record control path in ``external_drup.py`` remains the reference
instrument; this driver exists because it re-parses the whole record stream
and re-derives the checker binding for every record, which is quadratic in
batch use.  Here the protocol is loaded once, the drat-trim tree identity is
verified once before and once after the batch, and every UNSAT certificate is
still individually binding-verified (including its CNF rebuild) and
individually executed by the pinned external checker.  SAT certificates are
counted and skipped: they carry no DRUP proof.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any, Mapping, Sequence

import batch_engine_b as batch
import engine_b as eb
import external_drup as drup

BATCH_SCHEMA = "ORION.NQ.EngineB.ExternalDRUPBatchReceipt.v1"
BATCH_LINE_SCHEMA = "ORION.NQ.EngineB.ExternalDRUPBatchLine.v1"
BATCH_TERMINAL = "NQ_ENGINE_B_EXTERNAL_DRUP_ALL_UNSAT_CERTIFICATES_VERIFIED"
BATCH_INCOMPLETE = "CANNOT_CHECK_EXTERNAL_DRUP_BATCH_INCOMPLETE"
BATCH_REJECTED = "NQ_ENGINE_B_EXTERNAL_DRUP_CONTROL_REJECTED"
BATCH_TIMEOUT = "CANNOT_CHECK_EXTERNAL_DRUP_TIMEOUT"
BATCH_AUTHORITY = {
    "external_checker": "drat-trim at the pinned protocol identity",
    "proofs_externally_verified": True,
    "scientific_authority_delta": "NONE",
    "engine_a_agreement": "NOT_CLAIMED",
    "blinded_independence": "NOT_CLAIMED",
}


class ExternalDRUPBatchMismatch(RuntimeError):
    pass


def _iter_certificate_lines(path: Path):
    with Path(path).open("rb") as stream:
        for line_number, raw_line in enumerate(stream, 1):
            if not raw_line.endswith(b"\n") or raw_line == b"\n":
                raise ExternalDRUPBatchMismatch(
                    f"certificate line {line_number} is empty or lacks its newline"
                )
            payload = raw_line[:-1]
            try:
                value = json.loads(payload)
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                raise ExternalDRUPBatchMismatch(
                    f"certificate line {line_number} is not JSON"
                ) from error
            if eb.canonical_json_bytes(value) != payload:
                raise ExternalDRUPBatchMismatch(
                    f"certificate line {line_number} is not canonical JSON"
                )
            yield value


def _pair_certificates_with_records(
    certificates: Sequence[Mapping[str, Any]],
    record_stream: Path,
    *,
    require_exhaustive: bool = True,
) -> list[tuple[Mapping[str, Any], tuple[int, ...], int]]:
    """Attach each certificate's record payload in stream order.

    The execution phase emits exactly one certificate per input record in
    stream order, so a lockstep walk with strict record-id equality both
    avoids a second full in-memory record map and fail-closes on any drift.
    A deliberately truncated batch (``max_records``) may leave the record
    stream non-exhausted, but is then never allowed to claim completeness.
    """

    stream = batch.iter_records(record_stream)
    paired: list[tuple[Mapping[str, Any], tuple[int, ...], int]] = []
    for certificate in certificates:
        record = next(stream, None)
        if record is None or record.record_id != certificate.get("record_id"):
            raise ExternalDRUPBatchMismatch(
                "certificate stream is not in lockstep with the record stream"
            )
        paired.append((certificate, record.sequence, record.required_bins))
    if require_exhaustive and next(stream, None) is not None:
        raise ExternalDRUPBatchMismatch("record stream has records beyond the certificate stream")
    return paired


_WORKER: dict[str, Any] = {}


def _initialize_worker(config: Mapping[str, Any]) -> None:
    _WORKER["artifact_root"] = Path(config["artifact_root"])
    _WORKER["checker"] = config["checker_binary"]
    _WORKER["timeout"] = config["timeout_seconds"]
    _WORKER["exit_code"] = config["success_exit_code"]
    _WORKER["marker"] = config["marker"]


def _check_one_certificate(payload: tuple[Any, ...]) -> dict[str, Any]:
    certificate, sequence, required_bins = payload
    record_id = certificate["record_id"]
    batch.verify_unsat_certificate_bindings(
        certificate,
        sequence=sequence,
        required_bins=required_bins,
        artifact_root=_WORKER["artifact_root"],
    )
    root = _WORKER["artifact_root"].resolve()
    cnf_path = root / certificate["cnf"]["path"]
    proof_path = root / certificate["proof"]["path"]
    command = (_WORKER["checker"], str(cnf_path), str(proof_path))
    started = time.monotonic()
    timed_out = False
    try:
        completed = subprocess.run(
            command,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=_WORKER["timeout"],
            env={**os.environ, "LC_ALL": "C", "LANG": "C"},
        )
        return_code: int | None = completed.returncode
        stdout, stderr = completed.stdout, completed.stderr
    except subprocess.TimeoutExpired as error:
        timed_out = True
        return_code = None
        stdout = error.stdout or b""
        stderr = error.stderr or b""
    duration_ms = int(round((time.monotonic() - started) * 1000.0))
    marker_seen = drup._verified_marker_seen(
        stdout, _WORKER["marker"]
    ) or drup._verified_marker_seen(stderr, _WORKER["marker"])
    if timed_out:
        terminal = drup.TIMEOUT_TERMINAL
    elif return_code == _WORKER["exit_code"] and marker_seen:
        terminal = drup.VERIFIED_TERMINAL
    else:
        terminal = drup.REJECTED_TERMINAL
    return {
        "schema": BATCH_LINE_SCHEMA,
        "record_id": record_id,
        "certificate_sha256": certificate["certificate_sha256"],
        "cnf_sha256": certificate["cnf_sha256"],
        "proof_sha256": certificate["proof"]["sha256"],
        "return_code": return_code,
        "verified_marker_seen": marker_seen,
        "terminal": terminal,
        "duration_ms": duration_ms,
        "stdout": stdout.decode("ascii", "replace"),
        "stderr": stderr.decode("ascii", "replace"),
    }


def _run_chunk(chunk: Sequence[tuple[Any, ...]]) -> list[dict[str, Any]]:
    return [_check_one_certificate(payload) for payload in chunk]


def run_batch(
    *,
    protocol_path: Path,
    record_stream: Path,
    certificates_path: Path,
    artifact_root: Path,
    checker: Path,
    checker_source_root: Path,
    receipts_path: Path,
    threads: int = 1,
    chunk_size: int = 32,
    max_records: int | None = None,
) -> dict[str, Any]:
    """Verify every UNSAT certificate against the pinned external checker."""

    protocol = drup.load_protocol(protocol_path)
    binding_before = drup._tool_binding(protocol, checker=checker, source_root=checker_source_root)
    certificates_on_disk = list(_iter_certificate_lines(certificates_path))
    certificate_lines = len(certificates_on_disk)
    certificates = (
        certificates_on_disk[:max_records] if max_records is not None else certificates_on_disk
    )
    partial_batch = len(certificates) < certificate_lines
    paired = _pair_certificates_with_records(
        certificates, record_stream, require_exhaustive=max_records is None
    )
    unsat = [
        payload
        for payload in paired
        if payload[0].get("status") == "UNSAT_PROOF_EMITTED_REQUIRES_EXTERNAL_CHECK"
    ]
    sat_skipped = len(paired) - len(unsat)
    chunks = [unsat[index : index + chunk_size] for index in range(0, len(unsat), chunk_size)]
    contract = protocol["success_contract"]
    initargs = {
        "artifact_root": str(Path(artifact_root)),
        "checker_binary": str(Path(checker).resolve()),
        "timeout_seconds": contract["timeout_seconds"],
        "success_exit_code": contract["exit_code"],
        "marker": contract["marker"],
    }
    started = time.monotonic()
    if threads <= 1:
        _initialize_worker(initargs)
        results = [line for chunk in chunks for line in _run_chunk(chunk)]
    else:
        with ProcessPoolExecutor(
            max_workers=threads,
            initializer=_initialize_worker,
            initargs=(initargs,),
        ) as pool:
            results = [
                line for chunk in pool.map(_run_chunk, chunks, chunksize=1) for line in chunk
            ]
    wall_ms = int(round((time.monotonic() - started) * 1000.0))
    counts = {terminal: 0 for terminal in drup.ALLOWED_TERMINALS}
    for line in results:
        counts[line["terminal"]] += 1
    receipts_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = receipts_path.with_name(f".{receipts_path.name}.{os.getpid()}.tmp")
    with temporary.open("wb") as output:
        for line in results:
            output.write(eb.canonical_json_bytes(line) + b"\n")
    os.replace(temporary, receipts_path)
    binding_after = drup._tool_binding(protocol, checker=checker, source_root=checker_source_root)
    if binding_after != binding_before:
        raise ExternalDRUPBatchMismatch("drat-trim source tree changed during the batch")
    verified = counts[drup.VERIFIED_TERMINAL]
    rejected = counts[drup.REJECTED_TERMINAL]
    timed_out = counts[drup.TIMEOUT_TERMINAL]
    if rejected or timed_out:
        terminal = BATCH_REJECTED if rejected else BATCH_TIMEOUT
    elif not partial_batch and verified == len(unsat) and len(unsat) > 0:
        terminal = BATCH_TERMINAL
    else:
        terminal = BATCH_INCOMPLETE
    receipts_bytes = receipts_path.read_bytes()
    receipt: dict[str, Any] = {
        "schema": BATCH_SCHEMA,
        "subject_commit": eb.SUBJECT_COMMIT,
        "terminal": terminal,
        "protocol": drup._file_binding(protocol_path, display_path=protocol_path.name),
        "record_stream": drup._file_binding(record_stream, display_path=record_stream.name),
        "certificates": drup._file_binding(certificates_path, display_path=certificates_path.name),
        "checker": binding_before,
        "counts": {
            "certificates_total": len(certificates),
            "certificate_lines_on_disk": certificate_lines,
            "unsat_certificates": len(unsat),
            "sat_certificates_skipped": sat_skipped,
            "verified": verified,
            "rejected": rejected,
            "timeout": timed_out,
            "records_paired": len(paired),
            "partial_batch": partial_batch,
        },
        "receipts": {
            "path": receipts_path.name,
            "bytes": len(receipts_bytes),
            "sha256": hashlib.sha256(receipts_bytes).hexdigest(),
            "lines": len(results),
        },
        "wall_ms": wall_ms,
        "runtime": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "machine": platform.machine(),
        },
        "authority": dict(BATCH_AUTHORITY),
    }
    receipt["batch_receipt_sha256"] = hashlib.sha256(
        eb.canonical_json_bytes(
            {key: value for key, value in receipt.items() if key != "batch_receipt_sha256"}
        )
    ).hexdigest()
    return receipt


def verify_batch_receipt(
    receipt: Mapping[str, Any],
    *,
    protocol_path: Path,
    record_stream: Path,
    certificates_path: Path,
    artifact_root: Path,
    checker: Path,
    checker_source_root: Path,
    receipts_path: Path,
    resample: int = 0,
) -> None:
    """Verify a batch receipt against its byte bindings and controls.

    With ``resample`` the single-record reference instrument is re-run on a
    deterministic sample of records so the batch path stays cross-validated
    against the frozen per-record control.
    """

    if type(receipt) is not dict or set(receipt) != {
        "schema",
        "subject_commit",
        "terminal",
        "protocol",
        "record_stream",
        "certificates",
        "checker",
        "counts",
        "receipts",
        "wall_ms",
        "runtime",
        "authority",
        "batch_receipt_sha256",
    }:
        raise ExternalDRUPBatchMismatch("batch receipt fields are not exact")
    if receipt["schema"] != BATCH_SCHEMA:
        raise ExternalDRUPBatchMismatch("batch receipt schema mismatch")
    if receipt["subject_commit"] != eb.SUBJECT_COMMIT:
        raise ExternalDRUPBatchMismatch("batch receipt subject mismatch")
    if (
        receipt["batch_receipt_sha256"]
        != hashlib.sha256(
            eb.canonical_json_bytes(
                {key: value for key, value in receipt.items() if key != "batch_receipt_sha256"}
            )
        ).hexdigest()
    ):
        raise ExternalDRUPBatchMismatch("batch receipt digest mismatch")
    protocol = drup.load_protocol(protocol_path)
    if receipt["protocol"] != drup._file_binding(protocol_path, display_path=protocol_path.name):
        raise ExternalDRUPBatchMismatch("batch receipt protocol binding mismatch")
    if receipt["record_stream"] != drup._file_binding(
        record_stream, display_path=record_stream.name
    ):
        raise ExternalDRUPBatchMismatch("batch receipt record stream binding mismatch")
    if receipt["certificates"] != drup._file_binding(
        certificates_path, display_path=certificates_path.name
    ):
        raise ExternalDRUPBatchMismatch("batch receipt certificate binding mismatch")
    if receipt["checker"] != drup._tool_binding(
        protocol, checker=checker, source_root=checker_source_root
    ):
        raise ExternalDRUPBatchMismatch("batch receipt checker binding mismatch")
    if receipt["authority"] != BATCH_AUTHORITY:
        raise ExternalDRUPBatchMismatch("batch receipt authority labels are not frozen")
    receipts_bytes = receipts_path.read_bytes()
    if receipt["receipts"] != {
        "path": receipts_path.name,
        "bytes": len(receipts_bytes),
        "sha256": hashlib.sha256(receipts_bytes).hexdigest(),
        "lines": receipt["receipts"]["lines"],
    }:
        raise ExternalDRUPBatchMismatch("batch receipt receipts binding mismatch")
    lines = list(_iter_certificate_lines(receipts_path))
    if len(lines) != receipt["receipts"]["lines"]:
        raise ExternalDRUPBatchMismatch("batch receipt line count mismatch")
    if any(line.get("schema") != BATCH_LINE_SCHEMA for line in lines):
        raise ExternalDRUPBatchMismatch("batch receipt line schema mismatch")
    counts = {terminal: 0 for terminal in drup.ALLOWED_TERMINALS}
    for line in lines:
        counts[line["terminal"]] += 1
        contract = protocol["success_contract"]
        if line["terminal"] == drup.VERIFIED_TERMINAL and not (
            line["return_code"] == contract["exit_code"] and line["verified_marker_seen"] is True
        ):
            raise ExternalDRUPBatchMismatch("verified line lacks success evidence")
        if (
            drup._verified_marker_seen(
                line["stdout"].encode("ascii", "replace"), contract["marker"]
            )
            or drup._verified_marker_seen(
                line["stderr"].encode("ascii", "replace"), contract["marker"]
            )
        ) is not line["verified_marker_seen"]:
            raise ExternalDRUPBatchMismatch("line marker flag disagrees with its logs")
    declared = receipt["counts"]
    if type(declared) is not dict or set(declared) != {
        "certificates_total",
        "certificate_lines_on_disk",
        "unsat_certificates",
        "sat_certificates_skipped",
        "verified",
        "rejected",
        "timeout",
        "records_paired",
        "partial_batch",
    }:
        raise ExternalDRUPBatchMismatch("batch receipt counts fields are not exact")
    certificate_lines = sum(1 for _ in _iter_certificate_lines(certificates_path))
    if declared["certificate_lines_on_disk"] != certificate_lines:
        raise ExternalDRUPBatchMismatch(
            "batch receipt certificate line count disagrees with the file"
        )
    if not 0 <= declared["certificates_total"] <= certificate_lines:
        raise ExternalDRUPBatchMismatch("batch receipt certificate total is out of range")
    if declared["records_paired"] != declared["certificates_total"]:
        raise ExternalDRUPBatchMismatch("batch receipt paired count disagrees")
    if declared["partial_batch"] is not (declared["certificates_total"] < certificate_lines):
        raise ExternalDRUPBatchMismatch("batch receipt partial flag disagrees")
    if declared["sat_certificates_skipped"] != (
        declared["certificates_total"] - declared["unsat_certificates"]
    ):
        raise ExternalDRUPBatchMismatch("batch receipt skip count disagrees")
    if (
        declared["verified"] != counts[drup.VERIFIED_TERMINAL]
        or declared["rejected"] != counts[drup.REJECTED_TERMINAL]
        or declared["timeout"] != counts[drup.TIMEOUT_TERMINAL]
    ):
        raise ExternalDRUPBatchMismatch("batch receipt counts disagree with its lines")
    if declared["unsat_certificates"] != len(lines):
        raise ExternalDRUPBatchMismatch("batch receipt did not check every certificate")
    expected_terminal = (
        BATCH_REJECTED
        if counts[drup.REJECTED_TERMINAL]
        else BATCH_TIMEOUT
        if counts[drup.TIMEOUT_TERMINAL]
        else BATCH_TERMINAL
        if not declared["partial_batch"]
        and counts[drup.VERIFIED_TERMINAL] == len(lines)
        and len(lines) > 0
        else BATCH_INCOMPLETE
    )
    if receipt["terminal"] != expected_terminal:
        raise ExternalDRUPBatchMismatch("batch receipt terminal is inconsistent")
    if resample:
        certificates = {
            certificate["record_id"]: certificate
            for certificate in _iter_certificate_lines(certificates_path)
        }
        sample = [line["record_id"] for line in lines[:: max(1, len(lines) // resample)][:resample]]
        control_root = receipts_path.parent / "resample_controls"
        control_root.mkdir(parents=True, exist_ok=True)
        for record_id in sample:
            certificate_path = control_root / f"{record_id}.certificate.json"
            certificate_path.write_text(
                json.dumps(certificates[record_id], indent=2, sort_keys=True) + "\n"
            )
            reference = drup.run_external_drup(
                protocol_path=protocol_path,
                record_stream=record_stream,
                record_id=record_id,
                certificate_path=certificate_path,
                artifact_root=artifact_root,
                checker=checker,
                checker_source_root=checker_source_root,
                log_root=control_root / "logs",
            )
            if reference["execution"]["terminal"] != drup.VERIFIED_TERMINAL:
                raise ExternalDRUPBatchMismatch(f"resample control failed for {record_id}")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--protocol", type=Path, default=root / "EXTERNAL_DRUP_CHECKER_PROTOCOL.json"
    )
    parser.add_argument("--record-stream", type=Path, required=True)
    parser.add_argument("--certificates", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--checker", type=Path, required=True)
    parser.add_argument("--checker-source-root", type=Path, required=True)
    parser.add_argument("--receipts", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--threads", type=int, default=1)
    parser.add_argument("--chunk-size", type=int, default=32)
    parser.add_argument("--max-records", type=int, default=None)
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--resample", type=int, default=0)
    args = parser.parse_args(argv)
    if args.threads < 1 or args.chunk_size < 1:
        parser.error("threads and chunk-size must be positive")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.verify:
        receipt = json.loads(args.output.read_text())
        verify_batch_receipt(
            receipt,
            protocol_path=args.protocol,
            record_stream=args.record_stream,
            certificates_path=args.certificates,
            artifact_root=args.artifact_root,
            checker=args.checker,
            checker_source_root=args.checker_source_root,
            receipts_path=args.receipts,
            resample=args.resample,
        )
        print(json.dumps({"terminal": receipt["terminal"], "verified": True}))
        return 0
    receipt = run_batch(
        protocol_path=args.protocol,
        record_stream=args.record_stream,
        certificates_path=args.certificates,
        artifact_root=args.artifact_root,
        checker=args.checker,
        checker_source_root=args.checker_source_root,
        receipts_path=args.receipts,
        threads=args.threads,
        chunk_size=args.chunk_size,
        max_records=args.max_records,
    )
    drup.write_receipt(args.output, receipt)
    print(json.dumps({"terminal": receipt["terminal"], "counts": receipt["counts"]}))
    return 0 if receipt["terminal"] == BATCH_TERMINAL else 1


if __name__ == "__main__":
    raise SystemExit(main())
