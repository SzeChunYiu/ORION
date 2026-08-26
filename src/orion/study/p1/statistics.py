"""Frozen statistical procedures for the ORION-P1 hidden-formulation study.

Every procedure here is fixed by `papers/orion-11-recursive-epistemic-reconstruction/
protocol/PROTOCOL_V1.json` (`statistics` block, `protocol_status: DESIGN_FROZEN`):

* Wilson 95% score intervals for standalone binary rates;
* paired percentile bootstrap with 10000 resamples for matched differences;
* 5 stochastic repeats nested within task/system, with the **task/case** as the
  unit of analysis — repeats are reduced to one observation per case *before*
  an interval is taken, so `n` is never inflated by the repeat factor;
* Holm correction for inferential secondary families when p-values are reported;
* practical margins: H1 superiority at least +0.05 absolute root-success against
  the strongest matched baseline; H2 non-inferiority within +0.02 absolute
  unnecessary-reframe rate.

Nothing in this module chooses a statistic. It implements the frozen ones.

Dependencies are stdlib only (`math`, `random`, `bisect`, `statistics`); the
project declares no numeric third-party dependency and this module does not add
one.

Honesty contract: a procedure with no admissible input raises rather than
returning a number, and `assess_hypothesis` returns CANNOT_CHECK rather than a
verdict whenever the evidence cannot carry one. An empty denominator is never
0.0.
"""

from __future__ import annotations

import math
import random
from bisect import bisect_left, bisect_right
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum
from statistics import NormalDist

# --- frozen protocol constants -------------------------------------------------

PROTOCOL_ID = "P1.hidden-formulation.v1"
PROTOCOL_CONFIDENCE = 0.95
PROTOCOL_RESAMPLES = 10000
PROTOCOL_STOCHASTIC_REPEATS = 5
H1_SUPERIORITY_MARGIN = 0.05
H2_NON_INFERIORITY_MARGIN = 0.02


class IntervalMethod(str, Enum):
    WILSON_SCORE = "wilson_score"
    PAIRED_PERCENTILE_BOOTSTRAP = "paired_percentile_bootstrap"


@dataclass(frozen=True)
class Interval:
    """A point estimate and its two-sided interval.

    `point` is the estimate the interval was built around; a caller that reports
    `point` from one reduction and the interval from another has produced two
    inconsistent numbers in one row, which this type exists to prevent.
    """

    point: float
    low: float
    high: float
    confidence: float
    method: IntervalMethod = IntervalMethod.WILSON_SCORE

    def contains(self, value: float) -> bool:
        return self.low <= value <= self.high

    @property
    def width(self) -> float:
        return self.high - self.low

    def as_dict(self) -> dict:
        return {
            "point": self.point,
            "low": self.low,
            "high": self.high,
            "confidence": self.confidence,
            "method": self.method.value,
        }


def normal_quantile(probability: float) -> float:
    """Inverse standard-normal CDF from the stdlib (no scipy/numpy)."""

    if not 0.0 < probability < 1.0:
        raise ValueError("normal_quantile requires a probability in (0, 1)")
    return NormalDist().inv_cdf(probability)


def wilson_interval(
    successes: int,
    n: int,
    *,
    confidence: float = PROTOCOL_CONFIDENCE,
) -> Interval:
    """Wilson score interval for a binomial proportion.

    centre = (p + z^2/2n) / (1 + z^2/n)
    half   = z/(1 + z^2/n) * sqrt(p(1-p)/n + z^2/4n^2)

    `n` must be the number of independent units. For this study the unit is the
    frozen case, after the 5 stochastic repeats have been reduced (see
    `orion.study.p1.metrics.RepeatReduction`). Passing case-by-seed trials here
    would inflate `n` by the repeat factor and understate the interval.

    Raises on `n <= 0`: an empty denominator is CANNOT_CHECK, which the caller
    must represent as such, never as a rate of 0.0.
    """

    if n <= 0:
        raise ValueError("wilson_interval requires n > 0; an empty denominator is CANNOT_CHECK, not a rate")
    if not 0 <= successes <= n:
        raise ValueError(f"successes must lie in [0, n]; got {successes} of {n}")
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must lie in (0, 1)")

    z = normal_quantile(0.5 + confidence / 2.0)
    proportion = successes / n
    z2 = z * z
    denominator = 1.0 + z2 / n
    centre = (proportion + z2 / (2.0 * n)) / denominator
    half = (z / denominator) * math.sqrt(proportion * (1.0 - proportion) / n + z2 / (4.0 * n * n))
    return Interval(
        point=proportion,
        low=max(0.0, centre - half),
        high=min(1.0, centre + half),
        confidence=confidence,
        method=IntervalMethod.WILSON_SCORE,
    )


