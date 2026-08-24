"""Portfolio-integrity audit, validated by breaking the real disposition.

Four of issue #1086's "Definition of done" bullets are properties of the
portfolio record rather than of any experiment. These tests assert the shipped
record satisfies them, and then mutate that same record -- not a fixture -- to
confirm the audit refuses each violation. Asserting the no-alarm case matters as
much as the alarms: an auditor that fails everything closes no box.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from orion.programme.portfolio_integrity import (
    CONSOLIDATION_GROUPS,
    EXIT_CANNOT_CHECK,
    EXIT_MISSING_CONSOLIDATION,
    EXIT_PARTITION_COLLISION,
    EXIT_PASS,
    EXIT_STOPGO_MALFORMED,
    audit_disposition,
)

DISPOSITION = Path("papers/ISSUE_1086_PORTFOLIO_DISPOSITION_V1.json")


def _root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / DISPOSITION).is_file():
            return parent
    pytest.skip("portfolio disposition not found")


@pytest.fixture(scope="module")
def document() -> dict:
    return json.loads((_root() / DISPOSITION).read_text(encoding="utf-8"))


def test_the_shipped_disposition_passes(document):
    audit = audit_disposition(document)
    assert audit.exit_code == EXIT_PASS, audit.problems
    assert audit.passed


def test_every_surviving_paper_carries_its_own_external_partition(document):
    """Definition of done: unique primary endpoint, disjoint external partition."""

    audit = audit_disposition(document)
    partitions = dict(audit.partitions)
    assert set(partitions) == {"P1", "P2", "P3", "P4"}
    assert len(set(partitions.values())) == len(partitions), "partitions are not disjoint"


def test_no_benchmark_is_claimed_by_two_papers(document):
    """Definition of done: no public row is independent validation for two papers."""

    audit = audit_disposition(document)
    benchmarks = [benchmark for _, benchmark in audit.partitions]
    assert len(benchmarks) == len(set(benchmarks))


def test_a_shared_benchmark_is_refused(document):
    mutated = copy.deepcopy(document)
    for decision in mutated["decisions"]:
        required = decision.get("required_external_partitions")
        if isinstance(required, dict) and "P2" in required:
            required["P2"] = required["P1"]
            break
    else:  # pragma: no cover
        pytest.fail("no partition decision to mutate")
    audit = audit_disposition(mutated)
    assert audit.exit_code == EXIT_PARTITION_COLLISION
    assert any("claimed by both" in problem for problem in audit.problems)


def test_contradictory_partitions_for_one_paper_are_refused(document):
    mutated = copy.deepcopy(document)
    mutated["decisions"].append(
        {
            "decision_id": "DX",
            "papers": ["P1"],
            "status": "ADOPTED",
            "disposition": "OTHER",
            "required_external_partitions": {"P1": "SomeOtherBenchmark"},
        }
    )
    assert audit_disposition(mutated).exit_code == EXIT_PARTITION_COLLISION


@pytest.mark.parametrize("group", CONSOLIDATION_GROUPS)
def test_each_named_group_carries_an_adopted_consolidation(document, group):
    audit = audit_disposition(document)
    assert "+".join(group) in audit.consolidated_groups


@pytest.mark.parametrize("group", CONSOLIDATION_GROUPS)
def test_removing_a_consolidation_decision_is_refused(document, group):
    mutated = copy.deepcopy(document)
    mutated["decisions"] = [
        d for d in mutated["decisions"] if set(d.get("papers", [])) != set(group)
    ]
    audit = audit_disposition(mutated)
    assert audit.exit_code == EXIT_MISSING_CONSOLIDATION
    assert any("+".join(group) in problem for problem in audit.problems)


def test_a_consolidation_that_was_only_proposed_is_refused(document):
    mutated = copy.deepcopy(document)
    for decision in mutated["decisions"]:
        if set(decision.get("papers", [])) == {"P13", "P14"}:
            decision["status"] = "PROPOSED"
            break
    assert audit_disposition(mutated).exit_code == EXIT_MISSING_CONSOLIDATION


def test_p12_stop_go_defines_a_stop_branch(document):
    """"Passes once or stops" is only real if the stop branch is written down."""

    decision = next(d for d in document["decisions"] if d["papers"] == ["P12"])
    assert "STOP_GO" in decision["disposition"].upper()
    rule = decision["rule"].lower()
    assert "otherwise" in rule and "stop" in rule


def test_a_stop_go_rule_without_a_stop_branch_is_refused(document):
    mutated = copy.deepcopy(document)
    for decision in mutated["decisions"]:
        if decision.get("papers") == ["P12"]:
            decision["rule"] = "Publish P12 separately if its frozen successor study passes."
            break
    audit = audit_disposition(mutated)
    assert audit.exit_code == EXIT_STOPGO_MALFORMED
    assert any("no stop branch" in problem for problem in audit.problems)


def test_removing_p12_entirely_is_refused(document):
    mutated = copy.deepcopy(document)
    mutated["decisions"] = [d for d in mutated["decisions"] if d.get("papers") != ["P12"]]
    assert audit_disposition(mutated).exit_code == EXIT_STOPGO_MALFORMED


@pytest.mark.parametrize("bad", [None, "doc", 5, [], {}, {"decisions": []}, {"decisions": [1]}])
def test_malformed_dispositions_cannot_be_checked_and_never_pass(bad):
    audit = audit_disposition(bad)
    assert audit.exit_code == EXIT_CANNOT_CHECK
    assert not audit.passed


def test_the_audit_creates_no_scientific_authority(document):
    """The disposition says so; the audit must not quietly exceed it."""

    assert document["scientific_authority_delta"] == "NONE"
    assert "PORTFOLIO_EDITORIAL_DISPOSITION_ONLY" in document["authority"]


# --------------------------------------------------------------------------
# Cross-paper source sharing: reported, not silently tolerated.
# --------------------------------------------------------------------------


def test_shared_source_families_are_surfaced_not_hidden():
    """Six families are named by more than one paper; the audit must say so."""

    from orion.programme.portfolio_integrity import shared_source_families

    shared = dict(shared_source_families())
    assert set(shared) == {
        "CORE-Bench",
        "IPC",
        "LeanDojo",
        "PaperBench",
        "ScienceAgentBench",
        "WorkflowHub",
    }
    assert shared["ScienceAgentBench"] == ("P1", "P12", "P15+Q3")
    assert shared["WorkflowHub"] == ("P6", "P7", "P9")


def test_sharing_a_family_does_not_fail_the_audit(document):
    """A shared corpus with disjoint row partitions is legitimate; the audit reports it."""

    assert audit_disposition(document).exit_code == EXIT_PASS


def test_a_disjoint_family_map_reports_nothing():
    """No-alarm case: the report fires on real sharing, not on any map at all."""

    from orion.programme.portfolio_integrity import shared_source_families

    assert shared_source_families({"PA": ("X",), "PB": ("Y",)}) == ()


def test_the_family_map_covers_every_paper_the_issue_lists():
    from orion.programme.portfolio_integrity import ISSUE_SOURCE_FAMILIES

    assert set(ISSUE_SOURCE_FAMILIES) == {
        "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8",
        "P9", "P10", "P11", "P12", "P13+P14", "P15+Q3",
    }
    assert all(entries for entries in ISSUE_SOURCE_FAMILIES.values())
