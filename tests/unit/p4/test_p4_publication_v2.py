from __future__ import annotations

import json
from pathlib import Path

from orion.publication.manuscript_source import assemble

ROOT = Path(__file__).resolve().parents[3]
P4 = ROOT / "papers" / "orion-14-verified-scientific-discovery"
METRICS = P4 / "evidence" / "protected_v2" / "PUBLICATION_METRICS_V2.json"
MANUSCRIPT = P4 / "manuscript" / "main.tex"


def _manuscript_text() -> str:
    """The document LaTeX builds, not just its entry file.

    ``main.tex`` is a preamble plus ``\\input`` lines since the split, so
    reading it alone would find neither the phrases these tests require nor the
    ones they forbid, and would pass on both counts without checking anything.
    """

    return assemble(MANUSCRIPT)


def test_publication_metrics_match_reproduced_headline() -> None:
    data = json.loads(METRICS.read_text())
    # Exact execution identity belongs in the immutable evidence package. The
    # double-blind manuscript may deliberately omit developer/run identifiers.
    assert data["campaign_run_id"] == "31976589735"
    assert data["subject_commit"] == "f6e51b5c8f905382b8e2f5568d9035fc14241aa1"
    assert data["hypotheses"]["H1"]["status"] == "PASS"
    assert data["hypotheses"]["H2"]["status"] == "PASS"
    assert data["hypotheses"]["H3"]["status"] == "NOT_SUPPORTED"
    assert data["systems"]["ORION"]["false_promotion_rate"] == 0.0
    assert data["systems"]["ORION"]["clean_false_negative_count"] == 0
    strongest = data["strongest_frozen_comparator"]
    assert data["systems"][strongest]["false_promotion_rate"] == 0.5
    receipt = data["reproduction"]
    assert receipt["headline_reproduced"] is True
    assert receipt["orion_false_promotions"] == 0
    assert receipt["comparator_false_promotions"] == 180
    assert receipt["orion_clean_promotions"] == receipt["comparator_clean_promotions"] == 60
    assert receipt["promotion_opportunities"] == 360
    assert len(data["ablations"]) == 8
    for key in (
        "candidate_protected_identifier_hits",
        "comparator_protected_identifier_hits",
        "candidate_external_ip_connects",
        "comparator_external_ip_connects",
    ):
        assert data["telemetry"][key] == 0


def test_manuscript_uses_v2_and_reports_null_h3() -> None:
    text = _manuscript_text()
    assert "0/360" in text and "180/360" in text and "60/60" in text
    assert "H3 was not supported" in text
    assert "protocol-matched reimplementations" in text
    assert "39-case live-model arm" in text

    banned_stale_claims = [
        "execution bindings remain \\texttt{UNBOUND}",
        "No external results are reported",
        "awaiting external campaign",
        "remains externally \\texttt{CANNOT\\_CHECK}",
    ]
    assert not any(term in text for term in banned_stale_claims)


def test_blind_manuscript_has_no_operational_repository_leakage() -> None:
    text = _manuscript_text()

    # Publication-facing prose must preserve the science while remaining
    # double-blind and reader-facing. Exact run/repository identities stay in
    # the evidence manifest and anonymous review artifact, not the manuscript.
    banned_operational = [
        "31976589735",
        "SzeChunYiu/ORION",
        "GitHub Actions",
        "default branch",
        "pull request",
        "workflow run",
        "run_id",
        "papers/orion-14-verified-scientific-discovery/",
        "development/p4-",
        "evidence/protected_v",
        "host/evaluate_campaign",
        "host/independent_reproduce",
    ]
    assert not any(term in text for term in banned_operational)
