"""P3 instruments that make an absent measurement report as absent.

The two modules here answer the two halves of "did this experiment measure
anything": :mod:`treatment_contrast` on the independent-variable side (did the
ablated arm's input actually differ from the control's) and
:mod:`identity_opportunity` on the dependent-variable side (could the reported
merge/split violation have been non-zero).

Both were written from the P3 public-reference atlas; the failure they close is
recorded under ``research/failures/2026-08-unapplied-treatment-vacuous-null/``.
"""

from __future__ import annotations

from .identity_opportunity import (
    FALSE_MERGE_GUARD_ID,
    FALSE_SPLIT_GUARD_ID,
    UNRESOLVED_CALIBRATION_GUARD_ID,
    IdentityDecisionKind,
    IdentityDecisionLedger,
    IdentityDecisionReceipt,
    assess_identity_guards,
    build_identity_ledger,
    classify_identity_decision,
)
from .treatment_contrast import (
    InertAblation,
    NecessityAssessment,
    NecessityVerdictReason,
    TreatmentContrast,
    assess_coordinate_necessity,
    contrast_from_runs,
    require_treatment_applied,
)

__all__ = [
    "FALSE_MERGE_GUARD_ID",
    "FALSE_SPLIT_GUARD_ID",
    "IdentityDecisionKind",
    "IdentityDecisionLedger",
    "IdentityDecisionReceipt",
    "InertAblation",
    "NecessityAssessment",
    "NecessityVerdictReason",
    "TreatmentContrast",
    "UNRESOLVED_CALIBRATION_GUARD_ID",
    "assess_coordinate_necessity",
    "assess_identity_guards",
    "build_identity_ledger",
    "classify_identity_decision",
    "contrast_from_runs",
    "require_treatment_applied",
]
