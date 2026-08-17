#!/usr/bin/env python3
"""
Run official Deep scorer on archived candidate outputs.

Usage:
    python scripts/run_deep_official_scoring.py <official_input.jsonl> <output_dir>

Requires adapter running on http://127.0.0.1:8765
"""
import argparse
import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict

import aiohttp


LOGGER = logging.getLogger(__name__)
DEFAULT_ADAPTER_URL = "http://127.0.0.1:8765/v1/chat/completions"
ADAPTER_URL = DEFAULT_ADAPTER_URL
MODEL = "glm-5.3"
TEMPERATURE = 0.5

JUDGE_PROMPT_SYSTEM = """
You are an expert verifier for academic paper titles. Your task is to determine if a candidate paper title refers to the exact same paper as a ground truth title.
Note that the returned candidate title may be truncated, such as "The effects of external planets on inner systems: multiplicities, inclinations, and pathways to eccentric warm Jupiters" becoming "The effects of external planets on inner systems: multiplicities ...". Such cases should still be judged as correct.
Ignore minor differences in punctuation, capitalization, or the presence or absence of subtitles unless they fundamentally change the paper's identity.
Respond ONLY with a JSON object in the following format:
{"is_match": boolean, "reason": "A brief explanation for your decision."}
"""

JUDGE_PROMPT_USER_TEMPLATE = """
Please verify if the following two titles refer to the same paper.

Ground Truth Title:
`{ground_truth_title}`

Candidate Title:
`{candidate_title}`
"""


def parse_judge_output(output: str) -> bool:
    """Parse judge output to extract is_match boolean."""
    try:
        data = json.loads(output)
        if isinstance(data, dict) and "is_match" in data:
            return bool(data["is_match"])
    except (json.JSONDecodeError, TypeError):
        return "true" in output.lower()
    return False


async def judge_title_match(
    session: aiohttp.ClientSession,
    gt_title: str,
    candidate_title: str,
) -> tuple[bool, str]:
    """Judge if two titles match using the adapter."""
    messages = [
        {"role": "system", "content": JUDGE_PROMPT_SYSTEM},
        {
            "role": "user",
            "content": JUDGE_PROMPT_USER_TEMPLATE.format(
                ground_truth_title=gt_title,
                candidate_title=candidate_title,
            ),
        },
    ]

    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": TEMPERATURE,
        "max_tokens": 512,
    }

    try:
        async with session.post(ADAPTER_URL, json=payload, timeout=aiohttp.ClientTimeout(total=60)) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                raise RuntimeError(f"Adapter error {resp.status}: {error_text}")

            data = await resp.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            is_match = parse_judge_output(content)
            return is_match, content

    except asyncio.TimeoutError:
        raise RuntimeError("Judge request timed out")
    except Exception as e:
        raise RuntimeError(f"Judge request failed: {e}")


async def evaluate_single_item(
    session: aiohttp.ClientSession,
    item: Dict[str, Any],
    index: int,
    total: int,
    max_candidates: int = 5,
) -> Dict[str, Any]:
    """Evaluate a single item from official_input.jsonl."""
    input_data = item.get("input_data", {})
    question = input_data.get("question", "")
    gt_answer = input_data.get("answer", [])

    # Get candidate titles from inference_results
    inference_results = item.get("inference_results", [])
    if not inference_results:
        return {
            "index": index,
            "question": question,
            "error": "No inference_results",
        }

    # Get the last pass's final candidates
    last_pass = inference_results[-1]
    final_candidates = last_pass.get("final_candidates", [])

    # Extract candidate titles (limited to max_candidates for optimization)
    candidate_titles = []
    for candidate in final_candidates[:max_candidates]:
        if isinstance(candidate, dict):
            # Handle both formats: {metadata: {title: ...}} and {title: ...}
            if "metadata" in candidate and "title" in candidate.get("metadata", {}):
                candidate_titles.append(candidate["metadata"]["title"])
            elif "title" in candidate:
                candidate_titles.append(candidate["title"])

    # Judge each candidate against ground truth answers with early stopping
    judged_pairs = []
    hit = False

    for gt_title in gt_answer:
        if hit:
            break  # Early stop if already found a match
        for cand_title in candidate_titles:
            is_match, reason = await judge_title_match(session, gt_title, cand_title)
            judged_pairs.append({
                "ground_truth": gt_title,
                "candidate": cand_title,
                "is_match": is_match,
                "reason": reason,
            })
            if is_match:
                hit = True
                break  # Found match for this GT title

    LOGGER.info(f"[{index + 1}/{total}] Hit={hit}, GT titles={len(gt_answer)}, Candidates={len(candidate_titles)} (limited from {len(final_candidates)}), Judged={len(judged_pairs)}")

    return {
        "index": index,
        "question": question,
        "ground_truth_answers": gt_answer,
        "candidate_titles": candidate_titles,
        "total_candidates": len(final_candidates),
        "hit": hit,
        "judged_pairs": judged_pairs,
    }


