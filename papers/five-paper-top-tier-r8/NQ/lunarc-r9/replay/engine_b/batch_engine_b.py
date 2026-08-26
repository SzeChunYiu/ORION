"""Input, coverage, proof, and receipt boundaries for NQ clean-room Engine B."""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator, Mapping, Sequence

import engine_b as eb


class InputManifestMismatch(RuntimeError):
    pass


class InputRecordMismatch(RuntimeError):
    pass


class CoverageIncomplete(RuntimeError):
    pass


class ResourceBound(RuntimeError):
    pass


class SolverEnvironmentUnavailable(RuntimeError):
    pass


SHA256 = re.compile(r"[0-9a-f]{64}")
RECORD_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}")
COVERAGE_FIELDS = {
    "schema",
    "subject_commit",
    "scope",
    "declared_complete",
    "expected_record_count",
    "coverage_argument_sha256",
    "generator_identity",
    "normalization_identity",
}


@dataclass(frozen=True)
class SequenceRecord:
    record_id: str
    scope: str
    sequence: tuple[int, ...]
    required_bins: int


@dataclass(frozen=True)
class VerifiedInputBundle:
    stream_path: Path
    coverage_path: Path
    record_count: int
    scope: str
    manifest_sha256: str


def _file_record(root: Path, relative: str) -> dict[str, Any]:
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != relative:
        raise ValueError(f"input path is not canonical: {relative}")
    source = root / path
    if source.is_symlink():
        raise ValueError(f"input path must not be a symlink: {relative}")
    data = source.read_bytes()
    return {
        "path": relative,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def _manifest_digest(manifest: Mapping[str, Any]) -> str:
    payload = {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    return hashlib.sha256(eb.canonical_json_bytes(payload)).hexdigest()


def _parse_record_object(value: Any) -> SequenceRecord:
    if type(value) is not dict or set(value) != {
        "schema",
        "record_id",
        "scope",
        "sequence",
        "required_bins",
    }:
        raise InputRecordMismatch("sequence record fields are not exact")
    if value["schema"] != "ORION.NQ.EngineB.SequenceRecord.v1":
        raise InputRecordMismatch("sequence record schema mismatch")
    if type(value["record_id"]) is not str or not RECORD_ID.fullmatch(value["record_id"]):
        raise InputRecordMismatch("sequence record_id is not canonical")
    if type(value["scope"]) is not str or not value["scope"]:
        raise InputRecordMismatch("sequence scope is missing")
    if type(value["sequence"]) is not list:
        raise InputRecordMismatch("sequence payload must be a JSON list")
    sequence = tuple(value["sequence"])
    if not 1 <= len(sequence) <= 31 or any(
        type(element) is not int or not 0 <= element < 125 for element in sequence
    ):
        raise InputRecordMismatch("sequence is outside the canonical length-31 group scope")
    required_bins = value["required_bins"]
    if type(required_bins) is not int or not 1 <= required_bins <= 4:
        raise InputRecordMismatch("required_bins is outside Engine B scope")
    return SequenceRecord(value["record_id"], value["scope"], sequence, required_bins)


def iter_records(path: Path) -> Iterator[SequenceRecord]:
    seen: set[str] = set()
    with path.open("rb") as stream:
        for line_number, raw_line in enumerate(stream, 1):
            if not raw_line.endswith(b"\n") or raw_line == b"\n":
                raise InputRecordMismatch(
                    f"record line {line_number} is empty or lacks its final newline"
                )
            payload = raw_line[:-1]
            try:
                value = json.loads(payload)
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                raise InputRecordMismatch(
                    f"record line {line_number} is not canonical JSON"
                ) from error
            if eb.canonical_json_bytes(value) != payload:
                raise InputRecordMismatch(f"record line {line_number} is not canonical JSON")
            record = _parse_record_object(value)
            if record.record_id in seen:
                raise InputRecordMismatch(f"duplicate record_id: {record.record_id}")
            seen.add(record.record_id)
            yield record


def _load_coverage(path: Path) -> dict[str, Any]:
    try:
        coverage = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise InputManifestMismatch("coverage declaration cannot be parsed") from error
    if type(coverage) is not dict or set(coverage) != COVERAGE_FIELDS:
        raise InputManifestMismatch("coverage declaration fields are not exact")
    if coverage["schema"] != "ORION.NQ.EngineB.CoverageDeclaration.v1":
        raise InputManifestMismatch("coverage declaration schema mismatch")
    if coverage["subject_commit"] != eb.SUBJECT_COMMIT:
        raise InputManifestMismatch("coverage declaration subject mismatch")
    if type(coverage["scope"]) is not str or not coverage["scope"]:
        raise InputManifestMismatch("coverage declaration scope is missing")
    if type(coverage["expected_record_count"]) is not int or coverage["expected_record_count"] < 0:
        raise InputManifestMismatch("coverage expected_record_count is invalid")
    if type(coverage["coverage_argument_sha256"]) is not str or not SHA256.fullmatch(
        coverage["coverage_argument_sha256"]
    ):
        raise InputManifestMismatch("coverage argument digest is invalid")
    if type(coverage["generator_identity"]) is not str or not coverage["generator_identity"]:
        raise InputManifestMismatch("coverage generator identity is missing")
    if (
        type(coverage["normalization_identity"]) is not str
        or not coverage["normalization_identity"]
    ):
        raise InputManifestMismatch("coverage normalization identity is missing")
    if type(coverage["declared_complete"]) is not bool:
        raise InputManifestMismatch("coverage declared_complete flag is not Boolean")
    return coverage


def build_input_manifest(root: Path, *, stream_path: str, coverage_path: str) -> dict[str, Any]:
    root = root.resolve()
    stream_record = _file_record(root, stream_path)
    coverage_record = _file_record(root, coverage_path)
    records = tuple(iter_records(root / stream_path))
    coverage = _load_coverage(root / coverage_path)
    scopes = {record.scope for record in records}
    if scopes != {coverage["scope"]}:
        raise InputManifestMismatch("record scopes do not match the coverage declaration")
    manifest: dict[str, Any] = {
        "schema": "ORION.NQ.EngineB.InputManifest.v1",
        "subject_commit": eb.SUBJECT_COMMIT,
        "scope": coverage["scope"],
        "record_count": len(records),
        "stream": stream_record,
        "coverage": coverage_record,
    }
    manifest["manifest_sha256"] = _manifest_digest(manifest)
    return manifest


def _verify_file_record(root: Path, record: Mapping[str, Any]) -> Path:
    if type(record) is not dict or set(record) != {"path", "bytes", "sha256"}:
        raise InputManifestMismatch("input manifest file record shape is not exact")
    observed = _file_record(root, record["path"])
    if observed != record:
        raise InputManifestMismatch(f"input manifest mismatch for {record['path']}")
    return root / record["path"]


def verify_input_manifest(root: Path, manifest: Mapping[str, Any]) -> VerifiedInputBundle:
    root = root.resolve()
    if type(manifest) is not dict or set(manifest) != {
        "schema",
        "subject_commit",
        "scope",
        "record_count",
        "stream",
        "coverage",
        "manifest_sha256",
    }:
        raise InputManifestMismatch("input manifest fields are not exact")
    if manifest["schema"] != "ORION.NQ.EngineB.InputManifest.v1":
        raise InputManifestMismatch("input manifest schema mismatch")
    if manifest["subject_commit"] != eb.SUBJECT_COMMIT:
        raise InputManifestMismatch("input manifest subject mismatch")
    if manifest["manifest_sha256"] != _manifest_digest(manifest):
        raise InputManifestMismatch("input manifest content digest mismatch")
    stream_path = _verify_file_record(root, manifest["stream"])
    coverage_path = _verify_file_record(root, manifest["coverage"])
    coverage = _load_coverage(coverage_path)
    if not coverage["declared_complete"]:
        raise CoverageIncomplete("input coverage is not declared complete")
    records = tuple(iter_records(stream_path))
    if (
        len(records) != manifest["record_count"]
        or len(records) != coverage["expected_record_count"]
    ):
        raise InputManifestMismatch("input record count does not match its bindings")
    if manifest["scope"] != coverage["scope"] or {record.scope for record in records} != {
        coverage["scope"]
    }:
        raise InputManifestMismatch("input scope does not match its bindings")
    return VerifiedInputBundle(
        stream_path,
        coverage_path,
        len(records),
        coverage["scope"],
        manifest["manifest_sha256"],
    )


def _certificate_digest(certificate: Mapping[str, Any]) -> str:
    payload = {key: value for key, value in certificate.items() if key != "certificate_sha256"}
    return hashlib.sha256(eb.canonical_json_bytes(payload)).hexdigest()


def _certificate_artifact(
    source_path: Path, *, artifact_root: Path, artifact_format: str
) -> dict[str, Any]:
    root = artifact_root.resolve()
    source = source_path.resolve()
    if source.is_symlink() or not source.is_relative_to(root):
        raise ValueError("certificate artifact escapes its declared root or is a symlink")
    data = source.read_bytes()
    return {
        "path": source.relative_to(root).as_posix(),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "format": artifact_format,
    }


def build_unsat_certificate(
    *,
    record_id: str,
    encoded: eb.FactorizationEncoding,
    solver_identity: str,
    cnf_path: Path,
    proof_path: Path,
    artifact_root: Path,
) -> dict[str, Any]:
    cnf = _certificate_artifact(cnf_path, artifact_root=artifact_root, artifact_format="DIMACS_CNF")
    proof = _certificate_artifact(proof_path, artifact_root=artifact_root, artifact_format="DRUP")
    proof["externally_checked"] = False
    certificate: dict[str, Any] = {
        "schema": "ORION.NQ.EngineB.UNSATCertificate.v2",
        "subject_commit": eb.SUBJECT_COMMIT,
        "record_id": record_id,
        "status": "UNSAT_PROOF_EMITTED_REQUIRES_EXTERNAL_CHECK",
        "solver_identity": solver_identity,
        "sequence_sha256": hashlib.sha256(
            eb.canonical_json_bytes(list(encoded.sequence))
        ).hexdigest(),
        "required_bins": encoded.required_bins,
        "cnf_sha256": encoded.cnf_sha256,
        "cnf": cnf,
        "proof": proof,
    }
    certificate["certificate_sha256"] = _certificate_digest(certificate)
    return certificate


def verify_unsat_certificate_bindings(
    certificate: Mapping[str, Any],
    *,
    sequence: Sequence[int],
    required_bins: int,
    artifact_root: Path,
) -> None:
    if type(certificate) is not dict or set(certificate) != {
        "schema",
        "subject_commit",
        "record_id",
        "status",
        "solver_identity",
        "sequence_sha256",
        "required_bins",
        "cnf_sha256",
        "cnf",
        "proof",
        "certificate_sha256",
    }:
        raise eb.CertificateMismatch("UNSAT certificate fields are not exact")
    if certificate.get("schema") != "ORION.NQ.EngineB.UNSATCertificate.v2":
        raise eb.CertificateMismatch("UNSAT certificate schema mismatch")
    if certificate.get("subject_commit") != eb.SUBJECT_COMMIT:
        raise eb.CertificateMismatch("UNSAT certificate subject mismatch")
    if type(certificate.get("record_id")) is not str or not RECORD_ID.fullmatch(
        certificate["record_id"]
    ):
        raise eb.CertificateMismatch("UNSAT certificate record id is not canonical")
    if certificate.get("status") != "UNSAT_PROOF_EMITTED_REQUIRES_EXTERNAL_CHECK":
        raise eb.CertificateMismatch("UNSAT certificate status mismatch")
    if type(certificate.get("solver_identity")) is not str or not certificate["solver_identity"]:
        raise eb.CertificateMismatch("UNSAT certificate solver identity is missing")
    if certificate.get("required_bins") != required_bins:
        raise eb.CertificateMismatch("UNSAT certificate bin mismatch")
    encoded = eb.build_factorization_cnf(sequence, required_bins)
    if certificate.get("cnf_sha256") != encoded.cnf_sha256:
        raise eb.CertificateMismatch("UNSAT certificate CNF mismatch")
    sequence_digest = hashlib.sha256(eb.canonical_json_bytes(list(encoded.sequence))).hexdigest()
    if certificate.get("sequence_sha256") != sequence_digest:
        raise eb.CertificateMismatch("UNSAT certificate sequence mismatch")
    if certificate.get("certificate_sha256") != _certificate_digest(certificate):
        raise eb.CertificateMismatch("UNSAT certificate content digest mismatch")
    try:
        root = artifact_root.resolve()
        for label, expected_format in (("cnf", "DIMACS_CNF"), ("proof", "DRUP")):
            artifact = certificate[label]
            expected_fields = {"path", "bytes", "sha256", "format"}
            if label == "proof":
                expected_fields.add("externally_checked")
            if type(artifact) is not dict or set(artifact) != expected_fields:
                raise eb.CertificateMismatch(f"UNSAT {label} binding fields are not exact")
            path = Path(artifact["path"])
            if (
                type(artifact["path"]) is not str
                or path.is_absolute()
                or ".." in path.parts
                or path.as_posix() != artifact["path"]
            ):
                raise eb.CertificateMismatch(f"UNSAT {label} path is not canonical")
            source = root / path
            if source.is_symlink() or not source.resolve().is_relative_to(root):
                raise eb.CertificateMismatch(f"UNSAT {label} path escapes its root")
            data = source.read_bytes()
            observed = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
            if observed != {"bytes": artifact["bytes"], "sha256": artifact["sha256"]}:
                raise eb.CertificateMismatch(f"UNSAT {label} content binding mismatch")
            if artifact["format"] != expected_format:
                raise eb.CertificateMismatch(f"UNSAT {label} format mismatch")
        if certificate["proof"]["externally_checked"] is not False:
            raise eb.CertificateMismatch("UNSAT certificate launders external proof checking")
        if (root / certificate["cnf"]["path"]).read_bytes() != dimacs_bytes(encoded.cnf):
            raise eb.CertificateMismatch("UNSAT DIMACS bytes differ from the encoded CNF")
    except (KeyError, OSError, TypeError) as error:
        raise eb.CertificateMismatch("UNSAT artifact binding is malformed") from error


def seal_receipt(payload: Mapping[str, Any], bindings: Mapping[str, Any]) -> dict[str, Any]:
    receipt: dict[str, Any] = {
        "schema": "ORION.NQ.EngineB.Receipt.v1",
        "subject_commit": eb.SUBJECT_COMMIT,
        "payload": dict(payload),
        "bindings": dict(bindings),
        "authority": {
            "blinded_independence": "NOT_CLAIMED",
            "d4_c5_cubed": "OPEN",
            "paper_authority_delta": "NONE",
            "scientific_authority_delta": "NONE",
        },
    }
    receipt["receipt_sha256"] = hashlib.sha256(eb.canonical_json_bytes(receipt)).hexdigest()
    return receipt


def build_resource_bound_receipt(
    *,
    source_manifest_sha256: str,
    input_manifest_sha256: str,
    processed_records: int,
    total_records: int,
    reason: str,
) -> dict[str, Any]:
    if not 0 <= processed_records <= total_records:
        raise ValueError("processed record count is outside total records")
    return seal_receipt(
        {
            "terminal": "CANNOT_CHECK_RESOURCE_BOUND",
            "reason": reason,
            "processed_records": processed_records,
            "unprocessed_records": total_records - processed_records,
            "total_records": total_records,
            "d4_c5_cubed": "OPEN",
            "full_strata_closed": False,
        },
        {
            "source_manifest_sha256": source_manifest_sha256,
            "input_manifest_sha256": input_manifest_sha256,
        },
    )


def build_environment_receipt(
    *,
    source_manifest_sha256: str,
    input_manifest_sha256: str,
    total_records: int,
    reason: str,
) -> dict[str, Any]:
    return seal_receipt(
        {
            "terminal": "CANNOT_CHECK_ENVIRONMENT",
            "reason": reason,
            "processed_records": 0,
            "unprocessed_records": total_records,
            "total_records": total_records,
            "d4_c5_cubed": "OPEN",
            "full_strata_closed": False,
        },
        {
            "source_manifest_sha256": source_manifest_sha256,
            "input_manifest_sha256": input_manifest_sha256,
        },
    )


def dimacs_bytes(cnf: eb.CNF) -> bytes:
    lines = [f"p cnf {cnf.variable_count} {len(cnf.clauses)}\n"]
    lines.extend(" ".join(map(str, clause)) + " 0\n" for clause in cnf.clauses)
    return "".join(lines).encode("ascii")


def write_dimacs(cnf: eb.CNF, destination: Path) -> None:
    destination.write_bytes(dimacs_bytes(cnf))


def solve_record_with_pysat(
    record: SequenceRecord,
    *,
    proof_root: Path,
    solver_name: str = "g4",
) -> dict[str, Any]:
    try:
        from pysat.solvers import Solver
    except ImportError as error:
        raise SolverEnvironmentUnavailable("python-sat is not installed") from error
    encoded = eb.build_factorization_cnf(record.sequence, record.required_bins)
    with Solver(name=solver_name, bootstrap_with=encoded.cnf.clauses, with_proof=True) as solver:
        if solver.solve():
            model_values = solver.get_model() or []
            model = {abs(literal): literal > 0 for literal in model_values}
            return eb.build_sat_certificate(
                record_id=record.record_id,
                encoded=encoded,
                model=model,
                solver_identity=f"PYTHON_SAT_{solver_name}",
            )
        proof_lines = solver.get_proof()
    if not proof_lines:
        raise SolverEnvironmentUnavailable("SAT solver returned UNSAT without a proof")
    proof_root.mkdir(parents=True, exist_ok=True)
    cnf_path = proof_root / f"{record.record_id}.cnf"
    cnf_temporary = cnf_path.with_name(f".{cnf_path.name}.{os.getpid()}.tmp")
    cnf_temporary.write_bytes(dimacs_bytes(encoded.cnf))
    os.replace(cnf_temporary, cnf_path)
    proof_path = proof_root / f"{record.record_id}.drup"
    temporary = proof_path.with_name(f".{proof_path.name}.{os.getpid()}.tmp")
    temporary.write_text("\n".join(proof_lines) + "\n")
    os.replace(temporary, proof_path)
    return build_unsat_certificate(
        record_id=record.record_id,
        encoded=encoded,
        solver_identity=f"PYTHON_SAT_{solver_name}",
        cnf_path=cnf_path,
        proof_path=proof_path,
        artifact_root=proof_root,
    )


def chunk_records(records: Sequence[Any], chunk_size: int) -> tuple[tuple[Any, ...], ...]:
    if type(chunk_size) is not int or chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer")
    return tuple(
        tuple(records[index : index + chunk_size]) for index in range(0, len(records), chunk_size)
    )


def _solve_chunk_worker(
    arguments: tuple[tuple[SequenceRecord, ...], str, str, float],
) -> tuple[dict[str, Any], ...]:
    records, proof_root, solver_name, deadline = arguments
    results = []
    for record in records:
        if time.monotonic() >= deadline:
            raise ResourceBound("wall clock guard reached before record dispatch")
        results.append(
            solve_record_with_pysat(record, proof_root=Path(proof_root), solver_name=solver_name)
        )
        if time.monotonic() >= deadline:
            raise ResourceBound("wall clock guard reached after record execution")
    return tuple(results)


def execute_bundle(
    bundle: VerifiedInputBundle,
    *,
    certificates_path: Path,
    proof_root: Path,
    threads: int,
    max_wall_seconds: int,
    solver_name: str = "g4",
) -> dict[str, Any]:
    if type(threads) is not int or not 1 <= threads <= 32:
        raise ValueError("threads must be an integer from one through thirty-two")
    if type(max_wall_seconds) is not int or max_wall_seconds <= 0:
        raise ValueError("max_wall_seconds must be positive")
    records = tuple(iter_records(bundle.stream_path))
    deadline = time.monotonic() + max_wall_seconds
    arguments = tuple(
        (chunk, str(proof_root), solver_name, deadline) for chunk in chunk_records(records, 64)
    )
    certificates_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = certificates_path.with_name(f".{certificates_path.name}.{os.getpid()}.tmp")
    sat_count = 0
    unsat_unchecked = 0
    processed = 0
    with temporary.open("wb") as output:
        with ProcessPoolExecutor(max_workers=threads) as executor:
            for certificate_chunk in executor.map(_solve_chunk_worker, arguments, chunksize=1):
                for certificate in certificate_chunk:
                    output.write(eb.canonical_json_bytes(certificate) + b"\n")
                    processed += 1
                    sat_count += certificate["status"] == "SAT_K_DISJOINT_ZERO_SUMS"
                    unsat_unchecked += (
                        certificate["status"] == "UNSAT_PROOF_EMITTED_REQUIRES_EXTERNAL_CHECK"
                    )
    os.replace(temporary, certificates_path)
    data = certificates_path.read_bytes()
    terminal = (
        "NQ_ENGINE_B_STRUCTURAL_EXECUTION_COMPLETE"
        if unsat_unchecked == 0
        else "CANNOT_CHECK_ENVIRONMENT"
    )
    return {
        "terminal": terminal,
        "processed_records": processed,
        "total_records": len(records),
        "sat_witness_certificates": sat_count,
        "unsat_proofs_requiring_external_check": unsat_unchecked,
        "certificate_stream": {
            "path": certificates_path.name,
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        },
        "coverage_audit": "HASH_BOUND_DECLARATION_NOT_EXTERNALLY_AUDITED",
        "d4_c5_cubed": "OPEN",
        "full_strata_closed": False,
        "blinded_independence": "NOT_CLAIMED",
    }
