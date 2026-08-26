#!/usr/bin/env python3
"""Build the deterministic clean-room source manifest."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import fiberguard_cleanroom as fg


SOURCE_PATHS = tuple(
    sorted(
        (
            "BLINDING_BREACH.json",
            "README.md",
            "SOURCE_PROTOCOL.json",
            "SUBMISSION_BLOCKER.json",
            "build_manifest.py",
            "fiberguard_cleanroom.py",
            "run_replay.py",
            "slurm/job_c_r8_1.slurm",
            "tests/test_execution_guards.py",
            "tests/test_fiberguard_cleanroom.py",
            "tests/test_hostile_guards.py",
            "verify_receipt.py",
        )
    )
)


def parse_args() -> argparse.Namespace:
    cleanroom = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=cleanroom)
    parser.add_argument("--output", type=Path, default=cleanroom / "SOURCE_MANIFEST.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = fg.build_manifest(args.root, SOURCE_PATHS)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(f".{args.output.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    os.replace(temporary, args.output)
    print(manifest["manifest_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
