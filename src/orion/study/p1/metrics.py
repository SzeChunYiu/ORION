"""Scoring for the ORION-P1 hidden-formulation study (issue #98, step 6).

**Package boundary.** This is the only module in `orion.study.p1` permitted to
read `HiddenShiftCase.protected_gold`. Systems under test receive a `PublicView`;
`tables.py` reads archived records, never live cases. Keeping gold access in one
module is what makes the protocol's `hidden_labels` access policy checkable.

Three rules are enforced by the types here rather than by discipline:

1. **An abstention is not a pass.** On a negative control the three outcomes
   UNNECESSARY_REFRAME / ABSTAINED / CORRECT_RESTRAINT partition the cases and
   are all reported. A system that declines is never credited with restraint.
2. **CANNOT_CHECK never becomes 0.** A case with no trace (no credential, no
   run) is excluded from both numerator and denominator and named in
   `cannot_check_case_ids`. A case whose repeats are only partially present is
   CANNOT_CHECK too: a rate reduced over an unknown subset of seeds is a
   different measurement.
3. **The unit is the case.** The frozen 5 stochastic repeats are reduced to one
   observation per case before any rate is formed, so a Wilson interval taken on
   a `BinaryRate` from here has `n = cases`, never `cases x seeds`. The
   reduction used is recorded on every rate.

Metric-by-metric definitions are on the individual fields and on `score_case`.
"""

from __future__ import annotations

import dataclasses

import hashlib
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field, replace
from enum import Enum

from .cases import HiddenShiftCase, TaskFamily
from .systems import ResourceUse, SystemTrace

SCHEMA_VERSION = "orion.p1.case-record.v1"

CONTROL_FAMILIES = frozenset(
    {
        TaskFamily.EVIDENCE_ONLY_CONTROL.value,
        TaskFamily.EXECUTION_ONLY_CONTROL.value,
    }
)
HIDDEN_SHIFT_FAMILIES = frozenset(
    {
        TaskFamily.HIDDEN_PARENT_DOMAIN.value,
        TaskFamily.HIDDEN_REPRESENTATION.value,
        TaskFamily.HIDDEN_DECOMPOSITION.value,
        TaskFamily.HIDDEN_MEASUREMENT.value,
    }
)

#: Sentinel for "the system named no responsibility family". It is not a class
#: in the macro-F1 label universe: an unnamed prediction is a false negative for
#: the gold class and a false positive for nothing.
NO_LABEL = "<none>"


class ScoreStatus(str, Enum):
    SCORED = "SCORED"
    CANNOT_CHECK = "CANNOT_CHECK"


class SystemRole(str, Enum):
    SUBJECT = "SUBJECT"
    BASELINE = "BASELINE"
    ABLATION = "ABLATION"
    UNSPECIFIED = "UNSPECIFIED"


class ControlOutcome(str, Enum):
    """Mutually exclusive outcomes on a negative control.

    ABSTAINED is its own outcome and is never folded into CORRECT_RESTRAINT.
    """

    UNNECESSARY_REFRAME = "UNNECESSARY_REFRAME"
    ABSTAINED = "ABSTAINED"
    CORRECT_RESTRAINT = "CORRECT_RESTRAINT"
    NOT_A_CONTROL = "NOT_A_CONTROL"


#: Tie-break for the per-case modal control outcome: the worst outcome wins, so
#: a split panel of repeats can never be rounded into restraint.
CONTROL_SEVERITY: tuple[ControlOutcome, ...] = (
    ControlOutcome.UNNECESSARY_REFRAME,
    ControlOutcome.ABSTAINED,
    ControlOutcome.CORRECT_RESTRAINT,
)


class RepeatReduction(str, Enum):
    """How the frozen 5 stochastic repeats collapse to one case observation.

    MAJORITY  - performance metrics: success on strictly more than half the repeats.
    ANY       - safety metrics: one violation in any repeat marks the case.
    ALL       - integrity metrics: the case holds only if every repeat holds.
    MODE_SEVERITY - the categorical control outcome, ties broken to the worst.
    TRIAL_POOLED  - not reduced; pooled over trials (set and label metrics that
                    are not standalone binary rates and take no Wilson interval).
    """

    MAJORITY = "MAJORITY"
    ANY = "ANY"
    ALL = "ALL"
    MODE_SEVERITY = "MODE_SEVERITY"
    TRIAL_POOLED = "TRIAL_POOLED"


class FailureMode(str, Enum):
    """Single-stage failure attribution, assigned by the precedence in
    `classify_failure`. `contributing_failure_modes` keeps everything that
    applied so the attribution is auditable rather than lossy."""

    NONE = "NONE"
    CANNOT_CHECK = "CANNOT_CHECK"
    AUTHORITY_VIOLATION = "AUTHORITY_VIOLATION"
    INVARIANT_VIOLATION = "INVARIANT_VIOLATION"
    TRACE_INFIDELITY = "TRACE_INFIDELITY"
    ABSTENTION = "ABSTENTION"
    UNNECESSARY_REFRAME = "UNNECESSARY_REFRAME"
    MISSED_REFRAME = "MISSED_REFRAME"
    WRONG_RESPONSIBILITY = "WRONG_RESPONSIBILITY"
    WRONG_REFRAME_TARGET = "WRONG_REFRAME_TARGET"
    INCOMPLETE_REOPEN = "INCOMPLETE_REOPEN"
    OVER_REOPEN = "OVER_REOPEN"
    UNRESOLVED_ROOT = "UNRESOLVED_ROOT"


def blinded_case_id(case_id: str, *, suite_fingerprint: str = "") -> str:
    """Stable pseudonym for publication tables.

    Deterministic in (case id, suite fingerprint) so the same archive always
    yields the same blinded id and a reader can re-derive it from the host-owned
    suite; the published table never carries the raw id.
    """

    digest = hashlib.sha256(f"{suite_fingerprint}:{case_id}".encode()).hexdigest()
    return f"P1-C-{digest[:10]}"


