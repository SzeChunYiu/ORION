#!/usr/bin/env python3
"""P2: ORION route/stopping against BM25 and an RRF hybrid on TREC-COVID.

Runs the arms through P2's own harness. ``BudgetedSession`` supplies the whole
metered surface -- route calls, reads, route stops, budget enforcement -- so
tool calls, candidate judgments and premature stopping are read off recorded
session events rather than counted by anything written here.

The topic -> route-probe mapping is the frozen artifact from PR #1178. Its
sha256 is verified before a single arm runs; a mismatch aborts. A mapping that
could be edited after a number is known would not be a freeze.

Two of the five routes are genuinely unavailable on this corpus and are
declared so in the freeze. ORION's plan computes
``complete = not saw_unavailable and not budget_exhausted``, so it is expected
to decline completeness here while the bm25 policy returns complete=True. That
contrast is the result, not a defect to engineer away.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from orion.study.p2.baselines import (  # noqa: E402
    BM25_B,
    BM25_K1,
    HashedDistributionalScorer,
    tokenize,
)
from orion.study.p2.cases import Budget, RouteAvailability  # noqa: E402
from orion.study.p2.corpus import DiscoveryRoute  # noqa: E402
from orion.study.p2.offline_systems import OfflineDiscoverySystem, Policy  # noqa: E402
from orion.study.p2.runner import PublicIndex, SessionConfig  # noqa: E402
from orion.study.p2.runner import BudgetedSession  # noqa: E402
from orion.study.p2.systems import RetrievedRecord  # noqa: E402

DATA = Path.home() / "orion-work/trec/trec-covid"
HERE = Path(__file__).resolve().parent
FREEZE = HERE / "P2_TREC_COVID_ROUTE_FREEZE_V2.json"
EXPECTED_FREEZE_SHA = "1b1fca4008c9ed54bc27feff658972fbb68d8c86d38db47e267f8d0ae45a7e56"

ARMS = [
    Policy(system_id="bm25", mode="bm25"),
    Policy(system_id="rrf_hybrid", mode="hybrid"),
    Policy(system_id="orion_strong_new", mode="strong_new"),
    Policy(system_id="orion_full", mode="full"),
]


class Bm25Index:
    """Same Okapi formula, tokenizer and IDF as orion.study.p2.baselines."""

    def __init__(self, docs: list[tuple[str, str]]) -> None:
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

    def search(self, text: str, depth: int) -> list[str]:
        scores: dict[int, float] = defaultdict(float)
        for term in dict.fromkeys(tokenize(text)):
            hits = self.postings.get(term)
            if not hits:
                continue
            idf = self.idf(term)
            for idx, freq in hits:
                norm = BM25_K1 * (1.0 - BM25_B + BM25_B * self.lengths[idx] / (self.avg or 1.0))
                scores[idx] += idf * (freq * (BM25_K1 + 1.0) / (freq + norm))
        ranked = sorted(scores.items(), key=lambda kv: (-kv[1], self.doc_ids[kv[0]]))
        return [self.doc_ids[i] for i, _ in ranked[:depth]]


def ndcg_at_k(ranking: list[str], rel: dict[str, int], k: int) -> float:
    dcg = sum((2 ** rel.get(d, 0) - 1) / math.log2(i + 2) for i, d in enumerate(ranking[:k]))
    ideal = sorted(rel.values(), reverse=True)[:k]
    idcg = sum((2 ** g - 1) / math.log2(i + 2) for i, g in enumerate(ideal))
    return (dcg / idcg) if idcg else 0.0


def recall_at_k(ranking: list[str], rel: dict[str, int], k: int) -> float:
    positives = {d for d, g in rel.items() if g > 0}
    return (len(positives & set(ranking[:k])) / len(positives)) if positives else 0.0


def main() -> int:
    if not FREEZE.is_file():
        print(f"P2_ARMS_CANNOT_CHECK: freeze missing at {FREEZE}")
        return 3
    body = FREEZE.read_bytes()
    got = hashlib.sha256(body).hexdigest()
    if got != EXPECTED_FREEZE_SHA:
        print(f"ABORT: freeze sha256 {got} != committed {EXPECTED_FREEZE_SHA}")
        return 4
    freeze = json.loads(body)
    print(f"freeze verified: {got[:16]}...  topics={freeze['topic_count']}")

    corpus_path = DATA / "corpus.jsonl"
    if not corpus_path.is_file():
        print(f"P2_ARMS_CANNOT_CHECK: corpus missing at {corpus_path}")
        return 3
    docs: list[tuple[str, str]] = []
    meta: dict[str, tuple[str, str]] = {}
    for line in corpus_path.open():
        row = json.loads(line)
        title, text = row.get("title", ""), row.get("text", "")
        docs.append((row["_id"], f"{title} {text}"))
        meta[row["_id"]] = (title, text)
    print(f"corpus documents: {len(docs)}")
    index = Bm25Index(docs)
    dense = HashedDistributionalScorer(docs)
    depth = freeze["posting_depth"]

    rels: dict[str, dict[str, int]] = defaultdict(dict)
    with (DATA / "qrels" / "test.tsv").open() as fh:
        next(fh)
        for line in fh:
            qid, did, score = line.split()
            rels[qid][did] = int(score)

    budget = Budget(**freeze["budget"])
    unavailable = tuple(
        RouteAvailability(route=DiscoveryRoute[name], goes_unavailable_after_calls=0)
        for name in sorted(freeze["unavailable_routes"])
    )

    def record_for(doc_id: str) -> RetrievedRecord:
        title, text = meta[doc_id]
        return RetrievedRecord(
            doc_id=doc_id,
            content_identity=doc_id,
            content_digest=hashlib.sha256(f"{title}{text}".encode()).hexdigest()[:32],
            version=1,
            title=title,
            abstract=text,
            venue="",
            year=0,
            authors=(),
            references=(),  # BEIR trec-covid ships no citation graph
        )

    results: dict = {
        "schema": "P2.TrecCovidArms.v1",
        "freeze_sha256": got,
        "budget": freeze["budget"],
        "unavailable_routes": freeze["unavailable_routes"],
        "per_topic": [],
    }

    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else 0
    selected = freeze["topics"][:limit] if limit else freeze["topics"]
    for topic in selected:
        qid = topic["topic"]
        probe_text = topic["probe_text"]
        wanted: set[str] = set()
        postings: list[tuple[str, str, tuple[str, ...]]] = []
        for route, probes in topic["routes"].items():
            for probe in probes:
                text = probe_text[probe]
                if route == "SEMANTIC":
                    qvec = dense.vectorize(text)
                    scored = sorted(
                        ((dense.score(d, qvec), d) for d, _ in docs), reverse=True
                    )[:depth]
                    hits = tuple(d for _, d in scored)
                else:
                    hits = tuple(index.search(text, depth))
                # PublicIndex.lookup matches key == probe exactly, and the
                # policy queries with the probe TEXT from view.route_probes.
                # Keying these on the probe NAME made every lookup miss and
                # every arm score 0.0000 while route calls still registered.
                postings.append((route, text, hits))
                wanted.update(hits)
        public = PublicIndex(
            records=tuple((d, record_for(d)) for d in sorted(wanted)),
            postings=tuple(postings),
        )
        config = SessionConfig(
            task_id=f"trec-covid-{qid}",
            availability=unavailable,
            budget=budget,
            extraction_questions=(probe_text["question"],),
            extraction_shift_after_reads=None,
        )
        rel = rels.get(qid, {})
        row: dict = {"topic": qid, "relevant_documents": sum(1 for g in rel.values() if g > 0),
                     "arms": {}}
        for policy in ARMS:
            session = BudgetedSession(public, config)
            system = OfflineDiscoverySystem(policy)
            view = _view_for(topic, budget)
            try:
                report = system.run(view, session, seed=0)
                note = report.notes if isinstance(report.notes, str) else "; ".join(report.notes)
                complete = report.task_closed_as_complete
            except Exception as exc:  # a policy that dies is recorded, not hidden
                note, complete = f"RAISED {type(exc).__name__}: {exc}", None
            # RouteEvent exposes retrieved_doc_ids; an earlier version of this
            # driver read a non-existent `records` attribute and silently
            # surfaced nothing, which showed up as every arm scoring 0.0000.
            surfaced: list[str] = []
            seen: set[str] = set()
            for event in session.route_events:
                for doc_id in event.retrieved_doc_ids:
                    if doc_id not in seen:
                        seen.add(doc_id)
                        surfaced.append(doc_id)
            route_detail = [
                {"route": e.route, "status": str(e.status), "docs": len(e.retrieved_doc_ids)}
                for e in session.route_events
            ]
            stop_detail = [
                {"scope": d.scope, "route": d.route_id, "reason": d.reason}
                for d in session.stop_decisions
            ]
            row["arms"][policy.system_id] = {
                "route_detail": route_detail,
                "stop_detail": stop_detail,
                "recall_at_100": round(recall_at_k(surfaced, rel, 100), 6),
                "ndcg_at_10": round(ndcg_at_k(surfaced, rel, 10), 6),
                "route_calls": len(session.route_events),
                "reads": len(session.read_events),
                "route_stops": len(session.stop_decisions),
                "declared_complete": complete,
                "candidates_surfaced": len(surfaced),
                "note": note,
            }
        results["per_topic"].append(row)
        print(f"  topic {qid:>2}: " + "  ".join(
            f"{k}={v['ndcg_at_10']:.3f}/c={v['declared_complete']}" for k, v in row["arms"].items()))

    def macro(arm: str, metric: str) -> float:
        vals = [t["arms"][arm][metric] for t in results["per_topic"]]
        return round(sum(vals) / len(vals), 6)

    results["arms_macro"] = {
        p.system_id: {
            "recall_at_100": macro(p.system_id, "recall_at_100"),
            "ndcg_at_10": macro(p.system_id, "ndcg_at_10"),
            "mean_route_calls": macro(p.system_id, "route_calls"),
            "mean_reads": macro(p.system_id, "reads"),
            "mean_route_stops": macro(p.system_id, "route_stops"),
            "declared_complete_topics": sum(
                1 for t in results["per_topic"] if t["arms"][p.system_id]["declared_complete"]
            ),
        }
        for p in ARMS
    }
    out = HERE / ("P2_TREC_COVID_ARMS_SMOKE.json" if limit else "P2_TREC_COVID_ARMS_V1.json")
    out.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    print("\narm                 recall@100  nDCG@10  routes  reads  stops  complete/50")
    for k, v in results["arms_macro"].items():
        print(f"{k:20s}{v['recall_at_100']:10.4f}{v['ndcg_at_10']:9.4f}"
              f"{v['mean_route_calls']:8.2f}{v['mean_reads']:7.2f}"
              f"{v['mean_route_stops']:7.2f}{v['declared_complete_topics']:9d}")
    print(f"wrote {out} ({out.stat().st_size} bytes)")
    return 0


def _view_for(topic: dict, budget: Budget):
    from orion.study.p2.cases import PublicView

    routes = tuple(sorted(topic["routes"]))
    probes = tuple(
        (route, tuple(topic["probe_text"][p] for p in probes))
        for route, probes in sorted(topic["routes"].items())
    )
    return PublicView(
        task_id=f"trec-covid-{topic['topic']}",
        question=topic["probe_text"]["question"],
        initial_extraction_question=topic["probe_text"]["question"],
        available_routes=routes,
        route_probes=probes,
        budget=budget,
    )


if __name__ == "__main__":
    raise SystemExit(main())
