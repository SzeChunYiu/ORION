#!/usr/bin/env python3
"""Derive exact MetaSyn retrieval/screening false-negative counts.

This is an evaluator-side utility. It combines the already archived official
MetaSyn ID-only evaluation selections with the pinned review labels from the
released test split. Candidate execution remains gold-blind: labels are loaded
only here, after candidate output has been frozen.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from datasets import load_dataset


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _round4(value: float) -> float:
    return round(value, 4)


def _metrics(reference: set[int], retrieved: set[int], included: set[int]) -> dict[str, float | None]:
    retrieved_reference = reference & retrieved
    retained_reference = retrieved_reference & included
    if not reference:
        raise RuntimeError("released MetaSyn test review unexpectedly has empty reference set")
    retrieval_recall = len(retrieved_reference) / len(reference)
    retrieval_precision = len(retrieved_reference) / len(retrieved) if retrieved else 0.0
    conditional_retention = (
        len(retained_reference) / len(retrieved_reference) if retrieved_reference else None
    )
    post_retrieval_loss = len(retrieved_reference - included) / len(reference)
    inclusion_recall = len(reference & included) / len(reference)
    inclusion_precision = len(reference & included) / len(included) if included else 0.0
    inclusion_f1 = (
        2 * inclusion_recall * inclusion_precision / (inclusion_recall + inclusion_precision)
        if inclusion_recall + inclusion_precision
        else 0.0
    )
    return {
        "retrieval_recall": _round4(retrieval_recall),
        "retrieval_precision": _round4(retrieval_precision),
        "conditional_retention": (
            _round4(conditional_retention) if conditional_retention is not None else None
        ),
        "post_retrieval_loss": _round4(post_retrieval_loss),
        "inclusion_recall": _round4(inclusion_recall),
        "inclusion_precision": _round4(inclusion_precision),
        "inclusion_f1": _round4(inclusion_f1),
    }


def derive(evaluation_path: Path, dataset: str, revision: str) -> dict[str, Any]:
    evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
    if evaluation.get("status") != "succeeded":
        raise RuntimeError("official MetaSyn evaluation is not succeeded")
    if evaluation.get("coverage", {}).get("succeeded_reviews") != 86:
        raise RuntimeError("official MetaSyn evaluation does not cover all 86 reviews")

    reviews = load_dataset(dataset, "reviews", split="test", revision=revision)
    reference_by_id = {
        int(row["ID"]): {int(value) for value in (row.get("matched_corpus_ids") or [])}
        for row in reviews
    }
    if len(reference_by_id) != 86:
        raise RuntimeError(f"expected 86 released MetaSyn test reviews, got {len(reference_by_id)}")

    rows: list[dict[str, Any]] = []
    total_reference = total_retrieved_reference = total_included_reference = 0
    total_retrieval_missed = total_screening_missed = total_final_missed = 0

    for item in evaluation["per_review"]:
        review_id = int(item["review_id"])
        reference = reference_by_id[review_id]
        selection = item["selection"]
        retrieved = {int(value) for value in selection["retrieved_article_ids"]}
        included = {int(value) for value in selection["included_article_ids"]}
        if not included <= retrieved:
            raise RuntimeError(f"review {review_id}: included set is outside retrieved set")

        recomputed = _metrics(reference, retrieved, included)
        for name, value in recomputed.items():
            if item["metrics"].get(name) != value:
                raise RuntimeError(
                    f"review {review_id}: metric mismatch for {name}: "
                    f"official={item['metrics'].get(name)!r} recomputed={value!r}"
                )

        retrieved_reference = reference & retrieved
        included_reference = reference & included
        retrieval_missed = reference - retrieved
        screening_missed = retrieved_reference - included
        final_missed = reference - included
        row = {
            "review_id": review_id,
            "reference_count": len(reference),
            "retrieved_reference_count": len(retrieved_reference),
            "included_reference_count": len(included_reference),
            "retrieval_false_negative_count": len(retrieval_missed),
            "screening_false_negative_count": len(screening_missed),
            "final_false_negative_count": len(final_missed),
        }
        rows.append(row)
        total_reference += row["reference_count"]
        total_retrieved_reference += row["retrieved_reference_count"]
        total_included_reference += row["included_reference_count"]
        total_retrieval_missed += row["retrieval_false_negative_count"]
        total_screening_missed += row["screening_false_negative_count"]
        total_final_missed += row["final_false_negative_count"]

    rows.sort(key=lambda row: row["review_id"])
    if {row["review_id"] for row in rows} != set(reference_by_id):
        raise RuntimeError("official evaluation/test-split review IDs differ")

    return {
        "schema_version": "orion.p2.metasyn-fn-ledger.v1",
        "authority": "EVALUATOR_SIDE_DERIVATION_FROM_OFFICIAL_METASYN_ID_ONLY_SELECTIONS",
        "dataset": dataset,
        "dataset_revision": revision,
        "official_evaluation_sha256": _sha256(evaluation_path),
        "reviews": len(rows),
        "aggregate": {
            "reference_article_links": total_reference,
            "retrieved_reference_links": total_retrieved_reference,
            "included_reference_links": total_included_reference,
            "retrieval_false_negative_count": total_retrieval_missed,
            "screening_false_negative_count": total_screening_missed,
            "final_false_negative_count": total_final_missed,
        },
        "definitions": {
            "retrieval_false_negative_count": "reference links absent from the retrieved top-200 pool",
            "screening_false_negative_count": "retrieved reference links omitted from the final included set",
            "final_false_negative_count": "reference links absent from the final included set; retrieval and screening misses combined",
        },
        "candidate_labels_visible": False,
        "per_review": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluation", type=Path, required=True)
    parser.add_argument("--dataset", default="THUIR/MetaSyn")
    parser.add_argument("--dataset-revision", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = derive(args.evaluation, args.dataset, args.dataset_revision)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("METASYN_FN_LEDGER=" + json.dumps(payload["aggregate"], sort_keys=True))


if __name__ == "__main__":
    main()
