"""Native ORION-Q admission for Paper C / C1 all-m theorem evidence."""
from __future__ import annotations

_LOAD_PREFIX = "ORION_PAPER_C_C1_NATIVE_LOAD="
_DECISION_PREFIX = "ORION_PAPER_C_C1_NATIVE_DECISION="


def _decision(decision: str, next_phase: str) -> dict:
    record = {
        "decision": decision,
        "authority_scope": "FROZEN_STRUCTURAL_GRAMMAR_M_GE_5_ONLY",
        "cross_grammar_transfer": False,
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
    }
    code = (
        "import json;print('"
        + _DECISION_PREFIX
        + "'+json.dumps("
        + repr(record)
        + ",sort_keys=True,separators=(',',':')))"
    )
    return {
        "host_capability": "PYTHON",
        "payload": {"code": code, "cwd": ".", "timeout": 30},
        "result_contract": {
            "kind": "SHELL_JSON_TOKEN",
            "prefix": _DECISION_PREFIX,
            "required_payload_values": [
                {"path": ["decision"], "equals": decision},
                {
                    "path": ["authority_scope"],
                    "equals": "FROZEN_STRUCTURAL_GRAMMAR_M_GE_5_ONLY",
                },
                {"path": ["cross_grammar_transfer"], "equals": False},
                {"path": ["novelty_authority"], "equals": False},
                {"path": ["physical_quantum_advantage_claim"], "equals": False},
            ],
            "evidence_rules": [
                {
                    "evidence_key": "PAPER_C_C1_NATIVE_DECISION",
                    "path": ["decision"],
                    "transform": "STRING",
                }
            ],
        },
        "next_phase": next_phase,
    }


_LOAD_CODE = r'''
import hashlib,json
from pathlib import Path

source=json.loads(Path("research/extensions/orion-qg/PAPER_C_C1_ALL_M_DECISION_RESULTS_2026-08-24.json").read_text())
generic=json.loads(Path("development/orion-qg-regime-geometry/PAPER_C_C1_ALL_M_GENERIC_VERIFICATION_2026-08-24.json").read_text())

def canonical(value):
 return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False)

source_unsigned=dict(source);source_observed=source_unsigned.pop("result_digest",None)
generic_unsigned=dict(generic);generic_observed=generic_unsigned.pop("verification_digest",None)
out={
 "source_digest":source_observed==hashlib.sha256(canonical(source_unsigned).encode()).hexdigest(),
 "generic_digest":generic_observed==hashlib.sha256(canonical(generic_unsigned).encode()).hexdigest(),
 "positive":source.get("terminal")=="PAPER_C_C1_ALL_M_GE_5_FOUR_INDEX_DECISION_THEOREM_MACHINE_CORROBORATED__M4_SHARP_COUNTEREXAMPLE",
 "gates":all(source.get("gates",{}).values()),
 "generic":generic.get("decision")=="ACCEPT_EXACT_FROZEN_ALL_M_DECISION_THEOREM" and all(generic.get("checks",{}).values()),
 "m5_n2":source.get("complete_regressions",{}).get("m5_n2",{}).get("count")==11628,
 "m4_sharp":source.get("sharpness",{}).get("all_checks") is True,
 "parent":source.get("qg12_parent_binding",{}).get("all_checks") is True,
 "four_index":source.get("certificate",{}).get("maximum_clause_support_terms")==4,
 "scope":source.get("scientific_authority")=="EXACT_FROZEN_STRUCTURAL_GRAMMAR_M_GE_5_ONLY",
 "no_value":source.get("exact_value_authority") is False,
 "no_optimizer":source.get("optimizer_witness_authority") is False,
 "no_novelty":source.get("novelty_authority") is False,
 "no_physical":source.get("physical_quantum_advantage_claim") is False,
}
print("ORION_PAPER_C_C1_NATIVE_LOAD="+canonical(out))
'''

_ACCEPT_OBSERVATIONS = {
    "PAPER_C_C1_SOURCE_DIGEST": ["YES"],
    "PAPER_C_C1_GENERIC_DIGEST": ["YES"],
    "PAPER_C_C1_POSITIVE": ["YES"],
    "PAPER_C_C1_GATES": ["YES"],
    "PAPER_C_C1_GENERIC": ["YES"],
    "PAPER_C_C1_M5_N2": ["YES"],
    "PAPER_C_C1_M4_SHARP": ["YES"],
    "PAPER_C_C1_PARENT": ["YES"],
    "PAPER_C_C1_FOUR_INDEX": ["YES"],
    "PAPER_C_C1_SCOPE": ["YES"],
    "PAPER_C_C1_NO_VALUE": ["YES"],
    "PAPER_C_C1_NO_OPTIMIZER": ["YES"],
    "PAPER_C_C1_NO_NOVELTY": ["YES"],
    "PAPER_C_C1_NO_PHYSICAL": ["YES"],
}

