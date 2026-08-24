"""ScientificStructureAssimilationReceipt.v1 — absorb epistemology before mechanics (#454).

This is deliberately upstream of ``MechanismAssimilationReceipt.v1``. A donor
paper can change what counts as an object, explanation, anomaly, admissible
revision, inquiry, preservation rule, or scientific authority before any
algorithmic primitive is copied. Recording only the algorithm in that case is
not assimilation; it is loss of scientific structure.

A receipt is non-authorizing. ``ADMITTED`` means the donor's commitments and
ORION consequences were recorded without one of the fail-closed hostile modes;
it never means the donor is reproduced, a scientific claim is true, or ORION owns
novelty. Material structural donors must carry a receipt identity before their
mechanics can be admitted downstream under #318.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable

from orion.novelty.hashing import sha256_canonical

SCHEMA_ID = "orion.scientific-structure-assimilation-receipt.v1"


class StructuralCoordinate(str, Enum):
    A_SCIENTIFIC_ONTOLOGY = "A_SCIENTIFIC_ONTOLOGY"
    B_EXPLANATION_KNOWLEDGE = "B_EXPLANATION_KNOWLEDGE"
    C_FAILURE_ANOMALY = "C_FAILURE_ANOMALY"
    D_REVISION = "D_REVISION"
    E_INQUIRY_INTERVENTION = "E_INQUIRY_INTERVENTION"
    F_EVIDENCE_VERIFICATION_AUTHORITY = "F_EVIDENCE_VERIFICATION_AUTHORITY"
    G_ORION_RELATIONSHIP = "G_ORION_RELATIONSHIP"


REQUIRED_COORDINATES = tuple(StructuralCoordinate)


class StructuralDisposition(str, Enum):
    ADOPT_STRUCTURE = "ADOPT_STRUCTURE"
    ADAPT_STRUCTURE = "ADAPT_STRUCTURE"
    COMPOSE_STRUCTURES = "COMPOSE_STRUCTURES"
    CONFLICT = "CONFLICT"
    ORTHOGONAL = "ORTHOGONAL"
    DEFER_CANNOT_CHECK = "DEFER/CANNOT_CHECK"


class StructuralSourceKind(str, Enum):
    PRIMARY_PAPER = "PRIMARY_PAPER"
    OFFICIAL_CODE = "OFFICIAL_CODE"
    SECONDARY = "SECONDARY"


class StructuralSourceAccess(str, Enum):
    FULL_TEXT = "FULL_TEXT"
    ABSTRACT_ONLY = "ABSTRACT_ONLY"
    UNREACHABLE = "UNREACHABLE"


class StructuralAuthority(str, Enum):
    NONE = "NONE"
    DESCRIPTIVE = "DESCRIPTIVE"
    BOUNDED = "BOUNDED"
    GENERAL = "GENERAL"


_AUTHORITY_ORDER = tuple(StructuralAuthority)


def authority_rank(authority: StructuralAuthority | str) -> int:
    return _AUTHORITY_ORDER.index(StructuralAuthority(authority))


class StructuralHostileFindingKind(str, Enum):
    ALGORITHM_ONLY_ABSORPTION = "ALGORITHM_ONLY_ABSORPTION"
    PHILOSOPHY_LAUNDERING = "PHILOSOPHY_LAUNDERING"
    INCOMPATIBLE_BLEND = "INCOMPATIBLE_BLEND"
    AUTHORITY_ESCALATION = "AUTHORITY_ESCALATION"
    REPRESENTATION_ERASURE = "REPRESENTATION_ERASURE"
    PRESERVATION_ERASURE = "PRESERVATION_ERASURE"
    SCOPE_LAUNDERING = "SCOPE_LAUNDERING"
    LLM_MYSTIFICATION = "LLM_MYSTIFICATION"
    NEGATIVE_RESULT_DELETION = "NEGATIVE_RESULT_DELETION"
    CITATION_ONLY_RECEIPT = "CITATION_ONLY_RECEIPT"
    UNGROUNDED_SOURCE = "UNGROUNDED_SOURCE"
    MISSING_UPSTREAM_STRUCTURE = "MISSING_UPSTREAM_STRUCTURE"


class StructuralAssimilationVerdict(str, Enum):
    ADMITTED = "ADMITTED"
    BLOCKED = "BLOCKED"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class StructuralDonorIdentity:
    donor_id: str
    title: str
    source_uri: str
    source_kind: StructuralSourceKind
    access: StructuralSourceAccess
    source_scope: str

    def __post_init__(self) -> None:
        if not all(str(value).strip() for value in (self.donor_id, self.title, self.source_uri, self.source_scope)):
            raise ValueError("structural donor identity requires id/title/source/scope")
        object.__setattr__(self, "source_kind", StructuralSourceKind(self.source_kind))
        object.__setattr__(self, "access", StructuralSourceAccess(self.access))


@dataclass(frozen=True)
class StructuralAssumptionProfile:
    """Explicit schema-pressure assumptions from the #454/RLC harvest.

    These are intentionally first-class fields rather than prose embedded in A-G.
    An explicit ``NOT_MATERIAL: ...`` explanation is acceptable; an empty field is
    not. This prevents an algorithm summary from silently discarding a donor's
    agent/world, state, stochasticity, strategy, memory, computation, interface,
    or simple-baseline assumptions.
    """

    agent_world_coupling_assumption: str
    common_state_sufficiency_assumption: str
    exogenous_stochasticity_semantics: str
    strategic_link_required_followups: str
    working_memory_vs_audit_history: str
    computation_is_action_wait_semantics: str
    interface_components_joint_or_independent: str
    simple_baseline_that_could_make_donor_unnecessary: str

    def __post_init__(self) -> None:
        for name, value in self.__dict__.items():
            if not str(value).strip():
                raise ValueError(f"structural assumption profile field must be explicit: {name}")


@dataclass(frozen=True)
class CoordinateAssessment:
    coordinate: StructuralCoordinate
    commitment: str
    disposition: StructuralDisposition
    donor_owner_refs: tuple[str, ...]
    orion_consequence: str
    evidence_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "coordinate", StructuralCoordinate(self.coordinate))
        object.__setattr__(self, "disposition", StructuralDisposition(self.disposition))
        if not self.commitment.strip():
            raise ValueError("coordinate assessment requires a donor commitment")
        if not self.evidence_refs:
            raise ValueError("coordinate assessment requires source-grounding evidence refs")
        if not self.orion_consequence.strip():
            raise ValueError("coordinate assessment requires an ORION consequence or explicit NO_CHANGE rationale")


@dataclass(frozen=True)
class StructuralAssimilationDraft:
    receipt_id: str
    donor: StructuralDonorIdentity
    assessments: tuple[CoordinateAssessment, ...]
    assumption_profile: StructuralAssumptionProfile
    donor_authority: StructuralAuthority
    claimed_authority: StructuralAuthority
    material_structural_donor: bool = True
    representation_boundary: str = ""
    preservation_rule: str = ""
    claims_cross_domain_generalization: bool = False
    scope_extension_rationale: str = ""
    llm_involved: bool = False
    explicit_non_llm_machinery: tuple[str, ...] = ()
    llm_marginal_role_checked: bool = False
    donor_has_relevant_negative_result: bool = False
    negative_results: tuple[str, ...] = ()
    conflict_tests: tuple[str, ...] = ()
    downstream_children: tuple[str, ...] = ()
    explicit_no_change_reason: str = ""
    mechanism_receipt_ids: tuple[str, ...] = ()
    structural_receipt_id_for_mechanics: str = ""

    def __post_init__(self) -> None:
        if not self.receipt_id.strip():
            raise ValueError("structural assimilation receipt requires an id")
        object.__setattr__(self, "donor_authority", StructuralAuthority(self.donor_authority))
        object.__setattr__(self, "claimed_authority", StructuralAuthority(self.claimed_authority))


@dataclass(frozen=True)
class StructuralHostileFinding:
    kind: StructuralHostileFindingKind
    detail: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "kind", StructuralHostileFindingKind(self.kind))
        if not self.detail.strip():
            raise ValueError("hostile structural finding requires detail")


@dataclass(frozen=True)
class ScientificStructureAssimilationReceipt:
    schema_id: str
    receipt_id: str
    donor: StructuralDonorIdentity
    assessments: tuple[CoordinateAssessment, ...]
    assumption_profile: StructuralAssumptionProfile
    hostile_findings: tuple[StructuralHostileFinding, ...]
    verdict: StructuralAssimilationVerdict
    verdict_reasons: tuple[str, ...]
    structural_receipt_id_for_mechanics: str
    content_hash: str = field(default="")

    @property
    def grants_authority(self) -> str:
        return "NONE"

    @property
    def grants_novelty(self) -> bool:
        return False

    @property
    def grants_donor_equivalence(self) -> bool:
        return False

    @property
    def self_authorizing(self) -> bool:
        return False


@dataclass(frozen=True)
class StructuralAssimilationClosureReport:
    receipt_ids: tuple[str, ...]
    admitted_receipts: int
    cannot_check_receipts: int
    blocked_receipts: int
    no_material_change_rounds: int
    terminal: str
    method_disposition: str
    grants_authority: str = "NONE"
    self_authorizing: bool = False


def _finding(kind: StructuralHostileFindingKind, detail: str) -> StructuralHostileFinding:
    return StructuralHostileFinding(kind, detail)


def assess_structural_assimilation(draft: StructuralAssimilationDraft) -> tuple[StructuralHostileFinding, ...]:
    findings: list[StructuralHostileFinding] = []
    coordinates = [assessment.coordinate for assessment in draft.assessments]
    invalid = [coordinate.value for coordinate in REQUIRED_COORDINATES if coordinates.count(coordinate) != 1]
    if invalid:
        findings.append(_finding(
            StructuralHostileFindingKind.ALGORITHM_ONLY_ABSORPTION,
            "receipt must contain exactly one A-G structural assessment; invalid: " + ", ".join(invalid),
        ))

    if draft.donor.source_kind is StructuralSourceKind.SECONDARY:
        findings.append(_finding(
            StructuralHostileFindingKind.UNGROUNDED_SOURCE,
            "a secondary source cannot settle a donor's structural commitments",
        ))

    missing_ownership = [
        assessment.coordinate.value
        for assessment in draft.assessments
        if assessment.disposition not in {StructuralDisposition.ORTHOGONAL, StructuralDisposition.DEFER_CANNOT_CHECK}
        and not assessment.donor_owner_refs
    ]
    if missing_ownership:
        findings.append(_finding(
            StructuralHostileFindingKind.PHILOSOPHY_LAUNDERING,
            "material donor structure lacks donor ownership refs: " + ", ".join(missing_ownership),
        ))

    if any(a.disposition is StructuralDisposition.CONFLICT for a in draft.assessments) and not draft.conflict_tests:
        findings.append(_finding(
            StructuralHostileFindingKind.INCOMPATIBLE_BLEND,
            "CONFLICT disposition requires an explicit discriminator/test rather than prose blending",
        ))

    if authority_rank(draft.claimed_authority) > authority_rank(draft.donor_authority):
        findings.append(_finding(
            StructuralHostileFindingKind.AUTHORITY_ESCALATION,
            f"donor authority {draft.donor_authority.value} escalated to {draft.claimed_authority.value}",
        ))

    revision_material = any(
        a.coordinate in {StructuralCoordinate.A_SCIENTIFIC_ONTOLOGY, StructuralCoordinate.D_REVISION}
        and a.disposition not in {StructuralDisposition.ORTHOGONAL, StructuralDisposition.DEFER_CANNOT_CHECK}
        for a in draft.assessments
    )
    if revision_material and not draft.representation_boundary.strip():
        findings.append(_finding(
            StructuralHostileFindingKind.REPRESENTATION_ERASURE,
            "material ontology/revision absorption must state fixed-versus-revisable representation boundary",
        ))
    if revision_material and not draft.preservation_rule.strip():
        findings.append(_finding(
            StructuralHostileFindingKind.PRESERVATION_ERASURE,
            "material revision absorption must state preservation/revalidation behavior",
        ))

    if draft.claims_cross_domain_generalization and not draft.scope_extension_rationale.strip():
        findings.append(_finding(
            StructuralHostileFindingKind.SCOPE_LAUNDERING,
            f"source is scoped to {draft.donor.source_scope!r}; cross-domain generalization has no rationale",
        ))

    if draft.llm_involved and (not draft.explicit_non_llm_machinery or not draft.llm_marginal_role_checked):
        findings.append(_finding(
            StructuralHostileFindingKind.LLM_MYSTIFICATION,
            "LLM-involved donor must separate explicit machinery and check the marginal LLM role",
        ))

    if draft.donor_has_relevant_negative_result and not draft.negative_results:
        findings.append(_finding(
            StructuralHostileFindingKind.NEGATIVE_RESULT_DELETION,
            "known donor negative/control result was omitted from the structural receipt",
        ))

    if not draft.downstream_children and not draft.explicit_no_change_reason.strip():
        findings.append(_finding(
            StructuralHostileFindingKind.CITATION_ONLY_RECEIPT,
            "receipt names a donor but records neither a downstream consequence nor explicit NO_CHANGE rationale",
        ))

    if draft.material_structural_donor and draft.mechanism_receipt_ids and not draft.structural_receipt_id_for_mechanics.strip():
        findings.append(_finding(
            StructuralHostileFindingKind.MISSING_UPSTREAM_STRUCTURE,
            "material structural donor has downstream mechanism receipts but no upstream structural receipt identity",
        ))

    return tuple(findings)


def seal_structural_assimilation(draft: StructuralAssimilationDraft) -> ScientificStructureAssimilationReceipt:
    findings = assess_structural_assimilation(draft)
    reasons: list[str] = []
    if findings:
        verdict = StructuralAssimilationVerdict.BLOCKED
        reasons.extend(f"{finding.kind.value}: {finding.detail}" for finding in findings)
    elif draft.donor.access is not StructuralSourceAccess.FULL_TEXT:
        verdict = StructuralAssimilationVerdict.CANNOT_CHECK
        reasons.append("donor body not fully source-grounded; structural commitments remain CANNOT_CHECK")
    else:
        verdict = StructuralAssimilationVerdict.ADMITTED
        reasons.append("full primary/official source read; A-G structure and explicit assumption profile recorded; no hostile finding")

    receipt = ScientificStructureAssimilationReceipt(
        schema_id=SCHEMA_ID,
        receipt_id=draft.receipt_id,
        donor=draft.donor,
        assessments=draft.assessments,
        assumption_profile=draft.assumption_profile,
        hostile_findings=findings,
        verdict=verdict,
        verdict_reasons=tuple(reasons),
        structural_receipt_id_for_mechanics=(
            draft.structural_receipt_id_for_mechanics or draft.receipt_id
        ),
    )
    return ScientificStructureAssimilationReceipt(
        **{**receipt.__dict__, "content_hash": sha256_canonical(receipt)}
    )


def build_structural_assimilation_closure(
    receipts: Iterable[ScientificStructureAssimilationReceipt],
    *,
    no_material_change_rounds: int,
) -> StructuralAssimilationClosureReport:
    receipts = tuple(receipts)
    if not receipts:
        raise ValueError("structural assimilation closure requires receipts")
    ids = [receipt.receipt_id for receipt in receipts]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate structural assimilation receipt id")
    admitted = sum(receipt.verdict is StructuralAssimilationVerdict.ADMITTED for receipt in receipts)
    cannot_check = sum(receipt.verdict is StructuralAssimilationVerdict.CANNOT_CHECK for receipt in receipts)
    blocked = sum(receipt.verdict is StructuralAssimilationVerdict.BLOCKED for receipt in receipts)
    saturated = blocked == 0 and cannot_check == 0 and no_material_change_rounds >= 2
    return StructuralAssimilationClosureReport(
        receipt_ids=tuple(sorted(ids)),
        admitted_receipts=admitted,
        cannot_check_receipts=cannot_check,
        blocked_receipts=blocked,
        no_material_change_rounds=no_material_change_rounds,
        terminal=("STRUCTURAL_ASSIMILATION_SATURATED" if saturated else "CANNOT_CHECK"),
        method_disposition=("USEFUL_PROCESS_NOT_NOVEL" if saturated else "CANNOT_CHECK"),
    )
