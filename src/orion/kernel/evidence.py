from __future__ import annotations

import errno
import functools
import hashlib
import os
import selectors
import shutil
import signal
import stat
import subprocess
import sys
import time
from functools import lru_cache
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from orion.core.evidence import EvidenceRecord, evidence_record_fingerprint

from .transition import canonical_digest

_REF_SEPARATOR = ":"
_HASH_SEPARATOR = "@"
_MIN_DIGEST_PREFIX = 8
_COMMIT_ANCHOR_PREFIX = "git:"
EVIDENCE_MANIFEST_SCHEMA_VERSION = "orion.host-evidence-manifest.v1"
EVIDENCE_SOURCE_SCHEMA_VERSION = "orion.host-evidence-source.v1"
EVIDENCE_SNAPSHOT_SCHEMA_VERSION = "orion.host-evidence-snapshot.v1"
EVIDENCE_RECORD_SCHEMA_VERSION = "orion.host-evidence-record.v1"
MAX_EVIDENCE_RECORD_BYTES = 8_388_608
MAX_EVIDENCE_SNAPSHOT_BYTES = 33_554_432
MAX_EVIDENCE_CAPTURE_LOCAL_BYTES = 33_554_432
MAX_EVIDENCE_CAPTURE_GIT_COMMANDS = 16_384
MAX_EVIDENCE_CAPTURE_GIT_STDOUT_BYTES = 67_108_864
MAX_EVIDENCE_CAPTURE_GIT_STDERR_BYTES = 16_777_216
MAX_EVIDENCE_CAPTURE_ELAPSED_NS = 60_000_000_000
MAX_EVIDENCE_CAPTURE_PATH_COMPONENTS = 65_536
MAX_EVIDENCE_CAPTURE_TREE_ENTRIES = 100_000
MAX_EVIDENCE_CAPTURE_GIT_OBJECT_BYTES = 67_108_864
MAX_EVIDENCE_CAPTURE_GIT_OBJECTS = 16_384
MAX_EVIDENCE_SOURCE_COUNT = 4_096
MAX_EVIDENCE_BINDING_COUNT = 8_192
MAX_EVIDENCE_OBLIGATION_COUNT = 4_096
MAX_EVIDENCE_SNAPSHOT_RECORDS = 4_096
MAX_EVIDENCE_ROOT_COUNT = 256
MAX_EVIDENCE_ROOT_PATH_BYTES = 4_096
MAX_EVIDENCE_ROOT_PATH_COMPONENTS = 4_096
MAX_EVIDENCE_TEXT_BYTES = 4_096
MAX_EVIDENCE_GIT_CONTROL_BYTES = 1_048_576
MAX_EVIDENCE_EXECUTABLE_BYTES = 134_217_728
MAX_EVIDENCE_GIT_TREE_ENTRIES = 100_000
_OS_OPEN_SUPPORTS_DIR_FD = os.open in os.supports_dir_fd
_OS_STAT_SUPPORTS_DIR_FD = os.stat in os.supports_dir_fd
_OS_STAT_SUPPORTS_NOFOLLOW = os.stat in os.supports_follow_symlinks
_CAPTURE_WORK_USAGE_COORDINATES = frozenset(
    {
        "distinct_git_objects",
        "git_commands",
        "git_object_bytes",
        "git_stderr_bytes",
        "git_stdout_bytes",
        "local_bytes_read",
        "path_components",
        "tree_entries",
    }
)
_CAPTURE_WORK_EXHAUSTED_COORDINATES = frozenset(
    {
        "elapsed_ns",
        "git_commands",
        "git_object_bytes",
        "git_objects",
        "git_stderr_bytes",
        "git_stdout_bytes",
        "local_bytes",
        "path_components",
        "tree_entries",
    }
)


def _require_exact_text(value: object, field_name: str) -> None:
    if type(value) is not str or not value or value != value.strip():
        raise ValueError(f"{field_name} must be nonblank exact text")


def _require_exact_tuple(value: object, field_name: str) -> None:
    if type(value) is not tuple:
        raise ValueError(f"{field_name} must be an exact immutable tuple")


def _require_relative_path_text(value: object, field_name: str) -> None:
    if type(value) is not str or not value or "\x00" in value:
        raise ValueError(f"{field_name} must be nonempty exact path text")


def _require_text_byte_cap(value: str, field_name: str) -> None:
    if len(value.encode("utf-8")) > MAX_EVIDENCE_TEXT_BYTES:
        raise ValueError(f"{field_name} exceeds the evidence text byte cap")


def _bounded_diagnostic_text(value: str) -> str:
    """Retain a stable bounded diagnostic prefix; diagnostics grant no authority."""

    encoded = value.encode("utf-8", errors="replace")
    if len(encoded) <= MAX_EVIDENCE_TEXT_BYTES:
        return encoded.decode("utf-8", errors="strict")
    suffix = (
        "...[truncated-sha256:"
        + hashlib.sha256(encoded).hexdigest()[:16]
        + "]"
    ).encode("ascii")
    if len(suffix) >= MAX_EVIDENCE_TEXT_BYTES:
        return suffix[:MAX_EVIDENCE_TEXT_BYTES].decode("ascii")
    prefix = encoded[: MAX_EVIDENCE_TEXT_BYTES - len(suffix)]
    while prefix:
        try:
            decoded_prefix = prefix.decode("utf-8", errors="strict")
            break
        except UnicodeDecodeError:
            prefix = prefix[:-1]
    else:
        decoded_prefix = ""
    return decoded_prefix + suffix.decode("ascii")


@dataclass(frozen=True)
class EvidenceRoleBinding:
    """One host-owned evidence-role-to-obligation registration."""

    binding_id: str
    evidence_ref: str
    role_id: str
    obligation_id: str

    def __post_init__(self) -> None:
        for field_name in (
            "binding_id",
            "evidence_ref",
            "role_id",
            "obligation_id",
        ):
            _require_exact_text(getattr(self, field_name), field_name)
            _require_text_byte_cap(getattr(self, field_name), field_name)


@dataclass(frozen=True)
class HostEvidenceSource:
    """Host-owned typed source coordinate; candidate refs remain opaque IDs."""

    source_id: str
    backend_type: str
    root_scheme: str
    relative_path: str
    expected_content_sha256: str = ""
    git_revision: str = ""
    media_type: str = "application/octet-stream"
    schema_version: str = EVIDENCE_SOURCE_SCHEMA_VERSION
    source_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for field_name in (
            "source_id",
            "backend_type",
            "root_scheme",
            "media_type",
            "schema_version",
        ):
            _require_exact_text(getattr(self, field_name), field_name)
            _require_text_byte_cap(getattr(self, field_name), field_name)
        _require_relative_path_text(self.relative_path, "relative_path")
        _require_text_byte_cap(self.relative_path, "relative_path")
        if self.schema_version != EVIDENCE_SOURCE_SCHEMA_VERSION:
            raise ValueError(f"unsupported evidence source schema: {self.schema_version!r}")
        if self.backend_type not in {"file", "git"}:
            raise ValueError("backend_type must be 'file' or 'git'")
        if type(self.expected_content_sha256) is not str:
            raise ValueError("expected_content_sha256 must be an exact string")
        if type(self.git_revision) is not str:
            raise ValueError("git_revision must be an exact string")
        _require_text_byte_cap(
            self.expected_content_sha256, "expected_content_sha256"
        )
        _require_text_byte_cap(self.git_revision, "git_revision")
        if self.backend_type == "file":
            _require_sha256(
                self.expected_content_sha256, "expected_content_sha256"
            )
            if self.git_revision:
                raise ValueError("file source cannot carry a Git revision")
        else:
            _require_exact_text(self.git_revision, "git_revision")
            if self.expected_content_sha256:
                raise ValueError("Git source content digest is derived at capture")
        object.__setattr__(
            self,
            "source_hash",
            canonical_digest(
                {
                    "schema_version": self.schema_version,
                    "source_id": self.source_id,
                    "backend_type": self.backend_type,
                    "root_scheme": self.root_scheme,
                    "relative_path": self.relative_path,
                    "expected_content_sha256": self.expected_content_sha256,
                    "git_revision": self.git_revision,
                    "media_type": self.media_type,
                },
                domain="orion.host-evidence-source.v1",
            ),
        )


@dataclass(frozen=True)
class HostEvidenceManifest:
    """Inert host policy data; registration does not authorize a transition."""

    manifest_id: str
    required_obligation_ids: tuple[str, ...]
    sources: tuple[HostEvidenceSource, ...]
    bindings: tuple[EvidenceRoleBinding, ...]
    schema_version: str = EVIDENCE_MANIFEST_SCHEMA_VERSION
    manifest_hash: str = field(init=False)

    def __post_init__(self) -> None:
        _require_exact_text(self.manifest_id, "manifest_id")
        _require_exact_text(self.schema_version, "schema_version")
        _require_text_byte_cap(self.manifest_id, "manifest_id")
        _require_text_byte_cap(self.schema_version, "schema_version")
        if self.schema_version != EVIDENCE_MANIFEST_SCHEMA_VERSION:
            raise ValueError(f"unsupported evidence manifest schema: {self.schema_version!r}")
        _require_exact_tuple(
            self.required_obligation_ids, "required_obligation_ids"
        )
        _require_exact_tuple(self.sources, "sources")
        _require_exact_tuple(self.bindings, "bindings")
        if len(self.sources) > MAX_EVIDENCE_SOURCE_COUNT:
            raise ValueError("manifest exceeds the evidence source count cap")
        if len(self.bindings) > MAX_EVIDENCE_BINDING_COUNT:
            raise ValueError("manifest exceeds the evidence binding count cap")
        if len(self.required_obligation_ids) > MAX_EVIDENCE_OBLIGATION_COUNT:
            raise ValueError("manifest exceeds the evidence obligation count cap")
        if any(type(source) is not HostEvidenceSource for source in self.sources):
            raise ValueError("sources must contain exact HostEvidenceSource values")
        if any(type(binding) is not EvidenceRoleBinding for binding in self.bindings):
            raise ValueError("bindings must contain exact EvidenceRoleBinding values")
        object.__setattr__(
            self,
            "required_obligation_ids",
            tuple(sorted(self.required_obligation_ids)),
        )
        object.__setattr__(
            self,
            "sources",
            tuple(sorted(self.sources, key=lambda item: item.source_id)),
        )
        object.__setattr__(
            self,
            "bindings",
            tuple(sorted(self.bindings, key=lambda item: item.binding_id)),
        )
        for obligation_id in self.required_obligation_ids:
            _require_exact_text(obligation_id, "required obligation id")
            _require_text_byte_cap(obligation_id, "required obligation id")
        if len(set(self.required_obligation_ids)) != len(
            self.required_obligation_ids
        ):
            raise ValueError("required obligation ids must be unique")

        binding_ids: set[str] = set()
        source_ids = [source.source_id for source in self.sources]
        if len(set(source_ids)) != len(source_ids):
            raise ValueError("duplicate evidence source id")
        registered_sources = set(source_ids)
        semantic_bindings: set[tuple[str, str, str]] = set()
        roles_by_ref_obligation: dict[tuple[str, str], str] = {}
        required = set(self.required_obligation_ids)
        for binding in self.bindings:
            if binding.obligation_id not in required:
                raise ValueError(
                    f"binding targets unknown obligation: {binding.obligation_id}"
                )
            if binding.evidence_ref not in registered_sources:
                raise ValueError(
                    f"binding targets unknown evidence source: {binding.evidence_ref}"
                )
            if binding.binding_id in binding_ids:
                raise ValueError("duplicate evidence binding id")
            binding_ids.add(binding.binding_id)
            semantic = (
                binding.evidence_ref,
                binding.role_id,
                binding.obligation_id,
            )
            if semantic in semantic_bindings:
                raise ValueError("duplicate evidence role binding")
            semantic_bindings.add(semantic)
            coordinate = (binding.evidence_ref, binding.obligation_id)
            previous_role = roles_by_ref_obligation.setdefault(
                coordinate, binding.role_id
            )
            if previous_role != binding.role_id:
                raise ValueError("conflicting evidence roles for one obligation")

        payload = {
            "schema_version": self.schema_version,
            "manifest_id": self.manifest_id,
            "required_obligation_ids": sorted(self.required_obligation_ids),
            "sources": [
                [source.source_id, source.source_hash]
                for source in self.sources
            ],
            "bindings": [
                {
                    "binding_id": item.binding_id,
                    "evidence_ref": item.evidence_ref,
                    "role_id": item.role_id,
                    "obligation_id": item.obligation_id,
                }
                for item in sorted(self.bindings, key=lambda item: item.binding_id)
            ],
        }
        object.__setattr__(
            self,
            "manifest_hash",
            canonical_digest(payload, domain="orion.host-evidence-manifest.v1"),
        )


