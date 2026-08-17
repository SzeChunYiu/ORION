from __future__ import annotations

from pathlib import Path

from orion.study.p3_public_reference_publication import generate


def _metric(rate: float) -> dict[str, float]:
    return {"rate": rate, "ci95_low": rate, "ci95_high": rate, "n": 4.0}


def test_generate_writes_tables_and_three_svgs(tmp_path: Path) -> None:
    systems = {
        "orion": {"accuracy": _metric(1.0), "false_merge": _metric(0.0), "false_split": _metric(0.0), "abstention": _metric(0.0)},
        "flat_predicate_canonicalization": {"accuracy": _metric(0.75), "false_merge": _metric(0.25), "false_split": _metric(0.0), "abstention": _metric(0.0)},
        "exact_coordinate_conservative": {"accuracy": _metric(0.75), "false_merge": _metric(0.0), "false_split": _metric(0.0), "abstention": _metric(0.25)},
    }
    comparison = {"candidate_minus_baseline": -0.25, "ci95_low": -0.5, "ci95_high": -0.1, "n": 4.0}
    zero = {"candidate_minus_baseline": 0.0, "ci95_low": 0.0, "ci95_high": 0.0, "n": 4.0}
    analysis = {
        "pooled": {
            "systems": systems,
            "primary_comparisons": {
                "false_merge_orion_minus_flat": comparison,
                "false_split_orion_minus_exact": zero,
            },
            "ablation_deltas": {
                "force_compatibility_without_obstruction": {
                    "false_merge_ablation_minus_full": {"candidate_minus_baseline": 0.25, "ci95_low": 0.1, "ci95_high": 0.5, "n": 4.0}
                }
            },
        },
        "by_case_family": {
            "polarity_modality_attribution_context": {
                "case_count": 4,
                "orion": {"false_merge_rate": 0.0},
                "flat_predicate_canonicalization": {"false_merge_rate": 0.25},
                "exact_coordinate_conservative": {"abstention_rate": 0.25},
            }
        },
    }
    generate(analysis, tmp_path)

    table = (tmp_path / "PUBLIC_REFERENCE_CONFIRMATORY_TABLES_V1.md").read_text()
    assert "ORION − flat false merge" in table
    assert "-0.2500" in table
    for name in (
        "PR3-F1_false_merge_by_system.svg",
        "PR3-F2_flat_false_merge_by_case_family.svg",
        "PR3-F3_ablation_false_merge_deltas.svg",
    ):
        text = (tmp_path / name).read_text()
        assert text.startswith("<svg")
        assert "</svg>" in text
