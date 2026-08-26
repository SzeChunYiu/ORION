#!/usr/bin/env python3
"""Build first-wave Q/QG publication figures from receipt-verified source data.

Scientific JSON is read from each paper's declared git cut, not from the PR merge worktree.
The script first verifies every configured scalar appears in the union of the bound source
artifacts, then writes source-data JSON/CSV-like tables plus SVG/PNG figures.

The figures are publication displays only and grant no scientific authority.
"""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import subprocess
import sys
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONFIG = ROOT / "papers/Q_QG_FIGURE_SOURCE_V1.json"
CUTS = {
    "Q1": "ca7df1055a43f97eaf8d142a62011c4c261af368",
    "Q4": "ca7df1055a43f97eaf8d142a62011c4c261af368",
    "QG1": "c5ba39fef4f25c46de5fb69bf07f50530f4693ca",
    "QG2": "ca7df1055a43f97eaf8d142a62011c4c261af368",
}


def git_show(cut: str, path: str) -> str:
    proc = subprocess.run(
        ["git", "show", f"{cut}:{path}"], cwd=ROOT, check=True, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    return proc.stdout


def load_source(paper: str, path: str) -> Any:
    # Q2 publication-denominator artifacts are created by this publication branch.
    if paper == "Q2" and path.startswith("papers/"):
        return json.loads((ROOT / path).read_text(encoding="utf-8"))
    cut = CUTS[paper]
    return json.loads(git_show(cut, path))


def scalars(obj: Any):
    if isinstance(obj, dict):
        for v in obj.values():
            yield from scalars(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from scalars(v)
    elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
        yield float(obj)


def found_number(value: float, pool: list[float]) -> bool:
    return any(math.isclose(float(value), x, rel_tol=1e-12, abs_tol=1e-12) for x in pool)


def save(fig, out_dir: pathlib.Path, stem: str) -> None:
    fig.tight_layout()
    fig.savefig(out_dir / f"{stem}.svg", bbox_inches="tight")
    fig.savefig(out_dir / f"{stem}.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def q1_figure(data: dict[str, Any], out_dir: pathlib.Path) -> None:
    labels = ["Split-anchor\nrefutation", "Frame-for-Tag\nborrow"]
    exact = [data["split"]["exact"], data["borrow"]["exact"]]
    restricted = [data["split"]["restricted"], data["borrow"]["restricted"]]
    x = np.arange(len(labels))
    width = 0.35
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.bar(x - width / 2, exact, width, label="Exact optimum")
    ax.bar(x + width / 2, restricted, width, label="Restricted family")
    ax.set_ylabel("Frozen structural cost")
    ax.set_xticks(x, labels)
    ax.set_ylim(0, max(restricted) + 2)
    ax.legend(frameon=False)
    ax.set_title("Exact counterexamples open the family; support ≥3 is theorem-excluded")
    ax.text(
        0.5, 0.02,
        f"R6S all-n support ceiling ≤ {data['all_n_support_ceiling']}  |  "
        f"Lemma-B tuples: {data['r6s_class_tuples_checked']:,}  |  "
        f"Lemma-E cases: {data['r6s_local_inequality_cases']:,}",
        transform=ax.transAxes, ha="center", va="bottom", fontsize=8,
    )
    save(fig, out_dir, "Q1_counterexamples_and_support_ceiling")


def q2_figure(data: dict[str, Any], out_dir: pathlib.Path) -> None:
    names = ["Declared\nreceipts", "Graph\nnodes", "Explicit\nexclusions", "Successor\nedges", "Standalone\nnegatives"]
    values = [
        data["declared_receipt_universe"], data["included_graph_nodes"],
        data["explicit_exclusions"], data["asserted_successor_edges"],
        data["standalone_negative_or_absorbed_nodes"],
    ]
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    bars = ax.bar(names, values)
    ax.set_ylabel("Count in frozen publication object")
    ax.set_title("Q2 declared denominator and auditable successor graph")
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.6, str(val), ha="center", va="bottom")
    save(fig, out_dir, "Q2_declared_denominator")


def q4_figure(data: dict[str, Any], out_dir: pathlib.Path) -> None:
    fig, axes = plt.subplots(3, 2, figsize=(8.2, 9.0))
    axes = axes.ravel()

    panels = [
        ("N4-A typed prior", [data["N4_A"]["candidate"], data["N4_A"]["control"], data["N4_A"]["other"]], ["typed", "flat prior", "known graph"], "mean utility"),
        ("N4-B scoped reopening", [data["N4_B"]["candidate"], data["N4_B"]["control"], data["N4_B"]["other"], data["N4_B"]["hostile"]], ["scoped", "never", "unscoped", "always"], "mean utility"),
        ("N4-C decision-targeted verification", [data["N4_C"]["candidate"], data["N4_C"]["control"]], ["targeted", "random"], "mean regret ↓"),
        ("N4-D full-chain transport", [data["N4_D"]["candidate_recall"], data["N4_D"]["last_hop_recall"], data["N4_D"]["candidate_fpr"]], ["full recall", "last-hop recall", "full FPR"], "registered rate"),
        ("N4-E decision-coupled probing", [data["N4_E"]["candidate"], data["N4_E"]["control"]], ["decision", "info gain"], "mean utility"),
        ("N4-F3 mixed transport", [data["N4_F3"]["candidate"], data["N4_F3"]["control"], data["N4_F3"]["naive"]], ["typed", "rederive", "carry"], "mean utility"),
    ]
    for ax, (title, vals, names, ylabel) in zip(axes, panels):
        bars = ax.bar(names, vals)
        ax.axhline(0, linewidth=0.7)
        ax.set_title(title, fontsize=10)
        ax.set_ylabel(ylabel, fontsize=8)
        ax.tick_params(axis="x", labelrotation=20, labelsize=8)
        for bar, val in zip(bars, vals):
            va = "bottom" if val >= 0 else "top"
            offset = 0.02 * (max(vals) - min(vals) + 1)
            y = val + offset if val >= 0 else val - offset
            ax.text(bar.get_x()+bar.get_width()/2, y, f"{val:g}", ha="center", va=va, fontsize=7)
    fig.suptitle("Q4: six matched-information mechanism worlds (native scales preserved)", y=1.01)
    save(fig, out_dir, "Q4_primary_effects_small_multiples")


def qg1_figures(data: dict[str, Any], out_dir: pathlib.Path) -> None:
    fig, ax = plt.subplots(figsize=(6.2, 4.1))
    names = ["QG6 syndrome-rank\nsafe ceiling", "QG9 intrinsic\nsupport number"]
    vals = [data["r6i_safe_syndrome_rank_ceiling"], data["r6i_intrinsic_support_number"]]
    bars = ax.bar(names, vals)
    ax.set_ylabel("R6I support bound")
    ax.set_ylim(0, max(vals) + 1.5)
    ax.set_title("A sound proof-derived ceiling need not be intrinsic")
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x()+bar.get_width()/2, val+0.15, str(val), ha="center")
    ax.text(
        0.5, 0.03,
        f"StabPrep frozen vocabulary: {data['stabprep_mixed_feature_cells']} mixed cells; "
        f"irreducible floor {data['stabprep_irreducible_errors']}/{data['stabprep_registered_instances']}",
        transform=ax.transAxes, ha="center", fontsize=8,
    )
    save(fig, out_dir, "QG1_R6I_support_bound_hierarchy")

    # Exact normalized 2-D certificate slice for t_r > 0 and t_c <= t_nc.
    y = np.linspace(0, 4.5, 400)  # y = t_tag/t_r
    boundary = np.maximum(5.0, 2.0 + 2.0 * y)  # x=(t_c+t_nc)/t_r
    fig2, ax2 = plt.subplots(figsize=(6.3, 4.5))
    ax2.plot(boundary, y, label="certificate boundary")
    ax2.fill_betweenx(y, boundary, 12, alpha=0.2, label="support-1 certificate applies")
    ax2.set_xlim(0, 12)
    ax2.set_ylim(0, 4.5)
    ax2.set_xlabel(r"$(t_c+t_{nc})/t_r$")
    ax2.set_ylabel(r"$t_{tag}/t_r$")
    ax2.set_title(r"QG16 reduced certificate slice ($t_r>0$, $t_c\leq t_{nc}$)")
    ax2.text(1.0, 3.8, "outside: certificate silent\n(not support-2 necessity)", fontsize=8)
    ax2.legend(frameon=False, fontsize=8)
    save(fig2, out_dir, "QG1_QG16_certificate_cone_slice")


def qg2_figure(data: dict[str, Any], out_dir: pathlib.Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(8.0, 3.8))
    ax = axes[0]
    vals = [data["exact_forecasts"], data["counterexamples"]]
    bars = ax.bar(["exact on registered\nDP comparisons", "exact\ncounterexample"], vals)
    ax.set_yscale("symlog", linthresh=1)
    ax.set_ylabel("Registered comparison count (symlog)")
    ax.set_title(f"{data['dp_compared']:,} exact DP comparisons")
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x()+bar.get_width()/2, val*1.08 if val>1 else 1.2, f"{val:,}", ha="center", fontsize=8)

    ax2 = axes[1]
    vals2 = [data["counterexample_old_forecast"], data["counterexample_exact"], data["counterexample_repaired_f2"]]
    bars2 = ax2.bar(["old F", "exact DP", "repaired F2"], vals2)
    ax2.set_ylabel("Frozen structural cost")
    ax2.set_ylim(0, max(vals2)+2)
    ax2.set_title("One row refutes universal exactness")
    for bar, val in zip(bars2, vals2):
        ax2.text(bar.get_x()+bar.get_width()/2, val+0.15, str(val), ha="center")
    ax2.text(0.5, 0.03, f"R6S support ceiling ≤ {data['theorem_support_ceiling']} survives", transform=ax2.transAxes, ha="center", fontsize=8)
    save(fig, out_dir, "QG2_forecast_refutation_and_repair")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="build/q_qg_figures")
    args = ap.parse_args()
    out = ROOT / args.out
    out.mkdir(parents=True, exist_ok=True)

    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    errors: list[str] = []
    verified: dict[str, Any] = {"schema": "ORIONQ.FigureBuildVerification.v1", "figures": {}}

    for fig_id, spec in cfg["figures"].items():
        paper = spec["paper"]
        pool: list[float] = []
        source_rows = []
        for path in spec["sources"]:
            try:
                obj = load_source(paper, path)
            except Exception as exc:
                errors.append(f"SOURCE_LOAD_FAIL:{fig_id}:{path}:{exc}")
                continue
            vals = list(scalars(obj))
            pool.extend(vals)
            source_rows.append({"path": path, "numeric_scalars": len(vals)})
        missing = [v for v in spec.get("expected_values", []) if not found_number(float(v), pool)]
        if missing:
            errors.append(f"EXPECTED_VALUE_NOT_FOUND:{fig_id}:{missing}")
        verified["figures"][fig_id] = {
            "paper": paper,
            "sources": source_rows,
            "expected_values": spec.get("expected_values", []),
            "missing": missing,
        }

    if errors:
        print("Q_QG_FIGURE_BUILD=FAIL")
        for err in errors:
            print(f"- {err}")
        (out / "verification.json").write_text(json.dumps(verified, indent=2) + "\n", encoding="utf-8")
        return 1

    # Export exact source data used for plotting.
    (out / "source_data.json").write_text(
        json.dumps({k: v["data"] for k, v in cfg["figures"].items()}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out / "verification.json").write_text(json.dumps(verified, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    q1_figure(cfg["figures"]["Q1_counterexamples"]["data"], out)
    q2_figure(cfg["figures"]["Q2_denominator"]["data"], out)
    q4_figure(cfg["figures"]["Q4_primary_effects"]["data"], out)
    qg1_figures(cfg["figures"]["QG1_support_hierarchy"]["data"], out)
    qg2_figure(cfg["figures"]["QG2_refutation"]["data"], out)

    print("Q_QG_FIGURE_BUILD=PASS")
    print("RECEIPT_VERIFIED_EXPECTED_VALUES=PASS")
    print("FIGURES=6")
    print(f"OUTPUT={out.relative_to(ROOT)}")
    print("SCIENTIFIC_AUTHORITY=UNCHANGED_BY_FIGURES")
    return 0


if __name__ == "__main__":
    sys.exit(main())
