#!/usr/bin/env python3
"""Dependency-free publication statistics helpers for ORION paper protocols."""
from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path
from statistics import mean
from typing import Sequence


def wilson_interval(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if total <= 0:
        raise ValueError("total must be positive")
    if successes < 0 or successes > total:
        raise ValueError("successes must be between 0 and total")
    p = successes / total
    z2 = z * z
    denom = 1.0 + z2 / total
    center = (p + z2 / (2.0 * total)) / denom
    half = z * math.sqrt((p * (1.0 - p) / total) + (z2 / (4.0 * total * total))) / denom
    return max(0.0, center - half), min(1.0, center + half)


def required_n_for_proportion_half_width(half_width: float, assumed_p: float = 0.5, z: float = 1.959963984540054) -> int:
    """Normal-approximation planning bound; confirm with pilot-specific design."""
    if not 0 < half_width < 1:
        raise ValueError("half_width must be in (0, 1)")
    if not 0 < assumed_p < 1:
        raise ValueError("assumed_p must be in (0, 1)")
    return math.ceil((z * z * assumed_p * (1.0 - assumed_p)) / (half_width * half_width))


def percentile(values: Sequence[float], q: float) -> float:
    if not values:
        raise ValueError("values must be non-empty")
    if not 0 <= q <= 1:
        raise ValueError("q must be in [0, 1]")
    ordered = sorted(float(v) for v in values)
    if len(ordered) == 1:
        return ordered[0]
    pos = q * (len(ordered) - 1)
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return ordered[lo]
    weight = pos - lo
    return ordered[lo] * (1.0 - weight) + ordered[hi] * weight


def bootstrap_mean_ci(values: Sequence[float], *, confidence: float = 0.95, resamples: int = 10_000, seed: int = 20260816) -> tuple[float, float, float]:
    if not values:
        raise ValueError("values must be non-empty")
    if not 0 < confidence < 1:
        raise ValueError("confidence must be in (0, 1)")
    if resamples <= 0:
        raise ValueError("resamples must be positive")
    xs = tuple(float(v) for v in values)
    rng = random.Random(seed)
    boot = [mean(rng.choices(xs, k=len(xs))) for _ in range(resamples)]
    alpha = (1.0 - confidence) / 2.0
    return mean(xs), percentile(boot, alpha), percentile(boot, 1.0 - alpha)


def paired_bootstrap_difference_ci(candidate: Sequence[float], baseline: Sequence[float], *, confidence: float = 0.95, resamples: int = 10_000, seed: int = 20260816) -> tuple[float, float, float]:
    if len(candidate) != len(baseline) or not candidate:
        raise ValueError("candidate and baseline must have the same positive length")
    diffs = tuple(float(a) - float(b) for a, b in zip(candidate, baseline, strict=True))
    return bootstrap_mean_ci(diffs, confidence=confidence, resamples=resamples, seed=seed)


def summarize_result_jsonl(path: Path, metric: str) -> dict[str, dict[str, float]]:
    grouped: dict[str, list[float]] = {}
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            raw = raw.strip()
            if not raw:
                continue
            record = json.loads(raw)
            system_id = str(record["system_id"])
            metrics = record.get("metrics", {})
            if metric in metrics:
                grouped.setdefault(system_id, []).append(float(metrics[metric]))
    output: dict[str, dict[str, float]] = {}
    for system_id, values in sorted(grouped.items()):
        point, lo, hi = bootstrap_mean_ci(values)
        output[system_id] = {"n": len(values), "mean": point, "ci95_low": lo, "ci95_high": hi}
    return output


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    precision = sub.add_parser("precision", help="plan N for a binomial proportion half-width")
    precision.add_argument("--half-width", type=float, required=True)
    precision.add_argument("--assumed-p", type=float, default=0.5)
    summarize = sub.add_parser("summarize", help="summarize one metric from result JSONL")
    summarize.add_argument("jsonl", type=Path)
    summarize.add_argument("--metric", required=True)
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    if args.command == "precision":
        print(required_n_for_proportion_half_width(args.half_width, args.assumed_p))
    elif args.command == "summarize":
        print(json.dumps(summarize_result_jsonl(args.jsonl, args.metric), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
