#!/usr/bin/env python3
"""Strict integrity wrapper for the frozen MAX-R5 N2 confirmation.

A scientifically negative prospective G gate is a valid experiment and does not
turn into an infrastructure failure. Integrity/semantic failures do.
"""
from __future__ import annotations

import json

import max_r5_n2_joint_internal_confirmation as c


def main():
    r = c.main()
    assert r["schema"] == "ORIONQ.MAXR5.N2JointInternalConfirmation.v1"
    assert r["source"]["blob"] == "15369e8e886efbb3d32f3b2dfe2cfbb96ddebeba"
    assert r["source"]["commit"] == "be306f5830549304176365750d712093950bbdde"
    assert r["n_spatial_orbitals"] == 6
    assert r["n_qubits"] == 12
    assert r["hostile_dp_exhaustive_2q_cases"] == 256
    assert r["gates"]["semantic"]
    assert r["gates"]["joint_realizability"]
    assert r["gates"]["matched_counts_and_ancilla"]
    assert r["gates"]["normalization_le_1pct"]
    assert r["gates"]["no_stronger_oracle"]
    assert r["gates"]["outer_cost_separated"]
    assert r["controlled_outer_SELECT_cost_status"] == "NOT_SYNTHESIZED__R5_CLOSURE_REQUIRED"
    assert r["outer_composition_incumbent"]["outer_blocks"] == r["outer_composition_successor"]["outer_blocks"]
    assert r["donor_composed_incumbent"]["coefficient_rotation_count"] == r["one_pct_successor"]["coefficient_rotation_count"]
    out = {
        "schema": "ORIONQ.MAXR5.N2JointInternalStrict.v1",
        "verification_valid": True,
        "scientific_protocol_pass": bool(r["r5_n2_internal_protocol_pass"]),
        "authority": r["authority"],
        "one_pct_G_reduction": r["one_pct_G_reduction"],
        "one_pct_normalization_overhead": r["one_pct_normalization_overhead"],
    }
    print("ORIONQ_MAX_R5_N2_STRICT=" + json.dumps(out, sort_keys=True))
    return r


if __name__ == "__main__":
    main()
