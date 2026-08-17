"""Authority semantics: LLM scores cannot authorize; missing hostile => CANNOT_CHECK."""

from orion.novelty import NoveltyFinalState, SourceAccess, seal_certificate
from orion.novelty.fixtures import example_supported_draft as _draft
from orion.novelty.fixtures import hostile_route as _hostile
from orion.novelty.fixtures import prior_work as _prior


def test_llm_score_cannot_authorize_novelty_supported():
    cert = seal_certificate(
        _draft(
            llm_novelty_score=0.99,
            llm_proposed_state=NoveltyFinalState.NOVELTY_SUPPORTED,
            confidence=0.99,
            hostile_already_solved_route=None,
        )
    )
    assert cert.final_state is NoveltyFinalState.CANNOT_CHECK
    assert cert.llm_novelty_score == 0.99
    assert "llm" in " ".join(cert.authority_reasons).lower() or any(
        "cannot" in reason.lower() and "llm" in reason.lower() for reason in cert.authority_reasons
    ) or any("hostile" in reason.lower() for reason in cert.authority_reasons)


def test_missing_hostile_route_is_cannot_check_even_with_perfect_llm_score():
    cert = seal_certificate(
        _draft(
            hostile_already_solved_route=None,
            llm_novelty_score=1.0,
            llm_proposed_state=NoveltyFinalState.NOVELTY_SUPPORTED,
        )
    )
    assert cert.final_state is NoveltyFinalState.CANNOT_CHECK
    assert any("hostile" in reason.lower() for reason in cert.authority_reasons)


def test_unexecuted_hostile_route_is_cannot_check():
    cert = seal_certificate(
        _draft(
            hostile_already_solved_route=_hostile(executed=False),
            llm_proposed_state=NoveltyFinalState.NOVELTY_SUPPORTED,
        )
    )
    assert cert.final_state is NoveltyFinalState.CANNOT_CHECK


def test_inaccessible_material_source_forces_cannot_check():
    cert = seal_certificate(
        _draft(
            inaccessible_material_sources=("patent:US0000000",),
            unresolved_sources=("patent:US0000000",),
            llm_novelty_score=0.0,
            llm_proposed_state=NoveltyFinalState.ALREADY_SOLVED,
        )
    )
    assert cert.final_state is NoveltyFinalState.CANNOT_CHECK
    assert any("inaccessible" in reason.lower() for reason in cert.authority_reasons)


def test_llm_score_is_recorded_but_does_not_set_supported_when_rules_allow_support():
    cert = seal_certificate(_draft(llm_novelty_score=0.12, confidence=0.12))
    assert cert.final_state is NoveltyFinalState.NOVELTY_SUPPORTED
    assert cert.llm_novelty_score == 0.12
    assert cert.final_state is not cert.llm_proposed_state


def test_llm_cannot_force_already_solved_against_surviving_residual():
    cert = seal_certificate(
        _draft(
            llm_novelty_score=0.0,
            llm_proposed_state=NoveltyFinalState.ALREADY_SOLVED,
        )
    )
    assert cert.final_state is NoveltyFinalState.NOVELTY_SUPPORTED


def test_literature_search_wrapped_around_llm_judge_is_not_supported():
    cert = seal_certificate(
        _draft(
            residual_implementation_evidence=(),
            discriminating_experiment=_draft().discriminating_experiment,
            llm_novelty_score=0.91,
            llm_proposed_state=NoveltyFinalState.NOVELTY_SUPPORTED,
        )
    )
    assert cert.final_state is not NoveltyFinalState.NOVELTY_SUPPORTED
    # wrapping search around a judge, with no residual implementation evidence,
    # cannot mint a supported novelty state
    assert cert.final_state in {
        NoveltyFinalState.NOVELTY_NARROWED,
        NoveltyFinalState.CANNOT_CHECK,
    }


def test_abstract_only_close_prior_that_could_absorb_is_cannot_check():
    close = _prior("arxiv:2606.12071", access=SourceAccess.ABSTRACT_ONLY)
    cert = seal_certificate(
        _draft(
            closest_prior_by_function=(close,),
            inaccessible_material_sources=("arxiv:2606.12071",),
        )
    )
    assert cert.final_state is NoveltyFinalState.CANNOT_CHECK
