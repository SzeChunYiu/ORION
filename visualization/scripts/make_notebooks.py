#!/usr/bin/env python3
"""Deterministically build the ORION evidence-atlas notebooks.

The generator deliberately uses only the Python standard library.  Notebook
runtime cells use matplotlib, plus the normalized, receipt-derived atlas.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


VISUALIZATION_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = VISUALIZATION_ROOT / "notebooks"


def _lines(source: str) -> list[str]:
    source = source.strip("\n") + "\n"
    return source.splitlines(keepends=True)


def _markdown(cell_id: str, source: str) -> dict[str, object]:
    return {
        "cell_type": "markdown",
        "id": cell_id,
        "metadata": {},
        "source": _lines(source),
    }


def _code(cell_id: str, source: str, *, tags: list[str] | None = None) -> dict[str, object]:
    metadata: dict[str, object] = {}
    if tags:
        metadata["tags"] = tags
    return {
        "cell_type": "code",
        "execution_count": None,
        "id": cell_id,
        "metadata": metadata,
        "outputs": [],
        "source": _lines(source),
    }


def _notebook(cells: list[dict[str, object]]) -> dict[str, object]:
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


BOOTSTRAP = r'''
from pathlib import Path
import json
import sys


def find_visualization_root(start=Path.cwd()):
    """Find visualization/ whether Jupyter starts at the repo root or notebooks/."""
    start = start.resolve()
    candidates = [start / "visualization", start, *start.parents]
    for candidate in candidates:
        if candidate.name == "visualization" and (candidate / "data" / "derived" / "atlas.json").exists():
            return candidate
        nested = candidate / "visualization"
        if (nested / "data" / "derived" / "atlas.json").exists():
            return nested
    raise FileNotFoundError(
        "Could not find visualization/data/derived/atlas.json. "
        "Build the atlas from the repository root first."
    )


VIS_ROOT = find_visualization_root()
sys.path.insert(0, str(VIS_ROOT / "src"))
ATLAS_PATH = VIS_ROOT / "data" / "derived" / "atlas.json"
atlas = json.loads(ATLAS_PATH.read_text(encoding="utf-8"))


def as_rows(value):
    """Return normalized records without changing their scientific values."""
    if isinstance(value, list):
        return [row for row in value if isinstance(row, dict)]
    if isinstance(value, dict):
        return [row for row in value.values() if isinstance(row, dict)]
    return []


def first(row, *keys, default=None):
    for key in keys:
        if key in row and row[key] is not None:
            return row[key]
    return default


def paper_id(row):
    raw = str(first(row, "paper_id", "paper", "id", default="UNSCOPED"))
    return raw.replace("ORION-", "")


def exact_status(row):
    return str(first(row, "terminal", "status", "result_state", "authority", default="UNSPECIFIED"))


def numeric_value(row):
    value = first(row, "value", "observed", "count", default=None)
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None


paper_states = as_rows(atlas.get("paper_states", []))
metrics_by_paper = atlas.get("metrics", {})
metrics = as_rows(atlas.get("metric_records", []))
anomalies = as_rows(atlas.get("anomalies", []))
sources = as_rows(atlas.get("sources", []))
des_execution = as_rows(atlas.get("des_execution", []))
framework_mechanics = atlas.get("framework_mechanics", {})

print(f"Atlas: {ATLAS_PATH}")
print(
    f"Loaded {len(paper_states)} paper states, {len(metrics)} metrics, "
    f"{len(anomalies)} anomalies, {len(des_execution)} frozen DES rows and "
    f"{len(sources)} sources."
)
'''


STYLE = r"""
import matplotlib.pyplot as plt
import textwrap
from matplotlib.colors import ListedColormap  # noqa: F401 -- used by heatmap notebooks

plt.rcParams.update({
    "figure.figsize": (10, 5.5),
    "axes.grid": True,
    "grid.alpha": 0.20,
    "font.size": 10,
})

STATE_COLORS = {
    "PASS": "#2e7d32",
    "SUPPORTED": "#2e7d32",
    "FAIL": "#c62828",
    "GATE_NOT_MET": "#c62828",
    "CANNOT_CHECK": "#ef6c00",
    "UNKNOWN": "#6a1b9a",
    "NOT_AUTHORITY": "#455a64",
    "NOT_EXECUTED": "#757575",
}


def state_color(text):
    upper = str(text).upper()
    for token, color in STATE_COLORS.items():
        if token in upper:
            return color
    return "#1565c0"


def human_label(value, width=18):
    # Wrap machine identifiers without changing canonical capitalization.
    cleaned = str(value).replace("_", " ").replace(":", " — ")
    return "\n".join(textwrap.wrap(cleaned, width=width, break_long_words=False))
"""


DISPLAY_HELPERS = r'''
def print_records(rows, fields, limit=30):
    """Small dependency-free table for exact atlas fields."""
    rows = list(rows)
    if not rows:
        print("No records match the current display selectors.")
        return
    widths = {
        field: min(
            48,
            max(len(field), *(len(str(first(row, field, default=""))) for row in rows[:limit])),
        )
        for field in fields
    }
    print(" | ".join(field.ljust(widths[field]) for field in fields))
    print("-+-".join("-" * widths[field] for field in fields))
    for row in rows[:limit]:
        print(" | ".join(str(first(row, field, default=""))[: widths[field]].ljust(widths[field]) for field in fields))
    if len(rows) > limit:
        print(f"... {len(rows) - limit} more record(s); change DISPLAY_LIMIT to inspect them.")
'''


OVERVIEW_CELLS = [
    _markdown(
        "overview-title",
        r"""
# ORION P1–P15 evidence atlas

## Scope and authority

This notebook is a **receipt browser**, not a new experiment and not a publication-readiness certificate. It visualizes normalized fields copied from repository evidence. A local replay, finite witness, hash, or passing harness can establish only its registered bounded scope. It does **not** establish external independence, broad generalization, superiority, novelty, or top-tier readiness. `FAIL`, `UNKNOWN`, `CANNOT_CHECK`, `GATE_NOT_MET`, `NOT_AUTHORITY`, and not-executed outcomes remain visible.

The notebook reads `visualization/data/derived/atlas.json`; it never replaces the cited source receipt.
""",
    ),
    _markdown(
        "overview-theory",
        r"""
