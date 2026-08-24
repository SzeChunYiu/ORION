"""Native ORION-Q admission for Paper C / C2 separation evidence."""
from __future__ import annotations

_LOAD = "ORION_PAPER_C_C2_NATIVE_LOAD="
_DECISION = "ORION_PAPER_C_C2_NATIVE_DECISION="


def _record(decision: str, phase: str) -> dict:
    payload = {
        "decision": decision,
        "scope": "FROZEN_STRUCTURAL_GRAMMAR_CONSTRUCTION_ONLY",
        "cross_grammar_transfer": False,
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
                    "equals": "FROZEN_STRUCTURAL_GRAMMAR_CONSTRUCTION_ONLY",
                },
                {"path": ["cross_grammar_transfer"], "equals": False},
                {"path": ["novelty_authority"], "equals": False},
                {"path": ["physical_quantum_advantage_claim"], "equals": False},
            ],
            "evidence_rules": [
                {"evidence_key": "PAPER_C_C2_NATIVE_DECISION", "path": ["decision"], "transform": "STRING"}
            ],
        },
        "next_phase": phase,
    }


_LOAD_CODE = r'''
import hashlib,json
from pathlib import Path

source=json.loads(Path("research/extensions/orion-qg/PAPER_C_C2_PAIR_GAIN_VALUE_SEPARATION_RESULTS_2026-08-24.json").read_text())
generic=json.loads(Path("development/orion-qg-regime-geometry/PAPER_C_C2_PAIR_GAIN_VALUE_GENERIC_VERIFICATION_2026-08-24.json").read_text())

def canonical(value):
 return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False)

s=dict(source);sd=s.pop("result_digest",None)
g=dict(generic);gd=g.pop("verification_digest",None)
direct=source.get("direct_exact_checks",{}).get("rows",[])
out={
 "source_digest":sd==hashlib.sha256(canonical(s).encode()).hexdigest(),
 "generic_digest":gd==hashlib.sha256(canonical(g).encode()).hexdigest(),
 "positive":source.get("terminal")=="PAPER_C_C2_COMPLETE_PAIR_INFORMATION_VALUE_GAP_2T_MINUS_1_UNBOUNDED__OPTIMIZER_TRIPLE_VS_PAIR_SEPARATION",
 "gates":all(source.get("gates",{}).values()),
 "generic":generic.get("decision")=="ACCEPT_PAIR_INFORMATION_VALUE_AND_OPTIMIZER_SEPARATION" and all(generic.get("checks",{}).values()),
 "pair_same":source.get("gates",{}).get("pair_information_exactly_identical") is True,
 "local_complete":source.get("gates",{}).get("local_partition_proof_complete") is True,
 "direct":len(direct)==2 and all(row.get("pair_information_identical") and row.get("A_formula_exact") and row.get("B_formula_exact") for row in direct),
 "unbounded":source.get("unbounded_additive_value_ambiguity") is True,
 "value_false":source.get("complete_pair_information_value_sufficient") is False,
 "optimizer_false":source.get("complete_pair_information_optimizer_sufficient") is False,
 "parent":source.get("c1_parent_binding",{}).get("all_checks") is True,
 "scope":source.get("scientific_authority")=="EXACT_FROZEN_STRUCTURAL_GRAMMAR_CONSTRUCTION_ONLY",
 "no_novelty":source.get("novelty_authority") is False,
 "no_physical":source.get("physical_quantum_advantage_claim") is False,
}
print("ORION_PAPER_C_C2_NATIVE_LOAD="+canonical(out))
'''

_ACCEPT = {
    "PAPER_C_C2_SOURCE_DIGEST": ["YES"],
    "PAPER_C_C2_GENERIC_DIGEST": ["YES"],
    "PAPER_C_C2_POSITIVE": ["YES"],
    "PAPER_C_C2_GATES": ["YES"],
    "PAPER_C_C2_GENERIC": ["YES"],
    "PAPER_C_C2_PAIR_SAME": ["YES"],
    "PAPER_C_C2_LOCAL_COMPLETE": ["YES"],
    "PAPER_C_C2_DIRECT": ["YES"],
    "PAPER_C_C2_UNBOUNDED": ["YES"],
    "PAPER_C_C2_VALUE_FALSE": ["YES"],
    "PAPER_C_C2_OPTIMIZER_FALSE": ["YES"],
    "PAPER_C_C2_PARENT": ["YES"],
    "PAPER_C_C2_SCOPE": ["YES"],
    "PAPER_C_C2_NO_NOVELTY": ["YES"],
    "PAPER_C_C2_NO_PHYSICAL": ["YES"],
}

