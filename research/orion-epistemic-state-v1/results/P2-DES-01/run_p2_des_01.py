#!/usr/bin/env python3
"""Execute the prospectively frozen P2-DES-01 TREC-COVID study.

The policy phase receives corpus text and public topic formulations only.  It
materializes and hashes every ranking and decision before this process opens the
qrels file.  Public qrels are then used by the evaluator, never by a policy.
"""

from __future__ import annotations

import argparse
import hashlib
import heapq
import json
import math
import os
import platform
import random
import re
import resource
import shutil
import socket
import statistics
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


JOB_ID = "P2-DES-01"
SCHEMA_PREFIX = "orion.p2-des-01"
EXPECTED_TOPICS = tuple(str(index) for index in range(1, 51))
POLICY_ORDER = (
    "BM25_QUESTION",
    "LOCAL_MULTIFORM_RRF",
    "DIVERSIFIED_ROUND_ROBIN",
    "LOCAL_SATURATION_STOP",
    "RANDOM_REMOTE",
    "ANALOGY_PRF",
    "STRUCTURAL_JUMP",
    "IDEAL_DONOR_PRODUCT_RRF",
)
BM25_K1 = 1.2
BM25_B = 0.75
RRF_K = 60
QUERY_DEPTH = 300
READ_BUDGET = 100
QUERY_BUDGET = 4
SATURATION_JACCARD_MIN = 0.20
SATURATION_THIRD_UNIQUE_MAX = 0.25
FEEDBACK_DOCUMENTS = 20
BRIDGE_TERMS = 8
BRIDGE_MIN_FEEDBACK_DF = 3
BRIDGE_MAX_CORPUS_DF_FRACTION = 0.10
BOOTSTRAP_RESAMPLES = 10_000
BOOTSTRAP_SEED = 20_260_825
TOKEN_RE = re.compile(r"[^\W_]+", re.UNICODE)
FORBIDDEN_POLICY_KEYS = {
    "answer",
    "family_label",
    "generator_label",
    "gold",
    "label",
    "metric",
    "outcome",
    "qrel",
    "qrels",
    "relevance",
    "relevant",
}


class PreconditionError(RuntimeError):
    """A frozen hard precondition was not attained."""


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    path.write_bytes(canonical_json_bytes(value))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tokenize(text: str) -> tuple[str, ...]:
    return tuple(token.lower() for token in TOKEN_RE.findall(text) if len(token) >= 2)


def stable_seed(topic_id: str) -> int:
    return int.from_bytes(hashlib.sha256(f"{BOOTSTRAP_SEED}:{topic_id}".encode()).digest()[:8], "big")


class Bm25Index:
    """A deterministic inverted Okapi BM25 index over the complete corpus."""

    def __init__(self, documents: Sequence[tuple[str, str]]) -> None:
        self.doc_ids: list[str] = []
        self.texts: list[str] = []
        self.lengths: list[int] = []
        self.postings: dict[str, list[tuple[int, int]]] = defaultdict(list)
        self.doc_index: dict[str, int] = {}
        for doc_id, text in documents:
            if doc_id in self.doc_index:
                raise PreconditionError(f"duplicate corpus document id: {doc_id}")
            index = len(self.doc_ids)
            self.doc_index[doc_id] = index
            self.doc_ids.append(doc_id)
            self.texts.append(text)
            terms = tokenize(text)
            self.lengths.append(len(terms))
            for term, frequency in Counter(terms).items():
                self.postings[term].append((index, frequency))
        if not self.doc_ids:
            raise PreconditionError("corpus contains zero documents")
        self.count = len(self.doc_ids)
        self.average_length = sum(self.lengths) / self.count

    def document_frequency(self, term: str) -> int:
        return len(self.postings.get(term, ()))

    def inverse_document_frequency(self, term: str) -> float:
        df = self.document_frequency(term)
        return math.log(1.0 + (self.count - df + 0.5) / (df + 0.5))

    def search(self, query: str | Sequence[str], depth: int = QUERY_DEPTH) -> list[str]:
        terms = tokenize(query) if isinstance(query, str) else tuple(query)
        scores: dict[int, float] = defaultdict(float)
        for term in dict.fromkeys(terms):
            postings = self.postings.get(term)
            if not postings:
                continue
            inverse_df = self.inverse_document_frequency(term)
            for index, frequency in postings:
                normalization = BM25_K1 * (
                    1.0 - BM25_B + BM25_B * self.lengths[index] / (self.average_length or 1.0)
                )
                scores[index] += inverse_df * (
                    frequency * (BM25_K1 + 1.0) / (frequency + normalization)
                )
        ordered = heapq.nsmallest(
            min(depth, len(scores)),
            scores.items(),
            key=lambda pair: (-pair[1], self.doc_ids[pair[0]]),
        )
        return [self.doc_ids[index] for index, _ in ordered]

    def bridge_terms(self, feedback_doc_ids: Sequence[str], excluded: set[str]) -> list[str]:
        feedback_df: Counter[str] = Counter()
        feedback_tf: Counter[str] = Counter()
        for doc_id in feedback_doc_ids[:FEEDBACK_DOCUMENTS]:
            counts = Counter(tokenize(self.texts[self.doc_index[doc_id]]))
            feedback_df.update(counts.keys())
            feedback_tf.update(counts)
        scored: list[tuple[float, str]] = []
        maximum_df = self.count * BRIDGE_MAX_CORPUS_DF_FRACTION
        for term, local_df in feedback_df.items():
            corpus_df = self.document_frequency(term)
            if (
                term in excluded
                or local_df < BRIDGE_MIN_FEEDBACK_DF
                or corpus_df <= 0
                or corpus_df > maximum_df
            ):
                continue
            score = math.log(1.0 + self.count / (corpus_df + 1.0)) * math.log(
                1.0 + feedback_tf[term]
            )
            scored.append((score, term))
        scored.sort(key=lambda item: (-item[0], item[1]))
        return [term for _, term in scored[:BRIDGE_TERMS]]


