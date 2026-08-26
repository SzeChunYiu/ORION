from __future__ import annotations

from orion_research_harness.campaign_control import decide_campaign, manifest_digest, validate_manifest
from orion_research_harness.campaign_protocol import CampaignState
from orion_research_harness.domains.orion_rg import X1A_DAVENPORT_3_5_CAMPAIGN_MANIFEST
from orion_research_harness.domains.registry import builtin_campaign_ids, load_builtin_campaign


def _state(phase_id: str, observations: dict[str, str], obligations=()):
    manifest = X1A_DAVENPORT_3_5_CAMPAIGN_MANIFEST
    return CampaignState.create(
        campaign_id=manifest["campaign_id"],
        claim_id=manifest["claim_id"],
        phase_id=phase_id,
        cycle_index={"S0": 0, "D0": 1, "B0": 2}[phase_id],
        manifest_digest=manifest_digest(manifest),
        observations=observations,
        active_hard_obligations=obligations,
        protected_refs=(),
        authority_ceiling=manifest["authority_ceiling"],
    )


def test_x1a_manifest_is_registered_and_non_authorizing():
    manifest = X1A_DAVENPORT_3_5_CAMPAIGN_MANIFEST
    validate_manifest(manifest)
    assert manifest["campaign_id"] in builtin_campaign_ids()
    assert load_builtin_campaign(manifest["campaign_id"]) is manifest
    assert manifest["authority_ceiling"] == "NON_AUTHORIZING_MATH_DISCOVERY_FIBRE"
    terminal = manifest["phases"]["FRONTIER_FROZEN"]
    assert terminal["terminal_name"] == "X1A_ONE_BLOCK_DEFICIT_DISCOVERY_FIBRE_FROZEN__NO_THEOREM_AUTHORITY"


def test_x1a_control_orders_donor_refusal_before_deficit_reframe():
    manifest = X1A_DAVENPORT_3_5_CAMPAIGN_MANIFEST

    s0 = _state(
        "S0",
        {"X1A_DONOR_REVIEW_NEEDED": "YES"},
        obligations=("X1A_BIND_CURRENT_DONOR_FRONTIER",),
    )
    d0 = decide_campaign(s0, manifest)
    assert d0.selected_id == "COMPUTE:X1A_VERIFY_DONORS"

    donor_bound = _state(
        "D0",
        {"X1A_DONOR_VERIFIED": "YES"},
        obligations=("X1A_REFUTE_NAIVE_DK_ROUTE",),
    )
    d1 = decide_campaign(donor_bound, manifest)
    assert d1.selected_id == "COMPUTE:X1A_RECONSTRUCT_DK_OBSTRUCTION"

    blocked = _state(
        "B0",
        {"X1A_ORDINARY_DK_ROUTE_BLOCKED": "YES"},
        obligations=("X1A_FREEZE_ONE_BLOCK_DEFICIT",),
    )
    d2 = decide_campaign(blocked, manifest)
    assert d2.selected_id == "COMPUTE:X1A_ONE_BLOCK_DEFICIT"
    assert d2.revision["selected_mechanic_id"] == "REV:X1A_REFRAME_TO_LIFT_COMPATIBLE_OBSTRUCTION"


def test_x1a_finite_calibration_cannot_claim_family_theorem():
    manifest = X1A_DAVENPORT_3_5_CAMPAIGN_MANIFEST
    contract = manifest["capabilities"]["x1a.reconstruct_one_block_deficit"]["result_contract"]
    required = {tuple(row["path"]): row["equals"] for row in contract["required_payload_values"]}
    assert required[("calibration_only",)] is True
    assert required[("family_theorem_authority",)] is False
    assert required[("novelty_authority",)] is False
    assert required[("scientific_authority",)] is False
