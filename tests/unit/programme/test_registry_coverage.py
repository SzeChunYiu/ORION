"""A registry lists what it covers and implies nothing about what it does not."""

from __future__ import annotations

import json
from pathlib import Path

from orion.programme.panel_resolution import duplicate_arms, inspect_metric, MetricResolution
from orion.programme.records import Outcome
from orion.programme.registry_coverage import (
    MIN_ARMS,
    PanelCandidate,
    coverage_report,
    declared_artifacts,
    discover_candidates,
    panel_block,
)

REPO = Path(__file__).resolve().parents[3]
PAPERS = REPO / "papers"
METHOD_AUTHORITY = (
    PAPERS
    / "orion-14-verified-scientific-discovery"
    / "method_authority_extension"
    / "METHOD_AUTHORITY_BENCH_SUMMARY_V1.json"
)


def _panel(arms: dict, **extra) -> dict:
    return {"summary": arms, **extra}


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def test_a_panel_needs_a_decision_beside_it(tmp_path):
    """A bare table of per-arm numbers is usually an intermediate, not a claim."""

    arms = {f"arm{i}": {"rate": i / 10} for i in range(MIN_ARMS)}
    (tmp_path / "bare.json").write_text(json.dumps(_panel(arms)))
    assert discover_candidates(tmp_path, declared=()) == ()

    (tmp_path / "decided.json").write_text(json.dumps(_panel(arms, terminal="X_SUPPORTED")))
    found = discover_candidates(tmp_path, declared=())
    assert len(found) == 1
    assert found[0].terminal == "X_SUPPORTED"


def test_two_arms_are_not_a_panel(tmp_path):
    arms = {"a": {"rate": 0.0}, "b": {"rate": 1.0}}
    (tmp_path / "pair.json").write_text(json.dumps(_panel(arms, terminal="T")))
    assert discover_candidates(tmp_path, declared=()) == ()


def test_a_metric_one_arm_omits_is_not_shared(tmp_path):
    """A missing rate is not a zero, so it cannot be intersected in."""

    arms = {
        "a": {"shared": 1.0, "only_a": 0.5},
        "b": {"shared": 1.0},
        "c": {"shared": 1.0},
    }
    key, block, metrics = panel_block(_panel(arms))
    assert key == "summary"
    assert metrics == ("shared",)


def test_an_artifact_with_no_panel_block_is_not_a_candidate(tmp_path):
    (tmp_path / "flat.json").write_text(json.dumps({"terminal": "T", "score": 1.0}))
    assert discover_candidates(tmp_path, declared=()) == ()


# ---------------------------------------------------------------------------
# The gap
# ---------------------------------------------------------------------------


def test_an_unregistered_panel_is_cannot_check_not_clean():
    registered = PanelCandidate(
        artifact="a", paper_id="P1", systems_key="summary", arms=3, metrics=(), terminal="T", declared=True
    )
    missing = PanelCandidate(
        artifact="b", paper_id="P1", systems_key="summary", arms=3, metrics=(), terminal="T", declared=False
    )
    assert registered.outcome is Outcome.PASS
    assert missing.outcome is Outcome.CANNOT_CHECK
    assert missing.outcome.blocks


def test_a_positive_terminal_is_recognised_as_the_sharper_case():
    supported = PanelCandidate("a", "P1", "summary", 3, (), "X_SUPERIORITY_SUPPORTED", False)
    negative = PanelCandidate("b", "P1", "summary", 3, (), "X_GATE_NOT_MET", False)
    assert supported.claims_support
    assert not negative.claims_support


def test_the_registries_do_not_cover_every_decided_panel():
    """The live measurement. If this ever passes with zero gaps, delete it."""

    report = coverage_report(PAPERS)
    assert report.outcome is Outcome.CANNOT_CHECK
    assert report.unregistered, "no gap found -- either it was closed or discovery broke"
    # Every gap found so far is behind a claim of support, which is the point.
    assert report.unregistered_positives
    artifacts = {Path(c.artifact).name for c in report.unregistered}
    assert "P14B_BALANCED_GOVERNANCE_RESULT_RECEIPT_V1.json" in artifacts
    assert "METHOD_AUTHORITY_BENCH_SUMMARY_V1.json" in artifacts


