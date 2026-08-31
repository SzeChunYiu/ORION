#!/usr/bin/env python3
from __future__ import annotations
import hashlib
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]

FILES = {
    "SOURCE.md": (REPO / "papers/orion-01-certificate-realization/theory-B-MANUSCRIPT_V2.md", "286e49f0ba93b21f4d2bc140390b254d7b64f3c4abf001a24fcc79b26c544988"),
    "CLAIM_LEDGER.md": (REPO / "papers/orion-01-certificate-realization/theory-B-CLAIM_LEDGER_R2.md", "d0a9539d27321dceb22df2717c795cede7358040537f2ded023fa5aa41446ea3"),
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
