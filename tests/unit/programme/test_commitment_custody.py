"""Every way a commitment audit can report nothing must block, not pass."""

from __future__ import annotations

import hashlib

import pytest

from orion.programme.commitment_custody import (
    CustodyAudit,
    CustodyReason,
    DisclosureAttempt,
    DisclosureKind,
    DisclosureProbe,
    ProspectiveScore,
    SchemeCanary,
    SealedSecret,
    attempt_disclosure,
    audit_commitment_custody,
    require_withheld,
)
from orion.programme.records import Outcome

DOMAIN = ("ALPHA", "BETA", "GAMMA", "DELTA")
RATIONALE = "the four registered families the protocol publishes"


def scheme(secret: str, nonce: str) -> str:
    return hashlib.sha256(f"{secret}|{nonce}".encode()).hexdigest()


CANARY = SchemeCanary(secret="ALPHA", nonce="canary-nonce", digest=scheme("ALPHA", "canary-nonce"))


def sealed(secret: str, nonce: str, *, ordinal: int) -> SealedSecret:
    return SealedSecret(
        secret_id=f"case-{ordinal:03d}",
        digest=scheme(secret, nonce),
        domain=DOMAIN,
        domain_rationale=RATIONALE,
        ordinal=ordinal,
    )


def ordinal_probe() -> DisclosureProbe:
    return DisclosureProbe(
        probe_id="ordinal-nonce",
        kind=DisclosureKind.ORDINAL,
        nonce_candidates=lambda item: (str(item.ordinal),),
        cost_rationale="one guess that the nonce is the publication position",
    )


def silent_probe() -> DisclosureProbe:
    return DisclosureProbe(
        probe_id="silent",
        kind=DisclosureKind.CONSTANT,
        nonce_candidates=lambda item: (),
        cost_rationale="a probe that yields no candidate, to pin that zero work blocks",
    )


class TestSealedSecret:
    def test_requires_an_enumerable_domain_of_at_least_two(self) -> None:
        with pytest.raises(ValueError, match="already open"):
            SealedSecret(
                secret_id="c1",
                digest="d",
                domain=("ONLY",),
                domain_rationale=RATIONALE,
                ordinal=1,
            )

    def test_requires_a_domain_rationale(self) -> None:
        with pytest.raises(ValueError, match="domain rationale is required"):
            SealedSecret(
                secret_id="c1", digest="d", domain=DOMAIN, domain_rationale="  ", ordinal=1
            )

    def test_rejects_duplicate_domain_candidates(self) -> None:
        with pytest.raises(ValueError, match="must be distinct"):
            SealedSecret(
                secret_id="c1",
                digest="d",
                domain=("ALPHA", "ALPHA"),
                domain_rationale=RATIONALE,
                ordinal=1,
            )

    def test_rejects_blank_identity_and_digest(self) -> None:
        with pytest.raises(ValueError, match="secret id is required"):
            SealedSecret(
                secret_id=" ", digest="d", domain=DOMAIN, domain_rationale=RATIONALE, ordinal=1
            )
        with pytest.raises(ValueError, match="published digest is required"):
            SealedSecret(
                secret_id="c1", digest=" ", domain=DOMAIN, domain_rationale=RATIONALE, ordinal=1
            )

    def test_ordinal_is_one_based(self) -> None:
        with pytest.raises(ValueError, match="1-based"):
            SealedSecret(
                secret_id="c1", digest="d", domain=DOMAIN, domain_rationale=RATIONALE, ordinal=0
            )

    def test_domain_size_is_reported(self) -> None:
        item = sealed("ALPHA", "n", ordinal=1)
        assert item.domain_size == 4
        assert item.as_json()["domain_size"] == 4


class TestDisclosureProbe:
    def test_requires_a_cost_rationale(self) -> None:
        with pytest.raises(ValueError, match="cost rationale is required"):
            DisclosureProbe(
                probe_id="p",
                kind=DisclosureKind.ORDINAL,
                nonce_candidates=lambda item: (),
                cost_rationale="",
            )

    def test_requires_an_identity(self) -> None:
        with pytest.raises(ValueError, match="probe id is required"):
            DisclosureProbe(
                probe_id=" ",
                kind=DisclosureKind.ORDINAL,
                nonce_candidates=lambda item: (),
                cost_rationale="x",
            )


