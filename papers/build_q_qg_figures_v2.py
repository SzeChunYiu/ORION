#!/usr/bin/env python3
"""Build standalone Q/QG publication plots from receipt-verified source data.

V2 supersedes the exploratory V1 plot layout. Every quantitative chart is a distinct figure
(no subplot grids). Source validation is identical in spirit: each configured scalar must be
found in the bound source artifacts at the paper-specific scientific cut before plotting.
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
    if paper == "Q2" and path.startswith("papers/"):
        return json.loads((ROOT / path).read_text(encoding="utf-8"))
    return json.loads(git_show(CUTS[paper], path))


def scalars(obj: Any):
    if isinstance(obj, dict):
        for value in obj.values():
            yield from scalars(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from scalars(value)
    elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
        yield float(obj)


def found_number(value: float, pool: list[float]) -> bool:
    return any(math.isclose(float(value), x, rel_tol=1e-12, abs_tol=1e-12) for x in pool)


def save(fig, out_dir: pathlib.Path, stem: str) -> None:
    fig.tight_layout()
    fig.savefig(out_dir / f"{stem}.svg", bbox_inches="tight")
    fig.savefig(out_dir / f"{stem}.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def bar_plot(out_dir: pathlib.Path, stem: str, title: str, ylabel: str, names: list[str], vals: list[float], *, zero_line: bool = False, ylim: tuple[float, float] | None = None) -> None:
    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    bars = ax.bar(names, vals)
    if zero_line:
        ax.axhline(0, linewidth=0.7)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", labelrotation=15)
    if ylim is not None:
        ax.set_ylim(*ylim)
    spread = max(vals) - min(vals) if vals else 1
    offset = max(0.03 * (spread if spread else 1), 0.05)
    for bar, val in zip(bars, vals):
        y = val + offset if val >= 0 else val - offset
        ax.text(bar.get_x() + bar.get_width()/2, y, f"{val:g}", ha="center", va="bottom" if val >= 0 else "top", fontsize=8)
    save(fig, out_dir, stem)


def build_q1(data: dict[str, Any], out: pathlib.Path) -> list[str]:
    names = ["Split-anchor\nrefutation", "Frame-for-Tag\nborrow"]
    exact = [data["split"]["exact"], data["borrow"]["exact"]]
    restricted = [data["split"]["restricted"], data["borrow"]["restricted"]]
    x = np.arange(len(names))
    width = 0.35
    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    ax.bar(x - width/2, exact, width, label="Exact optimum")
    ax.bar(x + width/2, restricted, width, label="Restricted family")
    ax.set_ylabel("Frozen structural cost")
    ax.set_xticks(x, names)
    ax.set_ylim(0, max(restricted) + 2)
    ax.legend(frameon=False)
    ax.set_title("Exact counterexamples open restricted families")
    ax.text(
        0.5, 0.02,
        f"Separate R6S theorem: all-n support ceiling ≤ {data['all_n_support_ceiling']}",
        transform=ax.transAxes, ha="center", va="bottom", fontsize=8,
    )
    stem = "Q1_counterexamples_and_support_ceiling_v2"
    save(fig, out, stem)
    return [stem]


def build_q2(data: dict[str, Any], out: pathlib.Path) -> list[str]:
    stem = "Q2_declared_denominator_v2"
    bar_plot(
        out, stem, "Q2 frozen publication denominator", "Count",
        ["Declared\nreceipts", "Graph\nnodes", "Explicit\nexclusions", "Successor\nedges", "Standalone\nnegatives"],
        [data["declared_receipt_universe"], data["included_graph_nodes"], data["explicit_exclusions"], data["asserted_successor_edges"], data["standalone_negative_or_absorbed_nodes"]],
    )
    return [stem]


def build_q4(data: dict[str, Any], out: pathlib.Path) -> list[str]:
    stems: list[str] = []
    specs = [
        ("Q4_N4A_typed_prior", "N4-A: typed versus flattened prior", "mean utility", ["typed", "flat prior", "known graph"], [data["N4_A"]["candidate"], data["N4_A"]["control"], data["N4_A"]["other"]]),
        ("Q4_N4B_scoped_reopening", "N4-B: dependency scope controls reopening", "mean utility", ["scoped", "never", "unscoped", "always"], [data["N4_B"]["candidate"], data["N4_B"]["control"], data["N4_B"]["other"], data["N4_B"]["hostile"]]),
        ("Q4_N4C_targeted_verification", "N4-C: decision-targeted verification", "mean scalarized regret ↓", ["targeted", "random"], [data["N4_C"]["candidate"], data["N4_C"]["control"]]),
        ("Q4_N4D_chain_transport", "N4-D: full-chain transport checking", "registered battery rate", ["full recall", "last-hop recall", "full FPR"], [data["N4_D"]["candidate_recall"], data["N4_D"]["last_hop_recall"], data["N4_D"]["candidate_fpr"]]),
        ("Q4_N4E_decision_coupled", "N4-E: decision-coupled probing", "mean utility", ["decision", "info gain"], [data["N4_E"]["candidate"], data["N4_E"]["control"]]),
        ("Q4_N4F3_remint_transport", "N4-F3: typed remint/transport", "mixed-transport mean utility", ["typed", "rederive", "carry"], [data["N4_F3"]["candidate"], data["N4_F3"]["control"], data["N4_F3"]["naive"]]),
    ]
    for stem, title, ylabel, names, vals in specs:
        bar_plot(out, stem, title, ylabel, names, vals, zero_line=True)
        stems.append(stem)
    return stems


def build_qg1(data: dict[str, Any], out: pathlib.Path) -> list[str]:
    stems: list[str] = []
    stem1 = "QG1_R6I_support_bound_hierarchy_v2"
    bar_plot(
        out, stem1, "R6I: sound proof ceiling versus intrinsic support", "Support bound",
        ["QG6 syndrome-rank\nsafe ceiling", "QG9 intrinsic\nsupport number"],
        [data["r6i_safe_syndrome_rank_ceiling"], data["r6i_intrinsic_support_number"]],
        ylim=(0, data["r6i_safe_syndrome_rank_ceiling"] + 1.5),
    )
    stems.append(stem1)

    y = np.linspace(0, 4.5, 400)
    boundary = np.maximum(5.0, 2.0 + 2.0 * y)
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    ax.plot(boundary, y, label="certificate boundary")
    ax.fill_betweenx(y, boundary, 12, alpha=0.2, label="support-one certificate applies")
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 4.5)
    ax.set_xlabel(r"$(t_c+t_{nc})/t_r$")
    ax.set_ylabel(r"$t_{tag}/t_r$")
    ax.set_title(r"QG16 normalized certificate slice ($t_r>0$, $t_c\leq t_{nc}$)")
    ax.text(0.6, 3.8, "outside: certificate silent\n(not support-two necessity)", fontsize=8)
    ax.legend(frameon=False, fontsize=8)
    stem2 = "QG1_QG16_certificate_cone_slice_v2"
    save(fig, out, stem2)
    stems.append(stem2)
    return stems


def build_qg2(data: dict[str, Any], out: pathlib.Path) -> list[str]:
    stems: list[str] = []
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    vals = [data["exact_forecasts"], data["counterexamples"]]
    bars = ax.bar(["exact on registered\nDP comparisons", "exact\ncounterexample"], vals)
    ax.set_yscale("symlog", linthresh=1)
    ax.set_ylabel("Registered comparison count (symlog)")
    ax.set_title(f"Initial forecaster: {data['dp_compared']:,} exact-DP comparisons")
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x()+bar.get_width()/2, val*1.08 if val > 1 else 1.2, f"{val:,}", ha="center", fontsize=8)
    stem1 = "QG2_registered_comparison_counts_v2"
    save(fig, out, stem1)
    stems.append(stem1)

    stem2 = "QG2_exact_counterexample_repair_v2"
    bar_plot(
        out, stem2, "One exact row refutes universal closed-form exactness", "Frozen structural cost",
        ["old F", "exact DP", "repaired F2"],
        [data["counterexample_old_forecast"], data["counterexample_exact"], data["counterexample_repaired_f2"]],
        ylim=(0, max(data["counterexample_old_forecast"], data["counterexample_exact"]) + 2),
    )
    stems.append(stem2)
    return stems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="build/q_qg_figures_v2")
    args = ap.parse_args()
    out = ROOT / args.out
    out.mkdir(parents=True, exist_ok=True)
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))

    errors: list[str] = []
    verification: dict[str, Any] = {"schema": "ORIONQ.FigureBuildVerification.v2", "figures": {}}
    for fig_id, spec in cfg["figures"].items():
        pool: list[float] = []
        source_rows = []
        for path in spec["sources"]:
            try:
                obj = load_source(spec["paper"], path)
            except Exception as exc:
                errors.append(f"SOURCE_LOAD_FAIL:{fig_id}:{path}:{exc}")
                continue
            vals = list(scalars(obj))
            pool.extend(vals)
            source_rows.append({"path": path, "numeric_scalars": len(vals)})
        missing = [v for v in spec.get("expected_values", []) if not found_number(float(v), pool)]
        if missing:
            errors.append(f"EXPECTED_VALUE_NOT_FOUND:{fig_id}:{missing}")
        verification["figures"][fig_id] = {"sources": source_rows, "expected_values": spec.get("expected_values", []), "missing": missing}

    (out / "verification.json").write_text(json.dumps(verification, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if errors:
        print("Q_QG_FIGURE_BUILD_V2=FAIL")
        for err in errors:
            print(f"- {err}")
        return 1

    (out / "source_data.json").write_text(
        json.dumps({k: v["data"] for k, v in cfg["figures"].items()}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    stems: list[str] = []
    stems += build_q1(cfg["figures"]["Q1_counterexamples"]["data"], out)
    stems += build_q2(cfg["figures"]["Q2_denominator"]["data"], out)
    stems += build_q4(cfg["figures"]["Q4_primary_effects"]["data"], out)
    stems += build_qg1(cfg["figures"]["QG1_support_hierarchy"]["data"], out)
    stems += build_qg2(cfg["figures"]["QG2_refutation"]["data"], out)

    (out / "generated_stems.json").write_text(json.dumps(stems, indent=2) + "\n", encoding="utf-8")
    print("Q_QG_FIGURE_BUILD_V2=PASS")
    print("RECEIPT_VERIFIED_EXPECTED_VALUES=PASS")
    print(f"STANDALONE_FIGURES={len(stems)}")
    print(f"OUTPUT={out.relative_to(ROOT)}")
    print("SCIENTIFIC_AUTHORITY=UNCHANGED_BY_FIGURES")
    return 0


if __name__ == "__main__":
    sys.exit(main())
