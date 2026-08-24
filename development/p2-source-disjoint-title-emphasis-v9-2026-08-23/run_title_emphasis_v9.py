#!/usr/bin/env python3
"""Execute the single frozen P2 V9 title-emphasis diagnostic exactly once."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import importlib.util
import json
import math
import platform
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import scipy
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer


METRICS = (
    "recall_at_005",
    "recall_at_010",
    "recall_at_020",
    "fraction_screened_at_95_recall",
    "wss_at_95",
    "cre20",
)


def import_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def hash_lines(values: list[str]) -> str:
    return hashlib.sha256("\n".join(values).encode("ascii")).hexdigest()


def canonical_json_sha256(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def parse_label(value: Any, location: str) -> int:
    token = " ".join(str(value or "").split()).casefold()
    if token in {"1", "1.0", "true"}:
        return 1
    if token in {"0", "0.0", "false"}:
        return 0
    raise ValueError(f"Nonbinary label at {location}: {token!r}")


def load_population(stage: Path, freeze: dict[str, Any], prep: Any) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any], bool]:
    provisional: dict[str, dict[str, dict[str, Any]]] = {}
    receipt: dict[str, Any] = {}
    for review in prep.REVIEWS:
        path = stage / f"{review}.csv"
        by_content: dict[str, dict[str, Any]] = {}
        conflicts = 0
        raw_rows = 0
        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None or not {"record_id", "title", "abstract", "label_included"}.issubset(reader.fieldnames):
                raise ValueError(f"Unexpected schema in {path}: {reader.fieldnames}")
            for row_number, row in enumerate(reader, start=2):
                raw_rows += 1
                title, abstract = prep.normalize(row["title"]), prep.normalize(row["abstract"])
                if not (title or abstract):
                    continue
                content_id = prep.content_identity(title, abstract)
                record_id = prep.normalize(row["record_id"]) or f"row-{row_number:09d}"
                value = {
                    "record_id": record_id,
                    "title": title,
                    "abstract": abstract,
                    "label": parse_label(row["label_included"], f"{path.name}:{row_number}"),
                }
                if content_id in by_content:
                    if by_content[content_id]["label"] != value["label"]:
                        conflicts += 1
                    if record_id < by_content[content_id]["record_id"]:
                        by_content[content_id] = value
                else:
                    by_content[content_id] = value
        provisional[review] = by_content
        receipt[review] = {"raw_rows": raw_rows, "duplicate_content_label_conflicts": conflicts}

    prior = set()
    # The prior identities themselves are not serialized. Rebuild them using the
    # same preflight and require their aggregate hash to equal the freeze.
    raise_if = "population loader requires injected prior set"
    return provisional, {"internal_marker": raise_if, "per_review": receipt}, False


def execute_complete_order(v8: Any, matrix: Any, labels: np.ndarray, seed: list[int], batch_size: int) -> tuple[list[int], int]:
    selected = list(seed)
    remaining = np.ones(len(labels), dtype=bool)
    remaining[selected] = False
    fits = 0
    while remaining.any():
        model = v8.u4_model()
        v8.fit_u4(model, matrix, labels, selected)
        fits += 1
        pool = np.flatnonzero(remaining)
        scores = np.asarray(model.decision_function(matrix[pool]), dtype=float)
        ranked = pool[np.argsort(-scores, kind="stable")]
        chosen = ranked[:batch_size]
        selected.extend(int(index) for index in chosen)
        remaining[chosen] = False
    return selected, fits


def execute_envelope(v8: Any, base: Any, title: Any, labels: np.ndarray, seed: list[int], batch_size: int) -> tuple[list[int], int]:
    selected = list(seed)
    remaining = np.ones(len(labels), dtype=bool)
    remaining[selected] = False
    fits = 0
    while remaining.any():
        base_model, title_model = v8.u4_model(), v8.u4_model()
        v8.fit_u4(base_model, base, labels, selected)
        v8.fit_u4(title_model, title, labels, selected)
        fits += 2
        pool = np.flatnonzero(remaining)
        base_z = v8.zscore(np.asarray(base_model.decision_function(base[pool]), dtype=float))
        title_z = v8.zscore(np.asarray(title_model.decision_function(title[pool]), dtype=float))
        scores = base_z + 0.25 * (title_z - base_z)
        ranked = pool[np.argsort(-scores, kind="stable")]
        chosen = ranked[:batch_size]
        selected.extend(int(index) for index in chosen)
        remaining[chosen] = False
    return selected, fits


def build_population(
    prep: Any,
    v8: Any,
    stage: Path,
    population_freeze: dict[str, Any],
    swift_root: Path,
    v5_packet: Path,
    v5_stage: Path,
    v6_root: Path,
    v8_root: Path,
    kifms_stage: Path,
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any], bool]:
    v5 = import_module(v5_packet / "run_synergy_label_blind_preflight_v5.py", "p2_v5_preflight_exec")
    swift_content, _ = v5.load_swift_content(swift_root)
    v5_content, _ = prep.load_v5_content(v5_stage, v5)
    kifms_content, _ = prep.load_kifms_content(v8, v6_root, kifms_stage)
    prior_content = swift_content | v5_content | kifms_content
    if hash_lines(sorted(prior_content)) != population_freeze["prior_union_content_set_sha256"]:
        return {}, {"prior_union_hash_passed": False}, False

    provisional: dict[str, dict[str, dict[str, Any]]] = {}
    source_receipt: dict[str, Any] = {}
    for review in prep.REVIEWS:
        path = stage / f"{review}.csv"
        by_content: dict[str, dict[str, Any]] = {}
        conflicts = 0
        raw_rows = 0
        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None or not {"record_id", "title", "abstract", "label_included"}.issubset(reader.fieldnames):
                raise ValueError(f"Unexpected schema in {path}: {reader.fieldnames}")
            for row_number, row in enumerate(reader, start=2):
                raw_rows += 1
                title, abstract = prep.normalize(row["title"]), prep.normalize(row["abstract"])
                if not (title or abstract):
                    continue
                content_id = prep.content_identity(title, abstract)
                record_id = prep.normalize(row["record_id"]) or f"row-{row_number:09d}"
                value = {
                    "record_id": record_id,
                    "title": title,
                    "abstract": abstract,
                    "label": parse_label(row["label_included"], f"{path.name}:{row_number}"),
                }
                if content_id in by_content:
                    if by_content[content_id]["label"] != value["label"]:
                        conflicts += 1
                    if record_id < by_content[content_id]["record_id"]:
                        by_content[content_id] = value
                else:
                    by_content[content_id] = value
        provisional[review] = by_content
        source_receipt[review] = {"raw_rows": raw_rows, "duplicate_content_label_conflicts": conflicts}

    owners: dict[str, set[str]] = defaultdict(set)
    for review, rows in provisional.items():
        for content_id in rows:
            owners[content_id].add(review)
    shared = {content_id for content_id, values in owners.items() if len(values) > 1}

    final: dict[str, list[dict[str, Any]]] = {}
    passed = True
    for review in prep.REVIEWS:
        rows = []
        for content_id, value in provisional[review].items():
            if content_id in prior_content or content_id in shared:
                continue
            identity = prep.record_identity(review, content_id)
            rows.append({
                "record_identity": identity,
                "content_identity": content_id,
                "title": value["title"],
                "abstract": value["abstract"],
                "text": f'{value["title"]} {value["abstract"]}'.strip(),
                "label": value["label"],
            })
        rows.sort(key=lambda row: row["record_identity"])
        labels = np.asarray([row["label"] for row in rows], dtype=np.int8)
        expected = population_freeze["per_review"][review]
        content_hash = hash_lines(sorted(row["content_identity"] for row in rows))
        record_hash = hash_lines([row["record_identity"] for row in rows])
        ok = (
            source_receipt[review]["raw_rows"] == expected["raw_rows"]
            and source_receipt[review]["duplicate_content_label_conflicts"] == 0
            and len(rows) == expected["canonical_rows"]
            and content_hash == expected["canonical_content_set_sha256"]
            and record_hash == expected["canonical_record_order_sha256"]
            and 0 < int(labels.sum()) < len(labels)
        )
        source_receipt[review].update({
            "canonical_rows": len(rows),
            "included_rows": int(labels.sum()),
            "excluded_rows": int(len(labels) - labels.sum()),
            "canonical_content_set_sha256": content_hash,
            "canonical_record_order_sha256": record_hash,
            "passed": ok,
        })
        passed = passed and ok
        final[review] = rows
    union = {row["content_identity"] for rows in final.values() for row in rows}
    passed = passed and len(union & prior_content) == 0 and len(union) == sum(len(rows) for rows in final.values())
    return final, {
        "prior_union_hash_passed": True,
        "per_review": source_receipt,
        "final_prior_union_overlap_count": len(union & prior_content),
        "final_candidate_pairwise_duplicate_excess": sum(len(rows) for rows in final.values()) - len(union),
        "total_canonical_rows": sum(len(rows) for rows in final.values()),
        "passed": passed,
    }, passed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--swift-root", type=Path, required=True)
    parser.add_argument("--v5-packet", type=Path, required=True)
    parser.add_argument("--v5-stage", type=Path, required=True)
    parser.add_argument("--v6-root", type=Path, required=True)
    parser.add_argument("--v8-root", type=Path, required=True)
    parser.add_argument("--kifms-stage", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    start = time.monotonic()
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    protocol = json.loads((args.packet / "PROTOCOL_FREEZE_V9.json").read_text())
    source = json.loads((args.packet / "SOURCE_SELECTION_FREEZE_V9.json").read_text())
    population_freeze = json.loads((args.packet / "POPULATION_FREEZE_V9.json").read_text())
    implementation = json.loads((args.packet / "IMPLEMENTATION_FREEZE_V9.json").read_text())
    prep = import_module(args.packet / "prepare_population_v9.py", "p2_v9_prepare")
    v8 = import_module(args.v8_root / "run_donor_envelopment_v8.py", "p2_v8_exact")
    active = import_module(args.v8_root / "pinned_active_core_v3.py", "p2_v8_active")

    fixed_paths = {
        "protocol_v9": args.packet / "PROTOCOL_FREEZE_V9.json",
        "source_selection_v9": args.packet / "SOURCE_SELECTION_FREEZE_V9.json",
        "population_freeze_v9": args.packet / "POPULATION_FREEZE_V9.json",
        "preflight_runner_v9": args.packet / "prepare_population_v9.py",
        "runner_v9": Path(__file__).resolve(),
        "v8_result": args.v8_root / "RESULT_V8.json",
        "v8_adjudication": args.v8_root / "SCIENTIFIC_ADJUDICATION_V8.json",
        "v8_next_discriminator": args.v8_root / "NEXT_DISCRIMINATOR_V9.json",
        "v8_runner": args.v8_root / "run_donor_envelopment_v8.py",
        "pinned_active_core_v3": args.v8_root / "pinned_active_core_v3.py",
    }
    binding = {role: {"expected": implementation["fixed_sha256"][role], "actual": sha256_file(path)} for role, path in fixed_paths.items()}
    for item in binding.values():
        item["passed"] = item["actual"] == item["expected"]
    source_binding = {}
    for item in source["selected_reviews"]:
        path = args.stage / item["filename"]
        source_binding[item["review"]] = {
            "bytes_expected": item["bytes"],
            "bytes_actual": path.stat().st_size if path.is_file() else None,
            "sha256_expected": item["sha256"],
            "sha256_actual": sha256_file(path) if path.is_file() else None,
        }
        source_binding[item["review"]]["passed"] = (
            source_binding[item["review"]]["bytes_expected"] == source_binding[item["review"]]["bytes_actual"]
            and source_binding[item["review"]]["sha256_expected"] == source_binding[item["review"]]["sha256_actual"]
        )
    binding_ok = all(item["passed"] for item in binding.values()) and all(item["passed"] for item in source_binding.values())
    result: dict[str, Any] = {
        "identity": protocol["identity"],
        "scope": protocol["scope"],
        "execution_started_at_utc": started,
        "binding_receipt": {"fixed": binding, "sources": source_binding, "passed": binding_ok},
        "forbidden_claims": protocol["forbidden_claims"],
        "preserved_parent_terminal": protocol["preserved_parent_terminal"],
        "software": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__, "scikit_learn": sklearn.__version__},
    }
    if not binding_ok:
        result["terminal"] = protocol["terminals"]["cannot_check"]
        args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
        return 2

    rows_by_review, population_receipt, population_ok = build_population(
        prep, v8, args.stage, population_freeze, args.swift_root, args.v5_packet, args.v5_stage,
        args.v6_root, args.v8_root, args.kifms_stage
    )
    result["population_receipt"] = population_receipt
    if not population_ok:
        result["terminal"] = protocol["terminals"]["cannot_check"]
        result["elapsed_seconds"] = time.monotonic() - start
        args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
        return 3

    arms_by_review: dict[str, Any] = {}
    deltas_by_review: dict[str, Any] = {}
    for review in prep.REVIEWS:
        rows = rows_by_review[review]
        labels = np.asarray([row["label"] for row in rows], dtype=np.int8)
        identities = [row["record_identity"] for row in rows]
        texts = [row["text"] for row in rows]
        title_texts = [f'{row["title"]} {row["title"]} {row["abstract"]}'.strip() for row in rows]
        batch_size = max(10, math.ceil(0.002 * len(rows)))
        seed = active.initial_seed(review, labels, identities)
        base = TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_df=0.95, sublinear_tf=True, lowercase=True).fit_transform(texts)
        title = TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_df=0.95, sublinear_tf=True, lowercase=True).fit_transform(title_texts)
        print(f"review_start={review} rows={len(rows)} batch={batch_size}", flush=True)
        base_order, base_fits = execute_complete_order(v8, base, labels, seed, batch_size)
        title_order, title_fits = execute_complete_order(v8, title, labels, seed, batch_size)
        envelope_order, envelope_fits = execute_envelope(v8, base, title, labels, seed, batch_size)
        orders = {"EXACT_U4": (base_order, base_fits, int(base.shape[1])), "TITLE_ONLY_U4": (title_order, title_fits, int(title.shape[1])), "U4_PLUS_TITLE_A250": (envelope_order, envelope_fits, int(base.shape[1]) + int(title.shape[1]))}
        review_arms = {}
        for arm, (order, fits, features) in orders.items():
            review_arms[arm] = {
                "metrics": v8.metrics_for_order(active, order, labels),
                "order_sha256": active.order_sha256(order, identities),
                "model_fits": fits,
                "features": features,
            }
        arms_by_review[review] = review_arms
        deltas_by_review[review] = {
            arm: v8.delta_metrics(review_arms[arm]["metrics"], review_arms["EXACT_U4"]["metrics"])
            for arm in ("TITLE_ONLY_U4", "U4_PLUS_TITLE_A250")
        }
        print(f"review_complete={review}", flush=True)

    controller = "U4_PLUS_TITLE_A250"
    aggregate_delta = {metric: float(np.mean([deltas_by_review[r][controller][metric] for r in prep.REVIEWS])) for metric in METRICS}
    positive_counts = {metric: sum(deltas_by_review[r][controller][metric] > 0 for r in prep.REVIEWS) for metric in ("cre20", "recall_at_010")}
    worst_r10 = min(deltas_by_review[r][controller]["recall_at_010"] for r in prep.REVIEWS)
    absolute_wss = {r: arms_by_review[r][controller]["metrics"]["wss_at_95"] for r in prep.REVIEWS}
    gates = {
        "G1_BINDING": True,
        "G2_SOURCE_CONTENT_AND_POPULATION": True,
        "G3_MEAN_DELTA_CRE20": aggregate_delta["cre20"] >= 0.010858985820770889,
        "G4_MEAN_DELTA_R10": aggregate_delta["recall_at_010"] >= 0.010858985820770889,
        "G5_MEAN_DELTA_WSS95": aggregate_delta["wss_at_95"] >= 0.0,
        "G6_POSITIVE_CRE20_SIGN": positive_counts["cre20"] >= 6,
        "G7_POSITIVE_R10_SIGN": positive_counts["recall_at_010"] >= 6,
        "G8_WORST_REVIEW_R10_HARM": worst_r10 >= -0.05,
        "G9_ABSOLUTE_WORK_SAVING": all(value > 0 for value in absolute_wss.values()),
    }
    admitted = all(gates.values())
    result.update({
        "arms_by_review": arms_by_review,
        "controller_delta_by_review": {r: deltas_by_review[r][controller] for r in prep.REVIEWS},
        "title_only_delta_by_review": {r: deltas_by_review[r]["TITLE_ONLY_U4"] for r in prep.REVIEWS},
        "aggregate_controller_delta_vs_u4": aggregate_delta,
        "strictly_positive_review_counts": positive_counts,
        "worst_review_delta_r10": worst_r10,
        "absolute_controller_wss95_by_review": absolute_wss,
        "gates": gates,
        "failed_gates": [name for name, passed in gates.items() if not passed],
        "residual_admitted": admitted,
        "fallback": "U4_PLUS_TITLE_A250" if admitted else "EXACT_U4",
        "terminal": protocol["terminals"]["positive"] if admitted else protocol["terminals"]["negative"],
        "execution_completed_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "elapsed_seconds": time.monotonic() - start,
    })
    result["result_payload_sha256"] = canonical_json_sha256(result)
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
