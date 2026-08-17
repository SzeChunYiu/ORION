from __future__ import annotations

import argparse
import errno
import json
import os
import stat
from dataclasses import dataclass
from pathlib import Path

from .freeze import freeze_protected_suite


def _secure_open_supported() -> bool:
    return bool(
        hasattr(os, "O_NOFOLLOW")
        and hasattr(os, "O_DIRECTORY")
        and os.open in getattr(os, "supports_dir_fd", set())
        and os.mkdir in getattr(os, "supports_dir_fd", set())
        and os.unlink in getattr(os, "supports_dir_fd", set())
    )


def _path_parts(path: Path) -> tuple[bool, tuple[str, ...]]:
    raw = path.parts
    absolute = path.is_absolute()
    parts = raw[1:] if absolute else raw
    cleaned = tuple(part for part in parts if part not in ("", "."))
    if not cleaned or ".." in cleaned:
        raise ValueError("freeze paths must be concrete and non-traversing")
    return absolute, cleaned


def _open_parent_dir(path: Path, *, create: bool) -> tuple[int, str]:
    absolute, parts = _path_parts(path)
    parent_parts = parts[:-1]
    filename = parts[-1]
    current_fd = os.open(
        "/" if absolute else ".",
        os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
    )
    try:
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
        for part in parent_parts:
            try:
                next_fd = os.open(part, flags, dir_fd=current_fd)
            except OSError as exc:
                if exc.errno != errno.ENOENT or not create:
                    raise
                os.mkdir(part, mode=0o700, dir_fd=current_fd)
                next_fd = os.open(part, flags, dir_fd=current_fd)
            os.close(current_fd)
            current_fd = next_fd
        return current_fd, filename
    except Exception:
        os.close(current_fd)
        raise


def _read_protected_json(path: Path) -> dict[str, object]:
    parent_fd, filename = _open_parent_dir(path, create=False)
    file_fd: int | None = None
    try:
        file_fd = os.open(filename, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent_fd)
        metadata = os.fstat(file_fd)
        if not stat.S_ISREG(metadata.st_mode):
            raise ValueError("protected suite must be a regular file")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(file_fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        try:
            value = json.loads(b"".join(chunks).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"protected suite is not valid UTF-8 JSON: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError("protected suite JSON root must be an object")
        return value
    finally:
        if file_fd is not None:
            os.close(file_fd)
        os.close(parent_fd)


@dataclass
class _ReservedOutput:
    parent_fd: int
    file_fd: int
    filename: str
    committed: bool = False

    def cleanup(self) -> None:
        try:
            if not self.committed:
                try:
                    os.unlink(self.filename, dir_fd=self.parent_fd)
                except FileNotFoundError:
                    pass
        finally:
            os.close(self.file_fd)
            os.close(self.parent_fd)


def _reserve_output(path: Path) -> _ReservedOutput:
    parent_fd, filename = _open_parent_dir(path, create=True)
    try:
        file_fd = os.open(
            filename,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            0o600,
            dir_fd=parent_fd,
        )
    except Exception:
        os.close(parent_fd)
        raise
    return _ReservedOutput(parent_fd=parent_fd, file_fd=file_fd, filename=filename)


def _write_all(fd: int, payload: bytes) -> None:
    offset = 0
    while offset < len(payload):
        written = os.write(fd, payload[offset:])
        if written <= 0:
            raise OSError("short write while freezing P5 artifacts")
        offset += written
    os.fsync(fd)


def _identity_key(path: Path) -> str:
    return os.path.normcase(os.path.abspath(os.path.normpath(os.fspath(path))))


def _validate_path_identities(
    protected_suite: Path,
    candidate_packet: Path,
    commitment: Path,
) -> None:
    identities = {
        "protected-suite": _identity_key(protected_suite),
        "candidate-packet": _identity_key(candidate_packet),
        "commitment": _identity_key(commitment),
    }
    if len(set(identities.values())) != len(identities):
        raise ValueError("protected suite, candidate packet, and commitment paths must be distinct")


def _encode(value: dict[str, object]) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Freeze a protected ORION-P5 hidden-cause suite without crossing custody paths"
    )
    parser.add_argument("--protected-suite", type=Path, required=True)
    parser.add_argument("--candidate-packet", type=Path, required=True)
    parser.add_argument("--commitment", type=Path, required=True)
    args = parser.parse_args(argv)

    if not _secure_open_supported():
        raise RuntimeError("secure descriptor-relative no-follow filesystem operations are unavailable")

    _validate_path_identities(
        args.protected_suite,
        args.candidate_packet,
        args.commitment,
    )
    protected = _read_protected_json(args.protected_suite)
    candidate, commitment = freeze_protected_suite(protected)

    candidate_output: _ReservedOutput | None = None
    commitment_output: _ReservedOutput | None = None
    try:
        # Reserve both names before writing either payload so an existing or
        # aliased output cannot leave a seemingly complete one-sided freeze.
        candidate_output = _reserve_output(args.candidate_packet)
        commitment_output = _reserve_output(args.commitment)
        _write_all(candidate_output.file_fd, _encode(candidate))
        _write_all(commitment_output.file_fd, _encode(commitment))
        candidate_output.committed = True
        commitment_output.committed = True
    finally:
        if commitment_output is not None:
            commitment_output.cleanup()
        if candidate_output is not None:
            candidate_output.cleanup()
    return 0


__all__ = ["main"]
