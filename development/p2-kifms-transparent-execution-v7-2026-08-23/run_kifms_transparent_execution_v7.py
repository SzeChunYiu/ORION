#!/usr/bin/env python3
"""Run the outcome-unopened P2 KIFMS V7 transparent public execution.

V7 is a materially different successor to V6: it replaces the unavailable
independent-custody requirement with a hash-frozen, fully disclosed public-data
development execution.  It never claims independent confirmation.  Source
titles, abstracts, and row-level labels remain in memory and are not emitted.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import importlib.util
import json
import math
import platform
import re
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import scipy
import sklearn
from scipy.stats import binomtest
from sklearn.feature_extraction.text import TfidfVectorizer


ARMS = ("R0_L0", "R0_L1", "R1_L0", "R1_L1")
BASE_METRICS = (
    "recall_at_005",
    "recall_at_010",
    "recall_at_020",
    "fraction_screened_at_95_recall",
    "wss_at_95",
)
METRICS = BASE_METRICS + ("cre20",)
LABEL_HEADERS = ["noisy_inclusion", "expert_inclusion", "fulltext_inclusion"]
ALLOWED_LABEL_TOKENS = {
    "0": 0,
    "0.0": 0,
    "false": 0,
    "1": 1,
    "1.0": 1,
    "true": 1,
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def hash_lines(values: list[str]) -> str:
    return hashlib.sha256("\n".join(values).encode("ascii")).hexdigest()


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


def normalize_text(value: Any) -> str:
    return " ".join(str(value or "").split())


def normalize_pmid(value: Any) -> str:
    text = normalize_text(value)
    match = re.search(r"(\d+)(?:/)?$", text)
    return match.group(1) if match else text


def content_identity(title: Any, abstract: Any) -> str:
    text = f"{normalize_text(title)} {normalize_text(abstract)}"
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def parse_label(raw: Any, location: str) -> int:
    token = normalize_text(raw).casefold()
    if token not in ALLOWED_LABEL_TOKENS:
        raise ValueError(f"Unmapped expert_inclusion value at {location}: {token!r}")
    return ALLOWED_LABEL_TOKENS[token]


def verify_frozen_bindings(packet: Path, v6: Path, stage: Path) -> tuple[dict[str, Any], bool]:
    implementation = json.loads((packet / "IMPLEMENTATION_FREEZE_V7.json").read_text())
    rights = json.loads((v6 / "SOURCE_RIGHTS_PROVENANCE_RECEIPT_V6.json").read_text())
    fixed_paths = {
        "protocol_v7": packet / "PROTOCOL_FREEZE_V7.json",
        "runner_v7": Path(__file__).resolve(),
        "pinned_active_core_v3": packet / "pinned_active_core_v3.py",
        "pinned_factorial_core_v4": packet / "pinned_factorial_core_v4.py",
        "v6_protocol": v6 / "PROTOCOL_FREEZE_V6.json",
        "v6_population": v6 / "SOURCE_FAMILY_AND_POPULATION_FREEZE_V6.json",
        "v6_overlap": v6 / "LABEL_BLIND_OVERLAP_RECEIPT_V6.json",
        "v6_rights": v6 / "SOURCE_RIGHTS_PROVENANCE_RECEIPT_V6.json",
    }
    fixed: dict[str, Any] = {}
    passed = True
    for role, path in fixed_paths.items():
        expected = implementation["fixed_sha256"][role]
        actual = sha256_file(path) if path.is_file() else None
        ok = actual == expected
        fixed[role] = {"expected": expected, "actual": actual, "passed": ok}
        passed = passed and ok

    staged: dict[str, Any] = {}
    for source in rights["source"]["csv_files"]:
        path = stage / source["filename"]
        actual_hash = sha256_file(path) if path.is_file() else None
        actual_bytes = path.stat().st_size if path.is_file() else None
        ok = actual_hash == source["sha256"] and actual_bytes == source["bytes"]
        staged[source["filename"]] = {
            "bytes_expected": source["bytes"],
            "bytes_actual": actual_bytes,
            "sha256_expected": source["sha256"],
            "sha256_actual": actual_hash,
            "passed": ok,
        }
        passed = passed and ok
    return {"fixed": fixed, "staged_sources": staged, "passed": passed}, passed


def read_with_labels(stage: Path, overlap: dict[str, Any]) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    reviews: dict[str, list[dict[str, Any]]] = {}
    receipt: dict[str, Any] = {}
    for review in overlap["review_units"]:
        expected = overlap["per_review"][review]
        path = stage / expected["filename"]
        rows: list[dict[str, Any]] = []
        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.reader(handle, delimiter=";")
            header = next(reader)
            if header[:3] != LABEL_HEADERS:
                raise ValueError(f"Unexpected label header boundary in {path}: {header[:3]}")
            positions = {name: header.index(name) for name in ("key", "title", "abstract", "pubmed_id")}
            for row_number, row in enumerate(reader, start=2):
                title = normalize_text(row[positions["title"]])
                abstract = normalize_text(row[positions["abstract"]])
                key = normalize_text(row[positions["key"]]) or f"row-{row_number:09d}"
                rows.append(
                    {
                        "key": key,
                        "row_number": row_number,
                        "content_id": content_identity(title, abstract),
                        "empty_text": not (title or abstract),
                        "pmid": normalize_pmid(row[positions["pubmed_id"]]),
                        "label": parse_label(row[1], f"{path.name}:{row_number}"),
                        "text": f"{title} {abstract}".strip(),
                    }
                )
        if len(rows) != expected["raw_rows"]:
            raise ValueError(f"Raw row mismatch for {review}: {len(rows)}")
        reviews[review] = rows
        receipt[review] = {"raw_rows": len(rows), "header": header}
    return reviews, receipt


def within_review_canonicalize(
    source: dict[str, list[dict[str, Any]]]
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    output: dict[str, list[dict[str, Any]]] = {}
    receipts: dict[str, Any] = {}
    for review, source_rows in source.items():
        seen_content: set[str] = set()
        seen_pmids: set[str] = set()
        retained: list[dict[str, Any]] = []
        empty = duplicate_content = duplicate_pmid = duplicate_label_conflict = 0
        first_label: dict[str, int] = {}
        for row in sorted(source_rows, key=lambda value: (value["key"], value["row_number"])):
            if row["empty_text"]:
                empty += 1
                continue
            if row["content_id"] in seen_content:
                duplicate_content += 1
                if first_label[row["content_id"]] != row["label"]:
                    duplicate_label_conflict += 1
                continue
            if row["pmid"] and row["pmid"] in seen_pmids:
                duplicate_pmid += 1
                continue
            seen_content.add(row["content_id"])
            first_label[row["content_id"]] = row["label"]
            if row["pmid"]:
                seen_pmids.add(row["pmid"])
            retained.append(row)
        output[review] = retained
        receipts[review] = {
            "empty_text_rows": empty,
            "within_review_duplicate_content_excess": duplicate_content,
            "within_review_duplicate_pmid_excess_after_content_dedup": duplicate_pmid,
            "duplicate_content_label_conflicts": duplicate_label_conflict,
            "provisional_unique_rows": len(retained),
        }
    return output, receipts


def final_after_candidate_external_drop(
    provisional: dict[str, list[dict[str, Any]]], drop_review: str, drop_content: str
) -> dict[str, list[dict[str, Any]]]:
    after_external = {
        review: [
            row
            for row in rows
            if not (review == drop_review and row["content_id"] == drop_content)
        ]
        for review, rows in provisional.items()
    }
    content_owners: dict[str, set[str]] = defaultdict(set)
    pmid_owners: dict[str, set[str]] = defaultdict(set)
    for review, rows in after_external.items():
        for row in rows:
            content_owners[row["content_id"]].add(review)
            if row["pmid"]:
                pmid_owners[row["pmid"]].add(review)
    shared_content = {value for value, owners in content_owners.items() if len(owners) > 1}
    shared_pmids = {value for value, owners in pmid_owners.items() if len(owners) > 1}
    return {
        review: [
            row
            for row in rows
            if row["content_id"] not in shared_content
            and (not row["pmid"] or row["pmid"] not in shared_pmids)
        ]
        for review, rows in after_external.items()
    }


def matches_v6_population(final: dict[str, list[dict[str, Any]]], overlap: dict[str, Any]) -> bool:
    for review, rows in final.items():
        expected = overlap["per_review"][review]
        if len(rows) != expected["canonical_rows"]:
            return False
        if hash_lines(sorted(row["content_id"] for row in rows)) != expected["canonical_content_set_sha256"]:
            return False
        if hash_lines(sorted(row["pmid"] for row in rows if row["pmid"])) != expected["canonical_pmid_set_sha256"]:
            return False
    union_content = sorted({row["content_id"] for rows in final.values() for row in rows})
    union_pmids = sorted({row["pmid"] for rows in final.values() for row in rows if row["pmid"]})
    return (
        sum(len(rows) for rows in final.values()) == overlap["total_canonical_rows"]
        and hash_lines(union_content) == overlap["canonical_union_content_set_sha256"]
        and hash_lines(union_pmids) == overlap["canonical_union_pmid_set_sha256"]
    )


def reconstruct_frozen_population(
    provisional: dict[str, list[dict[str, Any]]], overlap: dict[str, Any]
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    # V6 records exactly one raw V5 content match and zero SWIFT/PMID matches.
    # Enumerate the single outcome-blind content deletion and require a unique
    # candidate that reproduces every frozen per-review and union hash.
    candidates: list[tuple[str, str, dict[str, list[dict[str, Any]]]]] = []
    for review, rows in provisional.items():
        for row in rows:
            final = final_after_candidate_external_drop(provisional, review, row["content_id"])
            if matches_v6_population(final, overlap):
                candidates.append((review, row["content_id"], final))
    if len(candidates) != 1:
        raise ValueError(f"Frozen V6 population reconstruction is not unique: {len(candidates)} candidates")
    drop_review, drop_content, final = candidates[0]
    return final, {
        "unique_external_exclusion_reconstructed": True,
        "candidate_count": 1,
        "excluded_review": drop_review,
        "excluded_content_identity_sha256": hashlib.sha256(drop_content.encode("ascii")).hexdigest(),
        "canonical_rows": sum(len(rows) for rows in final.values()),
        "canonical_union_content_set_sha256": hash_lines(
            sorted({row["content_id"] for rows in final.values() for row in rows})
        ),
    }


def cre20(order: list[int], labels: np.ndarray) -> float:
    positives = int(labels.sum())
    if positives <= 0 or positives >= len(labels):
        raise ValueError("CRE20 requires both classes")
    total = 0.0
    n = len(order)
    for i, index in enumerate(order, start=1):
        total += int(labels[index]) * max(0.20 - i / n, 0.0)
    return total / (0.20 * positives)


def component_effects(arms: dict[str, dict[str, float]]) -> dict[str, dict[str, float]]:
    output = {name: {} for name in ("interaction", "learner_balancer_main_effect", "representation_main_effect")}
    for metric in METRICS:
        r0l0, r0l1 = arms["R0_L0"][metric], arms["R0_L1"][metric]
        r1l0, r1l1 = arms["R1_L0"][metric], arms["R1_L1"][metric]
        output["representation_main_effect"][metric] = 0.5 * ((r1l0 - r0l0) + (r1l1 - r0l1))
        output["learner_balancer_main_effect"][metric] = 0.5 * ((r0l1 - r0l0) + (r1l1 - r1l0))
        output["interaction"][metric] = (r1l1 - r0l1) - (r1l0 - r0l0)
    return output


def mean(values: list[float]) -> float:
    return float(np.mean(values))


def execute(packet: Path, v6: Path, stage: Path, out: Path) -> None:
    start = time.monotonic()
    protocol = json.loads((packet / "PROTOCOL_FREEZE_V7.json").read_text())
    overlap = json.loads((v6 / "LABEL_BLIND_OVERLAP_RECEIPT_V6.json").read_text())
    binding, binding_ok = verify_frozen_bindings(packet, v6, stage)
    result: dict[str, Any] = {
        "identity": protocol["identity"],
        "scope": protocol["scope"],
        "execution_started_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "binding_receipt": binding,
        "custody": {
            "mode": "HASH_FROZEN_TRANSPARENT_PUBLIC_DEVELOPMENT_EXECUTION",
            "independent_custody": False,
            "confirmatory_claim_permitted": False,
        },
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "scikit_learn": sklearn.__version__,
        },
        "preserved_terminals": protocol["preserved_terminals"],
        "forbidden_claims": protocol["forbidden_claims"],
    }
    if not binding_ok:
        result["terminal"] = protocol["terminals"]["cannot_check"]
        out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        return

    print("binding_passed; opening exact public KIFMS expert_inclusion labels", flush=True)
    source_rows, source_receipt = read_with_labels(stage, overlap)
    provisional, canonicalization_receipt = within_review_canonicalize(source_rows)
    final, reconstruction_receipt = reconstruct_frozen_population(provisional, overlap)
    result["source_receipt"] = source_receipt
    result["canonicalization_receipt"] = canonicalization_receipt
    result["population_reconstruction_receipt"] = reconstruction_receipt

    active = import_module(packet / "pinned_active_core_v3.py", "p2_kifms_v7_active")
    factorial = import_module(packet / "pinned_factorial_core_v4.py", "p2_kifms_v7_factorial")
    reviews = tuple(overlap["review_units"])
    arms_by_review: dict[str, Any] = {}
    effects_by_review: dict[str, Any] = {}
    full_by_review: dict[str, Any] = {}
    class_counts: dict[str, Any] = {}
    for review in reviews:
        rows = sorted(final[review], key=lambda row: active.record_identity(review, row["content_id"]))
        texts = [row["text"] for row in rows]
        identities = [active.record_identity(review, row["content_id"]) for row in rows]
        labels = np.asarray([row["label"] for row in rows], dtype=np.int8)
        class_counts[review] = {"negative": int((labels == 0).sum()), "positive": int(labels.sum())}
        if class_counts[review]["negative"] == 0 or class_counts[review]["positive"] == 0:
            raise ValueError(f"Both classes required in {review}")
        batch_size = max(10, math.ceil(0.002 * len(rows)))
        seed = active.initial_seed(review, labels, identities)
        seed_hash = hashlib.sha256("\n".join(identities[i] for i in seed).encode("ascii")).hexdigest()
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
            order, fits = factorial.execute_arm(active, arm, matrices[representation], labels, seed, batch_size)
            metrics = active.order_metrics(order, labels)
            metrics["cre20"] = cre20(order, labels)
            review_arms[arm] = {
                "features": int(matrices[representation].shape[1]),
                "metrics": metrics,
                "model_fits": fits,
                "order_sha256": active.order_sha256(order, identities),
            }
        review_arms["adapter_receipt"] = {
            "batch_size": batch_size,
            "initial_seed_record_identities_sha256": seed_hash,
            "text_list_sha256": active.hash_text_list(texts),
        }
        arms_by_review[review] = review_arms
        effects_by_review[review] = component_effects({arm: review_arms[arm]["metrics"] for arm in ARMS})
        full_by_review[review] = {
            metric: review_arms["R0_L0"]["metrics"][metric] - review_arms["R1_L1"]["metrics"][metric]
            for metric in METRICS
        }
        print(f"review_complete review={review}", flush=True)

    mean_arm = {
        arm: {metric: mean([arms_by_review[r][arm]["metrics"][metric] for r in reviews]) for metric in METRICS}
        for arm in ARMS
    }
    mean_effect = {
        effect: {metric: mean([effects_by_review[r][effect][metric] for r in reviews]) for metric in METRICS}
        for effect in ("representation_main_effect", "learner_balancer_main_effect", "interaction")
    }
    mean_full = {metric: mean([full_by_review[r][metric] for r in reviews]) for metric in METRICS}
    learner_r10 = {r: effects_by_review[r]["learner_balancer_main_effect"]["recall_at_010"] for r in reviews}
    learner_cre20 = {r: effects_by_review[r]["learner_balancer_main_effect"]["cre20"] for r in reviews}
    full_r10 = {r: full_by_review[r]["recall_at_010"] for r in reviews}
    performance_gates = {
        "C1_CRE20_MAGNITUDE": mean_effect["learner_balancer_main_effect"]["cre20"] >= 0.010858985820770889,
        "C2_CRE20_SIGN": sum(value > 0 for value in learner_cre20.values()) >= 12,
        "C3_R10_MAGNITUDE": mean_effect["learner_balancer_main_effect"]["recall_at_010"] >= 0.010858985820770889,
        "C4_R10_SIGN": sum(value > 0 for value in learner_r10.values()) >= 12,
        "C5_LEARNER_WORK_SAVING": mean_effect["learner_balancer_main_effect"]["wss_at_95"] >= 0,
        "C6_LEARNER_HARM": min(learner_r10.values()) >= -0.05,
        "G3_FULL_ARM_R10_MARGIN": mean_full["recall_at_010"] >= 0.05,
        "G4_FULL_ARM_WORK_SAVING": mean_full["wss_at_95"] >= 0,
        "G5_FULL_ARM_HARM": min(full_r10.values()) >= -0.05,
        "G6_ABSOLUTE_WORK_SAVING": all(arms_by_review[r]["R0_L0"]["metrics"]["wss_at_95"] > 0 for r in reviews),
    }
    all_performance = all(performance_gates.values())
    terminal = protocol["terminals"]["public_performance_pass"] if all_performance else protocol["terminals"]["public_performance_adverse"]
    result.update(
        {
            "arms_by_review": arms_by_review,
            "effects_by_review": effects_by_review,
            "full_arm_candidate_minus_u4_by_review": full_by_review,
            "unweighted_mean_arm_metrics": mean_arm,
            "unweighted_mean_component_effects": mean_effect,
            "mean_full_arm_candidate_minus_u4": mean_full,
            "class_counts": class_counts,
            "performance_gates": performance_gates,
            "failed_performance_gates": [name for name, value in performance_gates.items() if not value],
            "strictly_positive_review_counts": {
                "learner_cre20": sum(value > 0 for value in learner_cre20.values()),
                "learner_r10": sum(value > 0 for value in learner_r10.values()),
            },
            "two_sided_exact_binomial_sign_p": {
                "learner_cre20": float(binomtest(sum(value > 0 for value in learner_cre20.values()), len(reviews), 0.5).pvalue),
                "learner_r10": float(binomtest(sum(value > 0 for value in learner_r10.values()), len(reviews), 0.5).pvalue),
            },
            "v6_independent_custody_gate": False,
            "confirmatory_terminal_available": False,
            "elapsed_seconds": time.monotonic() - start,
            "execution_completed_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "terminal": terminal,
        }
    )
    result["result_payload_sha256"] = canonical_json_sha256(result)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--v6", type=Path, required=True)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    execute(args.packet.resolve(), args.v6.resolve(), args.stage.resolve(), args.out.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
