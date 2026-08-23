"""Prospective harness campaign for the first unresolved C45^3 rank-3 fibre.

The campaign binds the donor-known C15^3 base, reconstructs the exact one-block
deficit for C45^3, and freezes the mixed-kernel missing-sum problem as the next
scientific obligation. It grants no theorem or novelty authority.
"""
from __future__ import annotations

_ARITH_PREFIX = "ORIONRG_X1C_ARITH="

_ARITHMETIC = r'''
import json

def dk_c3(k):
    if k < 3:
        raise ValueError("stabilized formula only used for k>=3")
    return 3*k + 6

n = 45
target = 3*n - 2
kernel_davenport = 43  # donor-known D(C_15^3)
needed_blocks = kernel_davenport
k42 = dk_c3(42)
k43 = dk_c3(43)
guaranteed_blocks = max(k for k in range(3, 100) if dk_c3(k) <= target)
out = {
    "n": n,
    "target_length": target,
    "kernel": "C_15^3",
    "kernel_davenport": kernel_davenport,
    "D42_C3cubed": k42,
    "D43_C3cubed": k43,
    "guaranteed_quotient_zero_sum_blocks": guaranteed_blocks,
    "needed_kernel_blocks": needed_blocks,
    "effective_block_deficit": needed_blocks - guaranteed_blocks,
    "exactly_one_block_short": needed_blocks - guaranteed_blocks == 1,
    "classical_inductive_upper_bound": k43,
    "c15_known_answer_absorbed": True,
    "c45_theorem_authority": False,
    "infinite_family_authority": False,
    "novelty_authority": False,
    "scientific_authority": False,
}
print("ORIONRG_X1C_ARITH=" + json.dumps(out, sort_keys=True, separators=(",", ":")))
'''

