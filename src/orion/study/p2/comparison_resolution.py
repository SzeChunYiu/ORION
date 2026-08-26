"""Could a campaign have reported anything other than what it reported?

P2's Wide campaigns publish a paired equivalence interval over 399 matched
questions. The V3 result reads::

    "paired_distinct_question_iou": {
      "n": 399, "ties": 399, "wins": 0, "losses": 0,
      "ci95_low": 0.0, "ci95_high": 0.0, ...
    }

Read at face value that is the strongest equivalence evidence a bootstrap can
produce: a zero-width interval centred on zero, over four hundred tasks. Read
against the rest of the same artifact it is not evidence at all. The three
compared arms carry three distinct candidate digests and **one** evaluator-output
digest between them. Whatever the arms did differently upstream, the official
scorer emitted the same bytes for all three, so every paired difference is
exactly zero by construction. Resampling four hundred zeros gives a zero-width
interval however many resamples are drawn, and would do so at *n* = 4 as
convincingly as at *n* = 399.

The cause sits underneath both observations and needs no invented threshold,
because the campaign freezes its own. The frozen rule requires an average-IoU
delta of 0.03 before superiority is supported. Every arm in every completed
campaign scores about 0.004. The entire measured performance of the best arm is
an order of magnitude smaller than the difference the campaign was built to
detect, so deleting a competing arm outright would not reach the threshold. All
three systems retrieve almost nothing, which is why their per-question scores
tie four hundred times and their evaluator outputs are byte-identical. Those are
symptoms. The floor is the finding.

V1 of the same campaign adds a second defect that is easy to miss: there all
three arms carry *one* candidate digest as well, so the campaign scored a single
system against itself three times and reported the resulting 399 ties as a
paired equivalence interval.

That is not a small reporting infelicity. ``P2-U-T2`` is a false-closure
non-inferiority guard, and a guard discharged by a degenerate interval is
discharged by an instrument with no resolution --- the same failure as a
differential that agrees because both sides return a constant, and the same
failure as a rate that reports ``0.0`` because its denominator was empty.

This module reads a published campaign result and asks the one question the
result does not ask itself: **could this campaign have produced a different
verdict?** It computes nothing about discovery quality and takes no view on
whether the systems are in fact equivalent. It reports resolution.

What it checks
--------------
0. *The measurement floor.* Every arm scoring below the campaign's own frozen
   effect threshold means no outcome could have crossed it.
1. *Arm distinguishability.* Distinct candidate inputs that yield one evaluator
   output digest are a comparison with no resolution.
2. *Degenerate paired interval.* ``ties == n`` with no wins and no losses gives a
   zero-width interval by construction, independent of the sample size that
   appears to support it.
3. *Monotonicity of the sampled family.* ``max_iou_at_k`` is a maximum over the
   top *k*, so it cannot decrease in *k*. A decrease proves the family is not
   measuring what its name says.
4. *Absent runtime measurement.* Token, duration and tool-call totals that are
   all exactly zero are an unrecorded measurement rather than a measured zero.

Checks 3 and 4 are not new discipline. ``scripts/score_wide_comparison.py``
already refuses the sampled family in terms this module reuses --- "an absent
measurement wearing the costume of a number" --- and already refuses a metric
whose denominator is missing. The defect is that the rule lives in one scorer
and the published result artifacts came out of another.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

SCHEMA_VERSION = "orion.p2.comparison-resolution.v1"

#: The sampled family upstream emits without seeding. Named here so the exclusion
#: rule is applied to result artifacts and not only inside one scorer.
SAMPLED_FAMILY_MARKER = "max_iou_at"

#: Totals that are a measurement when present and an absence when uniformly zero.
RUNTIME_TOTAL_FIELDS: tuple[str, ...] = (
    "total_tokens",
    "total_duration_sec",
    "avg_tool_call_count",
    "avg_turn_count",
)


class Resolution(Enum):
    """Whether the campaign could have reported anything else."""

    HAS_RESOLUTION = "HAS_RESOLUTION"
    ZERO_RESOLUTION = "ZERO_RESOLUTION"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class ResolutionReport:
    """One campaign result, and what it could have said.

    Two finding lists rather than one. "This comparison could not have produced
    a different verdict" and "this artifact publishes a metric its own scorer
    excludes" are different claims with different consequences, and a single
    list let a campaign with genuine resolution look defective for a reporting
    slip -- which is how the control for this guard first failed its own test.
    """

    resolution: Resolution
    resolution_findings: tuple[str, ...] = ()
    reporting_findings: tuple[str, ...] = ()
    arms: int = 0
    distinct_candidate_digests: int = 0
    distinct_evaluator_digests: int = 0
    paired: dict[str, Any] = field(default_factory=dict)
    floor: dict[str, Any] = field(default_factory=dict)
    non_monotone_at_k: tuple[str, ...] = ()
    sampled_family_published: tuple[str, ...] = ()
    absent_runtime_totals: tuple[str, ...] = ()

    @property
    def findings(self) -> tuple[str, ...]:
        """Everything found, resolution first. Kept for reading, not for logic."""

        return self.resolution_findings + self.reporting_findings

    def as_json(self) -> dict[str, Any]:
        return {
            "resolution": self.resolution.value,
            "resolution_findings": list(self.resolution_findings),
            "reporting_findings": list(self.reporting_findings),
            "arms": self.arms,
            "distinct_candidate_digests": self.distinct_candidate_digests,
            "distinct_evaluator_digests": self.distinct_evaluator_digests,
            "paired": dict(self.paired),
            "floor": dict(self.floor),
            "non_monotone_at_k": list(self.non_monotone_at_k),
            "sampled_family_published": list(self.sampled_family_published),
            "absent_runtime_totals": list(self.absent_runtime_totals),
        }


def _at_k_curve(metrics: dict[str, Any]) -> list[tuple[int, float]]:
    """The ``max_iou_at_k`` points present, ordered by k."""

    points: list[tuple[int, float]] = []
    for key, value in metrics.items():
        if SAMPLED_FAMILY_MARKER not in key or not isinstance(value, (int, float)):
            continue
        suffix = key.rsplit("_", 1)[-1]
        if suffix.isdigit():
            points.append((int(suffix), float(value)))
    return sorted(points)


def non_monotone_at_k(official: dict[str, Any]) -> tuple[str, ...]:
    """Arms whose sampled family decreases in k, which it cannot do.

    A maximum over the top *k* candidates is a maximum over a superset of the
    top *k-1*, so the curve is non-decreasing for any real measurement. Reported
    per arm rather than as one boolean, because an arm that is monotone while
    others are not would mean something different from all of them failing.
    """

    offending: list[str] = []
    for arm, metrics in official.items():
        if not isinstance(metrics, dict):
            continue
        curve = _at_k_curve(metrics)
        for (_, earlier), (later_k, later) in zip(curve, curve[1:]):
            if later < earlier:
                offending.append(f"{arm}: max_iou_at_{later_k}={later} < previous {earlier}")
                break
    return tuple(offending)


def absent_runtime_totals(official: dict[str, Any]) -> tuple[str, ...]:
    """Arms reporting every runtime total as exactly zero.

    A system that ran and consumed nothing does not exist. Uniform zeros across
    tokens, duration and call counts are the runtime evidence never having been
    transported, which is a different fact from a cheap run and must not be
    averaged with one.
    """

    offending: list[str] = []
    for arm, metrics in official.items():
        if not isinstance(metrics, dict):
            continue
        present = [f for f in RUNTIME_TOTAL_FIELDS if isinstance(metrics.get(f), (int, float))]
        if present and all(float(metrics[f]) == 0.0 for f in present):
            offending.append(f"{arm}: {', '.join(present)} all exactly zero")
    return tuple(offending)


def paired_interval_is_degenerate(paired: dict[str, Any]) -> bool:
    """Is the interval zero-width because every pair tied?

    Distinguished from a genuinely tight interval: an interval earned from
    varying differences narrows with n, while an interval over identical
    differences is zero-width at any n. Only the second is reported here.
    """

    if not paired:
        return False
    n = paired.get("n")
    ties = paired.get("ties")
    wins = paired.get("wins")
    losses = paired.get("losses")
    if not all(isinstance(v, int) for v in (n, ties, wins, losses)):
        return False
    return bool(n) and ties == n and wins == 0 and losses == 0


def headline_cannot_reach_the_required_delta(payload: dict[str, Any]) -> dict[str, Any]:
    """Is every arm's whole score smaller than the difference the campaign must detect?

    This is the root diagnosis, and it needs no invented threshold: the campaign
    freezes its own. ``scientific_rule.required_official_avg_iou_delta`` is the
    difference in average IoU that the frozen rule requires before superiority
    is supported. If the *largest* arm's average IoU is itself below that
    number, then deleting the other arm entirely would not produce the required
    delta, and no sample size, resampling scheme or routing policy can change
    that. The campaign is at the measurement floor.

    Both completed campaigns are: every arm scores about 0.004 against a
    required delta of 0.03. Three systems that all retrieve almost nothing are
    indistinguishable because there is nothing to distinguish, which is why
    their per-question scores tie 399 times and their evaluator outputs are
    byte-identical. Those are symptoms; this is the cause.
    """

    official = payload.get("official") or {}
    rule = payload.get("scientific_rule") or {}
    required = rule.get("required_official_avg_iou_delta")
    scores = {
        arm: float(metrics["avg_iou"])
        for arm, metrics in official.items()
        if arm != "orion_minus_primary_baseline"
        and isinstance(metrics, dict)
        and isinstance(metrics.get("avg_iou"), (int, float))
    }
    if not scores or not isinstance(required, (int, float)):
        return {"checked": False, "at_floor": False}

    best = max(scores.values())
    return {
        "checked": True,
        "at_floor": best < float(required),
        "best_arm_avg_iou": best,
        "required_avg_iou_delta": float(required),
        "arm_scores": scores,
    }


def inspect_campaign_result(payload: dict[str, Any]) -> ResolutionReport:
    """Read one published campaign result and report its resolution."""

    candidates = payload.get("candidate_sha256") or {}
    evaluators = payload.get("evaluator_output_sha256") or {}
    official = payload.get("official") or {}
    paired = payload.get("paired_distinct_question_iou") or {}

    resolution_findings: list[str] = []
    reporting_findings: list[str] = []

    distinct_candidates = len(set(candidates.values()))
    distinct_evaluators = len(set(evaluators.values()))
    arms = len(evaluators)

    # Two distinct failures, and the first version of this check only caught the
    # second. V1 of the campaign gives all three arms the *same* candidate
    # digest, so it compared one system against itself three times -- a stronger
    # defect than V3's, and one that slipped past a condition requiring the
    # candidates to differ.
    floor = headline_cannot_reach_the_required_delta(payload)
    zero_resolution = False
    if floor.get("at_floor"):
        zero_resolution = True
        resolution_findings.append(
            f"every arm is at the measurement floor: the best arm's average IoU is "
            f"{floor['best_arm_avg_iou']:.6f}, below the "
            f"{floor['required_avg_iou_delta']} delta the frozen rule requires before "
            "superiority is supported, so deleting a competing arm outright would not "
            "reach the threshold and no sample size can"
        )
    if arms >= 2 and distinct_candidates == 1:
        zero_resolution = True
        resolution_findings.append(
            f"{arms} arms share one candidate digest, so the compared inputs are "
            "byte-identical; this is one system scored against itself and no "
            "comparison exists to be measured"
        )
    elif arms >= 2 and distinct_evaluators == 1 and distinct_candidates > 1:
        zero_resolution = True
        resolution_findings.append(
            f"{arms} arms carry {distinct_candidates} distinct candidate digests and "
            f"{distinct_evaluators} evaluator-output digest; every paired difference is "
            "zero by construction and no paired statistic over them can distinguish "
            "the arms"
        )

    degenerate = paired_interval_is_degenerate(paired)
    if degenerate:
        resolution_findings.append(
            f"the paired interval is zero-width because all {paired.get('n')} pairs tied "
            f"({paired.get('wins')} wins, {paired.get('losses')} losses); a zero-width "
            "interval over identical differences is produced at any sample size and is "
            "not equivalence evidence"
        )

    offending_at_k = non_monotone_at_k(official)
    if offending_at_k:
        reporting_findings.append(
            "the sampled max_iou_at_k family decreases in k, which a maximum over the "
            "top k cannot do: " + "; ".join(offending_at_k)
        )

    published_sampled = tuple(
        sorted(
            {
                key
                for metrics in official.values()
                if isinstance(metrics, dict)
                for key in metrics
                if SAMPLED_FAMILY_MARKER in key
            }
        )
    )
    if published_sampled:
        reporting_findings.append(
            "the result artifact publishes the unseeded sampled family that "
            "score_wide_comparison.py excludes by rule: " + ", ".join(published_sampled)
        )

    absent_runtime = absent_runtime_totals(official)
    if absent_runtime:
        reporting_findings.append(
            "runtime totals are uniformly zero, which is an untransported measurement "
            "rather than a measured zero: " + "; ".join(absent_runtime)
        )

    if not evaluators or not official:
        resolution = Resolution.CANNOT_CHECK
        resolution_findings.append(
            "the artifact records no per-arm evaluator digest or no official block, so "
            "its resolution cannot be assessed"
        )
    elif zero_resolution or degenerate:
        resolution = Resolution.ZERO_RESOLUTION
    else:
        resolution = Resolution.HAS_RESOLUTION

    return ResolutionReport(
        resolution=resolution,
        floor=floor,
        resolution_findings=tuple(resolution_findings),
        reporting_findings=tuple(reporting_findings),
        arms=arms,
        distinct_candidate_digests=distinct_candidates,
        distinct_evaluator_digests=distinct_evaluators,
        paired=dict(paired),
        non_monotone_at_k=offending_at_k,
        sampled_family_published=published_sampled,
        absent_runtime_totals=absent_runtime,
    )


# ---------------------------------------------------------------------------
# Non-vacuity, and the survey
# ---------------------------------------------------------------------------

#: Every published P2 Wide campaign result, relative to the repository root.
CAMPAIGN_RESULTS: tuple[str, ...] = (
    "papers/orion-12-open-world-scientific-discovery/evidence/external_results/"
    "P2_WIDE_OPENAIRE_MATCHED_RESULT_V1.json",
    "papers/orion-12-open-world-scientific-discovery/evidence/external_results/"
    "P2_WIDE_OPENAIRE_MATCHED_RESULT_V3.json",
)


def well_resolved_control() -> dict[str, Any]:
    """A campaign that does have resolution, so the guard has something to pass.

    A check that fires on everything it is shown reports the checker, not the
    subject --- which is the exact failure this module exists to name, and there
    would be no defence against having committed it here. So the control is
    carried in the module beside the finding rather than only in a test file:
    two arms with different candidates, different evaluator output, a paired
    split that is not all ties, a monotone sampled family, and non-zero runtime
    totals.
    """

    return {
        "candidate_sha256": {"arm_a": "a" * 64, "arm_b": "b" * 64},
        "evaluator_output_sha256": {"arm_a": "c" * 64, "arm_b": "d" * 64},
        "official": {
            "arm_a": {
                "avg_iou": 0.31,
                "avg_max_iou_at_1": 0.31,
                "avg_max_iou_at_2": 0.38,
                "avg_max_iou_at_4": 0.41,
                "total_tokens": 918_244,
                "total_duration_sec": 4102.5,
                "avg_tool_call_count": 7.2,
                "avg_turn_count": 3.1,
            },
            "arm_b": {
                "avg_iou": 0.27,
                "avg_max_iou_at_1": 0.27,
                "avg_max_iou_at_2": 0.33,
                "avg_max_iou_at_4": 0.35,
                "total_tokens": 812_119,
                "total_duration_sec": 3877.0,
                "avg_tool_call_count": 6.4,
                "avg_turn_count": 2.8,
            },
        },
        "paired_distinct_question_iou": {
            "n": 399,
            "ties": 214,
            "wins": 108,
            "losses": 77,
            "ci95_low": 0.006,
            "ci95_high": 0.061,
        },
        # Carried so the floor check is exercised rather than skipped. A control
        # that omits the frozen rule leaves that check reporting `checked:
        # false`, which is not the same as passing it.
        "scientific_rule": {"required_official_avg_iou_delta": 0.03},
    }


def survey(repo_root: Any) -> dict[str, Any]:
    """Inspect every published campaign result, and the control alongside them."""

    import json
    from pathlib import Path

    root = Path(repo_root).resolve()
    campaigns: dict[str, Any] = {}
    for relative in CAMPAIGN_RESULTS:
        target = root / relative
        name = target.name
        if not target.is_file():
            campaigns[name] = {
                "resolution": Resolution.CANNOT_CHECK.value,
                "resolution_findings": ["artifact is not on the branch"],
                "reporting_findings": [],
            }
            continue
        payload = json.loads(target.read_text(encoding="utf-8"))
        campaigns[name] = inspect_campaign_result(payload).as_json()

    control = inspect_campaign_result(well_resolved_control())
    zero = sorted(
        name
        for name, report in campaigns.items()
        if report["resolution"] == Resolution.ZERO_RESOLUTION.value
    )
    return {
        "campaigns": campaigns,
        "zero_resolution_campaigns": zero,
        "control": control.as_json(),
        "control_passes": control.resolution is Resolution.HAS_RESOLUTION,
        "every_published_campaign_has_zero_resolution": len(zero) == len(campaigns),
    }


def build_report(repo_root: Any, *, date: str) -> dict[str, Any]:
    """Everything this module establishes, with what it does not."""

    result = survey(repo_root)
    return {
        "schema_version": SCHEMA_VERSION,
        "record": "P2_COMPARISON_RESOLUTION",
        "date": date,
        **result,
        "what_this_establishes": (
            "Both completed P2 Wide campaigns ran at the measurement floor. Their frozen "
            "rule requires an average-IoU delta of 0.03 before superiority is supported, "
            "and every arm in both scores about 0.004 -- so the whole measured "
            "performance of the best arm is smaller than the difference the campaign "
            "exists to detect, and deleting a competing arm outright would not reach the "
            "threshold. Everything else follows from that. Both published a paired "
            "equivalence interval that no possible outcome could have widened. V1 gave "
            "its three arms one "
            "candidate digest, so it scored a single system against itself and reported "
            "399 ties; V3 gave its three arms distinct candidates but one "
            "evaluator-output digest, so every paired difference was zero by "
            "construction. In both, ci95 is [0.0, 0.0] over 399 questions, which reads "
            "as the strongest equivalence evidence a bootstrap can give and is instead "
            "the signature of an instrument with no resolution. Both also publish the "
            "unseeded max_iou_at_k family that the paper's own scorer excludes by rule, "
            "and in both that family decreases in k -- which a maximum over the top k "
            "cannot do -- and both report every runtime total as exactly zero. The "
            "guard is shown to be capable of passing: a control campaign with distinct "
            "arms, a mixed paired split, a monotone sampled family and non-zero runtime "
            "totals is reported as having resolution."
        ),
        "not_licensed": [
            "any claim that the compared systems are or are not equivalent; this "
            "measures the instrument, not the systems",
            "any claim that either campaign's terminal was wrong; both correctly read "
            "CANNOT_CHECK, V3 because provider validity reached 0.716 against a frozen "
            "0.90 -- what is established here is that the paired interval beside those "
            "terminals could not have said anything else",
            "any claim that a repaired campaign would find a difference; resolution is "
            "a precondition for measuring one, not evidence of one",
            "any diagnosis of *why* the arms are at the floor; that the retrieval scores "
            "near zero is measured here, the reason it does is not",
        ],
    }


def main(argv: list[str]) -> int:
    """CLI entry point. ``argv`` is required: there is no implicit run."""

    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(
        prog="orion-p2-comparison-resolution",
        description="Ask whether a published P2 campaign could have reported anything else.",
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

    for name, campaign in sorted(report["campaigns"].items()):
        print(f"  {campaign['resolution']:16s} {name}")
        for finding in campaign.get("resolution_findings", ()):
            print(f"      ! {finding[:110]}")
        for finding in campaign.get("reporting_findings", ()):
            print(f"      - {finding[:110]}")
    print(f"  control passes (guard is not vacuous): {report['control_passes']}")

    if not report["control_passes"]:
        print("THE GUARD FIRES ON A CAMPAIGN THAT HAS RESOLUTION")
        return 3
    # Zero resolution is the finding, not an error: reporting it is this
    # module's job, so it exits clean and the ledger carries the verdict.
    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    raise SystemExit(main(sys.argv[1:]))
