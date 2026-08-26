#!/usr/bin/env python3
"""Scorer-compatible, gold-blind AutoResearchBench Wide external probe.

The released AutoResearchBench bundle contains 1,000 records with an explicit
``type`` discriminator (600 ``deep`` and 400 ``wide``).  The ``arxiv_id`` field
is list-valued in the released bundle for both task families, so container shape
must never be used to infer the task family.

The host-owned ``prepare`` command is the only lane allowed to read decrypted
gold.  Candidate execution sees only ``{task_id, question}``.  This adapter also
mirrors the pinned Wide scorer's edge semantics: modern and legacy arXiv IDs are
accepted, empty questions are omitted from the scorer's GT mapping, and duplicate
non-empty question strings use the scorer's last-write mapping.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
BASE = HERE / "run_autoresearchbench_wide_keyless.py"
MODERN_ID = re.compile(r"(\d{4}\.\d{4,5})")
VERSION_SUFFIX = re.compile(r"v\d+$", re.IGNORECASE)


def _load_base():
    spec = importlib.util.spec_from_file_location("orion_p2_arb_wide_base", BASE)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load keyless Wide runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalize_arxiv_id(value: str) -> str:
    """Return the pinned scorer-compatible unversioned arXiv identifier."""

    cleaned = re.sub(r"(?i)^\s*arxiv:\s*", "", str(value or "")).strip()
    if not cleaned:
        return ""
    modern = MODERN_ID.search(cleaned)
    if modern:
        return modern.group(1)
    if "/abs/" in cleaned:
        cleaned = cleaned.split("/abs/", 1)[1]
    cleaned = cleaned.strip().strip("/")
    cleaned = VERSION_SUFFIX.sub("", cleaned)
    return cleaned


def _jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number}: record must be an object")
            rows.append(value)
    return rows


def _record_type(record: dict[str, Any]) -> str:
    return str(record.get("type") or "").strip().lower()


def prepare(full_path: Path, public_path: Path, gt_path: Path) -> dict[str, Any]:
    """Host-only split preserving the exact released 400-record Wide domain."""

    base = _load_base()
    full = _jsonl(full_path)
    type_counts: dict[str, int] = {}
    public: list[dict[str, Any]] = []
    gt: list[dict[str, Any]] = []
    seen_nonempty_questions: set[str] = set()
    legacy_target_count = 0
    empty_target_task_count = 0
    empty_question_task_count = 0
    duplicate_question_task_count = 0

    for record in full:
        record_type = _record_type(record)
        type_counts[record_type] = type_counts.get(record_type, 0) + 1
        if record_type != "wide":
            continue

        raw_ids = record.get("arxiv_id")
        if not isinstance(raw_ids, list):
            raise ValueError("released Wide record has non-list arxiv_id")
        question = str(record.get("question") or "").strip()
        if not question:
            empty_question_task_count += 1
        elif question in seen_nonempty_questions:
            duplicate_question_task_count += 1
        else:
            seen_nonempty_questions.add(question)

        normalized_ids: list[str] = []
        for raw in raw_ids:
            normalized = normalize_arxiv_id(str(raw or ""))
            if normalized:
                normalized_ids.append(normalized)
                if not MODERN_ID.fullmatch(normalized):
                    legacy_target_count += 1
        normalized_ids = list(dict.fromkeys(normalized_ids))
        if not normalized_ids:
            empty_target_task_count += 1

        task_id = f"arb-wide-{len(public) + 1:04d}"
        public.append({"task_id": task_id, "question": question})
        gt.append({"question": question, "arxiv_id": normalized_ids})

    if type_counts.get("wide") != 400 or type_counts.get("deep") != 600:
        raise ValueError(f"unexpected released task partition: {type_counts}")
    if len(public) != 400:
        raise ValueError(f"expected 400 Wide records at pinned release, got {len(public)}")

    leaked = [path for item in public for path in base._hidden_paths(item)]
    if leaked:
        raise AssertionError(
            "hidden labels crossed candidate boundary: " + ",".join(leaked[:5])
        )
    base._write_jsonl(public_path, public)
    base._write_jsonl(gt_path, gt)
    return {
        "schema_version": "orion.p2.autoresearchbench-wide-split.v5",
        "pinned_upstream_commit": base.PINNED_AUTORESEARCHBENCH_COMMIT,
        "release_task_type_field": "type",
        "release_task_type_counts": type_counts,
        "wide_tasks": len(public),
        "legacy_target_id_count": legacy_target_count,
        "empty_target_task_count": empty_target_task_count,
        "empty_question_task_count": empty_question_task_count,
        "duplicate_question_task_count": duplicate_question_task_count,
        "official_gt_mapping_question_count": len(seen_nonempty_questions),
        "official_question_semantics": (
            "empty questions omitted from GT mapping; duplicate nonempty questions "
            "use last-write GT mapping exactly as pinned scorer"
        ),
        "candidate_hidden_label_paths": leaked,
        "public_sha256": base._sha256(public_path),
        "gt_sha256": base._sha256(gt_path),
    }


def _empty_question_output(task_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    output = {
        "input_data": {"question": ""},
        "inference_results": [
            {
                "pass_id": 0,
                "status": "benchmark_empty_question",
                "final_candidates": [],
                "turn_details": [],
            }
        ],
    }
    trace = {
        "task_id": task_id,
        "query": None,
        "provider": None,
        "fetch_status": "BENCHMARK_EMPTY_QUESTION",
        "candidate_count": 0,
        "candidate_arxiv_ids": [],
        "duration_seconds": 0.0,
        "note": "pinned official GT loader omits empty question keys; no provider request issued",
    }
    return output, trace


def run_candidate(
    public_path: Path,
    output_path: Path,
    trace_path: Path,
    *,
    max_results: int,
    limit: int | None,
) -> dict[str, Any]:
    """Run candidates from public questions only, skipping meaningless empty queries."""

    base = _load_base()
    base._normalize_id = normalize_arxiv_id
    records = _jsonl(public_path)
    if limit is not None:
        records = records[:limit]
    for record in records:
        if set(record) != {"task_id", "question"}:
            raise AssertionError(f"candidate input schema drift: {sorted(record)}")
        leaked = base._hidden_paths(record)
        if leaked:
            raise AssertionError("candidate input contains hidden labels: " + ",".join(leaked))

    nonempty = [record for record in records if str(record["question"]).strip()]
    empty_count = len(records) - len(nonempty)
    tmp_public = output_path.with_name(output_path.name + ".nonempty-public.tmp")
    tmp_output = output_path.with_name(output_path.name + ".nonempty-output.tmp")
    tmp_trace = trace_path.with_name(trace_path.name + ".nonempty-trace.tmp")

    if nonempty:
        base._write_jsonl(tmp_public, nonempty)
        base_manifest = base.run_candidate(
            tmp_public,
            tmp_output,
            tmp_trace,
            max_results=max_results,
            limit=None,
        )
        nonempty_outputs = _jsonl(tmp_output)
        nonempty_traces = _jsonl(tmp_trace)
        if len(nonempty_outputs) != len(nonempty) or len(nonempty_traces) != len(nonempty):
            raise AssertionError("base Wide candidate output cardinality drifted")
    else:
        base_manifest = {"status_counts": {}}
        nonempty_outputs = []
        nonempty_traces = []

    output_iter = iter(nonempty_outputs)
    trace_iter = iter(nonempty_traces)
    outputs: list[dict[str, Any]] = []
    traces: list[dict[str, Any]] = []
    for record in records:
        if str(record["question"]).strip():
            outputs.append(next(output_iter))
            traces.append(next(trace_iter))
        else:
            output, trace = _empty_question_output(str(record["task_id"]))
            outputs.append(output)
            traces.append(trace)

    base._write_jsonl(output_path, outputs)
    base._write_jsonl(trace_path, traces)
    for path in (tmp_public, tmp_output, tmp_trace):
        if path.exists():
            path.unlink()

    status_counts = dict(base_manifest.get("status_counts") or {})
    if empty_count:
        status_counts["BENCHMARK_EMPTY_QUESTION"] = empty_count
    return {
        "schema_version": "orion.p2.autoresearchbench-wide-keyless-run.v5",
        "candidate_input_sha256": base._sha256(public_path),
        "candidate_output_sha256": base._sha256(output_path),
        "trace_sha256": base._sha256(trace_path),
        "tasks_attempted": len(records),
        "provider_requests": len(nonempty),
        "empty_question_records_without_provider_request": empty_count,
        "provider": "arxiv-export-api",
        "provider_min_interval_seconds": 3.0,
        "requests_per_nonempty_task": 1,
        "max_results_per_task": max_results,
        "status_counts": status_counts,
        "hidden_labels_visible_to_candidate": False,
        "identifier_normalizer": "modern_legacy_empty_target_and_question_compatible",
    }


def summarize(
    split_manifest_path: Path,
    run_manifest_path: Path,
    evaluation_path: Path,
    candidate_path: Path,
    trace_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    base = _load_base()
    summary = base.summarize(
        split_manifest_path,
        run_manifest_path,
        evaluation_path,
        candidate_path,
        trace_path,
        output_path,
    )
    split = json.loads(split_manifest_path.read_text(encoding="utf-8"))
    run = json.loads(run_manifest_path.read_text(encoding="utf-8"))
    aggregate = summary.get("official_aggregate_stats") or {}
    summary["schema_version"] = "orion.p2.autoresearchbench-wide-official.v5"
    summary["release_task_type_counts"] = split["release_task_type_counts"]
    summary["legacy_target_id_count"] = split["legacy_target_id_count"]
    summary["empty_target_task_count"] = split["empty_target_task_count"]
    summary["empty_question_task_count"] = split["empty_question_task_count"]
    summary["duplicate_question_task_count"] = split["duplicate_question_task_count"]
    summary["official_gt_mapping_question_count"] = split[
        "official_gt_mapping_question_count"
    ]
    summary["provider_requests"] = run["provider_requests"]
    summary["official_records_evaluated"] = aggregate.get("total_records")
    summary["identifier_normalizer"] = (
        "modern_legacy_empty_target_and_question_compatible"
    )
    output_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_prepare = sub.add_parser("prepare")
    p_prepare.add_argument("--full", type=Path, required=True)
    p_prepare.add_argument("--public", type=Path, required=True)
    p_prepare.add_argument("--gt", type=Path, required=True)
    p_prepare.add_argument("--manifest", type=Path, required=True)

    p_run = sub.add_parser("run")
    p_run.add_argument("--public", type=Path, required=True)
    p_run.add_argument("--output", type=Path, required=True)
    p_run.add_argument("--trace", type=Path, required=True)
    p_run.add_argument("--manifest", type=Path, required=True)
    p_run.add_argument("--max-results", type=int, default=20)
    p_run.add_argument("--limit", type=int)

    p_summary = sub.add_parser("summarize")
    p_summary.add_argument("--split-manifest", type=Path, required=True)
    p_summary.add_argument("--run-manifest", type=Path, required=True)
    p_summary.add_argument("--evaluation", type=Path, required=True)
    p_summary.add_argument("--candidate", type=Path, required=True)
    p_summary.add_argument("--trace", type=Path, required=True)
    p_summary.add_argument("--output", type=Path, required=True)

    args = parser.parse_args(argv)
    if args.command == "prepare":
        payload = prepare(args.full, args.public, args.gt)
        args.manifest.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print("ARB_WIDE_SPLIT=" + json.dumps(payload, sort_keys=True))
        return 0
    if args.command == "run":
        payload = run_candidate(
            args.public,
            args.output,
            args.trace,
            max_results=args.max_results,
            limit=args.limit,
        )
        args.manifest.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print("ARB_WIDE_RUN=" + json.dumps(payload, sort_keys=True))
        return 0
    if args.command == "summarize":
        payload = summarize(
            args.split_manifest,
            args.run_manifest,
            args.evaluation,
            args.candidate,
            args.trace,
            args.output,
        )
        print("ARB_WIDE_OFFICIAL=" + json.dumps(payload, sort_keys=True))
        return 0
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
