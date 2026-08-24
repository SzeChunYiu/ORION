#!/usr/bin/env python3
"""Execute the frozen P2 SYNERGY V5 content-disjoint mechanism transport."""

from __future__ import annotations

import argparse
import csv
import datetime
import hashlib
import importlib.util
import json
import platform
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import openpyxl
import scipy
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer


REVIEWS = ("Walker_2018", "Brouwer_2019", "Hall_2012", "Wassenaar_2017", "Leenaars_2020")
ARMS = ("R0_L0", "R0_L1", "R1_L0", "R1_L1")
METRICS = (
    "recall_at_005",
    "recall_at_010",
    "recall_at_020",
    "fraction_screened_at_95_recall",
    "wss_at_95",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json_sha256(value: Any) -> str:
    body = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


def import_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_binding(
    target_root: Path,
    stage_root: Path,
    swift_root: Path,
    v4_root: Path,
    implementation_path: Path,
) -> tuple[dict[str, Any], bool]:
    implementation = json.loads(implementation_path.read_text(encoding="utf-8"))
    fixed_paths = {
        "selection_freeze": target_root / "SOURCE_FAMILY_SELECTION_FREEZE_V5.json",
        "source_download_binding": target_root / "SOURCE_DOWNLOAD_BINDING_V5.json",
        "preflight_runner": target_root / "run_synergy_label_blind_preflight_v5.py",
        "preflight_result": target_root / "POPULATION_PREFLIGHT_V5.json",
        "population_freeze": target_root / "POPULATION_AND_CONTENT_FREEZE_V5.json",
        "protocol_freeze": target_root / "PROTOCOL_FREEZE_V5.json",
        "runner": Path(__file__).resolve(),
        "v3_result": swift_root / "RESULT_V3.json",
        "v4_result": v4_root / "RESULT_V4.json",
        "v4_runner": v4_root / "run_swift_controller_factorization_v4.py",
    }
    fixed: dict[str, Any] = {}
    passed = True
    for name, path in fixed_paths.items():
        expected = implementation["fixed_sha256"][name]
        actual = sha256_file(path) if path.is_file() else None
        item_passed = actual == expected
        fixed[name] = {
            "bytes": path.stat().st_size if path.is_file() else None,
            "passed": item_passed,
            "sha256_actual": actual,
            "sha256_expected": expected,
        }
        passed = passed and item_passed

    source_binding = json.loads((target_root / "SOURCE_DOWNLOAD_BINDING_V5.json").read_text())
    staged: dict[str, Any] = {}
    for item in source_binding["files"]:
        path = stage_root / item["review"] / item["filename"]
        actual = sha256_file(path) if path.is_file() else None
        actual_bytes = path.stat().st_size if path.is_file() else None
        item_passed = actual == item["sha256"] and actual_bytes == item["bytes"]
        staged[f"{item['review']}/{item['filename']}"] = {
            "bytes_actual": actual_bytes,
            "bytes_expected": item["bytes"],
            "passed": item_passed,
            "sha256_actual": actual,
            "sha256_expected": item["sha256"],
        }
        passed = passed and item_passed
    return {"fixed_files": fixed, "staged_source_files": staged, "passed": passed}, passed


def load_labels(path: Path, preflight: Any) -> tuple[list[str], dict[str, int], dict[str, Any]]:
    ordered_ids: list[str] = []
    labels: dict[str, int] = {}
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != ["openalex_id", "doi", "pmid", "label_included"]:
            raise ValueError(f"Unexpected label schema: {reader.fieldnames}")
        for row_number, row in enumerate(reader, start=2):
            work_id = preflight.normalize_openalex_id(row["openalex_id"])
            raw = preflight.normalize(row["label_included"])
            if raw not in ("0", "1"):
                raise ValueError(f"Nonbinary label at {path}:{row_number}")
            value = int(raw)
            if work_id in labels and labels[work_id] != value:
                raise ValueError(f"Conflicting labels for {work_id}")
            if work_id not in labels:
                ordered_ids.append(work_id)
            labels[work_id] = value
    return ordered_ids, labels, {
        "label_rows": len(ordered_ids),
        "included_rows_before_population_exclusions": sum(labels.values()),
        "excluded_rows_before_population_exclusions": len(labels) - sum(labels.values()),
    }


def build_rows(
    stage_root: Path,
    swift_root: Path,
    population_freeze: dict[str, Any],
    preflight: Any,
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any], bool]:
    swift_content, swift_receipt = preflight.load_swift_content(swift_root)
    provisional: dict[str, dict[str, dict[str, Any]]] = {}
    receipts: dict[str, Any] = {}
    for review in REVIEWS:
        ordered_ids, labels, label_receipt = load_labels(stage_root / review / "labels.csv", preflight)
        works, works_receipt = preflight.load_works(stage_root / review)
        by_content: dict[str, dict[str, Any]] = {}
        duplicate_label_conflicts = 0
        for work_id in ordered_ids:
            work = works.get(work_id)
            if work is None:
                continue
            title, abstract = work["title"], work["abstract"]
            if not title and not abstract:
                continue
            content_id = preflight.content_identity(title, abstract)
            value = {
                "abstract": abstract,
                "label": labels[work_id],
                "openalex_id": work_id,
                "title": title,
            }
            if content_id in by_content:
                if by_content[content_id]["label"] != value["label"]:
                    duplicate_label_conflicts += 1
                if work_id < by_content[content_id]["openalex_id"]:
                    by_content[content_id] = value
            else:
                by_content[content_id] = value
        provisional[review] = by_content
        receipts[review] = {
            **label_receipt,
            "duplicate_content_label_conflicts": duplicate_label_conflicts,
            "work_rows": works_receipt["raw_work_rows"],
        }

    owners: dict[str, set[str]] = defaultdict(set)
    for review, rows in provisional.items():
        for content_id in rows:
            owners[content_id].add(review)
    shared_successor = {content_id for content_id, reviews in owners.items() if len(reviews) > 1}

    final: dict[str, list[dict[str, Any]]] = {}
    passed = True
    for review in REVIEWS:
        rows: list[dict[str, Any]] = []
        for content_id, value in provisional[review].items():
            if content_id in swift_content or content_id in shared_successor:
                continue
            identity = preflight.record_identity(review, content_id)
            rows.append(
                {
                    "content_identity": content_id,
                    "label": value["label"],
                    "openalex_id": value["openalex_id"],
                    "record_identity": identity,
                    "text": f"{value['title']} {value['abstract']}".strip(),
                }
            )
        rows.sort(key=lambda row: row["record_identity"])
        labels = np.asarray([row["label"] for row in rows], dtype=np.int8)
        expected = population_freeze["per_review"][review]
        content_hash = preflight.hash_lines(sorted(row["content_identity"] for row in rows))
        openalex_hash = preflight.hash_lines(sorted(row["openalex_id"] for row in rows))
        record_hash = preflight.hash_lines([row["record_identity"] for row in rows])
        review_passed = (
            len(rows) == expected["canonical_rows"]
            and content_hash == expected["canonical_content_set_sha256"]
            and openalex_hash == expected["canonical_openalex_id_set_sha256"]
            and record_hash == expected["canonical_record_order_sha256"]
            and 0 < int(labels.sum()) < len(labels)
        )
        receipts[review].update(
            {
                "canonical_rows": len(rows),
                "included_rows": int(labels.sum()),
                "excluded_rows": int(len(labels) - labels.sum()),
                "canonical_content_set_sha256": content_hash,
                "canonical_openalex_id_set_sha256": openalex_hash,
                "canonical_record_order_sha256": record_hash,
                "population_passed": review_passed,
            }
        )
        passed = passed and review_passed
        final[review] = rows
    union = set().union(*({row["content_identity"] for row in rows} for rows in final.values()))
    passed = (
        passed
        and sum(len(rows) for rows in final.values()) == population_freeze["total_canonical_rows"]
        and len(union & swift_content) == 0
        and len(union) == sum(len(rows) for rows in final.values())
    )
    receipt = {
        "reviews": receipts,
        "swift_receipt": swift_receipt,
        "final_swift_overlap_count": len(union & swift_content),
        "final_pairwise_duplicate_excess": sum(len(rows) for rows in final.values()) - len(union),
        "total_canonical_rows": sum(len(rows) for rows in final.values()),
        "passed": passed,
    }
    return final, receipt, passed


