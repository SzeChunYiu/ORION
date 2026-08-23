from __future__ import annotations

from orion_research_harness.epistemic_authority import (
    AuthorityContext,
    AuthorityTerminal,
    BlockerDetermination,
    Coercion,
    EffectRequest,
    HardAuthorityObligation,
    Judgment,
    JudgmentType,
    RootClass,
    RootGrant,
    SupportFamily,
    authorize_effect,
    revoke_premises,
    support_family_valid,
)


def _type(domain: str, *, kind: str = "PASS", scope: tuple[str, ...] = ("subject",), content: str = "sha256:content", epoch: int = 1):
    return JudgmentType(domain, kind, scope, content, epoch)


def _effect(domain: str = "ASSERT", *, epoch: int = 1, scope: tuple[str, ...] = ("subject",)):
    return EffectRequest("effect:1", domain, "commit", scope, "sha256:payload", epoch)


def _grant(domain: str = "ASSERT", *, epoch: int = 1, scope: tuple[str, ...] = ("subject",)):
    return RootGrant(
        grant_id="grant:1",
        domain=domain,
        scope_ids=scope,
        root_id="root:standing",
        root_class=RootClass.STANDING_POLICY,
        epoch=epoch,
        payload_digest="sha256:payload",
    )


def _context(*, judgments=(), coercions=(), blocker=BlockerDetermination.REFUTED, epoch: int = 1):
    return AuthorityContext(
        judgments=tuple(judgments),
        hard_obligations=(
            HardAuthorityObligation("o:1", _type("ASSERT", epoch=epoch), additional_premise_ids=("premise:science",)),
        ),
        roots=(_grant(epoch=epoch),),
        coercions=tuple(coercions),
        blocker_determinations=(("blocker:absolute", blocker),),
        required_blocker_type_ids=("blocker:absolute",),
        valid_premise_ids=("premise:science", "premise:coercion", "root:standing"),
        revoked_premise_ids=(),
        support_families=(),
        history=(),
    )


def test_generic_pass_confidence_and_utility_do_not_authorize_without_typed_support():
    context = _context(judgments=())
    decision = authorize_effect(_effect(), context, confidence=1.0, expected_utility=10_000.0)
    assert decision.terminal is AuthorityTerminal.CANNOT_CHECK
    assert decision.authorized is False


def test_foreign_domain_pass_cannot_discharge_without_registered_coercion():
    foreign = Judgment("j:foreign", _type("REFRAME"), support_premise_ids=("premise:science",))
    decision = authorize_effect(_effect(), _context(judgments=(foreign,)))
    assert decision.terminal is not AuthorityTerminal.AUTHORIZED
    assert decision.authorized is False


def test_exact_registered_coercion_allows_typed_cross_domain_discharge():
    foreign_type = _type("REFRAME")
    target_type = _type("ASSERT")
    foreign = Judgment("j:foreign", foreign_type, support_premise_ids=("premise:science",))
    coercion = Coercion(
        coercion_id="c:reframe-to-assert",
        input_type=foreign_type,
        output_type=target_type,
        issuer_root_id="root:standing",
        semantic_premise_ids=("premise:coercion",),
        lineage_ids=("j:foreign",),
        valid_from_epoch=1,
        valid_through_epoch=1,
    )
    decision = authorize_effect(_effect(), _context(judgments=(foreign,), coercions=(coercion,)))
    assert decision.terminal is AuthorityTerminal.AUTHORIZED
    assert decision.authorized is True
    assert decision.coercion_path_ids == ("c:reframe-to-assert",)


def test_stale_epoch_coercion_is_denied():
    foreign_type = _type("REFRAME", epoch=2)
    target_type = _type("ASSERT", epoch=2)
    foreign = Judgment("j:foreign", foreign_type, support_premise_ids=("premise:science",))
    stale = Coercion(
        coercion_id="c:stale",
        input_type=foreign_type,
        output_type=target_type,
        issuer_root_id="root:standing",
        semantic_premise_ids=("premise:coercion",),
        lineage_ids=("j:foreign",),
        valid_from_epoch=1,
        valid_through_epoch=1,
    )
    context = AuthorityContext(
        judgments=(foreign,),
        hard_obligations=(HardAuthorityObligation("o", target_type, additional_premise_ids=("premise:science",)),),
        roots=(_grant(epoch=2),),
        coercions=(stale,),
        blocker_determinations=(("blocker:absolute", BlockerDetermination.REFUTED),),
        required_blocker_type_ids=("blocker:absolute",),
        valid_premise_ids=("premise:science", "premise:coercion", "root:standing"),
        revoked_premise_ids=(),
        support_families=(),
        history=(),
    )
    decision = authorize_effect(_effect(epoch=2), context)
    assert decision.terminal is AuthorityTerminal.DENIED
    assert "stale" in decision.reason.lower() or "epoch" in decision.reason.lower()


