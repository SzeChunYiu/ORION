#!/usr/bin/env python3
"""Gold-blind MetaSyn retrieval + deterministic protocol-screening probe.

MetaSyn's released 86-review test set supports an official ID-only evaluation
with strict JSON and no LLM judge. This runner uses that credential-free path.
A host-only ``prepare`` process reads the released review records and writes a
public allowlisted task file. The candidate ``run`` process receives only those
public protocol fields plus the public PubMed corpus; it never loads review
labels such as ``matched_corpus_ids``.

Retrieval uses the pinned MetaSyn BM25 implementation. Screening is deliberately
simple and predeclared here: it scores title/abstract evidence against public
PI/ECO/question terms, enforces a public search-end-year ceiling when available,
and includes a bounded subset by transparent rank/field-hit rules. It is an
external protocol-screening probe, not the final full multi-provider ORION run.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from statistics import fmean
from typing import Any

PINNED_METASYN_COMMIT = "51b95b7061e1faf241c205eb7f8e5c2bccff4848"
DEFAULT_DATASET = "THUIR/MetaSyn"
PUBLIC_FIELDS = (
    "ID",
    "Research_Question",
    "Population",
    "Intervention",
    "Exposure",
    "Comparison",
    "Outcome",
    "search_start_date",
    "search_end_date",
    "inclusion_criteria",
    "exclusion_criteria",
    "source_review_corpus_ids",
)
HIDDEN_LABEL_KEYS = frozenset(
    {
        "matched_corpus_ids",
        "matched_titles",
        "effect_direction",
        "key_insights",
        "included_articles",
        "reference_article_ids",
        "gold",
        "ground_truth",
        "label",
        "labels",
    }
)
WORD = re.compile(r"\b[a-z][a-z0-9-]{2,}\b", re.IGNORECASE)
YEAR = re.compile(r"(?:19|20)\d{2}")
STOPWORDS = frozenset(
    """
    the and for with from into over under between among this that these those
    study studies review reviews research question population intervention
    exposure comparison outcome effect effects patients patient participants
    using use used evaluate evaluation analysis analyses clinical trial trials
    systematic meta-analysis article articles paper papers include included
    inclusion exclude excluded exclusion criteria reported report investigate
    investigated whether association associations impact impacts compared versus
    based related among during after before within without across where when
    which whose their there such other also were was are is be been being has
    have had does do did can could may might should would will than then both
    """.split()
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number}: expected an object")
            records.append(value)
    return records


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def sanitize_review(review: dict[str, Any]) -> dict[str, Any]:
    """Return the exact public candidate view; label-like fields are not copied."""

    public = {field: review.get(field) for field in PUBLIC_FIELDS}
    if isinstance(public.get("ID"), bool) or not isinstance(public.get("ID"), int):
        raise ValueError("MetaSyn review ID must be an integer")
    source_ids = public.get("source_review_corpus_ids") or []
    public["source_review_corpus_ids"] = [int(value) for value in source_ids]
    if any(key.lower() in HIDDEN_LABEL_KEYS for key in public):
        raise AssertionError("hidden MetaSyn label field crossed candidate boundary")
    return public


def _tokens(value: Any) -> set[str]:
    text = "" if value in (None, "", "NR") else str(value)
    return {
        token.lower()
        for token in WORD.findall(text)
        if token.lower() not in STOPWORDS and len(token) >= 3
    }


def _end_year(review: dict[str, Any]) -> int | None:
    matches = YEAR.findall(str(review.get("search_end_date") or ""))
    return int(matches[-1]) if matches else None


def _field_sets(review: dict[str, Any]) -> list[set[str]]:
    intervention = review.get("Intervention")
    if not _tokens(intervention):
        intervention = review.get("Exposure")
    fields = (
        review.get("Research_Question"),
        review.get("Population"),
        intervention,
        review.get("Comparison"),
        review.get("Outcome"),
    )
    return [tokens for value in fields if (tokens := _tokens(value))]


def screen_candidates(
    review: dict[str, Any], candidates: list[dict[str, Any]], *, cap: int = 60
) -> list[int]:
    """Deterministically screen a retrieved pool from public protocol fields only.

    Predeclared rule:
    * reject known publications after the protocol search-end year;
    * include rank <= 20 when at least one PI/ECO/question field matches;
    * include any rank when >=3 fields match;
    * include candidates with >=2 field matches and BM25 score >=25% of the
      task's top retrieved score;
    * cap the final list at 60 in original retrieval order.

    No benchmark labels, linked-study titles or reference IDs participate.
    """

    if cap < 1:
        raise ValueError("screen cap must be positive")
    fields = _field_sets(review)
    if not fields:
        return []
    end_year = _end_year(review)
    top_score = max(
        (float(item.get("score") or 0.0) for item in candidates), default=0.0
    )
    selected: list[int] = []
    for fallback_rank, candidate in enumerate(candidates, 1):
        corpus_id = int(candidate["corpus_id"])
        rank = int(candidate.get("rank") or fallback_rank)
        year = candidate.get("year")
        if end_year is not None and isinstance(year, int) and year > end_year:
            continue
        evidence = _tokens(
            f"{candidate.get('title') or ''} {candidate.get('abstract') or ''}"
        )
        hits = sum(bool(field & evidence) for field in fields)
        score = float(candidate.get("score") or 0.0)
        normalized = score / top_score if top_score > 0 else 0.0
        keep = (rank <= 20 and hits >= 1) or hits >= 3 or (
            hits >= 2 and normalized >= 0.25
        )
        if keep:
            selected.append(corpus_id)
        if len(selected) == cap:
            break
    return selected


def prepare(
    output_path: Path,
    manifest_path: Path,
    *,
    dataset: str,
    dataset_revision: str | None,
) -> dict[str, Any]:
    """Host-only release split: load full reviews, write only the public allowlist."""

    from metasyn.data import load_reviews  # type: ignore[import-not-found]

    reviews = [dict(row) for row in load_reviews("test", dataset, dataset_revision)]
    if len(reviews) != 86:
        raise RuntimeError(f"expected 86 MetaSyn test reviews, found {len(reviews)}")
    public = [sanitize_review(review) for review in reviews]
    _write_jsonl(output_path, public)
    payload = {
        "schema_version": "orion.p2.metasyn-public-split.v1",
        "pinned_upstream_commit": PINNED_METASYN_COMMIT,
        "dataset": dataset,
        "dataset_revision": dataset_revision,
        "test_reviews": len(public),
        "public_fields": list(PUBLIC_FIELDS),
        "hidden_label_fields_visible_to_candidate": False,
        "public_reviews_sha256": _sha256(output_path),
    }
    manifest_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return payload


def _results_tree_digest(results_dir: Path) -> str:
    digest = hashlib.sha256()
    paths = sorted(results_dir.rglob("results.json"))
    for path in paths:
        digest.update(str(path.relative_to(results_dir)).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def run_candidate(
    public_reviews_path: Path,
    results_dir: Path,
    manifest_path: Path,
    *,
    dataset: str,
    dataset_revision: str | None,
    top_k: int,
    screen_cap: int,
) -> dict[str, Any]:
    """Candidate lane: public reviews + public corpus only; no MetaSyn labels loaded."""

    from metasyn.data import load_corpus  # type: ignore[import-not-found]
    from metasyn.sparse import BM25Retriever  # type: ignore[import-not-found]

    public_reviews = _jsonl(public_reviews_path)
    if len(public_reviews) != 86:
        raise RuntimeError(f"candidate expected 86 public reviews, found {len(public_reviews)}")
    for review in public_reviews:
        unexpected = set(review) - set(PUBLIC_FIELDS)
        if unexpected:
            raise AssertionError(f"candidate review contains unexpected fields: {sorted(unexpected)}")
        if any(key.lower() in HIDDEN_LABEL_KEYS for key in review):
            raise AssertionError("candidate review contains a hidden label field")

    corpus = load_corpus(dataset, dataset_revision)
    retriever = BM25Retriever(corpus)
    results_dir.mkdir(parents=True, exist_ok=True)
    retrieved_counts: list[int] = []
    included_counts: list[int] = []

    for index, review in enumerate(public_reviews, 1):
        retrieved = retriever.search(review, k=top_k)
        retrieved_ids = [int(item["corpus_id"]) for item in retrieved]
        included_ids = screen_candidates(review, retrieved, cap=screen_cap)
        if len(retrieved_ids) != len(set(retrieved_ids)):
            raise AssertionError("MetaSyn retriever returned duplicate corpus IDs")
        if not set(included_ids) <= set(retrieved_ids):
            raise AssertionError("screening selected an article outside the retrieved pool")
        review_id = int(review["ID"])
        target = results_dir / f"review_{review_id}" / "results.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(
                {
                    "review_id": review_id,
                    "retrieved_article_ids": retrieved_ids,
                    "included_article_ids": included_ids,
                    "unmatched_included_article_ids": [],
                    "unmatched_included_entries": [],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        retrieved_counts.append(len(retrieved_ids))
        included_counts.append(len(included_ids))
        if index % 10 == 0 or index == len(public_reviews):
            print(
                f"METASYN_PROGRESS={index}/86 mean_retrieved={fmean(retrieved_counts):.2f} "
                f"mean_included={fmean(included_counts):.2f}",
                flush=True,
            )

    payload = {
        "schema_version": "orion.p2.metasyn-keyless-run.v1",
        "pinned_upstream_commit": PINNED_METASYN_COMMIT,
        "dataset": dataset,
        "dataset_revision": dataset_revision,
        "public_reviews_sha256": _sha256(public_reviews_path),
        "results_tree_sha256": _results_tree_digest(results_dir),
        "reviews_attempted": len(public_reviews),
        "retriever": "pinned MetaSyn BM25 title+abstract",
        "retrieval_top_k": top_k,
        "screening": "predeclared PI/ECO/question field-hit rule",
        "screen_cap": screen_cap,
        "mean_retrieved": round(fmean(retrieved_counts), 4),
        "mean_included": round(fmean(included_counts), 4),
        "hidden_label_fields_visible_to_candidate": False,
    }
    manifest_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return payload


def summarize(
    split_manifest_path: Path,
    run_manifest_path: Path,
    evaluation_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    split = json.loads(split_manifest_path.read_text(encoding="utf-8"))
    run = json.loads(run_manifest_path.read_text(encoding="utf-8"))
    evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
    if evaluation.get("status") != "succeeded":
        raise RuntimeError("MetaSyn official ID-only evaluator did not succeed")
    payload = {
        "schema_version": "orion.p2.metasyn-id-only-official.v1",
        "benchmark": "MetaSyn",
        "pinned_upstream_commit": PINNED_METASYN_COMMIT,
        "dataset": split["dataset"],
        "dataset_revision": split["dataset_revision"],
        "candidate": "ORION keyless BM25 + deterministic public-protocol screening probe",
        "claim_scope": "external_probe_not_full_multi_provider_orion",
        "authority": "OFFICIAL_METASYN_ID_ONLY_EVALUATOR",
        "selection_source": "json",
        "id_only": True,
        "test_reviews": split["test_reviews"],
        "hidden_label_fields_visible_to_candidate": False,
        "public_reviews_sha256": split["public_reviews_sha256"],
        "results_tree_sha256": run["results_tree_sha256"],
        "official_evaluation_sha256": _sha256(evaluation_path),
        "coverage": evaluation.get("coverage"),
        "macro_metrics": evaluation.get("macro_metrics"),
        "metric_counts": evaluation.get("metric_counts"),
        "mean_retrieved": run["mean_retrieved"],
        "mean_included": run["mean_included"],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_prepare = sub.add_parser("prepare")
    p_prepare.add_argument("--output", type=Path, required=True)
    p_prepare.add_argument("--manifest", type=Path, required=True)
    p_prepare.add_argument("--dataset", default=DEFAULT_DATASET)
    p_prepare.add_argument("--dataset-revision")

    p_run = sub.add_parser("run")
    p_run.add_argument("--public-reviews", type=Path, required=True)
    p_run.add_argument("--results-dir", type=Path, required=True)
    p_run.add_argument("--manifest", type=Path, required=True)
    p_run.add_argument("--dataset", default=DEFAULT_DATASET)
    p_run.add_argument("--dataset-revision")
    p_run.add_argument("--top-k", type=int, default=200)
    p_run.add_argument("--screen-cap", type=int, default=60)

    p_summary = sub.add_parser("summarize")
    p_summary.add_argument("--split-manifest", type=Path, required=True)
    p_summary.add_argument("--run-manifest", type=Path, required=True)
    p_summary.add_argument("--evaluation", type=Path, required=True)
    p_summary.add_argument("--output", type=Path, required=True)

    args = parser.parse_args(argv)
    if args.command == "prepare":
        payload = prepare(
            args.output,
            args.manifest,
            dataset=args.dataset,
            dataset_revision=args.dataset_revision,
        )
        print("METASYN_SPLIT=" + json.dumps(payload, sort_keys=True))
        return 0
    if args.command == "run":
        payload = run_candidate(
            args.public_reviews,
            args.results_dir,
            args.manifest,
            dataset=args.dataset,
            dataset_revision=args.dataset_revision,
            top_k=args.top_k,
            screen_cap=args.screen_cap,
        )
        print("METASYN_RUN=" + json.dumps(payload, sort_keys=True))
        return 0
    if args.command == "summarize":
        payload = summarize(
            args.split_manifest,
            args.run_manifest,
            args.evaluation,
            args.output,
        )
        print("METASYN_OFFICIAL=" + json.dumps(payload, sort_keys=True))
        return 0
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())