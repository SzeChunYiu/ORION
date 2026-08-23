"""Non-authorizing harness campaign for the assembled X1-B C15 candidate proof."""
from __future__ import annotations

_PREFIX = "ORIONRG_X1B_C15_AUDIT="

X1B_C15_CANDIDATE_PROOF_AUDIT_CAMPAIGN_MANIFEST = {
    "schema": "ORION.ResearchCampaignManifest.v1",
    "campaign_id": "orion-rg:x1b-c15-candidate-proof-audit",
    "claim_id": "orion-rg:x1b-c15-davenport-43-candidate",
    "description": (
        "Bind the exact committed C15 proof spine and reconstruct the corrected "
        "greedy residual tree. A passing audit remains explicitly non-authorizing."
    ),
    "initial_phase": "S0",
    "initial_observations": {"X1B_C15_PROOF_AUDIT_NEEDED": "YES"},
    "authority_ceiling": "INTERNAL_CANDIDATE_PROOF_AUDIT_ONLY",
    "protected_refs": [],
    "capabilities": {
        "x1b.c15.audit": {
            "host_capability": "SHELL",
            "payload": {
                "argv": [
                    "python",
                    "research/domains/orion-rg/x1b_c15_candidate_proof_audit.py",
                ],
                "cwd": ".",
                "timeout": 60,
            },
            "declared_read_paths": [
                "research/domains/orion-rg/x1b_c15_candidate_proof_audit.py",
                "research/domains/orion-rg/X1B_C15_DAVENPORT_43_CANDIDATE_THEOREM_2026-08-22.md",
                "research/domains/orion-rg/X1B_K3_10PT_RESIDUAL_CLOSURE_THEOREM_2026-08-22.md",
                "research/domains/orion-rg/X1B_K4_13PT_RESIDUAL_CLOSURE_THEOREM_2026-08-22.md",
                "research/domains/orion-rg/X1B_C15_14PT_NO_SHORT_RAW_CONFIRM_RESULT_2026-08-22.md",
                "research/domains/orion-rg/X1B_C15_16PT_RAW_QUOTIENT_RESULT_2026-08-22.md",
                "research/domains/orion-rg/X1B_GEROLDINGER_YANG_PGROUP_SCALARIZATION_DONOR_AUDIT_2026-08-22.md",
                "research/domains/orion-rg/X1B_C15_DONOR_NUMERICAL_SPINE_AUDIT_2026-08-22.md",
            ],
            "result_contract": {
                "kind": "SHELL_JSON_TOKEN",
                "prefix": _PREFIX,
                "required_payload_values": [
                    {"path": ["candidate_claim"], "equals": "D(C_15^3)=43"},
                    {"path": ["artifact_integrity_ok"], "equals": True},
                    {"path": ["residual_tree_ok"], "equals": True},
                    {"path": ["all_internal_audit_gates"], "equals": True},
                    {"path": ["external_peer_review_complete"], "equals": False},
                    {"path": ["novelty_authority"], "equals": False},
                    {"path": ["scientific_authority"], "equals": False},
                    {"path": ["publication_authority"], "equals": False},
                    {"path": ["infinite_family_authority"], "equals": False},
                ],
                "evidence_rules": [
                    {"evidence_key": "X1B_C15_ARTIFACT_INTEGRITY", "path": ["artifact_integrity_ok"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "X1B_C15_RESIDUAL_TREE_AUDITED", "path": ["residual_tree_ok"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "X1B_C15_INTERNAL_AUDIT_PASS", "path": ["all_internal_audit_gates"], "transform": "BOOL_YES_NO"},
                ],
            },
            "next_phase": "INTERNAL_AUDIT_RECORDED",
        },
    },
    "phases": {
        "S0": {
            "active_hard_obligations": ["X1B_C15_BIND_AND_AUDIT_PROOF_SPINE"],
            "responsibility_hypotheses": [
                {
                    "hypothesis_id": "RESP:X1B_C15_INTERNAL_AUDIT",
                    "expected_observations": {"X1B_C15_PROOF_AUDIT_NEEDED": ["YES"]},
                }
            ],
            "interface_checks": [
                {"check_id": "IFACE:X1B_C15_EXACT_ARTIFACT_BINDING", "scope": "EVIDENCE_BINDING", "state": "PASS"},
                {"check_id": "IFACE:X1B_C15_CORRECTED_RESIDUAL_TREE", "scope": "PROOF_EXHAUSTIVENESS", "state": "PASS"},
                {"check_id": "IFACE:X1B_C15_NO_SELF_PROMOTION", "scope": "AUTHORITY", "state": "PASS"},
            ],
            "revision_mechanics": [
                {
                    "mechanic_id": "REV:X1B_C15_PRESERVE_CANDIDATE_STATUS",
                    "kind": "VERIFY_ONLY",
                    "read_coordinates": ["EVIDENCE", "SEMANTICS"],
                    "write_coordinates": ["BOUNDED_RESULT"],
                    "preservation_obligations": [
                        "PRESERVE:EXTERNAL_REVIEW_PENDING",
                        "PRESERVE:NOVELTY_OPEN",
                        "PRESERVE:NO_PUBLICATION_AUTHORITY",
                    ],
                    "cost": 0.1,
                }
            ],
            "computation_actions": [
                {
                    "action_id": "COMPUTE:X1B_C15_AUDIT",
                    "kind": "VERIFY",
                    "expected_decision_value": 10.0,
                    "cost": 0.1,
                    "discharges_obligations": ["X1B_C15_BIND_AND_AUDIT_PROOF_SPINE"],
                }
            ],
            "responsibility_bindings": {
                "RESP:X1B_C15_INTERNAL_AUDIT": ["REV:X1B_C15_PRESERVE_CANDIDATE_STATUS"]
            },
            "selected_capabilities": {
                "COMPUTE:X1B_C15_AUDIT": "x1b.c15.audit"
            },
        },
        "INTERNAL_AUDIT_RECORDED": {
            "terminal": True,
            "terminal_name": "X1B_C15_CANDIDATE_PROOF_INTERNAL_AUDIT_PASSED__EXTERNAL_REVIEW_PENDING",
            "active_hard_obligations": [],
        },
    },
}
