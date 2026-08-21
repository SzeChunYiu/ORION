"""QG-12 native ORION-Q admission for the SixLCU all-instance P0 theorem."""
from __future__ import annotations

_LOAD = "ORIONQG_QG12_NATIVE_LOAD="
_DECISION = "ORIONQG_QG12_NATIVE_DECISION="


def _record(decision: str, next_phase: str) -> dict:
    payload = {
        "decision": decision,
        "scope": "SIXLCU_ONLY",
        "cross_family_transfer": False,
        "novelty_authority": False,
        "scientific_authority": False,
        "physical_quantum_advantage_claim": False,
    }
    code = (
        "import json; print('" + _DECISION + "' + json.dumps(" + repr(payload)
        + ", sort_keys=True, separators=(',', ':')))"
    )
    return {
        "host_capability": "PYTHON",
        "payload": {"code": code, "cwd": ".", "timeout": 30},
        "result_contract": {
            "kind": "SHELL_JSON_TOKEN", "prefix": _DECISION,
            "required_payload_values": [
                {"path": ["decision"], "equals": decision},
                {"path": ["scope"], "equals": "SIXLCU_ONLY"},
                {"path": ["cross_family_transfer"], "equals": False},
                {"path": ["novelty_authority"], "equals": False},
                {"path": ["scientific_authority"], "equals": False},
            ],
            "evidence_rules": [
                {"evidence_key": "QG12_NATIVE_DECISION", "path": ["decision"], "transform": "STRING"}
            ],
        },
        "next_phase": next_phase,
    }


_LOAD_CODE = r'''
import hashlib, json
from pathlib import Path

a = json.loads(Path("artifacts/orion-qg-qg12-sixlcu-p0-theorem.json").read_text())
g = json.loads(Path("artifacts/orion-qg-qg12-generic-verification.json").read_text())
u = dict(a); observed = u.pop("result_digest", None)
canon = json.dumps(u, sort_keys=True, separators=(",", ":"), allow_nan=False)
out = {
 "positive": a.get("terminal") == "QG12_SIXLCU_P0_ALL_INSTANCE_THEOREM_MACHINE_CHECKED",
 "digest": observed == hashlib.sha256(canon.encode()).hexdigest(),
 "gates": all(a.get("gates", {}).values()),
 "generic": g.get("decision") == "ACCEPT" and all(g.get("checks", {}).values()),
 "partition203": a.get("production_gain_decomposition", {}).get("partition_count") == 203,
 "shape11": a.get("production_gain_decomposition", {}).get("shape_count") == 11,
 "all_shapes": a.get("proof_ledger", {}).get("all_11_shapes_covered") is True,
 "converse": a.get("proof_ledger", {}).get("converse_explicit_partition_witnesses") is True,
 "n1": a.get("blind_complete_regression", {}).get("n1_count") == 729,
 "n2": a.get("blind_complete_regression", {}).get("n2_count") == 38760,
 "zero_mismatch": a.get("blind_complete_regression", {}).get("zero_mismatches") is True,
 "qg4_bound": a.get("qg4_binding", {}).get("all_bound") is True,
 "no_external": a.get("network_access") is False and a.get("chemistry_sources_read") is False and a.get("protected_subject_read") is False,
 "novelty_false": a.get("novelty_authority") is False,
}
print("ORIONQG_QG12_NATIVE_LOAD=" + json.dumps(out, sort_keys=True, separators=(",", ":")))
'''

_ACCEPT = {
    "QG12_POSITIVE": ["YES"], "QG12_DIGEST": ["YES"], "QG12_GATES": ["YES"],
    "QG12_GENERIC": ["YES"], "QG12_PARTITIONS": ["YES"], "QG12_SHAPES": ["YES"],
    "QG12_ALL_SHAPES": ["YES"], "QG12_CONVERSE": ["YES"], "QG12_N1": ["YES"],
    "QG12_N2": ["YES"], "QG12_ZERO_MISMATCH": ["YES"], "QG12_QG4_BOUND": ["YES"],
    "QG12_NO_EXTERNAL": ["YES"], "QG12_NOVELTY_FALSE": ["YES"],
}

