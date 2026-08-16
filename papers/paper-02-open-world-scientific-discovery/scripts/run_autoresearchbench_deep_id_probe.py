#!/usr/bin/env python3
"""Gold-blind AutoResearchBench Deep probe and host-owned evaluator adapters.

The released bundle contains an explicit ``type`` field: 600 ``deep`` records
and 400 ``wide`` records.  Both families use list-valued ``arxiv_id`` fields in
the released bundle, so task family must be selected by ``type`` rather than by
container shape.

Candidate execution receives only ``{task_id, question}``.  Host-owned gold is
kept separately.  The deterministic exact-ID evaluator remains a declared
non-official deviation.  ``build-official-input`` may join frozen candidate
output to gold titles only after candidate execution, producing the input
contract required by the pinned official Deep LLM title judge.
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
    spec = importlib.util.spec_from_file_location(
        "orion_p2_arb_wide_compat_for_deep", WIDE_COMPAT
    )
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
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number}: expected object")
            rows.append(value)
    return rows


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def prepare(full_path: Path, public_path: Path, gt_path: Path) -> dict[str, Any]:
    """Host-only split of the exact released 600-record Deep partition."""

    wide = _load_wide()
    public: list[dict[str, Any]] = []
    gt: list[dict[str, Any]] = []
    type_counts: dict[str, int] = {}
    empty_question_count = 0
    empty_target_count = 0
    seen_nonempty: set[str] = set()
    duplicate_question_count = 0
    title_gold_count = 0

    for record in _jsonl(full_path):
        record_type = str(record.get("type") or "").strip().lower()
        type_counts[record_type] = type_counts.get(record_type, 0) + 1
        if record_type != "deep":
            continue

        question = str(record.get("question") or "").strip()
        if not question:
            empty_question_count += 1
        elif question in seen_nonempty:
            duplicate_question_count += 1
        else:
            seen_nonempty.add(question)

        normalized_ids = list(
            dict.fromkeys(
                normalized
                for normalized in (
                    wide.normalize_arxiv_id(str(raw or ""))
                    for raw in _as_list(record.get("arxiv_id"))
                )
                if normalized
            )
        )
        if len(normalized_ids) > 1:
            raise ValueError(
                f"Deep record unexpectedly contains multiple usable target ids: {len(normalized_ids)}"
            )
        target_id = normalized_ids[0] if normalized_ids else ""
        if not target_id:
            empty_target_count += 1

        titles = [str(x).strip() for x in _as_list(record.get("answer")) if str(x).strip()]
        if titles:
            title_gold_count += 1

        task_id = f"arb-deep-{len(public) + 1:04d}"
        public.append({"task_id": task_id, "question": question})
        gt.append(
            {
                "task_id": task_id,
                "question": question,
                "target_arxiv_id": target_id,
                "ground_truth_titles": titles,
            }
        )

    if type_counts.get("deep") != 600 or type_counts.get("wide") != 400:
        raise ValueError(f"unexpected released task partition: {type_counts}")
    if len(public) != 600:
        raise ValueError(f"expected 600 Deep records at pinned release, got {len(public)}")

    expected_public_keys = {"task_id", "question"}
    for index, record in enumerate(public, 1):
        if set(record) != expected_public_keys:
            raise AssertionError(
                f"hidden field crossed Deep candidate boundary at record {index}: "
                f"{sorted(set(record) - expected_public_keys)}"
            )

    _write_jsonl(public_path, public)
    _write_jsonl(gt_path, gt)
    return {
        "schema_version": "orion.p2.autoresearchbench-deep-id-split.v3",
        "pinned_upstream_commit": PINNED_AUTORESEARCHBENCH_COMMIT,
        "release_task_type_field": "type",
        "release_task_type_counts": type_counts,
        "deep_tasks": len(public),
        "empty_question_task_count": empty_question_count,
        "duplicate_question_task_count": duplicate_question_count,
        "empty_target_task_count": empty_target_count,
        "exact_id_scorable_task_count": len(public) - empty_target_count,
        "title_gold_task_count": title_gold_count,
        "candidate_public_fields": sorted(expected_public_keys),
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
    manifest["schema_version"] = "orion.p2.autoresearchbench-deep-keyless-run.v3"
    manifest["benchmark_lane"] = "Deep candidate shared by exact-ID and official-title evaluation"
    manifest["hidden_labels_visible_to_candidate"] = False
    return manifest


def evaluate(
    public_path: Path,
    gt_path: Path,
    candidate_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    """Host-owned exact-ID deviation; no title judge and no semantic proxy."""

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
        "schema_version": "orion.p2.autoresearchbench-deep-id-eval.v3",
        "benchmark": "AutoResearchBench Deep",
        "pinned_upstream_commit": PINNED_AUTORESEARCHBENCH_COMMIT,
        "metric": "exact_target_arxiv_id_retrieval_success",
        "official_deep_metric": False,
        "official_deep_metric_blocker": "official title judge requires OpenAI-compatible endpoint",
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


def build_official_input(
    public_path: Path,
    gt_path: Path,
    candidate_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    """Host-side post-candidate join for the pinned official Deep title judge."""

    public = _jsonl(public_path)
    gt = _jsonl(gt_path)
    candidate = _jsonl(candidate_path)
    if not (len(public) == len(gt) == len(candidate)):
        raise ValueError(
            f"official Deep cardinality mismatch public={len(public)} gt={len(gt)} candidate={len(candidate)}"
        )

    joined: list[dict[str, Any]] = []
    for public_record, gt_record, candidate_record in zip(public, gt, candidate, strict=True):
        task_id = str(public_record["task_id"])
        if gt_record.get("task_id") != task_id:
            raise AssertionError(f"official Deep GT order drift at {task_id}")
        question = str(public_record.get("question") or "")
        if candidate_record.get("input_data", {}).get("question", "") != question:
            raise AssertionError(f"official Deep candidate order drift at {task_id}")

        converted_passes: list[dict[str, Any]] = []
        for result in candidate_record.get("inference_results") or []:
            converted_candidates = []
            for item in result.get("final_candidates") or []:
                if not isinstance(item, dict):
                    continue
                title = str(item.get("title") or "").strip()
                if title:
                    converted_candidates.append({"metadata": {"title": title}})
            status = str(result.get("status") or "")
            if converted_candidates:
                state = "candidate"
            elif status == "ok":
                state = "none"
            else:
                state = "empty"
            converted = dict(result)
            converted["final_candidate_state"] = state
            converted["final_candidates"] = converted_candidates
            converted_passes.append(converted)

        joined.append(
            {
                "input_data": {
                    "question": question,
                    "answer": list(gt_record.get("ground_truth_titles") or []),
                },
                "inference_results": converted_passes,
            }
        )

    _write_jsonl(output_path, joined)
    payload = {
        "schema_version": "orion.p2.autoresearchbench-deep-official-input.v1",
        "records": len(joined),
        "candidate_output_sha256": _sha256(candidate_path),
        "evaluator_gt_sha256": _sha256(gt_path),
        "official_input_sha256": _sha256(output_path),
        "gold_join_stage": "host_owned_after_candidate_freeze",
        "candidate_labels_visible": False,
    }
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
        "schema_version": "orion.p2.autoresearchbench-deep-id-summary.v3",
        "benchmark": "AutoResearchBench Deep",
        "candidate": "ORION keyless public-arXiv probe",
        "claim_scope": "deterministic_external_probe_not_official_deep_title_judge",
        "authority": "DETERMINISTIC_DEEP_ID_EXTERNAL_PROBE",
        "pinned_upstream_commit": PINNED_AUTORESEARCHBENCH_COMMIT,
        "release_task_type_counts": split["release_task_type_counts"],
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


def summarize_official(
    split_manifest_path: Path,
    run_manifest_path: Path,
    official_input_path: Path,
    official_evaluation_path: Path,
    trace_path: Path,
    output_path: Path,
    *,
    judge_model: str,
) -> dict[str, Any]:
    split = json.loads(split_manifest_path.read_text(encoding="utf-8"))
    run = json.loads(run_manifest_path.read_text(encoding="utf-8"))
    evaluation = json.loads(official_evaluation_path.read_text(encoding="utf-8"))
    payload = {
        "schema_version": "orion.p2.autoresearchbench-deep-official-summary.v1",
        "benchmark": "AutoResearchBench Deep",
        "candidate": "ORION keyless public-arXiv external probe",
        "claim_scope": "official_deep_scorer_external_probe_not_full_multi_provider_orion",
        "authority": "OFFICIAL_DEEP_TITLE_JUDGE_EXTERNAL_PROBE",
        "pinned_upstream_commit": PINNED_AUTORESEARCHBENCH_COMMIT,
        "deep_tasks": split["deep_tasks"],
        "tasks_attempted": run["tasks_attempted"],
        "hidden_labels_visible_to_candidate": False,
        "judge_model": judge_model,
        "official_summary": evaluation.get("summary"),
        "split_manifest_sha256": _sha256(split_manifest_path),
        "run_manifest_sha256": _sha256(run_manifest_path),
        "official_input_sha256": _sha256(official_input_path),
        "official_evaluation_sha256": _sha256(official_evaluation_path),
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

    p_build = sub.add_parser("build-official-input")
    p_build.add_argument("--public", type=Path, required=True)
    p_build.add_argument("--gt", type=Path, required=True)
    p_build.add_argument("--candidate", type=Path, required=True)
    p_build.add_argument("--output", type=Path, required=True)

    p_summary = sub.add_parser("summarize")
    p_summary.add_argument("--split-manifest", type=Path, required=True)
    p_summary.add_argument("--run-manifest", type=Path, required=True)
    p_summary.add_argument("--evaluation", type=Path, required=True)
    p_summary.add_argument("--trace", type=Path, required=True)
    p_summary.add_argument("--output", type=Path, required=True)

    p_official = sub.add_parser("summarize-official")
    p_official.add_argument("--split-manifest", type=Path, required=True)
    p_official.add_argument("--run-manifest", type=Path, required=True)
    p_official.add_argument("--official-input", type=Path, required=True)
    p_official.add_argument("--official-evaluation", type=Path, required=True)
    p_official.add_argument("--trace", type=Path, required=True)
    p_official.add_argument("--output", type=Path, required=True)
    p_official.add_argument("--judge-model", required=True)

    args = parser.parse_args(argv)
    if args.command == "prepare":
        payload = prepare(args.full, args.public, args.gt)
        args.manifest.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print("ARB_DEEP_SPLIT=" + json.dumps(payload, sort_keys=True))
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
        print("ARB_DEEP_RUN=" + json.dumps(payload, sort_keys=True))
        return 0
    if args.command == "evaluate":
        payload = evaluate(args.public, args.gt, args.candidate, args.output)
        print("ARB_DEEP_ID_EVAL=" + json.dumps({k: v for k, v in payload.items() if k != "per_task"}, sort_keys=True))
        return 0
    if args.command == "build-official-input":
        payload = build_official_input(args.public, args.gt, args.candidate, args.output)
        print("ARB_DEEP_OFFICIAL_INPUT=" + json.dumps(payload, sort_keys=True))
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
    if args.command == "summarize-official":
        payload = summarize_official(
            args.split_manifest,
            args.run_manifest,
            args.official_input,
            args.official_evaluation,
            args.trace,
            args.output,
            judge_model=args.judge_model,
        )
        print("ARB_DEEP_OFFICIAL_SUMMARY=" + json.dumps(payload, sort_keys=True))
        return 0
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
