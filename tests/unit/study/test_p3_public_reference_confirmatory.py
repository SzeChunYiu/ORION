from __future__ import annotations

from orion.study.p3_public_reference_confirmatory import confirmatory_verdict


def _analysis(fm_point: float, fm_high: float, fs_point: float, fs_high: float) -> dict[str, object]:
    return {
        "primary_comparisons": {
            "false_merge_orion_minus_flat": {
                "candidate_minus_baseline": fm_point,
                "ci95_low": fm_point - 0.1,
                "ci95_high": fm_high,
                "n": 32.0,
            },
            "false_split_orion_minus_exact": {
                "candidate_minus_baseline": fs_point,
                "ci95_low": fs_point - 0.01,
                "ci95_high": fs_high,
                "n": 32.0,
            },
        }
    }


def test_confirmatory_pass_requires_margin_and_ci() -> None:
    verdict = confirmatory_verdict(_analysis(-0.125, -0.03125, 0.0, 0.0))
    assert verdict["false_merge_superiority"] is True
    assert verdict["false_split_noninferiority"] is True
    assert verdict["confirmatory_primary_pass"] is True


def test_false_merge_point_margin_without_ci_exclusion_does_not_pass() -> None:
    verdict = confirmatory_verdict(_analysis(-0.125, 0.0, 0.0, 0.0))
    assert verdict["false_merge_superiority"] is False
    assert verdict["confirmatory_primary_pass"] is False


def test_false_split_ci_must_remain_inside_noninferiority_margin() -> None:
    verdict = confirmatory_verdict(_analysis(-0.125, -0.01, 0.0, 0.04))
    assert verdict["false_split_noninferiority"] is False
    assert verdict["confirmatory_primary_pass"] is False