async def run_evaluation(
    input_file: Path,
    output_file: Path,
    slice_end: int | None = None,
    max_candidates: int = 5,
) -> Dict[str, Any]:
    """Run the official Deep evaluation."""
    # Load input items
    LOGGER.info(f"Loading input from {input_file}")
    items = []
    with open(input_file, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))

    total = len(items)
    if slice_end:
        total = min(total, slice_end)
        items = items[:total]

    LOGGER.info(f"Evaluating {total} items (max {max_candidates} candidates per item)")

    # Run evaluation with semaphore for rate limiting
    semaphore = asyncio.Semaphore(3)  # Max 3 concurrent judge requests
    results = []

    async with aiohttp.ClientSession() as session:
        for index, item in enumerate(items):
            result = await evaluate_single_item(session, item, index, total, max_candidates)
            results.append(result)

    # Compute metrics
    hits = sum(1 for r in results if r.get("hit", False))
    total_attempted = len(results)
    hit_rate = hits / total_attempted if total_attempted > 0 else 0.0

    metrics = {
        "total_items": total_attempted,
        "hits": hits,
        "hit_rate": hit_rate,
        "items": results,
    }

    # Write output
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(metrics, f, indent=2)

    LOGGER.info(f"Results written to {output_file}")
    LOGGER.info(f"Metrics: {hits}/{total_attempted} = {hit_rate:.3%}")

    return metrics


def compute_hashes(input_file: Path) -> Dict[str, str]:
    """Compute SHA256 hashes for content binding."""
    hashes = {}

    # Input file hash
    with open(input_file, "rb") as f:
        hashes["input_sha256"] = sha256(f.read()).hexdigest()

    return hashes


async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    parser = argparse.ArgumentParser(description="Run official Deep scorer")
    parser.add_argument("input_file", type=Path, help="Path to official_input.jsonl")
    parser.add_argument("output_dir", type=Path, help="Output directory")
    parser.add_argument("--slice-end", type=int, help="Run on first N items only (for validation)")
    parser.add_argument("--max-candidates", type=int, default=5, help="Max candidates to judge per item (default: 5)")
    parser.add_argument("--adapter-url", default=DEFAULT_ADAPTER_URL, help="Adapter URL")
    args = parser.parse_args()

    global ADAPTER_URL
    ADAPTER_URL = args.adapter_url

    # Check if adapter is responding
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(ADAPTER_URL.replace("/v1/chat/completions", "/")) as resp:
                if resp.status != 200:
                    LOGGER.error(f"Adapter not responding: {resp.status}")
                    sys.exit(1)
    except Exception as e:
        LOGGER.error(f"Adapter check failed: {e}")
        sys.exit(1)

    # Run evaluation
    output_file = args.output_dir / "official_evaluation.json"
    metrics = await run_evaluation(args.input_file, output_file, args.slice_end, args.max_candidates)

    # Compute hashes
    hashes = compute_hashes(args.input_file)

    # Write summary
    summary = {
        "schema_version": "orion.p2.autoresearchbench-deep-official-evaluation.v1",
        "authority": "OFFICIAL_DEEP_LLM_TITLE_JUDGE",
        "model": MODEL,
        "adapter_url": ADAPTER_URL,
        "temperature": TEMPERATURE,
        "input_file": str(args.input_file),
        "input_sha256": hashes["input_sha256"],
        "slice_end": args.slice_end,
        "evaluated_at": datetime.now().isoformat(),
        "metrics": {
            "total_items": metrics["total_items"],
            "hits": metrics["hits"],
            "hit_rate": metrics["hit_rate"],
        },
    }

    summary_file = args.output_dir / "summary.json"
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)

    LOGGER.info(f"Summary written to {summary_file}")
    print(f"\n✓ Evaluation complete: {metrics['hits']}/{metrics['total_items']} = {metrics['hit_rate']:.3%}")


if __name__ == "__main__":
    asyncio.run(main())