## Theory and methodology

ORION treats epistemic state and claim authority as typed, revisable objects. A compact reading aid is

$$S_t=(K_t,W_t,M_t), \qquad S_{t+1}=\mathcal{T}(S_t,e_t),$$

where $K$ is current knowledge, $W$ records unresolved/unknown material, $M$ records methods or mechanics, and $e_t$ is new evidence. The visual atlas adds no new transition: it projects already committed receipts.

The non-escalation rule is represented schematically as

$$\operatorname{claim}(r)\;\preceq\;\operatorname{authority}(r)\;\preceq\;\operatorname{scope}(r).$$

`\preceq` means “no broader than,” not a numeric score. The categorical matrix below shows **membership in the atlas's recorded status classes**; exact terminal strings remain visible in the table rather than becoming unreadable axis labels. Its cells are not ordered quality grades.
""",
    ),
    _code("overview-load", BOOTSTRAP),
    _code("overview-style", STYLE + "\n\n" + DISPLAY_HELPERS),
    _markdown(
        "overview-controls-doc",
        r"""
## Editable display selectors

Edit and rerun the next cell. Selectors only change the view; they never change the atlas or erase the full anomaly count printed later.
""",
    ),
    _code(
        "overview-controls",
        r"""
PAPERS = [f"P{i}" for i in range(1, 16)]
STATUS_CONTAINS = None      # e.g. "CANNOT_CHECK"; None shows every exact state
DISPLAY_LIMIT = 30
""",
        tags=["parameters"],
    ),
    _markdown(
        "overview-results",
        r"""
## Results: recorded status-class map

Each filled cell says only that the recorded status class occurs for that paper in the normalized atlas. Exact terminals are retained in the table below. Multiple cells in a row are expected when a paper has multiple scoped results.
""",
    ),
    _code(
        "overview-heatmap",
        r"""
selected_states = [
    row for row in paper_states
    if paper_id(row) in PAPERS
    and (STATUS_CONTAINS is None or STATUS_CONTAINS.upper() in exact_status(row).upper())
]

status_classes = sorted({str(first(row, "status", default="UNSPECIFIED")) for row in selected_states})
matrix = [
    [int(any(paper_id(row) == pid and str(first(row, "status", default="UNSPECIFIED")) == state for row in selected_states))
     for state in status_classes]
    for pid in PAPERS
]

fig, ax = plt.subplots(figsize=(max(9, 1.15 * len(status_classes)), 7))
if status_classes:
    image = ax.imshow(matrix, aspect="auto", cmap=ListedColormap(["#f5f5f5", "#1565c0"]), vmin=0, vmax=1)
    ax.set_xticks(range(len(status_classes)), [human_label(state, 16) for state in status_classes])
    ax.set_yticks(range(len(PAPERS)), PAPERS)
    ax.grid(False)
    ax.set_title("Recorded status-class membership (binary display, not a quality scale)")
    for i, row in enumerate(matrix):
        for j, present in enumerate(row):
            if present:
                ax.text(j, i, "●", ha="center", va="center", color="white", fontsize=8)
else:
    ax.text(0.5, 0.5, "No states match the selectors", ha="center", va="center")
    ax.set_axis_off()
plt.tight_layout()
plt.show()
""",
    ),
    _code(
        "overview-table",
        r"""
print_records(
    selected_states,
    ["paper_id", "title", "status", "terminal", "authority", "claim_ceiling"],
    DISPLAY_LIMIT,
)
print(f"\nUnfiltered anomaly records retained in atlas: {len(anomalies)}")
""",
    ),
    _markdown(
        "overview-discussion",
        r"""
## Discussion and anomaly reading

Heterogeneous terminal strings are intentional: ORION separates execution, scientific validity, and claim authority. A green local result beside `CANNOT_CHECK` is not contradictory when the former concerns a bounded replay and the latter concerns external or prospective authority. Review the anomaly notebook before interpreting any isolated metric.

## Claim ceiling

This view can support statements about what the cited repository receipts record. It cannot independently validate those receipts or convert local/bounded evidence into submission readiness. See `visualization/reports/CLAIM_CEILINGS.md`.
""",
    ),
]


FLAGSHIP_CELLS = [
    _markdown(
        "flagship-title",
        r"""
# P1–P5 flagship evidence

## Scope and authority

The five flagship identities are P1 Recursive Epistemic Reconstruction, P2 Open-World Scientific Knowledge Discovery, P3 Global Knowledge Portrait, P4 Verified Scientific Discovery, and P5 Self-ORION. This notebook displays their receipt-derived measurements without treating unlike metrics as commensurate. All five stronger external gates remain bounded by their recorded authority state.
""",
    ),
    _markdown(
        "flagship-theory",
        r"""
## Theory, methodology, and algorithms

A discovery ranking metric may be displayed with the standard definition

$$\operatorname{DCG}@k=\sum_{i=1}^{k}\frac{2^{\mathrm{rel}_i}-1}{\log_2(i+1)},\qquad
\operatorname{nDCG}@k=\frac{\operatorname{DCG}@k}{\operatorname{IDCG}@k}.$$

But a programme terminal is a **vector gate**, not a single favorable coordinate:

$$G=\bigwedge_{j=1}^{d} g_j(m_j,\tau_j).$$

Therefore a favorable nDCG coordinate does not override P2's recorded overall `FAIL`. For recursive reconstruction, a schematic update is $S_{t+1}=\mathcal{R}(S_t,e_t)$; for claim admission, evidence identity, execution identity, and authority remain separate inputs. These equations explain the reading logic; they are not new empirical results.
""",
    ),
    _code("flagship-load", BOOTSTRAP),
    _code("flagship-style", STYLE + "\n\n" + DISPLAY_HELPERS),
    _markdown(
        "flagship-controls-doc",
        r"""
## Editable selectors and display thresholds

Choose one exact metric name at a time so units and estimands are not mixed. `MIN_VALUE` is only a display filter and defaults to no filtering.
""",
    ),
    _code(
        "flagship-controls",
        r"""
