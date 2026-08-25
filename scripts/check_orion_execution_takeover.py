#!/usr/bin/env python3
"""Validate the canonical ORION V3 takeover queue without executing it."""

from pathlib import Path

from orion.discovery.execution_takeover import BLOCKED, load_manifest, ready_job_ids, validate_manifest


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/orion-discovery-v3/EXECUTION_TAKEOVER_MANIFEST_V1.json"


def main() -> None:
    manifest = load_manifest(MANIFEST)
    validate_manifest(manifest)
    ready = ready_job_ids(manifest)
    blocked = sum(job["status"] == BLOCKED for job in manifest["jobs"])
    print(
        "ORION_DISCOVERY_V3_TAKEOVER_VALID "
        f"jobs={len(manifest['jobs'])} ready={len(ready)} blocked={blocked}"
    )


if __name__ == "__main__":
    main()
