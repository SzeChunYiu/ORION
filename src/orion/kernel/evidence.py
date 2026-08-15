from __future__ import annotations

import hashlib
import subprocess
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from orion.core.evidence import EvidenceRecord, evidence_record_fingerprint

_REF_SEPARATOR = ":"
_HASH_SEPARATOR = "@"
_MIN_DIGEST_PREFIX = 8
_COMMIT_ANCHOR_PREFIX = "git:"


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


def _blob_at_commit(root: Path, revision: str, relative_path: str) -> bytes | None:
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
