"""Prospective finite closure for cross-domain transfer (#286) and assimilation (#318).

The pre-outcome panel and exact expectations live under
``development/cross-domain-transfer-closure`` and were committed before this
module. Candidate policies operate on ``PublicTransferCase`` only; protected
case type and gold action are kept in ``ProtectedTransferCase`` and enter only
at scoring time.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
from typing import Iterable

from orion.knowledge.mechanism_assimilation import (
    AssimilationAuthority,
    AssimilationClaim,
    AssimilationDraft,
    AssumptionStatus,
    DonorAssumption,
    DonorIdentity,
    DonorMechanism,
    DonorSourceAccess,
    DonorSourceKind,
    seal_assimilation,
)
from orion.knowledge.nearest_work import (
    AbsorptionDisposition,
    NearestWorkComparison,
    NoveltyCase,
    NoveltyVerdict,
    WorkRelation,
    assess_novelty_case,
)

DOMAINS = ("software", "retrieval", "semantics", "authority", "measurement")
FAMILIES = (
    "scoped_repair",
    "coverage_stop",
    "semantic_transport",
    "noncomp_authority",
    "measurement_redesign",
)
CASE_TYPES = ("positive", "positive", "positive", "near_miss", "near_miss", "negative", "negative", "partial")


class TransferAction(str, Enum):
    APPLY_FULL = "APPLY_FULL"
    APPLY_PARTIAL = "APPLY_PARTIAL"
    REJECT = "REJECT"
    NO_TRANSFER = "NO_TRANSFER"


class TransferArm(str, Enum):
    NO_TRANSFER = "NO_TRANSFER"
    RAW_TRAJECTORY = "RAW_TRAJECTORY"
    SUMMARY_MEMORY = "SUMMARY_MEMORY"
    ABSTRACT_INSIGHT = "ABSTRACT_INSIGHT"
    SKILL_INSTRUCTION = "SKILL_INSTRUCTION"
    SURFACE_SIMILARITY = "SURFACE_SIMILARITY"
    ABSTRACT_INSIGHT_SIGNATURE = "ABSTRACT_INSIGHT_SIGNATURE"
    MECHANIC_CONTRACT_RECEIPT = "MECHANIC_CONTRACT_RECEIPT"
    ORACLE = "ORACLE"


@dataclass(frozen=True)
class PublicTransferCase:
    case_id: str
    family_token: str
    source_domain: str
    target_domain: str
    surface_similarity: bool
    source_signature: tuple[tuple[str, str], ...]
    target_signature: tuple[tuple[str, str], ...]
    available_submechanic: bool
    abstract_insight: str
    mechanic_contract: tuple[str, ...]

    def source(self) -> dict[str, str]:
        return dict(self.source_signature)

    def target(self) -> dict[str, str]:
        return dict(self.target_signature)


@dataclass(frozen=True)
class ProtectedTransferCase:
    public: PublicTransferCase
    case_type: str
    gold_action: TransferAction


@dataclass(frozen=True)
class ArmMetrics:
    correct: int
    negative_transfer: int
    positive_full_correct: int
    partial_correct: int
    worst_domain_correct: int


@dataclass(frozen=True)
class TransferClosureReport:
    case_count: int
    arm_metrics: tuple[tuple[str, ArmMetrics], ...]
    issue_286_terminal: str
    issue_318_terminal: str
    parent_ties_contract: bool
    assimilation_novelty_verdict: str
    grants_scientific_authority: bool = False
    grants_novelty_authority: bool = False
    grants_issue_closure_authority: bool = False


def _opaque_case_id(family_index: int, case_index: int) -> str:
    return sha256(f"orion-transfer-v1:{family_index}:{case_index}".encode()).hexdigest()[:16]


def build_protected_panel() -> tuple[ProtectedTransferCase, ...]:
    cases: list[ProtectedTransferCase] = []
    for family_index, family in enumerate(FAMILIES):
        source_domain = DOMAINS[family_index]
        for case_index, case_type in enumerate(CASE_TYPES):
            target_domain = DOMAINS[(family_index + case_index + 1) % len(DOMAINS)]
            surface = case_type in {"positive", "near_miss"} or (
                case_type == "negative" and case_index == 5
            )
            requested_family = f"unrelated-{family}" if case_type == "negative" else family
            source_assumption = "stable"
            target_assumption = "changed" if case_type == "near_miss" else "stable"
            full_ok = case_type == "positive"
            partial_ok = case_type == "partial"
            source_signature = (
                ("family", family),
                ("assumption", source_assumption),
                ("tool", "available"),
            )
            target_signature = (
                ("requested_family", requested_family),
                ("assumption", target_assumption),
                ("full_preconditions", "met" if full_ok else "unmet"),
                ("partial_preconditions", "met" if partial_ok else "unmet"),
                ("tool", "available"),
            )
            public = PublicTransferCase(
                case_id=_opaque_case_id(family_index, case_index),
                family_token=family,
                source_domain=source_domain,
                target_domain=target_domain,
                surface_similarity=surface,
                source_signature=source_signature,
                target_signature=target_signature,
                available_submechanic=partial_ok,
                abstract_insight=f"apply {family} only where its source assumptions survive",
                mechanic_contract=(
                    f"family={family}",
                    "require assumption compatibility",
                    "require full preconditions for full transfer",
                    "allow registered submechanic only when partial preconditions hold",
                    "reject rather than compensate for an assumption mismatch",
                ),
            )
            gold = {
                "positive": TransferAction.APPLY_FULL,
                "near_miss": TransferAction.REJECT,
                "negative": TransferAction.NO_TRANSFER,
                "partial": TransferAction.APPLY_PARTIAL,
            }[case_type]
            cases.append(ProtectedTransferCase(public=public, case_type=case_type, gold_action=gold))
    return tuple(cases)


def _signature_action(case: PublicTransferCase) -> TransferAction:
    source = case.source()
    target = case.target()
    if target["requested_family"] != source["family"]:
        return TransferAction.NO_TRANSFER
    if target["assumption"] != source["assumption"]:
        return TransferAction.REJECT
    if target["full_preconditions"] == "met":
        return TransferAction.APPLY_FULL
    if case.available_submechanic and target["partial_preconditions"] == "met":
        return TransferAction.APPLY_PARTIAL
    return TransferAction.REJECT


def choose_action(arm: TransferArm, case: PublicTransferCase) -> TransferAction:
    arm = TransferArm(arm)
    if arm is TransferArm.NO_TRANSFER:
        return TransferAction.NO_TRANSFER
    if arm in {TransferArm.RAW_TRAJECTORY, TransferArm.SURFACE_SIMILARITY}:
        return TransferAction.APPLY_FULL if case.surface_similarity else TransferAction.NO_TRANSFER
    if arm in {TransferArm.SUMMARY_MEMORY, TransferArm.ABSTRACT_INSIGHT, TransferArm.SKILL_INSTRUCTION}:
        if case.target()["requested_family"] == case.family_token:
            return TransferAction.APPLY_FULL
        return TransferAction.NO_TRANSFER
    if arm in {TransferArm.ABSTRACT_INSIGHT_SIGNATURE, TransferArm.MECHANIC_CONTRACT_RECEIPT}:
        return _signature_action(case)
    raise ValueError("ORACLE must be evaluated only by the protected evaluator")


def score_arm(arm: TransferArm, cases: Iterable[ProtectedTransferCase]) -> ArmMetrics:
    arm = TransferArm(arm)
    by_domain: dict[str, list[bool]] = {domain: [] for domain in DOMAINS}
    correct = 0
    negative_transfer = 0
    positive_full_correct = 0
    partial_correct = 0
    for case in cases:
        action = case.gold_action if arm is TransferArm.ORACLE else choose_action(arm, case.public)
        is_correct = action is case.gold_action
        correct += int(is_correct)
        by_domain[case.public.target_domain].append(is_correct)
        if case.case_type in {"near_miss", "negative"} and action in {
            TransferAction.APPLY_FULL,
            TransferAction.APPLY_PARTIAL,
        }:
            negative_transfer += 1
        if case.case_type == "positive" and action is TransferAction.APPLY_FULL:
            positive_full_correct += 1
        if case.case_type == "partial" and action is TransferAction.APPLY_PARTIAL:
            partial_correct += 1
    return ArmMetrics(
        correct=correct,
        negative_transfer=negative_transfer,
        positive_full_correct=positive_full_correct,
        partial_correct=partial_correct,
        worst_domain_correct=min(sum(values) for values in by_domain.values()),
    )


def build_assimilation_demo() -> tuple[tuple[str, str], ...]:
    donor = DonorIdentity(
        donor_id="prospective-donor-v1",
        title="Prospective transfer donor",
        source_kind=DonorSourceKind.PRIMARY_PAPER,
        source_uri="registered:prospective-donor-v1",
        access=DonorSourceAccess.FULL_TEXT,
    )
    assumption = DonorAssumption(
        assumption_id="A1",
        text="target signature preserves the load-bearing source assumption",
        status=AssumptionStatus.PRESERVED,
    )
    mechanism = DonorMechanism(
        mechanism_id="signature-gated-transfer",
        donor_name="signature-gated applicability",
        summary="admit transfer only when registered source/target assumptions are compatible",
        donor_authority=AssimilationAuthority.BOUNDED,
        assumptions=(assumption,),
    )
    demos = (
        AssimilationDraft(
            receipt_id="ADOPT-1",
            donor=donor,
            mechanism=mechanism,
            disposition=AbsorptionDisposition.ADOPT,
            claim=AssimilationClaim(
                orion_name="signature-gated applicability",
                target_mechanic_ids=("transfer-selector",),
                orion_authority=AssimilationAuthority.BOUNDED,
            ),
            evidence_refs=("development/cross-domain-transfer-closure/ASSIMILATION_DEMO_V1.json",),
        ),
        AssimilationDraft(
            receipt_id="ADAPT-1",
            donor=donor,
            mechanism=mechanism,
            disposition=AbsorptionDisposition.ADAPT,
            claim=AssimilationClaim(
                orion_name="evidence-bound transfer record",
                target_mechanic_ids=("transfer-record",),
                orion_authority=AssimilationAuthority.BOUNDED,
                delta="bind explicit failure modes, falsifiers, and authority boundary",
            ),
            evidence_refs=("development/cross-domain-transfer-closure/ASSIMILATION_DEMO_V1.json",),
        ),
        AssimilationDraft(
            receipt_id="COMPOSE-1",
            donor=donor,
            mechanism=mechanism,
            disposition=AbsorptionDisposition.COMPOSE,
            claim=AssimilationClaim(
                orion_name="abstract insight plus signature compatibility",
                target_mechanic_ids=("abstract-insight", "transfer-selector"),
                orion_authority=AssimilationAuthority.BOUNDED,
                delta="compose two donor-owned parts without claiming either primitive",
                composed_with=("abstract-insight",),
                composition_evidence=("development/cross-domain-transfer-closure/PANEL_V1.json",),
            ),
            evidence_refs=("development/cross-domain-transfer-closure/ASSIMILATION_DEMO_V1.json",),
        ),
    )
    return tuple((draft.receipt_id, seal_assimilation(draft).verdict.value) for draft in demos)


def build_assimilation_novelty_assessment():
    """Route the absorbed generic transfer mechanism through the existing #287 logic."""

    case = NoveltyCase(
        paper_id="ORION-PROGRAMME",
        target_claim="signature-gated cross-domain transfer is an ORION invention",
        comparisons=(
            NearestWorkComparison(
                work_id="transfer-parent-product",
                relation=WorkRelation.SUBSUMES_CANDIDATE,
                absorbed_mechanism_ids=("signature-gated-transfer", "abstract-insight-transfer"),
                residual_delta_ids=(),
                note="the frozen abstract-insight+signature arm matches the richer contract arm",
            ),
        ),
        candidate_delta_ids=(),
        falsifier_ids=("cross-domain-transfer-closure-v1",),
    )
    return assess_novelty_case(case)


def build_closure_report() -> TransferClosureReport:
    cases = build_protected_panel()
    metrics = tuple((arm.value, score_arm(arm, cases)) for arm in TransferArm)
    by_name = dict(metrics)
    parent_ties = by_name[TransferArm.ABSTRACT_INSIGHT_SIGNATURE.value] == by_name[
        TransferArm.MECHANIC_CONTRACT_RECEIPT.value
    ]
    issue_286_terminal = "ABSTRACTION_ONLY" if parent_ties else "CANNOT_CHECK"
    demos = build_assimilation_demo()
    novelty = build_assimilation_novelty_assessment()
    process_green = all(verdict == "ADMITTED" for _, verdict in demos) and novelty.verdict is NoveltyVerdict.SUBSUMED
    issue_318_terminal = "PROCESS_USEFUL_NOT_NOVEL" if parent_ties and process_green else "CANNOT_CHECK"
    return TransferClosureReport(
        case_count=len(cases),
        arm_metrics=metrics,
        issue_286_terminal=issue_286_terminal,
        issue_318_terminal=issue_318_terminal,
        parent_ties_contract=parent_ties,
        assimilation_novelty_verdict=novelty.verdict.value,
    )
