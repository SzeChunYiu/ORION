#!/usr/bin/env python3
"""Diagnose R23 parent replay drift without executing any R24 policy."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import subprocess
from typing import Any


HERE = Path(__file__).resolve().parent
R23_EXECUTOR = HERE.parent / "r23-density-backoff-revival" / "fiberguard_pmlb_proposal_ordering_r23.py"
R23_RESULT = HERE.parent / "r23-density-backoff-revival" / "FIBERGUARD_PMLB_PROPOSAL_ORDERING_R23_RESULTS.json"
R23_EXECUTOR_SHA256 = "6bb4e377462249c3630ceacc56073ba385a82805c79eda58809c42b8ee1562aa"
R23_RESULT_SHA256 = "cf1a0db71ab135278b64c02633f07d05a23604a121f0b62743f4e59c6358fc77"
PMLB_COMMIT = "7c1f4bdc00136dc2e55c87fa6b8ba6e8af6d1a68"
PMLB_TREE = "ca5d36e9093c2f7360db57198c8c0586a3217a60"
MISSING = object()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _shown(value: Any) -> Any:
    if value is MISSING:
        return "<MISSING>"
    text = canonical_json(value)
    return value if len(text) <= 400 else text[:400] + "..."


def structured_diff(frozen: Any, replay: Any, sample_limit: int = 100) -> dict[str, Any]:
    """Return deterministic JSON-path differences without normalizing values."""
    rows: list[dict[str, Any]] = []
    numeric_deltas: list[float] = []

    def add(path: str, kind: str, left: Any, right: Any) -> None:
        row = {"path": path, "kind": kind, "frozen": _shown(left), "replay": _shown(right)}
        if (
            left is not MISSING
            and right is not MISSING
            and isinstance(left, (int, float))
            and not isinstance(left, bool)
            and isinstance(right, (int, float))
            and not isinstance(right, bool)
        ):
            delta = abs(float(left) - float(right))
            row["abs_numeric_difference"] = delta
            numeric_deltas.append(delta)
        rows.append(row)

    def walk(left: Any, right: Any, path: str) -> None:
        if left is MISSING or right is MISSING:
            add(path, "missing", left, right)
            return
        if type(left) is not type(right):
            add(path, "type", left, right)
            return
        if isinstance(left, dict):
            for key in sorted(set(left) | set(right)):
                child = f"{path}.{key}"
                walk(left.get(key, MISSING), right.get(key, MISSING), child)
            return
        if isinstance(left, list):
            for index in range(max(len(left), len(right))):
                walk(
                    left[index] if index < len(left) else MISSING,
                    right[index] if index < len(right) else MISSING,
                    f"{path}[{index}]",
                )
            return
        if left != right:
            add(path, "value", left, right)

    walk(frozen, replay, "$")
    return {
        "difference_count": len(rows),
        "numeric_difference_count": len(numeric_deltas),
        "max_abs_numeric_difference": max(numeric_deltas, default=0.0),
        "samples_truncated": len(rows) > sample_limit,
        "samples": rows[:sample_limit],
    }


def load_r23():
    data = R23_EXECUTOR.read_bytes()
    if sha256_bytes(data) != R23_EXECUTOR_SHA256:
        raise RuntimeError("R23 executor binding drift")
    spec = importlib.util.spec_from_file_location("orion02_r23_parent_diagnostic", R23_EXECUTOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen R23 executor")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git_value(repo: Path, expression: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(repo), "rev-parse", expression], text=True
    ).strip()


def first_byte_difference(left: bytes, right: bytes) -> int | None:
    for index, (a, b) in enumerate(zip(left, right)):
        if a != b:
            return index
    return None if len(left) == len(right) else min(len(left), len(right))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--subject-repo", required=True, type=Path)
    parser.add_argument("--fresh-parent-output", required=True, type=Path)
    parser.add_argument("--diagnostic-output", required=True, type=Path)
    args = parser.parse_args()

    subject = args.subject_repo.resolve()
    if git_value(subject, "HEAD") != PMLB_COMMIT:
        raise SystemExit("pinned PMLB commit drift")
    if git_value(subject, "HEAD^{tree}") != PMLB_TREE:
        raise SystemExit("pinned PMLB tree drift")
    frozen_bytes = R23_RESULT.read_bytes()
    if sha256_bytes(frozen_bytes) != R23_RESULT_SHA256:
        raise SystemExit("frozen R23 result binding drift")

    r23 = load_r23()
    parent, _ = r23.execute(
        subject,
        r23.R22_FREEZE.resolve(),
        r23.R22_RESULT.resolve(),
    )
    fresh_bytes = (r23.canonical_json(parent) + "\n").encode()
    args.fresh_parent_output.write_bytes(fresh_bytes)
    diff = structured_diff(json.loads(frozen_bytes), json.loads(fresh_bytes))
    identical = fresh_bytes == frozen_bytes
    receipt = {
        "schema": "ORION.FiberGuard.R24.R23ParentReplayDiagnostic.v1",
        "terminal": (
            "R23_PARENT_REPLAY_BYTE_IDENTICAL"
            if identical
            else "R23_PARENT_REPLAY_BYTE_DRIFT_DIAGNOSED"
        ),
        "attempt_id": "ORION02-REVIVAL-002-R24-ARM-CONDITIONAL-BOUNDARY-FIBRES",
        "counts_toward_100": False,
        "r24_policy_executed": False,
        "r24_scientific_outcome_exposed": False,
        "purpose": "post-job-3550259 infrastructure diagnosis only",
        "pmlb_commit": PMLB_COMMIT,
        "pmlb_tree": PMLB_TREE,
        "r23_executor_sha256": R23_EXECUTOR_SHA256,
        "frozen_parent": {
            "path": str(R23_RESULT),
            "bytes": len(frozen_bytes),
            "sha256": sha256_bytes(frozen_bytes),
        },
        "fresh_parent": {
            "path": str(args.fresh_parent_output),
            "bytes": len(fresh_bytes),
            "sha256": sha256_bytes(fresh_bytes),
        },
        "byte_identical": identical,
        "first_byte_difference_offset": first_byte_difference(frozen_bytes, fresh_bytes),
        "structured_diff": diff,
        "environment": {
            "python": platform.python_version(),
            "machine": platform.machine(),
            "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED"),
            "OPENBLAS_NUM_THREADS": os.environ.get("OPENBLAS_NUM_THREADS"),
            "OMP_NUM_THREADS": os.environ.get("OMP_NUM_THREADS"),
            "MKL_NUM_THREADS": os.environ.get("MKL_NUM_THREADS"),
        },
        "authority": {
            "scientific_authority_delta": "NONE",
            "submission_authorized": False,
            "top_tier_gate_pass": False,
            "freeze_authorized": False,
        },
    }
    args.diagnostic_output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["terminal"])
    print("FROZEN_PARENT_SHA256 " + receipt["frozen_parent"]["sha256"])
    print("FRESH_PARENT_SHA256 " + receipt["fresh_parent"]["sha256"])
    print("STRUCTURED_DIFFERENCE_COUNT " + str(diff["difference_count"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
