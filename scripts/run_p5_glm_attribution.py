#!/usr/bin/env python3
"""P5 GLM-5.2 Hidden Cause Attribution Campaign Driver.

This script runs the Q1-Q4 attribution prompt against GLM-5.2 for all 24
hidden-cause cases, validates results against ground truth, and outputs
raw records and metrics.

Run with: python scripts/run_p5_glm_attribution.py

Environment variables:
    GLM_API_KEY: API key for cmkey.cn (or use z.ai Anthropic endpoint)
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import urllib.request
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

# Add ORION src to path
script_dir = Path(__file__).parent
repo_root = script_dir.parent
sys.path.insert(0, str(repo_root / "src"))

# Configuration from the original run
# Allow env override for endpoint and model (required for local adapter)
BASE_URL = os.environ.get("GLM_BASE_URL", "https://api2.cmkey.cn/v1")
MODEL = os.environ.get("GLM_MODEL", "glm-5.2")
TEMPERATURE = 0.0
MAX_TOKENS = 4096

# Q1-Q4 Attribution Prompt (matches original trial)
ATTRIBUTION_PROMPT = """You are a rigorous scientific failure analyst specializing in root cause attribution for software development and research systems.

Your task is to analyze a failure case and attribute it to ONE of these eight root cause families:

ROOT CAUSE FAMILIES:
1. RETRIEVAL_MISS - Search, retrieval, or lookup system fails to find relevant content that exists
2. ROUTING_PLANNING_MISS - Agent correctly identifies a problem but routes or plans the solution incorrectly
3. IMPLEMENTATION_BUG - Code has a concrete bug (off-by-one, wrong logic, incorrect implementation)
4. ENVIRONMENT_DEPENDENCY_TOOL_FAILURE - Failure due to external dependency, environment, or tool compatibility
5. EVALUATOR_METRIC_BUG - Measurement, evaluation, or benchmarking system is flawed or misaligned
6. REPRESENTATION_GAP - Correct algorithm/data but wrong representation, encoding, or format choice
7. MEASUREMENT_SPECIFICATION_GAP - Evaluation protocol or metric specification doesn't capture intended outcome
8. METHOD_BASIS_GAP - Foundational method or approach cannot handle required generalization

For each case, provide:
1. ATTRIBUTED_ROOT_CAUSE: Your best judgment of which family the failure belongs to
2. CONFIDENCE: HIGH (clear signal), MEDIUM (ambiguous), or LOW (insufficient information)
3. COMPETING_CAUSES: List any other plausible families (if confidence is HIGH, may omit)
4. INTERVENTION_PREDICTION: Given the attributed cause, can this be feasibly fixed by the candidate? (YES/NO/CANNOT_DETERMINE)

Respond in JSON format:
{
  "attributed_root_cause": "FAMILY_NAME",
  "confidence": "HIGH|MEDIUM|LOW",
  "competing_causes": ["FAMILY_NAME", ...],
  "intervention_prediction": "YES|NO|CANNOT_DETERMINE",
  "reasoning": "Brief explanation"
}

---

Case {CASE_ID}:

VISIBLE SYMPTOM:
{VISIBLE_SYMPTOM}

CONTEXT:
{CONTEXT}

