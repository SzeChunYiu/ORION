"""Fail-closed guard for the P3 analysis unit.

P3 scores ontology alignment. A single ontology pair yields hundreds of
correspondence rows, and it is tempting to treat those rows as samples: it
turns ``n=1`` into ``n=91`` and makes a confidence interval appear out of a
single case. It is not sound. Rows inside one pair share the seed ontology,
the label vocabulary, the reference-alignment construction and the matcher's
own decision threshold, so they are not independent draws from anything.

The V21 result stated this discipline in prose and obeyed it -- it reported
exact finite-case counts and explicitly declined to report a population
estimand, confidence interval or p value over pair cells. The V22 next
discriminator re-froze it as a prohibited promotion (``no pair cell treated
as an independent case``). What neither did was mechanize it, so nothing
stopped a later report from quietly resampling rows.

This module is that missing third thing. It reads a P3 aggregate report and
refuses it unless the declared analysis unit is one of the admissible units,
and unless any interval or p value it carries is backed by enough cases.

The guard distinguishes *could not check* from *checked and fine*. A report
it cannot parse exits ``5``; it never exits ``0`` by falling through.

Run it against a report::

    python -m orion.study.p3.analysis_unit_guard --report <aggregate>.json

Exit codes: 0 PASS, 2 inadmissible unit, 3 interval below the minimum case
count, 4 no unit declared, 5 malformed -- could not check.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

__all__ = [
    "ADMISSIBLE_UNITS",
    "INADMISSIBLE_UNITS",
    "EXIT_CANNOT_CHECK",
    "EXIT_INADMISSIBLE_UNIT",
    "EXIT_INTERVAL_UNDERPOWERED",
    "EXIT_NO_UNIT",
    "EXIT_PASS",
    "GuardVerdict",
    "assess_report",
    "main",
]

#: Units that carry independence for P3. A track is a set of pairs; a case is
#: one scored (pair, protocol) instance. Both aggregate over correspondences
#: rather than treating them as draws.
ADMISSIBLE_UNITS = frozenset({"ontology_pair", "track", "case"})

#: Units that do not carry independence, named explicitly so that a typo in a
#: report is a parse failure rather than a silent pass.
INADMISSIBLE_UNITS = frozenset(
    {"correspondence_row", "pair_cell", "mapping", "correspondence", "seed", "episode", "generated_row", "row"}
)

EXIT_PASS = 0
EXIT_INADMISSIBLE_UNIT = 2
EXIT_INTERVAL_UNDERPOWERED = 3
EXIT_NO_UNIT = 4
EXIT_CANNOT_CHECK = 5

#: Keys whose presence means the report is making a population claim.
_INTERVAL_KEYS = ("confidence_interval", "ci", "ci_lower", "ci_upper", "p_value", "bootstrap")


@dataclass(frozen=True)
class GuardVerdict:
    """The outcome of assessing one report. ``exit_code`` is the whole verdict."""

    exit_code: int
    terminal: str
    problems: tuple[str, ...] = field(default=())

    @property
    def passed(self) -> bool:
        return self.exit_code == EXIT_PASS


def _carries_population_claim(aggregate: dict[str, Any]) -> bool:
    """True when the aggregate reports an interval, a p value or a bootstrap.

    Checked by key presence rather than truthiness: a reported ``p_value`` of
    ``0.0`` is still a population claim, and ``ci_lower`` of ``0`` is too.
    """

    return any(key in aggregate for key in _INTERVAL_KEYS)


def assess_report(report: Any, *, minimum_cases: int = 7) -> GuardVerdict:
    """Assess one parsed P3 aggregate report against the frozen unit rule.

    ``report`` must be a mapping carrying an ``aggregates`` list. Anything
    else is CANNOT_CHECK -- this function never guesses a shape.
    """

    if not isinstance(report, dict):
        return GuardVerdict(EXIT_CANNOT_CHECK, "P3_V22_ANALYSIS_UNIT_CANNOT_CHECK", ("report is not an object",))
    aggregates = report.get("aggregates")
    if not isinstance(aggregates, list) or not aggregates:
        return GuardVerdict(
            EXIT_CANNOT_CHECK,
            "P3_V22_ANALYSIS_UNIT_CANNOT_CHECK",
            ("report carries no non-empty 'aggregates' list",),
        )

    problems: list[str] = []
    worst = EXIT_PASS
    for position, aggregate in enumerate(aggregates):
        label = f"aggregates[{position}]"
        if not isinstance(aggregate, dict):
            return GuardVerdict(
                EXIT_CANNOT_CHECK, "P3_V22_ANALYSIS_UNIT_CANNOT_CHECK", (f"{label} is not an object",)
            )
        name = aggregate.get("name", label)
        unit = aggregate.get("analysis_unit")
        if unit is None:
            problems.append(f"{name}: declares no analysis_unit")
            worst = max(worst, EXIT_NO_UNIT)
            continue
        if not isinstance(unit, str):
            return GuardVerdict(
                EXIT_CANNOT_CHECK, "P3_V22_ANALYSIS_UNIT_CANNOT_CHECK", (f"{name}: analysis_unit is not a string",)
            )
        if unit not in ADMISSIBLE_UNITS:
            reason = "explicitly inadmissible" if unit in INADMISSIBLE_UNITS else "unrecognised"
            problems.append(f"{name}: analysis_unit {unit!r} is {reason}; admissible units are {sorted(ADMISSIBLE_UNITS)}")
            worst = max(worst, EXIT_INADMISSIBLE_UNIT)
            continue
        if _carries_population_claim(aggregate):
            cases = aggregate.get("case_count")
            if not isinstance(cases, int):
                return GuardVerdict(
                    EXIT_CANNOT_CHECK,
                    "P3_V22_ANALYSIS_UNIT_CANNOT_CHECK",
                    (f"{name}: reports an interval or p value but carries no integer case_count",),
                )
            if cases < minimum_cases:
                problems.append(
                    f"{name}: reports an interval or p value on {cases} case(s); minimum is {minimum_cases}"
                )
                worst = max(worst, EXIT_INTERVAL_UNDERPOWERED)

    if worst == EXIT_PASS:
        return GuardVerdict(EXIT_PASS, "P3_V22_ANALYSIS_UNIT_PASS")
    return GuardVerdict(worst, "P3_V22_ANALYSIS_UNIT_FAIL", tuple(problems))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True, help="P3 aggregate report JSON")
    parser.add_argument("--minimum-cases", type=int, default=7)
    args = parser.parse_args(argv)

    try:
        report = json.loads(args.report.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"P3_V22_ANALYSIS_UNIT_CANNOT_CHECK: {error}", file=sys.stderr)
        return EXIT_CANNOT_CHECK

    verdict = assess_report(report, minimum_cases=args.minimum_cases)
    for problem in verdict.problems:
        print(f"  {problem}", file=sys.stderr)
    print(verdict.terminal)
    return verdict.exit_code


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
