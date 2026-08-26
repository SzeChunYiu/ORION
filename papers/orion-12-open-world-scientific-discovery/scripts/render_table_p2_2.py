#!/usr/bin/env python3
"""Render Table P2-2 (baselines + ablations with cost metrics).

This table is generated from the archived RESULTS_SUMMARY_V1.json and
OFFLINE_RUN_MANIFEST_V1.json and never hand-transcribed.

Usage::

    python3 papers/paper-02-open-world-scientific-discovery/scripts/render_table_p2_2.py            # write
    python3 papers/paper-02-open-world-scientific-discovery/scripts/render_table_p2_2.py --check    # verify
    python3 papers/paper-02-open-world-scientific-discovery/scripts/render_table_p2_2.py --stdout   # print

Standard library only. Exit codes: 0 ok, 1 drift under ``--check``, 2 missing input.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PAPER_ROOT = Path(__file__).resolve().parents[1]
RESULTS_PATH = PAPER_ROOT / "evidence" / "offline_results" / "RESULTS_SUMMARY_V1.json"
MANIFEST_PATH = PAPER_ROOT / "protocol" / "OFFLINE_RUN_MANIFEST_V1.json"
TABLE_PATH = PAPER_ROOT / "protocol" / "TABLE_P2-2_baseline_ablation_cost.md"


# System display names
SYSTEM_LABELS = {
    "orion_full": "ORION full",
    "protocol_driven_systematic_review": "Protocol-driven systematic review",
    "sparse_dense_hybrid": "Sparse+dense hybrid",
    "one_pass_rag": "One-pass RAG",
    "bm25_keyword": "BM25/keyword",
    "dense_retrieval": "Dense-route comparator",
    "agentic_single_route": "Agentic single route",
    "no_route_independence_check": "Ablation: no route-independence check",
    "no_question_conditioned_read_ledger": "Ablation: no question-conditioned read ledger",
    "route_stop_can_close_task": "Ablation: route stop can close task",
    "no_unavailable_route_open_state": "Ablation: no unavailable-route open state",
    "coverage_diagnostic_controls_stopping": "Ablation: coverage diagnostic controls stopping",
    "no_content_identity_dedup": "Ablation: no content-identity dedup",
    "adaptive_multiroute_exploratory": "Exploratory: adaptive multiroute",
}


def cell(value: object) -> str:
    """Render one value as a pipe-table cell: never empty, never pipe-breaking."""
    if value is None:
        return "n/a"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, (list, tuple)):
        return "; ".join(cell(v) for v in value) if value else "n/a"
    text = str(value).replace("|", "\\|").replace("\n", " ").strip()
    return text or "n/a"


def render(results: dict, manifest: dict) -> str:
    lines: list[str] = []
    add = lines.append

    add("# Table P2-2: Baselines and ablations with cost metrics")
    add("")
    add("<!-- GENERATED FILE - DO NOT EDIT BY HAND.")
    add("     Regenerate with:")
    add("       python3 papers/paper-02-open-world-scientific-discovery/scripts/render_table_p2_2.py")
    add("     Sources: evidence/offline_results/RESULTS_SUMMARY_V1.json")
    add("              protocol/OFFLINE_RUN_MANIFEST_V1.json -->")
    add("")

    # Metadata
    add("## Metadata")
    add("")
    add("| Field | Value |")
    add("| --- | --- |")
    add(f"| Analysis authority | `{cell(results['analysis_authority'])}` |")
    add(f"| Tasks (n) | {cell(results['frozen_run']['n_tasks'])} |")
    add(f"| Systems (total) | {cell(results['frozen_run']['n_systems'])} |")
    add(f"| Result records | {cell(results['frozen_run']['n_result_records'])} |")
    add(f"| Results SHA256 | `{cell(results['frozen_run']['record_digest_sha256'][:32])}\u2026` |")
    add("")

    # Resource limits from manifest
    resource_limits = manifest.get("resource_limits", {})
    add("## Resource limits (per-task budgets)")
    add("")
    add("| Resource | Limit |")
    add("| --- | --- |")
    add(f"| Max model tokens | {cell(resource_limits.get('max_model_tokens_per_task', 'n/a'))} |")
    add(f"| Max route calls | {cell(resource_limits.get('max_route_calls_per_task', 'n/a'))} |")
    add(f"| Max tool calls | {cell(resource_limits.get('max_tool_calls_per_task', 'n/a'))} |")
    add(f"| Max wall-clock seconds | {cell(resource_limits.get('max_wallclock_seconds_per_task', 'n/a'))} |")
    add("")

    # Baselines
    add("## Confirmatory baselines")
    add("")
    add("| System | Recall | Premature closure | Duplicate processing | Routes used | Legitimate rereads | Pass | Cannot check |")
    add("| --- | --- | --- | --- | --- | --- | --- | --- |")

    baselines = [
        "protocol_driven_systematic_review",
        "sparse_dense_hybrid",
        "one_pass_rag",
        "bm25_keyword",
        "dense_retrieval",
        "agentic_single_route",
    ]

    for system_id in baselines:
        sys_data = results["systems"].get(system_id, {})
        add(f"| {cell(SYSTEM_LABELS.get(system_id, system_id))} | "
            f"{cell(sys_data.get('mean_complete_gold_recall', 'n/a'))} | "
            f"{cell(sys_data.get('premature_task_closure_rate', 'n/a'))} | "
            f"{cell(sys_data.get('mean_duplicate_processing_rate', 'n/a'))} | "
            f"{cell(sys_data.get('mean_routes_used', 'n/a'))} | "
            f"{cell(sys_data.get('mean_legitimate_reread_count', 'n/a'))} | "
            f"{cell(sys_data.get('pass_rate', 'n/a'))} | "
            f"{cell(sys_data.get('cannot_check_rate', 'n/a'))} |")

    add("")

    # ORION full
    add("## Full ORION")
    add("")
    add("| System | Recall | Premature closure | Duplicate processing | Routes used | Legitimate rereads | Pass | Cannot check |")
    add("| --- | --- | --- | --- | --- | --- | --- | --- |")

    orion_data = results["systems"].get("orion_full", {})
    add(f"| {cell(SYSTEM_LABELS.get('orion_full', 'orion_full'))} | "
        f"{cell(orion_data.get('mean_complete_gold_recall', 'n/a'))} | "
        f"{cell(orion_data.get('premature_task_closure_rate', 'n/a'))} | "
        f"{cell(orion_data.get('mean_duplicate_processing_rate', 'n/a'))} | "
        f"{cell(orion_data.get('mean_routes_used', 'n/a'))} | "
        f"{cell(orion_data.get('mean_legitimate_reread_count', 'n/a'))} | "
        f"{cell(orion_data.get('pass_rate', 'n/a'))} | "
        f"{cell(orion_data.get('cannot_check_rate', 'n/a'))} |")
    add("")

    # Ablations
    add("## Safety ablations")
    add("")
    add("| System | Recall | Premature closure | Duplicate processing | Routes used | Legitimate rereads | Pass | Cannot check |")
    add("| --- | --- | --- | --- | --- | --- | --- | --- |")

    ablations = [
        "no_route_independence_check",
        "no_question_conditioned_read_ledger",
        "route_stop_can_close_task",
        "no_unavailable_route_open_state",
        "coverage_diagnostic_controls_stopping",
        "no_content_identity_dedup",
    ]

    for system_id in ablations:
        sys_data = results["systems"].get(system_id, {})
        add(f"| {cell(SYSTEM_LABELS.get(system_id, system_id))} | "
            f"{cell(sys_data.get('mean_complete_gold_recall', 'n/a'))} | "
            f"{cell(sys_data.get('premature_task_closure_rate', 'n/a'))} | "
            f"{cell(sys_data.get('mean_duplicate_processing_rate', 'n/a'))} | "
            f"{cell(sys_data.get('mean_routes_used', 'n/a'))} | "
            f"{cell(sys_data.get('mean_legitimate_reread_count', 'n/a'))} | "
            f"{cell(sys_data.get('pass_rate', 'n/a'))} | "
            f"{cell(sys_data.get('cannot_check_rate', 'n/a'))} |")
    add("")

    # Exploratory
    add("## Exploratory comparator (non-confirmatory)")
    add("")
    add("| System | Recall | Premature closure | Duplicate processing | Routes used | Legitimate rereads | Pass | Cannot check |")
    add("| --- | --- | --- | --- | --- | --- | --- | --- |")

    exploratory_data = results["systems"].get("adaptive_multiroute_exploratory", {})
    add(f"| {cell(SYSTEM_LABELS.get('adaptive_multiroute_exploratory', 'adaptive_multiroute_exploratory'))} | "
        f"{cell(exploratory_data.get('mean_complete_gold_recall', 'n/a'))} | "
        f"{cell(exploratory_data.get('premature_task_closure_rate', 'n/a'))} | "
        f"{cell(exploratory_data.get('mean_duplicate_processing_rate', 'n/a'))} | "
        f"{cell(exploratory_data.get('mean_routes_used', 'n/a'))} | "
        f"{cell(exploratory_data.get('mean_legitimate_reread_count', 'n/a'))} | "
        f"{cell(exploratory_data.get('pass_rate', 'n/a'))} | "
        f"{cell(exploratory_data.get('cannot_check_rate', 'n/a'))} |")
    add("")

    # Interpretation
    add("## Interpretation")
    add("")
    add(f"- Authority: `{results.get('analysis_authority', 'DESCRIPTIVE_ONLY')}` — no inferential claims are made from this n={results['frozen_run']['n_tasks']} offline campaign.")
    add(f"- Strongest confirmatory baseline: `{results.get('headline', {}).get('strongest_confirmatory_baseline', 'protocol_driven_systematic_review')}` with recall {results['systems'].get('protocol_driven_systematic_review', {}).get('mean_complete_gold_recall', 'n/a')}.")
    add(f"- ORION full recall advantage: +{results.get('headline', {}).get('orion_minus_strongest_baseline_recall', 'n/a')} over strongest baseline.")
    add(f"- ORION full premature-closure advantage: {results.get('headline', {}).get('orion_minus_strongest_baseline_premature_closure', 'n/a')} (negative = fewer premature closures).")
    add("- Cost metrics (routes used, legitimate rereads) are descriptive resource consumption from the frozen offline companion; wall-clock is intentionally fixed to zero, so these reflect algorithmic behavior, not empirical time.")
    add("")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the committed table differs from a fresh render")
    parser.add_argument("--stdout", action="store_true", help="print the rendered table instead of writing it")
    args = parser.parse_args(argv)

    if not RESULTS_PATH.exists():
        print(f"missing results input: {RESULTS_PATH}", file=sys.stderr)
        return 2
    if not MANIFEST_PATH.exists():
        print(f"missing manifest input: {MANIFEST_PATH}", file=sys.stderr)
        return 2

    results_data = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    manifest_data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    rendered = render(results_data, manifest_data)

    if args.stdout:
        sys.stdout.write(rendered)
        return 0

    if args.check:
        if not TABLE_PATH.exists():
            print(f"missing rendered table: {TABLE_PATH}", file=sys.stderr)
            return 1
        current = TABLE_PATH.read_text(encoding="utf-8")
        if current != rendered:
            print("TABLE_P2-2 is stale; rerun render_table_p2_2.py", file=sys.stderr)
            return 1
        print("TABLE_P2-2 matches source JSON files")
        return 0

    TABLE_PATH.write_text(rendered, encoding="utf-8")
    print(f"wrote {TABLE_PATH} ({len(rendered)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
