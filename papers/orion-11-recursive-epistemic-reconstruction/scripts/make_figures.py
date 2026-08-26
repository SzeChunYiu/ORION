#!/usr/bin/env python3
"""Generate the five required P1 publication figures from archived results.

Figures generated (matching issue #98 L124–128 verbatim specs):

* **P1-2 Main outcome:** root success by task family × system with uncertainty.
* **P1-3 Selectivity frontier:** false-reframe rate vs hidden-shift success.
* **P1-4 Reopening:** reopen precision/recall/F1 by dependency depth/family.
* **P1-5 Efficiency:** cost-to-success / success-cost Pareto frontier.
* **P1-6 Recursion stability:** invariant/trace error vs recursion depth.

All figures are generated deterministically from the frozen archive at
`results/raw/test_scored.jsonl`. Use ``--check`` to verify committed PDFs
are current (CI-able). Matplotlib is imported lazily with a clear install hint
if missing (it is an optional dependency under the ``plots`` extra).

The live arm (`orion_live_provider`) is included now that its 86 missing
cells have been recovered: the frozen archive carries 2880 scored records and
no CANNOT_CHECK record remains, so every system is plotted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

# Add src to path for imports
REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from orion.study.p1.statistics import (
    wilson_interval,
    H1_SUPERIORITY_MARGIN,
    H2_NON_INFERIORITY_MARGIN,
    PROTOCOL_CONFIDENCE,
)

PAPER = Path(__file__).resolve().parent.parent
RESULTS_DIR = PAPER / "results" / "raw"
ARCHIVE = RESULTS_DIR / "test_scored.jsonl"
OUTPUT_DIR = PAPER / "results" / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Figure output paths
#: PDF metadata that makes a figure a function of its data and nothing else.
#:
#: Matplotlib stamps a wall-clock ``CreationDate`` into every PDF it writes, so
#: two runs over identical records produced different bytes and a different
#: sha256. `manifest.json` therefore recorded when someone last ran the figure
#: pipeline rather than what the figures contain, and a real change to a figure
#: could not be told from a re-run --- every re-run rewrote the hash anyway.
#: Passing ``None`` omits the key. The rest of this module already set seeds and
#: font types "for reproducible output"; this is the field that was actually
#: making it irreproducible.
REPRODUCIBLE_PDF_METADATA = {"CreationDate": None}

FIGURES = {
    "P1-2": OUTPUT_DIR / "P1-2_main_outcome.pdf",
    "P1-3": OUTPUT_DIR / "P1-3_selectivity_frontier.pdf",
    "P1-4": OUTPUT_DIR / "P1-4_reopening.pdf",
    "P1-5": OUTPUT_DIR / "P1-5_efficiency.pdf",
    "P1-6": OUTPUT_DIR / "P1-6_recursion_stability.pdf",
}

MANIFEST_PATH = OUTPUT_DIR / "manifest.json"

# Systems to plot (exclude orion_live_provider which has CANNOT_CHECK records)
SYSTEMS_PLOTTED = [
    "static_react_tool_workflow",
    "tree_search_iterative_research",
    "arex_like_recursive_audit_followup",
    "scion_like_dependency_execution_plan",
    "iris_like_information_state_revision",
    "orion_full",
    "orion_without_explicit_W",
    "orion_without_explicit_M",
    "generic_retry_instead_of_typed_reframe",
    "full_reset_instead_of_dependency_reopen",
    "orion_without_mechanic_self_audit",
    "orion_live_provider",
]

# System display names
SYSTEM_LABELS = {
    "static_react_tool_workflow": "Static ReAct",
    "tree_search_iterative_research": "Tree Search",
    "arex_like_recursive_audit_followup": "AREX-like",
    "scion_like_dependency_execution_plan": "SCION-like",
    "iris_like_information_state_revision": "Iris-like",
    "orion_full": "ORION Full",
    "orion_without_explicit_W": "ORION no W",
    "orion_without_explicit_M": "ORION no M",
    "generic_retry_instead_of_typed_reframe": "Generic Retry",
    "full_reset_instead_of_dependency_reopen": "Full Reset",
    "orion_without_mechanic_self_audit": "ORION no Self-Audit",
    "orion_live_provider": "Live Provider (glm-5.2)",
}

# Task family display names
FAMILY_LABELS = {
    "hidden_parent_domain": "Hidden Domain",
    "hidden_representation_or_coordinate_system": "Hidden Representation",
    "hidden_decomposition_or_interface": "Hidden Decomposition",
    "hidden_measurement_or_operationalization": "Hidden Measurement",
    "evidence_only_negative_control": "Evidence Control",
    "execution_only_negative_control": "Execution Control",
}


def _import_matplotlib():
    """Lazily import matplotlib with a clear install hint if missing."""
    try:
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend

        # Set deterministic parameters for reproducible output
        import matplotlib.pyplot as plt
        import random

        # Fix random seeds for deterministic output
        random.seed(42)
        if hasattr(matplotlib, "rcParams"):
            matplotlib.rcParams["pdf.fonttype"] = 42  # Use TrueType fonts for portability
            matplotlib.rcParams["figure.dpi"] = 100
            matplotlib.rcParams["savefig.dpi"] = 300

        return plt
    except ImportError as e:
        print("ERROR: matplotlib is required for figure generation.", file=sys.stderr)
        print("Install with: uv pip install matplotlib", file=sys.stderr)
        print("Or: pip install matplotlib", file=sys.stderr)
        raise SystemExit(1) from e


def load_records() -> list[dict[str, Any]]:
    """Load all scored records from the archive."""
    if not ARCHIVE.exists():
        print(f"ERROR: Archive not found: {ARCHIVE}", file=sys.stderr)
        raise SystemExit(1)

    records = []
    with open(ARCHIVE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


def filter_cannot_check(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    """Filter out any CANNOT_CHECK records that remain in the archive.

    Returns (filtered_records, cannot_check_count). After the 2026-08-17
    live-provider recovery the archive carries zero CANNOT_CHECK records;
    the filter is kept so that an unexpected regeneration that reintroduces
    provider failures still degrades gracefully with the count reported in
    the manifest instead of silently plotting incomplete cells.
    """
    filtered = [r for r in records if r.get("status") != "CANNOT_CHECK"]
    cannot_check = len(records) - len(filtered)
    return filtered, cannot_check


def figure_p1_2_main_outcome(records: list[dict[str, Any]], plt) -> Path:
    """P1-2 Main outcome: root success by task family × system with uncertainty."""
    # Aggregate: for each system × family, compute root success rate with Wilson interval
    data = {}  # (system, family) -> [successes, total]
    for system in SYSTEMS_PLOTTED:
        for family in FAMILY_LABELS.keys():
            data[(system, family)] = [0, 0]

    for record in records:
        system = record.get("system_id")
        family = record.get("task_family")
        if system not in SYSTEMS_PLOTTED:
            continue
        if (system, family) not in data:
            continue
        data[(system, family)][1] += 1
        if record.get("root_success", False):
            data[(system, family)][0] += 1

    # Create grouped bar plot
    fig, ax = plt.subplots(figsize=(12, 6))

    families = list(FAMILY_LABELS.keys())
    n_families = len(families)
    n_systems = len(SYSTEMS_PLOTTED)
    bar_width = 0.8 / n_systems

    x = range(n_families)
    offsets = [-bar_width * (n_systems - 1) / 2 + i * bar_width for i in range(n_systems)]

    for i, system in enumerate(SYSTEMS_PLOTTED):
        rates = []
        yerr_low = []
        yerr_high = []
        for family in families:
            successes, total = data[(system, family)]
            if total > 0:
                interval = wilson_interval(successes, total, confidence=PROTOCOL_CONFIDENCE)
                rates.append(interval.point)
                # Round-off can place the Wilson point a few ulps outside an
                # endpoint at exact 0/1 cells. Matplotlib rejects a negative
                # error magnitude even when it is only floating-point noise.
                yerr_low.append(max(0.0, interval.point - interval.low))
                yerr_high.append(max(0.0, interval.high - interval.point))
            else:
                rates.append(0.0)
                yerr_low.append(0.0)
                yerr_high.append(0.0)

        ax.bar(
            [xi + offsets[i] for xi in x],
            rates,
            width=bar_width,
            label=SYSTEM_LABELS.get(system, system),
            yerr=[yerr_low, yerr_high],
            capsize=3,
            alpha=0.8,
        )

    ax.set_xlabel("Task Family")
    ax.set_ylabel("Root Success Rate")
    ax.set_title("P1-2: Main Outcome - Root Success by Task Family × System")
    ax.set_xticks(x)
    ax.set_xticklabels([FAMILY_LABELS.get(f, f) for f in families], rotation=45, ha="right")
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=8)
    ax.set_ylim(0, 1.05)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()

    out_path = FIGURES["P1-2"]
    fig.savefig(
        out_path,
        format="pdf",
        dpi=300,
        bbox_inches="tight",
        metadata=REPRODUCIBLE_PDF_METADATA,
    )
    plt.close(fig)
    return out_path


def figure_p1_3_selectivity_frontier(records: list[dict[str, Any]], plt) -> Path:
    """P1-3 Selectivity frontier: false-reframe rate vs hidden-shift success."""
    # Aggregate by system: false-reframe rate on controls vs success on hidden shift
    data = {}
    for system in SYSTEMS_PLOTTED:
        data[system] = {
            "hidden_success": [0, 0],  # [successes, total] on hidden shift
            "control_reframe": [0, 0],  # [false reframes, total] on controls
        }

    for record in records:
        system = record.get("system_id")
        if system not in SYSTEMS_PLOTTED:
            continue
        is_control = record.get("is_control", False)
        if is_control:
            data[system]["control_reframe"][1] += 1
            if record.get("reframed", False):
                data[system]["control_reframe"][0] += 1
        else:
            data[system]["hidden_success"][1] += 1
            if record.get("root_success", False):
                data[system]["hidden_success"][0] += 1

    fig, ax = plt.subplots(figsize=(10, 8))

    for system in SYSTEMS_PLOTTED:
        succ, n_hidden = data[system]["hidden_success"]
        refr, n_control = data[system]["control_reframe"]

        hidden_rate = succ / n_hidden if n_hidden > 0 else 0
        reframe_rate = refr / n_control if n_control > 0 else 0

        ax.scatter(
            reframe_rate * 100,
            hidden_rate * 100,
            label=SYSTEM_LABELS.get(system, system),
            s=100,
            alpha=0.7,
            edgecolors="black",
            linewidths=1,
        )

    # Ideal: low false-reframe (left), high hidden-success (top)
    ax.set_xlabel("False-Reframe Rate on Controls (%)")
    ax.set_ylabel("Hidden-Shift Success Rate (%)")
    ax.set_title("P1-3: Selectivity Frontier - False-Reframe vs Hidden-Shift Success")
    ax.legend(fontsize=9, loc="best")
    ax.grid(alpha=0.3)
    ax.set_xlim(-5, 105)
    ax.set_ylim(-5, 105)
    fig.tight_layout()

    out_path = FIGURES["P1-3"]
    fig.savefig(
        out_path,
        format="pdf",
        dpi=300,
        bbox_inches="tight",
        metadata=REPRODUCIBLE_PDF_METADATA,
    )
    plt.close(fig)
    return out_path


def figure_p1_4_reopening(records: list[dict[str, Any]], plt) -> Path:
    """P1-4 Reopening: reopen precision/recall/F1 by dependency depth/family."""
    # Aggregate by system and dependency depth: average precision, recall, F1
    data = {}  # (system, depth) -> [precision_sum, recall_sum, f1_sum, count]
    for system in SYSTEMS_PLOTTED:
        for depth in range(6):  # Assume max depth ~5
            data[(system, depth)] = [0.0, 0.0, 0.0, 0]

    for record in records:
        system = record.get("system_id")
        if system not in SYSTEMS_PLOTTED:
            continue
        depth = min(record.get("dependency_depth", 0), 5)
        reopen = record.get("reopen", {})
        if not reopen:
            continue
        prec = reopen.get("precision") or 0.0
        rec = reopen.get("recall") or 0.0
        f1 = reopen.get("f1") or 0.0
        if prec > 0:  # Only count if reopening metrics exist
            data[(system, depth)][0] += prec
            data[(system, depth)][1] += rec
            data[(system, depth)][2] += f1
            data[(system, depth)][3] += 1

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    depths = sorted(set(d for (_, d) in data.keys()))

    for idx, (metric_idx, metric_name) in enumerate([(0, "Precision"), (1, "Recall"), (2, "F1")]):
        ax = axes[idx]
        for system in SYSTEMS_PLOTTED:
            values = []
            for depth in depths:
                entry = data[(system, depth)]
                count = entry[3]
                if count > 0:
                    values.append(entry[metric_idx] / count)
                else:
                    values.append(0.0)
            ax.plot(depths, values, marker="o", label=SYSTEM_LABELS.get(system, system), alpha=0.7)

        ax.set_xlabel("Dependency Depth")
        ax.set_ylabel(metric_name)
        ax.set_title(f"Reopening {metric_name}")
        ax.legend(fontsize=7, loc="best")
        ax.grid(alpha=0.3)
        ax.set_xticks(depths)

    fig.suptitle("P1-4: Reopening Metrics by Dependency Depth", fontsize=14)
    fig.tight_layout()

    out_path = FIGURES["P1-4"]
    fig.savefig(
        out_path,
        format="pdf",
        dpi=300,
        bbox_inches="tight",
        metadata=REPRODUCIBLE_PDF_METADATA,
    )
    plt.close(fig)
    return out_path


def figure_p1_5_efficiency(records: list[dict[str, Any]], plt) -> Path:
    """P1-5 Efficiency: cost-to-success / success-cost Pareto frontier."""
    # Aggregate by system: average cost per case and success rate
    data = {}
    for system in SYSTEMS_PLOTTED:
        data[system] = {"cost": [], "success": []}

    for record in records:
        system = record.get("system_id")
        if system not in SYSTEMS_PLOTTED:
            continue
        resources = record.get("resources", {})
        # Use model_tokens as cost metric
        cost = resources.get("model_tokens", 0)
        success = 1.0 if record.get("root_success", False) else 0.0
        data[system]["cost"].append(cost)
        data[system]["success"].append(success)

    fig, ax = plt.subplots(figsize=(10, 8))

    for system in SYSTEMS_PLOTTED:
        costs = data[system]["cost"]
        successes = data[system]["success"]
        avg_cost = sum(costs) / len(costs) if costs else 0
        avg_success = sum(successes) / len(successes) if successes else 0

        # Cost-to-success: lower is better; success rate: higher is better
        # Plot with marker size proportional to success rate
        ax.scatter(
            avg_cost,
            avg_success * 100,
            label=SYSTEM_LABELS.get(system, system),
            s=150,
            alpha=0.7,
            edgecolors="black",
            linewidths=1,
        )

    ax.set_xlabel("Average Model Tokens per Case")
    ax.set_ylabel("Root Success Rate (%)")
    ax.set_title("P1-5: Efficiency - Cost vs Success Pareto Frontier")
    ax.legend(fontsize=9, loc="best")
    ax.grid(alpha=0.3)
    fig.tight_layout()

    out_path = FIGURES["P1-5"]
    fig.savefig(
        out_path,
        format="pdf",
        dpi=300,
        bbox_inches="tight",
        metadata=REPRODUCIBLE_PDF_METADATA,
    )
    plt.close(fig)
    return out_path


def figure_p1_6_recursion_stability(records: list[dict[str, Any]], plt) -> Path:
    """P1-6 Recursion stability: invariant/trace error vs recursion depth."""
    # Aggregate by system: errors vs max recursion depth
    data = {}  # system -> list of (depth, invariant_errors, trace_errors)
    for system in SYSTEMS_PLOTTED:
        data[system] = []

    for record in records:
        system = record.get("system_id")
        if system not in SYSTEMS_PLOTTED:
            continue
        depth = record.get("max_recursion_depth", 0)
        inv_errors = record.get("invariant_violation_count", 0)
        trace_fidelity = record.get("trace_fidelity", True)
        trace_errors = 0 if trace_fidelity else 1
        data[system].append((depth, inv_errors, trace_errors))

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Invariant violations vs depth
    ax1 = axes[0]
    for system in SYSTEMS_PLOTTED:
        points = data[system]
        if points:
            depths, invs, _ = zip(*points)
            # Plot average violations per depth
            depth_avg = {}
            for d, inv, _ in points:
                if d not in depth_avg:
                    depth_avg[d] = [0, 0]
                depth_avg[d][0] += inv
                depth_avg[d][1] += 1
            x = sorted(depth_avg.keys())
            y = [depth_avg[d][0] / depth_avg[d][1] for d in x]
            ax1.plot(x, y, marker="o", label=SYSTEM_LABELS.get(system, system), alpha=0.7)

    ax1.set_xlabel("Max Recursion Depth")
    ax1.set_ylabel("Avg Invariant Violations")
    ax1.set_title("Invariant Violations vs Recursion Depth")
    ax1.legend(fontsize=8, loc="best")
    ax1.grid(alpha=0.3)

    # Trace fidelity errors vs depth
    ax2 = axes[1]
    for system in SYSTEMS_PLOTTED:
        points = data[system]
        if points:
            depth_avg = {}
            for d, _, tr in points:
                if d not in depth_avg:
                    depth_avg[d] = [0, 0]
                depth_avg[d][0] += tr
                depth_avg[d][1] += 1
            x = sorted(depth_avg.keys())
            y = [depth_avg[d][0] / depth_avg[d][1] for d in x]
            ax2.plot(x, [100 * (1 - v) for v in y], marker="o", label=SYSTEM_LABELS.get(system, system), alpha=0.7)

    ax2.set_xlabel("Max Recursion Depth")
    ax2.set_ylabel("Trace Error Rate (%)")
    ax2.set_title("Trace Error vs Recursion Depth")
    ax2.legend(fontsize=8, loc="best")
    ax2.grid(alpha=0.3)

    fig.suptitle("P1-6: Recursion Stability - Errors vs Depth", fontsize=14)
    fig.tight_layout()

    out_path = FIGURES["P1-6"]
    fig.savefig(
        out_path,
        format="pdf",
        dpi=300,
        bbox_inches="tight",
        metadata=REPRODUCIBLE_PDF_METADATA,
    )
    plt.close(fig)
    return out_path


def compute_manifest(paths: dict[str, Path], cannot_check_count: int) -> dict[str, Any]:
    """Compute SHA256 hashes of all generated PDFs for reproducibility."""
    manifest: dict[str, Any] = {
        "generated_by": "scripts/make_figures.py",
        "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "archive_sha256": hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),
        "cannot_check_records_excluded": cannot_check_count,
        "exclusion_reason": (
            f"{cannot_check_count} CANNOT_CHECK records excluded (provider API failures)"
            if cannot_check_count
            else "no CANNOT_CHECK records in the archive (all cells recovered)"
        ),
        "figures": {},
    }

    for name, path in paths.items():
        if path.exists():
            sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
            manifest["figures"][name] = {
                "path": str(path.relative_to(PAPER)),
                "sha256": sha256,
                "size_bytes": path.stat().st_size,
            }
        else:
            manifest["figures"][name] = {"error": "file not generated"}

    return manifest


def check_committed_figures(cannot_check_count: int) -> list[str]:
    """Return fail-closed staleness errors without rewriting committed files."""

    if not MANIFEST_PATH.is_file():
        return [f"manifest absent: {MANIFEST_PATH}"]
    try:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"manifest is invalid JSON: {exc}"]

    errors: list[str] = []
    expected_inputs = {
        "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "archive_sha256": hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),
    }
    for key, expected in expected_inputs.items():
        if manifest.get(key) != expected:
            errors.append(f"{key} is stale")
    if manifest.get("cannot_check_records_excluded") != cannot_check_count:
        errors.append("CANNOT_CHECK exclusion count is stale")

    entries = manifest.get("figures") or {}
    for name, path in FIGURES.items():
        entry = entries.get(name) or {}
        if not path.is_file():
            errors.append(f"figure absent: {name}")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if entry.get("sha256") != actual:
            errors.append(f"figure hash mismatch: {name}")
        if entry.get("size_bytes") != path.stat().st_size:
            errors.append(f"figure size mismatch: {name}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if committed PDFs are stale")
    args = parser.parse_args(argv)

    # Load data
    records = load_records()
    print(f"Loaded {len(records)} records from {ARCHIVE}")

    # Filter CANNOT_CHECK
    filtered, cannot_check_count = filter_cannot_check(records)
    print(f"Filtered out {cannot_check_count} CANNOT_CHECK records")
    print(f"Using {len(filtered)} records for plotting")

    if args.check:
        errors = check_committed_figures(cannot_check_count)
        if errors:
            for error in errors:
                print(f"FIGURE_CHECK: ERROR: {error}", file=sys.stderr)
            return 1
        print("FIGURE_CHECK: OK")
        return 0

    plt = _import_matplotlib()

    # Generate figures
    generated = {}
    generated["P1-2"] = figure_p1_2_main_outcome(filtered, plt)
    print(f"Generated {generated['P1-2']}")

    generated["P1-3"] = figure_p1_3_selectivity_frontier(filtered, plt)
    print(f"Generated {generated['P1-3']}")

    generated["P1-4"] = figure_p1_4_reopening(filtered, plt)
    print(f"Generated {generated['P1-4']}")

    generated["P1-5"] = figure_p1_5_efficiency(filtered, plt)
    print(f"Generated {generated['P1-5']}")

    generated["P1-6"] = figure_p1_6_recursion_stability(filtered, plt)
    print(f"Generated {generated['P1-6']}")

    # Write manifest
    manifest = compute_manifest(generated, cannot_check_count)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {MANIFEST_PATH}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
