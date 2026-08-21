"""Typed corroboration strength for custody and agreement artifacts.

Why this module exists
----------------------

On 2026-08-21 a dual-harness custody runner re-derived a lane receipt's declared
`result_digest`, matched it, and recorded ACCEPT with verdict AGREE. The receipt
was scientifically defective: a menu-reduction bug had produced a wrong residue,
and the run was nevertheless deterministic, replay-identical, gate-passing and
perfectly digest-valid.

Nothing was wrong with the runner. The mistake was in what its verdict was taken
to mean. Matching a declared digest proves an artifact is **intact and
self-consistent**; it says nothing about whether the computation inside was
**correct**, because a buggy analyzer emits a perfectly digest-valid receipt.
Deterministic double-run replay is equally blind for the same reason — a
deterministic bug reproduces exactly.

Two things did catch that defect, and neither was custody: a cross-check against
a *different* lane's committed lemma, and a verifier that re-derived the science
from primitives instead of re-reading the receipt.

So corroboration strength is a typed property, and a custody artifact must state
which kind it carries. This module refuses to let an artifact claim scientific
corroboration on provenance evidence alone.
"""

from __future__ import annotations

from typing import Any, Mapping

#: Digest/replay evidence only. Proves the artifact is intact and reproducible.
#: Proves nothing about correctness. This is what plain custody yields.
PROVENANCE_ONLY = "PROVENANCE_ONLY"

#: An independent implementation re-derived the result from primitives, without
#: importing the analyzer's tables or re-reading its receipt.
FROM_PRIMITIVES_VERIFIED = "FROM_PRIMITIVES_VERIFIED"

#: The result was checked for consistency against a different lane's committed
#: lemma or receipt, so a defect must be consistent across independent work to
#: survive.
CROSS_LEMMA_BOUND = "CROSS_LEMMA_BOUND"

CORROBORATION_KINDS = frozenset(
    {PROVENANCE_ONLY, FROM_PRIMITIVES_VERIFIED, CROSS_LEMMA_BOUND}
)

#: Only these kinds may back a claim that a result is scientifically corroborated.
SCIENTIFIC_CORROBORATION_KINDS = frozenset(
    {FROM_PRIMITIVES_VERIFIED, CROSS_LEMMA_BOUND}
)


def validate_corroboration(record: Mapping[str, Any]) -> None:
    """Fail closed on a custody artifact that overclaims.

    `record` must carry `corroboration_kind`. If it also asserts
    `scientific_corroboration: true`, the kind must be one that can support
    that assertion — provenance evidence alone cannot.
    """
    if not isinstance(record, Mapping):
        raise TypeError("corroboration record must be an object")

    kind = record.get("corroboration_kind")
    if kind not in CORROBORATION_KINDS:
        raise ValueError(
            f"corroboration_kind must be one of {sorted(CORROBORATION_KINDS)}; "
            f"got {kind!r}. A custody artifact must state what its evidence "
            "actually establishes."
        )

    claims_science = bool(record.get("scientific_corroboration", False))
    if claims_science and kind not in SCIENTIFIC_CORROBORATION_KINDS:
        raise ValueError(
            f"corroboration_kind {kind} cannot support "
            "scientific_corroboration=true. Matching a declared digest proves "
            "the artifact is intact, not that the computation was correct: a "
            "buggy analyzer emits a perfectly digest-valid receipt, and a "
            "deterministic bug replays exactly. Bind a from-primitives verifier "
            "decision or a cross-lemma consistency check instead."
        )


def describe(kind: str) -> str:
    """One line stating what a kind does and does not establish."""
    if kind == PROVENANCE_ONLY:
        return (
            "provenance only: artifact intact and reproducible; correctness NOT "
            "established"
        )
    if kind == FROM_PRIMITIVES_VERIFIED:
        return (
            "independently re-derived from primitives; correctness corroborated "
            "on the verifier's stated domain"
        )
    if kind == CROSS_LEMMA_BOUND:
        return (
            "consistent with an independently committed lemma; a defect would "
            "have to survive that cross-check"
        )
    raise ValueError(f"unknown corroboration kind: {kind}")
