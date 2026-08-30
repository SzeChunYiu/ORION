from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# parents[2], not parents[3]. This file used to sit one directory deeper; the
# papers-directory refactor moved it up and the index was not followed, so ROOT
# resolved to the repository's *parent* and every source path missed. The script
# then exited with "missing official P9 evidence" for files that were present all
# along, and P9's manuscript has been unbuildable ever since: main.tex inputs
# generated_result_macros.tex, which is generated from the summary this produces.
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RESEARCH = ROOT / "research" / "extensions" / "p9-structured-neural"
OUT = HERE / "evidence" / "OFFICIAL_EVIDENCE_SUMMARY_V1.json"
PAIRED_D1 = HERE / "evidence" / "D1_PAIRED_EFFECTS_V1.json"

SOURCES = {
    "a5": RESEARCH / "A5_D0_EXPLICIT_RESULT_V1.json",
    "a2_a4": RESEARCH / "A2_A4_D0_EXPLICIT_RESULT_V1.json",
    "m1": RESEARCH / "execution" / "M1_EXECUTION_RESULT_V1_5.json",
    "d1": RESEARCH / "execution" / "D1_EXECUTION_RESULT_V1_2.json",
}
RECEIPTS = {
    "a2_a4": RESEARCH / "A2_A4_D0_COMPLETION_RECEIPT_V1.md",
    "m1": HERE / "P9_SCIENTIFIC_CLOSURE_RECEIPT_V1.md",
    "d1": HERE / "evidence" / "D1_OFFICIAL_WORKFLOW_RECEIPT_V1.md",
}
INTEGRATION_RECEIPT = HERE / "evidence" / "P9_INTEGRATION_AUTHORITY_RECEIPT_V1.md"
UNIFIED_LEDGER_JSON = HERE / "evidence" / "P9_UNIFIED_RESOURCE_LEDGER_V2.json"
UNIFIED_LEDGER_RECEIPT = HERE / "top_tier" / "P9_UNIFIED_RESOURCE_LEDGER_RESULT_RECEIPT_V2.md"
CAUSAL_RECEIPT_MD = HERE / "top_tier" / "P9_CAUSAL_DIAGNOSTIC_RESULT_RECEIPT_V1.md"
TOP_TIER_OUTCOMES_LEDGER = ROOT / "papers" / "candidates" / "TOP_TIER_EXECUTION_LEDGER_2026-08-23.md"
EXPECTED_TERMINALS = {
    "a5": "A5_D0_EXPLICIT_INFERENCE_SUFFICIENT",
    "a2_a4": "A2_A4_D0_EXPLICIT_INFERENCE_SUFFICIENT",
    "m1": "M1_GLOBAL_COMPOSITION_RESIDUAL",
    "d1": "D1_TYPED_STRUCTURE_TRANSFER_SUPPORTED",
}
EXPECTED_DIGESTS = {
    "m1": "sha256:01e1b62da27b424d453c63b798a5cbb13a915a4546b8ced68fcf84c32d04d97e",
    "d1": "sha256:34003fb8ffcecec6ed01654e40c644ff05b7640be56b398a45efc1e52a30141a",
}
EXPECTED_IDENTITIES = {
    "m1_corpus": "sha256:01ae54ca4d8cf423b0ac20bf0e085f1ecdf6cec7a1f142cc09b5df0a90d9cc3a",
    "d1_dataset": "sha256:2775298457b7bdee815b207733507cd27d55719df314ef6352bb601bd709c19c",
}


