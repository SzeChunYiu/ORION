from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Iterable, Sequence

from orion.study.p3_public_reference import load_jsonl, summarize
from orion.study.p3_public_reference_analysis import analyze

FALSE_MERGE_SUPERIORITY_MARGIN = -0.05
FALSE_SPLIT_NONINFERIORITY_MARGIN = 0.03


def confirmatory_verdict(analysis: dict[str, object]) -> dict[str, object]:
    primary = analysis["primary_comparisons"]
    assert isinstance(primary, dict)
    fm = primary["false_merge_orion_minus_flat"]
    fs = primary["false_split_orion_minus_exact"]
    assert isinstance(fm, dict) and isinstance(fs, dict)
    fm_point = float(fm["candidate_minus_baseline"])
    fm_high = float(fm["ci95_high"])
    fs_point = float(fs["candidate_minus_baseline"])
    fs_high = float(fs["ci95_high"])
    superiority = fm_point <= FALSE_MERGE_SUPERIORITY_MARGIN and fm_high < 0.0
    noninferiority = fs_point <= FALSE_SPLIT_NONINFERIORITY_MARGIN and fs_high <= FALSE_SPLIT_NONINFERIORITY_MARGIN
    return {
        "false_merge_superiority": superiority,
        "false_split_noninferiority": noninferiority,
        "confirmatory_primary_pass": bool(superiority and noninferiority),
        "rules": {
            "false_merge": (
                "ORION-minus-flat point estimate <= -0.05 and upper bound of the "
                "paired 95% bootstrap CI < 0"
            ),
            "false_split": (
                "ORION-minus-exact point estimate <= +0.03 and upper bound of the "
                "paired 95% bootstrap CI <= +0.03"
            ),
        },
    }


def _stratified(cases: Sequence[dict[str, object]], key: str) -> dict[str, object]:
    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for case in cases:
        groups[str(case[key])].append(case)
    return {name: summarize(group) for name, group in sorted(groups.items())}


def analyze_confirmatory(cases: Sequence[dict[str, object]]) -> dict[str, object]:
    pooled = analyze(cases)
    return {
        "schema_version": "orion.p3.public-reference-confirmatory-analysis.v1",
        "case_count": len(cases),
        "pooled": pooled,
        "confirmatory_verdict": confirmatory_verdict(pooled),
        "by_discipline": _stratified(cases, "discipline"),
        "by_case_family": _stratified(cases, "case_family"),
        "inference_policy": {
            "primary": "confirmatory verdict is based only on the two predeclared paired primary comparisons",
            "ablations": "descriptive paired intervals only; no significance claims and no multiplicity-adjusted p-values",
            "relationship_to_primary_run": "the earlier 32-case result is not pooled into the confirmatory verdict",
            "stochastic_repeats": 1,
            "reason": "the evaluated mapping rules are deterministic",
        },
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Analyze the frozen disjoint ORION-P3 public-reference confirmatory holdout")
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    report = analyze_confirmatory(load_jsonl(args.cases))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
