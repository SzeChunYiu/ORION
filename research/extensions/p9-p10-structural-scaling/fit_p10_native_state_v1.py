from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
import warnings
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parents[3]
P10 = ROOT / "papers" / "candidates" / "paper-10-content-bound-math-evaluation"
FRAMEWORK = ROOT / "papers" / "candidates" / "orion-learning-machine" / "framework"
sys.path.insert(0, str(FRAMEWORK))
from orion_learning_machine.adapters import lean_source  # noqa: E402

MANIFEST = P10 / "benchmark" / "MATHLIB_CORPUS_V2_MANIFEST.json"
CORPUS = P10 / "benchmark" / "corpus" / "mathlib4_e72c1e277f31"
V21 = P10 / "results" / "MATHLIB_TRANSFER_V2_1.json"
MATHLIB_COMMIT = "e72c1e277f31441626621f7d0c7207862fc25569"
LEAN_TOOLCHAIN = "leanprover/lean4:v4.34.0-rc1"
CS = (0.01, 0.1, 1.0, 10.0)
FAMILIES = tuple(name for name, _ in lean_source.TACTIC_FAMILIES)
FAMILY_INDEX = {name: index for index, name in enumerate(FAMILIES)}
SHAPES = (
    "equality", "iff", "conjunction", "disjunction", "implication_function",
    "forall", "exists", "order_comparison", "arithmetic_algebraic", "prop_type_sort", "other",
)
TOKEN_BUCKETS = ("0-31", "32-63", "64-127", "128-255", "256-511", "512+")
DEPTH_BUCKETS = ("0-2", "3-5", "6-9", "10+")
FLAGS = (
    "has_equality", "has_conjunction_disjunction", "has_implication_function",
    "has_quantification", "has_arithmetic_algebraic", "has_prop_type_sort",
)
DENOMINATOR = 11_842
warnings.filterwarnings("ignore", category=ConvergenceWarning)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_population() -> list[dict[str, Any]]:
    manifest = json.loads(MANIFEST.read_text())
    rows: list[dict[str, Any]] = []
    order = 0
    for item in manifest["files"]:
        text = (CORPUS / item["path"]).read_text(encoding="utf-8")
        for theorem in lean_source.parse_lean_source(text, item["path"]):
            mechanics = list(theorem.tactics)
            for action_index in range(1, len(mechanics)):
                transition_id = hashlib.sha256(
                    f"{item['path']}|{theorem.theorem_name}|{action_index}".encode()
                ).hexdigest()[:32]
                rows.append({
                    "transition_id": transition_id,
                    "source_path": item["path"],
                    "source_sha256": item["sha256"],
                    "theorem_name": theorem.theorem_name,
                    "top_module": item["top_module"],
                    "previous_family": mechanics[action_index - 1],
                    "true_action": mechanics[action_index],
                    "source_order": order,
                })
                order += 1
    expected = int(json.loads(V21.read_text())["leave_top_module_out"]["transitions"])
    if len(rows) != expected or expected != DENOMINATOR:
        raise SystemExit(f"source transition denominator mismatch: {len(rows)} vs {expected}")
    return rows