PAPERS = ["P1", "P2", "P3", "P4", "P5"]
available_metric_names = sorted({str(first(row, "metric", "name", "metric_name", default="")) for row in metrics if paper_id(row) in PAPERS and numeric_value(row) is not None})
METRIC_NAME = "recall_at_100" if "recall_at_100" in available_metric_names else (available_metric_names[0] if available_metric_names else None)
MIN_VALUE = None
DISPLAY_LIMIT = 40
print("Available exact metric names:", available_metric_names)
print("Selected:", METRIC_NAME)
""",
        tags=["parameters"],
    ),
    _markdown(
        "flagship-results",
        r"""
## Results: raw values and one-metric ECDF

Every point is an atlas record, directly labelled by paper and method. Rate metrics use their full 0–1 domain so small differences are not magnified by a cropped axis. The right panel is the empirical cumulative distribution of the same selected metric; it does not smooth a small sample or mix metrics.
""",
    ),
    _code(
        "flagship-scatter-density",
        r"""
selected_metrics = [
    row for row in metrics
    if paper_id(row) in PAPERS
    and numeric_value(row) is not None
    and (METRIC_NAME is None or str(first(row, "metric", "name", "metric_name", default="")) == METRIC_NAME)
    and (MIN_VALUE is None or numeric_value(row) >= MIN_VALUE)
]
fig, (ax_values, ax_ecdf) = plt.subplots(1, 2, figsize=(13, 5.5), gridspec_kw={"width_ratios": [1.25, 1]})
if selected_metrics:
    rows = sorted(
        selected_metrics,
        key=lambda row: (paper_id(row), str(first(row, "name", "arm", "case_id", default=""))),
    )
    values = [numeric_value(row) for row in rows]
    display_names = {
        "bm25": "BM25",
        "orion_full": "ORION full",
        "orion_strong_new": "ORION strong-new",
        "rrf_hybrid": "RRF hybrid",
    }
    labels = [
        f"{paper_id(row)} — {human_label(display_names.get(str(first(row, 'name', 'arm', 'case_id', default='receipt')), first(row, 'name', 'arm', 'case_id', default='receipt')), 24)}"
        for row in rows
    ]
    unit = str(first(rows[0], "unit", default="receipt unit"))
    metric_label = human_label(METRIC_NAME, 32)
    y = list(range(len(rows)))
    ax_values.scatter(values, y, s=52, color="#1565c0", zorder=3)
    ax_values.set_yticks(y, labels)
    ax_values.invert_yaxis()
    ax_values.set_title(f"Raw receipt values: {metric_label}")
    ax_values.set_xlabel(f"{metric_label} ({unit})")
    ax_values.set_ylabel("paper and method")
    for value, ypos in zip(values, y):
        ax_values.annotate(
            f"{value:.3f}",
            (value, ypos),
            xytext=(6, 0),
            textcoords="offset points",
            va="center",
            fontsize=9,
        )
    ordered = sorted(values)
    cumulative = [(index + 1) / len(ordered) for index in range(len(ordered))]
    ax_ecdf.step(ordered, cumulative, where="post", color="#1565c0", linewidth=2)
    ax_ecdf.scatter(ordered, cumulative, color="#1565c0", s=28, zorder=3)
    ax_ecdf.set_title(f"Empirical cumulative distribution (n={len(ordered)})")
    ax_ecdf.set_xlabel(f"{metric_label} ({unit})")
    ax_ecdf.set_ylabel("cumulative fraction")
    ax_ecdf.set_ylim(0, 1.02)
    if unit.lower() in {"rate", "fraction", "proportion", "probability"}:
        for ax in (ax_values, ax_ecdf):
            ax.set_xlim(0, 1)
    fig.text(
        0.5,
        0.01,
        "Receipt-level display only; no favorable direction or external authority is inferred.",
        ha="center",
        fontsize=9,
        color="#455a64",
    )
else:
    for ax in (ax_values, ax_ecdf):
        ax.text(0.5, 0.5, "No matching numeric records", ha="center", va="center")
        ax.set_axis_off()
plt.tight_layout(rect=(0, 0.05, 1, 1))
plt.show()
""",
    ),
    _code(
        "flagship-table",
        r"""
print_records(selected_metrics, ["paper_id", "metric", "name", "value", "unit", "status", "source_id"], DISPLAY_LIMIT)

flagship_anomalies = [row for row in anomalies if paper_id(row) in PAPERS]
print(f"\nP1–P5 anomaly records (unfiltered): {len(flagship_anomalies)}")
print_records(flagship_anomalies, ["paper_id", "anomaly_id", "severity", "status", "summary"], DISPLAY_LIMIT)
""",
    ),
    _markdown(
        "flagship-discussion",
        r"""
## Discussion: load-bearing anomalies

- **P2:** the overall result remains `FAIL` even when an nDCG coordinate looks favorable. A single metric must not replace the frozen multi-endpoint terminal.
- **P5:** the requested model was `glm-5.2`, while the served model was `glm-5.3`. This is an execution-identity mismatch, not evidence for the requested-model condition.

Inspect the linked receipts to explain mechanism; the visualization intentionally does not guess missing causes.

## Claim ceiling

These plots show exact normalized receipt values at their registered scope. They do not prove that the flagship algorithms generalize, outperform alternatives, or satisfy independent/top-tier publication gates.
""",
    ),
]


FORMAL_CELLS = [
    _markdown(
        "formal-title",
        r"""
# P6–P10 formal and structured evidence

## Scope and authority

This notebook covers bounded formal certificates, structured navigation/authority/learning/problem-solving evidence, and explicit failed or not-executed gates. A complete finite certificate can validate its finite object; it does not become a universal theorem or independent external validation.
""",
    ),
    _markdown(
        "formal-theory",
        r"""
## Theory, methodology, and algorithms

For a frozen finite domain $D$ and explicit certificate $C$, the executable obligation has the form

$$\operatorname{Verify}(D,C)=\bigwedge_{x\in D}\phi(x,C).$$

Completeness of the planned run additionally requires

$$n_{\mathrm{observed}}=n_{\mathrm{planned}},$$

and replay binding can be written schematically as

$$H(I,C,O)=h_{\mathrm{registered}}.$$

