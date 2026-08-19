"""Finite scientific-closure checker for the P6 successor (#463).

The checker deliberately separates two questions:

1. Do the already-merged T1--T7 component contracts satisfy their registered
   non-authorizing/minimality invariants on a bounded finite family?
2. After primary-source parent attribution, does #463 still require a new
   universal mathematical primitive?

A green report is not scientific, novelty, adoption, paper-promotion, or merge
authority.  It is evidence for the host-side #463 terminal only.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from itertools import combinations, product
from typing import Sequence

from orion.self_orion.epistemic_control import (
    EpistemicControlStatus,
    compose_epistemic_control,
)
from orion.self_orion.revision_gate import RevisionGateStatus, assess_revision_gate

from .canonical import content_digest
from .epistemic_computation import (
    ComputationSelectionStatus,
    assess_computation_action,
    build_computation_action,
    select_epistemic_computation,
)
from .epistemic_responsibility import (
    ResponsibilityStatus,
    assess_responsibility,
    build_responsibility_hypothesis,
)
from .higher_order_epistemic_mechanics import (
    AssessmentStatus,
    SelectionStatus,
    assess_mechanic,
    build_mechanic,
    less_or_equal_invasiveness,
    select_minimal_admissible,
    strictly_less_invasive,
)
from .interface_adequacy import (
    InterfaceAdequacyStatus,
    InterfaceCheckState,
    assess_interface_adequacy,
    build_interface_check,
)
from .social_evidence import (
    SocialEvidenceIndependenceStatus,
    TruthfulnessState,
    assess_social_evidence_independence,
    build_social_evidence_record,
)
from .uncertainty_containment import (
    ContainmentStatus,
    ValidityState,
    assess_containment,
    build_validity_envelope,
)


class FormalClosureRecommendation(str, Enum):
    FORMAL_COMPONENTS_ONLY_NO_UNIFIED_CALCULUS = (
        "FORMAL_COMPONENTS_ONLY_NO_UNIFIED_CALCULUS"
    )
    INTERNAL_INVARIANT_DEFECT = "INTERNAL_INVARIANT_DEFECT"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class FormalParentDisposition:
    component_id: str
    parent_source_ids: tuple[str, ...]
    disposition: str
    new_unified_primitive_required: bool

    def unsigned(self) -> dict[str, object]:
        return {
            "component_id": self.component_id,
            "parent_source_ids": list(self.parent_source_ids),
            "disposition": self.disposition,
            "new_unified_primitive_required": self.new_unified_primitive_required,
        }


_PARENT_DISPOSITIONS: tuple[FormalParentDisposition, ...] = (
    FormalParentDisposition(
        component_id="RESPONSIBILITY_AND_MINIMAL_DIAGNOSIS",
        parent_source_ids=(
            "doi:10.1016/0004-3702(87)90062-2",
            "doi:10.1016/0004-3702(87)90063-4",
            "arxiv:2309.16180",
        ),
        disposition="ADOPT_MODEL_BASED_DIAGNOSIS_AND_PREFERRED_HYPOTHESES",
        new_unified_primitive_required=False,
    ),
    FormalParentDisposition(
        component_id="MINIMAL_AND_ITERATED_BELIEF_CHANGE",
        parent_source_ids=(
            "doi:10.2307/2274239",
            "doi:10.1016/0004-3702(91)90069-V",
            "doi:10.1016/S0004-3702(96)00038-0",
            "arxiv:2112.13557",
        ),
        disposition="ADOPT_AGM_MINIMAL_CHANGE_AND_EPISTEMIC_STATE_REVISION",
        new_unified_primitive_required=False,
    ),
    FormalParentDisposition(
        component_id="INTERFACE_INFORMATION_SUFFICIENCY",
        parent_source_ids=(
            "doi:10.1214/aoms/1177729032",
            "Li-Walsh-Littman:AI&M-2006-state-abstraction",
        ),
        disposition="ADOPT_BLACKWELL_AND_STATE_ABSTRACTION_SUFFICIENCY",
        new_unified_primitive_required=False,
    ),
    FormalParentDisposition(
        component_id="EPISTEMIC_COMPUTATION_ALLOCATION",
        parent_source_ids=(
            "Horvitz:UAI-1987-resource-constraints",
            "doi:10.1016/0004-3702(91)90015-C",
            "arxiv:1207.5879",
        ),
        disposition="ADOPT_RATIONAL_METAREASONING_VALUE_OF_COMPUTATION",
        new_unified_primitive_required=False,
    ),
    FormalParentDisposition(
        component_id="UNCERTAINTY_CONTAINMENT",
        parent_source_ids=("Aubin:Viability-Theory", "arxiv:1609.06408"),
        disposition="ADOPT_SAFE_SET_VIABILITY_AND_INVARIANCE",
        new_unified_primitive_required=False,
    ),
    FormalParentDisposition(
        component_id="SOCIAL_EVIDENCE_DEPENDENCE",
        parent_source_ids=(
            "doi:10.1214/aos/1176343654",
            "doi:10.1287/mnsc.33.3.373",
        ),
        disposition="ADOPT_DEPENDENT_INFORMATION_AND_EPISTEMIC_LOGIC",
        new_unified_primitive_required=False,
    ),
    FormalParentDisposition(
        component_id="MINIMAL_REPAIR_PERSISTENCE",
        parent_source_ids=("doi:10.1145/303976.303983",),
        disposition="ADOPT_MINIMAL_REPAIR_AND_PERSISTENT_INFORMATION",
        new_unified_primitive_required=False,
    ),
    FormalParentDisposition(
        component_id="SCIENTIFIC_AUTHORITY_AND_PRESERVATION_BOUNDARY",
        parent_source_ids=("ORION:P6-V2.1", "ORION:P8-V2.1"),
        disposition="KEEP_ORION_TYPED_NONCOMPENSATORY_INTERFACE",
        new_unified_primitive_required=False,
    ),
)


def formal_parent_dispositions() -> tuple[FormalParentDisposition, ...]:
    return _PARENT_DISPOSITIONS


def _powerset(values: Sequence[str]) -> tuple[tuple[str, ...], ...]:
    items = tuple(values)
    return tuple(
        tuple(combo)
        for size in range(len(items) + 1)
        for combo in combinations(items, size)
    )


@dataclass(frozen=True)
class FiniteFormalClosureReport:
    generated_revision_signatures: int
    preorder_reflexive_cases: int
    preorder_transitivity_checks: int
    strict_minimality_checks: int
    narrower_unresolved_blocks_broader: bool
    incomparable_minima_remain_plural: bool
    authority_noncompensatory: bool
    hard_computation_obligation_precedence: bool
    local_compute_stop_is_not_global_stop: bool
    containment_never_promotes_truth: bool
    shared_provenance_not_independent: bool
    incomplete_social_provenance_unresolved: bool
    composed_controller_non_authorizing: bool
    all_checks_passed: bool
    digest: str

    @property
    def grants_scientific_authority(self) -> bool:
        return False

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "HigherOrderFormalFiniteClosure.v1",
            "generated_revision_signatures": self.generated_revision_signatures,
            "preorder_reflexive_cases": self.preorder_reflexive_cases,
            "preorder_transitivity_checks": self.preorder_transitivity_checks,
            "strict_minimality_checks": self.strict_minimality_checks,
            "narrower_unresolved_blocks_broader": self.narrower_unresolved_blocks_broader,
            "incomparable_minima_remain_plural": self.incomparable_minima_remain_plural,
            "authority_noncompensatory": self.authority_noncompensatory,
            "hard_computation_obligation_precedence": self.hard_computation_obligation_precedence,
            "local_compute_stop_is_not_global_stop": self.local_compute_stop_is_not_global_stop,
            "containment_never_promotes_truth": self.containment_never_promotes_truth,
            "shared_provenance_not_independent": self.shared_provenance_not_independent,
            "incomplete_social_provenance_unresolved": self.incomplete_social_provenance_unresolved,
            "composed_controller_non_authorizing": self.composed_controller_non_authorizing,
            "all_checks_passed": self.all_checks_passed,
            "grants_scientific_authority": False,
        }

    def verify(self) -> None:
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("finite formal closure digest mismatch")


@dataclass(frozen=True)
class FormalClosureReport:
    parent_component_count: int
    parent_coverage_complete: bool
    unresolved_parent_components: tuple[str, ...]
    new_unified_primitive_count: int
    finite_checker_green: bool
    recommendation: FormalClosureRecommendation
    design_dispositions: tuple[str, ...]
    parent_disposition_digests: tuple[str, ...]
    finite_checker_digest: str
    digest: str

    @property
    def grants_scientific_authority(self) -> bool:
        return False

    @property
    def grants_novelty_authority(self) -> bool:
        return False

    @property
    def grants_paper_promotion_authority(self) -> bool:
        return False

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "HigherOrderFormalClosureReport.v1",
            "parent_component_count": self.parent_component_count,
            "parent_coverage_complete": self.parent_coverage_complete,
            "unresolved_parent_components": list(self.unresolved_parent_components),
            "new_unified_primitive_count": self.new_unified_primitive_count,
            "finite_checker_green": self.finite_checker_green,
            "recommendation": self.recommendation.value,
            "design_dispositions": list(self.design_dispositions),
            "parent_disposition_digests": list(self.parent_disposition_digests),
            "finite_checker_digest": self.finite_checker_digest,
            "grants_scientific_authority": False,
            "grants_novelty_authority": False,
            "grants_paper_promotion_authority": False,
        }

    def verify(self) -> None:
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("formal closure report digest mismatch")


def _build_revision_signatures() -> tuple[object, ...]:
    write_sets = _powerset(("EVIDENCE", "MODEL", "REPRESENTATION"))
    preservation_sets = ((), ("PRESERVE:BASE",))
    authority_sets = ((), ("AUTH:MODEL",))
    mechanics = []
    for index, (writes, preserves, authorities) in enumerate(
        product(write_sets, preservation_sets, authority_sets)
    ):
        mechanics.append(
            build_mechanic(
                mechanic_id=f"finite-mechanic-{index}",
                claim_id="finite-claim",
                write_coordinates=writes,
                preservation_obligations=preserves,
                required_authorities=authorities,
                cost=float(index % 3),
            )
        )
    return tuple(mechanics)


def _check_preorder_and_minimality(mechanics: Sequence[object]) -> tuple[int, int, int]:
    assessments = {
        mechanic.digest: assess_mechanic(
            mechanic,
            obligation_states={},
            granted_authorities=("AUTH:MODEL",),
        )
        for mechanic in mechanics
    }
    if any(item.status is not AssessmentStatus.ADMISSIBLE for item in assessments.values()):
        raise AssertionError("generated finite signature unexpectedly inadmissible")

    reflexive = 0
    for mechanic in mechanics:
        if not less_or_equal_invasiveness(mechanic, mechanic):
            raise AssertionError("invasiveness relation is not reflexive")
        reflexive += 1

    transitivity = 0
    for left in mechanics:
        for middle in mechanics:
            if not less_or_equal_invasiveness(left, middle):
                continue
            for right in mechanics:
                if less_or_equal_invasiveness(middle, right):
                    transitivity += 1
                    if not less_or_equal_invasiveness(left, right):
                        raise AssertionError("invasiveness relation is not transitive")

    strict = 0
    for narrow in mechanics:
        for broad in mechanics:
            if not strictly_less_invasive(narrow, broad):
                continue
            strict += 1
            selection = select_minimal_admissible(
                (narrow, broad),
                (assessments[narrow.digest], assessments[broad.digest]),
            )
            if (
                selection.status is not SelectionStatus.UNIQUE_MINIMUM
                or selection.selected_mechanic_digest != narrow.digest
            ):
                raise AssertionError(
                    "strictly narrower admissible revision lost to broader one"
                )
    return reflexive, transitivity, strict


def _check_revision_edge_cases() -> tuple[bool, bool, bool]:
    narrow_unresolved = build_mechanic(
        mechanic_id="narrow-unresolved",
        claim_id="unresolved-claim",
        write_coordinates=("EVIDENCE",),
        hard_requirements=("DISC",),
    )
    broad = build_mechanic(
        mechanic_id="broad-admissible",
        claim_id="unresolved-claim",
        write_coordinates=("EVIDENCE", "MODEL"),
    )
    # Omission of the registered hard-requirement state is itself fail-closed
    # UNRESOLVED; no string/enum coercion is used by the closure checker.
    narrow_assessment = assess_mechanic(narrow_unresolved, obligation_states={})
    broad_assessment = assess_mechanic(broad, obligation_states={})
    unresolved_selection = select_minimal_admissible(
        (narrow_unresolved, broad), (narrow_assessment, broad_assessment)
    )
    narrower_unresolved_blocks_broader = (
        narrow_assessment.status is AssessmentStatus.UNRESOLVED
        and broad_assessment.status is AssessmentStatus.ADMISSIBLE
        and unresolved_selection.status is SelectionStatus.UNRESOLVED
        and "NARROWER_UNRESOLVED_CANDIDATE" in unresolved_selection.reasons
    )

    left = build_mechanic(
        mechanic_id="left-incomparable",
        claim_id="plural-claim",
        write_coordinates=("MODEL",),
    )
    right = build_mechanic(
        mechanic_id="right-incomparable",
        claim_id="plural-claim",
        write_coordinates=("REPRESENTATION",),
    )
    plural_selection = select_minimal_admissible(
        (left, right),
        (
            assess_mechanic(left, obligation_states={}),
            assess_mechanic(right, obligation_states={}),
        ),
    )
    incomparable_minima_remain_plural = (
        plural_selection.status is SelectionStatus.MULTIPLE_MINIMA
        and len(plural_selection.minimal_mechanic_digests) == 2
    )

    authority_results = []
    for cost in (0.0, 1000.0):
        candidate = build_mechanic(
            mechanic_id=f"authority-cost-{int(cost)}",
            claim_id="authority-claim",
            write_coordinates=("MODEL",),
            required_authorities=("AUTH:PROTECTED",),
            cost=cost,
        )
        authority_results.append(
            assess_mechanic(candidate, obligation_states={}, granted_authorities=())
        )
    authority_noncompensatory = all(
        item.status is AssessmentStatus.BLOCKED
        and "AUTHORITY_MISSING:AUTH:PROTECTED" in item.reasons
        for item in authority_results
    )
    return (
        narrower_unresolved_blocks_broader,
        incomparable_minima_remain_plural,
        authority_noncompensatory,
    )


def _check_computation() -> tuple[bool, bool]:
    mandatory = build_computation_action(
        action_id="mandatory-verify",
        claim_id="compute-claim",
        kind="VERIFY",
        expected_decision_value=-10.0,
        cost=0.0,
        discharges_obligations=("VERIFY",),
    )
    tempting = build_computation_action(
        action_id="tempting-optional",
        claim_id="compute-claim",
        kind="THINK_MORE",
        expected_decision_value=100.0,
        cost=0.0,
    )
    selection = select_epistemic_computation(
        (mandatory, tempting),
        (
            assess_computation_action(mandatory, requirement_states={}),
            assess_computation_action(tempting, requirement_states={}),
        ),
        active_hard_obligations=("VERIFY",),
    )
    hard_precedence = (
        selection.status is ComputationSelectionStatus.SELECTED
        and selection.selected_action_id == mandatory.action_id
        and "HARD_OBLIGATION_PRECEDENCE" in selection.reasons
    )

    stop_a = build_computation_action(
        action_id="stop-a",
        claim_id="stop-claim",
        kind="OPTIONAL",
        expected_decision_value=0.0,
        cost=0.0,
    )
    stop_b = build_computation_action(
        action_id="stop-b",
        claim_id="stop-claim",
        kind="OPTIONAL",
        expected_decision_value=1.0,
        cost=2.0,
    )
    stop = select_epistemic_computation(
        (stop_a, stop_b),
        (
            assess_computation_action(stop_a, requirement_states={}),
            assess_computation_action(stop_b, requirement_states={}),
        ),
    )
    return hard_precedence, stop.status is ComputationSelectionStatus.LOCAL_COMPUTATION_STOP


def _check_containment() -> bool:
    envelope = build_validity_envelope(
        envelope_id="finite-envelope",
        claim_id="containment-claim",
        subject_id="subject",
        context_states={
            "supported": ValidityState.SUPPORTED,
            "invalid": ValidityState.INVALID,
            "unresolved": ValidityState.UNRESOLVED,
        },
        evidence_ids=("evidence",),
    )
    reports = tuple(
        assess_containment(envelope, context_id=context)
        for context in ("supported", "invalid", "unresolved", "unknown")
    )
    return (
        tuple(item.status for item in reports)
        == (
            ContainmentStatus.IN_SCOPE,
            ContainmentStatus.BLOCKED,
            ContainmentStatus.UNRESOLVED,
            ContainmentStatus.UNRESOLVED,
        )
        and all(not item.establishes_model_correctness for item in reports)
        and all(not item.grants_scientific_authority for item in reports)
        and all(not item.rewrites_model for item in reports)
    )


def _check_social_evidence() -> tuple[bool, bool]:
    shared = assess_social_evidence_independence(
        (
            build_social_evidence_record(
                report_id="shared-1",
                agent_id="agent-1",
                claim_id="social-claim",
                direct_observation_ids=("obs-1",),
                upstream_source_ids=("common-source",),
                truthfulness_state=TruthfulnessState.SATISFIED,
            ),
            build_social_evidence_record(
                report_id="shared-2",
                agent_id="agent-2",
                claim_id="social-claim",
                direct_observation_ids=("obs-2",),
                upstream_source_ids=("common-source",),
                truthfulness_state=TruthfulnessState.SATISFIED,
            ),
        )
    )
    shared_not_independent = (
        shared.status is SocialEvidenceIndependenceStatus.CORRELATED
        and "common-source" in shared.shared_upstream_source_ids
    )

    incomplete = assess_social_evidence_independence(
        (
            build_social_evidence_record(
                report_id="incomplete-1",
                agent_id="agent-1",
                claim_id="social-incomplete",
                direct_observation_ids=("obs-1",),
                upstream_source_ids=(),
                truthfulness_state=TruthfulnessState.SATISFIED,
            ),
            build_social_evidence_record(
                report_id="incomplete-2",
                agent_id="agent-2",
                claim_id="social-incomplete",
                direct_observation_ids=("obs-2",),
                upstream_source_ids=("source-2",),
                truthfulness_state=TruthfulnessState.SATISFIED,
            ),
        )
    )
    incomplete_unresolved = (
        incomplete.status is SocialEvidenceIndependenceStatus.UNRESOLVED
        and "PROVENANCE_BASIS_INCOMPLETE" in incomplete.reasons
    )
    return shared_not_independent, incomplete_unresolved


def _identified_revision_gate(claim_id: str):
    h1 = build_responsibility_hypothesis(
        hypothesis_id="h1",
        claim_id=claim_id,
        expected_observations={"disc": ("YES",)},
    )
    h2 = build_responsibility_hypothesis(
        hypothesis_id="h2",
        claim_id=claim_id,
        expected_observations={"disc": ("NO",)},
    )
    responsibility = assess_responsibility(
        (h1, h2), observed_outcomes={"disc": "YES"}
    )
    if responsibility.status is not ResponsibilityStatus.IDENTIFIED:
        raise AssertionError("finite controller responsibility not identified")
    interface = assess_interface_adequacy(
        (
            build_interface_check(
                check_id="interface-pass",
                scope="OBSERVATION",
                state=InterfaceCheckState.PASS,
                evidence_ids=("interface-evidence",),
                required=True,
            ),
        )
    )
    if interface.status is not InterfaceAdequacyStatus.ADEQUATE:
        raise AssertionError("finite controller interface not adequate")
    mechanic = build_mechanic(
        mechanic_id="bounded-revision",
        claim_id=claim_id,
        write_coordinates=("MODEL",),
    )
    gate = assess_revision_gate(
        responsibility=responsibility,
        interface=interface,
        mechanics=(mechanic,),
        assessments=(assess_mechanic(mechanic, obligation_states={}),),
        responsibility_bindings={"h1": (mechanic.mechanic_id,)},
    )
    if gate.status is not RevisionGateStatus.CANDIDATE_SELECTED:
        raise AssertionError("finite controller revision not selected")
    return gate


def _check_control_composition(local_stop_available: bool) -> tuple[bool, bool]:
    claim_id = "control-claim"
    gate = _identified_revision_gate(claim_id)
    optional = build_computation_action(
        action_id="control-local-stop",
        claim_id=claim_id,
        kind="OPTIONAL",
        expected_decision_value=0.0,
        cost=0.0,
    )
    computation = select_epistemic_computation(
        (optional,),
        (assess_computation_action(optional, requirement_states={}),),
    )
    if local_stop_available and computation.status is not ComputationSelectionStatus.LOCAL_COMPUTATION_STOP:
        raise AssertionError("control local computation stop unavailable")
    envelope = build_validity_envelope(
        envelope_id="control-envelope",
        claim_id=claim_id,
        subject_id="subject",
        context_states={"current": ValidityState.SUPPORTED},
        evidence_ids=("containment-evidence",),
    )
    containment = assess_containment(envelope, context_id="current")
    social = assess_social_evidence_independence(
        (
            build_social_evidence_record(
                report_id="independent-1",
                agent_id="agent-a",
                claim_id=claim_id,
                direct_observation_ids=("obs-a",),
                upstream_source_ids=("source-a",),
                truthfulness_state=TruthfulnessState.SATISFIED,
            ),
            build_social_evidence_record(
                report_id="independent-2",
                agent_id="agent-b",
                claim_id=claim_id,
                direct_observation_ids=("obs-b",),
                upstream_source_ids=("source-b",),
                truthfulness_state=TruthfulnessState.SATISFIED,
            ),
        )
    )
    control = compose_epistemic_control(
        revision=gate,
        computation=computation,
        containment=containment,
        social_evidence=(social,),
        require_independent_social_evidence=True,
    )
    controller_non_authorizing = (
        control.status is EpistemicControlStatus.REVISION_CANDIDATE
        and not control.grants_scientific_authority
        and not control.grants_revision_authority
        and not control.grants_adoption_authority
        and not control.grants_promotion_authority
        and not control.grants_merge_authority
        and not control.grants_global_task_stop_authority
    )

    ambiguous_claim = "ambiguous-control"
    ambiguous_responsibility = assess_responsibility(
        (
            build_responsibility_hypothesis(
                hypothesis_id="ambiguous-1",
                claim_id=ambiguous_claim,
                expected_observations={"disc": ("YES",)},
            ),
            build_responsibility_hypothesis(
                hypothesis_id="ambiguous-2",
                claim_id=ambiguous_claim,
                expected_observations={"disc": ("YES",)},
            ),
        ),
        observed_outcomes={"disc": "YES"},
    )
    ambiguous_interface = assess_interface_adequacy(
        (
            build_interface_check(
                check_id="ambiguous-interface",
                scope="OBSERVATION",
                state=InterfaceCheckState.PASS,
                required=True,
            ),
        )
    )
    ambiguous_mechanic = build_mechanic(
        mechanic_id="ambiguous-mechanic",
        claim_id=ambiguous_claim,
        write_coordinates=("MODEL",),
    )
    ambiguous_gate = assess_revision_gate(
        responsibility=ambiguous_responsibility,
        interface=ambiguous_interface,
        mechanics=(ambiguous_mechanic,),
        assessments=(assess_mechanic(ambiguous_mechanic, obligation_states={}),),
        responsibility_bindings={},
    )
    ambiguous_optional = build_computation_action(
        action_id="ambiguous-stop",
        claim_id=ambiguous_claim,
        kind="OPTIONAL",
        expected_decision_value=0.0,
        cost=0.0,
    )
    ambiguous_compute = select_epistemic_computation(
        (ambiguous_optional,),
        (assess_computation_action(ambiguous_optional, requirement_states={}),),
    )
    local_control = compose_epistemic_control(
        revision=ambiguous_gate,
        computation=ambiguous_compute,
    )
    local_stop_not_global = (
        ambiguous_gate.status is RevisionGateStatus.UNRESOLVED
        and ambiguous_compute.status is ComputationSelectionStatus.LOCAL_COMPUTATION_STOP
        and local_control.status is EpistemicControlStatus.LOCAL_COMPUTATION_STOP
        and not local_control.grants_global_task_stop_authority
        and "GLOBAL_TASK_REMAINS_OPEN" in local_control.reasons
    )
    return controller_non_authorizing, local_stop_not_global


def run_finite_formal_closure_checks() -> FiniteFormalClosureReport:
    mechanics = _build_revision_signatures()
    reflexive, transitivity, strict = _check_preorder_and_minimality(mechanics)
    (
        narrower_unresolved,
        incomparable_minima,
        authority_noncompensatory,
    ) = _check_revision_edge_cases()
    hard_compute, local_stop_available = _check_computation()
    containment = _check_containment()
    shared_social, incomplete_social = _check_social_evidence()
    controller_non_authorizing, local_stop_not_global = _check_control_composition(
        local_stop_available
    )

    booleans = (
        narrower_unresolved,
        incomparable_minima,
        authority_noncompensatory,
        hard_compute,
        local_stop_available,
        local_stop_not_global,
        containment,
        shared_social,
        incomplete_social,
        controller_non_authorizing,
    )
    all_checks_passed = (
        all(booleans)
        and reflexive == len(mechanics)
        and transitivity > 0
        and strict > 0
    )
    payload = {
        "version": "HigherOrderFormalFiniteClosure.v1",
        "generated_revision_signatures": len(mechanics),
        "preorder_reflexive_cases": reflexive,
        "preorder_transitivity_checks": transitivity,
        "strict_minimality_checks": strict,
        "narrower_unresolved_blocks_broader": narrower_unresolved,
        "incomparable_minima_remain_plural": incomparable_minima,
        "authority_noncompensatory": authority_noncompensatory,
        "hard_computation_obligation_precedence": hard_compute,
        "local_compute_stop_is_not_global_stop": local_stop_not_global,
        "containment_never_promotes_truth": containment,
        "shared_provenance_not_independent": shared_social,
        "incomplete_social_provenance_unresolved": incomplete_social,
        "composed_controller_non_authorizing": controller_non_authorizing,
        "all_checks_passed": all_checks_passed,
        "grants_scientific_authority": False,
    }
    report = FiniteFormalClosureReport(
        generated_revision_signatures=len(mechanics),
        preorder_reflexive_cases=reflexive,
        preorder_transitivity_checks=transitivity,
        strict_minimality_checks=strict,
        narrower_unresolved_blocks_broader=narrower_unresolved,
        incomparable_minima_remain_plural=incomparable_minima,
        authority_noncompensatory=authority_noncompensatory,
        hard_computation_obligation_precedence=hard_compute,
        local_compute_stop_is_not_global_stop=local_stop_not_global,
        containment_never_promotes_truth=containment,
        shared_provenance_not_independent=shared_social,
        incomplete_social_provenance_unresolved=incomplete_social,
        composed_controller_non_authorizing=controller_non_authorizing,
        all_checks_passed=all_checks_passed,
        digest=content_digest(payload),
    )
    report.verify()
    return report


def build_formal_closure_report() -> FormalClosureReport:
    parents = formal_parent_dispositions()
    finite = run_finite_formal_closure_checks()
    unresolved = tuple(
        sorted(
            item.component_id
            for item in parents
            if not item.parent_source_ids or item.disposition.startswith("DEFER")
        )
    )
    new_primitives = sum(
        int(item.new_unified_primitive_required) for item in parents
    )
    parent_coverage_complete = not unresolved
    if not finite.all_checks_passed:
        recommendation = FormalClosureRecommendation.INTERNAL_INVARIANT_DEFECT
    elif not parent_coverage_complete:
        recommendation = FormalClosureRecommendation.CANNOT_CHECK
    elif new_primitives == 0:
        recommendation = (
            FormalClosureRecommendation.FORMAL_COMPONENTS_ONLY_NO_UNIFIED_CALCULUS
        )
    else:
        recommendation = FormalClosureRecommendation.CANNOT_CHECK

    dispositions = (
        "KEEP_TYPED_COMPONENT_INTERFACES",
        "KEEP_NON_AUTHORIZING_COMPOSITION",
        "STRIKE_UNIFIED_CALCULUS_NOVELTY",
        "JUMP_REMAINS_SEPARATE_FOLLOWUP",
    )
    parent_digests = tuple(
        sorted(content_digest(item.unsigned()) for item in parents)
    )
    payload = {
        "version": "HigherOrderFormalClosureReport.v1",
        "parent_component_count": len(parents),
        "parent_coverage_complete": parent_coverage_complete,
        "unresolved_parent_components": list(unresolved),
        "new_unified_primitive_count": new_primitives,
        "finite_checker_green": finite.all_checks_passed,
        "recommendation": recommendation.value,
        "design_dispositions": list(dispositions),
        "parent_disposition_digests": list(parent_digests),
        "finite_checker_digest": finite.digest,
        "grants_scientific_authority": False,
        "grants_novelty_authority": False,
        "grants_paper_promotion_authority": False,
    }
    report = FormalClosureReport(
        parent_component_count=len(parents),
        parent_coverage_complete=parent_coverage_complete,
        unresolved_parent_components=unresolved,
        new_unified_primitive_count=new_primitives,
        finite_checker_green=finite.all_checks_passed,
        recommendation=recommendation,
        design_dispositions=dispositions,
        parent_disposition_digests=parent_digests,
        finite_checker_digest=finite.digest,
        digest=content_digest(payload),
    )
    report.verify()
    return report


__all__ = [
    "FiniteFormalClosureReport",
    "FormalClosureRecommendation",
    "FormalClosureReport",
    "FormalParentDisposition",
    "build_formal_closure_report",
    "formal_parent_dispositions",
    "run_finite_formal_closure_checks",
]
