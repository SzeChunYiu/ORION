#!/usr/bin/env python3
"""Render Figure P2-2 (recall vs query-count curves).

This figure is generated from the archived OFFLINE_MECHANISMS_V1.json trajectory
data and never hand-transcribed.

Usage::

    python3 papers/orion-12-open-world-scientific-discovery/scripts/render_figure_p2_2.py            # write
    python3 papers/orion-12-open-world-scientific-discovery/scripts/render_figure_p2_2.py --check    # verify
    python3 papers/orion-12-open-world-scientific-discovery/scripts/render_figure_p2_2.py --stdout   # print

Matplotlib is an optional dependency under the ``plots`` extra.
Exit codes: 0 ok, 1 drift under ``--check``, 2 missing input.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zlib
import tempfile
import re
from pathlib import Path

PAPER_ROOT = Path(__file__).resolve().parents[1]
MECHANISMS_PATH = PAPER_ROOT / "evidence" / "offline_results" / "OFFLINE_MECHANISMS_V1.json"
FIGURE_OUTPUT = PAPER_ROOT / "manuscript" / "figures" / "P2-2_recall_vs_queries.pdf"
TEX_OUTPUT = PAPER_ROOT / "manuscript" / "figures" / "P2-2_recall_vs_queries.tex"
MANIFEST_OUTPUT = PAPER_ROOT / "manuscript" / "figures" / "P2-2_manifest.json"


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
            matplotlib.rcParams["font.size"] = 10
            matplotlib.rcParams["axes.labelsize"] = 10
            matplotlib.rcParams["axes.titlesize"] = 11
            matplotlib.rcParams["legend.fontsize"] = 9
            matplotlib.rcParams["xtick.labelsize"] = 9
            matplotlib.rcParams["ytick.labelsize"] = 9

        return plt
    except ImportError as e:
        print("ERROR: matplotlib is required for figure generation.", file=sys.stderr)
        print("Install with: uv pip install 'orion[plots]'", file=sys.stderr)
        print("Or: pip install matplotlib", file=sys.stderr)
        raise SystemExit(1) from e


def render_plt(trajectory_data: dict, plt, destination: Path | None = None) -> Path:
    """Generate the recall-vs-query-count figure using matplotlib."""
    # Extract trajectory data for the two systems
    orion_trajectory = trajectory_data["trajectory_systems"]["orion_full"]
    protocol_trajectory = trajectory_data["trajectory_systems"]["protocol_driven_systematic_review"]
    n_tasks = int(trajectory_data["n_tasks"])

    # Extract query counts and recall values
    orion_queries = [point["queries"] for point in orion_trajectory]
    orion_recall = [point["mean_complete_gold_recall"] for point in orion_trajectory]

    protocol_queries = [point["queries"] for point in protocol_trajectory]
    protocol_recall = [point["mean_complete_gold_recall"] for point in protocol_trajectory]

    # Create figure
    fig, ax = plt.subplots(figsize=(7, 5))

    # Plot ORION full (solid line)
    ax.plot(orion_queries, orion_recall, 'o-', linewidth=2, markersize=6,
            label='ORION full', color='#1f77b4', alpha=0.8)

    # Plot protocol-driven systematic review (dashed line)
    ax.plot(protocol_queries, protocol_recall, 's--', linewidth=2, markersize=6,
            label='Protocol-driven systematic review', color='#ff7f0e', alpha=0.8)

    # Add grid and labels
    ax.set_xlabel('Search query count', fontweight='bold')
    ax.set_ylabel('Complete-gold recall', fontweight='bold')
    ax.set_title('Cumulative Discovery vs Query Count', fontweight='bold')

    # Set y-axis limits
    ax.set_ylim(-0.05, 1.05)
    ax.set_xlim(-0.5, max(orion_queries) + 0.5)

    # Add grid
    ax.grid(True, alpha=0.3, linestyle='--')

    # Add legend
    ax.legend(loc='lower right', framealpha=0.9)

    # Add annotation about data source
    ax.text(0.02, 0.98, f'{n_tasks} frozen tasks; deterministic repeats collapsed; descriptive only',
            transform=ax.transAxes, fontsize=8, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

    fig.tight_layout()

    # Save PDF
    target = destination or FIGURE_OUTPUT
    target.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(target, format='pdf', dpi=300, bbox_inches='tight')
    plt.close(fig)

    return target


def render_tex(trajectory_data: dict) -> str:
    """Generate the LaTeX version of the figure for manuscript inclusion."""
    lines: list[str] = []
    add = lines.append
    n_tasks = int(trajectory_data["n_tasks"])

    add("% GENERATED from evidence/offline_results/OFFLINE_MECHANISMS_V1.json")
    add("% Regenerate with: papers/orion-12-open-world-scientific-discovery/scripts/render_figure_p2_2.py")
    add("\\begin{tikzpicture}[x=0.48cm,y=5.0cm]")

    # Axes
    add("\\draw[->] (0,0) -- (12.7,0) node[right]{search queries};")
    add("\\draw[->] (0,0) -- (0,1.08);")
    add("\\node[rotate=90,anchor=south] at (-1.02,0.54) {complete-gold recall};")

    # Tick marks
    add("\\foreach \\x in {0,2,4,6,8,10,12} \\draw (\\x,0.012) -- (\\x,-0.012) node[below]{\\x};")
    add("\\foreach \\y/\\lab in {0/0,0.25/.25,0.5/.50,0.75/.75,1/1.0} \\draw (0.10,\\y) -- (-0.10,\\y) node[left]{\\lab};")

    # TikZ coordinates are whitespace-separated. Commas between tuples make
    # pgf parse the next tuple as part of the previous coordinate and fail.
    orion_trajectory = trajectory_data["trajectory_systems"]["orion_full"]
    orion_coords = " ".join(f"({pt['queries']},{pt['mean_complete_gold_recall']:.6f})" for pt in orion_trajectory)
    add(f"\\draw[thick] plot coordinates {{{orion_coords}}};")

    protocol_trajectory = trajectory_data["trajectory_systems"]["protocol_driven_systematic_review"]
    protocol_coords = " ".join(f"({pt['queries']},{pt['mean_complete_gold_recall']:.6f})" for pt in protocol_trajectory)
    add(f"\\draw[thick,dashed] plot coordinates {{{protocol_coords}}};")

    # Labels
    add("\\node[anchor=west] at (8.3,0.94) {ORION full};")
    add("\\node[anchor=west] at (8.3,0.69) {Protocol SLR};")
    add(f"\\node[anchor=west,font=\\scriptsize] at (0,1.14) {{{n_tasks} frozen tasks; repeats collapsed; descriptive only}};")

    add("\\end{tikzpicture}")
    return "\n".join(lines)


def _matplotlib_version() -> str:
    import matplotlib

    return matplotlib.__version__


def compute_manifest() -> dict:
    """Compute SHA256 hashes of generated artifacts."""
    manifest: dict[str, any] = {
        "generated_by": "scripts/render_figure_p2_2.py",
        "source_hash": {
            "OFFLINE_MECHANISMS_V1.json": hashlib.sha256(
                MECHANISMS_PATH.read_bytes()
            ).hexdigest()
        },
        "artifacts": {}
    }

    if FIGURE_OUTPUT.exists():
        manifest["artifacts"]["pdf"] = {
            "path": str(FIGURE_OUTPUT.relative_to(PAPER_ROOT)),
            "sha256": hashlib.sha256(FIGURE_OUTPUT.read_bytes()).hexdigest(),
            "size_bytes": FIGURE_OUTPUT.stat().st_size,
        }
    else:
        manifest["artifacts"]["pdf"] = {"error": "file not generated"}

    if TEX_OUTPUT.exists():
        manifest["artifacts"]["tex"] = {
            "path": str(TEX_OUTPUT.relative_to(PAPER_ROOT)),
            "sha256": hashlib.sha256(TEX_OUTPUT.read_bytes()).hexdigest(),
            "size_bytes": TEX_OUTPUT.stat().st_size,
        }
    else:
        manifest["artifacts"]["tex"] = {"error": "file not generated"}

    manifest["matplotlib_version"] = _matplotlib_version()
    return manifest



def _check(mechanisms_data: dict, rendered_tex: str) -> int:
    """Compare the committed artifacts against a fresh render, writing nothing.

    The previous `--check` wrote the tex, the PDF and the manifest and *then* asserted
    that those freshly written files existed. It destroyed the evidence of drift before
    looking for it, so it could not fail -- which is how the manifest came to record a
    `source_hash` for a version of `OFFLINE_MECHANISMS_V1.json` that is no longer in the
    tree, and how the committed PDF came to differ from what the committed data renders.

    Absent is reported separately from different. "Could not check" is not a pass.
    """

    missing = [path for path in (TEX_OUTPUT, FIGURE_OUTPUT, MANIFEST_OUTPUT) if not path.exists()]
    if missing:
        for path in missing:
            print(f"CANNOT_CHECK: committed artifact absent: {path}", file=sys.stderr)
        return 2

    drift: list[str] = []

    if TEX_OUTPUT.read_text(encoding="utf-8") != rendered_tex:
        drift.append(f"{TEX_OUTPUT.name}: committed tex differs from a fresh render")

    manifest = json.loads(MANIFEST_OUTPUT.read_text(encoding="utf-8"))
    recorded_source = manifest.get("source_hash", {}).get(MECHANISMS_PATH.name)
    actual_source = hashlib.sha256(MECHANISMS_PATH.read_bytes()).hexdigest()
    if recorded_source != actual_source:
        drift.append(
            f"{MANIFEST_OUTPUT.name}: records source_hash {recorded_source} for "
            f"{MECHANISMS_PATH.name}, which currently hashes to {actual_source}"
        )

    # The PDF is only comparable against the renderer that produced it. Matplotlib changes
    # its output between minor versions, so running a different one and reporting DRIFT
    # would be a false alarm, and reporting a pass would be worse. Say which it is.
    recorded_renderer = manifest.get("matplotlib_version")
    running_renderer = _matplotlib_version()
    unchecked: list[str] = []
    if recorded_renderer is not None and recorded_renderer != running_renderer:
        unchecked.append(
            f"{FIGURE_OUTPUT.name}: rendered by matplotlib {recorded_renderer}, running "
            f"{running_renderer}; figure content is not comparable across renderer versions"
        )
    else:
        with tempfile.TemporaryDirectory(prefix="p2-2-check-") as scratch:
            fresh_pdf = render_plt(mechanisms_data, _import_matplotlib(), Path(scratch) / FIGURE_OUTPUT.name)
            # Matplotlib stamps a CreationDate, so the bytes never match. The drawn content
            # is what matters, and it is deterministic: two renders of the same data under
            # one renderer version produce identical content streams.
            if _pdf_content(fresh_pdf) != _pdf_content(FIGURE_OUTPUT):
                drift.append(f"{FIGURE_OUTPUT.name}: committed figure content differs from a fresh render")

    if drift:
        for line in drift:
            print(f"DRIFT: {line}", file=sys.stderr)
        return 1

    if unchecked:
        for line in unchecked:
            print(f"CANNOT_CHECK: {line}", file=sys.stderr)
        print("P2-2 tex and manifest source hash match; the figure content was not comparable")
        return 3

    print("P2-2 tex, figure content and manifest source hash all match the committed data")
    return 0


def _pdf_content(path: Path) -> bytes:
    """The drawn content of a PDF, excluding the metadata matplotlib stamps with a clock."""

    raw = path.read_bytes()
    streams = []
    for match in re.finditer(rb"stream\r?\n(.*?)endstream", raw, re.S):
        try:
            streams.append(zlib.decompress(match.group(1)))
        except zlib.error:
            streams.append(match.group(1))
    return b"".join(streams)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if committed artifacts differ from fresh render")
    parser.add_argument("--stdout", action="store_true", help="print LaTeX instead of writing files")
    args = parser.parse_args(argv)

    if not MECHANISMS_PATH.exists():
        print(f"missing mechanisms input: {MECHANISMS_PATH}", file=sys.stderr)
        return 2

    # Load trajectory data
    mechanisms_data = json.loads(MECHANISMS_PATH.read_text(encoding="utf-8"))

    # Render LaTeX
    rendered_tex = render_tex(mechanisms_data)

    if args.stdout:
        sys.stdout.write(rendered_tex)
        return 0

    if args.check:
        return _check(mechanisms_data, rendered_tex)

    # Write LaTeX
    TEX_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    TEX_OUTPUT.write_text(rendered_tex, encoding="utf-8")

    # Generate PDF with matplotlib
    plt = _import_matplotlib()
    render_plt(mechanisms_data, plt)
    print(f"wrote {FIGURE_OUTPUT}")

    # Write manifest
    manifest = compute_manifest()
    MANIFEST_OUTPUT.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {MANIFEST_OUTPUT}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