Each equality has a distinct role. Certificate verification does not supply external authority; hash identity does not prove scientific truth; and a prospective protocol with no execution has no empirical result.
""",
    ),
    _code("formal-load", BOOTSTRAP),
    _code("formal-style", STYLE + "\n\n" + DISPLAY_HELPERS),
    _markdown(
        "formal-controls-doc",
        r"""
## Editable selectors and thresholds

`MIN_RECORDS` controls which evidence-presence columns are shown. It is a display threshold, not a scientific acceptance threshold.
""",
    ),
    _code(
        "formal-controls",
        r"""
PAPERS = ["P6", "P7", "P8", "P9", "P10"]
MIN_RECORDS = 1
DISPLAY_LIMIT = 50
""",
        tags=["parameters"],
    ),
    _markdown(
        "formal-results",
        r"""
## Results: evidence-presence heatmap

The heatmap is binary: it records whether the atlas contains one or more rows of each exact metric name for each paper. It neither rescales nor compares scientific values.
""",
    ),
    _code(
        "formal-heatmap",
        r"""
metric_names = sorted({str(first(row, "metric", "name", "metric_name", default="UNNAMED")) for row in metrics if paper_id(row) in PAPERS})
metric_names = [
    name for name in metric_names
    if sum(1 for row in metrics if paper_id(row) in PAPERS and str(first(row, "metric", "name", "metric_name", default="UNNAMED")) == name) >= MIN_RECORDS
]
presence = [
    [int(any(paper_id(row) == pid and str(first(row, "metric", "name", "metric_name", default="UNNAMED")) == name for row in metrics)) for name in metric_names]
    for pid in PAPERS
]

fig, ax = plt.subplots(figsize=(8.5, max(5.5, 0.45 * len(metric_names))))
if metric_names:
    ax.imshow(
        list(map(list, zip(*presence))),
        aspect="auto",
        cmap=ListedColormap(["#f5f5f5", "#00897b"]),
        vmin=0,
        vmax=1,
    )
    ax.set_xticks(range(len(PAPERS)), PAPERS)
    ax.set_yticks(range(len(metric_names)), [human_label(name, 28) for name in metric_names])
    ax.grid(False)
    ax.set_title("Metric-record presence (binary, not performance)")
else:
    ax.text(0.5, 0.5, "No metrics match the display threshold", ha="center", va="center")
    ax.set_axis_off()
plt.tight_layout()
plt.show()
""",
    ),
    _code(
        "formal-table",
        r"""
formal_states = [row for row in paper_states if paper_id(row) in PAPERS]
formal_anomalies = [row for row in anomalies if paper_id(row) in PAPERS]
print("EXACT STATES")
print_records(formal_states, ["paper_id", "title", "status", "terminal", "authority", "claim_ceiling"], DISPLAY_LIMIT)
print("\nANOMALIES")
print_records(formal_anomalies, ["paper_id", "anomaly_id", "severity", "status", "summary", "explanation"], DISPLAY_LIMIT)
""",
    ),
    _markdown(
        "formal-discussion",
        r"""
## Discussion: anomalies and honest negatives

- **P7:** 738 cases were planned but only 736 were observed. The run is invalid; the residual is $738-736=2$, not a rounding issue or a near-pass.
- **P9:** the digits D-A result remains `CANNOT_CHECK`. A separately registered revival receipt preserves the append-only replay-failure terminal, records archive-matched replay agreement, and leaves the scientific successor frozen and unexecuted. Do not erase either the historical failure or the remaining scientific boundary.
- **P10:** the prospective study was not executed. Protocol existence, code, or historical results are not a substitute for prospective observations.

P6 finite-certificate evidence remains bounded to the explicit certified structures. P8 should be read only through its exact atlas status and source receipt.

## Claim ceiling

The heatmap demonstrates evidence inventory coverage, not algorithmic superiority. Formal/local evidence remains bounded; invalid, discrepant, and not-executed studies cannot be promoted.
""",
    ),
]


GOVERNANCE_CELLS = [
    _markdown(
        "governance-title",
        r"""
# P11–P15 state, governance, and harness evidence

## Scope and authority

This notebook displays later-paper state, robustness, responsibility, RSE, and evidence-admission receipts. Internal authorship, finite corruption worlds, and cryptographic validity are kept distinct from independent scientific authority.
""",
    ),
    _markdown(
        "governance-theory",
        r"""
## Theory, methodology, and algorithms

A support count can be viewed schematically as

$$s_f(\tau)=\sum_{i=1}^{n}\mathbf{1}\{d(f(x_i),y_i)\le\tau\},$$

while forward-time evaluation requires a temporal split

$$\max(t_{\mathrm{train}})<\min(t_{\mathrm{test}}).$$

For responsibility experiments, a finite matrix indexes arm $a$ and corruption world $w$: $R_{a,w}$. For P15, the central non-implication is

$$\operatorname{Verify}(pk,m,\sigma)=1\;\not\Rightarrow\;\operatorname{True}(m).$$

A signature authenticates a statement under a key; it does not establish key custody, fact truth, scientific validity, or claim authority.
""",
    ),
    _code("governance-load", BOOTSTRAP),
    _code("governance-style", STYLE + "\n\n" + DISPLAY_HELPERS),
    _markdown(
        "governance-controls-doc",
        r"""
## Editable selectors and thresholds

Select one exact numeric metric for a raw-value bar plot. The display threshold does not alter terminals and should not be used to hide adverse rows.
""",
    ),
    _code(
        "governance-controls",
        r"""
PAPERS = ["P11", "P12", "P13", "P14", "P15"]
available_metric_names = sorted({str(first(row, "metric", "name", "metric_name", default="")) for row in metrics if paper_id(row) in PAPERS and numeric_value(row) is not None})
METRIC_NAME = "unsafe_reuse_rate" if "unsafe_reuse_rate" in available_metric_names else (available_metric_names[0] if available_metric_names else None)
MIN_VALUE = None
DISPLAY_LIMIT = 60
print("Available exact metric names:", available_metric_names)
print("Selected:", METRIC_NAME)
""",
        tags=["parameters"],
    ),
    _markdown(
        "governance-results",
        r"""
## Results: selected exact metric

Horizontal bars show individual normalized atlas rows on their natural scale. Repeated paper labels mean the receipt supplies multiple rows; the notebook does not average them. For the default unsafe-reuse view, lower is better and rate values use the full 0–1 domain.
""",
    ),
    _code(
        "governance-bars",
        r"""
