from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Mapping, Sequence

# Frozen hidden-cause family order from PROTOCOL / PROTECTED_SUITE_V1.
FAMILIES: tuple[str, ...] = (
    "RETRIEVAL_MISS",
    "ROUTING_PLANNING_MISS",
    "IMPLEMENTATION_BUG",
    "ENVIRONMENT_DEPENDENCY_TOOL_FAILURE",
    "EVALUATOR_METRIC_BUG",
    "REPRESENTATION_GAP",
    "MEASUREMENT_SPECIFICATION_GAP",
    "METHOD_BASIS_GAP",
)

SOURCE = "papers/orion-15-self-orion/evidence/glm-5.2-attribution/results.jsonl"
CAMPAIGN_ID = "p5-glm-5.2-attribution-v1"
AUTHORITY = (
    "These tables are deterministic presentation artifacts of the archived "
    "glm-5.2 hidden-cause *attribution* campaign (n=24, single model, single run). "
    "They do not establish protected fresh-transfer improvement, matched "
    "baseline/ablation results, specialist-regression trajectories, or "
    "intervention-backed repair. Missing campaign axes are recorded as "
    "CANNOT_CHECK rather than filled with proxies."
)

PRESERVED_ERRORS: tuple[tuple[str, str, str], ...] = (
    ("P5-HC-002", "RETRIEVAL_MISS", "REPRESENTATION_GAP"),
    ("P5-HC-012", "ENVIRONMENT_DEPENDENCY_TOOL_FAILURE", "IMPLEMENTATION_BUG"),
    ("P5-HC-018", "REPRESENTATION_GAP", "METHOD_BASIS_GAP"),
)


