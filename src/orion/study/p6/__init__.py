"""P6 instruments that make an unfalsifiable formal check report as unfalsifiable.

P6's authority is two deterministic checker scripts that enumerate a bounded
model space and print a case count. A case count says how much was enumerated;
it says nothing about whether any of it could have come out the other way. Both
scripts contain claims whose condition is unsatisfiable over their own space ---
``x != x`` counted 320 and 1,536 times --- and one of them computes its
``"terminal": "PASS"`` from three of them.

:mod:`lift_theories` and :mod:`finite_model_theories` transcribe each shipped
checker's claims as predicates over a supplied rule and register the wrong
theories a reviewer would want rejected; :mod:`refutation_audit` runs both and
blocks when a check has no live falsifier or accepts a false theory. The
mechanism itself is :mod:`orion.programme.refutation_capacity`, which builds its
verdict from :class:`orion.programme.guard_exercise.GuardExercise`.

The failure they close is recorded under
``research/failures/2026-08-unfalsifiable-check-zero-refutation-capacity/``.
"""

from __future__ import annotations

from .finite_model_theories import (
    FALSE_ADMISSIBILITY_THEORIES,
    donor_valid,
    finite_model_space,
    reference_admissible,
)
from .lift_theories import (
    FALSE_LIFT_THEORIES,
    INDEPENDENT_LIFT,
    SHIPPED_ROWS_SHA256,
    canonical_rows_digest,
    lifting_model_space,
    reference_lift,
)

__all__ = [
    "FALSE_ADMISSIBILITY_THEORIES",
    "FALSE_LIFT_THEORIES",
    "INDEPENDENT_LIFT",
    "SHIPPED_ROWS_SHA256",
    "canonical_rows_digest",
    "donor_valid",
    "finite_model_space",
    "lifting_model_space",
    "reference_admissible",
    "reference_lift",
]