class TestSchemeCanary:
    def test_reproduced_by_the_real_scheme(self) -> None:
        assert CANARY.reproduced_by(scheme)

    def test_not_reproduced_by_a_drifted_scheme(self) -> None:
        assert not CANARY.reproduced_by(lambda s, n: hashlib.sha256(n.encode()).hexdigest())

    def test_requires_every_field(self) -> None:
        with pytest.raises(ValueError, match="canary nonce is required"):
            SchemeCanary(secret="ALPHA", nonce="", digest="d")


class TestAttemptDisclosure:
    def test_opens_every_commitment_whose_nonce_is_guessed(self) -> None:
        secrets = [sealed("GAMMA", str(index), ordinal=index) for index in range(1, 5)]
        attempt = attempt_disclosure(ordinal_probe(), secrets, scheme=scheme)
        assert attempt.disclosed == 4
        assert attempt.disclosed_ids == tuple(item.secret_id for item in secrets)
        assert attempt.disclosure_rate == 1.0
        assert not attempt.budget_exhausted

    def test_counts_digests_with_nonces_outermost(self) -> None:
        # GAMMA is the third of four domain candidates, so one nonce guess costs
        # three evaluations per secret. Any other loop order would understate the
        # cost of a real attack, which is the number the finding rests on.
        secrets = [sealed("GAMMA", str(index), ordinal=index) for index in range(1, 4)]
        attempt = attempt_disclosure(ordinal_probe(), secrets, scheme=scheme)
        assert attempt.digests_computed == 9
        assert attempt.digests_per_disclosure == 3.0
        assert attempt.cost_summary() == "3.0 digests per recovered secret"

    def test_opens_nothing_when_the_nonce_is_unguessed(self) -> None:
        secrets = [sealed("ALPHA", "8f3c-unguessable", ordinal=1)]
        attempt = attempt_disclosure(ordinal_probe(), secrets, scheme=scheme)
        assert attempt.disclosed == 0
        assert attempt.disclosure_rate == 0.0
        assert attempt.digests_per_disclosure is None
        assert attempt.cost_summary() == "4 digests recovered nothing"

    def test_marks_an_attack_that_ran_out_of_budget(self) -> None:
        secrets = [sealed("DELTA", str(index), ordinal=index) for index in range(1, 6)]
        attempt = attempt_disclosure(ordinal_probe(), secrets, scheme=scheme, budget_digests=6)
        assert attempt.budget_exhausted
        assert attempt.digests_computed == 6

    def test_rejects_a_budget_that_allows_no_work(self) -> None:
        with pytest.raises(ValueError, match="at least one digest"):
            attempt_disclosure(ordinal_probe(), [], scheme=scheme, budget_digests=0)

    def test_rate_is_none_rather_than_zero_when_nothing_was_sealed(self) -> None:
        attempt = attempt_disclosure(ordinal_probe(), [], scheme=scheme)
        assert attempt.sealed == 0
        assert attempt.disclosure_rate is None
        assert attempt.resolution is None
        assert not attempt.attempted


class TestDisclosureAttemptValidation:
    def test_cannot_open_more_than_was_sealed(self) -> None:
        with pytest.raises(ValueError, match="cannot open more commitments"):
            DisclosureAttempt(
                probe_id="p",
                sealed=1,
                disclosed=2,
                digests_computed=1,
                budget_digests=10,
                disclosed_ids=("a", "b"),
                budget_exhausted=False,
            )

    def test_every_disclosure_must_be_named(self) -> None:
        with pytest.raises(ValueError, match="cannot be named"):
            DisclosureAttempt(
                probe_id="p",
                sealed=2,
                disclosed=2,
                digests_computed=1,
                budget_digests=10,
                disclosed_ids=("a",),
                budget_exhausted=False,
            )

    def test_counts_cannot_be_negative(self) -> None:
        with pytest.raises(ValueError, match="cannot be negative"):
            DisclosureAttempt(
                probe_id="p",
                sealed=-1,
                disclosed=0,
                digests_computed=0,
                budget_digests=10,
                disclosed_ids=(),
                budget_exhausted=False,
            )


