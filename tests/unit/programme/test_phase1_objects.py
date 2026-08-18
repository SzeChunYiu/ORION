from __future__ import annotations

import pytest

from orion.programme.phase1_objects import (
    BreakthroughEpisode,
    CheckStatus,
    InventedMethodCandidate,
    MethodAuthorityRecord,
    MethodFibre,
    MethodRealization,
    StructuralEpisode,
)


# Hostile fixtures are intentionally tiny and synthetic: they test contract boundaries,
# not scientific performance or cross-domain equivalence.
def _realization(**overrides: object) -> MethodRealization:
    values: dict[str, object] = {
        "object_id": "r-1",
        "method_id": "m-1",
        "assumptions": ("a-stationary",),
        "effects": ("e-improves",),
        "failures": ("f-diverges",),
        "lineage": ("source:paper-1",),
    }
    values.update(overrides)
    return MethodRealization(**values)


def test_same_surface_different_effect_is_not_merged_by_realization() -> None:
    left = _realization(object_id="left", effects=("e-safe",))
    right = _realization(object_id="right", effects=("e-unsafe",))
    assert left.assumptions == right.assumptions
    assert left.effects != right.effects
    assert left.object_id != right.object_id


def test_different_surface_same_effect_retains_distinct_method_ids() -> None:
    left = _realization(object_id="left", assumptions=("a-observed",))
    right = _realization(object_id="right", assumptions=("a-hidden",))
    assert left.effects == right.effects
    assert left.assumptions != right.assumptions
    assert left.method_id == right.method_id  # identity is not inferred from effect alone


def test_assumption_erasure_and_provenance_loss_fail_closed() -> None:
    with pytest.raises(ValueError, match="assumptions"):
        _realization(assumptions=())
    with pytest.raises(ValueError, match="lineage"):
        _realization(lineage=())


def test_invalid_composition_fails_closed() -> None:
    with pytest.raises(ValueError, match="at least one realization"):
        MethodFibre(
            object_id="f-1", signature_id="s-1", realization_ids=(), reduction_id="red-1"
        )


def test_unknown_cannot_launder_into_adoption() -> None:
    with pytest.raises(ValueError, match="laundered"):
        MethodAuthorityRecord(
            object_id="auth-1",
            validity=CheckStatus.UNKNOWN,
            applicability=CheckStatus.VERIFIED,
            transfer=CheckStatus.VERIFIED,
            novelty=CheckStatus.VERIFIED,
            utility=CheckStatus.VERIFIED,
            adoption=CheckStatus.VERIFIED,
        )


def test_valid_no_alarm_path_is_explicit_and_non_authoritative() -> None:
    authority = MethodAuthorityRecord(
        object_id="auth-1",
        validity=CheckStatus.VERIFIED,
        applicability=CheckStatus.VERIFIED,
        transfer=CheckStatus.VERIFIED,
        novelty=CheckStatus.VERIFIED,
        utility=CheckStatus.VERIFIED,
        adoption=CheckStatus.VERIFIED,
    )
    episode = StructuralEpisode(
        object_id="episode-1", structure_ids=("sig-1",), split="holdout", outcome=CheckStatus.VERIFIED
    )
    candidate = InventedMethodCandidate(object_id="candidate-1", episode_id="episode-1", proposed_edit="add-op")
    assert authority.adoption is CheckStatus.VERIFIED
    assert episode.scoreable
    assert candidate.authority_granted is False


def test_p10_requires_cutoff_and_candidate_cannot_grant_authority() -> None:
    with pytest.raises(ValueError, match="cutoff"):
        BreakthroughEpisode(
            object_id="b-1", pre_state_id="pre", method_space_edit="edit", post_state_id="post", cutoff=""
        )
    with pytest.raises(ValueError, match="non-authoritative"):
        InventedMethodCandidate(
            object_id="candidate-1", episode_id="episode-1", proposed_edit="add-op", authority_granted=True
        )
