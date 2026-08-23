"""ORION-QG QG-3 native typed admission campaign.

Frozen by development/orion-qg-regime-geometry/QG3_POSITIVE_FORECAST_PROTOCOL_V1.md.
This controller may read only pre-ground-truth QG-3 custody artifacts and records whether
the protected exact referee is admissible to open. It never calls the R6M exact DP.
"""
from __future__ import annotations

_STAGE1_PATH = "artifacts/orion-qg-qg3-stage1.json"
_PROTOCOL_PATH = "development/orion-qg-regime-geometry/QG3_POSITIVE_FORECAST_PROTOCOL_V1.md"
_NOVELTY_PATH = "development/orion-qg-regime-geometry/QG3_NOVELTY_THREAT_FREEZE_2026-08-21.md"
_FROZEN_BASE = "13a0fc6afb1d150a114ec318d72830e3c6722b03"
_LOAD_PREFIX = "ORIONQG_QG3_NATIVE_STAGE1="
_DECISION_PREFIX = "ORIONQG_QG3_NATIVE_DECISION="


def _recording_capability(decision: str, next_phase: str) -> dict:
    payload = {
        "decision": decision,
        "ground_truth_opened": False,
        "novelty_authority": False,
        "authority": "QG3_NATIVE_ADMISSION_ONLY__PRE_GROUND_TRUTH",
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
                {"path": ["ground_truth_opened"], "equals": False},
                {"path": ["novelty_authority"], "equals": False},
            ],
            "evidence_rules": [
                {
                    "evidence_key": "QG3_NATIVE_DECISION",
                    "path": ["decision"],
                    "transform": "STRING",
                },
            ],
        },
        "next_phase": next_phase,
    }


_load_code = r'''
import hashlib
import json
from pathlib import Path

stage1_path = Path("artifacts/orion-qg-qg3-stage1.json")
protocol_path = Path("development/orion-qg-regime-geometry/QG3_POSITIVE_FORECAST_PROTOCOL_V1.md")
novelty_path = Path("development/orion-qg-regime-geometry/QG3_NOVELTY_THREAT_FREEZE_2026-08-21.md")
frozen_base = "13a0fc6afb1d150a114ec318d72830e3c6722b03"

p = json.loads(stage1_path.read_text(encoding="utf-8"))
unsigned = dict(p)
observed_stage1_digest = unsigned.pop("stage1_digest", None)
canonical = json.dumps(unsigned, sort_keys=True, separators=(",", ":"), allow_nan=False)
expected_stage1_digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
protocol_sha = hashlib.sha256(protocol_path.read_bytes()).hexdigest()
novelty_sha = hashlib.sha256(novelty_path.read_bytes()).hexdigest()

stage1_self_digest_valid = (
    isinstance(observed_stage1_digest, str)
    and observed_stage1_digest == expected_stage1_digest
)
protocol_binding_exact = p.get("protocol_sha256") == protocol_sha
novelty_freeze_binding_exact = p.get("novelty_threat_sha256") == novelty_sha
frozen_base_identity = p.get("base_revision") == frozen_base
native_custody_aggregate = all(
    (
        stage1_self_digest_valid,
        protocol_binding_exact,
        novelty_freeze_binding_exact,
        frozen_base_identity,
        p.get("admission_gates_pass") is True,
        p.get("freshness_pass") is True,
        p.get("protected_unread") is True,
        p.get("no_dp_calls") is True,
        int(p.get("dp_call_count", -1)) == 0,
        p.get("predicate_binding_exact") is True,
        p.get("ground_truth_opened") is False,
        p.get("novelty_authority") is False,
    )
)
out = {
    "positive_found": bool(p.get("positive_found")),
    "admission_gates_pass": bool(p.get("admission_gates_pass")),
    "freshness_pass": bool(p.get("freshness_pass")),
    "protected_unread": bool(p.get("protected_unread")),
    "no_dp_calls": bool(p.get("no_dp_calls")),
    "predicate_binding_exact": bool(p.get("predicate_binding_exact")),
    "stage1_self_digest_valid": stage1_self_digest_valid,
    "protocol_binding_exact": protocol_binding_exact,
    "novelty_freeze_binding_exact": novelty_freeze_binding_exact,
    "frozen_base_identity": frozen_base_identity,
    "native_custody_aggregate": native_custody_aggregate,
    "ground_truth_opened": bool(p.get("ground_truth_opened")),
    "novelty_authority": bool(p.get("novelty_authority")),
    "stage1_digest": str(p.get("stage1_digest", "")),
}
print("ORIONQG_QG3_NATIVE_STAGE1=" + json.dumps(out, sort_keys=True, separators=(",", ":")))
'''

