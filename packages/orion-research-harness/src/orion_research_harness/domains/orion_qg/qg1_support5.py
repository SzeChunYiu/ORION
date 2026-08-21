"""Native ORION-Q campaign admission for QG-1 support-five theorem."""
from __future__ import annotations

_RESULT_PATH = "artifacts/orion-qg-qg1-support5-theorem.json"
_GENERIC_PATH = "artifacts/orion-qg-qg1-generic-verification.json"
_PROTOCOL_PATH = "development/orion-qg-regime-geometry/QG1_RANK2_SUPPORT5_PROTOCOL_V1.md"
_NOVELTY_PATH = "development/orion-qg-regime-geometry/QG1_NOVELTY_THREAT_FREEZE_2026-08-21.md"
_FROZEN_BASE = "e6011bbeae68d91b5cce45ffa34e67306905844d"
_LOAD_PREFIX = "ORIONQG_QG1_NATIVE_LOAD="
_DECISION_PREFIX = "ORIONQG_QG1_NATIVE_DECISION="
_POSITIVE = "QG1_RANK2_ALL_N_SUPPORT5_SUFFICIENCY_MACHINE_VERIFIED"


def _record(decision: str, next_phase: str) -> dict:
    payload = {
        "decision": decision,
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
        "authority": "QG1_NATIVE_THEOREM_ADMISSION_ONLY",
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
                {"path": ["novelty_authority"], "equals": False},
                {"path": ["physical_quantum_advantage_claim"], "equals": False},
            ],
            "evidence_rules": [
                {
                    "evidence_key": "QG1_NATIVE_DECISION",
                    "path": ["decision"],
                    "transform": "STRING",
                }
            ],
        },
        "next_phase": next_phase,
    }


_load_code = r'''
import hashlib
import json
from pathlib import Path

result_path = Path("artifacts/orion-qg-qg1-support5-theorem.json")
generic_path = Path("artifacts/orion-qg-qg1-generic-verification.json")
protocol_path = Path("development/orion-qg-regime-geometry/QG1_RANK2_SUPPORT5_PROTOCOL_V1.md")
novelty_path = Path("development/orion-qg-regime-geometry/QG1_NOVELTY_THREAT_FREEZE_2026-08-21.md")
frozen_base = "e6011bbeae68d91b5cce45ffa34e67306905844d"
positive_terminal = "QG1_RANK2_ALL_N_SUPPORT5_SUFFICIENCY_MACHINE_VERIFIED"

r = json.loads(result_path.read_text(encoding="utf-8"))
g = json.loads(generic_path.read_text(encoding="utf-8"))
unsigned = dict(r)
observed_digest = unsigned.pop("result_digest", None)
canonical = json.dumps(unsigned, sort_keys=True, separators=(",", ":"), allow_nan=False)
expected_digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
protocol_sha = hashlib.sha256(protocol_path.read_bytes()).hexdigest()
novelty_sha = hashlib.sha256(novelty_path.read_bytes()).hexdigest()

custody = all((
    isinstance(observed_digest, str) and observed_digest == expected_digest,
    r.get("base_revision") == frozen_base,
    r.get("protocol_sha256") == protocol_sha,
    r.get("novelty_threat_sha256") == novelty_sha,
    g.get("theorem_result_digest") == observed_digest,
    r.get("chemistry_sources_read") is False,
    g.get("chemistry_sources_read") is False,
    r.get("novelty_authority") is False,
    g.get("novelty_authority") is False,
    r.get("physical_quantum_advantage_claim") is False,
))
positive = (
    r.get("terminal") == positive_terminal
    and all(bool(v) for v in r.get("gates", {}).values())
    and all(bool(v) for v in r.get("proof_audit", {}).values())
)
generic_pass = g.get("verification_pass") is True
accept = custody and positive and generic_pass
out = {
    "custody": custody,
    "positive": positive,
    "generic_pass": generic_pass,
    "accept": accept,
    "result_digest": str(observed_digest or ""),
    "chemistry_sources_read": bool(r.get("chemistry_sources_read")),
    "novelty_authority": bool(r.get("novelty_authority")),
}
print("ORIONQG_QG1_NATIVE_LOAD=" + json.dumps(out, sort_keys=True, separators=(",", ":")))
'''

