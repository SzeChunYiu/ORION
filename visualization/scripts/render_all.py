#!/usr/bin/env python3
"""Render deterministic static figures from the normalized evidence atlas."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "visualization/src"))

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from orion_visualization import (  # noqa: E402
    apply_atlas_style,
    pareto_frontier,
    plot_dependency_diagram,
    plot_ecdf,
    plot_forest,
    plot_status_matrix,
    save_figure,
)


AUTHORITY_BOUNDARY = "REPOSITORY_RECEIPTS_ONLY__NO_EXTERNAL_AUTHORITY_DELTA"


def load_atlas(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_both(fig, name: str, output_root: Path) -> list[Path]:
    outputs: list[Path] = []
    for fmt in ("svg", "png"):
        directory = output_root / "figures/static" / fmt
        outputs.extend(save_figure(fig, directory / name, formats=(fmt,)))
    plt.close(fig)
    return outputs


def evidence_status(value: str) -> str:
    mapping = {
        "BOUNDED_PASS": "PASS",
        "BOUNDARY": "NULL",
        "NOT_AUTHORITY": "CANNOT_CHECK",
    }
    return mapping.get(
        value,
        value
        if value in {"PASS", "FAIL", "UNKNOWN", "CANNOT_CHECK", "NULL", "ADVERSE", "MIXED"}
        else "UNKNOWN",
    )


def render(atlas: dict, output_root: Path) -> list[Path]:
    outputs: list[Path] = []
    metrics = atlas["metrics"]

    # 1. Framework orientation.  Arrows are declared conceptual dependencies,
    # not effect estimates or causal edges.
    nodes = [row["paper"] for row in atlas["framework"]["nodes"]]
    roles = {row["paper"]: row["role"] for row in atlas["framework"]["nodes"]}
    groups = {
        paper: (
            "flagship"
            if int(paper[1:]) <= 5
            else "formal / structured"
            if int(paper[1:]) <= 10
            else "state / governance / harness"
        )
        for paper in nodes
    }
    edges = [(row["source"], row["target"]) for row in atlas["framework"]["edges"]]
    positions = {
        "P1": (0, 2),
        "P2": (1, 2),
        "P3": (2, 2),
        "P4": (3, 2),
        "P5": (4, 2),
        "P6": (4, 1),
        "P7": (3, 1),
        "P8": (2, 1),
        "P9": (1, 1),
        "P10": (0, 1),
        "P11": (0, 0),
        "P12": (1, 0),
        "P13": (2, 0),
        "P14": (3, 0),
        "P15": (4, 0),
    }
    fig, ax, _ = plot_dependency_diagram(
        nodes,
        edges,
        groups=groups,
        positions=positions,
        title=(
            "ORION P1-P15 conceptual dependency map\n"
            "Arrow = declared conceptual dependency, not a causal effect"
        ),
    )
    fig.set_size_inches(10.5, 5.8)
    for text in ax.texts:
        label = text.get_text()
        if label in roles:
            text.set_text(f"{label}\n{roles[label]}")
    outputs += save_both(fig, "00_framework_map", output_root)

    # 2. Non-scalarized paper x gate status matrix.
    papers = [f"P{i}" for i in range(1, 16)]
    gates = ["registered_source", "bounded_result", "external_authority"]
    by_key = {(row["paper"], row["gate"]): row["state"] for row in atlas["gate_states"]}
    matrix = [[evidence_status(by_key[(paper, gate)]) for gate in gates] for paper in papers]
    fig, _ = plot_status_matrix(
        matrix,
        papers,
        ["Registered source", "Bounded result", "External authority"],
        title="Evidence gates (categorical; no readiness score)",
    )
    if fig.axes[0].get_legend() is not None:
        fig.axes[0].get_legend().remove()
    outputs += save_both(fig, "01_paper_gate_matrix", output_root)

    # 3. P1 paired hidden-shift effect intervals.
    p1_intervals = metrics["P1"]["hidden_shift_intervals"]
    p1_parent_labels = {
        "active_voi_repair_parent": "Active value-of-information parent",
        "darc_r2act_dependency_parent": "DARC/R2ACT dependency parent",
        "causalflow_minimal_counterfactual_parent": "CausalFlow counterfactual parent",
    }
    fig, ax = plot_forest(
        [100 * row["difference"] for row in p1_intervals],
        [100 * row["ci95_low"] for row in p1_intervals],
        [100 * row["ci95_high"] for row in p1_intervals],
        [p1_parent_labels[row["parent"]] for row in p1_intervals],
        statuses=["PASS"] * len(p1_intervals),
        reference=0.0,
        title=(
            "P1 hidden-shift effects (n=480 paired cases per comparator)\n"
            "Receipt-reported 95% paired bootstrap intervals; 10,000 resamples"
        ),
        xlabel="ORION − comparator success-rate difference (percentage points)",
        show_status_legend=False,
    )
    ax.set_xlim(-2, 61)
    for y, row in zip(np.arange(len(p1_intervals))[::-1], p1_intervals, strict=True):
        ax.text(
            100 * row["ci95_high"] + 1.0,
            y,
            f"{100 * row['difference']:.1f} [{100 * row['ci95_low']:.1f}, "
            f"{100 * row['ci95_high']:.1f}]",
            va="center",
            fontsize=8,
        )
    outputs += save_both(fig, "02_p1_hidden_shift_forest", output_root)

    # 4. P1 success-cost trade-off; cost is minimized and success maximized.
    p1_arms = metrics["P1"]["arms"]
    apply_atlas_style()
    x = np.asarray([row["mean_spent_budget"] for row in p1_arms], dtype=float)
    y = np.asarray([row["protected_root_task_success_rate"] for row in p1_arms], dtype=float)
    frontier = pareto_frontier(np.column_stack((x, y)), maximize=(False, True))
    fig, ax = plt.subplots(figsize=(8.6, 5.4), constrained_layout=True)
    for x_value, y_value, is_frontier in zip(x, y, frontier, strict=True):
        ax.scatter(
            x_value,
            y_value,
            s=62,
            color="#6B7280",
            edgecolor="#111827" if is_frontier else "white",
            linewidth=1.7 if is_frontier else 0.8,
            zorder=3,
        )
    short = {
        "active_voi_repair_parent": "Active VoI",
        "car_like_causal_replay": "CAR-like",
        "causalflow_minimal_counterfactual_parent": "CausalFlow",
        "cost_greedy_repair": "Cost-greedy",
        "darc_r2act_dependency_parent": "DARC/R2ACT",
        "immediate_outcome_flip_repair": "Outcome-flip",
        "orion_mutation_necessity": "ORION full",
        "orion_with_unlimited_intervention_budget": "Unlimited budget",
        "orion_without_KWM_level_ordering": "− KWM ordering",
        "orion_without_dependency_impact_binding": "− Dependency binding",
        "orion_without_lower_level_exclusion": "− Lower-level exclusion",
        "orion_without_protected_sibling_check": "− Sibling check",
        "reflect_like_replay": "Reflect replay",
        "static_no_reframe": "Static",
    }
    grouped: dict[tuple[float, float], list[str]] = defaultdict(list)
    for row in p1_arms:
        grouped[(row["mean_spent_budget"], row["protected_root_task_success_rate"])].append(
            short[row["arm"]]
        )
    offsets = {
        "Static": (5, 4),
        "Reflect replay": (6, 7),
        "Cost-greedy / Outcome-flip": (6, -17),
        "− Lower-level exclusion": (5, 5),
        "DARC/R2ACT": (5, 5),
        "− Sibling check": (-62, 6),
        "ORION full / Unlimited budget": (-44, 9),
        "− Dependency binding": (6, -16),
        "− KWM ordering": (6, -16),
        "Active VoI": (8, 8),
        "CAR-like / CausalFlow": (-80, 6),
    }
    for coordinates, labels in grouped.items():
        label = " / ".join(labels)
        ax.annotate(
            label,
            coordinates,
            xytext=offsets[label],
            textcoords="offset points",
            fontsize=8,
        )
    ax.set(
        xlim=(-0.18, 4.25),
        ylim=(-0.02, 1.055),
        title="P1 observed cost–success grid (bounded receipt; no authority ranking)",
        xlabel="Mean intervention budget spent (receipt units; lower is better)",
        ylabel="Protected-root task success rate (higher is better)",
    )
    ax.grid(color="#E5E7EB", linewidth=0.8)
    ax.text(
        0.99,
        0.04,
        "Black outline = nondominated within displayed 2D grid",
        transform=ax.transAxes,
        ha="right",
        fontsize=8,
        color="#4B5563",
    )
    ax.text(
        0.0,
        -0.16,
        "Point geometry is receipt-derived; external scientific authority remains CANNOT CHECK.",
        transform=ax.transAxes,
        fontsize=8,
        color="#4B5563",
    )
    outputs += save_both(fig, "03_p1_cost_success_pareto", output_root)

    # 5. P2 comparable rates on separate full 0-1 axes.  Reads use a different
    # unit and remain in atlas.json/notebooks rather than sharing this scale.
    p2_arms = metrics["P2"]["arms"]
    p2_gate = metrics["P2"]["gate"]
    p2_labels = {
        "bm25": "BM25",
        "orion_full": "ORION full",
        "orion_strong_new": "ORION strong-new",
        "rrf_hybrid": "RRF hybrid",
    }
    fig, axes = plt.subplots(1, 2, figsize=(9.8, 4.6), sharey=True, constrained_layout=True)
    y_positions = np.arange(len(p2_arms))[::-1]
    for ax, key, panel_title in zip(
        axes,
        ("recall_at_100", "ndcg_at_10"),
        ("Recall@100", "nDCG@10"),
        strict=True,
    ):
        values = [row[key] for row in p2_arms]
        for y_value, value, row in zip(y_positions, values, p2_arms, strict=True):
            color = "#0072B2" if row["arm"].startswith("orion") else "#6B7280"
            ax.scatter(value, y_value, s=60, color=color, edgecolor="white", linewidth=0.7)
            ax.text(value + 0.025, y_value, f"{value:.3f}", va="center", fontsize=8)
        ax.set(xlim=(0.0, 1.0), xlabel="Rate (fixed 0–1 scale)", title=panel_title)
        ax.grid(axis="x", color="#E5E7EB", linewidth=0.8)
    axes[0].set(yticks=y_positions, yticklabels=[p2_labels[row["arm"]] for row in p2_arms])
    fig.suptitle("P2 TREC-COVID retrieval: two estimands, overall frozen gate = FAIL")
    fig.text(
        0.5,
        -0.04,
        (
            "FAIL: recall noninferiority interval crossed "
            f"{p2_gate['criteria']['recall_noninferiority']['margin']:.2f} and ORION used "
            f"{p2_gate['criteria']['cost_reduction']['reads_vs_comparator_pct']:.1f}% more reads."
        ),
        ha="center",
        fontsize=8,
        color="#9A3412",
    )
    outputs += save_both(fig, "04_p2_retrieval_rates", output_root)

    # 6. P3 accuracy intervals across systems/ablations.
    p3_accuracy = [row for row in metrics["P3"]["systems"] if row["metric"] == "accuracy"]
    p3_order = [
        "orion",
        "exact_coordinate_conservative",
        "flat_predicate_canonicalization",
        "ablation:force_compatibility_without_obstruction",
        "ablation:remove_construct",
        "ablation:remove_measurement",
        "ablation:remove_modality_polarity_attribution_discourse",
        "ablation:remove_referent",
        "ablation:remove_temporal_context",
    ]
    p3_by_system = {row["system"]: row for row in p3_accuracy}
    p3_accuracy = [p3_by_system[system] for system in p3_order]
    p3_labels = {
        "orion": "ORION",
        "exact_coordinate_conservative": "Exact-coordinate conservative",
        "flat_predicate_canonicalization": "Flat-predicate canonicalization",
        "ablation:force_compatibility_without_obstruction": "Ablation — forced compatibility",
        "ablation:remove_construct": "Ablation — no construct",
        "ablation:remove_measurement": "Ablation — no measurement",
        "ablation:remove_modality_polarity_attribution_discourse": (
            "Ablation — no modality/polarity/discourse"
        ),
        "ablation:remove_referent": "Ablation — no referent",
        "ablation:remove_temporal_context": "Ablation — no temporal context",
    }
    fig, ax = plot_forest(
        [row["rate"] for row in p3_accuracy],
        [row["ci95_low"] for row in p3_accuracy],
        [row["ci95_high"] for row in p3_accuracy],
        [p3_labels[row["system"]] for row in p3_accuracy],
        statuses=["PASS"] * len(p3_accuracy),
        reference=None,
        title=(
            "P3 exact 32-case accuracy with Wilson 95% intervals\n"
            "Uniform markers = one bounded public-reference receipt, not external authority"
        ),
        xlabel="Accuracy (fixed 0–1 scale)",
        show_status_legend=False,
    )
    ax.set_xlim(0.0, 1.0)
    for y_value, row in zip(np.arange(len(p3_accuracy))[::-1], p3_accuracy, strict=True):
        successes = int(round(row["rate"] * row["n"]))
        ax.text(
            1.015,
            y_value,
            f"{successes}/32  [{row['ci95_low']:.3f}, {row['ci95_high']:.3f}]",
            transform=ax.get_yaxis_transform(),
            va="center",
            fontsize=8,
            clip_on=False,
        )
    outputs += save_both(fig, "05_p3_accuracy_forest", output_root)

    # 7. P6/P7 finite formal counts.  The log count axis exposes all four event
    # classes without turning the largest donor-multiplied count into quality.
    formal_keys = ["full_success", "partial_failure", "countermodels", "separation_witnesses"]
    formal_labels = [
        "Full-success\nevents",
        "Partial-failure\nevents",
        "Countermodels",
        "Separation\nwitnesses",
    ]
    p6_counts = [metrics["P6"]["counts"][key] for key in formal_keys]
    p7_counts = [metrics["P7"]["counts"][key] for key in formal_keys]
    if np.any(np.asarray([*p6_counts, *p7_counts], dtype=float) <= 0):
        raise ValueError("log-count display requires strictly positive event counts")
    x_positions = np.arange(len(formal_keys))
    fig, ax = plt.subplots(figsize=(8.5, 5.1), constrained_layout=True)
    width = 0.36
    ax.bar(
        x_positions - width / 2, p6_counts, width, color="#0072B2", label="P6 certificate lifting"
    )
    ax.bar(x_positions + width / 2, p7_counts, width, color="#E69F00", label="P7 closure carrying")
    ax.set_yscale("log")
    ax.set(
        xticks=x_positions,
        xticklabels=formal_labels,
        ylabel="Enumerated formula-event count (log scale)",
        title=(
            "P6/P7 finite event counts: identical totals are not independent replication\n"
            f"Separate finite receipts; P7's distinct {metrics['P7']['planned_cases']}/{metrics['P7']['observed_cases']} programme execution remains invalid"
        ),
    )
    ax.grid(axis="y", color="#E5E7EB", linewidth=0.8, which="both")
    ax.legend(frameon=False)
    for x_value, height in zip(x_positions, p6_counts, strict=True):
        ax.text(
            x_value,
            height * 1.12,
            f"both {int(height):,}",
            ha="center",
            va="bottom",
            fontsize=8,
        )
    outputs += save_both(fig, "06_p6_p7_formal_counts", output_root)

    # 8. P11 gate-not-met query deltas as an ECDF plus every raw observation.
    # A KDE is intentionally avoided for 30 discrete registered queries.
    p11_delta = np.asarray([100 * row["delta"] for row in metrics["P11"]["queries"]])
    fig, ax = plot_ecdf(
        p11_delta,
        title="P11 compiled-minus-universal query deltas (terminal: gate not met)",
        xlabel="Compiled − universal balanced accuracy (percentage points)",
    )
    ax.axvline(0.0, color="#D55E00", linewidth=1.2, linestyle="--")
    ax.scatter(p11_delta, np.full_like(p11_delta, 0.025), marker="|", s=72, color="#111827")
    ax.text(
        0.99,
        0.05,
        "Positive = compiled better",
        transform=ax.transAxes,
        ha="right",
        fontsize=8,
        color="#4B5563",
    )
    outputs += save_both(fig, "07_p11_delta_ecdf", output_root)
    ordered = np.sort(p11_delta)
    fig, ax = plt.subplots(figsize=(7.8, 6.0), constrained_layout=True)
    ranks = np.arange(1, ordered.size + 1)
    colors = np.where(ordered > 0, "#0072B2", "#D55E00")
    ax.scatter(ordered, ranks, s=42, c=colors, edgecolor="white", linewidth=0.6, zorder=3)
    ax.axvline(0.0, color="#111827", linewidth=1.1, linestyle="--")
    ax.set(
        xlabel="Compiled − universal balanced accuracy (percentage points)",
        ylabel="Ordered registered query (worst → best)",
        title="P11 all 30 query deltas (raw, sorted, descriptive)",
        yticks=[1, 5, 10, 15, 20, 25, 30],
    )
    ax.grid(color="#E5E7EB", linewidth=0.8)
    ax.text(
        0.01,
        0.98,
        "Orange ≤ 0; blue > 0",
        transform=ax.transAxes,
        va="top",
        fontsize=8,
        color="#4B5563",
    )
    outputs += save_both(fig, "08_p11_delta_strip", output_root)

    # 9. P12 ordered sigma strata with all 32 independent family blocks.
    p12_families = metrics["P12"]["families"]
    sigma_values = sorted({float(row["sigma"]) for row in p12_families})
    fig, ax = plt.subplots(figsize=(8.3, 5.2), constrained_layout=True)
    jitter = np.linspace(-0.13, 0.13, 8)
    for index, sigma in enumerate(sigma_values):
        deltas = np.asarray(
            [row["delta_vs_stronger_one_signal"] for row in p12_families if row["sigma"] == sigma]
        )
        ax.scatter(
            index + jitter[: deltas.size],
            deltas,
            s=34,
            color="#56B4E9",
            alpha=0.78,
            edgecolor="white",
            linewidth=0.5,
            zorder=2,
        )
        ax.scatter(index, deltas.mean(), s=84, marker="D", color="#0072B2", zorder=3)
        ax.text(
            index,
            0.344,
            f"mean {deltas.mean():.3f}",
            ha="center",
            va="center",
            fontsize=8,
        )
    ax.axhspan(0.329, 0.359, color="#F3F6F8", zorder=0)
    ax.axhline(0.0, color="#111827", linewidth=1.0)
    ax.axhline(
        0.12, color="#E69F00", linewidth=1.2, linestyle="--", label="Per-stratum mean gate = 0.12"
    )
    ax.axhline(
        0.15, color="#6B7280", linewidth=1.1, linestyle=":", label="Overall mean gate = 0.15"
    )
    ax.set(
        xlim=(-0.45, len(sigma_values) - 0.55),
        ylim=(0.0, 0.36),
        xticks=np.arange(len(sigma_values)),
        xticklabels=[f"σ = {sigma:.1f}" for sigma in sigma_values],
        xlabel="Registered noise stratum",
        ylabel="Allocation-rate gain vs stronger one-signal arm",
        title=(
            "P12 family-block gains by registered noise σ (8 blocks per stratum)\n"
            "mean labels use a separate top annotation band"
        ),
    )
    ax.grid(axis="y", color="#E5E7EB", linewidth=0.8)
    ax.legend(frameon=False, loc="lower left")
    outputs += save_both(fig, "09_p12_family_blocks_by_sigma", output_root)

    # 10. P13 three-objective safety-cost trade-off.  Unsafe reuse is a first-
    # class objective rather than being omitted from a 2D "safety frontier".
    p13_arms = metrics["P13"]["arms"]
    p13_points = np.asarray(
        [
            [row["mean_cost"], row["verified_correct_rate"], row["unsafe_reuse_rate"]]
            for row in p13_arms
        ]
    )
    p13_frontier = pareto_frontier(p13_points, maximize=(False, True, False))
    fig, ax = plt.subplots(figsize=(8.8, 5.6), constrained_layout=True)
    normalization = plt.Normalize(0.0, 0.30)
    colormap = plt.get_cmap("YlOrRd")
    offsets = {
        "UNQUALIFIED": (6, 6),
        "CONFIDENCE_ONLY": (6, -25),
        "UNVERIFIED_RCS": (6, 7),
        "AUTHENTICATED_RCS": (6, -24),
        "ALWAYS_RAW": (-84, 6),
    }
    p13_labels = {
        "UNQUALIFIED": "Unqualified",
        "CONFIDENCE_ONLY": "Confidence only",
        "UNVERIFIED_RCS": "Unverified RCS",
        "AUTHENTICATED_RCS": "Authenticated RCS",
        "ALWAYS_RAW": "Always raw",
    }
    for row, is_frontier in zip(p13_arms, p13_frontier, strict=True):
        ax.scatter(
            row["mean_cost"],
            row["verified_correct_rate"],
            s=95,
            color=colormap(normalization(row["unsafe_reuse_rate"])),
            edgecolor="#111827" if is_frontier else "#9CA3AF",
            linewidth=1.8 if is_frontier else 1.0,
            zorder=3,
        )
        ax.annotate(
            f"{p13_labels[row['arm']]}\nunsafe reuse {100 * row['unsafe_reuse_rate']:.1f}%",
            (row["mean_cost"], row["verified_correct_rate"]),
            xytext=offsets[row["arm"]],
            textcoords="offset points",
            fontsize=8,
        )
    ax.set(
        xlim=(0.7, 6.05),
        ylim=(0.90, 1.00),
        xlabel="Mean cost (receipt units; lower is better)",
        ylabel="Verified-correct rate (higher is better; axis 0.90–1.00)",
        title="P13 finite-world cost–correctness–unsafe-reuse trade-off",
    )
    ax.grid(color="#E5E7EB", linewidth=0.8)
    colorbar = fig.colorbar(
        plt.cm.ScalarMappable(norm=normalization, cmap=colormap), ax=ax, fraction=0.046, pad=0.04
    )
    colorbar.set_label("Unsafe-reuse rate (lower is better)")
    ax.text(
        0.99,
        0.02,
        "Black outline = nondominated across cost↓, correct↑, unsafe reuse↓",
        transform=ax.transAxes,
        ha="right",
        fontsize=8,
        color="#4B5563",
    )
    ax.text(
        0.0,
        -0.18,
        "One bounded finite-world receipt; no population-safety or external-authority claim.",
        transform=ax.transAxes,
        fontsize=8,
        color="#4B5563",
    )
    outputs += save_both(fig, "10_p13_three_objective_tradeoff", output_root)

    # 11. P14 rate panels keep the false-promotion direction explicit rather
    # than using one heatmap palette with contradictory desirability.
    p14_arms = metrics["P14"]["arms"]
    p14_order = [
        "ORION_RSE_FULL",
        "MULTI_REVIEW",
        "RAW_POSITIVE",
        "REFLECTION_CHECKLIST",
        "DONOR_AWARE_REVIEW",
    ]
    p14_by_arm = {row["arm"]: row for row in p14_arms}
    p14_arms = [p14_by_arm[arm] for arm in p14_order]
    p14_labels = {
        "ORION_RSE_FULL": "ORION-RSE full",
        "MULTI_REVIEW": "Multi-review",
        "RAW_POSITIVE": "Raw positive",
        "REFLECTION_CHECKLIST": "Reflection checklist",
        "DONOR_AWARE_REVIEW": "Donor-aware review",
    }
    p14_panels = [
        ("disposition_accuracy", "Disposition accuracy\n↑ higher is better", "#0072B2"),
        ("false_promotion_rate", "False-promotion rate\n↓ lower is better", "#D55E00"),
        ("useful_discovery_recall", "Useful-discovery recall\n↑ higher is better", "#009E73"),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(11.2, 5.0), sharey=True, constrained_layout=True)
    y_positions = np.arange(len(p14_arms))[::-1]
    for ax, (key, title, color) in zip(axes, p14_panels, strict=True):
        for y_value, row in zip(y_positions, p14_arms, strict=True):
            value = row[key]
            ax.scatter(value, y_value, s=58, color=color, edgecolor="white", linewidth=0.7)
            offset = -0.035 if value > 0.90 else 0.035
            ax.text(
                value + offset,
                y_value,
                f"{value:.2f}",
                ha="right" if offset < 0 else "left",
                va="center",
                fontsize=8,
            )
        ax.set(
            xlim=(-0.025, 1.025),
            xlabel="Rate (fixed 0–1 scale; padded endpoints)",
            title=title,
        )
        ax.grid(axis="x", color="#E5E7EB", linewidth=0.8)
    axes[0].set(yticks=y_positions, yticklabels=[p14_labels[row["arm"]] for row in p14_arms])
    fig.suptitle("P14 governance-contract conformance on 28 internally authored cases")
    fig.text(
        0.5,
        -0.05,
        "Receipt reports rates without intervals; external scientific validity remains CANNOT CHECK.",
        ha="center",
        fontsize=8,
        color="#4B5563",
    )
    outputs += save_both(fig, "11_p14_governance_rates", output_root)

    # 12. P15 lifecycle versus scientific-contract/authority gates.
    p15 = metrics["P15"]["workflows"]
    p15_gates = [
        "spawn_ok",
        "output_complete",
        "replay_match",
        "scientific_contract_valid",
        "claim_authority",
    ]
    p15_matrix = [
        [
            "PASS"
            if row[key]
            else "CANNOT_CHECK"
            if key in {"scientific_contract_valid", "claim_authority"}
            else "FAIL"
            for key in p15_gates
        ]
        for row in p15
    ]
    fig, _ = plot_status_matrix(
        p15_matrix,
        [
            {
                "REAL-P6-ETS-TWO-CHECKER": "P6 ETS two-checker",
                "REAL-P9-QWEN-NEGATIVE": "P9 Qwen negative",
                "REAL-P10-OCME-TWO-CHECKER": "P10 OCME two-checker",
                "REAL-P10-NATIVE-LEAN-CANNOT-CHECK": "P10 native Lean",
            }[row["id"]]
            for row in p15
        ],
        ["Spawn", "Output", "Replay", "Contract", "Authority"],
        title=(
            "P15 bounded workflow-contract receipts\n"
            "3 receipt-level AUTHORIZED_SCIENCE; 1 CANNOT CHECK\n"
            "Receipt dispositions only — not publication or external authority"
        ),
    )
    ax = fig.axes[0]
    ax.tick_params(axis="x")
    if ax.get_legend() is not None:
        ax.get_legend().remove()
    outputs += save_both(fig, "12_p15_workflow_matrix", output_root)

    # 13. Frozen #1332 DES coverage.  Each row is normalized only by its own
    # registered denominator; the percentages are execution coverage, never a
    # performance or readiness score.  Observed and valid remain separate so
    # P4's mechanical execution and P7's invalid near-complete generation are
    # not promoted into scientific outcomes.
    des_rows = atlas["des_execution"]
    y = np.arange(len(des_rows))[::-1]
    observed_pct = np.asarray(
        [100 * row["observed"] / row["planned"] for row in des_rows], dtype=float
    )
    valid_pct = np.asarray(
        [100 * row["valid"] / row["planned"] for row in des_rows], dtype=float
    )
    fig, ax = plt.subplots(figsize=(11.8, 7.4), constrained_layout=True)
    ax.barh(y, np.full(len(des_rows), 100.0), height=0.60, color="#E5E7EB", label="Planned")
    ax.barh(y, observed_pct, height=0.42, color="#56B4E9", label="Observed / executed")
    ax.barh(y, valid_pct, height=0.20, color="#009E73", label="Valid at registered internal scope")
    for y_value, row, observed_value, valid_value in zip(
        y, des_rows, observed_pct, valid_pct, strict=True
    ):
        if valid_value == 0:
            ax.scatter(0, y_value, marker="|", s=90, color="#111827", linewidth=1.6, zorder=4)
        ax.text(
            102,
            y_value,
            f"{row['valid']}/{row['observed']}/{row['planned']} {row['unit']}",
            va="center",
            fontsize=7.5,
        )
    ax.set(
        xlim=(0, 142),
        xticks=np.arange(0, 101, 20),
        xticklabels=[f"{value}%" for value in range(0, 101, 20)],
        yticks=y,
        yticklabels=[row["paper"] for row in des_rows],
        xlabel="Within-paper registered denominator coverage (not performance)",
        ylabel="Frozen DES job",
        title=(
            "Frozen #1332 P1–P15 execution coverage\n"
            "right labels = valid / observed / planned in each paper's own unit; "
            "gray planned · blue observed · green valid"
        ),
    )
    ax.grid(axis="x", color="#E5E7EB", linewidth=0.8)
    ax.text(
        0,
        -0.09,
        "All external-authority states remain CANNOT CHECK and every paper-authority delta remains NONE.",
        transform=ax.transAxes,
        fontsize=8,
        color="#4B5563",
    )
    outputs += save_both(fig, "13_des_execution_coverage", output_root)

    # 14. Core dynamic-state mechanics.  Four different estimands remain in
    # separate panels; no cross-panel scalar or authority score is computed.
    mechanics = atlas["framework_mechanics"]
    collision = mechanics["collision"]
    update = mechanics["update_algebra"]
    projection = mechanics["projection"]
    census = mechanics["census"]
    fig, axes = plt.subplots(2, 2, figsize=(12.2, 8.8), constrained_layout=True)

    terminal_order = ["ADMISSIBLE", "BLOCKED", "CANNOT_CHECK"]
    action_order = [
        "ACQUIRE_EVIDENCE",
        "DISCRIMINATE",
        "OBTAIN_EXTERNAL_CUSTODY",
        "REVALIDATE",
        "STOP",
    ]
    action_labels = ["Acquire", "Discriminate", "Custody", "Revalidate", "Stop"]
    collision_matrix = np.asarray(
        [
            [collision["terminal_action_counts"].get(terminal, {}).get(action, 0) for action in action_order]
            for terminal in terminal_order
        ],
        dtype=int,
    )
    ax = axes[0, 0]
    image = ax.imshow(np.log1p(collision_matrix), cmap="Blues", aspect="auto")
    for row_index in range(collision_matrix.shape[0]):
        for column_index in range(collision_matrix.shape[1]):
            ax.text(column_index, row_index, str(collision_matrix[row_index, column_index]), ha="center", va="center", fontsize=8)
    ax.set(
        xticks=np.arange(len(action_labels)),
        xticklabels=action_labels,
        yticks=np.arange(len(terminal_order)),
        yticklabels=[label.replace("_", " ") for label in terminal_order],
        xlabel="Next action",
        ylabel="Legacy terminal",
        title=(
            f"A. Terminal → action collisions (n={collision['state_count']} states)\n"
            f"{collision['different_action_pairs']:,}/{collision['same_terminal_pairs']:,} same-terminal pairs diverge"
        ),
    )
    ax.tick_params(axis="x", rotation=25)
    colorbar = fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    colorbar.set_label("log(1 + state count)")

    ax = axes[0, 1]
    mutations = update["mutations"]
    mutation_y = np.arange(len(mutations))[::-1]
    mutation_rates = np.asarray(
        [100 * row["detections"] / row["cases"] for row in mutations], dtype=float
    )
    ax.hlines(mutation_y, 0, mutation_rates, color="#BFD7EA", linewidth=2)
    ax.scatter(mutation_rates, mutation_y, s=58, color="#0072B2", edgecolor="white", zorder=3)
    for y_value, rate, row in zip(mutation_y, mutation_rates, mutations, strict=True):
        ax.text(min(rate + 2, 103), y_value, f"{row['detections']:,}/{row['cases']:,}", va="center", fontsize=7.5)
    total_law_cases = sum(row["pass"] + row["fail"] for row in update["laws"])
    ax.set(
        xlim=(0, 118),
        xticks=np.arange(0, 101, 20),
        xticklabels=[f"{value}%" for value in range(0, 101, 20)],
        yticks=mutation_y,
        yticklabels=[row["mutation"].removeprefix("M-").replace("-", " ").title() for row in mutations],
        xlabel="Detected mutation cases / exercised mutation cases",
        title=(
            f"B. Update algebra: {update['mutations_killed']}/{update['mutation_count']} mutants killed\n"
            f"registered law failures = {update['law_failures']} across {total_law_cases:,} law cases"
        ),
    )
    ax.grid(axis="x", color="#E5E7EB", linewidth=0.8)

    ax = axes[1, 0]
    surfaces = ["PROMOTION_V1", "READINESS_V1"]
    projection_terminals = ["ADMISSIBLE", "BLOCKED", "CANNOT_CHECK", "PROVISIONAL"]
    projection_matrix = np.asarray(
        [
            [
                projection["surface_results"][surface]["terminal_counts"].get(terminal, 0)
                for terminal in projection_terminals
            ]
            for surface in surfaces
        ],
        dtype=int,
    )
    image = ax.imshow(np.log1p(projection_matrix), cmap="PuBuGn", aspect="auto")
    for row_index in range(projection_matrix.shape[0]):
        for column_index in range(projection_matrix.shape[1]):
            ax.text(column_index, row_index, str(projection_matrix[row_index, column_index]), ha="center", va="center", fontsize=8)
    ax.set(
        xticks=np.arange(len(projection_terminals)),
        xticklabels=[label.replace("_", " ") for label in projection_terminals],
        yticks=np.arange(len(surfaces)),
        yticklabels=[surface.replace("_V1", "").title() for surface in surfaces],
        xlabel="Legacy terminal",
        ylabel="Projection surface",
        title=(
            f"C. Projection replay: {projection['matched_rows']:,}/{projection['row_denominator']:,} rows match\n"
            f"{projection['noninjective_groups']}/{projection['noninjective_groups']} groups noninjective; "
            f"{projection['action_divergent_groups']} action-divergent"
        ),
    )
    ax.tick_params(axis="x", rotation=25)
    colorbar = fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    colorbar.set_label("log(1 + row count)")

    ax = axes[1, 1]
    held_out = census["folds"][str(census["held_out_fold"])]
    all_counts = [census["classified_occurrences"], census["unclassified_occurrences"]]
    held_counts = [held_out["classified"], held_out["unclassified"]]
    totals = [sum(all_counts), sum(held_counts)]
    classified_pct = [100 * all_counts[0] / totals[0], 100 * held_counts[0] / totals[1]]
    unclassified_pct = [100 - value for value in classified_pct]
    census_y = np.arange(2)[::-1]
    ax.barh(census_y, classified_pct, color="#0072B2", label="Classified")
    ax.barh(census_y, unclassified_pct, left=classified_pct, color="#D55E00", label="Unclassified retained")
    for y_value, left, counts in zip(census_y, classified_pct, [all_counts, held_counts], strict=True):
        ax.text(left / 2, y_value, f"{counts[0]:,}", ha="center", va="center", color="white", fontsize=8)
        ax.text(left + (100 - left) / 2, y_value, f"{counts[1]:,}", ha="center", va="center", color="white", fontsize=8)
    ax.set(
        xlim=(0, 100),
        xticks=np.arange(0, 101, 20),
        xticklabels=[f"{value}%" for value in range(0, 101, 20)],
        yticks=census_y,
        yticklabels=["All occurrences", f"Held-out fold {census['held_out_fold']}"],
        xlabel="Occurrence share",
        title=(
            f"D. Source-tree census (n={census['occurrences']:,} occurrences)\n"
            f"terminal={census['terminal']}; text-cap-censored files={census['likely_text_cap_censored_count']}"
        ),
    )
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=2)

    fig.suptitle(
        "Dynamic epistemic-state mechanics — finite internal receipts only; no external authority delta",
        fontsize=14,
    )
    outputs += save_both(fig, "14_framework_mechanics_receipts", output_root)

    return outputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--atlas", type=Path, default=ROOT / "visualization/data/derived/atlas.json"
    )
    parser.add_argument("--output-root", type=Path, default=ROOT / "visualization")
    args = parser.parse_args()
    outputs = render(load_atlas(args.atlas), args.output_root)
    for path in outputs:
        print(path)
    print(f"FIGURES={len(outputs)}")
    print(f"SCIENTIFIC_AUTHORITY={AUTHORITY_BOUNDARY}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