PAPER_C_C1_ALL_M_CAMPAIGN_MANIFEST = {
    "schema": "ORION.ResearchCampaignManifest.v1",
    "campaign_id": "orion-paper-c:c1-all-m-decision-certificate",
    "claim_id": "orion-paper-c:c1-four-index-iff-m-ge-5",
    "initial_phase": "S0",
    "initial_observations": {"PAPER_C_C1_NEED": "YES"},
    "authority_ceiling": "FROZEN_STRUCTURAL_GRAMMAR_M_GE_5_ONLY",
    "protected_refs": [],
    "capabilities": {
        "paper_c_c1.load": {
            "host_capability": "PYTHON",
            "payload": {"code": _LOAD_CODE, "cwd": ".", "timeout": 30},
            "declared_read_paths": [
                "research/extensions/orion-qg/PAPER_C_C1_ALL_M_DECISION_RESULTS_2026-08-24.json",
                "development/orion-qg-regime-geometry/PAPER_C_C1_ALL_M_GENERIC_VERIFICATION_2026-08-24.json",
            ],
            "result_contract": {
                "kind": "SHELL_JSON_TOKEN",
                "prefix": _LOAD_PREFIX,
                "required_payload_values": [
                    {"path": ["no_novelty"], "equals": True},
                    {"path": ["no_physical"], "equals": True},
                ],
                "evidence_rules": [
                    {"evidence_key": "PAPER_C_C1_SOURCE_DIGEST", "path": ["source_digest"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "PAPER_C_C1_GENERIC_DIGEST", "path": ["generic_digest"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "PAPER_C_C1_POSITIVE", "path": ["positive"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "PAPER_C_C1_GATES", "path": ["gates"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "PAPER_C_C1_GENERIC", "path": ["generic"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "PAPER_C_C1_M5_N2", "path": ["m5_n2"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "PAPER_C_C1_M4_SHARP", "path": ["m4_sharp"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "PAPER_C_C1_PARENT", "path": ["parent"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "PAPER_C_C1_FOUR_INDEX", "path": ["four_index"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "PAPER_C_C1_SCOPE", "path": ["scope"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "PAPER_C_C1_NO_VALUE", "path": ["no_value"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "PAPER_C_C1_NO_OPTIMIZER", "path": ["no_optimizer"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "PAPER_C_C1_NO_NOVELTY", "path": ["no_novelty"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "PAPER_C_C1_NO_PHYSICAL", "path": ["no_physical"], "transform": "BOOL_YES_NO"},
                ],
            },
            "next_phase": "D0",
        },
        "paper_c_c1.accept": _decision(
            "ACCEPT_EXACT_FROZEN_ALL_M_DECISION_THEOREM", "ACCEPT_RECORDED"
        ),
        "paper_c_c1.reject": _decision("REJECT", "REJECT_RECORDED"),
    },
    "phases": {
        "S0": {
            "active_hard_obligations": ["PAPER_C_C1_LOAD"],
            "responsibility_hypotheses": [
                {
                    "hypothesis_id": "RESP:LOAD",
                    "expected_observations": {"PAPER_C_C1_NEED": ["YES"]},
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
                    "discharges_obligations": ["PAPER_C_C1_LOAD"],
                }
            ],
            "responsibility_bindings": {"RESP:LOAD": ["REV:WAIT"]},
            "selected_capabilities": {"COMPUTE:LOAD": "paper_c_c1.load"},
        },
        "D0": {
            "active_hard_obligations": [],
            "responsibility_hypotheses": [
                {"hypothesis_id": "RESP:ACCEPT", "expected_observations": _ACCEPT_OBSERVATIONS},
                {
                    "hypothesis_id": "RESP:REJECT",
                    "expected_observations": {"PAPER_C_C1_POSITIVE": ["NO"]},
                },
            ],
            "interface_checks": [
                {"check_id": "IFACE:FROZEN_SCOPE", "scope": "TRANSFER", "state": "PASS"},
                {"check_id": "IFACE:NO_NOVELTY", "scope": "AUTHORITY", "state": "PASS"},
            ],
            "revision_mechanics": [
                {
                    "mechanic_id": "REV:ACCEPT",
                    "kind": "ACCEPT_BOUNDED_THEOREM_EVIDENCE",
                    "read_coordinates": ["EVIDENCE", "COMPILER_GRAMMAR"],
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
                "REV:ACCEPT": "paper_c_c1.accept",
                "REV:REJECT": "paper_c_c1.reject",
            },
        },
        "ACCEPT_RECORDED": {
            "terminal": True,
            "terminal_name": "PAPER_C_C1_NATIVE_ACCEPT_RECORDED",
            "active_hard_obligations": [],
        },
        "REJECT_RECORDED": {
            "terminal": True,
            "terminal_name": "PAPER_C_C1_NATIVE_REJECT_RECORDED",
            "active_hard_obligations": [],
        },
    },
}
