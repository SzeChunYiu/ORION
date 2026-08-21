"""Native ORION-Q admission for QG-13 V2 combined-edit mining."""
from __future__ import annotations

_LOAD = "ORIONQG_QG13V2_NATIVE_LOAD="
_DEC = "ORIONQG_QG13V2_NATIVE_DECISION="


def _decision(decision: str, next_phase: str):
    payload = {
        "decision": decision,
        "new_theorem_authority": False,
        "novelty_authority": False,
        "support4_theorem_authority": False,
    }
    code = "import json;print('" + _DEC + "'+json.dumps(" + repr(payload) + ",sort_keys=True,separators=(',',':')))"
    return {
        "host_capability": "PYTHON",
        "payload": {"code": code, "cwd": ".", "timeout": 30},
        "result_contract": {
            "kind": "SHELL_JSON_TOKEN",
            "prefix": _DEC,
            "required_payload_values": [
                {"path": ["decision"], "equals": decision},
                {"path": ["new_theorem_authority"], "equals": False},
                {"path": ["novelty_authority"], "equals": False},
                {"path": ["support4_theorem_authority"], "equals": False},
            ],
            "evidence_rules": [{"evidence_key": "QG13V2_DECISION", "path": ["decision"], "transform": "STRING"}],
        },
        "next_phase": next_phase,
    }


_LOAD_CODE = r'''
import hashlib,json
from pathlib import Path
a=json.loads(Path('artifacts/orion-qg-qg13v2-combined-edit.json').read_text())
g=json.loads(Path('artifacts/orion-qg-qg13v2-generic-verification.json').read_text())
u=dict(a);obs=u.pop('result_digest');canon=json.dumps(u,sort_keys=True,separators=(',',':'),allow_nan=False)
t=a.get('terminal','')
out={
 'digest':obs==hashlib.sha256(canon.encode()).hexdigest(),
 'generic':g.get('decision')=='ACCEPT' and all(g.get('checks',{}).values()),
 'binding':a.get('production_signature_binding',{}).get('all_exact') is True,
 'candidate':t=='QG13V2_SUPPORT4_CANDIDATE',
 'obstruction':t=='QG13V2_MINIMAL_COMBINED_EDIT_OBSTRUCTION',
 'resource':t=='QG13V2_RESOURCE_COUNTEREXAMPLE',
 'bounded_terminal':t in {'QG13V2_SUPPORT4_CANDIDATE','QG13V2_MINIMAL_COMBINED_EDIT_OBSTRUCTION','QG13V2_RESOURCE_COUNTEREXAMPLE'},
 'authority':a.get('new_theorem_authority') is False and a.get('novelty_authority') is False,
 'no_parent_open':a.get('parent_receipts_opened_during_synthesis') is False,
 'no_sensitive':a.get('chemistry_sources_read') is False and a.get('protected_subject_read') is False and a.get('network_access') is False,
}
print('ORIONQG_QG13V2_NATIVE_LOAD='+json.dumps(out,sort_keys=True,separators=(',',':')))
'''

COMMON = {
    "QG13V2_DIGEST": ["YES"],
    "QG13V2_GENERIC": ["YES"],
    "QG13V2_BINDING": ["YES"],
    "QG13V2_BOUNDED": ["YES"],
    "QG13V2_AUTH": ["YES"],
    "QG13V2_NO_PARENT": ["YES"],
    "QG13V2_NO_SENSITIVE": ["YES"],
}

