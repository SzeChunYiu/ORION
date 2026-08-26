#!/usr/bin/env python3
"""Guarded fixture validation and exhaustive clean-room replay entry point."""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import build_manifest
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
    authorization_path: Path | None = None,
    repository: Path,
    workers: int,
    command: tuple[str, ...] | None = None,
    slurm_job_id: str | None = None,
) -> dict[str, Any]:
    # Identity is checked before any exhaustive dispatcher can start.
    packet = fg.require_packet_identity(packet_path, repository=repository)
    if authorization_path is None:
        raise fg.ExecutionAuthorizationMismatch(
            "external root-review execution authorization is required"
        )
    authorization = fg.require_execution_authorization(
        authorization_path,
        repository=repository,
        scientific_subject_commit=packet["packet_commit"],
        source_manifest_sha256=str(manifest["manifest_sha256"]),
    )
    stdout = io.StringIO()
    stderr = io.StringIO()
    started_at = (
        datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")
    )
    start = time.perf_counter_ns()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        payload = fg.execute_all_panels(workers=workers)
    end = time.perf_counter_ns()
    ended_at = datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")
    payload["packet_identity"] = {
        "schema": packet["schema"],
        "packet_commit": packet["packet_commit"],
        "base_commit": packet["base_commit"],
        "branch": packet["branch"],
    }
    payload["execution_authorization"] = authorization
    payload["execution_provenance"] = fg.build_execution_provenance(
        repository=repository,
        workers=workers,
        command=command or tuple(sys.argv),
        started_at=started_at,
        ended_at=ended_at,
        wall_time_seconds=(end - start) / 1_000_000_000,
        maximum_rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        exit_code=0,
        stdout=stdout.getvalue().encode("utf-8"),
        stderr=stderr.getvalue().encode("utf-8"),
        slurm_job_id=slurm_job_id or os.environ.get("SLURM_JOB_ID", "NOT_SLURM"),
    )
    return fg.seal_payload(payload, manifest_sha256=str(manifest["manifest_sha256"]))


def _repository_root() -> Path:
    output = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
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
    parser.add_argument(
        "--authorization-file",
        type=Path,
        default=(
            Path(os.environ["FIBERGUARD_EXECUTION_AUTHORIZATION"])
            if "FIBERGUARD_EXECUTION_AUTHORIZATION" in os.environ
            else None
        ),
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
    fg.verify_manifest(
        cleanroom,
        manifest,
        required_paths=build_manifest.SOURCE_PATHS,
    )
    if args.mode == "fixtures":
        receipt = prepare_fixture_receipt(manifest)
    else:
        receipt = prepare_execution_receipt(
            manifest=manifest,
            packet_path=args.packet_file,
            authorization_path=args.authorization_file,
            repository=repository,
            workers=args.workers,
            command=tuple(sys.argv),
            slurm_job_id=os.environ.get("SLURM_JOB_ID"),
        )
    write_json_atomic(args.output, receipt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
