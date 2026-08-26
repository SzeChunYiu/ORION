from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

from orion.study.p13.authenticated_successor import (
    NOT_SUPPORTED,
    SUPPORTED,
    WORLDS,
    adjudicate,
    build_core,
    gold_support,
    load_gold_spec,
)
from orion.study.p13.successor_authority import build_active_claim_authority

ROOT = Path(__file__).resolve().parents[4]
PAPER = ROOT / "papers/orion-23-responsibility-carrying-state"
RESULT = PAPER / "P13B_AUTHENTICATED_CERTIFICATE_CORRUPTION_RESULT_V1.json"
AUTHORITY = PAPER / "P13_ACTIVE_CLAIM_AUTHORITY_V2.json"


def test_gold_is_computed_from_state_and_task_not_certificate() -> None:
    spec = load_gold_spec()
    assert gold_support(spec, "Z3", "REPAIR") is True
    assert gold_support(spec, "Z5", "REPAIR") is False
    core = build_core()
    assert core["gold_reads_certificate"] is False
    assert core["authority_boundary"] == "controlled_finite_world_not_external_validation"


def test_every_required_world_has_real_opportunities_before_scoring() -> None:
    core = build_core()
    assert set(core["corruption_worlds"]) == set(WORLDS)
    assert all(core["corruption_worlds"][world]["mutation_opportunities"] > 0 for world in WORLDS)


def test_protected_result_recomputes_as_bounded_positive() -> None:
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    rebuilt = adjudicate(result["core"], byte_identical_replay=True)
    assert rebuilt["summary"] == result["summary"]
    assert rebuilt["gates"] == result["gates"]
    assert result["terminal"] == SUPPORTED
    assert result["core"]["panel_denominator"] == 30
    assert result["replay"]["byte_identical"] is True


def test_zero_opportunity_or_one_unsafe_authenticated_reuse_forces_negative() -> None:
    core = build_core()
    blind = deepcopy(core)
    blind["corruption_worlds"]["OMITTED_SUPPORT"]["mutation_opportunities"] = 0
    assert adjudicate(blind, byte_identical_replay=True)["terminal"] == NOT_SUPPORTED

    unsafe = deepcopy(core)
    unsafe["corruption_worlds"]["OVERBROAD_SUPPORT"]["panel"]["arms"][
        "AUTHENTICATED_RCS"
    ]["unsafe_reuse"] = 1
    assert adjudicate(unsafe, byte_identical_replay=True)["terminal"] == NOT_SUPPORTED


def test_replay_is_a_noncompensatory_gate() -> None:
    assert adjudicate(build_core(), byte_identical_replay=False)["terminal"] == NOT_SUPPORTED


def test_v2_authority_rebuilds_and_forbids_external_promotion() -> None:
    authority = json.loads(AUTHORITY.read_text(encoding="utf-8"))
    assert authority == build_active_claim_authority()
    assert authority["active_claim_leaves"][1]["terminal"] == SUPPORTED
    assert authority["historical_boundary_leaf"]["terminal"] == (
        "P13A_EMPIRICAL_SAFETY_COST_AUTHORITY_WITHHELD"
    )
    assert "EXTERNAL_VALIDATION" in authority["forbidden_promotions"]