selected_metrics = [
    row for row in metrics
    if paper_id(row) in PAPERS
    and numeric_value(row) is not None
    and (METRIC_NAME is None or str(first(row, "metric", "name", "metric_name", default="")) == METRIC_NAME)
    and (MIN_VALUE is None or numeric_value(row) >= MIN_VALUE)
]
fig, ax = plt.subplots(figsize=(10.5, 5.5))
if selected_metrics:
    rows = sorted(selected_metrics, key=lambda row: numeric_value(row), reverse=True)
    display_names = {
        "UNQUALIFIED": "Unqualified",
        "CONFIDENCE_ONLY": "Confidence only",
        "UNVERIFIED_RCS": "Unverified RCS",
        "ALWAYS_RAW": "Always raw",
        "AUTHENTICATED_RCS": "Authenticated RCS",
    }
    labels = [
        f"{paper_id(row)} — {human_label(display_names.get(str(first(row, 'case_id', 'arm', 'label', 'name', default=METRIC_NAME)), first(row, 'case_id', 'arm', 'label', 'name', default=METRIC_NAME)), 28)}"
        for row in rows
    ]
    values = [numeric_value(row) for row in rows]
    unit = str(first(rows[0], "unit", default="receipt unit"))
    metric_label = human_label(METRIC_NAME, 40)
    is_unsafe_reuse = METRIC_NAME == "unsafe_reuse_rate"
    direction_note = "; lower is better" if is_unsafe_reuse else ""
    y = list(range(len(values)))
    bars = ax.barh(y, values, height=0.62, color="#455a64")
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlabel(f"{metric_label} ({unit}{direction_note})")
    ax.set_ylabel("paper and receipt row")
    ax.set_title(
        "Unsafe reuse by P13 control arm (bounded internal receipts)"
        if is_unsafe_reuse
        else f"Raw receipt values: {metric_label}"
    )
    if unit.lower() in {"rate", "fraction", "proportion", "probability"}:
        ax.set_xlim(0, 1)
    for bar, value in zip(bars, values):
        ax.annotate(
            f"{value:.1%}" if unit.lower() == "rate" else f"{value:g}",
            (value, bar.get_y() + bar.get_height() / 2),
            xytext=(6, 0),
            textcoords="offset points",
            va="center",
            fontsize=9,
        )
    fig.text(
        0.5,
        0.01,
        (
            "A zero bar is a bounded receipt value, not evidence of external safety authority."
            if is_unsafe_reuse
            else "Receipt-level display only; favorable direction and external authority are not inferred."
        ),
        ha="center",
        fontsize=9,
        color="#455a64",
    )
else:
    ax.text(0.5, 0.5, "No matching numeric records", ha="center", va="center")
    ax.set_axis_off()
plt.tight_layout(rect=(0, 0.05, 1, 1))
plt.show()
""",
    ),
    _code(
        "governance-table",
        r"""
governance_states = [row for row in paper_states if paper_id(row) in PAPERS]
governance_anomalies = [row for row in anomalies if paper_id(row) in PAPERS]
print("EXACT STATES")
print_records(governance_states, ["paper_id", "title", "status", "terminal", "authority", "claim_ceiling"], DISPLAY_LIMIT)
print("\nSELECTED METRIC ROWS")
print_records(selected_metrics, ["paper_id", "metric", "name", "value", "unit", "case_id", "arm", "status"], DISPLAY_LIMIT)
print("\nANOMALIES")
print_records(governance_anomalies, ["paper_id", "anomaly_id", "severity", "status", "summary"], DISPLAY_LIMIT)
""",
    ),
    _markdown(
        "governance-discussion",
        r"""
## Discussion: gate and authority boundaries

- **P11:** 30 query results and support counts `LINEAR=3`, `RBF=5`, `KNN=5` coexist with terminal `GATE_NOT_MET`; counts do not override the gate.
- **P12:** 32 receipt families span $\sigma\in\{0.2,0.4,0.6,0.8\}$; the registered active-authority receipt says `forward_time_deployability=CANNOT_CHECK` and `campaign_executed=false` for the public-data stop/go campaign.
- **P13:** the five-arm/four-corruption-world result is bounded finite. A separately registered P13A receipt retains historical terminal `P14_CONTROLLED_SUFFICIENCY_DEBT_GATE_NOT_MET` with observed maximum deviation $0.0556640625>0.05$; the exact historical label is preserved rather than silently renamed.
- **P14:** the 28 internally authored cases are not an external pilot. The separate 67-packet pilot analytics receipt is `NOT_AUTHORITY` because frontier-agent execution and independent human adjudication have not run.
- **P15:** four real-workflow receipts include three `AUTHORIZED_SCIENCE` receipt dispositions and one honest `CANNOT_CHECK`; these are not publication/external-authority labels. Separately, the active-authority receipt records 0 signature-layer detections and 6 false promotions under full key compromise, exposing the boundary: valid signatures do not prove custody or truth.

## Claim ceiling

The displayed receipts support only their registered finite/local statements. They do not establish forward-time transfer, external-pilot independence, production-scale reliability, secure key custody, or scientific truth from provenance/signatures.
""",
    ),
]


ANOMALY_CELLS = [
    _markdown(
        "anomaly-title",
        r"""
# ORION anomaly audit

## Scope and authority

This notebook makes adverse, null, missing, discrepant, and boundary outcomes first-class. It is an audit view over committed atlas records, not an automated explanation engine. Explanations below must remain traceable to source receipts; unresolved causes stay unresolved.
""",
    ),
    _markdown(
        "anomaly-theory",
        r"""
## Theory, methodology, and algorithms

For planned-versus-observed coverage, the exact residual is

$$r_n=n_{\mathrm{planned}}-n_{\mathrm{observed}}.$$

For categorical scientific terminals, do not average labels. Preserve the evidence vector

$$E=(e_{\mathrm{execution}},e_{\mathrm{science}},e_{\mathrm{independence}},e_{\mathrm{authority}}),$$