def test_the_p14b_gap_this_module_found_is_closed_in_the_adjudication():
    """It used to assert ``"p14b" not in adjudication``. That gap is now measured.

    ``orion.study.p14.balanced_governance`` points the gate-attainability
    instrument at P14B's positive terminal, and the adjudication carries what it
    found: the terminal could have printed either word, and four of its eight
    gates could not have. P14B stays outside the *panel-resolution* registries,
    which is a different instrument and a different question --- so the live
    measurement above still finds it unregistered there.
    """

    adjudication = json.loads(
        (PAPERS / "orion-24-orion-rse" / "P14_GATE_ATTAINABILITY_ADJUDICATION_V1.json").read_text()
    )
    assert "p14a" in adjudication
    assert "p14b" in adjudication
    assert "p14c" in adjudication

    block = adjudication["p14b"]
    assert block["terminal_retained_verbatim"] == "P14B_BALANCED_GOVERNANCE_SUPERIORITY_SUPPORTED"
    assert block["committed_digest_reproduced"] is True
    assert block["terminal_reach"]["distinct_terminals"] == 2
    assert block["gates_published"] == 8
    assert len(block["gates_that_discriminate"]) == 4
    assert block["hypothesis_gates_without_refutation_capacity"] == [
        "full_discovery_recall_one",
        "matched_budget",
    ]
    assert adjudication["edits_no_frozen_result"] is True


# ---------------------------------------------------------------------------
# What the unexamined P4 panel turns out to contain
# ---------------------------------------------------------------------------


def test_the_method_authority_panel_separates_without_variation():
    document = json.loads(METHOD_AUTHORITY.read_text())
    assert document["terminal"] == "P4_METHOD_AUTHORITY_SUPPORTED"
    systems = document["systems"]
    assert len(systems) == 4

    for metric in ("false_promotion_rate", "clean_promotion_coverage"):
        report = inspect_metric(systems, metric)
        assert report.resolution is MetricResolution.SEPARATED_WITHOUT_VARIATION
        assert report.distinct_values == 2
        assert set(report.values.values()) <= {0.0, 1.0}


def test_two_of_the_four_method_authority_arms_cannot_differ():
    document = json.loads(METHOD_AUTHORITY.read_text())
    assert duplicate_arms(document["systems"]) == [
        ("provenance_only_policy", "visible_success_policy")
    ]


def test_the_method_authority_claim_still_rests_on_a_real_separation():
    """Not a false result. The subject is the only arm good on both axes.

    Without this the module would read as an argument that the claim is wrong,
    and it is not: the finding is that nobody checked, not that it fails.
    """

    systems = json.loads(METHOD_AUTHORITY.read_text())["systems"]
    subject = systems["P4_MethodTransferReceipt_coordinate_product"]
    assert subject["false_promotion_rate"] == 0.0
    assert subject["clean_promotion_coverage"] == 1.0
    others = [name for name in systems if name != "P4_MethodTransferReceipt_coordinate_product"]
    assert others
    for name in others:
        rates = systems[name]
        assert not (rates["false_promotion_rate"] == 0.0 and rates["clean_promotion_coverage"] == 1.0)


def test_declared_artifacts_reads_all_three_registries():
    declared = declared_artifacts()
    assert any("PUBLICATION_METRICS_V2" in a for a in declared)  # PUBLISHED_PANELS
    assert any("P14A_CONTROLLED_GOVERNANCE" in a for a in declared)  # PUBLISHED_MARGIN_GATES
    assert any("ANALYSIS.json" in a for a in declared)  # PUBLISHED_ABLATIONS