X1C_C45_MIXED_KERNEL_CAMPAIGN_MANIFEST = {
    "schema": "ORION.ResearchCampaignManifest.v1",
    "campaign_id": "orion-rg:x1c-c45-mixed-kernel-frontier",
    "claim_id": "orion-rg:x1c-c45-rank3",
    "description": (
        "Absorb the donor-known C15^3 base, reconstruct the exact one-block "
        "deficit for C45^3, and freeze mixed-kernel missing-sum geometry."
    ),
    "initial_phase": "S0",
    "initial_observations": {"X1C_DONOR_REVIEW_NEEDED": "YES"},
    "authority_ceiling": "NON_AUTHORIZING_MATH_DISCOVERY_FIBRE",
    "protected_refs": [],
    "capabilities": {
        "x1c.verify_current_donors": {
            "host_capability": "VERIFY_EVIDENCE",
            "payload": {
                "claim": (
                    "Verify donor scope only: (1) D(C_15^3)=43 is already known, "
                    "including the current 2026 statement that d(C_n^3)=d*(C_n^3) "
                    "for n=3 p^k; (2) Freeze--Schmid gives D_k(C_3^3)=3k+6 for "
                    "k>=3; (3) Geroldinger--Yang 2026 proves nu_p=d-1 for p-groups "
                    "but does not state an exact nu/nu_3/nu_5 value for C_15^3; "
                    "(4) report any current exact D(C_45^3) theorem if found. "
                    "Do not assess ORION novelty."
                ),
                "sources": [
                    "https://arxiv.org/pdf/2608.19090",
                    "https://www.math.univ-paris13.fr/~schmid/personal/schmid_28t.pdf",
                    "https://arxiv.org/pdf/math/0610416",
                ],
                "required_scope": "DONOR_BINDING_ONLY",
            },
            "result_contract": {
                "kind": "DIRECT_JSON",
                "required_payload_values": [
                    {"path": ["passed"], "equals": True},
                ],
                "evidence_rules": [
                    {"evidence_key": "X1C_DONOR_REVIEW_COMPLETE", "path": ["passed"], "transform": "BOOL_YES_NO"},
                ],
            },
            "next_phase": "B0",
        },
        "x1c.reconstruct_one_block_deficit": {
            "host_capability": "PYTHON",
            "payload": {"code": _ARITHMETIC, "cwd": ".", "timeout": 30},
            "result_contract": {
                "kind": "SHELL_JSON_TOKEN",
                "prefix": _ARITH_PREFIX,
                "required_payload_values": [
                    {"path": ["target_length"], "equals": 133},
                    {"path": ["kernel_davenport"], "equals": 43},
                    {"path": ["D42_C3cubed"], "equals": 132},
                    {"path": ["D43_C3cubed"], "equals": 135},
                    {"path": ["guaranteed_quotient_zero_sum_blocks"], "equals": 42},
                    {"path": ["needed_kernel_blocks"], "equals": 43},
                    {"path": ["effective_block_deficit"], "equals": 1},
                    {"path": ["exactly_one_block_short"], "equals": True},
                    {"path": ["c15_known_answer_absorbed"], "equals": True},
                    {"path": ["c45_theorem_authority"], "equals": False},
                    {"path": ["infinite_family_authority"], "equals": False},
                    {"path": ["novelty_authority"], "equals": False},
                    {"path": ["scientific_authority"], "equals": False},
                ],
                "evidence_rules": [
                    {"evidence_key": "X1C_ONE_BLOCK_DEFICIT", "path": ["exactly_one_block_short"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "X1C_C15_DONOR_ABSORBED", "path": ["c15_known_answer_absorbed"], "transform": "BOOL_YES_NO"},
                ],
            },
            "next_phase": "MIXED_KERNEL_OPEN",
        },
    },
    "phases": {
        "S0": {
            "active_hard_obligations": ["X1C_BIND_CURRENT_DONORS"],
            "responsibility_hypotheses": [
                {"hypothesis_id": "RESP:X1C_DONOR_FIRST_REFUSAL", "expected_observations": {"X1C_DONOR_REVIEW_NEEDED": ["YES"]}}
            ],
            "interface_checks": [
                {"check_id": "IFACE:X1C_NO_C15_RECLAIM", "scope": "NOVELTY_BOUNDARY", "state": "PASS"},
                {"check_id": "IFACE:X1C_NO_C45_OUTCOME", "scope": "PROSPECTIVE_FREEZE", "state": "PASS"},
            ],
            "revision_mechanics": [
                {"mechanic_id": "REV:X1C_ABSORB_DONORS", "kind": "ABSORB", "write_coordinates": ["EVIDENCE"], "preservation_obligations": ["PRESERVE:C15_DONOR_CREDIT", "PRESERVE:NOVELTY_OPEN"], "cost": 0.1}
            ],
            "computation_actions": [
                {"action_id": "COMPUTE:X1C_VERIFY_DONORS", "kind": "VERIFY", "expected_decision_value": 10.0, "cost": 0.1, "discharges_obligations": ["X1C_BIND_CURRENT_DONORS"]}
            ],
            "responsibility_bindings": {"RESP:X1C_DONOR_FIRST_REFUSAL": ["REV:X1C_ABSORB_DONORS"]},
            "selected_capabilities": {"COMPUTE:X1C_VERIFY_DONORS": "x1c.verify_current_donors"},
        },
        "B0": {
            "active_hard_obligations": ["X1C_FREEZE_ONE_BLOCK_DEFICIT"],
            "responsibility_hypotheses": [
                {"hypothesis_id": "RESP:X1C_DEFICIT_ARITHMETIC", "expected_observations": {"X1C_DONOR_REVIEW_COMPLETE": ["YES"]}}
            ],
            "interface_checks": [
                {"check_id": "IFACE:X1C_ARITHMETIC_NOT_THEOREM", "scope": "CLAIM_CEILING", "state": "PASS"}
            ],
            "revision_mechanics": [
                {"mechanic_id": "REV:X1C_REFRAME_MIXED_KERNEL", "kind": "REFRAME", "read_coordinates": ["EVIDENCE"], "write_coordinates": ["RESIDUAL"], "preservation_obligations": ["PRESERVE:NO_THEOREM_FROM_ARITHMETIC", "PRESERVE:NOVELTY_OPEN"], "cost": 0.1}
            ],
            "computation_actions": [
                {"action_id": "COMPUTE:X1C_ONE_BLOCK_DEFICIT", "kind": "VERIFY", "expected_decision_value": 10.0, "cost": 0.1, "discharges_obligations": ["X1C_FREEZE_ONE_BLOCK_DEFICIT"]}
            ],
            "responsibility_bindings": {"RESP:X1C_DEFICIT_ARITHMETIC": ["REV:X1C_REFRAME_MIXED_KERNEL"]},
            "selected_capabilities": {"COMPUTE:X1C_ONE_BLOCK_DEFICIT": "x1c.reconstruct_one_block_deficit"},
        },
        "MIXED_KERNEL_OPEN": {
            "terminal": True,
            "terminal_name": "X1C_C45_ONE_BLOCK_DEFICIT_FROZEN__MIXED_KERNEL_NU_GEOMETRY_OPEN__NO_THEOREM_AUTHORITY",
            "active_hard_obligations": [],
        },
    },
}