def reciprocal_rank_fusion(rankings: Sequence[Sequence[str]], depth: int = QUERY_DEPTH) -> list[str]:
    scores: dict[str, float] = defaultdict(float)
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, start=1):
            scores[doc_id] += 1.0 / (RRF_K + rank)
    return [
        doc_id
        for doc_id, _ in sorted(scores.items(), key=lambda item: (-item[1], item[0]))[:depth]
    ]


def diversified_round_robin(rankings: Sequence[Sequence[str]], depth: int = QUERY_DEPTH) -> list[str]:
    output: list[str] = []
    seen: set[str] = set()
    cursor = 0
    while len(output) < depth:
        progressed = False
        for ranking in rankings:
            if cursor < len(ranking):
                progressed = True
                doc_id = ranking[cursor]
                if doc_id not in seen:
                    seen.add(doc_id)
                    output.append(doc_id)
                    if len(output) >= depth:
                        break
        if not progressed:
            break
        cursor += 1
    return output


def mean_pairwise_jaccard(rankings: Sequence[Sequence[str]], depth: int = READ_BUDGET) -> float:
    sets = [set(ranking[:depth]) for ranking in rankings]
    values: list[float] = []
    for left in range(len(sets)):
        for right in range(left + 1, len(sets)):
            union = sets[left] | sets[right]
            values.append(len(sets[left] & sets[right]) / len(union) if union else 0.0)
    return statistics.fmean(values) if values else 0.0


def saturation_state(rankings: Sequence[Sequence[str]]) -> dict[str, Any]:
    jaccard = mean_pairwise_jaccard(rankings)
    first_two = set(rankings[0][:READ_BUDGET]) | set(rankings[1][:READ_BUDGET])
    third = set(rankings[2][:READ_BUDGET])
    third_unique = third - first_two
    third_unique_fraction = len(third_unique) / max(1, len(third))
    triggered = (
        jaccard >= SATURATION_JACCARD_MIN
        and third_unique_fraction <= SATURATION_THIRD_UNIQUE_MAX
    )
    return {
        "mean_pairwise_jaccard": jaccard,
        "third_route_marginal_unique_fraction": third_unique_fraction,
        "triggered": triggered,
    }


def merge_head_and_remote(local: Sequence[str], remote: Sequence[str]) -> list[str]:
    output = list(local[:60])
    seen = set(output)
    local_top_300 = set(local[:QUERY_DEPTH])
    for doc_id in remote:
        if doc_id in seen or doc_id in local_top_300:
            continue
        output.append(doc_id)
        seen.add(doc_id)
        if len(output) >= READ_BUDGET:
            return output
    for doc_id in local[60:]:
        if doc_id not in seen:
            output.append(doc_id)
            seen.add(doc_id)
            if len(output) >= READ_BUDGET:
                break
    return output


def deterministic_remote_sample(index: Bm25Index, local: Sequence[str], topic_id: str) -> list[str]:
    excluded = set(local[:QUERY_DEPTH])
    rng = random.Random(stable_seed(topic_id))
    selected: list[str] = []
    seen: set[str] = set()
    maximum_attempts = max(10_000, index.count * 2)
    attempts = 0
    while len(selected) < 40 and attempts < maximum_attempts:
        doc_id = index.doc_ids[rng.randrange(index.count)]
        attempts += 1
        if doc_id in excluded or doc_id in seen:
            continue
        seen.add(doc_id)
        selected.append(doc_id)
    return selected


def clipped_unresolvedness(rankings: Sequence[Sequence[str]]) -> float:
    at_100 = set().union(*(set(ranking[:READ_BUDGET]) for ranking in rankings))
    at_300 = set().union(*(set(ranking[:QUERY_DEPTH]) for ranking in rankings))
    value = 1.0 - len(at_100) / max(1, len(at_300))
    return min(1.0, max(0.0, value))


