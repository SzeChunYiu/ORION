from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from .model import MechanicCell, MechanicDimension


class UncertaintyKind(str, Enum):
    MEASUREMENT = "MEASUREMENT"
    MODEL_FORMALISM = "MODEL_FORMALISM"
    IDENTIFICATION = "IDENTIFICATION"
    SEARCH_COVERAGE = "SEARCH_COVERAGE"
    IDENTITY_PROVENANCE = "IDENTITY_PROVENANCE"
    EXECUTION_VARIABILITY = "EXECUTION_VARIABILITY"
    RESPONSIBILITY_CAUSAL = "RESPONSIBILITY_CAUSAL"
    RESOURCE_CENSORING = "RESOURCE_CENSORING"


class UncertaintyRepresentation(str, Enum):
    INTERVAL = "INTERVAL"
    SET_VALUED = "SET_VALUED"
    DISTRIBUTION = "DISTRIBUTION"
    ALTERNATIVE_HYPOTHESES = "ALTERNATIVE_HYPOTHESES"
    BOUNDS = "BOUNDS"
    UNKNOWN = "UNKNOWN"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class UncertaintyRule:
    rule_id: str
    mechanic_id: str
    kind: UncertaintyKind
    default_representation: UncertaintyRepresentation
    source: str
    propagation_semantics: str
    reduction_evidence: str
    forbidden_collapse: str

    def __post_init__(self) -> None:
        required = (self.rule_id, self.mechanic_id, self.source, self.propagation_semantics, self.reduction_evidence, self.forbidden_collapse)
        if any(not item.strip() for item in required):
            raise ValueError("uncertainty rule fields cannot be empty")


@dataclass(frozen=True)
class MechanicUncertaintyPlan:
    mechanic_id: str
    rules: tuple[UncertaintyRule, ...]
    probability_policy: str
    step_specific_quantification_open: bool = True

    def __post_init__(self) -> None:
        if not self.mechanic_id.strip() or not self.rules or not self.probability_policy.strip():
            raise ValueError("uncertainty plan requires identity/rules/probability policy")
        if any(item.mechanic_id != self.mechanic_id for item in self.rules):
            raise ValueError("uncertainty rule mechanic mismatch")


def _rule(cell: MechanicCell, kind: UncertaintyKind, representation: UncertaintyRepresentation, source: str, propagation: str, reduction: str, forbidden: str) -> UncertaintyRule:
    return UncertaintyRule(
        rule_id=f"uncertainty:{cell.mechanic_id}:{kind.value.lower()}",
        mechanic_id=cell.mechanic_id,
        kind=kind,
        default_representation=representation,
        source=source,
        propagation_semantics=propagation,
        reduction_evidence=reduction,
        forbidden_collapse=forbidden,
    )


def default_uncertainty_plan(cell: MechanicCell) -> MechanicUncertaintyPlan:
    return MechanicUncertaintyPlan(
        mechanic_id=cell.mechanic_id,
        rules=(
            _rule(cell, UncertaintyKind.MEASUREMENT, UncertaintyRepresentation.BOUNDS, "instrument/observation/model error in measured quantities", "propagate only through a declared measurement/transform model; correlated dependence is preserved when relevant", "calibration, repeated/independent measurement, stronger instrument or validated measurement model", "do not report a bare point value as if measurement uncertainty were zero"),
            _rule(cell, UncertaintyKind.MODEL_FORMALISM, UncertaintyRepresentation.SET_VALUED, "multiple compatible representations/models or an approximate formalism", "retain the surviving model/formalism set or explicit approximation/error semantics", "discriminating evidence, theorem, hostile case or stronger representation that rules out alternatives", "do not convert model plurality into one confidence-weighted winner without a licensed model-selection rule"),
            _rule(cell, UncertaintyKind.IDENTIFICATION, UncertaintyRepresentation.BOUNDS, "evidence constrains but does not uniquely determine the target quantity/mechanism", "propagate an identified set/bounds to downstream decisions", "new evidence/intervention/assumption justified strongly enough to shrink the identified set", "do not replace partial identification with a point estimate solely for convenience"),
            _rule(cell, UncertaintyKind.SEARCH_COVERAGE, UncertaintyRepresentation.UNKNOWN, "unknown relevant sources/domains/representations outside the searched universe", "carry open coverage residuals and bounded-saturation scope/cutoff", "heterogeneous route/source/domain challenges, fresh search and omission audits", "zero new hits in one route is not zero probability of missing knowledge"),
            _rule(cell, UncertaintyKind.IDENTITY_PROVENANCE, UncertaintyRepresentation.ALTERNATIVE_HYPOTHESES, "ambiguous entity/event/source/claim identity or lineage", "keep alternative identity/linkage hypotheses until witnessed", "stable identifiers, source selectors, mapping witnesses or independent provenance checks", "do not merge records/claims because labels look similar"),
            _rule(cell, UncertaintyKind.EXECUTION_VARIABILITY, UncertaintyRepresentation.INTERVAL, "stochastic provider/model/tool/runtime variation across comparable runs", "retain run identity and empirical variation; use distributions only when sampling/calibration supports them", "replicated matched executions or deterministic/replayable execution paths", "do not treat one stochastic run as the deterministic mechanic output"),
            _rule(cell, UncertaintyKind.RESPONSIBILITY_CAUSAL, UncertaintyRepresentation.ALTERNATIVE_HYPOTHESES, "multiple plausible causes/responsible layers for a residual/failure", "block high-impact repair while material responsibility alternatives remain", "a discriminator/intervention that separates causes", "repeated recurrence does not by itself prove a cause"),
            _rule(cell, UncertaintyKind.RESOURCE_CENSORING, UncertaintyRepresentation.CANNOT_CHECK, "budget/time/tool limits stop observation while obligations remain open", "retain open obligations and resource-bound terminal", "additional justified resources or a cheaper valid discriminator", "resource exhaustion cannot be represented as evidence of closure"),
        ),
        probability_policy="Probability distributions are used only where calibrated data/model assumptions justify them. Otherwise retain intervals, sets, alternative hypotheses, bounds, UNKNOWN or CANNOT_CHECK.",
        step_specific_quantification_open=True,
    )


def apply_default_uncertainty_plan(cell: MechanicCell) -> MechanicCell:
    plan = default_uncertainty_plan(cell)
    semantics = (plan.probability_policy, *tuple(f"{item.rule_id}:{item.default_representation.value}:{item.propagation_semantics}" for item in plan.rules))
    empirical_open = tuple(dict.fromkeys(cell.empirical_open_coordinates + ("step-specific uncertainty sources, dependence structure, calibration/coverage, propagation law and decision consequences",)))
    provisional = tuple(dict.fromkeys((*cell.provisional_dimensions, MechanicDimension.UNCERTAINTY)))
    return replace(cell, uncertainty_semantics=semantics, empirical_open_coordinates=empirical_open, provisional_dimensions=provisional)


def apply_default_uncertainty_plans(cells: tuple[MechanicCell, ...]) -> tuple[MechanicCell, ...]:
    return tuple(apply_default_uncertainty_plan(cell) for cell in cells)
