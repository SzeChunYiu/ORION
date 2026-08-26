"""Mechanical PEER_REVIEW_READY gate (issue #153).

A paper may claim the terminal only when the required artifacts exist.
An honest non-claim (CANNOT_CHECK / not ready) must pass. P1 H1 on the
frozen 48-case arm is underpowered; promoting that arm to PEER_REVIEW_READY or
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


def test_only_in_present_tense_prose_does_not_hide_a_claim() -> None:
    text = (
        "**Terminal:** `ORION-P4 = PEER_REVIEW_READY`; "
        "the only remaining work is external editorial review.\n"
    )
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
    paper = tmp_path / "orion-11-recursive-epistemic-reconstruction"
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
    paper = tmp_path / "orion-14-verified-scientific-discovery"
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


def test_real_tree_p1_p2_and_p4_claim_ready_and_have_artifacts() -> None:
    reports = {item.paper_id: item for item in evaluate_tree(PAPERS)}
    assert set(reports) == {"P1", "P2", "P3", "P4", "P5"}
    assert reports["P4"].claims_ready is True
    assert reports["P4"].ok is True
    assert reports["P4"].missing_artifacts == ()
    assert reports["P1"].claims_ready is True
    assert reports["P1"].p1_successor_valid is True
    assert reports["P1"].ok is True
    assert reports["P2"].claims_ready is True
    assert reports["P2"].ok is True
    assert reports["P2"].missing_artifacts == ()
    for paper_id in ("P3", "P5"):
        assert reports[paper_id].claims_ready is False, paper_id
        assert reports[paper_id].ok is True, paper_id


def test_p1_h1_on_the_frozen_arm_is_underpowered_and_not_supported() -> None:
    reports = {item.paper_id: item for item in evaluate_tree(PAPERS)}
    p1 = reports["P1"]
    assert p1.h1_verdict == "NOT_SUPPORTED"
    assert p1.h1_powered is False
    assert TierRule.from_n(48).underpowered
    assert p1.claims_ready is True
    assert p1.p1_successor_valid is True
    assert p1.ok is True


def test_claiming_p1_ready_without_the_powered_successor_fails(tmp_path: Path) -> None:
    paper = tmp_path / "repo" / "papers" / "orion-11-recursive-epistemic-reconstruction"
    _write(paper / "JOURNAL_READINESS.md", "**Terminal:** `ORION-P1 = PEER_REVIEW_READY`\n")
    _write(
        paper / "results" / "P1-T2_baseline_ablation_results.json",
        json.dumps({"rows": []}),
    )
    report = evaluate_paper(paper)
    assert report.claims_ready is True
    assert report.p1_successor_valid is False
    assert report.ok is False
    assert any("successor" in reason.lower() for reason in report.blockers)


def test_h1_supported_while_underpowered_fails_even_without_a_ready_claim(tmp_path: Path) -> None:
    paper = tmp_path / "orion-11-recursive-epistemic-reconstruction"
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


def test_a_narrowed_terminal_is_not_read_as_a_full_readiness_claim() -> None:
    """`PEER_REVIEW_READY_NARROWED` is a weaker terminal, not this one.

    This gate originally used a plain `"PEER_REVIEW_READY" in line` test and so read
    P2's real line

        `ORION-P2 = PEER_REVIEW_READY_NARROWED` when the narrowed manuscript compiles

    as a claim of full readiness, then failed the paper for lacking the artifacts such
    a claim would need. Two separate mistakes in one line: the token was matched as a
    prefix of a longer one, and a "when" clause was treated as an assertion rather than
    a definition of done.

    Both directions are pinned here. A narrowed terminal and a conditional line must not
    register as claims, and a real unconditional claim still must — a gate that stopped
    firing altogether would also make this test's first half pass.
    """

    # Bare narrowed terminal, with no conditional word anywhere on the line. This is the
    # case that actually exercises the token discipline: an earlier version of this test
    # used P2's real line, which contains "when", and so still passed when the token was
    # reverted to a plain substring test. The conditional clause was masking the defect.
    bare_narrowed = "`ORION-P2 = PEER_REVIEW_READY_NARROWED`\n"
    assert claims_peer_review_ready(bare_narrowed) is False

    narrowed_terminal = "**Terminal:** `ORION-P2 PEER_REVIEW_READY_NARROWED`\n"
    assert claims_peer_review_ready(narrowed_terminal) is False

    # P2's real line, which is both narrowed and conditional.
    narrowed = "`ORION-P2 = PEER_REVIEW_READY_NARROWED` when the manuscript compiles cleanly\n"
    assert claims_peer_review_ready(narrowed) is False

    conditional = "`ORION-P2 = PEER_REVIEW_READY` once section 8's checks pass\n"
    assert claims_peer_review_ready(conditional) is False

    negated = "**Current terminal:** not PEER_REVIEW_READY.\n"
    assert claims_peer_review_ready(negated) is False

    # Non-vacuity: the gate must still catch an unconditional present-tense claim.
    real_claim = "`ORION-P2 = PEER_REVIEW_READY`\n"
    assert claims_peer_review_ready(real_claim) is True

    terminal_line = "**Terminal:** `ORION-P4 PEER_REVIEW_READY`\n"
    assert claims_peer_review_ready(terminal_line) is True