def load_public_inputs(data_root: Path) -> tuple[list[tuple[str, str]], list[dict[str, str]], dict[str, Any]]:
    corpus_path = data_root / "corpus.jsonl"
    queries_path = data_root / "queries.jsonl"
    qrels_path = data_root / "qrels" / "test.tsv"
    for path in (corpus_path, queries_path, qrels_path):
        if not path.is_file():
            raise PreconditionError(f"required input missing: {path}")

    documents: list[tuple[str, str]] = []
    corpus_top_level_keys: set[str] = set()
    with corpus_path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            row = json.loads(line)
            corpus_top_level_keys.update(str(key).lower() for key in row)
            if "_id" not in row:
                raise PreconditionError(f"corpus line {line_number} lacks _id")
            documents.append(
                (
                    str(row["_id"]),
                    f"{row.get('title', '')} {row.get('text', '')}",
                )
            )

    forbidden = sorted(corpus_top_level_keys & FORBIDDEN_POLICY_KEYS)
    if forbidden:
        raise PreconditionError(f"forbidden policy-visible corpus keys: {forbidden}")

    topics: list[dict[str, str]] = []
    query_top_level_keys: set[str] = set()
    with queries_path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            row = json.loads(line)
            query_top_level_keys.update(str(key).lower() for key in row)
            metadata = row.get("metadata") or {}
            topic = {
                "topic_id": str(row.get("_id", "")),
                "question": str(row.get("text", "")),
                "keyword_query": str(metadata.get("query", "")),
                "narrative": str(metadata.get("narrative", "")),
            }
            if not all(topic.values()):
                raise PreconditionError(
                    f"query line {line_number} lacks one or more frozen public forms: {topic['topic_id']}"
                )
            topics.append(topic)
    forbidden_queries = sorted(query_top_level_keys & FORBIDDEN_POLICY_KEYS)
    if forbidden_queries:
        raise PreconditionError(f"forbidden policy-visible query keys: {forbidden_queries}")
    topic_ids = tuple(sorted((topic["topic_id"] for topic in topics), key=int))
    if topic_ids != EXPECTED_TOPICS:
        raise PreconditionError(
            f"topic identity mismatch: expected {EXPECTED_TOPICS}, got {topic_ids}"
        )
    topics.sort(key=lambda item: int(item["topic_id"]))
    public_manifest = {
        "corpus_documents": len(documents),
        "topics": len(topics),
        "corpus_top_level_keys": sorted(corpus_top_level_keys),
        "query_top_level_keys": sorted(query_top_level_keys),
        "forbidden_policy_keys_found": [],
        "corpus_sha256": sha256_file(corpus_path),
        "queries_sha256": sha256_file(queries_path),
        "qrels_stat_before_policy_phase": {
            "bytes": qrels_path.stat().st_size,
            "sha256": "DEFERRED_UNTIL_AFTER_POLICY_OUTPUT_HASH",
        },
    }
    return documents, topics, public_manifest


def generate_policy_outputs(index: Bm25Index, topics: Sequence[Mapping[str, str]]) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    for topic in topics:
        topic_id = topic["topic_id"]
        forms = [topic["question"], topic["keyword_query"], topic["narrative"]]
        local_rankings = [index.search(form, QUERY_DEPTH) for form in forms]
        if any(len(ranking) < READ_BUDGET for ranking in local_rankings):
            raise PreconditionError(f"topic {topic_id}: a registered local ranking has fewer than 100 items")
        local_rrf = reciprocal_rank_fusion(local_rankings, QUERY_DEPTH)
        diversified = diversified_round_robin(local_rankings, QUERY_DEPTH)
        saturation = saturation_state(local_rankings)
        excluded = set(tokenize(" ".join(forms)))
        bridges = index.bridge_terms(local_rrf[:FEEDBACK_DOCUMENTS], excluded)
        analogy_query = tuple(tokenize(topic["question"])) + tuple(bridges)
        analogy = index.search(analogy_query, QUERY_DEPTH)
        if len(analogy) < READ_BUDGET:
            # The predeclared fill is the local ranking, not a hidden retune.
            analogy = list(dict.fromkeys(analogy + local_rrf))[:QUERY_DEPTH]
        random_remote = (
            merge_head_and_remote(local_rrf, deterministic_remote_sample(index, local_rrf, topic_id))
            if saturation["triggered"]
            else local_rrf[:READ_BUDGET]
        )
        jump_licensed = bool(saturation["triggered"] and bridges)
        structural = (
            merge_head_and_remote(local_rrf, analogy)
            if jump_licensed
            else local_rrf[:READ_BUDGET]
        )
        ideal = reciprocal_rank_fusion([local_rrf, diversified, analogy], QUERY_DEPTH)
        stop_depth = 60 if saturation["triggered"] else READ_BUDGET
        unresolvedness = clipped_unresolvedness(local_rankings)
        rankings = {
            "BM25_QUESTION": local_rankings[0][:READ_BUDGET],
            "LOCAL_MULTIFORM_RRF": local_rrf[:READ_BUDGET],
            "DIVERSIFIED_ROUND_ROBIN": diversified[:READ_BUDGET],
            "LOCAL_SATURATION_STOP": local_rrf[:stop_depth],
            "RANDOM_REMOTE": random_remote[:READ_BUDGET],
            "ANALOGY_PRF": analogy[:READ_BUDGET],
            "STRUCTURAL_JUMP": structural[:READ_BUDGET],
            "IDEAL_DONOR_PRODUCT_RRF": ideal[:READ_BUDGET],
        }
        if set(rankings) != set(POLICY_ORDER):
            raise PreconditionError(f"topic {topic_id}: policy set drift")
        cases.append(
            {
                "topic_id": topic_id,
                "policy_rankings": rankings,
                "policy_full_counterfactual_to_100": {
                    "LOCAL_SATURATION_STOP": local_rrf[:READ_BUDGET]
                },
                "task_closure_declared": {
                    policy: bool(policy == "LOCAL_SATURATION_STOP" and saturation["triggered"])
                    for policy in POLICY_ORDER
                },
                "local_saturation": saturation,
                "bridge_terms": bridges,
                "jump_licensed": jump_licensed,
                "unresolvedness_estimate": unresolvedness,
                "registered_query_calls": {
                    "BM25_QUESTION": 1,
                    "LOCAL_MULTIFORM_RRF": 3,
                    "DIVERSIFIED_ROUND_ROBIN": 3,
                    "LOCAL_SATURATION_STOP": 3,
                    "RANDOM_REMOTE": 4 if saturation["triggered"] else 3,
                    "ANALOGY_PRF": 4,
                    "STRUCTURAL_JUMP": 4 if jump_licensed else 3,
                    "IDEAL_DONOR_PRODUCT_RRF": 4,
                },
                "route_sources": {
                    "local": ["question", "keyword_query", "narrative"],
                    "remote": "bridge_term_BM25_outside_LOCAL_MULTIFORM_RRF_top300",
                },
            }
        )
        print(
            f"topic {topic_id:>2}: saturation={saturation['triggered']} "
            f"bridges={len(bridges)} jump={jump_licensed}",
            flush=True,
        )
    return {
        "schema": f"{SCHEMA_PREFIX}.pre-score-policy-outputs.v1",
        "job_id": JOB_ID,
        "qrels_opened": false,
        "cases": cases,
    }