and apply non-escalation componentwise. A favorable scalar coordinate cannot erase a failing component; a missing prospective component stays `CANNOT_CHECK` or not executed.
""",
    ),
    _code("anomaly-load", BOOTSTRAP),
    _code("anomaly-style", STYLE + "\n\n" + DISPLAY_HELPERS),
    _markdown(
        "anomaly-controls-doc",
        r"""
## Editable selectors and exact-label filter

Anomaly labels are categorical and are not assigned an unsupported ordinal severity rank. Paper and exact-status filters change only the visible subset. The unfiltered anomaly count is always printed.
""",
    ),
    _code(
        "anomaly-controls",
        r"""
PAPERS = [f"P{i}" for i in range(1, 16)]
STATUS_CONTAINS = None
DISPLAY_LIMIT = 100
""",
        tags=["parameters"],
    ),
    _markdown(
        "anomaly-results",
        r"""
## Results: anomaly distribution and paper map

The left plot counts exact stored anomaly labels. The right plot maps each retained record to its paper and exact label; P1 has no retained anomaly record. Counts reflect the atlas inventory, not event rates or comparative paper quality.
""",
    ),
    _code(
        "anomaly-plots",
        r"""
selected_anomalies = [
    row for row in anomalies
    if paper_id(row) in PAPERS
    and (STATUS_CONTAINS is None or STATUS_CONTAINS.upper() in exact_status(row).upper())
]


severity_labels = sorted({str(first(row, "severity", default="UNSPECIFIED")) for row in selected_anomalies})
severity_counts = [sum(str(first(row, "severity", default="UNSPECIFIED")) == label for row in selected_anomalies) for label in severity_labels]
fig, (ax_severity, ax_inventory) = plt.subplots(1, 2, figsize=(13, 5.5), gridspec_kw={"width_ratios": [0.9, 1.2]})
if selected_anomalies:
    y = list(range(len(severity_labels)))
    bars = ax_severity.barh(y, severity_counts, color="#6a1b9a", height=0.68)
    ax_severity.set_yticks(y, [human_label(label, 18) for label in severity_labels])
    ax_severity.invert_yaxis()
    ax_severity.set_title("Retained records by exact anomaly label")
    ax_severity.set_xlabel("anomaly records (count)")
    ax_severity.set_ylabel("exact label")
    ax_severity.set_xlim(0, max(severity_counts) + 0.6)
    ax_severity.set_xticks(range(0, max(severity_counts) + 1))
    for bar, count in zip(bars, severity_counts):
        ax_severity.text(count + 0.08, bar.get_y() + bar.get_height() / 2, str(count), va="center")

    severity_order = severity_labels
    severity_index = {label: index for index, label in enumerate(severity_order)}
    paper_index = {pid: index for index, pid in enumerate(PAPERS)}
    palette = {
        "FAIL": "#c62828",
        "ADVERSE": "#ad1457",
        "CANNOT_CHECK": "#ef6c00",
        "BOUNDARY": "#1565c0",
        "NULL": "#6a1b9a",
        "NOT_AUTHORITY": "#455a64",
        "MIXED": "#5d4037",
    }
    for row in selected_anomalies:
        pid = paper_id(row)
        severity = str(first(row, "severity", default="UNSPECIFIED"))
        ax_inventory.scatter(
            paper_index[pid],
            severity_index[severity],
            s=88,
            marker="o",
            color=palette.get(severity.upper(), "#757575"),
            edgecolor="white",
            linewidth=0.8,
            zorder=3,
        )
    ax_inventory.set_xticks(range(len(PAPERS)), PAPERS)
    ax_inventory.set_yticks(range(len(severity_order)), [human_label(label, 18) for label in severity_order])
    ax_inventory.set_xlim(-0.6, len(PAPERS) - 0.4)
    ax_inventory.set_ylim(-0.6, len(severity_order) - 0.4)
    ax_inventory.invert_yaxis()
    ax_inventory.set_title("Which anomaly label is retained for each paper")
    ax_inventory.set_xlabel("paper (P1 has no retained anomaly record)")
    ax_inventory.set_ylabel("exact anomaly label")
    ax_inventory.grid(axis="x", alpha=0.18)
else:
    for ax in (ax_severity, ax_inventory):
        ax.text(0.5, 0.5, "No anomalies match the display selectors", ha="center", va="center")
        ax.set_axis_off()
plt.tight_layout()
plt.show()
""",
    ),
    _code(
        "anomaly-table",
        r"""
print_records(
    selected_anomalies,
    ["paper_id", "anomaly_id", "severity", "status", "summary", "observed", "expected", "explanation", "source_ids"],
    DISPLAY_LIMIT,
)
""",
    ),
    _markdown(
        "anomaly-discussion",
        r"""
## Discussion: mandatory retained findings

1. **P2:** overall `FAIL` despite nDCG; a favorable coordinate cannot replace the registered terminal.
2. **P5:** requested `glm-5.2`, served `glm-5.3`; requested-condition identity was not met.
3. **P7:** 738 planned, 736 observed; the run is invalid and the coverage residual is 2.
4. **P9:** digits D-A is `CANNOT_CHECK`; the replay-revival receipt keeps the old failure terminal, records archive-matched agreement, and leaves the scientific successor unexecuted.
5. **P10:** prospective experiment not executed; no empirical promotion is available.
6. **P11:** terminal `GATE_NOT_MET`, despite available query/support-count rows.
7. **P12:** `forward_time_deployability=CANNOT_CHECK`; the registered public-data stop/go campaign is not executed.
8. **P13:** bounded finite result plus the separately registered historical adverse terminal; neither may erase the other.
9. **P14:** the 67-packet pilot analytics are `NOT_AUTHORITY`; internally authored cases are not external validation.
10. **P15:** full key compromise produced 0 signature detections and 6 false promotions; verification cannot establish custody, fact truth, or scientific authority.

Use `visualization/reports/ANOMALY_AUDIT.md` for the explanation and next-discriminator table.

## Claim ceiling

An anomaly plot can expose contradictions, missingness, and boundary cases. It cannot repair them. Until the relevant frozen discriminator is executed and bound, adverse statuses remain adverse and unresolved statuses remain `CANNOT_CHECK`.
""",
    ),
]

DES_EXECUTION_CELLS = [
    _markdown(
        "des-title",
        r"""
# Frozen #1332 DES execution and framework mechanics

## Scope and authority

