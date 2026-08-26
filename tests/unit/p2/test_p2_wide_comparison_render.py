"""The external Wide table must refuse to lie, in the specific ways tables do.

Validated on synthetic summaries with known contents, and validated in the
negative: each refusal path is exercised, and the no-alarm case renders. The
numbers in this file are invented fixtures, not results.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = (
    ROOT
    / "papers"
    / "orion-12-open-world-scientific-discovery"
    / "scripts"
    / "render_wide_comparison.py"
)


def _module():
    spec = importlib.util.spec_from_file_location("render_wide_comparison", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _summary(**overrides):
    """A synthetic, obviously-fake summary. No real outcome appears in this file."""

    summary = {
        "pinned_upstream_commit": "a46c9bfb8968786f73f0a6a5b365b5384cd0f96d",
        "systems": {
            "wide_lexical_arxiv": {
                "exact_metrics": {"avg_iou": 0.1111, "avg_recall": 0.2222, "avg_precision": 0.3333},
                "scored_tasks": 150,
            },
            "wide_governed_multiroute": {
                "exact_metrics": {"avg_iou": 0.4444, "avg_recall": 0.5555, "avg_precision": 0.6666},
                "scored_tasks": 150,
            },
        },
        "comparison": {
            "paired_tasks": 150,
            "mean_difference": 0.3333,
            "ci_low": 0.2222,
            "ci_high": 0.4444,
            "resamples": 10000,
            "seed": 20260817,
            "interval_definition": "paired percentile bootstrap over matched tasks, 95%",
        },
        "precision": {"n": 150, "achieved_half_width": 0.08002, "tier": "TIER_D_min"},
        "cost_ratio": {
            "candidate_requests_per_task": 3.0,
            "baseline_requests_per_task": 3.0,
            "ratio": 1.0,
            "ceiling": 1.25,
            "within_ceiling": True,
        },
        "verdict": {
            "outcome": "PROMOTE",
            "reason": "synthetic fixture",
            "underpowered_label": True,
            "underpowered_note": "synthetic fixture note",
        },
        "run_manifest": {
            "systems": {
                "wide_lexical_arxiv": {"provider_requests_per_task": 3.0},
                "wide_governed_multiroute": {"provider_requests_per_task": 3.0},
            }
        },
    }
    summary.update(overrides)
    return summary


def test_caption_states_n_unit_uncertainty_role_and_the_underpowered_label():
    module = _module()
    text = module.caption(_summary())
    assert "N=150" in text
    assert "aggregation unit is the task" in text
    assert "paired percentile bootstrap" in text
    assert "UNDERPOWERED" in text, "the label must travel with the number it qualifies"
    assert "matched at 3.0 provider requests" in text
    assert "unseeded" in text, "the excluded sampled family must be explained in the caption"


def test_both_renderings_carry_every_system_and_the_paired_interval():
    module = _module()
    summary = _summary()
    md, tex = module.markdown(summary), module.latex(summary)
    for system_id in summary["systems"]:
        assert system_id in md
        assert system_id in tex
    for rendering in (md, tex):
        assert "0.3333" in rendering  # mean difference
        assert "0.2222" in rendering and "0.4444" in rendering  # interval bounds
        assert "PROMOTE" in rendering


def test_render_refuses_a_summary_that_would_misrepresent_the_evidence():
    module = _module()

    with pytest.raises(module.RefusedToRender):
        module.markdown(_summary(systems={}))

    missing_metric = _summary()
    missing_metric["systems"]["wide_governed_multiroute"]["exact_metrics"] = {}
    with pytest.raises(module.RefusedToRender):
        module.markdown(missing_metric)

    for key in ("comparison", "verdict", "precision", "cost_ratio"):
        incomplete = _summary()
        del incomplete[key]
        with pytest.raises(module.RefusedToRender):
            module.markdown(incomplete)


def test_no_alarm_the_complete_summary_renders():
    module = _module()
    md = module.markdown(_summary())
    assert md.startswith("# Table P2-2-external")
    assert "Do not edit by hand" in md


def test_a_shrink_or_reframe_verdict_renders_as_plainly_as_a_win():
    """The failure branch must be as presentable as the success branch."""

    module = _module()
    summary = _summary(
        verdict={
            "outcome": "SHRINK_OR_REFRAME",
            "reason": "synthetic null fixture",
            "underpowered_label": False,
            "underpowered_note": "synthetic",
        }
    )
    md = module.markdown(summary)
    assert "SHRINK_OR_REFRAME" in md
    assert "UNDERPOWERED" not in module.caption(summary)


def test_cli_writes_both_artifacts(tmp_path):
    module = _module()
    summary_path = tmp_path / "summary.json"
    summary_path.write_text(json.dumps(_summary()), encoding="utf-8")
    md_out, tex_out = tmp_path / "table.md", tmp_path / "table.tex"
    assert module.main(
        [
            "--summary",
            str(summary_path),
            "--markdown-out",
            str(md_out),
            "--latex-out",
            str(tex_out),
        ]
    ) == 0
    assert md_out.is_file() and tex_out.is_file()
    assert "Table P2-2-external" in md_out.read_text(encoding="utf-8")
