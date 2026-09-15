"""Score a finished P3 evaluation checkpoint into per-system metrics, aggregates,
hypothesis tests, and report tables.

Consumes ``evaluation/run-full/checkpoint.jsonl`` (one raw prediction per line:
sid, ci, seed, + 11 coordinates, preservation_conditions, recoverability_target)
and the gold file (``gold/combined_gold.json``).  Emits:

  - ``analysis/metrics_by_system_seed.json``   raw per-(system,seed) metrics
  - ``analysis/aggregates.json``               bootstrap means + Wilson CIs per system
  - ``analysis/hypotheses.json``               H1a/H1b/H2/H3/H4 tests
  - ``analysis/report_table_latex.tex``        LaTeX table body for the manuscript
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, "src")

from orion.study.metrics import compute_all_metrics
from orion.study import statistics as stats

PAPER = Path(__file__).resolve().parents[1]
CHECKPOINT = PAPER / "evaluation" / "run-full" / "checkpoint.jsonl"
GOLD = PAPER / "gold" / "combined_gold.json"
OUT = PAPER / "evaluation" / "analysis"

ALL_SYSTEMS = [
    "ORION_FULL",
    "VanillaLongContext", "ScientificRAG", "CrossDomainRAG",
    "FlatUniversalSchema", "SCOPE_SCION_Like", "ProvenanceSchema",
    "ORION_no_referent", "ORION_no_construct", "ORION_no_measurement",
    "ORION_no_context", "ORION_no_modality_polarity_attribution_discourse",
    "ORION_no_obstruction", "ORION_no_recoverability", "ORION_no_W_expansion",
]
FULL = "ORION_FULL"
BASELINES = [s for s in ALL_SYSTEMS[:7] if s != FULL]

# Gold integration verdict bucket used by some metrics
GOLD_KEYS = [
    "referent_relation", "construct_relation", "measurement_relation",
    "context_relation", "polarity_relation", "modality_relation",
    "attribution_relation", "discourse_relation", "mapping_relation",
    "contradiction_verdict", "integration_verdict",
]


def load_gold(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and "annotations" in payload:
        return payload["annotations"]
    raise ValueError(f"unrecognized gold shape: {path}")


def pred_metrics(gold_case: dict, rec: dict) -> dict:
    """Convert one checkpoint record to a metrics-style prediction dict."""
    pred = {k: str(rec.get(k, "UNRESOLVED")) for k in GOLD_KEYS}
    pred["preservation_conditions"] = list(rec.get("preservation_conditions", []))
    pred["recoverability_target"] = list(rec.get("recoverability_target", []))
    return pred


def main() -> int:
    if not CHECKPOINT.exists():
        print(f"checkpoint not found: {CHECKPOINT}")
        return 1
    OUT.mkdir(parents=True, exist_ok=True)

    gold = load_gold(GOLD)
    by_case = {str(a.get("case_id")): a for a in gold}

    records: list[dict] = [
        json.loads(line) for line in CHECKPOINT.read_text().splitlines() if line.strip()
    ]
    print(f"{len(records)} checkpoint records, {len(gold)} gold cases")

    # Group predictions into per-(system,seed) lists aligned with gold order.
    per_run: dict[tuple[str, int], list[dict]] = defaultdict(list)
    per_run_cases: dict[tuple[str, int], list[str]] = defaultdict(list)

    # Ignore FAILED checkpoint lines (they are UNRESOLVED placeholders and would
    # poison metrics as abstentions).  A run is only complete when every case is a
    # real prediction (notes=seed=...).  We keep every (system,seed) that has all
    # 32 cases mapped to some explicit prediction.
    for rec in records:
        key = (rec["sid"], int(rec["seed"]))
        case = by_case.get(rec["case_id"])
        if case is None:
            continue
        per_run[key].append(pred_metrics(case, rec))
        per_run_cases[key].append(rec["case_id"])

    # Score each (system, seed).
    run_metrics: dict[str, dict[int, dict[str, float]]] = defaultdict(dict)
    for (sid, seed), preds in sorted(per_run.items()):
        # Align melded predictions to gold order by case_id.
        ordered = {c: p for c, p in zip(per_run_cases[(sid, seed)], preds)}
        gold_aligned = [{**g, **ordered[g["case_id"]]} for g in gold if g["case_id"] in ordered]
        if len(gold_aligned) != len(gold):
            print(f"  SKIP {sid} seed={seed}: {len(gold_aligned)}/{len(gold)} cases")
            continue
        m = compute_all_metrics(gold, gold_aligned)
        run_metrics[sid][seed] = m

    complete_systems = {s for s, d in run_metrics.items() if len(d) == 5}
    print(f"systems with all 5 seeds: {len(complete_systems)}/15")
    for s in ALL_SYSTEMS:
        print(f"  {s}: {len(run_metrics.get(s, {}))}/5 seeds")

    # Raw per-(system,seed) metrics dump.
    (OUT / "metrics_by_system_seed.json").write_text(
        json.dumps({s: {str(se): m for se, m in d.items()}
                    for s, d in run_metrics.items()}, indent=2),
        encoding="utf-8")

    # Aggregate across seeds.
    aggregates: dict[str, dict] = {}
    for sid, by_seed in run_metrics.items():
        if len(by_seed) < 2:
            continue
        metrics_list = [by_seed[se] for se in sorted(by_seed)]
        aggregates[sid] = stats.aggregate_across_runs(metrics_list)
    (OUT / "aggregates.json").write_text(
        json.dumps(aggregates, indent=2), encoding="utf-8")

    # ── Hypothesis tests (only if FULL has all 5 seeds) ──────────────────────
    hypotheses: dict = {"H1a_superiority": {}, "H1b_non_inferiority": {},
                        "H2_recoverability": {}, "H3_obstruction": {},
                        "H4_ablation_direction": {}}

    if FULL in run_metrics and len(run_metrics[FULL]) == 5:
        fm_full = [run_metrics[FULL][se].get("false_merge_rate", 0.0)
                   for se in range(5)]
        vi_full = [run_metrics[FULL][se].get("valid_integration_rate", 0.0)
                   for se in range(5)]
        best_fm, best_fm_name = 1.1, None
        for b in BASELINES:
            if b not in run_metrics or len(run_metrics[b]) < 5:
                continue
            fm_b = [run_metrics[b][se].get("false_merge_rate", 0.0) for se in range(5)]
            mean_b = sum(fm_b) / len(fm_b)
            if mean_b < best_fm:
                best_fm, best_fm_name = mean_b, b
        if best_fm_name:
            fm_best = [run_metrics[best_fm_name][se].get("false_merge_rate", 0.0)
                       for se in range(5)]
            diff = [a - b for a, b in zip(fm_best, fm_full)]
            lo, hi = stats.percentile(sorted(diff), 2.5), stats.percentile(sorted(diff), 97.5)
            mean_diff = sum(diff) / len(diff)
            hypotheses["H1a_superiority"] = {
                "delta": 0.05,
                "strongest_baseline": best_fm_name,
                "full_fm_mean": sum(fm_full) / len(fm_full),
                "baseline_fm_mean": sum(fm_best) / len(fm_best),
                "bootstrap_ci_95": [lo, hi],
                "effect_mean": mean_diff,
                "superior": mean_diff >= 0.05,
            }

        # H1b: non-inferiority on VI.
        if best_fm_name:
            vi_best = [run_metrics[best_fm_name][se].get("valid_integration_rate", 0.0)
                       for se in range(5)]
            diff = [full - base for full, base in zip(vi_full, vi_best)]
            lo, hi = stats.percentile(sorted(diff), 2.5), stats.percentile(sorted(diff), 97.5)
            mean_diff = sum(diff) / len(diff)
            hypotheses["H1b_non_inferiority"] = {
                "delta": 0.03,
                "strongest_baseline": best_fm_name,
                "full_vi_mean": sum(vi_full) / len(vi_full),
                "baseline_vi_mean": sum(vi_best) / len(vi_best),
                "bootstrap_ci_95": [lo, hi],
                "effect_mean": mean_diff,
                "non_inferior": mean_diff >= -0.03,
            }

        # H2: recoverability.
        if FULL in aggregates:
            rec = aggregates[FULL].get("source_recoverability_rate", {})
            hypotheses["H2_recoverability"] = {
                "target": 0.80,
                "mean": rec.get("mean"),
                "ci_95": rec.get("ci95"),
                "confirmed": (rec.get("mean") or 0.0) >= 0.80,
            }

        # H3: obstruction precision/recall.
        if FULL in aggregates:
            op = aggregates[FULL].get("obstruction_precision", {})
            orr = aggregates[FULL].get("obstruction_recall", {})
            hypotheses["H3_obstruction"] = {
                "precision_target": 0.70, "precision_mean": op.get("mean"),
                "recall_target": 0.50, "recall_mean": orr.get("mean"),
                "confirmed_p": (op.get("mean") or 0.0) >= 0.70,
                "confirmed_r": (orr.get("mean") or 0.0) >= 0.50,
            }

        # H4: ablation direction (degradation of fm_rate relative to FULL).
        ablations = [s for s in ALL_SYSTEMS if s.startswith("ORION_no_")]
        adj = []
        for a in ablations:
            if a not in run_metrics or len(run_metrics[a]) < 5:
                continue
            fm_a = [run_metrics[a][se].get("false_merge_rate", 0.0) for se in range(5)]
            fm_f = [run_metrics[FULL][se].get("false_merge_rate", 0.0) for se in range(5)]
            diff_mean = sum(b - a for a, b in zip(fm_f, fm_a)) / 5
            adj.append({"ablation": a, "fm_diff_vs_full": diff_mean,
                        "degraded": diff_mean > 0.001})
        hypotheses["H4_ablation_direction"] = {
            "ablations": adj,
            "any_ablation_degrading": any(x["degraded"] for x in adj),
        }

    (OUT / "hypotheses.json").write_text(
        json.dumps(hypotheses, indent=2), encoding="utf-8")

    # ── LaTeX report table ────────────────────────────────────────────────────
    latex_lines = ["\\begin{tabular}{lrrrrr}",
                   "\\toprule",
                   "System & $\\overline{\\text{FM}}$ & CI & $\\overline{\\text{VI}}$ & CI & $n$ \\\\",
                   "\\midrule"]
    for sid in ALL_SYSTEMS:
        agg = aggregates.get(sid)
        if not agg:
            continue
        fm = agg.get("fm").get("mean", float("nan")) if "fm" in agg else agg.get("false_merge_rate", {}).get("mean", float("nan"))
        # normalize key names to align with aggregate output
        fm = agg.get("false_merge_rate", {}).get("mean", float("nan"))
        fm_ci = agg.get("false_merge_rate", {}).get("ci95", [float("nan"), float("nan")])
        vi = agg.get("valid_integration_rate", {}).get("mean", float("nan"))
        vi_ci = agg.get("valid_integration_rate", {}).get("ci95", [float("nan"), float("nan")])
        n = agg.get("valid_integration_rate", {}).get("n_runs", 0)
        latex_lines.append(
            f"{sid} & {fm:.3f} & [{fm_ci[0]:.3f}, {fm_ci[1]:.3f}] & "
            f"{vi:.3f} & [{vi_ci[0]:.3f}, {vi_ci[1]:.3f}] & {n} \\\\")
    latex_lines.append("\\bottomrule")
    latex_lines.append("\\end{tabular}")
    (OUT / "report_table_latex.tex").write_text("\n".join(latex_lines), encoding="utf-8")

    print("\nWrote analysis outputs to", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())