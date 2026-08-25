from __future__ import annotations

import math

from orion_research_harness.paper_programme_conformance import _p2, paper_programme_conformance
from orion_research_harness.paper_programme_runtime import (
    P13Action,
    p11_accessible_rank_dimension,
    p11_cached_future_coverage,
    p11_one_step_future_coverage,
    p12_joint_alloc,
    p12_success,
    p13_rcs_action,
    p14_governance_disposition,
)


def test_p11_accessible_rank_and_optionality_laws_are_executable():
    assert p11_accessible_rank_dimension(20, 3) == math.comb(20, 3) == 1140
    assert p11_one_step_future_coverage(retained=5, universe=20) == 0.25
    assert p11_cached_future_coverage(retained=5, universe=20, cache_count=2) == 1 - 0.75**2


def test_p11_invalid_resource_coordinates_fail_closed():
    for args in ((0, 3), (3, 4)):
        try:
            p11_accessible_rank_dimension(*args)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid parity-family coordinates must be rejected")


def test_p12_joint_allocator_obeys_matched_budget_and_routes_by_need():
    assert p12_joint_alloc(2.0, 0.0, budget=2) == (2, 0)
    assert p12_joint_alloc(0.0, 2.0, budget=2) == (0, 2)
    assert p12_joint_alloc(1.0, 1.0, budget=2) == (1, 1)
    assert p12_success((2, 0), (2, 0)) is True
    assert p12_success((1, 1), (2, 0)) is False
    assert sum(p12_joint_alloc(2.0, 2.0, budget=2)) <= 2


def test_p13_responsibility_scoped_reuse_reopens_or_cannot_checks():
    assert p13_rcs_action("Z1", "PREDICT", recoverable=False) is P13Action.REUSE
    assert p13_rcs_action("Z1", "VERIFY", recoverable=True) is P13Action.REOPEN
    assert p13_rcs_action("Z1", "VERIFY", recoverable=False) is P13Action.CANNOT_CHECK
    assert p13_rcs_action("Z3", "REPAIR", recoverable=False) is P13Action.REUSE


def test_p14_governance_policy_preserves_noncompensatory_dispositions():
    base = {
        "evidence_integrity": True,
        "frozen_protocol": True,
        "identifiable": True,
        "positive": True,
        "donor_owned": False,
        "interaction_only": False,
        "live_negative_history": False,
        "material_new_evidence": True,
    }
    assert p14_governance_disposition(base) == "SUPPORTED_RESIDUAL"
    assert p14_governance_disposition({**base, "evidence_integrity": False}) == "CANNOT_CHECK"
    assert p14_governance_disposition({**base, "positive": False}) == "NEGATIVE"
    assert p14_governance_disposition({**base, "donor_owned": True}) == "SUBSUMED"
    assert p14_governance_disposition({**base, "interaction_only": True}) == "INTERACTION_ONLY"
    assert p14_governance_disposition(
        {**base, "live_negative_history": True, "material_new_evidence": False}
    ) == "RETAIN_NEGATIVE"


def test_p14_gold_or_private_fields_are_not_policy_inputs():
    bad = {
        "evidence_integrity": True,
        "frozen_protocol": True,
        "identifiable": True,
        "positive": True,
        "donor_owned": False,
        "interaction_only": False,
        "live_negative_history": False,
        "material_new_evidence": True,
        "gold_disposition": "SUPPORTED_RESIDUAL",
    }
    try:
        p14_governance_disposition(bad)
    except ValueError:
        pass
    else:
        raise AssertionError("gold disposition must never be accepted as a policy input")


def test_p2_programme_probe_consumes_current_route_stop_audit_schema():
    positive, fail_closed, owner = _p2()
    assert positive is True
    assert fail_closed is True
    assert owner == "live P2 discovery suite route-stop/task-stop evaluator"


def test_p1_p15_programme_semantic_matrix_is_fully_operational():
    report = paper_programme_conformance()
    assert report["schema"] == "ORION.HarnessPaperProgrammeConformance.v1"
    assert report["terminal"] == "ORION_HARNESS_P1_P15_OPERATIONAL"
    assert report["paper_programme_operational"] is True
    assert report["failed_paper_ids"] == []
    assert [row["paper_id"] for row in report["papers"]] == [f"P{i}" for i in range(1, 16)]
    assert all(row["operational"] for row in report["papers"])
    assert all(row["positive_probe"] for row in report["papers"])
    assert all(row["fail_closed_probe"] for row in report["papers"])
    assert report["grants_scientific_authority"] is False
    assert report["grants_novelty_authority"] is False
    assert report["grants_promotion_authority"] is False
    assert report["grants_global_task_stop_authority"] is False
