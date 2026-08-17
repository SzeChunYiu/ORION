#!/usr/bin/env python3
"""Gold-blind keyless AutoResearchBench Wide candidate runner.

The host ``prepare`` command is the only command allowed to read the decrypted
benchmark record. It splits Wide records into a public candidate file containing
only task id + question and an evaluator-only GT file. ``run`` accepts only the
public file and searches the public arXiv API under ORION's canonical rate gate.
The resulting JSONL matches the pinned AutoResearchBench Wide scorer contract.

This runner is deliberately modest: it is a credential-free external probe, not
a replacement for the full multi-provider live campaign. Its value is that it
turns the Wide evaluator from an access audit into a real, reproducible official
score without leaking gold into candidate custody.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from orion.knowledge.providers.arxiv import ArxivClient, FetchStatus, TransportResponse
from orion.knowledge.rate import RateGate

PINNED_AUTORESEARCHBENCH_COMMIT = "a46c9bfb8968786f73f0a6a5b365b5384cd0f96d"
ARXIV_ID = re.compile(r"(\d{4}\.\d{4,5})")
TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9-]{3,}")
HIDDEN_KEYS = frozenset({"answer", "arxiv_id", "ground_truth", "gold", "target"})

# Generic instruction/research vocabulary is deliberately suppressed so the
# keyless query is driven by topical terms in the public question rather than by
# benchmark boilerplate. Nothing here is learned from benchmark labels.
STOPWORDS = frozenset(
    """
    about against along also among answer around based because been before being
    benchmark benchmarks between both camera cameras compare compared compares
    comparison comparisons condition conditions could dataset datasets directly
    does during each evaluate evaluated evaluates evaluation evaluations example
    examples explicitly find finding following from ground include includes including
    into looking methods model models network networks only other paper papers primarily
    propose proposes proposed research specifically standard strong study studies such
    target targets task tasks that their them then these they this those through using
    uses used what when where which while with work works years roughly results report
    reports reported should would whose within without approach approaches method system
    systems architecture architectures objective objectives experiment experiments
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
                raise ValueError(f"{path}:{line_number}: record must be an object")
            records.append(value)
    return records


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def _hidden_paths(value: Any, prefix: str = "$") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            child = f"{prefix}.{key}"
            if str(key).lower() in HIDDEN_KEYS:
                found.append(child)
            found.extend(_hidden_paths(item, child))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found.extend(_hidden_paths(item, f"{prefix}[{index}]"))
    return found


def prepare(full_path: Path, public_path: Path, gt_path: Path) -> dict[str, Any]:
    """Split decrypted benchmark records before the candidate process sees them."""

    full = _jsonl(full_path)
    public: list[dict[str, Any]] = []
    gt: list[dict[str, Any]] = []
    seen_questions: set[str] = set()
    for record in full:
        # Wide records have a list of target arXiv ids; Deep has one string id.
        raw_ids = record.get("arxiv_id")
        if not isinstance(raw_ids, list):
            continue
        question = str(record.get("question") or "").strip()
        if not question or question in seen_questions:
            raise ValueError("Wide benchmark contains an empty or duplicate question")
        normalized_ids = []
        for value in raw_ids:
            match = ARXIV_ID.search(str(value))
            if match:
                normalized_ids.append(match.group(1))
        if not normalized_ids:
            raise ValueError("Wide benchmark record has no usable arXiv id")
        task_id = f"arb-wide-{len(public) + 1:04d}"
        public.append({"task_id": task_id, "question": question})
        gt.append({"question": question, "arxiv_id": list(dict.fromkeys(normalized_ids))})
        seen_questions.add(question)

    if len(public) != 400:
        raise ValueError(f"expected 400 Wide records at pinned release, got {len(public)}")
    leaked = [path for item in public for path in _hidden_paths(item)]
    if leaked:
        raise AssertionError("hidden labels crossed candidate boundary: " + ",".join(leaked[:5]))
    _write_jsonl(public_path, public)
    _write_jsonl(gt_path, gt)
    return {
        "schema_version": "orion.p2.autoresearchbench-wide-split.v1",
        "pinned_upstream_commit": PINNED_AUTORESEARCHBENCH_COMMIT,
        "wide_tasks": len(public),
        "candidate_hidden_label_paths": leaked,
        "public_sha256": _sha256(public_path),
        "gt_sha256": _sha256(gt_path),
    }


