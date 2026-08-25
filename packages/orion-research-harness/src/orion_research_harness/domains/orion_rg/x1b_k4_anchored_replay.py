"""Harness replay for the prospectively frozen X1-B k=4 negative result."""
from __future__ import annotations

_PREFIX = "ORIONRG_X1B_K4_ANCHORED="

X1B_K4_ANCHORED_REPLAY_CAMPAIGN_MANIFEST = {
    "schema": "ORION.ResearchCampaignManifest.v1",
    "campaign_id": "orion-rg:x1b-k4-anchored-replay",
    "claim_id": "orion-rg:x1b-c15-k4-one-functional-anchor",
    "description": (
        "Replay the prospectively frozen 13-point k=4 anchored-scalar test and "
        "preserve its negative outcome: six exact quotient obstruction orbits."
    ),
    "initial_phase": "S0",
    "initial_observations": {"X1B_K4_REPLAY_NEEDED": "YES"},
    "authority_ceiling": "NEGATIVE_FINITE_STRATEGY_EVIDENCE_ONLY",
    "protected_refs": [],
    "capabilities": {
        "x1b.k4.replay": {
            "host_capability": "SHELL",
            "payload": {
                "argv": [
                    "python",
                    "research/domains/orion-rg/x1b_k4_13pt_anchored_scalar.py",
                ],
                "cwd": ".",
                "timeout": 180,
                "max_output_bytes": 400_000,
            },
            "declared_read_paths": [
                "research/domains/orion-rg/X1B_K4_13PT_ANCHORED_SCALAR_PROTOCOL.md",
                "research/domains/orion-rg/x1b_k4_13pt_anchored_scalar.py",
                "research/domains/orion-rg/X1B_K4_13PT_ANCHORED_SCALAR_FIRST_RESULT_2026-08-22.md",
            ],
            "result_contract": {
                "kind": "SHELL_JSON_TOKEN",
                "prefix": _PREFIX,
                "required_payload_values": [
                    {"path": ["evidence_status"], "equals": "PROSPECTIVE_FROZEN_PROTOCOL_EXECUTION"},
                    {"path": ["gl33_size"], "equals": 11232},
                    {"path": ["raw_candidate_count"], "equals": 170352},
                    {"path": ["canonical_no_short_zero_sum_orbit_count"], "equals": 22},
                    {"path": ["packing_exactly_two_orbit_count"], "equals": 15},
                    {"path": ["zero_closing_anchor_orbit_count"], "equals": 6},
                    {"path": ["admitted_canonical_code_digest"], "equals": "e8af9c90a8a0b3c2ded358c26a5bb23f21793e5b122fd876ca4e41297694c527"},
                    {"path": ["finite_k4_residual_closed_by_one_functional_anchor"], "equals": False},
                    {"path": ["c15_theorem_authority"], "equals": False},
                    {"path": ["novelty_authority"], "equals": False},
                    {"path": ["scientific_authority"], "equals": False},
                ],
                "evidence_rules": [
                    {"evidence_key": "X1B_K4_ONE_FUNCTIONAL_CLOSED", "path": ["finite_k4_residual_closed_by_one_functional_anchor"], "transform": "BOOL_YES_NO"},
                ],
            },
            "next_phase": "NEGATIVE_REPLAYED",
        },
    },
    "phases": {
        "S0": {
            "active_hard_obligations": ["X1B_K4_REPLAY_FROZEN_TEST"],
            "responsibility_hypotheses": [
                {
                    "hypothesis_id": "RESP:X1B_K4_REPLAY",
                    "expected_observations": {"X1B_K4_REPLAY_NEEDED": ["YES"]},
                }
            ],
            "interface_checks": [
                {"check_id": "IFACE:X1B_K4_PROTOCOL_PRECEDES_OUTCOME", "scope": "PROSPECTIVE_EVIDENCE", "state": "PASS"},
                {"check_id": "IFACE:X1B_K4_NEGATIVE_FIRST_CLASS", "scope": "NEGATIVE_HISTORY", "state": "PASS"},
                {"check_id": "IFACE:X1B_K4_NO_THEOREM_PROMOTION", "scope": "AUTHORITY", "state": "PASS"},
            ],
            "revision_mechanics": [
                {
                    "mechanic_id": "REV:X1B_K4_PRESERVE_OBSTRUCTION",
                    "kind": "DIAGNOSE",
                    "write_coordinates": ["NEGATIVE_EVIDENCE", "RESIDUAL"],
                    "preservation_obligations": [
                        "PRESERVE:SIX_OBSTRUCTION_ORBITS",
                        "PRESERVE:NO_C15_THEOREM_AUTHORITY",
                        "PRESERVE:NOVELTY_OPEN",
                    ],
                    "cost": 0.1,
                }
            ],
            "computation_actions": [
                {
                    "action_id": "COMPUTE:X1B_K4_REPLAY",
                    "kind": "VERIFY",
                    "expected_decision_value": 10.0,
                    "cost": 0.1,
                    "discharges_obligations": ["X1B_K4_REPLAY_FROZEN_TEST"],
                }
            ],
            "responsibility_bindings": {
                "RESP:X1B_K4_REPLAY": ["REV:X1B_K4_PRESERVE_OBSTRUCTION"]
            },
            "selected_capabilities": {
                "COMPUTE:X1B_K4_REPLAY": "x1b.k4.replay"
            },
        },
        "NEGATIVE_REPLAYED": {
            "terminal": True,
            "terminal_name": "X1B_K4_ONE_FUNCTIONAL_ANCHOR_REFUTED__SIX_OBSTRUCTIONS_REPLAYED",
            "active_hard_obligations": [],
        },
    },
}