This notebook keeps the frozen `P1-DES-01` through `P15-DES-01` execution packets separate from the other bounded studies in the atlas. It distinguishes **planned**, **observed/executed**, and **valid at the packet's registered internal scope**. None of these is external scientific authority. Every DES packet retains `external_authority_state=CANNOT_CHECK` and paper-authority delta `NONE`.

Missing or unscored outcomes remain missing, `CANNOT_CHECK`, or invalid. They are never filled with estimated performance values.
""",
    ),
    _markdown(
        "des-theory",
        r"""
## Theory, methodology, and algorithms

For each paper's own registered denominator, define execution coverage—not performance—as

$$c_{\mathrm{obs}}=\frac{n_{\mathrm{observed}}}{n_{\mathrm{planned}}},\qquad
c_{\mathrm{valid}}=\frac{n_{\mathrm{valid}}}{n_{\mathrm{planned}}},\qquad
0\le c_{\mathrm{valid}}\le c_{\mathrm{obs}}\le 1.$$

The distinction is load-bearing: P4 has mechanically executed arm-cases without external terminal-gold scores, while P7 generated almost all planned rows but has zero valid rows because its frozen denominator drifted.

For legacy projection $\pi$ and next-action rule $a$, a finite collision witness has

$$\pi(s_1)=\pi(s_2),\qquad a(s_1)\ne a(s_2).$$

Such a witness shows that the legacy terminal cannot reconstruct the decision-relevant state on the enumerated class. The update receipt separately checks finite algebraic laws such as idempotence,

$$\mathcal{T}(\mathcal{T}(S,e),e)=\mathcal{T}(S,e),$$

plus replay, commutation/noncommutation, revocation locality, authority non-amplification, and six registered mutants. These are finite internal checks, not universal theorems or external validation.
""",
    ),
    _code("des-load", BOOTSTRAP),
    _code("des-style", STYLE + "\n\n" + DISPLAY_HELPERS),
    _markdown(
        "des-controls-doc",
        r"""
## Editable selectors

Choose which paper rows to display. The selector only changes presentation; it does not change denominators, terminals, anomaly records, or authority.
""",
    ),
    _code(
        "des-controls",
        r"""
PAPERS = [f"P{i}" for i in range(1, 16)]
DISPLAY_LIMIT = 30
""",
        tags=["parameters"],
    ),
    _markdown(
        "des-results-doc",
        r"""
## Results: planned, observed, and valid coverage

Bars are normalized **within each paper's own unit**. Absolute denominators are printed at right and must not be pooled across papers. A short black mark at zero makes an exact zero valid count visible.
""",
    ),
    _code(
        "des-coverage",
        r"""
selected_des = [row for row in des_execution if paper_id(row) in PAPERS]
selected_des.sort(key=lambda row: int(paper_id(row)[1:]))
y = list(range(len(selected_des)))[::-1]
observed_pct = [100 * row["observed"] / row["planned"] for row in selected_des]
valid_pct = [100 * row["valid"] / row["planned"] for row in selected_des]
fig, ax = plt.subplots(figsize=(12, max(5.5, 0.43 * len(selected_des) + 1.8)))
ax.barh(y, [100] * len(selected_des), height=0.60, color="#e0e0e0", label="Planned")
ax.barh(y, observed_pct, height=0.42, color="#42a5f5", label="Observed / executed")
ax.barh(y, valid_pct, height=0.20, color="#00897b", label="Valid at registered internal scope")
for y_value, row, valid in zip(y, selected_des, valid_pct):
    if valid == 0:
        ax.scatter(0, y_value, marker="|", s=90, color="#212121", linewidth=1.6, zorder=4)
    ax.text(102, y_value, f"{row['valid']}/{row['observed']}/{row['planned']} {row['unit']}", va="center", fontsize=8)
ax.set_xlim(0, 145)
ax.set_xticks(range(0, 101, 20), [f"{value}%" for value in range(0, 101, 20)])
ax.set_yticks(y, [paper_id(row) for row in selected_des])
ax.set_xlabel("Within-paper denominator coverage (not performance)")
ax.set_ylabel("Frozen DES job")
ax.set_title("Frozen DES execution coverage — gray planned · blue observed · green valid")
ax.grid(axis="x", alpha=0.20)
plt.tight_layout()
plt.show()
""",
    ),
    _code(
        "des-table",
        r"""
print_records(
    selected_des,
    ["paper_id", "job_id", "planned", "observed", "valid", "unit", "status", "terminal", "external_authority_state", "paper_authority_delta", "source_id"],
    DISPLAY_LIMIT,
)
""",
    ),
    _markdown(
        "des-mechanics-doc",
        r"""
## Results: finite mechanics receipts

The following views use distinct estimands: terminal/action collision counts, mutation detection fractions, projection replay counts, and source-census classification shares. They are deliberately not collapsed into one framework score.
""",
    ),
    _code(
        "des-mechanics",
        r"""
collision = framework_mechanics["collision"]
update = framework_mechanics["update_algebra"]
projection = framework_mechanics["projection"]
census = framework_mechanics["census"]

fig, axes = plt.subplots(2, 2, figsize=(13, 9))

terminals = ["ADMISSIBLE", "BLOCKED", "CANNOT_CHECK"]
actions = ["ACQUIRE_EVIDENCE", "DISCRIMINATE", "OBTAIN_EXTERNAL_CUSTODY", "REVALIDATE", "STOP"]
matrix = [[collision["terminal_action_counts"].get(t, {}).get(a, 0) for a in actions] for t in terminals]
image = axes[0, 0].imshow([[__import__("math").log1p(value) for value in row] for row in matrix], cmap="Blues", aspect="auto")
for r, row in enumerate(matrix):
    for c, value in enumerate(row):
        axes[0, 0].text(c, r, str(value), ha="center", va="center", fontsize=8)
axes[0, 0].set_xticks(range(len(actions)), [human_label(a, 12) for a in actions], rotation=25)
axes[0, 0].set_yticks(range(len(terminals)), [human_label(t, 16) for t in terminals])
axes[0, 0].set_title(f"Terminal → action states\n{collision['different_action_pairs']:,}/{collision['same_terminal_pairs']:,} same-terminal pairs diverge")

