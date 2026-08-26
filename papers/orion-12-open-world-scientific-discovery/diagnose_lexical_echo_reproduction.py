#!/usr/bin/env python3
"""Why the frozen lexical-echo result no longer equals a fresh run.

`test_p2_lexical_echo_successor.py::test_result_artifact_matches_a_fresh_run`
fails on `recorded["arms"] == payload["arms"]` while the assertions above it --
`parameters_sha256`, `verdict`, `world_content_hash` -- all pass. Read as
"the frozen digest matches but the numbers moved", that is alarming.

The current committed diagnosis observes only ulp-scale changes in reported
`mrr_at_50` values. The script derives that description from the measurements on
every run rather than assuming the same count, field set, or maximum ULP distance
will hold in another environment. No gate reads `mrr_at_50`: G1, G2, G3 and G5
read `hit_at_10`, G4 reads `hit_at_1`, and the smallest gate threshold is 0.01.

So the defect is in the comparison only when the measured checks below establish
that boundary. A reproduction check that demands bit-equality of a floating-point
mean across environments is asking for something no environment can promise,
which makes it an unattainable gate rather than a failed one.

Exit codes: 0 the diagnosis holds, 2 it does not, 3 CANNOT_CHECK.
"""

from __future__ import annotations

import json
import math
import platform
import sys
from pathlib import Path

# Fields any gate consumes. These must match exactly; the tolerance below is
# never allowed to touch them, or it would be laundering a real change.
GATE_READ_FIELDS = ("hit_at_1", "hit_at_10")


def ulp_distance(left: float, right: float, cap: int = 4096) -> int:
    if left == right:
        return 0
    low, high = min(left, right), max(left, right)
    steps = 0
    while low < high and steps < cap:
        low = math.nextafter(low, math.inf)
        steps += 1
    return steps


def walk(fresh, committed, path=""):
    if isinstance(fresh, dict) and isinstance(committed, dict):
        for key in sorted(set(fresh) | set(committed)):
            if key in fresh and key in committed:
                yield from walk(fresh[key], committed[key], f"{path}/{key}")
            else:
                yield (path + "/" + key, None, None, "PRESENT_ON_ONE_SIDE_ONLY")
    elif isinstance(fresh, list) and isinstance(committed, list) and len(fresh) == len(committed):
        for index, (a, b) in enumerate(zip(fresh, committed)):
            yield from walk(a, b, f"{path}[{index}]")
    elif fresh != committed:
        kind = "FLOAT" if isinstance(fresh, float) and isinstance(committed, float) else "NON_FLOAT"
        yield (path, fresh, committed, kind)


def build_finding(
    *,
    float_diffs: list[dict[str, object]],
    max_ulps: int,
    deterministic: bool,
    checks: dict[str, bool],
) -> str:
    """Describe exactly the measurements that support (or fail to support) the diagnosis."""
    fields = sorted({str(diff.get("field")) for diff in float_diffs})
    count = len(float_diffs)
    noun = "value" if count == 1 else "values"
    field_text = ", ".join(fields) if fields else "none"
    failing = sorted(name for name, passed in checks.items() if not passed)
    if failing:
        return (
            f"Diagnosis not established: {count} reported float {noun} differ; fields: "
            f"{field_text}; maximum distance is {max_ulps} ulps. Failing checks: "
            + ", ".join(failing)
            + "."
        )
    freshness = "bit-identical" if deterministic else "not bit-identical"
    return (
        f"{count} reported float {noun} differ; fields: {field_text}; maximum distance is "
        f"{max_ulps} ulps. Two fresh runs are {freshness} to each other, the frozen parameter "
        "digest still matches, and the verdict and every gate result are unchanged. No changed "
        "field is read by a registered gate."
    )


def main() -> int:
    try:
        from orion.study.p2 import echo_campaign as campaign
    except Exception as exc:
        print(json.dumps({"status": "CANNOT_CHECK", "error": str(exc)}))
        return 3

    first = campaign.run_campaign()
    second = campaign.run_campaign()
    deterministic = json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)

    committed = json.loads(Path(campaign.DEFAULT_OUTPUT).read_text(encoding="utf-8"))
    differences = list(walk(first["arms"], committed["arms"], ""))

    float_diffs, other_diffs = [], []
    for path, fresh, was, kind in differences:
        if kind == "FLOAT":
            float_diffs.append(
                {
                    "path": path,
                    "committed": was,
                    "fresh": fresh,
                    "ulps": ulp_distance(fresh, was),
                    "relative": abs(fresh - was) / max(abs(fresh), abs(was), 1e-300),
                    "field": path.rsplit("/", 1)[-1],
                }
            )
        else:
            other_diffs.append({"path": path, "committed": was, "fresh": fresh, "kind": kind})

    gate_fields_touched = sorted(
        {d["field"] for d in float_diffs if d["field"] in GATE_READ_FIELDS}
    )
    max_ulps = max((d["ulps"] for d in float_diffs), default=0)
    max_relative = max((d["relative"] for d in float_diffs), default=0.0)

    checks = {
        "two_fresh_runs_are_bit_identical": deterministic,
        "frozen_parameter_digest_still_matches":
            committed.get("parameters_sha256") == campaign.frozen_digest(),
        "verdict_unchanged": committed.get("verdict") == first.get("verdict"),
        "world_content_hash_unchanged":
            committed.get("world_content_hash") == first.get("world_content_hash"),
        "gate_results_unchanged": committed.get("gate_results") == first.get("gate_results"),
        "no_non_float_difference": not other_diffs,
        "no_gate_read_field_differs": not gate_fields_touched,
        "every_float_difference_is_within_four_ulps": max_ulps <= 4,
    }
    finding = build_finding(
        float_diffs=float_diffs,
        max_ulps=max_ulps,
        deterministic=deterministic,
        checks=checks,
    )

    print(
        json.dumps(
            {
                "schema": "orion.p2.lexical-echo-reproduction-diagnosis.v1",
                "record": "P2_LEXICAL_ECHO_REPRODUCTION_DIAGNOSIS",
                "authority_scope": "DIAGNOSIS_ONLY",
                "relabels_nothing": "The frozen result and its verdict are untouched.",
                "environment": {
                    "python": platform.python_version(),
                    "platform": platform.platform(),
                },
                "gate_read_fields": list(GATE_READ_FIELDS),
                "smallest_gate_threshold": 0.01,
                "float_differences": float_diffs,
                "non_float_differences": other_diffs,
                "max_ulps": max_ulps,
                "max_relative_difference": max_relative,
                "checks": checks,
                "finding": finding,
                "consequence": (
                    "The failure is a comparison defect only when the measured checks above pass. "
                    "Bit-equality of a floating-point mean is not attainable across library "
                    "versions, so a reproduction check that demands it is an unattainable gate. "
                    "The check should compare gate-read fields and all non-float values exactly, "
                    "and permit a declared ulp-scale difference only on reported floats no gate "
                    "consumes."
                ),
                "all_checks_pass": all(checks.values()),
            },
            indent=2,
        )
    )
    return 0 if all(checks.values()) else 2


if __name__ == "__main__":
    sys.exit(main())
