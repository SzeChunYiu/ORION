"""P4 study lane: verified scientific discovery.

Holds the P4-specific instruments that the scope-general modules in
:mod:`orion.programme` are parameterised by. The protected V2 campaign itself
lives under ``papers/paper-04-verified-scientific-discovery/``.
"""

from orion.study.p4.claim_axis import ClaimAxisAssessment, assess_claim_axis
from orion.study.p4.promotion_cues import (
    CUSTODY_SPLITS,
    P4_SHORTCUT_PROBES,
    PROMOTION_CUE_NAMES,
    audit_promotion_terminal,
    extract_promotion_cues,
    false_promotion_exercise,
    labelled_case,
)

__all__ = [
    "ClaimAxisAssessment",
    "CUSTODY_SPLITS",
    "P4_SHORTCUT_PROBES",
    "PROMOTION_CUE_NAMES",
    "audit_promotion_terminal",
    "assess_claim_axis",
    "extract_promotion_cues",
    "false_promotion_exercise",
    "labelled_case",
]