QG12_SIXLCU_P0_CAMPAIGN_MANIFEST = {
    "schema": "ORION.ResearchCampaignManifest.v1",
    "campaign_id": "orion-qg:qg12-sixlcu-p0-theorem",
    "claim_id": "orion-qg:qg12-sixlcu-p0-all-instance",
    "initial_phase": "S0",
    "initial_observations": {"QG12_NEED": "YES"},
    "authority_ceiling": "NON_AUTHORIZING_SIXLCU_THEOREM_EVIDENCE",
    "protected_refs": [],
    "capabilities": {
        "qg12.load": {
            "host_capability": "PYTHON",
            "payload": {"code": _LOAD_CODE, "cwd": ".", "timeout": 30},
            "declared_read_paths": [
                "artifacts/orion-qg-qg12-sixlcu-p0-theorem.json",
                "artifacts/orion-qg-qg12-generic-verification.json",
            ],
            "result_contract": {
                "kind": "SHELL_JSON_TOKEN", "prefix": _LOAD,
                "required_payload_values": [{"path": ["novelty_false"], "equals": True}],
                "evidence_rules": [
                    {"evidence_key": "QG12_POSITIVE", "path": ["positive"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG12_DIGEST", "path": ["digest"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG12_GATES", "path": ["gates"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG12_GENERIC", "path": ["generic"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG12_PARTITIONS", "path": ["partition203"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG12_SHAPES", "path": ["shape11"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG12_ALL_SHAPES", "path": ["all_shapes"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG12_CONVERSE", "path": ["converse"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG12_N1", "path": ["n1"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG12_N2", "path": ["n2"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG12_ZERO_MISMATCH", "path": ["zero_mismatch"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG12_QG4_BOUND", "path": ["qg4_bound"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG12_NO_EXTERNAL", "path": ["no_external"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG12_NOVELTY_FALSE", "path": ["novelty_false"], "transform": "BOOL_YES_NO"},
                ],
            },
            "next_phase": "D0",
        },
        "qg12.accept": _record("ACCEPT_ALL_INSTANCE_P0_THEOREM", "ACCEPT_RECORDED"),
        "qg12.reject": _record("REJECT", "REJECT_RECORDED"),
    },
    "phases": {
        "S0": {
            "active_hard_obligations": ["QG12_LOAD"],
            "responsibility_hypotheses": [{"hypothesis_id": "RESP:LOAD", "expected_observations": {"QG12_NEED": ["YES"]}}],
            "interface_checks": [{"check_id": "IFACE:SERIALIZED", "scope": "EVIDENCE_BINDING", "state": "PASS"}],
            "revision_mechanics": [{"mechanic_id": "REV:WAIT", "kind": "WAIT_EVIDENCE", "write_coordinates": ["EVIDENCE"], "cost": 0.1}],
            "computation_actions": [{"action_id": "COMPUTE:LOAD", "kind": "VERIFY", "expected_decision_value": 5.0, "cost": 0.1, "discharges_obligations": ["QG12_LOAD"]}],
            "responsibility_bindings": {"RESP:LOAD": ["REV:WAIT"]},
            "selected_capabilities": {"COMPUTE:LOAD": "qg12.load"},
        },
        "D0": {
            "active_hard_obligations": [],
            "responsibility_hypotheses": [
                {"hypothesis_id": "RESP:ACCEPT", "expected_observations": _ACCEPT},
                {"hypothesis_id": "RESP:REJECT", "expected_observations": {"QG12_POSITIVE": ["NO"]}},
            ],
            "interface_checks": [
                {"check_id": "IFACE:SIXLCU_ONLY", "scope": "TRANSFER", "state": "PASS"},
                {"check_id": "IFACE:NO_NOVELTY_LAUNDER", "scope": "AUTHORITY", "state": "PASS"},
            ],
            "revision_mechanics": [
                {"mechanic_id": "REV:ACCEPT", "kind": "ACCEPT_BOUNDED_THEOREM_EVIDENCE", "read_coordinates": ["EVIDENCE", "COMPILER_FAMILY"], "write_coordinates": ["BOUNDED_RESULT"], "cost": 0.1},
                {"mechanic_id": "REV:REJECT", "kind": "REJECT", "read_coordinates": ["EVIDENCE"], "write_coordinates": ["TERMINAL"], "cost": 0.1},
            ],
            "computation_actions": [{"action_id": "COMPUTE:NONE", "kind": "NONE", "expected_decision_value": 0.0, "cost": 1.0}],
            "responsibility_bindings": {"RESP:ACCEPT": ["REV:ACCEPT"], "RESP:REJECT": ["REV:REJECT"]},
            "selected_capabilities": {"REV:ACCEPT": "qg12.accept", "REV:REJECT": "qg12.reject"},
        },
        "ACCEPT_RECORDED": {"terminal": True, "terminal_name": "QG12_NATIVE_ACCEPT_RECORDED", "active_hard_obligations": []},
        "REJECT_RECORDED": {"terminal": True, "terminal_name": "QG12_NATIVE_REJECT_RECORDED", "active_hard_obligations": []},
    },
}
