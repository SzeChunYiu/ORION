"""`MechanismAssimilationReceipt.v1` — absorb donor work without stealing novelty (#318).

A disposition says *what we decided about a work*. An assimilation receipt says
*what we took, from which exact artifact, what came with it, and what we did not
silently drop*. `research/novelty/self-application/` already records the former;
this records the latter, which is what #318 asks for.

An assimilation ledger without hostile checks is a bibliography with verbs. Four
failure modes make absorption look like invention, and each is checked here
rather than left to review:

**Rebranding** — a donor mechanism renamed and claimed. Caught by requiring a
stated delta whenever ORION's name differs from the donor's.

**Lost assumptions** — a mechanism adopted outside the regime where it was
validated. Caught by requiring every donor assumption to be explicitly
`PRESERVED`, `RELAXED` or `DROPPED`, with a justification for the latter two.

**Authority escalation** — a donor's bounded claim arriving unbounded. Caught by
ordering the authority ladder and refusing any receipt that climbs it.

**Fake composition** — asserting two absorbed mechanisms compose without showing
it. Caught by requiring evidence references whenever `composed_with` is non-empty.

Everything fails closed. A receipt whose donor source cannot be reached is
`CANNOT_CHECK`, never `ADMITTED`; a receipt with any hostile finding is `BLOCKED`.
No receipt grants authority, and none is self-authorizing: admission means the
absorption was recorded honestly, not that ORION may now claim the mechanism.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from orion.knowledge.nearest_work import AbsorptionDisposition
from orion.novelty.hashing import sha256_canonical

SCHEMA_ID = "orion.mechanism-assimilation-receipt.v1"


class DonorSourceKind(str, Enum):
    """What the mechanism was read from.

    `SECONDARY` exists so a receipt can *record* that it was built from a survey
    or a blog post rather than pretend it was not. It never admits: #318 requires
    primary-paper or official-code identities, and a source that only describes
    the mechanism cannot settle what its assumptions were.
    """

    PRIMARY_PAPER = "PRIMARY_PAPER"
    OFFICIAL_CODE = "OFFICIAL_CODE"
    SECONDARY = "SECONDARY"


class DonorSourceAccess(str, Enum):
    FULL_TEXT = "FULL_TEXT"
    ABSTRACT_ONLY = "ABSTRACT_ONLY"
    UNREACHABLE = "UNREACHABLE"


class AssumptionStatus(str, Enum):
    PRESERVED = "PRESERVED"
    RELAXED = "RELAXED"
    DROPPED = "DROPPED"


class AssimilationAuthority(str, Enum):
    """How strongly a mechanism's result may be claimed.

    Ordered. `authority_rank` is the only place the order lives, so a later
    addition cannot silently change what counts as escalation.
    """

    NONE = "NONE"
    DESCRIPTIVE = "DESCRIPTIVE"
    BOUNDED = "BOUNDED"
    GENERAL = "GENERAL"


AUTHORITY_ORDER: tuple[AssimilationAuthority, ...] = (
    AssimilationAuthority.NONE,
    AssimilationAuthority.DESCRIPTIVE,
    AssimilationAuthority.BOUNDED,
    AssimilationAuthority.GENERAL,
)


def authority_rank(authority: AssimilationAuthority) -> int:
    return AUTHORITY_ORDER.index(AssimilationAuthority(authority))


class HostileFindingKind(str, Enum):
    REBRANDING = "REBRANDING"
    LOST_ASSUMPTIONS = "LOST_ASSUMPTIONS"
    AUTHORITY_ESCALATION = "AUTHORITY_ESCALATION"
    FAKE_COMPOSITION = "FAKE_COMPOSITION"
    UNGROUNDED_SOURCE = "UNGROUNDED_SOURCE"


class AssimilationVerdict(str, Enum):
    ADMITTED = "ADMITTED"
    BLOCKED = "BLOCKED"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class DonorIdentity:
    """The exact artifact the mechanism was read from."""

    donor_id: str
    title: str
    source_kind: DonorSourceKind
    source_uri: str
    access: DonorSourceAccess

    def __post_init__(self) -> None:
        if not self.donor_id.strip() or not self.title.strip():
            raise ValueError("donor identity requires an id and a title")
        if not self.source_uri.strip():
            raise ValueError("donor identity requires a source uri")
        object.__setattr__(self, "source_kind", DonorSourceKind(self.source_kind))
        object.__setattr__(self, "access", DonorSourceAccess(self.access))


@dataclass(frozen=True)
class DonorAssumption:
    """A condition the donor's mechanism was validated under."""

    assumption_id: str
    text: str
    status: AssumptionStatus
    justification: str = ""

    def __post_init__(self) -> None:
        if not self.assumption_id.strip() or not self.text.strip():
            raise ValueError("donor assumption requires an id and text")
        object.__setattr__(self, "status", AssumptionStatus(self.status))


