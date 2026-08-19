from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
RESEARCH = ROOT / "research" / "extensions" / "p9-structured-neural"
RESULTS = RESEARCH / "results"
OUT = Path(__file__).resolve().parent / "evidence" / "OFFICIAL_EVIDENCE_SUMMARY_V1.json"

SOURCES = {
    "a5": RESEARCH / "A5_D0_EXPLICIT_RESULT_V1.json",
    "a2_a4": RESULTS / "A2_A4_D0_EXPLICIT_RESULT_V1_1.json",
    "m1": RESULTS / "M1_RESULT_V1_5.json",
    "d1": RESULTS / "D1_RESULT_V1_2.json",
}

VERIFICATIONS = {
    "a2_a4": RESULTS / "A2_A4_D0_EXPLICIT_VERIFICATION_V1_1.json",
    "m1": RESULTS / "M1_INDEPENDENT_VERIFICATION_V1_5.json",
    "d1": RESULTS / "D1_INDEPENDENT_VERIFICATION_V1_2.json",
}

EXPECTED_TERMINALS = {
    "a5": {"A5_D0_EXPLICIT_INFERENCE_SUFFICIENT"},
    "a2_a4": {"A2_A4_D0_EXPLICIT_INFERENCE_SUFFICIENT"},
    "m1": {"M1_GLOBAL_COMPOSITION_RESIDUAL"},
    "d1": {"D1_TYPED_STRUCTURE_TRANSFER_SUPPORTED"},
}

EXPECTED_DIGESTS = {
    "a2_a4": "sha256:f775c6046520d10c346657fd13f24b51cd776b7436a2a99afc93e4c1ce9bb7f3",
    "m1": "sha256:01e1b62da27b424d453c63b798a5cbb13a915a4546b8ced68fcf84c32d04d97e",
    "d1": "sha256:34003fb8ffcecec6ed01654e40c644ff05b7640be56b398a45efc1e52a30141a",
}

INVALID_STATUS_MARKERS = {
    "INVALIDATED_PENDING_EXECUTABLE_HOSTILE_REPLAY",
    "INVALIDATED_PREVIOUS_ATTESTATION",
    "CANNOT_CHECK_PENDING_REEXECUTION",
    "CANNOT_CHECK",
    "INVALIDATED",
}


