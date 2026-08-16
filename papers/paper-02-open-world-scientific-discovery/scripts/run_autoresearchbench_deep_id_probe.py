#!/usr/bin/env python3
"""Deterministic, gold-blind AutoResearchBench Deep-ID external probe.

The pinned *official* Deep metric uses an OpenAI-compatible title judge and
therefore remains unavailable without judge authority.  The released Deep tasks
also contain a scalar target arXiv identifier.  This script uses that identifier
only in a host-owned evaluator to provide a clearly labelled deterministic
external probe: exact target-ID retrieval success.

This is intentionally **not** the official Deep score and must never be reported
as one.  Candidate execution receives only ``{task_id, question}`` and reuses the
same public-arXiv keyless search lane as the Wide probe.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
WIDE_COMPAT = HERE / "run_autoresearchbench_wide_compat.py"
PINNED_AUTORESEARCHBENCH_COMMIT = "a46c9bfb8968786f73f0a6a5b365b5384cd0f96d"


def _load_wide():
    spec = importlib.util.spec_from_file_location("orion_p2_arb_wide_compat_for_deep", WIDE_COMPAT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Wide compatibility runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
                raise ValueError(f"{path}:{line_number}: expected object")
            records.append(value)
    return records


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def prepare(full_path: Path, public_path: Path, gt_path: Path) -> dict[str, Any]:
    """Host-only split of scalar-ID Deep tasks."""

    wide = _load_wide()
    public: list[dict[str, Any]] = []
    gt: list[dict[str, Any]] = []
    empty_question_count = 0
    empty_target_count = 0
    seen_nonempty: set[str] = set()
    duplicate_question_count = 0

    for record in _jsonl(full_path):
        raw_id = record.get("arxiv_id")
        if isinstance(raw_id, list):
            continue
        question = str(record.get("question") or "").strip()
        if not question:
            empty_question_count += 1
        elif question in seen_nonempty:
            duplicate_question_count += 1
        else:
            seen_nonempty.add(question)
        target_id = wide.normalize_arxiv_id(str(raw_id or ""))
        if not target_id:
            empty_target_count += 1
        task_id = f"arb-deep-{len(public) + 1:04d}"
        public.append({"task_id": task_id, "question": question})
        gt.append({"task_id": task_id, "question": question, "target_arxiv_id": target_id})

    if len(public) != 600:
        raise ValueError(f"expected 600 Deep records at pinned release, got {len(public)}")
    # Gold custody assertion: candidate file has only public task identity + text.
    serialized_public = json.dumps(public, sort_keys=True)
    for forbidden in ("answer", "arxiv_id", "target_arxiv_id", "gold", "ground_truth"):
        if forbidden in serialized_public:
            raise AssertionError(f"hidden field crossed Deep candidate boundary: {forbidden}")
    _write_jsonl(public_path, public)
    _write_jsonl(gt_path, gt)
    return {
        "schema_version": "orion.p2.autoresearchbench-deep-id-split.v1",
        "pinned_upstream_commit": PINNED_AUTORESEARCHBENCH_COMMIT,
        "deep_tasks": len(public),
        "empty_question_task_count": empty_question_count,
        "duplicate_question_task_count": duplicate_question_count,
        "empty_target_task_count": empty_target_count,
        "hidden_labels_visible_to_candidate": False,
        "public_sha256": _sha256(public_path),
        "gt_sha256": _sha256(gt_path),
    }


def run_candidate(
    public_path: Path,
    output_path: Path,
    trace_path: Path,
    *,
    max_results: int,
    limit: int | None,
) -> dict[str, Any]:
    """Candidate lane: exactly the same public-arXiv search path as Wide."""

    wide = _load_wide()
    manifest = wide.run_candidate(
        public_path,
        output_path,
        trace_path,
        max_results=max_results,
        limit=limit,
    )
    manifest["schema_version"] = "orion.p2.autoresearchbench-deep-id-keyless-run.v1"
    manifest["benchmark_lane"] = "Deep-ID deterministic deviation"
    manifest["hidden_labels_visible_to_candidate"] = False
    return manifest


def evaluate(
    public_path: Path,
    gt_path: Path,
    candidate_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    """Host-owned exact-ID evaluator; no title judge and no semantic proxy."""

    wide = _load_wide()
    public = _jsonl(public_path)
    gt = _jsonl(gt_path)
    candidate = _jsonl(candidate_path)
    if not (len(public) == len(gt) == len(candidate)):
        raise ValueError(
            f"Deep-ID cardinality mismatch public={len(public)} gt={len(gt)} candidate={len(candidate)}"
        )

    per_task: list[dict[str, Any]] = []
    hits = 0
    scorable = 0
    total_predicted = 0
    for public_record, gt_record, candidate_record in zip(public, gt, candidate, strict=True):
        task_id = str(public_record["task_id"])
        if gt_record.get("task_id") != task_id:
            raise AssertionError(f"Deep-ID GT order drift at {task_id}")
        if candidate_record.get("input_data", {}).get("question", "") != public_record.get("question", ""):
            raise AssertionError(f"Deep-ID candidate question order drift at {task_id}")
        target = str(gt_record.get("target_arxiv_id") or "")
        passes = candidate_record.get("inference_results") or []
        candidates = passes[0].get("final_candidates", []) if passes else []
        predicted = {
            wide.normalize_arxiv_id(str(item.get("arxiv_id") or ""))
            for item in candidates
            if isinstance(item, dict)
        }
        predicted.discard("")
        total_predicted += len(predicted)
        hit: bool | None
        if target:
            scorable += 1
            hit = target in predicted
            hits += int(hit)
        else:
            hit = None
        per_task.append(
            {
                "task_id": task_id,
                "target_present": bool(target),
                "target_hit": hit,
                "predicted_count": len(predicted),
                "provider_status": passes[0].get("status") if passes else "missing",
            }
        )

    payload = {
        "schema_version": "orion.p2.autoresearchbench-deep-id-eval.v1",
        "benchmark": "AutoResearchBench Deep",
        "pinned_upstream_commit": PINNED_AUTORESEARCHBENCH_COMMIT,
        "metric": "exact_target_arxiv_id_retrieval_success",
        "official_deep_metric": False,
        "official_deep_metric_blocker": "OpenAI-compatible title judge unavailable",
        "authority": "DETERMINISTIC_DEEP_ID_EXTERNAL_PROBE",
        "total_records": len(public),
        "scorable_records": scorable,
        "empty_target_records": len(public) - scorable,
        "target_hits": hits,
        "target_hit_rate": round(hits / scorable, 6) if scorable else None,
        "mean_predicted_count": round(total_predicted / len(public), 6) if public else 0.0,
        "public_input_sha256": _sha256(public_path),
        "evaluator_gt_sha256": _sha256(gt_path),
        "candidate_output_sha256": _sha256(candidate_path),
        "per_task": per_task,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def summarize(
    split_manifest_path: Path,
    run_manifest_path: Path,
    evaluation_path: Path,
    trace_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    split = json.loads(split_manifest_path.read_text(encoding="utf-8"))
    run = json.loads(run_manifest_path.read_text(encoding="utf-8"))
    evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
    payload = {
        "schema_version": "orion.p2.autoresearchbench-deep-id-summary.v1",
        "benchmark": "AutoResearchBench Deep",
        "candidate": "ORION keyless public-arXiv probe",
        "claim_scope": "deterministic_external_probe_not_official_deep_title_judge",
        "authority": "DETERMINISTIC_DEEP_ID_EXTERNAL_PROBE",
        "pinned_upstream_commit": PINNED_AUTORESEARCHBENCH_COMMIT,
        "deep_tasks": split["deep_tasks"],
        "tasks_attempted": run["tasks_attempted"],
        "provider_requests": run.get("provider_requests"),
        "hidden_labels_visible_to_candidate": False,
        "empty_question_task_count": split["empty_question_task_count"],
        "empty_target_task_count": split["empty_target_task_count"],
        "provider_status_counts": run["status_counts"],
        "target_hit_rate": evaluation["target_hit_rate"],
        "target_hits": evaluation["target_hits"],
        "scorable_records": evaluation["scorable_records"],
        "mean_predicted_count": evaluation["mean_predicted_count"],
        "split_manifest_sha256": _sha256(split_manifest_path),
        "run_manifest_sha256": _sha256(run_manifest_path),
        "evaluation_sha256": _sha256(evaluation_path),
        "trace_sha256": _sha256(trace_path),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


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

    p_eval = sub.add_parser("evaluate")
    p_eval.add_argument("--public", type=Path, required=True)
    p_eval.add_argument("--gt", type=Path, required=True)
    p_eval.add_argument("--candidate", type=Path, required=True)
    p_eval.add_argument("--output", type=Path, required=True)

    p_summary = sub.add_parser("summarize")
    p_summary.add_argument("--split-manifest", type=Path, required=True)
    p_summary.add_argument("--run-manifest", type=Path, required=True)
    p_summary.add_argument("--evaluation", type=Path, required=True)
    p_summary.add_argument("--trace", type=Path, required=True)
    p_summary.add_argument("--output", type=Path, required=True)

    args = parser.parse_args(argv)
    if args.command == "prepare":
        payload = prepare(args.full, args.public, args.gt)
        args.manifest.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print("ARB_DEEP_ID_SPLIT=" + json.dumps(payload, sort_keys=True))
        return 0
    if args.command == "run":
        payload = run_candidate(
            args.public,
            args.output,
            args.trace,
            max_results=args.max_results,
            limit=args.limit,
        )
        args.manifest.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print("ARB_DEEP_ID_RUN=" + json.dumps(payload, sort_keys=True))
        return 0
    if args.command == "evaluate":
        payload = evaluate(args.public, args.gt, args.candidate, args.output)
        print("ARB_DEEP_ID_EVAL=" + json.dumps({k: v for k, v in payload.items() if k != "per_task"}, sort_keys=True))
        return 0
    if args.command == "summarize":
        payload = summarize(
            args.split_manifest,
            args.run_manifest,
            args.evaluation,
            args.trace,
            args.output,
        )
        print("ARB_DEEP_ID_SUMMARY=" + json.dumps(payload, sort_keys=True))
        return 0
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
