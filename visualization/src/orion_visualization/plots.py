"""Receipt-first plots for the ORION evidence atlas.

All functions validate numeric inputs before creating a figure.  They accept
already-extracted observations and never manufacture missing values.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np
from matplotlib import colors as mpl_colors
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from numpy.typing import ArrayLike

from .authority import EvidenceStatus, classify_statuses
from .styles import (
    STATUS_COLORS,
    STATUS_MARKERS,
    apply_atlas_style,
    new_figure,
)
from .transforms import as_finite_1d, as_finite_2d, ecdf, pareto_frontier


def _labels(values: Sequence[Any], *, expected: int, name: str) -> list[str]:
    labels = [str(value) for value in values]
    if len(labels) != expected:
        raise ValueError(f"{name} must have length {expected}")
    return labels


def _optional_statuses(values: Sequence[Any] | None, *, expected: int):
    if values is None:
        return (EvidenceStatus.UNKNOWN,) * expected
    states = classify_statuses(values)
    if len(states) != expected:
        raise ValueError(f"statuses must have length {expected}")
    return states


def _status_legend(ax, statuses: Sequence[EvidenceStatus]) -> None:
    seen = list(dict.fromkeys(statuses))
    handles = [
        Line2D(
            [],
            [],
            linestyle="none",
            marker=STATUS_MARKERS[status],
            markersize=7,
            markerfacecolor=STATUS_COLORS[status],
            markeredgecolor="white",
            label=status.value,
        )
        for status in seen
    ]
    if handles:
        ax.legend(handles=handles, title="Evidence state", frameon=False)


def plot_forest(
    estimates: ArrayLike,
    lower: ArrayLike,
    upper: ArrayLike,
    labels: Sequence[Any],
    *,
    statuses: Sequence[Any] | None = None,
    reference: float | None = 0.0,
    title: str = "Effect estimates and intervals",
    xlabel: str = "Estimate",
    show_status_legend: bool = True,
):
    """Plot estimates with intervals; no interval is inferred from point data."""

    apply_atlas_style()
    estimate = as_finite_1d(estimates, name="estimates")
    low = as_finite_1d(lower, name="lower")
    high = as_finite_1d(upper, name="upper")
    if not (estimate.size == low.size == high.size):
        raise ValueError("estimates, lower and upper must have the same length")
    if np.any(low > estimate) or np.any(estimate > high):
        raise ValueError("intervals must satisfy lower <= estimate <= upper")
    item_labels = _labels(labels, expected=estimate.size, name="labels")
    states = _optional_statuses(statuses, expected=estimate.size)
    if reference is not None:
        reference = as_finite_1d([reference], name="reference")[0]

    height = max(3.2, 0.48 * estimate.size + 1.5)
    fig, ax = new_figure(figsize=(7.5, height))
    y = np.arange(estimate.size)[::-1]
    for index, y_value in enumerate(y):
        color = STATUS_COLORS[states[index]]
        ax.hlines(y_value, low[index], high[index], color=color, linewidth=2.0, zorder=2)
        ax.scatter(
            estimate[index],
            y_value,
            marker=STATUS_MARKERS[states[index]],
            s=58,
            color=color,
            edgecolor="white",
            linewidth=0.7,
            zorder=3,
        )
    if reference is not None:
        ax.axvline(reference, color="#333333", linewidth=1.0, linestyle="--", alpha=0.75)
    ax.set(yticks=y, yticklabels=item_labels, xlabel=xlabel, title=title)
    ax.grid(axis="x", color="#E5E7EB", linewidth=0.8)
    if show_status_legend:
        _status_legend(ax, states)
    return fig, ax


def plot_pareto_scatter(
    x: ArrayLike,
    y: ArrayLike,
    *,
    labels: Sequence[Any] | None = None,
    statuses: Sequence[Any] | None = None,
    maximize: tuple[bool, bool] = (True, True),
    annotate: bool = True,
    title: str = "Trade-off and Pareto frontier",
    xlabel: str = "Objective 1",
    ylabel: str = "Objective 2",
    connect_frontier: bool = True,
):
    """Scatter two observed objectives and return the non-dominated mask."""

    apply_atlas_style()
    x_values = as_finite_1d(x, name="x")
    y_values = as_finite_1d(y, name="y")
    if x_values.size != y_values.size:
        raise ValueError("x and y must have the same length")
    points = np.column_stack((x_values, y_values))
    frontier = pareto_frontier(points, maximize=maximize)
    states = _optional_statuses(statuses, expected=x_values.size)
    item_labels = None if labels is None else _labels(labels, expected=x_values.size, name="labels")

    fig, ax = new_figure()
    for index, (x_value, y_value) in enumerate(points):
        state = states[index]
        ax.scatter(
            x_value,
            y_value,
            marker=STATUS_MARKERS[state],
            color=STATUS_COLORS[state],
            s=68 if frontier[index] else 48,
            edgecolor="#111827" if frontier[index] else "white",
            linewidth=1.0 if frontier[index] else 0.7,
            zorder=3,
        )
        if annotate and item_labels is not None:
            ax.annotate(
                item_labels[index], (x_value, y_value), xytext=(4, 4), textcoords="offset points"
            )

    frontier_points = points[frontier]
    if connect_frontier and frontier_points.shape[0] > 1:
        order = np.argsort(frontier_points[:, 0], kind="stable")
        ax.plot(
            frontier_points[order, 0],
            frontier_points[order, 1],
            color="#111827",
            linewidth=1.1,
            linestyle="--",
            label="Non-dominated envelope",
            zorder=2,
        )
    ax.set(title=title, xlabel=xlabel, ylabel=ylabel)
    ax.grid(color="#E5E7EB", linewidth=0.8)
    _status_legend(ax, states)
    return fig, ax, frontier


def plot_heatmap(
    matrix: ArrayLike,
    row_labels: Sequence[Any],
    column_labels: Sequence[Any],
    *,
    annotate: bool = False,
    value_format: str = ".2g",
    cmap: str = "viridis",
    title: str = "Observed values",
    colorbar_label: str = "Value",
    vmin: float | None = None,
    vmax: float | None = None,
):
    """Plot a strictly finite numeric matrix."""

    apply_atlas_style()
    values = as_finite_2d(matrix, name="matrix")
    rows = _labels(row_labels, expected=values.shape[0], name="row_labels")
    columns = _labels(column_labels, expected=values.shape[1], name="column_labels")
    width = max(5.5, 0.72 * values.shape[1] + 2.0)
    height = max(3.8, 0.50 * values.shape[0] + 1.8)
    fig, ax = new_figure(figsize=(width, height))
    if vmin is not None:
        vmin = float(vmin)
    if vmax is not None:
        vmax = float(vmax)
    if vmin is not None and vmax is not None and vmin >= vmax:
        raise ValueError("vmin must be smaller than vmax")
    image = ax.imshow(values, aspect="auto", cmap=cmap, vmin=vmin, vmax=vmax)
    ax.set(
        xticks=np.arange(values.shape[1]),
        xticklabels=columns,
        yticks=np.arange(values.shape[0]),
        yticklabels=rows,
        title=title,
    )
    ax.tick_params(axis="x", rotation=35)
    colorbar = fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    colorbar.set_label(colorbar_label)
    if annotate:
        colormap = image.get_cmap()
        normalizer = image.norm
        for row_index in range(values.shape[0]):
            for column_index in range(values.shape[1]):
                value = values[row_index, column_index]
                red, green, blue, _ = colormap(normalizer(value))
                luminance = 0.2126 * red + 0.7152 * green + 0.0722 * blue
                ax.text(
                    column_index,
                    row_index,
                    format(value, value_format),
                    ha="center",
                    va="center",
                    color="#111827" if luminance > 0.52 else "white",
                    fontsize=9,
                )
    return fig, ax


def plot_ecdf(
    values: ArrayLike,
    *,
    title: str = "Empirical cumulative distribution",
    xlabel: str = "Observed value",
    ylabel: str = "Cumulative fraction",
):
    """Plot an empirical CDF without a parametric distribution assumption."""

    apply_atlas_style()
    x, probability = ecdf(values)
    fig, ax = new_figure()
    ax.step(x, probability, where="post", color="#0072B2", linewidth=2.0)
    ax.scatter(x, probability, color="#0072B2", s=20, zorder=3)
    ax.set(title=title, xlabel=xlabel, ylabel=ylabel, ylim=(0.0, 1.02))
    ax.grid(color="#E5E7EB", linewidth=0.8)
    return fig, ax


def _kde(values: np.ndarray) -> tuple[np.ndarray, np.ndarray] | None:
    if values.size < 3 or np.unique(values).size < 2:
        return None
    standard_deviation = float(np.std(values, ddof=1))
    q25, q75 = np.percentile(values, [25, 75])
    robust_scale = min(standard_deviation, float((q75 - q25) / 1.34))
    if robust_scale <= 0.0:
        robust_scale = standard_deviation
    bandwidth = 0.9 * robust_scale * values.size ** (-0.2)
    if not np.isfinite(bandwidth) or bandwidth <= 0.0:
        return None
    grid = np.linspace(
        float(np.min(values) - 3 * bandwidth), float(np.max(values) + 3 * bandwidth), 256
    )
    scaled = (grid[:, None] - values[None, :]) / bandwidth
    density = np.exp(-0.5 * scaled * scaled).sum(axis=1)
    density /= values.size * bandwidth * np.sqrt(2.0 * np.pi)
    return grid, density


def plot_distribution(
    values: ArrayLike,
    *,
    kind: str = "auto",
    bins: str | int | Sequence[float] = "auto",
    title: str = "Observed distribution",
    xlabel: str = "Observed value",
    ylabel: str = "Density",
):
    """Plot deterministic Gaussian KDE when supported, otherwise a histogram.

    The returned ``actual_kind`` makes a constant/small-sample fallback explicit.
    """

    apply_atlas_style()
    observations = as_finite_1d(values)
    requested = kind.strip().lower()
    if requested not in {"auto", "density", "histogram"}:
        raise ValueError("kind must be 'auto', 'density', or 'histogram'")
    density = None if requested == "histogram" else _kde(observations)
    actual_kind = "density" if density is not None else "histogram"

    fig, ax = new_figure()
    if density is not None:
        grid, estimate = density
        ax.plot(grid, estimate, color="#0072B2", linewidth=2.0)
        ax.fill_between(grid, 0.0, estimate, color="#56B4E9", alpha=0.35)
        ax.set_ylabel(ylabel)
    else:
        ax.hist(
            observations,
            bins=bins,
            density=False,
            color="#56B4E9",
            edgecolor="white",
            linewidth=0.8,
        )
        ax.set_ylabel("Count")
    ax.set(title=title, xlabel=xlabel)
    ax.grid(axis="y", color="#E5E7EB", linewidth=0.8)
    return fig, ax, actual_kind


def plot_trajectories(
    x: ArrayLike,
    series: Mapping[Any, ArrayLike],
    *,
    title: str = "Observed trajectories",
    xlabel: str = "Step",
    ylabel: str = "Observed value",
):
    """Plot named sequences against a shared, finite x coordinate."""

    apply_atlas_style()
    x_values = as_finite_1d(x, name="x")
    if not series:
        raise ValueError("series must contain at least one trajectory")
    checked: list[tuple[str, np.ndarray]] = []
    for label, values in series.items():
        observations = as_finite_1d(values, name=f"series[{label!r}]")
        if observations.size != x_values.size:
            raise ValueError("all trajectories and x must have the same length")
        checked.append((str(label), observations))

    fig, ax = new_figure()
    palette = plt.get_cmap("tab10")
    for index, (label, observations) in enumerate(checked):
        ax.plot(
            x_values,
            observations,
            marker="o",
            markersize=3.5,
            linewidth=1.6,
            color=palette(index % 10),
            label=label,
        )
    ax.set(title=title, xlabel=xlabel, ylabel=ylabel)
    ax.grid(color="#E5E7EB", linewidth=0.8)
    ax.legend(frameon=False)
    return fig, ax


def plot_status_matrix(
    statuses: Sequence[Sequence[Any]],
    row_labels: Sequence[Any],
    column_labels: Sequence[Any],
    *,
    title: str = "Paper by evidence gate",
):
    """Plot a categorical paper x gate matrix without ordinal color semantics."""

    apply_atlas_style()
    rows = [list(row) for row in statuses]
    if not rows or not rows[0] or any(len(row) != len(rows[0]) for row in rows):
        raise ValueError("statuses must be a non-empty rectangular matrix")
    if len(row_labels) != len(rows) or len(column_labels) != len(rows[0]):
        raise ValueError("row_labels and column_labels shape must match statuses shape")
    row_names = _labels(row_labels, expected=len(rows), name="row_labels")
    column_names = _labels(column_labels, expected=len(rows[0]), name="column_labels")
    order = list(EvidenceStatus)
    index_by_status = {status: index for index, status in enumerate(order)}
    encoded = np.empty((len(rows), len(rows[0])), dtype=int)
    classified: list[list[EvidenceStatus]] = []
    for row_index, row in enumerate(rows):
        states = list(classify_statuses(row))
        classified.append(states)
        encoded[row_index] = [index_by_status[state] for state in states]

    cmap = mpl_colors.ListedColormap([STATUS_COLORS[status] for status in order])
    norm = mpl_colors.BoundaryNorm(np.arange(-0.5, len(order) + 0.5), cmap.N)
    width = max(6.0, 0.85 * len(column_names) + 2.3)
    height = max(3.5, 0.50 * len(row_names) + 1.8)
    fig, ax = new_figure(figsize=(width, height))
    ax.imshow(encoded, aspect="auto", cmap=cmap, norm=norm)
    ax.set(
        xticks=np.arange(len(column_names)),
        xticklabels=column_names,
        yticks=np.arange(len(row_names)),
        yticklabels=row_names,
        title=title,
    )
    ax.tick_params(axis="x", rotation=35)
    present = [state for state in order if any(state in row for row in classified)]
    display = {
        EvidenceStatus.PASS: "PASS",
        EvidenceStatus.FAIL: "FAIL",
        EvidenceStatus.UNKNOWN: "UNKNOWN",
        EvidenceStatus.CANNOT_CHECK: "CANNOT CHECK",
        EvidenceStatus.NULL: "NULL",
        EvidenceStatus.ADVERSE: "ADVERSE",
        EvidenceStatus.MIXED: "MIXED",
    }
    for row_index, states in enumerate(classified):
        for column_index, state in enumerate(states):
            text_color = (
                "#111827" if state in {EvidenceStatus.NULL, EvidenceStatus.MIXED} else "white"
            )
            label = display[state].replace(" ", "\n")
            ax.text(
                column_index,
                row_index,
                label,
                ha="center",
                va="center",
                color=text_color,
                fontsize=7,
                fontweight="bold",
            )
    handles = [Patch(facecolor=STATUS_COLORS[state], label=display[state]) for state in present]
    ax.legend(
        handles=handles,
        title="Evidence state",
        frameon=False,
        bbox_to_anchor=(1.02, 1.0),
        loc="upper left",
    )
    return fig, ax
