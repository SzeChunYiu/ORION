#!/usr/bin/env python3
"""Gold-blind OpenAlex acquisition successor for the frozen P2 development tasks."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from orion.study.p2.arb_runtime import (
    derive_current_vocabulary_query,
    derive_lexical_variant_query,
)
from orion.study.p2.arb_scoring import normalize_arxiv_id

SCHEMA = "orion.p2.openalex-public-successor.v1"
USER_AGENT = "ORION-P2-open-data-successor/0.1 (+https://github.com/SzeChunYiu/ORION)"
ARXIV = re.compile(r"(?:arxiv\.org/(?:abs|pdf)/|arXiv:)?([^/?#]+)", re.I)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")


def prepare(bundle: Path, public: Path, gold: Path, manifest: Path) -> None:
    bundle_hash = sha256(bundle)
    if bundle_hash != "db1839438033a32dd7d76913575d4b76f144d5e442aaac29be4eda32326392c6":
        raise ValueError(f"unexpected decrypted bundle sha256: {bundle_hash}")
    wide = [row for row in read_jsonl(bundle) if row.get("type") == "wide"]
    if len(wide) != 400:
        raise ValueError(f"expected 400 Wide rows, got {len(wide)}")
    public_rows: list[dict[str, Any]] = []
    gold_rows: list[dict[str, Any]] = []
    for index, row in enumerate(wide, 1):
        task_id = f"arb-wide-{index:04d}"
        question = str(row.get("question", "")).strip()
        ids = sorted({normalize_arxiv_id(str(x)) for x in row.get("arxiv_id", []) if str(x).strip()})
        ids = [x for x in ids if x]
        if not question or not ids:
            raise ValueError(f"{task_id} lacks public question or gold arXiv identity")
        public_rows.append({"task_id": task_id, "question": question})
        gold_rows.append({"task_id": task_id, "gold_arxiv_ids": ids})
    write_jsonl(public, public_rows)
    write_jsonl(gold, gold_rows)
    receipt = {
        "schema_version": SCHEMA,
        "stage": "gold_separation",
        "bundle_sha256": bundle_hash,
        "wide_rows": 400,
        "public_sha256": sha256(public),
        "gold_sha256": sha256(gold),
        "hidden_gold_fields_in_public": [],
    }
    manifest.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def arxiv_id(work: dict[str, Any]) -> str | None:
    raw = str((work.get("ids") or {}).get("arxiv", "") or "").strip()
    if raw:
        match = ARXIV.search(raw)
        value = normalize_arxiv_id(match.group(1) if match else raw)
        return value or None
    doi = str(work.get("doi", "") or (work.get("ids") or {}).get("doi", "") or "").strip()
    match = re.search(r"10\.48550/arxiv\.([^?#]+)", doi, re.I)
    if not match:
        return None
    value = normalize_arxiv_id(match.group(1))
    return value or None


def safe_raw_query(question: str, limit: int = 180) -> str:
    """Return a complete-word prefix within OpenAlex's accepted search length."""

    if len(question) <= limit:
        return question
    prefix = question[: limit + 1]
    return prefix.rsplit(" ", 1)[0].strip()


