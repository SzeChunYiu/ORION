#!/usr/bin/env python3
"""Render the P1 v2.2.4 primary/replication result figure from archives."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "papers" / "orion-11-recursive-epistemic-reconstruction"
EVIDENCE = ROOT / "research" / "revival" / "p1" / "confirmatory" / "v2.2"
PRIMARY = EVIDENCE / "primary" / "PRIMARY_RESULT.json"
REPLICATION = EVIDENCE / "replication" / "REPLICATION_RESULT.json"
OUTPUT = PAPER / "manuscript" / "figures" / "P1-7_necessity_replication.pdf"

SYSTEMS = (
    ("active_voi_repair_parent", "Active-VOI"),
    ("darc_r2act_dependency_parent", "DARC/R2Act"),
    ("causalflow_minimal_counterfactual_parent", "CausalFlow"),
    ("orion_mutation_necessity", "ORION"),
)
ABLATIONS = (
    ("orion_mutation_necessity", "Full"),
    ("orion_without_protected_sibling_check", "No sibling"),
    ("orion_without_dependency_impact_binding", "No dependency"),
    ("orion_without_lower_level_exclusion", "No lower-level"),
    ("orion_without_KWM_level_ordering", "No K/W/M"),
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(output: Path) -> None:
    os.environ.setdefault("MPLCONFIGDIR", "/tmp/orion-matplotlib")
    import matplotlib

    matplotlib.use("Agg")
    matplotlib.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "pdf.fonttype": 42,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )
    import matplotlib.pyplot as plt
    import numpy as np

    primary = _load(PRIMARY)["arm_summary"]
    replication = _load(REPLICATION)["arm_summary"]
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.0))
    colors = ("#335C81", "#D17A22")
    width = 0.36

    x = np.arange(len(SYSTEMS))
    primary_hidden = [
        primary[key]["hidden_shift_protected_root_task_success_rate"]
        for key, _ in SYSTEMS
    ]
    replication_hidden = [
        replication[key]["hidden_shift_protected_root_task_success_rate"]
        for key, _ in SYSTEMS
    ]
    axes[0].bar(x - width / 2, primary_hidden, width, label="Primary", color=colors[0])
    axes[0].bar(
        x + width / 2,
        replication_hidden,
        width,
        label="Replication",
        color=colors[1],
    )
    axes[0].set_xticks(x, [label for _, label in SYSTEMS], rotation=18, ha="right")
    axes[0].set_ylabel("Protected root-task success")
    axes[0].set_title("a  Hidden-shift comparison")
    axes[0].legend(frameon=False, loc="upper left")

    x = np.arange(len(ABLATIONS))
    primary_ablation = [
        primary[key]["protected_root_task_success_rate"] for key, _ in ABLATIONS
    ]
    replication_ablation = [
        replication[key]["protected_root_task_success_rate"] for key, _ in ABLATIONS
    ]
    axes[1].bar(x - width / 2, primary_ablation, width, color=colors[0])
    axes[1].bar(x + width / 2, replication_ablation, width, color=colors[1])
    axes[1].set_xticks(
        x,
        [label for _, label in ABLATIONS],
        rotation=18,
        ha="right",
    )
    axes[1].set_ylabel("Whole-grid protected success")
    axes[1].set_title("b  Registered mechanism ablations")

    for axis in axes:
        axis.set_ylim(0, 1.08)
        axis.set_yticks(np.linspace(0, 1, 6))
        axis.grid(axis="y", color="#D9D9D9", linewidth=0.6)
        axis.set_axisbelow(True)

    fig.suptitle("P1 v2.2.4: pre-bound primary and disjoint replication", y=1.01)
    fig.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        output,
        format="pdf",
        bbox_inches="tight",
        metadata={
            "Title": "P1 v2.2.4 primary and replication",
            "Author": "ORION",
            "Creator": "make_necessity_figure.py",
            "CreationDate": None,
            "ModDate": None,
        },
    )
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        if not OUTPUT.exists():
            raise SystemExit(f"missing figure: {OUTPUT}")
        with tempfile.TemporaryDirectory(prefix="p1-necessity-figure-") as temp:
            candidate = Path(temp) / OUTPUT.name
            render(candidate)
            if _sha(candidate) != _sha(OUTPUT):
                raise SystemExit("P1-7 figure is stale")
        print(f"P1-7 current: {_sha(OUTPUT)}")
        return 0
    render(OUTPUT)
    print(f"wrote {OUTPUT} {_sha(OUTPUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
