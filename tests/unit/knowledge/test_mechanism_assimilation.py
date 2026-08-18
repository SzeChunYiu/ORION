"""`MechanismAssimilationReceipt.v1` refuses the four ways absorption becomes theft.

Each hostile check has a firing case and a matching no-alarm case. A guard that
only ever fires is indistinguishable from a broken guard, and one that never
fires on real input gets switched off — so both directions are pinned.
"""

from __future__ import annotations

import pytest

from orion.knowledge.mechanism_assimilation import (
    SCHEMA_ID,
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
    HostileFindingKind,
    authority_rank,
    seal_assimilation,
)
from orion.knowledge.nearest_work import AbsorptionDisposition

PRIMARY = DonorIdentity(
    donor_id="arxiv:2509.04708",
    title="Bayesian Diagnosability and Active Fault Identification",
    source_kind=DonorSourceKind.PRIMARY_PAPER,
    source_uri="https://arxiv.org/abs/2509.04708",
    access=DonorSourceAccess.FULL_TEXT,
)

MECHANISM = DonorMechanism(
    mechanism_id="m:active-diagnosis",
    donor_name="active fault identification",
    summary="Active inputs make otherwise undiagnosable faults distinguishable.",
    donor_authority=AssimilationAuthority.BOUNDED,
    assumptions=(
        DonorAssumption("a1", "faults come from a known finite set", AssumptionStatus.PRESERVED),
    ),
)

CLEAN_CLAIM = AssimilationClaim(
    orion_name="active diagnosability probe",
    target_mechanic_ids=("P1.DIAGNOSABILITY",),
    orion_authority=AssimilationAuthority.BOUNDED,
    delta="scoped to epistemic coordinates rather than physical faults",
)


def _draft(**overrides) -> AssimilationDraft:
    base = {
        "receipt_id": "assim:p1:active-diagnosis",
        "donor": PRIMARY,
        "mechanism": MECHANISM,
        "disposition": AbsorptionDisposition.ADOPT,
        "claim": CLEAN_CLAIM,
    }
    base.update(overrides)
    return AssimilationDraft(**base)


def _kinds(draft: AssimilationDraft) -> set[HostileFindingKind]:
    return {finding.kind for finding in seal_assimilation(draft).hostile_findings}


def test_a_clean_absorption_is_admitted_and_grants_nothing() -> None:
    receipt = seal_assimilation(_draft())
    assert receipt.verdict is AssimilationVerdict.ADMITTED
    assert receipt.hostile_findings == ()
    assert receipt.schema_id == SCHEMA_ID
    assert len(receipt.content_hash) == 64
    # Admission records an honest absorption. It is not permission to claim the
    # mechanism, which is the whole distinction #318 exists to hold.
    assert receipt.grants_authority == "NONE"
    assert receipt.self_authorizing is False


def test_renaming_without_a_delta_is_rebranding() -> None:
    renamed = AssimilationClaim(
        orion_name="epistemic diagnosability licensing",
        target_mechanic_ids=("P1.DIAGNOSABILITY",),
        orion_authority=AssimilationAuthority.BOUNDED,
    )
    assert HostileFindingKind.REBRANDING in _kinds(_draft(claim=renamed))
    # No alarm: the same rename with a stated difference is a contribution.
    assert HostileFindingKind.REBRANDING not in _kinds(_draft())
    # No alarm: keeping the donor's own name is never rebranding, delta or not.
    same_name = AssimilationClaim(
        orion_name=MECHANISM.donor_name,
        target_mechanic_ids=("P1.DIAGNOSABILITY",),
        orion_authority=AssimilationAuthority.BOUNDED,
    )
    assert HostileFindingKind.REBRANDING not in _kinds(_draft(claim=same_name))


