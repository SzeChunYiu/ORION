from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from .model import MechanicCell


class DiagnosisState(str, Enum):
    UNCLASSIFIED = "UNCLASSIFIED"
    MULTIPLE_HYPOTHESES = "MULTIPLE_HYPOTHESES"
    DISCRIMINATOR_REQUIRED = "DISCRIMINATOR_REQUIRED"
    LOCALLY_ATTRIBUTED = "LOCALLY_ATTRIBUTED"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class MechanicDiagnosisPlan:
    mechanic_id: str
    hypothesis_sources: tuple[str, ...]
    evidence_inputs: tuple[str, ...]
    discriminator_rule: str
    attribution_rule: str
    recurrence_rule: str
    unresolved_rule: str

    def __post_init__(self) -> None:
        if not self.mechanic_id.strip() or not self.hypothesis_sources or not self.evidence_inputs:
            raise ValueError("diagnosis plan requires identity, hypothesis sources and evidence inputs")
        if any(not value.strip() for value in (self.discriminator_rule, self.attribution_rule, self.recurrence_rule, self.unresolved_rule)):
            raise ValueError("diagnosis plan requires discriminator/attribution/recurrence/unresolved rules")


def default_diagnosis_plan(cell: MechanicCell) -> MechanicDiagnosisPlan:
    return MechanicDiagnosisPlan(
        mechanic_id=cell.mechanic_id,
        hypothesis_sources=(
            "registered failure-mode cause hypotheses",
            "current residual responsibility layers",
            "structurally similar prior task/mechanic episodes",
            "dependency/upstream failures and interface violations",
            "representation/search/measurement/evaluator/method alternatives",
        ),
        evidence_inputs=(
            "pre/post state identity",
            "observability/metric receipts",
            "failure-mode detector outputs",
            "dependency/evaluator/provider versions",
            "prior episode/negative-history matches",
            "counterfactual/intervention/discriminator outcomes where available",
        ),
        discriminator_rule=(
            "When multiple material cause/responsibility hypotheses imply different repairs, select or design an observation/computation/experiment whose possible outcomes separate them before high-impact revision."
        ),
        attribution_rule=(
            "Attribute responsibility only to the narrowest layer/cause supported by discriminating evidence; retain competing hypotheses or bounds when evidence cannot identify one cause."
        ),
        recurrence_rule=(
            "Repeated failures across variations increase evidence that a failure pattern is stable, but do not by themselves prove causal responsibility or authorize a reusable guard."
        ),
        unresolved_rule=(
            "If required distinguishing evidence cannot be acquired or resources expire, retain MULTIPLE_HYPOTHESES/CANNOT_CHECK and block repairs whose validity depends on choosing one cause."
        ),
    )


def apply_default_diagnosis_plan(cell: MechanicCell) -> MechanicCell:
    plan = default_diagnosis_plan(cell)
    empirical_open = tuple(dict.fromkeys(cell.empirical_open_coordinates + ("step-specific diagnosis hypothesis space, detectability/identifiability, discriminator quality, causal calibration and diagnosis cost",)))
    return replace(
        cell,
        diagnosis_semantics=(
            *tuple(f"hypothesis_source:{item}" for item in plan.hypothesis_sources),
            *tuple(f"evidence_input:{item}" for item in plan.evidence_inputs),
            plan.discriminator_rule,
            plan.attribution_rule,
            plan.recurrence_rule,
            plan.unresolved_rule,
        ),
        empirical_open_coordinates=empirical_open,
    )


def apply_default_diagnosis_plans(cells: tuple[MechanicCell, ...]) -> tuple[MechanicCell, ...]:
    return tuple(apply_default_diagnosis_plan(cell) for cell in cells)
