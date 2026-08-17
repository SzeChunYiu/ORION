#!/usr/bin/env python3
"""Materialize and bind the P1 authority-value holdout without running any arm.

The effective protocol is an immutable base plus an optional pre-confirmatory
amendment.  The freezer binds the whole protocol chain so a later execution
cannot silently evaluate the easier predecessor decision rule.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from orion.study.p1_causal.authority_value_cases import (
    generate_authority_value_tasks,
    serialize_gold,
    serialize_public,
    task_manifest,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PROTOCOL = (
    ROOT
    / "research"
    / "revival"
    / "p1"
    / "protocol"
    / "P1.authority-value.v2.1.1.json"
)
SOURCE_PATHS = (
    "src/orion/study/p1_causal/authority_value_cases.py",
    "src/orion/study/p1_causal/authority_value_policies.py",
    "src/orion/study/p1_causal/authority_value_scoring.py",
    "research/revival/p1/P1_DONOR_ASSIMILATION_LEDGER_V1.json",
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data).hexdigest()


def load_effective_protocol(protocol_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return effective protocol plus immutable chain identity.

    Direct base protocols are accepted for development tooling.  Publication
    freezing uses the amendment path by default.
    """

    raw = protocol_path.read_bytes()
    payload = json.loads(raw)
    if payload.get("schema_version") != "orion.publication-protocol-amendment.v1":
        if payload.get("protocol_status") != "DESIGN_FROZEN":
            raise ValueError("authority-value protocol is not DESIGN_FROZEN")
        if payload.get("outcome_accessed") is not False:
            raise ValueError("authority-value protocol records outcome access")
        identity = {
            "kind": "base_only",
            "base_path": str(protocol_path.relative_to(ROOT)),
            "base_sha256": hashlib.sha256(raw).hexdigest(),
            "base_git_blob_sha": _git_blob_sha(raw),
            "effective_protocol_version": payload["protocol_version"],
            "chain_sha256": hashlib.sha256(raw).hexdigest(),
        }
        return payload, identity

    if payload.get("protocol_status") != "DESIGN_FROZEN":
        raise ValueError("authority-value amendment is not DESIGN_FROZEN")
    if payload.get("confirmatory_outcome_accessed") is not False:
        raise ValueError("authority-value amendment records confirmatory outcome access")
    base_rel = Path(str(payload["base_protocol_path"]))
    base_path = ROOT / base_rel
    base_raw = base_path.read_bytes()
    base = json.loads(base_raw)
    if base.get("protocol_status") != "DESIGN_FROZEN":
        raise ValueError("amendment base is not DESIGN_FROZEN")
    if base.get("outcome_accessed") is not False:
        raise ValueError("amendment base records outcome access")
    if base.get("protocol_version") != payload.get("base_protocol_version"):
        raise ValueError("amendment base protocol version mismatch")
    actual_blob = _git_blob_sha(base_raw)
    if actual_blob != payload.get("base_protocol_git_blob_sha"):
        raise ValueError("amendment base Git blob identity mismatch")

    effective = copy.deepcopy(base)
    overrides = payload.get("overrides", {})
    if not isinstance(overrides, dict):
        raise ValueError("amendment overrides must be an object")
    for key, value in overrides.items():
        effective[key] = copy.deepcopy(value)
    effective["protocol_version"] = payload["protocol_version"]
    effective["effective_amendment_path"] = str(protocol_path.relative_to(ROOT))
    effective["confirmatory_outcome_accessed"] = False

    chain_material = base_raw + b"\0" + raw
    identity = {
        "kind": "base_plus_amendment",
        "base_path": str(base_rel),
        "base_sha256": hashlib.sha256(base_raw).hexdigest(),
        "base_git_blob_sha": actual_blob,
        "amendment_path": str(protocol_path.relative_to(ROOT)),
        "amendment_sha256": hashlib.sha256(raw).hexdigest(),
        "amendment_git_blob_sha": _git_blob_sha(raw),
        "effective_protocol_version": effective["protocol_version"],
        "chain_sha256": hashlib.sha256(chain_material).hexdigest(),
    }
    return effective, identity


def freeze(protocol_path: Path, outdir: Path) -> dict:
    protocol, protocol_identity = load_effective_protocol(protocol_path)
    plan = protocol["fresh_holdout_plan"]
    seed = int(plan["confirmatory_seed"])
    expected_n = int(plan["base_task_count"])

    tasks = generate_authority_value_tasks(seed=seed)
    manifest = task_manifest(tasks)
    if manifest["n"] != expected_n:
        raise ValueError(f"holdout count drift: {manifest['n']} != {expected_n}")
    if manifest["candidate_view_leak_count"] != 0:
        raise ValueError("candidate-view leak detected before arm execution")

    public_bytes = serialize_public(tasks)
    gold_bytes = serialize_gold(tasks)
    public_ids = [json.loads(line)["task_id"] for line in public_bytes.decode().splitlines()]
    gold_ids = [json.loads(line)["task_id"] for line in gold_bytes.decode().splitlines()]
    if public_ids != gold_ids or len(set(public_ids)) != expected_n:
        raise ValueError("public/gold task identity mismatch or duplicate")

    bindings = {
        "schema_version": "P1.authority-value-holdout-freeze.v1",
        "protocol_id": protocol["protocol_id"],
        "protocol_version": protocol["protocol_version"],
        "protocol_chain": protocol_identity,
        "primary_comparator": protocol["primary_hypothesis"]["primary_comparator"],
        "confirmatory_seed": seed,
        "n": expected_n,
        "public_sha256": hashlib.sha256(public_bytes).hexdigest(),
        "protected_gold_sha256": hashlib.sha256(gold_bytes).hexdigest(),
        "candidate_view_leak_count": 0,
        "arms_executed": False,
        "source_sha256": {path: _sha(ROOT / path) for path in SOURCE_PATHS},
        "by_family": manifest["by_family"],
        "claim_boundary": "HOLDOUT_IDENTITY_ONLY__NO_ARM_OUTPUT__NO_SCIENTIFIC_RESULT",
    }
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "PUBLIC_CASES.jsonl").write_bytes(public_bytes)
    (outdir / "PROTECTED_GOLD.jsonl").write_bytes(gold_bytes)
    (outdir / "HOLDOUT_FREEZE.json").write_text(
        json.dumps(bindings, indent=2, sort_keys=True) + "\n"
    )
    return bindings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    binding = freeze(args.protocol, args.outdir)
    print(json.dumps(binding, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
