"""QG-8 native ORION-Q admission for the objective-indexed support-two cone."""
from __future__ import annotations

_LOAD = "ORIONQG_QG8_NATIVE_LOAD="
_DECISION = "ORIONQG_QG8_NATIVE_DECISION="


def _decision_capability(decision: str, next_phase: str) -> dict:
    payload = {
        "decision": decision,
        "outside_cone_semantics": "NOT_EQUAL_SUPPORT3_REQUIRED",
        "global_boundary_sharpness": "OPEN",
        "novelty_authority": False,
        "scientific_authority": False,
    }
    code = (
        "import json; print('" + _DECISION + "' + json.dumps("
        + repr(payload) + ", sort_keys=True, separators=(',', ':')))"
    )
    return {
        "host_capability": "PYTHON",
        "payload": {"code": code, "cwd": ".", "timeout": 30},
        "result_contract": {
            "kind": "SHELL_JSON_TOKEN",
            "prefix": _DECISION,
            "required_payload_values": [
                {"path": ["decision"], "equals": decision},
                {"path": ["outside_cone_semantics"], "equals": "NOT_EQUAL_SUPPORT3_REQUIRED"},
                {"path": ["global_boundary_sharpness"], "equals": "OPEN"},
                {"path": ["novelty_authority"], "equals": False},
                {"path": ["scientific_authority"], "equals": False},
            ],
            "evidence_rules": [
                {"evidence_key": "QG8_NATIVE_DECISION", "path": ["decision"], "transform": "STRING"}
            ],
        },
        "next_phase": next_phase,
    }


_LOAD_CODE = r'''
import hashlib, json
from pathlib import Path

a = json.loads(Path("artifacts/orion-qg-qg8-support-phase.json").read_text())
g = json.loads(Path("artifacts/orion-qg-qg8-generic-verification.json").read_text())
u = dict(a); observed = u.pop("result_digest", None)
canon = json.dumps(u, sort_keys=True, separators=(",", ":"), allow_nan=False)
q = a.get("qg2_binding", {}); objs = q.get("objectives", {})
out = {
 "positive": a.get("terminal") == "QG8_OBJECTIVE_INDEXED_SUPPORT2_CONE_ALL_N_MACHINE_CHECKED",
 "digest": observed == hashlib.sha256(canon.encode()).hexdigest(),
 "gates": all(a.get("gates", {}).values()),
 "proof": all(a.get("proof_audit", {}).values()),
 "generic": g.get("decision") == "ACCEPT" and all(g.get("checks", {}).values()),
 "cone": a.get("support2_cone", {}).get("conditions") == ["t_c >= 2*t_r", "t_nc >= 2*t_r"],
 "o0": objs.get("O0", {}).get("classification", {}).get("inside_support2_cone") is True,
 "o1": objs.get("O1", {}).get("classification", {}).get("inside_support2_cone") is False,
 "o2": objs.get("O2", {}).get("classification", {}).get("inside_support2_cone") is True,
 "o1_control": bool(q.get("support3_witnesses")),
 "boundary_open": a.get("support2_cone", {}).get("global_boundary_sharpness") == "OPEN",
 "novelty": a.get("novelty_authority") is False,
}
print("ORIONQG_QG8_NATIVE_LOAD=" + json.dumps(out, sort_keys=True, separators=(",", ":")))
'''

_ACCEPT_OBS = {
    "QG8_POSITIVE": ["YES"], "QG8_DIGEST": ["YES"], "QG8_GATES": ["YES"],
    "QG8_PROOF": ["YES"], "QG8_GENERIC": ["YES"], "QG8_CONE": ["YES"],
    "QG8_O0": ["YES"], "QG8_O1": ["YES"], "QG8_O2": ["YES"],
    "QG8_O1_CONTROL": ["YES"], "QG8_BOUNDARY_OPEN": ["YES"], "QG8_NOVELTY": ["YES"],
}

