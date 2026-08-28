#!/usr/bin/env python3
"""Independently recheck every positive CR-B witness using only integer arithmetic."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Mapping, Sequence


SUBJECT_COMMIT = "0c451e862a0eeddac7c673813c4dc499f134b088"
SAT_STATUS = "SAT_K_DISJOINT_ZERO_SUMS"
UNSAT_STATUS = "UNSAT_PROOF_EMITTED_REQUIRES_EXTERNAL_CHECK"
SHA256 = re.compile(r"[0-9a-f]{64}")


class PositiveWitnessMismatch(RuntimeError):
    """A positive certificate is missing, malformed, or mathematically invalid."""


def canonical_bytes(value: Any) -> bytes:
    def reject_float(item: Any) -> None:
        if type(item) is float:
            raise PositiveWitnessMismatch("floating-point value is not canonical")
        if type(item) is dict:
            for key, child in item.items():
                if type(key) is not str:
                    raise PositiveWitnessMismatch("canonical JSON key is not a string")
                reject_float(child)
        elif type(item) is list:
            for child in item:
                reject_float(child)

    reject_float(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def canonical_digest(value: Mapping[str, Any]) -> str:
    payload = {key: item for key, item in value.items() if key != "certificate_sha256"}
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _canonical_json_lines(path: Path) -> tuple[dict[str, Any], ...]:
    records: list[dict[str, Any]] = []
    with path.open("rb") as stream:
        for line_number, raw in enumerate(stream, 1):
            if not raw.endswith(b"\n") or raw == b"\n":
                raise PositiveWitnessMismatch(f"noncanonical JSONL at line {line_number}")
            try:
                value = json.loads(raw)
            except json.JSONDecodeError as error:
                raise PositiveWitnessMismatch(f"malformed JSONL at line {line_number}") from error
            if type(value) is not dict or raw != canonical_bytes(value) + b"\n":
                raise PositiveWitnessMismatch(f"noncanonical JSONL at line {line_number}")
            records.append(value)
    return tuple(records)


def _coordinate_sum_is_zero(sequence: Sequence[int], selected: Sequence[int]) -> bool:
    totals = [0, 0, 0]
    for index in selected:
        element = sequence[index]
        totals[0] += element // 25
        totals[1] += (element % 25) // 5
        totals[2] += element % 5
    return all(value % 5 == 0 for value in totals)


def _verify_sat(record: Mapping[str, Any], certificate: Mapping[str, Any]) -> None:
    expected_fields = {
        "schema",
        "subject_commit",
        "record_id",
        "status",
        "solver_identity",
        "sequence_sha256",
        "required_bins",
        "cnf_sha256",
        "witness_bins",
        "certificate_sha256",
    }
    if set(certificate) != expected_fields:
        raise PositiveWitnessMismatch("positive certificate fields are not exact")
    if certificate.get("schema") != "ORION.NQ.EngineB.SATCertificate.v1":
        raise PositiveWitnessMismatch("positive certificate schema mismatch")
    if certificate.get("subject_commit") != SUBJECT_COMMIT:
        raise PositiveWitnessMismatch("positive certificate subject mismatch")
    if certificate.get("record_id") != record.get("record_id"):
        raise PositiveWitnessMismatch("positive certificate record binding mismatch")
    if certificate.get("status") != SAT_STATUS:
        raise PositiveWitnessMismatch("positive certificate status mismatch")
    sequence = record.get("sequence")
    required_bins = record.get("required_bins")
    if (
        type(sequence) is not list
        or not sequence
        or any(type(element) is not int or not 0 <= element < 125 for element in sequence)
    ):
        raise PositiveWitnessMismatch("record sequence is malformed")
    if type(required_bins) is not int or not 1 <= required_bins <= 4:
        raise PositiveWitnessMismatch("record bin requirement is malformed")
    if certificate.get("required_bins") != required_bins:
        raise PositiveWitnessMismatch("positive certificate bin count mismatch")
    if certificate.get("sequence_sha256") != hashlib.sha256(canonical_bytes(sequence)).hexdigest():
        raise PositiveWitnessMismatch("positive certificate sequence digest mismatch")
    if not SHA256.fullmatch(str(certificate.get("cnf_sha256", ""))):
        raise PositiveWitnessMismatch("positive certificate CNF digest is malformed")
    if certificate.get("certificate_sha256") != canonical_digest(certificate):
        raise PositiveWitnessMismatch("positive certificate content digest mismatch")
    bins = certificate.get("witness_bins")
    if type(bins) is not list or len(bins) != required_bins:
        raise PositiveWitnessMismatch("positive witness bin count mismatch")
    flattened: list[int] = []
    for selected in bins:
        if (
            type(selected) is not list
            or not selected
            or any(type(index) is not int or not 0 <= index < len(sequence) for index in selected)
            or selected != sorted(set(selected))
        ):
            raise PositiveWitnessMismatch("positive witness indices are malformed")
        flattened.extend(selected)
        if not _coordinate_sum_is_zero(sequence, selected):
            raise PositiveWitnessMismatch("positive witness bin is not zero-sum")
    if len(flattened) != len(set(flattened)):
        raise PositiveWitnessMismatch("positive witness bins are not disjoint")


def verify_positive_witness_streams(
    record_stream: Path, certificate_stream: Path
) -> dict[str, Any]:
    records = _canonical_json_lines(record_stream)
    certificates = _canonical_json_lines(certificate_stream)
    record_by_id: dict[str, dict[str, Any]] = {}
    for record in records:
        record_id = record.get("record_id")
        if type(record_id) is not str or record_id in record_by_id:
            raise PositiveWitnessMismatch("record identifiers are missing or duplicate")
        record_by_id[record_id] = record
    seen: set[str] = set()
    sat_count = 0
    for certificate in certificates:
        record_id = certificate.get("record_id")
        if type(record_id) is not str or record_id not in record_by_id or record_id in seen:
            raise PositiveWitnessMismatch(
                "certificate identifiers are missing, unknown, or duplicate"
            )
        seen.add(record_id)
        status = certificate.get("status")
        if status == SAT_STATUS:
            _verify_sat(record_by_id[record_id], certificate)
            sat_count += 1
        elif status != UNSAT_STATUS:
            raise PositiveWitnessMismatch("certificate has an unknown status")
    if seen != set(record_by_id):
        raise PositiveWitnessMismatch("certificate stream does not cover the record stream")
    core: dict[str, Any] = {
        "schema": "ORION.ORION04.CRB.PositiveWitnessGateReceipt.v1",
        "terminal": "ORION04_CRB_POSITIVE_WITNESSES_INDEPENDENTLY_RECHECKED",
        "record_count": len(records),
        "certificate_count": len(certificates),
        "sat_witnesses_verified": sat_count,
        "record_stream_sha256": _file_sha256(record_stream),
        "certificate_stream_sha256": _file_sha256(certificate_stream),
        "implementation_independence": "STANDARD_LIBRARY_ONLY_NO_ENGINE_IMPORT",
        "unsat_authority": "NONE_EXTERNAL_DRUP_GATE_SEPARATE",
        "d4": "OPEN",
        "scientific_authority_delta": "NONE_UNTIL_FULL_REPLAY_CHAIN_ADJUDICATED",
    }
    return {**core, "receipt_sha256": hashlib.sha256(canonical_bytes(core)).hexdigest()}


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record-stream", type=Path, required=True)
    parser.add_argument("--certificates", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    receipt = verify_positive_witness_streams(args.record_stream, args.certificates)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(f".{args.output.name}.{os.getpid()}.tmp")
    temporary.write_bytes(canonical_bytes(receipt) + b"\n")
    os.replace(temporary, args.output)
    print(json.dumps({"terminal": receipt["terminal"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