@dataclass(frozen=True)
class SetComparison:
    """Set-level comparison of reopened dependencies against gold."""

    true_positives: int = 0
    false_positives: int = 0
    false_negatives: int = 0

    @property
    def predicted(self) -> int:
        return self.true_positives + self.false_positives

    @property
    def actual(self) -> int:
        return self.true_positives + self.false_negatives

    @property
    def applicable(self) -> bool:
        """False only when nothing was proposed and nothing was required.

        Empty-versus-empty is not a perfect score and not a zero; it is a
        comparison that was never posed, and every derived quantity is None.
        """

        return bool(self.predicted or self.actual)

    @property
    def precision(self) -> float | None:
        if not self.applicable:
            return None
        return self.true_positives / self.predicted if self.predicted else 0.0

    @property
    def recall(self) -> float | None:
        if not self.applicable:
            return None
        return self.true_positives / self.actual if self.actual else 0.0

    @property
    def f1(self) -> float | None:
        precision, recall = self.precision, self.recall
        if precision is None or recall is None:
            return None
        if precision + recall == 0.0:
            return 0.0
        return 2.0 * precision * recall / (precision + recall)

    def __add__(self, other: SetComparison) -> SetComparison:
        return SetComparison(
            true_positives=self.true_positives + other.true_positives,
            false_positives=self.false_positives + other.false_positives,
            false_negatives=self.false_negatives + other.false_negatives,
        )

    def as_dict(self) -> dict:
        return {
            "true_positives": self.true_positives,
            "false_positives": self.false_positives,
            "false_negatives": self.false_negatives,
            "precision": self.precision,
            "recall": self.recall,
            "f1": self.f1,
        }


@dataclass(frozen=True)
class BinaryRate:
    """A rate together with the unit and repeat reduction that produced it.

    `value` is None when `n == 0` — an empty denominator is CANNOT_CHECK and is
    never rendered as 0.0. The `(successes, n)` pair is exactly what a Wilson
    interval must be taken on, so the point estimate and the interval can never
    come from two different reductions.
    """

    successes: int = 0
    n: int = 0
    unit: str = "case"
    reduction: RepeatReduction = RepeatReduction.MAJORITY

    @property
    def value(self) -> float | None:
        return self.successes / self.n if self.n else None

    @property
    def checkable(self) -> bool:
        return self.n > 0

    def as_dict(self) -> dict:
        return {
            "successes": self.successes,
            "n": self.n,
            "value": self.value,
            "unit": self.unit,
            "reduction": self.reduction.value,
        }


@dataclass(frozen=True)
class ResourceSummary:
    """Matched-budget accounting. Means are per scored trial."""

    trials: int = 0
    wallclock_seconds_total: float = 0.0
    model_tokens_total: int = 0
    tool_calls_total: int = 0
    search_queries_total: int = 0

    def _mean(self, total: float) -> float | None:
        return total / self.trials if self.trials else None

    @property
    def wallclock_seconds_mean(self) -> float | None:
        return self._mean(self.wallclock_seconds_total)

    @property
    def model_tokens_mean(self) -> float | None:
        return self._mean(self.model_tokens_total)

    @property
    def tool_calls_mean(self) -> float | None:
        return self._mean(self.tool_calls_total)

    @property
    def search_queries_mean(self) -> float | None:
        return self._mean(self.search_queries_total)

    def as_dict(self) -> dict:
        return {
            "trials": self.trials,
            "wallclock_seconds_total": self.wallclock_seconds_total,
            "wallclock_seconds_mean": self.wallclock_seconds_mean,
            "model_tokens_total": self.model_tokens_total,
            "model_tokens_mean": self.model_tokens_mean,
            "tool_calls_total": self.tool_calls_total,
            "tool_calls_mean": self.tool_calls_mean,
            "search_queries_total": self.search_queries_total,
            "search_queries_mean": self.search_queries_mean,
        }


# --- per-case scoring ----------------------------------------------------------


@dataclass(frozen=True)
class CaseScore:
    """One system's scored outcome on one case at one seed.

    Every metric field is `None` when `status is CANNOT_CHECK`. A consumer that
    coerces those to 0 has manufactured a failure that was never observed.
    """

    schema_version: str
    system_id: str
    system_role: SystemRole
    case_id: str
    blinded_case_id: str
    task_family: str
    dependency_depth: int
    seed: int
    status: ScoreStatus
    is_control: bool
    is_hidden_shift: bool
    reframe_required: bool
    suite_fingerprint: str = ""
    subject_revision: str = ""
    cannot_check_reason: str = ""

    root_success: bool | None = None
    abstained: bool | None = None
    reframed: bool | None = None
    control_outcome: ControlOutcome = ControlOutcome.NOT_A_CONTROL
    responsibility_gold: str = ""
    responsibility_predicted: str = ""
    responsibility_correct: bool | None = None
    reframe_target_correct: bool | None = None
    #: Axis-level credit: every coordinate class named is correct, even where the
    #: specific value on the axis was not. Strictly weaker than
    #: `reframe_target_correct` and never a substitute for it in reporting.
    reframe_axis_correct: bool | None = None
    reopen: SetComparison | None = None
    gold_dependency_count: int = 0
    stale_closures: int | None = None
    invariant_violation_count: int | None = None
    authority_violation_count: int | None = None
    trace_fidelity: bool | None = None
    trace_fidelity_faults: tuple[str, ...] = ()
    depth_adequate: bool | None = None
    max_recursion_depth: int | None = None
    resources: ResourceUse | None = None
    failure_mode: FailureMode = FailureMode.CANNOT_CHECK
    contributing_failure_modes: tuple[str, ...] = ()


def _normalise(label: str) -> str:
    return label.strip().lower()


