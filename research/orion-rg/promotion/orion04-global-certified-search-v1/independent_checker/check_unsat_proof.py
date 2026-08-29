#!/usr/bin/env python3
"""Bind an OPB instance and proof to a pinned external proof-checker result."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Sequence

POSITIVE = "ORION04_C0_31_PROVED__D4_C5CUBED_EXACT_30"
NEGATIVE = "ORION04_GLOBAL_CERTIFIED_SEARCH_CANNOT_CHECK"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--instance", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--proof", type=Path, required=True)
    parser.add_argument("--checker", type=Path, required=True)
    parser.add_argument("--expected-checker-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--checker-argument-order",
        choices=("instance-proof", "proof-instance"),
        default="instance-proof",
    )
    args = parser.parse_args(argv)

    manifest = json.loads(args.manifest.read_text())
    checker_digest = sha256(args.checker)
    instance_digest = sha256(args.instance)
    proof_digest = sha256(args.proof)
    parameters = manifest.get("parameters", {})
    checks = {
        "registered_schema": manifest.get("schema")
        == "ORION.ORION04.GlobalCertifiedSearchInstanceManifest.v1",
        "registered_protocol": manifest.get("protocol_id")
        == "ORION04.D4.GLOBAL_CERTIFIED_SEARCH.v1",
        "registered_full_parameters": parameters
        == {
            "prime": 5,
            "rank": 3,
            "length": 31,
            "support_lower_bound": 14,
            "max_short_length": 5,
            "positive_multiplicities": [1, 2, 4],
        },
        "instance_digest": manifest.get("opb_sha256") == instance_digest,
        "checker_digest": checker_digest == args.expected_checker_sha256,
        "proof_nonempty": args.proof.stat().st_size > 0,
        "manifest_has_no_preclaimed_authority": manifest.get("c0_31_authority") is False
        and manifest.get("exact_d4_authority") is False
        and manifest.get("proof_checked") is False,
    }

    if args.checker_argument_order == "instance-proof":
        command = [str(args.checker), str(args.instance), str(args.proof)]
    else:
        command = [str(args.checker), str(args.proof), str(args.instance)]

    completed: subprocess.CompletedProcess[str] | None = None
    if all(checks.values()):
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
        checks["external_checker_exit_zero"] = completed.returncode == 0
    else:
        checks["external_checker_exit_zero"] = False

    positive = all(checks.values())
    report: dict[str, Any] = {
        "schema": "ORION.ORION04.GlobalCertifiedSearchProofReceipt.v1",
        "protocol_id": "ORION04.D4.GLOBAL_CERTIFIED_SEARCH.v1",
        "instance_sha256": instance_digest,
        "proof_sha256": proof_digest,
        "checker_path": str(args.checker),
        "checker_sha256": checker_digest,
        "checker_command": command,
        "checker_returncode": None if completed is None else completed.returncode,
        "checker_stdout_sha256": None
        if completed is None
        else hashlib.sha256(completed.stdout.encode()).hexdigest(),
        "checker_stderr_sha256": None
        if completed is None
        else hashlib.sha256(completed.stderr.encode()).hexdigest(),
        "checks": checks,
        "terminal": POSITIVE if positive else NEGATIVE,
        "c0_31_authority": positive,
        "exact_d4_30_authority": positive,
        "exact_d4_31_authority": False,
        "novelty_authority": False,
        "venue_authority": False,
    }
    unsigned = dict(report)
    report["receipt_digest"] = hashlib.sha256(canonical(unsigned).encode()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        "ORION04_UNSAT_PROOF_CHECK="
        + canonical(
            {
                "terminal": report["terminal"],
                "all_checks": all(checks.values()),
                "receipt_digest": report["receipt_digest"],
            }
        )
    )
    return 0 if positive else 1


if __name__ == "__main__":
    raise SystemExit(main())
