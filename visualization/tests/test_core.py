from __future__ import annotations

import json
from pathlib import Path

import matplotlib
import numpy as np
import pytest

from orion_visualization.authority import EvidenceStatus, classify_status
from orion_visualization.diagrams import plot_dependency_diagram
from orion_visualization.io import sha256_file, source_record, verify_source_record
from orion_visualization.plots import (
    plot_distribution,
    plot_ecdf,
    plot_forest,
    plot_heatmap,
    plot_pareto_scatter,
    plot_status_matrix,
    plot_trajectories,
)
from orion_visualization.styles import STATUS_COLORS, save_figure
from orion_visualization.transforms import (
    as_finite_1d,
    ecdf,
    jaccard_similarity,
    pareto_frontier,
    wilson_interval,
)


def test_agg_backend_is_selected() -> None:
    assert matplotlib.get_backend().lower() == "agg"


def test_source_record_binds_bytes_but_makes_no_authority_claim(tmp_path: Path) -> None:
    receipt = tmp_path / "receipt.json"
    receipt.write_text(json.dumps({"status": "FAIL"}), encoding="utf-8")

    record = source_record(receipt, root=tmp_path)

    assert record.path == "receipt.json"
    assert record.byte_count == receipt.stat().st_size
    assert record.sha256 == sha256_file(receipt)
    assert record.as_dict()["integrity_scope"] == "bytes_only"
    assert verify_source_record(record, root=tmp_path)

    receipt.write_text(json.dumps({"status": "PASS"}), encoding="utf-8")
    assert not verify_source_record(record, root=tmp_path)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("PASS", EvidenceStatus.PASS),
        ("failed", EvidenceStatus.FAIL),
        ("UNKNOWN", EvidenceStatus.UNKNOWN),
        ("cannot-check", EvidenceStatus.CANNOT_CHECK),
        (None, EvidenceStatus.NULL),
        ("null", EvidenceStatus.NULL),
        ("adverse", EvidenceStatus.ADVERSE),
    ],
)
def test_status_classification_preserves_non_success_states(
    raw: object, expected: EvidenceStatus
) -> None:
    assert classify_status(raw) is expected


def test_status_classification_preserves_mixed_as_a_distinct_state() -> None:
    assert classify_status("mixed").value == "MIXED"


def test_status_classification_rejects_unrecognised_values() -> None:
    with pytest.raises(ValueError, match="unrecognised evidence status"):
        classify_status("looks-good")


def test_status_palette_has_distinct_colors() -> None:
    required = {
        EvidenceStatus.PASS,
        EvidenceStatus.FAIL,
        EvidenceStatus.UNKNOWN,
        EvidenceStatus.CANNOT_CHECK,
        EvidenceStatus.NULL,
        EvidenceStatus.ADVERSE,
        EvidenceStatus("MIXED"),
    }
    assert required <= STATUS_COLORS.keys()
    assert len({STATUS_COLORS[item] for item in required}) == len(required)


def test_finite_numeric_checks_are_strict() -> None:
    assert np.array_equal(as_finite_1d([1, 2.5]), np.array([1.0, 2.5]))
    for invalid in ([1, np.nan], [1, np.inf], ["1", "2"], [True, False], []):
        with pytest.raises((TypeError, ValueError)):
            as_finite_1d(invalid)


def test_wilson_interval_hand_checkable_cases() -> None:
    assert wilson_interval(0, 1) == pytest.approx((0.0, 0.7934506856))
    assert wilson_interval(1, 1) == pytest.approx((0.2065493144, 1.0))
    low, high = wilson_interval(5, 10)
    assert low == pytest.approx(0.2365930905)
    assert high == pytest.approx(0.7634069095)


def test_jaccard_and_ecdf() -> None:
    assert jaccard_similarity({1, 2}, {2, 3}) == pytest.approx(1 / 3)
    assert jaccard_similarity(set(), set()) == 1.0
    x, y = ecdf([3, 1, 1])
    assert np.array_equal(x, np.array([1.0, 1.0, 3.0]))
    assert np.array_equal(y, np.array([1 / 3, 2 / 3, 1.0]))


