from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from .model import MechanicCell


class SaturationCoordinate(str, Enum):
    KNOWLEDGE = "KNOWLEDGE"
    FORMULATION = "FORMULATION"
    ROUTE_COVERAGE = "ROUTE_COVERAGE"
    PARENT_DOMAIN = "PARENT_DOMAIN"
    CONTRADICTION_OBSTRUCTION = "CONTRADICTION_OBSTRUCTION"
    FAILURE_EXPERIENCE = "FAILURE_EXPERIENCE"
    METHOD_OPERATOR = "METHOD_OPERATOR"


@dataclass(frozen=True)
class SaturationCoordinateRule:
    coordinate: SaturationCoordinate
    flatness_semantics: str
    reopen_trigger: str

    def __post_init__(self) -> None:
        if not self.flatness_semantics.strip() or not self.reopen_trigger.strip():
            raise ValueError("saturation coordinate requires flatness and reopen semantics")


@dataclass(frozen=True)
class MechanicSaturationPlan:
    mechanic_id: str
    basis_id: str
    minimum_consecutive_flat_rounds: int
    coordinates: tuple[SaturationCoordinateRule, ...]
    required_audits: tuple[str, ...]
    false_saturation_challenges: tuple[str, ...]
    resource_bound_semantics: str
    freshness_semantics: str

    def __post_init__(self) -> None:
        if not self.mechanic_id.strip() or not self.basis_id.strip() or self.minimum_consecutive_flat_rounds < 1:
            raise ValueError("saturation plan requires identity/basis and positive flat-round count")
        if not self.coordinates or not self.required_audits or not self.false_saturation_challenges:
            raise ValueError("saturation plan requires coordinates, audits and false-saturation challenges")

    @property
    def absolute_complete(self) -> bool:
        return False


def default_saturation_plan(cell: MechanicCell) -> MechanicSaturationPlan:
    return MechanicSaturationPlan(
        mechanic_id=cell.mechanic_id,
        basis_id=f"saturation-basis:{cell.mechanic_id}:shadow-v0",
        minimum_consecutive_flat_rounds=2,
        coordinates=(
            SaturationCoordinateRule(SaturationCoordinate.KNOWLEDGE, "No new retained material mechanism, evidence root, contradiction/counterexample, assumption/scope update, derivation or unresolved-fibre update after typed deduplication.", "Any new material knowledge object or evidence-lineage change."),
            SaturationCoordinateRule(SaturationCoordinate.FORMULATION, "Question, representation, decomposition, interface, measurement and evaluator audits produce no material target-relevant change.", "Any supported reframe of question/representation/decomposition/interface/measurement/evaluator."),
            SaturationCoordinateRule(SaturationCoordinate.ROUTE_COVERAGE, "All applicable registered route obligations have execution or justified-inapplicability receipts and route neighborhoods are stable at the declared cutoff.", "Any uncovered applicable route, unstable citation/source neighborhood or route implementation change."),
            SaturationCoordinateRule(SaturationCoordinate.PARENT_DOMAIN, "Parent-domain searches and assimilation no longer add a material variable, mechanism, failure mode, validation practice or alternative decomposition.", "Discovery of a new relevant discipline or a known discipline yielding a new material coordinate."),
            SaturationCoordinateRule(SaturationCoordinate.CONTRADICTION_OBSTRUCTION, "No new material contradiction, obstruction, discriminator or identified-set boundary appears.", "Any new conflict/obstruction/discriminator or changed compatibility context."),
            SaturationCoordinateRule(SaturationCoordinate.FAILURE_EXPERIENCE, "Fresh/variant episodes add no new material failure pattern, harmful control, guard candidate or transfer boundary relevant to this mechanic.", "A fresh/variant failure or guard-transfer result changes the failure/lesson map."),
            SaturationCoordinateRule(SaturationCoordinate.METHOD_OPERATOR, "No new operator/method challenger survives failure attribution and reaches an evidence-bearing evaluation obligation.", "A new supported method/operator residual or challenger changes the method frontier."),
        ),
        required_audits=(
            "registered search-route coverage audit",
            "parent-domain and nearest-work equivalence audit",
            "independent/adversarial omission challenge",
            "freshness/searched-through cutoff audit",
            "evidence-lineage independence audit",
            "operator-order/processing-order perturbation where order could affect the retained substantive state",
        ),
        false_saturation_challenges=(
            "mask current framework/domain vocabulary and rerun function-only search",
            "ask which mature discipline would describe the same operation using variables absent from the current cell",
            "search historical/mathematical/implementation analogues outside the incumbent literature neighborhood",
            "attempt to construct a counterexample or task variation that changes the decision while current growth coordinates remain flat",
            "reverse or perturb material expansion/consolidation/review order and check whether substantive retained state changes",
            "inspect present-but-missed, retrieved-but-unused and resource-censored failure classes separately from absent knowledge",
        ),
        resource_bound_semantics="If resources expire while any material coordinate/audit remains open, return CANNOT_CHECK_RESOURCE_BOUND; never round up to saturated or down to scientific refutation.",
        freshness_semantics="Every bounded saturation receipt records the searched-through/evidence cutoff. Material work after that cutoff or a changed route implementation can reopen the receipt.",
    )


def apply_default_saturation_plan(cell: MechanicCell) -> MechanicCell:
    plan = default_saturation_plan(cell)
    criteria = (
        f"basis={plan.basis_id}",
        f"minimum_consecutive_flat_rounds={plan.minimum_consecutive_flat_rounds}",
        *tuple(f"coordinate:{item.coordinate.value}:{item.flatness_semantics}:reopen={item.reopen_trigger}" for item in plan.coordinates),
        *tuple(f"audit:{item}" for item in plan.required_audits),
        *tuple(f"false_saturation_challenge:{item}" for item in plan.false_saturation_challenges),
        plan.resource_bound_semantics,
        plan.freshness_semantics,
        "absolute_complete=false",
    )
    empirical_open = tuple(
        dict.fromkeys(
            cell.empirical_open_coordinates
            + (
                "prospective false-saturation recall, flat-round calibration, route/parent-domain adequacy and stopping utility on fresh real tasks",
            )
        )
    )
    return replace(cell, saturation_criteria=criteria, empirical_open_coordinates=empirical_open)


def apply_default_saturation_plans(cells: tuple[MechanicCell, ...]) -> tuple[MechanicCell, ...]:
    return tuple(apply_default_saturation_plan(cell) for cell in cells)