QG1_SUPPORT5_CAMPAIGN_MANIFEST = {
    "schema": "ORION.ResearchCampaignManifest.v1",
    "campaign_id": "orion-qg:qg1-rank2-support5-theorem",
    "claim_id": "orion-qg:qg1-rank2-all-n-support5",
    "description": "Native ORION-Q non-authorizing admission of the QG-1 machine theorem receipt.",
    "initial_phase": "S0",
    "initial_observations": {"QG1_RECEIPT_NEEDED": "YES"},
    "authority_ceiling": "INTERNAL_MACHINE_THEOREM_CANDIDATE_ONLY",
    "protected_refs": [],
    "capabilities": {
        "qg1.load": {
            "host_capability": "PYTHON",
            "payload": {"code": _load_code, "cwd": ".", "timeout": 30},
            "declared_read_paths": [
                _RESULT_PATH,
                _GENERIC_PATH,
                _PROTOCOL_PATH,
                _NOVELTY_PATH,
            ],
            "result_contract": {
                "kind": "SHELL_JSON_TOKEN",
                "prefix": _LOAD_PREFIX,
                "required_payload_values": [],
                "evidence_rules": [
                    {"evidence_key": "QG1_CUSTODY", "path": ["custody"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG1_POSITIVE", "path": ["positive"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG1_GENERIC_PASS", "path": ["generic_pass"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG1_ACCEPT", "path": ["accept"], "transform": "BOOL_YES_NO"},
                    {"evidence_key": "QG1_RESULT_DIGEST", "path": ["result_digest"], "transform": "STRING"},
                ],
            },
            "next_phase": "D0",
        },
        "qg1.accept": _record("ACCEPT", "ACCEPT_RECORDED"),
        "qg1.reject": _record("REJECT", "REJECT_RECORDED"),
        "qg1.cannot": _record("CANNOT_CHECK", "CANNOT_RECORDED"),
    },
    "phases": {
        "S0": {
            "active_hard_obligations": ["QG1_RECEIPT_LOADED"],
            "responsibility_hypotheses": [
                {
                    "hypothesis_id": "RESP:QG1_RECEIPT_MISSING",
                    "expected_observations": {"QG1_RECEIPT_NEEDED": ["YES"]},
                }
            ],
            "interface_checks": [
                {"check_id": "IFACE:QG1_LOCAL_ONLY", "scope": "EVIDENCE", "state": "PASS"}
            ],
            "revision_mechanics": [
                {"mechanic_id": "REV:QG1_WAIT", "kind": "WAIT_EVIDENCE", "cost": 0.1}
            ],
            "computation_actions": [
                {
                    "action_id": "COMPUTE:QG1_LOAD",
                    "kind": "VERIFY",
                    "expected_decision_value": 5.0,
                    "cost": 0.1,
                    "discharges_obligations": ["QG1_RECEIPT_LOADED"],
                }
            ],
            "responsibility_bindings": {"RESP:QG1_RECEIPT_MISSING": ["REV:QG1_WAIT"]},
            "selected_capabilities": {"COMPUTE:QG1_LOAD": "qg1.load"},
        },
        "D0": {
            "active_hard_obligations": [],
            "responsibility_hypotheses": [
                {
                    "hypothesis_id": "RESP:QG1_ACCEPT",
                    "expected_observations": {"QG1_ACCEPT": ["YES"], "QG1_CUSTODY": ["YES"]},
                },
                {
                    "hypothesis_id": "RESP:QG1_REJECT",
                    "expected_observations": {"QG1_ACCEPT": ["NO"], "QG1_CUSTODY": ["YES"]},
                },
                {
                    "hypothesis_id": "RESP:QG1_CANNOT_CHECK",
                    "expected_observations": {"QG1_CUSTODY": ["NO"]},
                },
            ],
            "interface_checks": [
                {"check_id": "IFACE:QG1_NONAUTHORIZING", "scope": "AUTHORITY", "state": "PASS"}
            ],
            "revision_mechanics": [
                {"mechanic_id": "REV:QG1_ACCEPT", "kind": "ACCEPT_MACHINE_THEOREM", "cost": 1.0},
                {"mechanic_id": "REV:QG1_REJECT", "kind": "REJECT_MACHINE_THEOREM", "cost": 0.1},
                {"mechanic_id": "REV:QG1_CANNOT", "kind": "CANNOT_CHECK", "cost": 0.1},
            ],
            "computation_actions": [
                {"action_id": "COMPUTE:QG1_NONE", "kind": "NONE", "expected_decision_value": 0.0, "cost": 1.0}
            ],
            "responsibility_bindings": {
                "RESP:QG1_ACCEPT": ["REV:QG1_ACCEPT"],
                "RESP:QG1_REJECT": ["REV:QG1_REJECT"],
                "RESP:QG1_CANNOT_CHECK": ["REV:QG1_CANNOT"],
            },
            "selected_capabilities": {
                "REV:QG1_ACCEPT": "qg1.accept",
                "REV:QG1_REJECT": "qg1.reject",
                "REV:QG1_CANNOT": "qg1.cannot",
            },
        },
        "ACCEPT_RECORDED": {"terminal": True, "terminal_name": "QG1_NATIVE_ACCEPT_RECORDED", "active_hard_obligations": []},
        "REJECT_RECORDED": {"terminal": True, "terminal_name": "QG1_NATIVE_REJECT_RECORDED", "active_hard_obligations": []},
        "CANNOT_RECORDED": {"terminal": True, "terminal_name": "QG1_NATIVE_CANNOT_CHECK_RECORDED", "active_hard_obligations": []},
    },
}