def fetch(query: str, protocol: dict[str, Any], last_request: list[float]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    provider = protocol["provider"]
    params = {
        "search": query,
        "per-page": int(provider["per_page"]),
        "select": ",".join(provider["selected_fields"]),
    }
    url = provider["endpoint"] + "?" + urllib.parse.urlencode(params)
    retry_statuses = set(provider["retry_statuses"])
    attempts: list[dict[str, Any]] = []
    for attempt in range(1, int(provider["maximum_attempts_per_call"]) + 1):
        delay = float(provider["minimum_inter_request_seconds"]) - (time.monotonic() - last_request[0])
        if delay > 0:
            time.sleep(delay)
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        started = time.monotonic()
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                body = response.read()
                status = int(response.status)
        except urllib.error.HTTPError as exc:
            status, body = int(exc.code), exc.read()
        except (urllib.error.URLError, TimeoutError) as exc:
            status, body = 0, repr(exc).encode()
        last_request[0] = time.monotonic()
        attempts.append({
            "attempt": attempt,
            "http_status": status,
            "duration_seconds": round(time.monotonic() - started, 4),
            "body_sha256": hashlib.sha256(body).hexdigest(),
            "bytes": len(body),
        })
        if status == 200:
            payload = json.loads(body)
            return payload, attempts
        if status not in retry_statuses:
            break
        time.sleep(min(8.0, 2.0 ** attempt))
    return {"results": []}, attempts


def unique_ids(works: list[dict[str, Any]]) -> list[str]:
    return list(dict.fromkeys(x for work in works if (x := arxiv_id(work))))


def rrf(groups: list[list[str]], cap: int = 20, k: int = 60) -> list[str]:
    scores: Counter[str] = Counter()
    first: dict[str, tuple[int, int]] = {}
    for qi, group in enumerate(groups):
        for ri, item in enumerate(group, 1):
            scores[item] += 1.0 / (k + ri)
            first.setdefault(item, (qi, ri))
    return sorted(scores, key=lambda x: (-scores[x], first[x], x))[:cap]


def run(public: Path, protocol_path: Path, trace_path: Path, candidate_path: Path) -> None:
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    wanted = protocol["task_selection"]["task_ids"]
    visible = {row["task_id"]: row for row in read_jsonl(public)}
    if any(task_id not in visible for task_id in wanted):
        raise ValueError("frozen task identity missing from public split")
    last_request = [0.0]
    traces: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    for index, task_id in enumerate(wanted, 1):
        question = " ".join(visible[task_id]["question"].split())
        query_rows = [
            ("Q0_SAFE_RAW", safe_raw_query(question, 180)),
            ("Q1_CURRENT", derive_current_vocabulary_query(question, limit=6).query),
            ("Q2_VARIANT", derive_lexical_variant_query(question, limit=8).query),
        ]
        groups: list[list[str]] = []
        calls: list[dict[str, Any]] = []
        for query_id, query in query_rows:
            payload, attempts = fetch(query, protocol, last_request)
            works = list(payload.get("results") or [])
            ids = unique_ids(works)
            groups.append(ids)
            calls.append({
                "query_id": query_id,
                "query": query,
                "attempts": attempts,
                "result_count": len(works),
                "arxiv_identity_count": len(ids),
                "arxiv_ids": ids,
                "works": [
                    {"openalex_id": w.get("id"), "arxiv_id": arxiv_id(w), "doi": w.get("doi"),
                     "title": w.get("title"), "publication_year": w.get("publication_year")}
                    for w in works
                ],
            })
        arms = {
            "B0_RAW": groups[0][:20],
            "B1_CURRENT": groups[1][:20],
            "S1_RRF3": rrf(groups, 20),
        }
        traces.append({"task_id": task_id, "calls": calls})
        candidates.append({"task_id": task_id, "arms": arms})
        print(f"P2_OPENALEX {index}/{len(wanted)} task={task_id}", flush=True)
    trace_path.write_text(json.dumps({"schema_version": SCHEMA, "tasks": traces}, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    write_jsonl(candidate_path, candidates)


def replay(source_trace: Path, protocol_path: Path, candidate_path: Path) -> None:
    """Recover admitted successful response bytes through the V2 identity bridge."""

    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    expected = protocol["source_trace"]["sha256"]
    if sha256(source_trace) != expected:
        raise ValueError("source trace hash does not match the V3 replay freeze")
    admitted = protocol["source_trace"]["admitted_queries"]
    trace = json.loads(source_trace.read_text(encoding="utf-8"))
    candidates: list[dict[str, Any]] = []
    admitted_calls = 0
    for task in trace["tasks"]:
        by_query = {call["query_id"]: call for call in task["calls"]}
        groups: list[list[str]] = []
        for query_id in admitted:
            call = by_query[query_id]
            if call["attempts"][-1]["http_status"] != 200:
                raise ValueError(f"{task['task_id']}:{query_id} is not an admitted HTTP-200 call")
            admitted_calls += 1
            groups.append(list(dict.fromkeys(x for work in call["works"] if (x := arxiv_id(work)))))
        candidates.append({
            "task_id": task["task_id"],
            "arms": {
                "B0_RAW": groups[0][:20],
                "B1_CURRENT": groups[1][:20],
                "S1_RRF3": rrf(groups, 20),
            },
        })
    if admitted_calls != int(protocol["source_trace"]["required_final_http_200_calls"]):
        raise ValueError(f"expected 48 admitted calls, got {admitted_calls}")
    write_jsonl(candidate_path, candidates)


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def bootstrap_delta(a: list[float], b: list[float], seed: int, n: int) -> list[float]:
    rng = random.Random(seed)
    size = len(a)
    out = []
    for _ in range(n):
        idx = [rng.randrange(size) for _ in range(size)]
        out.append(mean([a[i] - b[i] for i in idx]))
    return sorted(out)


def quantile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    x = (len(values) - 1) * p
    lo, hi = math.floor(x), math.ceil(x)
    return values[lo] if lo == hi else values[lo] * (hi - x) + values[hi] * (x - lo)


def sign_p(a: list[float], b: list[float]) -> float:
    wins = sum(x > y for x, y in zip(a, b))
    losses = sum(x < y for x, y in zip(a, b))
    n = wins + losses
    if n == 0:
        return 1.0
    k = min(wins, losses)
    return min(1.0, 2.0 * sum(math.comb(n, i) for i in range(k + 1)) / (2 ** n))


def score(gold_path: Path, candidates_path: Path, trace_path: Path, protocol_path: Path, out: Path) -> None:
    gold = {row["task_id"]: set(row["gold_arxiv_ids"]) for row in read_jsonl(gold_path)}
    rows = read_jsonl(candidates_path)
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    arms = ["B0_RAW", "B1_CURRENT", "S1_RRF3"]
    per_task: list[dict[str, Any]] = []
    metric: dict[str, dict[str, list[float]]] = {arm: {"recall": [], "precision": [], "iou": []} for arm in arms}
    for row in rows:
        target = gold[row["task_id"]]
        scores: dict[str, Any] = {}
        for arm in arms:
            predicted = set(row["arms"][arm])
            hit = len(target & predicted)
            recall = hit / len(target)
            precision = hit / len(predicted) if predicted else 0.0
            union = len(target | predicted)
            iou = hit / union if union else 0.0
            metric[arm]["recall"].append(recall)
            metric[arm]["precision"].append(precision)
            metric[arm]["iou"].append(iou)
            scores[arm] = {"gold_count": len(target), "predicted_count": len(predicted), "hit_count": hit,
                           "recall": recall, "precision": precision, "iou": iou}
        per_task.append({"task_id": row["task_id"], "scores": scores})
    aggregate = {
        arm: {
            "mean_recall": mean(metric[arm]["recall"]),
            "mean_precision": mean(metric[arm]["precision"]),
            "mean_iou": mean(metric[arm]["iou"]),
            "tasks_with_any_gold_hit": sum(x > 0 for x in metric[arm]["recall"]),
        }
        for arm in arms
    }
    strongest = max(("B0_RAW", "B1_CURRENT"), key=lambda arm: aggregate[arm]["mean_recall"])
    deltas = bootstrap_delta(metric["S1_RRF3"]["recall"], metric[strongest]["recall"],
                             int(protocol["statistics"]["paired_bootstrap_seed"]),
                             int(protocol["statistics"]["paired_bootstrap_resamples"]))
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    admitted_queries = set((protocol.get("source_trace") or {}).get("admitted_queries") or [])
    statuses = [
        attempt["http_status"]
        for task in trace["tasks"]
        for call in task["calls"]
        if not admitted_queries or call["query_id"] in admitted_queries
        for attempt in call["attempts"][-1:]
    ]
    required_transport_calls = int(
        (protocol.get("source_trace") or {}).get("required_final_http_200_calls", 72)
    )
    gates = {
        "G1_TRANSPORT": len(statuses) == required_transport_calls and all(x == 200 for x in statuses),
        "G2_EMISSION": aggregate["S1_RRF3"]["tasks_with_any_gold_hit"] >= 12 and aggregate["S1_RRF3"]["mean_recall"] >= 0.20,
        "G3_FUSION": aggregate["S1_RRF3"]["mean_recall"] - aggregate[strongest]["mean_recall"] >= 0.05 and quantile(deltas, 0.025) > 0,
        "G4_NO_PRECISION_COLLAPSE": aggregate["S1_RRF3"]["mean_precision"] >= aggregate[strongest]["mean_precision"] - 0.02,
    }
    if not gates["G1_TRANSPORT"]:
        terminal = protocol["cannot_check_terminal"]
    elif all(gates.values()):
        terminal = protocol["positive_terminal"]
    else:
        terminal = protocol["negative_successor_terminal"]
    result = {
        "schema_version": SCHEMA,
        "claim_scope": protocol["claim_scope"],
        "terminal": terminal,
        "aggregate": aggregate,
        "strongest_single_view": strongest,
        "s1_minus_strongest": {
            "mean_recall_delta": aggregate["S1_RRF3"]["mean_recall"] - aggregate[strongest]["mean_recall"],
            "bootstrap_95_ci": [quantile(deltas, 0.025), quantile(deltas, 0.975)],
            "exact_two_sided_sign_p": sign_p(metric["S1_RRF3"]["recall"], metric[strongest]["recall"]),
        },
        "gates": gates,
        "transport_final_status_counts": dict(Counter(statuses)),
        "task_count": len(rows),
        "per_task": per_task,
        "receipts": {"protocol_sha256": sha256(protocol_path), "gold_sha256": sha256(gold_path),
                     "candidate_sha256": sha256(candidates_path), "trace_sha256": sha256(trace_path),
                     "script_sha256": sha256(Path(__file__))},
        "forbidden_claims": protocol["forbidden_claims"],
    }
    out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--bundle", type=Path, required=True); p.add_argument("--public", type=Path, required=True)
    p.add_argument("--gold", type=Path, required=True); p.add_argument("--manifest", type=Path, required=True)
    r = sub.add_parser("run")
    r.add_argument("--public", type=Path, required=True); r.add_argument("--protocol", type=Path, required=True)
    r.add_argument("--trace", type=Path, required=True); r.add_argument("--candidates", type=Path, required=True)
    v = sub.add_parser("replay")
    v.add_argument("--source-trace", type=Path, required=True); v.add_argument("--protocol", type=Path, required=True)
    v.add_argument("--candidates", type=Path, required=True)
    s = sub.add_parser("score")
    s.add_argument("--gold", type=Path, required=True); s.add_argument("--candidates", type=Path, required=True)
    s.add_argument("--trace", type=Path, required=True); s.add_argument("--protocol", type=Path, required=True)
    s.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "prepare": prepare(args.bundle, args.public, args.gold, args.manifest)
    elif args.command == "run": run(args.public, args.protocol, args.trace, args.candidates)
    elif args.command == "replay": replay(args.source_trace, args.protocol, args.candidates)
    else: score(args.gold, args.candidates, args.trace, args.protocol, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
