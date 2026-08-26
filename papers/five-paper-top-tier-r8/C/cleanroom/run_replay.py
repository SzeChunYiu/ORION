#!/usr/bin/env python3
"""Guarded fixture validation and exhaustive clean-room replay entry point."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Mapping

import fiberguard_cleanroom as fg


def write_json_atomic(destination: Path, value: Mapping[str, Any]) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(f".{destination.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    os.replace(temporary, destination)


def prepare_fixture_receipt(manifest: Mapping[str, Any]) -> dict[str, Any]:
    return fg.seal_payload(
        fg.validate_non_outcome_fixtures(),
        manifest_sha256=str(manifest["manifest_sha256"]),
    )


def prepare_execution_receipt(
    *,
    manifest: Mapping[str, Any],
    packet_path: Path,
    repository: Path,
    workers: int,
) -> dict[str, Any]:
    # Identity is checked before any exhaustive dispatcher can start.
    packet = fg.require_packet_identity(packet_path, repository=repository)
    payload = fg.execute_all_panels(workers=workers)
    payload["packet_identity"] = {
        "packet_commit": packet["packet_commit"],
        "base_commit": packet["base_commit"],
        "branch": packet["branch"],
    }
    return fg.seal_payload(payload, manifest_sha256=str(manifest["manifest_sha256"]))


def _repository_root() -> Path:
    output = subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"], text=True
    ).strip()
    return Path(output)


def parse_args() -> argparse.Namespace:
    cleanroom = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("fixtures", "execute"), required=True)
    parser.add_argument("--manifest", type=Path, default=cleanroom / "SOURCE_MANIFEST.json")
    parser.add_argument(
        "--packet-file",
        type=Path,
        default=cleanroom.parents[1] / "R8_PACKET_COMMIT.json",
    )
    parser.add_argument("--repository", type=Path, default=None)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=1)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cleanroom = Path(__file__).resolve().parent
    repository = args.repository.resolve() if args.repository else _repository_root()
    manifest = json.loads(args.manifest.read_text())
    fg.verify_manifest(cleanroom, manifest)
    if args.mode == "fixtures":
        receipt = prepare_fixture_receipt(manifest)
    else:
        receipt = prepare_execution_receipt(
            manifest=manifest,
            packet_path=args.packet_file,
            repository=repository,
            workers=args.workers,
        )
    write_json_atomic(args.output, receipt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