@dataclass(frozen=True)
class DonorMechanism:
    """The atomic donor cell, named as the donor names it."""

    mechanism_id: str
    donor_name: str
    summary: str
    donor_authority: AssimilationAuthority
    assumptions: tuple[DonorAssumption, ...] = ()

    def __post_init__(self) -> None:
        if not self.mechanism_id.strip() or not self.donor_name.strip():
            raise ValueError("donor mechanism requires an id and the donor's own name for it")
        if not self.summary.strip():
            raise ValueError("donor mechanism requires a summary")
        object.__setattr__(self, "donor_authority", AssimilationAuthority(self.donor_authority))


@dataclass(frozen=True)
class AssimilationClaim:
    """What ORION calls the mechanism, and what ORION added to it."""

    orion_name: str
    target_mechanic_ids: tuple[str, ...]
    orion_authority: AssimilationAuthority
    delta: str = ""
    composed_with: tuple[str, ...] = ()
    composition_evidence: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.orion_name.strip():
            raise ValueError("assimilation claim requires an ORION-side name")
        if not self.target_mechanic_ids:
            raise ValueError("assimilation claim requires at least one target mechanic cell")
        object.__setattr__(self, "orion_authority", AssimilationAuthority(self.orion_authority))


@dataclass(frozen=True)
class HostileFinding:
    kind: HostileFindingKind
    detail: str

    def __post_init__(self) -> None:
        if not self.detail.strip():
            raise ValueError("a hostile finding must say what it found")
        object.__setattr__(self, "kind", HostileFindingKind(self.kind))


@dataclass(frozen=True)
class AssimilationDraft:
    receipt_id: str
    donor: DonorIdentity
    mechanism: DonorMechanism
    disposition: AbsorptionDisposition
    claim: AssimilationClaim
    not_taken: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.receipt_id.strip():
            raise ValueError("receipt requires an id")
        object.__setattr__(self, "disposition", AbsorptionDisposition(self.disposition))


@dataclass(frozen=True)
class MechanismAssimilationReceipt:
    schema_id: str
    receipt_id: str
    donor: DonorIdentity
    mechanism: DonorMechanism
    disposition: AbsorptionDisposition
    claim: AssimilationClaim
    not_taken: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    hostile_findings: tuple[HostileFinding, ...]
    verdict: AssimilationVerdict
    verdict_reasons: tuple[str, ...]
    content_hash: str = field(default="")

    @property
    def grants_authority(self) -> str:
        """Always `NONE`. Admission records an honest absorption, nothing more."""

        return "NONE"

    @property
    def self_authorizing(self) -> bool:
        return False


def _rebranding(draft: AssimilationDraft) -> HostileFinding | None:
    """A different name with no stated difference is a rename, not a contribution."""

    donor_name = draft.mechanism.donor_name.strip().casefold()
    orion_name = draft.claim.orion_name.strip().casefold()
    if donor_name == orion_name:
        return None
    if draft.claim.delta.strip():
        return None
    return HostileFinding(
        HostileFindingKind.REBRANDING,
        f"renamed {draft.mechanism.donor_name!r} to {draft.claim.orion_name!r} with no stated delta",
    )


def _lost_assumptions(draft: AssimilationDraft) -> HostileFinding | None:
    """Relaxing or dropping a donor's assumption is a claim, so it needs a reason."""

    unjustified = [
        assumption.assumption_id
        for assumption in draft.mechanism.assumptions
        if assumption.status is not AssumptionStatus.PRESERVED and not assumption.justification.strip()
    ]
    if not unjustified:
        return None
    return HostileFinding(
        HostileFindingKind.LOST_ASSUMPTIONS,
        "assumptions relaxed or dropped without justification: " + ", ".join(sorted(unjustified)),
    )


