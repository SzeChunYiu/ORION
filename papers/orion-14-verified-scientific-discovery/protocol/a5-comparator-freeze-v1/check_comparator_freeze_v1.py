#!/usr/bin/env python3
"""Fail-closed verifier for A5's pre-outcome C1--C4 execution freeze."""
from __future__ import annotations

import ast
import importlib.util
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[4]
FREEZE = HERE / "COMPARATOR_EXECUTION_FREEZE_V1.json"
ADAPTER = HERE / "comparator_adapters_v1.py"
PROTOCOL = ROOT / "papers/orion-14-verified-scientific-discovery/protocol/P4_NATURALISTIC_IDENTIFIABILITY_SUCCESSOR_V2_AMENDMENT.json"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def git_blob(path: Path) -> str:
    return subprocess.check_output(["git", "hash-object", str(path)], cwd=ROOT, text=True).strip()


def load_adapter():
    spec = importlib.util.spec_from_file_location("a5_adapter", ADAPTER)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    p = json.loads(FREEZE.read_text(encoding="utf-8"))
    roles = {x["id"]: x for x in p["comparators"]}
    checks: dict[str, bool] = {}
    checks["schema"] = p["schema"] == "ORION.A5.NaturalisticComparatorExecutionFreeze.v1"
    checks["outcome_blind"] = (
        p["protected_outcomes_accessed"] is False
        and p["case_adjudication_outcomes_consumed"] is False
        and p["comparator_execution_started"] is False
    )
    checks["protocol_blob_bound"] = git_blob(PROTOCOL) == p["protocol_binding"]["git_blob"]
    checks["adapter_blob_bound"] = git_blob(ADAPTER) == p["adapter_binding"]["git_blob"]
    checks["four_roles_exact"] = set(roles) == {
        "C1_CALIBRATED_THREEWAY_NLI",
        "C2_SCIENTIFIC_EVIDENCE_ESCALATION",
        "C3_PROVENANCE_AWARE_VERIFIER",
        "C4_INFORMATION_EQUIVALENT_TYPED_DONOR",
    }
    checks["shared_three_terminal_alphabet"] = p["shared_terminal_alphabet"] == [
        "ResolvedTrue", "ResolvedFalse", "CannotCheck"
    ]
    backbone = p["backbone"]
    checks["immutable_backbone_revision"] = bool(HEX40.fullmatch(backbone["revision"]))
    checks["immutable_backbone_hash"] = bool(HEX64.fullmatch(backbone["model_sha256"]))
    checks["backbone_exact_known_hash"] = backbone["model_sha256"] == "06d6fd89edd4f97816831626daafbdb0b029cf63bae8edc0bccab1d64e2e7707"
    checks["backbone_exact_size"] = backbone["model_bytes"] == 368877646
    checks["backbone_named_labels"] = backbone["native_named_labels_required"] == [
        "entailment", "neutral", "contradiction"
    ]
    checks["c2_declared_reimplementation"] = roles["C2_SCIENTIFIC_EVIDENCE_ESCALATION"]["identity"].startswith("declared reimplementation")
    checks["c3_declared_reimplementation"] = roles["C3_PROVENANCE_AWARE_VERIFIER"]["identity"].startswith("declared reimplementation")
    c4 = roles["C4_INFORMATION_EQUIVALENT_TYPED_DONOR"]
    checks["c4_same_output_alphabet"] = c4["output_parity"] == p["shared_terminal_alphabet"]
    checks["c4_no_gold_field"] = not any("gold" in x.lower() for x in c4["typed_coordinates"])
    checks["c4_expected_576"] = c4["exhaustive_preoutcome_test_states"] == 576
    checks["runtime_fully_pinned"] = set(p["runtime_lock"]) == {
        "python", "torch", "transformers", "safetensors", "sentencepiece", "protobuf"
    } and all(re.fullmatch(r"\d+(?:\.\d+)+", v) for v in p["runtime_lock"].values())
    checks["no_postoutcome_retune"] = p["shared_resource_envelope"]["post_outcome_retuning"] == "forbidden"

    tree = ast.parse(ADAPTER.read_text(encoding="utf-8"))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    checks["adapter_stdlib_only"] = imports <= {"__future__", "itertools", "json"}
    text = ADAPTER.read_text(encoding="utf-8")
    checks["adapter_no_network_or_file_reads"] = not any(x in text for x in ("urllib", "requests", "open(", "Path("))

    mod = load_adapter()
    audit = mod.audit()
    checks["adapter_audit_green"] = audit["decision"] == "GREEN" and all(audit["checks"].values())
    checks["c4_exhaustive_576"] = audit["c4_typed_states_checked"] == 576
    checks["c4_exact_candidate_tie"] = audit["checks"]["c4_exhaustive_equality"] is True
    checks["c4_exact_alphabet_observed"] = set(audit["c4_outputs_observed"]) == set(p["shared_terminal_alphabet"])
    checks["c4_hostile_gold_and_missing_fields"] = (
        audit["hostile"]["c4_extra_gold_field_rejected"] is True
        and audit["hostile"]["c4_missing_candidate_field_rejected"] is True
    )
    checks["terminal"] = p["terminal"] == "FOUR_COMPARATORS_EXECUTION_IDENTITIES_FROZEN__OUTCOMES_UNRUN"
    checks["no_authority_delta"] = p["scientific_authority_delta"] == "NONE__COMPARATOR_FREEZE_ONLY"

    good = all(checks.values())
    print(json.dumps({"decision": "GREEN" if good else "REJECT", "checks": checks, "adapter_audit": audit}, indent=2, sort_keys=True))
    return 0 if good else 1


if __name__ == "__main__":
    raise SystemExit(main())