Attribute this case:"""


@dataclass
class AttributionResult:
    """Result from GLM-5.2 for a single case."""
    case_id: str
    gold_root_cause: str
    attributed_root_cause: str
    confidence: str
    competing_causes: list[str]
    intervention_prediction: str
    reasoning: str
    prompt_tokens: int
    completion_tokens: int
    latency_seconds: float
    correct: bool
    error: str | None = None


def load_protected_suite(path: Path) -> dict[str, Any]:
    """Load the protected hidden cause suite."""
    with open(path) as f:
        return json.load(f)


def call_glm(prompt: str) -> tuple[str, int, int, float]:
    """Call GLM-5.2 API and return response, token counts, and latency."""
    api_key = os.environ.get("GLM_API_KEY", "")
    is_local = BASE_URL.startswith("http://127.0.0.1") or BASE_URL.startswith("http://localhost")

    if not api_key and not is_local:
        raise RuntimeError("Set GLM_API_KEY environment variable (no silent fallback)")

    body = json.dumps({
        "model": MODEL,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "messages": [{"role": "user", "content": prompt}]
    }).encode()

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    req = urllib.request.Request(
        f"{BASE_URL}/chat/completions",
        data=body,
        headers=headers
    )

    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            data = json.load(response)
            raw = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            latency = time.time() - start
            return raw, prompt_tokens, completion_tokens, latency
    except Exception as e:
        latency = time.time() - start
        raise RuntimeError(f"GLM API call failed: {e}") from e


def parse_glm_response(raw: str) -> dict[str, Any]:
    """Parse JSON response from GLM-5.2."""
    try:
        # Try to extract JSON from the response
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0]
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0]

        return json.loads(raw.strip())
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse GLM response as JSON: {e}\n\nRaw response:\n{raw}") from e


def attribute_case(case: dict[str, Any]) -> AttributionResult:
    """Run GLM-5.2 attribution for a single case."""
    case_id = case["case_id"]
    gold_cause = case["protected_root_cause"]

    # Format prompt
    prompt = ATTRIBUTION_PROMPT.replace("{CASE_ID}", case_id).replace(
        "{VISIBLE_SYMPTOM}", case["visible_symptom"]
    ).replace(
        "{CONTEXT}", json.dumps(case["candidate_visible_context"], indent=2)
    )

    try:
        # Call GLM-5.2
        raw, prompt_tokens, completion_tokens, latency = call_glm(prompt)

        # Parse response
        parsed = parse_glm_response(raw)

        attributed = parsed.get("attributed_root_cause", "")
        confidence = parsed.get("confidence", "LOW")
        competing = parsed.get("competing_causes", [])
        intervention = parsed.get("intervention_prediction", "CANNOT_DETERMINE")
        reasoning = parsed.get("reasoning", "")

        # Validate against root causes
        from orion.study.p5.freeze import ROOT_CAUSES
        if attributed not in ROOT_CAUSES:
            raise ValueError(f"Invalid root cause: {attributed}")

        # Check correctness
        correct = attributed == gold_cause

        return AttributionResult(
            case_id=case_id,
            gold_root_cause=gold_cause,
            attributed_root_cause=attributed,
            confidence=confidence,
            competing_causes=competing,
            intervention_prediction=intervention,
            reasoning=reasoning,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            latency_seconds=latency,
            correct=correct,
            error=None
        )
    except Exception as e:
        return AttributionResult(
            case_id=case_id,
            gold_root_cause=gold_cause,
            attributed_root_cause="ERROR",
            confidence="LOW",
            competing_causes=[],
            intervention_prediction="CANNOT_DETERMINE",
            reasoning=str(e),
            prompt_tokens=0,
            completion_tokens=0,
            latency_seconds=0,
            correct=False,
            error=str(e)
        )


def compute_metrics(results: list[AttributionResult]) -> dict[str, Any]:
    """Compute attribution metrics."""
    total = len(results)
    correct = sum(1 for r in results if r.correct)
    incorrect = sum(1 for r in results if not r.correct and r.error is None)
    errors = sum(1 for r in results if r.error is not None)

    # Per-family metrics
    from orion.study.p5.freeze import ROOT_CAUSES
    family_metrics = {}
    for family in sorted(ROOT_CAUSES):
        family_results = [r for r in results if r.gold_root_cause == family]
        if family_results:
            family_correct = sum(1 for r in family_results if r.correct)
            family_total = len(family_results)
            family_metrics[family] = {
                "recall": family_correct / family_total if family_total > 0 else 0,
                "f1": family_correct / family_total if family_total > 0 else 0,  # Perfect precision assumption
                "cases": [r.case_id for r in family_results]
            }

    # Macro F1
    if family_metrics:
        macro_f1 = sum(m["f1"] for m in family_metrics.values()) / len(family_metrics)
    else:
        macro_f1 = 0.0

    # False method change rate (when attribution is correct but intervention is NO)
    correct_with_no = [
        r for r in results
        if r.correct and r.intervention_prediction == "NO"
    ]
    false_method_change_rate = len(correct_with_no) / correct if correct > 0 else 0

    # Confidence distribution
    confidence_dist = {}
    for r in results:
        conf = r.confidence
        confidence_dist[conf] = confidence_dist.get(conf, 0) + 1

    # Total tokens
    total_prompt = sum(r.prompt_tokens for r in results)
    total_completion = sum(r.completion_tokens for r in results)

    return {
        "total_cases": total,
        "correct_attributions": correct,
        "incorrect_attributions": incorrect,
        "errors": errors,
        "accuracy": correct / total if total > 0 else 0,
        "macro_f1": macro_f1,
        "false_method_change_rate": false_method_change_rate,
        "per_family_metrics": family_metrics,
        "confidence_distribution": confidence_dist,
        "total_prompt_tokens": total_prompt,
        "total_completion_tokens": total_completion,
        "total_tokens": total_prompt + total_completion,
        "avg_latency": sum(r.latency_seconds for r in results) / total if total > 0 else 0
    }


def main() -> int:
    """Run the P5 GLM-5.2 attribution campaign."""
    # Parse arguments
    if len(sys.argv) > 1:
        suite_path = Path(sys.argv[1])
    else:
        suite_path = Path("papers/orion-15-self-orion/evidence/hidden-cause-suite/PROTECTED_SUITE_V1.json")

    if not suite_path.exists():
        print(f"Error: Suite file not found: {suite_path}", file=sys.stderr)
        return 1

    # Output paths
    output_dir = Path("papers/orion-15-self-orion/evidence/glm-5.2-attribution")
    output_dir.mkdir(parents=True, exist_ok=True)
    results_path = output_dir / "results.jsonl"
    report_path = output_dir / "report.json"

    print(f"P5 GLM-5.2 Attribution Campaign")
    print(f"================================")
    print(f"Model: {MODEL} via {BASE_URL}")
    print(f"Suite: {suite_path}")
    print(f"Output: {results_path}")
    print()

    # Load suite
    print("Loading protected suite...")
    suite = load_protected_suite(suite_path)
    cases = suite["cases"]
    print(f"Loaded {len(cases)} cases")
    print()

    # Run attribution for each case
    results = []
    for i, case in enumerate(cases, 1):
        case_id = case["case_id"]
        print(f"[{i}/{len(cases)}] Attributing {case_id}...", end=" ", flush=True)

        result = attribute_case(case)
        results.append(result)

        if result.error:
            print(f"ERROR: {result.error}")
        else:
            status = "✓" if result.correct else "✗"
            print(f"{status} {result.attributed_root_cause} ({result.confidence})")

    print()
    print("Computing metrics...")
    metrics = compute_metrics(results)

    # Write results JSONL
    print(f"Writing results to {results_path}...")
    with open(results_path, "w") as f:
        for result in results:
            f.write(json.dumps(asdict(result)) + "\n")

    # Write report JSON
    print(f"Writing report to {report_path}...")
    report = {
        "campaign_id": "p5-glm-5.2-attribution-v1",
        "model": MODEL,
        "endpoint": BASE_URL,
        "timestamp": time.time(),
        "suite_path": str(suite_path),
        "results_path": str(results_path),
        "metrics": metrics,
        "per_case_summary": [
            {
                "case_id": r.case_id,
                "gold": r.gold_root_cause,
                "attributed": r.attributed_root_cause,
                "correct": r.correct,
                "confidence": r.confidence,
                "intervention": r.intervention_prediction
            }
            for r in results
        ]
    }
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print()
    print("=" * 50)
    print("ATTRIBUTION RESULTS")
    print("=" * 50)
    print(f"Total cases: {metrics['total_cases']}")
    print(f"Correct: {metrics['correct_attributions']}/{metrics['total_cases']} ({metrics['accuracy']:.1%})")
    print(f"Incorrect: {metrics['incorrect_attributions']}")
    print(f"Errors: {metrics['errors']}")
    print(f"Macro F1: {metrics['macro_f1']:.3f}")
    print(f"False method change rate: {metrics['false_method_change_rate']:.1%}")
    print()
    print("Per-family performance:")
    for family, m in metrics["per_family_metrics"].items():
        print(f"  {family}: F1={m['f1']:.2f}, cases={', '.join(m['cases'])}")
    print()
    print(f"Total tokens: {metrics['total_tokens']}")
    print(f"Avg latency: {metrics['avg_latency']:.1f}s")

    return 0


if __name__ == "__main__":
    sys.exit(main())
