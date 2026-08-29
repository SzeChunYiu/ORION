#!/usr/bin/env python3
"""Fail-closed cross-host comparator for the certified-neighborhood replay.

Environment identity is reported separately. Scientific booleans, strings,
integers, keys, list lengths, and non-finite values must agree exactly. Finite
floating values may differ only by a fixed machine-level tolerance; every such
difference is retained in the comparison receipt.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

ATOL = 1e-10
RTOL = 1e-10


def compare(observed: Any, registered: Any, path: str, differences: list[dict[str, Any]]) -> None:
    if isinstance(observed, bool) or isinstance(registered, bool):
        if type(observed) is not type(registered) or observed != registered:
            differences.append({"path": path, "kind": "exact", "observed": observed, "registered": registered})
        return
    if isinstance(observed, int) and isinstance(registered, int):
        if observed != registered:
            differences.append({"path": path, "kind": "integer", "observed": observed, "registered": registered})
        return
    if isinstance(observed, (int, float)) and isinstance(registered, (int, float)):
        left = float(observed)
        right = float(registered)
        if math.isnan(left) or math.isnan(right) or math.isinf(left) or math.isinf(right):
            if not (math.isnan(left) and math.isnan(right)) and left != right:
                differences.append({"path": path, "kind": "nonfinite", "observed": observed, "registered": registered})
            return
        if not math.isclose(left, right, rel_tol=RTOL, abs_tol=ATOL):
            differences.append({
                "path": path,
                "kind": "numeric",
                "observed": observed,
                "registered": registered,
                "absolute_difference": abs(left - right),
                "relative_difference": abs(left - right) / max(abs(right), ATOL),
            })
        return
    if type(observed) is not type(registered):
        differences.append({"path": path, "kind": "type", "observed": type(observed).__name__, "registered": type(registered).__name__})
        return
    if isinstance(observed, dict):
        for key in sorted(set(observed) | set(registered)):
            child = f"{path}/{key}"
            if key not in observed or key not in registered:
                differences.append({"path": child, "kind": "key", "observed_present": key in observed, "registered_present": key in registered})
            else:
                compare(observed[key], registered[key], child, differences)
        return
    if isinstance(observed, list):
        if len(observed) != len(registered):
            differences.append({"path": path, "kind": "length", "observed": len(observed), "registered": len(registered)})
        for index, (left, right) in enumerate(zip(observed, registered)):
            compare(left, right, f"{path}/{index}", differences)
        return
    if observed != registered:
        differences.append({"path": path, "kind": "exact", "observed": observed, "registered": registered})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--observed", type=Path, required=True)
    parser.add_argument("--registered", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    observed = json.loads(args.observed.read_text())
    registered = json.loads(args.registered.read_text())
    observed_environment = observed.pop("environment", None)
    registered_environment = registered.pop("environment", None)
    differences: list[dict[str, Any]] = []
    compare(observed, registered, "", differences)
    receipt = {
        "schema": "ORION02.CNBR.CrossHostReplayComparison.v1",
        "absolute_tolerance": ATOL,
        "relative_tolerance": RTOL,
        "scientific_equivalent": not differences,
        "differences": differences,
        "observed_environment": observed_environment,
        "registered_environment": registered_environment,
        "environment_excluded_from_scientific_projection": True,
        "authority": {
            "cross_host_byte_identity": False,
            "scientific_projection_equivalence": not differences,
            "external_independence": False,
            "journal_authority": False,
        },
    }
    args.output.write_text(json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n")
    if differences:
        for row in differences[:100]:
            print(json.dumps(row, sort_keys=True))
        raise SystemExit(f"scientific replay disagreement: {len(differences)} differences")
    print("ORION_02_CNBR_CROSS_HOST_SCIENTIFIC_EQUIVALENCE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
