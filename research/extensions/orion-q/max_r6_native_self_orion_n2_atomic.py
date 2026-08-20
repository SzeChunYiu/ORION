#!/usr/bin/env python3
"""Erratum-1 adapter for native N2: atomize donor-incomplete OR semantics.

Decision logic remains in production ORION modules. This wrapper changes only
how the frozen responsibility category is represented to the conjunction-based
ResponsibilityHypothesis.v1 schema.
"""
from __future__ import annotations

from orion.transfer.v2.epistemic_responsibility import (
    assess_responsibility,
    build_responsibility_hypothesis,
)

import max_r6_native_self_orion_n0 as n0
import max_r6_native_self_orion_n2 as n2


def atomic_build_responsibility(state):
    ev = state["visible_evidence"]
    hypotheses = (
        build_responsibility_hypothesis(
            hypothesis_id="RESP:CURRENT_SEARCH_INCOMPLETE",
            claim_id=n0.CLAIM,
            expected_observations={"R5H_CURRENT_ALPHABET_EXACT": ("NO",)},
            support_evidence_ids=("r5h-search-space-status",),
        ),
        build_responsibility_hypothesis(
            hypothesis_id="RESP:DONOR_GENERAL_M_INCOMPLETE",
            claim_id=n0.CLAIM,
            expected_observations={
                "R5H_CURRENT_ALPHABET_EXACT": ("YES",),
                "GENERAL_M_DONOR_OUTCOME": ("DOMINATES_OR_INCONCLUSIVE",),
            },
            support_evidence_ids=("general-m-donor-closure-status",),
        ),
        build_responsibility_hypothesis(
            hypothesis_id="RESP:DONOR_INTERFACE_UNRESOLVED",
            claim_id=n0.CLAIM,
            expected_observations={
                "R5H_CURRENT_ALPHABET_EXACT": ("YES",),
                "FOQCS_INTERFACE_ENVELOPE": ("UNRESOLVED",),
            },
            support_evidence_ids=("foqcs-interface-closure-status",),
        ),
        build_responsibility_hypothesis(
            hypothesis_id="RESP:INTERFACE_INADEQUATE",
            claim_id=n0.CLAIM,
            expected_observations={
                "R5H_CURRENT_ALPHABET_EXACT": ("YES",),
                "GENERAL_M_DONOR_OUTCOME": ("NONDOMINATING_OR_CLOSED",),
                "FOQCS_INTERFACE_ENVELOPE": ("OPTIMISTIC_BOUND_REGISTERED",),
                "FOQCS_OPTIMISTIC_DOMINATES_H4_DONOR": ("YES", "UNRESOLVED"),
            },
            support_evidence_ids=("foqcs-interface-envelope",),
        ),
        build_responsibility_hypothesis(
            hypothesis_id="RESP:METHOD_LANGUAGE_INADEQUATE",
            claim_id=n0.CLAIM,
            expected_observations={
                "R5H_CURRENT_ALPHABET_EXACT": ("YES",),
                "GENERAL_M_DONOR_OUTCOME": ("NONDOMINATING_OR_CLOSED",),
                "FOQCS_INTERFACE_ENVELOPE": ("OPTIMISTIC_BOUND_REGISTERED",),
                "FOQCS_OPTIMISTIC_DOMINATES_H4_DONOR": ("NO",),
                "CURRENT_METHOD_INCREMENTAL_VALUE_ON_H4": (
                    "NONE_OVER_DIRECT_CLIQUE_DONOR",
                ),
            },
            support_evidence_ids=("r5h-mixed-collapse", "foqcs-optimistic-envelope"),
        ),
    )
    observed = {
        "R5H_CURRENT_ALPHABET_EXACT": ev["R5H_CURRENT_ALPHABET_EXACT"],
        "GENERAL_M_DONOR_OUTCOME": ev["GENERAL_M_DONOR_OUTCOME"],
        "FOQCS_INTERFACE_ENVELOPE": ev["FOQCS_INTERFACE_ENVELOPE"],
        "FOQCS_OPTIMISTIC_DOMINATES_H4_DONOR": ev[
            "FOQCS_OPTIMISTIC_DOMINATES_H4_DONOR"
        ],
        "CURRENT_METHOD_INCREMENTAL_VALUE_ON_H4": ev[
            "CURRENT_METHOD_INCREMENTAL_VALUE_ON_H4"
        ],
    }
    return hypotheses, observed, assess_responsibility(hypotheses, observed_outcomes=observed)


# Patch only the frozen adapter and responsibility->revision aliases. Production
# assessment, revision selection, computation allocation, and control stay native.
n2.build_responsibility = atomic_build_responsibility

_orig_assess = n2.assess_revision_gate

def assess_revision_gate_atomic(*, responsibility, interface, mechanics, assessments, responsibility_bindings):
    bindings = dict(responsibility_bindings)
    bindings.pop("RESP:DONOR_CLOSURE_INCOMPLETE", None)
    bindings["RESP:DONOR_GENERAL_M_INCOMPLETE"] = ("REV:ABSORB_DONOR",)
    bindings["RESP:DONOR_INTERFACE_UNRESOLVED"] = ("REV:ABSORB_DONOR",)
    return _orig_assess(
        responsibility=responsibility,
        interface=interface,
        mechanics=mechanics,
        assessments=assessments,
        responsibility_bindings=bindings,
    )

n2.assess_revision_gate = assess_revision_gate_atomic

if __name__ == "__main__":
    n2.main()