def _axes(coordinates: Sequence[str]) -> frozenset[str]:
    """The coordinate classes named, dropping the specific value on each.

    Do NOT "fix" this to collapse an axis and its value into one class: they do
    not collapse on this data, and the subset test below is what makes the
    metric work. `('W.REPRESENTATIONS', 'representation:vector_resultant')`
    reduces to TWO classes, `{'W.REPRESENTATIONS', 'REPRESENTATION'}`, because
    the value's prefix is the family word rather than the engine's axis token.

    The metric is therefore `predicted <= gold`, not equality: a system naming
    the axis alone is a subset of gold's two classes and scores True, which is
    the partial credit this exists to give. Tightening it to equality, or
    editing this function to merge the pair, silently changes the metric for
    every system.

    One consequence worth knowing where the metric is defined: a system can
    satisfy the axis test by emitting a token from gold's *value* vocabulary
    (`parent_domain:anything`) rather than from the engine's coordinate
    namespace. That is not a leak — the comparison is host-side and no system
    sees gold — but it means axis credit is weaker than "named the right
    coordinate", and the strict `reframe_target_correct` remains the metric that
    requires naming both.
    """

    out: set[str] = set()
    for item in coordinates:
        text = item.strip()
        if text:
            out.add((text.split(":", 1)[0] if ":" in text else text).strip().upper())
    return frozenset(out)


def _trace_fidelity_faults(trace: SystemTrace) -> tuple[str, ...]:
    """Internal-consistency audit of a trace against **its own claims only**.

    Deliberately gold-free. `trace_fidelity` is the dependent variable of H4 and
    is bucketed by the case's gold `dependency_depth`; folding gold into the
    metric itself would put the same quantity on both axes and make the metric
    correlate with root success by construction. Depth adequacy against gold is
    reported separately as `depth_adequate`.
    """

    faults: list[str] = []
    if trace.max_recursion_depth < 0:
        faults.append("negative_recursion_depth")
    if trace.reframed:
        # Reframing without naming a target or a responsibility is NOT a
        # self-contradiction. It is an honest report from a system with no typed
        # attribution mechanism, which is exactly what the untyped baselines and
        # the generic-retry ablation exist to test. Scoring it as trace
        # infidelity reports an *attribution* failure as *bookkeeping*, and since
        # integrity outranks performance in the precedence order, it would mask
        # the defining property of those systems behind a housekeeping label.
        # Both reach the taxonomy through responsibility_correct and
        # reframe_axis_correct instead.
        #
        # Claiming a reframe while recording no recursion depth IS a
        # contradiction: the trace asserts an act it also says never ran.
        if trace.max_recursion_depth < 1:
            faults.append("reframe_without_recursion_depth")
    if trace.reopened and not trace.reframed:
        faults.append("reopen_without_reframe")
    if trace.abstained:
        if trace.root_solved:
            faults.append("abstention_claims_root_success")
        if trace.reframed:
            faults.append("abstention_with_reframe")
    return tuple(faults)


def classify_failure(score: CaseScore) -> tuple[FailureMode, tuple[str, ...]]:
    """Attribute the case to ONE failure stage, and list every stage that fired.

    Precedence (strictest first): authority > invariant > trace integrity >
    abstention > control selectivity > diagnosis > targeting > reopening >
    terminal outcome. Safety and integrity outrank performance because no
    positive metric may compensate for them; the stage order otherwise follows
    the pipeline, so the *earliest* broken stage owns the failure.
    """

    if score.status is ScoreStatus.CANNOT_CHECK:
        return FailureMode.CANNOT_CHECK, (FailureMode.CANNOT_CHECK.value,)

    contributing: list[FailureMode] = []
    if score.authority_violation_count:
        contributing.append(FailureMode.AUTHORITY_VIOLATION)
    if score.invariant_violation_count:
        contributing.append(FailureMode.INVARIANT_VIOLATION)
    if score.trace_fidelity is False:
        contributing.append(FailureMode.TRACE_INFIDELITY)
    if score.abstained:
        contributing.append(FailureMode.ABSTENTION)
    if score.control_outcome is ControlOutcome.UNNECESSARY_REFRAME:
        contributing.append(FailureMode.UNNECESSARY_REFRAME)
    if score.reframe_required and score.reframed is False:
        contributing.append(FailureMode.MISSED_REFRAME)
    if score.responsibility_correct is False:
        contributing.append(FailureMode.WRONG_RESPONSIBILITY)
    if score.reframe_axis_correct is False:
        contributing.append(FailureMode.WRONG_REFRAME_TARGET)
    if score.reopen is not None and score.reopen.false_negatives:
        contributing.append(FailureMode.INCOMPLETE_REOPEN)
    if score.reopen is not None and score.reopen.false_positives:
        contributing.append(FailureMode.OVER_REOPEN)
    if score.root_success is False:
        contributing.append(FailureMode.UNRESOLVED_ROOT)

    if not contributing:
        return FailureMode.NONE, ()
    return contributing[0], tuple(mode.value for mode in contributing)