def mean(values: list[float]) -> float:
    return float(np.mean(values))


def execute(
    target_root: Path,
    stage_root: Path,
    swift_root: Path,
    v4_root: Path,
    implementation_path: Path,
    out_path: Path,
) -> None:
    start = time.monotonic()
    started_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    protocol = json.loads((target_root / "PROTOCOL_FREEZE_V5.json").read_text())
    population_freeze = json.loads((target_root / "POPULATION_AND_CONTENT_FREEZE_V5.json").read_text())
    implementation = json.loads(implementation_path.read_text())
    binding, binding_ok = verify_binding(
        target_root, stage_root, swift_root, v4_root, implementation_path
    )
    result: dict[str, Any] = {
        "binding_receipt": binding,
        "claim_scope": protocol["scope"],
        "execution_started_at_utc": started_at,
        "forbidden_claims": protocol["forbidden_claims"],
        "identity": protocol["identity"],
        "implementation_freeze_sha256": sha256_file(implementation_path),
        "nonpromotion_rule": protocol["nonpromotion_rule"],
        "preserved_adverse_terminals": protocol["preserved_adverse_terminals"],
        "protocol_freeze_sha256": sha256_file(target_root / "PROTOCOL_FREEZE_V5.json"),
        "software": {
            "numpy": np.__version__,
            "openpyxl": openpyxl.__version__,
            "python": platform.python_version(),
            "scikit_learn": sklearn.__version__,
            "scipy": scipy.__version__,
        },
    }
    cannot_check = protocol["terminals"]["cannot_check"]
    if not binding_ok:
        result.update({"terminal": cannot_check})
        out_path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
        return

    preflight = import_module(
        target_root / "run_synergy_label_blind_preflight_v5.py", "p2_synergy_v5_preflight"
    )
    v3 = import_module(
        swift_root / "run_swift_cross_review_controller_transport_v3.py", "p2_swift_v3_active"
    )
    v4 = import_module(
        v4_root / "run_swift_controller_factorization_v4.py", "p2_swift_v4_factor"
    )
    print("binding_passed; opening frozen labels and rebuilding population", flush=True)
    review_rows, population_receipt, population_ok = build_rows(
        stage_root, swift_root, population_freeze, preflight
    )
    result["population_receipt"] = population_receipt
    if not population_ok:
        result.update({"terminal": cannot_check})
        out_path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
        return

    arms_by_review: dict[str, Any] = {}
    effects_by_review: dict[str, Any] = {}
    full_arm_effects_by_review: dict[str, Any] = {}
    for review in REVIEWS:
        rows = review_rows[review]
        texts = [row["text"] for row in rows]
        identities = [row["record_identity"] for row in rows]
        labels = np.asarray([row["label"] for row in rows], dtype=np.int8)
        batch_size = max(10, int(np.ceil(0.002 * len(rows))))
        seed = v3.initial_seed(review, labels, identities)
        seed_hash = hashlib.sha256(
            "\n".join(identities[index] for index in seed).encode("ascii")
        ).hexdigest()
        print(f"vectorize review={review} rows={len(rows)} batch={batch_size}", flush=True)
        r0 = TfidfVectorizer(
            ngram_range=(1, 2), min_df=2, max_features=50000, sublinear_tf=True, lowercase=True
        ).fit_transform(texts)
        r1 = TfidfVectorizer(
            ngram_range=(1, 2), min_df=1, max_df=0.95, sublinear_tf=True, lowercase=True
        ).fit_transform(texts)
        matrices = {"R0": r0, "R1": r1}
        review_arms: dict[str, Any] = {}
        for arm in ARMS:
            print(f"arm_execute review={review} arm={arm}", flush=True)
            representation = arm.split("_")[0]
            order, fits = v4.execute_arm(
                v3, arm, matrices[representation], labels, seed, batch_size
            )
            review_arms[arm] = {
                "features": int(matrices[representation].shape[1]),
                "metrics": v3.order_metrics(order, labels),
                "model_fits": fits,
                "order_sha256": v3.order_sha256(order, identities),
            }
        review_arms["adapter_receipt"] = {
            "batch_size": batch_size,
            "initial_seed_record_identities_sha256": seed_hash,
            "text_list_sha256": v3.hash_text_list(texts),
        }
        arms_by_review[review] = review_arms
        effects_by_review[review] = v4.component_effects(
            {arm: review_arms[arm]["metrics"] for arm in ARMS}
        )
        full_arm_effects_by_review[review] = {
            metric: review_arms["R0_L0"]["metrics"][metric]
            - review_arms["R1_L1"]["metrics"][metric]
            for metric in METRICS
        }
        del matrices, r0, r1
        print(f"review_complete review={review}", flush=True)

    mean_arm_metrics = {
        arm: {
            metric: mean([arms_by_review[review][arm]["metrics"][metric] for review in REVIEWS])
            for metric in METRICS
        }
        for arm in ARMS
    }
    mean_effects = {
        effect: {
            metric: mean([effects_by_review[review][effect][metric] for review in REVIEWS])
            for metric in METRICS
        }
        for effect in ("representation_main_effect", "learner_balancer_main_effect", "interaction")
    }
    mean_full_arm = {
        metric: mean([full_arm_effects_by_review[review][metric] for review in REVIEWS])
        for metric in METRICS
    }
    learner_by_review = {
        review: effects_by_review[review]["learner_balancer_main_effect"]["recall_at_010"]
        for review in REVIEWS
    }
    worst_learner_review = min(REVIEWS, key=lambda review: learner_by_review[review])
    full_by_review = {
        review: full_arm_effects_by_review[review]["recall_at_010"] for review in REVIEWS
    }
    worst_full_review = min(REVIEWS, key=lambda review: full_by_review[review])
    mechanism_gates = {
        "M1_BINDING": True,
        "M2_CONTENT_DISJOINT_POPULATION": True,
        "M3_LEARNER_RECALL10_MAGNITUDE": mean_effects["learner_balancer_main_effect"]["recall_at_010"]
        >= 0.010858985820770889,
        "M4_LEARNER_RECALL10_SIGN": sum(value > 0 for value in learner_by_review.values()) >= 4,
        "M5_LEARNER_WORK_SAVING": mean_effects["learner_balancer_main_effect"]["wss_at_95"]
        >= 0.0,
        "M6_LEARNER_HARM": learner_by_review[worst_learner_review] >= -0.05,
    }
    candidate_wss = {
        review: arms_by_review[review]["R0_L0"]["metrics"]["wss_at_95"] for review in REVIEWS
    }
    preserved_v3_gates = {
        "G1_BINDING": True,
        "G2_POPULATION": True,
        "G3_PRIMARY_MARGIN": mean_full_arm["recall_at_010"] >= 0.05,
        "G4_WORK_SAVING": mean_full_arm["wss_at_95"] >= 0.0,
        "G5_HARM": full_by_review[worst_full_review] >= -0.05,
        "G6_ABSOLUTE_WORK_SAVING": all(value > 0 for value in candidate_wss.values()),
    }
    terminal = (
        protocol["terminals"]["mechanism_positive"]
        if all(mechanism_gates.values())
        else protocol["terminals"]["mechanism_negative"]
    )
    result.update(
        {
            "arms_by_review": arms_by_review,
            "effects_by_review": effects_by_review,
            "elapsed_seconds": time.monotonic() - start,
            "execution_completed_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "failed_mechanism_gates": [name for name, value in mechanism_gates.items() if not value],
            "failed_preserved_v3_gates": [name for name, value in preserved_v3_gates.items() if not value],
            "full_arm_candidate_minus_u4_by_review": full_arm_effects_by_review,
            "mechanism_gates": mechanism_gates,
            "mean_full_arm_candidate_minus_u4": mean_full_arm,
            "preserved_v3_gates": preserved_v3_gates,
            "terminal": terminal,
            "total_canonical_rows": population_receipt["total_canonical_rows"],
            "unweighted_mean_arm_metrics": mean_arm_metrics,
            "unweighted_mean_component_effects": mean_effects,
            "worst_full_arm_review_at_recall_010": {
                "effect": full_by_review[worst_full_review],
                "review": worst_full_review,
            },
            "worst_learner_review_at_recall_010": {
                "effect": learner_by_review[worst_learner_review],
                "review": worst_learner_review,
            },
        }
    )
    result["result_payload_sha256"] = canonical_json_sha256(result)
    out_path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-root", type=Path, required=True)
    parser.add_argument("--stage-root", type=Path, required=True)
    parser.add_argument("--swift-root", type=Path, required=True)
    parser.add_argument("--v4-root", type=Path, required=True)
    parser.add_argument("--implementation", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    execute(
        args.target_root.resolve(),
        args.stage_root.resolve(),
        args.swift_root.resolve(),
        args.v4_root.resolve(),
        args.implementation.resolve(),
        args.out.resolve(),
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
