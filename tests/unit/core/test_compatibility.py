from __future__ import annotations

import pytest

from orion.core.compatibility import (
    Context,
    GlueStatus,
    PairwiseStatus,
    TypedCompatibilityComplex,
    glue,
    pairwise_compatibility,
)


def _parity(context_id: str, variables: tuple[str, str], parity: int) -> Context:
    allowed = frozenset(
        (a, b) for a in (0, 1) for b in (0, 1) if (a ^ b) == parity
    )
    return Context(context_id=context_id, variables=variables, allowed=allowed)


def _parity_complex() -> TypedCompatibilityComplex:
    return TypedCompatibilityComplex(
        contexts=(
            _parity("U_xy", ("x", "y"), 0),
            _parity("U_yz", ("y", "z"), 0),
            _parity("U_xz", ("x", "z"), 1),
        )
    )


def test_parity_obstruction_is_the_known_answer():
    """The incumbent falsifier (RAKL Paper I §02, with proof): every pairwise
    overlap is compatible, yet no global assignment exists. An implementation
    answering GLUED here is refuted — this is the case pairwise checks cannot
    catch."""

    complex_ = _parity_complex()
    pairs = [
        (a, b)
        for i, a in enumerate(complex_.contexts)
        for b in complex_.contexts[i + 1 :]
    ]
    assert all(
        pairwise_compatibility(a, b) is PairwiseStatus.COMPATIBLE for a, b in pairs
    )
    verdict = glue(complex_)
    assert verdict.status is GlueStatus.OBSTRUCTED
    assert set(verdict.obstruction_cover) == {"U_xy", "U_yz", "U_xz"}


def test_coherent_parities_glue_with_a_section():
    complex_ = TypedCompatibilityComplex(
        contexts=(
            _parity("U_xy", ("x", "y"), 0),
            _parity("U_yz", ("y", "z"), 0),
            _parity("U_xz", ("x", "z"), 0),
        )
    )
    verdict = glue(complex_)
    assert verdict.status is GlueStatus.GLUED
    section = dict(verdict.section)
    assert section["x"] == section["y"] == section["z"]


def test_resource_bound_yields_cannot_check_not_a_verdict():
    wide = Context(
        context_id="wide",
        variables=tuple(f"v{i}" for i in range(8)),
        allowed=frozenset({tuple(range(8))} | {tuple(range(1, 9))} | {
            tuple((j + k) % 11 for j in range(8)) for k in range(9)
        }),
    )
    verdict = glue(TypedCompatibilityComplex(contexts=(wide,)), search_bound=10)
    assert verdict.status is GlueStatus.CANNOT_CHECK
    assert not verdict.obstruction_cover
    assert not verdict.section


def test_disjoint_vocabulary_cannot_manufacture_an_obstruction():
    a = Context("A", ("p",), frozenset({(0,)}))
    b = Context("B", ("q",), frozenset({(1,)}))
    assert pairwise_compatibility(a, b) is PairwiseStatus.NO_OVERLAP
    assert glue(TypedCompatibilityComplex(contexts=(a, b))).status is GlueStatus.GLUED


def test_pairwise_incompatibility_is_detected():
    a = Context("A", ("x",), frozenset({(0,)}))
    b = Context("B", ("x",), frozenset({(1,)}))
    assert pairwise_compatibility(a, b) is PairwiseStatus.INCOMPATIBLE
    assert glue(TypedCompatibilityComplex(contexts=(a, b))).status is GlueStatus.OBSTRUCTED


def test_empty_allowed_set_is_refused_as_a_chart():
    with pytest.raises(ValueError, match="contradiction"):
        Context("bad", ("x",), frozenset())