class TestAuditVerdicts:
    def test_disclosed_secret_fails_and_names_the_probe(self) -> None:
        secrets = [sealed("BETA", str(index), ordinal=index) for index in range(1, 25)]
        audit = audit_commitment_custody(
            custody_id="suite",
            secrets=secrets,
            probes=(ordinal_probe(),),
            scheme=scheme,
            canary=CANARY,
        )
        assert audit.outcome is Outcome.FAIL
        assert audit.reason is CustodyReason.SECRET_DISCLOSED
        assert "ordinal-nonce opened 24 of 24" in audit.detail
        assert audit.worst_disclosure_rate == 1.0
        assert audit.blocks

    def test_withheld_commitment_passes(self) -> None:
        secrets = [
            sealed("BETA", f"{index}-1f9c4a2b-unguessable", ordinal=index) for index in range(1, 5)
        ]
        audit = audit_commitment_custody(
            custody_id="suite",
            secrets=secrets,
            probes=(ordinal_probe(),),
            scheme=scheme,
            canary=CANARY,
        )
        assert audit.outcome is Outcome.PASS
        assert audit.reason is CustodyReason.WITHHELD_UNDER_ENUMERATION
        assert not audit.blocks

    def test_no_probe_registered_blocks(self) -> None:
        audit = audit_commitment_custody(
            custody_id="suite",
            secrets=[sealed("ALPHA", "n", ordinal=1)],
            probes=(),
            scheme=scheme,
            canary=CANARY,
        )
        assert audit.outcome is Outcome.CANNOT_CHECK
        assert audit.reason is CustodyReason.NO_PROBE_REGISTERED

    def test_no_sealed_secret_blocks(self) -> None:
        audit = audit_commitment_custody(
            custody_id="suite",
            secrets=(),
            probes=(ordinal_probe(),),
            scheme=scheme,
            canary=CANARY,
        )
        assert audit.outcome is Outcome.CANNOT_CHECK
        assert audit.reason is CustodyReason.NO_SEALED_SECRET

    def test_a_scheme_that_cannot_reproduce_the_canary_blocks(self) -> None:
        # The whole failure mode this guards: a wrong scheme model opens nothing
        # and would otherwise be reported as a commitment that held.
        def drifted(secret: str, nonce: str) -> str:
            return hashlib.sha256(f"{nonce}|{secret}".encode()).hexdigest()

        audit = audit_commitment_custody(
            custody_id="suite",
            secrets=[sealed("ALPHA", "1", ordinal=1)],
            probes=(ordinal_probe(),),
            scheme=drifted,
            canary=CANARY,
        )
        assert audit.outcome is Outcome.CANNOT_CHECK
        assert audit.reason is CustodyReason.SCHEME_NOT_DEMONSTRATED
        assert audit.attempts == ()

    def test_a_probe_that_computed_no_digest_blocks(self) -> None:
        audit = audit_commitment_custody(
            custody_id="suite",
            secrets=[sealed("ALPHA", "1", ordinal=1)],
            probes=(silent_probe(),),
            scheme=scheme,
            canary=CANARY,
        )
        assert audit.outcome is Outcome.CANNOT_CHECK
        assert audit.reason is CustodyReason.NO_DIGEST_COMPUTED
        assert "silent" in audit.detail

    def test_one_silent_probe_blocks_even_beside_a_working_one(self) -> None:
        audit = audit_commitment_custody(
            custody_id="suite",
            secrets=[sealed("ALPHA", "unguessable", ordinal=1)],
            probes=(ordinal_probe(), silent_probe()),
            scheme=scheme,
            canary=CANARY,
        )
        assert audit.outcome is Outcome.CANNOT_CHECK
        assert audit.reason is CustodyReason.NO_DIGEST_COMPUTED

    def test_budget_exhaustion_blocks_rather_than_clears(self) -> None:
        secrets = [sealed("DELTA", "unguessable", ordinal=index) for index in range(1, 5)]
        audit = audit_commitment_custody(
            custody_id="suite",
            secrets=secrets,
            probes=(ordinal_probe(),),
            scheme=scheme,
            canary=CANARY,
            budget_digests=5,
        )
        assert audit.outcome is Outcome.CANNOT_CHECK
        assert audit.reason is CustodyReason.BUDGET_EXHAUSTED

    def test_a_disclosure_inside_budget_outranks_another_probes_exhaustion(self) -> None:
        # A recovered secret is recovered whatever some other attack ran out of.
        secrets = [sealed("ALPHA", str(index), ordinal=index) for index in range(1, 4)]
        greedy = DisclosureProbe(
            probe_id="greedy",
            kind=DisclosureKind.SMALL_INTEGER,
            nonce_candidates=lambda item: tuple(str(value) for value in range(10_000)),
            cost_rationale="an unbounded sweep, to force exhaustion beside a real disclosure",
        )
        audit = audit_commitment_custody(
            custody_id="suite",
            secrets=secrets,
            probes=(ordinal_probe(), greedy),
            scheme=scheme,
            canary=CANARY,
            budget_digests=20,
        )
        assert audit.outcome is Outcome.FAIL
        assert audit.reason is CustodyReason.SECRET_DISCLOSED

    def test_a_ceiling_finer_than_the_manifest_can_express_blocks(self) -> None:
        secrets = [sealed("ALPHA", "unguessable", ordinal=index) for index in range(1, 5)]
        audit = audit_commitment_custody(
            custody_id="suite",
            secrets=secrets,
            probes=(ordinal_probe(),),
            scheme=scheme,
            canary=CANARY,
            max_disclosure_rate=0.1,
        )
        assert audit.outcome is Outcome.CANNOT_CHECK
        assert audit.reason is CustodyReason.CEILING_FINER_THAN_RESOLUTION

    def test_ceiling_must_be_a_rate(self) -> None:
        with pytest.raises(ValueError, match=r"lie in \[0, 1\]"):
            audit_commitment_custody(
                custody_id="suite",
                secrets=[sealed("ALPHA", "1", ordinal=1)],
                probes=(ordinal_probe(),),
                scheme=scheme,
                canary=CANARY,
                max_disclosure_rate=1.5,
            )


