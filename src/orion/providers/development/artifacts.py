from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class DevelopmentArtifactRef:
    artifact_id: str
    content_hash: str
    media_type: str
    byte_length: int

    def __post_init__(self) -> None:
        if not self.artifact_id.strip() or not self.media_type.strip() or self.byte_length < 0:
            raise ValueError("development artifact identity/media/length are required")
        if len(self.content_hash) != 64 or any(ch not in "0123456789abcdef" for ch in self.content_hash):
            raise ValueError("development artifact hash must be SHA-256")


class DevelopmentArtifactStore(Protocol):
    def put(self, content: bytes, *, media_type: str) -> DevelopmentArtifactRef: ...

    def get(self, artifact_id: str) -> bytes: ...


class InMemoryDevelopmentArtifactStore:
    """Deterministic test/local artifact store."""

    def __init__(self) -> None:
        self._content: dict[str, bytes] = {}

    def put(self, content: bytes, *, media_type: str) -> DevelopmentArtifactRef:
        if not media_type.strip():
            raise ValueError("artifact media type is required")
        digest = hashlib.sha256(content).hexdigest()
        artifact_id = f"development-artifact:{digest}"
        self._content.setdefault(artifact_id, bytes(content))
        return DevelopmentArtifactRef(artifact_id, digest, media_type, len(content))

    def get(self, artifact_id: str) -> bytes:
        try:
            return self._content[artifact_id]
        except KeyError as exc:
            raise KeyError(f"unknown development artifact: {artifact_id}") from exc


class FileSystemDevelopmentArtifactStore:
    """Durable content-addressed patch/artifact store for protected Shadow runs.

    Content is immutable by hash. Metadata is deterministic and written adjacent
    to the bytes. `get` re-hashes the file so post-hoc filesystem mutation is
    detected before a candidate executor receives the patch.
    """

    def __init__(self, root: Path | str) -> None:
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        if not self.root.is_dir():
            raise ValueError("development artifact root must be a directory")

    @staticmethod
    def _digest_from_id(artifact_id: str) -> str:
        prefix = "development-artifact:"
        if not artifact_id.startswith(prefix):
            raise KeyError(f"unknown development artifact identity: {artifact_id}")
        digest = artifact_id[len(prefix):]
        if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
            raise KeyError(f"invalid development artifact identity: {artifact_id}")
        return digest

    def _data_path(self, digest: str) -> Path:
        return self.root / digest[:2] / digest[2:]

    def _metadata_path(self, digest: str) -> Path:
        return self.root / digest[:2] / f"{digest[2:]}.meta"

    def put(self, content: bytes, *, media_type: str) -> DevelopmentArtifactRef:
        if not media_type.strip():
            raise ValueError("artifact media type is required")
        digest = hashlib.sha256(content).hexdigest()
        data_path = self._data_path(digest)
        meta_path = self._metadata_path(digest)
        data_path.parent.mkdir(parents=True, exist_ok=True)
        if data_path.exists() and hashlib.sha256(data_path.read_bytes()).hexdigest() != digest:
            raise RuntimeError("existing development artifact content hash mismatch")
        if not data_path.exists():
            temporary = data_path.with_suffix(data_path.suffix + ".tmp")
            temporary.write_bytes(content)
            if hashlib.sha256(temporary.read_bytes()).hexdigest() != digest:
                temporary.unlink(missing_ok=True)
                raise RuntimeError("development artifact temporary write hash mismatch")
            temporary.replace(data_path)
        metadata = f"media_type={media_type}\nbyte_length={len(content)}\ncontent_hash={digest}\n"
        if meta_path.exists() and meta_path.read_text(encoding="utf-8") != metadata:
            raise RuntimeError("development artifact metadata mismatch for existing content")
        if not meta_path.exists():
            meta_path.write_text(metadata, encoding="utf-8")
        return DevelopmentArtifactRef(
            f"development-artifact:{digest}", digest, media_type, len(content)
        )

    def get(self, artifact_id: str) -> bytes:
        digest = self._digest_from_id(artifact_id)
        path = self._data_path(digest)
        try:
            content = path.read_bytes()
        except FileNotFoundError as exc:
            raise KeyError(f"unknown development artifact: {artifact_id}") from exc
        if hashlib.sha256(content).hexdigest() != digest:
            raise RuntimeError("development artifact content hash mismatch")
        return content


__all__ = [
    "DevelopmentArtifactRef",
    "DevelopmentArtifactStore",
    "FileSystemDevelopmentArtifactStore",
    "InMemoryDevelopmentArtifactStore",
]
