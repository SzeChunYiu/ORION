"""Reviewed V2 bounded epistemic-study surface.

The original V1 implementation is preserved in ``bounded_epistemic_study_v1``.
V2 keeps the same non-authorizing data model and interaction bookkeeping, but
makes evaluator/authority separation load-bearing for frozen atom studies.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from . import bounded_epistemic_study_v1 as _v1
from .canonical import content_digest


ReachabilityStatus = _v1.ReachabilityStatus
ReachabilityDeltaStatus = _v1.ReachabilityDeltaStatus
ResourceBound = _v1.ResourceBound
ReachabilityWitness = _v1.ReachabilityWitness
ReachabilityDeltaReport = _v1.ReachabilityDeltaReport
ContractInteractionReport = _v1.ContractInteractionReport

build_resource_bound = _v1.build_resource_bound
build_reachability_witness = _v1.build_reachability_witness
compare_reachability = _v1.compare_reachability
analyze_contract_interaction = _v1.analyze_contract_interaction


@dataclass(frozen=True)
class BoundedEpistemicAtomStudy(_v1.BoundedEpistemicAtomStudy):
    """V2 study record with explicit evaluator/authority independence."""

    def verify(self) -> None:
        super().verify()
        if self.evaluator_id == self.authority_owner_id:
            raise ValueError(
                "atom study evaluator must be independent of the authority owner"
            )


def build_atom_study(
    *,
    atom_id: str,
    structure_version: str,
    target_contract_ids: Sequence[str],
    resource_bound: ResourceBound,
    positive_case_ids: Sequence[str],
    no_atom_control_ids: Sequence[str],
    parent_baseline_ids: Sequence[str],
    evaluator_id: str,
    authority_owner_id: str,
    parent_atom_ids: Sequence[str] = (),
    ablation_or_replacement_ids: Sequence[str] = (),
    decomposition_hypotheses: Sequence[str] = (),
    interaction_hypotheses: Sequence[str] = (),
    recursion_stop_rules: Sequence[str] = (),
    protected_field_ids: Sequence[str] = (),
    outcome_accessed: bool = False,
) -> BoundedEpistemicAtomStudy:
    resource_bound.verify()
    payload = {
        "version": "BoundedEpistemicAtomStudy.v1",
        "atom_id": str(atom_id),
        "parent_atom_ids": list(_v1._ordered(parent_atom_ids)),
        "structure_version": str(structure_version),
        "target_contract_ids": list(_v1._sorted_unique(target_contract_ids)),
        "resource_bound": resource_bound.unsigned(),
        "positive_case_ids": list(_v1._sorted_unique(positive_case_ids)),
        "no_atom_control_ids": list(_v1._sorted_unique(no_atom_control_ids)),
        "parent_baseline_ids": list(_v1._sorted_unique(parent_baseline_ids)),
        "ablation_or_replacement_ids": list(
            _v1._sorted_unique(ablation_or_replacement_ids)
        ),
        "decomposition_hypotheses": list(
            _v1._sorted_unique(decomposition_hypotheses)
        ),
        "interaction_hypotheses": list(_v1._sorted_unique(interaction_hypotheses)),
        "recursion_stop_rules": list(_v1._sorted_unique(recursion_stop_rules)),
        "evaluator_id": str(evaluator_id),
        "authority_owner_id": str(authority_owner_id),
        "protected_field_ids": list(_v1._sorted_unique(protected_field_ids)),
        "outcome_accessed": bool(outcome_accessed),
        "grants_scientific_authority": False,
    }
    study = BoundedEpistemicAtomStudy(
        atom_id=payload["atom_id"],
        parent_atom_ids=tuple(payload["parent_atom_ids"]),
        structure_version=payload["structure_version"],
        target_contract_ids=tuple(payload["target_contract_ids"]),
        resource_bound=resource_bound,
        positive_case_ids=tuple(payload["positive_case_ids"]),
        no_atom_control_ids=tuple(payload["no_atom_control_ids"]),
        parent_baseline_ids=tuple(payload["parent_baseline_ids"]),
        ablation_or_replacement_ids=tuple(payload["ablation_or_replacement_ids"]),
        decomposition_hypotheses=tuple(payload["decomposition_hypotheses"]),
        interaction_hypotheses=tuple(payload["interaction_hypotheses"]),
        recursion_stop_rules=tuple(payload["recursion_stop_rules"]),
        evaluator_id=payload["evaluator_id"],
        authority_owner_id=payload["authority_owner_id"],
        protected_field_ids=tuple(payload["protected_field_ids"]),
        outcome_accessed=payload["outcome_accessed"],
        digest=content_digest(payload),
    )
    study.verify()
    return study


__all__ = [
    "BoundedEpistemicAtomStudy",
    "ContractInteractionReport",
    "ReachabilityDeltaReport",
    "ReachabilityDeltaStatus",
    "ReachabilityStatus",
    "ReachabilityWitness",
    "ResourceBound",
    "analyze_contract_interaction",
    "build_atom_study",
    "build_reachability_witness",
    "build_resource_bound",
    "compare_reachability",
]