def score_case(
    case: HiddenShiftCase,
    trace: SystemTrace | None,
    *,
    system_id: str,
    seed: int,
    system_role: SystemRole = SystemRole.UNSPECIFIED,
    suite_fingerprint: str = "",
    subject_revision: str = "",
    cannot_check_reason: str = "",
    elapsed_seconds: float | None = None,
) -> CaseScore:
    """Score one trace against one case's protected gold.

    `trace=None` means the system produced no trace for this case — no live
    provider credential, a symmetric outage, a harness error. That is
    CANNOT_CHECK and propagates as CANNOT_CHECK: it is neither a success nor a
    failure and it never enters a denominator.

    Metric definitions:

    * `root_success` - the system solved the root task, did not abstain, and
      cleared it in the responsibility family gold names. An abstention is never
      a root success even if `root_solved` was set; that combination is also
      recorded as a trace-fidelity fault. Nor is clearing a residual in the wrong
      family: `trace.root_solved` is gold-free and can only report that the system
      cleared what it saw, so responsibility consistency is what distinguishes
      solving the root from repairing a symptom (see the predicate for why this
      is constitutive rather than a second charge).
    * `control_outcome` - on a negative control, exactly one of
      UNNECESSARY_REFRAME / ABSTAINED / CORRECT_RESTRAINT.
    * `responsibility_correct` - the claimed responsibility family equals gold
      (whitespace- and case-normalised). An unclaimed family is incorrect.
    * `reframe_target_correct` - only defined where gold requires a reframe:
      the system reframed **and** its target coordinates equal gold's as a set.
      `None` on controls, where the reframe itself is the error.
    * `reopen` - set comparison of `trace.reopened` against
      `gold.dependencies_to_reopen`.
    * `stale_closures` - gold dependencies left closed, i.e. the reopen false
      negatives; the numerator of the stale-closure survival rate.
    * `trace_fidelity` - internal consistency of the trace's own claims (see
      `_trace_fidelity_faults`); gold-free by construction.
    * `depth_adequate` - `max_recursion_depth >= gold.dependency_depth`;
      reported separately from fidelity, not folded into it.
    """

    gold = case.protected_gold
    family = case.task_family.value
    is_control = family in CONTROL_FAMILIES
    common = {
        "schema_version": SCHEMA_VERSION,
        "system_id": system_id,
        "system_role": system_role,
        "case_id": case.case_id,
        "blinded_case_id": blinded_case_id(case.case_id, suite_fingerprint=suite_fingerprint),
        "task_family": family,
        "dependency_depth": gold.dependency_depth,
        "seed": seed,
        "is_control": is_control,
        "is_hidden_shift": family in HIDDEN_SHIFT_FAMILIES,
        "reframe_required": gold.reframe_required,
        "suite_fingerprint": suite_fingerprint,
        "subject_revision": subject_revision,
        "responsibility_gold": gold.responsibility_family,
        "gold_dependency_count": len(set(gold.dependencies_to_reopen)),
    }

    if trace is None:
        return CaseScore(
            status=ScoreStatus.CANNOT_CHECK,
            cannot_check_reason=cannot_check_reason or "no trace was produced for this case",
            failure_mode=FailureMode.CANNOT_CHECK,
            contributing_failure_modes=(FailureMode.CANNOT_CHECK.value,),
            **common,
        )

    if trace.case_id != case.case_id:
        raise ValueError(f"trace {trace.case_id!r} does not belong to case {case.case_id!r}")
    if trace.system_id != system_id:
        raise ValueError(f"trace system {trace.system_id!r} does not match {system_id!r}")
    if trace.seed != seed:
        raise ValueError(f"trace seed {trace.seed} does not match {seed}")

    abstained = bool(trace.abstained)
    reframed = bool(trace.reframed)

    predicted_family = trace.responsibility_family.strip() or NO_LABEL
    responsibility_correct = _normalise(predicted_family) == _normalise(gold.responsibility_family)

    # Responsibility consistency is *constitutive of* root success, not an extra
    # charge laid on top of it.
    #
    # `trace.root_solved` is gold-free by contract: `baselines.solved()` asks only
    # whether the system saw a material cue and then cleared it. It cannot ask
    # whether the cue it cleared belongs to the family that actually owns the
    # defect, because the system never sees gold. So a system can clear a symptom
    # in one responsibility family and truthfully report "I cleared what I saw"
    # while the root — in a different family — stands untouched. That is exactly
    # what produced `p1-c111`: gold INTERFACE, an EXECUTION marker ("crashes")
    # matched, the execution symptom repaired, and a record that simultaneously
    # claimed `root_success=True`, `responsibility_correct=False` and
    # `failure_mode=MISSED_REFRAME`. A record cannot be both a root success and a
    # missed reframe.
    #
    # This is deliberately NOT the pattern the module refuses elsewhere. Stale
    # closures are kept out of `root_solved` (see `baselines` module docstring)
    # because a system that repairs the root and leaves a dependent conclusion
    # standing did two things — one right, one wrong — and folding the second into
    # the first double-charges one mistake. Here there is no second act to charge:
    # the system never touched the root at all. Withholding `root_success` is the
    # primary metric declining to report a success that did not occur.
    #
    # The predicate is a strict tightening: it can only turn True into False, never
    # False into True, so it cannot manufacture a success anywhere. Its effect on
    # the frozen campaign is to move the headline from 1/48 to 0/48 — the honest
    # direction, and the one the floor-effect diagnosis already reached by hand.
    # The frozen archive is NOT rewritten; it is retired to instrument-validation
    # status and keeps the defective value it recorded.
    root_success = bool(trace.root_solved) and not abstained and responsibility_correct

    if not is_control:
        control_outcome = ControlOutcome.NOT_A_CONTROL
    elif abstained:
        control_outcome = ControlOutcome.ABSTAINED
    elif reframed:
        control_outcome = ControlOutcome.UNNECESSARY_REFRAME
    else:
        control_outcome = ControlOutcome.CORRECT_RESTRAINT

    if gold.reframe_required:
        # Gold names an axis and a value on it, e.g.
        # ('W.REPRESENTATIONS', 'representation:vector_resultant'). Exact set
        # equality collapses two different competencies into one bit: naming the
        # right coordinate class, and naming the right value within it. A system
        # that says "the search universe is wrong" is partly right; one that says
        # "the measurement model is wrong" is simply wrong. Scoring both False
        # discards the signal — and every mechanical system emits an axis only,
        # so the strict metric reads 0 everywhere by construction.
        #
        # The strict form is kept, because a frozen metric is not loosened in
        # place. The axis form sits beside it and is what failure attribution
        # reads, since naming the wrong axis is the real targeting failure.
        reframe_target_correct = reframed and set(trace.target_coordinates) == set(
            gold.target_coordinates
        )
        gold_axes = _axes(gold.target_coordinates)
        predicted_axes = _axes(trace.target_coordinates)
        reframe_axis_correct = bool(reframed and predicted_axes and predicted_axes <= gold_axes)
    else:
        reframe_target_correct = None
        reframe_axis_correct = None

    reopened = set(trace.reopened)
    required = set(gold.dependencies_to_reopen)
    reopen = SetComparison(
        true_positives=len(reopened & required),
        false_positives=len(reopened - required),
        false_negatives=len(required - reopened),
    )

    faults = _trace_fidelity_faults(trace)

    score = CaseScore(
        status=ScoreStatus.SCORED,
        root_success=root_success,
        abstained=abstained,
        reframed=reframed,
        control_outcome=control_outcome,
        responsibility_predicted=predicted_family,
        responsibility_correct=responsibility_correct,
        reframe_target_correct=reframe_target_correct,
        reframe_axis_correct=reframe_axis_correct,
        reopen=reopen,
        stale_closures=reopen.false_negatives,
        invariant_violation_count=len(trace.invariant_violations),
        authority_violation_count=len(trace.authority_violations),
        trace_fidelity=not faults,
        trace_fidelity_faults=faults,
        depth_adequate=trace.max_recursion_depth >= gold.dependency_depth,
        max_recursion_depth=trace.max_recursion_depth,
        # A system reports its own wallclock only if it did timed external work.
        # Mechanical systems do none, so trace.resources.wallclock_seconds is
        # 0.0 by construction, and a cost-to-success frontier built on it plots
        # every mechanical system at the origin. The harness measures the real
        # figure per run; prefer it when supplied, and fall back to the system's
        # own report only when no run record was available.
        resources=(
            trace.resources
            if elapsed_seconds is None
            else dataclasses.replace(trace.resources, wallclock_seconds=elapsed_seconds)
        ),
        **common,
    )
    mode, contributing = classify_failure(score)
    return replace(score, failure_mode=mode, contributing_failure_modes=contributing)