def _dump(path: Path, payload: Mapping[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _load_results(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise ValueError(f"{path}:{line_no} is not a JSON object")
        rows.append(row)
    if len(rows) != 24:
        raise ValueError(f"archived attribution campaign must contain 24 rows, got {len(rows)}")
    return rows


def _family_metrics(rows: Sequence[Mapping[str, object]]) -> dict[str, dict[str, object]]:
    out: dict[str, dict[str, object]] = {}
    for family in FAMILIES:
        family_rows = [r for r in rows if r.get("gold_root_cause") == family]
        total = len(family_rows)
        tp = sum(
            1
            for r in rows
            if r.get("gold_root_cause") == family
            and r.get("attributed_root_cause") == family
        )
        fp = sum(
            1
            for r in rows
            if r.get("gold_root_cause") != family
            and r.get("attributed_root_cause") == family
        )
        fn = sum(
            1
            for r in rows
            if r.get("gold_root_cause") == family
            and r.get("attributed_root_cause") != family
        )
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        out[family] = {
            "cases": [str(r["case_id"]) for r in family_rows],
            "correct": tp,
            "f1": f1,
            "fn": fn,
            "fp": fp,
            "precision": precision,
            "recall": recall,
            "total": total,
            "tp": tp,
        }
    return out


def generate(rows: Sequence[Mapping[str, object]], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    incorrect = [r for r in rows if r.get("correct") is not True]
    preserved = tuple(
        (str(r["case_id"]), str(r["gold_root_cause"]), str(r["attributed_root_cause"]))
        for r in incorrect
    )
    if preserved != PRESERVED_ERRORS:
        raise ValueError(f"archived error set drifted: {preserved!r}")

    confusion: dict[str, dict[str, int]] = {}
    for gold in FAMILIES:
        counts: Counter[str] = Counter()
        for row in rows:
            if row.get("gold_root_cause") == gold:
                counts[str(row["attributed_root_cause"])] += 1
        confusion[gold] = {f"attributed_{label}": n for label, n in sorted(counts.items())}

    family_metrics = _family_metrics(rows)
    correct_n = sum(1 for r in rows if r.get("correct") is True)
    correct_with_no = [
        r for r in rows if r.get("correct") is True and r.get("intervention_prediction") == "NO"
    ]
    prompt_tokens = sum(int(r.get("prompt_tokens") or 0) for r in rows)
    completion_tokens = sum(int(r.get("completion_tokens") or 0) for r in rows)
    latencies = [float(r["latency_seconds"]) for r in rows if r.get("latency_seconds") is not None]
    avg_latency = (sum(latencies) / len(latencies)) if latencies else 0.0
    confidence = Counter(str(r.get("confidence")) for r in rows)
    interventions = Counter(str(r.get("intervention_prediction")) for r in rows)
    macro_f1 = sum(float(m["f1"]) for m in family_metrics.values()) / len(family_metrics)

    common = {
        "campaign_id": CAMPAIGN_ID,
        "empirical_authority": "CANNOT_CHECK",
        "issue": 102,
        "model": "glm-5.2",
        "n_cases": 24,
        "paper_id": "P5",
        "source_results": SOURCE,
    }

    _dump(
        out_dir / "TABLE_P5_2_REPLAY_VS_FRESH.json",
        {
            **common,
            "schema_version": "orion.p5.table.replay-vs-fresh.v1",
            "table_id": "P5-2",
            "status": "CANNOT_CHECK",
            "reason": (
                "Archived glm-5.2 rows contain attribution labels only; no motivating-replay "
                "score, fresh-transfer score, or harmful-transfer flag is present."
            ),
            "rows": [],
            "required_fields_absent": [
                "motivating_replay_delta",
                "fresh_transfer_delta",
                "harmful_transfer",
            ],
        },
    )

    _dump(
        out_dir / "TABLE_P5_3_HIDDEN_CAUSE_ATTRIBUTION.json",
        {
            **common,
            "schema_version": "orion.p5.hidden-cause-attribution.v1",
            "table_id": "P5-3",
            "status": "ARCHIVED_ATTRIBUTION_ONLY",
            "summary_metrics": {
                "accuracy": correct_n / len(rows),
                "avg_latency_seconds": avg_latency,
                "correct_attributions": correct_n,
                "errors": sum(1 for r in rows if r.get("error") not in (None, "")),
                "false_method_change_rate": (len(correct_with_no) / correct_n) if correct_n else 0.0,
                "incorrect_attributions": len(incorrect),
                "macro_f1": macro_f1,
                "total_cases": len(rows),
                "total_tokens": prompt_tokens + completion_tokens,
            },
            "confidence_distribution": dict(sorted(confidence.items())),
            "confusion_matrix": confusion,
            "incorrect_cases": [
                {
                    "attributed": gold_attr[2],
                    "case_id": gold_attr[0],
                    "confidence": next(
                        str(r.get("confidence")) for r in rows if r.get("case_id") == gold_attr[0]
                    ),
                    "gold": gold_attr[1],
                }
                for gold_attr in PRESERVED_ERRORS
            ],
            "intervention_predictions": dict(sorted(interventions.items())),
            "per_family_metrics": family_metrics,
            "limitations": (
                "Single-model single-run evaluation without repetition confidence intervals. "
                "Full campaign requires protected fresh-transfer execution with matched baselines."
            ),
        },
    )

    _dump(
        out_dir / "TABLE_P5_4_LONGITUDINAL.json",
        {
            **common,
            "schema_version": "orion.p5.table.longitudinal.v1",
            "table_id": "P5-4",
            "status": "CANNOT_CHECK",
            "reason": (
                "Attribution archive is a one-shot 24-case screen; no self-improvement round "
                "index or motivating/fresh trajectory exists."
            ),
            "rows": [],
        },
    )
    _dump(
        out_dir / "TABLE_P5_5_IMPROVEMENT_INTEGRITY_FRONTIER.json",
        {
            **common,
            "schema_version": "orion.p5.table.integrity-frontier.v1",
            "table_id": "P5-5",
            "status": "CANNOT_CHECK",
            "reason": (
                "No matched baseline or ablation campaign is archived; glm-5.2 attribution "
                "cannot populate an improvement-vs-integrity frontier."
            ),
            "rows": [],
        },
    )
    _dump(
        out_dir / "TABLE_P5_6_FAILURE_RECURRENCE.json",
        {
            **common,
            "schema_version": "orion.p5.table.failure-recurrence.v1",
            "table_id": "P5-6",
            "status": "CANNOT_CHECK",
            "reason": (
                "No negative-history on/off rounds are archived. The three attribution errors "
                "are preserved identities, not recurrence counts."
            ),
            "preserved_attribution_errors": [
                {"case_id": c, "gold": g, "attributed": a} for c, g, a in PRESERVED_ERRORS
            ],
            "rows": [],
        },
    )
    _dump(
        out_dir / "TABLE_P5_7_ATTRIBUTION_COST.json",
        {
            **common,
            "schema_version": "orion.p5.table.attribution-cost.v1",
            "table_id": "P5-7",
            "status": "ARCHIVED_ATTRIBUTION_ONLY",
            "note": (
                "Cost of the archived attribution screen only — not time-to-protected-"
                "validated-improvement."
            ),
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "avg_latency_seconds": avg_latency,
            "n_cases": len(rows),
            "endpoint": "http://127.0.0.1:8765",
        },
    )

    md = [
        "# ORION-P5 glm-5.2 attribution publication tables V1",
        "",
        AUTHORITY,
        "",
        "## Table P5-2 — fresh-transfer vs motivating replay",
        "",
        "Status: `CANNOT_CHECK`. Archived rows have no replay/fresh deltas.",
        "",
        "## Table P5-3 — hidden-cause attribution confusion",
        "",
        f"Accuracy {correct_n}/{len(rows)} = {correct_n / len(rows):.4f}; macro-F1 {macro_f1:.4f}.",
        "Preserved errors: P5-HC-002, P5-HC-012, P5-HC-018.",
        "",
        "| Gold family | n | correct | precision | recall | F1 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for family, block in family_metrics.items():
        md.append(
            f"| `{family}` | {block['total']} | {block['correct']} | "
            f"{float(block['precision']):.4f} | {float(block['recall']):.4f} | "
            f"{float(block['f1']):.4f} |"
        )
    md += [
        "",
        "| Case | Gold | Attributed |",
        "|---|---|---|",
        "| `P5-HC-002` | `RETRIEVAL_MISS` | `REPRESENTATION_GAP` |",
        "| `P5-HC-012` | `ENVIRONMENT_DEPENDENCY_TOOL_FAILURE` | `IMPLEMENTATION_BUG` |",
        "| `P5-HC-018` | `REPRESENTATION_GAP` | `METHOD_BASIS_GAP` |",
        "",
        "## Table P5-4 — longitudinal specialist regression",
        "",
        "Status: `CANNOT_CHECK`. No improvement-round trajectory is archived.",
        "",
        "## Table P5-5 — improvement vs integrity frontier",
        "",
        "Status: `CANNOT_CHECK`. No matched baseline/ablation results are archived.",
        "",
        "## Table P5-6 — recognized-failure recurrence",
        "",
        "Status: `CANNOT_CHECK`. No negative-history on/off rounds are archived.",
        "",
        "## Table P5-7 — attribution-campaign cost",
        "",
        f"Prompt tokens {prompt_tokens}; completion tokens {completion_tokens}; "
        f"total {prompt_tokens + completion_tokens}; mean latency {avg_latency:.4f}s.",
        "This is not cost-to-protected-validated-improvement.",
        "",
        f"**Authority boundary.** {AUTHORITY}",
        "",
    ]
    (out_dir / "P5_ATTRIBUTION_TABLES_V1.md").write_text("\n".join(md), encoding="utf-8")
    (out_dir / "README.md").write_text(
        "\n".join(
            [
                "# P5 glm-5.2 attribution publication tables",
                "",
                AUTHORITY,
                "",
                "Rebuild (no model call, no suite execution):",
                "",
                "```bash",
                "make paper05-attribution-publication",
                "```",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate P5-2..P5-7 tables from archived glm-5.2 attribution results"
    )
    parser.add_argument("--results", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    generate(_load_results(args.results), args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