@dataclass(frozen=True)
class HostEvidenceRecord:
    """One exact host capture result; it is evidence data, never authority."""

    capture_ordinal: int
    ref: str
    status: EvidenceStatus
    backend_type: str
    scheme: str
    relative_path: str
    declared_digest: str
    resolved_source_revision: str
    source_object_format: str
    source_reference_oid: str
    source_blob_oid: str
    source_tree_entry_mode: str
    root_configuration_hash: str
    role_bindings: tuple[EvidenceRoleBinding, ...]
    content_bytes: bytes
    content_available: bool
    source_device: int | None = None
    source_inode: int | None = None
    source_size: int | None = None
    source_mtime_ns: int | None = None
    source_ctime_ns: int | None = None
    note: str = ""
    schema_version: str = EVIDENCE_RECORD_SCHEMA_VERSION
    content_hash: str = field(init=False)
    byte_length: int = field(init=False)
    record_hash: str = field(init=False)

    def __post_init__(self) -> None:
        if type(self.capture_ordinal) is not int or self.capture_ordinal < 0:
            raise ValueError("capture_ordinal must be a nonnegative exact integer")
        for field_name in (
            "ref",
            "backend_type",
            "scheme",
            "schema_version",
        ):
            _require_exact_text(getattr(self, field_name), field_name)
            _require_text_byte_cap(getattr(self, field_name), field_name)
        _require_relative_path_text(self.relative_path, "relative_path")
        _require_text_byte_cap(self.relative_path, "relative_path")
        _require_sha256(self.root_configuration_hash, "root_configuration_hash")
        if self.schema_version != EVIDENCE_RECORD_SCHEMA_VERSION:
            raise ValueError(f"unsupported evidence record schema: {self.schema_version!r}")
        if type(self.status) is not EvidenceStatus:
            raise ValueError("status must be an exact EvidenceStatus")
        for field_name in (
            "declared_digest",
            "resolved_source_revision",
            "source_object_format",
            "source_reference_oid",
            "source_blob_oid",
            "source_tree_entry_mode",
            "note",
        ):
            if type(getattr(self, field_name)) is not str:
                raise ValueError(f"{field_name} must be an exact string")
            _require_text_byte_cap(getattr(self, field_name), field_name)
        _require_exact_tuple(self.role_bindings, "role_bindings")
        if len(self.role_bindings) > MAX_EVIDENCE_BINDING_COUNT:
            raise ValueError("record exceeds the evidence binding count cap")
        if any(
            type(binding) is not EvidenceRoleBinding
            for binding in self.role_bindings
        ):
            raise ValueError("record role bindings must be exact bindings")
        object.__setattr__(
            self,
            "role_bindings",
            tuple(sorted(self.role_bindings, key=lambda item: item.binding_id)),
        )
        binding_ids: set[str] = set()
        for binding in self.role_bindings:
            if binding.evidence_ref != self.ref:
                raise ValueError("record role bindings must exactly target the record ref")
            if binding.binding_id in binding_ids:
                raise ValueError("record role binding ids must be unique")
            binding_ids.add(binding.binding_id)
        if type(self.content_bytes) is not bytes:
            raise ValueError("content_bytes must be exact immutable bytes")
        if len(self.content_bytes) > MAX_EVIDENCE_RECORD_BYTES:
            raise ValueError("content exceeds the evidence record byte cap")
        if type(self.content_available) is not bool:
            raise ValueError("content_available must be an exact bool")
        if not self.content_available and self.content_bytes:
            raise ValueError("unavailable content cannot carry payload bytes")
        metadata = (
            self.source_device,
            self.source_inode,
            self.source_size,
            self.source_mtime_ns,
            self.source_ctime_ns,
        )
        if any(value is not None and type(value) is not int for value in metadata):
            raise ValueError("source metadata must contain exact integers or None")
        if self.backend_type not in {"file", "git", "unmapped"}:
            raise ValueError("evidence requires a supported backend")
        git_fields = (
            self.resolved_source_revision,
            self.source_object_format,
            self.source_reference_oid,
            self.source_blob_oid,
            self.source_tree_entry_mode,
        )
        if self.backend_type == "file" and any(git_fields):
            raise ValueError("file evidence cannot carry Git-only fields")
        if self.backend_type == "git" and any(value is not None for value in metadata):
            raise ValueError("Git evidence cannot carry filesystem-only metadata")
        if self.backend_type == "unmapped" and (
            self.status is not EvidenceStatus.ROLE_UNMAPPED
            or any(git_fields)
            or any(value is not None for value in metadata)
            or self.content_available
        ):
            raise ValueError("unmapped evidence must be an inert role-unmapped record")

        content_hash = (
            hashlib.sha256(self.content_bytes).hexdigest()
            if self.content_available
            else ""
        )
        if self.status is EvidenceStatus.RESOLVED:
            if not self.role_bindings:
                raise ValueError("resolved evidence requires a host role binding")
            if not self.content_available:
                raise ValueError("resolved evidence requires available content")
            if self.backend_type == "file" and self.declared_digest != content_hash:
                raise ValueError(
                    "resolved file digest must match captured content"
                )
            if self.backend_type == "git":
                if self.source_object_format not in {"sha1", "sha256"}:
                    raise ValueError("resolved Git evidence requires an object format")
                oid_length = 40 if self.source_object_format == "sha1" else 64
                for field_name in (
                    "source_reference_oid",
                    "resolved_source_revision",
                    "source_blob_oid",
                ):
                    value = getattr(self, field_name)
                    if (
                        len(value) != oid_length
                        or any(character not in "0123456789abcdef" for character in value)
                    ):
                        raise ValueError(
                            f"resolved Git {field_name} must be one full storage OID"
                        )
                if self.source_tree_entry_mode not in {"100644", "100755"}:
                    raise ValueError("resolved Git evidence requires a regular-file mode")
                if (
                    _git_object_oid(
                        self.source_object_format, "blob", self.content_bytes
                    )
                    != self.source_blob_oid
                ):
                    raise ValueError(
                        "resolved Git payload must match its storage OID"
                    )
        byte_length = len(self.content_bytes) if self.content_available else 0
        object.__setattr__(self, "content_hash", content_hash)
        object.__setattr__(self, "byte_length", byte_length)
        object.__setattr__(
            self,
            "record_hash",
            canonical_digest(
                _host_record_payload(self), domain="orion.host-evidence-record.v1"
            ),
        )

    @property
    def resolved(self) -> bool:
        return self.status is EvidenceStatus.RESOLVED

    @property
    def utf8_text(self) -> str | None:
        """Strict derived view; invalid UTF-8 never rewrites byte identity."""

        if not self.content_available:
            return None
        try:
            return self.content_bytes.decode("utf-8", errors="strict")
        except UnicodeDecodeError:
            return None


@dataclass(frozen=True)
class HostEvidenceSnapshot:
    """A deterministic sequence of exact occasions, not an atomic FS instant."""

    root_configuration_hash: str
    manifest_hash: str
    captured_at_authority_revision: str
    captured_at_support_revision: str
    required_obligation_ids: tuple[str, ...]
    records: tuple[HostEvidenceRecord, ...]
    schema_version: str = EVIDENCE_SNAPSHOT_SCHEMA_VERSION
    capture_work_usage: tuple[tuple[str, int], ...] = ()
    capture_work_exhausted_dimensions: tuple[str, ...] = ()
    unresolved_obligation_ids: tuple[str, ...] = field(init=False)
    snapshot_id: str = field(init=False)

    def __post_init__(self) -> None:
        for field_name in (
            "root_configuration_hash",
            "manifest_hash",
            "captured_at_authority_revision",
            "captured_at_support_revision",
        ):
            _require_sha256(getattr(self, field_name), field_name)
        _require_exact_text(self.schema_version, "schema_version")
        _require_text_byte_cap(self.schema_version, "schema_version")
        if self.schema_version != EVIDENCE_SNAPSHOT_SCHEMA_VERSION:
            raise ValueError(f"unsupported evidence snapshot schema: {self.schema_version!r}")
        _require_exact_tuple(
            self.required_obligation_ids, "required_obligation_ids"
        )
        _require_exact_tuple(self.records, "records")
        _require_exact_tuple(self.capture_work_usage, "capture_work_usage")
        _require_exact_tuple(
            self.capture_work_exhausted_dimensions,
            "capture_work_exhausted_dimensions",
        )
        if len(self.required_obligation_ids) > MAX_EVIDENCE_OBLIGATION_COUNT:
            raise ValueError("snapshot exceeds the evidence obligation count cap")
        if len(self.records) > MAX_EVIDENCE_SNAPSHOT_RECORDS:
            raise ValueError("snapshot exceeds the evidence snapshot record count cap")
        if any(type(record) is not HostEvidenceRecord for record in self.records):
            raise ValueError("records must contain exact HostEvidenceRecord values")
        if (
            sum(len(record.role_bindings) for record in self.records)
            > MAX_EVIDENCE_BINDING_COUNT
        ):
            raise ValueError("snapshot exceeds the evidence binding count cap")
        object.__setattr__(
            self,
            "required_obligation_ids",
            tuple(sorted(self.required_obligation_ids)),
        )
        object.__setattr__(
            self,
            "records",
            tuple(sorted(self.records, key=lambda item: item.ref)),
        )
        usage: list[tuple[str, int]] = []
        for item in self.capture_work_usage:
            if (
                type(item) is not tuple
                or len(item) != 2
                or type(item[0]) is not str
                or not item[0]
                or type(item[1]) is not int
                or item[1] < 0
            ):
                raise ValueError("capture work usage must contain text/integer pairs")
            _require_text_byte_cap(item[0], "capture work usage coordinate")
            if item[0] not in _CAPTURE_WORK_USAGE_COORDINATES:
                raise ValueError("capture work usage coordinate is unknown")
            usage.append(item)
        usage.sort(key=lambda item: item[0])
        if len({item[0] for item in usage}) != len(usage):
            raise ValueError("capture work usage coordinates must be unique")
        object.__setattr__(self, "capture_work_usage", tuple(usage))
        exhausted: list[str] = []
        for coordinate in self.capture_work_exhausted_dimensions:
            _require_exact_text(coordinate, "capture work exhausted coordinate")
            _require_text_byte_cap(
                coordinate, "capture work exhausted coordinate"
            )
            if coordinate not in _CAPTURE_WORK_EXHAUSTED_COORDINATES:
                raise ValueError("capture work exhausted coordinate is unknown")
            exhausted.append(coordinate)
        if len(set(exhausted)) != len(exhausted):
            raise ValueError("capture work exhausted coordinates must be unique")
        object.__setattr__(
            self,
            "capture_work_exhausted_dimensions",
            tuple(sorted(exhausted)),
        )
        if sum(record.byte_length for record in self.records) > MAX_EVIDENCE_SNAPSHOT_BYTES:
            raise ValueError("content exceeds the evidence snapshot byte cap")
        for obligation_id in self.required_obligation_ids:
            _require_exact_text(obligation_id, "required obligation id")
            _require_text_byte_cap(obligation_id, "required obligation id")
        if len(set(self.required_obligation_ids)) != len(
            self.required_obligation_ids
        ):
            raise ValueError("required obligation ids must be unique")
        refs: set[str] = set()
        ordinals: set[int] = set()
        for expected_ordinal, record in enumerate(self.records):
            if record.ref in refs or record.capture_ordinal in ordinals:
                raise ValueError("snapshot records require unique refs and ordinals")
            if record.capture_ordinal != expected_ordinal:
                raise ValueError("snapshot ordinals must be contiguous canonical ref order")
            refs.add(record.ref)
            ordinals.add(record.capture_ordinal)
            if record.root_configuration_hash != self.root_configuration_hash:
                raise ValueError("record root configuration does not match snapshot")

        unresolved: list[str] = []
        for obligation_id in self.required_obligation_ids:
            bound = [
                record
                for record in self.records
                if any(
                    binding.obligation_id == obligation_id
                    for binding in record.role_bindings
                )
            ]
            if not bound or any(not record.resolved for record in bound):
                unresolved.append(obligation_id)
        object.__setattr__(self, "unresolved_obligation_ids", tuple(unresolved))
        object.__setattr__(
            self,
            "snapshot_id",
            canonical_digest(
                _host_snapshot_payload(self),
                domain="orion.host-evidence-snapshot.v1",
            ),
        )

    @property
    def cannot_check(self) -> bool:
        return bool(self.unresolved_obligation_ids) or any(
            not record.resolved for record in self.records
        )


def _host_record_payload(record: HostEvidenceRecord) -> dict[str, object]:
    return {
        "schema_version": record.schema_version,
        "capture_ordinal": record.capture_ordinal,
        "ref": record.ref,
        "status": record.status.value,
        "backend_type": record.backend_type,
        "scheme": record.scheme,
        "relative_path": record.relative_path,
        "declared_digest": record.declared_digest,
        "resolved_source_revision": record.resolved_source_revision,
        "source_object_format": record.source_object_format,
        "source_reference_oid": record.source_reference_oid,
        "source_blob_oid": record.source_blob_oid,
        "source_tree_entry_mode": record.source_tree_entry_mode,
        "root_configuration_hash": record.root_configuration_hash,
        "role_bindings": [
            {
                "binding_id": item.binding_id,
                "evidence_ref": item.evidence_ref,
                "role_id": item.role_id,
                "obligation_id": item.obligation_id,
            }
            for item in sorted(record.role_bindings, key=lambda item: item.binding_id)
        ],
        "content_available": record.content_available,
        "content_digest_algorithm": "sha256" if record.content_available else "",
        "content_hash": record.content_hash,
        "byte_length": record.byte_length,
        "source_device": record.source_device,
        "source_inode": record.source_inode,
        "source_size": record.source_size,
        "source_mtime_ns": record.source_mtime_ns,
        "source_ctime_ns": record.source_ctime_ns,
        "note": record.note,
    }


def _host_snapshot_payload(snapshot: HostEvidenceSnapshot) -> dict[str, object]:
    return {
        "schema_version": snapshot.schema_version,
        "root_configuration_hash": snapshot.root_configuration_hash,
        "manifest_hash": snapshot.manifest_hash,
        "captured_at_authority_revision": snapshot.captured_at_authority_revision,
        "captured_at_support_revision": snapshot.captured_at_support_revision,
        "required_obligation_ids": sorted(snapshot.required_obligation_ids),
        "capture_work_usage": [
            list(item) for item in snapshot.capture_work_usage
        ],
        "capture_work_exhausted_dimensions": list(
            snapshot.capture_work_exhausted_dimensions
        ),
        "records": [
            [record.ref, record.record_hash]
            for record in sorted(snapshot.records, key=lambda item: item.ref)
        ],
    }


def snapshot_hash(snapshot: HostEvidenceSnapshot) -> str:
    """Recompute the acyclic snapshot commitment; the ID is not its own input."""

    if type(snapshot) is not HostEvidenceSnapshot:
        raise ValueError("snapshot must be an exact HostEvidenceSnapshot")
    return canonical_digest(
        _host_snapshot_payload(snapshot), domain="orion.host-evidence-snapshot.v1"
    )