def test_dropping_a_donor_assumption_needs_a_reason() -> None:
    dropped = DonorMechanism(
        mechanism_id=MECHANISM.mechanism_id,
        donor_name=MECHANISM.donor_name,
        summary=MECHANISM.summary,
        donor_authority=MECHANISM.donor_authority,
        assumptions=(DonorAssumption("a1", "faults come from a known finite set", AssumptionStatus.DROPPED),),
    )
    assert HostileFindingKind.LOST_ASSUMPTIONS in _kinds(_draft(mechanism=dropped))

    justified = DonorMechanism(
        mechanism_id=MECHANISM.mechanism_id,
        donor_name=MECHANISM.donor_name,
        summary=MECHANISM.summary,
        donor_authority=MECHANISM.donor_authority,
        assumptions=(
            DonorAssumption(
                "a1",
                "faults come from a known finite set",
                AssumptionStatus.RELAXED,
                justification="epistemic coordinates are enumerable per problem, so the finite set is per-instance",
            ),
        ),
    )
    assert HostileFindingKind.LOST_ASSUMPTIONS not in _kinds(_draft(mechanism=justified))


def test_a_mechanism_cannot_gain_authority_by_being_absorbed() -> None:
    escalated = AssimilationClaim(
        orion_name="active diagnosability probe",
        target_mechanic_ids=("P1.DIAGNOSABILITY",),
        orion_authority=AssimilationAuthority.GENERAL,
        delta="scoped to epistemic coordinates rather than physical faults",
    )
    assert HostileFindingKind.AUTHORITY_ESCALATION in _kinds(_draft(claim=escalated))

    # No alarm in both safe directions: equal authority, and a deliberate
    # *demotion*, which is the honest move when the transfer is untested.
    assert HostileFindingKind.AUTHORITY_ESCALATION not in _kinds(_draft())
    demoted = AssimilationClaim(
        orion_name="active diagnosability probe",
        target_mechanic_ids=("P1.DIAGNOSABILITY",),
        orion_authority=AssimilationAuthority.DESCRIPTIVE,
        delta="scoped to epistemic coordinates rather than physical faults",
    )
    assert HostileFindingKind.AUTHORITY_ESCALATION not in _kinds(_draft(claim=demoted))


def test_claiming_composition_requires_showing_it() -> None:
    asserted = AssimilationClaim(
        orion_name="active diagnosability probe",
        target_mechanic_ids=("P1.DIAGNOSABILITY",),
        orion_authority=AssimilationAuthority.BOUNDED,
        delta="scoped to epistemic coordinates rather than physical faults",
        composed_with=("m:mutation-permission",),
    )
    assert HostileFindingKind.FAKE_COMPOSITION in _kinds(_draft(claim=asserted))

    shown = AssimilationClaim(
        orion_name="active diagnosability probe",
        target_mechanic_ids=("P1.DIAGNOSABILITY",),
        orion_authority=AssimilationAuthority.BOUNDED,
        delta="scoped to epistemic coordinates rather than physical faults",
        composed_with=("m:mutation-permission",),
        composition_evidence=("tests/unit/study/p1/test_licensing.py",),
    )
    assert HostileFindingKind.FAKE_COMPOSITION not in _kinds(_draft(claim=shown))


def test_a_secondary_source_cannot_ground_an_assimilation() -> None:
    survey = DonorIdentity(
        donor_id="survey:2026",
        title="A survey of diagnosis methods",
        source_kind=DonorSourceKind.SECONDARY,
        source_uri="https://example.org/survey",
        access=DonorSourceAccess.FULL_TEXT,
    )
    assert HostileFindingKind.UNGROUNDED_SOURCE in _kinds(_draft(donor=survey))
    # No alarm: official code grounds it as well as a primary paper does.
    code = DonorIdentity(
        donor_id="github:org/repo",
        title="Reference implementation",
        source_kind=DonorSourceKind.OFFICIAL_CODE,
        source_uri="https://github.com/org/repo",
        access=DonorSourceAccess.FULL_TEXT,
    )
    assert HostileFindingKind.UNGROUNDED_SOURCE not in _kinds(_draft(donor=code))


