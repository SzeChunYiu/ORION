"""Finite, non-authorizing closure checker for failure atoms #516/#517/#518.

This module does not implement a runtime failure detector, automatic scientific
refutation, or a semantic transport engine.  It makes three bounded negative /
subsumption arguments executable:

* F1: matched worlds can be identical on every registered public observation
  while differing in protected material-validity semantics.  A detector that
  sees only the public observation cannot classify both correctly.
* F2: the fields of ``FailureKnowledge.v1`` have structural owners in
  TMS/ATMS/nogood reasoning plus existing ORION responsibility/provenance/
  authority interfaces at the registered resolution.
* F3: semantic staleness is an instance of support/evidence/obligation
  transport.  Identity/complete transport can preserve a negative conclusion;
  verified semantic change reopens it; incomplete target-ambiguous transport
  stays unresolved.

A green report is evidence for host-side issue disposition only.  It grants no
scientific, novelty, adoption, merge, or issue-closure authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from orion.transfer.v2.canonical import content_digest


class F1Recommendation(str, Enum):
    MULTIPLE_FAILURE_SIGNAL_ATOMS_REQUIRED = "MULTIPLE_FAILURE_SIGNAL_ATOMS_REQUIRED"
    CANNOT_CHECK = "CANNOT_CHECK"


class F2Recommendation(str, Enum):
    TMS_NOGOOD_PLUS_RESPONSIBILITY_SUFFICIENT = (
        "TMS_NOGOOD_PLUS_RESPONSIBILITY_SUFFICIENT"
    )
    CANNOT_CHECK = "CANNOT_CHECK"


class F3Recommendation(str, Enum):
    P7_TRANSPORT_SUFFICIENT = "P7_TRANSPORT_SUFFICIENT"
    CANNOT_CHECK = "CANNOT_CHECK"


class ProtectedMateriality(str, Enum):
    VALID = "VALID"
    MATERIAL_FAILURE = "MATERIAL_FAILURE"


class TransportWitnessKind(str, Enum):
    IDENTITY = "IDENTITY"
    COMPLETE = "COMPLETE"
    VERIFIED_SEMANTIC_CHANGE = "VERIFIED_SEMANTIC_CHANGE"
    INCOMPLETE_TARGET_AMBIGUOUS = "INCOMPLETE_TARGET_AMBIGUOUS"


class NegativeApplicability(str, Enum):
    APPLIES = "APPLIES"
    REOPENED = "REOPENED"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class F1IndistinguishabilityPair:
    pair_id: str
    public_observable_ids: tuple[str, ...]
    world_a_materiality: ProtectedMateriality
    world_b_materiality: ProtectedMateriality
    specialized_discriminator_id: str

    def verify(self) -> None:
        if not self.pair_id or not self.public_observable_ids:
            raise ValueError("F1 pair requires an identity and public observations")
        if any(not item for item in self.public_observable_ids):
            raise ValueError("F1 public observation identities must be non-empty")
        if self.world_a_materiality is self.world_b_materiality:
            raise ValueError("F1 indistinguishability pair must split protected materiality")
        if not self.specialized_discriminator_id:
            raise ValueError("F1 pair requires the extra evidence source that can distinguish it")


_F1_PAIRS: tuple[F1IndistinguishabilityPair, ...] = (
    F1IndistinguishabilityPair(
        pair_id="physical-invariant-hidden-from-public-trace",
        public_observable_ids=(
            "RUN_COMPLETED",
            "NUMERIC_OUTPUT_PLAUSIBLE",
            "NO_EXCEPTION",
            "LOCAL_RESIDUAL_WITHIN_PUBLIC_TOLERANCE",
        ),
        world_a_materiality=ProtectedMateriality.VALID,
        world_b_materiality=ProtectedMateriality.MATERIAL_FAILURE,
        specialized_discriminator_id="NATIVE_PHYSICAL_INVARIANT_CHECK",
    ),
    F1IndistinguishabilityPair(
        pair_id="custody-integrity-hidden-from-score",
        public_observable_ids=(
            "RUN_COMPLETED",
            "EVALUATOR_SCORE_HIGH",
            "NO_EXCEPTION",
            "ARTIFACT_PRESENT",
        ),
        world_a_materiality=ProtectedMateriality.VALID,
        world_b_materiality=ProtectedMateriality.MATERIAL_FAILURE,
        specialized_discriminator_id="PROTECTED_CUSTODY_PROTOCOL_AUDIT",
    ),
    F1IndistinguishabilityPair(
        pair_id="proof-validity-hidden-from-plausible-text",
        public_observable_ids=(
            "DERIVATION_TEXT_COMPLETE",
            "LOCAL_STEPS_PLAUSIBLE",
            "NO_EXCEPTION",
            "FINAL_CLAIM_FORMAT_VALID",
        ),
        world_a_materiality=ProtectedMateriality.VALID,
        world_b_materiality=ProtectedMateriality.MATERIAL_FAILURE,
        specialized_discriminator_id="NATIVE_PROOF_VERIFIER",
    ),
    F1IndistinguishabilityPair(
        pair_id="cross-step-composition-hidden-from-local-checks",
        public_observable_ids=(
            "ALL_LOCAL_STEPS_ACCEPTED",
            "FINAL_ARTIFACT_PRESENT",
            "NO_EXCEPTION",
            "LOCAL_CONFIDENCE_HIGH",
        ),
        world_a_materiality=ProtectedMateriality.VALID,
        world_b_materiality=ProtectedMateriality.MATERIAL_FAILURE,
        specialized_discriminator_id="CROSS_STEP_SEMANTIC_CONSISTENCY_CHECK",
    ),
)


@dataclass(frozen=True)
class F2ParentMapping:
    field_name: str
    structural_owner: str
    parent_capability: str
    new_orion_primitive_required: bool = False

    def verify(self) -> None:
        if not self.field_name or not self.structural_owner or not self.parent_capability:
            raise ValueError("F2 parent mapping rows must be fully identified")


_F2_REQUIRED_FIELDS: tuple[str, ...] = (
    "failure_id",
    "target_contract_id",
    "regime_id",
    "attempted_trace_ids",
    "observed_failure_id",
    "responsibility_state_id",
    "excluded_condition_ids",
    "still_live_alternative_ids",
    "preserved_success_ids",
    "frozen_context",
    "required_same_coordinates",
    "reopen_on_change_coordinates",
    "evidence_ids",
    "authority_owner_id",
)


_F2_PARENT_MAPPINGS: tuple[F2ParentMapping, ...] = (
    F2ParentMapping(
        field_name="failure_id",
        structural_owner="EPISODE_PROVENANCE",
        parent_capability="IDENTITY_OF_THE_FAILED_EPISODE",
    ),
    F2ParentMapping(
        field_name="target_contract_id",
        structural_owner="ORION_TYPED_CONTRACT_INTERFACE",
        parent_capability="CLAIM_OR_CONTRACT_RELATIVE_SCOPE",
    ),
    F2ParentMapping(
        field_name="regime_id",
        structural_owner="ATMS_CONTEXT_PLUS_P7_CHART_IDENTITY",
        parent_capability="ENVIRONMENT_OR_REGIME_RELATIVE_REASONING",
    ),
    F2ParentMapping(
        field_name="attempted_trace_ids",
        structural_owner="EPISODE_PROVENANCE",
        parent_capability="ORDERED_ATTEMPT_LINEAGE",
    ),
    F2ParentMapping(
        field_name="observed_failure_id",
        structural_owner="EVIDENCE_PROVENANCE",
        parent_capability="IDENTITY_OF_THE_OBSERVED_FAILURE_EVIDENCE",
    ),
    F2ParentMapping(
        field_name="responsibility_state_id",
        structural_owner="P6_EPISTEMIC_RESPONSIBILITY",
        parent_capability="CLAIM_RELATIVE_RESPONSIBILITY_HYPOTHESIS_STATE",
    ),
    F2ParentMapping(
        field_name="excluded_condition_ids",
        structural_owner="TMS_ATMS_NOGOOD",
        parent_capability="CONTEXT_SCOPED_CONTRADICTION_OR_CONFLICT",
    ),
    F2ParentMapping(
        field_name="still_live_alternative_ids",
        structural_owner="ATMS_ALTERNATIVE_ENVIRONMENTS",
        parent_capability="NON_NOGOOD_ALTERNATIVES_REMAIN_AVAILABLE",
    ),
    F2ParentMapping(
        field_name="preserved_success_ids",
        structural_owner="TMS_JUSTIFICATION_GRAPH",
        parent_capability="UNAFFECTED_JUSTIFIED_NODES_REMAIN_SUPPORTED",
    ),
    F2ParentMapping(
        field_name="frozen_context",
        structural_owner="ATMS_ASSUMPTION_ENVIRONMENT",
        parent_capability="CONTEXT_BOUND_JUSTIFICATION_AND_CONFLICT_SCOPE",
    ),
    F2ParentMapping(
        field_name="required_same_coordinates",
        structural_owner="ATMS_CONTEXT_MATCHING",
        parent_capability="REUSE_ONLY_UNDER_REQUIRED_ASSUMPTION_ENVIRONMENT",
    ),
    F2ParentMapping(
        field_name="reopen_on_change_coordinates",
        structural_owner="P7_TRANSPORT_AND_REOPENING",
        parent_capability="REOPEN_WHEN_LOAD_BEARING_SEMANTICS_CHANGE",
    ),
    F2ParentMapping(
        field_name="evidence_ids",
        structural_owner="TMS_JUSTIFICATIONS_PLUS_ORION_PROVENANCE",
        parent_capability="REASON_AND_EVIDENCE_LINEAGE_FOR_THE_CONFLICT",
    ),
    F2ParentMapping(
        field_name="authority_owner_id",
        structural_owner="P4_P8_AUTHORITY",
        parent_capability="EXTERNAL_NON_COMPENSATORY_REFUTATION_AUTHORITY",
    ),
)


@dataclass(frozen=True)
class F3TransportCase:
    case_id: str
    surface_context_changed: bool
    witness_kind: TransportWitnessKind
    expected_applicability: NegativeApplicability

    def verify(self) -> None:
        if not self.case_id:
            raise ValueError("F3 transport case requires an identity")
        if not self.surface_context_changed and self.witness_kind is not TransportWitnessKind.IDENTITY:
            raise ValueError("unchanged F3 context must use identity transport")
        if self.surface_context_changed and self.witness_kind is TransportWitnessKind.IDENTITY:
            raise ValueError("changed F3 context cannot claim identity transport")


_F3_CASES: tuple[F3TransportCase, ...] = (
    F3TransportCase(
        case_id="identity-context-old-negative-still-applies",
        surface_context_changed=False,
        witness_kind=TransportWitnessKind.IDENTITY,
        expected_applicability=NegativeApplicability.APPLIES,
    ),
    F3TransportCase(
        case_id="semantic-preserving-rename-or-refactor",
        surface_context_changed=True,
        witness_kind=TransportWitnessKind.COMPLETE,
        expected_applicability=NegativeApplicability.APPLIES,
    ),
    F3TransportCase(
        case_id="measurement-or-evaluator-repaired",
        surface_context_changed=True,
        witness_kind=TransportWitnessKind.VERIFIED_SEMANTIC_CHANGE,
        expected_applicability=NegativeApplicability.REOPENED,
    ),
    F3TransportCase(
        case_id="objective-changed-old-failure-no-longer-same-contract",
        surface_context_changed=True,
        witness_kind=TransportWitnessKind.VERIFIED_SEMANTIC_CHANGE,
        expected_applicability=NegativeApplicability.REOPENED,
    ),
    F3TransportCase(
        case_id="domain-expanded-partial-mapping",
        surface_context_changed=True,
        witness_kind=TransportWitnessKind.INCOMPLETE_TARGET_AMBIGUOUS,
        expected_applicability=NegativeApplicability.UNRESOLVED,
    ),
    F3TransportCase(
        case_id="representation-mapping-missing",
        surface_context_changed=True,
        witness_kind=TransportWitnessKind.INCOMPLETE_TARGET_AMBIGUOUS,
        expected_applicability=NegativeApplicability.UNRESOLVED,
    ),
)


def f1_indistinguishability_pairs() -> tuple[F1IndistinguishabilityPair, ...]:
    return _F1_PAIRS


def f2_parent_mappings() -> tuple[F2ParentMapping, ...]:
    return _F2_PARENT_MAPPINGS


def f3_transport_cases() -> tuple[F3TransportCase, ...]:
    return _F3_CASES


def assess_f3_transport(case: F3TransportCase) -> NegativeApplicability:
    """Apply the frozen P7-style transport disposition to one negative lesson.

    ``COMPLETE`` means the load-bearing support/referent/satisfaction/defeater
    semantics have been transported, not merely that names or hashes match.
    ``INCOMPLETE_TARGET_AMBIGUOUS`` is fail-closed because two target worlds
    remain consistent with the established mapping facts but disagree about the
    old negative conclusion.
    """

    case.verify()
    if case.witness_kind in (TransportWitnessKind.IDENTITY, TransportWitnessKind.COMPLETE):
        return NegativeApplicability.APPLIES
    if case.witness_kind is TransportWitnessKind.VERIFIED_SEMANTIC_CHANGE:
        return NegativeApplicability.REOPENED
    if case.witness_kind is TransportWitnessKind.INCOMPLETE_TARGET_AMBIGUOUS:
        return NegativeApplicability.UNRESOLVED
    raise AssertionError("unhandled F3 transport witness")


@dataclass(frozen=True)
class FailureAtomPilotClosureReport:
    f1_pair_count: int
    f1_all_pairs_split_protected_materiality: bool
    f1_public_only_universal_detector_possible: bool
    f1_recommendation: F1Recommendation
    f2_parent_mapping_count: int
    f2_unmapped_fields: tuple[str, ...]
    f2_new_primitive_fields: tuple[str, ...]
    f2_recommendation: F2Recommendation
    f3_transport_case_count: int
    f3_mismatched_cases: tuple[str, ...]
    f3_semantic_transport_delegated_to_p7: bool
    f3_recommendation: F3Recommendation
    all_checks_passed: bool
    digest: str

    @property
    def grants_scientific_authority(self) -> bool:
        return False

    @property
    def grants_novelty_authority(self) -> bool:
        return False

    @property
    def grants_issue_closure_authority(self) -> bool:
        return False

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "FailureAtomPilotClosureReport.v1",
            "f1_pair_count": self.f1_pair_count,
            "f1_all_pairs_split_protected_materiality": self.f1_all_pairs_split_protected_materiality,
            "f1_public_only_universal_detector_possible": self.f1_public_only_universal_detector_possible,
            "f1_recommendation": self.f1_recommendation.value,
            "f2_parent_mapping_count": self.f2_parent_mapping_count,
            "f2_unmapped_fields": list(self.f2_unmapped_fields),
            "f2_new_primitive_fields": list(self.f2_new_primitive_fields),
            "f2_recommendation": self.f2_recommendation.value,
            "f3_transport_case_count": self.f3_transport_case_count,
            "f3_mismatched_cases": list(self.f3_mismatched_cases),
            "f3_semantic_transport_delegated_to_p7": self.f3_semantic_transport_delegated_to_p7,
            "f3_recommendation": self.f3_recommendation.value,
            "all_checks_passed": self.all_checks_passed,
            "grants_scientific_authority": False,
            "grants_novelty_authority": False,
            "grants_issue_closure_authority": False,
        }

    def verify(self) -> None:
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("failure atom pilot closure digest mismatch")


def _assess_f1(
    pairs: Sequence[F1IndistinguishabilityPair],
) -> tuple[bool, bool, F1Recommendation]:
    if not pairs:
        return False, True, F1Recommendation.CANNOT_CHECK
    split = True
    for pair in pairs:
        pair.verify()
        split = split and pair.world_a_materiality is not pair.world_b_materiality

    # For each pair, every registered public input to a public-only detector is
    # identical in the two worlds while the protected target differs.  Any
    # deterministic function of that input must emit the same output in both
    # worlds and therefore be wrong on at least one member of the pair.
    public_only_possible = not split
    recommendation = (
        F1Recommendation.MULTIPLE_FAILURE_SIGNAL_ATOMS_REQUIRED
        if split and not public_only_possible
        else F1Recommendation.CANNOT_CHECK
    )
    return split, public_only_possible, recommendation


def _assess_f2(
    mappings: Sequence[F2ParentMapping],
) -> tuple[tuple[str, ...], tuple[str, ...], F2Recommendation]:
    for row in mappings:
        row.verify()
    by_field = {row.field_name: row for row in mappings}
    if len(by_field) != len(tuple(mappings)):
        raise ValueError("duplicate F2 field mapping")

    unmapped = tuple(sorted(set(_F2_REQUIRED_FIELDS) - set(by_field)))
    extra = tuple(sorted(set(by_field) - set(_F2_REQUIRED_FIELDS)))
    if extra:
        raise ValueError("unexpected F2 field mapping: " + ",".join(extra))
    new_primitive = tuple(
        sorted(row.field_name for row in mappings if row.new_orion_primitive_required)
    )
    recommendation = (
        F2Recommendation.TMS_NOGOOD_PLUS_RESPONSIBILITY_SUFFICIENT
        if not unmapped and not new_primitive
        else F2Recommendation.CANNOT_CHECK
    )
    return unmapped, new_primitive, recommendation


def _assess_f3(
    cases: Sequence[F3TransportCase],
) -> tuple[tuple[str, ...], bool, F3Recommendation]:
    if not cases:
        return (), False, F3Recommendation.CANNOT_CHECK
    mismatched = []
    semantic_change_seen = False
    complete_nonidentity_seen = False
    ambiguous_seen = False
    for case in cases:
        case.verify()
        actual = assess_f3_transport(case)
        if actual is not case.expected_applicability:
            mismatched.append(case.case_id)
        semantic_change_seen = semantic_change_seen or (
            case.witness_kind is TransportWitnessKind.VERIFIED_SEMANTIC_CHANGE
        )
        complete_nonidentity_seen = complete_nonidentity_seen or (
            case.witness_kind is TransportWitnessKind.COMPLETE
        )
        ambiguous_seen = ambiguous_seen or (
            case.witness_kind is TransportWitnessKind.INCOMPLETE_TARGET_AMBIGUOUS
        )

    delegated = semantic_change_seen and complete_nonidentity_seen and ambiguous_seen
    recommendation = (
        F3Recommendation.P7_TRANSPORT_SUFFICIENT
        if not mismatched and delegated
        else F3Recommendation.CANNOT_CHECK
    )
    return tuple(sorted(mismatched)), delegated, recommendation


def build_failure_atom_pilot_closure_report() -> FailureAtomPilotClosureReport:
    f1_split, f1_public_only, f1_recommendation = _assess_f1(_F1_PAIRS)
    f2_unmapped, f2_new, f2_recommendation = _assess_f2(_F2_PARENT_MAPPINGS)
    f3_mismatched, f3_delegated, f3_recommendation = _assess_f3(_F3_CASES)

    all_checks_passed = (
        len(_F1_PAIRS) == 4
        and f1_split
        and not f1_public_only
        and f1_recommendation is F1Recommendation.MULTIPLE_FAILURE_SIGNAL_ATOMS_REQUIRED
        and len(_F2_PARENT_MAPPINGS) == 14
        and not f2_unmapped
        and not f2_new
        and f2_recommendation is F2Recommendation.TMS_NOGOOD_PLUS_RESPONSIBILITY_SUFFICIENT
        and len(_F3_CASES) == 6
        and not f3_mismatched
        and f3_delegated
        and f3_recommendation is F3Recommendation.P7_TRANSPORT_SUFFICIENT
    )

    payload = {
        "version": "FailureAtomPilotClosureReport.v1",
        "f1_pair_count": len(_F1_PAIRS),
        "f1_all_pairs_split_protected_materiality": f1_split,
        "f1_public_only_universal_detector_possible": f1_public_only,
        "f1_recommendation": f1_recommendation.value,
        "f2_parent_mapping_count": len(_F2_PARENT_MAPPINGS),
        "f2_unmapped_fields": list(f2_unmapped),
        "f2_new_primitive_fields": list(f2_new),
        "f2_recommendation": f2_recommendation.value,
        "f3_transport_case_count": len(_F3_CASES),
        "f3_mismatched_cases": list(f3_mismatched),
        "f3_semantic_transport_delegated_to_p7": f3_delegated,
        "f3_recommendation": f3_recommendation.value,
        "all_checks_passed": all_checks_passed,
        "grants_scientific_authority": False,
        "grants_novelty_authority": False,
        "grants_issue_closure_authority": False,
    }
    report = FailureAtomPilotClosureReport(
        f1_pair_count=payload["f1_pair_count"],
        f1_all_pairs_split_protected_materiality=payload[
            "f1_all_pairs_split_protected_materiality"
        ],
        f1_public_only_universal_detector_possible=payload[
            "f1_public_only_universal_detector_possible"
        ],
        f1_recommendation=F1Recommendation(payload["f1_recommendation"]),
        f2_parent_mapping_count=payload["f2_parent_mapping_count"],
        f2_unmapped_fields=tuple(payload["f2_unmapped_fields"]),
        f2_new_primitive_fields=tuple(payload["f2_new_primitive_fields"]),
        f2_recommendation=F2Recommendation(payload["f2_recommendation"]),
        f3_transport_case_count=payload["f3_transport_case_count"],
        f3_mismatched_cases=tuple(payload["f3_mismatched_cases"]),
        f3_semantic_transport_delegated_to_p7=payload[
            "f3_semantic_transport_delegated_to_p7"
        ],
        f3_recommendation=F3Recommendation(payload["f3_recommendation"]),
        all_checks_passed=payload["all_checks_passed"],
        digest=content_digest(payload),
    )
    report.verify()
    return report


__all__ = [
    "F1IndistinguishabilityPair",
    "F1Recommendation",
    "F2ParentMapping",
    "F2Recommendation",
    "F3Recommendation",
    "F3TransportCase",
    "FailureAtomPilotClosureReport",
    "NegativeApplicability",
    "ProtectedMateriality",
    "TransportWitnessKind",
    "assess_f3_transport",
    "build_failure_atom_pilot_closure_report",
    "f1_indistinguishability_pairs",
    "f2_parent_mappings",
    "f3_transport_cases",
]