def _salient_tokens(question: str, *, count: int = 5) -> list[str]:
    tokens: list[tuple[int, int, str]] = []
    seen: set[str] = set()
    for position, raw in enumerate(TOKEN.findall(question)):
        token = raw.lower().strip("-")
        if token in STOPWORDS or token in seen:
            continue
        if token.isdigit() or len(token) < 4:
            continue
        seen.add(token)
        # Prefer distinctive morphology/acronyms/long terms while retaining a
        # small position prior so the question's main topic is not discarded.
        score = len(token)
        if "-" in raw:
            score += 3
        if raw.isupper() and len(raw) >= 4:
            score += 4
        score += max(0, 5 - position // 12)
        tokens.append((score, -position, token))
    tokens.sort(reverse=True)
    return [token for _, _, token in tokens[:count]]


def derive_query(question: str) -> str:
    """Derive one deterministic arXiv query from public question text only."""

    terms = _salient_tokens(question)
    if len(terms) < 2:
        raise ValueError("could not derive at least two topical terms")
    # Three pairwise conjunctions are ORed in one provider request. This keeps
    # the public-request budget to one call/task while being less brittle than
    # requiring every selected term to occur in the same arXiv metadata record.
    pairs: list[str] = []
    for left, right in zip(terms[:4], terms[1:4], strict=False):
        pairs.append(f"(all:{left} AND all:{right})")
    return " OR ".join(pairs)


def _transport(url: str) -> TransportResponse:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "ORION-P2-AutoResearchBench/0.1 (+https://github.com/SzeChunYiu/ORION)",
            "Accept": "application/atom+xml",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:  # noqa: S310 - pinned public provider
            return TransportResponse(
                status=int(response.status),
                body=response.read().decode("utf-8", errors="replace"),
                headers={key: value for key, value in response.headers.items()},
            )
    except urllib.error.HTTPError as error:
        return TransportResponse(
            status=int(error.code),
            body=error.read().decode("utf-8", errors="replace"),
            headers={key: value for key, value in error.headers.items()},
        )


def _normalize_id(value: str) -> str:
    match = ARXIV_ID.search(value)
    return match.group(1) if match else ""


def run_candidate(
    public_path: Path,
    output_path: Path,
    trace_path: Path,
    *,
    max_results: int,
    limit: int | None,
) -> dict[str, Any]:
    """Run the candidate lane; this function cannot accept or discover a GT path."""

    records = _jsonl(public_path)
    if limit is not None:
        records = records[:limit]
    for record in records:
        leaked = _hidden_paths(record)
        if leaked:
            raise AssertionError("candidate input contains hidden labels: " + ",".join(leaked))
        if set(record) != {"task_id", "question"}:
            raise AssertionError(f"candidate input schema drift: {sorted(record)}")

    gate = RateGate(time.monotonic)
    client = ArxivClient(_transport, gate=gate)
    outputs: list[dict[str, Any]] = []
    traces: list[dict[str, Any]] = []
    status_counts: dict[str, int] = {}

    for index, record in enumerate(records, 1):
        wait = gate.wait_seconds("arxiv")
        if wait > 0:
            time.sleep(wait)
        query = derive_query(record["question"])
        started = time.monotonic()
        result = client.fetch(search_query=query, max_results=max_results)
        duration = max(0.0, time.monotonic() - started)
        status_counts[result.status.value] = status_counts.get(result.status.value, 0) + 1

        candidates: list[dict[str, str]] = []
        seen_ids: set[str] = set()
        for item in result.records:
            arxiv_id = _normalize_id(item.versioned_id or item.source_id)
            if not arxiv_id or arxiv_id in seen_ids:
                continue
            candidates.append({"arxiv_id": arxiv_id, "title": item.title})
            seen_ids.add(arxiv_id)

        outputs.append(
            {
                "input_data": {"question": record["question"]},
                "inference_results": [
                    {
                        "pass_id": 0,
                        "status": "ok" if result.status is FetchStatus.OK else result.status.value.lower(),
                        "final_candidates": candidates,
                        "turn_details": [
                            {
                                "action": "tool",
                                "duration": round(duration, 6),
                                "input_tokens": 0,
                                "output_tokens": 0,
                            }
                        ],
                    }
                ],
            }
        )
        traces.append(
            {
                "task_id": record["task_id"],
                "query": query,
                "provider": "arxiv-export-api",
                "fetch_status": result.status.value,
                "candidate_count": len(candidates),
                "candidate_arxiv_ids": sorted(seen_ids),
                "duration_seconds": round(duration, 6),
                "note": result.note,
            }
        )
        if index % 25 == 0 or index == len(records):
            print(f"ARB_WIDE_PROGRESS={index}/{len(records)} statuses={json.dumps(status_counts, sort_keys=True)}", flush=True)

    _write_jsonl(output_path, outputs)
    _write_jsonl(trace_path, traces)
    return {
        "schema_version": "orion.p2.autoresearchbench-wide-keyless-run.v1",
        "candidate_input_sha256": _sha256(public_path),
        "candidate_output_sha256": _sha256(output_path),
        "trace_sha256": _sha256(trace_path),
        "tasks_attempted": len(records),
        "provider": "arxiv-export-api",
        "provider_min_interval_seconds": 3.0,
        "requests_per_task": 1,
        "max_results_per_task": max_results,
        "status_counts": status_counts,
        "hidden_labels_visible_to_candidate": False,
    }


def summarize(
    split_manifest_path: Path,
    run_manifest_path: Path,
    evaluation_path: Path,
    candidate_path: Path,
    trace_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    split_manifest = json.loads(split_manifest_path.read_text(encoding="utf-8"))
    run_manifest = json.loads(run_manifest_path.read_text(encoding="utf-8"))
    evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
    aggregate = evaluation.get("aggregate_stats") or {}
    summary = {
        "schema_version": "orion.p2.autoresearchbench-wide-official.v1",
        "benchmark": "AutoResearchBench Wide",
        "pinned_upstream_commit": PINNED_AUTORESEARCHBENCH_COMMIT,
        "official_scorer": "evaluate/evaluate_wide_search.py",
        "candidate": "ORION keyless arXiv public-provider probe",
        "claim_scope": "external_probe_not_full_multi_provider_orion",
        "wide_tasks": split_manifest["wide_tasks"],
        "tasks_attempted": run_manifest["tasks_attempted"],
        "hidden_labels_visible_to_candidate": False,
        "public_input_sha256": split_manifest["public_sha256"],
        "evaluator_gt_sha256": split_manifest["gt_sha256"],
        "candidate_output_sha256": _sha256(candidate_path),
        "trace_sha256": _sha256(trace_path),
        "official_evaluation_sha256": _sha256(evaluation_path),
        "provider_status_counts": run_manifest["status_counts"],
        "official_aggregate_stats": aggregate,
        "authority": "OFFICIAL_WIDE_SCORER_EXTERNAL_PROBE",
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    prepare_parser = sub.add_parser("prepare")
    prepare_parser.add_argument("--full", type=Path, required=True)
    prepare_parser.add_argument("--public", type=Path, required=True)
    prepare_parser.add_argument("--gt", type=Path, required=True)
    prepare_parser.add_argument("--manifest", type=Path, required=True)

    run_parser = sub.add_parser("run")
    run_parser.add_argument("--public", type=Path, required=True)
    run_parser.add_argument("--output", type=Path, required=True)
    run_parser.add_argument("--trace", type=Path, required=True)
    run_parser.add_argument("--manifest", type=Path, required=True)
    run_parser.add_argument("--max-results", type=int, default=20)
    run_parser.add_argument("--limit", type=int)

    summary_parser = sub.add_parser("summarize")
    summary_parser.add_argument("--split-manifest", type=Path, required=True)
    summary_parser.add_argument("--run-manifest", type=Path, required=True)
    summary_parser.add_argument("--evaluation", type=Path, required=True)
    summary_parser.add_argument("--candidate", type=Path, required=True)
    summary_parser.add_argument("--trace", type=Path, required=True)
    summary_parser.add_argument("--output", type=Path, required=True)

    args = parser.parse_args(argv)
    if args.command == "prepare":
        manifest = prepare(args.full, args.public, args.gt)
        args.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print("ARB_WIDE_SPLIT=" + json.dumps(manifest, sort_keys=True))
        return 0
    if args.command == "run":
        manifest = run_candidate(
            args.public,
            args.output,
            args.trace,
            max_results=args.max_results,
            limit=args.limit,
        )
        args.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print("ARB_WIDE_RUN=" + json.dumps(manifest, sort_keys=True))
        return 0
    if args.command == "summarize":
        summary = summarize(
            args.split_manifest,
            args.run_manifest,
            args.evaluation,
            args.candidate,
            args.trace,
            args.output,
        )
        print("ARB_WIDE_OFFICIAL=" + json.dumps(summary, sort_keys=True))
        return 0
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