# --- archive record round-trip -------------------------------------------------


def case_score_to_record(score: CaseScore) -> dict:
    """Serialise a scored case to an archivable raw record.

    `tables.py` builds every published number from these records and never from
    a live case or trace object, so this is the schema boundary between the
    study run and the publication tables.
    """

    resources = score.resources
    return {
        "schema_version": score.schema_version,
        "system_id": score.system_id,
        "system_role": score.system_role.value,
        "case_id": score.case_id,
        "blinded_case_id": score.blinded_case_id,
        "task_family": score.task_family,
        "dependency_depth": score.dependency_depth,
        "seed": score.seed,
        "status": score.status.value,
        "is_control": score.is_control,
        "is_hidden_shift": score.is_hidden_shift,
        "reframe_required": score.reframe_required,
        "suite_fingerprint": score.suite_fingerprint,
        "subject_revision": score.subject_revision,
        "cannot_check_reason": score.cannot_check_reason,
        "root_success": score.root_success,
        "abstained": score.abstained,
        "reframed": score.reframed,
        "control_outcome": score.control_outcome.value,
        "responsibility_gold": score.responsibility_gold,
        "responsibility_predicted": score.responsibility_predicted,
        "responsibility_correct": score.responsibility_correct,
        "reframe_target_correct": score.reframe_target_correct,
        "reframe_axis_correct": score.reframe_axis_correct,
        "reopen": score.reopen.as_dict() if score.reopen is not None else None,
        "gold_dependency_count": score.gold_dependency_count,
        "stale_closures": score.stale_closures,
        "invariant_violation_count": score.invariant_violation_count,
        "authority_violation_count": score.authority_violation_count,
        "trace_fidelity": score.trace_fidelity,
        "trace_fidelity_faults": list(score.trace_fidelity_faults),
        "depth_adequate": score.depth_adequate,
        "max_recursion_depth": score.max_recursion_depth,
        "resources": None
        if resources is None
        else {
            "wallclock_seconds": resources.wallclock_seconds,
            "model_tokens": resources.model_tokens,
            "tool_calls": resources.tool_calls,
            "search_queries": resources.search_queries,
        },
        "failure_mode": score.failure_mode.value,
        "contributing_failure_modes": list(score.contributing_failure_modes),
    }


def case_score_from_record(record: Mapping) -> CaseScore:
    """Rebuild a scored case from an archived record.

    A record missing a required key raises. Silently defaulting a missing field
    would turn an incomplete archive into confident numbers.
    """

    version = record.get("schema_version")
    if version != SCHEMA_VERSION:
        raise ValueError(f"unsupported record schema {version!r}; expected {SCHEMA_VERSION!r}")
    for key in ("system_id", "case_id", "task_family", "seed", "status"):
        if key not in record:
            raise ValueError(f"record is missing required key {key!r}")

    reopen_payload = record.get("reopen")
    reopen = (
        None
        if reopen_payload is None
        else SetComparison(
            true_positives=int(reopen_payload["true_positives"]),
            false_positives=int(reopen_payload["false_positives"]),
            false_negatives=int(reopen_payload["false_negatives"]),
        )
    )
    resource_payload = record.get("resources")
    resources = (
        None
        if resource_payload is None
        else ResourceUse(
            wallclock_seconds=float(resource_payload.get("wallclock_seconds", 0.0)),
            model_tokens=int(resource_payload.get("model_tokens", 0)),
            tool_calls=int(resource_payload.get("tool_calls", 0)),
            search_queries=int(resource_payload.get("search_queries", 0)),
        )
    )
    return CaseScore(
        schema_version=SCHEMA_VERSION,
        system_id=record["system_id"],
        system_role=SystemRole(record.get("system_role", SystemRole.UNSPECIFIED.value)),
        case_id=record["case_id"],
        blinded_case_id=record.get("blinded_case_id", blinded_case_id(record["case_id"], suite_fingerprint=record.get("suite_fingerprint", ""))),
        task_family=record["task_family"],
        dependency_depth=int(record.get("dependency_depth", 0)),
        seed=int(record["seed"]),
        status=ScoreStatus(record["status"]),
        is_control=bool(record.get("is_control", record["task_family"] in CONTROL_FAMILIES)),
        is_hidden_shift=bool(record.get("is_hidden_shift", record["task_family"] in HIDDEN_SHIFT_FAMILIES)),
        reframe_required=bool(record.get("reframe_required", False)),
        suite_fingerprint=record.get("suite_fingerprint", ""),
        subject_revision=record.get("subject_revision", ""),
        cannot_check_reason=record.get("cannot_check_reason", ""),
        root_success=record.get("root_success"),
        abstained=record.get("abstained"),
        reframed=record.get("reframed"),
        control_outcome=ControlOutcome(record.get("control_outcome", ControlOutcome.NOT_A_CONTROL.value)),
        responsibility_gold=record.get("responsibility_gold", ""),
        responsibility_predicted=record.get("responsibility_predicted", ""),
        responsibility_correct=record.get("responsibility_correct"),
        reframe_target_correct=record.get("reframe_target_correct"),
        reframe_axis_correct=record.get("reframe_axis_correct"),
        reopen=reopen,
        gold_dependency_count=int(record.get("gold_dependency_count", 0)),
        stale_closures=record.get("stale_closures"),
        invariant_violation_count=record.get("invariant_violation_count"),
        authority_violation_count=record.get("authority_violation_count"),
        trace_fidelity=record.get("trace_fidelity"),
        trace_fidelity_faults=tuple(record.get("trace_fidelity_faults", ())),
        depth_adequate=record.get("depth_adequate"),
        max_recursion_depth=record.get("max_recursion_depth"),
        resources=resources,
        failure_mode=FailureMode(record.get("failure_mode", FailureMode.CANNOT_CHECK.value)),
        contributing_failure_modes=tuple(record.get("contributing_failure_modes", ())),
    )


