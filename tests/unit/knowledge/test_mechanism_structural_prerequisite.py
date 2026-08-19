from __future__ import annotations

from orion.knowledge.mechanism_assimilation import (
    AssimilationAuthority,
    AssimilationClaim,
    AssimilationDraft,
    AssimilationVerdict,
    DonorAssumption,
    DonorIdentity,
    DonorMechanism,
    DonorSourceAccess,
    DonorSourceKind,
    HostileFindingKind,
    AssumptionStatus,
    seal_assimilation,
)
from orion.knowledge.nearest_work import AbsorptionDisposition

DONOR = DonorIdentity(
    donor_id="arxiv:2607.12474",
    title="From Observation to Insight: Mechanistic World Models and the Quest for Autonomous Discovery",
    source_kind=DonorSourceKind.PRIMARY_PAPER,
    source_uri="https://arxiv.org/abs/2607.12474",
    access=DonorSourceAccess.FULL_TEXT,
)
MECHANISM = DonorMechanism(
    mechanism_id="m:mechanism-library",
    donor_name="Mechanistic World Model",
    summary="Organize predictive and explanatory computation around reusable mechanisms.",
    donor_authority=AssimilationAuthority.DESCRIPTIVE,
    assumptions=(
        DonorAssumption(
            "a:mechanism-abstraction",
            "reusable mechanisms are the central explanatory abstraction",
            AssumptionStatus.PRESERVED,
        ),
    ),
)
CLAIM = AssimilationClaim(
    orion_name="mechanism library",
    target_mechanic_ids=("P6.MECHANISM_LIBRARY",),
    orion_authority=AssimilationAuthority.DESCRIPTIVE,
    delta="ORION retains donor ownership and binds the mechanism to an explicit structural receipt",
)


def _draft(**overrides) -> AssimilationDraft:
    payload = dict(
        receipt_id="assim:mwm:mechanism-library",
        donor=DONOR,
        mechanism=MECHANISM,
        disposition=AbsorptionDisposition.ADOPT,
        claim=CLAIM,
        evidence_refs=("arxiv:2607.12474v2",),
    )
    payload.update(overrides)
    return AssimilationDraft(**payload)


def test_material_structural_donor_without_upstream_receipt_is_blocked() -> None:
    receipt = seal_assimilation(_draft(material_structural_donor=True))
    assert receipt.verdict is AssimilationVerdict.BLOCKED
    assert HostileFindingKind.MISSING_STRUCTURAL_RECEIPT in {f.kind for f in receipt.hostile_findings}
    assert receipt.grants_authority == "NONE"


def test_material_structural_donor_with_receipt_can_reach_normal_mechanism_checks() -> None:
    receipt = seal_assimilation(
        _draft(material_structural_donor=True, structural_receipt_id="ssa:v1:mwm")
    )
    assert receipt.verdict is AssimilationVerdict.ADMITTED
    assert HostileFindingKind.MISSING_STRUCTURAL_RECEIPT not in {f.kind for f in receipt.hostile_findings}
    assert receipt.structural_receipt_id == "ssa:v1:mwm"
    assert receipt.grants_authority == "NONE"
    assert receipt.self_authorizing is False


def test_non_structural_atomic_donor_is_not_forced_through_structural_programme() -> None:
    receipt = seal_assimilation(_draft(material_structural_donor=False))
    assert receipt.verdict is AssimilationVerdict.ADMITTED
    assert HostileFindingKind.MISSING_STRUCTURAL_RECEIPT not in {f.kind for f in receipt.hostile_findings}