QG8_SUPPORT_PHASE_CAMPAIGN_MANIFEST = {
    "schema": "ORION.ResearchCampaignManifest.v1",
    "campaign_id": "orion-qg:qg8-objective-support-phase",
    "claim_id": "orion-qg:qg8-support2-cone-all-n",
    "initial_phase": "S0",
    "initial_observations": {"QG8_NEED": "YES"},
    "authority_ceiling": "NON_AUTHORIZING_OBJECTIVE_PHASE_EVIDENCE",
    "protected_refs": [],
    "capabilities": {
        "qg8.load": {
            "host_capability": "PYTHON",
            "payload": {"code": _LOAD_CODE, "cwd": ".", "timeout": 30},
            "declared_read_paths": [
                "artifacts/orion-qg-qg8-support-phase.json",
                "artifacts/orion-qg-qg8-generic-verification.json",
            ],
            "result_contract": {
                "kind": "SHELL_JSON_TOKEN", "prefix": _LOAD,
                "required_payload_values": [{"path": ["novelty"], "equals": True}],
                "evidence_rules": [
                    {"evidence_key": "QG8_POSITIVE", "path": ["positive"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG8_DIGEST", "path": ["digest"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG8_GATES", "path": ["gates"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG8_PROOF", "path": ["proof"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG8_GENERIC", "path": ["generic"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG8_CONE", "path": ["cone"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG8_O0", "path": ["o0"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG8_O1", "path": ["o1"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG8_O2", "path": ["o2"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG8_O1_CONTROL", "path": ["o1_control"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG8_BOUNDARY_OPEN", "path": ["boundary_open"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG8_NOVELTY", "path": ["novelty"], "transform": "BOOL_YES_NO"},
                ],
            },
            "next_phase": "D0",
        },
        "qg8.accept": _decision_capability("ACCEPT_SUPPORT2_CONE", "ACCEPT_RECORDED"),
        "qg8.reject": _decision_capability("REJECT", "REJECT_RECORDED"),
    },
    "phases": {
        "S0": {
            "active_hard_obligations": ["QG8_LOAD"],
            "responsibility_hypotheses": [{"hypothesis_id": "RESP:LOAD", "expected_observations": {"QG8_NEED": ["YES"]}}],
            "interface_checks": [{"check_id": "IFACE:SERIALIZED", "scope": "EVIDENCE_BINDING", "state": "PASS"}],
            "revision_mechanics": [{"mechanic_id": "REV:WAIT", "kind": "WAIT_EVIDENCE", "write_coordinates": ["EVIDENCE"], "cost": 0.1}],
            "computation_actions": [{"action_id": "COMPUTE:LOAD", "kind": "VERIFY", "expected_decision_value": 5.0, "cost": 0.1, "discharges_obligations": ["QG8_LOAD"]}],
            "responsibility_bindings": {"RESP:LOAD": ["REV:WAIT"]},
            "selected_capabilities": {"COMPUTE:LOAD": "qg8.load"},
        },
        "D0": {
            "active_hard_obligations": [],
            "responsibility_hypotheses": [
                {"hypothesis_id": "RESP:ACCEPT", "expected_observations": _ACCEPT_OBS},
                {"hypothesis_id": "RESP:REJECT", "expected_observations": {"QG8_POSITIVE": ["NO"]}},
            ],
            "interface_checks": [
                {"check_id": "IFACE:OBJECTIVE_ID", "scope": "OBJECTIVE", "state": "PASS"},
                {"check_id": "IFACE:NO_OUTSIDE_LAUNDER", "scope": "AUTHORITY", "state": "PASS"},
            ],
            "revision_mechanics": [
                {"mechanic_id": "REV:ACCEPT", "kind": "ACCEPT_BOUNDED_THEOREM_EVIDENCE", "read_coordinates": ["EVIDENCE", "OBJECTIVE"], "write_coordinates": ["BOUNDED_RESULT"], "cost": 0.1},
                {"mechanic_id": "REV:REJECT", "kind": "REJECT", "read_coordinates": ["EVIDENCE"], "write_coordinates": ["TERMINAL"], "cost": 0.1},
            ],
            "computation_actions": [{"action_id": "COMPUTE:NONE", "kind": "NONE", "expected_decision_value": 0.0, "cost": 1.0}],
            "responsibility_bindings": {"RESP:ACCEPT": ["REV:ACCEPT"], "RESP:REJECT": ["REV:REJECT"]},
            "selected_capabilities": {"REV:ACCEPT": "qg8.accept", "REV:REJECT": "qg8.reject"},
        },
        "ACCEPT_RECORDED": {"terminal": True, "terminal_name": "QG8_NATIVE_ACCEPT_RECORDED", "active_hard_obligations": []},
        "REJECT_RECORDED": {"terminal": True, "terminal_name": "QG8_NATIVE_REJECT_RECORDED", "active_hard_obligations": []},
    },
}
