"""Mechanical PEER_REVIEW_READY gate (issue #153).

A paper may claim the terminal only when the required artifacts exist.
An honest non-claim (CANNOT_CHECK / not ready) must pass. P1 H1 on the
frozen 48-case arm is underpowered; promoting it to PEER_REVIEW_READY or
to a confirmatory SUPPORTED/PASS finding must fail closed.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from orion.publication.peer_review_ready import (
    claims_peer_review_ready,
    evaluate_paper,
    evaluate_tree,
    main,
)
from orion.study.p1.precision_tier import TierRule

REPO = Path(__file__).resolve().parents[3]
PAPERS = REPO / "papers"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def test_done_definition_is_not_a_claim() -> None:
    text = (
        "`ORION-P1 = PEER_REVIEW_READY` only when every gate is complete.\n"
        "**Current terminal:** `CANNOT_CHECK` / not peer-review ready.\n"
    )
    assert claims_peer_review_ready(text) is False


def test_explicit_terminal_line_is_a_claim() -> None:
    text = "**Terminal:** `ORION-P4 = PEER_REVIEW_READY`\n"
    assert claims_peer_review_ready(text) is True


def test_not_ready_current_terminal_is_not_a_claim() -> None:
    text = (
        "**Current terminal:** `CANNOT_CHECK` for externally supported "
        "ORION-vs-baseline discovery superiority; **not** `PEER_REVIEW_READY`.\n"
    )
    assert claims_peer_review_ready(text) is False


def test_a_claim_without_required_artifacts_fails(tmp_path: Path) -> None:
    paper = tmp_path / "paper-99-hollow"
    _write(
        paper / "JOURNAL_READINESS.md",
        "**Terminal:** `ORION-P9 = PEER_REVIEW_READY`\n",
    )
    report = evaluate_paper(paper)
    assert report.claims_ready is True
    assert report.ok is False
    assert report.missing_artifacts
    assert "manuscript/main.tex" in report.missing_artifacts


def test_an_honest_non_claim_passes_even_without_the_ready_bundle(tmp_path: Path) -> None:
    paper = tmp_path / "paper-01-recursive-epistemic-reconstruction"
    _write(
        paper / "JOURNAL_READINESS.md",
        "**Current terminal:** `CANNOT_CHECK` / not peer-review ready.\n"
        "`ORION-P1 = PEER_REVIEW_READY` only when the external study is powered.\n",
    )
    report = evaluate_paper(paper)
    assert report.claims_ready is False
    assert report.ok is True
    assert report.missing_artifacts == ()


def test_a_complete_claim_passes(tmp_path: Path) -> None:
    paper = tmp_path / "paper-04-verified-scientific-discovery"
    _write(paper / "JOURNAL_READINESS.md", "**Terminal:** `ORION-P4 = PEER_REVIEW_READY`\n")
    _write(paper / "manuscript" / "main.tex", "% manuscript\n")
    _write(paper / "evidence" / "CLAIM_LEDGER_V1.md", "# ledger\n")
    _write(paper / "protocol" / "PROTOCOL_V1.json", json.dumps({"paper_id": "P4"}))
    _write(
        paper / "evidence" / "protected_v2" / "PEER_REVIEW_READY_V2.md",
        "**Terminal:** `ORION-P4 = PEER_REVIEW_READY`\n",
    )
    _write(paper / "reproducibility" / "BINDING_MANIFEST_V2.md", "# binding\n")
    report = evaluate_paper(paper)
    assert report.claims_ready is True
    assert report.missing_artifacts == ()
    assert report.ok is True


def test_real_tree_only_p4_claims_ready_and_has_artifacts() -> None:
    reports = {item.paper_id: item for item in evaluate_tree(PAPERS)}
    assert set(reports) == {"P1", "P2", "P3", "P4", "P5"}
    assert reports["P4"].claims_ready is True
    assert reports["P4"].ok is True
    assert reports["P4"].missing_artifacts == ()
    for paper_id in ("P1", "P2", "P3", "P5"):
        assert reports[paper_id].claims_ready is False, paper_id
        assert reports[paper_id].ok is True, paper_id


def test_p1_h1_on_the_frozen_arm_is_underpowered_and_not_supported() -> None:
    reports = {item.paper_id: item for item in evaluate_tree(PAPERS)}
    p1 = reports["P1"]
    assert p1.h1_verdict == "NOT_SUPPORTED"
    assert p1.h1_powered is False
    assert TierRule.from_n(48).underpowered
    assert p1.claims_ready is False
    assert p1.ok is True


def test_claiming_p1_ready_while_h1_is_underpowered_fails() -> None:
    paper = PAPERS / "paper-01-recursive-epistemic-reconstruction"
    original = (paper / "JOURNAL_READINESS.md").read_text()
    report = evaluate_paper(paper, readiness_text="**Terminal:** `ORION-P1 = PEER_REVIEW_READY`\n")
    assert original  # the real file still exists; we only overrode the parse
    assert report.claims_ready is True
    assert report.ok is False
    assert any("underpowered" in reason.lower() or "NOT_SUPPORTED" in reason for reason in report.blockers)


def test_h1_supported_while_underpowered_fails_even_without_a_ready_claim(tmp_path: Path) -> None:
    paper = tmp_path / "paper-01-recursive-epistemic-reconstruction"
    _write(
        paper / "JOURNAL_READINESS.md",
        "**Current terminal:** `CANNOT_CHECK` / not peer-review ready.\n",
    )
    _write(
        paper / "results" / "P1-T2_baseline_ablation_results.json",
        json.dumps(
            {
                "rows": [
                    {
                        "system_id": "orion_full",
                        "scope": "ALL",
                        "n_cases_scored": 48,
                        "difference_vs_comparator": {
                            "assessment": {
                                "hypothesis_id": "P1.H1",
                                "verdict": "SUPPORTED",
                            }
                        },
                    }
                ]
            }
        ),
    )
    report = evaluate_paper(paper)
    assert report.claims_ready is False
    assert report.ok is False
    assert any("H1" in reason for reason in report.blockers)


def test_main_on_the_real_tree_exits_zero() -> None:
    assert main(["--papers", str(PAPERS)]) == 0


def test_main_fails_a_hollow_claim(tmp_path: Path) -> None:
    papers = tmp_path / "papers"
    paper = papers / "paper-99-hollow"
    _write(paper / "JOURNAL_READINESS.md", "**Terminal:** `ORION-P9 = PEER_REVIEW_READY`\n")
    assert main(["--papers", str(papers)]) == 1
