#!/usr/bin/env python3
"""Verify, safely decrypt, content-hash, and quarantine the SAB archive.

No entry name or entry body is printed.  The full path-bearing manifest stays
off-repository in an owner-only remote directory; the bounded receipt contains
only counts, byte totals, and hashes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath


EXPECTED_ARCHIVE_BYTES = 1_769_478_786
EXPECTED_ARCHIVE_SHA256 = "46e715d3b2196d459d2dff52aa487f506a95ec44b44262e82208d086ea879610"
EXPECTED_ENCRYPTED_FILES = 845


def hash_file(path: Path) -> tuple[str, int]:
    h = hashlib.sha256()
    count = 0
    with path.open("rb") as f:
        while chunk := f.read(8 * 1024 * 1024):
            h.update(chunk)
            count += len(chunk)
    return h.hexdigest(), count


def safe_relative(name: str) -> Path:
    pure = PurePosixPath(name)
    if not name or pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise ValueError("unsafe or empty ZIP member path")
    if "\\" in name:
        raise ValueError("backslash ZIP member path rejected")
    return Path(*pure.parts)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--archive", required=True)
    p.add_argument("--extract-root", required=True)
    p.add_argument("--manifest", required=True)
    p.add_argument("--receipt", required=True)
    p.add_argument("--password", required=True)
    args = p.parse_args()

    archive = Path(args.archive)
    final_root = Path(args.extract_root)
    manifest_path = Path(args.manifest)
    receipt_path = Path(args.receipt)
    archive_sha, archive_bytes = hash_file(archive)
    if archive_bytes != EXPECTED_ARCHIVE_BYTES or archive_sha != EXPECTED_ARCHIVE_SHA256:
        raise RuntimeError("archive byte count or SHA-256 mismatch")
    if final_root.exists():
        raise RuntimeError("extract root already exists; refusing overwrite")

    partial_root = final_root.with_name(final_root.name + f".partial-{os.getpid()}")
    partial_root.mkdir(parents=True, mode=0o700)
    manifest_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    receipt_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    password = args.password.encode("utf-8")
    entries = 0
    files = 0
    directories = 0
    encrypted_files = 0
    extracted_bytes = 0
    manifest_hasher = hashlib.sha256()

    try:
        with zipfile.ZipFile(archive) as zf, manifest_path.open("wb") as manifest:
            for info in zf.infolist():
                entries += 1
                rel = safe_relative(info.filename.rstrip("/"))
                out = partial_root / rel
                mode = (info.external_attr >> 16) & 0xFFFF
                if stat.S_ISLNK(mode):
                    raise RuntimeError("symbolic-link ZIP member rejected")
                if info.is_dir():
                    directories += 1
                    out.mkdir(parents=True, exist_ok=True, mode=0o700)
                    continue
                files += 1
                if info.flag_bits & 0x1:
                    encrypted_files += 1
                out.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                h = hashlib.sha256()
                count = 0
                with zf.open(info, pwd=password) as src, out.open("wb") as dst:
                    while chunk := src.read(4 * 1024 * 1024):
                        dst.write(chunk)
                        h.update(chunk)
                        count += len(chunk)
                os.chmod(out, 0o600)
                if count != info.file_size:
                    raise RuntimeError("decrypted member byte count mismatch")
                extracted_bytes += count
                record = json.dumps(
                    {"path": rel.as_posix(), "bytes": count, "sha256": h.hexdigest()},
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode() + b"\n"
                manifest.write(record)
                manifest_hasher.update(record)

        if encrypted_files != EXPECTED_ENCRYPTED_FILES:
            raise RuntimeError("encrypted file count mismatch")
        os.chmod(manifest_path, 0o600)
        partial_root.rename(final_root)
        os.chmod(final_root, 0o000)
    except Exception:
        shutil.rmtree(partial_root, ignore_errors=True)
        raise

    receipt = {
        "schema": "orion.p1.sab.lunarc.protected-artifact-stage.v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS",
        "terminal": "P1_SAB_LUNARC_ARCHIVE_STAGED_AND_HASH_MANIFESTED__EXTRACTED_TREE_QUARANTINED__ZERO_TASKS_RUN__ZERO_OUTCOMES_OPENED",
        "archive": {
            "bytes": archive_bytes,
            "sha256": archive_sha,
            "mode": oct(stat.S_IMODE(archive.stat().st_mode)),
            "remote_path_sha256": hashlib.sha256(str(archive).encode()).hexdigest(),
        },
        "extraction": {
            "zip_entries": entries,
            "files": files,
            "directories": directories,
            "encrypted_files": encrypted_files,
            "decrypted_file_bytes": extracted_bytes,
            "path_bearing_manifest_bytes": manifest_path.stat().st_size,
            "path_bearing_manifest_sha256": manifest_hasher.hexdigest(),
            "path_bearing_manifest_retained_off_repository": True,
            "entry_names_or_bodies_printed": False,
            "entry_bodies_semantically_inspected": False,
            "quarantined_root_mode": "0o0",
        },
        "password_source": "official_public_README_at_pinned_commit",
        "official_source_commit": "c26e151ed601ba109dc4d35e057ff8e73fec469d",
        "official_tasks_run": 0,
        "official_outcomes_opened": 0,
        "official_evaluator_invoked": False,
        "scientific_authority_delta": "NONE",
    }
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.chmod(receipt_path, 0o600)
    print(receipt["terminal"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
