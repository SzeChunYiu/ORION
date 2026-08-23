"""QG-6 native ORION-Q admission controller for syndrome-rank findings.

Consumes only serialized QG-6 analyzer/generic-verifier evidence.  It may accept
rank/binding findings but cannot promote the R6I support-five theorem; that remains
a separately owned QG-1 authority coordinate.
"""
from __future__ import annotations

_LOAD_PREFIX = "ORIONQG_QG6_NATIVE_LOAD="
_DECISION_PREFIX = "ORIONQG_QG6_NATIVE_DECISION="


def _record(decision: str, next_phase: str) -> dict:
    payload = {
        "decision": decision,
        "r6i_theorem_promotion": "PENDING_QG1",
        "novelty_authority": False,
        "scientific_authority": False,
        "physical_quantum_advantage_claim": False,
    }
    code = (
        "import json; print('"
        + _DECISION_PREFIX
        + "' + json.dumps("
        + repr(payload)
        + ", sort_keys=True, separators=(',', ':')))"
    )
    return {
        "host_capability": "PYTHON",
        "payload": {"code": code, "cwd": ".", "timeout": 30},
        "result_contract": {
            "kind": "SHELL_JSON_TOKEN",
            "prefix": _DECISION_PREFIX,
            "required_payload_values": [
                {"path": ["decision"], "equals": decision},
                {"path": ["r6i_theorem_promotion"], "equals": "PENDING_QG1"},
                {"path": ["novelty_authority"], "equals": False},
                {"path": ["scientific_authority"], "equals": False},
            ],
            "evidence_rules": [
                {"evidence_key": "QG6_NATIVE_DECISION", "path": ["decision"], "transform": "STRING"},
            ],
        },
        "next_phase": next_phase,
    }


_LOAD_CODE = r'''
import hashlib, json
from pathlib import Path

a = json.loads(Path("artifacts/orion-qg-qg6-syndrome-rank.json").read_text())
g = json.loads(Path("artifacts/orion-qg-qg6-generic-verification.json").read_text())
unsigned = dict(a); observed = unsigned.pop("result_digest", None)
canon = json.dumps(unsigned, sort_keys=True, separators=(",", ":"), allow_nan=False)
digest_ok = observed == hashlib.sha256(canon.encode()).hexdigest()

out = {
  "analyzer_positive": a.get("terminal") == "QG6_PRODUCTION_SYNDROME_RANK_INFERENCE_VERIFIED__R6M_D2_RECOVERS_SUPPORT2__R6I_D5_FOUND_THEOREM_PENDING_QG1",
  "analyzer_digest_valid": digest_ok,
  "all_analyzer_gates": all(a.get("gates", {}).values()),
  "generic_accept": g.get("decision") == "ACCEPT" and all(g.get("checks", {}).values()),
  "r6m_dimension2": a.get("r6m", {}).get("auto_dimension") == 2,
  "r6m_support2_recovered": a.get("r6m", {}).get("support_theorem_status") == "RECOVERED_FROM_EXISTING_R6S_CERTIFICATE",
  "r6i_dimension5": a.get("r6i", {}).get("auto_dimension") == 5,
  "r6i_promotion_pending": a.get("r6i", {}).get("support_theorem_status") == "PENDING_QG1_INDEPENDENT_DUAL_HARNESS",
  "no_chemistry": a.get("chemistry_sources_read") is False,
  "no_protected": a.get("protected_subject_read") is False,
  "novelty_authority": False,
}
print("ORIONQG_QG6_NATIVE_LOAD=" + json.dumps(out, sort_keys=True, separators=(",", ":")))
'''


