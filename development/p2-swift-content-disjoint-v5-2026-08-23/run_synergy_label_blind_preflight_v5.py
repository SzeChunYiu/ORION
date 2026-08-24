#!/usr/bin/env python3
"""Bind a label-blind, content-disjoint SYNERGY V5 population.

The runner reads source identifiers and text but never reads or emits the
``label_included`` field.  It removes every content identity found in the
opened SWIFT development panel and every identity shared by two selected
successor reviews before producing only hashes and aggregate counts.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import sys
import zipfile
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any


REVIEWS = ("Walker_2018", "Brouwer_2019", "Hall_2012", "Wassenaar_2017", "Leenaars_2020")


def normalize(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def normalize_openalex_id(value: Any) -> str:
    raw = normalize(value)
    return raw.rsplit("/", 1)[-1]


def abstract_from_index(value: Any) -> str:
    if not isinstance(value, dict):
        return ""
    positions: list[tuple[int, str]] = []
    for token, indexes in value.items():
        if not isinstance(indexes, list):
            continue
        for index in indexes:
            if isinstance(index, int):
                positions.append((index, str(token)))
    positions.sort(key=lambda item: (item[0], item[1]))
    return normalize(" ".join(token for _, token in positions))


def content_identity(title: str, abstract: str) -> str:
    return hashlib.sha256(normalize(f"{title} {abstract}").encode("utf-8")).hexdigest()


def record_identity(review: str, content_id: str) -> str:
    return hashlib.sha256(f"{review}\0{content_id}".encode("ascii")).hexdigest()


def hash_lines(values: list[str]) -> str:
    return hashlib.sha256("\n".join(values).encode("ascii")).hexdigest()


def load_label_ids(path: Path) -> tuple[list[str], dict[str, Any]]:
    ids: list[str] = []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        if header != ["openalex_id", "doi", "pmid", "label_included"]:
            raise ValueError(f"Unexpected label schema in {path}: {header}")
        for row_number, row in enumerate(reader, start=2):
            if len(row) != 4:
                raise ValueError(f"Unexpected label width in {path} row {row_number}")
            # Deliberately reference only the identifier cell.  The label value
            # is not inspected, counted, hashed, returned, or logged.
            ids.append(normalize_openalex_id(row[0]))
    counts = Counter(ids)
    return ids, {
        "label_identifier_rows": len(ids),
        "duplicate_label_identifier_excess": sum(count - 1 for count in counts.values()),
        "label_identifier_set_sha256": hash_lines(sorted(counts)),
        "label_schema": ["openalex_id", "doi", "pmid", "label_included"],
        "label_values_accessed": False,
    }


def load_works(review_root: Path) -> tuple[dict[str, dict[str, str]], dict[str, Any]]:
    works: dict[str, dict[str, str]] = {}
    duplicate_work_ids = 0
    member_count = 0
    raw_work_rows = 0
    for archive_path in sorted(review_root.glob("works_*.zip")):
        with zipfile.ZipFile(archive_path) as archive:
            for member in sorted(archive.namelist()):
                if not member.endswith(".json"):
                    continue
                member_count += 1
                rows = json.loads(archive.read(member))
                if not isinstance(rows, list):
                    raise ValueError(f"Expected a JSON list in {archive_path}:{member}")
                for row in rows:
                    raw_work_rows += 1
                    work_id = normalize_openalex_id(row.get("id"))
                    if not work_id:
                        raise ValueError(f"Missing OpenAlex id in {archive_path}:{member}")
                    value = {
                        "abstract": abstract_from_index(row.get("abstract_inverted_index")),
                        "title": normalize(row.get("title") or row.get("display_name")),
                    }
                    if work_id in works:
                        duplicate_work_ids += 1
                        if works[work_id] != value:
                            raise ValueError(f"Conflicting duplicate OpenAlex id {work_id}")
                    else:
                        works[work_id] = value
    return works, {
        "archive_count": len(list(review_root.glob("works_*.zip"))),
        "archive_json_member_count": member_count,
        "duplicate_work_identifier_excess": duplicate_work_ids,
        "raw_work_rows": raw_work_rows,
        "unique_work_identifiers": len(works),
        "work_identifier_set_sha256": hash_lines(sorted(works)),
    }


def load_v3_module(source_root: Path) -> Any:
    path = source_root / "run_swift_cross_review_controller_transport_v3.py"
    spec = importlib.util.spec_from_file_location("p2_swift_v3_preflight", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_swift_content(source_root: Path) -> tuple[set[str], dict[str, Any]]:
    v3 = load_v3_module(source_root)
    protocol = json.loads((source_root / "PROTOCOL_FREEZE_V3.json").read_text(encoding="utf-8"))
    pubmed, _ = v3.load_pubmed_snapshot(source_root / "private-source/pubmed-snapshot.jsonl")
    union: set[str] = set()
    counts: dict[str, int] = {}
    for review in v3.REVIEWS:
        rows, _ = v3.load_review(source_root, review, protocol, pubmed)
        identities = {row["content_identity"] for row in rows}
        union.update(identities)
        counts[review] = len(identities)
    return union, {
        "review_unique_content_counts": counts,
        "union_unique_content_count": len(union),
        "union_content_set_sha256": hash_lines(sorted(union)),
        "v3_result_sha256": hashlib.sha256((source_root / "RESULT_V3.json").read_bytes()).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage-root", type=Path, required=True)
    parser.add_argument("--swift-source-root", type=Path, required=True)
    parser.add_argument("--selection-freeze", type=Path, required=True)
    parser.add_argument("--source-binding", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    stage_root = args.stage_root.resolve()
    source_root = args.swift_source_root.resolve()
    selection = json.loads(args.selection_freeze.read_text(encoding="utf-8"))
    source_binding = json.loads(args.source_binding.read_text(encoding="utf-8"))
    if tuple(item["review"] for item in selection["selected_reviews"]) != REVIEWS:
        raise ValueError("Selected review order does not match the frozen runner")
    if not source_binding["all_passed"]:
        raise ValueError("Downloaded source binding did not pass")

    swift_content, swift_receipt = load_swift_content(source_root)
    provisional: dict[str, dict[str, dict[str, str]]] = {}
    receipts: dict[str, Any] = {}
    for review in REVIEWS:
        label_ids, label_receipt = load_label_ids(stage_root / review / "labels.csv")
        works, works_receipt = load_works(stage_root / review)
        seen_content: dict[str, str] = {}
        missing_work = 0
        empty_text = 0
        within_review_duplicate_content_excess = 0
        for work_id in label_ids:
            work = works.get(work_id)
            if work is None:
                missing_work += 1
                continue
            title, abstract = work["title"], work["abstract"]
            if not title and not abstract:
                empty_text += 1
                continue
            content_id = content_identity(title, abstract)
            if content_id in seen_content:
                within_review_duplicate_content_excess += 1
                if work_id < seen_content[content_id]:
                    seen_content[content_id] = work_id
            else:
                seen_content[content_id] = work_id
        provisional[review] = {
            content_id: {"openalex_id": work_id} for content_id, work_id in seen_content.items()
        }
        receipts[review] = {
            **label_receipt,
            **works_receipt,
            "missing_labeled_work_identifier_rows": missing_work,
            "empty_text_rows": empty_text,
            "within_review_duplicate_content_excess": within_review_duplicate_content_excess,
            "provisional_unique_content": len(seen_content),
            "work_identifiers_without_label": len(set(works) - set(label_ids)),
        }

    owners: dict[str, set[str]] = defaultdict(set)
    for review, rows in provisional.items():
        for content_id in rows:
            owners[content_id].add(review)
    shared_successor = {content_id for content_id, reviews in owners.items() if len(reviews) > 1}

    pairwise_before: list[dict[str, Any]] = []
    for review_a, review_b in combinations(REVIEWS, 2):
        count = len(set(provisional[review_a]) & set(provisional[review_b]))
        pairwise_before.append({"review_a": review_a, "review_b": review_b, "shared_content": count})

    final: dict[str, dict[str, str]] = {}
    for review in REVIEWS:
        before = provisional[review]
        swift_overlap = set(before) & swift_content
        successor_overlap = set(before) & shared_successor
        retained = {
            content_id: value
            for content_id, value in before.items()
            if content_id not in swift_overlap and content_id not in successor_overlap
        }
        record_ids = sorted(record_identity(review, content_id) for content_id in retained)
        content_ids = sorted(retained)
        openalex_ids = sorted(value["openalex_id"] for value in retained.values())
        receipts[review].update(
            {
                "excluded_swift_content_overlap": len(swift_overlap),
                "excluded_successor_pairwise_content_overlap": len(successor_overlap),
                "canonical_rows": len(retained),
                "canonical_content_set_sha256": hash_lines(content_ids),
                "canonical_openalex_id_set_sha256": hash_lines(openalex_ids),
                "canonical_record_order_sha256": hash_lines(record_ids),
            }
        )
        final[review] = {content_id: value["openalex_id"] for content_id, value in retained.items()}

    post_pairwise = []
    for review_a, review_b in combinations(REVIEWS, 2):
        post_pairwise.append(
            {
                "review_a": review_a,
                "review_b": review_b,
                "shared_content": len(set(final[review_a]) & set(final[review_b])),
            }
        )
    final_union = set().union(*(set(rows) for rows in final.values()))
    result = {
        "identity": "P2_SYNERGY_V5_LABEL_BLIND_CONTENT_DISJOINT_PREFLIGHT",
        "selection_freeze_sha256": hashlib.sha256(args.selection_freeze.read_bytes()).hexdigest(),
        "source_binding_sha256": hashlib.sha256(args.source_binding.read_bytes()).hexdigest(),
        "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "outcome_access_status": "NO_LABEL_VALUES, CLASS COUNTS, SEEDS, ACTIVE ORDERS, OR MODEL OUTCOMES ACCESSED",
        "review_receipts": receipts,
        "swift_development_receipt": swift_receipt,
        "pairwise_before_exclusion": pairwise_before,
        "shared_successor_content_identity_count": len(shared_successor),
        "pairwise_after_exclusion": post_pairwise,
        "final_swift_overlap_count": len(final_union & swift_content),
        "total_canonical_rows": sum(len(rows) for rows in final.values()),
        "canonical_union_content_set_sha256": hash_lines(sorted(final_union)),
        "passed": (
            len(final_union & swift_content) == 0
            and all(item["shared_content"] == 0 for item in post_pairwise)
            and all(receipts[review]["canonical_rows"] > 0 for review in REVIEWS)
        ),
    }
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
