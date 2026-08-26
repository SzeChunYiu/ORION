"""Reusable, receipt-first plotting primitives for the ORION evidence atlas."""

# Import style first so every downstream pyplot import uses the headless backend.
from .styles import (
    STATUS_COLORS,
    STATUS_MARKERS,
    STATUS_SYMBOLS,
    apply_atlas_style,
    save_figure,
)
from .authority import (
    AuthorityLevel,
    EvidenceStatus,
    classify_status,
    classify_statuses,
    status_counts,
)
from .diagrams import plot_dependency_diagram, plot_framework_diagram
from .io import (
    SourceRecord,
    load_json,
    sha256_file,
    source_record,
    verify_source_record,
    write_json,
)
from .plots import (
    plot_distribution,
    plot_ecdf,
    plot_forest,
    plot_heatmap,
    plot_pareto_scatter,
    plot_status_matrix,
    plot_trajectories,
)
from .transforms import (
    as_finite_1d,
    as_finite_2d,
    ecdf,
    jaccard_similarity,
    pareto_frontier,
    wilson_interval,
)

__all__ = [
    "AuthorityLevel",
    "EvidenceStatus",
    "STATUS_COLORS",
    "STATUS_MARKERS",
    "STATUS_SYMBOLS",
    "SourceRecord",
    "apply_atlas_style",
    "as_finite_1d",
    "as_finite_2d",
    "classify_status",
    "classify_statuses",
    "ecdf",
    "jaccard_similarity",
    "load_json",
    "pareto_frontier",
    "plot_dependency_diagram",
    "plot_distribution",
    "plot_ecdf",
    "plot_forest",
    "plot_framework_diagram",
    "plot_heatmap",
    "plot_pareto_scatter",
    "plot_status_matrix",
    "plot_trajectories",
    "save_figure",
    "sha256_file",
    "source_record",
    "status_counts",
    "verify_source_record",
    "wilson_interval",
    "write_json",
]
