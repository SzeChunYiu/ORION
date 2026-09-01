"""Deterministic Matplotlib styling and accessible evidence-state encodings."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Iterable

import matplotlib

# Headless, deterministic rendering is part of the public contract.  This call
# must precede pyplot imports in every module in this package.
matplotlib.use("Agg", force=True)

from matplotlib import pyplot as plt  # noqa: E402

from .authority import EvidenceStatus, classify_status


# Colors are chosen from/around color-vision-deficiency-safe palettes.  Status
# plots additionally use distinct glyphs so meaning never depends on hue alone.
STATUS_COLORS: dict[EvidenceStatus, str] = {
    EvidenceStatus.PASS: "#0072B2",  # blue
    EvidenceStatus.FAIL: "#D55E00",  # vermillion
    EvidenceStatus.UNKNOWN: "#6B7280",  # neutral gray
    EvidenceStatus.CANNOT_CHECK: "#6F2DBD",  # purple
    EvidenceStatus.NULL: "#B8B8B8",  # light gray
    EvidenceStatus.ADVERSE: "#CC79A7",  # reddish purple
    EvidenceStatus.MIXED: "#E69F00",  # orange
}

STATUS_MARKERS: dict[EvidenceStatus, str] = {
    EvidenceStatus.PASS: "o",
    EvidenceStatus.FAIL: "X",
    EvidenceStatus.UNKNOWN: "D",
    EvidenceStatus.CANNOT_CHECK: "s",
    EvidenceStatus.NULL: "P",
    EvidenceStatus.ADVERSE: "v",
    EvidenceStatus.MIXED: "h",
}

STATUS_SYMBOLS: dict[EvidenceStatus, str] = {
    EvidenceStatus.PASS: "P",
    EvidenceStatus.FAIL: "F",
    EvidenceStatus.UNKNOWN: "?",
    EvidenceStatus.CANNOT_CHECK: "C/C",
    EvidenceStatus.NULL: "null",
    EvidenceStatus.ADVERSE: "adv",
    EvidenceStatus.MIXED: "mix",
}


def apply_atlas_style() -> None:
    """Apply a compact, deterministic style suitable for print and notebooks."""

    matplotlib.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.labelsize": 10,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": False,
            "figure.dpi": 120,
            "savefig.dpi": 300,
            "savefig.transparent": False,
            "pdf.fonttype": 42,
            "svg.fonttype": "none",
            "svg.hashsalt": "orion-visualization-atlas-v1",
        }
    )


def status_color(value: Any) -> str:
    return STATUS_COLORS[classify_status(value)]


def status_marker(value: Any) -> str:
    return STATUS_MARKERS[classify_status(value)]


def new_figure(*, figsize: tuple[float, float] = (7.2, 4.5), constrained_layout: bool = True):
    """Create a styled Figure/Axes pair."""

    apply_atlas_style()
    return plt.subplots(figsize=figsize, constrained_layout=constrained_layout)


def save_figure(
    figure,
    output_base: str | os.PathLike[str],
    *,
    formats: Iterable[str] = ("png", "svg"),
) -> tuple[Path, ...]:
    """Save an Agg figure with stable SVG identifiers and no timestamps."""

    apply_atlas_style()
    base = Path(output_base)
    if base.suffix.lower() in {".png", ".svg"}:
        base = base.with_suffix("")
    base.parent.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    for item in formats:
        format_name = item.lower().lstrip(".")
        if format_name not in {"png", "svg"}:
            raise ValueError("formats may contain only 'png' and 'svg'")
        target = base.with_suffix(f".{format_name}")
        metadata: dict[str, Any]
        if format_name == "svg":
            metadata = {"Creator": "ORION visualization atlas", "Date": None}
        else:
            metadata = {"Software": "ORION visualization atlas"}
        figure.savefig(
            target,
            format=format_name,
            facecolor="white",
            metadata=metadata,
            bbox_inches="tight",
        )
        if format_name == "svg":
            # Matplotlib may leave spaces at the ends of path-data lines. They
            # are semantically irrelevant XML whitespace but make the generated
            # artifacts fail Git's whitespace check, so canonicalize them.
            lines = target.read_text(encoding="utf-8").splitlines()
            target.write_text(
                "\n".join(line.rstrip() for line in lines) + "\n",
                encoding="utf-8",
            )
        outputs.append(target)
    return tuple(outputs)


apply_atlas_style()