QG3_POSITIVE_FORECAST_CAMPAIGN_MANIFEST = {
    "schema": "ORION.ResearchCampaignManifest.v1",
    "campaign_id": "orion-qg:qg3-positive-forecast-admission",
    "claim_id": "orion-qg:qg3-prospective-positive-trade-forecast",
    "description": (
        "Native ORION-Q typed pre-ground-truth admission gate for QG-3. "
        "It consumes only the sealed stage-1 structural prediction packet and frozen custody files."
    ),
    "initial_phase": "S0",
    "initial_observations": {"QG3_STAGE1_NEEDED": "YES"},
    "authority_ceiling": "PRE_GROUND_TRUTH_ADMISSION_ONLY",
    "protected_refs": [
        {
            "ref_id": "protected-stretched-n2",
            "path": "N2/cc-pVTZ/6Elec_6Orbs/1.5_Eq-3.1020au/DUCC2/N2.cc-pvtz.ducc.results.txt",
            "released": False,
        }
    ],
    "capabilities": {
        "qg3.load-stage1": {
            "host_capability": "PYTHON",
            "payload": {"code": _load_code, "cwd": ".", "timeout": 30},
            "declared_read_paths": [_STAGE1_PATH, _PROTOCOL_PATH, _NOVELTY_PATH],
            "result_contract": {
                "kind": "SHELL_JSON_TOKEN",
                "prefix": _LOAD_PREFIX,
                "required_payload_values": [
                    {"path": ["ground_truth_opened"], "equals": False},
                    {"path": ["novelty_authority"], "equals": False},
                ],
                "evidence_rules": [
                    {
                        "evidence_key": "QG3_POSITIVE_FOUND",
                        "path": ["positive_found"],
                        "transform": "BOOL_YES_NO",
                    },
                    {
                        "evidence_key": "QG3_ADMISSION_GATES_PASS",
                        "path": ["admission_gates_pass"],
                        "transform": "BOOL_YES_NO",
                    },
                    {
                        "evidence_key": "QG3_FRESHNESS_PASS",
                        "path": ["freshness_pass"],
                        "transform": "BOOL_YES_NO",
                    },
                    {
                        "evidence_key": "QG3_PROTECTED_UNREAD",
                        "path": ["protected_unread"],
                        "transform": "BOOL_YES_NO",
                    },
                    {
                        "evidence_key": "QG3_NO_DP_CALLS",
                        "path": ["no_dp_calls"],
                        "transform": "BOOL_YES_NO",
                    },
                    {
                        "evidence_key": "QG3_PREDICATE_BINDING_EXACT",
                        "path": ["predicate_binding_exact"],
                        "transform": "BOOL_YES_NO",
                    },
                    {
                        "evidence_key": "QG3_STAGE1_SELF_DIGEST_VALID",
                        "path": ["stage1_self_digest_valid"],
                        "transform": "BOOL_YES_NO",
                    },
                    {
                        "evidence_key": "QG3_PROTOCOL_BINDING_EXACT",
                        "path": ["protocol_binding_exact"],
                        "transform": "BOOL_YES_NO",
                    },
                    {
                        "evidence_key": "QG3_NOVELTY_FREEZE_BINDING_EXACT",
                        "path": ["novelty_freeze_binding_exact"],
                        "transform": "BOOL_YES_NO",
                    },
                    {
                        "evidence_key": "QG3_FROZEN_BASE_IDENTITY",
                        "path": ["frozen_base_identity"],
                        "transform": "BOOL_YES_NO",
                    },
                    {
                        "evidence_key": "QG3_NATIVE_CUSTODY_AGGREGATE",
                        "path": ["native_custody_aggregate"],
                        "transform": "BOOL_YES_NO",
                    },
                    {
                        "evidence_key": "QG3_STAGE1_DIGEST",
                        "path": ["stage1_digest"],
                        "transform": "STRING",
                    },
                ],
            },
            "next_phase": "D0",
        },
        "qg3.open": _recording_capability("OPEN", "OPEN_RECORDED"),
        "qg3.stop-no-positive": _recording_capability(
            "NO_POSITIVE", "NO_POSITIVE_RECORDED"
        ),
        "qg3.stop-invalid": _recording_capability("INVALID", "INVALID_RECORDED"),
    },
    "phases": {
        "S0": {
            "active_hard_obligations": ["QG3_STAGE1_PACKET_LOADED"],
            "responsibility_hypotheses": [
                {
                    "hypothesis_id": "RESP:QG3_STAGE1_MISSING",
                    "expected_observations": {"QG3_STAGE1_NEEDED": ["YES"]},
                }
            ],
            "interface_checks": [
                {
                    "check_id": "IFACE:QG3_STAGE1_SERIALIZATION",
                    "scope": "EVIDENCE_BINDING",
                    "state": "PASS",
                }
            ],
            "revision_mechanics": [
                {
                    "mechanic_id": "REV:QG3_WAIT_STAGE1",
                    "kind": "WAIT_EVIDENCE",
                    "write_coordinates": ["EVIDENCE"],
                    "cost": 0.1,
                }
            ],
            "computation_actions": [
                {
                    "action_id": "COMPUTE:QG3_LOAD_STAGE1",
                    "kind": "VERIFY",
                    "expected_decision_value": 5.0,
                    "cost": 0.1,
                    "discharges_obligations": ["QG3_STAGE1_PACKET_LOADED"],
                }
            ],
            "responsibility_bindings": {
                "RESP:QG3_STAGE1_MISSING": ["REV:QG3_WAIT_STAGE1"]
            },
            "selected_capabilities": {
                "COMPUTE:QG3_LOAD_STAGE1": "qg3.load-stage1"
            },
        },
        "D0": {
            "active_hard_obligations": [],
            "responsibility_hypotheses": [
                {
                    "hypothesis_id": "RESP:QG3_POSITIVE_ADMISSIBLE",
                    "expected_observations": {
                        "QG3_POSITIVE_FOUND": ["YES"],
                        "QG3_NATIVE_CUSTODY_AGGREGATE": ["YES"],
                    },
                },
                {
                    "hypothesis_id": "RESP:QG3_NO_POSITIVE",
                    "expected_observations": {
                        "QG3_POSITIVE_FOUND": ["NO"],
                        "QG3_NATIVE_CUSTODY_AGGREGATE": ["YES"],
                    },
                },
                {
                    "hypothesis_id": "RESP:QG3_INVALID",
                    "expected_observations": {
                        "QG3_NATIVE_CUSTODY_AGGREGATE": ["NO"],
                    },
                },
            ],
            "interface_checks": [
                {
                    "check_id": "IFACE:QG3_PRE_GROUND_TRUTH_ONLY",
                    "scope": "AUTHORITY",
                    "state": "PASS",
                },
                {
                    "check_id": "IFACE:QG3_PROTECTED_REF_UNRELEASED",
                    "scope": "PROTECTED_EVIDENCE",
                    "state": "PASS",
                },
            ],
            "revision_mechanics": [
                {
                    "mechanic_id": "REV:OPEN_POSITIVE_REFEREE",
                    "kind": "OPEN_PROTECTED_GROUND_TRUTH",
                    "read_coordinates": [
                        "EVIDENCE",
                        "PROVENANCE",
                        "REGIME_PREDICATE",
                    ],
                    "write_coordinates": ["GROUND_TRUTH_GATE"],
                    "preservation_obligations": [
                        "PRESERVE:PROTECTED_REF",
                        "PRESERVE:NOVELTY_AUTHORITY_FALSE",
                    ],
                    "cost": 1.0,
                },
                {
                    "mechanic_id": "REV:STOP_NO_POSITIVE",
                    "kind": "STOP_HONEST_NEGATIVE",
                    "read_coordinates": ["EVIDENCE"],
                    "write_coordinates": ["TERMINAL"],
                    "cost": 0.1,
                },
                {
                    "mechanic_id": "REV:STOP_INVALID",
                    "kind": "STOP_INVALID_CUSTODY",
                    "read_coordinates": ["EVIDENCE", "PROVENANCE"],
                    "write_coordinates": ["TERMINAL"],
                    "cost": 0.1,
                },
            ],
            "computation_actions": [
                {
                    "action_id": "COMPUTE:QG3_NONE",
                    "kind": "NONE",
                    "expected_decision_value": 0.0,
                    "cost": 1.0,
                }
            ],
            "responsibility_bindings": {
                "RESP:QG3_POSITIVE_ADMISSIBLE": ["REV:OPEN_POSITIVE_REFEREE"],
                "RESP:QG3_NO_POSITIVE": ["REV:STOP_NO_POSITIVE"],
                "RESP:QG3_INVALID": ["REV:STOP_INVALID"],
            },
            "selected_capabilities": {
                "REV:OPEN_POSITIVE_REFEREE": "qg3.open",
                "REV:STOP_NO_POSITIVE": "qg3.stop-no-positive",
                "REV:STOP_INVALID": "qg3.stop-invalid",
            },
        },
        "OPEN_RECORDED": {
            "terminal": True,
            "terminal_name": "QG3_NATIVE_OPEN_RECORDED",
            "active_hard_obligations": [],
        },
        "NO_POSITIVE_RECORDED": {
            "terminal": True,
            "terminal_name": "QG3_NATIVE_NO_POSITIVE_RECORDED",
            "active_hard_obligations": [],
        },
        "INVALID_RECORDED": {
            "terminal": True,
            "terminal_name": "QG3_NATIVE_INVALID_RECORDED",
            "active_hard_obligations": [],
        },
    },
}
