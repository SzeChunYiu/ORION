from __future__ import annotations

import hashlib
from dataclasses import dataclass
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
    """Deterministic test/local artifact store; production hosts may replace it."""

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


__all__ = [
    "DevelopmentArtifactRef",
    "DevelopmentArtifactStore",
    "InMemoryDevelopmentArtifactStore",
]
