from __future__ import annotations

from orion_research_harness.research_v4_conformance import TERMINAL, research_v4_conformance


def test_v4_covariance_terminal_is_operational_and_non_authorizing():
    report = research_v4_conformance()
    assert report["schema"] == "ORION.PaperFrameworkHarnessCovarianceConformance.v4"
    assert report["terminal"] == TERMINAL
    assert report["operational"] is True
    assert report["failed_probes"] == []
    assert report["probes"] and all(report["probes"].values())
    assert report["framework_version"] == "0.3.10-shadow"
    assert report["paper_sync_epoch"] == "2026-08-22-paper-framework-harness-covariance-v4"
    assert report["grants_scientific_authority"] is False
    assert report["grants_novelty_authority"] is False
    assert report["grants_promotion_authority"] is False
    assert report["grants_global_task_stop_authority"] is False
