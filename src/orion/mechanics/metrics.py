from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from .model import MechanicCell, MetricDirection, MetricKind, MetricSpec


class MetricRole(str, Enum):
    BLOCKING_GATE = "BLOCKING_GATE"
    ROOT_EFFECTIVENESS = "ROOT_EFFECTIVENESS"
    LOCAL_PERFORMANCE = "LOCAL_PERFORMANCE"
    COVERAGE = "COVERAGE"
    RELIABILITY = "RELIABILITY"
    RESOURCE = "RESOURCE"
    UNCERTAINTY = "UNCERTAINTY"
    DIAGNOSTIC = "DIAGNOSTIC"


@dataclass(frozen=True)
class MetricRequirement:
    spec: MetricSpec
    role: MetricRole
    source_observation_ids: tuple[str, ...]
    decision_use: str
    root_transport_requirement: str
    construct_validity_note: str

    def __post_init__(self) -> None:
        if not self.source_observation_ids or any(not item.strip() for item in (self.decision_use, self.root_transport_requirement, self.construct_validity_note)):
            raise ValueError("metric requirement requires observations, decision use, root transport and validity note")


@dataclass(frozen=True)
class MechanicMetricPlan:
    mechanic_id: str
    requirements: tuple[MetricRequirement, ...]
    scalar_aggregation_policy: str
    step_specific_construct_open: bool = True

    def __post_init__(self) -> None:
        if not self.mechanic_id.strip() or not self.requirements or not self.scalar_aggregation_policy.strip():
            raise ValueError("metric plan requires identity, requirements and scalar policy")
        ids = [item.spec.metric_id for item in self.requirements]
        if len(set(ids)) != len(ids):
            raise ValueError("metric plan ids must be unique")


def _metric(cell: MechanicCell, suffix: str, description: str, kind: MetricKind, direction: MetricDirection, unit: str, role: MetricRole, source: tuple[str, ...], decision_use: str, root_transport: str, validity: str, *, threshold: str = "", uncertainty: str = "") -> MetricRequirement:
    return MetricRequirement(
        spec=MetricSpec(
            metric_id=f"metric:{cell.mechanic_id}:{suffix}",
            description=description,
            kind=kind,
            direction=direction,
            unit=unit,
            required_for_handoff=True,
            threshold_semantics=threshold,
            uncertainty_semantics=uncertainty,
        ),
        role=role,
        source_observation_ids=source,
        decision_use=decision_use,
        root_transport_requirement=root_transport,
        construct_validity_note=validity,
    )


