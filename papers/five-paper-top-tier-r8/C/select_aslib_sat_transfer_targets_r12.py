#!/usr/bin/env python3
"""Prospective metadata-only target selector for FiberGuard ASlib transfer R12.

The locked representation is {Pre, lobjois}, selected previously on SAT12-ALL.
This selector is deliberately outcome-blind: it reads only Git tree path names and
scenario description.txt blobs. It never reads algorithm_runs, feature_values,
feature_costs, feature_runstatus, ground truth, or CV outcome content.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any

import yaml

SCHEMA = "ORION.FiberGuard.ASlibSATTransferEligibility.R12.v1"
ASLIB_COMMIT = "551b22beef8df17de59286b4822ef720e0aa4d6f"
SOURCE_SCENARIO = "SAT12-ALL"
SOURCE_RESULT_SHA256 = "7c0778836101d5fe44b024e302c3fc0848faf5a994fc1e51b80831d82fd5e652"
LOCKED_STEPS = ("Pre", "lobjois")
REQUIRED_FILES = (
    "description.txt",
    "algorithm_runs.arff",
    "feature_values.arff",
    "feature_costs.arff",
    "feature_runstatus.arff",
)
SAT_NAME = re.compile(r"^SAT[0-9].*")


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(repo), *args], text=True, stderr=subprocess.STDOUT
    ).strip()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def dependency_closure(
    selected: tuple[str, ...], feature_steps: dict[str, dict[str, Any]]
) -> tuple[str, ...]:
    closure = set(selected)
    changed = True
    while changed:
        changed = False
        for step in tuple(closure):
            cfg = feature_steps.get(step)
            if cfg is None:
                continue
            requirements = cfg.get("requires", []) or []
            if isinstance(requirements, str):
                requirements = [requirements]
            for required in requirements:
                if required not in closure:
                    closure.add(required)
                    changed = True
    return tuple(sorted(closure))


def normalize_performance_type(raw: Any) -> tuple[str, ...]:
    if raw is None:
        return ()
    if isinstance(raw, str):
        return (raw.lower(),)
    if isinstance(raw, list):
        return tuple(str(x).lower() for x in raw)
    return (str(raw).lower(),)


def run(repo: Path) -> dict[str, Any]:
    head = git(repo, "rev-parse", "HEAD")
    if head != ASLIB_COMMIT:
        raise ValueError(f"ASlib HEAD mismatch: {head} != {ASLIB_COMMIT}")

    paths = set(git(repo, "ls-tree", "-r", "--name-only", "HEAD").splitlines())
    scenario_names = sorted(
        {
            path.split("/", 1)[0]
            for path in paths
            if "/" in path and SAT_NAME.match(path.split("/", 1)[0])
        }
    )

    eligible: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    descriptions_read: list[str] = []

    for scenario in scenario_names:
        reasons: list[str] = []
        required_paths = [f"{scenario}/{name}" for name in REQUIRED_FILES]
        missing = [path for path in required_paths if path not in paths]
        if missing:
            reasons.append("missing_required_paths:" + ",".join(missing))

        description_path = f"{scenario}/description.txt"
        if description_path not in paths:
            excluded.append({"scenario": scenario, "reasons": reasons or ["missing_description"]})
            continue

        text = git(repo, "show", f"HEAD:{description_path}")
        descriptions_read.append(description_path)
        desc = yaml.safe_load(text)
        if not isinstance(desc, dict):
            reasons.append("description_not_mapping")
            desc = {}

        performance_types = normalize_performance_type(desc.get("performance_type"))
        if performance_types and "runtime" not in performance_types:
            reasons.append("non_runtime_performance_type:" + ",".join(performance_types))

        try:
            cutoff = float(desc.get("algorithm_cutoff_time"))
            if not cutoff > 0:
                raise ValueError
        except (TypeError, ValueError):
            cutoff = None
            reasons.append("invalid_algorithm_cutoff_time")

        feature_steps = desc.get("feature_steps") or {}
        if not isinstance(feature_steps, dict):
            feature_steps = {}
            reasons.append("feature_steps_not_mapping")

        missing_steps = [step for step in LOCKED_STEPS if step not in feature_steps]
        if missing_steps:
            reasons.append("missing_locked_steps:" + ",".join(missing_steps))
            closure: tuple[str, ...] = ()
        else:
            closure = dependency_closure(LOCKED_STEPS, feature_steps)
            if closure != tuple(sorted(LOCKED_STEPS)):
                reasons.append("locked_step_dependency_closure_changed:" + ",".join(closure))

        # Keep the source scenario visible as a calibration row, but never call
        # it a transfer target.
        if scenario == SOURCE_SCENARIO:
            reasons.append("source_calibration_scenario")

        row = {
            "scenario": scenario,
            "description_blob_sha1": git(repo, "rev-parse", f"HEAD:{description_path}"),
            "algorithm_cutoff_time": cutoff,
            "performance_type": list(performance_types),
            "locked_steps": list(LOCKED_STEPS),
            "locked_step_dependency_closure": list(closure),
        }
        if reasons:
            row["reasons"] = reasons
            excluded.append(row)
        else:
            eligible.append(row)

    result = {
        "schema": SCHEMA,
        "status": "ELIGIBILITY_FROZEN",
        "authority": {
            "metadata_only": True,
            "target_algorithm_outcomes_read": False,
            "target_feature_values_read": False,
            "target_feature_cost_values_read": False,
            "target_runstatus_values_read": False,
            "target_ground_truth_read": False,
            "target_cv_outcomes_read": False,
            "representation_reselection_allowed": False,
        },
        "upstream": {
            "commit": ASLIB_COMMIT,
            "source_scenario": SOURCE_SCENARIO,
            "source_result_sha256": SOURCE_RESULT_SHA256,
        },
        "locked_representation": list(LOCKED_STEPS),
        "eligibility_rule": {
            "scenario_name_regex": SAT_NAME.pattern,
            "required_files": list(REQUIRED_FILES),
            "performance_type": "runtime_if_declared",
            "positive_numeric_algorithm_cutoff": True,
            "locked_steps_present": True,
            "locked_dependency_closure_exact": list(sorted(LOCKED_STEPS)),
            "source_scenario_excluded_from_transfer": True,
        },
        "sat_scenarios_seen": len(scenario_names),
        "description_blobs_read": descriptions_read,
        "eligible_count": len(eligible),
        "eligible": eligible,
        "excluded_count": len(excluded),
        "excluded": excluded,
    }
    payload = canonical_json(result).encode()
    result["content_sha256"] = hashlib.sha256(payload).hexdigest()
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--aslib-git-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.aslib_git_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(canonical_json(result) + "\n", encoding="utf-8")
    print(
        "FIBERGUARD_ASLIB_TRANSFER_ELIGIBILITY_FROZEN",
        f"sat_seen={result['sat_scenarios_seen']}",
        f"eligible={result['eligible_count']}",
        "targets=" + ",".join(row["scenario"] for row in result["eligible"]),
    )


if __name__ == "__main__":
    main()