class TestCustodyAuditType:
    @pytest.mark.parametrize(
        "reason", [item for item in CustodyReason if item.is_vacuity]
    )
    def test_no_vacuity_reason_can_be_paired_with_pass(self, reason: CustodyReason) -> None:
        with pytest.raises(ValueError, match="cannot yield PASS"):
            CustodyAudit(
                custody_id="suite",
                outcome=Outcome.PASS,
                reason=reason,
                detail="",
                attempts=(),
            )

    def test_the_two_verdict_reasons_are_not_vacuity(self) -> None:
        assert not CustodyReason.WITHHELD_UNDER_ENUMERATION.is_vacuity
        assert not CustodyReason.SECRET_DISCLOSED.is_vacuity

    def test_a_passing_audit_must_carry_its_attempts(self) -> None:
        with pytest.raises(ValueError, match="must carry the attempts"):
            CustodyAudit(
                custody_id="suite",
                outcome=Outcome.PASS,
                reason=CustodyReason.WITHHELD_UNDER_ENUMERATION,
                detail="",
                attempts=(),
            )

    def test_cannot_check_blocks_exactly_as_fail_does(self) -> None:
        assert Outcome.CANNOT_CHECK.blocks
        assert Outcome.FAIL.blocks
        assert not Outcome.PASS.blocks

    def test_requires_an_identity(self) -> None:
        with pytest.raises(ValueError, match="custody id is required"):
            CustodyAudit(
                custody_id=" ",
                outcome=Outcome.FAIL,
                reason=CustodyReason.SECRET_DISCLOSED,
                detail="",
                attempts=(),
            )


class TestProspectiveScore:
    def _blocking(self) -> CustodyAudit:
        return audit_commitment_custody(
            custody_id="suite",
            secrets=[sealed("BETA", "1", ordinal=1)],
            probes=(ordinal_probe(),),
            scheme=scheme,
            canary=CANARY,
        )

    def _passing(self) -> CustodyAudit:
        return audit_commitment_custody(
            custody_id="suite",
            secrets=[sealed("BETA", "unguessable-9c1", ordinal=1)],
            probes=(ordinal_probe(),),
            scheme=scheme,
            canary=CANARY,
        )

    def test_refuses_to_hold_a_score_whose_key_was_disclosed(self) -> None:
        with pytest.raises(ValueError, match="custody audit for suite returned FAIL"):
            ProspectiveScore(score_name="attribution_accuracy", value=0.875, audit=self._blocking())

    def test_holds_a_score_whose_key_survived(self) -> None:
        score = ProspectiveScore(
            score_name="attribution_accuracy", value=0.875, audit=self._passing()
        )
        assert score.as_json()["value"] == 0.875

    def test_requires_a_score_name(self) -> None:
        with pytest.raises(ValueError, match="score name is required"):
            ProspectiveScore(score_name="", value=0.0, audit=self._passing())


class TestRequireWithheld:
    def test_raises_on_a_blocking_audit(self) -> None:
        audit = audit_commitment_custody(
            custody_id="suite",
            secrets=[sealed("BETA", "1", ordinal=1)],
            probes=(ordinal_probe(),),
            scheme=scheme,
            canary=CANARY,
        )
        with pytest.raises(ValueError, match="SECRET_DISCLOSED"):
            require_withheld(audit)

    def test_is_silent_on_a_passing_audit(self) -> None:
        audit = audit_commitment_custody(
            custody_id="suite",
            secrets=[sealed("BETA", "unguessable-9c1", ordinal=1)],
            probes=(ordinal_probe(),),
            scheme=scheme,
            canary=CANARY,
        )
        require_withheld(audit)
