"""Bounded, non-authorizing study objects for recursive epistemic atoms.

The module does not define a universal discovery grammar and does not compute
scientific reachability from raw science.  It binds externally supplied
reachability witnesses, pre-outcome atom-study protocols, and simple set-level
interaction bookkeeping so #507 can recursively test proposed atoms without
turning ablation labels into scientific authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

from .canonical import content_digest


def _sorted_unique(values: Sequence[str]) -> tuple[str, ...]:
    return tuple(sorted({str(value) for value in values}))


def _ordered(values: Sequence[str]) -> tuple[str, ...]:
    return tuple(str(value) for value in values)


def _canonical_pairs(values: Mapping[str, float]) -> tuple[tuple[str, float], ...]:
    rows: list[tuple[str, float]] = []
    for raw_name, raw_value in values.items():
        name = str(raw_name)
        if not name:
            raise ValueError("resource name is required")
        value = float(raw_value)
        if value < 0:
            raise ValueError("resource bounds must be non-negative")
        rows.append((name, value))
    rows.sort(key=lambda row: row[0])
    if not rows:
        raise ValueError("at least one named resource bound is required")
    return tuple(rows)


class ReachabilityStatus(str, Enum):
    REACHABLE = "REACHABLE"
    UNREACHABLE = "UNREACHABLE"
    UNRESOLVED = "UNRESOLVED"


class ReachabilityDeltaStatus(str, Enum):
    OLD_UNREACHABLE_NEW_REACHABLE = "OLD_UNREACHABLE_NEW_REACHABLE"
    OLD_UNRESOLVED_NEW_REACHABLE = "OLD_UNRESOLVED_NEW_REACHABLE"
    NO_REACHABILITY_EXPANSION = "NO_REACHABILITY_EXPANSION"
    REGRESSION = "REGRESSION"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class ResourceBound:
    resources: tuple[tuple[str, float], ...]
    digest: str

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "EpistemicResourceBound.v1",
            "resources": [[name, value] for name, value in self.resources],
        }

    def verify(self) -> None:
        if not self.resources:
            raise ValueError("resource bound requires at least one resource")
        names = [name for name, _ in self.resources]
        if names != sorted(set(names)):
            raise ValueError("resource names must be unique and canonical")
        if any(not name or value < 0 for name, value in self.resources):
            raise ValueError("invalid resource bound")
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("resource bound digest mismatch")


def build_resource_bound(resources: Mapping[str, float]) -> ResourceBound:
    rows = _canonical_pairs(resources)
    payload = {
        "version": "EpistemicResourceBound.v1",
        "resources": [[name, value] for name, value in rows],
    }
    bound = ResourceBound(resources=rows, digest=content_digest(payload))
    bound.verify()
    return bound


@dataclass(frozen=True)
class ReachabilityWitness:
    regime_id: str
    contract_id: str
    resource_bound: ResourceBound
    status: ReachabilityStatus
    witness_ids: tuple[str, ...]
    evaluator_id: str
    protected: bool
    digest: str

    @property
    def grants_scientific_authority(self) -> bool:
        return False

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "BoundedReachabilityWitness.v1",
            "regime_id": self.regime_id,
            "contract_id": self.contract_id,
            "resource_bound": self.resource_bound.unsigned(),
            "status": self.status.value,
            "witness_ids": list(self.witness_ids),
            "evaluator_id": self.evaluator_id,
            "protected": self.protected,
            "grants_scientific_authority": False,
        }

    def verify(self) -> None:
        self.resource_bound.verify()
        if not self.regime_id or not self.contract_id:
            raise ValueError("regime and contract identities are required")
        if not self.evaluator_id:
            raise ValueError("reachability evaluator identity is required")
        if not self.witness_ids:
            raise ValueError("reachability status requires at least one witness/reason identity")
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("reachability witness digest mismatch")


def build_reachability_witness(
    *,
    regime_id: str,
    contract_id: str,
    resource_bound: ResourceBound,
    status: ReachabilityStatus,
    witness_ids: Sequence[str],
    evaluator_id: str,
    protected: bool = False,
) -> ReachabilityWitness:
    resource_bound.verify()
    witness_tuple = _sorted_unique(witness_ids)
    payload = {
        "version": "BoundedReachabilityWitness.v1",
        "regime_id": str(regime_id),
        "contract_id": str(contract_id),
        "resource_bound": resource_bound.unsigned(),
        "status": ReachabilityStatus(status).value,
        "witness_ids": list(witness_tuple),
        "evaluator_id": str(evaluator_id),
        "protected": bool(protected),
        "grants_scientific_authority": False,
    }
    witness = ReachabilityWitness(
        regime_id=payload["regime_id"],
        contract_id=payload["contract_id"],
        resource_bound=resource_bound,
        status=ReachabilityStatus(payload["status"]),
        witness_ids=witness_tuple,
        evaluator_id=payload["evaluator_id"],
        protected=payload["protected"],
        digest=content_digest(payload),
    )
    witness.verify()
    return witness


@dataclass(frozen=True)
class ReachabilityDeltaReport:
    contract_id: str
    old_regime_id: str
    new_regime_id: str
    old_witness_digest: str
    new_witness_digest: str
    status: ReachabilityDeltaStatus
    reasons: tuple[str, ...]
    digest: str

    @property
    def grants_atom_necessity(self) -> bool:
        return False

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "BoundedReachabilityDelta.v1",
            "contract_id": self.contract_id,
            "old_regime_id": self.old_regime_id,
            "new_regime_id": self.new_regime_id,
            "old_witness_digest": self.old_witness_digest,
            "new_witness_digest": self.new_witness_digest,
            "status": self.status.value,
            "reasons": list(self.reasons),
            "grants_atom_necessity": False,
        }

    def verify(self) -> None:
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("reachability delta digest mismatch")


def compare_reachability(
    old: ReachabilityWitness,
    new: ReachabilityWitness,
) -> ReachabilityDeltaReport:
    old.verify()
    new.verify()
    if old.contract_id != new.contract_id:
        raise ValueError("reachability comparison is contract-relative")
    if old.resource_bound.digest != new.resource_bound.digest:
        raise ValueError("reachability comparison requires the same resource bound")

    reasons: list[str] = []
    if old.status is ReachabilityStatus.UNREACHABLE and new.status is ReachabilityStatus.REACHABLE:
        status = ReachabilityDeltaStatus.OLD_UNREACHABLE_NEW_REACHABLE
        reasons.append("EXTERNAL_OLD_UNREACHABILITY_AND_NEW_CONSTRUCTION_WITNESSES_RECORDED")
    elif old.status is ReachabilityStatus.UNRESOLVED and new.status is ReachabilityStatus.REACHABLE:
        status = ReachabilityDeltaStatus.OLD_UNRESOLVED_NEW_REACHABLE
        reasons.append("OLD_STATUS_UNRESOLVED_NOT_AN_OLD_REGIME_IMPOSSIBILITY_PROOF")
    elif new.status is ReachabilityStatus.UNRESOLVED or old.status is ReachabilityStatus.UNRESOLVED:
        status = ReachabilityDeltaStatus.UNRESOLVED
        reasons.append("AT_LEAST_ONE_REACHABILITY_SIDE_IS_UNRESOLVED")
    elif old.status is ReachabilityStatus.REACHABLE and new.status is ReachabilityStatus.UNREACHABLE:
        status = ReachabilityDeltaStatus.REGRESSION
        reasons.append("NEW_REGIME_LOSES_A_PREVIOUSLY_REACHABLE_CONTRACT_UNDER_THE_BOUND")
    else:
        status = ReachabilityDeltaStatus.NO_REACHABILITY_EXPANSION
        reasons.append("NO_NEW_REACHABLE_CONTRACT_ESTABLISHED_BY_THE_PAIRED_WITNESSES")

    payload = {
        "version": "BoundedReachabilityDelta.v1",
        "contract_id": old.contract_id,
        "old_regime_id": old.regime_id,
        "new_regime_id": new.regime_id,
        "old_witness_digest": old.digest,
        "new_witness_digest": new.digest,
        "status": status.value,
        "reasons": sorted(set(reasons)),
        "grants_atom_necessity": False,
    }
    report = ReachabilityDeltaReport(
        contract_id=old.contract_id,
        old_regime_id=old.regime_id,
        new_regime_id=new.regime_id,
        old_witness_digest=old.digest,
        new_witness_digest=new.digest,
        status=status,
        reasons=tuple(payload["reasons"]),
        digest=content_digest(payload),
    )
    report.verify()
    return report


@dataclass(frozen=True)
class BoundedEpistemicAtomStudy:
    atom_id: str
    parent_atom_ids: tuple[str, ...]
    structure_version: str
    target_contract_ids: tuple[str, ...]
    resource_bound: ResourceBound
    positive_case_ids: tuple[str, ...]
    no_atom_control_ids: tuple[str, ...]
    parent_baseline_ids: tuple[str, ...]
    ablation_or_replacement_ids: tuple[str, ...]
    decomposition_hypotheses: tuple[str, ...]
    interaction_hypotheses: tuple[str, ...]
    recursion_stop_rules: tuple[str, ...]
    evaluator_id: str
    authority_owner_id: str
    protected_field_ids: tuple[str, ...]
    outcome_accessed: bool
    digest: str

    @property
    def grants_scientific_authority(self) -> bool:
        return False

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "BoundedEpistemicAtomStudy.v1",
            "atom_id": self.atom_id,
            "parent_atom_ids": list(self.parent_atom_ids),
            "structure_version": self.structure_version,
            "target_contract_ids": list(self.target_contract_ids),
            "resource_bound": self.resource_bound.unsigned(),
            "positive_case_ids": list(self.positive_case_ids),
            "no_atom_control_ids": list(self.no_atom_control_ids),
            "parent_baseline_ids": list(self.parent_baseline_ids),
            "ablation_or_replacement_ids": list(self.ablation_or_replacement_ids),
            "decomposition_hypotheses": list(self.decomposition_hypotheses),
            "interaction_hypotheses": list(self.interaction_hypotheses),
            "recursion_stop_rules": list(self.recursion_stop_rules),
            "evaluator_id": self.evaluator_id,
            "authority_owner_id": self.authority_owner_id,
            "protected_field_ids": list(self.protected_field_ids),
            "outcome_accessed": self.outcome_accessed,
            "grants_scientific_authority": False,
        }

    def verify(self) -> None:
        self.resource_bound.verify()
        if not self.atom_id or not self.structure_version:
            raise ValueError("atom and structure identities are required")
        if any(not atom_id for atom_id in self.parent_atom_ids):
            raise ValueError("parent decomposition path identities must be non-empty")
        if len(self.parent_atom_ids) != len(set(self.parent_atom_ids)):
            raise ValueError("parent decomposition path cannot repeat an atom identity")
        if not self.target_contract_ids:
            raise ValueError("atom study requires at least one target contract")
        if not self.positive_case_ids or not self.no_atom_control_ids:
            raise ValueError("atom study requires positive and no-atom control cases")
        if set(self.positive_case_ids) & set(self.no_atom_control_ids):
            raise ValueError("positive and no-atom control case sets overlap")
        if not self.parent_baseline_ids:
            raise ValueError("atom study requires at least one parent/baseline")
        if not self.evaluator_id or not self.authority_owner_id:
            raise ValueError("evaluator and authority owner identities are required")
        if self.outcome_accessed:
            raise ValueError("atom study protocol cannot be constructed after outcome access")
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("atom study digest mismatch")


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
        "parent_atom_ids": list(_ordered(parent_atom_ids)),
        "structure_version": str(structure_version),
        "target_contract_ids": list(_sorted_unique(target_contract_ids)),
        "resource_bound": resource_bound.unsigned(),
        "positive_case_ids": list(_sorted_unique(positive_case_ids)),
        "no_atom_control_ids": list(_sorted_unique(no_atom_control_ids)),
        "parent_baseline_ids": list(_sorted_unique(parent_baseline_ids)),
        "ablation_or_replacement_ids": list(_sorted_unique(ablation_or_replacement_ids)),
        "decomposition_hypotheses": list(_sorted_unique(decomposition_hypotheses)),
        "interaction_hypotheses": list(_sorted_unique(interaction_hypotheses)),
        "recursion_stop_rules": list(_sorted_unique(recursion_stop_rules)),
        "evaluator_id": str(evaluator_id),
        "authority_owner_id": str(authority_owner_id),
        "protected_field_ids": list(_sorted_unique(protected_field_ids)),
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


@dataclass(frozen=True)
class ContractInteractionReport:
    left_atom_id: str
    right_atom_id: str
    left_only_contract_ids: tuple[str, ...]
    right_only_contract_ids: tuple[str, ...]
    shared_individual_contract_ids: tuple[str, ...]
    synergy_contract_ids: tuple[str, ...]
    lost_in_combination_contract_ids: tuple[str, ...]
    digest: str

    @property
    def grants_atom_independence_claim(self) -> bool:
        return False

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "BoundedAtomInteractionReport.v1",
            "left_atom_id": self.left_atom_id,
            "right_atom_id": self.right_atom_id,
            "left_only_contract_ids": list(self.left_only_contract_ids),
            "right_only_contract_ids": list(self.right_only_contract_ids),
            "shared_individual_contract_ids": list(self.shared_individual_contract_ids),
            "synergy_contract_ids": list(self.synergy_contract_ids),
            "lost_in_combination_contract_ids": list(self.lost_in_combination_contract_ids),
            "grants_atom_independence_claim": False,
        }

    def verify(self) -> None:
        if not self.left_atom_id or not self.right_atom_id:
            raise ValueError("interaction atom identities are required")
        if self.left_atom_id == self.right_atom_id:
            raise ValueError("interaction requires two distinct atom identities")
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("atom interaction digest mismatch")


def analyze_contract_interaction(
    *,
    left_atom_id: str,
    right_atom_id: str,
    left_reachable_contract_ids: Sequence[str],
    right_reachable_contract_ids: Sequence[str],
    combined_reachable_contract_ids: Sequence[str],
) -> ContractInteractionReport:
    left = set(_sorted_unique(left_reachable_contract_ids))
    right = set(_sorted_unique(right_reachable_contract_ids))
    combined = set(_sorted_unique(combined_reachable_contract_ids))
    union = left | right
    payload = {
        "version": "BoundedAtomInteractionReport.v1",
        "left_atom_id": str(left_atom_id),
        "right_atom_id": str(right_atom_id),
        "left_only_contract_ids": sorted(left - right),
        "right_only_contract_ids": sorted(right - left),
        "shared_individual_contract_ids": sorted(left & right),
        "synergy_contract_ids": sorted(combined - union),
        "lost_in_combination_contract_ids": sorted(union - combined),
        "grants_atom_independence_claim": False,
    }
    report = ContractInteractionReport(
        left_atom_id=payload["left_atom_id"],
        right_atom_id=payload["right_atom_id"],
        left_only_contract_ids=tuple(payload["left_only_contract_ids"]),
        right_only_contract_ids=tuple(payload["right_only_contract_ids"]),
        shared_individual_contract_ids=tuple(payload["shared_individual_contract_ids"]),
        synergy_contract_ids=tuple(payload["synergy_contract_ids"]),
        lost_in_combination_contract_ids=tuple(payload["lost_in_combination_contract_ids"]),
        digest=content_digest(payload),
    )
    report.verify()
    return report


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