def test_findings_block_even_when_the_donor_is_unreachable() -> None:
    """A definite defect must not be softened into an open question.

    Every hostile check is computable from the receipt alone. If an unreachable
    source downgraded a real finding to CANNOT_CHECK, the same receipt could be
    retried later and quietly admitted once the source came back — the defect
    would never have been recorded as a defect.
    """

    unreachable = DonorIdentity(
        donor_id="arxiv:2509.04708",
        title="Bayesian Diagnosability and Active Fault Identification",
        source_kind=DonorSourceKind.PRIMARY_PAPER,
        source_uri="https://arxiv.org/abs/2509.04708",
        access=DonorSourceAccess.UNREACHABLE,
    )
    escalated = AssimilationClaim(
        orion_name="active diagnosability probe",
        target_mechanic_ids=("P1.DIAGNOSABILITY",),
        orion_authority=AssimilationAuthority.GENERAL,
        delta="scoped to epistemic coordinates rather than physical faults",
    )
    receipt = seal_assimilation(_draft(donor=unreachable, claim=escalated))
    assert receipt.verdict is AssimilationVerdict.BLOCKED
    assert HostileFindingKind.AUTHORITY_ESCALATION in {f.kind for f in receipt.hostile_findings}


def test_an_unreachable_donor_with_no_findings_is_cannot_check_not_admitted() -> None:
    unreachable = DonorIdentity(
        donor_id="arxiv:2509.04708",
        title="Bayesian Diagnosability and Active Fault Identification",
        source_kind=DonorSourceKind.PRIMARY_PAPER,
        source_uri="https://arxiv.org/abs/2509.04708",
        access=DonorSourceAccess.UNREACHABLE,
    )
    receipt = seal_assimilation(_draft(donor=unreachable))
    assert receipt.verdict is AssimilationVerdict.CANNOT_CHECK
    assert receipt.hostile_findings == ()


def test_assumptions_declared_from_an_abstract_cannot_be_admitted() -> None:
    """Declaring a donor's validated regime from its abstract is a guess."""

    abstract_only = DonorIdentity(
        donor_id="arxiv:2509.04708",
        title="Bayesian Diagnosability and Active Fault Identification",
        source_kind=DonorSourceKind.PRIMARY_PAPER,
        source_uri="https://arxiv.org/abs/2509.04708",
        access=DonorSourceAccess.ABSTRACT_ONLY,
    )
    assert seal_assimilation(_draft(donor=abstract_only)).verdict is AssimilationVerdict.CANNOT_CHECK

    # No alarm: an abstract-only donor whose mechanism declares no assumptions is
    # not guessing about anything, so it is admissible.
    assumption_free = DonorMechanism(
        mechanism_id=MECHANISM.mechanism_id,
        donor_name=MECHANISM.donor_name,
        summary=MECHANISM.summary,
        donor_authority=MECHANISM.donor_authority,
    )
    receipt = seal_assimilation(_draft(donor=abstract_only, mechanism=assumption_free))
    assert receipt.verdict is AssimilationVerdict.ADMITTED


def test_the_authority_ladder_is_ordered_and_total() -> None:
    ranks = [authority_rank(authority) for authority in AssimilationAuthority]
    assert ranks == sorted(ranks)
    assert len(set(ranks)) == len(list(AssimilationAuthority))


def test_content_hash_changes_with_the_claim() -> None:
    first = seal_assimilation(_draft())
    other = AssimilationClaim(
        orion_name="active diagnosability probe",
        target_mechanic_ids=("P1.DIAGNOSABILITY", "P1.LICENSING.v2"),
        orion_authority=AssimilationAuthority.BOUNDED,
        delta="scoped to epistemic coordinates rather than physical faults",
    )
    assert seal_assimilation(_draft(claim=other)).content_hash != first.content_hash


def test_a_receipt_without_a_target_cell_is_refused_at_construction() -> None:
    with pytest.raises(ValueError):
        AssimilationClaim(
            orion_name="active diagnosability probe",
            target_mechanic_ids=(),
            orion_authority=AssimilationAuthority.BOUNDED,
        )
