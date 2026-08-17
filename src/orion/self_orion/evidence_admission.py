from __future__ import annotations

import errno
import hashlib
import os
import stat
from dataclasses import dataclass
from pathlib import Path

from orion.self_orion.phase2_campaign import Phase2ExternalObservationBundle


def _is_sha256(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789abcdef" for character in value)


@dataclass(frozen=True)
class EvidenceArtifactBinding:
    """Host-visible identity for one result-bearing Phase-2 artifact."""

    artifact_id: str
    relative_path: str
    sha256: str

    def __post_init__(self) -> None:
        if not self.artifact_id.strip() or not self.relative_path.strip():
            raise ValueError("artifact id and relative path are required")
        if not _is_sha256(self.sha256):
            raise ValueError("artifact binding hash must be SHA-256")


@dataclass(frozen=True)
class Phase2EvidenceReceipt:
    """Receipt whose authority comes from re-reading host-visible bytes."""

    subject_revision_hash: str
    evaluator_artifact_hash: str
    evaluation_epoch_id: str
    artifacts: tuple[EvidenceArtifactBinding, ...]

    def __post_init__(self) -> None:
        if not _is_sha256(self.subject_revision_hash) or not _is_sha256(
            self.evaluator_artifact_hash
        ):
            raise ValueError("receipt subject/evaluator bindings must be SHA-256")
        if not self.evaluation_epoch_id.strip():
            raise ValueError("receipt evaluation epoch is required")


@dataclass(frozen=True)
class EvidenceAdmissionReport:
    blockers: tuple[str, ...]
    observed_hashes: tuple[tuple[str, str], ...]

    @property
    def admitted(self) -> bool:
        return not self.blockers


def _secure_descriptor_traversal_available() -> bool:
    return bool(
        hasattr(os, "O_NOFOLLOW")
        and hasattr(os, "O_DIRECTORY")
        and os.open in getattr(os, "supports_dir_fd", set())
    )


def _read_beneath_root_fd(
    root_fd: int,
    logical: Path,
) -> tuple[bytes | None, str | None]:
    """Read one regular file without re-resolving attacker-mutable pathnames.

    Every parent directory and the final file are opened relative to an
    already-open root descriptor with ``O_NOFOLLOW``.  A symlink swap between
    a pathname check and the read therefore cannot redirect the verifier to a
    different tree.
    """

    parts = logical.parts
    if not parts:
        return None, "artifact_path_invalid"

    current_fd = os.dup(root_fd)
    file_fd: int | None = None
    try:
        directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
        for part in parts[:-1]:
            next_fd = os.open(part, directory_flags, dir_fd=current_fd)
            os.close(current_fd)
            current_fd = next_fd

        file_fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW, dir_fd=current_fd)
        metadata = os.fstat(file_fd)
        if not stat.S_ISREG(metadata.st_mode):
            return None, "artifact_not_regular"

        chunks: list[bytes] = []
        while True:
            chunk = os.read(file_fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        return b"".join(chunks), None
    except OSError as exc:
        if exc.errno == errno.ENOENT:
            return None, "artifact_missing"
        if exc.errno in {errno.ELOOP, errno.ENOTDIR}:
            return None, "artifact_path_unsafe"
        return None, f"artifact_read_error:{exc.errno}"
    finally:
        if file_fd is not None:
            os.close(file_fd)
        os.close(current_fd)


def verify_phase2_evidence_receipt(
    receipt: Phase2EvidenceReceipt,
    artifact_root: str | Path,
    *,
    expected_subject_revision_hash: str | None = None,
    expected_evaluator_artifact_hash: str | None = None,
    expected_evaluation_epoch_id: str | None = None,
) -> EvidenceAdmissionReport:
    """Fail closed unless every declared artifact exists and hashes exactly.

    The caller may supply the expected closure bindings.  A receipt never
    proves those identities by merely restating them; they are compared here
    against host-selected expectations and the bytes are read from disk.
    Path traversal is descriptor-relative and no-follow so the checked path
    cannot be swapped to a symlink between validation and read.
    """

    blockers: list[str] = []
    observed: list[tuple[str, str]] = []

    if expected_subject_revision_hash is not None:
        if receipt.subject_revision_hash != expected_subject_revision_hash:
            blockers.append("subject_revision_mismatch")
    if expected_evaluator_artifact_hash is not None:
        if receipt.evaluator_artifact_hash != expected_evaluator_artifact_hash:
            blockers.append("evaluator_artifact_mismatch")
    if expected_evaluation_epoch_id is not None:
        if receipt.evaluation_epoch_id != expected_evaluation_epoch_id:
            blockers.append("evaluation_epoch_mismatch")

    if not receipt.artifacts:
        blockers.append("no_artifacts_bound")
        return EvidenceAdmissionReport(tuple(blockers), tuple(observed))

    if not _secure_descriptor_traversal_available():
        blockers.append("secure_descriptor_traversal_unavailable")
        return EvidenceAdmissionReport(tuple(blockers), tuple(observed))

    root_path = Path(artifact_root)
    try:
        root_fd = os.open(
            root_path,
            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
        )
    except OSError as exc:
        if exc.errno in {errno.ELOOP, errno.ENOTDIR}:
            blockers.append("artifact_root_unsafe")
        elif exc.errno == errno.ENOENT:
            blockers.append("artifact_root_missing")
        else:
            blockers.append(f"artifact_root_open_error:{exc.errno}")
        return EvidenceAdmissionReport(tuple(blockers), tuple(observed))

    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    try:
        for binding in receipt.artifacts:
            if binding.artifact_id in seen_ids:
                blockers.append(f"duplicate_artifact_id:{binding.artifact_id}")
            else:
                seen_ids.add(binding.artifact_id)

            if binding.relative_path in seen_paths:
                blockers.append(f"duplicate_artifact_path:{binding.relative_path}")
            else:
                seen_paths.add(binding.relative_path)

            logical = Path(binding.relative_path)
            if logical.is_absolute() or ".." in logical.parts:
                blockers.append(f"artifact_path_escape:{binding.artifact_id}")
                continue

            data, read_blocker = _read_beneath_root_fd(root_fd, logical)
            if read_blocker is not None:
                blockers.append(f"{read_blocker}:{binding.artifact_id}")
                continue
            assert data is not None

            actual = hashlib.sha256(data).hexdigest()
            observed.append((binding.artifact_id, actual))
            if actual != binding.sha256:
                blockers.append(f"artifact_hash_mismatch:{binding.artifact_id}")
    finally:
        os.close(root_fd)

    return EvidenceAdmissionReport(tuple(blockers), tuple(observed))


def verify_phase2_observation_bundle_artifacts(
    bundle: Phase2ExternalObservationBundle,
    receipt: Phase2EvidenceReceipt,
    artifact_root: str | Path,
) -> EvidenceAdmissionReport:
    """Bind external observations to verified host-visible result bytes."""

    report = verify_phase2_evidence_receipt(
        receipt,
        artifact_root,
        expected_subject_revision_hash=bundle.subject_revision_hash,
        expected_evaluator_artifact_hash=bundle.evaluator_artifact_hash,
        expected_evaluation_epoch_id=bundle.evaluation_epoch_id,
    )
    blockers = list(report.blockers)

    by_id: dict[str, EvidenceArtifactBinding] = {}
    for binding in receipt.artifacts:
        if binding.artifact_id not in by_id:
            by_id[binding.artifact_id] = binding

    for observation in bundle.observations:
        if observation.subject_revision_hash != bundle.subject_revision_hash:
            blockers.append(
                f"observation_subject_mismatch:{observation.criterion.value}"
            )
        if observation.evaluator_artifact_hash != bundle.evaluator_artifact_hash:
            blockers.append(
                f"observation_evaluator_mismatch:{observation.criterion.value}"
            )
        if observation.evaluation_epoch_id != bundle.evaluation_epoch_id:
            blockers.append(f"observation_epoch_mismatch:{observation.criterion.value}")

        binding = by_id.get(observation.evidence_artifact_id)
        if binding is None:
            blockers.append(
                f"observation_artifact_unbound:{observation.evidence_artifact_id}"
            )
            continue
        if binding.sha256 != observation.evidence_artifact_hash:
            blockers.append(
                f"observation_artifact_hash_mismatch:{observation.evidence_artifact_id}"
            )

    return EvidenceAdmissionReport(tuple(blockers), report.observed_hashes)
