"""Finite decomposition checker for Jump pilot atoms #510/#511/#512.

The checker is deliberately negative/non-authorizing.  It does not generate an
epistemic opportunity, thought experiment, or concept.  It checks pre-frozen
finite countermodels showing that the three broad proposal labels contain
independently load-bearing evidence/operator/transformation families at the
registered resolution.

A green report supports host-side decomposition dispositions only.  It grants
no scientific, novelty, adoption, merge, or issue-closure authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from orion.transfer.v2.canonical import content_digest


class J1Recommendation(str, Enum):
    MULTIPLE_TENSION_ATOMS_REQUIRED = "MULTIPLE_TENSION_ATOMS_REQUIRED"
    CANNOT_CHECK = "CANNOT_CHECK"


class J2Recommendation(str, Enum):
    MULTIPLE_IMAGINATION_ATOMS_REQUIRED = "MULTIPLE_IMAGINATION_ATOMS_REQUIRED"
    CANNOT_CHECK = "CANNOT_CHECK"


class J3Recommendation(str, Enum):
    MULTIPLE_CONCEPT_ATOMS_REQUIRED = "MULTIPLE_CONCEPT_ATOMS_REQUIRED"
    CANNOT_CHECK = "CANNOT_CHECK"


class OpportunityMateriality(str, Enum):
    MATERIAL_OPPORTUNITY = "MATERIAL_OPPORTUNITY"
    NO_MATERIAL_OPPORTUNITY = "NO_MATERIAL_OPPORTUNITY"


@dataclass(frozen=True)
class J1OpportunityPair:
    pair_id: str
    public_observable_ids: tuple[str, ...]
    material_world: OpportunityMateriality
    control_world: OpportunityMateriality
    separating_witness_family: str

    def verify(self) -> None:
        if not self.pair_id or not self.public_observable_ids:
            raise ValueError("J1 pair requires identity and public observations")
        if any(not item for item in self.public_observable_ids):
            raise ValueError("J1 public observation identities must be non-empty")
        if self.material_world is self.control_world:
            raise ValueError("J1 pair must differ in protected opportunity materiality")
        if not self.separating_witness_family:
            raise ValueError("J1 pair requires a separating structural witness family")


_J1_PAIRS: tuple[J1OpportunityPair, ...] = (
    J1OpportunityPair(
        pair_id="unification-deficit-vs-legitimate-specialization",
        public_observable_ids=(
            "ZERO_PREDICTION_ERROR",
            "LOCAL_CONTRACTS_SATISFIED",
            "LOW_UNCERTAINTY",
        ),
        material_world=OpportunityMateriality.MATERIAL_OPPORTUNITY,
        control_world=OpportunityMateriality.NO_MATERIAL_OPPORTUNITY,
        separating_witness_family="CROSS_CONTEXT_UNIFICATION_OR_BRIDGE_EVIDENCE",
    ),
    J1OpportunityPair(
        pair_id="stable-invariant-vs-symmetry-looking-coincidence",
        public_observable_ids=(
            "ZERO_PREDICTION_ERROR",
            "LOCAL_CONTRACTS_SATISFIED",
            "TRANSFORMATION_PATTERN_VISIBLE",
        ),
        material_world=OpportunityMateriality.MATERIAL_OPPORTUNITY,
        control_world=OpportunityMateriality.NO_MATERIAL_OPPORTUNITY,
        separating_witness_family="INVARIANCE_UNDER_REGISTERED_TRANSFORMATIONS",
    ),
    J1OpportunityPair(
        pair_id="structural-analogy-vs-surface-analogy",
        public_observable_ids=(
            "ZERO_PREDICTION_ERROR",
            "LOCAL_CONTRACTS_SATISFIED",
            "CROSS_DOMAIN_SIMILARITY_PRESENT",
        ),
        material_world=OpportunityMateriality.MATERIAL_OPPORTUNITY,
        control_world=OpportunityMateriality.NO_MATERIAL_OPPORTUNITY,
        separating_witness_family="VERIFIED_RELATIONAL_CORRESPONDENCE",
    ),
    J1OpportunityPair(
        pair_id="new-affordance-vs-novelty-without-function",
        public_observable_ids=(
            "CURRENT_OBJECTIVE_SATISFIED",
            "ARTIFACT_UNUSUAL_FEATURE_PRESENT",
            "NO_CURRENT_FAILURE",
        ),
        material_world=OpportunityMateriality.MATERIAL_OPPORTUNITY,
        control_world=OpportunityMateriality.NO_MATERIAL_OPPORTUNITY,
        separating_witness_family="EXECUTABLE_FUNCTION_OR_AFFORDANCE_WITNESS",
    ),
)


class J2Operation(str, Enum):
    DIRECT_INTERVENTION = "DIRECT_INTERVENTION"
    ASSUMPTION_RELAXATION = "ASSUMPTION_RELAXATION"
    FRAME_TRANSFORMATION = "FRAME_TRANSFORMATION"
    SYSTEM_COUPLING = "SYSTEM_COUPLING"
    FORMAL_COUNTEREXAMPLE = "FORMAL_COUNTEREXAMPLE"


@dataclass(frozen=True)
class J2OperationCase:
    case_id: str
    contract_id: str
    required_operations: tuple[J2Operation, ...]
    special_thought_operation: bool
    parent_family: str

    def verify(self) -> None:
        if not self.case_id or not self.contract_id or not self.parent_family:
            raise ValueError("J2 operation case identities are required")
        if not self.required_operations:
            raise ValueError("J2 operation case requires at least one operation")
        if len(self.required_operations) != len(set(self.required_operations)):
            raise ValueError("J2 operation requirements must be unique")
        if self.special_thought_operation:
            if self.required_operations == (J2Operation.DIRECT_INTERVENTION,):
                raise ValueError("ordinary intervention is a no-special-operation control")


_J2_CASES: tuple[J2OperationCase, ...] = (
    J2OperationCase(
        case_id="ordinary-intervention-sufficient-control",
        contract_id="identify-by-cheapest-physical-intervention",
        required_operations=(J2Operation.DIRECT_INTERVENTION,),
        special_thought_operation=False,
        parent_family="BAYESIAN_OR_ACTIVE_EXPERIMENT_DESIGN",
    ),
    J2OperationCase(
        case_id="assumption-relaxation-unique",
        contract_id="identify-which-incumbent-postulate-causes-conflict",
        required_operations=(J2Operation.ASSUMPTION_RELAXATION,),
        special_thought_operation=True,
        parent_family="COUNTERFACTUAL_ASSUMPTION_RELAXATION",
    ),
    J2OperationCase(
        case_id="frame-transformation-unique",
        contract_id="expose-frame-dependent-vs-invariant-structure",
        required_operations=(J2Operation.FRAME_TRANSFORMATION,),
        special_thought_operation=True,
        parent_family="REPRESENTATION_OR_OBSERVER_TRANSFORMATION",
    ),
    J2OperationCase(
        case_id="system-coupling-unique",
        contract_id="separate-local-theories-by-coupled-behavior",
        required_operations=(J2Operation.SYSTEM_COUPLING,),
        special_thought_operation=True,
        parent_family="SYSTEM_COMPOSITION_OR_CROSS_DOMAIN_COUPLING",
    ),
    J2OperationCase(
        case_id="formal-counterexample-unique",
        contract_id="separate-conjectures-by-constructed-countermodel",
        required_operations=(J2Operation.FORMAL_COUNTEREXAMPLE,),
        special_thought_operation=True,
        parent_family="COUNTEREXAMPLE_GUIDED_OR_FORMAL_SEARCH",
    ),
)


class J3Transformation(str, Enum):
    INTRODUCE_LATENT_OBJECT = "INTRODUCE_LATENT_OBJECT"
    SPLIT_CONTEXTUAL_VARIABLE = "SPLIT_CONTEXTUAL_VARIABLE"
    QUOTIENT_IDENTIFY_STATES = "QUOTIENT_IDENTIFY_STATES"
    LIFT_RELATIONAL_REPRESENTATION = "LIFT_RELATIONAL_REPRESENTATION"
    BRIDGE_CORRESPONDENCE = "BRIDGE_CORRESPONDENCE"


@dataclass(frozen=True)
class J3TransformationCase:
    case_id: str
    contract_id: str
    required_transformations: tuple[J3Transformation, ...]
    parent_family: str
    preservation_obligation_id: str

    def verify(self) -> None:
        if (
            not self.case_id
            or not self.contract_id
            or not self.parent_family
            or not self.preservation_obligation_id
        ):
            raise ValueError("J3 transformation case identities are required")
        if not self.required_transformations:
            raise ValueError("J3 case requires at least one transformation")
        if len(self.required_transformations) != len(set(self.required_transformations)):
            raise ValueError("J3 transformation requirements must be unique")


_J3_CASES: tuple[J3TransformationCase, ...] = (
    J3TransformationCase(
        case_id="latent-object-introduction",
        contract_id="intervention-transfer-through-hidden-mechanism",
        required_transformations=(J3Transformation.INTRODUCE_LATENT_OBJECT,),
        parent_family="BACON_GLAUBER_LATENT_OR_THEORETICAL_TERM_DISCOVERY",
        preservation_obligation_id="PRESERVE_OBSERVED_LOCAL_LAWS",
    ),
    J3TransformationCase(
        case_id="contextual-split",
        contract_id="resolve-context-dependent-local-law-conflict",
        required_transformations=(J3Transformation.SPLIT_CONTEXTUAL_VARIABLE,),
        parent_family="REPRESENTATION_OR_CAUSAL_REFACTORIZATION",
        preservation_obligation_id="PRESERVE_VALID_LOCAL_SUBDOMAIN_RESULTS",
    ),
    J3TransformationCase(
        case_id="quotient-identification",
        contract_id="derive-hidden-invariant-under-resource-bound",
        required_transformations=(J3Transformation.QUOTIENT_IDENTIFY_STATES,),
        parent_family="ABSTRACTION_EQUIVALENCE_OR_QUOTIENT_REPRESENTATION",
        preservation_obligation_id="PRESERVE_OBSERVABLE_EQUIVALENCE_CLASSES",
    ),
    J3TransformationCase(
        case_id="relational-lift",
        contract_id="make-nonlocal-mechanism-locally-derivable",
        required_transformations=(J3Transformation.LIFT_RELATIONAL_REPRESENTATION,),
        parent_family="REPRESENTATION_LEARNING_OR_STRUCTURAL_ABSTRACTION",
        preservation_obligation_id="PRESERVE_OLD_REGIME_PREDICTIONS",
    ),
    J3TransformationCase(
        case_id="bridge-correspondence",
        contract_id="transfer-between-two-exact-local-theories",
        required_transformations=(J3Transformation.BRIDGE_CORRESPONDENCE,),
        parent_family="ANALOGY_IDENTITY_ABDUCTION_OR_CK_COMPOSITION",
        preservation_obligation_id="PRESERVE_BOTH_LOCAL_THEORY_CONTRACTS",
    ),
)


def j1_opportunity_pairs() -> tuple[J1OpportunityPair, ...]:
    return _J1_PAIRS


def j2_operation_cases() -> tuple[J2OperationCase, ...]:
    return _J2_CASES


def j3_transformation_cases() -> tuple[J3TransformationCase, ...]:
    return _J3_CASES


def reachable_j2_contracts(enabled: Sequence[J2Operation]) -> tuple[str, ...]:
    enabled_set = set(enabled)
    reachable = [
        case.contract_id
        for case in _J2_CASES
        if set(case.required_operations) <= enabled_set
    ]
    return tuple(sorted(reachable))


def reachable_j3_contracts(enabled: Sequence[J3Transformation]) -> tuple[str, ...]:
    enabled_set = set(enabled)
    reachable = [
        case.contract_id
        for case in _J3_CASES
        if set(case.required_transformations) <= enabled_set
    ]
    return tuple(sorted(reachable))


@dataclass(frozen=True)
class JumpAtomPilotClosureReport:
    j1_pair_count: int
    j1_all_pairs_split_materiality: bool
    j1_distinct_witness_family_count: int
    j1_public_only_universal_signal_possible: bool
    j1_recommendation: J1Recommendation
    j2_operation_case_count: int
    j2_special_operator_case_count: int
    j2_independently_load_bearing_operations: tuple[str, ...]
    j2_ordinary_intervention_control_preserved: bool
    j2_recommendation: J2Recommendation
    j3_transformation_case_count: int
    j3_independently_load_bearing_transformations: tuple[str, ...]
    j3_distinct_parent_family_count: int
    j3_recommendation: J3Recommendation
    all_checks_passed: bool
    digest: str

    @property
    def grants_scientific_authority(self) -> bool:
        return False

    @property
    def grants_novelty_authority(self) -> bool:
        return False

    @property
    def grants_adoption_authority(self) -> bool:
        return False

    @property
    def grants_issue_closure_authority(self) -> bool:
        return False

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "JumpAtomPilotClosureReport.v1",
            "j1_pair_count": self.j1_pair_count,
            "j1_all_pairs_split_materiality": self.j1_all_pairs_split_materiality,
            "j1_distinct_witness_family_count": self.j1_distinct_witness_family_count,
            "j1_public_only_universal_signal_possible": self.j1_public_only_universal_signal_possible,
            "j1_recommendation": self.j1_recommendation.value,
            "j2_operation_case_count": self.j2_operation_case_count,
            "j2_special_operator_case_count": self.j2_special_operator_case_count,
            "j2_independently_load_bearing_operations": list(
                self.j2_independently_load_bearing_operations
            ),
            "j2_ordinary_intervention_control_preserved": self.j2_ordinary_intervention_control_preserved,
            "j2_recommendation": self.j2_recommendation.value,
            "j3_transformation_case_count": self.j3_transformation_case_count,
            "j3_independently_load_bearing_transformations": list(
                self.j3_independently_load_bearing_transformations
            ),
            "j3_distinct_parent_family_count": self.j3_distinct_parent_family_count,
            "j3_recommendation": self.j3_recommendation.value,
            "all_checks_passed": self.all_checks_passed,
            "grants_scientific_authority": False,
            "grants_novelty_authority": False,
            "grants_adoption_authority": False,
            "grants_issue_closure_authority": False,
        }

    def verify(self) -> None:
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("jump atom pilot closure digest mismatch")


def _assess_j1() -> tuple[bool, int, bool, J1Recommendation]:
    for pair in _J1_PAIRS:
        pair.verify()
    split = all(pair.material_world is not pair.control_world for pair in _J1_PAIRS)
    witness_count = len({pair.separating_witness_family for pair in _J1_PAIRS})

    # The public observation tuple is, by construction, the complete public
    # input on both members of each matched pair.  Because the protected target
    # differs, a deterministic public-only signal must return the same value for
    # both members and therefore fails at least one member of every split pair.
    public_only_possible = not split
    recommendation = (
        J1Recommendation.MULTIPLE_TENSION_ATOMS_REQUIRED
        if split and witness_count == len(_J1_PAIRS) and not public_only_possible
        else J1Recommendation.CANNOT_CHECK
    )
    return split, witness_count, public_only_possible, recommendation


def _independent_j2_operations() -> tuple[str, ...]:
    all_operations = tuple(J2Operation)
    all_reach = set(reachable_j2_contracts(all_operations))
    independent: list[str] = []
    for operation in all_operations:
        without = tuple(item for item in all_operations if item is not operation)
        lost = all_reach - set(reachable_j2_contracts(without))
        if lost:
            independent.append(operation.value)
    return tuple(sorted(independent))


def _assess_j2() -> tuple[tuple[str, ...], bool, J2Recommendation]:
    for case in _J2_CASES:
        case.verify()
    independent = _independent_j2_operations()
    ordinary = next(
        case for case in _J2_CASES if case.case_id == "ordinary-intervention-sufficient-control"
    )
    ordinary_control = (
        ordinary.special_thought_operation is False
        and ordinary.required_operations == (J2Operation.DIRECT_INTERVENTION,)
    )
    special_operations = {
        operation.value
        for case in _J2_CASES
        if case.special_thought_operation
        for operation in case.required_operations
    }
    independently_special = special_operations <= set(independent)
    recommendation = (
        J2Recommendation.MULTIPLE_IMAGINATION_ATOMS_REQUIRED
        if ordinary_control and independently_special and len(special_operations) >= 2
        else J2Recommendation.CANNOT_CHECK
    )
    return independent, ordinary_control, recommendation


def _independent_j3_transformations() -> tuple[str, ...]:
    all_transformations = tuple(J3Transformation)
    all_reach = set(reachable_j3_contracts(all_transformations))
    independent: list[str] = []
    for transformation in all_transformations:
        without = tuple(item for item in all_transformations if item is not transformation)
        lost = all_reach - set(reachable_j3_contracts(without))
        if lost:
            independent.append(transformation.value)
    return tuple(sorted(independent))


def _assess_j3() -> tuple[tuple[str, ...], int, J3Recommendation]:
    for case in _J3_CASES:
        case.verify()
    independent = _independent_j3_transformations()
    parent_count = len({case.parent_family for case in _J3_CASES})
    recommendation = (
        J3Recommendation.MULTIPLE_CONCEPT_ATOMS_REQUIRED
        if len(independent) == len(tuple(J3Transformation)) and parent_count >= 3
        else J3Recommendation.CANNOT_CHECK
    )
    return independent, parent_count, recommendation


def build_jump_atom_pilot_closure_report() -> JumpAtomPilotClosureReport:
    j1_split, j1_witness_count, j1_public_only, j1_recommendation = _assess_j1()
    j2_independent, j2_control, j2_recommendation = _assess_j2()
    j3_independent, j3_parent_count, j3_recommendation = _assess_j3()
    special_count = sum(case.special_thought_operation for case in _J2_CASES)

    all_checks_passed = (
        len(_J1_PAIRS) == 4
        and j1_split
        and j1_witness_count == 4
        and not j1_public_only
        and j1_recommendation is J1Recommendation.MULTIPLE_TENSION_ATOMS_REQUIRED
        and len(_J2_CASES) == 5
        and special_count == 4
        and j2_control
        and len(j2_independent) == 5
        and j2_recommendation is J2Recommendation.MULTIPLE_IMAGINATION_ATOMS_REQUIRED
        and len(_J3_CASES) == 5
        and len(j3_independent) == 5
        and j3_parent_count == 5
        and j3_recommendation is J3Recommendation.MULTIPLE_CONCEPT_ATOMS_REQUIRED
    )

    payload = {
        "version": "JumpAtomPilotClosureReport.v1",
        "j1_pair_count": len(_J1_PAIRS),
        "j1_all_pairs_split_materiality": j1_split,
        "j1_distinct_witness_family_count": j1_witness_count,
        "j1_public_only_universal_signal_possible": j1_public_only,
        "j1_recommendation": j1_recommendation.value,
        "j2_operation_case_count": len(_J2_CASES),
        "j2_special_operator_case_count": special_count,
        "j2_independently_load_bearing_operations": list(j2_independent),
        "j2_ordinary_intervention_control_preserved": j2_control,
        "j2_recommendation": j2_recommendation.value,
        "j3_transformation_case_count": len(_J3_CASES),
        "j3_independently_load_bearing_transformations": list(j3_independent),
        "j3_distinct_parent_family_count": j3_parent_count,
        "j3_recommendation": j3_recommendation.value,
        "all_checks_passed": all_checks_passed,
        "grants_scientific_authority": False,
        "grants_novelty_authority": False,
        "grants_adoption_authority": False,
        "grants_issue_closure_authority": False,
    }
    report = JumpAtomPilotClosureReport(
        j1_pair_count=payload["j1_pair_count"],
        j1_all_pairs_split_materiality=payload["j1_all_pairs_split_materiality"],
        j1_distinct_witness_family_count=payload["j1_distinct_witness_family_count"],
        j1_public_only_universal_signal_possible=payload[
            "j1_public_only_universal_signal_possible"
        ],
        j1_recommendation=J1Recommendation(payload["j1_recommendation"]),
        j2_operation_case_count=payload["j2_operation_case_count"],
        j2_special_operator_case_count=payload["j2_special_operator_case_count"],
        j2_independently_load_bearing_operations=tuple(
            payload["j2_independently_load_bearing_operations"]
        ),
        j2_ordinary_intervention_control_preserved=payload[
            "j2_ordinary_intervention_control_preserved"
        ],
        j2_recommendation=J2Recommendation(payload["j2_recommendation"]),
        j3_transformation_case_count=payload["j3_transformation_case_count"],
        j3_independently_load_bearing_transformations=tuple(
            payload["j3_independently_load_bearing_transformations"]
        ),
        j3_distinct_parent_family_count=payload["j3_distinct_parent_family_count"],
        j3_recommendation=J3Recommendation(payload["j3_recommendation"]),
        all_checks_passed=payload["all_checks_passed"],
        digest=content_digest(payload),
    )
    report.verify()
    return report


__all__ = [
    "J1OpportunityPair",
    "J1Recommendation",
    "J2Operation",
    "J2OperationCase",
    "J2Recommendation",
    "J3Recommendation",
    "J3Transformation",
    "J3TransformationCase",
    "JumpAtomPilotClosureReport",
    "OpportunityMateriality",
    "build_jump_atom_pilot_closure_report",
    "j1_opportunity_pairs",
    "j2_operation_cases",
    "j3_transformation_cases",
    "reachable_j2_contracts",
    "reachable_j3_contracts",
]
