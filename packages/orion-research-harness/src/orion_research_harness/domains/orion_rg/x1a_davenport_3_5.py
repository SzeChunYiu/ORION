"""Harness campaign for the first ORION-RG Davenport breakthrough fibre.

This tranche does not attempt to prove the rank-3 theorem.  It binds the current
external donor inputs and reconstructs the exact one-block deficit that the next
obstruction-atlas campaign must attack.  Every output is non-authorizing.
"""
from __future__ import annotations

_DONOR_PREFIX = "ORIONRG_X1A_DONOR="
_DEFICIT_PREFIX = "ORIONRG_X1A_DEFICIT="

_DONOR_ARITHMETIC = r'''
import json

# External mathematical inputs are verified in the preceding VERIFY_EVIDENCE
# capability.  This code only reconstructs their arithmetic consequences.
p = 3
freeze_schmid_lower_intercept = 5 * (p - 1) // 2
ideal_intercept = 2 * p - 2
out = {
    "p": p,
    "freeze_schmid_lower_intercept": freeze_schmid_lower_intercept,
    "ideal_intercept": ideal_intercept,
    "ordinary_dk_sharp_induction_blocked": freeze_schmid_lower_intercept > ideal_intercept,
    "gap": freeze_schmid_lower_intercept - ideal_intercept,
    "novelty_authority": False,
    "scientific_authority": False,
}
print("ORIONRG_X1A_DONOR=" + json.dumps(out, sort_keys=True, separators=(",", ":")))
'''

_DEFICIT_ARITHMETIC = r'''
import json

# Freeze--Schmid gives D_0(C_3^3)=6 and k_D(C_3^3)=3; hence
# D_k(C_3^3)=3k+6 for k>=3.  For n=15 the conjectured Davenport threshold
# is 43 and the complementary C_5^3 Davenport constant is 13.
def dk_c3(k):
    if k < 3:
        raise ValueError("this reconstruction uses only the stabilized k>=3 formula")
    return 3 * k + 6

target_length = 3 * 15 - 2
cofactor_davenport = 3 * 5 - 2
k12 = dk_c3(12)
k13 = dk_c3(13)
guaranteed_blocks = max(k for k in range(3, 30) if dk_c3(k) <= target_length)
out = {
    "target_length": target_length,
    "cofactor_davenport": cofactor_davenport,
    "D12_C3cubed": k12,
    "D13_C3cubed": k13,
    "guaranteed_quotient_zero_sum_blocks": guaranteed_blocks,
    "effective_block_deficit": cofactor_davenport - guaranteed_blocks,
    "exactly_one_block_short": cofactor_davenport - guaranteed_blocks == 1,
    "calibration_only": True,
    "family_theorem_authority": False,
    "novelty_authority": False,
    "scientific_authority": False,
}
print("ORIONRG_X1A_DEFICIT=" + json.dumps(out, sort_keys=True, separators=(",", ":")))
'''