# --- aggregation ---------------------------------------------------------------


def _majority(flags: Sequence[bool]) -> bool:
    return sum(1 for flag in flags if flag) * 2 > len(flags)


def _seed_mean(flags: Sequence[bool]) -> float:
    """Fraction of repeats that hit, keeping within-case resolution.

    The frozen unit is the case, so every *reported rate* is majority-reduced.
    That reduction is lossy — a system succeeding on 4/5 repeats and one
    succeeding on 5/5 both reduce to a solved case. These seed means are carried
    as a diagnostic so the discarded resolution stays visible and a matched
    difference can be re-derived on it without changing the resampling unit.
    """

    return sum(1.0 for flag in flags if flag) / len(flags) if flags else 0.0


def _modal_control_outcome(outcomes: Sequence[ControlOutcome]) -> ControlOutcome:
    counts = {outcome: outcomes.count(outcome) for outcome in set(outcomes)}
    best = max(counts.values())
    for outcome in CONTROL_SEVERITY:
        if counts.get(outcome, 0) == best:
            return outcome
    return ControlOutcome.NOT_A_CONTROL


def label_is_real(label: str) -> bool:
    return bool(label.strip()) and label != NO_LABEL


def _macro_f1(pairs: Sequence[tuple[str, str]]) -> tuple[float | None, tuple[str, ...]]:
    """Macro-averaged F1 over responsibility families.

    Label universe: every non-sentinel label seen as gold or as a prediction.
    Per class, precision/recall are 0.0 when their denominator is 0 (the
    `zero_division=0` convention); the macro average is the unweighted mean over
    the universe. `NO_LABEL` is excluded from the universe, so an unnamed
    prediction is a false negative for the gold class and nothing else.
    """

    if not pairs:
        return None, ()
    universe = sorted(
        {gold for gold, _ in pairs if label_is_real(gold)}
        | {predicted for _, predicted in pairs if label_is_real(predicted)}
    )
    if not universe:
        return None, ()
    scores: list[float] = []
    for label in universe:
        tp = sum(1 for gold, predicted in pairs if gold == label and predicted == label)
        fp = sum(1 for gold, predicted in pairs if gold != label and predicted == label)
        fn = sum(1 for gold, predicted in pairs if gold == label and predicted != label)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        scores.append(2.0 * precision * recall / (precision + recall) if precision + recall else 0.0)
    return sum(scores) / len(scores), tuple(universe)


@dataclass(frozen=True)
class SystemAggregate:
    """Case-reduced metrics for one system over one scope (all cases, or one family).

    Rates carrying `unit="case"` are Wilson-eligible: `n` counts frozen cases
    after repeat reduction. Rates and set comparisons carrying
    `unit="trial"`/`TRIAL_POOLED` are pooled diagnostics and take no Wilson
    interval — pooling them would inflate `n` by the repeat factor.
    """

    system_id: str
    system_role: SystemRole
    scope: str
    n_cases_total: int
    n_cases_scored: int
    n_trials_scored: int
    cannot_check_case_ids: tuple[str, ...]
    repeats_per_case: tuple[tuple[str, int], ...]
    expected_repeats: int
    repeat_coverage_ok: bool

    root_success: BinaryRate
    hidden_shift_success: BinaryRate
    unnecessary_reframe: BinaryRate
    control_abstention: BinaryRate
    control_correct_restraint: BinaryRate
    reframe_target_accuracy: BinaryRate
    invariant_violation: BinaryRate
    authority_violation: BinaryRate
    trace_fidelity: BinaryRate
    depth_adequacy: BinaryRate

    responsibility_macro_f1: float | None
    responsibility_labels: tuple[str, ...]
    reopen: SetComparison
    stale_closure_survival: BinaryRate
    resources: ResourceSummary

    trace_fidelity_by_depth: tuple[tuple[int, BinaryRate], ...] = ()
    invariant_violation_by_depth: tuple[tuple[int, BinaryRate], ...] = ()
    reopen_by_depth: tuple[tuple[int, SetComparison], ...] = ()
    per_case_metrics: dict[str, dict[str, float]] = field(default_factory=dict)
    #: raw case id -> publication pseudonym, so a table can name a case without
    #: republishing the host-owned suite.
    blinded_by_case: dict[str, str] = field(default_factory=dict)

    @property
    def cannot_check_cases(self) -> int:
        return len(self.cannot_check_case_ids)

    def blinded(self, case_ids: Iterable[str]) -> tuple[str, ...]:
        return tuple(self.blinded_by_case.get(case_id, case_id) for case_id in case_ids)

    def as_dict(self) -> dict:
        return {
            "system_id": self.system_id,
            "system_role": self.system_role.value,
            "scope": self.scope,
            "n_cases_total": self.n_cases_total,
            "n_cases_scored": self.n_cases_scored,
            "n_trials_scored": self.n_trials_scored,
            "cannot_check_cases": self.cannot_check_cases,
            "cannot_check_case_ids": list(self.cannot_check_case_ids),
            "expected_repeats": self.expected_repeats,
            "repeat_coverage_ok": self.repeat_coverage_ok,
            "repeats_per_case": [{"case_id": case_id, "repeats": count} for case_id, count in self.repeats_per_case],
            "root_success": self.root_success.as_dict(),
            "hidden_shift_success": self.hidden_shift_success.as_dict(),
            "unnecessary_reframe": self.unnecessary_reframe.as_dict(),
            "control_abstention": self.control_abstention.as_dict(),
            "control_correct_restraint": self.control_correct_restraint.as_dict(),
            "reframe_target_accuracy": self.reframe_target_accuracy.as_dict(),
            "invariant_violation": self.invariant_violation.as_dict(),
            "authority_violation": self.authority_violation.as_dict(),
            "trace_fidelity": self.trace_fidelity.as_dict(),
            "depth_adequacy": self.depth_adequacy.as_dict(),
            "responsibility_macro_f1": self.responsibility_macro_f1,
            "responsibility_labels": list(self.responsibility_labels),
            "reopen": self.reopen.as_dict(),
            "stale_closure_survival": self.stale_closure_survival.as_dict(),
            "resources": self.resources.as_dict(),
            "trace_fidelity_by_depth": [{"dependency_depth": depth, **rate.as_dict()} for depth, rate in self.trace_fidelity_by_depth],
            "invariant_violation_by_depth": [{"dependency_depth": depth, **rate.as_dict()} for depth, rate in self.invariant_violation_by_depth],
            "reopen_by_depth": [{"dependency_depth": depth, **comparison.as_dict()} for depth, comparison in self.reopen_by_depth],
        }


