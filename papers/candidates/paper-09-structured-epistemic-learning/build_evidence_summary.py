from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
RESEARCH = ROOT / "research" / "extensions" / "p9-structured-neural"
OUT = HERE / "evidence" / "OFFICIAL_EVIDENCE_SUMMARY_V1.json"

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


def load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise SystemExit(f"missing official P9 evidence: {path.relative_to(ROOT)}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"official evidence is not a mapping: {path.relative_to(ROOT)}")
    return value


def require_receipt(name: str, *tokens: str) -> dict[str, Any]:
    path = RECEIPTS[name]
    if not path.is_file():
        raise SystemExit(f"missing verification receipt: {path.relative_to(ROOT)}")
    text = path.read_text(encoding="utf-8")
    missing = [token for token in tokens if token not in text]
    if missing:
        raise SystemExit(f"{name} verification receipt missing required tokens: {missing}")
    return {"status": "BOUNDED_VERIFIED", "verification_path": str(path.relative_to(ROOT)), "required_tokens": list(tokens)}


def check(name: str, data: dict[str, Any]) -> None:
    if data.get("terminal") != EXPECTED_TERMINALS[name]:
        raise SystemExit(f"{name} unexpected terminal: {data.get('terminal')!r}")
    if name in EXPECTED_DIGESTS and data.get("result_digest") != EXPECTED_DIGESTS[name]:
        raise SystemExit(f"{name} result digest mismatch: {data.get('result_digest')!r}")
    if name == "a5" and data.get("verification_state") != "BOUNDED_VERIFIED":
        raise SystemExit(f"A5 not bounded verified: {data.get('verification_state')!r}")
    if name == "a2_a4":
        if data.get("verification_state") != "BOUNDED_VERIFIED":
            raise SystemExit(f"A2/A4 not bounded verified: {data.get('verification_state')!r}")
        hostile = data.get("hostile_checks")
        if not isinstance(hostile, dict) or not hostile or not all(v is True for v in hostile.values()):
            raise SystemExit(f"A2/A4 hostile checks not all green: {hostile!r}")


def a5_summary(data: dict[str, Any]) -> dict[str, Any]:
    views = data["views"]
    return {
        "terminal": data["terminal"], "verification_state": data["verification_state"],
        "typed_accuracy": views["TYPED"]["full_task_accuracy"],
        "typed_unknown_rate": views["TYPED"]["unknown_rate"],
        "current_accuracy": views["CURRENT"]["full_task_accuracy"],
        "semantic_accuracy": views["SEMANTIC"]["full_task_accuracy"],
        "result_digest": data.get("result_digest"),
    }


def a2_summary(data: dict[str, Any]) -> dict[str, Any]:
    relation, history = data["relation_views"], data["history_views"]
    return {
        "terminal": data["terminal"],
        "relation": {v: {"coverage": relation[v]["coverage"], "full_task_accuracy": relation[v]["full_task_accuracy"]} for v in ("SURFACE","TOPOLOGY","TYPED","CURRENT","SEMANTIC")},
        "history": {v: {"coverage": history[v]["coverage"], "full_task_accuracy": history[v]["full_task_accuracy"]} for v in ("SURFACE","TOPOLOGY","TYPED","CURRENT","SEMANTIC")},
        "hostile_checks": data["hostile_checks"],
        "verification_state": data["verification_state"],
    }


def m1_summary(data: dict[str, Any]) -> dict[str, Any]:
    compact: dict[str, Any] = {}
    for view_name in ("SURFACE","TOPOLOGY","TYPED","CURRENT","SEMANTIC"):
        view = data["views"][view_name]
        overall = view["test_overall"]
        row: dict[str, Any] = {
            "accuracy": overall["accuracy"],
            "exact_view_deterministic_accuracy_ceiling": overall["exact_view_deterministic_accuracy_ceiling"],
            "ceiling_violation": overall["ceiling_violation"],
        }
        if view_name in {"CURRENT","SEMANTIC"}:
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
    return {"terminal": data["terminal"], "protocol": data.get("protocol"), "corpus_manifest_digest": data.get("corpus_manifest_digest"), "views": compact, "result_digest": data["result_digest"]}


def d1_summary(data: dict[str, Any]) -> dict[str, Any]:
    compact = {}
    for name, arm in data["results"].items():
        compact[name] = {
            "selected_model": arm["selected"]["config_id"],
            "dev_accuracy": arm["selected"]["dev"]["accuracy"],
            "test_accuracy": arm["test"]["accuracy"],
            "macro_f1": arm["test"]["macro_f1"],
            "double_corruption_accuracy": arm["test"]["double_corruption_accuracy"],
            "unresolved_accuracy": arm["test"]["unresolved_accuracy"],
        }
    return {
        "terminal": data["terminal"], "subject_sha": data.get("subject_sha"),
        "train_domains": data.get("train_domains"), "test_domain": data.get("test_domain"),
        "dataset_manifest_digest": data.get("dataset_manifest_digest"),
        "typed_minus_transcript": data.get("typed_minus_transcript"),
        "typed_minus_same_information_serialized": data.get("typed_minus_same_information_serialized"),
        "exact_typed_relational_comparator": data.get("exact_typed_relational_comparator"),
        "results": compact, "result_digest": data["result_digest"],
    }


def main() -> None:
    loaded = {name: load(path) for name, path in SOURCES.items()}
    for name, data in loaded.items(): check(name, data)
    verifications = {
        "a2_a4": require_receipt("a2_a4", "A2_A4_D0_EXPLICIT_INFERENCE_SUFFICIENT", "BOUNDED_VERIFIED"),
        "m1": require_receipt("m1", "M1_GLOBAL_COMPOSITION_RESIDUAL", "BOUNDED_VERIFIED_WITH_ADJUDICATED_NON_MATERIAL_DISCREPANCY", "Material discrepancy count `0`"),
        "d1": require_receipt("d1", "D1_TYPED_STRUCTURE_TRANSFER_SUPPORTED", "zero material discrepancies"),
    }
    summary = {
        "schema": "P9.OfficialEvidenceSummary.v1",
        "source_paths": {name: str(path.relative_to(ROOT)) for name, path in SOURCES.items()},
        "a5": a5_summary(loaded["a5"]), "a2_a4": a2_summary(loaded["a2_a4"]),
        "m1": m1_summary(loaded["m1"]), "d1": d1_summary(loaded["d1"]),
        "independent_verification": verifications,
        "independent_expectations_are_results": False,
        "authority": "PAPER_EVIDENCE_SUMMARY_ONLY_NO_SCIENTIFIC_AUTHORITY",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(OUT.relative_to(ROOT))


if __name__ == "__main__": main()
