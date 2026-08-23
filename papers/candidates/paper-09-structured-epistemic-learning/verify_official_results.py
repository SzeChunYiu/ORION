from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
RESEARCH = ROOT / "research" / "extensions" / "p9-structured-neural"
EXPECTATION_PATH = RESEARCH / "verification" / "INDEPENDENT_REPLAY_EXPECTATIONS_V1.json"
OFFICIAL_PATHS = {
    "A5_D0": RESEARCH / "A5_D0_EXPLICIT_RESULT_V1.json",
    "A2_A4_D0": RESEARCH / "A2_A4_D0_EXPLICIT_RESULT_V1.json",
    "M1": RESEARCH / "M1_RESULT_V1.json",
    "D1": RESEARCH / "D1_RESULT_V1.json",
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


def nested(data: dict[str, Any], *keys: str) -> Any:
    cur: Any = data
    for key in keys:
        if not isinstance(cur, dict) or key not in cur:
            raise KeyError(".".join(keys))
        cur = cur[key]
    return cur


def verify_a5(actual: dict[str, Any], expected: dict[str, Any], mismatches: list[dict[str, Any]]) -> None:
    compare("A5.terminal", actual.get("terminal"), expected["expected_terminal"], mismatches)
    views = actual.get("views")
    if not isinstance(views, dict):
        mismatches.append({"path": "A5.views", "expected": "mapping", "actual": type(views).__name__})
        return
    for mode in ("TYPED", "CURRENT", "SEMANTIC"):
        exp = expected[mode]
        got = views.get(mode)
        if not isinstance(got, dict):
            mismatches.append({"path": f"A5.{mode}", "expected": "mapping", "actual": got})
            continue
        compare(f"A5.{mode}.sample_count", got.get("sample_count"), exp["sample_count"], mismatches)
        compare(f"A5.{mode}.accuracy", got.get("full_task_accuracy"), exp["accuracy"], mismatches)
        compare(f"A5.{mode}.unknown_rate", got.get("unknown_rate"), exp["unknown_rate"], mismatches)


def verify_a2_a4(actual: dict[str, Any], expected: dict[str, Any], mismatches: list[dict[str, Any]]) -> None:
    compare("A2_A4.terminal", actual.get("terminal"), expected["expected_terminal"], mismatches)
    relation = actual.get("relation_views")
    history = actual.get("history_views")
    hostile = actual.get("hostile_checks")
    if not isinstance(relation, dict) or not isinstance(history, dict):
        mismatches.append({"path": "A2_A4.views", "expected": "measured mappings", "actual": None})
        return
    for mode, exp in expected["relation"].items():
        got = relation.get(mode, {})
        compare(f"A2_A4.relation.{mode}.coverage", got.get("coverage"), exp["coverage"], mismatches)
        compare(
            f"A2_A4.relation.{mode}.full_task_accuracy",
            got.get("full_task_accuracy"),
            exp["full_task_accuracy"],
            mismatches,
        )
    for mode, exp in expected["history"].items():
        got = history.get(mode, {})
        compare(f"A2_A4.history.{mode}.coverage", got.get("coverage"), exp["coverage"], mismatches)
        compare(
            f"A2_A4.history.{mode}.full_task_accuracy",
            got.get("full_task_accuracy"),
            exp["full_task_accuracy"],
            mismatches,
        )
        if "hostile_pair_same_prediction" in exp:
            compare(
                f"A2_A4.history.{mode}.hostile_pair_same_prediction",
                got.get("hidden_view_pair_prediction_equal"),
                exp["hostile_pair_same_prediction"],
                mismatches,
            )
    if not isinstance(hostile, dict) or not hostile or not all(value is True for value in hostile.values()):
        mismatches.append({"path": "A2_A4.hostile_checks", "expected": "all measured true", "actual": hostile})


def verify_d1(actual: dict[str, Any], expected: dict[str, Any], mismatches: list[dict[str, Any]]) -> None:
    compare("D1.terminal", actual.get("terminal"), expected["expected_terminal"], mismatches)
    compare("D1.test_domain", actual.get("test_domain"), expected["whole_domain_test"], mismatches)
    results = actual.get("results")
    if not isinstance(results, dict):
        mismatches.append({"path": "D1.results", "expected": "mapping", "actual": type(results).__name__})
        return
    for arm, exp in expected["arms"].items():
        got = results.get(arm)
        if not isinstance(got, dict):
            mismatches.append({"path": f"D1.{arm}", "expected": "mapping", "actual": got})
            continue
        selected = got.get("selected") if isinstance(got.get("selected"), dict) else {}
        test = got.get("test") if isinstance(got.get("test"), dict) else {}
        dev_configs = got.get("dev_configurations")
        compare(f"D1.{arm}.selected_model", selected.get("config_id"), exp["selected_model"], mismatches)
        compare(f"D1.{arm}.test_accuracy", test.get("accuracy"), exp["test_accuracy"], mismatches)
        compare(f"D1.{arm}.macro_f1", test.get("macro_f1"), exp["macro_f1"], mismatches)
        compare(
            f"D1.{arm}.double_corruption_accuracy",
            test.get("double_corruption_accuracy"),
            exp["double_corruption_accuracy"],
            mismatches,
        )
        compare(f"D1.{arm}.unresolved_accuracy", test.get("unresolved_accuracy"), exp["unresolved_accuracy"], mismatches)
        if isinstance(dev_configs, list):
            selected_dev = next(
                (row for row in dev_configs if isinstance(row, dict) and row.get("config_id") == selected.get("config_id")),
                None,
            )
            if isinstance(selected_dev, dict):
                compare(f"D1.{arm}.dev_accuracy", selected_dev.get("accuracy"), exp["dev_accuracy"], mismatches)
            else:
                mismatches.append({"path": f"D1.{arm}.dev_accuracy", "expected": exp["dev_accuracy"], "actual": "selected config missing"})
        else:
            mismatches.append({"path": f"D1.{arm}.dev_configurations", "expected": "list", "actual": dev_configs})
    compare("D1.typed_minus_transcript", actual.get("typed_minus_transcript"), expected["typed_minus_transcript"], mismatches)
    compare(
        "D1.typed_minus_same_information_serialized",
        actual.get("typed_minus_same_information_serialized"),
        expected["typed_minus_same_information_serialized"],
        mismatches,
    )
    oracle = actual.get("exact_typed_relational_comparator")
    if isinstance(oracle, dict):
        compare(
            "D1.exact_typed_relational_comparator_accuracy",
            oracle.get("accuracy"),
            expected["exact_typed_relational_comparator_accuracy"],
            mismatches,
        )
    else:
        mismatches.append({"path": "D1.exact_typed_relational_comparator", "expected": "mapping", "actual": oracle})


def verify_m1(actual: dict[str, Any], expected: dict[str, Any], mismatches: list[dict[str, Any]]) -> None:
    compare("M1.terminal", actual.get("terminal"), expected["expected_terminal_family"], mismatches)
    views = actual.get("views")
    if not isinstance(views, dict):
        mismatches.append({"path": "M1.views", "expected": "mapping", "actual": type(views).__name__})
        return
    # The independent verifier's quantitative M1 expectation is intentionally approximate
    # and scoped to the transport/global-composition residual.  Require CURRENT and SEMANTIC
    # to remain below their information ceilings on the transport family and near the 0.5
    # expected diagnostic level rather than overfitting an exact float not frozen as exact.
    for mode in ("CURRENT", "SEMANTIC"):
        view = views.get(mode)
        if not isinstance(view, dict):
            mismatches.append({"path": f"M1.{mode}", "expected": "mapping", "actual": view})
            continue
        overall = view.get("test_overall")
        if not isinstance(overall, dict):
            mismatches.append({"path": f"M1.{mode}.test_overall", "expected": "mapping", "actual": overall})
            continue
        fam = overall.get("per_family_accuracy")
        if not isinstance(fam, dict):
            mismatches.append({"path": f"M1.{mode}.per_family_accuracy", "expected": "mapping", "actual": fam})
            continue
        transport = fam.get("TRANSPORT_GLUING")
        if not isinstance(transport, (int, float)):
            mismatches.append({"path": f"M1.{mode}.transport_accuracy", "expected": "numeric", "actual": transport})
            continue
        if abs(float(transport) - float(expected["transport_F2_independent_reimplementation"]["protected_test_accuracy_approx"])) > 0.10:
            mismatches.append(
                {
                    "path": f"M1.{mode}.transport_accuracy_approx",
                    "expected": expected["transport_F2_independent_reimplementation"]["protected_test_accuracy_approx"],
                    "tolerance": 0.10,
                    "actual": transport,
                }
            )
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
        "schema": "P9.FinalOfficialVsIndependentReceipt.v1",
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