def _authority_escalation(draft: AssimilationDraft) -> HostileFinding | None:
    """A mechanism cannot become more authoritative by being absorbed."""

    donor = draft.mechanism.donor_authority
    orion = draft.claim.orion_authority
    if authority_rank(orion) <= authority_rank(donor):
        return None
    return HostileFinding(
        HostileFindingKind.AUTHORITY_ESCALATION,
        f"donor claims {donor.value}; ORION claims {orion.value}",
    )


def _fake_composition(draft: AssimilationDraft) -> HostileFinding | None:
    """Asserting that two mechanisms compose is a result, not a note."""

    if not draft.claim.composed_with:
        return None
    if draft.claim.composition_evidence:
        return None
    return HostileFinding(
        HostileFindingKind.FAKE_COMPOSITION,
        "composed_with declares " + ", ".join(draft.claim.composed_with) + " with no composition evidence",
    )


def _ungrounded_source(draft: AssimilationDraft) -> HostileFinding | None:
    if draft.donor.source_kind is not DonorSourceKind.SECONDARY:
        return None
    return HostileFinding(
        HostileFindingKind.UNGROUNDED_SOURCE,
        f"donor {draft.donor.donor_id} is a secondary source; #318 requires a primary paper or official code",
    )


HOSTILE_CHECKS = (
    _ungrounded_source,
    _rebranding,
    _lost_assumptions,
    _authority_escalation,
    _fake_composition,
)


def assess_assimilation(draft: AssimilationDraft) -> tuple[HostileFinding, ...]:
    """Every hostile finding, in a stable order. Empty means none fired."""

    findings = [check(draft) for check in HOSTILE_CHECKS]
    return tuple(finding for finding in findings if finding is not None)


def seal_assimilation(draft: AssimilationDraft) -> MechanismAssimilationReceipt:
    """Turn a draft into a content-addressed receipt with its verdict computed.

    Order matters, and the stronger refusal wins. A hostile finding is a definite
    defect in the receipt's own internal consistency -- a rename with no delta, a
    climb up the authority ladder -- and every check is computable without reading
    the donor. So findings block even when the source is unreachable; letting
    `CANNOT_CHECK` mask them would report a definite defect as an open question,
    and an open question invites a later retry that quietly succeeds.

    An unreachable donor with no findings is still `CANNOT_CHECK`: the checks that
    matter most cannot be evaluated *against the donor*, and calling that
    `ADMITTED` would convert *could not check* into *checked and clean*.
    """

    findings = assess_assimilation(draft)
    reasons: list[str] = []
    if findings:
        verdict = AssimilationVerdict.BLOCKED
        reasons.extend(f"{finding.kind.value}: {finding.detail}" for finding in findings)
        if draft.donor.access is DonorSourceAccess.UNREACHABLE:
            reasons.append("donor source is also unreachable; the block stands on the findings above")
    elif draft.donor.access is DonorSourceAccess.UNREACHABLE:
        verdict = AssimilationVerdict.CANNOT_CHECK
        reasons.append("donor source unreachable; assumptions and authority cannot be checked against it")
    elif draft.donor.access is DonorSourceAccess.ABSTRACT_ONLY and draft.mechanism.assumptions:
        verdict = AssimilationVerdict.CANNOT_CHECK
        reasons.append(
            "assumptions are declared from an abstract-only read; a full text is required to "
            "confirm the donor's validated regime"
        )
    else:
        verdict = AssimilationVerdict.ADMITTED
        reasons.append("no hostile finding; donor source is primary and readable")

    receipt = MechanismAssimilationReceipt(
        schema_id=SCHEMA_ID,
        receipt_id=draft.receipt_id,
        donor=draft.donor,
        mechanism=draft.mechanism,
        disposition=draft.disposition,
        claim=draft.claim,
        not_taken=draft.not_taken,
        evidence_refs=draft.evidence_refs,
        hostile_findings=findings,
        verdict=verdict,
        verdict_reasons=tuple(reasons),
    )
    return MechanismAssimilationReceipt(
        **{**receipt.__dict__, "content_hash": sha256_canonical(receipt)}
    )