@dataclass(frozen=True)
class BootstrapDifference:
    """A matched difference `mean(a) - mean(b)` with its percentile interval.

    `n` is the number of matched units resampled (cases, not case-by-seed
    trials). `seed` and `resamples` are carried so the number can be regenerated
    exactly; a difference reported without them is not reproducibly verifiable.

    `two_sided_p` is the bootstrap p-value `2 * min(P(d <= 0), P(d >= 0))`,
    floored at `p_floor = 1/resamples`. The floor exists so the value handed to
    `holm_correction` is never a fabricated 0.0 — with 10000 resamples nothing
    smaller than 1e-4 is resolvable and the table must print it as such.
    """

    point: float
    low: float
    high: float
    confidence: float
    resamples: int
    n: int
    seed: int
    two_sided_p: float
    p_floor: float
    method: IntervalMethod = IntervalMethod.PAIRED_PERCENTILE_BOOTSTRAP

    def contains(self, value: float) -> bool:
        return self.low <= value <= self.high

    @property
    def interval(self) -> Interval:
        return Interval(
            point=self.point,
            low=self.low,
            high=self.high,
            confidence=self.confidence,
            method=self.method,
        )

    def as_dict(self) -> dict:
        return {
            "point": self.point,
            "low": self.low,
            "high": self.high,
            "confidence": self.confidence,
            "resamples": self.resamples,
            "n": self.n,
            "seed": self.seed,
            "two_sided_p": self.two_sided_p,
            "p_floor": self.p_floor,
            "method": self.method.value,
        }


def paired_bootstrap_difference(
    a: Sequence[float],
    b: Sequence[float],
    *,
    resamples: int = PROTOCOL_RESAMPLES,
    seed: int,
    confidence: float = PROTOCOL_CONFIDENCE,
) -> BootstrapDifference:
    """Paired percentile bootstrap of `mean(a) - mean(b)`.

    `a[i]` and `b[i]` must be the two systems' values for the **same** unit; the
    pairing is the whole point, since both systems ran the same frozen cases.
    The per-unit differences are resampled with replacement, which is the paired
    bootstrap (resampling the two samples independently would discard the
    pairing and inflate the interval).

    Percentile convention, fixed so results are regenerable: with `R` resamples
    and `alpha = 1 - confidence`, the interval is
    `sorted[floor(alpha/2 * R)]` to `sorted[ceil((1 - alpha/2) * R) - 1]`
    (indices 250 and 9749 at the frozen R = 10000, confidence = 0.95).

    Determinism: `random.Random(seed)` (CPython Mersenne Twister). The same seed
    and inputs give the same interval on every run; the seed is carried in the
    result so a table consumer can re-derive it.
    """

    values_a = [float(value) for value in a]
    values_b = [float(value) for value in b]
    if len(values_a) != len(values_b):
        raise ValueError("paired bootstrap requires aligned, equal-length samples")
    n = len(values_a)
    if n == 0:
        raise ValueError("paired bootstrap requires at least one matched unit; an empty pairing is CANNOT_CHECK")
    if resamples <= 0:
        raise ValueError("resamples must be positive")
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must lie in (0, 1)")

    differences = [values_a[index] - values_b[index] for index in range(n)]
    point = math.fsum(differences) / n

    rng = random.Random(seed)
    draws = [math.fsum(rng.choices(differences, k=n)) / n for _ in range(resamples)]
    draws.sort()

    alpha = 1.0 - confidence
    low_index = min(max(int(math.floor(alpha / 2.0 * resamples)), 0), resamples - 1)
    high_index = min(max(int(math.ceil((1.0 - alpha / 2.0) * resamples)) - 1, 0), resamples - 1)

    at_or_below_zero = bisect_right(draws, 0.0)
    at_or_above_zero = resamples - bisect_left(draws, 0.0)
    p_floor = 1.0 / resamples
    raw_p = 2.0 * min(at_or_below_zero, at_or_above_zero) / resamples

    return BootstrapDifference(
        point=point,
        low=draws[low_index],
        high=draws[high_index],
        confidence=confidence,
        resamples=resamples,
        n=n,
        seed=seed,
        two_sided_p=min(1.0, max(p_floor, raw_p)),
        p_floor=p_floor,
    )


