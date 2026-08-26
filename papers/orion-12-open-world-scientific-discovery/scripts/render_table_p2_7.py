#!/usr/bin/env python3
"""Render Table P2-7 (Wide vs Deep external performance comparison).

This table is generated from the archived AutoResearchBench Wide and Deep probe
results and never hand-transcribed.

Usage::

    python3 papers/paper-02-open-world-scientific-discovery/scripts/render_table_p2_7.py            # write
    python3 papers/paper-02-open-world-scientific-discovery/scripts/render_table_p2_7.py --check    # verify
    python3 papers/paper-02-open-world-scientific-discovery/scripts/render_table_p2_7.py --stdout   # print

Standard library only. Exit codes: 0 ok, 1 drift under ``--check``, 2 missing input.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PAPER_ROOT = Path(__file__).resolve().parents[1]
WIDE_PATH = PAPER_ROOT / "evidence" / "external_results" / "AUTORESEARCHBENCH_WIDE_KEYLESS_PROBE_V1.json"
DEEP_PATH = PAPER_ROOT / "evidence" / "external_results" / "AUTORESEARCHBENCH_DEEP_ID_PROBE_V1.json"
TABLE_PATH = PAPER_ROOT / "protocol" / "TABLE_P2-7_wide_deep_comparison.md"


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


def render(wide: dict, deep: dict) -> str:
    lines: list[str] = []
    add = lines.append

    add("# Table P2-7: AutoResearchBench Wide vs Deep external performance comparison")
    add("")
    add("<!-- GENERATED FILE - DO NOT EDIT BY HAND.")
    add("     Regenerate with:")
    add("       python3 papers/paper-02-open-world-scientific-discovery/scripts/render_table_p2_7.py")
    add("     Sources: evidence/external_results/AUTORESEARCHBENCH_WIDE_KEYLESS_PROBE_V1.json")
    add("              evidence/external_results/AUTORESEARCHBENCH_DEEP_ID_PROBE_V1.json -->")
    add("")

    # Schema versions and authority
    add("## Probe metadata")
    add("")
    add("| Benchmark | Authority | Candidate | Claim scope |")
    add("| --- | --- | --- | --- |")
    add(f"| {cell(wide['benchmark'])} | `{cell(wide['authority'])}` | {cell(wide['candidate'])} | {cell(wide['claim_scope'])} |")
    add(f"| {cell(deep['benchmark'])} | `{cell(deep['authority'])}` | {cell(deep['candidate'])} | {cell(deep['claim_scope'])} |")
    add("")

    # Coverage
    add("## Coverage")
    add("")
    add("| Benchmark | Tasks attempted | Records evaluated | Provider requests | Schema version |")
    add("| --- | --- | --- | --- | --- |")
    add(f"| {cell(wide['benchmark'])} | {cell(wide.get('coverage', {}).get('tasks_attempted', wide.get('tasks_attempted', 'n/a')))} | {cell(wide.get('coverage', {}).get('official_records_evaluated', wide.get('official_records_evaluated', 'n/a')))} | {cell(wide.get('coverage', {}).get('provider_requests', wide.get('provider_requests', 'n/a')))} | `{cell(wide['schema_version'])}` |")
    add(f"| {cell(deep['benchmark'])} | {cell(deep.get('tasks_attempted', 'n/a'))} | {cell(deep.get('scorable_records', deep.get('official_records_evaluated', 'n/a')))} | {cell(deep.get('provider_requests', 'n/a'))} | `{cell(deep['schema_version'])}` |")
    add("")

    # Wide official metrics
    add("## Wide official metrics (400 tasks)")
    add("")
    add("The Wide benchmark uses the official deterministic scorer with IoU, recall, and precision metrics.")
    add("")
    wide_metrics = wide.get("official_metrics", {})
    add("| Metric | Value |")
    add("| --- | --- |")
    add(f"| Average IoU | {cell(wide_metrics.get('avg_iou', 'n/a'))} |")
    add(f"| Average recall | {cell(wide_metrics.get('avg_recall', 'n/a'))} |")
    add(f"| Average precision | {cell(wide_metrics.get('avg_precision', 'n/a'))} |")
    add(f"| IoU range | [{cell(wide_metrics.get('iou_min', 'n/a'))}, {cell(wide_metrics.get('iou_max', 'n/a'))}] |")
    add(f"| Recall range | [{cell(wide_metrics.get('recall_min', 'n/a'))}, {cell(wide_metrics.get('recall_max', 'n/a'))}] |")
    add("")

    # Deep metrics
    add("## Deep ID-probe metrics (600 tasks)")
    add("")
    add("The Deep benchmark probe uses deterministic target identification (not the official title judge).")
    add("")
    add("| Metric | Value |")
    add("| --- | --- |")
    add(f"| Target hit rate | {cell(deep.get('target_hit_rate', 'n/a'))} |")
    add(f"| Mean predicted count | {cell(deep.get('mean_predicted_count', 'n/a'))} |")
    add(f"| Scorable records | {cell(deep.get('scorable_records', 'n/a'))} |")
    add("")

    # Provider status
    add("## Provider status counts")
    add("")
    add("| Benchmark | OK | RATE_LIMITED | SERVICE_ERROR |")
    add("| --- | --- | --- | --- |")
    wide_status = wide.get('provider_status_counts', {})
    deep_status = deep.get('provider_status_counts', {})
    add(f"| Wide | {cell(wide_status.get('OK', 'n/a'))} | {cell(wide_status.get('RATE_LIMITED', 'n/a'))} | {cell(wide_status.get('SERVICE_ERROR', 'n/a'))} |")
    add(f"| Deep | {cell(deep_status.get('OK', 'n/a'))} | {cell(deep_status.get('RATE_LIMITED', 'n/a'))} | {cell(deep_status.get('SERVICE_ERROR', 'n/a'))} |")
    add("")

    # Interpretation
    add("## Interpretation")
    add("")
    add("### Wide probe")
    wide_interpret = wide.get("interpretation", {})
    if wide_interpret:
        completed = wide_interpret.get("completed")
        if completed:
            add(f"Completed: {cell(completed)}")
            add("")
        not_claimed = wide_interpret.get("not_claimed", [])
        if not_claimed:
            add("Not claimed:")
            for item in not_claimed:
                add(f"- {cell(item)}")
    else:
        add("*No explicit interpretation field in source JSON*")
    add("")
    add("### Deep probe")
    deep_interpret = deep.get("interpretation", {})
    if deep_interpret:
        completed = deep_interpret.get("completed")
        if completed:
            add(f"Completed: {cell(completed)}")
            add("")
        not_claimed = deep_interpret.get("not_claimed", [])
        if not_claimed:
            add("Not claimed:")
            for item in not_claimed:
                add(f"- {cell(item)}")
    else:
        add("*No explicit interpretation field in source JSON. Deep probe authority is `DETERMINISTIC_DEEP_ID_EXTERNAL_PROBE`, which is a deterministic target-ID probe, not the official Deep title judge. A separate official-judge archive exists as `evidence/external_results/DEEP_OFFICIAL_ARCHIVE_V1.json` and is not this table's Deep row.*")
    add("")

    # Content bindings
    add("## Content integrity hashes (representative)")
    add("")
    add("Wide probe content bindings:")
    add(f"- Candidate output SHA256: `{cell(wide.get('content_bindings', {}).get('candidate_output_sha256', 'n/a')[:32])}\u2026`")
    add(f"- Official evaluation SHA256: `{cell(wide.get('content_bindings', {}).get('official_evaluation_sha256', 'n/a')[:32])}\u2026`")
    add("")
    add("Deep probe content bindings:")
    add(f"- Evaluation SHA256: `{cell(deep.get('evaluation_sha256', 'n/a')[:32])}\u2026`")
    add(f"- Trace SHA256: `{cell(deep.get('trace_sha256', 'n/a')[:32])}\u2026`")
    add("")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the committed table differs from a fresh render")
    parser.add_argument("--stdout", action="store_true", help="print the rendered table instead of writing it")
    args = parser.parse_args(argv)

    if not WIDE_PATH.exists():
        print(f"missing Wide probe input: {WIDE_PATH}", file=sys.stderr)
        return 2
    if not DEEP_PATH.exists():
        print(f"missing Deep probe input: {DEEP_PATH}", file=sys.stderr)
        return 2

    wide_data = json.loads(WIDE_PATH.read_text(encoding="utf-8"))
    deep_data = json.loads(DEEP_PATH.read_text(encoding="utf-8"))
    rendered = render(wide_data, deep_data)

    if args.stdout:
        sys.stdout.write(rendered)
        return 0

    if args.check:
        if not TABLE_PATH.exists():
            print(f"missing rendered table: {TABLE_PATH}", file=sys.stderr)
            return 1
        current = TABLE_PATH.read_text(encoding="utf-8")
        if current != rendered:
            print("TABLE_P2-7 is stale; rerun render_table_p2_7.py", file=sys.stderr)
            return 1
        print("TABLE_P2-7 matches source probe JSON files")
        return 0

    TABLE_PATH.write_text(rendered, encoding="utf-8")
    print(f"wrote {TABLE_PATH} ({len(rendered)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
