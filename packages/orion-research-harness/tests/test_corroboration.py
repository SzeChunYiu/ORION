"""Custody artifacts may not claim correctness on provenance evidence.

Regression for the 2026-08-21 finding: a dual-harness custody runner matched a
lane receipt's declared `result_digest` and recorded ACCEPT / AGREE on a
scientifically defective receipt (a menu-reduction bug had produced the wrong
residue). The run was deterministic, replay-identical, gate-passing and
digest-valid throughout. Digest custody establishes integrity, not correctness.
"""

import pytest

from orion_research_harness.corroboration import (
    CROSS_LEMMA_BOUND,
    FROM_PRIMITIVES_VERIFIED,
    PROVENANCE_ONLY,
    describe,
    validate_corroboration,
)


def test_digest_custody_cannot_claim_scientific_corroboration():
    with pytest.raises(ValueError, match="cannot support"):
        validate_corroboration(
            {
                "corroboration_kind": PROVENANCE_ONLY,
                "scientific_corroboration": True,
                "note": "re-derived result_digest and matched; verdict AGREE",
            }
        )


def test_provenance_only_is_fine_when_it_does_not_overclaim():
    validate_corroboration(
        {"corroboration_kind": PROVENANCE_ONLY, "scientific_corroboration": False}
    )
    validate_corroboration({"corroboration_kind": PROVENANCE_ONLY})


@pytest.mark.parametrize("kind", [FROM_PRIMITIVES_VERIFIED, CROSS_LEMMA_BOUND])
def test_independent_evidence_may_claim_corroboration(kind):
    validate_corroboration(
        {"corroboration_kind": kind, "scientific_corroboration": True}
    )


def test_kind_is_mandatory_and_closed():
    with pytest.raises(ValueError, match="corroboration_kind must be one of"):
        validate_corroboration({"scientific_corroboration": False})
    with pytest.raises(ValueError, match="corroboration_kind must be one of"):
        validate_corroboration({"corroboration_kind": "LOOKS_FINE_TO_ME"})


def test_every_kind_states_what_it_does_not_establish():
    assert "correctness NOT established" in describe(PROVENANCE_ONLY)
    for kind in (FROM_PRIMITIVES_VERIFIED, CROSS_LEMMA_BOUND):
        assert describe(kind)
    with pytest.raises(ValueError):
        describe("nonsense")