def _load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise SystemExit(f"missing official P9 evidence: {path.relative_to(ROOT)}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"official evidence is not a mapping: {path.relative_to(ROOT)}")
    return data


def _reject_invalid(name: str, data: dict[str, Any]) -> None:
    for field in ("status", "verification_state", "terminal"):
        value = data.get(field)
        if isinstance(value, str) and value in INVALID_STATUS_MARKERS:
            raise SystemExit(f"{name} evidence is invalid/pending: {field}={value}")
    terminal = data.get("terminal")
    if terminal not in EXPECTED_TERMINALS[name]:
        raise SystemExit(f"{name} has unrecognized/nonfinal terminal: {terminal!r}")
    expected_digest = EXPECTED_DIGESTS.get(name)
    if expected_digest is not None and data.get("result_digest") != expected_digest:
        raise SystemExit(
            f"{name} result digest mismatch: {data.get('result_digest')!r} != {expected_digest!r}"
        )


def _verification(name: str, result: dict[str, Any]) -> dict[str, Any]:
    path = VERIFICATIONS[name]
    verification = _load(path)
    status = verification.get("status")
    if not isinstance(status, str) or not status.startswith("BOUNDED_VERIFIED"):
        raise SystemExit(f"{name} verification is not bounded-verified: {status!r}")
    official_digest = verification.get("official_result_digest")
    if official_digest != result.get("result_digest"):
        raise SystemExit(
            f"{name} verification/result digest mismatch: {official_digest!r} != {result.get('result_digest')!r}"
        )
    discrepancy_count = verification.get("discrepancy_count")
    counts = verification.get("discrepancy_counts")
    if discrepancy_count is not None and discrepancy_count != 0:
        raise SystemExit(f"{name} verification has discrepancies: {discrepancy_count}")
    if isinstance(counts, dict) and counts.get("material") != 0:
        raise SystemExit(f"{name} verification has material discrepancies: {counts!r}")
    return {
        "status": status,
        "verification_path": str(path.relative_to(ROOT)),
        "material_discrepancies": counts.get("material", 0) if isinstance(counts, dict) else 0,
        "non_material_discrepancies": counts.get("non_material", 0) if isinstance(counts, dict) else 0,
    }


def _a5_summary(data: dict[str, Any]) -> dict[str, Any]:
    views = data.get("views")
    if not isinstance(views, dict):
        raise SystemExit("A5 official evidence lacks view results")
    if data.get("verification_state") != "BOUNDED_VERIFIED":
        raise SystemExit(f"A5 is not BOUNDED_VERIFIED: {data.get('verification_state')!r}")
    return {
        "terminal": data["terminal"],
        "verification_state": data["verification_state"],
        "typed_accuracy": views["TYPED"]["full_task_accuracy"],
        "typed_unknown_rate": views["TYPED"]["unknown_rate"],
        "current_accuracy": views["CURRENT"]["full_task_accuracy"],
        "semantic_accuracy": views["SEMANTIC"]["full_task_accuracy"],
        "result_digest": data.get("result_digest"),
    }


def _a2_a4_summary(data: dict[str, Any]) -> dict[str, Any]:
    relation = data.get("relation_views")
    history = data.get("history_views")
    hostile = data.get("hostile_checks")
    if not isinstance(relation, dict) or not isinstance(history, dict) or not isinstance(hostile, dict):
        raise SystemExit("A2/A4 official evidence lacks measured result blocks")
    if not all(value is True for value in hostile.values()):
        raise SystemExit(f"A2/A4 hostile checks are not all green: {hostile!r}")
    return {
        "terminal": data["terminal"],
        "relation": {
            view: {
                "coverage": relation[view]["coverage"],
                "full_task_accuracy": relation[view]["full_task_accuracy"],
            }
            for view in ("SURFACE", "TOPOLOGY", "TYPED", "CURRENT", "SEMANTIC")
        },
        "history": {
            view: {
                "coverage": history[view]["coverage"],
                "full_task_accuracy": history[view]["full_task_accuracy"],
            }
            for view in ("SURFACE", "TOPOLOGY", "TYPED", "CURRENT", "SEMANTIC")
        },
        "hostile_checks": hostile,
        "result_digest": data.get("result_digest"),
    }


def _m1_summary(data: dict[str, Any]) -> dict[str, Any]:
    views = data.get("views")
    if not isinstance(views, dict):
        raise SystemExit("M1 official evidence lacks view results")
    compact_views: dict[str, Any] = {}
    for view_name in ("SURFACE", "TOPOLOGY", "TYPED", "CURRENT", "SEMANTIC"):
        view = views[view_name]
        overall = view["test_overall"]
        row: dict[str, Any] = {
            "accuracy": overall["accuracy"],
            "exact_view_deterministic_accuracy_ceiling": overall[
                "exact_view_deterministic_accuracy_ceiling"
            ],
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
                "task_information_ceiling": gluing["test"][
                    "exact_view_deterministic_accuracy_ceiling"
                ],
            }
            row["mechanic_ranking_test_accuracy"] = mechanic["test"]["accuracy"]
        compact_views[view_name] = row
    return {
        "terminal": data["terminal"],
        "protocol": data.get("protocol"),
        "corpus_manifest_digest": data.get("corpus_manifest_digest"),
        "views": compact_views,
        "result_digest": data.get("result_digest"),
    }


def _d1_summary(data: dict[str, Any]) -> dict[str, Any]:
    results = data.get("results")
    if not isinstance(results, dict):
        raise SystemExit("D1 official evidence lacks representation-arm results")
    compact_results = {}
    for name, arm in results.items():
        compact_results[name] = {
            "selected_model": arm["selected"]["config_id"],
            "dev_accuracy": arm["selected"]["dev"]["accuracy"],
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
        "typed_minus_same_information_serialized": data.get(
            "typed_minus_same_information_serialized"
        ),
        "exact_typed_relational_comparator": data.get("exact_typed_relational_comparator"),
        "results": compact_results,
        "result_digest": data.get("result_digest"),
    }


def main() -> None:
    loaded = {name: _load(path) for name, path in SOURCES.items()}
    for name, data in loaded.items():
        _reject_invalid(name, data)

    verifications = {
        name: _verification(name, loaded[name]) for name in ("a2_a4", "m1", "d1")
    }

    summary = {
        "schema": "P9.OfficialEvidenceSummary.v1",
        "source_paths": {name: str(path.relative_to(ROOT)) for name, path in SOURCES.items()},
        "a5": _a5_summary(loaded["a5"]),
        "a2_a4": _a2_a4_summary(loaded["a2_a4"]),
        "m1": _m1_summary(loaded["m1"]),
        "d1": _d1_summary(loaded["d1"]),
        "independent_verification": verifications,
        "independent_expectations_are_results": False,
        "authority": "PAPER_EVIDENCE_SUMMARY_ONLY_NO_SCIENTIFIC_AUTHORITY",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
