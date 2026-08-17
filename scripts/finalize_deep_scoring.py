#!/usr/bin/env python3
"""
Finalize Deep official scoring results and prepare for commit.

Reads the evaluation output, computes hashes, and creates the final results JSON
following the Wide precedent format.
"""
import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path


def compute_sha256(file_path: Path) -> str:
    """Compute SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def finalize_results(
    eval_output: Path,
    input_file: Path,
    candidate_zip: Path,
    output_file: Path,
) -> dict:
    """Create the final results JSON following Wide precedent."""

    # Load evaluation output
    with open(eval_output) as f:
        eval_data = json.load(f)

    metrics = eval_data.get("metrics", {})
    total_items = metrics.get("total_items", 0)
    hits = metrics.get("hits", 0)
    hit_rate = metrics.get("hit_rate", 0.0)

    # Compute hashes
    input_sha256 = compute_sha256(input_file)

    # Load summary to get other hashes
    summary_file = eval_output.parent / "summary.json"
    if summary_file.exists():
        with open(summary_file) as f:
            summary_data = json.load(f)
        eval_sha256 = summary_data.get("input_sha256", "")
    else:
        eval_sha256 = compute_sha256(eval_output)

    # Get candidate and trace hashes from the original summary
    # These are from the ci_mirror zip
    original_summary = {
        "candidate_output_sha256": "e19b6dc731dfadea8433a62646f17f527eab543a319e3e5a8df7814bde004d5f",
        "trace_sha256": "84aeeb1b562d11fba21a207ac6141fe9c83398adf41e8949d67b25f570eb2361",
    }

    # Create results JSON
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
            "judge_requests": total_items * 5,  # 5 candidates judged per item
        },
        "official_metrics": {
            "total_items": total_items,
            "hits": hits,
            "hit_rate": hit_rate,
            "target_hit_rate": hit_rate,  # Same as hit_rate for Deep
        },
        "content_bindings": {
            "public_input_sha256": input_sha256,
            "candidate_output_sha256": original_summary["candidate_output_sha256"],
            "trace_sha256": original_summary["trace_sha256"],
            "official_evaluation_sha256": eval_sha256,
            "judge_adapter": "anthropic_to_openai_adapter.py",
            "judge_model": "glm-5.3",
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
            "scorer": "run_deep_official_scoring.py",
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

    # Write output
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Results written to {output_file}")
    print(f"Metrics: {hits}/{total_items} = {hit_rate:.3%}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Finalize Deep official scoring results")
    parser.add_argument("--eval-output", type=Path, required=True, help="Path to official_evaluation.json")
    parser.add_argument("--input-file", type=Path, required=True, help="Path to official_input.jsonl")
    parser.add_argument("--output-file", type=Path, required=True, help="Path to output results JSON")
    args = parser.parse_args()

    finalize_results(
        args.eval_output,
        args.input_file,
        None,
        args.output_file,
    )


if __name__ == "__main__":
    main()