def load_qrels_after_policy_hash(data_root: Path) -> tuple[dict[str, dict[str, int]], dict[str, Any]]:
    path = data_root / "qrels" / "test.tsv"
    qrels: dict[str, dict[str, int]] = defaultdict(dict)
    row_count = 0
    duplicate_pairs = 0
    with path.open(encoding="utf-8") as handle:
        header = next(handle, "").strip().split()
        if len(header) < 3:
            raise PreconditionError(f"malformed qrels header: {header}")
        for line_number, line in enumerate(handle, start=2):
            fields = line.split()
            if len(fields) != 3:
                raise PreconditionError(f"malformed qrels line {line_number}")
            topic_id, doc_id, label_text = fields
            label = int(label_text)
            if doc_id in qrels[topic_id]:
                duplicate_pairs += 1
            qrels[topic_id][doc_id] = label
            row_count += 1
    if tuple(sorted(qrels, key=int)) != EXPECTED_TOPICS:
        raise PreconditionError("qrels topic identity does not equal frozen 50-topic set")
    return qrels, {
        "qrels_sha256": sha256_file(path),
        "qrels_bytes": path.stat().st_size,
        "qrels_rows": row_count,
        "duplicate_topic_document_pairs": duplicate_pairs,
    }


def recall_at_depth(ranking: Sequence[str], judgments: Mapping[str, int]) -> float:
    relevant = {doc_id for doc_id, grade in judgments.items() if grade > 0}
    return len(relevant & set(ranking)) / len(relevant) if relevant else 0.0


def ndcg_at_10(ranking: Sequence[str], judgments: Mapping[str, int]) -> float:
    dcg = sum(
        (2 ** judgments.get(doc_id, 0) - 1) / math.log2(index + 2)
        for index, doc_id in enumerate(ranking[:10])
    )
    ideal = sorted(judgments.values(), reverse=True)[:10]
    ideal_dcg = sum((2**grade - 1) / math.log2(index + 2) for index, grade in enumerate(ideal))
    return dcg / ideal_dcg if ideal_dcg else 0.0


