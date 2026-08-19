"""Prospective programme-level ADOPT/ADAPT/COMPOSE experiment for #318.

This is intentionally outside the P1/P2 paper-local ledgers.  It consumes three
full-text, already source-grounded structural donors from #454 and asks whether the
atomic MechanismAssimilationReceipt.v1 can record clean programme-level paths into the
Self-ORION V3 revision-responsibility lane without rebranding, dropping assumptions,
escalating authority, or asserting composition without evidence.

The experiment evaluates the *assimilation method*.  It does not claim the imported
mechanics are ORION novelty or that V3's scientific hypothesis is true.
"""

from __future__ import annotations

from dataclasses import dataclass

from orion.knowledge.mechanism_assimilation import (
    AssimilationAuthority,
    AssimilationClaim,
    AssimilationDraft,
    AssimilationVerdict,
    AssumptionStatus,
    DonorAssumption,
    DonorIdentity,
    DonorMechanism,
    DonorSourceAccess,
    DonorSourceKind,
    MechanismAssimilationReceipt,
    seal_assimilation,
)
from orion.knowledge.nearest_work import AbsorptionDisposition


@dataclass(frozen=True)
class ProgrammeAssimilationResult:
    receipts: tuple[MechanismAssimilationReceipt, ...]

    @property
    def dispositions(self) -> frozenset[AbsorptionDisposition]:
        return frozenset(receipt.disposition for receipt in self.receipts)

    @property
    def all_admitted(self) -> bool:
        return all(receipt.verdict is AssimilationVerdict.ADMITTED for receipt in self.receipts)

    @property
    def grants_authority(self) -> bool:
        return any(receipt.grants_authority != "NONE" for receipt in self.receipts)


def _identity(donor_id: str, title: str, source_uri: str) -> DonorIdentity:
    return DonorIdentity(
        donor_id=donor_id,
        title=title,
        source_kind=DonorSourceKind.PRIMARY_PAPER,
        source_uri=source_uri,
        access=DonorSourceAccess.FULL_TEXT,
    )


def _adopt() -> AssimilationDraft:
    """ADOPT donor-owned preservation across a regime transition."""
    return AssimilationDraft(
        receipt_id="programme:v1:adopt:self-revising-preservation",
        donor=_identity(
            "arxiv:2606.01444v1",
            "Self-Revising Discovery Systems for Science: A Categorical Framework for Agentic Artificial Intelligence",
            "https://arxiv.org/abs/2606.01444v1",
        ),
        mechanism=DonorMechanism(
            mechanism_id="donor:self-revising:preservation-transport",
            donor_name="provenance-preserving transport across representational-regime transitions",
            summary="Old artifacts/evidence are transported across a regime transition and residual content is explicitly revalidated rather than silently discarded.",
            donor_authority=AssimilationAuthority.BOUNDED,
            assumptions=(
                DonorAssumption(
                    "typed-regime",
                    "source and target scientific states are typed by explicit representational regimes",
                    AssumptionStatus.PRESERVED,
                ),
                DonorAssumption(
                    "revalidation",
                    "affected evidence/claims are revalidated after transport",
                    AssumptionStatus.PRESERVED,
                ),
            ),
        ),
        disposition=AbsorptionDisposition.ADOPT,
        claim=AssimilationClaim(
            orion_name="provenance-preserving transport across representational-regime transitions",
            target_mechanic_ids=("v3:preserve-evidence-across-regime",),
            orion_authority=AssimilationAuthority.BOUNDED,
            delta="",
        ),
        not_taken=(
            "the donor's categorical formalism is not claimed as ORION invention",
            "the donor receipt does not authorize an actual regime revision",
        ),
        evidence_refs=(
            "research/structural-assimilation-v1/STRUCTURAL_ASSIMILATION_CLOSURE_V1.md",
        ),
        material_structural_donor=True,
        structural_receipt_id="ssa:v1:self-revising-2606.01444v1",
    )