QG13V2_COMBINED_EDIT_CAMPAIGN_MANIFEST = {
    "schema": "ORION.ResearchCampaignManifest.v1",
    "campaign_id": "orion-qg:qg13v2-r6i-combined-edits",
    "claim_id": "orion-qg:qg13v2-support5-tightness-edit-grammar",
    "initial_phase": "S0",
    "initial_observations": {"QG13V2_NEED": "YES"},
    "authority_ceiling": "NON_AUTHORIZING_COMBINED_EDIT_EVIDENCE",
    "protected_refs": [],
    "capabilities": {
        "qg13v2.load": {
            "host_capability": "PYTHON",
            "payload": {"code": _LOAD_CODE, "cwd": ".", "timeout": 30},
            "declared_read_paths": [
                "artifacts/orion-qg-qg13v2-combined-edit.json",
                "artifacts/orion-qg-qg13v2-generic-verification.json",
            ],
            "result_contract": {
                "kind": "SHELL_JSON_TOKEN",
                "prefix": _LOAD,
                "required_payload_values": [{"path": ["authority"], "equals": True}],
                "evidence_rules": [
                    {"evidence_key": "QG13V2_DIGEST", "path": ["digest"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG13V2_GENERIC", "path": ["generic"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG13V2_BINDING", "path": ["binding"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG13V2_CANDIDATE", "path": ["candidate"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG13V2_OBSTRUCTION", "path": ["obstruction"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG13V2_RESOURCE", "path": ["resource"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG13V2_BOUNDED", "path": ["bounded_terminal"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG13V2_AUTH", "path": ["authority"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG13V2_NO_PARENT", "path": ["no_parent_open"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG13V2_NO_SENSITIVE", "path": ["no_sensitive"], "transform": "BOOL_YES_NO"},
                ],
            },
            "next_phase": "D0",
        },
        "qg13v2.candidate": _decision("ACCEPT_SUPPORT4_CANDIDATE", "CANDIDATE_RECORDED"),
        "qg13v2.obstruction": _decision("ACCEPT_MINIMAL_OBSTRUCTION", "OBSTRUCTION_RECORDED"),
        "qg13v2.resource": _decision("ACCEPT_RESOURCE_BOUNDARY", "RESOURCE_RECORDED"),
        "qg13v2.reject": _decision("REJECT", "REJECT_RECORDED"),
    },
    "phases": {
        "S0": {
            "active_hard_obligations": ["QG13V2_LOAD"],
            "responsibility_hypotheses": [{"hypothesis_id": "RESP:LOAD", "expected_observations": {"QG13V2_NEED": ["YES"]}}],
            "interface_checks": [{"check_id": "IFACE:SERIALIZED", "scope": "EVIDENCE_BINDING", "state": "PASS"}],
            "revision_mechanics": [{"mechanic_id": "REV:WAIT", "kind": "WAIT_EVIDENCE", "write_coordinates": ["EVIDENCE"], "cost": 0.1}],
            "computation_actions": [{"action_id": "COMPUTE:LOAD", "kind": "VERIFY", "expected_decision_value": 5.0, "cost": 0.1, "discharges_obligations": ["QG13V2_LOAD"]}],
            "responsibility_bindings": {"RESP:LOAD": ["REV:WAIT"]},
            "selected_capabilities": {"COMPUTE:LOAD": "qg13v2.load"},
        },
        "D0": {
            "active_hard_obligations": [],
            "responsibility_hypotheses": [
                {"hypothesis_id": "RESP:CAND", "expected_observations": {**COMMON, "QG13V2_CANDIDATE": ["YES"]}},
                {"hypothesis_id": "RESP:OBS", "expected_observations": {**COMMON, "QG13V2_OBSTRUCTION": ["YES"]}},
                {"hypothesis_id": "RESP:RES", "expected_observations": {**COMMON, "QG13V2_RESOURCE": ["YES"]}},
                {"hypothesis_id": "RESP:REJECT", "expected_observations": {"QG13V2_BOUNDED": ["NO"]}},
            ],
            "interface_checks": [
                {"check_id": "IFACE:NO_SELF_AUTH", "scope": "AUTHORITY", "state": "PASS"},
                {"check_id": "IFACE:NEGATIVE_FIRST_CLASS", "scope": "TERMINAL", "state": "PASS"},
            ],
            "revision_mechanics": [
                {"mechanic_id": "REV:CAND", "kind": "ACCEPT_BOUNDED_CANDIDATE", "read_coordinates": ["EVIDENCE"], "write_coordinates": ["BOUNDED_RESULT"], "cost": 0.1},
                {"mechanic_id": "REV:OBS", "kind": "ACCEPT_BOUNDED_OBSTRUCTION", "read_coordinates": ["EVIDENCE"], "write_coordinates": ["BOUNDED_RESULT"], "cost": 0.1},
                {"mechanic_id": "REV:RES", "kind": "ACCEPT_RESOURCE_BOUNDARY", "read_coordinates": ["EVIDENCE"], "write_coordinates": ["BOUNDED_RESULT"], "cost": 0.1},
                {"mechanic_id": "REV:REJECT", "kind": "REJECT", "read_coordinates": ["EVIDENCE"], "write_coordinates": ["TERMINAL"], "cost": 0.1},
            ],
            "computation_actions": [{"action_id": "COMPUTE:NONE", "kind": "NONE", "expected_decision_value": 0.0, "cost": 1.0}],
            "responsibility_bindings": {
                "RESP:CAND": ["REV:CAND"], "RESP:OBS": ["REV:OBS"], "RESP:RES": ["REV:RES"], "RESP:REJECT": ["REV:REJECT"]
            },
            "selected_capabilities": {
                "REV:CAND": "qg13v2.candidate", "REV:OBS": "qg13v2.obstruction", "REV:RES": "qg13v2.resource", "REV:REJECT": "qg13v2.reject"
            },
        },
        "CANDIDATE_RECORDED": {"terminal": True, "terminal_name": "QG13V2_NATIVE_CANDIDATE_RECORDED", "active_hard_obligations": []},
        "OBSTRUCTION_RECORDED": {"terminal": True, "terminal_name": "QG13V2_NATIVE_OBSTRUCTION_RECORDED", "active_hard_obligations": []},
        "RESOURCE_RECORDED": {"terminal": True, "terminal_name": "QG13V2_NATIVE_RESOURCE_RECORDED", "active_hard_obligations": []},
        "REJECT_RECORDED": {"terminal": True, "terminal_name": "QG13V2_NATIVE_REJECT_RECORDED", "active_hard_obligations": []},
    },
}
