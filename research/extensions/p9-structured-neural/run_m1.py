#!/usr/bin/env python3
"""Execute the frozen P9 M1 classical-learning protocol and emit JSON."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from orion.study.p9.m1_runtime import run_m1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--subject-sha", default=os.environ.get("GITHUB_SHA"))
    args = parser.parse_args()

    result = run_m1(subject_sha=args.subject_sha)
    encoded = json.dumps(result, sort_keys=True, indent=2)
    print(encoded)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
