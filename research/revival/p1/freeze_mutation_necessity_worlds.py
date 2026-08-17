#!/usr/bin/env python3
"""Materialize the P1 mutation-necessity holdout without running any arm."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from orion.study.p1_causal.necessity_cases import (
    candidate_view_leaks,
    serialize_protected,
    serialize_public,
    world_manifest,
)
from orion.study.p1_causal.necessity_cases_v2 import generate_necessity_worlds_v2

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PROTOCOL = (
    ROOT
    / "research"
    / "revival"
    / "p1"
    / "protocol"
    / "P1.epistemic-mutation-necessity.v2.2.1.json"
)
AMENDMENT_SCHEMA = "orion.publication-protocol-amendment.v1"
SOURCE_PATHS = (
    "src/orion/study/p1_causal/necessity_cases.py",
    "src/orion/study/p1_causal/necessity_cases_v2.py",
    "src/orion/study/p1_causal/necessity_engine.py",
    "src/orion/study/p1_causal/necessity_policies.py",
    "src/orion/study/p1_causal/necessity_scoring.py",
    "src/orion/study/p1_causal/necessity_statistics.py",
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data).hexdigest()


def _load_node(
    path: Path,
    *,
    seen: frozenset[Path],
) -> tuple[dict[str, Any], list[dict[str, str]], bytes]:
    resolved = path.resolve()
    if resolved in seen:
        raise ValueError("mutation-necessity protocol cycle")
    raw = path.read_bytes()
    payload = json.loads(raw)
    rel = str(path.relative_to(ROOT))
    node = {
        "path": rel,
        "protocol_version": str(payload.get("protocol_version", "")),
        "schema_version": str(payload.get("schema_version", "")),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "git_blob_sha": _git_blob_sha(raw),
    }
    if payload.get("schema_version") != AMENDMENT_SCHEMA:
        if payload.get("protocol_status") != "DESIGN_FROZEN":
            raise ValueError("base protocol not DESIGN_FROZEN")
        if payload.get("outcome_accessed") is not False:
            raise ValueError("base protocol records outcome access")
        return copy.deepcopy(payload), [node], raw

    if payload.get("protocol_status") != "DESIGN_FROZEN":
        raise ValueError("amendment not DESIGN_FROZEN")
    if payload.get("confirmatory_outcome_accessed") is not False:
        raise ValueError("amendment records confirmatory outcome access")
    base_path = ROOT / str(payload["base_protocol_path"])
    base_payload = json.loads(base_path.read_text())
    if base_payload.get("protocol_version") != payload.get("base_protocol_version"):
        raise ValueError("amendment base version mismatch")
    effective, nodes, material = _load_node(
        base_path,
        seen=seen | frozenset({resolved}),
    )
    overrides = payload.get("overrides", {})
    if not isinstance(overrides, dict):
        raise ValueError("amendment overrides must be object")
    for key, value in overrides.items():
        effective[key] = copy.deepcopy(value)
    effective["protocol_version"] = payload["protocol_version"]
    effective["effective_amendment_path"] = rel
    effective["confirmatory_outcome_accessed"] = False
    return effective, [*nodes, node], material + b"\0" + raw


def load_effective_protocol(path: Path = DEFAULT_PROTOCOL) -> tuple[dict[str, Any], dict[str, Any]]:
    effective, nodes, material = _load_node(path, seen=frozenset())
    return effective, {
        "kind": "base_only" if len(nodes) == 1 else "base_plus_amendments",
        "nodes": nodes,
        "effective_protocol_version": effective["protocol_version"],
        "chain_sha256": hashlib.sha256(material).hexdigest(),
    }


def freeze(protocol_path: Path, outdir: Path) -> dict[str, Any]:
    protocol, identity = load_effective_protocol(protocol_path)
    plan = protocol["fresh_world_plan"]
    if plan.get("generator_id") != "P1.mutation-necessity-worlds.v2":
        raise ValueError("unsupported confirmatory generator")
    worlds = generate_necessity_worlds_v2(
        seed=int(plan["confirmatory_seed"]),
        hidden_shift_n=int(plan["hidden_shift_n"]),
        control_n=int(plan["negative_control_n"]),
    )
    manifest = world_manifest(worlds)
    if manifest["n"] != int(plan["total_n"]):
        raise ValueError("world count drift")
    if manifest["hidden_shift_n"] != int(plan["hidden_shift_n"]):
        raise ValueError("hidden-shift count drift")
    if manifest["negative_control_n"] != int(plan["negative_control_n"]):
        raise ValueError("control count drift")
    if manifest["candidate_view_leak_count"] != 0:
        raise ValueError("candidate-view leak detected")
    if any(candidate_view_leaks(item.public) for item in worlds):
        raise ValueError("candidate-view leak audit disagreement")
    if {repair.declared_cost for item in worlds for repair in item.public.repairs} != {1.0}:
        raise ValueError("v2 repair unit-cost drift")
    if {probe.declared_cost for item in worlds for probe in item.public.diagnostic_probes} != {1.0}:
        raise ValueError("v2 probe unit-cost drift")

    public = serialize_public(worlds)
    protected = serialize_protected(worlds)
    public_ids = [json.loads(line)["task_id"] for line in public.decode().splitlines()]
    protected_ids = [json.loads(line)["task_id"] for line in protected.decode().splitlines()]
    if public_ids != protected_ids or len(set(public_ids)) != len(worlds):
        raise ValueError("public/protected task identity mismatch")

    binding = {
        "schema_version": "P1.epistemic-mutation-necessity-world-freeze.v1",
        "protocol_id": protocol["protocol_id"],
        "protocol_version": protocol["protocol_version"],
        "protocol_chain": identity,
        "confirmatory_seed": int(plan["confirmatory_seed"]),
        "n": len(worlds),
        "hidden_shift_n": manifest["hidden_shift_n"],
        "negative_control_n": manifest["negative_control_n"],
        "public_sha256": hashlib.sha256(public).hexdigest(),
        "protected_response_matrix_sha256": hashlib.sha256(protected).hexdigest(),
        "candidate_view_leak_count": 0,
        "by_family": manifest["by_family"],
        "source_sha256": {path: _sha(ROOT / path) for path in SOURCE_PATHS},
        "arms_executed": False,
        "outcome_accessed": False,
        "claim_boundary": "WORLD_AND_RESPONSE_IDENTITY_ONLY__NO_ARM_OUTPUT__NO_SCIENTIFIC_RESULT",
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
