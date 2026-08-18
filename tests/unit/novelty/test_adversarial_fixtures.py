"""Adversarial novelty-mirage fixtures required by issue #287."""

from orion.novelty import NoveltyFinalState, adversarial_fixtures, seal_certificate
from orion.novelty.fixtures import (
    broad_claim_narrow_residual_draft,
    composition_of_knowns_draft,
    new_terminology_for_old_mechanism_draft,
)


def test_new_terminology_for_old_mechanism_is_not_novelty_supported():
    draft = new_terminology_for_old_mechanism_draft()
    cert = seal_certificate(draft)
    assert cert.final_state is NoveltyFinalState.ALREADY_SOLVED
    assert cert.final_state is not NoveltyFinalState.NOVELTY_SUPPORTED
    assert "epistemic" in draft.claim_text.lower() or "responsibility" in draft.claim_text.lower() or draft.claim_text


def test_composition_of_knowns_does_not_self_authorize_novelty():
    draft = composition_of_knowns_draft()
    cert = seal_certificate(draft)
    assert cert.final_state is not NoveltyFinalState.NOVELTY_SUPPORTED
    assert cert.final_state in {
        NoveltyFinalState.NOVELTY_NARROWED,
        NoveltyFinalState.ALREADY_SOLVED,
        NoveltyFinalState.CANNOT_CHECK,
    }
    assert cert.smallest_residual
    assert cert.smallest_residual != cert.original_claim_text


def test_broad_claim_is_narrowed_to_surviving_residual():
    draft = broad_claim_narrow_residual_draft()
    cert = seal_certificate(draft)
    assert cert.final_state is NoveltyFinalState.NOVELTY_NARROWED
    assert cert.smallest_residual
    assert cert.original_claim_text != cert.smallest_residual
    assert len(cert.smallest_residual) < len(cert.original_claim_text) or "only" in cert.smallest_residual.lower()


def test_adversarial_fixture_registry_exposes_the_required_cases():
    fixtures = adversarial_fixtures()
    ids = {item.claim_id for item in fixtures}
    assert "adv:new-terminology-old-mechanism" in ids
    assert "adv:composition-of-knowns" in ids
    assert "adv:broad-claim-narrow-residual" in ids
    states = {seal_certificate(item).final_state for item in fixtures}
    assert NoveltyFinalState.NOVELTY_SUPPORTED not in states