def _adapt() -> AssimilationDraft:
    """ADAPT AWM persistent revision into a narrower responsibility-gated response."""
    return AssimilationDraft(
        receipt_id="programme:v1:adapt:awm-evolver",
        donor=_identity(
            "arxiv:2604.22748v3",
            "Agentic World Modeling: Foundations, Capabilities, Laws, and Beyond",
            "https://arxiv.org/abs/2604.22748v3",
        ),
        mechanism=DonorMechanism(
            mechanism_id="donor:awm:l3-evolver",
            donor_name="persistent evidence-driven world-model evolution",
            summary="Prediction failure against new evidence can drive persistent world-model revision, with regression validation rather than untracked overwrite.",
            donor_authority=AssimilationAuthority.DESCRIPTIVE,
            assumptions=(
                DonorAssumption(
                    "world-model-scope",
                    "the response is a world-model revision rather than arbitrary objective/evaluator mutation",
                    AssumptionStatus.PRESERVED,
                ),
                DonorAssumption(
                    "regression-validation",
                    "persistent updates retain regression validation against prior capability/evidence",
                    AssumptionStatus.PRESERVED,
                ),
            ),
        ),
        disposition=AbsorptionDisposition.ADAPT,
        claim=AssimilationClaim(
            orion_name="responsibility-gated persistent model revision",
            target_mechanic_ids=("v3:revision-response-selector",),
            orion_authority=AssimilationAuthority.DESCRIPTIVE,
            delta="ORION narrows the donor response: discrepancy alone does not license revision; a discriminator must first localize responsibility and may instead choose evidence acquisition, containment, execution repair, evaluator repair, or unresolved.",
        ),
        not_taken=(
            "generic discrepancy-driven persistent model revision remains donor-owned",
            "no authority to revise objective or evaluator is inherited",
        ),
        evidence_refs=(
            "research/structural-assimilation-v1/STRUCTURAL_ASSIMILATION_CLOSURE_V1.md",
            "research/self-orion-v3/revision-level-discrimination/PREFREEZE_STAGE0_CASE_CONTRACT.md",
        ),
        material_structural_donor=True,
        structural_receipt_id="ssa:v1:awm-2604.22748v3",
    )


def _compose() -> AssimilationDraft:
    """COMPOSE MWM localization with the already-adopted preservation obligation."""
    return AssimilationDraft(
        receipt_id="programme:v1:compose:mwm-localize-plus-preserve",
        donor=_identity(
            "arxiv:2607.12474v2",
            "From Observation to Insight: Mechanistic World Models and the Quest for Autonomous Discovery",
            "https://arxiv.org/abs/2607.12474v2",
        ),
        mechanism=DonorMechanism(
            mechanism_id="donor:mwm:localized-mechanism-update",
            donor_name="localized mechanism update and recomposition",
            summary="Mechanism-centric representations support localizing failure to implicated mechanisms and updating/recomposing them rather than replacing an entire model.",
            donor_authority=AssimilationAuthority.DESCRIPTIVE,
            assumptions=(
                DonorAssumption(
                    "mechanism-identity",
                    "reusable mechanism identity is represented explicitly enough to localize implicated components",
                    AssumptionStatus.PRESERVED,
                ),
                DonorAssumption(
                    "localization-not-authority",
                    "failure localization does not itself grant scientific adoption authority",
                    AssumptionStatus.PRESERVED,
                ),
            ),
        ),
        disposition=AbsorptionDisposition.COMPOSE,
        claim=AssimilationClaim(
            orion_name="localized revision with provenance-preserving transport",
            target_mechanic_ids=("v3:localized-revision-with-preservation",),
            orion_authority=AssimilationAuthority.DESCRIPTIVE,
            delta="The programme composes donor-owned mechanism localization with the separately adopted preservation/transport obligation; neither component is renamed as ORION novelty.",
            composed_with=("programme:v1:adopt:self-revising-preservation",),
            composition_evidence=(
                "tests/unit/self_orion/test_revision_level_v3.py::test_responsibility_gated_policy_solves_white_box_stage0",
                "research/self-orion-v3/revision-level-discrimination/PREFREEZE_STAGE0_CASE_CONTRACT.md#preservation-and-history-split",
            ),
        ),
        not_taken=(
            "generic mechanism-centric representation remains MWM-owned",
            "verified regime transport remains Self-Revising-owned",
            "the composition is a programme hypothesis/input, not a novelty verdict",
        ),
        evidence_refs=(
            "research/structural-assimilation-v1/STRUCTURAL_ASSIMILATION_CLOSURE_V1.md",
            "tests/unit/self_orion/test_revision_level_v3.py",
        ),
        material_structural_donor=True,
        structural_receipt_id="ssa:v1:mwm-2607.12474v2",
    )


def run_programme_assimilation_experiment() -> ProgrammeAssimilationResult:
    receipts = tuple(seal_assimilation(draft) for draft in (_adopt(), _adapt(), _compose()))
    return ProgrammeAssimilationResult(receipts=receipts)
