#!/usr/bin/env python3
"""Score the matched-budget Wide comparison with the pinned upstream evaluator.

The comparison runner produces one candidate file per system in upstream's own
inference-output shape. This script hands each of those to
``evaluate/evaluate_wide_search.py`` from a checkout of the pinned
AutoResearchBench commit and runs it **verbatim** — no reimplementation of the
metric, because the point of an official score is that we did not define it.

It then applies the paper's frozen statistical rules to the per-task IoUs the
evaluator emits: a paired percentile bootstrap over matched tasks, the achieved
precision half-width, and the pre-declared decision rule. Three things are
deliberately refused:

* ``avg_max_iou_at_k`` is never reported as a score. Upstream samples it without
  seeding, so its value is not reproducible from a pinned evaluator hash, and at
  three passes the ``at_4/8/16`` variants receive no samples and emit ``0.0`` —
  an absent measurement wearing the costume of a number.
* No metric is emitted when its denominator is missing.
* A non-inferiority verdict is refused when measured consumption exceeds the
  frozen cost ceiling, because equivalence bought by spending more is not a
  result.

The verdict is decided by the paired interval, which is the plan's primary test.
The proportion half-width is reported alongside it and, when it exceeds the
superiority margin, attaches the plan's ``UNDERPOWERED`` label to the result — it
does not override the outcome. Gating on it would have declared the plan's own
committed tier incapable of deciding anything, which is not what the plan says.

Usage::

    score_wide_comparison.py --run-dir <cmp dir> --gt <host gt.jsonl> \\
        --upstream-dir <pinned AutoResearchBench checkout> --out <summary.json>
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

PINNED_UPSTREAM_COMMIT = "a46c9bfb8968786f73f0a6a5b365b5384cd0f96d"
STATS_MODULE = (
    Path(__file__).resolve().parents[3]
    / "research"
    / "paper-programme-v1"
    / "protocols"
    / "publication_stats.py"
)
BOOTSTRAP_RESAMPLES = 10_000
BOOTSTRAP_SEED = 20260817
#: From STATISTICAL_PLAN_V1.json. Restated here only so the script fails loudly
#: if the plan and this code ever disagree; the plan is the authority.
DELTA_SUP = 0.03
DELTA_NI = 0.01
COST_RATIO_CEILING = 1.25
TIERS = {"TIER_A_full": 0.03, "TIER_B_committed": 0.05, "TIER_C_reduced": 0.075, "TIER_D_min": 0.10}


def _load_stats():
    spec = importlib.util.spec_from_file_location("publication_stats", STATS_MODULE)
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise RuntimeError(f"cannot load {STATS_MODULE}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


stats = _load_stats()


def check_plan_agreement(plan_path: Path) -> dict[str, Any]:
    """Fail rather than silently diverge from the frozen plan's margins."""

    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    text = json.dumps(plan)
    problems: list[str] = []
    if f"{DELTA_SUP}" not in text:
        problems.append(f"delta_sup {DELTA_SUP} not found in the frozen plan")
    if f"{DELTA_NI}" not in text:
        problems.append(f"delta_ni {DELTA_NI} not found in the frozen plan")
    if problems:
        raise SystemExit("frozen-plan disagreement: " + "; ".join(problems))
    return {"plan_path": str(plan_path), "delta_sup": DELTA_SUP, "delta_ni": DELTA_NI}


def run_official_evaluator(
    upstream_dir: Path, candidate: Path, gt: Path, output: Path
) -> dict[str, Any]:
    """Run upstream's evaluator as a subprocess, from its own directory.

    Invoked as a subprocess on purpose: the evaluator imports its sibling
    ``utils`` module and reads its own environment, so importing it into this
    process would quietly change the thing we are claiming to have run.
    """

    script = upstream_dir / "evaluate" / "evaluate_wide_search.py"
    if not script.is_file():
        raise SystemExit(f"pinned upstream evaluator not found at {script}")
    completed = subprocess.run(
        [
            sys.executable,
            str(script),
            "--input",
            str(candidate),
            "--gt-file",
            str(gt),
            "--output",
            str(output),
            "--no-jina",
        ],
        cwd=str(upstream_dir),
        capture_output=True,
        text=True,
        timeout=1800,
    )
    if completed.returncode != 0:
        raise SystemExit(
            f"upstream evaluator failed ({completed.returncode}):\n"
            f"{completed.stdout[-2000:]}\n{completed.stderr[-2000:]}"
        )
    return json.loads(output.read_text(encoding="utf-8"))


