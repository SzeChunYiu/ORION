#!/usr/bin/env python3
"""Attribute ORION-11's measured advantage to a conjunct of the frozen criterion.

`analysis/discriminating-power-v1` reports that six of six ablation comparisons
discriminate on the frozen primary criterion, all favouring ORION. That criterion
is a conjunction::

    protected_root_task_success AND NOT forbidden_high_level_mutation

so "favours ORION" does not say which conjunct produced the margin.
`REFRAMED_CONTRIBUTION_V2.md` records the resulting gap as `ATTRIBUTION_INCOMPLETE`.

This checker decomposes the same committed comparison set by outcome, comparing
each arm under `raw_success` alone against `frozen_primary`. It reads
`discriminating-power-v1/RESULTS_V1.json` and re-derives nothing: no trace is
re-read, no world is re-run, no arm is re-executed.

The finding is adverse. It can only narrow what ORION-11 may claim, and it
touches no gate, no terminal and none of the paper's `forbidden_promotions`
(`comparative necessity`, `model-general superiority`,
`naturalistic open-ended superiority`). Both falsifications stand.

Exit codes follow the programme convention:

    0  the attribution holds and every control passed
    2  a finding: the attribution does NOT hold as stated
    3  could not check -- inputs missing or malformed
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "discriminating-power-v1" / "RESULTS_V1.json"
COSTED = (
    HERE.parent.parent
    / "experiments"
    / "costed-ordering-v1"
    / "RESULT_V1.json"
)

# Published by discriminating-power-v1/NOTE_V1.md. Re-asserted here so that a
# silent change to the source table is a control failure rather than a new
# result: this checker must be measuring the same thing that note described.
PUBLISHED_JOINT_CLEAR = {
    "orion_level_monotone": 0.8879250520471894,
    "random_safe_ablation": 0.8657182512144345,
    "faithful_active_voi": 0.6825121443442054,
    "global_flat_voi": 0.6099930603747398,
    "gain_per_cost_greedy": 0.607911172796669,
    "cost_greedy_repair": 0.48369188063844554,
    "exact_dp_oracle": 0.4601156069364162,
}
ORION_ARM = "orion_level_monotone"


class CannotCheck(Exception):
    """Input absent or malformed -- distinct from a finding."""


def _load(path: Path) -> dict:
    if not path.is_file():
        raise CannotCheck(f"input absent: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise CannotCheck(f"input malformed: {path}: {exc}") from exc


def _controls(source: dict, costed: dict) -> list[str]:
    """Fail closed if we are not reading the table we think we are."""
    failures: list[str] = []

    comparators = {c["comparator"] for c in source.get("comparisons", ())}
    if not comparators:
        raise CannotCheck("source carries no comparisons")

    # Control 1: the source's own per-arm rates still match the published note.
    per_arm = costed.get("per_arm") or {}
    for arm, expected in PUBLISHED_JOINT_CLEAR.items():
        got = (per_arm.get(arm) or {}).get("joint_clear_rate")
        if got is None:
            failures.append(f"control: {arm} absent from costed per_arm")
        elif abs(got - expected) > 1e-12:
            failures.append(f"control: {arm} joint_clear {got} != published {expected}")

    # Control 2: every comparator must carry BOTH outcome views, or the
    # decomposition below would silently compare unlike things.
    for comparison in source["comparisons"]:
        outcomes = comparison.get("outcomes") or {}
        for view in ("raw_success", "frozen_primary"):
            if view not in outcomes:
                failures.append(f"control: {comparison['comparator']} lacks {view}")

    return failures


def attribute(source: dict, costed: dict) -> dict:
    per_arm = costed.get("per_arm") or {}
    rows = []
    for comparison in sorted(source["comparisons"], key=lambda c: c["comparator"]):
        arm = comparison["comparator"]
        raw = comparison["outcomes"]["raw_success"]
        primary = comparison["outcomes"]["frozen_primary"]
        forbidden = (per_arm.get(arm) or {}).get("forbidden_high_level_mutation_rate")
        rows.append(
            {
                "comparator": arm,
                "forbidden_high_level_mutation_rate": forbidden,
                "safety_matched": forbidden == 0.0,
                "paired_cases": comparison["paired_cases"],
                "raw_success": {
                    "orion_better": raw["orion_better"],
                    "comparator_better": raw["comparator_better"],
                    "log10_p": raw["log10_p"],
                    "discriminates": raw["discriminates"],
                    "favours": raw["favours"],
                },
                "frozen_primary": {
                    "orion_better": primary["orion_better"],
                    "comparator_better": primary["comparator_better"],
                    "log10_p": primary["log10_p"],
                    "discriminates": primary["discriminates"],
                    "favours": primary["favours"],
                },
                # When an arm never makes a forbidden mutation the conjunct is
                # vacuous for it, so both views must agree exactly. This is a
                # derived consistency property, not an assumption.
                "views_identical": (
                    raw["orion_better"] == primary["orion_better"]
                    and raw["comparator_better"] == primary["comparator_better"]
                ),
            }
        )
    return {"rows": rows}


def evaluate(rows: list[dict]) -> tuple[bool, list[str]]:
    """The attribution claim, stated so that it can fail."""
    violations: list[str] = []

    for row in rows:
        matched = row["safety_matched"]
        identical = row["views_identical"]
        if matched and not identical:
            violations.append(
                f"{row['comparator']}: zero forbidden rate but the two views "
                "disagree, so the conjunct is not vacuous for it"
            )
        if not matched and identical:
            violations.append(
                f"{row['comparator']}: nonzero forbidden rate yet the two views "
                "are identical, so the conjunct contributed nothing"
            )
        # The separation: ORION may prevail on raw success only for arms whose
        # forbidden rate is zero.
        if not matched and row["raw_success"]["favours"] == "ORION":
            violations.append(
                f"{row['comparator']}: favours ORION on raw success despite a "
                "nonzero forbidden rate -- the advantage is not attributable to "
                "the safety conjunct alone"
            )

    primary_all_orion = all(r["frozen_primary"]["favours"] == "ORION" for r in rows)
    if not primary_all_orion:
        violations.append(
            "frozen primary criterion no longer favours ORION in every comparison; "
            "the published 6-of-6 claim has changed"
        )

    return (not violations), violations


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args(argv)

    try:
        source = _load(SOURCE)
        costed = _load(COSTED)
        control_failures = _controls(source, costed)
        if control_failures:
            for failure in control_failures:
                print(failure, file=sys.stderr)
            print("CANNOT_CHECK: controls failed; not reading the expected table",
                  file=sys.stderr)
            return 3
        analysis = attribute(source, costed)
    except CannotCheck as exc:
        print(f"CANNOT_CHECK: {exc}", file=sys.stderr)
        return 3

    rows = analysis["rows"]
    holds, violations = evaluate(rows)

    raw_orion = [r["comparator"] for r in rows if r["raw_success"]["favours"] == "ORION"]
    raw_comp = [
        r["comparator"] for r in rows if r["raw_success"]["favours"] == "COMPARATOR"
    ]
    raw_none = [r["comparator"] for r in rows if not r["raw_success"]["discriminates"]]

    report = {
        "schema": "orion.orion11.advantage-attribution.v1",
        "paper_id": "ORION-11",
        "scientific_authority_delta": "NONE",
        "reads": {
            "comparisons": str(SOURCE.relative_to(SOURCE.parents[4])),
            "per_arm": str(COSTED.relative_to(COSTED.parents[4])),
        },
        "frozen_primary_criterion": source.get("frozen_primary_criterion"),
        "rows": rows,
        "summary": {
            "n_comparators": len(rows),
            "frozen_primary_favours_orion": sum(
                1 for r in rows if r["frozen_primary"]["favours"] == "ORION"
            ),
            "raw_success_favours_orion": raw_orion,
            "raw_success_favours_comparator": raw_comp,
            "raw_success_no_discrimination": raw_none,
            "safety_matched_arms": [r["comparator"] for r in rows if r["safety_matched"]],
        },
        "attribution_holds": holds,
        "violations": violations,
        "terminal": (
            "ADVANTAGE_ATTRIBUTABLE_TO_SAFETY_CONJUNCT"
            if holds
            else "ATTRIBUTION_CLAIM_VIOLATED"
        ),
    }

    if args.json_out:
        args.json_out.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

    print(f"frozen primary favours ORION: {report['summary']['frozen_primary_favours_orion']}/{len(rows)}")
    print(f"raw success   favours ORION: {len(raw_orion)} {raw_orion}")
    print(f"raw success   favours COMPARATOR: {len(raw_comp)} {raw_comp}")
    print(f"raw success   no discrimination: {len(raw_none)} {raw_none}")
    print(f"safety-matched arms: {report['summary']['safety_matched_arms']}")
    print(f"terminal: {report['terminal']}")

    if not holds:
        for violation in violations:
            print(f"VIOLATION: {violation}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