def evaluate(policy_outputs: Mapping[str, Any], qrels: Mapping[str, Mapping[str, int]]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for case in policy_outputs["cases"]:
        topic_id = case["topic_id"]
        judgments = qrels[topic_id]
        relevant = {doc_id for doc_id, grade in judgments.items() if grade > 0}
        for policy in POLICY_ORDER:
            ranking = case["policy_rankings"][policy]
            relevant_found = len(relevant & set(ranking))
            recall = recall_at_depth(ranking, judgments)
            declared = bool(case["task_closure_declared"][policy])
            counterfactual = case["policy_full_counterfactual_to_100"].get(policy, ranking)
            tail = counterfactual[len(ranking) : READ_BUDGET]
            missed_in_own_tail = len(relevant & set(tail))
            premature = bool(declared and missed_in_own_tail > 0)
            judged = sum(1 for doc_id in ranking if doc_id in judgments)
            residual = 1.0 - recall
            unresolvedness = float(case["unresolvedness_estimate"])
            rows.append(
                {
                    "topic_id": topic_id,
                    "policy_id": policy,
                    "status": "SCORED",
                    "returned_depth": len(ranking),
                    "unique_documents_returned": len(set(ranking)),
                    "registered_query_calls": case["registered_query_calls"][policy],
                    "relevant_documents_total": len(relevant),
                    "relevant_documents_found": relevant_found,
                    "recall_at_100_budget": recall,
                    "ndcg_at_10": ndcg_at_10(ranking, judgments),
                    "judged_fraction_at_returned_depth": judged / len(ranking) if ranking else 0.0,
                    "relevant_yield_per_100_reads": (
                        relevant_found * 100.0 / len(ranking) if ranking else 0.0
                    ),
                    "qrels_bounded_residual_fraction": residual,
                    "unresolvedness_estimate": unresolvedness,
                    "calibrated_unresolvedness_brier": (unresolvedness - residual) ** 2,
                    "local_saturation_triggered": bool(case["local_saturation"]["triggered"]),
                    "jump_licensed": bool(case["jump_licensed"]),
                    "bridge_term_count": len(case["bridge_terms"]),
                    "task_closure_declared": declared,
                    "qrels_relevant_in_own_withheld_tail": missed_in_own_tail,
                    "premature_task_closure": premature,
                }
            )
    return {
        "schema": f"{SCHEMA_PREFIX}.raw-policy-outcomes.v1",
        "job_id": JOB_ID,
        "case_policy_rows": rows,
    }


def bootstrap_mean_interval(values: Sequence[float], *, seed: int) -> dict[str, float | int]:
    if not values:
        return {"n": 0, "mean": 0.0, "lower_95": 0.0, "upper_95": 0.0}
    rng = random.Random(seed)
    size = len(values)
    draws = sorted(
        statistics.fmean(values[rng.randrange(size)] for _ in range(size))
        for _ in range(BOOTSTRAP_RESAMPLES)
    )
    lower_index = int(0.025 * (BOOTSTRAP_RESAMPLES - 1))
    upper_index = int(0.975 * (BOOTSTRAP_RESAMPLES - 1))
    return {
        "n": size,
        "mean": statistics.fmean(values),
        "lower_95": draws[lower_index],
        "upper_95": draws[upper_index],
        "resamples": BOOTSTRAP_RESAMPLES,
        "seed": seed,
    }


def aggregate(raw: Mapping[str, Any]) -> dict[str, Any]:
    rows = raw["case_policy_rows"]
    by_policy: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    by_key: dict[tuple[str, str], Mapping[str, Any]] = {}
    for row in rows:
        by_policy[row["policy_id"]].append(row)
        by_key[(row["topic_id"], row["policy_id"])] = row

    summaries: dict[str, Any] = {}
    for policy in POLICY_ORDER:
        items = by_policy[policy]
        summaries[policy] = {
            "topic_rows": len(items),
            "mean_recall_at_100_budget": statistics.fmean(
                item["recall_at_100_budget"] for item in items
            ),
            "mean_ndcg_at_10": statistics.fmean(item["ndcg_at_10"] for item in items),
            "mean_judged_fraction_at_returned_depth": statistics.fmean(
                item["judged_fraction_at_returned_depth"] for item in items
            ),
            "mean_relevant_yield_per_100_reads": statistics.fmean(
                item["relevant_yield_per_100_reads"] for item in items
            ),
            "mean_qrels_bounded_residual_fraction": statistics.fmean(
                item["qrels_bounded_residual_fraction"] for item in items
            ),
            "mean_calibrated_unresolvedness_brier": statistics.fmean(
                item["calibrated_unresolvedness_brier"] for item in items
            ),
            "premature_task_closures": sum(bool(item["premature_task_closure"]) for item in items),
            "declared_task_closures": sum(bool(item["task_closure_declared"]) for item in items),
            "harmful_topics_vs_local_multiform_rrf": sum(
                item["recall_at_100_budget"]
                < by_key[(item["topic_id"], "LOCAL_MULTIFORM_RRF")]["recall_at_100_budget"]
                for item in items
            ),
            "tied_topics_vs_local_multiform_rrf": sum(
                item["recall_at_100_budget"]
                == by_key[(item["topic_id"], "LOCAL_MULTIFORM_RRF")]["recall_at_100_budget"]
                for item in items
            ),
        }

    primary_deltas = [
        by_key[(topic_id, "STRUCTURAL_JUMP")]["recall_at_100_budget"]
        - by_key[(topic_id, "IDEAL_DONOR_PRODUCT_RRF")]["recall_at_100_budget"]
        for topic_id in EXPECTED_TOPICS
    ]
    licensed_topics = [
        topic_id
        for topic_id in EXPECTED_TOPICS
        if by_key[(topic_id, "STRUCTURAL_JUMP")]["jump_licensed"]
    ]
    remote_deltas = [
        by_key[(topic_id, "STRUCTURAL_JUMP")]["recall_at_100_budget"]
        - by_key[(topic_id, "LOCAL_MULTIFORM_RRF")]["recall_at_100_budget"]
        for topic_id in licensed_topics
    ]
    return {
        "policy_summaries": summaries,
        "primary_contrast": bootstrap_mean_interval(primary_deltas, seed=BOOTSTRAP_SEED),
        "remote_jump_contrast_on_licensed_topics": bootstrap_mean_interval(
            remote_deltas, seed=BOOTSTRAP_SEED + 1
        ),
        "licensed_jump_topics": licensed_topics,
        "licensed_jump_topic_count": len(licensed_topics),
        "primary_harmful_topics": sum(delta < 0 for delta in primary_deltas),
        "primary_tied_topics": sum(delta == 0 for delta in primary_deltas),
        "primary_beneficial_topics": sum(delta > 0 for delta in primary_deltas),
        "remote_harmful_topics": sum(delta < 0 for delta in remote_deltas),
        "remote_tied_topics": sum(delta == 0 for delta in remote_deltas),
        "remote_beneficial_topics": sum(delta > 0 for delta in remote_deltas),
    }


def file_record(path: Path) -> dict[str, Any]:
    return {"path": path.name, "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--expected-freeze-sha256", required=True)
    parser.add_argument("--subject-sha", required=True)
    parser.add_argument("--freeze-commit", required=True)
    parser.add_argument("--implementation-sha", required=True)
    parser.add_argument("--source-archive-sha256", required=True)
    args = parser.parse_args()

    started = time.time()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    freeze_sha = sha256_file(args.freeze)
    if freeze_sha != args.expected_freeze_sha256:
        raise PreconditionError(
            f"freeze digest mismatch: expected {args.expected_freeze_sha256}, got {freeze_sha}"
        )
    freeze = json.loads(args.freeze.read_text(encoding="utf-8"))
    if freeze["job_id"] != JOB_ID or freeze["git"]["subject_sha"] != args.subject_sha:
        raise PreconditionError("freeze job or subject identity mismatch")
    frozen_copy = output_dir / "FREEZE_V1.json"
    if args.freeze.resolve() != frozen_copy:
        shutil.copyfile(args.freeze, frozen_copy)

    print("P2-DES-01 policy phase starting; qrels remain unopened", flush=True)
    documents, topics, public_manifest = load_public_inputs(args.data_root)
    index_started = time.time()
    index = Bm25Index(documents)
    index_seconds = time.time() - index_started
    print(
        f"indexed {index.count} documents, {len(index.postings)} terms in {index_seconds:.3f}s",
        flush=True,
    )
    policy_outputs = generate_policy_outputs(index, topics)
    pre_score_path = output_dir / "PRE_SCORE_POLICY_OUTPUTS_V1.json"
    write_json(pre_score_path, policy_outputs)
    pre_score_sha = sha256_file(pre_score_path)
    print(f"policy outputs frozen before qrels: {pre_score_sha}", flush=True)

    # Outcome access begins only after the complete policy artifact exists and
    # its digest has been recorded above.
    qrels, qrels_manifest = load_qrels_after_policy_hash(args.data_root)
    raw = evaluate(policy_outputs, qrels)
    raw_path = output_dir / "RAW_POLICY_OUTCOMES_V1.json"
    write_json(raw_path, raw)
    aggregate_result = aggregate(raw)

    hard_preconditions = [
        {"id": "HP1_INPUTS_PRESENT_AND_DIGESTED", "attained": True},
        {"id": "HP2_EXACT_50_FROZEN_TOPICS_NO_DROPS", "attained": True},
        {"id": "HP3_POLICY_OUTPUTS_HASHED_BEFORE_QRELS_OPEN", "attained": True},
        {"id": "HP4_NO_FORBIDDEN_LABEL_FIELDS_IN_POLICY_INPUT", "attained": True},
        {"id": "HP5_MATCHED_100_READ_AND_4_QUERY_MAXIMA", "attained": True},
        {
            "id": "HP6_MATERIAL_BIOMEDICAL_NEURAL_DONOR_BOUND",
            "attained": False,
            "reason": "No frozen model, tokenizer, weights, and revision were supplied; the internal lexical/PRF product is not substituted for this donor.",
        },
        {
            "id": "HP7_LICENSED_REVIEW_AND_REMINTED_TRANSFER_WORLDS_BOUND",
            "attained": False,
            "reason": "Neither an independently licensed review corpus nor an independent reminted cross-domain world with gold custody was supplied.",
        },
        {
            "id": "HP8_EXTERNAL_INDEPENDENT_GOLD_CUSTODY",
            "attained": False,
            "reason": "TREC-COVID qrels are public and evaluator access is same-session; this is not external independent custody.",
        },
    ]
    exact_terminal = "CANNOT_CHECK_STRONG_DONOR_OR_TRANSFER_BINDING_UNAVAILABLE"
    missing = [entry["id"] for entry in hard_preconditions if not entry["attained"]]
    result = {
        "schema": f"{SCHEMA_PREFIX}.primary-result.v1",
        "job_id": JOB_ID,
        "exact_terminal": exact_terminal,
        "terminal_reason": "The full positive is precluded by prospectively frozen unmet material-donor, transfer-world, and independent-custody hard preconditions. TREC-COVID internal rows remain scored and retained.",
        "aggregate": aggregate_result,
        "hard_preconditions": hard_preconditions,
        "unmet_hard_preconditions": missing,
        "denominators": {
            "frozen_topics": 50,
            "scored_topics": len(topics),
            "policies": len(POLICY_ORDER),
            "case_policy_rows_expected": 400,
            "case_policy_rows_retained": len(raw["case_policy_rows"]),
            "dropped_topics": 0,
            "dropped_case_policy_rows": 0,
            "crashed_case_policy_rows": 0,
        },
        "claim_ceiling": "Public TREC-COVID qrels-bounded internal comparison only; no full P2 superiority, global closure, transfer, external independence, or paper-authority claim.",
    }
    primary_path = output_dir / "PRIMARY_RESULT_V1.json"
    write_json(primary_path, result)

    ideal = {
        "schema": f"{SCHEMA_PREFIX}.ideal-donor-result.v1",
        "job_id": JOB_ID,
        "strongest_runnable_donor": "IDEAL_DONOR_PRODUCT_RRF",
        "composition": [
            "LOCAL_MULTIFORM_RRF",
            "DIVERSIFIED_ROUND_ROBIN",
            "ANALOGY_PRF",
        ],
        "composition_rule": "equal-weight RRF with k=60, frozen before outcomes",
        "result": aggregate_result["policy_summaries"]["IDEAL_DONOR_PRODUCT_RRF"],
        "material_donor": {
            "id": "BIOMEDICAL_NEURAL_HYBRID",
            "status": "CANNOT_CHECK_UNAVAILABLE_NOT_SUBSTITUTED",
            "proxy_substitution": false,
        },
        "oracle_selection_used": false,
        "claim_boundary": "The runnable product is an internal donor envelope and is not the missing material biomedical neural donor.",
    }
    ideal_path = output_dir / "IDEAL_DONOR_RESULT_V1.json"
    write_json(ideal_path, ideal)

    rows = raw["case_policy_rows"]
    controls = {
        "schema": f"{SCHEMA_PREFIX}.negative-controls.v1",
        "job_id": JOB_ID,
        "random_remote": aggregate_result["policy_summaries"]["RANDOM_REMOTE"],
        "local_saturation_stop": aggregate_result["policy_summaries"]["LOCAL_SATURATION_STOP"],
        "label_leakage_probe": {
            "status": "PASS_INTERNAL_CONFORMANCE",
            "forbidden_policy_visible_keys_found": [],
            "qrels_loaded_after_pre_score_artifact_sha256": pre_score_sha,
            "external_independence": false,
        },
        "adverse_and_null_retention": {
            "structural_jump_harmful_topics_vs_local": aggregate_result["policy_summaries"]["STRUCTURAL_JUMP"]["harmful_topics_vs_local_multiform_rrf"],
            "structural_jump_tied_topics_vs_local": aggregate_result["policy_summaries"]["STRUCTURAL_JUMP"]["tied_topics_vs_local_multiform_rrf"],
            "primary_harmful_topics": aggregate_result["primary_harmful_topics"],
            "primary_tied_topics": aggregate_result["primary_tied_topics"],
            "rows_retained": len(rows),
        },
    }
    controls_path = output_dir / "NEGATIVE_CONTROLS_V1.json"
    write_json(controls_path, controls)

    transfer = {
        "schema": f"{SCHEMA_PREFIX}.transfer-result.v1",
        "job_id": JOB_ID,
        "trec_covid_public_world": {
            "status": "SCORED_INTERNAL_PUBLIC_GOLD",
            "topics": 50,
        },
        "licensed_review_world": {
            "status": "CANNOT_CHECK",
            "reason": "No licensed corpus path, digest, task freeze, or gold custody was provided; no proxy was substituted.",
        },
        "reminted_cross_domain_world": {
            "status": "CANNOT_CHECK",
            "reason": "No independent remint, task freeze, or gold custody was provided; a same-corpus synthetic split was not substituted.",
        },
        "external_independence": "CANNOT_CHECK",
        "transfer_terminal": "CANNOT_CHECK_TRANSFER_WORLDS_UNAVAILABLE",
    }
    transfer_path = output_dir / "TRANSFER_RESULT_V1.json"
    write_json(transfer_path, transfer)

    elapsed = time.time() - started
    usage = resource.getrusage(resource.RUSAGE_SELF)
    resource_ledger = {
        "schema": f"{SCHEMA_PREFIX}.resource-ledger.v1",
        "job_id": JOB_ID,
        "slurm": {
            "job_id": os.environ.get("SLURM_JOB_ID", "NOT_IN_SLURM"),
            "job_name": os.environ.get("SLURM_JOB_NAME", "NOT_IN_SLURM"),
            "node": os.environ.get("SLURMD_NODENAME", socket.gethostname()),
            "cpus_per_task": int(os.environ.get("SLURM_CPUS_PER_TASK", "1")),
        },
        "runtime": {
            "wallclock_seconds": elapsed,
            "index_seconds": index_seconds,
            "user_cpu_seconds": usage.ru_utime,
            "system_cpu_seconds": usage.ru_stime,
            "max_rss_platform_units": usage.ru_maxrss,
            "python": sys.version,
            "platform": platform.platform(),
        },
        "frozen_maxima": {
            "candidate_reads_per_topic_policy": READ_BUDGET,
            "registered_queries_per_topic_policy": QUERY_BUDGET,
            "model_tokens": 0,
        },
        "observed": {
            "maximum_returned_depth": max(row["returned_depth"] for row in rows),
            "maximum_registered_query_calls": max(row["registered_query_calls"] for row in rows),
            "case_policy_rows": len(rows),
            "resource_cap_binding": false,
        },
        "censoring": {
            "status": "NOT_CENSORED",
            "timeouts_as_obstruction": false,
            "cap_hits_as_incapability": false,
        },
    }
    resource_path = output_dir / "RESOURCE_LEDGER_V1.json"
    write_json(resource_path, resource_ledger)

    raw_manifest = {
        "schema": f"{SCHEMA_PREFIX}.raw-manifest.v1",
        "job_id": JOB_ID,
        "input_bindings": {
            **public_manifest,
            **qrels_manifest,
            "qrels_opened_only_after_pre_score_policy_outputs_sha256": pre_score_sha,
        },
        "execution_bindings": {
            "subject_sha": args.subject_sha,
            "freeze_commit": args.freeze_commit,
            "implementation_sha": args.implementation_sha,
            "freeze_sha256": freeze_sha,
            "source_archive_sha256": args.source_archive_sha256,
        },
        "artifacts": [file_record(pre_score_path), file_record(raw_path)],
        "denominators": result["denominators"],
        "qrels_access_sequence": "PRE_SCORE_POLICY_OUTPUTS_V1.json written and hashed before qrels/test.tsv open",
    }
    manifest_path = output_dir / "RAW_MANIFEST_V1.json"
    write_json(manifest_path, raw_manifest)

    bound_paths = [
        pre_score_path,
        raw_path,
        primary_path,
        ideal_path,
        controls_path,
        resource_path,
        transfer_path,
        manifest_path,
    ]
    case_index = [
        {
            "topic_id": row["topic_id"],
            "policy_id": row["policy_id"],
            "status": row["status"],
            "recall_at_100_budget": row["recall_at_100_budget"],
            "premature_task_closure": row["premature_task_closure"],
            "qrels_bounded_residual_fraction": row["qrels_bounded_residual_fraction"],
        }
        for row in rows
    ]
    packet = {
        "schema": f"{SCHEMA_PREFIX}.result-binding-packet.v1",
        "job_id": JOB_ID,
        "git": {
            "subject_sha": args.subject_sha,
            "fresh_origin_main_sha": freeze["git"]["fresh_origin_main_sha"],
            "freeze_commit": args.freeze_commit,
            "implementation_head_sha": args.implementation_sha,
            "branch": freeze["git"]["branch"],
            "result_commit": "BOUND_AFTER_EXECUTION__NOT_SELF_REFERENTIAL",
        },
        "digests": {
            "freeze_sha256": freeze_sha,
            "source_archive_sha256": args.source_archive_sha256,
            "raw_sha256": sha256_file(raw_path),
            "artifacts": [file_record(path) for path in bound_paths],
        },
        "denominators": result["denominators"],
        "hard_precondition_attainment": hard_preconditions,
        "leakage_and_censoring": {
            "policy_label_leakage": "NOT_DETECTED_INTERNAL_CONFORMANCE",
            "qrels_access_after_policy_hash": true,
            "resource_censoring": "NOT_CENSORED",
        },
        "strongest_donor": {
            "runnable": "IDEAL_DONOR_PRODUCT_RRF",
            "material_biomedical_neural_hybrid": "CANNOT_CHECK_UNAVAILABLE_NOT_SUBSTITUTED",
        },
        "resource_vector": resource_ledger,
        "transfer": transfer,
        "case_level_outcomes": case_index,
        "exact_terminal": exact_terminal,
        "claim_ceiling": result["claim_ceiling"],
        "external_authority_state": "CANNOT_CHECK",
        "manuscript_writing_owner": "P1_P15_REWRITE_LANE",
        "computation_session_paper_authority_delta": "NONE",
    }
    packet_path = output_dir / "RESULT_BINDING_PACKET_V1.json"
    write_json(packet_path, packet)
    print(f"exact_terminal={exact_terminal}", flush=True)
    print("MANUSCRIPT_WRITING_OWNER = P1_P15_REWRITE_LANE", flush=True)
    print("COMPUTATION_SESSION_PAPER_AUTHORITY_DELTA = NONE", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except PreconditionError as error:
        print(f"CANNOT_CHECK_INPUT_BINDING_OR_PRECONDITION_FAILED: {error}", file=sys.stderr)
        raise SystemExit(3)