QG6_SYNDROME_COMPRESSION_CAMPAIGN_MANIFEST = {
    "schema": "ORION.ResearchCampaignManifest.v1",
    "campaign_id": "orion-qg:qg6-syndrome-compression",
    "claim_id": "orion-qg:qg6-production-syndrome-rank",
    "description": "Native admission for production-derived syndrome quotient dimensions.",
    "initial_phase": "S0",
    "initial_observations": {"QG6_EVIDENCE_NEEDED": "YES"},
    "authority_ceiling": "NON_AUTHORIZING_META_THEOREM_EVIDENCE",
    "protected_refs": [],
    "capabilities": {
        "qg6.load": {
            "host_capability": "PYTHON",
            "payload": {"code": _LOAD_CODE, "cwd": ".", "timeout": 30},
            "declared_read_paths": [
                "artifacts/orion-qg-qg6-syndrome-rank.json",
                "artifacts/orion-qg-qg6-generic-verification.json",
            ],
            "result_contract": {
                "kind": "SHELL_JSON_TOKEN",
                "prefix": _LOAD_PREFIX,
                "required_payload_values": [
                    {"path": ["novelty_authority"], "equals": False},
                ],
                "evidence_rules": [
                    {"evidence_key": "QG6_ANALYZER_POSITIVE", "path": ["analyzer_positive"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG6_ANALYZER_DIGEST_VALID", "path": ["analyzer_digest_valid"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG6_ANALYZER_GATES", "path": ["all_analyzer_gates"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG6_GENERIC_ACCEPT", "path": ["generic_accept"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG6_R6M_D2", "path": ["r6m_dimension2"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG6_R6M_SUPPORT2_RECOVERED", "path": ["r6m_support2_recovered"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG6_R6I_D5", "path": ["r6i_dimension5"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG6_R6I_PENDING", "path": ["r6i_promotion_pending"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG6_NO_CHEMISTRY", "path": ["no_chemistry"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG6_NO_PROTECTED", "path": ["no_protected"], "transform": "BOOL_YES_NO"},
                ],
            },
            "next_phase": "D0",
        },
        "qg6.accept": _record("ACCEPT_RANK_FINDINGS", "ACCEPT_RECORDED"),
        "qg6.reject": _record("REJECT", "REJECT_RECORDED"),
    },
    "phases": {
        "S0": {
            "active_hard_obligations": ["QG6_EVIDENCE_LOADED"],
            "responsibility_hypotheses": [
                {"hypothesis_id": "RESP:QG6_LOAD", "expected_observations": {"QG6_EVIDENCE_NEEDED": ["YES"]}}
            ],
            "interface_checks": [
                {"check_id": "IFACE:QG6_SERIALIZED_EVIDENCE", "scope": "EVIDENCE_BINDING", "state": "PASS"}
            ],
            "revision_mechanics": [
                {"mechanic_id": "REV:QG6_WAIT", "kind": "WAIT_EVIDENCE", "write_coordinates": ["EVIDENCE"], "cost": 0.1}
            ],
            "computation_actions": [
                {
                    "action_id": "COMPUTE:QG6_LOAD",
                    "kind": "VERIFY",
                    "expected_decision_value": 5.0,
                    "cost": 0.1,
                    "discharges_obligations": ["QG6_EVIDENCE_LOADED"],
                }
            ],
            "responsibility_bindings": {"RESP:QG6_LOAD": ["REV:QG6_WAIT"]},
            "selected_capabilities": {"COMPUTE:QG6_LOAD": "qg6.load"},
        },
        "D0": {
            "active_hard_obligations": [],
            "responsibility_hypotheses": [
                {
                    "hypothesis_id": "RESP:QG6_ACCEPT",
                    "expected_observations": {
                        "QG6_ANALYZER_POSITIVE": ["YES"],
                        "QG6_ANALYZER_DIGEST_VALID": ["YES"],
                        "QG6_ANALYZER_GATES": ["YES"],
                        "QG6_GENERIC_ACCEPT": ["YES"],
                        "QG6_R6M_D2": ["YES"],
                        "QG6_R6M_SUPPORT2_RECOVERED": ["YES"],
                        "QG6_R6I_D5": ["YES"],
                        "QG6_R6I_PENDING": ["YES"],
                        "QG6_NO_CHEMISTRY": ["YES"],
                        "QG6_NO_PROTECTED": ["YES"],
                    },
                },
                {
                    "hypothesis_id": "RESP:QG6_REJECT",
                    "expected_observations": {
                        "QG6_ANALYZER_POSITIVE": ["NO"],
                    },
                },
            ],
            "interface_checks": [
                {"check_id": "IFACE:QG6_NO_AUTHORITY_LAUNDER", "scope": "AUTHORITY", "state": "PASS"},
                {"check_id": "IFACE:QG6_R6I_OWNERSHIP", "scope": "THEOREM_OWNERSHIP", "state": "PASS"},
            ],
            "revision_mechanics": [
                {
                    "mechanic_id": "REV:QG6_ACCEPT_RANK_FINDINGS",
                    "kind": "ACCEPT_BOUNDED_EVIDENCE",
                    "read_coordinates": ["EVIDENCE", "SEMANTICS"],
                    "write_coordinates": ["BOUNDED_RESULT"],
                    "preservation_obligations": ["PRESERVE:QG1_AUTHORITY_PENDING", "PRESERVE:NOVELTY_FALSE"],
                    "cost": 0.1,
                },
                {
                    "mechanic_id": "REV:QG6_REJECT",
                    "kind": "REJECT_INVALID_BINDING",
                    "read_coordinates": ["EVIDENCE"],
                    "write_coordinates": ["TERMINAL"],
                    "cost": 0.1,
                },
            ],
            "computation_actions": [
                {"action_id": "COMPUTE:QG6_NONE", "kind": "NONE", "expected_decision_value": 0.0, "cost": 1.0}
            ],
            "responsibility_bindings": {
                "RESP:QG6_ACCEPT": ["REV:QG6_ACCEPT_RANK_FINDINGS"],
                "RESP:QG6_REJECT": ["REV:QG6_REJECT"],
            },
            "selected_capabilities": {
                "REV:QG6_ACCEPT_RANK_FINDINGS": "qg6.accept",
                "REV:QG6_REJECT": "qg6.reject",
            },
        },
        "ACCEPT_RECORDED": {
            "terminal": True,
            "terminal_name": "QG6_NATIVE_ACCEPT_RECORDED",
            "active_hard_obligations": [],
        },
        "REJECT_RECORDED": {
            "terminal": True,
            "terminal_name": "QG6_NATIVE_REJECT_RECORDED",
            "active_hard_obligations": [],
        },
    },
}
