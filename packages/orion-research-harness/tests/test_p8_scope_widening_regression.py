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
    authorize_effect,
)


def _type(domain: str, scope: tuple[str, ...]) -> JudgmentType:
    return JudgmentType(domain, "PASS", scope, "sha256:content", 1)


def test_scope_widening_requires_explicit_coercion_declaration():
    narrow = _type("REFRAME", ("subject",))
    wide = _type("ASSERT", ("subject", "other"))
    judgment = Judgment("j:narrow", narrow, ("premise:science",))
    coercion = Coercion(
        "c:implicit-widen",
        narrow,
        wide,
        "root:standing",
        ("premise:coercion",),
        ("j:narrow",),
        1,
        1,
    )
    context = AuthorityContext(
        judgments=(judgment,),
        hard_obligations=(HardAuthorityObligation("o:wide", wide, ("premise:science",)),),
        roots=(RootGrant("g", "ASSERT", ("subject", "other"), "root:standing", RootClass.STANDING_POLICY, 1, "sha256:payload"),),
        coercions=(coercion,),
        blocker_determinations=(("blocker:absolute", BlockerDetermination.REFUTED),),
        required_blocker_type_ids=("blocker:absolute",),
        valid_premise_ids=("premise:science", "premise:coercion", "root:standing"),
        revoked_premise_ids=(),
        support_families=(),
        history=(),
    )
    effect = EffectRequest("e", "ASSERT", "commit", ("subject", "other"), "sha256:payload", 1)
    decision = authorize_effect(effect, context)
    assert decision.terminal is not AuthorityTerminal.AUTHORIZED


def test_explicit_protected_scope_widening_can_be_registered():
    narrow = _type("REFRAME", ("subject",))
    wide = _type("ASSERT", ("subject", "other"))
    judgment = Judgment("j:narrow", narrow, ("premise:science",))
    coercion = Coercion(
        "c:explicit-widen",
        narrow,
        wide,
        "root:standing",
        ("premise:coercion",),
        ("j:narrow",),
        1,
        1,
        allow_scope_widening=True,
    )
    context = AuthorityContext(
        judgments=(judgment,),
        hard_obligations=(HardAuthorityObligation("o:wide", wide, ("premise:science",)),),
        roots=(RootGrant("g", "ASSERT", ("subject", "other"), "root:standing", RootClass.STANDING_POLICY, 1, "sha256:payload"),),
        coercions=(coercion,),
        blocker_determinations=(("blocker:absolute", BlockerDetermination.REFUTED),),
        required_blocker_type_ids=("blocker:absolute",),
        valid_premise_ids=("premise:science", "premise:coercion", "root:standing"),
        revoked_premise_ids=(),
        support_families=(),
        history=(),
    )
    effect = EffectRequest("e", "ASSERT", "commit", ("subject", "other"), "sha256:payload", 1)
    assert authorize_effect(effect, context).terminal is AuthorityTerminal.AUTHORIZED