def test_scope_widening_coercion_is_denied_when_output_does_not_exactly_match_obligation():
    foreign_type = _type("REFRAME", scope=("subject",))
    too_wide = _type("ASSERT", scope=("subject", "other"))
    required = _type("ASSERT", scope=("subject",))
    foreign = Judgment("j:foreign", foreign_type, support_premise_ids=("premise:science",))
    coercion = Coercion(
        coercion_id="c:wide",
        input_type=foreign_type,
        output_type=too_wide,
        issuer_root_id="root:standing",
        semantic_premise_ids=("premise:coercion",),
        lineage_ids=("j:foreign",),
        valid_from_epoch=1,
        valid_through_epoch=1,
    )
    context = AuthorityContext(
        judgments=(foreign,),
        hard_obligations=(HardAuthorityObligation("o", required, additional_premise_ids=("premise:science",)),),
        roots=(_grant(),),
        coercions=(coercion,),
        blocker_determinations=(("blocker:absolute", BlockerDetermination.REFUTED),),
        required_blocker_type_ids=("blocker:absolute",),
        valid_premise_ids=("premise:science", "premise:coercion", "root:standing"),
        revoked_premise_ids=(),
        support_families=(),
        history=(),
    )
    decision = authorize_effect(_effect(), context)
    assert decision.terminal is not AuthorityTerminal.AUTHORIZED


def test_unprotected_or_missing_coercion_issuer_root_is_denied():
    foreign_type = _type("REFRAME")
    foreign = Judgment("j:foreign", foreign_type, support_premise_ids=("premise:science",))
    coercion = Coercion(
        coercion_id="c:untrusted",
        input_type=foreign_type,
        output_type=_type("ASSERT"),
        issuer_root_id="root:not-registered",
        semantic_premise_ids=("premise:coercion",),
        lineage_ids=("j:foreign",),
        valid_from_epoch=1,
        valid_through_epoch=1,
    )
    decision = authorize_effect(_effect(), _context(judgments=(foreign,), coercions=(coercion,)))
    assert decision.terminal is AuthorityTerminal.DENIED
    assert decision.authorized is False


def test_undetermined_blocker_is_cannot_check_not_authorized():
    exact = Judgment("j:exact", _type("ASSERT"), support_premise_ids=("premise:science",))
    decision = authorize_effect(
        _effect(),
        _context(judgments=(exact,), blocker=BlockerDetermination.UNDETERMINED),
    )
    assert decision.terminal is AuthorityTerminal.CANNOT_CHECK


def test_established_blocker_is_denied_and_positive_evidence_cannot_compensate():
    exact = Judgment("j:exact", _type("ASSERT"), support_premise_ids=("premise:science",))
    decision = authorize_effect(
        _effect(),
        _context(judgments=(exact,), blocker=BlockerDetermination.ESTABLISHED),
        confidence=1.0,
        expected_utility=1e12,
    )
    assert decision.terminal is AuthorityTerminal.DENIED


def test_revocation_breaks_certificate_when_no_complete_support_set_remains():
    family = SupportFamily("k", (("a", "b"),))
    assert support_family_valid(family, valid_premise_ids=("a", "b"), revoked_premise_ids=()) is True
    assert support_family_valid(family, valid_premise_ids=("a", "b"), revoked_premise_ids=("a",)) is False


def test_revocation_preserves_certificate_when_independent_complete_alternate_support_survives():
    family = SupportFamily("k", (("a", "b"), ("c", "d")))
    assert support_family_valid(
        family,
        valid_premise_ids=("a", "b", "c", "d"),
        revoked_premise_ids=("a",),
    ) is True


def test_revocation_is_forward_only_and_append_only_history():
    context = AuthorityContext(
        judgments=(),
        hard_obligations=(),
        roots=(),
        coercions=(),
        blocker_determinations=(),
        required_blocker_type_ids=(),
        valid_premise_ids=("a", "b"),
        revoked_premise_ids=(),
        support_families=(SupportFamily("k", (("a", "b"),)),),
        history=("AUTHORIZED:k@1",),
    )
    revised = revoke_premises(context, ("a",), epoch=2)
    assert revised.history[0] == "AUTHORIZED:k@1"
    assert revised.history[-1] == "REVOKE:a@2"
    assert "a" in revised.revoked_premise_ids
    assert support_family_valid(revised.support_families[0], revised.valid_premise_ids, revised.revoked_premise_ids) is False
