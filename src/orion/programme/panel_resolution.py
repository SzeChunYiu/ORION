"""Could this hypothesis have come out differently?

A comparison panel reports, for each system, a rate on each metric, and then
decides hypotheses from differences between those rates. The decision is only
informative if the metric it is decided on can take different values across the
panel. When every system scores the same, the hypothesis is settled before any
system runs, and its verdict --- ``PASS`` or ``NOT_SUPPORTED`` alike --- records
the benchmark rather than the systems.

P4's protected panel shows both halves of that at once. Its ``false_promotion``
rate ranges from 0.0 to 0.917 across eleven systems, and the hypothesis decided
on it separates cleanly with a 95% interval of [-0.553, -0.447]. Its
``clean_coverage`` is exactly 1.0 for all eleven, and the non-inferiority
hypothesis decided on that one reports an interval of [0.0, 0.0] and ``PASS``.
Its ``correct_cannot_check`` rate is also exactly 1.0 for all eleven, and the
hypothesis decided on *that* reports [0.0, 0.0] and ``NOT_SUPPORTED``. Two of
the three verdicts are properties of a saturated metric. A guard that no system
in the panel can fail has not been passed.

The distinction this module has to get right
--------------------------------------------
A zero-width interval is not by itself a defect. Two cases produce one and they
mean opposite things.

*Saturation.* Every system sits at the same value, usually the metric's ceiling
or floor. The difference is constant because there is nothing to differ about.
Nothing is learned.

*Separation.* The systems sit at different constants --- one at 1.0, another at
0.0 --- so the paired difference is constant but large. Something is learned,
and it is the strongest thing the metric can say. What is *not* learned is any
measure of uncertainty: the interval's width is zero because the sample is
constant, not because the estimate is precise, and reporting it beside an
interval earned from variation invites the reader to compare the two widths.

Collapsing those two into "degenerate interval" would either excuse a saturated
guard or condemn a perfect separation, so both are reported by name.

What this does not do
---------------------
It takes no view on whether a saturated metric is the wrong metric. A benchmark
on which every system achieves perfect clean coverage may be measuring something
real that is simply easy; that is a question about the benchmark's difficulty,
and answering it needs a system that fails, which is exactly what the panel does
not contain.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

SCHEMA_VERSION = "orion.programme.panel-resolution.v1"

#: Metric values treated as extremal. A rate saturated away from either bound is
#: still saturated, but a panel pinned at a bound is the case worth naming: it
#: cannot move in one direction at all.
EXTREMES: tuple[float, ...] = (0.0, 1.0)

#: Distinct values closer together than this are treated as one. Rates computed
#: over the same denominator differ by at least one count, so this only absorbs
#: float representation, never a real one-case difference.
TOLERANCE = 1e-12


class MetricResolution(Enum):
    """What a metric can express across the panel it was measured on."""

    DISCRIMINATES = "DISCRIMINATES"
    SATURATED = "SATURATED"
    SEPARATED_WITHOUT_VARIATION = "SEPARATED_WITHOUT_VARIATION"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class MetricReport:
    """One metric, read across every system in the panel."""

    metric: str
    resolution: MetricResolution
    values: dict[str, float]
    distinct_values: int
    at_extreme: float | None = None
    detail: str = ""

    def as_json(self) -> dict[str, Any]:
        return {
            "metric": self.metric,
            "resolution": self.resolution.value,
            "values": dict(self.values),
            "distinct_values": self.distinct_values,
            "at_extreme": self.at_extreme,
            "detail": self.detail,
        }


def _distinct(values: list[float]) -> list[float]:
    unique: list[float] = []
    for value in sorted(values):
        if not unique or abs(value - unique[-1]) > TOLERANCE:
            unique.append(value)
    return unique


def inspect_metric(systems: dict[str, dict[str, Any]], metric: str) -> MetricReport:
    """Read one metric across the panel and say what it can express.

    ``systems`` maps a system name to its reported rates. Systems that do not
    report the metric are skipped rather than defaulted: a missing rate is not a
    zero, and treating it as one would manufacture the variation this module
    exists to detect.
    """

    values = {
        name: float(rates[metric])
        for name, rates in systems.items()
        if isinstance(rates, dict) and isinstance(rates.get(metric), (int, float))
    }
    if len(values) < 2:
        return MetricReport(
            metric=metric,
            resolution=MetricResolution.CANNOT_CHECK,
            values=values,
            distinct_values=len(values),
            detail="fewer than two systems report this metric, so it has no panel to vary over",
        )

    unique = _distinct(list(values.values()))
    if len(unique) == 1:
        held = unique[0]
        extreme = next((e for e in EXTREMES if abs(held - e) <= TOLERANCE), None)
        where = f"at the metric's {'ceiling' if extreme == 1.0 else 'floor'}" if extreme is not None else f"at {held}"
        return MetricReport(
            metric=metric,
            resolution=MetricResolution.SATURATED,
            values=values,
            distinct_values=1,
            at_extreme=extreme,
            detail=(
                f"all {len(values)} systems score {held} {where}; any hypothesis decided "
                "on this metric is settled before a system runs, and its verdict records "
                "the benchmark rather than the systems"
            ),
        )

    # More than one value. Whether the panel *varies* in the sense a confidence
    # interval needs is a different question, and one this module cannot answer
    # from rates alone: two systems each perfectly constant across their own
    # cases separate without any within-system variation to resample.
    if len(unique) == 2 and all(
        any(abs(value - e) <= TOLERANCE for e in EXTREMES) for value in unique
    ):
        return MetricReport(
            metric=metric,
            resolution=MetricResolution.SEPARATED_WITHOUT_VARIATION,
            values=values,
            distinct_values=2,
            detail=(
                "the panel splits between the metric's floor and its ceiling with nothing "
                "in between; the separation is real and maximal, but a paired interval "
                "over it is zero-width because the difference is constant, so its width "
                "is not a measure of precision and must not be read beside an interval "
                "earned from variation"
            ),
        )

    return MetricReport(
        metric=metric,
        resolution=MetricResolution.DISCRIMINATES,
        values=values,
        distinct_values=len(unique),
        detail=f"{len(unique)} distinct values across {len(values)} systems",
    )


def inspect_panel(
    systems: dict[str, dict[str, Any]], metrics: tuple[str, ...] | None = None
) -> dict[str, MetricReport]:
    """Read every numeric metric the panel reports, or the named ones."""

    if metrics is None:
        found: set[str] = set()
        for rates in systems.values():
            if isinstance(rates, dict):
                found.update(
                    key
                    for key, value in rates.items()
                    if isinstance(value, (int, float)) and not isinstance(value, bool)
                )
        metrics = tuple(sorted(found))
    return {metric: inspect_metric(systems, metric) for metric in metrics}


# ---------------------------------------------------------------------------
# The published panels, and the report
# ---------------------------------------------------------------------------

#: Panels on the branch that decide hypotheses from per-system rates, with the
#: metric each hypothesis is decided on. Listed rather than discovered, because
#: the mapping from a hypothesis to the metric it rests on is not derivable from
#: the artifact --- and guessing it is how a saturated guard gets excused.
PUBLISHED_PANELS: tuple[dict[str, Any], ...] = (
    {
        "artifact": "papers/paper-04-verified-scientific-discovery/evidence/protected_v2/PUBLICATION_METRICS_V2.json",
        "paper_id": "P4",
        "hypothesis_metrics": {
            "H1": "false_promotion_rate",
            "H2": "clean_coverage",
            "H3": "correct_cannot_check_rate",
        },
    },
    {
        "artifact": "research/campaigns/2026-08-21-p4-battery-v3-identifiable/PANEL_V3.json",
        "paper_id": "P4",
        "hypothesis_metrics": {
            "H1": "false_promotion_rate",
            "H2": "clean_coverage",
            "H3": "correct_cannot_check_rate",
        },
    },
)


def discriminating_control() -> dict[str, dict[str, Any]]:
    """A panel on which every check must stay quiet.

    Carried beside the finding for the same reason P2's resolution audit carries
    one: a check that fires on every panel it is shown reports the check. Three
    systems, three distinct rates, none at a bound.
    """

    return {
        "system_a": {"guard_rate": 0.91, "outcome_rate": 0.12},
        "system_b": {"guard_rate": 0.84, "outcome_rate": 0.47},
        "system_c": {"guard_rate": 0.88, "outcome_rate": 0.63},
    }


def inspect_published_panel(repo_root: Any, panel: dict[str, Any]) -> dict[str, Any]:
    """One registered panel: what each hypothesis rests on, and whether it holds."""

    import json
    from pathlib import Path

    target = Path(repo_root).resolve() / panel["artifact"]
    if not target.is_file():
        return {
            "artifact": panel["artifact"],
            "paper_id": panel["paper_id"],
            "readable": False,
            "hypotheses": {},
            "metrics": {},
        }

    payload = json.loads(target.read_text(encoding="utf-8"))
    systems = payload.get("systems") or {}
    reports = inspect_panel(systems)

    hypotheses: dict[str, Any] = {}
    for name, metric in panel["hypothesis_metrics"].items():
        declared = (payload.get("hypotheses") or {}).get(name) or payload.get(name) or {}
        report = reports.get(metric)
        hypotheses[name] = {
            "decided_on": metric,
            "declared_status": declared.get("status"),
            "declared_ci95": [declared.get("ci95_low"), declared.get("ci95_high")],
            "metric_resolution": report.resolution.value if report else "CANNOT_CHECK",
            "verdict_could_have_differed": bool(
                report and report.resolution is not MetricResolution.SATURATED
            ),
        }

    return {
        "artifact": panel["artifact"],
        "paper_id": panel["paper_id"],
        "readable": True,
        "systems": len(systems),
        "hypotheses": hypotheses,
        "metrics": {name: report.as_json() for name, report in sorted(reports.items())},
    }


def build_report(repo_root: Any, *, date: str) -> dict[str, Any]:
    """Everything this module establishes, with what it does not."""

    panels = [inspect_published_panel(repo_root, panel) for panel in PUBLISHED_PANELS]
    control = inspect_panel(discriminating_control())
    control_clean = all(
        report.resolution is MetricResolution.DISCRIMINATES for report in control.values()
    )

    settled: list[str] = []
    for panel in panels:
        for name, hypothesis in panel.get("hypotheses", {}).items():
            if not hypothesis["verdict_could_have_differed"]:
                settled.append(
                    f"{panel['paper_id']} {name} ({panel['artifact'].rsplit('/', 1)[-1]}): "
                    f"declared {hypothesis['declared_status']} on {hypothesis['decided_on']}, "
                    "which is saturated"
                )

    return {
        "schema_version": SCHEMA_VERSION,
        "record": "PANEL_RESOLUTION",
        "date": date,
        "panels": panels,
        "hypotheses_settled_before_any_system_ran": settled,
        "control": {name: report.as_json() for name, report in sorted(control.items())},
        "control_is_clean": control_clean,
        "what_this_establishes": (
            "P4's protected panel decides three hypotheses from per-system rates, and in "
            "the published V2 panel two of the three rest on metrics every system scores "
            "identically. clean_coverage is exactly 1.0 for all eleven systems, so the "
            "non-inferiority hypothesis decided on it reports [0.0, 0.0] and PASS -- a "
            "guard no system in the panel can fail. correct_cannot_check_rate is also "
            "1.0 for all eleven, so the hypothesis decided on it reports [0.0, 0.0] and "
            "NOT_SUPPORTED -- a negative that records the benchmark rather than the "
            "systems. Only false_promotion_rate discriminates, ranging 0.0 to 0.917, and "
            "the hypothesis decided on it separates with a real interval. The later V3 "
            "panel repairs one of the two: correct_cannot_check_rate varies there, while "
            "clean_coverage remains saturated at 1.0 across every system. Saturation is "
            "distinguished from separation rather than merged with it: a panel split "
            "between a metric's floor and its ceiling also yields a zero-width interval, "
            "and that one is the strongest thing the metric can say."
        ),
        "not_licensed": [
            "any claim that a saturated metric is the wrong metric; a benchmark on which "
            "every system is perfect may measure something real that is simply easy, and "
            "settling that needs a system that fails, which these panels do not contain",
            "any claim about H1, whose metric discriminates across the panel and whose "
            "interval is earned",
            "any claim that the panels' verdicts were recorded dishonestly; each is what "
            "its stated rule produces on its stated metric -- what is established is that "
            "two of them could not have been anything else",
        ],
    }


def main(argv: list[str]) -> int:
    """CLI entry point. ``argv`` is required: there is no implicit run."""

    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(
        prog="orion-panel-resolution",
        description="Ask whether a panel's hypotheses could have come out differently.",
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--date", required=True)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)

    report = build_report(args.repo_root, date=args.date)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"written: {args.output}")

    for panel in report["panels"]:
        print(f"  {panel['artifact'].rsplit('/', 1)[-1]} ({panel['paper_id']})")
        for name, hypothesis in sorted(panel.get("hypotheses", {}).items()):
            flag = " " if hypothesis["verdict_could_have_differed"] else "!"
            print(
                f"    {flag} {name}: declared {hypothesis['declared_status']} on "
                f"{hypothesis['decided_on']} -> {hypothesis['metric_resolution']}"
            )
    print(f"  control is clean (guard is not vacuous): {report['control_is_clean']}")

    if not report["control_is_clean"]:
        print("THE GUARD FIRES ON A PANEL WHOSE METRICS ALL DISCRIMINATE")
        return 3
    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    raise SystemExit(main(sys.argv[1:]))