def _require_sha256(value: object, field_name: str) -> None:
    if (
        type(value) is not str
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise ValueError(f"{field_name} must be a lowercase SHA-256 digest")


@dataclass(frozen=True)
class _OpenedRoot:
    scheme: str
    configured_path: Path
    file_descriptor: int | None
    source_device: int | None
    source_inode: int | None
    open_status: EvidenceStatus | None = None
    note: str = ""
    git_directory_fd: int | None = None
    git_source_device: int | None = None
    git_source_inode: int | None = None
    git_open_status: EvidenceStatus | None = None
    git_note: str = ""


@dataclass(frozen=True)
class _CaptureResult:
    status: EvidenceStatus
    backend_type: str
    scheme: str
    relative_path: str
    declared_digest: str = ""
    resolved_source_revision: str = ""
    source_object_format: str = ""
    source_reference_oid: str = ""
    source_blob_oid: str = ""
    source_tree_entry_mode: str = ""
    content_bytes: bytes = b""
    content_available: bool = False
    source_device: int | None = None
    source_inode: int | None = None
    source_size: int | None = None
    source_mtime_ns: int | None = None
    source_ctime_ns: int | None = None
    note: str = ""


@dataclass
class _CaptureWorkState:
    max_local_bytes: int
    max_git_commands: int
    max_git_stdout_bytes: int
    max_git_stderr_bytes: int
    max_elapsed_ns: int
    max_path_components: int
    max_tree_entries: int
    max_git_object_bytes: int
    max_git_objects: int
    started_at_ns: int = field(default_factory=time.monotonic_ns)
    local_bytes_read: int = 0
    git_commands: int = 0
    git_stdout_bytes: int = 0
    git_stderr_bytes: int = 0
    path_components: int = 0
    tree_entries: int = 0
    git_object_bytes: int = 0
    distinct_git_objects: int = 0
    seen_git_objects: set[tuple[int, int, str, str, str]] = field(
        default_factory=set,
        repr=False,
    )
    verified_git_objects: dict[tuple[int, int, str, str, str], bytes] = field(
        default_factory=dict,
        repr=False,
    )
    exhausted_dimensions: set[str] = field(default_factory=set, repr=False)

    @property
    def remaining_local_bytes(self) -> int:
        return max(0, self.max_local_bytes - self.local_bytes_read)

    def charge_local_bytes(self, observed: int) -> bool:
        if type(observed) is not int or observed < 0:
            raise ValueError("observed local bytes must be a nonnegative integer")
        if observed > self.remaining_local_bytes:
            self.local_bytes_read = self.max_local_bytes
            self.exhausted_dimensions.add("local_bytes")
            return False
        self.local_bytes_read += observed
        return True

    def reserve_git_command(self) -> bool:
        if not self.check_deadline():
            return False
        if self.git_commands >= self.max_git_commands:
            self.exhausted_dimensions.add("git_commands")
            return False
        self.git_commands += 1
        return True

    def check_deadline(self) -> bool:
        if self.deadline_exhausted:
            self.exhausted_dimensions.add("elapsed_ns")
            return False
        return True

    def remaining_git_output(self, stream: str) -> int:
        if stream == "stdout":
            return max(0, self.max_git_stdout_bytes - self.git_stdout_bytes)
        if stream == "stderr":
            return max(0, self.max_git_stderr_bytes - self.git_stderr_bytes)
        raise ValueError("Git output stream must be stdout or stderr")

    def charge_git_output(self, stream: str, observed: int) -> bool:
        if type(observed) is not int or observed < 0:
            raise ValueError("observed Git output bytes must be a nonnegative integer")
        remaining = self.remaining_git_output(stream)
        coordinate = f"git_{stream}_bytes"
        if observed > remaining:
            if stream == "stdout":
                self.git_stdout_bytes += observed
            else:
                self.git_stderr_bytes += observed
            self.exhausted_dimensions.add(coordinate)
            return False
        if stream == "stdout":
            self.git_stdout_bytes += observed
        else:
            self.git_stderr_bytes += observed
        return True

    def charge_path_components(self, observed: int) -> bool:
        if self.path_components + observed > self.max_path_components:
            self.exhausted_dimensions.add("path_components")
            return False
        self.path_components += observed
        return True

    def charge_tree_entry(self) -> bool:
        if self.tree_entries >= self.max_tree_entries:
            self.exhausted_dimensions.add("tree_entries")
            return False
        self.tree_entries += 1
        return True

    def cached_git_object(
        self, key: tuple[int, int, str, str, str]
    ) -> bytes | None:
        return self.verified_git_objects.get(key)

    def reserve_git_object(
        self,
        key: tuple[int, int, str, str, str],
        declared_size: int,
    ) -> bool:
        is_new = key not in self.seen_git_objects
        if is_new and self.distinct_git_objects >= self.max_git_objects:
            self.exhausted_dimensions.add("git_objects")
            return False
        if self.git_object_bytes + declared_size > self.max_git_object_bytes:
            self.exhausted_dimensions.add("git_object_bytes")
            return False
        self.git_object_bytes += declared_size
        if is_new:
            self.seen_git_objects.add(key)
            self.distinct_git_objects += 1
        return True

    def cache_git_object(
        self,
        key: tuple[int, int, str, str, str],
        payload: bytes,
    ) -> None:
        self.verified_git_objects[key] = payload

    def usage(self) -> tuple[tuple[str, int], ...]:
        return (
            ("distinct_git_objects", self.distinct_git_objects),
            ("git_commands", self.git_commands),
            ("git_object_bytes", self.git_object_bytes),
            ("git_stderr_bytes", self.git_stderr_bytes),
            ("git_stdout_bytes", self.git_stdout_bytes),
            ("local_bytes_read", self.local_bytes_read),
            ("path_components", self.path_components),
            ("tree_entries", self.tree_entries),
        )

    @property
    def deadline_exhausted(self) -> bool:
        return time.monotonic_ns() - self.started_at_ns >= self.max_elapsed_ns

    @property
    def remaining_seconds(self) -> float:
        remaining_ns = self.max_elapsed_ns - (
            time.monotonic_ns() - self.started_at_ns
        )
        return max(0.0, remaining_ns / 1_000_000_000)


def _read_open_descriptor(fd: int, limit: int) -> tuple[bytes, bool]:
    """Read one opened regular-file occasion, bounded by limit plus one byte."""

    chunks: list[bytes] = []
    observed = 0
    while observed <= limit:
        chunk = os.read(fd, min(1_048_576, limit + 1 - observed))
        if not chunk:
            break
        chunks.append(chunk)
        observed += len(chunk)
    payload = b"".join(chunks)
    return payload, len(payload) > limit


def _safe_relative_parts(location: str) -> tuple[str, ...] | None:
    if not location or "\x00" in location or location.startswith("/"):
        return None
    parts = tuple(location.split("/"))
    if not parts or any(part in {"", ".", ".."} for part in parts):
        return None
    return parts


def _descriptor_metadata(info: os.stat_result) -> tuple[int, int, int, int, int]:
    return (
        info.st_dev,
        info.st_ino,
        info.st_size,
        info.st_mtime_ns,
        info.st_ctime_ns,
    )



def _classify_open_error_for_role(
    error: OSError,
    directory_fd: int,
    component: str,
    *,
    require_directory: bool,
) -> EvidenceStatus:
    """Classify an open failure against the role expected of the component."""

    if not require_directory:
        return _classify_open_error(error, directory_fd, component)
    if error.errno in {errno.ENOENT, errno.ELOOP}:
        return _classify_open_error(error, directory_fd, component)
    import stat as _stat

    try:
        current = os.stat(
            component, dir_fd=directory_fd, follow_symlinks=False
        )
    except OSError:
        return _classify_open_error(error, directory_fd, component)
    if _stat.S_ISLNK(current.st_mode):
        return EvidenceStatus.SYMLINK_DISALLOWED
    if not _stat.S_ISDIR(current.st_mode):
        return EvidenceStatus.NON_REGULAR_FILE
    return EvidenceStatus.UNREADABLE_ARTIFACT

def _capture_local_file(
    opened_root: _OpenedRoot,
    *,
    location: str,
    declared_digest: str,
    work_state: _CaptureWorkState,
) -> _CaptureResult:
    if not work_state.check_deadline():
        return _CaptureResult(
            EvidenceStatus.WORK_BUDGET_EXHAUSTED,
            "file",
            opened_root.scheme,
            location,
            declared_digest=declared_digest,
            note="snapshot elapsed-time work budget is exhausted",
        )
    if opened_root.file_descriptor is None:
        return _CaptureResult(
            opened_root.open_status or EvidenceStatus.UNREADABLE_ARTIFACT,
            "file",
            opened_root.scheme,
            location,
            declared_digest=declared_digest,
            note=opened_root.note or "registered root could not be opened",
        )
    parts = _safe_relative_parts(location)
    if parts is None:
        return _CaptureResult(
            EvidenceStatus.ESCAPES_ROOT,
            "file",
            opened_root.scheme,
            location,
            declared_digest=declared_digest,
            note="protected evidence path must be an unambiguous relative path",
        )
    if not work_state.charge_path_components(len(parts)):
        return _CaptureResult(
            EvidenceStatus.WORK_BUDGET_EXHAUSTED,
            "file",
            opened_root.scheme,
            location,
            declared_digest=declared_digest,
            note="snapshot path-component work budget is exhausted",
        )
    if len(declared_digest) < 64:
        return _CaptureResult(
            EvidenceStatus.DIGEST_TOO_SHORT,
            "file",
            opened_root.scheme,
            location,
            declared_digest=declared_digest,
            note="protected evidence requires a full SHA-256 digest",
        )
    if (
        len(declared_digest) != 64
        or any(character not in "0123456789abcdef" for character in declared_digest)
    ):
        return _CaptureResult(
            EvidenceStatus.MALFORMED_REF,
            "file",
            opened_root.scheme,
            location,
            declared_digest=declared_digest,
            note="protected evidence digest must be 64 lowercase hexadecimal characters",
        )

    directory_fd = os.dup(opened_root.file_descriptor)
    final_fd: int | None = None
    failure_component = parts[-1]
    failure_component_must_be_directory = False
    try:
        directory_flags = _directory_open_flags()
        for component in parts[:-1]:
            failure_component = component
            failure_component_must_be_directory = True
            next_fd = os.open(
                component,
                directory_flags,
                dir_fd=directory_fd,
            )
            os.close(directory_fd)
            directory_fd = next_fd
            if not work_state.check_deadline():
                return _CaptureResult(
                    EvidenceStatus.WORK_BUDGET_EXHAUSTED,
                    "file",
                    opened_root.scheme,
                    location,
                    declared_digest=declared_digest,
                    note="snapshot elapsed-time work budget is exhausted",
                )
        failure_component = parts[-1]
        failure_component_must_be_directory = False
        pre_open = os.stat(
            parts[-1], dir_fd=directory_fd, follow_symlinks=False
        )
        if stat.S_ISLNK(pre_open.st_mode):
            return _CaptureResult(
                EvidenceStatus.SYMLINK_DISALLOWED,
                "file",
                opened_root.scheme,
                location,
                declared_digest=declared_digest,
                note="protected evidence final component is a symlink",
            )
        if not stat.S_ISREG(pre_open.st_mode):
            return _CaptureResult(
                EvidenceStatus.NON_REGULAR_FILE,
                "file",
                opened_root.scheme,
                location,
                declared_digest=declared_digest,
                note="protected evidence must be a regular file",
            )
        final_flags = os.O_RDONLY | os.O_NONBLOCK | os.O_NOCTTY
        final_flags |= getattr(os, "O_CLOEXEC", 0)
        final_flags |= getattr(os, "O_NOFOLLOW_ANY", 0) or os.O_NOFOLLOW
        final_fd = os.open(parts[-1], final_flags, dir_fd=directory_fd)
        before = os.fstat(final_fd)
        if not stat.S_ISREG(before.st_mode):
            return _CaptureResult(
                EvidenceStatus.NON_REGULAR_FILE,
                "file",
                opened_root.scheme,
                location,
                declared_digest=declared_digest,
                note="protected evidence must be a regular file",
            )
        if (
            pre_open.st_dev,
            pre_open.st_ino,
            stat.S_IFMT(pre_open.st_mode),
        ) != (
            before.st_dev,
            before.st_ino,
            stat.S_IFMT(before.st_mode),
        ):
            return _CaptureResult(
                EvidenceStatus.CHANGED_DURING_CAPTURE,
                "file",
                opened_root.scheme,
                location,
                declared_digest=declared_digest,
                note="path entry changed between no-follow stat and open",
            )
        if before.st_size > MAX_EVIDENCE_RECORD_BYTES:
            return _CaptureResult(
                EvidenceStatus.TOO_LARGE,
                "file",
                opened_root.scheme,
                location,
                declared_digest=declared_digest,
                note=f"evidence exceeds {MAX_EVIDENCE_RECORD_BYTES} bytes",
            )
        if not work_state.check_deadline():
            return _CaptureResult(
                EvidenceStatus.WORK_BUDGET_EXHAUSTED,
                "file",
                opened_root.scheme,
                location,
                declared_digest=declared_digest,
                note="snapshot elapsed-time work budget is exhausted",
            )
        remaining_local_bytes = work_state.remaining_local_bytes
        if before.st_size > remaining_local_bytes:
            work_state.exhausted_dimensions.add("local_bytes")
            return _CaptureResult(
                EvidenceStatus.WORK_BUDGET_EXHAUSTED,
                "file",
                opened_root.scheme,
                location,
                declared_digest=declared_digest,
                note="snapshot local-byte work budget is exhausted",
            )
        payload, too_large = _read_open_descriptor(
            final_fd, min(MAX_EVIDENCE_RECORD_BYTES, remaining_local_bytes)
        )
        after = os.fstat(final_fd)
        if not work_state.charge_local_bytes(len(payload)):
            return _CaptureResult(
                EvidenceStatus.WORK_BUDGET_EXHAUSTED,
                "file",
                opened_root.scheme,
                location,
                declared_digest=declared_digest,
                note="snapshot local-byte work budget changed during capture",
            )
        if not work_state.check_deadline():
            return _CaptureResult(
                EvidenceStatus.WORK_BUDGET_EXHAUSTED,
                "file",
                opened_root.scheme,
                location,
                declared_digest=declared_digest,
                note="snapshot elapsed-time work budget is exhausted",
            )
        if too_large:
            return _CaptureResult(
                EvidenceStatus.TOO_LARGE,
                "file",
                opened_root.scheme,
                location,
                declared_digest=declared_digest,
                note=f"evidence exceeds {MAX_EVIDENCE_RECORD_BYTES} bytes",
            )
        content_hash = hashlib.sha256(payload).hexdigest()
        status = EvidenceStatus.RESOLVED
        note = ""
        if _descriptor_metadata(before) != _descriptor_metadata(after):
            status = EvidenceStatus.CHANGED_DURING_CAPTURE
            note = "file descriptor metadata changed during capture"
        elif content_hash != declared_digest:
            status = EvidenceStatus.DIGEST_MISMATCH
            note = "captured bytes do not match the full declared SHA-256 digest"
        return _CaptureResult(
            status,
            "file",
            opened_root.scheme,
            location,
            declared_digest=declared_digest,
            content_bytes=payload,
            content_available=True,
            source_device=before.st_dev,
            source_inode=before.st_ino,
            source_size=before.st_size,
            source_mtime_ns=before.st_mtime_ns,
            source_ctime_ns=before.st_ctime_ns,
            note=note,
        )
    except OSError as error:
        if not work_state.check_deadline():
            return _CaptureResult(
                EvidenceStatus.WORK_BUDGET_EXHAUSTED,
                "file",
                opened_root.scheme,
                location,
                declared_digest=declared_digest,
                note="snapshot elapsed-time work budget is exhausted",
            )
        status = _classify_open_error_for_role(
            error,
            directory_fd,
            failure_component,
            require_directory=failure_component_must_be_directory,
        )
        return _CaptureResult(
            status,
            "file",
            opened_root.scheme,
            location,
            declared_digest=declared_digest,
            note=str(error),
        )
    finally:
        if final_fd is not None:
            os.close(final_fd)
        os.close(directory_fd)


def _missing_capture_capability() -> str:
    required_flags = ("O_DIRECTORY", "O_NONBLOCK", "O_NOCTTY")
    missing = [name for name in required_flags if not getattr(os, name, 0)]
    if not (getattr(os, "O_NOFOLLOW", 0) or getattr(os, "O_NOFOLLOW_ANY", 0)):
        missing.append("O_NOFOLLOW")
    if not _OS_OPEN_SUPPORTS_DIR_FD:
        missing.append("open(dir_fd=...)")
    if not _OS_STAT_SUPPORTS_DIR_FD or not _OS_STAT_SUPPORTS_NOFOLLOW:
        missing.append("stat(dir_fd=..., follow_symlinks=False)")
    return ",".join(missing)


def _directory_open_flags() -> int:
    flags = os.O_RDONLY | os.O_DIRECTORY
    flags |= getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW_ANY", 0) or os.O_NOFOLLOW
    return flags


def _classify_open_error(
    error: OSError, directory_fd: int | None, component: str
) -> EvidenceStatus:
    if error.errno == errno.ENOENT:
        return EvidenceStatus.MISSING_ARTIFACT
    if error.errno == errno.ELOOP:
        return EvidenceStatus.SYMLINK_DISALLOWED
    if directory_fd is not None:
        try:
            info = os.stat(component, dir_fd=directory_fd, follow_symlinks=False)
        except OSError:
            info = None
        if info is not None and stat.S_ISLNK(info.st_mode):
            return EvidenceStatus.SYMLINK_DISALLOWED
        if info is not None and not stat.S_ISREG(info.st_mode):
            return EvidenceStatus.NON_REGULAR_FILE
    if error.errno in {errno.ENOTDIR, errno.EISDIR}:
        return EvidenceStatus.NON_REGULAR_FILE
    return EvidenceStatus.UNREADABLE_ARTIFACT


def _read_git_control_file(
    git_directory_fd: int,
    *parts: str,
) -> tuple[bool, bytes | None, str]:
    """Read one bounded admin control file without following repository links."""

    directory_fd = os.dup(git_directory_fd)
    final_fd: int | None = None
    try:
        for component in parts[:-1]:
            try:
                next_fd = os.open(
                    component,
                    _directory_open_flags(),
                    dir_fd=directory_fd,
                )
            except OSError as error:
                if error.errno == errno.ENOENT:
                    return False, None, ""
                return True, None, f"unsafe Git administrative path: {'/'.join(parts)}"
            os.close(directory_fd)
            directory_fd = next_fd
        try:
            pre_open = os.stat(
                parts[-1], dir_fd=directory_fd, follow_symlinks=False
            )
        except OSError as error:
            if error.errno == errno.ENOENT:
                return False, None, ""
            return True, None, f"unreadable Git administrative entry: {'/'.join(parts)}"
        if not stat.S_ISREG(pre_open.st_mode):
            return True, None, f"unsafe Git administrative entry: {'/'.join(parts)}"
        if pre_open.st_size > MAX_EVIDENCE_GIT_CONTROL_BYTES:
            return True, None, f"oversized Git administrative entry: {'/'.join(parts)}"
        flags = os.O_RDONLY | os.O_NONBLOCK | os.O_NOCTTY
        flags |= getattr(os, "O_CLOEXEC", 0)
        flags |= getattr(os, "O_NOFOLLOW_ANY", 0) or os.O_NOFOLLOW
        final_fd = os.open(parts[-1], flags, dir_fd=directory_fd)
        before = os.fstat(final_fd)
        if not stat.S_ISREG(before.st_mode):
            return True, None, f"unsafe Git administrative entry: {'/'.join(parts)}"
        if (pre_open.st_dev, pre_open.st_ino) != (before.st_dev, before.st_ino):
            return True, None, f"changed Git administrative entry: {'/'.join(parts)}"
        payload, too_large = _read_open_descriptor(
            final_fd, MAX_EVIDENCE_GIT_CONTROL_BYTES
        )
        after = os.fstat(final_fd)
        if too_large:
            return True, None, f"oversized Git administrative entry: {'/'.join(parts)}"
        if _descriptor_metadata(before) != _descriptor_metadata(after):
            return True, None, f"changed Git administrative entry: {'/'.join(parts)}"
        return True, payload, ""
    except OSError:
        return True, None, f"unreadable Git administrative entry: {'/'.join(parts)}"
    finally:
        if final_fd is not None:
            os.close(final_fd)
        os.close(directory_fd)


def _config_declares_include(payload: bytes) -> bool:
    for raw_line in payload.splitlines():
        line = raw_line.lstrip(b" \t")
        if not line.startswith(b"[") or b"]" not in line:
            continue
        header = line[1 : line.index(b"]")].strip().lower()
        section = header.split(None, 1)[0].rstrip(b'"')
        if section in {b"include", b"includeif"}:
            return True
    return False


def _config_declares_lazy_object_source(payload: bytes) -> bool:
    """Whether the local configuration can make object reads fetch remotely.

    Lazy fetch only happens in promisor/partial-clone repositories. When the
    host Git predates the ``--no-lazy-fetch`` guard, such repositories must be
    rejected outright so a capture can never trigger a network fetch.
    """

    for raw_line in payload.splitlines():
        line = raw_line.split(b"#", 1)[0].split(b";", 1)[0].strip().lower()
        if b"=" not in line:
            continue
        key = line.split(b"=", 1)[0].strip()
        if key in {b"promisor", b"partialclonefilter", b"partialclone"}:
            return True
    return False


def _protected_git_layout_issue(git_directory_fd: int) -> str:
    for parts, label in (
        (("objects", "info", "alternates"), "object alternates"),
        (("objects", "info", "http-alternates"), "HTTP object alternates"),
        (("commondir",), "commondir indirection"),
    ):
        present, _, note = _read_git_control_file(git_directory_fd, *parts)
        if present:
            return note or f"protected Git V1 rejects {label}"
    config_present, config_bytes, note = _read_git_control_file(
        git_directory_fd, "config"
    )
    if config_present and config_bytes is None:
        return note or "protected Git V1 cannot bind the local configuration"
    if config_bytes is not None and _config_declares_include(config_bytes):
        return "protected Git V1 rejects local config includes"
    if (
        config_bytes is not None
        and not _git_supports_no_lazy_fetch()
        and _config_declares_lazy_object_source(config_bytes)
    ):
        return (
            "protected Git V1 rejects promisor/partial-clone repositories on a "
            "Git without --no-lazy-fetch"
        )
    return ""


def _looks_like_bare_repository(root_fd: int) -> bool:
    try:
        head = os.stat("HEAD", dir_fd=root_fd, follow_symlinks=False)
        objects = os.stat("objects", dir_fd=root_fd, follow_symlinks=False)
        refs = os.stat("refs", dir_fd=root_fd, follow_symlinks=False)
    except OSError:
        return False
    return (
        stat.S_ISREG(head.st_mode)
        and stat.S_ISDIR(objects.st_mode)
        and stat.S_ISDIR(refs.st_mode)
    )


def _open_root_without_symlinks(scheme: str, path: Path) -> _OpenedRoot:
    capability_gap = _missing_capture_capability()
    if capability_gap:
        return _OpenedRoot(
            scheme,
            path,
            None,
            None,
            None,
            EvidenceStatus.CAPABILITY_UNAVAILABLE,
            f"missing protected capture capability: {capability_gap}",
        )
    if not path.is_absolute() or any(part in {".", ".."} for part in path.parts):
        return _OpenedRoot(
            scheme,
            path,
            None,
            None,
            None,
            EvidenceStatus.ESCAPES_ROOT,
            "registered evidence root must be an absolute lexical path",
        )
    flags = _directory_open_flags()
    directory_fd: int | None = None
    try:
        directory_fd = os.open(os.sep, flags)
        for component in path.parts[1:]:
            try:
                next_fd = os.open(component, flags, dir_fd=directory_fd)
            except OSError as error:
                status = _classify_open_error(error, directory_fd, component)
                return _OpenedRoot(
                    scheme,
                    path,
                    None,
                    None,
                    None,
                    status,
                    str(error),
                )
            os.close(directory_fd)
            directory_fd = next_fd
        info = os.fstat(directory_fd)
        if not stat.S_ISDIR(info.st_mode):
            return _OpenedRoot(
                scheme,
                path,
                None,
                None,
                None,
                EvidenceStatus.NON_REGULAR_FILE,
                "registered root is not a directory",
            )
        opened_fd = directory_fd
        directory_fd = None
        git_directory_fd: int | None = None
        git_source_device: int | None = None
        git_source_inode: int | None = None
        git_open_status: EvidenceStatus | None = None
        git_note = ""
        try:
            git_directory_fd = os.open(".git", flags, dir_fd=opened_fd)
            git_info = os.fstat(git_directory_fd)
            if not stat.S_ISDIR(git_info.st_mode):
                os.close(git_directory_fd)
                git_directory_fd = None
                git_open_status = EvidenceStatus.UNSUPPORTED_GIT_LAYOUT
                git_note = "protected Git V1 requires .git to be a directory"
            else:
                layout_issue = _protected_git_layout_issue(git_directory_fd)
                if layout_issue:
                    os.close(git_directory_fd)
                    git_directory_fd = None
                    git_open_status = EvidenceStatus.UNSUPPORTED_GIT_LAYOUT
                    git_note = layout_issue
                else:
                    git_source_device = git_info.st_dev
                    git_source_inode = git_info.st_ino
        except OSError as error:
            git_directory_fd = None
            try:
                git_entry = os.stat(
                    ".git", dir_fd=opened_fd, follow_symlinks=False
                )
            except OSError:
                git_entry = None
            if git_entry is None and error.errno == errno.ENOENT:
                if _looks_like_bare_repository(opened_fd):
                    git_open_status = EvidenceStatus.UNSUPPORTED_GIT_LAYOUT
                    git_note = "protected Git V1 does not admit bare repository roots"
                else:
                    git_open_status = EvidenceStatus.NOT_A_REPOSITORY
                    git_note = "protected Git V1 requires a .git directory"
            else:
                git_open_status = EvidenceStatus.UNSUPPORTED_GIT_LAYOUT
                git_note = "protected Git V1 rejects gitfiles, symlinks, and special .git entries"
        return _OpenedRoot(
            scheme,
            path,
            opened_fd,
            info.st_dev,
            info.st_ino,
            git_directory_fd=git_directory_fd,
            git_source_device=git_source_device,
            git_source_inode=git_source_inode,
            git_open_status=git_open_status,
            git_note=git_note,
        )
    except OSError as error:
        return _OpenedRoot(
            scheme,
            path,
            None,
            None,
            None,
            _classify_open_error(error, None, str(path)),
            str(error),
        )
    finally:
        if directory_fd is not None:
            os.close(directory_fd)


def _open_roots(roots: Mapping[str, Path]) -> tuple[_OpenedRoot, ...]:
    if len(roots) > MAX_EVIDENCE_ROOT_COUNT:
        raise ValueError("evidence roots exceed the root count cap")
    copied: list[tuple[str, Path]] = []
    path_components = 0
    for scheme, path in roots.items():
        _require_exact_text(scheme, "evidence root scheme")
        _require_text_byte_cap(scheme, "evidence root scheme")
        if not isinstance(path, Path):
            raise ValueError("evidence roots must contain pathlib.Path values")
        try:
            encoded_path = os.fsencode(path)
        except (TypeError, UnicodeEncodeError) as error:
            raise ValueError("evidence root path must be encodable") from error
        if len(encoded_path) > MAX_EVIDENCE_ROOT_PATH_BYTES:
            raise ValueError("evidence root exceeds the root path byte cap")
        path_components += len(path.parts)
        if path_components > MAX_EVIDENCE_ROOT_PATH_COMPONENTS:
            raise ValueError("evidence roots exceed the path component cap")
        copied.append((scheme, path))
    return tuple(
        _open_root_without_symlinks(scheme, path)
        for scheme, path in sorted(copied)
    )


_EXECUTABLE_IDENTITY_CACHE: dict[
    tuple[str, int, int, int, int, int], dict[str, object]
] = {}


def _executable_artifact_identity(path: str | None) -> dict[str, object]:
    if path is None:
        return {"path": "UNAVAILABLE", "status": "UNAVAILABLE"}
    fd: int | None = None
    try:
        flags = os.O_RDONLY | os.O_NONBLOCK | os.O_NOCTTY
        flags |= getattr(os, "O_CLOEXEC", 0)
        flags |= getattr(os, "O_NOFOLLOW_ANY", 0) or os.O_NOFOLLOW
        fd = os.open(path, flags)
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):
            return {"path": path, "status": "NOT_REGULAR"}
        key = (
            path,
            before.st_dev,
            before.st_ino,
            before.st_size,
            before.st_mtime_ns,
            before.st_ctime_ns,
        )
        cached = _EXECUTABLE_IDENTITY_CACHE.get(key)
        if cached is not None:
            return cached
        if before.st_size > MAX_EVIDENCE_EXECUTABLE_BYTES:
            return {
                "path": path,
                "status": "TOO_LARGE",
                "byte_length": before.st_size,
            }
        digest = hashlib.sha256()
        observed = 0
        while True:
            chunk = os.read(fd, min(65_536, MAX_EVIDENCE_EXECUTABLE_BYTES + 1 - observed))
            if not chunk:
                break
            observed += len(chunk)
            if observed > MAX_EVIDENCE_EXECUTABLE_BYTES:
                return {
                    "path": path,
                    "status": "TOO_LARGE",
                    "byte_length": observed,
                }
            digest.update(chunk)
        after = os.fstat(fd)
        if _descriptor_metadata(before) != _descriptor_metadata(after):
            return {"path": path, "status": "CHANGED_DURING_HASH"}
        identity = {
            "path": path,
            "status": "BOUND",
            "source_device": before.st_dev,
            "source_inode": before.st_ino,
            "byte_length": observed,
            "source_mtime_ns": before.st_mtime_ns,
            "source_ctime_ns": before.st_ctime_ns,
            "sha256": digest.hexdigest(),
        }
        _EXECUTABLE_IDENTITY_CACHE[key] = identity
        return identity
    except OSError as error:
        return {
            "path": path,
            "status": "UNAVAILABLE",
            "errno": error.errno,
        }
    finally:
        if fd is not None:
            os.close(fd)


