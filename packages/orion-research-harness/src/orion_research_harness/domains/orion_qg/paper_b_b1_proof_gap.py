"""Native admission for Paper B / B1 rank-only proof-gap evidence."""
from __future__ import annotations

_LOAD = "ORION_PAPER_B_B1_NATIVE_LOAD="
_DECISION = "ORION_PAPER_B_B1_NATIVE_DECISION="


def _record(decision: str, phase: str) -> dict:
    payload = {
        "decision": decision,
        "scope": "R6I_UNIT_OBJECTIVE_AND_DEFINED_ZSD_PROOF_CLASS_ONLY",
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
    }
    code = (
        "import json;print('"
        + _DECISION
        + "'+json.dumps("
        + repr(payload)
        + ",sort_keys=True,separators=(',',':')))"
    )
    return {
        "host_capability": "PYTHON",
        "payload": {"code": code, "cwd": ".", "timeout": 30},
        "result_contract": {
            "kind": "SHELL_JSON_TOKEN",
            "prefix": _DECISION,
            "required_payload_values": [
                {"path": ["decision"], "equals": decision},
                {
                    "path": ["scope"],
                    "equals": "R6I_UNIT_OBJECTIVE_AND_DEFINED_ZSD_PROOF_CLASS_ONLY",
                },
                {"path": ["novelty_authority"], "equals": False},
                {"path": ["physical_quantum_advantage_claim"], "equals": False},
            ],
            "evidence_rules": [
                {
                    "evidence_key": "PAPER_B_B1_NATIVE_DECISION",
                    "path": ["decision"],
                    "transform": "STRING",
                }
            ],
        },
        "next_phase": phase,
    }


_LOAD_CODE = r'''
import hashlib,json
from pathlib import Path

source=json.loads(Path("research/extensions/orion-qg/PAPER_B_B1_RANK_ONLY_PROOF_GAP_RESULTS_2026-08-24.json").read_text())
generic=json.loads(Path("development/orion-qg-regime-geometry/PAPER_B_B1_RANK_ONLY_PROOF_GAP_GENERIC_2026-08-24.json").read_text())

def canonical(value):
 return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False)

s=dict(source);sd=s.pop("result_digest",None)
g=dict(generic);gd=g.pop("verification_digest",None)
prod=source.get("production_instantiation",{})
products=source.get("direct_product",{}).get("rows",[])
out={
 "source_digest":sd==hashlib.sha256(canonical(s).encode()).hexdigest(),
 "generic_digest":gd==hashlib.sha256(canonical(g).encode()).hexdigest(),
 "positive":source.get("terminal")=="PAPER_B_B1_R6I_RANK_ONLY_CERTIFICATE_COMPLEXITY_5_VS_INTRINSIC_1__DIRECT_PRODUCT_GAP_4T_MACHINE_CORROBORATED",
 "gates":all(source.get("gates",{}).values()),
 "generic":generic.get("decision")=="ACCEPT_EXACT_RANK_ONLY_PROOF_GAP" and all(generic.get("checks",{}).values()),
 "production":prod.get("certificate_complexity")==5 and prod.get("intrinsic_support")==1 and prod.get("all_checks") is True,
 "product":len(products)==5 and products[-1].get("copies")==100 and products[-1].get("additive_gap")==400,
 "parents":all(row.get("all_checks") for row in source.get("parent_bindings",{}).values()),
 "nobroad":source.get("all_local_proof_systems_lower_bound") is False and source.get("all_syndrome_preserving_systems_lower_bound") is False,
 "scope":source.get("scientific_authority")=="R6I_UNIT_OBJECTIVE_AND_DEFINED_ZSD_PROOF_CLASS_ONLY",
 "no_novelty":source.get("novelty_authority") is False,
 "no_physical":source.get("physical_quantum_advantage_claim") is False,
}
print("ORION_PAPER_B_B1_NATIVE_LOAD="+canonical(out))
'''

_NAMES = (
    "source_digest",
    "generic_digest",
    "positive",
    "gates",
    "generic",
    "production",
    "product",
    "parents",
    "nobroad",
    "scope",
    "no_novelty",
    "no_physical",
)
_ACCEPT = {f"PAPER_B_B1_{name.upper()}": ["YES"] for name in _NAMES}

