from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
RESEARCH = ROOT / "research" / "extensions" / "p9-structured-neural"
EXPECTATION_PATH = RESEARCH / "verification" / "INDEPENDENT_REPLAY_EXPECTATIONS_V1.json"
OFFICIAL_PATHS = {
    "A5_D0": RESEARCH / "A5_D0_EXPLICIT_RESULT_V1.json",
    "A2_A4_D0": RESEARCH / "A2_A4_D0_EXPLICIT_RESULT_V1.json",
    "M1": RESEARCH / "execution" / "M1_EXECUTION_RESULT_V1_5.json",
    "D1": RESEARCH / "execution" / "D1_EXECUTION_RESULT_V1_2.json",
}
OUT = RESEARCH / "verification" / "FINAL_P9_OFFICIAL_VS_INDEPENDENT_V1.json"


def load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise SystemExit(f"missing required artifact: {path.relative_to(ROOT)}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"artifact is not a mapping: {path.relative_to(ROOT)}")
    return data


def close(a: Any, b: Any, *, atol: float = 1e-12) -> bool:
    if isinstance(a, bool) or isinstance(b, bool):
        return a is b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return math.isclose(float(a), float(b), abs_tol=atol, rel_tol=0.0)
    return a == b


def compare(path: str, actual: Any, expected: Any, mismatches: list[dict[str, Any]]) -> None:
    if not close(actual, expected):
        mismatches.append({"path": path, "expected": expected, "actual": actual})


def selected_dev(arm: dict[str, Any]) -> dict[str, Any]:
    """Return the dev metrics for the frozen selected D1 config.

    The durable D1 archive stores selected model identity separately from the
    full dev-configuration rows. Binding them by config_id is part of the
    verifier adapter; it does not re-select a model or inspect test outcomes.
    """

    selected = arm.get("selected")
    configurations = arm.get("dev_configurations")
    if not isinstance(selected, dict) or not isinstance(configurations, list):
        raise SystemExit("D1 arm lacks selected/dev_configurations structure")
    config_id = selected.get("config_id")
    matches = [row for row in configurations if isinstance(row, dict) and row.get("config_id") == config_id]
    if len(matches) != 1 or not isinstance(matches[0].get("dev"), dict):
        raise SystemExit(f"D1 selected config {config_id!r} does not bind exactly one dev row")
    return matches[0]["dev"]


def verify_a5(actual: dict[str, Any], expected: dict[str, Any], mismatches: list[dict[str, Any]]) -> None:
    compare("A5.terminal", actual.get("terminal"), expected["expected_terminal"], mismatches)
    views = actual.get("views", {})
    for mode in ("TYPED", "CURRENT", "SEMANTIC"):
        got = views.get(mode, {})
        exp = expected[mode]
        compare(f"A5.{mode}.sample_count", got.get("sample_count"), exp["sample_count"], mismatches)
        compare(f"A5.{mode}.accuracy", got.get("accuracy"), exp["accuracy"], mismatches)
        compare(f"A5.{mode}.unknown_rate", got.get("unknown_rate"), exp["unknown_rate"], mismatches)


def verify_a2_a4(actual: dict[str, Any], expected: dict[str, Any], mismatches: list[dict[str, Any]]) -> None:
    compare("A2_A4.terminal", actual.get("terminal"), expected["expected_terminal"], mismatches)
    relation = actual.get("relation_views", {})
    history = actual.get("history_views", {})
    for mode, exp in expected["relation"].items():
        got = relation.get(mode, {})
        compare(f"A2_A4.relation.{mode}.coverage", got.get("coverage"), exp["coverage"], mismatches)
        compare(f"A2_A4.relation.{mode}.full_task_accuracy", got.get("full_task_accuracy"), exp["full_task_accuracy"], mismatches)
    for mode, exp in expected["history"].items():
        got = history.get(mode, {})
        compare(f"A2_A4.history.{mode}.coverage", got.get("coverage"), exp["coverage"], mismatches)
        compare(f"A2_A4.history.{mode}.full_task_accuracy", got.get("full_task_accuracy"), exp["full_task_accuracy"], mismatches)
        if "hostile_pair_same_prediction" in exp:
            compare(f"A2_A4.history.{mode}.hostile_pair_same_prediction", got.get("hidden_view_pair_prediction_equal"), exp["hostile_pair_same_prediction"], mismatches)
    hostile = actual.get("hostile_checks")
    if not isinstance(hostile, dict) or not hostile or not all(v is True for v in hostile.values()):
        mismatches.append({"path": "A2_A4.hostile_checks", "expected": "all measured true", "actual": hostile})


def verify_d1(actual: dict[str, Any], expected: dict[str, Any], mismatches: list[dict[str, Any]]) -> None:
    compare("D1.terminal", actual.get("terminal"), expected["expected_terminal"], mismatches)
    compare("D1.test_domain", actual.get("test_domain"), expected["whole_domain_test"], mismatches)
    results = actual.get("results", {})
    for arm, exp in expected["arms"].items():
        got = results.get(arm, {})
        selected = got.get("selected", {})
        dev = selected_dev(got)
        test = got.get("test", {})
        compare(f"D1.{arm}.selected_model", selected.get("config_id"), exp["selected_model"], mismatches)
        compare(f"D1.{arm}.test_accuracy", test.get("accuracy"), exp["test_accuracy"], mismatches)
        compare(f"D1.{arm}.macro_f1", test.get("macro_f1"), exp["macro_f1"], mismatches)
        compare(f"D1.{arm}.double_corruption_accuracy", test.get("double_corruption_accuracy"), exp["double_corruption_accuracy"], mismatches)
        compare(f"D1.{arm}.unresolved_accuracy", test.get("unresolved_accuracy"), exp["unresolved_accuracy"], mismatches)
        compare(f"D1.{arm}.dev_accuracy", dev.get("accuracy"), exp["dev_accuracy"], mismatches)
    compare("D1.typed_minus_transcript", actual.get("typed_minus_transcript"), expected["typed_minus_transcript"], mismatches)
    compare("D1.typed_minus_same_information_serialized", actual.get("typed_minus_same_information_serialized"), expected["typed_minus_same_information_serialized"], mismatches)
    compare("D1.exact_typed_relational_comparator_accuracy", actual.get("exact_typed_relational_comparator", {}).get("accuracy"), expected["exact_typed_relational_comparator_accuracy"], mismatches)


def verify_m1(actual: dict[str, Any], expected: dict[str, Any], mismatches: list[dict[str, Any]]) -> None:
    compare("M1.terminal", actual.get("terminal"), expected["expected_terminal_family"], mismatches)
    views = actual.get("views", {})
    target = float(expected["transport_F2_independent_reimplementation"]["protected_test_accuracy_approx"])
    for mode in ("CURRENT", "SEMANTIC"):
        overall = views.get(mode, {}).get("test_overall", {})
        fam = overall.get("per_family_accuracy", {})
        transport = fam.get("TRANSPORT_GLUING")
        if not isinstance(transport, (int, float)):
            mismatches.append({"path": f"M1.{mode}.transport_accuracy", "expected": "numeric", "actual": transport})
            continue
        if abs(float(transport) - target) > 0.10:
            mismatches.append({"path": f"M1.{mode}.transport_accuracy_approx", "expected": target, "tolerance": 0.10, "actual": transport})
        if float(transport) >= 1.0 - 1e-12:
            mismatches.append({"path": f"M1.{mode}.transport_residual", "expected": "below exact ceiling", "actual": transport})


def main() -> None:
    expectations = load(EXPECTATION_PATH)
    actuals = {name: load(path) for name, path in OFFICIAL_PATHS.items()}
    mismatches: list[dict[str, Any]] = []
    verify_m1(actuals["M1"], expectations["M1"], mismatches)
    verify_a5(actuals["A5_D0"], expectations["A5_D0"], mismatches)
    verify_a2_a4(actuals["A2_A4_D0"], expectations["A2_A4_D0"], mismatches)
    verify_d1(actuals["D1"], expectations["D1"], mismatches)
    receipt = {
        "schema": "P9.FinalOfficialVsIndependentReceipt.v1.2",
        "expectation_path": str(EXPECTATION_PATH.relative_to(ROOT)),
        "official_paths": {name: str(path.relative_to(ROOT)) for name, path in OFFICIAL_PATHS.items()},
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "terminal": "INDEPENDENT_REPLAY_AGREES" if not mismatches else "DISAGREEMENT_BLOCKS_PROMOTION",
        "claim_authority": "VERIFICATION_RECEIPT_ONLY_NO_SCIENTIFIC_AUTHORITY",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    if mismatches:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