def _root_configuration_hash(opened_roots: tuple[_OpenedRoot, ...]) -> str:
    payload = {
        "capture_policy": "orion.descriptor-root-capture.v1",
        "git_executable": _GIT_EXECUTABLE or "UNAVAILABLE",
        "git_executable_artifact": _executable_artifact_identity(_GIT_EXECUTABLE),
        "git_fd_helper_executable": _GIT_FD_HELPER_EXECUTABLE,
        "git_fd_helper_executable_artifact": _executable_artifact_identity(
            _GIT_FD_HELPER_EXECUTABLE
        ),
        "git_fd_helper_source_sha256": hashlib.sha256(
            _GIT_FD_EXEC_HELPER.encode("utf-8")
        ).hexdigest(),
        "git_invocation_policy": "orion.protected-git-plumbing.v1",
        "capture_work_limits": {
            "local_bytes": MAX_EVIDENCE_CAPTURE_LOCAL_BYTES,
            "git_commands": MAX_EVIDENCE_CAPTURE_GIT_COMMANDS,
            "git_stdout_bytes": MAX_EVIDENCE_CAPTURE_GIT_STDOUT_BYTES,
            "git_stderr_bytes": MAX_EVIDENCE_CAPTURE_GIT_STDERR_BYTES,
            "git_output_overflow_probe_bytes_per_stream": 1,
            "elapsed_ns": MAX_EVIDENCE_CAPTURE_ELAPSED_NS,
            "path_components": MAX_EVIDENCE_CAPTURE_PATH_COMPONENTS,
            "tree_entries": MAX_EVIDENCE_CAPTURE_TREE_ENTRIES,
            "git_object_bytes": MAX_EVIDENCE_CAPTURE_GIT_OBJECT_BYTES,
            "git_objects": MAX_EVIDENCE_CAPTURE_GIT_OBJECTS,
            "git_control_bytes": MAX_EVIDENCE_GIT_CONTROL_BYTES,
            "executable_bytes": MAX_EVIDENCE_EXECUTABLE_BYTES,
        },
        "roots": [
            {
                "scheme": item.scheme,
                "configured_path": str(item.configured_path),
                "source_device": item.source_device,
                "source_inode": item.source_inode,
                "open_status": item.open_status.value if item.open_status else "OPENED",
                "git_source_device": item.git_source_device,
                "git_source_inode": item.git_source_inode,
                "git_open_status": (
                    item.git_open_status.value
                    if item.git_open_status
                    else "OPENED"
                ),
            }
            for item in opened_roots
        ],
    }
    return canonical_digest(payload, domain="orion.evidence-root-configuration.v1")