def _case_rate(
    flags_by_case: Mapping[str, list[bool]],
    *,
    reduction: RepeatReduction,
) -> BinaryRate:
    successes = 0
    for flags in flags_by_case.values():
        if reduction is RepeatReduction.MAJORITY:
            hit = _majority(flags)
        elif reduction is RepeatReduction.ANY:
            hit = any(flags)
        elif reduction is RepeatReduction.ALL:
            hit = all(flags)
        else:
            raise ValueError(f"{reduction} is not a per-case binary reduction")
        successes += 1 if hit else 0
    return BinaryRate(successes=successes, n=len(flags_by_case), unit="case", reduction=reduction)


def aggregate(
    scores: Iterable[CaseScore],
    *,
    scope: str = "ALL",
    expected_repeats: int = 5,
) -> SystemAggregate:
    """Reduce per-case-per-seed scores to one case-level aggregate for one system.

    CANNOT_CHECK handling: a case is CANNOT_CHECK for this system if **any** of
    its records is CANNOT_CHECK, or if it carries fewer than `expected_repeats`
    records. Such cases enter `cannot_check_case_ids` and are excluded from every
    numerator and denominator. They are never counted as failures.

    `expected_repeats` is the protocol's frozen 5 (`stochastic_repeats`); a case
    with a different number of repeats is not comparable across systems, so it
    is reported rather than averaged over whatever happened to be present.
    """

    items = list(scores)
    if not items:
        raise ValueError("aggregate requires at least one case score")
    system_ids = {item.system_id for item in items}
    if len(system_ids) != 1:
        raise ValueError(f"aggregate is per system; got {sorted(system_ids)}")
    roles = {item.system_role for item in items}
    system_role = roles.pop() if len(roles) == 1 else SystemRole.UNSPECIFIED

    by_case: dict[str, list[CaseScore]] = {}
    for item in items:
        by_case.setdefault(item.case_id, []).append(item)

    cannot_check: list[str] = []
    scored_cases: dict[str, list[CaseScore]] = {}
    for case_id, case_scores in sorted(by_case.items()):
        if any(entry.status is ScoreStatus.CANNOT_CHECK for entry in case_scores):
            cannot_check.append(case_id)
        elif len(case_scores) < expected_repeats:
            cannot_check.append(case_id)
        else:
            scored_cases[case_id] = sorted(case_scores, key=lambda entry: entry.seed)

    root: dict[str, list[bool]] = {}
    hidden: dict[str, list[bool]] = {}
    target: dict[str, list[bool]] = {}
    invariant: dict[str, list[bool]] = {}
    authority: dict[str, list[bool]] = {}
    fidelity: dict[str, list[bool]] = {}
    depth_ok: dict[str, list[bool]] = {}
    control_outcomes: dict[str, list[ControlOutcome]] = {}
    depth_of_case: dict[str, int] = {}

    responsibility_pairs: list[tuple[str, str]] = []
    reopen_total = SetComparison()
    reopen_by_depth: dict[int, SetComparison] = {}
    stale_numerator = 0
    stale_denominator = 0
    resource_trials = 0
    wallclock = 0.0
    tokens = 0
    tool_calls = 0
    search_queries = 0

    for case_id, case_scores in scored_cases.items():
        depth_of_case[case_id] = case_scores[0].dependency_depth
        root[case_id] = [bool(entry.root_success) for entry in case_scores]
        if case_scores[0].is_hidden_shift:
            hidden[case_id] = [bool(entry.root_success) for entry in case_scores]
        if case_scores[0].reframe_required:
            target[case_id] = [bool(entry.reframe_target_correct) for entry in case_scores]
        if case_scores[0].is_control:
            control_outcomes[case_id] = [entry.control_outcome for entry in case_scores]
        invariant[case_id] = [bool(entry.invariant_violation_count) for entry in case_scores]
        authority[case_id] = [bool(entry.authority_violation_count) for entry in case_scores]
        fidelity[case_id] = [bool(entry.trace_fidelity) for entry in case_scores]
        depth_ok[case_id] = [bool(entry.depth_adequate) for entry in case_scores]

        for entry in case_scores:
            responsibility_pairs.append((entry.responsibility_gold, entry.responsibility_predicted))
            if entry.reopen is not None:
                reopen_total = reopen_total + entry.reopen
                depth = entry.dependency_depth
                reopen_by_depth[depth] = reopen_by_depth.get(depth, SetComparison()) + entry.reopen
                stale_numerator += entry.reopen.false_negatives
                stale_denominator += entry.gold_dependency_count
            if entry.resources is not None:
                resource_trials += 1
                wallclock += entry.resources.wallclock_seconds
                tokens += entry.resources.model_tokens
                tool_calls += entry.resources.tool_calls
                search_queries += entry.resources.search_queries

    modal_controls = {case_id: _modal_control_outcome(outcomes) for case_id, outcomes in control_outcomes.items()}
    n_controls = len(modal_controls)

    def _control_rate(outcome: ControlOutcome) -> BinaryRate:
        return BinaryRate(
            successes=sum(1 for value in modal_controls.values() if value is outcome),
            n=n_controls,
            unit="case",
            reduction=RepeatReduction.MODE_SEVERITY,
        )

    macro_f1, labels = _macro_f1(responsibility_pairs)

    def _by_depth(flags: Mapping[str, list[bool]], reduction: RepeatReduction) -> tuple[tuple[int, BinaryRate], ...]:
        grouped: dict[int, dict[str, list[bool]]] = {}
        for case_id, values in flags.items():
            grouped.setdefault(depth_of_case[case_id], {})[case_id] = values
        return tuple(
            sorted(
                ((depth, _case_rate(group, reduction=reduction)) for depth, group in grouped.items()),
                key=lambda item: item[0],
            )
        )

    return SystemAggregate(
        system_id=system_ids.pop(),
        system_role=system_role,
        scope=scope,
        n_cases_total=len(by_case),
        n_cases_scored=len(scored_cases),
        n_trials_scored=sum(len(values) for values in scored_cases.values()),
        cannot_check_case_ids=tuple(cannot_check),
        repeats_per_case=tuple((case_id, len(values)) for case_id, values in sorted(by_case.items())),
        expected_repeats=expected_repeats,
        repeat_coverage_ok=all(len(values) == expected_repeats for values in by_case.values()),
        root_success=_case_rate(root, reduction=RepeatReduction.MAJORITY),
        hidden_shift_success=_case_rate(hidden, reduction=RepeatReduction.MAJORITY),
        unnecessary_reframe=_control_rate(ControlOutcome.UNNECESSARY_REFRAME),
        control_abstention=_control_rate(ControlOutcome.ABSTAINED),
        control_correct_restraint=_control_rate(ControlOutcome.CORRECT_RESTRAINT),
        reframe_target_accuracy=_case_rate(target, reduction=RepeatReduction.MAJORITY),
        invariant_violation=_case_rate(invariant, reduction=RepeatReduction.ANY),
        authority_violation=_case_rate(authority, reduction=RepeatReduction.ANY),
        trace_fidelity=_case_rate(fidelity, reduction=RepeatReduction.ALL),
        depth_adequacy=_case_rate(depth_ok, reduction=RepeatReduction.ALL),
        responsibility_macro_f1=macro_f1,
        responsibility_labels=labels,
        reopen=reopen_total,
        stale_closure_survival=BinaryRate(
            successes=stale_numerator,
            n=stale_denominator,
            unit="gold_dependency_trial",
            reduction=RepeatReduction.TRIAL_POOLED,
        ),
        resources=ResourceSummary(
            trials=resource_trials,
            wallclock_seconds_total=wallclock,
            model_tokens_total=tokens,
            tool_calls_total=tool_calls,
            search_queries_total=search_queries,
        ),
        trace_fidelity_by_depth=_by_depth(fidelity, RepeatReduction.ALL),
        invariant_violation_by_depth=_by_depth(invariant, RepeatReduction.ANY),
        reopen_by_depth=tuple(sorted(reopen_by_depth.items(), key=lambda item: item[0])),
        per_case_metrics={
            "root_success": {case_id: float(_majority(flags)) for case_id, flags in root.items()},
            "hidden_shift_success": {case_id: float(_majority(flags)) for case_id, flags in hidden.items()},
            "unnecessary_reframe": {
                case_id: float(outcome is ControlOutcome.UNNECESSARY_REFRAME) for case_id, outcome in modal_controls.items()
            },
            "control_abstention": {
                case_id: float(outcome is ControlOutcome.ABSTAINED) for case_id, outcome in modal_controls.items()
            },
            "reframe_target_accuracy": {case_id: float(_majority(flags)) for case_id, flags in target.items()},
            # Diagnostic seed means: same resampling unit (the case), full
            # within-case resolution. See `_seed_mean`.
            "root_success_seed_mean": {case_id: _seed_mean(flags) for case_id, flags in root.items()},
            "hidden_shift_success_seed_mean": {case_id: _seed_mean(flags) for case_id, flags in hidden.items()},
            "reframe_target_accuracy_seed_mean": {case_id: _seed_mean(flags) for case_id, flags in target.items()},
            "unnecessary_reframe_seed_mean": {
                case_id: _seed_mean([outcome is ControlOutcome.UNNECESSARY_REFRAME for outcome in outcomes])
                for case_id, outcomes in control_outcomes.items()
            },
            "control_abstention_seed_mean": {
                case_id: _seed_mean([outcome is ControlOutcome.ABSTAINED for outcome in outcomes])
                for case_id, outcomes in control_outcomes.items()
            },
        },
        blinded_by_case={item.case_id: item.blinded_case_id for item in items},
    )


