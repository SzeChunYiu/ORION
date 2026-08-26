#!/usr/bin/env python3
"""Independent, fail-closed verifier for CR-B aggregate bundles.

This module intentionally does not import or reuse an aggregate producer's
normalizer, partition builder, or proof-checking wrapper.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import subprocess
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path, PurePosixPath
from typing import Any


CONTRACT_VERSION = "orion.crb.independent-bundle.v1"
FIELD_ORDER = 5
VECTOR_DIMENSION = 3
AUTHORITY = "internal_conformance_only"


class VerificationError(ValueError):
    """Raised when a bundle cannot satisfy the independent contract."""


def _canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        separators=(",", ":"),
    ).encode("ascii")


def _json_sha256(value: object) -> str:
    return hashlib.sha256(_canonical_json_bytes(value)).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_mapping(value: object, context: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise VerificationError(f"{context} must be a JSON object")
    return value


def _require_list(value: object, context: str) -> list[Any]:
    if not isinstance(value, list):
        raise VerificationError(f"{context} must be a JSON array")
    return value


def _require_int(value: object, context: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise VerificationError(f"{context} must be an integer >= {minimum}")
    return value


def _require_string(value: object, context: str) -> str:
    if not isinstance(value, str) or not value:
        raise VerificationError(f"{context} must be a nonempty string")
    return value


def _require_sha256(value: object, context: str) -> str:
    text = _require_string(value, context)
    if len(text) != 64 or any(character not in "0123456789abcdef" for character in text):
        raise VerificationError(f"{context} must be a lowercase SHA-256 hex digest")
    return text


def _require_exact_keys(value: Mapping[str, Any], expected: set[str], context: str) -> None:
    missing = expected.difference(value)
    extra = set(value).difference(expected)
    if missing or extra:
        details: list[str] = []
        if missing:
            details.append(f"missing={sorted(missing)}")
        if extra:
            details.append(f"extra={sorted(extra)}")
        raise VerificationError(f"{context} has invalid keys ({', '.join(details)})")


def _invert_matrix_mod_5(matrix: tuple[tuple[int, ...], ...]) -> tuple[tuple[int, ...], ...]:
    augmented = [
        [*matrix[row], *(1 if row == column else 0 for column in range(VECTOR_DIMENSION))]
        for row in range(VECTOR_DIMENSION)
    ]

    for column in range(VECTOR_DIMENSION):
        pivot = next(
            (row for row in range(column, VECTOR_DIMENSION) if augmented[row][column]),
            None,
        )
        if pivot is None:
            raise VerificationError("anchor matrix is singular over F5")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]

        inverse = pow(augmented[column][column], -1, FIELD_ORDER)
        augmented[column] = [(entry * inverse) % FIELD_ORDER for entry in augmented[column]]
        for row in range(VECTOR_DIMENSION):
            if row == column:
                continue
            factor = augmented[row][column]
            augmented[row] = [
                (entry - factor * pivot_entry) % FIELD_ORDER
                for entry, pivot_entry in zip(augmented[row], augmented[column], strict=True)
            ]

    return tuple(tuple(augmented[row][VECTOR_DIMENSION:]) for row in range(VECTOR_DIMENSION))


def _parse_sequence(sequence: object) -> tuple[tuple[int, int, int], ...]:
    if isinstance(sequence, (str, bytes)) or not isinstance(sequence, Sequence):
        raise VerificationError("representative must be a sequence of F5 vectors")
    if len(sequence) < VECTOR_DIMENSION:
        raise VerificationError("representative must contain at least three vectors")

    parsed: list[tuple[int, int, int]] = []
    for vector_index, vector in enumerate(sequence):
        if isinstance(vector, (str, bytes)) or not isinstance(vector, Sequence):
            raise VerificationError(f"representative vector {vector_index} must be an array")
        if len(vector) != VECTOR_DIMENSION:
            raise VerificationError(
                f"representative vector {vector_index} must have dimension {VECTOR_DIMENSION}"
            )
        entries: list[int] = []
        for coordinate_index, coordinate in enumerate(vector):
            if (
                isinstance(coordinate, bool)
                or not isinstance(coordinate, int)
                or not 0 <= coordinate < FIELD_ORDER
            ):
                raise VerificationError(
                    "representative coordinate "
                    f"{vector_index}:{coordinate_index} is not an element of F5"
                )
            entries.append(coordinate)
        parsed.append((entries[0], entries[1], entries[2]))
    return tuple(parsed)


def normalize_sequence(sequence: object) -> tuple[tuple[int, int, int], ...]:
    """Return the lexicographically minimal full-rank GL(3, F5) representative.

    Vectors are interpreted as columns. Every ordered independent anchor triple
    is mapped to the standard basis, all transformed columns are sorted, and
    the least resulting tuple is returned. Rank-deficient input fails closed.
    """

    vectors = _parse_sequence(sequence)
    candidates: list[tuple[tuple[int, int, int], ...]] = []

    for anchors in itertools.permutations(range(len(vectors)), VECTOR_DIMENSION):
        matrix = tuple(
            tuple(vectors[anchors[column]][row] for column in range(VECTOR_DIMENSION))
            for row in range(VECTOR_DIMENSION)
        )
        try:
            inverse = _invert_matrix_mod_5(matrix)
        except VerificationError:
            continue

        transformed = tuple(
            sorted(
                tuple(
                    sum(inverse[row][column] * vector[column] for column in range(3)) % FIELD_ORDER
                    for row in range(3)
                )
                for vector in vectors
            )
        )
        candidates.append(transformed)

    if not candidates:
        raise VerificationError("representative is not full rank over F5")
    return min(candidates)


def _reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise VerificationError(f"manifest contains duplicate JSON key {key!r}")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> None:
    raise VerificationError(f"manifest contains non-finite JSON constant {value}")


def _load_manifest(path: Path) -> Mapping[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise VerificationError(f"manifest is not a regular file: {path}")
    try:
        loaded = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_json_keys,
            parse_constant=_reject_json_constant,
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise VerificationError(f"cannot load manifest: {exc}") from exc
    return _require_mapping(loaded, "manifest")


def _safe_bundle_file(bundle_root: Path, relative: object, label: str) -> Path:
    text = _require_string(relative, f"{label} path")
    if "\\" in text:
        raise VerificationError(f"{label} path must use POSIX separators")
    pure = PurePosixPath(text)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise VerificationError(f"{label} path must be a normalized relative path")

    candidate = bundle_root.joinpath(*pure.parts)
    if not candidate.exists():
        raise VerificationError(f"missing {label}: {text}")
    if candidate.is_symlink() or not candidate.is_file():
        raise VerificationError(f"{label} is not a regular nonsymlink file: {text}")
    resolved = candidate.resolve()
    try:
        resolved.relative_to(bundle_root)
    except ValueError as exc:
        raise VerificationError(f"{label} escapes the bundle root: {text}") from exc
    return resolved


def _safe_bundle_directory(bundle_root: Path, relative: object, label: str) -> Path:
    text = _require_string(relative, f"{label} path")
    if "\\" in text:
        raise VerificationError(f"{label} path must use POSIX separators")
    pure = PurePosixPath(text)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise VerificationError(f"{label} path must be a normalized relative path")
    candidate = bundle_root.joinpath(*pure.parts)
    if candidate.is_symlink() or not candidate.is_dir():
        raise VerificationError(f"{label} is not a regular directory: {text}")
    resolved = candidate.resolve()
    try:
        resolved.relative_to(bundle_root)
    except ValueError as exc:
        raise VerificationError(f"{label} escapes the bundle root: {text}") from exc
    return resolved


def _verify_size_and_hash(
    path: Path,
    expected_size: object,
    expected_digest: object,
    label: str,
) -> None:
    size = _require_int(expected_size, f"{label} byte size")
    if path.stat().st_size != size:
        raise VerificationError(f"{label} size mismatch for {path.name}")
    digest = _require_sha256(expected_digest, f"{label} SHA-256")
    if _file_sha256(path) != digest:
        raise VerificationError(f"{label} hash mismatch for {path.name}")


def _parse_proof_binding(
    binding_value: object,
    *,
    bundle_root: Path,
    proof_root: Path,
    seen_proof_ids: set[str],
    seen_proof_paths: set[Path],
    seen_cnf_paths: set[Path],
) -> tuple[Path, Path]:
    binding = _require_mapping(binding_value, "UNSAT proof binding")
    _require_exact_keys(
        binding,
        {
            "proof_id",
            "proof_format",
            "cnf_path",
            "cnf_bytes",
            "cnf_sha256",
            "proof_path",
            "proof_bytes",
            "proof_sha256",
        },
        "UNSAT proof binding",
    )

    proof_format = _require_string(binding["proof_format"], "proof format")
    if proof_format not in {"DRAT", "DRUP"}:
        raise VerificationError("proof format must be DRAT or DRUP")

    cnf = _safe_bundle_file(bundle_root, binding["cnf_path"], "CNF")
    proof = _safe_bundle_file(bundle_root, binding["proof_path"], "proof")
    try:
        proof.relative_to(proof_root)
    except ValueError as exc:
        raise VerificationError("proof path is outside the declared proof root") from exc

    if proof in seen_proof_paths:
        raise VerificationError(f"reused proof path: {binding['proof_path']}")
    if cnf in seen_cnf_paths:
        raise VerificationError(f"reused CNF path: {binding['cnf_path']}")
    seen_proof_paths.add(proof)
    seen_cnf_paths.add(cnf)

    proof_id = _require_string(binding["proof_id"], "proof ID")
    if proof_id in seen_proof_ids:
        raise VerificationError(f"duplicate proof ID: {proof_id}")
    seen_proof_ids.add(proof_id)

    _verify_size_and_hash(cnf, binding["cnf_bytes"], binding["cnf_sha256"], "CNF")
    _verify_size_and_hash(
        proof,
        binding["proof_bytes"],
        binding["proof_sha256"],
        "proof",
    )
    return cnf, proof


def _verify_external_checker(
    checker_path: Path,
    manifest_digest: object,
    independent_digest: object,
) -> str:
    if checker_path.is_symlink() or not checker_path.is_file():
        raise VerificationError(
            f"external checker is not a regular nonsymlink file: {checker_path}"
        )
    if not os.access(checker_path, os.X_OK):
        raise VerificationError(f"external checker is not executable: {checker_path}")
    manifest_pin = _require_sha256(manifest_digest, "manifest checker SHA-256")
    independent_pin = _require_sha256(independent_digest, "independent checker SHA-256")
    if manifest_pin != independent_pin:
        raise VerificationError(
            "checker hash mismatch: manifest does not match the independent pin"
        )
    actual_digest = _file_sha256(checker_path)
    if actual_digest != independent_pin:
        raise VerificationError("external checker hash mismatch")
    return actual_digest


def _invoke_external_checker(
    checker_path: Path,
    cnf_path: Path,
    proof_path: Path,
    *,
    bundle_root: Path,
    timeout_seconds: float,
) -> None:
    try:
        completed = subprocess.run(
            [str(checker_path), str(cnf_path), str(proof_path)],
            cwd=bundle_root,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            shell=False,
            timeout=timeout_seconds,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise VerificationError(f"external checker could not complete: {exc}") from exc
    if completed.returncode != 0:
        raise VerificationError(
            "external checker rejected "
            f"{proof_path.name} for {cnf_path.name} with exit {completed.returncode}"
        )


def verify_bundle(
    manifest_path: str | Path,
    checker_path: str | Path,
    *,
    checker_sha256: str,
    checker_timeout_seconds: float = 300.0,
) -> dict[str, object]:
    """Verify a CR-B bundle and return a bounded internal-conformance report."""

    if checker_timeout_seconds <= 0:
        raise VerificationError("checker timeout must be positive")

    manifest_file = Path(manifest_path).expanduser().absolute()
    manifest = _load_manifest(manifest_file)
    bundle_root = manifest_file.parent.resolve()
    _require_exact_keys(
        manifest,
        {
            "contract_version",
            "field",
            "domain",
            "aggregate",
            "proof_root",
            "external_checker",
            "partitions",
        },
        "manifest",
    )
    if manifest["contract_version"] != CONTRACT_VERSION:
        raise VerificationError("unsupported contract version")

    field = _require_mapping(manifest["field"], "field")
    _require_exact_keys(field, {"order", "vector_dimension"}, "field")
    if field["order"] != FIELD_ORDER or field["vector_dimension"] != VECTOR_DIMENSION:
        raise VerificationError("field must be exactly three-dimensional F5")

    domain = _require_mapping(manifest["domain"], "domain")
    _require_exact_keys(domain, {"size", "sequence_length"}, "domain")
    domain_size = _require_int(domain["size"], "domain size", minimum=1)
    sequence_length = _require_int(
        domain["sequence_length"], "domain sequence length", minimum=VECTOR_DIMENSION
    )

    aggregate = _require_mapping(manifest["aggregate"], "aggregate")
    _require_exact_keys(aggregate, {"record_count", "outcomes"}, "aggregate")
    aggregate_record_count = _require_int(aggregate["record_count"], "aggregate record count")
    aggregate_outcomes = _require_mapping(aggregate["outcomes"], "aggregate outcomes")
    _require_exact_keys(aggregate_outcomes, {"SAT", "UNSAT"}, "aggregate outcomes")
    expected_sat = _require_int(aggregate_outcomes["SAT"], "aggregate SAT count")
    expected_unsat = _require_int(aggregate_outcomes["UNSAT"], "aggregate UNSAT count")

    proof_root = _safe_bundle_directory(bundle_root, manifest["proof_root"], "proof root")
    checker = Path(checker_path).expanduser().absolute()
    checker_contract = _require_mapping(manifest["external_checker"], "external checker")
    _require_exact_keys(checker_contract, {"sha256"}, "external checker")
    checker_digest = _verify_external_checker(
        checker,
        checker_contract["sha256"],
        checker_sha256,
    )

    partitions_value = _require_list(manifest["partitions"], "partitions")
    if not partitions_value:
        raise VerificationError("partitions must not be empty")

    partitions: list[tuple[int, int, Mapping[str, Any]]] = []
    for partition_index, partition_value in enumerate(partitions_value):
        partition = _require_mapping(partition_value, f"partition {partition_index}")
        _require_exact_keys(
            partition,
            {
                "partition_id",
                "start",
                "stop",
                "range_sha256",
                "record_count",
                "records",
            },
            f"partition {partition_index}",
        )
        start = _require_int(partition["start"], f"partition {partition_index} start")
        stop = _require_int(partition["stop"], f"partition {partition_index} stop")
        if stop <= start:
            raise VerificationError(f"partition {partition_index} range is empty")
        partitions.append((start, stop, partition))

    partitions.sort(key=lambda item: (item[0], item[1]))
    if partitions[0][0] != 0:
        raise VerificationError("partition coverage gap before ordinal 0")
    previous_stop = partitions[0][1]
    for start, stop, _partition in partitions[1:]:
        if start > previous_stop:
            raise VerificationError(f"partition coverage gap at ordinal {previous_stop}")
        if start < previous_stop:
            raise VerificationError(f"partition overlap at ordinal {start}")
        previous_stop = stop
    if previous_stop < domain_size:
        raise VerificationError(f"partition coverage gap after ordinal {previous_stop}")
    if previous_stop > domain_size:
        raise VerificationError("partition coverage exceeds declared domain size")

    seen_partition_ids: set[str] = set()
    seen_range_digests: set[str] = set()
    seen_representative_digests: set[str] = set()
    seen_proof_ids: set[str] = set()
    seen_proof_paths: set[Path] = set()
    seen_cnf_paths: set[Path] = set()
    proof_jobs: list[tuple[Path, Path]] = []
    record_total = 0
    outcome_counts = {"SAT": 0, "UNSAT": 0}

    for partition_index, (start, stop, partition) in enumerate(partitions):
        partition_id = _require_string(partition["partition_id"], "partition ID")
        if partition_id in seen_partition_ids:
            raise VerificationError(f"duplicate partition ID: {partition_id}")
        seen_partition_ids.add(partition_id)

        range_digest = _require_sha256(partition["range_sha256"], "range SHA-256")
        if range_digest != _json_sha256([start, stop]):
            raise VerificationError(f"range digest mismatch for {partition_id}")
        if range_digest in seen_range_digests:
            raise VerificationError(f"duplicate range digest for {partition_id}")
        seen_range_digests.add(range_digest)

        records = _require_list(partition["records"], f"records for {partition_id}")
        declared_count = _require_int(partition["record_count"], f"record count for {partition_id}")
        if declared_count != len(records):
            raise VerificationError(f"record count mismatch for {partition_id}")
        if declared_count != stop - start:
            raise VerificationError(f"record count does not fill range for {partition_id}")

        for offset, record_value in enumerate(records):
            context = f"record {partition_id}:{offset}"
            record = _require_mapping(record_value, context)
            outcome = record.get("outcome")
            if outcome == "SAT":
                expected_keys = {
                    "ordinal",
                    "representative",
                    "representative_sha256",
                    "outcome",
                }
            elif outcome == "UNSAT":
                expected_keys = {
                    "ordinal",
                    "representative",
                    "representative_sha256",
                    "outcome",
                    "proof",
                }
            else:
                raise VerificationError(f"{context} outcome must be SAT or UNSAT")
            _require_exact_keys(record, expected_keys, context)

            ordinal = _require_int(record["ordinal"], f"{context} ordinal")
            if ordinal != start + offset:
                raise VerificationError(f"{context} ordinal does not match its partition range")

            representative_value = _require_list(
                record["representative"], f"{context} representative"
            )
            if len(representative_value) != sequence_length:
                raise VerificationError(f"{context} representative has wrong sequence length")
            parsed = _parse_sequence(representative_value)
            canonical = normalize_sequence(parsed)
            if parsed != canonical:
                raise VerificationError(f"{context} representative is not canonical")

            representative_digest = _require_sha256(
                record["representative_sha256"], f"{context} representative SHA-256"
            )
            if representative_digest != _json_sha256(representative_value):
                raise VerificationError(f"{context} representative digest mismatch")
            if representative_digest in seen_representative_digests:
                raise VerificationError(f"duplicate representative digest at {context}")
            seen_representative_digests.add(representative_digest)

            outcome_counts[outcome] += 1
            if outcome == "UNSAT":
                proof_jobs.append(
                    _parse_proof_binding(
                        record["proof"],
                        bundle_root=bundle_root,
                        proof_root=proof_root,
                        seen_proof_ids=seen_proof_ids,
                        seen_proof_paths=seen_proof_paths,
                        seen_cnf_paths=seen_cnf_paths,
                    )
                )
        record_total += declared_count

    if record_total != aggregate_record_count:
        raise VerificationError("partition record counts do not match aggregate declaration")
    if aggregate_record_count != domain_size:
        raise VerificationError("aggregate record count does not match domain size")
    if outcome_counts != {"SAT": expected_sat, "UNSAT": expected_unsat}:
        raise VerificationError("record outcomes do not match aggregate declaration")
    if expected_sat + expected_unsat != aggregate_record_count:
        raise VerificationError("aggregate outcome counts do not sum to aggregate record count")
    if len(proof_jobs) != expected_unsat:
        raise VerificationError("not every UNSAT record has exactly one proof binding")

    inventory: set[Path] = set()
    for entry in proof_root.rglob("*"):
        if entry.is_symlink():
            raise VerificationError(f"proof inventory contains symlink: {entry}")
        if entry.is_file():
            inventory.add(entry.resolve())
    extra_proofs = inventory.difference(seen_proof_paths)
    if extra_proofs:
        relative = sorted(str(path.relative_to(bundle_root)) for path in extra_proofs)
        raise VerificationError(f"unlisted proof artifact(s): {relative}")
    missing_from_inventory = seen_proof_paths.difference(inventory)
    if missing_from_inventory:
        relative = sorted(str(path.relative_to(bundle_root)) for path in missing_from_inventory)
        raise VerificationError(f"missing proof artifact(s): {relative}")

    for cnf, proof in proof_jobs:
        _invoke_external_checker(
            checker,
            cnf,
            proof,
            bundle_root=bundle_root,
            timeout_seconds=checker_timeout_seconds,
        )

    return {
        "authority": AUTHORITY,
        "checker_sha256": checker_digest,
        "partitions_checked": len(partitions),
        "proofs_checked": len(proof_jobs),
        "records_checked": record_total,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="path to CR-B bundle manifest")
    parser.add_argument(
        "--checker",
        type=Path,
        required=True,
        help="pinned external DRAT/DRUP checker executable",
    )
    parser.add_argument(
        "--checker-sha256",
        required=True,
        help="independently trusted lowercase SHA-256 of the checker executable",
    )
    parser.add_argument(
        "--checker-timeout-seconds",
        type=float,
        default=300.0,
        help="per-proof checker timeout (default: 300)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        report = verify_bundle(
            args.manifest,
            args.checker,
            checker_sha256=args.checker_sha256,
            checker_timeout_seconds=args.checker_timeout_seconds,
        )
    except VerificationError as exc:
        print(f"CRB_INDEPENDENT_VERIFICATION_FAILED: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