@dataclass(frozen=True)
class _GitCommandResult:
    returncode: int | None
    stdout: bytes
    stderr: bytes
    root_stable: bool
    note: str = ""
    stdout_limited: bool = False
    stderr_limited: bool = False
    combined_limited: bool = False
    timed_out: bool = False
    work_budget_exhausted: bool = False

    @property
    def output_limited(self) -> bool:
        return (
            self.stdout_limited
            or self.stderr_limited
            or self.combined_limited
        )

    @property
    def process_limited(self) -> bool:
        return self.output_limited or self.timed_out


@dataclass(frozen=True)
class _GitRevisionResolution:
    status: EvidenceStatus
    object_format: str = ""
    reference_oid: str = ""
    commit_oid: str = ""
    note: str = ""


_GIT_EXECUTABLE = shutil.which("git", path=os.defpath)
if _GIT_EXECUTABLE is not None:
    _GIT_EXECUTABLE = os.path.realpath(_GIT_EXECUTABLE)


@functools.lru_cache(maxsize=1)
def _git_supports_no_lazy_fetch() -> bool:
    """Whether the frozen Git binary accepts the global ``--no-lazy-fetch``.

    The guard exists since Git 2.45. On an older Git the option is instead
    enforced by rejecting promisor/partial-clone repositories in the layout
    check, so a capture can never lazily fetch either way.
    """

    if _GIT_EXECUTABLE is None:
        return False
    try:
        probe = subprocess.run(  # noqa: S603 - absolute host-frozen executable
            [_GIT_EXECUTABLE, "--no-lazy-fetch", "--version"],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return probe.returncode == 0
_GIT_FD_HELPER_EXECUTABLE = os.path.realpath(sys.executable)
_GIT_FD_EXEC_HELPER = """
import os
import sys

try:
    fd = int(sys.argv[1])
    expected_device = int(sys.argv[2])
    expected_inode = int(sys.argv[3])
    git_executable = sys.argv[4]
    info = os.fstat(fd)
    if (info.st_mode & 0o170000) != 0o040000:
        raise RuntimeError("Git administrative descriptor is not a directory")
    if (info.st_dev, info.st_ino) != (expected_device, expected_inode):
        raise RuntimeError("Git administrative descriptor identity changed")
    os.fchdir(fd)
    os.close(fd)
    os.execve(git_executable, sys.argv[4:], os.environ)
except BaseException:
    os._exit(126)
""".strip()


def _root_descriptor_matches(opened_root: _OpenedRoot) -> bool:
    if opened_root.file_descriptor is None:
        return False
    try:
        current = os.stat(opened_root.configured_path, follow_symlinks=False)
        opened = os.fstat(opened_root.file_descriptor)
    except OSError:
        return False
    return (current.st_dev, current.st_ino) == (opened.st_dev, opened.st_ino)


def _run_protected_git(
    opened_root: _OpenedRoot,
    *arguments: str,
    stdout_limit: int = MAX_EVIDENCE_TEXT_BYTES,
    stderr_limit: int = MAX_EVIDENCE_TEXT_BYTES,
    combined_limit: int | None = None,
    timeout_seconds: float = 30,
    work_state: _CaptureWorkState | None = None,
) -> _GitCommandResult:
    for value, field_name in (
        (stdout_limit, "stdout_limit"),
        (stderr_limit, "stderr_limit"),
    ):
        if type(value) is not int or value < 0:
            raise ValueError(f"{field_name} must be a nonnegative exact integer")
    if combined_limit is None:
        combined_limit = stdout_limit + stderr_limit
    if type(combined_limit) is not int or combined_limit < 0:
        raise ValueError("combined_limit must be a nonnegative exact integer")
    if not isinstance(timeout_seconds, (int, float)) or timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")
    if _GIT_EXECUTABLE is None:
        return _GitCommandResult(None, b"", b"", True, "trusted Git unavailable")
    if (
        opened_root.git_directory_fd is None
        or opened_root.git_source_device is None
        or opened_root.git_source_inode is None
    ):
        return _GitCommandResult(
            None,
            b"",
            b"",
            True,
            opened_root.git_note or "protected Git administrative root unavailable",
        )
    if not _root_descriptor_matches(opened_root):
        return _GitCommandResult(None, b"", b"", False, "Git root changed")
    if work_state is not None:
        if not work_state.reserve_git_command():
            return _GitCommandResult(
                None,
                b"",
                b"",
                True,
                "snapshot Git command or deadline work budget is exhausted",
                work_budget_exhausted=True,
            )
        timeout_seconds = min(timeout_seconds, work_state.remaining_seconds)
        if timeout_seconds <= 0:
            return _GitCommandResult(
                None,
                b"",
                b"",
                True,
                "snapshot Git deadline work budget is exhausted",
                work_budget_exhausted=True,
            )
    environment = {
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_SYSTEM": os.devnull,
        "GIT_LITERAL_PATHSPECS": "1",
        "GIT_NO_LAZY_FETCH": "1",
        "GIT_OPTIONAL_LOCKS": "0",
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_DIR": ".",
        "LANG": "C",
        "LC_ALL": "C",
        "PATH": os.defpath,
    }
    process: subprocess.Popen[bytes] | None = None
    selector: selectors.BaseSelector | None = None
    stdout = bytearray()
    stderr = bytearray()
    stdout_limited = False
    stderr_limited = False
    combined_limited = False
    timed_out = False
    work_budget_exhausted = False

    def terminate() -> None:
        if process is None or process.poll() is not None:
            return
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except (AttributeError, OSError):
            try:
                process.kill()
            except OSError:
                pass
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            try:
                process.kill()
            except OSError:
                pass
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass

    try:
        process = subprocess.Popen(  # noqa: S603 - absolute host-frozen executable
            [
                _GIT_FD_HELPER_EXECUTABLE,
                "-I",
                "-S",
                "-c",
                _GIT_FD_EXEC_HELPER,
                str(opened_root.git_directory_fd),
                str(opened_root.git_source_device),
                str(opened_root.git_source_inode),
                _GIT_EXECUTABLE,
                "--no-replace-objects",
                *(
                    ("--no-lazy-fetch",)
                    if _git_supports_no_lazy_fetch()
                    else ()
                ),
                "--no-optional-locks",
                "--git-dir=.",
                *arguments,
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
            close_fds=True,
            env=environment,
            pass_fds=(opened_root.git_directory_fd,),
            start_new_session=True,
        )
        if process.stdout is None or process.stderr is None:
            raise OSError("protected Git pipes were not created")
        selector = selectors.DefaultSelector()
        selector.register(process.stdout, selectors.EVENT_READ, "stdout")
        selector.register(process.stderr, selectors.EVENT_READ, "stderr")
        deadline = time.monotonic() + float(timeout_seconds)
        while selector.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                timed_out = True
                break
            events = selector.select(remaining)
            if not events:
                timed_out = True
                break
            for key, _ in events:
                target = stdout if key.data == "stdout" else stderr
                stream_limit = (
                    stdout_limit if key.data == "stdout" else stderr_limit
                )
                stream_room = max(0, stream_limit - len(target))
                combined_room = max(
                    0, combined_limit - len(stdout) - len(stderr)
                )
                retain_room = min(stream_room, combined_room)
                global_room = (
                    work_state.remaining_git_output(key.data)
                    if work_state is not None
                    else 65_536
                )
                chunk = os.read(
                    key.fd,
                    min(65_536, retain_room + 1, global_room + 1),
                )
                if not chunk:
                    selector.unregister(key.fileobj)
                    continue
                if work_state is not None and not work_state.charge_git_output(
                    key.data, len(chunk)
                ):
                    work_budget_exhausted = True
                retained = chunk[:retain_room]
                target.extend(retained)
                if len(chunk) > stream_room:
                    if key.data == "stdout":
                        stdout_limited = True
                    else:
                        stderr_limited = True
                if len(chunk) > combined_room:
                    combined_limited = True
                if len(chunk) > retain_room:
                    break
            if (
                stdout_limited
                or stderr_limited
                or combined_limited
                or work_budget_exhausted
            ):
                break

        if (
            timed_out
            or stdout_limited
            or stderr_limited
            or combined_limited
            or work_budget_exhausted
        ):
            if (
                timed_out
                and work_state is not None
                and work_state.deadline_exhausted
            ):
                work_state.exhausted_dimensions.add("elapsed_ns")
                work_budget_exhausted = True
            terminate()
            if work_budget_exhausted:
                note = "snapshot Git output work budget is exhausted"
            elif timed_out:
                note = "Git command exceeded the protected wall-clock deadline"
            else:
                note = "Git output exceeded the protected byte limit"
            return _GitCommandResult(
                None,
                bytes(stdout),
                bytes(stderr),
                _root_descriptor_matches(opened_root),
                note,
                stdout_limited=stdout_limited,
                stderr_limited=stderr_limited,
                combined_limited=combined_limited,
                timed_out=timed_out,
                work_budget_exhausted=work_budget_exhausted,
            )
        remaining = max(0.001, deadline - time.monotonic())
        try:
            returncode = process.wait(timeout=remaining)
        except subprocess.TimeoutExpired:
            timed_out = True
            if work_state is not None and work_state.deadline_exhausted:
                work_state.exhausted_dimensions.add("elapsed_ns")
                work_budget_exhausted = True
            terminate()
            return _GitCommandResult(
                None,
                bytes(stdout),
                bytes(stderr),
                _root_descriptor_matches(opened_root),
                "Git command exceeded the protected wall-clock deadline",
                timed_out=True,
                work_budget_exhausted=work_budget_exhausted,
            )
    except (OSError, subprocess.SubprocessError) as error:
        terminate()
        return _GitCommandResult(
            None,
            bytes(stdout),
            bytes(stderr),
            _root_descriptor_matches(opened_root),
            str(error),
        )
    finally:
        if selector is not None:
            selector.close()
        if process is not None:
            if process.poll() is None:
                terminate()
            if process.stdout is not None:
                process.stdout.close()
            if process.stderr is not None:
                process.stderr.close()
    return _GitCommandResult(
        returncode,
        bytes(stdout),
        bytes(stderr),
        _root_descriptor_matches(opened_root),
    )


def _git_oid_length(object_format: str) -> int:
    if object_format == "sha1":
        return 40
    if object_format == "sha256":
        return 64
    return 0


def _is_full_git_oid(value: str, object_format: str) -> bool:
    return len(value) == _git_oid_length(object_format) and all(
        character in "0123456789abcdef" for character in value
    )


def _resolve_git_revision(
    opened_root: _OpenedRoot,
    revision: str,
    work_state: _CaptureWorkState,
) -> _GitRevisionResolution:
    """Resolve one mutable Git name once, then peel only its frozen object OID."""

    format_result = _run_protected_git(
        opened_root,
        "rev-parse",
        "--show-object-format=storage",
        work_state=work_state,
    )
    if not format_result.root_stable:
        return _GitRevisionResolution(EvidenceStatus.CHANGED_DURING_CAPTURE)
    if format_result.work_budget_exhausted:
        return _GitRevisionResolution(
            EvidenceStatus.WORK_BUDGET_EXHAUSTED,
            note=format_result.note,
        )
    if format_result.process_limited:
        return _GitRevisionResolution(
            EvidenceStatus.UNREADABLE_ARTIFACT,
            note=format_result.note,
        )
    if format_result.returncode != 0:
        return _GitRevisionResolution(
            EvidenceStatus.NOT_A_REPOSITORY,
            note=format_result.stderr.decode("utf-8", errors="replace"),
        )
    try:
        object_format = format_result.stdout.decode(
            "ascii", errors="strict"
        ).strip()
    except UnicodeDecodeError:
        return _GitRevisionResolution(
            EvidenceStatus.UNREADABLE_ARTIFACT,
            note="Git object storage format output is not ASCII",
        )
    if object_format not in {"sha1", "sha256"}:
        return _GitRevisionResolution(
            EvidenceStatus.UNREADABLE_ARTIFACT,
            note="unsupported Git object storage format",
        )

    if _is_full_git_oid(revision, object_format):
        reference_oid = revision
    elif revision.startswith(("refs/heads/", "refs/tags/")):
        check_ref = _run_protected_git(
            opened_root,
            "check-ref-format",
            revision,
            work_state=work_state,
        )
        if not check_ref.root_stable:
            return _GitRevisionResolution(EvidenceStatus.CHANGED_DURING_CAPTURE)
        if check_ref.work_budget_exhausted:
            return _GitRevisionResolution(
                EvidenceStatus.WORK_BUDGET_EXHAUSTED,
                object_format=object_format,
                note=check_ref.note,
            )
        if check_ref.process_limited:
            return _GitRevisionResolution(
                EvidenceStatus.UNREADABLE_ARTIFACT,
                object_format=object_format,
                note=check_ref.note,
            )
        if check_ref.returncode != 0:
            return _GitRevisionResolution(EvidenceStatus.MALFORMED_REF)
        resolve_ref = _run_protected_git(
            opened_root,
            "show-ref",
            "--verify",
            "--hash",
            "--",
            revision,
            work_state=work_state,
        )
        if not resolve_ref.root_stable:
            return _GitRevisionResolution(EvidenceStatus.CHANGED_DURING_CAPTURE)
        if resolve_ref.work_budget_exhausted:
            return _GitRevisionResolution(
                EvidenceStatus.WORK_BUDGET_EXHAUSTED,
                object_format=object_format,
                note=resolve_ref.note,
            )
        if resolve_ref.process_limited:
            return _GitRevisionResolution(
                EvidenceStatus.UNREADABLE_ARTIFACT,
                object_format=object_format,
                note=resolve_ref.note,
            )
        try:
            candidate = resolve_ref.stdout.decode(
                "ascii", errors="strict"
            ).strip()
        except UnicodeDecodeError:
            return _GitRevisionResolution(
                EvidenceStatus.UNREADABLE_ARTIFACT,
                object_format=object_format,
                note="Git reference resolution output is not ASCII",
            )
        if resolve_ref.returncode != 0 or not _is_full_git_oid(
            candidate, object_format
        ):
            return _GitRevisionResolution(EvidenceStatus.COMMIT_NOT_FOUND)
        reference_oid = candidate
    else:
        return _GitRevisionResolution(
            EvidenceStatus.MALFORMED_REF,
            note="protected Git revision must be a full OID or canonical ref",
        )

    return _peel_verified_git_reference(
        opened_root,
        object_format=object_format,
        reference_oid=reference_oid,
        work_state=work_state,
    )


def _git_object_oid(object_format: str, object_type: str, payload: bytes) -> str:
    preimage = (
        object_type.encode("ascii")
        + b" "
        + str(len(payload)).encode("ascii")
        + b"\x00"
        + payload
    )
    if object_format == "sha1":
        return hashlib.sha1(preimage, usedforsecurity=False).hexdigest()
    if object_format == "sha256":
        return hashlib.sha256(preimage).hexdigest()
    raise ValueError("unsupported Git object format")


def _read_verified_git_object(
    opened_root: _OpenedRoot,
    *,
    object_format: str,
    object_type: str,
    oid: str,
    limit: int,
    work_state: _CaptureWorkState,
) -> tuple[EvidenceStatus, bytes, str]:
    if (
        opened_root.git_source_device is None
        or opened_root.git_source_inode is None
    ):
        return (
            EvidenceStatus.UNREADABLE_ARTIFACT,
            b"",
            "Git administrative root identity is unavailable",
        )
    object_key = (
        opened_root.git_source_device,
        opened_root.git_source_inode,
        object_format,
        object_type,
        oid,
    )
    cached = work_state.cached_git_object(object_key)
    if cached is not None:
        return EvidenceStatus.RESOLVED, cached, ""
    size_result = _run_protected_git(
        opened_root,
        "cat-file",
        "-s",
        oid,
        work_state=work_state,
    )
    if not size_result.root_stable:
        return EvidenceStatus.CHANGED_DURING_CAPTURE, b"", "Git root changed"
    if size_result.work_budget_exhausted:
        return EvidenceStatus.WORK_BUDGET_EXHAUSTED, b"", size_result.note
    if size_result.output_limited or size_result.timed_out:
        return EvidenceStatus.UNREADABLE_ARTIFACT, b"", size_result.note
    try:
        declared_size = int(size_result.stdout.decode("ascii", errors="strict").strip())
    except ValueError:
        declared_size = -1
    if size_result.returncode != 0 or declared_size < 0:
        return EvidenceStatus.UNREADABLE_ARTIFACT, b"", "Git object is unavailable"
    if declared_size > limit:
        return EvidenceStatus.TOO_LARGE, b"", "Git object exceeds capture limit"
    if not work_state.reserve_git_object(object_key, declared_size):
        return (
            EvidenceStatus.WORK_BUDGET_EXHAUSTED,
            b"",
            "snapshot Git object work budget is exhausted",
        )
    content_result = _run_protected_git(
        opened_root,
        "cat-file",
        object_type,
        oid,
        stdout_limit=limit + 1,
        combined_limit=limit + 1 + MAX_EVIDENCE_TEXT_BYTES,
        work_state=work_state,
    )
    if not content_result.root_stable:
        return EvidenceStatus.CHANGED_DURING_CAPTURE, b"", "Git root changed"
    if content_result.work_budget_exhausted:
        return EvidenceStatus.WORK_BUDGET_EXHAUSTED, b"", content_result.note
    if content_result.stdout_limited or content_result.combined_limited:
        return EvidenceStatus.TOO_LARGE, b"", content_result.note
    if content_result.stderr_limited or content_result.timed_out:
        return EvidenceStatus.UNREADABLE_ARTIFACT, b"", content_result.note
    if content_result.returncode != 0:
        return EvidenceStatus.UNREADABLE_ARTIFACT, b"", "Git object cannot be read"
    payload = bytes(content_result.stdout)
    if len(payload) > limit:
        return EvidenceStatus.TOO_LARGE, b"", "Git object exceeds capture limit"
    if len(payload) != declared_size:
        return (
            EvidenceStatus.CHANGED_DURING_CAPTURE,
            payload,
            "Git object size changed during capture",
        )
    if _git_object_oid(object_format, object_type, payload) != oid:
        return (
            EvidenceStatus.GIT_OBJECT_MISMATCH,
            payload,
            "Git object bytes do not match their storage OID",
        )
    work_state.cache_git_object(object_key, payload)
    return EvidenceStatus.RESOLVED, payload, ""


def _peel_verified_git_reference(
    opened_root: _OpenedRoot,
    *,
    object_format: str,
    reference_oid: str,
    work_state: _CaptureWorkState,
) -> _GitRevisionResolution:
    current_oid = reference_oid
    expected_type: str | None = None
    seen: set[str] = set()
    for _ in range(32):
        if current_oid in seen:
            return _GitRevisionResolution(
                EvidenceStatus.GIT_OBJECT_MISMATCH,
                object_format=object_format,
                reference_oid=reference_oid,
                note="Git tag chain contains a cycle",
            )
        seen.add(current_oid)
        type_result = _run_protected_git(
            opened_root,
            "cat-file",
            "-t",
            current_oid,
            work_state=work_state,
        )
        if not type_result.root_stable:
            return _GitRevisionResolution(
                EvidenceStatus.CHANGED_DURING_CAPTURE,
                object_format=object_format,
                reference_oid=reference_oid,
            )
        if type_result.work_budget_exhausted:
            return _GitRevisionResolution(
                EvidenceStatus.WORK_BUDGET_EXHAUSTED,
                object_format=object_format,
                reference_oid=reference_oid,
                note=type_result.note,
            )
        if type_result.process_limited:
            return _GitRevisionResolution(
                EvidenceStatus.UNREADABLE_ARTIFACT,
                object_format=object_format,
                reference_oid=reference_oid,
                note=type_result.note,
            )
        if type_result.returncode != 0:
            return _GitRevisionResolution(
                EvidenceStatus.COMMIT_NOT_FOUND,
                object_format=object_format,
                reference_oid=reference_oid,
            )
        try:
            object_type = type_result.stdout.decode(
                "ascii", errors="strict"
            ).strip()
        except UnicodeDecodeError:
            return _GitRevisionResolution(
                EvidenceStatus.UNREADABLE_ARTIFACT,
                object_format=object_format,
                reference_oid=reference_oid,
                note="Git object type output is not ASCII",
            )
        if expected_type is not None and object_type != expected_type:
            return _GitRevisionResolution(
                EvidenceStatus.GIT_OBJECT_MISMATCH,
                object_format=object_format,
                reference_oid=reference_oid,
                note="annotated tag declared target type does not match object",
            )
        if object_type == "commit":
            return _GitRevisionResolution(
                EvidenceStatus.RESOLVED,
                object_format=object_format,
                reference_oid=reference_oid,
                commit_oid=current_oid,
            )
        if object_type != "tag":
            return _GitRevisionResolution(
                EvidenceStatus.COMMIT_NOT_FOUND,
                object_format=object_format,
                reference_oid=reference_oid,
                note="frozen Git coordinate does not peel to a commit",
            )
        status, tag_bytes, note = _read_verified_git_object(
            opened_root,
            object_format=object_format,
            object_type="tag",
            oid=current_oid,
            limit=MAX_EVIDENCE_RECORD_BYTES,
            work_state=work_state,
        )
        if status is not EvidenceStatus.RESOLVED:
            return _GitRevisionResolution(
                status,
                object_format=object_format,
                reference_oid=reference_oid,
                note=note,
            )
        if b"\n\n" not in tag_bytes:
            return _GitRevisionResolution(
                EvidenceStatus.GIT_OBJECT_MISMATCH,
                object_format=object_format,
                reference_oid=reference_oid,
                note="annotated tag headers are malformed",
            )
        header = tag_bytes.split(b"\n\n", 1)[0]
        header_lines = header.split(b"\n")
        if (
            len(header_lines) < 3
            or not header_lines[0].startswith(b"object ")
            or not header_lines[1].startswith(b"type ")
            or not header_lines[2].startswith(b"tag ")
            or not header_lines[2].removeprefix(b"tag ")
            or b"\x00" in header
        ):
            return _GitRevisionResolution(
                EvidenceStatus.GIT_OBJECT_MISMATCH,
                object_format=object_format,
                reference_oid=reference_oid,
                note="annotated tag headers are not in canonical order",
            )
        target_type = header_lines[1].removeprefix(b"type ")
        try:
            target_oid = header_lines[0].removeprefix(b"object ").decode(
                "ascii", errors="strict"
            )
        except UnicodeDecodeError:
            target_oid = ""
        if target_type not in {b"commit", b"tag"} or not _is_full_git_oid(
            target_oid, object_format
        ):
            return _GitRevisionResolution(
                EvidenceStatus.GIT_OBJECT_MISMATCH,
                object_format=object_format,
                reference_oid=reference_oid,
                note="annotated tag target is malformed or not commit-like",
            )
        expected_type = target_type.decode("ascii")
        current_oid = target_oid
    return _GitRevisionResolution(
        EvidenceStatus.TOO_LARGE,
        object_format=object_format,
        reference_oid=reference_oid,
        note="annotated tag chain exceeds the depth cap",
    )


def _find_verified_tree_entry(
    payload: bytes,
    object_format: str,
    target_name: bytes,
    work_state: _CaptureWorkState,
) -> tuple[EvidenceStatus, tuple[str, str] | None]:
    raw_oid_length = _git_oid_length(object_format) // 2
    if raw_oid_length <= 0:
        return EvidenceStatus.GIT_OBJECT_MISMATCH, None
    cursor = 0
    entry_count = 0
    previous_key: bytes | None = None
    match: tuple[str, str] | None = None
    while cursor < len(payload):
        space = payload.find(b" ", cursor)
        nul = payload.find(b"\x00", space + 1)
        if (
            space <= cursor
            or nul <= space + 1
            or nul + 1 + raw_oid_length > len(payload)
        ):
            return EvidenceStatus.GIT_OBJECT_MISMATCH, None
        try:
            mode = payload[cursor:space].decode("ascii", errors="strict")
        except UnicodeDecodeError:
            return EvidenceStatus.GIT_OBJECT_MISMATCH, None
        name = payload[space + 1 : nul]
        raw_oid = payload[nul + 1 : nul + 1 + raw_oid_length]
        if (
            mode not in {"40000", "100644", "100755", "120000", "160000"}
            or not name
            or name in {b".", b"..", b".git"}
            or b"/" in name
            or not any(raw_oid)
        ):
            return EvidenceStatus.GIT_OBJECT_MISMATCH, None
        entry_count += 1
        if not work_state.charge_tree_entry():
            return EvidenceStatus.WORK_BUDGET_EXHAUSTED, None
        if entry_count > MAX_EVIDENCE_GIT_TREE_ENTRIES:
            return EvidenceStatus.TOO_LARGE, None
        sort_key = name + (b"/" if mode == "40000" else b"\x00")
        if previous_key is not None and sort_key <= previous_key:
            return EvidenceStatus.GIT_OBJECT_MISMATCH, None
        previous_key = sort_key
        if name == target_name:
            if match is not None:
                return EvidenceStatus.GIT_OBJECT_MISMATCH, None
            match = (mode, raw_oid.hex())
        cursor = nul + 1 + raw_oid_length
    if match is None:
        return EvidenceStatus.PATH_NOT_IN_COMMIT, None
    return EvidenceStatus.RESOLVED, match


def _commit_tree_oid(payload: bytes, object_format: str) -> str | None:
    if b"\n\n" not in payload:
        return None
    header = payload.split(b"\n\n", 1)[0]
    if b"\x00" in header:
        return None
    lines = header.split(b"\n")
    if not lines or not lines[0].startswith(b"tree "):
        return None
    if any(line.startswith(b"tree ") for line in lines[1:]):
        return None
    try:
        tree_oid = lines[0].removeprefix(b"tree ").decode(
            "ascii", errors="strict"
        )
    except UnicodeDecodeError:
        return None
    return tree_oid if _is_full_git_oid(tree_oid, object_format) else None


def _capture_git_source(
    opened_root: _OpenedRoot,
    *,
    source: HostEvidenceSource,
    resolution: _GitRevisionResolution,
    work_state: _CaptureWorkState,
) -> _CaptureResult:
    declaration = f"git:{source.git_revision}"
    if resolution.status is not EvidenceStatus.RESOLVED:
        return _CaptureResult(
            resolution.status,
            "git",
            source.root_scheme,
            source.relative_path,
            declared_digest=declaration,
            resolved_source_revision=resolution.commit_oid,
            source_object_format=resolution.object_format,
            source_reference_oid=resolution.reference_oid,
            note=resolution.note,
        )
    parts = _safe_relative_parts(source.relative_path)
    if parts is None:
        return _CaptureResult(
            EvidenceStatus.ESCAPES_ROOT,
            "git",
            source.root_scheme,
            source.relative_path,
            declared_digest=declaration,
            resolved_source_revision=resolution.commit_oid,
            source_object_format=resolution.object_format,
            source_reference_oid=resolution.reference_oid,
            note="protected Git path must be an unambiguous relative path",
        )
    if not work_state.charge_path_components(len(parts)):
        return _CaptureResult(
            EvidenceStatus.WORK_BUDGET_EXHAUSTED,
            "git",
            source.root_scheme,
            source.relative_path,
            declared_digest=declaration,
            resolved_source_revision=resolution.commit_oid,
            source_object_format=resolution.object_format,
            source_reference_oid=resolution.reference_oid,
            note="snapshot path-component work budget is exhausted",
        )
    commit_status, commit_bytes, note = _read_verified_git_object(
        opened_root,
        object_format=resolution.object_format,
        object_type="commit",
        oid=resolution.commit_oid,
        limit=MAX_EVIDENCE_RECORD_BYTES,
        work_state=work_state,
    )
    if commit_status is not EvidenceStatus.RESOLVED:
        return _CaptureResult(
            commit_status,
            "git",
            source.root_scheme,
            source.relative_path,
            declared_digest=declaration,
            resolved_source_revision=resolution.commit_oid,
            source_object_format=resolution.object_format,
            source_reference_oid=resolution.reference_oid,
            note=note,
        )
    tree_oid = _commit_tree_oid(commit_bytes, resolution.object_format)
    if tree_oid is None:
        return _CaptureResult(
            EvidenceStatus.GIT_OBJECT_MISMATCH,
            "git",
            source.root_scheme,
            source.relative_path,
            declared_digest=declaration,
            resolved_source_revision=resolution.commit_oid,
            source_object_format=resolution.object_format,
            source_reference_oid=resolution.reference_oid,
            note="Git commit does not begin with one canonical tree header",
        )

    final_mode = ""
    blob_oid = ""
    current_tree_oid = tree_oid
    encoded_parts = tuple(part.encode("utf-8") for part in parts)
    for index, component in enumerate(encoded_parts):
        tree_status, tree_bytes, note = _read_verified_git_object(
            opened_root,
            object_format=resolution.object_format,
            object_type="tree",
            oid=current_tree_oid,
            limit=MAX_EVIDENCE_RECORD_BYTES,
            work_state=work_state,
        )
        if tree_status is not EvidenceStatus.RESOLVED:
            return _CaptureResult(
                tree_status,
                "git",
                source.root_scheme,
                source.relative_path,
                declared_digest=declaration,
                resolved_source_revision=resolution.commit_oid,
                source_object_format=resolution.object_format,
                source_reference_oid=resolution.reference_oid,
                note=note,
            )
        entry_status, entry = _find_verified_tree_entry(
            tree_bytes,
            resolution.object_format,
            component,
            work_state,
        )
        if entry_status is not EvidenceStatus.RESOLVED or entry is None:
            return _CaptureResult(
                entry_status,
                "git",
                source.root_scheme,
                source.relative_path,
                declared_digest=declaration,
                resolved_source_revision=resolution.commit_oid,
                source_object_format=resolution.object_format,
                source_reference_oid=resolution.reference_oid,
                note=(
                    "Git tree object exceeds the entry cap"
                    if entry_status is EvidenceStatus.TOO_LARGE
                    else "Git tree object is malformed or lacks the exact component"
                ),
            )
        mode, child_oid = entry
        if index < len(encoded_parts) - 1:
            if mode != "40000":
                return _CaptureResult(
                    EvidenceStatus.PATH_NOT_IN_COMMIT,
                    "git",
                    source.root_scheme,
                    source.relative_path,
                    declared_digest=declaration,
                    resolved_source_revision=resolution.commit_oid,
                    source_object_format=resolution.object_format,
                    source_reference_oid=resolution.reference_oid,
                    note="intermediate Git path component is not a tree",
                )
            current_tree_oid = child_oid
        else:
            final_mode = mode
            blob_oid = child_oid

    if final_mode not in {"100644", "100755"}:
        return _CaptureResult(
            EvidenceStatus.NON_REGULAR_FILE,
            "git",
            source.root_scheme,
            source.relative_path,
            declared_digest=declaration,
            resolved_source_revision=resolution.commit_oid,
            source_object_format=resolution.object_format,
            source_reference_oid=resolution.reference_oid,
            source_blob_oid=blob_oid,
            source_tree_entry_mode=final_mode,
            note="protected Git evidence must be a regular-file tree entry",
        )
    blob_status, blob_bytes, note = _read_verified_git_object(
        opened_root,
        object_format=resolution.object_format,
        object_type="blob",
        oid=blob_oid,
        limit=MAX_EVIDENCE_RECORD_BYTES,
        work_state=work_state,
    )
    return _CaptureResult(
        blob_status,
        "git",
        source.root_scheme,
        source.relative_path,
        declared_digest=declaration,
        resolved_source_revision=resolution.commit_oid,
        source_object_format=resolution.object_format,
        source_reference_oid=resolution.reference_oid,
        source_blob_oid=blob_oid,
        source_tree_entry_mode=final_mode,
        content_bytes=blob_bytes,
        content_available=(
            blob_status
            in {EvidenceStatus.RESOLVED, EvidenceStatus.GIT_OBJECT_MISMATCH}
            or bool(blob_bytes)
        ),
        note=note,
    )


def capture_host_evidence_snapshot(
    requested_refs: tuple[str, ...],
    *,
    roots: Mapping[str, Path],
    manifest: HostEvidenceManifest,
    captured_at_authority_revision: str,
    captured_at_support_revision: str,
) -> HostEvidenceSnapshot:
    """Freeze host-registered evidence without appraising or authorizing it."""

    _require_exact_tuple(requested_refs, "requested_refs")
    if len(requested_refs) > MAX_EVIDENCE_SOURCE_COUNT:
        raise ValueError("requested evidence exceeds the source count cap")
    for ref in requested_refs:
        _require_exact_text(ref, "requested evidence ref")
        if len(ref.encode("utf-8")) > MAX_EVIDENCE_TEXT_BYTES:
            raise ValueError("requested evidence ref exceeds the text byte cap")
    if len(set(requested_refs)) != len(requested_refs):
        raise ValueError("requested evidence refs must be unique")
    if type(manifest) is not HostEvidenceManifest:
        raise ValueError("manifest must be an exact HostEvidenceManifest")
    _require_sha256(
        captured_at_authority_revision, "captured_at_authority_revision"
    )
    _require_sha256(
        captured_at_support_revision, "captured_at_support_revision"
    )
    capture_refs = sorted(
        set(requested_refs)
        | {binding.evidence_ref for binding in manifest.bindings}
    )
    if len(capture_refs) > MAX_EVIDENCE_SNAPSHOT_RECORDS:
        raise ValueError("capture exceeds the evidence snapshot record count cap")

    work_state = _CaptureWorkState(
        MAX_EVIDENCE_CAPTURE_LOCAL_BYTES,
        MAX_EVIDENCE_CAPTURE_GIT_COMMANDS,
        MAX_EVIDENCE_CAPTURE_GIT_STDOUT_BYTES,
        MAX_EVIDENCE_CAPTURE_GIT_STDERR_BYTES,
        MAX_EVIDENCE_CAPTURE_ELAPSED_NS,
        MAX_EVIDENCE_CAPTURE_PATH_COMPONENTS,
        MAX_EVIDENCE_CAPTURE_TREE_ENTRIES,
        MAX_EVIDENCE_CAPTURE_GIT_OBJECT_BYTES,
        MAX_EVIDENCE_CAPTURE_GIT_OBJECTS,
    )
    opened_roots = _open_roots(roots)
    try:
        root_hash = _root_configuration_hash(opened_roots)
        work_state.check_deadline()
        root_by_scheme = {item.scheme: item for item in opened_roots}
        bindings_by_ref: dict[str, list[EvidenceRoleBinding]] = {}
        for binding in manifest.bindings:
            bindings_by_ref.setdefault(binding.evidence_ref, []).append(binding)
        sources_by_ref = {source.source_id: source for source in manifest.sources}
        git_revision_cache: dict[
            tuple[str, str], _GitRevisionResolution
        ] = {}
        records: list[HostEvidenceRecord] = []
        captured_bytes = 0
        for ordinal, ref in enumerate(capture_refs):
            role_bindings = tuple(
                sorted(bindings_by_ref.get(ref, ()), key=lambda item: item.binding_id)
            )
            if not role_bindings:
                result = _CaptureResult(
                    EvidenceStatus.ROLE_UNMAPPED,
                    "unmapped",
                    "unmapped",
                    ref,
                    note="no host role/obligation registration exists for this ref",
                )
            else:
                source = sources_by_ref[ref]
                opened_root = root_by_scheme.get(source.root_scheme)
                declaration = (
                    source.expected_content_sha256
                    if source.backend_type == "file"
                    else f"git:{source.git_revision}"
                )
                if opened_root is None:
                    result = _CaptureResult(
                        EvidenceStatus.UNKNOWN_SCHEME,
                        source.backend_type,
                        source.root_scheme,
                        source.relative_path,
                        declared_digest=declaration,
                        note=f"no root registered for scheme '{source.root_scheme}'",
                    )
                elif opened_root.file_descriptor is None:
                    result = _CaptureResult(
                        opened_root.open_status
                        or EvidenceStatus.UNREADABLE_ARTIFACT,
                        source.backend_type,
                        source.root_scheme,
                        source.relative_path,
                        declared_digest=declaration,
                        note=opened_root.note,
                    )
                elif (
                    source.backend_type == "git"
                    and opened_root.git_directory_fd is None
                ):
                    result = _CaptureResult(
                        opened_root.git_open_status
                        or EvidenceStatus.NOT_A_REPOSITORY,
                        source.backend_type,
                        source.root_scheme,
                        source.relative_path,
                        declared_digest=declaration,
                        note=opened_root.git_note,
                    )
                elif not work_state.check_deadline():
                    result = _CaptureResult(
                        EvidenceStatus.WORK_BUDGET_EXHAUSTED,
                        source.backend_type,
                        source.root_scheme,
                        source.relative_path,
                        declared_digest=declaration,
                        note="snapshot elapsed-time work budget is exhausted",
                    )
                elif source.backend_type == "git":
                    cache_key = (source.root_scheme, source.git_revision)
                    resolution = git_revision_cache.get(cache_key)
                    if resolution is None:
                        resolution = _resolve_git_revision(
                            opened_root,
                            source.git_revision,
                            work_state,
                        )
                        git_revision_cache[cache_key] = resolution
                    result = _capture_git_source(
                        opened_root,
                        source=source,
                        resolution=resolution,
                        work_state=work_state,
                    )
                else:
                    result = _capture_local_file(
                        opened_root,
                        location=source.relative_path,
                        declared_digest=source.expected_content_sha256,
                        work_state=work_state,
                    )
            result_bytes = len(result.content_bytes) if result.content_available else 0
            if (
                result.content_available
                and captured_bytes + result_bytes > MAX_EVIDENCE_SNAPSHOT_BYTES
            ):
                result = _CaptureResult(
                    EvidenceStatus.TOO_LARGE,
                    result.backend_type,
                    result.scheme,
                    result.relative_path,
                    declared_digest=result.declared_digest,
                    resolved_source_revision=result.resolved_source_revision,
                    source_object_format=result.source_object_format,
                    source_reference_oid=result.source_reference_oid,
                    source_blob_oid=result.source_blob_oid,
                    source_tree_entry_mode=result.source_tree_entry_mode,
                    note=f"snapshot exceeds {MAX_EVIDENCE_SNAPSHOT_BYTES} bytes",
                )
            else:
                captured_bytes += result_bytes
            records.append(
                HostEvidenceRecord(
                    capture_ordinal=ordinal,
                    ref=ref,
                    status=result.status,
                    backend_type=result.backend_type,
                    scheme=result.scheme,
                    relative_path=result.relative_path,
                    declared_digest=result.declared_digest,
                    resolved_source_revision=result.resolved_source_revision,
                    source_object_format=result.source_object_format,
                    source_reference_oid=result.source_reference_oid,
                    source_blob_oid=result.source_blob_oid,
                    source_tree_entry_mode=result.source_tree_entry_mode,
                    root_configuration_hash=root_hash,
                    role_bindings=role_bindings,
                    content_bytes=result.content_bytes,
                    content_available=result.content_available,
                    source_device=result.source_device,
                    source_inode=result.source_inode,
                    source_size=result.source_size,
                    source_mtime_ns=result.source_mtime_ns,
                    source_ctime_ns=result.source_ctime_ns,
                    note=_bounded_diagnostic_text(result.note),
                )
            )
        return HostEvidenceSnapshot(
            root_configuration_hash=root_hash,
            manifest_hash=manifest.manifest_hash,
            captured_at_authority_revision=captured_at_authority_revision,
            captured_at_support_revision=captured_at_support_revision,
            required_obligation_ids=manifest.required_obligation_ids,
            records=tuple(records),
            capture_work_usage=work_state.usage(),
            capture_work_exhausted_dimensions=tuple(
                work_state.exhausted_dimensions
            ),
        )
    finally:
        for opened_root in opened_roots:
            if opened_root.git_directory_fd is not None:
                os.close(opened_root.git_directory_fd)
            if opened_root.file_descriptor is not None:
                os.close(opened_root.file_descriptor)


class EvidenceStatus(str, Enum):
    """Why an evidence reference did or did not bind to real material."""

    RESOLVED = "RESOLVED"
    MALFORMED_REF = "MALFORMED_REF"
    UNKNOWN_SCHEME = "UNKNOWN_SCHEME"
    ESCAPES_ROOT = "ESCAPES_ROOT"
    MISSING_ARTIFACT = "MISSING_ARTIFACT"
    UNREADABLE_ARTIFACT = "UNREADABLE_ARTIFACT"
    DIGEST_MISMATCH = "DIGEST_MISMATCH"
    DIGEST_ABSENT = "DIGEST_ABSENT"
    DIGEST_TOO_SHORT = "DIGEST_TOO_SHORT"
    COMMIT_NOT_FOUND = "COMMIT_NOT_FOUND"
    PATH_NOT_IN_COMMIT = "PATH_NOT_IN_COMMIT"
    NOT_A_REPOSITORY = "NOT_A_REPOSITORY"
    UNSUPPORTED_GIT_LAYOUT = "UNSUPPORTED_GIT_LAYOUT"
    GIT_OBJECT_MISMATCH = "GIT_OBJECT_MISMATCH"
    ROLE_UNMAPPED = "ROLE_UNMAPPED"
    CAPABILITY_UNAVAILABLE = "CAPABILITY_UNAVAILABLE"
    SYMLINK_DISALLOWED = "SYMLINK_DISALLOWED"
    NON_REGULAR_FILE = "NON_REGULAR_FILE"
    TOO_LARGE = "TOO_LARGE"
    CHANGED_DURING_CAPTURE = "CHANGED_DURING_CAPTURE"
    WORK_BUDGET_EXHAUSTED = "WORK_BUDGET_EXHAUSTED"


@dataclass(frozen=True)
class EvidenceResolution:
    """The outcome of binding one `scheme:path@digest` reference to a file."""

    ref: str
    status: EvidenceStatus
    scheme: str = ""
    relative_path: str = ""
    declared_digest: str = ""
    actual_digest: str = ""
    note: str = ""
    content: str = ""

    @property
    def resolved(self) -> bool:
        return self.status is EvidenceStatus.RESOLVED


def artifact_digest(path: Path) -> str:
    """Return the sha256 hex digest of a file's bytes."""

    return hashlib.sha256(path.read_bytes()).hexdigest()


@lru_cache(maxsize=4096)
def _blob_at_commit_cached(root: str, revision: str, relative_path: str) -> bytes | None:
    """Cache-backed read of a pinned blob.

    Caching is sound here and only here: the content of a path at a named
    revision cannot change, so a repeat lookup must return the same bytes. The
    working-tree path deliberately has no cache, because a file on disk can and
    does change under a running process.
    """

    return _read_blob(Path(root), revision, relative_path)


def _blob_at_commit(root: Path, revision: str, relative_path: str) -> bytes | None:
    return _blob_at_commit_cached(str(root), revision, relative_path)


def _read_blob(root: Path, revision: str, relative_path: str) -> bytes | None:
    """Return the bytes a path had at a revision, or None if it cannot be read."""

    try:
        completed = subprocess.run(  # noqa: S603 - fixed argv, no shell
            ["git", "-C", str(root), "cat-file", "blob", f"{revision}:{relative_path}"],
            capture_output=True,
            check=False,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout


def _git_succeeds(root: Path, *arguments: str) -> bool:
    try:
        completed = subprocess.run(  # noqa: S603 - fixed argv, no shell
            ["git", "-C", str(root), *arguments],
            capture_output=True,
            check=False,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return completed.returncode == 0


def _is_repository(root: Path) -> bool:
    return _git_succeeds(root, "rev-parse", "--git-dir")


def _revision_exists(root: Path, revision: str) -> bool:
    return _git_succeeds(root, "rev-parse", "--verify", "--quiet", f"{revision}^{{commit}}")


def _resolve_at_commit(
    ref: str, root: Path, scheme: str, location: str, revision: str
) -> EvidenceResolution:
    """Bind a reference to the content a path had at a named revision.

    A commit anchor is a different claim from a content anchor: it pins what
    the citation said when it was made, which stays checkable after the working
    tree moves on. It is still content-addressed — the digest reported is the
    sha256 of the blob at that revision, not of whatever is on disk now.
    """

    if not _is_repository(root):
        return EvidenceResolution(
            ref,
            EvidenceStatus.NOT_A_REPOSITORY,
            scheme=scheme,
            relative_path=location,
            declared_digest=revision,
            note="commit-anchored evidence requires a git repository root",
        )
    if not _revision_exists(root, revision):
        return EvidenceResolution(
            ref,
            EvidenceStatus.COMMIT_NOT_FOUND,
            scheme=scheme,
            relative_path=location,
            declared_digest=revision,
            note="the cited revision does not exist in this repository",
        )
    blob = _blob_at_commit(root, revision, location)
    if blob is None:
        return EvidenceResolution(
            ref,
            EvidenceStatus.PATH_NOT_IN_COMMIT,
            scheme=scheme,
            relative_path=location,
            declared_digest=revision,
            note="the cited path did not exist at the cited revision",
        )
    return EvidenceResolution(
        ref,
        EvidenceStatus.RESOLVED,
        scheme=scheme,
        relative_path=location,
        declared_digest=revision,
        actual_digest=hashlib.sha256(blob).hexdigest(),
        content=blob.decode("utf-8", errors="replace"),
    )


def _parse(ref: str) -> tuple[str, str, str] | None:
    if _REF_SEPARATOR not in ref:
        return None
    scheme, _, remainder = ref.partition(_REF_SEPARATOR)
    if not scheme.strip() or not remainder.strip():
        return None
    location, separator, digest = remainder.partition(_HASH_SEPARATOR)
    if separator and not digest.strip():
        return None
    if not location.strip():
        return None
    return scheme.strip(), location.strip(), digest.strip()


def resolve_evidence_ref(
    ref: str,
    roots: Mapping[str, Path],
    *,
    require_digest: bool = True,
) -> EvidenceResolution:
    """Bind one evidence reference to a real artifact under a declared root.

    An answer may only claim evidence it can point at. A reference resolves
    when its scheme is registered, its path stays inside that root, the file
    exists, and (under `require_digest`) the declared digest prefix matches
    the artifact's actual sha256. Anything else is a typed non-resolution
    rather than a silent pass: fabricated citations must fail closed.
    """

    parsed = _parse(ref)
    if parsed is None:
        return EvidenceResolution(
            ref,
            EvidenceStatus.MALFORMED_REF,
            note="expected '<scheme>:<path>[@<sha256-prefix>]'",
        )
    scheme, location, digest = parsed
    if scheme not in roots:
        return EvidenceResolution(
            ref,
            EvidenceStatus.UNKNOWN_SCHEME,
            scheme=scheme,
            relative_path=location,
            note=f"no root registered for scheme '{scheme}'",
        )
    root = roots[scheme].resolve()
    if digest.startswith(_COMMIT_ANCHOR_PREFIX):
        revision = digest[len(_COMMIT_ANCHOR_PREFIX) :].strip()
        if not revision:
            return EvidenceResolution(
                ref,
                EvidenceStatus.MALFORMED_REF,
                scheme=scheme,
                relative_path=location,
                note="commit anchor is empty",
            )
        return _resolve_at_commit(ref, root, scheme, location, revision)
    candidate = (root / location).resolve()
    if not candidate.is_relative_to(root):
        return EvidenceResolution(
            ref,
            EvidenceStatus.ESCAPES_ROOT,
            scheme=scheme,
            relative_path=location,
            note="evidence path escapes its registered root",
        )
    if not candidate.is_file():
        return EvidenceResolution(
            ref,
            EvidenceStatus.MISSING_ARTIFACT,
            scheme=scheme,
            relative_path=location,
            declared_digest=digest,
            note="referenced artifact does not exist",
        )
    try:
        actual = artifact_digest(candidate)
    except OSError as error:  # pragma: no cover - filesystem dependent
        return EvidenceResolution(
            ref,
            EvidenceStatus.UNREADABLE_ARTIFACT,
            scheme=scheme,
            relative_path=location,
            note=str(error),
        )
    if not digest:
        if require_digest:
            return EvidenceResolution(
                ref,
                EvidenceStatus.DIGEST_ABSENT,
                scheme=scheme,
                relative_path=location,
                actual_digest=actual,
                note="evidence reference must pin a content digest",
            )
        return EvidenceResolution(
            ref,
            EvidenceStatus.RESOLVED,
            scheme=scheme,
            relative_path=location,
            actual_digest=actual,
            content=candidate.read_text(encoding="utf-8", errors="replace"),
        )
    if len(digest) < _MIN_DIGEST_PREFIX:
        return EvidenceResolution(
            ref,
            EvidenceStatus.DIGEST_TOO_SHORT,
            scheme=scheme,
            relative_path=location,
            declared_digest=digest,
            actual_digest=actual,
            note=f"digest prefix must be at least {_MIN_DIGEST_PREFIX} hex characters",
        )
    if not actual.startswith(digest.lower()):
        return EvidenceResolution(
            ref,
            EvidenceStatus.DIGEST_MISMATCH,
            scheme=scheme,
            relative_path=location,
            declared_digest=digest,
            actual_digest=actual,
            note="artifact content does not match the pinned digest",
        )
    return EvidenceResolution(
        ref,
        EvidenceStatus.RESOLVED,
        scheme=scheme,
        relative_path=location,
        declared_digest=digest,
        actual_digest=actual,
        content=candidate.read_text(encoding="utf-8", errors="replace"),
    )


def resolve_evidence_refs(
    refs: tuple[str, ...],
    roots: Mapping[str, Path],
    *,
    require_digest: bool = True,
) -> tuple[EvidenceResolution, ...]:
    """Resolve every reference, preserving order and reporting each outcome."""

    return tuple(
        resolve_evidence_ref(ref, roots, require_digest=require_digest) for ref in refs
    )


def evidence_record_for(resolution: EvidenceResolution) -> EvidenceRecord:
    """Build the canonical evidence record a resolved reference stands for.

    Both sides of the binding must construct this identically: the answering
    lane computes the fingerprint it declares, and the host recomputes it from
    the artifact actually on disk. Keeping one constructor is what makes the
    two computations comparable.
    """

    if not resolution.resolved:
        raise ValueError("only a resolved reference can become an evidence record")
    return EvidenceRecord(
        evidence_id=resolution.ref,
        content=resolution.content or resolution.actual_digest,
        source_uri=resolution.ref,
    )


def expected_binding(resolution: EvidenceResolution) -> str:
    """The fingerprint an answer must declare to content-bind this reference."""

    return evidence_record_fingerprint(evidence_record_for(resolution))


def build_evidence_index(
    resolutions: tuple[EvidenceResolution, ...],
) -> dict[str, EvidenceRecord]:
    """The host-owned evidence index, built only from references that resolved."""

    return {
        item.ref: evidence_record_for(item) for item in resolutions if item.resolved
    }
