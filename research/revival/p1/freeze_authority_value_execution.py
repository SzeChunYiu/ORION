#!/usr/bin/env python3
"""Bind the exact P1 authority-value evaluator/arms after holdout freeze.

This step runs **no candidate arm**. It converts a valid HOLDOUT_FREEZE into an
execution identity that later outcome code must reproduce byte-for-byte.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from freeze_authority_value_holdout import DEFAULT_PROTOCOL, ROOT, load_effective_protocol  # noqa: E402
from orion.study.p1_causal.authority_value_policies import MATCHED_ARMS  # noqa: E402

EXECUTION_SOURCE_PATHS = (
    "research/revival/p1/run_authority_value_campaign.py",
    "src/orion/study/p1_causal/authority_value_policies.py",
    "src/orion/study/p1_causal/authority_value_scoring.py",
    "src/orion/study/p1_causal/authority_value_statistics.py",
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def freeze_execution(protocol_path: Path, holdout_dir: Path, out: Path) -> dict:
    protocol, protocol_identity = load_effective_protocol(protocol_path)
    holdout_path = holdout_dir / "HOLDOUT_FREEZE.json"
    holdout = json.loads(holdout_path.read_text())
    public_path = holdout_dir / "PUBLIC_CASES.jsonl"
    gold_path = holdout_dir / "PROTECTED_GOLD.jsonl"

    if holdout.get("arms_executed") is not False:
        raise ValueError("holdout freeze already records arm execution")
    if holdout.get("protocol_chain", {}).get("chain_sha256") != protocol_identity["chain_sha256"]:
        raise ValueError("holdout/protocol chain mismatch")
    if _sha(public_path) != holdout.get("public_sha256"):
        raise ValueError("public holdout bytes drifted")
    if _sha(gold_path) != holdout.get("protected_gold_sha256"):
        raise ValueError("protected gold bytes drifted")
    if int(holdout.get("n", -1)) != int(protocol["fresh_holdout_plan"]["base_task_count"]):
        raise ValueError("holdout count drifted")

    rules = protocol["primary_decision_rule"]
    parameters = protocol["decision_parameters"]
    matched_arm_ids = tuple(str(item["id"]) for item in protocol["matched_arms"])
    available_arm_ids = {policy.__name__ for policy in MATCHED_ARMS}
    if len(set(matched_arm_ids)) != len(matched_arm_ids):
        raise ValueError("protocol matched-arm identities are duplicated")
    missing_arm_ids = sorted(set(matched_arm_ids) - available_arm_ids)
    if missing_arm_ids:
        raise ValueError(f"protocol matched-arm implementation missing:{missing_arm_ids}")
    expected_authority_raw = parameters.get("expected_authority_critical_n")
    expected_authority_n = (
        None if expected_authority_raw is None else int(expected_authority_raw)
    )
    if expected_authority_n is not None and int(
        holdout.get("authority_critical_n", -1)
    ) != expected_authority_n:
        raise ValueError("holdout authority-critical denominator drifted")
    binding = {
        "schema_version": "P1.authority-value-execution-freeze.v1",
        "protocol_id": protocol["protocol_id"],
        "protocol_version": protocol["protocol_version"],
        "protocol_chain_sha256": protocol_identity["chain_sha256"],
        "holdout_freeze_sha256": _sha(holdout_path),
        "public_sha256": holdout["public_sha256"],
        "protected_gold_sha256": holdout["protected_gold_sha256"],
        "n": holdout["n"],
        "authority_critical_n": (
            expected_authority_n
            if expected_authority_n is not None
            else holdout.get("authority_critical_n")
        ),
        "primary_arm": "orion_typed_permission_dependency_reopen",
        "primary_comparator": protocol["primary_hypothesis"]["primary_comparator"],
        "matched_arm_ids": list(matched_arm_ids),
        "primary_decision_rule": rules,
        "decision_parameters": parameters,
        "source_sha256": {path: _sha(ROOT / path) for path in EXECUTION_SOURCE_PATHS},
        "arms_executed": False,
        "outcome_accessed": False,
        "claim_boundary": "EXECUTION_IDENTITY_ONLY__NO_ARM_OUTPUT__NO_SCIENTIFIC_RESULT",
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(binding, indent=2, sort_keys=True) + "\n")
    return binding


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument("--holdout-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    binding = freeze_execution(args.protocol, args.holdout_dir, args.out)
    print(json.dumps(binding, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
