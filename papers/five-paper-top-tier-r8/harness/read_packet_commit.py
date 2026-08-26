#!/usr/bin/env python3
"""Resolve the exact R8 scientific subject only after custody validation."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from validate_r8_packet_binding import BindingError, resolve_subject_checkout, validate_binding


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--require-source-ref", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        if args.json:
            print(
                json.dumps(
                    validate_binding(
                        args.repo_root, require_source_ref=args.require_source_ref
                    ),
                    indent=2,
                    sort_keys=True,
                )
            )
        else:
            print(
                resolve_subject_checkout(
                    args.repo_root, require_source_ref=args.require_source_ref
                )
            )
    except BindingError as exc:
        print(f"R8_PACKET_BINDING_INVALID: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