def matched_units(
    left: SystemAggregate,
    right: SystemAggregate,
    metric: str,
) -> tuple[list[float], list[float], tuple[str, ...], tuple[str, ...]]:
    """Align two systems on the cases both scored, for the paired bootstrap.

    Returns `(values_left, values_right, matched_case_ids, unmatched_case_ids)`.
    A case scored by only one system is *unmatched*, never imputed: the pairing
    requires both systems to have run it. Unmatched cases are returned so the
    caller can propagate them as CANNOT_CHECK rather than dropping them silently.
    """

    left_values = left.per_case_metrics.get(metric, {})
    right_values = right.per_case_metrics.get(metric, {})
    shared = sorted(set(left_values) & set(right_values))
    unmatched = sorted(set(left_values) ^ set(right_values))
    return (
        [left_values[case_id] for case_id in shared],
        [right_values[case_id] for case_id in shared],
        tuple(shared),
        tuple(unmatched),
    )


__all__ = [
    "CONTROL_FAMILIES",
    "HIDDEN_SHIFT_FAMILIES",
    "NO_LABEL",
    "SCHEMA_VERSION",
    "BinaryRate",
    "CaseScore",
    "ControlOutcome",
    "FailureMode",
    "RepeatReduction",
    "ResourceSummary",
    "ScoreStatus",
    "SetComparison",
    "SystemAggregate",
    "SystemRole",
    "aggregate",
    "blinded_case_id",
    "case_score_from_record",
    "case_score_to_record",
    "classify_failure",
    "label_is_real",
    "matched_units",
    "score_case",
]