def per_task_iou(evaluation: dict[str, Any]) -> dict[str, float]:
    """Extract per-task IoU keyed by task identity, for paired comparison.

    Upstream's record shape is followed rather than guessed at: whichever of the
    known keys carries the per-record list is used, and an unrecognised shape is
    an error instead of an empty result that would read as a tie.
    """

    for key in ("records", "results", "per_record", "details"):
        rows = evaluation.get(key)
        if isinstance(rows, list) and rows:
            table: dict[str, float] = {}
            for index, row in enumerate(rows):
                if not isinstance(row, dict):
                    continue
                identity = str(
                    row.get("task_id")
                    or row.get("question")
                    or row.get("input_question")
                    or index
                )
                value = row.get("avg_iou", row.get("iou"))
                if isinstance(value, (int, float)):
                    table[identity] = float(value)
            if table:
                return table
    raise SystemExit(
        "could not locate per-record IoUs in the evaluator output; keys were: "
        + ",".join(sorted(evaluation))
    )


def headline(evaluation: dict[str, Any]) -> dict[str, Any]:
    """Keep the exactly-computed quantities; drop the unseeded sampled family."""

    summary = evaluation.get("summary", evaluation)
    kept = {
        key: summary[key]
        for key in ("avg_iou", "avg_recall", "avg_precision", "num_records", "record_count")
        if key in summary and isinstance(summary[key], (int, float))
    }
    dropped = sorted(key for key in summary if "max_iou_at" in key)
    return {
        "exact_metrics": kept,
        "excluded_sampled_metrics": dropped,
        "exclusion_reason": (
            "upstream samples max_iou_at_k without seeding, so the value is not "
            "reproducible from a pinned evaluator hash; at three passes the at_4/8/16 "
            "variants receive no samples and report 0.0, which is an absent "
            "measurement rather than a score"
        ),
    }


#: The same z the shared library uses for its 95% intervals. Restated rather than
#: re-derived so this script and `publication_stats` cannot drift apart.
Z_95 = 1.959963984540054


def achieved_precision(n: int) -> dict[str, Any]:
    """Achieved half-width at the plan's conservative p, and the tier it reaches.

    Tier membership is decided by the library's own sample-size function rather
    than by re-deriving its inverse here: two implementations of the same formula
    are two chances to be subtly wrong about how much evidence we have.
    """

    half_width = (Z_95 * 0.5 / (n ** 0.5)) if n else float("inf")
    tier = None
    for name, bound in sorted(TIERS.items(), key=lambda item: item[1]):
        if n >= stats.required_n_for_proportion_half_width(bound, 0.5):
            tier = name
            break
    return {
        "n": n,
        "achieved_half_width": round(half_width, 5),
        "assumed_p": 0.5,
        "tier": tier or "BELOW_TIER_D",
        "tier_rule": "n >= publication_stats.required_n_for_proportion_half_width(bound, 0.5)",
        "underpowered_for_delta_sup": half_width > DELTA_SUP,
    }


def compare(candidate: dict[str, float], baseline: dict[str, float]) -> dict[str, Any]:
    shared = sorted(set(candidate) & set(baseline))
    if not shared:
        raise SystemExit("no matched tasks between the two systems; pairing is impossible")
    left = [candidate[key] for key in shared]
    right = [baseline[key] for key in shared]
    low, high = stats.paired_bootstrap_difference_ci(
        left, right, resamples=BOOTSTRAP_RESAMPLES, seed=BOOTSTRAP_SEED
    )
    difference = sum(left) / len(left) - sum(right) / len(right)
    return {
        "paired_tasks": len(shared),
        "mean_difference": round(difference, 5),
        "ci_low": round(low, 5),
        "ci_high": round(high, 5),
        "resamples": BOOTSTRAP_RESAMPLES,
        "seed": BOOTSTRAP_SEED,
        "interval_definition": "paired percentile bootstrap over matched tasks, 95%",
    }


def cost_ratio(run_manifest: dict[str, Any], candidate: str, baseline: str) -> dict[str, Any]:
    """Measured consumption ratio, because non-inferiority at any cost is not a result."""

    systems = run_manifest.get("systems", {})
    left = float(systems.get(candidate, {}).get("provider_requests_per_task") or 0.0)
    right = float(systems.get(baseline, {}).get("provider_requests_per_task") or 0.0)
    ratio = (left / right) if right else float("inf")
    return {
        "candidate_requests_per_task": left,
        "baseline_requests_per_task": right,
        "ratio": round(ratio, 4),
        "ceiling": COST_RATIO_CEILING,
        "within_ceiling": ratio <= COST_RATIO_CEILING,
    }