def cohens_h(proportion_a: float, proportion_b: float) -> float:
    """Cohen's h for two proportions: 2*asin(sqrt(p1)) - 2*asin(sqrt(p2)).

    Reported only as a *secondary*, unpaired effect size. The protocol's
    practical margins are stated in absolute terms (+0.05, +0.02), so the
    headline effect size for this study is the absolute paired difference, not
    this quantity.
    """

    for proportion in (proportion_a, proportion_b):
        if not 0.0 <= proportion <= 1.0:
            raise ValueError("cohens_h requires proportions in [0, 1]")
    return 2.0 * math.asin(math.sqrt(proportion_a)) - 2.0 * math.asin(math.sqrt(proportion_b))


# --- multiplicity --------------------------------------------------------------


@dataclass(frozen=True)
class HolmEntry:
    label: str
    raw_p: float
    adjusted_p: float
    rejected: bool
    rank: int

    def as_dict(self) -> dict:
        return {
            "label": self.label,
            "raw_p": self.raw_p,
            "adjusted_p": self.adjusted_p,
            "rejected": self.rejected,
            "rank": self.rank,
        }


def holm_correction(
    pvalues: Sequence[float],
    *,
    alpha: float = 1.0 - PROTOCOL_CONFIDENCE,
    labels: Sequence[str] | None = None,
) -> tuple[HolmEntry, ...]:
    """Holm-Bonferroni step-down correction, returned in the caller's order.

    Sort ascending; the k-th smallest (0-based rank `k` of `m`) is multiplied by
    `m - k`, then a running maximum enforces monotonicity so an adjusted value
    can never fall below a smaller raw p-value's adjustment. Values are capped
    at 1.0. `rejected` is `adjusted_p <= alpha`, which the running maximum makes
    identical to the classical step-down stopping rule.
    """

    raw = [float(value) for value in pvalues]
    if any(not 0.0 <= value <= 1.0 for value in raw):
        raise ValueError("p-values must lie in [0, 1]")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie in (0, 1)")
    m = len(raw)
    if m == 0:
        return ()
    names = list(labels) if labels is not None else [f"p{index}" for index in range(m)]
    if len(names) != m:
        raise ValueError("labels must align with p-values")

    order = sorted(range(m), key=lambda index: (raw[index], index))
    adjusted = [0.0] * m
    ranks = [0] * m
    running = 0.0
    for rank, index in enumerate(order):
        running = max(running, (m - rank) * raw[index])
        adjusted[index] = min(1.0, running)
        ranks[index] = rank + 1

    return tuple(
        HolmEntry(
            label=names[index],
            raw_p=raw[index],
            adjusted_p=adjusted[index],
            rejected=adjusted[index] <= alpha,
            rank=ranks[index],
        )
        for index in range(m)
    )


# --- hypothesis verdicts -------------------------------------------------------


class HypothesisDirection(str, Enum):
    """How the frozen practical margin is read against the difference."""

    SUPERIORITY = "SUPERIORITY"
    NON_INFERIORITY = "NON_INFERIORITY"


