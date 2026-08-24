"""Native admission for Paper A / A1 explicit MultiTag-TARE evidence."""
from __future__ import annotations

_LOAD = "ORION_PAPER_A_A1_NATIVE_LOAD="
_DECISION = "ORION_PAPER_A_A1_NATIVE_DECISION="
_SCOPE = "DEFINED_MULTITAG_TARE_M2_STRUCTURAL_GRAMMAR_ONLY"


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
                    "evidence_key": "PAPER_A_A1_NATIVE_DECISION",
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

source=json.loads(Path("research/extensions/orion-qg/PAPER_A_A1_MULTITAG_TARE_RESULTS_2026-08-24.json").read_text())
generic=json.loads(Path("development/orion-qg-regime-geometry/PAPER_A_A1_MULTITAG_TARE_GENERIC_2026-08-24.json").read_text())

def canonical(value):
 return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False)

s=dict(source);sd=s.pop("result_digest",None)
g=dict(generic);gd=g.pop("verification_digest",None)
restore=source.get("restore_ledger",{})
signatures=source.get("signature_ledger",{})
descent=source.get("descent_ledger",{})
parent=source.get("r6m_parent_binding",{})
out={
 "source_digest":sd==hashlib.sha256(canonical(s).encode()).hexdigest(),
 "generic_digest":gd==hashlib.sha256(canonical(g).encode()).hexdigest(),
 "positive":source.get("terminal")=="PAPER_A_A1_MULTITAG_TARE_ALL_N_SUPPORT_AT_MOST_CONSTRAINT_RANK__R6M_SHARP_BINARY_COROLLARY",
 "gates":all(source.get("gates",{}).values()),
 "generic":generic.get("decision")=="ACCEPT_MULTITAG_CONSTRAINT_RANK_THEOREM" and all(generic.get("checks",{}).values()),
 "restore":restore.get("row_count")==768 and restore.get("max_delta")==2 and restore.get("all_checks") is True,
 "signatures":len(signatures.get("rows",[]))==9 and signatures.get("rows",[])[-1].get("tag_count")==8 and signatures.get("all_checks") is True,
 "descent":descent.get("symbolic_all_dimensions") is True and descent.get("all_checks") is True,
 "parent":parent.get("sharp_kappa")==2 and parent.get("all_checks") is True,
 "scope":source.get("scientific_authority")=="DEFINED_MULTITAG_TARE_M2_STRUCTURAL_GRAMMAR_ONLY",
 "no_sharp":source.get("multitag_sharpness_authority") is False,
 "no_outside":source.get("outside_cone_support_necessity") is False,
 "no_transfer":source.get("generic_multitag_tare_transfer") is False and source.get("cross_unrelated_grammar_transfer") is False,
 "no_novelty":source.get("novelty_authority") is False,
 "no_physical":source.get("physical_quantum_advantage_claim") is False,
}
print("ORION_PAPER_A_A1_NATIVE_LOAD="+canonical(out))
'''

_NAMES = (
    "source_digest",
    "generic_digest",
    "positive",
    "gates",
    "generic",
    "restore",
    "signatures",
    "descent",
    "parent",
    "scope",
    "no_sharp",
    "no_outside",
    "no_transfer",
    "no_novelty",
    "no_physical",
)
_ACCEPT = {f"PAPER_A_A1_{name.upper()}": ["YES"] for name in _NAMES}

PAPER_A_A1_MULTITAG_CAMPAIGN_MANIFEST = {
    "schema": "ORION.ResearchCampaignManifest.v1",
    "campaign_id": "orion-paper-a:a1-explicit-multitag-tare",
    "claim_id": "orion-paper-a:a1-constraint-rank-normal-form",
    "initial_phase": "S0",
    "initial_observations": {"PAPER_A_A1_NEED": "YES"},
    "authority_ceiling": _SCOPE,
    "protected_refs": [],
    "capabilities": {
        "paper_a_a1.load": {
            "host_capability": "PYTHON",
            "payload": {"code": _LOAD_CODE, "cwd": ".", "timeout": 30},
            "declared_read_paths": [
                "research/extensions/orion-qg/PAPER_A_A1_MULTITAG_TARE_RESULTS_2026-08-24.json",
                "development/orion-qg-regime-geometry/PAPER_A_A1_MULTITAG_TARE_GENERIC_2026-08-24.json",
            ],
            "result_contract": {
                "kind": "SHELL_JSON_TOKEN",
                "prefix": _LOAD,
                "required_payload_values": [
                    {"path": ["no_sharp"], "equals": True},
                    {"path": ["no_outside"], "equals": True},
                    {"path": ["no_transfer"], "equals": True},
                    {"path": ["no_novelty"], "equals": True},
                    {"path": ["no_physical"], "equals": True},
                ],
                "evidence_rules": [
                    {
                        "evidence_key": f"PAPER_A_A1_{name.upper()}",
                        "path": [name],
                        "transform": "BOOL_YES_NO",
                    }
                    for name in _NAMES
                ],
            },
            "next_phase": "D0",
        },
        "paper_a_a1.accept": _record(
            "ACCEPT_MULTITAG_CONSTRAINT_RANK_THEOREM", "ACCEPT_RECORDED"
        ),
        "paper_a_a1.reject": _record("REJECT", "REJECT_RECORDED"),
    },
    "phases": {
        "S0": {
            "active_hard_obligations": ["PAPER_A_A1_LOAD"],
            "responsibility_hypotheses": [
                {
                    "hypothesis_id": "RESP:LOAD",
                    "expected_observations": {"PAPER_A_A1_NEED": ["YES"]},
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
                    "discharges_obligations": ["PAPER_A_A1_LOAD"],
                }
            ],
            "responsibility_bindings": {"RESP:LOAD": ["REV:WAIT"]},
            "selected_capabilities": {"COMPUTE:LOAD": "paper_a_a1.load"},
        },
        "D0": {
            "active_hard_obligations": [],
            "responsibility_hypotheses": [
                {"hypothesis_id": "RESP:ACCEPT", "expected_observations": _ACCEPT},
                {
                    "hypothesis_id": "RESP:REJECT",
                    "expected_observations": {"PAPER_A_A1_POSITIVE": ["NO"]},
                },
            ],
            "interface_checks": [
                {
                    "check_id": "IFACE:GRAMMAR_BOUND",
                    "scope": "MULTITAG_TARE_M2",
                    "state": "PASS",
                },
                {
                    "check_id": "IFACE:NO_DONOR_BROADENING",
                    "scope": "AUTHORITY",
                    "state": "PASS",
                },
            ],
            "revision_mechanics": [
                {
                    "mechanic_id": "REV:ACCEPT",
                    "kind": "ACCEPT_BOUNDED_THEOREM_EVIDENCE",
                    "read_coordinates": ["EVIDENCE", "GRAMMAR"],
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
                "REV:ACCEPT": "paper_a_a1.accept",
                "REV:REJECT": "paper_a_a1.reject",
            },
        },
        "ACCEPT_RECORDED": {
            "terminal": True,
            "terminal_name": "PAPER_A_A1_NATIVE_ACCEPT_RECORDED",
            "active_hard_obligations": [],
        },
        "REJECT_RECORDED": {
            "terminal": True,
            "terminal_name": "PAPER_A_A1_NATIVE_REJECT_RECORDED",
            "active_hard_obligations": [],
        },
    },
}
