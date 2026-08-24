#!/usr/bin/env python3
"""Freeze V10 with the one provider-native, nonduplicate conflict group split."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


CONFLICT_REVIEW = "Appenzeller-Herzog_2020"
CONFLICT_CONTENT = "d1b054eda2f1fb8dea2e3ad78c9d32aba9819f9d2465b6509949ec11f4117bd4"
CONFLICT_RECORD_IDS = ("1003", "1018")


def import_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def hash_lines(values: list[str]) -> str:
    return hashlib.sha256("\n".join(values).encode("ascii")).hexdigest()


def native_record_identity(review: str, content_id: str, record_id: str | None = None) -> str:
    body = f"{review}\0{content_id}" if record_id is None else f"{review}\0{content_id}\0{record_id}"
    return hashlib.sha256(body.encode("ascii")).hexdigest()


def load_candidate_label_blind(stage: Path, v9: Any) -> tuple[dict[str, dict[str, list[dict[str, str]]]], dict[str, Any]]:
    output: dict[str, dict[str, list[dict[str, str]]]] = {}
    receipts: dict[str, Any] = {}
    for review in v9.REVIEWS:
        path = stage / f"{review}.csv"
        groups: dict[str, list[dict[str, str]]] = defaultdict(list)
        raw_rows = empty = 0
        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            required = {"record_id", "title", "abstract", "label_included"}
            if reader.fieldnames is None or not required.issubset(reader.fieldnames):
                raise ValueError(f"Unexpected schema in {path}: {reader.fieldnames}")
            header = list(reader.fieldnames)
            for row_number, row in enumerate(reader, start=2):
                raw_rows += 1
                title, abstract = v9.normalize(row["title"]), v9.normalize(row["abstract"])
                if not (title or abstract):
                    empty += 1
                    continue
                content_id = v9.content_identity(title, abstract)
                groups[content_id].append({
                    "record_id": v9.normalize(row["record_id"]) or f"row-{row_number:09d}",
                    "duplicate_record_id": v9.normalize(row.get("duplicate_record_id")),
                    "title": title,
                    "abstract": abstract,
                })
        output[review] = dict(groups)
        receipts[review] = {
            "raw_rows": raw_rows,
            "header_sha256": hashlib.sha256("\0".join(header).encode()).hexdigest(),
            "empty_text_rows": empty,
            "within_review_duplicate_content_excess": sum(len(values) - 1 for values in groups.values()),
            "successor_label_values_accessed": False,
        }
    return output, receipts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--swift-root", type=Path, required=True)
    parser.add_argument("--v5-packet", type=Path, required=True)
    parser.add_argument("--v5-stage", type=Path, required=True)
    parser.add_argument("--v6-root", type=Path, required=True)
    parser.add_argument("--v8-root", type=Path, required=True)
    parser.add_argument("--kifms-stage", type=Path, required=True)
    parser.add_argument("--v9-packet", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    v9 = import_module(args.v9_packet / "prepare_population_v9.py", "p2_v9_prepare_for_v10")
    v5 = import_module(args.v5_packet / "run_synergy_label_blind_preflight_v5.py", "p2_v5_for_v10")
    v8 = import_module(args.v8_root / "run_donor_envelopment_v8.py", "p2_v8_for_v10")
    swift_content, swift_receipt = v5.load_swift_content(args.swift_root)
    v5_content, v5_receipt = v9.load_v5_content(args.v5_stage, v5)
    kifms_content, kifms_receipt = v9.load_kifms_content(v8, args.v6_root, args.kifms_stage)
    prior_content = swift_content | v5_content | kifms_content
    groups_by_review, source_receipts = load_candidate_label_blind(args.stage, v9)

    exact_group = groups_by_review[CONFLICT_REVIEW].get(CONFLICT_CONTENT, [])
    conflict_rule_bound = (
        tuple(sorted(row["record_id"] for row in exact_group)) == CONFLICT_RECORD_IDS
        and len(exact_group) == 2
        and all(not row["duplicate_record_id"] for row in exact_group)
    )

    owners: dict[str, set[str]] = defaultdict(set)
    for review, groups in groups_by_review.items():
        for content_id in groups:
            owners[content_id].add(review)
    cross_review_shared = {content_id for content_id, reviews in owners.items() if len(reviews) > 1}

    per_review: dict[str, Any] = {}
    final_content_multiset: list[str] = []
    final_content_owners: dict[str, set[str]] = defaultdict(set)
    for review in v9.REVIEWS:
        record_identities: list[str] = []
        content_multiset: list[str] = []
        native_split_rows = 0
        for content_id, values in groups_by_review[review].items():
            if content_id in prior_content or content_id in cross_review_shared:
                continue
            if review == CONFLICT_REVIEW and content_id == CONFLICT_CONTENT:
                chosen = sorted(values, key=lambda row: row["record_id"])
                native_split_rows = len(chosen)
                for row in chosen:
                    record_identities.append(native_record_identity(review, content_id, row["record_id"]))
                    content_multiset.append(content_id)
                    final_content_owners[content_id].add(review)
            else:
                chosen = min(values, key=lambda row: row["record_id"])
                record_identities.append(native_record_identity(review, content_id))
                content_multiset.append(content_id)
                final_content_owners[content_id].add(review)
        record_identities.sort()
        content_multiset.sort()
        final_content_multiset.extend(content_multiset)
        per_review[review] = {
            **source_receipts[review],
            "canonical_rows": len(record_identities),
            "provider_native_split_rows": native_split_rows,
            "canonical_record_order_sha256": hash_lines(record_identities),
            "canonical_content_multiset_sha256": hash_lines(content_multiset),
            "canonical_unique_content_identities": len(set(content_multiset)),
        }

    final_unique = set(final_content_multiset)
    result = {
        "identity": "P2_V10_PROVIDER_NATIVE_CONFLICT_RESOLVED_POPULATION_FREEZE",
        "status": "FROZEN_AFTER_V9_POPULATION_FAILURE_AND_SOURCE_NATIVE_AUDIT_BEFORE_ANY_V10_MODEL_OUTCOME",
        "review_units": list(v9.REVIEWS),
        "outcome_boundary": {
            "v9_public_labels_open": True,
            "v10_model_outcomes_accessed": False,
            "independent_or_protected_custody": False,
        },
        "conflict_resolution": {
            "review": CONFLICT_REVIEW,
            "normalized_title_abstract_content_identity": CONFLICT_CONTENT,
            "provider_record_ids": list(CONFLICT_RECORD_IDS),
            "provider_duplicate_record_id_blank_for_both": conflict_rule_bound,
            "rule": "Only for this exact content group, retain both provider-native nonduplicate records and suffix canonical row identity with provider record_id; do not choose between labels. All other V9 canonicalization and exclusion rules remain unchanged.",
            "passed": conflict_rule_bound,
        },
        "prior_content_receipts": {"swift": swift_receipt, "synergy_v5": v5_receipt, "kifms_v7": kifms_receipt},
        "prior_union_content_identities": len(prior_content),
        "prior_union_content_set_sha256": hash_lines(sorted(prior_content)),
        "candidate_cross_review_shared_content_identities": len(cross_review_shared),
        "per_review": per_review,
        "total_canonical_rows": len(final_content_multiset),
        "canonical_unique_content_identities": len(final_unique),
        "canonical_content_multiset_sha256": hash_lines(sorted(final_content_multiset)),
        "final_prior_union_overlap_count": len(final_unique & prior_content),
        "final_cross_review_shared_content_count": sum(len(reviews) > 1 for reviews in final_content_owners.values()),
    }
    result["passed"] = (
        conflict_rule_bound
        and result["final_prior_union_overlap_count"] == 0
        and result["final_cross_review_shared_content_count"] == 0
        and all(item["canonical_rows"] > 0 for item in per_review.values())
    )
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
