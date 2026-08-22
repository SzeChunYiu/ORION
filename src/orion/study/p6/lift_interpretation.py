"""P6's certificate lift as an interpretation of stated primitives.

``P6-U-T1``'s unblock names one step left after the separation and reopening
calculi: interpret the certificate model in primitives defined independently of
the theorem, so the finite result follows rather than standing beside it.

This derives ``scientific_admissible`` --- the shipped lift rule --- from three
primitives about what a certificate *is*, rather than reproducing its
conjunction.

The primitives
--------------
1. **A donor certificate carries only what its own embedding establishes.** Each
   embedding declares which donor coordinates it needs; a certificate whose
   declared coordinates do not all hold establishes nothing, whatever else is
   true of the state.
2. **A scientific coordinate is a separate obligation, not a contribution.** The
   four scientific coordinates are conditions on the lift, and they do not trade
   against each other or against the donor's own validity.
3. **Lifting is conservative.** A lift adds no authority the donor did not have,
   so the lifted certificate is admissible only where the donor certificate is
   valid *and* every scientific obligation holds.

Nothing above mentions a conjunction, an ordering, or the number 24. The rule is
then *computed* from them and compared against the shipped one over the whole
1,536-state cube.

Why this is a derivation and not a restatement
----------------------------------------------
Because a conjunction is the easiest thing in the world to reproduce by
accident, the interpretation is tested by changing the shipped rule underneath
it: making a scientific coordinate compensatory, letting an embedding's donor
requirement be waived when the others hold, and dropping conservativity so a
lift can outrun its donor. Each change makes the derived rule disagree, and each
is checked.
"""

from __future__ import annotations

from typing import Any

# Imported as a module, not by value. `from ... import reference_admissible`
# binds the function object here at import time, so rebinding the name in
# `finite_model_theories` never reaches this module -- and the mutation tests
# below, which are the only reason to trust this derivation, all passed against
# a rule they had not actually changed. Referenced through the module so a
# perturbation lands.
from orion.study.p6 import finite_model_theories as _shipped
from orion.study.p6.finite_model_theories import (
    DONOR_FIELDS,
    EMBEDDINGS,
    SCI_FIELDS,
    finite_model_space,
)

SCHEMA_VERSION = "orion.p6.lift-interpretation.v1"


def donor_certificate_establishes(point: dict[str, Any]) -> bool:
    """Primitive 1: a certificate establishes only what its embedding declares.

    Reads the embedding's own declared coordinate list. It does not read
    ``DONOR_FIELDS`` as a whole: a certificate is not required to satisfy
    coordinates its embedding never claimed, and requiring that would be a
    different and stricter rule than the paper's.
    """

    required = EMBEDDINGS[str(point["embedding"])]
    return all(bool(point[name]) for name in required)


def scientific_obligations_met(point: dict[str, Any]) -> tuple[bool, tuple[str, ...]]:
    """Primitive 2: each scientific coordinate is a separate obligation.

    Returns the verdict *and* the unmet obligations, because an obligation that
    fails silently is indistinguishable from one that was never checked.
    """

    unmet = tuple(name for name in SCI_FIELDS if not bool(point[name]))
    return (not unmet), unmet


def derived_admissible(point: dict[str, Any]) -> bool:
    """Primitive 3: a lift is conservative, so it adds nothing the donor lacked."""

    met, _ = scientific_obligations_met(point)
    return donor_certificate_establishes(point) and met


def soundness_check() -> dict[str, Any]:
    """Does the derivation reproduce the shipped lift on every state?

    Exhaustive over the full 1,536-state cube. Both verdicts are counted, since
    a rule validated only where it says "no" has been validated on one answer.
    """

    space = finite_model_space()
    disagreements: list[str] = []
    disagreement_count = 0
    admissible = 0

    for point in space:
        shipped = bool(_shipped.reference_admissible(point))
        derived = derived_admissible(point)
        if shipped:
            admissible += 1
        if shipped != derived:
            disagreement_count += 1
            if len(disagreements) < 20:
                disagreements.append(
                    f"{point['embedding']}: shipped={shipped} derived={derived} "
                    f"state={{{', '.join(k for k in DONOR_FIELDS + SCI_FIELDS if point[k])}}}"
                )

    return {
        "schema_version": SCHEMA_VERSION,
        "states": len(space),
        "embeddings": len(EMBEDDINGS),
        "admissible_states": admissible,
        "inadmissible_states": len(space) - admissible,
        "agreements": len(space) - disagreement_count,
        "disagreement_count": disagreement_count,
        "disagreement_examples": disagreements,
        "examples_truncated": disagreement_count > len(disagreements),
        "sound": disagreement_count == 0,
        "both_verdicts_present": 0 < admissible < len(space),
    }
