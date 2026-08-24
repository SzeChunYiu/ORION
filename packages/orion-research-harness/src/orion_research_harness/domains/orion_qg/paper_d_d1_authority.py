"""Native admission for Paper D / D1 stratified-authority evidence."""
from __future__ import annotations

_LOAD = "ORION_PAPER_D_D1_NATIVE_LOAD="
_DECISION = "ORION_PAPER_D_D1_NATIVE_DECISION="
_SCOPE = "FORMAL_STRATIFIED_CERTIFICATE_CALCULUS_AND_BOUND_PARENT_INSTANTIATIONS_ONLY"


def _record(decision: str, phase: str) -> dict:
    payload = {
        "decision": decision,
        "scope": _SCOPE,
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
                {"path": ["scope"], "equals": _SCOPE},
                {"path": ["novelty_authority"], "equals": False},
                {"path": ["physical_quantum_advantage_claim"], "equals": False},
            ],
            "evidence_rules": [
                {
                    "evidence_key": "PAPER_D_D1_NATIVE_DECISION",
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

source=json.loads(Path("research/extensions/orion-qg/PAPER_D_D1_AUTHORITY_CALCULUS_RESULTS_2026-08-24.json").read_text())
generic=json.loads(Path("development/orion-qg-regime-geometry/PAPER_D_D1_AUTHORITY_CALCULUS_GENERIC_2026-08-24.json").read_text())

def canonical(value):
 return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False)

s=dict(source);sd=s.pop("result_digest",None)
g=dict(generic);gd=g.pop("verification_digest",None)
q=source.get("qg5_instantiation",{})
c=source.get("paper_c_noninterference",{})
out={
 "source_digest":sd==hashlib.sha256(canonical(s).encode()).hexdigest(),
 "generic_digest":gd==hashlib.sha256(canonical(g).encode()).hexdigest(),
 "positive":source.get("terminal")=="PAPER_D_D1_STRATIFIED_AUTHORITY_CALCULUS_EXACT_MINIMAL_RETRACTION__QG5_COUNTEREXAMPLE_LOCALIZED__SIXLCU_NONINTERFERENCE_CORROBORATED",
 "gates":all(source.get("gates",{}).values()),
 "generic":generic.get("decision")=="ACCEPT_STRATIFIED_AUTHORITY_CALCULUS" and all(generic.get("checks",{}).values()),
 "formal":source.get("formal_ledger",{}).get("total_models_checked")==254253 and source.get("formal_ledger",{}).get("failure_count")==0,
 "qg5":q.get("all_checks") is True and q.get("exact_retraction")==["ORIGINAL_CLOSED_FORM_EXACTNESS","ORIGINAL_REGIME_LABEL"],
 "paper_c":c.get("all_checks") is True and c.get("paper_d_ownership_claim") is False,
 "denominator":q.get("original_benchmark")=={"exact":9545,"total":9546,"errors":1,"universal_exactness":False},
 "no_prospective":source.get("prospective_repair_authority") is False and q.get("qg5b_is_prospective_confirmation") is False,
 "no_second":source.get("second_independent_forecasting_family") is False,
 "no_framework":source.get("real_static_framework_integration") is False,
 "scope":source.get("scientific_authority")=="FORMAL_STRATIFIED_CERTIFICATE_CALCULUS_AND_BOUND_PARENT_INSTANTIATIONS_ONLY",
 "no_novelty":source.get("novelty_authority") is False and source.get("generic_fixed_point_novelty_authority") is False,
 "no_physical":source.get("physical_quantum_advantage_claim") is False,
}
print("ORION_PAPER_D_D1_NATIVE_LOAD="+canonical(out))
'''

_NAMES = (
    "source_digest",
    "generic_digest",
    "positive",
    "gates",
    "generic",
    "formal",
    "qg5",
    "paper_c",
    "denominator",
    "no_prospective",
    "no_second",
    "no_framework",
    "scope",
    "no_novelty",
    "no_physical",
)
_ACCEPT = {f"PAPER_D_D1_{name.upper()}": ["YES"] for name in _NAMES}

PAPER_D_D1_AUTHORITY_CAMPAIGN_MANIFEST = {
    "schema": "ORION.ResearchCampaignManifest.v1",
    "campaign_id": "orion-paper-d:d1-stratified-authority",
    "claim_id": "orion-paper-d:d1-minimal-retraction",
    "initial_phase": "S0",
    "initial_observations": {"PAPER_D_D1_NEED": "YES"},
    "authority_ceiling": _SCOPE,
    "protected_refs": [],
    "capabilities": {
        "paper_d_d1.load": {
            "host_capability": "PYTHON",
            "payload": {"code": _LOAD_CODE, "cwd": ".", "timeout": 30},
            "declared_read_paths": [
                "research/extensions/orion-qg/PAPER_D_D1_AUTHORITY_CALCULUS_RESULTS_2026-08-24.json",
                "development/orion-qg-regime-geometry/PAPER_D_D1_AUTHORITY_CALCULUS_GENERIC_2026-08-24.json",
            ],
            "result_contract": {
                "kind": "SHELL_JSON_TOKEN",
                "prefix": _LOAD,
                "required_payload_values": [
                    {"path": ["denominator"], "equals": True},
                    {"path": ["no_prospective"], "equals": True},
                    {"path": ["no_second"], "equals": True},
                    {"path": ["no_framework"], "equals": True},
                    {"path": ["no_novelty"], "equals": True},
                    {"path": ["no_physical"], "equals": True},
                ],
                "evidence_rules": [
                    {
                        "evidence_key": f"PAPER_D_D1_{name.upper()}",
                        "path": [name],
                        "transform": "BOOL_YES_NO",
                    }
                    for name in _NAMES
                ],
            },
            "next_phase": "D0",
        },
        "paper_d_d1.accept": _record(
            "ACCEPT_STRATIFIED_AUTHORITY_CALCULUS", "ACCEPT_RECORDED"
        ),
        "paper_d_d1.reject": _record("REJECT", "REJECT_RECORDED"),
    },
    "phases": {
        "S0": {
            "active_hard_obligations": ["PAPER_D_D1_LOAD"],
            "responsibility_hypotheses": [
                {
                    "hypothesis_id": "RESP:LOAD",
                    "expected_observations": {"PAPER_D_D1_NEED": ["YES"]},
                }
            ],
            "interface_checks": [
                {
                    "check_id": "IFACE:SERIALIZED",
                    "scope": "EVIDENCE_BINDING",
                    "state": "PASS",
                }
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
                    "discharges_obligations": ["PAPER_D_D1_LOAD"],
                }
            ],
            "responsibility_bindings": {"RESP:LOAD": ["REV:WAIT"]},
            "selected_capabilities": {"COMPUTE:LOAD": "paper_d_d1.load"},
        },
        "D0": {
            "active_hard_obligations": [],
            "responsibility_hypotheses": [
                {"hypothesis_id": "RESP:ACCEPT", "expected_observations": _ACCEPT},
                {
                    "hypothesis_id": "RESP:REJECT",
                    "expected_observations": {"PAPER_D_D1_POSITIVE": ["NO"]},
                },
            ],
            "interface_checks": [
                {
                    "check_id": "IFACE:POST_OUTCOME_BOUND",
                    "scope": "AUTHORITY",
                    "state": "PASS",
                },
                {
                    "check_id": "IFACE:OWNER_BOUND",
                    "scope": "CROSS_FAMILY",
                    "state": "PASS",
                },
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
                "REV:ACCEPT": "paper_d_d1.accept",
                "REV:REJECT": "paper_d_d1.reject",
            },
        },
        "ACCEPT_RECORDED": {
            "terminal": True,
            "terminal_name": "PAPER_D_D1_NATIVE_ACCEPT_RECORDED",
            "active_hard_obligations": [],
        },
        "REJECT_RECORDED": {
            "terminal": True,
            "terminal_name": "PAPER_D_D1_NATIVE_REJECT_RECORDED",
            "active_hard_obligations": [],
        },
    },
}
