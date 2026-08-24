"""Native admission for the non-quantum C_5^3 Davenport tail corridor."""
from __future__ import annotations

_LOAD = "ORION_NONQUANTUM_M1_NATIVE_LOAD="
_DECISION = "ORION_NONQUANTUM_M1_NATIVE_DECISION="
_SCOPE = "DERIVED_C5_CUBED_GENERALIZED_DAVENPORT_TAIL_THEOREM_ONLY"


def _record(decision: str, phase: str) -> dict:
    payload = {
        "decision": decision,
        "scope": _SCOPE,
        "exact_d4_authority": False,
        "support_23_theorem_authority": False,
        "novelty_authority": False,
        "quantum_claim": False,
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
                {"path": ["scope"], "equals": _SCOPE},
                {"path": ["exact_d4_authority"], "equals": False},
                {"path": ["support_23_theorem_authority"], "equals": False},
                {"path": ["novelty_authority"], "equals": False},
                {"path": ["quantum_claim"], "equals": False},
            ],
            "evidence_rules": [
                {
                    "evidence_key": "NONQUANTUM_M1_NATIVE_DECISION",
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

source=json.loads(Path("research/orion-rg/NONQUANTUM_M1_DK_TAIL_CORRIDOR_RESULTS_2026-08-24.json").read_text())
generic=json.loads(Path("development/orion-rg-davenport/NONQUANTUM_M1_DK_TAIL_CORRIDOR_GENERIC_2026-08-24.json").read_text())

def canonical(value):
 return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False)

s=dict(source);sd=s.pop("result_digest",None)
g=dict(generic);gd=g.pop("verification_digest",None)
r=source.get("recurrence_ledger",{})
u=source.get("support_frontier",{})
out={
 "source_digest":sd==hashlib.sha256(canonical(s).encode()).hexdigest(),
 "generic_digest":gd==hashlib.sha256(canonical(g).encode()).hexdigest(),
 "positive":source.get("terminal")=="NONQUANTUM_M1_C5CUBED_ALL_K_GE4_ONE_UNIT_CORRIDOR__D4_30_IMPLIES_EXACT_TAIL_5K_PLUS10",
 "gates":all(source.get("gates",{}).values()),
 "generic":generic.get("decision")=="ACCEPT_C5_CUBED_TAIL_CORRIDOR" and all(generic.get("checks",{}).values()),
 "parents":source.get("parent_ledger",{}).get("all_checks") is True,
 "recurrence":r.get("all_checks") is True and r.get("max_k_checked")==10000,
 "d4_open":source.get("exact_d4_authority") is False and source.get("theorem",{}).get("current_exact_gate")=="D_4 in {30,31}",
 "support_nonaggregable":u.get("used_in_tail_proof") is False and u.get("aggregable_as_theorem") is False and source.get("support_23_theorem_authority") is False,
 "no_d4_31_tail":source.get("d4_31_determines_tail") is False and source.get("theorem",{}).get("d4_31_tail_consequence")=="NOT_DETERMINED",
 "scope":source.get("scientific_authority")=="DERIVED_C5_CUBED_GENERALIZED_DAVENPORT_TAIL_THEOREM_ONLY",
 "no_novelty":source.get("novelty_authority") is False and source.get("generic_recurrence_novelty_authority") is False,
 "no_quantum":source.get("quantum_claim") is False,
}
print("ORION_NONQUANTUM_M1_NATIVE_LOAD="+canonical(out))
'''

_NAMES = (
    "source_digest",
    "generic_digest",
    "positive",
    "gates",
    "generic",
    "parents",
    "recurrence",
    "d4_open",
    "support_nonaggregable",
    "no_d4_31_tail",
    "scope",
    "no_novelty",
    "no_quantum",
)
_ACCEPT = {f"NONQUANTUM_M1_{name.upper()}": ["YES"] for name in _NAMES}

NONQUANTUM_M1_TAIL_CORRIDOR_CAMPAIGN_MANIFEST = {
    "schema": "ORION.ResearchCampaignManifest.v1",
    "campaign_id": "orion-nonquantum-math:m1-dk-tail-corridor",
    "claim_id": "orion-nonquantum-math:m1-c5cubed-tail-theorem",
    "initial_phase": "S0",
    "initial_observations": {"NONQUANTUM_M1_NEED": "YES"},
    "authority_ceiling": _SCOPE,
    "protected_refs": [],
    "capabilities": {
        "nonquantum_m1.load": {
            "host_capability": "PYTHON",
            "payload": {"code": _LOAD_CODE, "cwd": ".", "timeout": 30},
            "declared_read_paths": [
                "research/orion-rg/NONQUANTUM_M1_DK_TAIL_CORRIDOR_RESULTS_2026-08-24.json",
                "development/orion-rg-davenport/NONQUANTUM_M1_DK_TAIL_CORRIDOR_GENERIC_2026-08-24.json",
            ],
            "result_contract": {
                "kind": "SHELL_JSON_TOKEN",
                "prefix": _LOAD,
                "required_payload_values": [
                    {"path": ["d4_open"], "equals": True},
                    {"path": ["support_nonaggregable"], "equals": True},
                    {"path": ["no_d4_31_tail"], "equals": True},
                    {"path": ["no_novelty"], "equals": True},
                    {"path": ["no_quantum"], "equals": True},
                ],
                "evidence_rules": [
                    {
                        "evidence_key": f"NONQUANTUM_M1_{name.upper()}",
                        "path": [name],
                        "transform": "BOOL_YES_NO",
                    }
                    for name in _NAMES
                ],
            },
            "next_phase": "D0",
        },
        "nonquantum_m1.accept": _record("ACCEPT_C5_CUBED_TAIL_CORRIDOR", "ACCEPT_RECORDED"),
        "nonquantum_m1.reject": _record("REJECT", "REJECT_RECORDED"),
    },
    "phases": {
        "S0": {
            "active_hard_obligations": ["NONQUANTUM_M1_LOAD"],
            "responsibility_hypotheses": [
                {
                    "hypothesis_id": "RESP:LOAD",
                    "expected_observations": {"NONQUANTUM_M1_NEED": ["YES"]},
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
                    "discharges_obligations": ["NONQUANTUM_M1_LOAD"],
                }
            ],
            "responsibility_bindings": {"RESP:LOAD": ["REV:WAIT"]},
            "selected_capabilities": {"COMPUTE:LOAD": "nonquantum_m1.load"},
        },
        "D0": {
            "active_hard_obligations": [],
            "responsibility_hypotheses": [
                {"hypothesis_id": "RESP:ACCEPT", "expected_observations": _ACCEPT},
                {
                    "hypothesis_id": "RESP:REJECT",
                    "expected_observations": {"NONQUANTUM_M1_POSITIVE": ["NO"]},
                },
            ],
            "interface_checks": [
                {"check_id": "IFACE:D4_OPEN", "scope": "AUTHORITY", "state": "PASS"},
                {"check_id": "IFACE:NONQUANTUM_OWNER", "scope": "OWNERSHIP", "state": "PASS"},
            ],
            "revision_mechanics": [
                {
                    "mechanic_id": "REV:ACCEPT",
                    "kind": "ACCEPT_BOUNDED_THEOREM_EVIDENCE",
                    "read_coordinates": ["EVIDENCE", "AUTHORITY_GRAPH"],
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
                {
                    "action_id": "COMPUTE:NONE",
                    "kind": "NONE",
                    "expected_decision_value": 0.0,
                    "cost": 1.0,
                }
            ],
            "responsibility_bindings": {
                "RESP:ACCEPT": ["REV:ACCEPT"],
                "RESP:REJECT": ["REV:REJECT"],
            },
            "selected_capabilities": {
                "REV:ACCEPT": "nonquantum_m1.accept",
                "REV:REJECT": "nonquantum_m1.reject",
            },
        },
        "ACCEPT_RECORDED": {
            "terminal": True,
            "terminal_name": "NONQUANTUM_M1_NATIVE_ACCEPT_RECORDED",
            "active_hard_obligations": [],
        },
        "REJECT_RECORDED": {
            "terminal": True,
            "terminal_name": "NONQUANTUM_M1_NATIVE_REJECT_RECORDED",
            "active_hard_obligations": [],
        },
    },
}