mutations = update["mutations"]
mutation_y = list(range(len(mutations)))[::-1]
rates = [100 * row["detections"] / row["cases"] for row in mutations]
axes[0, 1].hlines(mutation_y, 0, rates, color="#bbdefb", linewidth=2)
axes[0, 1].scatter(rates, mutation_y, color="#1565c0", s=55)
for y_value, rate, row in zip(mutation_y, rates, mutations):
    axes[0, 1].text(min(rate + 2, 103), y_value, f"{row['detections']:,}/{row['cases']:,}", va="center", fontsize=8)
axes[0, 1].set_xlim(0, 118)
axes[0, 1].set_yticks(mutation_y, [human_label(row["mutation"], 24) for row in mutations])
axes[0, 1].set_xlabel("Detection rate (%)")
axes[0, 1].set_title(f"{update['mutations_killed']}/{update['mutation_count']} mutants killed; law failures={update['law_failures']}")

surface_names = ["PROMOTION_V1", "READINESS_V1"]
projection_terminals = ["ADMISSIBLE", "BLOCKED", "CANNOT_CHECK", "PROVISIONAL"]
surface_matrix = [[projection["surface_results"][surface]["terminal_counts"].get(t, 0) for t in projection_terminals] for surface in surface_names]
axes[1, 0].imshow([[__import__("math").log1p(value) for value in row] for row in surface_matrix], cmap="PuBuGn", aspect="auto")
for r, row in enumerate(surface_matrix):
    for c, value in enumerate(row):
        axes[1, 0].text(c, r, str(value), ha="center", va="center", fontsize=8)
axes[1, 0].set_xticks(range(len(projection_terminals)), [human_label(t, 16) for t in projection_terminals], rotation=25)
axes[1, 0].set_yticks(range(len(surface_names)), [surface.replace("_V1", "").title() for surface in surface_names])
axes[1, 0].set_title(f"Projection replay {projection['matched_rows']:,}/{projection['row_denominator']:,}\n{projection['noninjective_groups']}/7 groups noninjective; {projection['action_divergent_groups']} action-divergent")

held = census["folds"][str(census["held_out_fold"])]
counts = [
    [census["classified_occurrences"], census["unclassified_occurrences"]],
    [held["classified"], held["unclassified"]],
]
totals = [sum(row) for row in counts]
classified = [100 * row[0] / total for row, total in zip(counts, totals)]
unclassified = [100 - value for value in classified]
census_y = [1, 0]
axes[1, 1].barh(census_y, classified, color="#1565c0", label="Classified")
axes[1, 1].barh(census_y, unclassified, left=classified, color="#ef6c00", label="Unclassified retained")
for y_value, left, row in zip(census_y, classified, counts):
    axes[1, 1].text(left / 2, y_value, f"{row[0]:,}", ha="center", va="center", color="white", fontsize=8)
    axes[1, 1].text(left + (100 - left) / 2, y_value, f"{row[1]:,}", ha="center", va="center", color="white", fontsize=8)
axes[1, 1].set_xlim(0, 100)
axes[1, 1].set_yticks(census_y, ["All occurrences", f"Held-out fold {census['held_out_fold']}"])
axes[1, 1].set_xlabel("Occurrence share (%)")
axes[1, 1].set_title(f"Source census n={census['occurrences']:,}\n{census['terminal']}; text-cap-censored files={census['likely_text_cap_censored_count']}")
axes[1, 1].legend(frameon=False, loc="lower center", bbox_to_anchor=(0.5, -0.28), ncol=2)

fig.suptitle("Finite internal framework-mechanics receipts — no external authority delta")
plt.tight_layout()
plt.show()
""",
    ),
    _markdown(
        "des-discussion",
        r"""
## Discussion and anomaly inspection

- **P2, P6, and P8** reach 100% valid coverage only for their registered bounded internal/public-reference units; external authority still remains `CANNOT_CHECK`.
- **P4** has 900/1,500 mechanically executed arm-cases but 0 external terminal-gold scores. Mechanical execution is not scientific scoring.
- **P7** has 736/738 observed rows but 0 valid rows. Near-complete generation cannot rescue a frozen-denominator violation.
- **P11 and P14** inspected all eight acquisition requirements/artifacts, but bound/present valid inputs remain 0. Preflight activity is not outcome execution.
- **P13** has 288/720 valid internal planner cells and 432 `CANNOT_CHECK` cells; the full intended control is therefore not attained.
- The collision atlas shows 4,355 different-action pairs among 9,201 same-terminal pairs on 144 finite states. This demonstrates finite nonreconstruction on the declared class, not empirical superiority.
- The update receipt records zero failures across 249,216 registered law cases and kills all six mutants. That is strong finite conformance evidence, not a universal proof.
- The projection receipt matches 5,760/5,760 rows while all seven reachable groups remain noninjective and six are action-divergent. Exact replay and information loss can coexist.
- The census retains 121,985 unclassified occurrences and terminal `RESOURCE_CAP_CENSORED`; classification success must not erase the residual.

## Claim ceiling

The notebook may show why the registered computations are internally coherent and where they fail. It may not claim external independence, population validity, universal necessity, superiority, novelty, or journal readiness. The remedy for a missing authority component is a new identity-bound experiment or external review—not a different plot.
""",
    ),
]

NOTEBOOKS = {
    "00_framework_overview.ipynb": OVERVIEW_CELLS,
    "01_p1_p5_flagships.ipynb": FLAGSHIP_CELLS,
    "02_p6_p10_formal_structured.ipynb": FORMAL_CELLS,
    "03_p11_p15_state_governance_harness.ipynb": GOVERNANCE_CELLS,
    "04_anomaly_audit.ipynb": ANOMALY_CELLS,
    "05_frozen_des_execution.ipynb": DES_EXECUTION_CELLS,
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=NOTEBOOK_DIR)
    args = parser.parse_args()
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, cells in NOTEBOOKS.items():
        output = output_dir / name
        payload = json.dumps(_notebook(cells), ensure_ascii=False, indent=1) + "\n"
        output.write_text(payload, encoding="utf-8")
        try:
            print(output.relative_to(VISUALIZATION_ROOT))
        except ValueError:
            print(output)


if __name__ == "__main__":
    main()
