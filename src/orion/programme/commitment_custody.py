"""Commitments that must survive an attack before they count as withholding anything.

A prospective result is a result whose answer key was fixed before the run and
withheld from the system being scored. Repositories demonstrate the "fixed
before" half with a cryptographic commitment: publish ``H(secret, nonce)`` up
front, open it afterwards. The "withheld" half is assumed to follow, because a
digest is not a secret.

It does not follow. A commitment hides its secret only while the secret's domain
is large *or* the nonce is unguessable, and a benchmark label is drawn from a
domain of eight. Every protection the scheme has therefore lives in the nonce,
and a nonce is not checkable by looking at it: ``0x…01`` and a CSPRNG draw are
both 64 hex characters, both unique across a suite, both non-zero. The only
question that separates them is whether a cheap enumeration opens the digest,
and that question has to be *run*.

P5 is the live example. ``papers/paper-05-self-orion/protocol/
PROTECTED_SUITE_FREEZE_V1.md`` states the defence in as many words --- "a raw
SHA-256 of ``protected_root_cause`` would be unsafe because the label has only
eight possible values and can be enumerated. The manifest therefore commits to
``{protected_root_cause, nonce}``" --- and the suite on disk ships
``root_cause_nonce`` values that are the case ordinal in hex, ``0…01`` through
``0…018``. Running the attack the document names recovers 24 of 24 protected
root causes from the manifest that document calls safe to publish, in 108
SHA-256 evaluations. ``validate_protected_suite`` accepted those nonces: it
rejected exactly one value, the all-zero nonce, out of 2^256.

It now refuses them, along with every other shape a registered probe generates
--- counters up from zero and down from 2^256, constant padding, short
alphabets, repeated blocks, fixed placeholders, derivations of a published
field, and one salt shared across a suite. ``orion.study.p5.freeze`` owns those
generators and ``orion.study.p5.hidden_cause_custody`` builds its probes from
the same ones, so a nonce the freeze accepts is by construction one the declared
adversary cannot enumerate. That closes the scheme; it does not reopen the
shipped artifact, whose labels are published in plaintext beside the nonces and
whose sealing no re-issue can restore.

The failure class is recorded under
``research/failures/2026-08-invertible-commitment-vacuous-custody/``.

The shape is the one :mod:`orion.programme.guard_exercise` and
:mod:`orion.programme.benchmark_identifiability` already name from two other
angles. A guard's zero violations is uninterpretable without its denominator; a
benchmark's score is uninterpretable while a cue recovers the label; and a
commitment's "nothing was disclosed" is uninterpretable unless somebody tried to
disclose it. In all three the honest verdict for an unrun check is
:data:`~orion.programme.records.Outcome.CANNOT_CHECK`, which blocks exactly as
``FAIL`` does, and in all three the type refuses to pair that state with a pass.

One check here has no analogue in the other two and matters more than the rest.
An attack that could not have worked proves nothing about the target, so an
audit whose modelled scheme does not reproduce a digest the real freeze emitted
returns ``SCHEME_NOT_DEMONSTRATED`` rather than "no secret disclosed". That is
the P1 lesson --- an unreachable path counted as a comparison --- applied to the
adversary rather than to the system under test.

Scope-general on purpose. It knows nothing about root causes, P5 or SHA-256; it
takes digests, an enumerable secret domain and a scheme, and returns a typed
verdict.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from enum import Enum

from orion.programme.records import Outcome

CommitmentScheme = Callable[[str, str], str]
"""``(secret, nonce) -> digest``, as the freeze that published the manifest computes it."""


class DisclosureKind(str, Enum):
    """How an adversary obtains the nonce candidates it tries.

    Every member names a way of *not* guessing: a nonce recovered from something
    already published, from the shape of the emitting loop, or from a value the
    generator reused. None of them is cryptanalysis, which is the point --- a
    commitment defeated by any of these was never withholding its secret.
    """

    ORDINAL = "ORDINAL"
    """The secret's position in the published order, in the manifest's own encoding."""

    SMALL_INTEGER = "SMALL_INTEGER"
    """A bounded sweep over small integers, the values a counter emits."""

    CONSTANT = "CONSTANT"
    """A fixed placeholder a generator left in: all-zero, all-``a``, a template digest."""

    PUBLISHED_FIELD = "PUBLISHED_FIELD"
    """A nonce derived from a field the manifest publishes beside the commitment."""

    RECOVERED_ELSEWHERE = "RECOVERED_ELSEWHERE"
    """A nonce opened for one secret, tried against the rest --- reuse, not guessing."""


@dataclass(frozen=True)
class SealedSecret:
    """One published commitment, plus the domain its secret is known to be drawn from.

    ``domain_rationale`` is required and must be non-empty, for the reason
    ``GuardExercise.opportunity_definition`` is: an audit over a domain nobody
    can justify is not an audit. The sentence has to say why an adversary knows
    these are the only candidates --- usually because they are a registered enum
    the protocol publishes.

    ``ordinal`` is the secret's 1-based position in the manifest as published.
    It is a field rather than an enumerate() index because it is the single most
    valuable thing an adversary has, and a probe that wants it should have to
    read it from the type.
    """

    secret_id: str
    digest: str
    domain: tuple[str, ...]
    domain_rationale: str
    ordinal: int

    def __post_init__(self) -> None:
        if not self.secret_id.strip():
            raise ValueError("secret id is required")
        if not self.digest.strip():
            raise ValueError(f"{self.secret_id}: a published digest is required")
        if len(self.domain) < 2:
            raise ValueError(
                f"{self.secret_id}: a domain of fewer than two candidates is already open; "
                "a commitment to a one-value domain discloses by being published"
            )
        if len(set(self.domain)) != len(self.domain):
            raise ValueError(f"{self.secret_id}: domain candidates must be distinct")
        if any(not value.strip() for value in self.domain):
            raise ValueError(f"{self.secret_id}: domain candidates must be non-blank")
        if not self.domain_rationale.strip():
            raise ValueError(
                f"{self.secret_id}: a domain rationale is required; a commitment whose "
                "secret space cannot be stated cannot be attacked or defended"
            )
        if self.ordinal < 1:
            raise ValueError(f"{self.secret_id}: ordinal is 1-based within the published order")

    @property
    def domain_size(self) -> int:
        return len(self.domain)

    def as_json(self) -> dict[str, object]:
        return {
            "secret_id": self.secret_id,
            "digest": self.digest,
            "domain_size": self.domain_size,
            "domain_rationale": self.domain_rationale,
            "ordinal": self.ordinal,
        }


@dataclass(frozen=True)
class DisclosureProbe:
    """A declared, cheap adversary: the nonce candidates it will try, and why they are cheap.

    ``cost_rationale`` carries the same obligation as ``ShortcutProbe``'s
    ``cue_rationale``. A probe is evidence only if its budget can be argued to
    be within reach of the party the commitment is protecting against, and that
    argument is a sentence, not a number.
    """

    probe_id: str
    kind: DisclosureKind
    nonce_candidates: Callable[[SealedSecret], Iterable[str]]
    cost_rationale: str

    def __post_init__(self) -> None:
        if not self.probe_id.strip():
            raise ValueError("probe id is required")
        if not self.cost_rationale.strip():
            raise ValueError(
                f"{self.probe_id}: a cost rationale is required; an attack nobody can "
                "argue is affordable neither condemns nor clears a commitment"
            )


@dataclass(frozen=True)
class SchemeCanary:
    """One opening the auditor may legitimately perform, used to prove the attack is real.

    The audit models the publisher's scheme. If that model is wrong --- a
    different field order, a different serialisation, a missing ``kind`` tag ---
    every digest fails to match and the audit reports a commitment that was never
    attacked as one that held. The canary is a ``(secret, nonce, digest)`` triple
    the real freeze emitted, so a mismatch is reported as an unusable instrument
    rather than as a clean result.
    """

    secret: str
    nonce: str
    digest: str

    def __post_init__(self) -> None:
        for field_name in ("secret", "nonce", "digest"):
            if not str(getattr(self, field_name)).strip():
                raise ValueError(f"canary {field_name} is required")

    def reproduced_by(self, scheme: CommitmentScheme) -> bool:
        return scheme(self.secret, self.nonce) == self.digest


@dataclass(frozen=True)
class DisclosureAttempt:
    """What one probe achieved against one manifest, with the work it took.

    ``digests_computed`` is reported alongside ``disclosed`` because the pair is
    the finding. "24 of 24 recovered" is a fact about the commitment; "in 108
    SHA-256 evaluations" is the fact that makes it indefensible.
    """

    probe_id: str
    sealed: int
    disclosed: int
    digests_computed: int
    budget_digests: int
    disclosed_ids: tuple[str, ...]
    budget_exhausted: bool

    def __post_init__(self) -> None:
        counts = (self.sealed, self.disclosed, self.digests_computed, self.budget_digests)
        if any(value < 0 for value in counts):
            raise ValueError(f"{self.probe_id}: attempt counts cannot be negative")
        if self.disclosed > self.sealed:
            raise ValueError(
                f"{self.probe_id}: {self.disclosed} disclosures over {self.sealed} sealed "
                "secrets; a probe cannot open more commitments than were published"
            )
        if len(self.disclosed_ids) != self.disclosed:
            raise ValueError(
                f"{self.probe_id}: {len(self.disclosed_ids)} named ids for {self.disclosed} "
                "disclosures; a disclosure that cannot be named cannot be repaired"
            )

    @property
    def attempted(self) -> bool:
        """True when the probe actually computed something. Zero digests is not a defence."""

        return self.digests_computed > 0

    @property
    def disclosure_rate(self) -> float | None:
        """Fraction of sealed secrets opened, or ``None`` when nothing was sealed.

        ``None`` rather than ``0.0``, for the reason ``GuardExercise.violation_rate``
        is: an empty manifest and a manifest that resisted the attack are
        different facts and must not print the same character.
        """

        if self.sealed == 0:
            return None
        return self.disclosed / self.sealed

    @property
    def resolution(self) -> float | None:
        """Finest non-zero disclosure rate this many sealed secrets can express."""

        if self.sealed == 0:
            return None
        return 1.0 / self.sealed

    @property
    def digests_per_disclosure(self) -> float | None:
        if self.disclosed == 0:
            return None
        return self.digests_computed / self.disclosed

    def cost_summary(self) -> str:
        """The work, phrased for a verdict detail a reader can act on without arithmetic."""

        if self.disclosed == 0:
            return f"{self.digests_computed} digests recovered nothing"
        return f"{self.digests_computed / self.disclosed:.1f} digests per recovered secret"

    def as_json(self) -> dict[str, object]:
        return {
            "probe_id": self.probe_id,
            "sealed": self.sealed,
            "disclosed": self.disclosed,
            "digests_computed": self.digests_computed,
            "budget_digests": self.budget_digests,
            "disclosed_ids": list(self.disclosed_ids),
            "budget_exhausted": self.budget_exhausted,
            "disclosure_rate": self.disclosure_rate,
            "resolution": self.resolution,
            "digests_per_disclosure": self.digests_per_disclosure,
        }


def attempt_disclosure(
    probe: DisclosureProbe,
    secrets: Iterable[SealedSecret],
    *,
    scheme: CommitmentScheme,
    budget_digests: int = 1_000_000,
) -> DisclosureAttempt:
    """Run one probe against every sealed secret and report what opened.

    Nonces are the outer loop and domain candidates the inner one, because that
    is the order the adversary works in: one nonce guess is tested against all
    eight labels at once. Reporting the count from any other order would
    understate how few evaluations a real attack needs.
    """

    if budget_digests < 1:
        raise ValueError(f"{probe.probe_id}: a disclosure budget must allow at least one digest")

    materialised = tuple(secrets)
    computed = 0
    opened: list[str] = []
    exhausted = False
    for sealed in materialised:
        found = False
        for nonce in probe.nonce_candidates(sealed):
            for candidate in sealed.domain:
                if computed >= budget_digests:
                    exhausted = True
                    break
                computed += 1
                if scheme(candidate, nonce) == sealed.digest:
                    opened.append(sealed.secret_id)
                    found = True
                    break
            if found or exhausted:
                break
        if exhausted:
            break

    return DisclosureAttempt(
        probe_id=probe.probe_id,
        sealed=len(materialised),
        disclosed=len(opened),
        digests_computed=computed,
        budget_digests=budget_digests,
        disclosed_ids=tuple(opened),
        budget_exhausted=exhausted,
    )


class CustodyReason(str, Enum):
    """Why a custody audit came out the way it did.

    The ``is_vacuity`` members are the ones the module exists for. Each is a way
    for an audit to report zero disclosures while having established nothing,
    and each would read as "the commitment held" if the verdict were a boolean.
    """

    WITHHELD_UNDER_ENUMERATION = "WITHHELD_UNDER_ENUMERATION"
    SECRET_DISCLOSED = "SECRET_DISCLOSED"
    NO_PROBE_REGISTERED = "NO_PROBE_REGISTERED"
    NO_SEALED_SECRET = "NO_SEALED_SECRET"
    SCHEME_NOT_DEMONSTRATED = "SCHEME_NOT_DEMONSTRATED"
    NO_DIGEST_COMPUTED = "NO_DIGEST_COMPUTED"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
    CEILING_FINER_THAN_RESOLUTION = "CEILING_FINER_THAN_RESOLUTION"

    @property
    def is_vacuity(self) -> bool:
        """True for the reasons that report an unrun attack, not a surviving commitment."""

        return self in {
            CustodyReason.NO_PROBE_REGISTERED,
            CustodyReason.NO_SEALED_SECRET,
            CustodyReason.SCHEME_NOT_DEMONSTRATED,
            CustodyReason.NO_DIGEST_COMPUTED,
            CustodyReason.BUDGET_EXHAUSTED,
            CustodyReason.CEILING_FINER_THAN_RESOLUTION,
        }


@dataclass(frozen=True)
class CustodyAudit:
    """A three-valued verdict on whether a published commitment withheld its secret."""

    custody_id: str
    outcome: Outcome
    reason: CustodyReason
    detail: str
    attempts: tuple[DisclosureAttempt, ...]

    def __post_init__(self) -> None:
        if not self.custody_id.strip():
            raise ValueError("custody id is required")
        if self.outcome is Outcome.PASS and self.reason.is_vacuity:
            raise ValueError(
                f"{self.custody_id}: {self.reason.value} cannot yield PASS; an attack that "
                "was not run is not an attack that failed"
            )
        if self.outcome is Outcome.PASS and not self.attempts:
            raise ValueError(
                f"{self.custody_id}: a passing custody audit must carry the attempts it survived"
            )

    @property
    def blocks(self) -> bool:
        return self.outcome.blocks

    @property
    def worst_disclosure_rate(self) -> float | None:
        rates = [item.disclosure_rate for item in self.attempts if item.disclosure_rate is not None]
        return max(rates) if rates else None

    def as_json(self) -> dict[str, object]:
        return {
            "custody_id": self.custody_id,
            "outcome": self.outcome.value,
            "reason": self.reason.value,
            "detail": self.detail,
            "worst_disclosure_rate": self.worst_disclosure_rate,
            "attempts": [item.as_json() for item in self.attempts],
        }


def audit_commitment_custody(
    *,
    custody_id: str,
    secrets: Iterable[SealedSecret],
    probes: Iterable[DisclosureProbe],
    scheme: CommitmentScheme,
    canary: SchemeCanary,
    budget_digests: int = 1_000_000,
    max_disclosure_rate: float = 0.0,
) -> CustodyAudit:
    """Audit whether every declared cheap attack fails to open the published commitments.

    ``max_disclosure_rate`` defaults to 0.0 --- not one secret may be recovered
    --- which is the only defensible ceiling for an answer key. A ceiling
    strictly between 0 and ``1/len(secrets)`` returns ``CANNOT_CHECK`` for the
    reason ``assess_guard`` does: every observable outcome would either satisfy
    it trivially or overshoot it by a whole secret.
    """

    if not 0.0 <= max_disclosure_rate <= 1.0:
        raise ValueError(f"{custody_id}: a disclosure ceiling must lie in [0, 1]")

    registered = tuple(probes)
    if not registered:
        return CustodyAudit(
            custody_id=custody_id,
            outcome=Outcome.CANNOT_CHECK,
            reason=CustodyReason.NO_PROBE_REGISTERED,
            detail=(
                f"{custody_id}: no disclosure probe was registered; a commitment nobody "
                "attacked reports no disclosure because nobody looked"
            ),
            attempts=(),
        )

    materialised = tuple(secrets)
    if not materialised:
        return CustodyAudit(
            custody_id=custody_id,
            outcome=Outcome.CANNOT_CHECK,
            reason=CustodyReason.NO_SEALED_SECRET,
            detail=(
                f"{custody_id}: no sealed secret was supplied; zero disclosures out of zero "
                "commitments is an absent measurement, not custody that held"
            ),
            attempts=(),
        )

    if not canary.reproduced_by(scheme):
        # Before the result is read as "the attack failed", the attack has to have
        # been capable of succeeding. A modelled scheme that cannot reproduce a
        # digest the real freeze emitted fails every comparison for a reason that
        # has nothing to do with the nonce.
        return CustodyAudit(
            custody_id=custody_id,
            outcome=Outcome.CANNOT_CHECK,
            reason=CustodyReason.SCHEME_NOT_DEMONSTRATED,
            detail=(
                f"{custody_id}: the modelled commitment scheme does not reproduce the canary "
                f"digest for secret {canary.secret!r}; every probe would report zero "
                "disclosures because the instrument is wrong, not because the nonce is strong"
            ),
            attempts=(),
        )

    attempts = tuple(
        attempt_disclosure(probe, materialised, scheme=scheme, budget_digests=budget_digests)
        for probe in registered
    )

    idle = [item.probe_id for item in attempts if not item.attempted]
    if idle:
        return CustodyAudit(
            custody_id=custody_id,
            outcome=Outcome.CANNOT_CHECK,
            reason=CustodyReason.NO_DIGEST_COMPUTED,
            detail=(
                f"{custody_id}: {', '.join(sorted(idle))} produced no nonce candidate and so "
                "computed no digest; a probe that never ran contributes a silent zero to the "
                "roll-up"
            ),
            attempts=attempts,
        )

    resolution = min(
        item.resolution for item in attempts if item.resolution is not None
    )
    if 0.0 < max_disclosure_rate < resolution:
        return CustodyAudit(
            custody_id=custody_id,
            outcome=Outcome.CANNOT_CHECK,
            reason=CustodyReason.CEILING_FINER_THAN_RESOLUTION,
            detail=(
                f"{custody_id}: a ceiling of {max_disclosure_rate} is finer than the "
                f"{resolution} resolution of {len(materialised)} sealed secrets; satisfying "
                "it is not distinguishable from opening none"
            ),
            attempts=attempts,
        )

    leaking = [
        item
        for item in attempts
        if item.disclosure_rate is not None and item.disclosure_rate > max_disclosure_rate
    ]
    if leaking:
        # FAIL is decided before BUDGET_EXHAUSTED: a secret recovered inside the
        # budget is recovered whatever some other probe ran out of.
        worst = max(leaking, key=lambda item: item.disclosure_rate or 0.0)
        return CustodyAudit(
            custody_id=custody_id,
            outcome=Outcome.FAIL,
            reason=CustodyReason.SECRET_DISCLOSED,
            detail=(
                f"{custody_id}: probe {worst.probe_id} opened {worst.disclosed} of "
                f"{worst.sealed} published commitments in {worst.digests_computed} digest "
                f"evaluations ({worst.cost_summary()})"
            ),
            attempts=attempts,
        )

    starved = [item.probe_id for item in attempts if item.budget_exhausted]
    if starved:
        return CustodyAudit(
            custody_id=custody_id,
            outcome=Outcome.CANNOT_CHECK,
            reason=CustodyReason.BUDGET_EXHAUSTED,
            detail=(
                f"{custody_id}: {', '.join(sorted(starved))} hit the {budget_digests}-digest "
                "budget before finishing; an attack that ran out of money did not establish "
                "that the commitment holds"
            ),
            attempts=attempts,
        )

    # The work is part of the verdict. A pass that does not say what it cost is
    # indistinguishable from a probe set that stopped looking, which is the
    # failure the whole module exists to make unreportable --- so the digests
    # spent are stated here, in the same sentence as the zero.
    spent = sum(item.digests_computed for item in attempts)
    return CustodyAudit(
        custody_id=custody_id,
        outcome=Outcome.PASS,
        reason=CustodyReason.WITHHELD_UNDER_ENUMERATION,
        detail=(
            f"{custody_id}: {len(attempts)} probes opened 0 of {len(materialised)} published "
            f"commitments in {spent} digest evaluations, none exhausting the "
            f"{budget_digests}-digest budget"
        ),
        attempts=attempts,
    )


def require_withheld(audit: CustodyAudit) -> None:
    """Raise unless ``audit`` passed. One line, before a result is called prospective."""

    if audit.blocks:
        raise ValueError(
            f"{audit.custody_id}: {audit.outcome.value} ({audit.reason.value}) --- {audit.detail}"
        )


@dataclass(frozen=True)
class ProspectiveScore:
    """A score against a protected answer key, which cannot exist unless the key was withheld.

    "Prospective" is a claim about custody, not about chronology. A key fixed
    before the run and recoverable from what was published is not a key the
    system was scored without, and no timestamp repairs that. This class refuses
    to hold such a number, so reporting one requires deleting the type rather
    than forgetting a check --- the same refusal ``AuditedScore`` makes about a
    leaking benchmark.
    """

    score_name: str
    value: float
    audit: CustodyAudit

    def __post_init__(self) -> None:
        if not self.score_name.strip():
            raise ValueError("score name is required")
        if self.audit.blocks:
            raise ValueError(
                f"{self.score_name}: custody audit for {self.audit.custody_id} returned "
                f"{self.audit.outcome.value} ({self.audit.reason.value}); {self.audit.detail}"
            )

    def as_json(self) -> dict[str, object]:
        return {
            "score_name": self.score_name,
            "value": self.value,
            "audit": self.audit.as_json(),
        }


__all__ = [
    "CommitmentScheme",
    "CustodyAudit",
    "CustodyReason",
    "DisclosureAttempt",
    "DisclosureKind",
    "DisclosureProbe",
    "ProspectiveScore",
    "SchemeCanary",
    "SealedSecret",
    "attempt_disclosure",
    "audit_commitment_custody",
    "require_withheld",
]