def merge_shards(paths: list[str]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    total_denominator = total_eligible = total_files = 0
    seen_shards: set[tuple[int, int]] = set()
    file_status: Counter[str] = Counter()
    for path in paths:
        data = json.loads(Path(path).read_text())
        if data.get("schema") != "P10.NativeTraceStateShard.v1":
            raise SystemExit(f"bad shard schema: {path}")
        if data.get("mathlib_commit") != MATHLIB_COMMIT or data.get("lean_toolchain") != LEAN_TOOLCHAIN:
            raise SystemExit("runtime identity mismatch in shard")
        identity = (int(data["shard_index"]), int(data["shard_count"]))
        if identity in seen_shards:
            raise SystemExit(f"duplicate shard {identity}")
        seen_shards.add(identity)
        total_denominator += int(data["transition_denominator"])
        total_eligible += int(data["eligible_transitions"])
        total_files += int(data["selected_files"])
        rows.extend(data["rows"])
        file_status.update(str(item["status"]) for item in data["files"])
    shard_counts = {count for _, count in seen_shards}
    if len(shard_counts) != 1 or len(seen_shards) != next(iter(shard_counts)):
        raise SystemExit(f"incomplete shard set: {sorted(seen_shards)}")
    return rows, {
        "transition_denominator": total_denominator,
        "reported_eligible_transitions": total_eligible,
        "selected_files": total_files,
        "file_status": dict(file_status),
    }


def verify_receipt(row: dict[str, Any]) -> bool:
    material = {
        key: row[key]
        for key in (
            "transition_id", "source_path", "source_sha256", "theorem_name", "action_index",
            "previous_family", "true_action", "state_sha256", "mathlib_commit", "lean_toolchain",
        )
    }
    expected = sha(json.dumps(material, sort_keys=True, separators=(",", ":")).encode())
    return expected == row.get("receipt_sha256")


def align_rows(trace_rows: list[dict[str, Any]], source_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    source = {row["transition_id"]: row for row in source_rows}
    aligned: list[dict[str, Any]] = []
    seen: set[str] = set()
    for trace in trace_rows:
        tid = trace["transition_id"]
        if tid in seen:
            raise SystemExit(f"duplicate transition receipt {tid}")
        seen.add(tid)
        original = source.get(tid)
        if original is None:
            raise SystemExit(f"trace transition not in V2.1 population: {tid}")
        for key in ("source_path", "source_sha256", "theorem_name", "top_module", "previous_family", "true_action"):
            if trace.get(key) != original.get(key):
                raise SystemExit(f"trace/source mismatch {tid} {key}")
        if not verify_receipt(trace):
            raise SystemExit(f"receipt verification failed: {tid}")
        aligned.append({**trace, "source_order": original["source_order"]})
    aligned.sort(key=lambda row: int(row["source_order"]))
    return aligned


def vector(row: dict[str, Any], kind: str) -> np.ndarray:
    state = row["state_features"]
    dep = row["dependency_features"]
    values: list[float] = [float(state["num_goals"]), float(state["context_cardinality"])]
    values.extend(float(state["context_shape_histogram"].get(shape_name, 0)) for shape_name in SHAPES)
    values.extend(1.0 if state.get(flag) else 0.0 for flag in FLAGS)
    values.extend(1.0 if state.get("goal_shape") == shape_name else 0.0 for shape_name in SHAPES)
    values.extend(1.0 if state.get("state_token_bucket") == bucket_name else 0.0 for bucket_name in TOKEN_BUCKETS)
    values.extend(1.0 if state.get("visible_depth_bucket") == bucket_name else 0.0 for bucket_name in DEPTH_BUCKETS)
    if kind in {"B3", "B4"}:
        values.extend(1.0 if row["previous_family"] == family else 0.0 for family in FAMILIES)
    if kind == "B4":
        values.extend([
            float(dep["context_reference_edges"]),
            float(dep["goal_context_references"]),
            float(dep["max_context_reference_indegree"]),
            float(dep["referencing_declaration_fraction"]),
        ])
    return np.asarray(values, dtype=np.float64)


def matrix(rows: list[dict[str, Any]], kind: str) -> np.ndarray:
    return np.vstack([vector(row, kind) for row in rows])


def labels(rows: list[dict[str, Any]]) -> np.ndarray:
    return np.asarray([FAMILY_INDEX[row["true_action"]] for row in rows], dtype=np.int64)


def fit_model(train: list[dict[str, Any]], kind: str, c: float, y_override: np.ndarray | None = None) -> LogisticRegression:
    X = matrix(train, kind)
    y = labels(train) if y_override is None else y_override
    if len(set(int(v) for v in y.tolist())) < 2:
        raise ValueError("training fold has fewer than two action classes")
    model = LogisticRegression(C=c, solver="lbfgs", max_iter=2000)
    model.fit(X, y)
    return model


def model_nll(model: LogisticRegression, rows: list[dict[str, Any]], kind: str) -> tuple[float, list[dict[str, Any]]]:
    X = matrix(rows, kind)
    probabilities = model.predict_proba(X)
    predictions = model.predict(X)
    class_to_col = {int(value): index for index, value in enumerate(model.classes_)}
    result: list[dict[str, Any]] = []
    total = 0.0
    for row, pred, probs in zip(rows, predictions, probabilities):
        true_index = FAMILY_INDEX[row["true_action"]]
        p_true = float(probs[class_to_col[true_index]]) if true_index in class_to_col else 1e-15
        p_true = max(p_true, 1e-15)
        total += -math.log(p_true)
        result.append({"predicted_action": FAMILIES[int(pred)], "p_true": p_true})
    return total, result


def choose_c(outer_train: list[dict[str, Any]], kind: str) -> tuple[float, dict[str, float]]:
    modules = sorted({row["top_module"] for row in outer_train})
    scores: dict[str, float] = {}
    for c in CS:
        total_loss = 0.0
        total_n = 0
        for held in modules:
            train = [row for row in outer_train if row["top_module"] != held]
            valid = [row for row in outer_train if row["top_module"] == held]
            if not valid:
                continue
            try:
                model = fit_model(train, kind, c)
                loss, _ = model_nll(model, valid, kind)
            except ValueError:
                loss = len(valid) * (-math.log(1e-15))
            total_loss += loss
            total_n += len(valid)
        scores[str(c)] = total_loss / total_n if total_n else float("inf")
    selected = min(CS, key=lambda c: (scores[str(c)], c))
    return selected, scores


def build_markov(train_source: list[dict[str, Any]]) -> tuple[dict[str, Counter[str]], Counter[str]]:
    next_by: dict[str, Counter[str]] = defaultdict(Counter)
    global_next: Counter[str] = Counter()
    for row in train_source:
        next_by[row["previous_family"]][row["true_action"]] += 1
        global_next[row["true_action"]] += 1
    return next_by, global_next


def markov_result(next_by: dict[str, Counter[str]], global_next: Counter[str], row: dict[str, Any]) -> tuple[dict[str, Any], str]:
    history_counts = next_by.get(row["previous_family"])
    counts = history_counts if history_counts else global_next
    prediction = counts.most_common(1)[0][0]
    denominator = sum(counts.values()) + len(FAMILIES)
    p_true = (counts.get(row["true_action"], 0) + 1) / denominator
    global_prediction = global_next.most_common(1)[0][0]
    return {"predicted_action": prediction, "p_true": p_true}, global_prediction


def forbidden_feature_scan(row: dict[str, Any]) -> bool:
    payload = json.dumps({
        "state_features": row["state_features"],
        "dependency_features": row["dependency_features"],
        "previous_family": row["previous_family"],
    }, sort_keys=True)
    forbidden = [row["source_path"], row["theorem_name"], row["top_module"], row["state_sha256"], row["transition_id"]]
    return not any(value and str(value) in payload for value in forbidden)


def hostile_identity_checks(rows: list[dict[str, Any]]) -> dict[str, bool]:
    future_step = True
    forbidden = True
    for row in rows:
        before = vector(row, "B4").tobytes()
        mutated = dict(row)
        mutated["true_action"] = FAMILIES[(FAMILY_INDEX[row["true_action"]] + 1) % len(FAMILIES)]
        future_step = future_step and before == vector(mutated, "B4").tobytes()
        forbidden = forbidden and forbidden_feature_scan(row)

    receipt_substitution = source_mutation = runtime_mutation = True
    if len(rows) >= 2:
        a = dict(rows[0])
        a["state_sha256"] = rows[1]["state_sha256"]
        receipt_substitution = not verify_receipt(a)
        b = dict(rows[0])
        b["source_sha256"] = "0" * 64
        source_mutation = not verify_receipt(b)
        c = dict(rows[0])
        c["mathlib_commit"] = "0" * 40
        runtime_mutation = not verify_receipt(c)
    return {
        "future_step_mutation": future_step,
        "module_identity_no_forbidden_fields": forbidden,
        "receipt_substitution": receipt_substitution,
        "source_mutation": source_mutation,
        "runtime_mutation": runtime_mutation,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--shards", nargs="+", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    source_rows = source_population()
    trace_rows, extraction = merge_shards(args.shards)
    if extraction["transition_denominator"] != DENOMINATOR:
        raise SystemExit(f"shard denominator mismatch: {extraction['transition_denominator']}")
    rows = align_rows(trace_rows, source_rows)
    if extraction["reported_eligible_transitions"] != len(rows):
        raise SystemExit("eligible count/row count mismatch")
    coverage = len(rows) / DENOMINATOR
    identity_controls = hostile_identity_checks(rows)

    if coverage < 0.80:
        output = {
            "schema": "P10.NativeStatePredictions.v1",
            "terminal": "CANNOT_CHECK_NATIVE_STATE_COVERAGE",
            "eligibility_coverage": coverage,
            "transition_denominator": DENOMINATOR,
            "eligible_transitions": len(rows),
            "extraction": extraction,
            "controls": identity_controls,
            "rows": [],
        }
        Path(args.output).write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
        print(json.dumps(output, indent=2, sort_keys=True))
        return

    source_by_module: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in source_rows:
        source_by_module[row["top_module"]].append(row)
    eligible_by_module: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        eligible_by_module[row["top_module"]].append(row)

    outer_modules = sorted(eligible_by_module)
    predictions: dict[str, dict[str, Any]] = {row["transition_id"]: {} for row in rows}
    fold_receipts: list[dict[str, Any]] = []
    shuffle_correct = shuffle_n = unigram_correct = 0
    dedup_b4_correct = dedup_b1_correct = dedup_n = 0
    secondary_correct = {"B2": 0, "B3": 0, "B4": 0}

    for outer in outer_modules:
        outer_train = [row for row in rows if row["top_module"] != outer]
        outer_test = eligible_by_module[outer]
        source_train = [row for row in source_rows if row["top_module"] != outer]
        next_by, global_next = build_markov(source_train)

        selected_c: dict[str, float] = {}
        inner_scores: dict[str, dict[str, float]] = {}
        fitted: dict[str, LogisticRegression] = {}
        test_outputs: dict[str, list[dict[str, Any]]] = {}
        for kind in ("B2", "B3", "B4"):
            c, scores = choose_c(outer_train, kind)
            selected_c[kind] = c
            inner_scores[kind] = scores
            fitted[kind] = fit_model(outer_train, kind, c)
            _, test_outputs[kind] = model_nll(fitted[kind], outer_test, kind)

        train_digests = {row["normalized_state_sha256"] for row in outer_train}
        strict_ids = {
            row["transition_id"]
            for row in outer_test
            if row["normalized_state_sha256"] not in train_digests
        }

        # Frozen label-shuffle control for B4.
        y_train = labels(outer_train)
        shuffled = np.array(y_train, copy=True)
        np.random.default_rng(914033).shuffle(shuffled)
        shuffle_model = fit_model(outer_train, "B4", selected_c["B4"], y_override=shuffled)
        _, shuffle_outputs = model_nll(shuffle_model, outer_test, "B4")

        for index, row in enumerate(outer_test):
            b1, b0_prediction = markov_result(next_by, global_next, row)
            b2 = test_outputs["B2"][index]
            b3 = test_outputs["B3"][index]
            b4 = test_outputs["B4"][index]
            predictions[row["transition_id"]] = {"B0_predicted_action": b0_prediction, "B1": b1, "B2": b2, "B3": b3, "B4": b4}
            for kind, result in (("B2", b2), ("B3", b3), ("B4", b4)):
                secondary_correct[kind] += int(result["predicted_action"] == row["true_action"])
            shuffle_correct += int(shuffle_outputs[index]["predicted_action"] == row["true_action"])
            shuffle_n += 1
            unigram_correct += int(b0_prediction == row["true_action"])
            if row["transition_id"] in strict_ids:
                dedup_n += 1
                dedup_b1_correct += int(b1["predicted_action"] == row["true_action"])
                dedup_b4_correct += int(b4["predicted_action"] == row["true_action"])

        fold_receipts.append({
            "held_out_module": outer,
            "train_rows": len(outer_train),
            "test_rows": len(outer_test),
            "strict_deduplicated_test_rows": len(strict_ids),
            "selected_C": selected_c,
            "nested_log_loss": inner_scores,
        })

    output_rows: list[dict[str, Any]] = []
    for row in rows:
        pred = predictions[row["transition_id"]]
        output_rows.append({
            "transition_id": row["transition_id"],
            "module": row["top_module"],
            "true_action": row["true_action"],
            "B1": pred["B1"],
            "B3": pred["B3"],
            "B4": pred["B4"],
        })

    shuffle_accuracy = shuffle_correct / shuffle_n
    unigram_accuracy = unigram_correct / shuffle_n
    near_duplicate_delta = (
        (dedup_b4_correct - dedup_b1_correct) / dedup_n if dedup_n else 0.0
    )
    controls = {
        **identity_controls,
        "label_shuffle": shuffle_accuracy <= unigram_accuracy + 0.02,
        "near_duplicate_strict_nonnegative": dedup_n > 0 and near_duplicate_delta >= 0,
    }
    terminal = "PREDICTIONS_READY_FOR_FROZEN_NATIVE_ANALYZER" if all(controls.values()) else "NATIVE_HOSTILE_CONTROL_FAILED"
    output = {
        "schema": "P10.NativeStatePredictions.v1",
        "terminal": terminal,
        "eligibility_coverage": coverage,
        "transition_denominator": DENOMINATOR,
        "eligible_transitions": len(rows),
        "extraction": extraction,
        "controls": controls,
        "shuffle_control": {
            "B4_shuffled_accuracy": shuffle_accuracy,
            "unigram_accuracy": unigram_accuracy,
            "margin": shuffle_accuracy - unigram_accuracy,
        },
        "near_duplicate_control": {
            "strict_rows": dedup_n,
            "B1_accuracy": dedup_b1_correct / dedup_n if dedup_n else None,
            "B4_accuracy": dedup_b4_correct / dedup_n if dedup_n else None,
            "B4_minus_B1": near_duplicate_delta if dedup_n else None,
        },
        "secondary_accuracy": {kind: count / len(rows) for kind, count in secondary_correct.items()},
        "fold_receipts": fold_receipts,
        "rows": output_rows,
    }
    Path(args.output).write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: output[key] for key in output if key not in {"rows", "fold_receipts"}}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
