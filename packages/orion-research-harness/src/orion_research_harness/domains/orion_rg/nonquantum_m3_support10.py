"""Native admission for non-quantum M3 support-10 exclusion."""
from __future__ import annotations

_LOAD = "ORION_NONQUANTUM_M3_NATIVE_LOAD="
_DECISION = "ORION_NONQUANTUM_M3_NATIVE_DECISION="
_SCOPE = "BOUNDED_C5CUBED_SUPPORT10_EXCLUSION_ONLY"


def _record(decision: str, phase: str) -> dict:
    payload = {
        "decision": decision,
        "scope": _SCOPE,
        "support_11_plus_theorem_authority": False,
        "support_23_theorem_authority": False,
        "independent_external_replay_complete": False,
        "prospective_validation_authority": False,
        "c0_31_authority": False,
        "exact_d4_authority": False,
        "novelty_authority": False,
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
                {"path": ["support_11_plus_theorem_authority"], "equals": False},
                {"path": ["support_23_theorem_authority"], "equals": False},
                {"path": ["independent_external_replay_complete"], "equals": False},
                {"path": ["prospective_validation_authority"], "equals": False},
                {"path": ["c0_31_authority"], "equals": False},
                {"path": ["exact_d4_authority"], "equals": False},
                {"path": ["novelty_authority"], "equals": False},
            ],
            "evidence_rules": [
                {
                    "evidence_key": "NONQUANTUM_M3_NATIVE_DECISION",
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

source=json.loads(Path("research/orion-rg/NONQUANTUM_M3_SUPPORT10_REPLAY_RESULTS_2026-08-24.json").read_text())
generic=json.loads(Path("development/orion-rg-davenport/NONQUANTUM_M3_SUPPORT10_REPLAY_GENERIC_2026-08-24.json").read_text())

def canonical(value):
 return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False)

s=dict(source);sd=s.pop("result_digest",None)
g=dict(generic);gd=g.pop("verification_digest",None)
r=source.get("replay_ledger",{})
out={
 "source_digest":sd==hashlib.sha256(canonical(s).encode()).hexdigest(),
 "generic_digest":gd==hashlib.sha256(canonical(g).encode()).hexdigest(),
 "positive":source.get("terminal")=="NONQUANTUM_M3_C5CUBED_SUPPORT10_BOTH_DEFICIT_PATTERNS_EXCLUDED__OBSTRUCTION_SUPPORT_AT_LEAST11",
 "gates":all(source.get("gates",{}).values()),
 "generic":generic.get("decision")=="ACCEPT_SUPPORT10_EXCLUSION" and all(generic.get("checks",{}).values()),
 "patterns":source.get("pattern_ledger",{}).get("patterns")==[[1,3,6],[3,0,7]],
 "dual":r.get("all_checks") is True and all(row.get("u128")==row.get("bytes") and row.get("u128",{}).get("solutions")==0 for row in r.get("rows",[])),
 "scope":source.get("scientific_authority")=="BOUNDED_C5CUBED_SUPPORT10_EXCLUSION_ONLY",
 "bounded":source.get("bounded_support_le10_theorem_authority") is True,
 "no_support11":source.get("support_11_plus_theorem_authority") is False,
 "no_support23":source.get("support_23_theorem_authority") is False,
 "no_external":source.get("independent_external_replay_complete") is False,
 "no_prospective":source.get("prospective_validation_authority") is False,
 "no_c0":source.get("c0_31_authority") is False,
 "no_d4":source.get("exact_d4_authority") is False,
 "no_novelty":source.get("novelty_authority") is False,
 "no_quantum":source.get("quantum_claim") is False,
}
print("ORION_NONQUANTUM_M3_NATIVE_LOAD="+canonical(out))
'''

_NAMES = (
    "source_digest", "generic_digest", "positive", "gates", "generic", "patterns",
    "dual", "scope", "bounded", "no_support11", "no_support23", "no_external",
    "no_prospective", "no_c0", "no_d4", "no_novelty", "no_quantum",
)
_ACCEPT = {f"NONQUANTUM_M3_{name.upper()}": ["YES"] for name in _NAMES}

NONQUANTUM_M3_SUPPORT10_CAMPAIGN_MANIFEST = {
    "schema": "ORION.ResearchCampaignManifest.v1",
    "campaign_id": "orion-nonquantum-math:m3-support10-replay",
    "claim_id": "orion-nonquantum-math:m3-support10-exclusion",
    "initial_phase": "S0",
    "initial_observations": {"NONQUANTUM_M3_NEED": "YES"},
    "authority_ceiling": _SCOPE,
    "protected_refs": [],
    "capabilities": {
        "nonquantum_m3.load": {
            "host_capability": "PYTHON",
            "payload": {"code": _LOAD_CODE, "cwd": ".", "timeout": 30},
            "declared_read_paths": [
                "research/orion-rg/NONQUANTUM_M3_SUPPORT10_REPLAY_RESULTS_2026-08-24.json",
                "development/orion-rg-davenport/NONQUANTUM_M3_SUPPORT10_REPLAY_GENERIC_2026-08-24.json",
            ],
            "result_contract": {
                "kind": "SHELL_JSON_TOKEN",
                "prefix": _LOAD,
                "required_payload_values": [
                    {"path": ["no_support11"], "equals": True},
                    {"path": ["no_support23"], "equals": True},
                    {"path": ["no_external"], "equals": True},
                    {"path": ["no_prospective"], "equals": True},
                    {"path": ["no_c0"], "equals": True},
                    {"path": ["no_d4"], "equals": True},
                    {"path": ["no_novelty"], "equals": True},
                    {"path": ["no_quantum"], "equals": True},
                ],
                "evidence_rules": [
                    {
                        "evidence_key": f"NONQUANTUM_M3_{name.upper()}",
                        "path": [name],
                        "transform": "BOOL_YES_NO",
                    }
                    for name in _NAMES
                ],
            },
            "next_phase": "D0",
        },
        "nonquantum_m3.accept": _record("ACCEPT_SUPPORT10_EXCLUSION", "ACCEPT_RECORDED"),
        "nonquantum_m3.reject": _record("REJECT", "REJECT_RECORDED"),
    },
    "phases": {
        "S0": {
            "active_hard_obligations": ["NONQUANTUM_M3_LOAD"],
            "responsibility_hypotheses": [
                {"hypothesis_id": "RESP:LOAD", "expected_observations": {"NONQUANTUM_M3_NEED": ["YES"]}}
            ],
            "interface_checks": [
                {"check_id": "IFACE:SERIALIZED", "scope": "EVIDENCE_BINDING", "state": "PASS"}
            ],
            "revision_mechanics": [
                {"mechanic_id": "REV:WAIT", "kind": "WAIT_EVIDENCE", "write_coordinates": ["EVIDENCE"], "cost": 0.1}
            ],
            "computation_actions": [
                {"action_id": "COMPUTE:LOAD", "kind": "VERIFY", "expected_decision_value": 5.0, "cost": 0.1, "discharges_obligations": ["NONQUANTUM_M3_LOAD"]}
            ],
            "responsibility_bindings": {"RESP:LOAD": ["REV:WAIT"]},
            "selected_capabilities": {"COMPUTE:LOAD": "nonquantum_m3.load"},
        },
        "D0": {
            "active_hard_obligations": [],
            "responsibility_hypotheses": [
                {"hypothesis_id": "RESP:ACCEPT", "expected_observations": _ACCEPT},
                {"hypothesis_id": "RESP:REJECT", "expected_observations": {"NONQUANTUM_M3_POSITIVE": ["NO"]}},
            ],
            "interface_checks": [
                {"check_id": "IFACE:POST_OUTCOME", "scope": "AUTHORITY", "state": "PASS"},
                {"check_id": "IFACE:BOUNDED", "scope": "AUTHORITY", "state": "PASS"},
            ],
            "revision_mechanics": [
                {"mechanic_id": "REV:ACCEPT", "kind": "ACCEPT_BOUNDED_THEOREM_EVIDENCE", "read_coordinates": ["EVIDENCE", "AUTHORITY_GRAPH"], "write_coordinates": ["BOUNDED_RESULT"], "cost": 0.1},
                {"mechanic_id": "REV:REJECT", "kind": "REJECT", "read_coordinates": ["EVIDENCE"], "write_coordinates": ["TERMINAL"], "cost": 0.1},
            ],
            "computation_actions": [
                {"action_id": "COMPUTE:NONE", "kind": "NONE", "expected_decision_value": 0.0, "cost": 1.0}
            ],
            "responsibility_bindings": {"RESP:ACCEPT": ["REV:ACCEPT"], "RESP:REJECT": ["REV:REJECT"]},
            "selected_capabilities": {"REV:ACCEPT": "nonquantum_m3.accept", "REV:REJECT": "nonquantum_m3.reject"},
        },
        "ACCEPT_RECORDED": {"terminal": True, "terminal_name": "NONQUANTUM_M3_NATIVE_ACCEPT_RECORDED", "active_hard_obligations": []},
        "REJECT_RECORDED": {"terminal": True, "terminal_name": "NONQUANTUM_M3_NATIVE_REJECT_RECORDED", "active_hard_obligations": []},
    },
}
