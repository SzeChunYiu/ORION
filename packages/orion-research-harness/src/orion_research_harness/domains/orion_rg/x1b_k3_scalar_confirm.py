"""Non-authorizing harness campaign for independent X1-B k=3 confirmation."""
from __future__ import annotations

_PREFIX = "ORIONRG_X1B_K3_CONFIRM="

X1B_K3_SCALAR_CONFIRM_CAMPAIGN_MANIFEST = {
    "schema": "ORION.ResearchCampaignManifest.v1",
    "campaign_id": "orion-rg:x1b-k3-scalar-confirm",
    "claim_id": "orion-rg:x1b-c15-k3-scalar-residual",
    "description": (
        "Run the independently frozen full-multiplicity verifier for the C15 "
        "k=3 scalar residual. Finite confirmation only; no C15 theorem authority."
    ),
    "initial_phase": "S0",
    "initial_observations": {"X1B_K3_CONFIRMATION_NEEDED": "YES"},
    "authority_ceiling": "FINITE_CONFIRMATORY_RECONSTRUCTION_ONLY",
    "protected_refs": [],
    "capabilities": {
        "x1b.k3.confirm": {
            "host_capability": "SHELL",
            "payload": {
                "argv": [
                    "python",
                    "research/domains/orion-rg/x1b_k3_scalar_residual_confirm.py",
                ],
                "cwd": ".",
                "timeout": 180,
            },
            "declared_read_paths": [
                "research/domains/orion-rg/x1b_k3_scalar_residual_confirm.py",
                "research/domains/orion-rg/X1B_K3_SCALAR_CONFIRMATORY_PROTOCOL.md",
            ],
            "result_contract": {
                "kind": "SHELL_JSON_TOKEN",
                "prefix": _PREFIX,
                "required_payload_values": [
                    {"path": ["evidence_status"], "equals": "INDEPENDENT_CONFIRMATORY_RECONSTRUCTION"},
                    {"path": ["algorithm"], "equals": "FULL_MULTIPLICITY_CANONICAL_AUGMENTATION"},
                    {"path": ["exploratory_module_imported"], "equals": False},
                    {"path": ["support_stabilizer_quotient_used"], "equals": False},
                    {"path": ["primitive_replay_complete"], "equals": True},
                    {"path": ["consistent_common_rhs_orbit_count"], "equals": 0},
                    {"path": ["finite_confirmatory_reconstruction"], "equals": True},
                    {"path": ["c15_theorem_authority"], "equals": False},
                    {"path": ["infinite_family_authority"], "equals": False},
                    {"path": ["novelty_authority"], "equals": False},
                    {"path": ["scientific_authority"], "equals": False},
                ],
                "evidence_rules": [
                    {"evidence_key": "X1B_K3_FINITE_CONFIRMED", "path": ["finite_confirmatory_reconstruction"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "X1B_K3_CONSISTENT_ORBITS", "path": ["consistent_common_rhs_orbit_count"], "transform": "STRING"},
                ],
            },
            "next_phase": "FINITE_CONFIRMED",
        },
    },
    "phases": {
        "S0": {
            "active_hard_obligations": ["X1B_K3_INDEPENDENT_CONFIRMATION"],
            "responsibility_hypotheses": [
                {
                    "hypothesis_id": "RESP:X1B_K3_CONFIRM",
                    "expected_observations": {"X1B_K3_CONFIRMATION_NEEDED": ["YES"]},
                }
            ],
            "interface_checks": [
                {"check_id": "IFACE:X1B_K3_PROTOCOL_FROZEN", "scope": "PROSPECTIVE_CONFIRMATORY_PROTOCOL", "state": "PASS"},
                {"check_id": "IFACE:X1B_K3_NO_EXPLORATORY_IMPORT", "scope": "INDEPENDENCE", "state": "PASS"},
                {"check_id": "IFACE:X1B_K3_NO_THEOREM_PROMOTION", "scope": "AUTHORITY", "state": "PASS"},
            ],
            "revision_mechanics": [
                {
                    "mechanic_id": "REV:X1B_K3_WAIT_CONFIRMATION",
                    "kind": "WAIT_EVIDENCE",
                    "write_coordinates": ["FINITE_EVIDENCE"],
                    "preservation_obligations": [
                        "PRESERVE:NO_C15_THEOREM_AUTHORITY",
                        "PRESERVE:NOVELTY_OPEN",
                    ],
                    "cost": 0.1,
                }
            ],
            "computation_actions": [
                {
                    "action_id": "COMPUTE:X1B_K3_CONFIRM",
                    "kind": "VERIFY",
                    "expected_decision_value": 10.0,
                    "cost": 0.1,
                    "discharges_obligations": ["X1B_K3_INDEPENDENT_CONFIRMATION"],
                }
            ],
            "responsibility_bindings": {
                "RESP:X1B_K3_CONFIRM": ["REV:X1B_K3_WAIT_CONFIRMATION"]
            },
            "selected_capabilities": {
                "COMPUTE:X1B_K3_CONFIRM": "x1b.k3.confirm"
            },
        },
        "FINITE_CONFIRMED": {
            "terminal": True,
            "terminal_name": "X1B_K3_FINITE_CONFIRMATORY_RECONSTRUCTION__NO_C15_THEOREM_AUTHORITY",
            "active_hard_obligations": [],
        },
    },
}
