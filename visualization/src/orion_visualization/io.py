"""Small, auditable I/O helpers for receipt-derived visualizations."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class SourceRecord:
    """A byte-level source binding.

    This record says only which bytes were read.  It is not a correctness,
    novelty, reproducibility, or independent-authority certificate.
    """

    path: str
    sha256: str
    byte_count: int

    def as_dict(self) -> dict[str, str | int]:
        return {
            "path": self.path,
            "sha256": self.sha256,
            "byte_count": self.byte_count,
            "integrity_scope": "bytes_only",
        }


def sha256_file(path: str | os.PathLike[str], *, chunk_size: int = 1024 * 1024) -> str:
    """Return the lowercase SHA-256 digest of a regular file."""

    if isinstance(chunk_size, bool) or not isinstance(chunk_size, int) or chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer")
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(f"source is not a regular file: {source}")
    digest = hashlib.sha256()
    with source.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_record(
    path: str | os.PathLike[str], *, root: str | os.PathLike[str] | None = None
) -> SourceRecord:
    """Create a path/size/digest record for an input file.

    When ``root`` is supplied the recorded path is relative and paths outside
    that root are rejected, preventing misleading ``../`` source identities.
    """

    source = Path(path).resolve(strict=True)
    if not source.is_file():
        raise FileNotFoundError(f"source is not a regular file: {source}")
    if root is None:
        recorded_path = source.as_posix()
    else:
        base = Path(root).resolve(strict=True)
        try:
            recorded_path = source.relative_to(base).as_posix()
        except ValueError as exc:
            raise ValueError(f"source {source} is outside root {base}") from exc
    return SourceRecord(recorded_path, sha256_file(source), source.stat().st_size)


def verify_source_record(
    record: SourceRecord | Mapping[str, Any], *, root: str | os.PathLike[str] | None = None
) -> bool:
    """Verify size and digest; return ``False`` for missing or changed bytes."""

    if not isinstance(record, SourceRecord):
        record = SourceRecord(
            path=str(record["path"]),
            sha256=str(record["sha256"]),
            byte_count=int(record["byte_count"]),
        )
    source = Path(record.path) if root is None else Path(root) / record.path
    try:
        resolved = source.resolve(strict=True)
    except FileNotFoundError:
        return False
    if root is not None:
        base = Path(root).resolve(strict=True)
        try:
            resolved.relative_to(base)
        except ValueError:
            return False
    if not resolved.is_file() or resolved.stat().st_size != record.byte_count:
        return False
    return sha256_file(resolved) == record.sha256.lower()


def load_json(path: str | os.PathLike[str]) -> Any:
    """Load UTF-8 JSON while retaining JSON null as Python ``None``."""

    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: str | os.PathLike[str], value: Any) -> Path:
    """Write deterministic, human-readable UTF-8 JSON."""

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
    target.write_text(payload + "\n", encoding="utf-8")
    return target
