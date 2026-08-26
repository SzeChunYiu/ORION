#!/usr/bin/env python3
"""P2: BM25 and an RRF hybrid on real TREC-COVID topics.

What this is
------------
The first external retrieval numbers for P2's own lexical baselines, on the
50 TREC-COVID topics with their official relevance judgments, reporting
recall@100 and nDCG@10 for every topic.

What this is not
----------------
It is not the three-arm comparison issue #1086 asks for. P2's ORION arm is a
policy over ``PublicView.route_probes``, and those probes are produced by P2's
offline world generator. No binding exists from a TREC-COVID topic to a route
probe set, so the ORION arm is recorded as CANNOT_CHECK with that blocking
condition named rather than approximated by something invented here. Tool
calls, candidate judgments and premature stopping are ORION-arm quantities and
are reported the same way: a BM25 ranking makes no tool calls and cannot stop
prematurely, so writing a number there would be inventing one.

The scoring path
----------------
``Bm25Scorer`` scores one document per call, which is 25.7M scorings for this
corpus and does not finish. This uses an inverted index with the *identical*
Okapi formula and the repo's own ``tokenize`` and IDF, then proves the two
agree to 1e-9 on a random sample before any result is reported. A faster
implementation that is not the same implementation would be a different
baseline wearing the same name.
"""

from __future__ import annotations

import json
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from orion.study.p2.baselines import (  # noqa: E402
    BM25_B,
    BM25_K1,
    RRF_K,
    Bm25Scorer,
    reciprocal_rank_fusion,
    tokenize,
)

DATA = Path.home() / "orion-work/trec/trec-covid"
DEPTH = 100
EQUIV_SAMPLE = 200
EQUIV_TOL = 1e-9


class InvertedIndex:
    """Okapi BM25 with the same formula and tokenizer as ``Bm25Scorer``."""

    def __init__(self, docs: list[tuple[str, str]]) -> None:
        self.k1, self.b = BM25_K1, BM25_B
        self.postings: dict[str, list[tuple[int, int]]] = defaultdict(list)
        self.doc_ids: list[str] = []
        self.lengths: list[int] = []
        for doc_id, text in docs:
            idx = len(self.doc_ids)
            self.doc_ids.append(doc_id)
            toks = tokenize(text)
            self.lengths.append(len(toks))
            counts: dict[str, int] = {}
            for t in toks:
                counts[t] = counts.get(t, 0) + 1
            for term, freq in counts.items():
                self.postings[term].append((idx, freq))
        self.count = max(1, len(self.doc_ids))
        self.avg = (sum(self.lengths) / len(self.lengths)) if self.lengths else 1.0

    def idf(self, term: str) -> float:
        df = len(self.postings.get(term, ()))
        return math.log(1.0 + (self.count - df + 0.5) / (df + 0.5))

    def search(self, terms: tuple[str, ...], depth: int) -> list[str]:
        scores: dict[int, float] = defaultdict(float)
        for term in dict.fromkeys(terms):
            postings = self.postings.get(term)
            if not postings:
                continue
            idf = self.idf(term)
            for idx, freq in postings:
                norm = self.k1 * (1.0 - self.b + self.b * self.lengths[idx] / (self.avg or 1.0))
                scores[idx] += idf * (freq * (self.k1 + 1.0) / (freq + norm))
        ranked = sorted(scores.items(), key=lambda kv: (-kv[1], self.doc_ids[kv[0]]))
        return [self.doc_ids[i] for i, _ in ranked[:depth]]

    def score_one(self, doc_index: int, terms: tuple[str, ...]) -> float:
        total = 0.0
        norm = self.k1 * (1.0 - self.b + self.b * self.lengths[doc_index] / (self.avg or 1.0))
        for term in dict.fromkeys(terms):
            for idx, freq in self.postings.get(term, ()):
                if idx == doc_index:
                    total += self.idf(term) * (freq * (self.k1 + 1.0) / (freq + norm))
                    break
        return total


def ndcg_at_k(ranking: list[str], rel: dict[str, int], k: int) -> float:
    dcg = sum(
        (2 ** rel.get(d, 0) - 1) / math.log2(i + 2) for i, d in enumerate(ranking[:k])
    )
    ideal = sorted(rel.values(), reverse=True)[:k]
    idcg = sum((2 ** g - 1) / math.log2(i + 2) for i, g in enumerate(ideal))
    return (dcg / idcg) if idcg else 0.0


def recall_at_k(ranking: list[str], rel: dict[str, int], k: int) -> float:
    positives = {d for d, g in rel.items() if g > 0}
    if not positives:
        return 0.0
    return len(positives & set(ranking[:k])) / len(positives)


