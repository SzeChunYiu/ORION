from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from orion.self_orion.rakl_donor_gate import (
    RaklDonorAudit,
    assess_rakl_donor_audit,
)
from orion.self_orion.saturation_vector import (
    DevelopmentSaturationAxis,
    DevelopmentSaturationReport,
)


class InventionTarget(str, Enum):
    NONE = "NONE"
    REPRESENTATION = "REPRESENTATION"
    OPERATOR = "OPERATOR"
    ONTOLOGY = "ONTOLOGY"


@dataclass(frozen=True)
class InventionReadinessEvidence:
    stable_residual_variation_ids: tuple[str, ...]
    ordinary_causes_excluded: bool
    cross_domain_routes_bounded_flat: bool
    representation_gap_supported: bool
    method_basis_gap_supported: bool
    ontology_gap_supported: bool
    discriminator_evidence_ids: tuple[str, ...]
    rakl_donor_audit: RaklDonorAudit | None = None
    method_challenger_id: str = ""


@dataclass(frozen=True)
class InventionReadinessReport:
    ready: bool
    target: InventionTarget
    reasons: tuple[str, ...]

    @property
    def grants_invention_authority(self) -> bool:
        return False

    @property
    def grants_promotion_authority(self) -> bool:
        return False


def assess_invention_readiness(
    saturation: DevelopmentSaturationReport,
    evidence: InventionReadinessEvidence,
    *,
    min_distinct_residual_variations: int = 2,
) -> InventionReadinessReport:
    """Require evidence before escalating a failure into representation/method invention.

    Clean-generation invention is a last resort. In addition to the existing
    failure-attribution and saturation requirements, the target must carry a
    target-specific, pinned RAKL donor audit. If RAKL already contains an exact
    or reconstructable surviving donor, invention is blocked and the donor is
    the required next action.
    """

    if min_distinct_residual_variations < 1:
        raise ValueError("minimum residual variations must be positive")
    required_axes = (
        DevelopmentSaturationAxis.KNOWLEDGE,
        DevelopmentSaturationAxis.SEARCH_UNIVERSE,
        DevelopmentSaturationAxis.OPERATOR,
        DevelopmentSaturationAxis.PATH,
    )
    reasons: list[str] = []
    missing_axes = tuple(axis.value for axis in required_axes if not saturation.flat(axis))
    if missing_axes:
        reasons.append("unsaturated_axes:" + ",".join(missing_axes))
    distinct_variations = len(set(evidence.stable_residual_variation_ids))
    if distinct_variations < min_distinct_residual_variations:
        reasons.append("residual_not_stable_across_distinct_variations")
    if not evidence.ordinary_causes_excluded:
        reasons.append("ordinary_failure_causes_not_excluded")
    if not evidence.cross_domain_routes_bounded_flat:
        reasons.append("cross_domain_transfer_search_not_bounded_flat")
    if not evidence.discriminator_evidence_ids:
        reasons.append("discriminator_evidence_missing")

    # Method-level invention requires a registered method challenger record
    # showing that the method-evolution search/absorb ladder was exhausted
    # before escalating to clean-sheet invention.
    if evidence.method_basis_gap_supported and not evidence.method_challenger_id:
        reasons.append("method_challenger_not_registered")

    if evidence.rakl_donor_audit is None:
        reasons.append("rakl_donor_audit_missing")
    else:
        donor_report = assess_rakl_donor_audit(evidence.rakl_donor_audit)
        if not donor_report.admissible:
            reasons.extend(
                "rakl_donor_audit_inadmissible:" + reason
                for reason in donor_report.reasons
                if not reason.startswith("rakl_surviving_donor_available:")
            )
        if donor_report.invention_preempted_by_reuse:
            reasons.append(
                "rakl_surviving_donor_available:"
                + ",".join(donor_report.reusable_donor_ids)
            )

    supported_targets = sum(
        (
            evidence.representation_gap_supported,
            evidence.method_basis_gap_supported,
            evidence.ontology_gap_supported,
        )
    )
    if supported_targets == 0:
        reasons.append("no_specific_missing_structure_supported")
    elif supported_targets > 1:
        reasons.append("invention_target_responsibility_ambiguous")
    if reasons:
        return InventionReadinessReport(False, InventionTarget.NONE, tuple(reasons))
    target = (
        InventionTarget.ONTOLOGY
        if evidence.ontology_gap_supported
        else InventionTarget.OPERATOR
        if evidence.method_basis_gap_supported
        else InventionTarget.REPRESENTATION
    )
    return InventionReadinessReport(
        True,
        target,
        (
            "relevant axes are bounded-flat, repeated residuals survive distinct variations, ordinary causes are excluded, discriminator evidence supports one missing-structure class, and a pinned RAKL donor audit found no surviving donor that should be reused instead",
        ),
    )


__all__ = [
    "InventionReadinessEvidence",
    "InventionReadinessReport",
    "InventionTarget",
    "assess_invention_readiness",
]
