#!/usr/bin/env python3
"""Freeze the pre-bound disjoint P1 necessity replication world identity.

This file is additive and does not modify the source surface bound by the primary
execution receipt.  It may run only after a committed supported primary result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from orion.study.p1_causal.necessity_cases import (
    candidate_view_leaks,
    serialize_protected,
    serialize_public,
    world_manifest,
)
from orion.study.p1_causal.necessity_cases_v2 import generate_necessity_worlds_v2

from freeze_mutation_necessity_worlds import (
    DEFAULT_PROTOCOL,
    ROOT,
    SOURCE_PATHS,
    load_effective_protocol,
)

PRIMARY_FREEZE = ROOT / "research" / "revival" / "p1" / "confirmatory" / "v2.2" / "PRIMARY_WORLD_FREEZE.json"
PRIMARY_RESULT = ROOT / "research" / "revival" / "p1" / "confirmatory" / "v2.2" / "primary" / "PRIMARY_RESULT.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def freeze(protocol_path: Path, outdir: Path) -> dict:
    primary_result = json.loads(PRIMARY_RESULT.read_text())
    if primary_result.get("terminal") != "P1_MUTATION_NECESSITY_SUPPORTED":
        raise ValueError("replication is gated on a supported committed primary result")
    primary = json.loads(PRIMARY_FREEZE.read_text())
    protocol, identity = load_effective_protocol(protocol_path)
    plan = protocol["fresh_world_plan"]
    seed = int(plan["replication_seed"])
    if seed == int(plan["confirmatory_seed"]):
        raise ValueError("replication seed is not disjoint")
    worlds = generate_necessity_worlds_v2(
        seed=seed,
        hidden_shift_n=int(plan["hidden_shift_n"]),
        control_n=int(plan["negative_control_n"]),
    )
    manifest = world_manifest(worlds)
    if manifest["n"] != int(plan["total_n"]):
        raise ValueError("replication count drift")
    if manifest["candidate_view_leak_count"] != 0:
        raise ValueError("replication candidate-view leak")
    if any(candidate_view_leaks(item.public) for item in worlds):
        raise ValueError("replication leak audit disagreement")
    public = serialize_public(worlds)
    protected = serialize_protected(worlds)
    public_sha = hashlib.sha256(public).hexdigest()
    protected_sha = hashlib.sha256(protected).hexdigest()
    if public_sha == primary["public_sha256"]:
        raise ValueError("replication public worlds are not disjoint from primary identity")
    if protected_sha == primary["protected_response_matrix_sha256"]:
        raise ValueError("replication protected worlds are not disjoint from primary identity")

    binding = {
        "schema_version": "P1.epistemic-mutation-necessity-replication-world-freeze.v1",
        "protocol_id": protocol["protocol_id"],
        "protocol_version": protocol["protocol_version"],
        "protocol_chain": identity,
        "subject_git_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "replication_seed": seed,
        "primary_confirmatory_seed": int(plan["confirmatory_seed"]),
        "n": manifest["n"],
        "hidden_shift_n": manifest["hidden_shift_n"],
        "negative_control_n": manifest["negative_control_n"],
        "public_sha256": public_sha,
        "protected_response_matrix_sha256": protected_sha,
        "primary_public_sha256": primary["public_sha256"],
        "primary_protected_response_matrix_sha256": primary["protected_response_matrix_sha256"],
        "candidate_view_leak_count": 0,
        "by_family": manifest["by_family"],
        "source_sha256": {path: _sha(ROOT / path) for path in SOURCE_PATHS},
        "arms_executed": False,
        "outcome_accessed": False,
        "claim_boundary": "REPLICATION_WORLD_IDENTITY_ONLY__PRIMARY_ALREADY_SUPPORTED__NO_REPLICATION_ARM_OUTPUT",
    }
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "WORLD_PUBLIC.jsonl").write_bytes(public)
    (outdir / "PROTECTED_RESPONSE_MATRIX.jsonl").write_bytes(protected)
    (outdir / "WORLD_FREEZE.json").write_text(json.dumps(binding, indent=2, sort_keys=True) + "\n")
    return binding


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    result = freeze(args.protocol, args.outdir)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