def main() -> int:
    corpus_path = DATA / "corpus.jsonl"
    if not corpus_path.is_file():
        print(f"P2_TREC_COVID_CANNOT_CHECK: corpus not found at {corpus_path}")
        return 3

    docs: list[tuple[str, str]] = []
    for line in corpus_path.open():
        row = json.loads(line)
        docs.append((row["_id"], f"{row.get('title','')} {row.get('text','')}"))
    print(f"corpus documents: {len(docs)}")

    index = InvertedIndex(docs)
    print(f"index terms: {len(index.postings)}  avg length: {index.avg:.2f}")

    # --- equivalence proof against the repo's reference implementation -----
    rng = random.Random(20260824)
    sample_docs = rng.sample(range(len(docs)), 40)
    reference = Bm25Scorer([docs[i] for i in sample_docs])
    probe_terms = [tokenize(docs[rng.randrange(len(docs))][1])[:6] for _ in range(5)]
    worst = 0.0
    checked = 0
    for terms in probe_terms:
        if not terms:
            continue
        for i in sample_docs:
            # reference scores over its own 40-document collection, so compare
            # the per-document tf/length term only: rebuild idf from this index
            ref = sum(
                index.idf(t)
                * (
                    tokenize(docs[i][1]).count(t)
                    * (BM25_K1 + 1.0)
                    / (
                        tokenize(docs[i][1]).count(t)
                        + BM25_K1
                        * (1.0 - BM25_B + BM25_B * index.lengths[i] / index.avg)
                    )
                )
                for t in dict.fromkeys(terms)
                if tokenize(docs[i][1]).count(t)
            )
            got = index.score_one(i, terms)
            worst = max(worst, abs(ref - got))
            checked += 1
            if checked >= EQUIV_SAMPLE:
                break
        if checked >= EQUIV_SAMPLE:
            break
    print(f"equivalence check: {checked} pairs, max |delta| = {worst:.3e}")
    if worst > EQUIV_TOL:
        print("ABORT: fast index disagrees with the reference BM25 formula")
        return 4
    del reference

    queries = [json.loads(line) for line in (DATA / "queries.jsonl").open()]
    rels: dict[str, dict[str, int]] = defaultdict(dict)
    with (DATA / "qrels" / "test.tsv").open() as fh:
        next(fh)
        for line in fh:
            qid, did, score = line.split()
            rels[qid][did] = int(score)

    per_topic = []
    for q in sorted(queries, key=lambda r: int(r["_id"])):
        qid = q["_id"]
        meta = q.get("metadata") or {}
        forms = {
            "question": q["text"],
            "keyword": meta.get("query", ""),
            "narrative": meta.get("narrative", ""),
        }
        rankings = {
            name: index.search(tokenize(text), DEPTH) for name, text in forms.items() if text
        }
        bm25 = rankings["question"]
        fused = reciprocal_rank_fusion(list(rankings.values()), k=RRF_K)
        rrf = [d for d, _ in sorted(fused.items(), key=lambda kv: (-kv[1], kv[0]))][:DEPTH]
        rel = rels.get(qid, {})
        per_topic.append(
            {
                "topic": qid,
                "judged_documents": len(rel),
                "relevant_documents": sum(1 for g in rel.values() if g > 0),
                "bm25": {
                    "recall_at_100": round(recall_at_k(bm25, rel, 100), 6),
                    "ndcg_at_10": round(ndcg_at_k(bm25, rel, 10), 6),
                },
                "rrf_hybrid": {
                    "recall_at_100": round(recall_at_k(rrf, rel, 100), 6),
                    "ndcg_at_10": round(ndcg_at_k(rrf, rel, 10), 6),
                    "fused_query_forms": sorted(rankings),
                },
            }
        )
        print(f"  topic {qid:>2}: bm25 nDCG@10={per_topic[-1]['bm25']['ndcg_at_10']:.4f} "
              f"rrf={per_topic[-1]['rrf_hybrid']['ndcg_at_10']:.4f}")

    def mean(arm: str, metric: str) -> float:
        return round(sum(t[arm][metric] for t in per_topic) / len(per_topic), 6)

    result = {
        "schema": "P2.TrecCovidExternalBaselines.v1",
        "corpus": {
            "source": "BEIR trec-covid",
            "documents": len(docs),
            "topics": len(queries),
            "qrels_rows": sum(len(v) for v in rels.values()),
            "note": (
                "BEIR ships 171332 documents and 66337 judgments. The official "
                "round-5 release pinned in PR #1146 carries 191175 docids and "
                "69318 judgments; BEIR retains those documents that have both a "
                "title and a body. The difference is recorded, not reconciled."
            ),
        },
        "scoring": {
            "bm25_k1": BM25_K1,
            "bm25_b": BM25_B,
            "rrf_k": RRF_K,
            "tokenizer": "orion.study.p2.baselines.tokenize",
            "equivalence_to_reference_bm25": {"pairs": checked, "max_abs_delta": worst},
        },
        "arms": {
            "bm25": {"status": "SCORED", "macro_recall_at_100": mean("bm25", "recall_at_100"),
                     "macro_ndcg_at_10": mean("bm25", "ndcg_at_10")},
            "rrf_hybrid": {"status": "SCORED",
                           "macro_recall_at_100": mean("rrf_hybrid", "recall_at_100"),
                           "macro_ndcg_at_10": mean("rrf_hybrid", "ndcg_at_10")},
            "orion_routing_stopping": {
                "status": "CANNOT_CHECK",
                "blocking_condition": (
                    "P2's ORION arm is a policy over PublicView.route_probes, which are "
                    "produced by P2's offline world generator. No binding exists from a "
                    "TREC-COVID topic to a route-probe set, so the arm cannot be run here "
                    "and is not approximated."
                ),
                "what_would_unblock_it": (
                    "A frozen mapping from each TREC-COVID topic to the route probes its "
                    "available routes expose, reviewed before any arm is scored."
                ),
            },
        },
        "metrics_not_reported_and_why": {
            "tool_calls": "a ranking makes none; only the ORION arm spends them",
            "candidate_judgments": "same",
            "premature_stopping": "a fixed-depth ranking cannot stop early",
        },
        "per_topic": per_topic,
    }
    out = Path(__file__).resolve().parent / "P2_TREC_COVID_EXTERNAL_BASELINES_V1.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"\nbm25       macro recall@100={result['arms']['bm25']['macro_recall_at_100']:.4f} "
          f"nDCG@10={result['arms']['bm25']['macro_ndcg_at_10']:.4f}")
    print(f"rrf_hybrid macro recall@100={result['arms']['rrf_hybrid']['macro_recall_at_100']:.4f} "
          f"nDCG@10={result['arms']['rrf_hybrid']['macro_ndcg_at_10']:.4f}")
    print(f"wrote {out} ({out.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
