#!/usr/bin/env python3
"""
Finalize Deep official scoring results and prepare for commit.

Reads the evaluation output, computes hashes, and creates the final results JSON
following the Wide precedent format.

Bindings are never hardcoded: candidate/trace digests are read from the run
manifest of the exact candidate campaign, and the judge control evidence must
explicitly pass before an archive is emitted.
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path


def compute_sha256(file_path: Path) -> str:
    """Compute SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def extract_metrics(eval_data: dict) -> tuple[int, int, float]:
    """Read metrics from either output shape.

    judge_checkpointed.py (the pinned checkpointed execution path) writes
    total_items/hits/hit_rate at the top level of official_evaluation.json;
    an earlier scorer revision nested them under "metrics".  Accept both,
    prefer the top-level shape.
    """
    for source in (eval_data, eval_data.get("metrics", {})):
        if isinstance(source, dict) and "total_items" in source:
            return (
                int(source.get("total_items", 0)),
                int(source.get("hits", 0)),
                float(source.get("hit_rate", 0.0)),
            )
    print("HARNESS ERROR: no metrics found in evaluation output", file=sys.stderr)
    sys.exit(3)


def finalize_results(
    eval_output: Path,
    input_file: Path,
    run_manifest: Path,
    control_json: Path,
    output_file: Path,
) -> dict:
    """Create the final results JSON following Wide precedent."""

    with open(eval_output) as f:
        eval_data = json.load(f)

    total_items, hits, hit_rate = extract_metrics(eval_data)

    # Content bindings come from the exact candidate campaign manifest —
    # never from a hardcoded digest of a superseded run.
    with open(run_manifest) as f:
        manifest = json.load(f)
    required = ("candidate_output_sha256", "trace_sha256", "candidate_input_sha256")
    missing = [k for k in required if not manifest.get(k)]
    if missing:
        print(f"HARNESS ERROR: run manifest missing {missing}", file=sys.stderr)
        sys.exit(3)

    # The judge control evidence must exist and must have passed in full.
    with open(control_json) as f:
        control = json.load(f)
    if control.get("verdict") != "CONTROL_PASSED":
        print(
            f"HARNESS ERROR: judge control verdict {control.get('verdict')!r} "
            "is not CONTROL_PASSED; refusing to archive",
            file=sys.stderr,
        )
        sys.exit(3)

    input_sha256 = compute_sha256(input_file)
    eval_sha256 = compute_sha256(eval_output)

    results = {
        "schema_version": "orion.p2.autoresearchbench-deep-official-archive.v1",
        "authority": "OFFICIAL_DEEP_LLM_TITLE_JUDGE",
        "benchmark": "AutoResearchBench Deep",
        "candidate": "ORION keyless public-arXiv probe",
        "claim_scope": "external_probe_not_full_multi_provider_orion",
        "pinned_upstream_commit": "a46c9bfb8968786f73f0a6a5b365b5384cd0f96d",
        "release_partition": {
            "task_type_field": "type",
            "deep_tasks": 600,
            "wide_tasks": 400,
        },
        "coverage": {
            "tasks_attempted": total_items,
            "official_records_evaluated": total_items,
            "judge_requests": total_items * 5,  # up to 5 candidates judged per item
        },
        "official_metrics": {
            "total_items": total_items,
            "hits": hits,
            "hit_rate": hit_rate,
            "target_hit_rate": hit_rate,  # Same as hit_rate for Deep
        },
        "judge_control": {
            "control_file": control_json.name,
            "verdict": control["verdict"],
            "passed": control.get("passed"),
            "total": control.get("total"),
            "positives_passed": control.get("positives_passed"),
            "negatives_passed": control.get("negatives_passed"),
        },
        "content_bindings": {
            "public_input_sha256": input_sha256,
            "candidate_output_sha256": manifest["candidate_output_sha256"],
            "trace_sha256": manifest["trace_sha256"],
            "official_evaluation_sha256": eval_sha256,
            "judge_adapter": "anthropic_to_openai_adapter.py",
            "judge_model": manifest.get("judge_model", "glm-5.3"),
            "judge_endpoint": "https://api.z.ai/api/anthropic/v1/messages",
            "judge_temperature": 0.5,
            "max_candidates_judged_per_item": 5,
        },
        "candidate_actions": {
            "workflow_run_id": 31976116215,
            "head_sha": "91fef308bbae4860d07a1e73935004055c5065e5",
            "created_at": "2026-08-16T22:21:27Z",
            "artifact_id": "from_ci_mirror_zip",
            "artifact_name": "p2-autoresearchbench-deep-id-91fef308bbae4860d07a1e73935004055c5065e5",
            "note": "Candidate execution completed with blocker: no judge credentials available. Official scoring completed via local adapter.",
        },
        "scorer_actions": {
            "scorer": "run_deep_official_scoring.py (executed via judge_checkpointed.py)",
            "adapter": "anthropic_to_openai_adapter.py",
            "completed_at": datetime.now().isoformat(),
        },
        "interpretation": {
            "completed": "official Deep LLM title judge scoring completed via local Anthropic→OpenAI protocol adapter",
            "not_claimed": [
                "full multi-provider ORION execution",
                "matched ORION-vs-baseline superiority",
                "inferential superiority",
            ],
        },
    }

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Results written to {output_file}")
    print(f"Metrics: {hits}/{total_items} = {hit_rate:.3%}")
    print(f"Bindings: candidate={manifest['candidate_output_sha256'][:12]}… trace={manifest['trace_sha256'][:12]}…")

    return results


def main():
    parser = argparse.ArgumentParser(description="Finalize Deep official scoring results")
    parser.add_argument("--eval-output", type=Path, required=True, help="Path to official_evaluation.json")
    parser.add_argument("--input-file", type=Path, required=True, help="Path to official_input.jsonl")
    parser.add_argument("--run-manifest", type=Path, required=True, help="Path to the candidate run manifest (source of content digests)")
    parser.add_argument("--control-json", type=Path, required=True, help="Path to judge control evidence (must be CONTROL_PASSED)")
    parser.add_argument("--output-file", type=Path, required=True, help="Path to output results JSON")
    args = parser.parse_args()

    finalize_results(
        args.eval_output,
        args.input_file,
        args.run_manifest,
        args.control_json,
        args.output_file,
    )


if __name__ == "__main__":
    main()
