#!/usr/bin/env python3
"""Execute the one-shot V10 provider-native conflict-resolved diagnostic."""

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
    "recall_at_005", "recall_at_010", "recall_at_020",
    "fraction_screened_at_95_recall", "wss_at_95", "cre20",
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


def build_population(
    prep: Any, v9prep: Any, v8: Any, stage: Path, freeze: dict[str, Any],
    swift_root: Path, v5_packet: Path, v5_stage: Path, v6_root: Path,
    kifms_stage: Path,
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any], bool]:
    v5 = import_module(v5_packet / "run_synergy_label_blind_preflight_v5.py", "p2_v5_exec_v10")
    swift_content, _ = v5.load_swift_content(swift_root)
    v5_content, _ = v9prep.load_v5_content(v5_stage, v5)
    kifms_content, _ = v9prep.load_kifms_content(v8, v6_root, kifms_stage)
    prior_content = swift_content | v5_content | kifms_content
    if hash_lines(sorted(prior_content)) != freeze["prior_union_content_set_sha256"]:
        return {}, {"prior_union_hash_passed": False}, False

    groups_by_review: dict[str, dict[str, list[dict[str, Any]]]] = {}
    source_receipts: dict[str, Any] = {}
    for review in v9prep.REVIEWS:
        groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        raw_rows = 0
        path = stage / f"{review}.csv"
        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            required = {"record_id", "title", "abstract", "label_included"}
            if reader.fieldnames is None or not required.issubset(reader.fieldnames):
                raise ValueError(f"Unexpected schema in {path}: {reader.fieldnames}")
            for row_number, row in enumerate(reader, start=2):
                raw_rows += 1
                title, abstract = v9prep.normalize(row["title"]), v9prep.normalize(row["abstract"])
                if not (title or abstract):
                    continue
                content_id = v9prep.content_identity(title, abstract)
                groups[content_id].append({
                    "record_id": v9prep.normalize(row["record_id"]) or f"row-{row_number:09d}",
                    "duplicate_record_id": v9prep.normalize(row.get("duplicate_record_id")),
                    "title": title,
                    "abstract": abstract,
                    "label": parse_label(row["label_included"], f"{path.name}:{row_number}"),
                })
        groups_by_review[review] = dict(groups)
        source_receipts[review] = {"raw_rows": raw_rows}

    owners: dict[str, set[str]] = defaultdict(set)
    for review, groups in groups_by_review.items():
        for content_id in groups:
            owners[content_id].add(review)
    cross_review_shared = {content_id for content_id, reviews in owners.items() if len(reviews) > 1}

    final: dict[str, list[dict[str, Any]]] = {}
    passed = True
    for review in v9prep.REVIEWS:
        rows: list[dict[str, Any]] = []
        nonnative_conflicts = 0
        native_split_bound = False
        for content_id, values in groups_by_review[review].items():
            if content_id in prior_content or content_id in cross_review_shared:
                continue
            labels = {row["label"] for row in values}
            if review == prep.CONFLICT_REVIEW and content_id == prep.CONFLICT_CONTENT:
                chosen = sorted(values, key=lambda row: row["record_id"])
                native_split_bound = (
                    tuple(row["record_id"] for row in chosen) == prep.CONFLICT_RECORD_IDS
                    and all(not row["duplicate_record_id"] for row in chosen)
                )
                for row in chosen:
                    rows.append({
                        "record_identity": prep.native_record_identity(review, content_id, row["record_id"]),
                        "content_identity": content_id,
                        "title": row["title"], "abstract": row["abstract"],
                        "text": f'{row["title"]} {row["abstract"]}'.strip(), "label": row["label"],
                    })
            else:
                if len(labels) > 1:
                    nonnative_conflicts += 1
                row = min(values, key=lambda value: value["record_id"])
                rows.append({
                    "record_identity": prep.native_record_identity(review, content_id),
                    "content_identity": content_id,
                    "title": row["title"], "abstract": row["abstract"],
                    "text": f'{row["title"]} {row["abstract"]}'.strip(), "label": row["label"],
                })
        rows.sort(key=lambda row: row["record_identity"])
        labels = np.asarray([row["label"] for row in rows], dtype=np.int8)
        expected = freeze["per_review"][review]
        content_multiset_hash = hash_lines(sorted(row["content_identity"] for row in rows))
        record_hash = hash_lines([row["record_identity"] for row in rows])
        ok = (
            source_receipts[review]["raw_rows"] == expected["raw_rows"]
            and nonnative_conflicts == 0 and len(rows) == expected["canonical_rows"]
            and content_multiset_hash == expected["canonical_content_multiset_sha256"]
            and record_hash == expected["canonical_record_order_sha256"]
            and 0 < int(labels.sum()) < len(labels)
            and (review != prep.CONFLICT_REVIEW or native_split_bound)
        )
        source_receipts[review].update({
            "canonical_rows": len(rows), "included_rows": int(labels.sum()),
            "excluded_rows": int(len(labels) - labels.sum()),
            "nonnative_duplicate_label_conflicts": nonnative_conflicts,
            "provider_native_split_bound": native_split_bound,
            "canonical_content_multiset_sha256": content_multiset_hash,
            "canonical_record_order_sha256": record_hash, "passed": ok,
        })
        passed = passed and ok
        final[review] = rows
    return final, {
        "prior_union_hash_passed": True, "per_review": source_receipts,
        "total_canonical_rows": sum(len(rows) for rows in final.values()), "passed": passed,
    }, passed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--v9-packet", type=Path, required=True)
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
    protocol = json.loads((args.packet / "PROTOCOL_FREEZE_V10.json").read_text())
    source = json.loads((args.v9_packet / "SOURCE_SELECTION_FREEZE_V9.json").read_text())
    population_freeze = json.loads((args.packet / "POPULATION_FREEZE_V10.json").read_text())
    implementation = json.loads((args.packet / "IMPLEMENTATION_FREEZE_V10.json").read_text())
    prep = import_module(args.packet / "prepare_population_v10.py", "p2_v10_prepare")
    v9prep = import_module(args.v9_packet / "prepare_population_v9.py", "p2_v9_prepare_exec_v10")
    v9run = import_module(args.v9_packet / "run_title_emphasis_v9.py", "p2_v9_order_core_v10")
    v8 = import_module(args.v8_root / "run_donor_envelopment_v8.py", "p2_v8_exact_v10")
    active = import_module(args.v8_root / "pinned_active_core_v3.py", "p2_v8_active_v10")

    fixed_paths = {
        "protocol_v10": args.packet / "PROTOCOL_FREEZE_V10.json",
        "source_native_audit_v10": args.packet / "SOURCE_NATIVE_CONFLICT_AUDIT_V10.json",
        "population_freeze_v10": args.packet / "POPULATION_FREEZE_V10.json",
        "preflight_runner_v10": args.packet / "prepare_population_v10.py",
        "runner_v10": Path(__file__).resolve(),
        "v9_result": args.v9_packet / "RESULT_V9.json",
        "v9_scientific_receipt": args.v9_packet / "SCIENTIFIC_RECEIPT_V9.json",
        "v9_source_selection": args.v9_packet / "SOURCE_SELECTION_FREEZE_V9.json",
        "v9_preflight_runner": args.v9_packet / "prepare_population_v9.py",
        "v9_order_core": args.v9_packet / "run_title_emphasis_v9.py",
        "v8_result": args.v8_root / "RESULT_V8.json",
        "v8_adjudication": args.v8_root / "SCIENTIFIC_ADJUDICATION_V8.json",
        "v8_next_discriminator": args.v8_root / "NEXT_DISCRIMINATOR_V9.json",
        "v8_runner": args.v8_root / "run_donor_envelopment_v8.py",
        "pinned_active_core_v3": args.v8_root / "pinned_active_core_v3.py",
    }
    binding = {role: {"expected": implementation["fixed_sha256"][role], "actual": sha256_file(path)} for role, path in fixed_paths.items()}
    for item in binding.values(): item["passed"] = item["actual"] == item["expected"]
    source_binding = {}
    for item in source["selected_reviews"]:
        path = args.stage / item["filename"]
        source_binding[item["review"]] = {
            "bytes_expected": item["bytes"], "bytes_actual": path.stat().st_size if path.is_file() else None,
            "sha256_expected": item["sha256"], "sha256_actual": sha256_file(path) if path.is_file() else None,
        }
        source_binding[item["review"]]["passed"] = source_binding[item["review"]]["bytes_expected"] == source_binding[item["review"]]["bytes_actual"] and source_binding[item["review"]]["sha256_expected"] == source_binding[item["review"]]["sha256_actual"]
    binding_ok = all(item["passed"] for item in binding.values()) and all(item["passed"] for item in source_binding.values())
    result: dict[str, Any] = {
        "identity": protocol["identity"], "scope": protocol["scope"],
        "execution_started_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "binding_receipt": {"fixed": binding, "sources": source_binding, "passed": binding_ok},
        "forbidden_claims": protocol["forbidden_claims"],
        "preserved_terminals": protocol["preserved_terminals"],
        "software": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__, "scikit_learn": sklearn.__version__},
    }
    if not binding_ok:
        result["terminal"] = protocol["terminals"]["cannot_check"]
        result["elapsed_seconds"] = time.monotonic() - start
        args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
        return 2

    rows_by_review, population_receipt, population_ok = build_population(
        prep, v9prep, v8, args.stage, population_freeze, args.swift_root,
        args.v5_packet, args.v5_stage, args.v6_root, args.kifms_stage,
    )
    result["population_receipt"] = population_receipt
    if not population_ok:
        result["terminal"] = protocol["terminals"]["cannot_check"]
        result["elapsed_seconds"] = time.monotonic() - start
        args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
        return 3

    arms_by_review: dict[str, Any] = {}
    controller_deltas: dict[str, Any] = {}
    title_deltas: dict[str, Any] = {}
    for review in v9prep.REVIEWS:
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
        base_order, base_fits = v9run.execute_complete_order(v8, base, labels, seed, batch_size)
        title_order, title_fits = v9run.execute_complete_order(v8, title, labels, seed, batch_size)
        envelope_order, envelope_fits = v9run.execute_envelope(v8, base, title, labels, seed, batch_size)
        orders = {"EXACT_U4": (base_order, base_fits, int(base.shape[1])), "TITLE_ONLY_U4": (title_order, title_fits, int(title.shape[1])), "U4_PLUS_TITLE_A250": (envelope_order, envelope_fits, int(base.shape[1]) + int(title.shape[1]))}
        review_arms = {}
        for arm, (order, fits, features) in orders.items():
            review_arms[arm] = {"metrics": v8.metrics_for_order(active, order, labels), "order_sha256": active.order_sha256(order, identities), "model_fits": fits, "features": features}
        arms_by_review[review] = review_arms
        controller_deltas[review] = v8.delta_metrics(review_arms["U4_PLUS_TITLE_A250"]["metrics"], review_arms["EXACT_U4"]["metrics"])
        title_deltas[review] = v8.delta_metrics(review_arms["TITLE_ONLY_U4"]["metrics"], review_arms["EXACT_U4"]["metrics"])
        print(f"review_complete={review}", flush=True)

    reviews = v9prep.REVIEWS
    aggregate = {metric: float(np.mean([controller_deltas[r][metric] for r in reviews])) for metric in METRICS}
    positive = {"cre20": sum(controller_deltas[r]["cre20"] > 0 for r in reviews), "recall_at_010": sum(controller_deltas[r]["recall_at_010"] > 0 for r in reviews)}
    worst_r10 = min(controller_deltas[r]["recall_at_010"] for r in reviews)
    absolute_wss = {r: arms_by_review[r]["U4_PLUS_TITLE_A250"]["metrics"]["wss_at_95"] for r in reviews}
    gates = {
        "G1_BINDING": True, "G2_SOURCE_CONTENT_AND_POPULATION": True,
        "G3_MEAN_DELTA_CRE20": aggregate["cre20"] >= 0.010858985820770889,
        "G4_MEAN_DELTA_R10": aggregate["recall_at_010"] >= 0.010858985820770889,
        "G5_MEAN_DELTA_WSS95": aggregate["wss_at_95"] >= 0.0,
        "G6_POSITIVE_CRE20_SIGN": positive["cre20"] >= 6,
        "G7_POSITIVE_R10_SIGN": positive["recall_at_010"] >= 6,
        "G8_WORST_REVIEW_R10_HARM": worst_r10 >= -0.05,
        "G9_ABSOLUTE_WORK_SAVING": all(value > 0 for value in absolute_wss.values()),
    }
    admitted = all(gates.values())
    result.update({
        "arms_by_review": arms_by_review, "controller_delta_by_review": controller_deltas,
        "title_only_delta_by_review": title_deltas, "aggregate_controller_delta_vs_u4": aggregate,
        "strictly_positive_review_counts": positive, "worst_review_delta_r10": worst_r10,
        "absolute_controller_wss95_by_review": absolute_wss, "gates": gates,
        "failed_gates": [name for name, value in gates.items() if not value],
        "residual_admitted": admitted, "fallback": "U4_PLUS_TITLE_A250" if admitted else "EXACT_U4",
        "terminal": protocol["terminals"]["positive"] if admitted else protocol["terminals"]["negative"],
        "execution_completed_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "elapsed_seconds": time.monotonic() - start,
    })
    result["result_payload_sha256"] = canonical_json_sha256(result)
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
