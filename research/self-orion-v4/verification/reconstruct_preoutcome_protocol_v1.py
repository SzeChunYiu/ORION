#!/usr/bin/env python3
"""Reconstruct the Self-ORION V4 pre-outcome protocol from the frozen constructor.

This is a custody audit, not a scientific rerun. The V4 execution commit stores a
post-outcome protocol at the same path whose execution receipt binds the earlier
pre-outcome bytes. The exact pre-outcome protocol is deterministically rebuilt by
the already-frozen constructor, hashed, and all files touched by that constructor
are restored byte-for-byte before this program exits.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CONF = ROOT / "research/self-orion-v4/confirmatory"
PROTOCOL = ROOT / "papers/orion-15-self-orion/protocol/SELF_ORION_V4_REVISION_LEVEL_PROTOCOL_V1.json"
FREEZE_RECEIPT = CONF / "CONFIRMATORY_FREEZE_RECEIPT_2026-08-27.json"
CONSTRUCTOR = CONF / "freeze_confirmatory_v4.py"
OUT = Path(__file__).resolve().parent / "PREOUTCOME_PROTOCOL_RECONSTRUCTION_V1.json"


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def require(ok: bool, msg: str) -> None:
    if not ok:
        raise AssertionError(msg)


def main() -> int:
    original_protocol = PROTOCOL.read_bytes()
    original_freeze = FREEZE_RECEIPT.read_bytes()
    freeze = json.loads(original_freeze)
    expected = freeze["digests"]["protocol_sha256"]
    post_outcome_sha = sha_bytes(original_protocol)
    regenerated_bytes: bytes | None = None
    proc_stdout = ""
    try:
        env = dict(os.environ)
        env["PYTHONPATH"] = str(ROOT / "src") + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
        proc = subprocess.run(
            [sys.executable, str(CONSTRUCTOR)],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
        )
        proc_stdout = proc.stdout
        require(proc.returncode == 0, f"constructor rc={proc.returncode}: {proc.stdout}\n{proc.stderr}")
        regenerated_bytes = PROTOCOL.read_bytes()
        regenerated = json.loads(regenerated_bytes)
        require(regenerated["outcome_accessed"] is False, "regenerated protocol is not pre-outcome")
        require(regenerated["confirmatory_execution_bindings"]["outcome_accessed"] is False, "binding outcome_accessed not false")
        require("confirmatory_execution_receipt" not in regenerated, "pre-outcome protocol unexpectedly contains execution receipt")
        require(sha_bytes(regenerated_bytes) == expected, f"pre-outcome protocol digest mismatch: {sha_bytes(regenerated_bytes)} != {expected}")
    finally:
        PROTOCOL.write_bytes(original_protocol)
        FREEZE_RECEIPT.write_bytes(original_freeze)

    require(PROTOCOL.read_bytes() == original_protocol, "post-outcome protocol restore failed")
    require(FREEZE_RECEIPT.read_bytes() == original_freeze, "freeze receipt restore failed")
    require(regenerated_bytes is not None, "no reconstructed protocol bytes")

    proof = {
        "schema": "ORION.PreOutcomeProtocolReconstruction.v1",
        "paper_id": "ORION-15",
        "protocol_id": "P5.self-orion-v4.revision-level.v1",
        "constructor": str(CONSTRUCTOR.relative_to(ROOT)),
        "constructor_sha256": sha_file(CONSTRUCTOR),
        "freeze_receipt": str(FREEZE_RECEIPT.relative_to(ROOT)),
        "freeze_receipt_sha256": sha_bytes(original_freeze),
        "expected_preoutcome_protocol_sha256": expected,
        "regenerated_preoutcome_protocol_sha256": sha_bytes(regenerated_bytes),
        "post_outcome_protocol_sha256": post_outcome_sha,
        "preoutcome_regenerated_from_frozen_constructor": True,
        "post_outcome_bytes_restored_exactly": True,
        "scientific_execution_rerun": False,
        "grants_scientific_authority": False,
        "status": "PASS",
        "terminal": "ORION_15_V4_PREOUTCOME_PROTOCOL_CUSTODY_RECONSTRUCTED",
    }
    OUT.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(proof["terminal"])
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"ORION_15_V4_PROTOCOL_RECONSTRUCTION=FAIL: {exc}", file=sys.stderr)
        raise SystemExit(2)