def verdict(
    comparison: dict[str, Any],
    precision: dict[str, Any],
    cost: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Apply the pre-declared decision rule, including its failure branches."""

    low, high, difference = comparison["ci_low"], comparison["ci_high"], comparison["mean_difference"]

    # The decision is driven by the paired interval, which is the plan's primary
    # test. The proportion half-width is a precision *statement* about a single
    # rate and is far more pessimistic than a paired design — gating the verdict
    # on it would have declared the plan's own committed tier unable to decide
    # anything, which is not what the plan says. Underpower is therefore a label
    # attached to the result, exactly as the plan words it, not an override.
    if low > DELTA_SUP:
        outcome, reason = "PROMOTE", f"paired interval lies entirely above delta_sup {DELTA_SUP}"
    elif low > -DELTA_NI and high < DELTA_SUP:
        if cost is not None and not cost["within_ceiling"]:
            outcome = "SHRINK_OR_REFRAME"
            reason = (
                f"interval sits inside the non-inferiority band, but measured consumption "
                f"ratio {cost['ratio']} exceeds the frozen ceiling {COST_RATIO_CEILING}, "
                "which makes a non-inferiority claim inadmissible"
            )
        else:
            outcome = "NON_INFERIOR"
            reason = (
                f"paired interval sits inside the non-inferiority band (-{DELTA_NI}, {DELTA_SUP}) "
                f"at a measured consumption ratio of "
                f"{cost['ratio'] if cost else 'unmeasured'}"
            )
    elif low <= -DELTA_NI and high >= DELTA_SUP:
        outcome = "INSUFFICIENT_EVIDENCE"
        reason = (
            "the paired interval spans both a material loss and a material win, so this N "
            "cannot separate the hypotheses"
        )
    else:
        outcome = "SHRINK_OR_REFRAME"
        reason = (
            "no superiority and no bounded non-inferiority; the declared response is to "
            "shrink or reframe the claim rather than present a null as a success"
        )
    return {
        "outcome": outcome,
        "reason": reason,
        "mean_difference": difference,
        "underpowered_label": precision["underpowered_for_delta_sup"],
        "underpowered_note": (
            f"achieved half-width {precision['achieved_half_width']} exceeds delta_sup "
            f"{DELTA_SUP}; the plan requires this label on the primary result at N="
            f"{precision['n']}"
            if precision["underpowered_for_delta_sup"]
            else "achieved precision meets the superiority margin"
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--gt", type=Path, required=True)
    parser.add_argument("--upstream-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument(
        "--candidate-system", default="wide_governed_multiroute", help="system under test"
    )
    parser.add_argument(
        "--baseline-system", default="wide_lexical_arxiv", help="matched-budget baseline"
    )
    parser.add_argument(
        "--plan",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "protocol" / "STATISTICAL_PLAN_V1.json",
    )
    args = parser.parse_args(argv)

    run_manifest = json.loads(
        (args.run_dir / "COMPARISON_RUN_MANIFEST.json").read_text(encoding="utf-8")
    )
    summary: dict[str, Any] = {
        "schema_version": "orion.p2.wide-comparison-score.v1",
        "pinned_upstream_commit": PINNED_UPSTREAM_COMMIT,
        "official_scorer": "evaluate/evaluate_wide_search.py run verbatim as a subprocess",
        "frozen_plan": check_plan_agreement(args.plan),
        "run_manifest": run_manifest,
        "systems": {},
    }

    tables: dict[str, dict[str, float]] = {}
    for system_id in (args.baseline_system, args.candidate_system):
        candidate = args.run_dir / f"candidate_{system_id}.jsonl"
        if not candidate.is_file():
            raise SystemExit(f"missing candidate output for {system_id}: {candidate}")
        evaluation_path = args.run_dir / f"official_eval_{system_id}.json"
        evaluation = run_official_evaluator(args.upstream_dir, candidate, args.gt, evaluation_path)
        tables[system_id] = per_task_iou(evaluation)
        summary["systems"][system_id] = {
            "candidate_path": candidate.name,
            "official_eval_path": evaluation_path.name,
            **headline(evaluation),
            "scored_tasks": len(tables[system_id]),
        }

    precision = achieved_precision(
        len(set(tables[args.candidate_system]) & set(tables[args.baseline_system]))
    )
    comparison = compare(tables[args.candidate_system], tables[args.baseline_system])
    summary["precision"] = precision
    summary["comparison"] = comparison
    cost = cost_ratio(run_manifest, args.candidate_system, args.baseline_system)
    summary["cost_ratio"] = cost
    summary["verdict"] = verdict(comparison, precision, cost)

    args.out.write_text(json.dumps(summary, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print("WIDE_COMPARISON_SCORE=" + json.dumps(summary["verdict"], sort_keys=True))
    print(json.dumps({k: v.get("exact_metrics") for k, v in summary["systems"].items()}, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
