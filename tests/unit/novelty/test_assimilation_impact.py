from types import SimpleNamespace

import pytest

from orion.knowledge.mechanism_assimilation import AssimilationVerdict
from orion.knowledge.nearest_work import AbsorptionDisposition
from orion.novelty.assimilation_impact import (
    AssimilationNoveltyImpactState,
    assess_assimilation_novelty_impact,
    assert_certificate_current_after_assimilation,
)
from orion.novelty.types import NoveltyFinalState


def _certificate(*mechanic_ids: str, state: NoveltyFinalState = NoveltyFinalState.NOVELTY_NARROWED):
    return SimpleNamespace(
        content_hash="cert-hash",
        final_state=state,
        claimed_mechanism_decomposition=tuple(
            SimpleNamespace(mechanism_id=mechanic_id) for mechanic_id in mechanic_ids
        ),
        absorption_decisions=(),
    )


def _assimilation(
    *target_ids: str,
    verdict: AssimilationVerdict = AssimilationVerdict.ADMITTED,
    disposition: AbsorptionDisposition = AbsorptionDisposition.ADOPT,
):
    return SimpleNamespace(
        content_hash="assimilation-hash",
        verdict=verdict,
        disposition=disposition,
        claim=SimpleNamespace(target_mechanic_ids=tuple(target_ids)),
    )


def test_material_overlap_forces_certificate_reassessment():
    receipt = assess_assimilation_novelty_impact(
        _certificate("mechanic.transfer.selector", "mechanic.transfer.contract"),
        _assimilation("mechanic.transfer.contract"),
    )

    assert receipt.state is AssimilationNoveltyImpactState.REASSESS_REQUIRED
    assert receipt.affected_mechanic_ids == ("mechanic.transfer.contract",)
    assert receipt.effective_final_state is NoveltyFinalState.CANNOT_CHECK
    assert receipt.grants_authority == "NONE"
    assert receipt.self_authorizing is False
    assert receipt.content_hash


def test_material_absorption_outside_certificate_surface_preserves_state():
    receipt = assess_assimilation_novelty_impact(
        _certificate("mechanic.transfer.contract"),
        _assimilation("mechanic.unrelated"),
    )

    assert receipt.state is AssimilationNoveltyImpactState.NO_MATERIAL_IMPACT
    assert receipt.effective_final_state is NoveltyFinalState.NOVELTY_NARROWED
    assert receipt.affected_mechanic_ids == ()


def test_defer_does_not_invalidate_novelty_even_when_target_id_matches():
    receipt = assess_assimilation_novelty_impact(
        _certificate("mechanic.transfer.contract"),
        _assimilation(
            "mechanic.transfer.contract",
            disposition=AbsorptionDisposition.DEFER,
        ),
    )

    assert receipt.state is AssimilationNoveltyImpactState.NO_MATERIAL_IMPACT
    assert receipt.effective_final_state is NoveltyFinalState.NOVELTY_NARROWED


def test_unsettled_assimilation_fails_closed():
    receipt = assess_assimilation_novelty_impact(
        _certificate("mechanic.transfer.contract"),
        _assimilation(
            "mechanic.transfer.contract",
            verdict=AssimilationVerdict.CANNOT_CHECK,
        ),
    )

    assert receipt.state is AssimilationNoveltyImpactState.CANNOT_CHECK
    assert receipt.effective_final_state is NoveltyFinalState.CANNOT_CHECK


def test_currentness_guard_rejects_stale_certificate():
    with pytest.raises(ValueError, match="re-assessment required"):
        assert_certificate_current_after_assimilation(
            _certificate("mechanic.transfer.contract"),
            _assimilation("mechanic.transfer.contract"),
        )


def test_currentness_guard_rejects_unsettled_assimilation():
    with pytest.raises(ValueError, match="assimilation is unsettled"):
        assert_certificate_current_after_assimilation(
            _certificate("mechanic.transfer.contract"),
            _assimilation(
                "mechanic.transfer.contract",
                verdict=AssimilationVerdict.CANNOT_CHECK,
            ),
        )
