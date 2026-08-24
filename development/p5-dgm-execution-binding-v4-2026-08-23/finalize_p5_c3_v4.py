#!/usr/bin/env python3
"""Finalize audit, cleanup inventory and checksums after deterministic validation."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    validator = subprocess.run(
        [sys.executable, str(HERE / "p5_c3_v4_validator.py")],
        capture_output=True,
        text=True,
        check=False,
    )
    if validator.returncode != 0:
        sys.stderr.write(validator.stdout)
        sys.stderr.write(validator.stderr)
        return validator.returncode
    receipt = json.loads(validator.stdout)
    if not receipt.get("passed"):
        return 1

    audit_path = HERE / "AUDIT_RECEIPT_V4.json"
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    audit["validation"] = {
        "validator": "p5_c3_v4_validator.py",
        "validator_sha256": sha(HERE / "p5_c3_v4_validator.py"),
        "checks_total": receipt["checks_total"],
        "checks_passed": receipt["checks_passed"],
        "checks_failed": receipt["checks_failed"],
        "passed": receipt["passed"],
        "checks": receipt["checks"],
    }
    write_json(audit_path, audit)

    checksum_path = HERE / "SHA256SUMS"
    checksum_path.unlink(missing_ok=True)
    cleanup_path = HERE / "CLEANUP_AUDIT_V4.json"
    cleanup = json.loads(cleanup_path.read_text(encoding="utf-8"))
    for _ in range(10):
        files = sorted(path for path in HERE.iterdir() if path.is_file() and path.name != "SHA256SUMS")
        largest = max(files, key=lambda path: path.stat().st_size)
        updated = dict(cleanup)
        updated["lane_file_count_before_sha256s"] = len(files)
        updated["lane_total_bytes_before_sha256s"] = sum(path.stat().st_size for path in files)
        updated["largest_file"] = {"path": largest.name, "bytes": largest.stat().st_size}
        prior = cleanup_path.read_bytes()
        write_json(cleanup_path, updated)
        cleanup = updated
        if cleanup_path.read_bytes() == prior:
            break

    files = sorted(path for path in HERE.iterdir() if path.is_file() and path.name != "SHA256SUMS")
    checksum_path.write_text(
        "".join(f"{sha(path)}  {path.name}\n" for path in files),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "passed": True,
                "checks_passed": receipt["checks_passed"],
                "checks_total": receipt["checks_total"],
                "checksum_entries": len(files),
                "sha256s_sha256": sha(checksum_path),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
