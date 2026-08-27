"""Declared full-census manifest, partitions, and materialization for Engine B.

This module freezes input identity only.  It derives the GL(3,5) matrix action
manifest, the preregistered ordinal partition plan for the two declared census
scopes, the strict outcome-free candidate record format, a fail-closed
materializer for the frozen shards, and the non-execution declaration receipt.
It never reads Engine-A generators, canonicalized candidates, forbidden sets,
orbit manifests, or aggregate results, and it never evaluates a predicate.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator, Mapping, Sequence

import engine_b as eb


class PartitionPlanMismatch(RuntimeError):
    """Raised when a declared partition plan is invalid or tampered."""


class CandidateStreamMismatch(RuntimeError):
    """Raised when a candidate stream violates its frozen record contract."""


class MatrixManifestMismatch(RuntimeError):
    """Raised when a GL(3,5) matrix action manifest is invalid or tampered."""


class DeclarationReceiptMismatch(RuntimeError):
    """Raised when a declaration receipt is invalid or overstates authority."""


SHA256 = re.compile(r"[0-9a-f]{64}")
GIT_COMMIT = re.compile(r"[0-9a-f]{40}")
PLAN_SCHEMA = "ORION.NQ.EngineB.FullCensusDeclaredPlan.v1"
MATRIX_SCHEMA = "ORION.NQ.EngineB.MatrixActionManifest.v1"
CANDIDATE_SCHEMA = "ORION.NQ.EngineB.CensusCandidate.v1"
MATERIALIZED_SCHEMA = "ORION.NQ.EngineB.MaterializedScope.v1"
RECEIPT_SCHEMA = "ORION.NQ.EngineB.FullCensusDeclarationReceipt.v1"
DECLARATION_TERMINAL = "NQ_CR_B_FULL_CENSUS_PARTITION_PLAN_FROZEN"
PARTITION_SIZE = 4_096

PLAN_AUTHORITY = {
    "aggregate_results_consumed": False,
    "blinded_independence": "NOT_CLAIMED",
    "d3_replay": "CANNOT_CHECK",
    "d4_c5_cubed": "OPEN",
    "engine_a_agreement": "NOT_CHECKED",
    "independent_replay_authority": "CANNOT_CHECK",
    "paper_authority_delta": "NONE",
    "scientific_authority_delta": "NONE",
}

SCOPE_AUTHORITY = {
    "engine_a_agreement": "NOT_CHECKED",
    "normalization_completeness": "CANNOT_CHECK",
    "orbit_completeness": "NOT_CLAIMED",
    "predicate_execution": "NOT_RUN",
    "scientific_authority_delta": "NONE",
}

RECEIPT_AUTHORITY = {
    "blinded_independence": "NOT_CLAIMED",
    "d4_c5_cubed": "OPEN",
    "engine_a_agreement": "NOT_CHECKED",
    "independent_replay_authority": "CANNOT_CHECK",
    "paper_authority_delta": "NONE",
}
RECEIPT_LABELS = {
    "aggregate_results_consumed": False,
    "materialized_candidate_records": 0,
    "lunarc_submission": "NOT_SUBMITTED",
    "d3_replay": "CANNOT_CHECK",
    "scientific_authority_delta": "NONE",
}


@dataclass(frozen=True)
class CensusSpec:
    """Frozen identity of one declared census scope."""

    scope: str
    kind: str
    expected_record_count: int
    sequence_length: int
    required_bins: int
    record_id_prefix: str

    def __post_init__(self) -> None:
        if not all(
            isinstance(getattr(self, field), str) and getattr(self, field)
            for field in ("scope", "kind", "record_id_prefix")
        ):
            raise ValueError("census scope identity fields must be nonempty strings")
        if type(self.expected_record_count) is not int or self.expected_record_count < 0:
            raise ValueError("expected_record_count must be a nonnegative integer")
        if type(self.sequence_length) is not int or not 1 <= self.sequence_length <= 31:
            raise ValueError("sequence_length must be an integer from one through thirty-one")
        if type(self.required_bins) is not int or not 1 <= self.required_bins <= 4:
            raise ValueError("required_bins must be an integer from one through four")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,32}", self.record_id_prefix):
            raise ValueError("record_id_prefix is not canonical")


D2_SPEC = CensusSpec(
    scope="NQ_D2_NORMALIZED_LENGTH_19",
    kind="d2_witness_census",
    expected_record_count=98_622,
    sequence_length=19,
    required_bins=2,
    record_id_prefix="nq-d2-",
)

D3_SPEC = CensusSpec(
    scope="NQ_D3_STRUCTURED_LENGTH_25",
    kind="d3_extension_census",
    expected_record_count=230_983,
    sequence_length=25,
    required_bins=3,
    record_id_prefix="nq-d3-",
)


def payload_sha256(value: Mapping[str, Any], *, digest_field: str) -> str:
    """Digest a mapping over its canonical JSON bytes minus the digest field."""

    if not isinstance(value, Mapping):
        raise TypeError("payload_sha256 requires a mapping")
    payload = {key: item for key, item in value.items() if key != digest_field}
    return hashlib.sha256(eb.canonical_json_bytes(payload)).hexdigest()


def record_identifier(spec: CensusSpec, ordinal: int) -> str:
    if type(ordinal) is not int or ordinal < 0:
        raise ValueError("ordinal must be a nonnegative integer")
    return f"{spec.record_id_prefix}{ordinal:08d}"


def build_partition_plan(
    *,
    specs: Sequence[CensusSpec] = (D2_SPEC, D3_SPEC),
    partition_size: int = PARTITION_SIZE,
) -> dict[str, Any]:
    """Freeze contiguous half-open ordinal partitions before any stream exists."""

    if type(partition_size) is not int or partition_size <= 0:
        raise ValueError("partition_size must be a positive integer")
    if not specs:
        raise ValueError("at least one census scope must be declared")
    scopes = []
    for spec in specs:
        if not isinstance(spec, CensusSpec):
            raise ValueError("declared scopes must be CensusSpec instances")
        partitions = []
        ordinal_start = 0
        index = 0
        while ordinal_start < spec.expected_record_count:
            ordinal_end = min(ordinal_start + partition_size, spec.expected_record_count)
            partitions.append(
                {
                    "partition_index": index,
                    "ordinal_start": ordinal_start,
                    "ordinal_end_exclusive": ordinal_end,
                    "record_count": ordinal_end - ordinal_start,
                }
            )
            ordinal_start = ordinal_end
            index += 1
        scopes.append(
            {
                "scope": spec.scope,
                "kind": spec.kind,
                "expected_record_count": spec.expected_record_count,
                "sequence_length": spec.sequence_length,
                "required_bins": spec.required_bins,
                "record_id_prefix": spec.record_id_prefix,
                "partition_size": partition_size,
                "partition_count": len(partitions),
                "partitions": partitions,
            }
        )
    if len({scope["scope"] for scope in scopes}) != len(scopes):
        raise ValueError("declared census scopes must be unique")
    plan: dict[str, Any] = {
        "schema": PLAN_SCHEMA,
        "subject_commit": eb.SUBJECT_COMMIT,
        "partition_size": partition_size,
        "authority": dict(PLAN_AUTHORITY),
        "scopes": scopes,
    }
    plan["plan_sha256"] = payload_sha256(plan, digest_field="plan_sha256")
    return plan


_SCOPE_FIELDS = {
    "scope",
    "kind",
    "expected_record_count",
    "sequence_length",
    "required_bins",
    "record_id_prefix",
    "partition_size",
    "partition_count",
    "partitions",
}
_PARTITION_FIELDS = {"partition_index", "ordinal_start", "ordinal_end_exclusive", "record_count"}


def verify_partition_plan(plan: Mapping[str, Any]) -> None:
    """Fail closed on any drift from the frozen contiguous partition contract."""

    if type(plan) is not dict or set(plan) != {
        "schema",
        "subject_commit",
        "partition_size",
        "authority",
        "scopes",
        "plan_sha256",
    }:
        raise PartitionPlanMismatch("partition plan fields are not exact")
    if plan["schema"] != PLAN_SCHEMA:
        raise PartitionPlanMismatch("partition plan schema mismatch")
    if plan["subject_commit"] != eb.SUBJECT_COMMIT:
        raise PartitionPlanMismatch("partition plan subject mismatch")
    if plan["plan_sha256"] != payload_sha256(plan, digest_field="plan_sha256"):
        raise PartitionPlanMismatch("partition plan content digest mismatch")
    if type(plan["partition_size"]) is not int or plan["partition_size"] <= 0:
        raise PartitionPlanMismatch("partition plan partition_size is invalid")
    if plan["authority"] != PLAN_AUTHORITY:
        raise PartitionPlanMismatch("partition plan authority labels are not the frozen set")
    if type(plan["scopes"]) is not list or not plan["scopes"]:
        raise PartitionPlanMismatch("partition plan declares no census scopes")
    for scope in plan["scopes"]:
        if type(scope) is not dict or set(scope) != _SCOPE_FIELDS:
            raise PartitionPlanMismatch("declared scope fields are not exact")
        if scope["partition_size"] != plan["partition_size"]:
            raise PartitionPlanMismatch("declared scope partition size differs from the plan")
        if type(scope["record_id_prefix"]) is not str or not re.fullmatch(
            r"[A-Za-z0-9][A-Za-z0-9_.-]{0,32}", scope["record_id_prefix"]
        ):
            raise PartitionPlanMismatch("declared scope record id prefix is not canonical")
        partitions = scope["partitions"]
        if type(partitions) is not list or not partitions:
            raise PartitionPlanMismatch("declared scope has no partitions")
        if scope["partition_count"] != len(partitions):
            raise PartitionPlanMismatch("declared scope partition count mismatch")
        expected_start = 0
        for index, partition in enumerate(partitions):
            if type(partition) is not dict or set(partition) != _PARTITION_FIELDS:
                raise PartitionPlanMismatch("declared partition fields are not exact")
            if partition["partition_index"] != index:
                raise PartitionPlanMismatch("declared partition index is not dense")
            if partition["ordinal_start"] != expected_start:
                raise PartitionPlanMismatch(
                    "declared ordinal partitions are not contiguous half-open ranges"
                )
            width = partition["ordinal_end_exclusive"] - partition["ordinal_start"]
            if (
                type(partition["ordinal_start"]) is not int
                or type(partition["ordinal_end_exclusive"]) is not int
                or partition["ordinal_start"] < 0
                or width <= 0
            ):
                raise PartitionPlanMismatch("declared partition ordinal range is invalid")
            if partition["record_count"] != width:
                raise PartitionPlanMismatch("declared partition record count mismatch")
            if index + 1 < len(partitions) and width != scope["partition_size"]:
                raise PartitionPlanMismatch("declared interior partition width is not frozen")
            expected_start = partition["ordinal_end_exclusive"]
        if expected_start != scope["expected_record_count"]:
            raise PartitionPlanMismatch("declared partitions do not cover the expected records")


def _row_digits(row: int) -> tuple[int, int, int]:
    return row // 25, (row // 5) % 5, row % 5


def iter_gl3_f5_matrix_bytes() -> Iterator[bytes]:
    """Yield every invertible 3x3 base-five matrix as 9 row-major bytes.

    Enumeration is lexicographic over the nine base-five digits; a matrix is
    emitted exactly when its rows are linearly independent over GF(5).
    """

    zero = (0, 0, 0)
    for first in range(125):
        row_one = _row_digits(first)
        if row_one == zero:
            continue
        span_one = {tuple((scalar * digit) % 5 for digit in row_one) for scalar in range(5)}
        for second in range(125):
            row_two = _row_digits(second)
            if row_two in span_one:
                continue
            span_two = {
                tuple((i * a + j * b) % 5 for a, b in zip(row_one, row_two))
                for i in range(5)
                for j in range(5)
            }
            for third in range(125):
                row_three = _row_digits(third)
                if row_three in span_two:
                    continue
                yield bytes((*row_one, *row_two, *row_three))


def build_matrix_action_manifest(dimension: int = 3) -> dict[str, Any]:
    """Digest-address every literal matrix of GL(3,5) in lexicographic order."""

    if dimension != 3:
        raise ValueError("the declared matrix action scope is GL(3,5) only")
    digest = hashlib.sha256()
    matrix_count = 0
    payload_bytes = 0
    batch: list[bytes] = []
    for matrix in iter_gl3_f5_matrix_bytes():
        batch.append(matrix)
        matrix_count += 1
        payload_bytes += len(matrix)
        if len(batch) >= 65_536:
            digest.update(b"".join(batch))
            batch.clear()
    digest.update(b"".join(batch))
    manifest: dict[str, Any] = {
        "schema": MATRIX_SCHEMA,
        "subject_commit": eb.SUBJECT_COMMIT,
        "group": "GL(3,5)",
        "dimension": 3,
        "modulus": 5,
        "encoding": "ROW_MAJOR_BASE_FIVE_BYTES_LEXICOGRAPHIC",
        "payload_action": "LEFT_MULTIPLICATION_ON_ELEMENT_COORDINATES",
        "matrix_count": matrix_count,
        "payload_bytes": payload_bytes,
        "matrix_sha256": digest.hexdigest(),
    }
    manifest["manifest_sha256"] = payload_sha256(manifest, digest_field="manifest_sha256")
    return manifest


def verify_matrix_action_manifest(manifest: Mapping[str, Any], *, regenerate: bool = False) -> None:
    if type(manifest) is not dict or set(manifest) != {
        "schema",
        "subject_commit",
        "group",
        "dimension",
        "modulus",
        "encoding",
        "payload_action",
        "matrix_count",
        "payload_bytes",
        "matrix_sha256",
        "manifest_sha256",
    }:
        raise MatrixManifestMismatch("matrix action manifest fields are not exact")
    if manifest["schema"] != MATRIX_SCHEMA:
        raise MatrixManifestMismatch("matrix action manifest schema mismatch")
    if manifest["subject_commit"] != eb.SUBJECT_COMMIT:
        raise MatrixManifestMismatch("matrix action manifest subject mismatch")
    if manifest["manifest_sha256"] != payload_sha256(manifest, digest_field="manifest_sha256"):
        raise MatrixManifestMismatch("matrix action manifest content digest mismatch")
    if (
        manifest["group"] != "GL(3,5)"
        or manifest["dimension"] != 3
        or manifest["modulus"] != 5
        or manifest["encoding"] != "ROW_MAJOR_BASE_FIVE_BYTES_LEXICOGRAPHIC"
        or manifest["payload_action"] != "LEFT_MULTIPLICATION_ON_ELEMENT_COORDINATES"
    ):
        raise MatrixManifestMismatch("matrix action manifest identity contract mismatch")
    if type(manifest["matrix_count"]) is not int or manifest["matrix_count"] != 1_488_000:
        raise MatrixManifestMismatch("matrix action manifest count is not the GL(3,5) order")
    if type(manifest["payload_bytes"]) is not int or manifest["payload_bytes"] != 9 * 1_488_000:
        raise MatrixManifestMismatch("matrix action manifest payload width mismatch")
    if not SHA256.fullmatch(str(manifest["matrix_sha256"])):
        raise MatrixManifestMismatch("matrix action payload digest is malformed")
    if not regenerate:
        return
    digest = hashlib.sha256()
    observed = 0
    batch: list[bytes] = []
    for matrix in iter_gl3_f5_matrix_bytes():
        batch.append(matrix)
        observed += 1
        if len(batch) >= 65_536:
            digest.update(b"".join(batch))
            batch.clear()
    digest.update(b"".join(batch))
    if observed != manifest["matrix_count"] or digest.hexdigest() != manifest["matrix_sha256"]:
        raise MatrixManifestMismatch("regenerated matrix payload disagrees with the manifest")


CANDIDATE_FIELDS = {
    "schema",
    "scope",
    "record_id",
    "ordinal",
    "sequence",
    "sequence_length",
    "required_bins",
    "sequence_sha256",
    "matrix_witness_sha256",
    "orbit_key_sha256",
    "derivation_sha256",
    "candidate_sha256",
}


def _sequence_digest(sequence: Sequence[int]) -> str:
    return hashlib.sha256(eb.canonical_json_bytes(list(sequence))).hexdigest()


def _require_digest(value: Any, label: str) -> str:
    if type(value) is not str or not SHA256.fullmatch(value):
        raise ValueError(f"{label} must be a lowercase sixty-four character hex digest")
    return value


def build_candidate_record(
    spec: CensusSpec,
    *,
    ordinal: int,
    sequence: Sequence[int],
    matrix_witness_sha256: str,
    orbit_key_sha256: str,
    derivation_sha256: str,
) -> dict[str, Any]:
    """Build one outcome-free candidate record bound to the frozen identity."""

    if type(ordinal) is not int or ordinal < 0:
        raise ValueError("ordinal must be a nonnegative integer")
    value = tuple(sequence)
    if len(value) != spec.sequence_length or any(
        type(element) is not int or not 0 <= element < 125 for element in value
    ):
        raise ValueError("candidate sequence is outside the declared census scope")
    record: dict[str, Any] = {
        "schema": CANDIDATE_SCHEMA,
        "scope": spec.scope,
        "record_id": record_identifier(spec, ordinal),
        "ordinal": ordinal,
        "sequence": list(value),
        "sequence_length": spec.sequence_length,
        "required_bins": spec.required_bins,
        "sequence_sha256": _sequence_digest(value),
        "matrix_witness_sha256": _require_digest(matrix_witness_sha256, "matrix witness digest"),
        "orbit_key_sha256": _require_digest(orbit_key_sha256, "orbit key digest"),
        "derivation_sha256": _require_digest(derivation_sha256, "derivation digest"),
    }
    record["candidate_sha256"] = payload_sha256(record, digest_field="candidate_sha256")
    return record


def parse_candidate_line(line: bytes, spec: CensusSpec, *, expected_ordinal: int) -> dict[str, Any]:
    """Parse one canonical candidate line exactly, failing closed on drift."""

    if type(line) is not bytes or not line.endswith(b"\n") or line == b"\n":
        raise CandidateStreamMismatch("candidate record line is empty or lacks its newline")
    payload = line[:-1]
    try:
        value = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise CandidateStreamMismatch("candidate record line is not canonical JSON") from error
    if eb.canonical_json_bytes(value) != payload:
        raise CandidateStreamMismatch("candidate record line is not byte-canonical")
    if type(value) is not dict or set(value) != CANDIDATE_FIELDS:
        raise CandidateStreamMismatch("candidate record fields are not exact")
    if value["schema"] != CANDIDATE_SCHEMA:
        raise CandidateStreamMismatch("candidate record schema mismatch")
    if value["scope"] != spec.scope:
        raise CandidateStreamMismatch("candidate record scope mismatch")
    if type(value["ordinal"]) is not int or value["ordinal"] != expected_ordinal:
        raise CandidateStreamMismatch("candidate record ordinal binding mismatch")
    if value["record_id"] != record_identifier(spec, expected_ordinal):
        raise CandidateStreamMismatch("candidate record id is not the frozen derivation")
    sequence = value["sequence"]
    if (
        type(sequence) is not list
        or len(sequence) != spec.sequence_length
        or any(type(element) is not int or not 0 <= element < 125 for element in sequence)
    ):
        raise CandidateStreamMismatch("candidate record sequence is outside the census scope")
    if value["sequence_length"] != spec.sequence_length:
        raise CandidateStreamMismatch("candidate record sequence length mismatch")
    if value["required_bins"] != spec.required_bins:
        raise CandidateStreamMismatch("candidate record bin count mismatch")
    if value["sequence_sha256"] != _sequence_digest(sequence):
        raise CandidateStreamMismatch("candidate record sequence digest mismatch")
    for label in ("matrix_witness_sha256", "orbit_key_sha256", "derivation_sha256"):
        if type(value[label]) is not str or not SHA256.fullmatch(value[label]):
            raise CandidateStreamMismatch(f"candidate record {label} is malformed")
    if value["candidate_sha256"] != payload_sha256(value, digest_field="candidate_sha256"):
        raise CandidateStreamMismatch("candidate record content digest mismatch")
    return value


def _spec_from_scope(scope: Mapping[str, Any]) -> CensusSpec:
    return CensusSpec(
        scope=scope["scope"],
        kind=scope["kind"],
        expected_record_count=scope["expected_record_count"],
        sequence_length=scope["sequence_length"],
        required_bins=scope["required_bins"],
        record_id_prefix=scope["record_id_prefix"],
    )


def _shard_relative_path(scope: str, partition_index: int) -> str:
    return f"{scope}/part-{partition_index:05d}.jsonl"


def _write_atomic(destination: Path, data: bytes) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(f".{destination.name}.{os.getpid()}.tmp")
    temporary.write_bytes(data)
    os.replace(temporary, destination)


def materialize_scope(
    stream_path: Path, scope: Mapping[str, Any], output_root: Path
) -> dict[str, Any]:
    """Materialize a complete candidate stream into its frozen shard layout."""

    spec = _spec_from_scope(scope)
    partitions = scope["partitions"]
    stream = Path(stream_path).read_bytes()
    lines = stream.splitlines(keepends=True)
    expected = scope["expected_record_count"]
    if len(lines) != expected:
        raise CandidateStreamMismatch(
            f"candidate stream is not declared complete: expected {expected} "
            f"records, observed {len(lines)}"
        )
    records = [
        parse_candidate_line(line, spec, expected_ordinal=ordinal)
        for ordinal, line in enumerate(lines)
    ]
    output_root = Path(output_root)
    materialized = []
    for partition in partitions:
        start = partition["ordinal_start"]
        end = partition["ordinal_end_exclusive"]
        shard = b"".join(eb.canonical_json_bytes(record) + b"\n" for record in records[start:end])
        relative = _shard_relative_path(spec.scope, partition["partition_index"])
        _write_atomic(output_root / relative, shard)
        materialized.append(
            {
                "partition_index": partition["partition_index"],
                "ordinal_start": start,
                "ordinal_end_exclusive": end,
                "record_count": end - start,
                "path": relative,
                "bytes": len(shard),
                "payload_sha256": hashlib.sha256(shard).hexdigest(),
                "first_record_id": records[start]["record_id"],
                "last_record_id": records[end - 1]["record_id"],
            }
        )
    manifest: dict[str, Any] = {
        "schema": MATERIALIZED_SCHEMA,
        "subject_commit": eb.SUBJECT_COMMIT,
        "scope": spec.scope,
        "expected_record_count": expected,
        "total_records": len(records),
        "stream_bytes": len(stream),
        "stream_sha256": hashlib.sha256(stream).hexdigest(),
        "partitions": materialized,
        "authority": dict(SCOPE_AUTHORITY),
    }
    manifest["manifest_sha256"] = payload_sha256(manifest, digest_field="manifest_sha256")
    _write_atomic(
        output_root / f"{spec.scope}/SCOPE_MANIFEST.json",
        json.dumps(manifest, indent=2, sort_keys=True).encode("ascii") + b"\n",
    )
    return manifest


def verify_materialized_scope(
    output_root: Path, scope: Mapping[str, Any], manifest: Mapping[str, Any]
) -> None:
    """Re-derive every shard byte from the stream contract and compare."""

    root = Path(output_root)
    spec = _spec_from_scope(scope)
    if type(manifest) is not dict or set(manifest) != {
        "schema",
        "subject_commit",
        "scope",
        "expected_record_count",
        "total_records",
        "stream_bytes",
        "stream_sha256",
        "partitions",
        "authority",
        "manifest_sha256",
    }:
        raise CandidateStreamMismatch("materialized scope manifest fields are not exact")
    if manifest["schema"] != MATERIALIZED_SCHEMA:
        raise CandidateStreamMismatch("materialized scope manifest schema mismatch")
    if manifest["subject_commit"] != eb.SUBJECT_COMMIT:
        raise CandidateStreamMismatch("materialized scope manifest subject mismatch")
    if manifest["scope"] != spec.scope:
        raise CandidateStreamMismatch("materialized scope manifest scope mismatch")
    if manifest["manifest_sha256"] != payload_sha256(manifest, digest_field="manifest_sha256"):
        raise CandidateStreamMismatch("materialized scope manifest content digest mismatch")
    if manifest["authority"] != SCOPE_AUTHORITY:
        raise CandidateStreamMismatch("materialized scope authority labels are not frozen")
    if manifest["total_records"] != scope["expected_record_count"]:
        raise CandidateStreamMismatch("materialized scope record count is not declared complete")
    expected_start = 0
    for index, shard in enumerate(manifest["partitions"]):
        if type(shard) is not dict or set(shard) != {
            "partition_index",
            "ordinal_start",
            "ordinal_end_exclusive",
            "record_count",
            "path",
            "bytes",
            "payload_sha256",
            "first_record_id",
            "last_record_id",
        }:
            raise CandidateStreamMismatch("materialized shard fields are not exact")
        partition = scope["partitions"][index]
        for field in ("partition_index", "ordinal_start", "ordinal_end_exclusive", "record_count"):
            if shard[field] != partition[field]:
                raise CandidateStreamMismatch(
                    f"materialized shard {field} drifts from the frozen plan"
                )
        if shard["ordinal_start"] != expected_start:
            raise CandidateStreamMismatch("materialized shards are not contiguous")
        expected_start = shard["ordinal_end_exclusive"]
        relative = _shard_relative_path(spec.scope, partition["partition_index"])
        if shard["path"] != relative:
            raise CandidateStreamMismatch("materialized shard path is not the frozen layout")
        source = root / relative
        if source.is_symlink():
            raise CandidateStreamMismatch("materialized shard must not be a symlink")
        data = source.read_bytes()
        if (
            len(data) != shard["bytes"]
            or hashlib.sha256(data).hexdigest() != shard["payload_sha256"]
        ):
            raise CandidateStreamMismatch("materialized shard bytes disagree with the digest")
        for ordinal, line in enumerate(
            data.splitlines(keepends=True), start=shard["ordinal_start"]
        ):
            record = parse_candidate_line(line, spec, expected_ordinal=ordinal)
            if (
                ordinal == shard["ordinal_start"]
                and record["record_id"] != shard["first_record_id"]
            ):
                raise CandidateStreamMismatch("materialized shard first record id mismatch")
            if (
                ordinal == shard["ordinal_end_exclusive"] - 1
                and record["record_id"] != shard["last_record_id"]
            ):
                raise CandidateStreamMismatch("materialized shard last record id mismatch")
    if expected_start != scope["expected_record_count"]:
        raise CandidateStreamMismatch("materialized shards do not cover the declared scope")
    declared = json.loads((root / f"{spec.scope}/SCOPE_MANIFEST.json").read_text())
    if declared != dict(manifest):
        raise CandidateStreamMismatch("declared scope manifest disagrees with the materialization")


def build_declaration_receipt(
    plan: Mapping[str, Any],
    *,
    origin_main_commit: str,
    stack_parent_commit: str,
    source_sha256: str,
) -> dict[str, Any]:
    """Seal the input-identity declaration with zero execution authority."""

    verify_partition_plan(plan)
    for label, value in (
        ("origin_main_commit", origin_main_commit),
        ("stack_parent_commit", stack_parent_commit),
    ):
        if type(value) is not str or not GIT_COMMIT.fullmatch(value):
            raise ValueError(f"{label} must be a forty character hex commit")
    if type(source_sha256) is not str or not SHA256.fullmatch(source_sha256):
        raise ValueError("source_sha256 must be a lowercase sixty-four character hex digest")
    receipt: dict[str, Any] = {
        "schema": RECEIPT_SCHEMA,
        "subject_commit": eb.SUBJECT_COMMIT,
        "terminal": DECLARATION_TERMINAL,
        "origin_main_commit": origin_main_commit,
        "stack_parent_commit": stack_parent_commit,
        "source_manifest_sha256": source_sha256,
        "plan_sha256": plan["plan_sha256"],
        "declared_scopes": [
            {"scope": scope["scope"], "expected_record_count": scope["expected_record_count"]}
            for scope in plan["scopes"]
        ],
        **dict(RECEIPT_LABELS),
        "authority": dict(RECEIPT_AUTHORITY),
    }
    receipt["receipt_sha256"] = payload_sha256(receipt, digest_field="receipt_sha256")
    return receipt


def verify_declaration_receipt(receipt: Mapping[str, Any], plan: Mapping[str, Any]) -> None:
    if type(receipt) is not dict or set(receipt) != {
        "schema",
        "subject_commit",
        "terminal",
        "origin_main_commit",
        "stack_parent_commit",
        "source_manifest_sha256",
        "plan_sha256",
        "declared_scopes",
        "aggregate_results_consumed",
        "materialized_candidate_records",
        "lunarc_submission",
        "d3_replay",
        "scientific_authority_delta",
        "authority",
        "receipt_sha256",
    }:
        raise DeclarationReceiptMismatch("declaration receipt fields are not exact")
    if receipt["schema"] != RECEIPT_SCHEMA:
        raise DeclarationReceiptMismatch("declaration receipt schema mismatch")
    if receipt["subject_commit"] != eb.SUBJECT_COMMIT:
        raise DeclarationReceiptMismatch("declaration receipt subject mismatch")
    if receipt["receipt_sha256"] != payload_sha256(receipt, digest_field="receipt_sha256"):
        raise DeclarationReceiptMismatch("declaration receipt content digest mismatch")
    if receipt["terminal"] != DECLARATION_TERMINAL:
        raise DeclarationReceiptMismatch("declaration receipt terminal is not the frozen plan")
    for label in ("origin_main_commit", "stack_parent_commit"):
        if type(receipt[label]) is not str or not GIT_COMMIT.fullmatch(receipt[label]):
            raise DeclarationReceiptMismatch(f"declaration receipt {label} is malformed")
    if type(receipt["source_manifest_sha256"]) is not str or not SHA256.fullmatch(
        receipt["source_manifest_sha256"]
    ):
        raise DeclarationReceiptMismatch("declaration receipt source digest is malformed")
    if receipt["plan_sha256"] != plan["plan_sha256"]:
        raise DeclarationReceiptMismatch("declaration receipt is not bound to this plan")
    for label, value in RECEIPT_LABELS.items():
        if receipt[label] != value:
            raise DeclarationReceiptMismatch(f"declaration receipt label {label} is not frozen")
    if receipt["authority"] != RECEIPT_AUTHORITY:
        raise DeclarationReceiptMismatch("declaration receipt authority labels are not frozen")
    expected_scopes = [
        {"scope": scope["scope"], "expected_record_count": scope["expected_record_count"]}
        for scope in plan["scopes"]
    ]
    if receipt["declared_scopes"] != expected_scopes:
        raise DeclarationReceiptMismatch("declaration receipt declared scopes drift from the plan")
