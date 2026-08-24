#!/usr/bin/env python3
"""Freeze a label-blind, content-disjoint seven-review V9 population."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


REVIEWS = (
    "Kitchenham_2010",
    "Bannach-Brown_2019",
    "Nagtegaal_2019",
    "Kwok_2020",
    "Appenzeller-Herzog_2020",
    "Wolters_2018",
    "Bos_2018",
)
V5_REVIEWS = ("Walker_2018", "Brouwer_2019", "Hall_2012", "Wassenaar_2017", "Leenaars_2020")


def import_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalize(value: Any) -> str:
    return " ".join(str(value or "").split())


def content_identity(title: Any, abstract: Any) -> str:
    return hashlib.sha256(f"{normalize(title)} {normalize(abstract)}".encode("utf-8")).hexdigest()


def record_identity(review: str, content_id: str) -> str:
    return hashlib.sha256(f"{review}\0{content_id}".encode("ascii")).hexdigest()


def hash_lines(values: list[str]) -> str:
    return hashlib.sha256("\n".join(values).encode("ascii")).hexdigest()


def load_v5_content(v5_stage: Path, v5_preflight: Any) -> tuple[set[str], dict[str, Any]]:
    union: set[str] = set()
    per_review: dict[str, Any] = {}
    for review in V5_REVIEWS:
        label_ids, label_receipt = v5_preflight.load_label_ids(v5_stage / review / "labels.csv")
        works, works_receipt = v5_preflight.load_works(v5_stage / review)
        content: set[str] = set()
        missing = empty = 0
        for work_id in label_ids:
            work = works.get(work_id)
            if work is None:
                missing += 1
                continue
            if not (work["title"] or work["abstract"]):
                empty += 1
                continue
            content.add(content_identity(work["title"], work["abstract"]))
        union.update(content)
        per_review[review] = {
            "source_content_identities": len(content),
            "missing_labeled_work_identifier_rows": missing,
            "empty_text_rows": empty,
            "label_values_accessed": label_receipt["label_values_accessed"],
            "raw_work_rows": works_receipt["raw_work_rows"],
        }
    return union, {
        "review_count": len(V5_REVIEWS),
        "union_content_identities": len(union),
        "union_content_set_sha256": hash_lines(sorted(union)),
        "per_review": per_review,
    }


def load_kifms_content(v8: Any, v6_root: Path, kifms_stage: Path) -> tuple[set[str], dict[str, Any]]:
    overlap = json.loads((v6_root / "LABEL_BLIND_OVERLAP_RECEIPT_V6.json").read_text())
    source, _ = v8.read_with_labels(kifms_stage, overlap)
    provisional, canonical_receipt = v8.within_review_canonicalize(source)
    final, reconstruction = v8.reconstruct_frozen_population(provisional, overlap)
    union = {row["content_id"] for rows in final.values() for row in rows}
    return union, {
        "review_count": len(final),
        "canonical_rows": sum(len(rows) for rows in final.values()),
        "union_content_identities": len(union),
        "union_content_set_sha256": hash_lines(sorted(union)),
        "reconstruction": reconstruction,
        "prior_outcomes_already_open": True,
        "canonicalization_receipt": canonical_receipt,
    }


def load_candidate_label_blind(stage: Path) -> tuple[dict[str, dict[str, dict[str, str]]], dict[str, Any]]:
    output: dict[str, dict[str, dict[str, str]]] = {}
    receipt: dict[str, Any] = {}
    for review in REVIEWS:
        path = stage / f"{review}.csv"
        by_content: dict[str, dict[str, str]] = {}
        raw_rows = empty = duplicate_content = 0
        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            expected = {"record_id", "title", "abstract", "label_included"}
            if reader.fieldnames is None or not expected.issubset(reader.fieldnames):
                raise ValueError(f"Unexpected schema in {path}: {reader.fieldnames}")
            header = list(reader.fieldnames)
            for row_number, row in enumerate(reader, start=2):
                raw_rows += 1
                title, abstract = normalize(row["title"]), normalize(row["abstract"])
                if not (title or abstract):
                    empty += 1
                    continue
                content_id = content_identity(title, abstract)
                record_id = normalize(row["record_id"]) or f"row-{row_number:09d}"
                value = {"record_id": record_id, "title": title, "abstract": abstract}
                if content_id in by_content:
                    duplicate_content += 1
                    if record_id < by_content[content_id]["record_id"]:
                        by_content[content_id] = value
                else:
                    by_content[content_id] = value
        output[review] = by_content
        receipt[review] = {
            "raw_rows": raw_rows,
            "header_sha256": hashlib.sha256("\0".join(header).encode("utf-8")).hexdigest(),
            "empty_text_rows": empty,
            "within_review_duplicate_content_excess": duplicate_content,
            "provisional_unique_content": len(by_content),
            "successor_label_values_accessed": False,
        }
    return output, receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--swift-root", type=Path, required=True)
    parser.add_argument("--v5-packet", type=Path, required=True)
    parser.add_argument("--v5-stage", type=Path, required=True)
    parser.add_argument("--v6-root", type=Path, required=True)
    parser.add_argument("--v8-root", type=Path, required=True)
    parser.add_argument("--kifms-stage", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    v5 = import_module(args.v5_packet / "run_synergy_label_blind_preflight_v5.py", "p2_v5_preflight")
    v8 = import_module(args.v8_root / "run_donor_envelopment_v8.py", "p2_v8_runner")
    swift_content, swift_receipt = v5.load_swift_content(args.swift_root)
    v5_content, v5_receipt = load_v5_content(args.v5_stage, v5)
    kifms_content, kifms_receipt = load_kifms_content(v8, args.v6_root, args.kifms_stage)
    prior_content = swift_content | v5_content | kifms_content
    provisional, candidate_receipt = load_candidate_label_blind(args.stage)

    owners: dict[str, set[str]] = defaultdict(set)
    for review, rows in provisional.items():
        for content_id in rows:
            owners[content_id].add(review)
    shared_candidate = {content_id for content_id, values in owners.items() if len(values) > 1}

    per_review: dict[str, Any] = {}
    final_union: set[str] = set()
    for review in REVIEWS:
        before = provisional[review]
        overlap_by_prior = {
            "swift": len(set(before) & swift_content),
            "synergy_v5": len(set(before) & v5_content),
            "kifms_v7": len(set(before) & kifms_content),
        }
        retained = set(before) - prior_content - shared_candidate
        record_ids = sorted(record_identity(review, value) for value in retained)
        final_union.update(retained)
        per_review[review] = {
            **candidate_receipt[review],
            "excluded_prior_union_content": len(set(before) & prior_content),
            "excluded_candidate_pairwise_content": len(set(before) & shared_candidate),
            "prior_overlap_by_family_not_mutually_exclusive": overlap_by_prior,
            "canonical_rows": len(retained),
            "canonical_content_set_sha256": hash_lines(sorted(retained)),
            "canonical_record_order_sha256": hash_lines(record_ids),
        }

    result = {
        "identity": "P2_V9_SOURCE_DISJOINT_TITLE_EMPHASIS_LABEL_BLIND_POPULATION_FREEZE",
        "status": "FROZEN_BEFORE_SUCCESSOR_LABEL_VALUE_OR_COMPARATIVE_OUTCOME_ACCESS_IN_THIS_LANE",
        "review_units": list(REVIEWS),
        "outcome_boundary": {
            "successor_label_values_accessed": False,
            "public_historical_outcomes_may_exist": True,
            "independent_or_protected_custody": False,
        },
        "prior_content_receipts": {
            "swift": swift_receipt,
            "synergy_v5": v5_receipt,
            "kifms_v7": kifms_receipt,
        },
        "prior_union_content_identities": len(prior_content),
        "prior_union_content_set_sha256": hash_lines(sorted(prior_content)),
        "candidate_pairwise_shared_content_identities": len(shared_candidate),
        "per_review": per_review,
        "total_canonical_rows": sum(item["canonical_rows"] for item in per_review.values()),
        "canonical_union_content_identities": len(final_union),
        "canonical_union_content_set_sha256": hash_lines(sorted(final_union)),
        "final_prior_union_overlap_count": len(final_union & prior_content),
        "final_candidate_pairwise_duplicate_excess": sum(item["canonical_rows"] for item in per_review.values()) - len(final_union),
    }
    result["passed"] = (
        result["final_prior_union_overlap_count"] == 0
        and result["final_candidate_pairwise_duplicate_excess"] == 0
        and all(item["canonical_rows"] > 0 for item in per_review.values())
    )
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
