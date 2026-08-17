from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path


SUBJECT_ATTESTATION_SCHEMA = "RepositorySubjectAttestation.v1"


def _git(root: Path, *args: str) -> bytes:
    try:
        result = subprocess.run(
            ("git", "-C", str(root), *args),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        detail = getattr(error, "stderr", b"")
        if isinstance(detail, bytes):
            detail = detail.decode("utf-8", errors="replace")
        raise RuntimeError(f"git command failed: {' '.join(args)}: {detail}") from error
    return result.stdout


def _text(root: Path, *args: str) -> str:
    return _git(root, *args).decode("utf-8").strip()


def _normalize_repository_identity(remote: str) -> str:
    value = remote.strip()
    if not value:
        return "repository:local-unbound"
    if value.startswith("git@") and ":" in value:
        host, path = value[4:].split(":", 1)
        return f"{host.lower()}/{path.removesuffix('.git').strip('/')}"
    if "://" in value:
        from urllib.parse import urlparse

        parsed = urlparse(value)
        host = (parsed.hostname or "").lower()
        path = parsed.path.removesuffix(".git").strip("/")
        if host and path:
            return f"{host}/{path}"
    return value.removesuffix(".git")


def is_derived_from_commit(
    root: Path | str,
    anchor_commit: str,
    commit_oid: str,
) -> bool:
    """Is `commit_oid` a descendant of `anchor_commit` in this repository?

    Ancestry is the derivation predicate: a Phase-2 subject is Phase-1-derived
    iff the Phase-1 terminal anchor is an ancestor of it. The anchor is supplied
    by the caller and never hardcoded here -- which commit is terminal is a
    governance fact recorded in the issue trail, not a constant this module may
    assert on its own.

    Ancestry is necessary, not sufficient: an evidence family must additionally
    share one `subject_revision_hash`, which this predicate does not check.

    Raises RuntimeError if either commit is unknown to the repository, so an
    unanswerable question is never silently reported as False.
    """

    for label, value in (("anchor", anchor_commit), ("subject", commit_oid)):
        if not value.strip():
            raise ValueError(f"{label} commit is required to test derivation")
    top = Path(_text(Path(root).resolve(), "rev-parse", "--show-toplevel")).resolve()
    for label, value in (("anchor", anchor_commit), ("subject", commit_oid)):
        try:
            _git(top, "cat-file", "-e", f"{value}^{{commit}}")
        except RuntimeError as error:
            raise RuntimeError(f"{label} commit {value!r} is unknown to this repository") from error
    result = subprocess.run(
        ("git", "-C", str(top), "merge-base", "--is-ancestor", anchor_commit, commit_oid),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode == 0:
        # A path was found, so it exists. This direction is sound even in a
        # shallow clone: truncated history can hide a path, never invent one.
        return True
    if result.returncode == 1:
        # "Not an ancestor" is only trustworthy over complete history. In a
        # shallow clone the connecting path may simply have been cut at the
        # graft boundary, so a bare False here would be a confident wrong
        # answer -- exactly the kind a fail-closed gate must not emit.
        if _text(top, "rev-parse", "--is-shallow-repository") == "true":
            raise RuntimeError(
                "cannot decide derivation in a shallow repository: no path was found "
                f"from {anchor_commit} to {commit_oid}, but history is truncated. "
                "Re-run with a complete clone (git fetch --unshallow)."
            )
        return False
    detail = result.stderr.decode("utf-8", errors="replace")
    raise RuntimeError(f"git merge-base --is-ancestor failed: {detail}")


@dataclass(frozen=True)
class TrackedObjectIdentity:
    path: str
    mode: str
    object_type: str
    git_oid: str
    content_sha256: str


@dataclass(frozen=True)
class RepositorySubjectAttestation:
    repository_identity: str
    commit_oid: str
    tree_oid: str
    git_object_format: str
    tracked_objects: tuple[TrackedObjectIdentity, ...]
    schema: str = SUBJECT_ATTESTATION_SCHEMA

    def __post_init__(self) -> None:
        if self.schema != SUBJECT_ATTESTATION_SCHEMA:
            raise ValueError("unsupported repository subject attestation schema")
        if any(
            not value.strip()
            for value in (
                self.repository_identity,
                self.commit_oid,
                self.tree_oid,
                self.git_object_format,
            )
        ):
            raise ValueError("subject attestation identity/commit/tree/object format are required")
        paths = [item.path for item in self.tracked_objects]
        if not paths or paths != sorted(paths) or len(paths) != len(set(paths)):
            raise ValueError("subject attestation tracked objects must be non-empty, unique and sorted")
        for item in self.tracked_objects:
            if len(item.content_sha256) != 64 or any(
                character not in "0123456789abcdef" for character in item.content_sha256
            ):
                raise ValueError("tracked object content identity must be SHA-256")

    @property
    def source_tree_sha256(self) -> str:
        manifest = [
            {
                "path": item.path,
                "mode": item.mode,
                "object_type": item.object_type,
                "git_oid": item.git_oid,
                "content_sha256": item.content_sha256,
            }
            for item in self.tracked_objects
        ]
        return hashlib.sha256(
            json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()

    @property
    def payload(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "repository_identity": self.repository_identity,
            "commit_oid": self.commit_oid,
            "tree_oid": self.tree_oid,
            "git_object_format": self.git_object_format,
            "tracked_object_count": len(self.tracked_objects),
            "source_tree_sha256": self.source_tree_sha256,
            "tracked_objects": [
                {
                    "path": item.path,
                    "mode": item.mode,
                    "object_type": item.object_type,
                    "git_oid": item.git_oid,
                    "content_sha256": item.content_sha256,
                }
                for item in self.tracked_objects
            ],
        }

    @property
    def subject_revision_hash(self) -> str:
        identity = {
            "schema": self.schema,
            "repository_identity": self.repository_identity,
            "commit_oid": self.commit_oid,
            "tree_oid": self.tree_oid,
            "git_object_format": self.git_object_format,
            "source_tree_sha256": self.source_tree_sha256,
        }
        return hashlib.sha256(
            json.dumps(identity, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()


def attest_repository_subject(
    root: Path | str,
    *,
    repository_identity: str | None = None,
) -> RepositorySubjectAttestation:
    """Bind the exact clean Git subject to SHA-256 content identities.

    The worktree must exactly equal HEAD. Git object IDs are preserved for
    provenance, while every tracked blob is independently SHA-256 content-bound
    so the Phase-2 subject identity does not rely only on the repository's Git
    object hash algorithm.
    """

    root_path = Path(root).resolve()
    top = Path(_text(root_path, "rev-parse", "--show-toplevel")).resolve()
    dirty = _text(top, "status", "--porcelain=v1", "--untracked-files=all")
    if dirty:
        raise RuntimeError("cannot attest Phase-2 subject from a dirty or untracked worktree")
    commit_oid = _text(top, "rev-parse", "HEAD")
    tree_oid = _text(top, "rev-parse", "HEAD^{tree}")
    try:
        object_format = _text(top, "rev-parse", "--show-object-format")
    except RuntimeError:
        object_format = "sha1"
    if repository_identity is None:
        try:
            remote = _text(top, "config", "--get", "remote.origin.url")
        except RuntimeError:
            remote = ""
        repository_identity = _normalize_repository_identity(remote)
    else:
        repository_identity = repository_identity.strip()
        if not repository_identity:
            raise ValueError("repository identity override cannot be empty")

    raw = _git(top, "ls-tree", "-r", "-z", "--full-tree", "HEAD")
    objects: list[TrackedObjectIdentity] = []
    for entry in raw.split(b"\0"):
        if not entry:
            continue
        metadata, path_bytes = entry.split(b"\t", 1)
        mode_bytes, type_bytes, oid_bytes = metadata.split(b" ", 2)
        mode = mode_bytes.decode("ascii")
        object_type = type_bytes.decode("ascii")
        git_oid = oid_bytes.decode("ascii")
        path = path_bytes.decode("utf-8", errors="surrogateescape")
        if object_type == "blob":
            content = _git(top, "cat-file", "blob", git_oid)
            content_hash = hashlib.sha256(content).hexdigest()
        else:
            # Submodule/other tree entries are not dereferenced into another
            # repository. Bind their exact Git object identity as content.
            content_hash = hashlib.sha256(
                f"{object_type}:{git_oid}".encode("ascii")
            ).hexdigest()
        objects.append(
            TrackedObjectIdentity(path, mode, object_type, git_oid, content_hash)
        )
    objects.sort(key=lambda item: item.path)
    return RepositorySubjectAttestation(
        repository_identity=repository_identity,
        commit_oid=commit_oid,
        tree_oid=tree_oid,
        git_object_format=object_format,
        tracked_objects=tuple(objects),
    )


def write_repository_subject_attestation(
    attestation: RepositorySubjectAttestation,
    path: Path | str,
) -> None:
    payload = {
        **attestation.payload,
        "subject_revision_hash": attestation.subject_revision_hash,
    }
    Path(path).write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


__all__ = [
    "SUBJECT_ATTESTATION_SCHEMA",
    "RepositorySubjectAttestation",
    "TrackedObjectIdentity",
    "attest_repository_subject",
    "is_derived_from_commit",
    "write_repository_subject_attestation",
]