def test_pareto_frontier_respects_direction_and_keeps_duplicates() -> None:
    points = np.array([[1, 4], [2, 3], [3, 2], [2, 2], [3, 2]], dtype=float)
    mask = pareto_frontier(points, maximize=(True, True))
    assert np.array_equal(mask, np.array([True, True, True, False, True]))

    minimize_both = pareto_frontier(points, maximize=(False, False))
    assert np.array_equal(minimize_both, np.array([True, False, False, True, False]))


def _assert_rendered(fig, tmp_path: Path, name: str) -> None:
    outputs = save_figure(fig, tmp_path / name)
    assert {path.suffix for path in outputs} == {".png", ".svg"}
    assert all(path.stat().st_size > 100 for path in outputs)


def test_numeric_plot_suite_renders(tmp_path: Path) -> None:
    fig, _ = plot_forest(
        [0.2, -0.1],
        [0.0, -0.3],
        [0.4, 0.1],
        ["P1", "P2"],
        statuses=["PASS", "ADVERSE"],
    )
    _assert_rendered(fig, tmp_path, "forest")

    fig, _, frontier = plot_pareto_scatter(
        [1, 2, 3],
        [3, 1, 2],
        labels=["a", "b", "c"],
        statuses=["PASS", "FAIL", "UNKNOWN"],
    )
    assert np.array_equal(frontier, np.array([True, False, True]))
    _assert_rendered(fig, tmp_path, "pareto")

    fig, ax, _ = plot_pareto_scatter(
        [1, 2, 3],
        [3, 1, 2],
        connect_frontier=False,
    )
    assert not ax.lines
    _assert_rendered(fig, tmp_path, "pareto-unconnected")

    fig, _ = plot_heatmap([[1, 2], [3, 4]], ["P1", "P2"], ["metric-a", "metric-b"], annotate=True)
    _assert_rendered(fig, tmp_path, "heatmap")

    fig, _ = plot_ecdf([1, 1, 3])
    _assert_rendered(fig, tmp_path, "ecdf")

    fig, _, actual_kind = plot_distribution([2, 2, 2])
    assert actual_kind == "histogram"
    _assert_rendered(fig, tmp_path, "distribution")

    fig, _ = plot_trajectories([0, 1, 2], {"observed": [1, 2, 1], "reference": [1, 1, 1]})
    _assert_rendered(fig, tmp_path, "trajectories")


def test_categorical_and_dependency_plots_render(tmp_path: Path) -> None:
    fig, ax = plot_status_matrix(
        [["PASS", "FAIL"], [None, "CANNOT_CHECK"], ["MIXED", "ADVERSE"]],
        ["P1", "P2", "P15"],
        ["replay", "external"],
    )
    cell_text = {text.get_text() for text in ax.texts}
    assert {"PASS", "FAIL", "NULL", "CANNOT\nCHECK", "MIXED", "ADVERSE"} <= cell_text
    assert "UNKNOWN" not in {text.get_text() for text in ax.get_legend().get_texts()}
    _assert_rendered(fig, tmp_path, "status-matrix")

    fig, _, positions = plot_dependency_diagram(
        ["receipt", "transform", "figure"],
        [("receipt", "transform"), ("transform", "figure")],
        groups={"receipt": "evidence", "transform": "method", "figure": "output"},
    )
    assert positions["receipt"][0] < positions["figure"][0]
    _assert_rendered(fig, tmp_path, "dependencies")


def test_rendering_is_byte_deterministic_for_png_and_svg(tmp_path: Path) -> None:
    first, _ = plot_heatmap([[1, 2], [3, 4]], ["a", "b"], ["x", "y"])
    second, _ = plot_heatmap([[1, 2], [3, 4]], ["a", "b"], ["x", "y"])
    first_paths = save_figure(first, tmp_path / "first")
    second_paths = save_figure(second, tmp_path / "second")

    assert [path.read_bytes() for path in first_paths] == [
        path.read_bytes() for path in second_paths
    ]


def test_validation_rejects_misleading_or_invalid_plot_inputs() -> None:
    with pytest.raises(ValueError, match="lower <= estimate <= upper"):
        plot_forest([0], [1], [2], ["bad"])
    with pytest.raises(ValueError, match="same length"):
        plot_trajectories([0, 1], {"bad": [1]})
    with pytest.raises(ValueError, match="shape"):
        plot_status_matrix([["PASS"]], ["P1"], ["a", "b"])
    with pytest.raises(ValueError, match="vmin"):
        plot_heatmap([[1]], ["P1"], ["metric"], vmin=1, vmax=1)
