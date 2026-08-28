#!/usr/bin/env python3
from __future__ import annotations
import hashlib
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]

FILES = {
    "SOURCE.md": (REPO / "papers/orion-01-certificate-realization/theory-A-MANUSCRIPT_V2.md", "596217cfcf623b77ab77ecbd2ae0abbffdaf7ef2392cb2f8915ed790eec68365"),
    "CLAIM_LEDGER.md": (REPO / "papers/orion-01-certificate-realization/theory-A-CLAIM_LEDGER_R2.md", "3c2a7771774856e2de2d18cf38f2b62c0e069301925a40624105349dd46d03db"),
}

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> int:
    for packaged_name, (canonical, expected) in FILES.items():
        packaged = HERE / packaged_name
        if not canonical.is_file() or not packaged.is_file():
            print(f"CANNOT_CHECK missing file: {canonical if not canonical.is_file() else packaged}", file=sys.stderr)
            return 3
        if packaged.read_bytes() != canonical.read_bytes():
            print(f"RED byte drift: {packaged_name} != {canonical}", file=sys.stderr)
            return 2
        got = sha256(packaged)
        if got != expected:
            print(f"RED sha256 mismatch for {packaged_name}: {got} != {expected}", file=sys.stderr)
            return 2
    required = ["COMPILE.md", "build.sh", "DATA_CODE_AVAILABILITY.md", "LICENSE_STATUS.md",
                "COVER_LETTER_DRAFT.md", "SUBMISSION_MANIFEST.json"]
    missing = [name for name in required if not (HERE / name).is_file()]
    if missing:
        print("CANNOT_CHECK missing package files: " + ", ".join(missing), file=sys.stderr)
        return 3
    print("ORION01_PACKAGE_SOURCE_BINDING_GREEN")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