def load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise SystemExit(f"missing official P9 evidence: {path.relative_to(ROOT)}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"official evidence is not a mapping: {path.relative_to(ROOT)}")
    return value


def selected_dev(arm: dict[str, Any]) -> dict[str, Any]:
    selected = arm.get("selected")
    configurations = arm.get("dev_configurations")
    if not isinstance(selected, dict) or not isinstance(configurations, list):
        raise SystemExit("D1 arm lacks selected/dev_configurations structure")
    config_id = selected.get("config_id")
    matches = [row for row in configurations if isinstance(row, dict) and row.get("config_id") == config_id]
    if len(matches) != 1 or not isinstance(matches[0].get("dev"), dict):
        raise SystemExit(f"D1 selected config {config_id!r} does not bind exactly one dev row")
    return matches[0]["dev"]


def require_receipt(name: str, *tokens: str, status: str = "BOUNDED_VERIFIED") -> dict[str, Any]:
    path = RECEIPTS[name]
    if not path.is_file():
        raise SystemExit(f"missing verification receipt: {path.relative_to(ROOT)}")
    text = path.read_text(encoding="utf-8")
    missing = [token for token in tokens if token not in text]
    if missing:
        raise SystemExit(f"{name} verification receipt missing required tokens: {missing}")
    return {
        "status": status,
        "verification_path": str(path.relative_to(ROOT)),
        "required_tokens": list(tokens),
    }


def require_file_tokens(path: Path, *tokens: str) -> dict[str, Any]:
    if not path.is_file():
        raise SystemExit(f"missing authority document: {path.relative_to(ROOT)}")
    text = path.read_text(encoding="utf-8")
    missing = [token for token in tokens if token not in text]
    if missing:
        raise SystemExit(f"{path.relative_to(ROOT)} missing required tokens: {missing}")
    return {"path": str(path.relative_to(ROOT)), "required_tokens": list(tokens)}


def unified_ledger_summary() -> dict[str, Any]:
    """Bind the unified I/A/C/M resource ledger V2 into the P9 evidence picture.

    Fail-closed: the committed ledger JSON and its bound run receipt must both
    exist and carry the pre-registered survival verdict.
    """
    if not UNIFIED_LEDGER_JSON.is_file():
        raise SystemExit(f"missing unified resource ledger: {UNIFIED_LEDGER_JSON.relative_to(ROOT)}")
    data = json.loads(UNIFIED_LEDGER_JSON.read_text(encoding="utf-8"))
    if data.get("schema") != "P9.UnifiedResourceLedger.v2":
        raise SystemExit(f"unexpected unified ledger schema: {data.get('schema')!r}")
    if data.get("terminal") != "P9_UNIFIED_RESOURCE_LEDGER_V2_GREEN":
        raise SystemExit(f"unified ledger not green: {data.get('terminal')!r}")
    if data.get("survival_verdict") != "SURVIVES_FULL_ACCOUNTING":
        raise SystemExit(f"unified ledger survival verdict: {data.get('survival_verdict')!r}")
    if data.get("scalarization") != "PROHIBITED" or data.get("row_count") != 15:
        raise SystemExit("unified ledger scalarization/row-count invariant violated")
    cells = data.get("cell_summaries", {})
    if set(cells) != {"D-A", "D-I", "B-I", "B-A", "B-C"}:
        raise SystemExit(f"unified ledger cell set mismatch: {sorted(cells)}")
    authority = require_file_tokens(
        UNIFIED_LEDGER_RECEIPT,
        "P9_UNIFIED_RESOURCE_LEDGER_V2_GREEN",
        str(data["receipt_sha256"]),
    )
    return {
        "schema": data["schema"],
        "terminal": data["terminal"],
        "survival_verdict": data["survival_verdict"],
        "dominance_contradiction_count": len(data.get("dominance_contradictions", [])),
        "audit_corrections": data["audit_corrections"],
        "per_cell": {
            task: {
                "probe_prediction": cell["probe_prediction_rederived"],
                "protected_gold": cell["protected_gold_rederived"],
            }
            for task, cell in sorted(cells.items())
        },
        "receipt_sha256": data["receipt_sha256"],
        "authority": authority,
    }


def top_tier_outcomes(ledger: dict[str, Any]) -> dict[str, Any]:
    """One coherent picture: positive, null, negative, CANNOT_CHECK, full ledger."""
    causal = require_file_tokens(
        CAUSAL_RECEIPT_MD,
        "diagnostic accuracy: `0.8`",
        "generic `UNCERTAINTY_ESCALATE_COMPUTE` accuracy: `0.2`",
        "protected causal gold is therefore `CANNOT_CHECK`",
    )
    outcomes_authority = require_file_tokens(
        TOP_TIER_OUTCOMES_LEDGER,
        "P9_REAL_ACCESSIBILITY_SCALING_V1_SUPPORTED",
        "wine: preregistered accessibility gap did not appear",
        "LLM_STRUCTURE_SCALING_FRONTIER_NOT_SUPPORTED",
    )
    r5_authority = require_file_tokens(
        HERE / "evidence" / "R5_REVIVAL_LEDGER_V1.json",
        "P9_CAUSAL_DIAGNOSTIC_TRANSPORT_V3_SUPPORTED",
        "EXECUTED AND REPRODUCED",
        "UNSOLVABLE within the frozen family",
        "CANNOT_CHECK-BLOCKED",
    )
    return {
        "schema": "P9.TopTierOutcomes.v1",
        "real_accessibility": {
            "terminal": "P9_REAL_ACCESSIBILITY_SCALING_V1_SUPPORTED",
            "wine_cell": "NULL_GAP_DID_NOT_APPEAR_NO_UNIVERSAL_DATASET_CLAIM",
            "authority": outcomes_authority,
        },
        "qwen_scaling": {
            "terminal": "LLM_STRUCTURE_SCALING_FRONTIER_NOT_SUPPORTED",
            "disposition": "NEGATIVE_PRESERVED_NOT_REPAIRED_NOT_RERUN",
            "authority": outcomes_authority,
        },
        "causal_diagnostic": {
            "diagnostic_accuracy": 0.8,
            "generic_compute_escalation_accuracy": 0.2,
            "d_a_protected_cell": "CANNOT_CHECK",
            "authority": causal,
        },
        "r5_revival_2026_08_28": {
            "protected_cell_execution": "EXECUTED_AND_REPRODUCED_NOT_BLOCKED",
            "causal_diagnostic_transport_v3_terminal":
                "P9_CAUSAL_DIAGNOSTIC_TRANSPORT_V3_SUPPORTED",
            "qwen_scaling_recovery":
                "NEGATIVE_CONFIRMED_AUTHORITATIVE_UNSOLVABLE_IN_FROZEN_FAMILY",
            "cannot_check_blocked_lanes": 2,
            "authority": r5_authority,
        },
        "unified_resource_ledger": ledger,
        "claim_boundary": (
            "Bounded P9 outcomes only. Matched full resource accounting does not "
            "establish a universal resource exchange rate, does not repair the "
            "D-A CANNOT_CHECK cell, and does not touch the Qwen scaling negative."
        ),
    }


def require_integration_authority() -> dict[str, Any]:
    if not INTEGRATION_RECEIPT.is_file():
        raise SystemExit(f"missing integration authority receipt: {INTEGRATION_RECEIPT.relative_to(ROOT)}")
    text = INTEGRATION_RECEIPT.read_text(encoding="utf-8")
    tokens = (
        "P9_VERIFIED_SCIENCE_INTEGRATED_ON_REVIEW_BRANCH",
        EXPECTED_DIGESTS["m1"],
        EXPECTED_DIGESTS["d1"],
        EXPECTED_IDENTITIES["m1_corpus"],
        EXPECTED_IDENTITIES["d1_dataset"],
        "MATERIAL_DISCREPANCIES = 0",
    )
    missing = [token for token in tokens if token not in text]
    if missing:
        raise SystemExit(f"integration authority receipt missing required tokens: {missing}")
    return {
        "status": "INTEGRATED_ARTIFACTS_MAY_BE_RENDERED_ON_REVIEW_BRANCH",
        "path": str(INTEGRATION_RECEIPT.relative_to(ROOT)),
        "required_tokens": list(tokens),
        "merged_to_main": False,
    }


def check(name: str, data: dict[str, Any]) -> None:
    if data.get("terminal") != EXPECTED_TERMINALS[name]:
        raise SystemExit(f"{name} unexpected terminal: {data.get('terminal')!r}")
    if name in EXPECTED_DIGESTS and data.get("result_digest") != EXPECTED_DIGESTS[name]:
        raise SystemExit(f"{name} result digest mismatch: {data.get('result_digest')!r}")
    if name == "m1" and data.get("corpus_manifest_digest") != EXPECTED_IDENTITIES["m1_corpus"]:
        raise SystemExit(f"M1 corpus digest mismatch: {data.get('corpus_manifest_digest')!r}")
    if name == "d1" and data.get("dataset_manifest_digest") != EXPECTED_IDENTITIES["d1_dataset"]:
        raise SystemExit(f"D1 dataset digest mismatch: {data.get('dataset_manifest_digest')!r}")
    if name == "a5" and data.get("verification_state") != "BOUNDED_VERIFIED":
        raise SystemExit(f"A5 not bounded verified: {data.get('verification_state')!r}")
    if name == "a2_a4":
        if data.get("verification_state") != "BOUNDED_VERIFIED":
            raise SystemExit(f"A2/A4 not bounded verified: {data.get('verification_state')!r}")
        hostile = data.get("hostile_checks")
        if not isinstance(hostile, dict) or not hostile or not all(v is True for v in hostile.values()):
            raise SystemExit(f"A2/A4 hostile checks not all green: {hostile!r}")


def check_paired_d1(data: dict[str, Any]) -> None:
    if data.get("schema") != "P9.D1PairedEffects.v1":
        raise SystemExit(f"unexpected D1 paired schema: {data.get('schema')!r}")
    if data.get("source_result_digest") != EXPECTED_DIGESTS["d1"]:
        raise SystemExit("D1 paired analysis is not bound to the official D1 result")
    if data.get("protected_n") != 128 or data.get("primary_arm") != "TYPED_RELATIONAL":
        raise SystemExit("D1 paired analysis protected population/primary arm mismatch")


def a5_summary(data: dict[str, Any]) -> dict[str, Any]:
    views = data["views"]
    return {
        "terminal": data["terminal"],
        "verification_state": data["verification_state"],
        "typed_accuracy": views["TYPED"]["accuracy"],
        "typed_unknown_rate": views["TYPED"]["unknown_rate"],
        "current_accuracy": views["CURRENT"]["accuracy"],
        "semantic_accuracy": views["SEMANTIC"]["accuracy"],
        "result_digest": data.get("result_digest"),
    }


def a2_summary(data: dict[str, Any]) -> dict[str, Any]:
    relation, history = data["relation_views"], data["history_views"]
    return {
        "terminal": data["terminal"],
        "relation": {
            v: {"coverage": relation[v]["coverage"], "full_task_accuracy": relation[v]["full_task_accuracy"]}
            for v in ("SURFACE", "TOPOLOGY", "TYPED", "CURRENT", "SEMANTIC")
        },
        "history": {
            v: {"coverage": history[v]["coverage"], "full_task_accuracy": history[v]["full_task_accuracy"]}
            for v in ("SURFACE", "TOPOLOGY", "TYPED", "CURRENT", "SEMANTIC")
        },
        "hostile_checks": data["hostile_checks"],
        "verification_state": data["verification_state"],
    }


def m1_summary(data: dict[str, Any]) -> dict[str, Any]:
    compact: dict[str, Any] = {}
    for view_name in ("SURFACE", "TOPOLOGY", "TYPED", "CURRENT", "SEMANTIC"):
        view = data["views"][view_name]
        overall = view["test_overall"]
        row: dict[str, Any] = {
            "accuracy": overall["accuracy"],
            "exact_view_deterministic_accuracy_ceiling": overall["exact_view_deterministic_accuracy_ceiling"],
            "ceiling_violation": overall["ceiling_violation"],
        }
        if view_name in {"CURRENT", "SEMANTIC"}:
            gluing = view["tasks"]["GLUING"]
            mechanic = view["tasks"]["MECHANIC_RANKING"]
            row["gluing"] = {
                "selected_feature": gluing["selected"]["feature_family"],
                "selected_model": gluing["selected"]["config_id"],
                "dev_accuracy": gluing["selected"]["dev"]["accuracy"],
                "test_accuracy": gluing["test"]["accuracy"],
                "task_information_ceiling": gluing["test"]["exact_view_deterministic_accuracy_ceiling"],
            }
            row["mechanic_ranking_test_accuracy"] = mechanic["test"]["accuracy"]
        compact[view_name] = row
    return {
        "terminal": data["terminal"],
        "protocol": data.get("protocol"),
        "corpus_manifest_digest": data.get("corpus_manifest_digest"),
        "views": compact,
        "result_digest": data["result_digest"],
    }


def d1_summary(data: dict[str, Any]) -> dict[str, Any]:
    compact: dict[str, Any] = {}
    for name, arm in data["results"].items():
        dev = selected_dev(arm)
        compact[name] = {
            "selected_model": arm["selected"]["config_id"],
            "dev_accuracy": dev["accuracy"],
            "test_accuracy": arm["test"]["accuracy"],
            "macro_f1": arm["test"]["macro_f1"],
            "double_corruption_accuracy": arm["test"]["double_corruption_accuracy"],
            "unresolved_accuracy": arm["test"]["unresolved_accuracy"],
        }
    return {
        "terminal": data["terminal"],
        "subject_sha": data.get("subject_sha"),
        "train_domains": data.get("train_domains"),
        "test_domain": data.get("test_domain"),
        "dataset_manifest_digest": data.get("dataset_manifest_digest"),
        "typed_minus_transcript": data.get("typed_minus_transcript"),
        "typed_minus_same_information_serialized": data.get("typed_minus_same_information_serialized"),
        "exact_typed_relational_comparator": data.get("exact_typed_relational_comparator"),
        "results": compact,
        "result_digest": data["result_digest"],
    }


def main() -> None:
    loaded = {name: load(path) for name, path in SOURCES.items()}
    for name, data in loaded.items():
        check(name, data)
    paired = load(PAIRED_D1)
    check_paired_d1(paired)

    verifications = {
        "a2_a4": require_receipt(
            "a2_a4",
            "A2_A4_D0_EXPLICIT_INFERENCE_SUFFICIENT",
            "BOUNDED_VERIFIED",
        ),
        "m1": require_receipt(
            "m1",
            "M1_GLOBAL_COMPOSITION_RESIDUAL",
            "BOUNDED_VERIFIED_WITH_ADJUDICATED_NON_MATERIAL_DISCREPANCY",
            "Material discrepancy count `0`",
        ),
        "d1": require_receipt(
            "d1",
            "D1_TYPED_STRUCTURE_TRANSFER_SUPPORTED",
            "MATERIAL_DISCREPANCIES = 0",
            status="BOUNDED_VERIFIED_PROVENANCE_RECEIPT",
        ),
    }
    integration = require_integration_authority()
    ledger = unified_ledger_summary()

    summary = {
        "schema": "P9.OfficialEvidenceSummary.v1.2",
        "source_paths": {name: str(path.relative_to(ROOT)) for name, path in SOURCES.items()},
        "derived_source_paths": {
            "d1_paired": str(PAIRED_D1.relative_to(ROOT)),
            "unified_resource_ledger_v2": str(UNIFIED_LEDGER_JSON.relative_to(ROOT)),
        },
        "a5": a5_summary(loaded["a5"]),
        "a2_a4": a2_summary(loaded["a2_a4"]),
        "m1": m1_summary(loaded["m1"]),
        "d1": d1_summary(loaded["d1"]),
        "d1_paired": paired,
        "top_tier_outcomes": top_tier_outcomes(ledger),
        "independent_verification": verifications,
        "integration_authority": integration,
        "independent_expectations_are_results": False,
        "authority": "PAPER_EVIDENCE_SUMMARY_ONLY_NO_SCIENTIFIC_AUTHORITY",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