def default_metric_plan(cell: MechanicCell) -> MechanicMetricPlan:
    prefix = f"observe:{cell.mechanic_id}:"
    reqs = (
        _metric(cell, "contract-gate", "Whether all blocking mechanic/authority/interface invariants pass.", MetricKind.SAFETY, MetricDirection.NON_COMPENSATORY_GATE, "bool", MetricRole.BLOCKING_GATE, (prefix + "run-status", prefix + "handoff-presence"), "Block promotion/finalization when false.", "No local metric may compensate for failure of this gate.", "Direct software/governance construct; still requires actual invariant checks.", threshold="must be true"),
        _metric(cell, "root-progress", "Change in the registered root-relevant obligation/effectiveness coordinate attributable to this mechanic.", MetricKind.QUALITY, MetricDirection.OBSERVE_ONLY, "typed_delta", MetricRole.ROOT_EFFECTIVENESS, (prefix + "residuals", prefix + "evidence-lineage"), "Determine whether local work advanced the root problem.", "Requires an explicit local-to-root transport witness; otherwise report local-only progress.", "The root construct is task-specific and cannot be replaced by a universal score."),
        _metric(cell, "residual-delta", "Change in material residual obligations attributable to the mechanic.", MetricKind.DIAGNOSTIC, MetricDirection.MINIMIZE, "count_delta", MetricRole.DIAGNOSTIC, (prefix + "residuals",), "Detect closure, stagnation or new gaps.", "Residual contraction counts as root progress only for root-relevant residuals.", "Residual detectors have bounded coverage; zero observed residuals is not completeness."),
        _metric(cell, "coverage-delta", "New relevant route/source/representation/evidence coverage attributable to the mechanic.", MetricKind.COVERAGE, MetricDirection.MAXIMIZE, "typed_count_delta", MetricRole.COVERAGE, (prefix + "evidence-lineage",), "Detect novelty/coverage gain and false flatness.", "Coverage gain must be relevance/lineage qualified; raw count is not root progress.", "Coverage is a proxy whose universe and relevance definition must be declared."),
        _metric(cell, "failure-rate", "Rate of failed/partial/blocked executions over a declared comparable episode set.", MetricKind.RELIABILITY, MetricDirection.MINIMIZE, "fraction", MetricRole.RELIABILITY, (prefix + "run-status",), "Monitor reliability and identify recurring failure classes.", "Lower failure rate cannot compensate for weakened tasks/evaluators or hidden cannot-check cases.", "Episode comparability and censoring policy are required for interpretation.", uncertainty="report sample size/interval or identified range when meaningful"),
        _metric(cell, "cost", "Normalized resource cost consumed by the mechanic.", MetricKind.COST, MetricDirection.MINIMIZE, "cost_unit", MetricRole.RESOURCE, (prefix + "cost",), "Compare matched-resource alternatives and enforce budget.", "Cost reduction counts only under preserved task/evaluator/quality gates.", "Valid only under the active provider cost/accounting model."),
        _metric(cell, "latency", "Wall-clock completion latency.", MetricKind.LATENCY, MetricDirection.MINIMIZE, "s", MetricRole.RESOURCE, (prefix + "latency",), "Control responsiveness and detect regressions.", "Latency improvement counts only under preserved outputs/invariants.", "Scheduling/environment effects limit cross-run comparability."),
        _metric(cell, "uncertainty-open", "Amount/type of unresolved uncertainty or cannot-check obligations after the mechanic.", MetricKind.UNCERTAINTY, MetricDirection.OBSERVE_ONLY, "typed_set", MetricRole.UNCERTAINTY, (prefix + "residuals",), "Prevent hidden uncertainty from being collapsed into a point score.", "Uncertainty reduction is useful only if caused by evidence/identification rather than discarded alternatives.", "Uncertainty semantics are mechanic-specific and may be interval/set/non-probabilistic."),
        _metric(cell, "blocking-regressions", "Count of newly violated blocking/root-interface/authority invariants.", MetricKind.SAFETY, MetricDirection.NON_COMPENSATORY_GATE, "count", MetricRole.BLOCKING_GATE, (prefix + "run-status", prefix + "residuals"), "Reject false progress/harmful changes.", "No positive metric may compensate for a blocking regression.", "Requires explicit invariant instrumentation.", threshold="must equal 0"),
    )
    return MechanicMetricPlan(
        mechanic_id=cell.mechanic_id,
        requirements=reqs,
        scalar_aggregation_policy="No universal scalar score. Hard gates are non-compensatory; any scalar utility/tradeoff requires an explicit scoped decision model and preserves the underlying metric vector.",
        step_specific_construct_open=True,
    )


def apply_default_metric_plan(cell: MechanicCell) -> MechanicCell:
    plan = default_metric_plan(cell)
    empirical_open = tuple(dict.fromkeys(cell.empirical_open_coordinates + ("step-specific effectiveness/performance constructs, metric validity/reliability/calibration, comparability and decision thresholds",)))
    return replace(cell, metrics=tuple(item.spec for item in plan.requirements), empirical_open_coordinates=empirical_open)


def apply_default_metric_plans(cells: tuple[MechanicCell, ...]) -> tuple[MechanicCell, ...]:
    return tuple(apply_default_metric_plan(cell) for cell in cells)