PAPER_C_C2_PAIR_VALUE_CAMPAIGN_MANIFEST = {
    "schema": "ORION.ResearchCampaignManifest.v1",
    "campaign_id": "orion-paper-c:c2-pair-value-separation",
    "claim_id": "orion-paper-c:c2-unbounded-pair-fiber-value-gap",
    "initial_phase": "S0",
    "initial_observations": {"PAPER_C_C2_NEED": "YES"},
    "authority_ceiling": "FROZEN_STRUCTURAL_GRAMMAR_CONSTRUCTION_ONLY",
    "protected_refs": [],
    "capabilities": {
        "paper_c_c2.load": {
            "host_capability": "PYTHON",
            "payload": {"code": _LOAD_CODE, "cwd": ".", "timeout": 30},
            "declared_read_paths": [
                "research/extensions/orion-qg/PAPER_C_C2_PAIR_GAIN_VALUE_SEPARATION_RESULTS_2026-08-24.json",
                "development/orion-qg-regime-geometry/PAPER_C_C2_PAIR_GAIN_VALUE_GENERIC_VERIFICATION_2026-08-24.json",
            ],
            "result_contract": {
                "kind": "SHELL_JSON_TOKEN",
                "prefix": _LOAD,
                "required_payload_values": [
                    {"path": ["no_novelty"], "equals": True},
                    {"path": ["no_physical"], "equals": True},
                ],
                "evidence_rules": [
                    {"evidence_key": "PAPER_C_C2_SOURCE_DIGEST", "path": ["source_digest"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "PAPER_C_C2_GENERIC_DIGEST", "path": ["generic_digest"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "PAPER_C_C2_POSITIVE", "path": ["positive"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "PAPER_C_C2_GATES", "path": ["gates"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "PAPER_C_C2_GENERIC", "path": ["generic"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "PAPER_C_C2_PAIR_SAME", "path": ["pair_same"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "PAPER_C_C2_LOCAL_COMPLETE", "path": ["local_complete"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "PAPER_C_C2_DIRECT", "path": ["direct"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "PAPER_C_C2_UNBOUNDED", "path": ["unbounded"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "PAPER_C_C2_VALUE_FALSE", "path": ["value_false"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "PAPER_C_C2_OPTIMIZER_FALSE", "path": ["optimizer_false"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "PAPER_C_C2_PARENT", "path": ["parent"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "PAPER_C_C2_SCOPE", "path": ["scope"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "PAPER_C_C2_NO_NOVELTY", "path": ["no_novelty"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "PAPER_C_C2_NO_PHYSICAL", "path": ["no_physical"], "transform": "BOOL_YES_NO"},
                ],
            },
            "next_phase": "D0",
        },
        "paper_c_c2.accept": _record(
            "ACCEPT_PAIR_INFORMATION_VALUE_AND_OPTIMIZER_SEPARATION", "ACCEPT_RECORDED"
        ),
        "paper_c_c2.reject": _record("REJECT", "REJECT_RECORDED"),
    },
    "phases": {
        "S0": {
            "active_hard_obligations": ["PAPER_C_C2_LOAD"],
            "responsibility_hypotheses": [
                {"hypothesis_id": "RESP:LOAD", "expected_observations": {"PAPER_C_C2_NEED": ["YES"]}}
            ],
            "interface_checks": [
                {"check_id": "IFACE:SERIALIZED", "scope": "EVIDENCE_BINDING", "state": "PASS"}
            ],
            "revision_mechanics": [
                {"mechanic_id": "REV:WAIT", "kind": "WAIT_EVIDENCE", "write_coordinates": ["EVIDENCE"], "cost": 0.1}
            ],
            "computation_actions": [
                {
                    "action_id": "COMPUTE:LOAD",
                    "kind": "VERIFY",
                    "expected_decision_value": 5.0,
                    "cost": 0.1,
                    "discharges_obligations": ["PAPER_C_C2_LOAD"],
                }
            ],
            "responsibility_bindings": {"RESP:LOAD": ["REV:WAIT"]},
            "selected_capabilities": {"COMPUTE:LOAD": "paper_c_c2.load"},
        },
        "D0": {
            "active_hard_obligations": [],
            "responsibility_hypotheses": [
                {"hypothesis_id": "RESP:ACCEPT", "expected_observations": _ACCEPT},
                {"hypothesis_id": "RESP:REJECT", "expected_observations": {"PAPER_C_C2_POSITIVE": ["NO"]}},
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
                {"mechanic_id": "REV:REJECT", "kind": "REJECT", "read_coordinates": ["EVIDENCE"], "write_coordinates": ["TERMINAL"], "cost": 0.1},
            ],
            "computation_actions": [
                {"action_id": "COMPUTE:NONE", "kind": "NONE", "expected_decision_value": 0.0, "cost": 1.0}
            ],
            "responsibility_bindings": {"RESP:ACCEPT": ["REV:ACCEPT"], "RESP:REJECT": ["REV:REJECT"]},
            "selected_capabilities": {"REV:ACCEPT": "paper_c_c2.accept", "REV:REJECT": "paper_c_c2.reject"},
        },
        "ACCEPT_RECORDED": {
            "terminal": True,
            "terminal_name": "PAPER_C_C2_NATIVE_ACCEPT_RECORDED",
            "active_hard_obligations": [],
        },
        "REJECT_RECORDED": {
            "terminal": True,
            "terminal_name": "PAPER_C_C2_NATIVE_REJECT_RECORDED",
            "active_hard_obligations": [],
        },
    },
}