class HypothesisVerdict(str, Enum):
    SUPPORTED = "SUPPORTED"
    NOT_SUPPORTED = "NOT_SUPPORTED"
    EQUIVALENT = "EQUIVALENT"
    UNDERPOWERED = "UNDERPOWERED"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class HypothesisAssessment:
    hypothesis_id: str
    verdict: HypothesisVerdict
    direction: HypothesisDirection
    margin: float
    rationale: str
    difference: BootstrapDifference | None = None

    def as_dict(self) -> dict:
        return {
            "hypothesis_id": self.hypothesis_id,
            "verdict": self.verdict.value,
            "direction": self.direction.value,
            "margin": self.margin,
            "rationale": self.rationale,
            "difference": self.difference.as_dict() if self.difference is not None else None,
        }


def assess_hypothesis(
    *,
    hypothesis_id: str,
    direction: HypothesisDirection,
    margin: float,
    difference: BootstrapDifference | None,
    cannot_check_units: int = 0,
    min_units: int = 0,
    margin_resolvable: bool | None = None,
    subject_abstention_rate: float | None = None,
    comparator_abstention_rate: float | None = None,
) -> HypothesisAssessment:
    """Read a matched difference against a frozen practical margin.

    Precedence, strictest first:

    1. `CANNOT_CHECK` when there is no matched difference, when any unit was
       CANNOT_CHECK (a missing trace may not be silently treated as a failure),
       or when a non-inferiority reading is confounded by abstention.
    2. `SUPPORTED` (superiority) only when the **whole** interval lies above the
       margin: `low > margin`, strictly. An interval that merely includes the
       margin is not support.
    3. `EQUIVALENT` (non-inferiority) only when `high < margin`, strictly.
    4. `UNDERPOWERED` when the result is inconclusive and the matched-unit count
       is below the caller's declared prospective N. `min_units` has no frozen
       value — `PROTOCOL_V1.json` names a prospective power analysis but binds no
       N, so this verdict is unreachable unless the caller declares one. No
       default is invented here.
    5. `NOT_SUPPORTED` otherwise.

    Abstention confound (non-inferiority only): the unnecessary-reframe rate on
    negative controls counts reframes, not abstentions, so a system that
    abstains on controls can lower the rate without ever showing restraint.
    Non-inferiority therefore requires both systems' control-abstention rates,
    and returns CANNOT_CHECK when the subject's exceeds the comparator's by more
    than the margin. This is a data-sufficiency guard, not a new statistic.
    """

    if difference is None:
        return HypothesisAssessment(
            hypothesis_id=hypothesis_id,
            verdict=HypothesisVerdict.CANNOT_CHECK,
            direction=direction,
            margin=margin,
            rationale="no matched difference was computed",
        )
    if cannot_check_units > 0:
        return HypothesisAssessment(
            hypothesis_id=hypothesis_id,
            verdict=HypothesisVerdict.CANNOT_CHECK,
            direction=direction,
            margin=margin,
            rationale=f"{cannot_check_units} matched unit(s) are CANNOT_CHECK and may not be scored as failures",
            difference=difference,
        )
    if difference.n <= 0:
        return HypothesisAssessment(
            hypothesis_id=hypothesis_id,
            verdict=HypothesisVerdict.CANNOT_CHECK,
            direction=direction,
            margin=margin,
            rationale="no matched units",
            difference=difference,
        )

    # A comparison whose N cannot resolve its own margin is UNDERPOWERED, not
    # NOT_SUPPORTED. Those say different things: the first reports that the
    # design could not answer, the second that it answered no. The prospective
    # analysis found the frozen 48-case suite needs roughly 7,800-12,600 cases
    # to resolve its +0.05 margin at 80% power, so reporting NOT_SUPPORTED from
    # it would dress an underpowered non-finding as evidence. Checked before the
    # direction dispatch because it is a property of the design, not of which
    # hypothesis is being asked. See protocol/PROSPECTIVE_POWER_V1.md.
    if margin_resolvable is False:
        return HypothesisAssessment(
            hypothesis_id=hypothesis_id,
            verdict=HypothesisVerdict.UNDERPOWERED,
            difference=difference,
            margin=margin,
            direction=direction,
            rationale=(
                "the design cannot resolve its own margin at this N; the interval "
                "is reported as an estimate and no rejection is claimed"
            ),
        )

    if direction is HypothesisDirection.NON_INFERIORITY:
        if subject_abstention_rate is None or comparator_abstention_rate is None:
            return HypothesisAssessment(
                hypothesis_id=hypothesis_id,
                verdict=HypothesisVerdict.CANNOT_CHECK,
                direction=direction,
                margin=margin,
                rationale="non-inferiority on unnecessary-reframe rate requires both systems' control-abstention rates; without them the rate cannot be read as restraint",
                difference=difference,
            )
        if subject_abstention_rate - comparator_abstention_rate > margin:
            return HypothesisAssessment(
                hypothesis_id=hypothesis_id,
                verdict=HypothesisVerdict.CANNOT_CHECK,
                direction=direction,
                margin=margin,
                rationale=(
                    f"control-abstention rate is {subject_abstention_rate:.4f} versus {comparator_abstention_rate:.4f}: "
                    "the unnecessary-reframe rate is confounded by abstention and cannot certify non-inferiority"
                ),
                difference=difference,
            )
        if difference.high < margin:
            return HypothesisAssessment(
                hypothesis_id=hypothesis_id,
                verdict=HypothesisVerdict.EQUIVALENT,
                direction=direction,
                margin=margin,
                rationale=f"upper bound {difference.high:.4f} lies strictly below the non-inferiority margin {margin:+.4f}",
                difference=difference,
            )
        if difference.n < min_units:
            return HypothesisAssessment(
                hypothesis_id=hypothesis_id,
                verdict=HypothesisVerdict.UNDERPOWERED,
                direction=direction,
                margin=margin,
                rationale=f"{difference.n} matched units is below the declared prospective N of {min_units}",
                difference=difference,
            )
        return HypothesisAssessment(
            hypothesis_id=hypothesis_id,
            verdict=HypothesisVerdict.NOT_SUPPORTED,
            direction=direction,
            margin=margin,
            rationale=f"upper bound {difference.high:.4f} reaches or exceeds the non-inferiority margin {margin:+.4f}",
            difference=difference,
        )

    if difference.low > margin:
        return HypothesisAssessment(
            hypothesis_id=hypothesis_id,
            verdict=HypothesisVerdict.SUPPORTED,
            direction=direction,
            margin=margin,
            rationale=f"lower bound {difference.low:.4f} lies strictly above the superiority margin {margin:+.4f}",
            difference=difference,
        )
    if difference.n < min_units:
        return HypothesisAssessment(
            hypothesis_id=hypothesis_id,
            verdict=HypothesisVerdict.UNDERPOWERED,
            direction=direction,
            margin=margin,
            rationale=f"{difference.n} matched units is below the declared prospective N of {min_units}",
            difference=difference,
        )
    return HypothesisAssessment(
        hypothesis_id=hypothesis_id,
        verdict=HypothesisVerdict.NOT_SUPPORTED,
        direction=direction,
        margin=margin,
        rationale=f"the {difference.confidence:.0%} interval [{difference.low:.4f}, {difference.high:.4f}] includes or lies below the superiority margin {margin:+.4f}",
        difference=difference,
    )


__all__ = [
    "H1_SUPERIORITY_MARGIN",
    "H2_NON_INFERIORITY_MARGIN",
    "PROTOCOL_CONFIDENCE",
    "PROTOCOL_ID",
    "PROTOCOL_RESAMPLES",
    "PROTOCOL_STOCHASTIC_REPEATS",
    "BootstrapDifference",
    "HolmEntry",
    "HypothesisAssessment",
    "HypothesisDirection",
    "HypothesisVerdict",
    "Interval",
    "IntervalMethod",
    "assess_hypothesis",
    "cohens_h",
    "holm_correction",
    "normal_quantile",
    "paired_bootstrap_difference",
    "wilson_interval",
]