X1A_DAVENPORT_3_5_CAMPAIGN_MANIFEST = {
    "schema": "ORION.ResearchCampaignManifest.v1",
    "campaign_id": "orion-rg:x1a-davenport-3-5-frontier",
    "claim_id": "orion-rg:x1a-odd-homocyclic-rank3",
    "description": (
        "Bind the current Davenport donor frontier and freeze the exact one-block "
        "deficit for C_15^3 before obstruction-atlas/theorem synthesis."
    ),
    "initial_phase": "S0",
    "initial_observations": {"X1A_DONOR_REVIEW_NEEDED": "YES"},
    "authority_ceiling": "NON_AUTHORIZING_MATH_DISCOVERY_FIBRE",
    "protected_refs": [],
    "capabilities": {
        "x1a.verify_donors": {
            "host_capability": "VERIFY_EVIDENCE",
            "payload": {
                "claim": (
                    "Verify only these donor inputs: (1) Freeze--Schmid gives "
                    "D_0(C_3^3)=6 and k_D(C_3^3)=3 and its Theorem 4.1 implies "
                    "D_k(C_p^3)>=pk+5(p-1)/2 for odd prime p; (2) for the p-group "
                    "C_5^3, D=13; (3) Grinsztajn 2026 gives the current general "
                    "homocyclic rank-3 upper bound D(C_n^3)<=4n-P(n)-2. "
                    "Do not assess ORION novelty or prove the target family theorem."
                ),
                "sources": [
                    "https://www.math.univ-paris13.fr/~schmid/personal/schmid_28t.pdf",
                    "https://github.com/maaxgrin/davenport-cn3-bound",
                ],
                "required_scope": "DONOR_BINDING_ONLY",
            },
            "result_contract": {
                "kind": "DIRECT_JSON",
                "required_payload_values": [
                    {"path": ["passed"], "equals": True},
                ],
                "evidence_rules": [
                    {"evidence_key": "X1A_DONOR_VERIFIED", "path": ["passed"], "transform": "BOOL_YES_NO"},
                ],
            },
            "next_phase": "D0",
        },
        "x1a.reconstruct_donor_obstruction": {
            "host_capability": "PYTHON",
            "payload": {"code": _DONOR_ARITHMETIC, "cwd": ".", "timeout": 30},
            "result_contract": {
                "kind": "SHELL_JSON_TOKEN",
                "prefix": _DONOR_PREFIX,
                "required_payload_values": [
                    {"path": ["ordinary_dk_sharp_induction_blocked"], "equals": True},
                    {"path": ["gap"], "equals": 1},
                    {"path": ["novelty_authority"], "equals": False},
                    {"path": ["scientific_authority"], "equals": False},
                ],
                "evidence_rules": [
                    {"evidence_key": "X1A_ORDINARY_DK_ROUTE_BLOCKED", "path": ["ordinary_dk_sharp_induction_blocked"], "transform": "BOOL_YES_NO"},
                ],
            },
            "next_phase": "B0",
        },
        "x1a.reconstruct_one_block_deficit": {
            "host_capability": "PYTHON",
            "payload": {"code": _DEFICIT_ARITHMETIC, "cwd": ".", "timeout": 30},
            "result_contract": {
                "kind": "SHELL_JSON_TOKEN",
                "prefix": _DEFICIT_PREFIX,
                "required_payload_values": [
                    {"path": ["target_length"], "equals": 43},
                    {"path": ["cofactor_davenport"], "equals": 13},
                    {"path": ["D12_C3cubed"], "equals": 42},
                    {"path": ["D13_C3cubed"], "equals": 45},
                    {"path": ["guaranteed_quotient_zero_sum_blocks"], "equals": 12},
                    {"path": ["effective_block_deficit"], "equals": 1},
                    {"path": ["exactly_one_block_short"], "equals": True},
                    {"path": ["calibration_only"], "equals": True},
                    {"path": ["family_theorem_authority"], "equals": False},
                    {"path": ["novelty_authority"], "equals": False},
                    {"path": ["scientific_authority"], "equals": False},
                ],
                "evidence_rules": [
                    {"evidence_key": "X1A_ONE_BLOCK_DEFICIT", "path": ["exactly_one_block_short"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "X1A_CALIBRATION_ONLY", "path": ["calibration_only"], "transform": "BOOL_YES_NO"},
                ],
            },
            "next_phase": "FRONTIER_FROZEN",
        },
    },
    "phases": {
        "S0": {
            "active_hard_obligations": ["X1A_BIND_CURRENT_DONOR_FRONTIER"],
            "responsibility_hypotheses": [
                {
                    "hypothesis_id": "RESP:X1A_DONOR_REVIEW",
                    "expected_observations": {"X1A_DONOR_REVIEW_NEEDED": ["YES"]},
                }
            ],
            "interface_checks": [
                {"check_id": "IFACE:X1A_DONOR_FIRST_REFUSAL", "scope": "NOVELTY_BOUNDARY", "state": "PASS"},
                {"check_id": "IFACE:X1A_NO_TARGET_OUTCOME", "scope": "PROSPECTIVE_FREEZE", "state": "PASS"},
            ],
            "revision_mechanics": [
                {
                    "mechanic_id": "REV:X1A_VERIFY_DONOR",
                    "kind": "VERIFY_MORE",
                    "write_coordinates": ["EVIDENCE"],
                    "preservation_obligations": ["PRESERVE:NOVELTY_OPEN"],
                    "cost": 0.1,
                }
            ],
            "computation_actions": [
                {
                    "action_id": "COMPUTE:X1A_VERIFY_DONORS",
                    "kind": "VERIFY",
                    "expected_decision_value": 10.0,
                    "cost": 0.1,
                    "discharges_obligations": ["X1A_BIND_CURRENT_DONOR_FRONTIER"],
                }
            ],
            "responsibility_bindings": {"RESP:X1A_DONOR_REVIEW": ["REV:X1A_VERIFY_DONOR"]},
            "selected_capabilities": {"COMPUTE:X1A_VERIFY_DONORS": "x1a.verify_donors"},
        },
        "D0": {
            "active_hard_obligations": ["X1A_REFUTE_NAIVE_DK_ROUTE"],
            "responsibility_hypotheses": [
                {
                    "hypothesis_id": "RESP:X1A_DK_ROUTE_OBSTRUCTION",
                    "expected_observations": {"X1A_DONOR_VERIFIED": ["YES"]},
                }
            ],
            "interface_checks": [
                {"check_id": "IFACE:X1A_DONOR_INPUT_NOT_ORION_RESULT", "scope": "AUTHORITY", "state": "PASS"},
            ],
            "revision_mechanics": [
                {
                    "mechanic_id": "REV:X1A_DIAGNOSE_STATE_VARIABLE",
                    "kind": "DIAGNOSE",
                    "read_coordinates": ["EVIDENCE"],
                    "write_coordinates": ["METHOD_STATE"],
                    "preservation_obligations": ["PRESERVE:FAILED_DK_ROUTE"],
                    "cost": 0.1,
                }
            ],
            "computation_actions": [
                {
                    "action_id": "COMPUTE:X1A_RECONSTRUCT_DK_OBSTRUCTION",
                    "kind": "VERIFY",
                    "expected_decision_value": 8.0,
                    "cost": 0.1,
                    "discharges_obligations": ["X1A_REFUTE_NAIVE_DK_ROUTE"],
                }
            ],
            "responsibility_bindings": {"RESP:X1A_DK_ROUTE_OBSTRUCTION": ["REV:X1A_DIAGNOSE_STATE_VARIABLE"]},
            "selected_capabilities": {"COMPUTE:X1A_RECONSTRUCT_DK_OBSTRUCTION": "x1a.reconstruct_donor_obstruction"},
        },
        "B0": {
            "active_hard_obligations": ["X1A_FREEZE_ONE_BLOCK_DEFICIT"],
            "responsibility_hypotheses": [
                {
                    "hypothesis_id": "RESP:X1A_ONE_BLOCK_DEFICIT",
                    "expected_observations": {"X1A_ORDINARY_DK_ROUTE_BLOCKED": ["YES"]},
                }
            ],
            "interface_checks": [
                {"check_id": "IFACE:X1A_C15_CALIBRATION_NOT_THEOREM", "scope": "CLAIM_CEILING", "state": "PASS"},
            ],
            "revision_mechanics": [
                {
                    "mechanic_id": "REV:X1A_REFRAME_TO_LIFT_COMPATIBLE_OBSTRUCTION",
                    "kind": "REFRAME",
                    "read_coordinates": ["METHOD_STATE", "EVIDENCE"],
                    "write_coordinates": ["RESIDUAL"],
                    "preservation_obligations": [
                        "PRESERVE:NO_THEOREM_FROM_FINITE_CALIBRATION",
                        "PRESERVE:NOVELTY_OPEN",
                    ],
                    "cost": 0.1,
                }
            ],
            "computation_actions": [
                {
                    "action_id": "COMPUTE:X1A_ONE_BLOCK_DEFICIT",
                    "kind": "VERIFY",
                    "expected_decision_value": 10.0,
                    "cost": 0.1,
                    "discharges_obligations": ["X1A_FREEZE_ONE_BLOCK_DEFICIT"],
                }
            ],
            "responsibility_bindings": {"RESP:X1A_ONE_BLOCK_DEFICIT": ["REV:X1A_REFRAME_TO_LIFT_COMPATIBLE_OBSTRUCTION"]},
            "selected_capabilities": {"COMPUTE:X1A_ONE_BLOCK_DEFICIT": "x1a.reconstruct_one_block_deficit"},
        },
        "FRONTIER_FROZEN": {
            "terminal": True,
            "terminal_name": "X1A_ONE_BLOCK_DEFICIT_DISCOVERY_FIBRE_FROZEN__NO_THEOREM_AUTHORITY",
            "active_hard_obligations": [],
        },
    },
}