PAPER_B_B1_PROOF_GAP_CAMPAIGN_MANIFEST = {
    "schema": "ORION.ResearchCampaignManifest.v1",
    "campaign_id": "orion-paper-b:b1-rank-only-proof-gap",
    "claim_id": "orion-paper-b:b1-zsd5-vs-kappa1",
    "initial_phase": "S0",
    "initial_observations": {"PAPER_B_B1_NEED": "YES"},
    "authority_ceiling": "R6I_UNIT_OBJECTIVE_AND_DEFINED_ZSD_PROOF_CLASS_ONLY",
    "protected_refs": [],
    "capabilities": {
        "paper_b_b1.load": {
            "host_capability": "PYTHON",
            "payload": {"code": _LOAD_CODE, "cwd": ".", "timeout": 30},
            "declared_read_paths": [
                "research/extensions/orion-qg/PAPER_B_B1_RANK_ONLY_PROOF_GAP_RESULTS_2026-08-24.json",
                "development/orion-qg-regime-geometry/PAPER_B_B1_RANK_ONLY_PROOF_GAP_GENERIC_2026-08-24.json",
            ],
            "result_contract": {
                "kind": "SHELL_JSON_TOKEN",
                "prefix": _LOAD,
                "required_payload_values": [
                    {"path": ["nobroad"], "equals": True},
                    {"path": ["no_novelty"], "equals": True},
                    {"path": ["no_physical"], "equals": True},
                ],
                "evidence_rules": [
                    {
                        "evidence_key": f"PAPER_B_B1_{name.upper()}",
                        "path": [name],
                        "transform": "BOOL_YES_NO",
                    }
                    for name in _NAMES
                ],
            },
            "next_phase": "D0",
        },
        "paper_b_b1.accept": _record("ACCEPT_EXACT_RANK_ONLY_PROOF_GAP", "ACCEPT_RECORDED"),
        "paper_b_b1.reject": _record("REJECT", "REJECT_RECORDED"),
    },
    "phases": {
        "S0": {
            "active_hard_obligations": ["PAPER_B_B1_LOAD"],
            "responsibility_hypotheses": [
                {
                    "hypothesis_id": "RESP:LOAD",
                    "expected_observations": {"PAPER_B_B1_NEED": ["YES"]},
                }
            ],
            "interface_checks": [
                {"check_id": "IFACE:SERIALIZED", "scope": "EVIDENCE_BINDING", "state": "PASS"}
            ],
            "revision_mechanics": [
                {
                    "mechanic_id": "REV:WAIT",
                    "kind": "WAIT_EVIDENCE",
                    "write_coordinates": ["EVIDENCE"],
                    "cost": 0.1,
                }
            ],
            "computation_actions": [
                {
                    "action_id": "COMPUTE:LOAD",
                    "kind": "VERIFY",
                    "expected_decision_value": 5.0,
                    "cost": 0.1,
                    "discharges_obligations": ["PAPER_B_B1_LOAD"],
                }
            ],
            "responsibility_bindings": {"RESP:LOAD": ["REV:WAIT"]},
            "selected_capabilities": {"COMPUTE:LOAD": "paper_b_b1.load"},
        },
        "D0": {
            "active_hard_obligations": [],
            "responsibility_hypotheses": [
                {"hypothesis_id": "RESP:ACCEPT", "expected_observations": _ACCEPT},
                {
                    "hypothesis_id": "RESP:REJECT",
                    "expected_observations": {"PAPER_B_B1_POSITIVE": ["NO"]},
                },
            ],
            "interface_checks": [
                {"check_id": "IFACE:CLASS_BOUND", "scope": "PROOF_SYSTEM", "state": "PASS"},
                {"check_id": "IFACE:NO_NOVELTY", "scope": "AUTHORITY", "state": "PASS"},
            ],
            "revision_mechanics": [
                {
                    "mechanic_id": "REV:ACCEPT",
                    "kind": "ACCEPT_BOUNDED_THEOREM_EVIDENCE",
                    "read_coordinates": ["EVIDENCE", "PROOF_SYSTEM"],
                    "write_coordinates": ["BOUNDED_RESULT"],
                    "cost": 0.1,
                },
                {
                    "mechanic_id": "REV:REJECT",
                    "kind": "REJECT",
                    "read_coordinates": ["EVIDENCE"],
                    "write_coordinates": ["TERMINAL"],
                    "cost": 0.1,
                },
            ],
            "computation_actions": [
                {"action_id": "COMPUTE:NONE", "kind": "NONE", "expected_decision_value": 0.0, "cost": 1.0}
            ],
            "responsibility_bindings": {
                "RESP:ACCEPT": ["REV:ACCEPT"],
                "RESP:REJECT": ["REV:REJECT"],
            },
            "selected_capabilities": {
                "REV:ACCEPT": "paper_b_b1.accept",
                "REV:REJECT": "paper_b_b1.reject",
            },
        },
        "ACCEPT_RECORDED": {
            "terminal": True,
            "terminal_name": "PAPER_B_B1_NATIVE_ACCEPT_RECORDED",
            "active_hard_obligations": [],
        },
        "REJECT_RECORDED": {
            "terminal": True,
            "terminal_name": "PAPER_B_B1_NATIVE_REJECT_RECORDED",
            "active_hard_obligations": [],
        },
    },
}

