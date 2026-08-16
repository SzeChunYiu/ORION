#!/usr/bin/env python3
"""Compatibility front-end for the keyless AutoResearchBench Wide probe.

AutoResearchBench's official Wide scorer accepts both modern numeric arXiv IDs,
legacy archive/category identifiers, and released tasks whose normalized target
set is empty. Earlier ORION probe attempts were narrower than that contract.
This front-end mirrors the scorer's identifier domain while preserving the same
host/candidate custody boundary and all 400 released Wide tasks.
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
    """Return the scorer-compatible unversioned arXiv identifier.

    The pinned scorer extracts modern ``YYMM.NNNNN`` identifiers and otherwise
    retains the cleaned string. For legacy candidate records, arXiv Atom IDs may
    include an ``/abs/`` URL prefix and ``vN`` suffix, so those transport-only
    decorations are removed before the string is handed to the scorer.
    """

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


def prepare(full_path: Path, public_path: Path, gt_path: Path) -> dict[str, Any]:
    """Host-only Wide split that preserves the scorer's complete task domain."""

    base = _load_base()
    full = _jsonl(full_path)
    public: list[dict[str, Any]] = []
    gt: list[dict[str, Any]] = []
    seen_questions: set[str] = set()
    legacy_target_count = 0
    empty_target_task_count = 0

    for record in full:
        # Wide records have list-valued targets; Deep records have a scalar ID.
        raw_ids = record.get("arxiv_id")
        if not isinstance(raw_ids, list):
            continue
        question = str(record.get("question") or "").strip()
        if not question or question in seen_questions:
            raise ValueError("Wide benchmark contains an empty or duplicate question")

        normalized_ids: list[str] = []
        for raw in raw_ids:
            normalized = normalize_arxiv_id(str(raw or ""))
            if normalized:
                normalized_ids.append(normalized)
                if not MODERN_ID.fullmatch(normalized):
                    legacy_target_count += 1
        normalized_ids = list(dict.fromkeys(normalized_ids))
        if not normalized_ids:
            # The pinned official scorer normalizes an empty released target list
            # to an empty set and scores it rather than removing the task. Keep
            # the task and record this benchmark property explicitly.
            empty_target_task_count += 1

        task_id = f"arb-wide-{len(public) + 1:04d}"
        public.append({"task_id": task_id, "question": question})
        gt.append({"question": question, "arxiv_id": normalized_ids})
        seen_questions.add(question)

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
        "schema_version": "orion.p2.autoresearchbench-wide-split.v3",
        "pinned_upstream_commit": base.PINNED_AUTORESEARCHBENCH_COMMIT,
        "wide_tasks": len(public),
        "legacy_target_id_count": legacy_target_count,
        "empty_target_task_count": empty_target_task_count,
        "candidate_hidden_label_paths": leaked,
        "public_sha256": base._sha256(public_path),
        "gt_sha256": base._sha256(gt_path),
    }


def run_candidate(
    public_path: Path,
    output_path: Path,
    trace_path: Path,
    *,
    max_results: int,
    limit: int | None,
) -> dict[str, Any]:
    base = _load_base()
    base._normalize_id = normalize_arxiv_id
    manifest = base.run_candidate(
        public_path,
        output_path,
        trace_path,
        max_results=max_results,
        limit=limit,
    )
    manifest["schema_version"] = "orion.p2.autoresearchbench-wide-keyless-run.v3"
    manifest["identifier_normalizer"] = "modern_legacy_and_empty_target_compatible"
    return manifest


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
    summary["schema_version"] = "orion.p2.autoresearchbench-wide-official.v3"
    summary["legacy_target_id_count"] = split["legacy_target_id_count"]
    summary["empty_target_task_count"] = split["empty_target_task_count"]
    summary["identifier_normalizer"] = "modern_legacy_and_empty_target_compatible"
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
