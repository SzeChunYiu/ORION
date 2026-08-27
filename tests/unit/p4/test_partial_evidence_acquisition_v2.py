"""Issue #281: P4.partial-evidence-acquisition.v2 protocol freeze and scaffolding.

Frozen P4 V2 (P4.protected-authority.v2) is an integrity input, never an edit target.
"""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

import pytest

from orion.study.p4_partial_evidence.campaign import campaign_status, detect_protected_host
from orion.study.p4_partial_evidence.mechanism import (
    AuthorityTerminal,
    CustodyClass,
    FrozenActionRegistry,
    FrozenRegistryError,
    PartialEvidenceCase,
    UnresolvedDefeater,
    acquire_and_reevaluate,
)
from orion.study.p4_partial_evidence.protocol import (
    FOLLOWUP_PROTOCOL_ID,
    FROZEN_P4_CAMPAIGN_ID,
    load_followup_protocol,
    protocol_root,
)
from orion.study.p4_partial_evidence.reproduce import reproduce_p4_v2_hypotheses

ROOT = Path(__file__).resolve().parents[3]
P4 = ROOT / "papers" / "orion-14-verified-scientific-discovery"
FROZEN_HASHES = {
    "evidence/protected_v2/PUBLICATION_METRICS_V2.json": (
        "42c50a01c1d491fbf423aab3d88ec4f44192015e3fa96a78c007524ed19ef81d"
    ),
    "evidence/protected_v2/FAMILY_CONTRAST_V2.json": (
        "7b3a48a398496d321c648904a3b90ab19dee415fe785b9a67b72b3cf60aa4123"
    ),
    "JOURNAL_READINESS.md": "711f4c92d2758bafe46ff8d9f567a2241e248086aa640f250c7d6d93f02e657d",
    "protocol/PROTECTED_RUN_BINDINGS_V2.json": (
        "ea5c97b3032d461bb595b502f688cb82a7e0651ea9907742095b501340c30fc5"
    ),
    "protocol/PROTOCOL_V1.json": "fe11555a38f24bdb0161d011eef43e842f7bb149e8b0295467d95cbb5e83a77f",
}


def test_frozen_p4_v2_artifacts_are_byte_identical() -> None:
    for rel, expected in FROZEN_HASHES.items():
        digest = sha256((P4 / rel).read_bytes()).hexdigest()
        assert digest == expected, f"frozen P4 V2 artifact mutated: {rel}"


def test_h1_h2_h3_are_reproduced_without_relabeling_h3() -> None:
    receipt = reproduce_p4_v2_hypotheses()
    assert receipt["frozen_campaign_id"] == FROZEN_P4_CAMPAIGN_ID
    assert receipt["followup_protocol_id"] == FOLLOWUP_PROTOCOL_ID
    assert receipt["p4_v2_readiness"] == "PEER_REVIEW_READY"
    assert receipt["H1"]["status"] == "PASS"
    assert receipt["H1"]["orion_false_promotions"] == "0/360"
    assert receipt["H1"]["comparator_false_promotions"] == "180/360"
    assert receipt["H1"]["effect"] == -0.5
    assert receipt["H1"]["ci95"] == [-0.5527777777777778, -0.44722222222222224]
    assert receipt["H2"]["status"] == "PASS"
    assert receipt["H2"]["orion_clean_promotions"] == "60/60"
    assert receipt["H2"]["comparator_clean_promotions"] == "60/60"
    assert receipt["H2"]["effect"] == 0.0
    assert receipt["H3"]["status"] == "NOT_SUPPORTED"
    assert receipt["H3"]["orion_correct_cannot_check"] == "30/30"
    assert receipt["H3"]["comparator_correct_cannot_check"] == "30/30"
    assert receipt["H3"]["effect"] == 0.0
    assert receipt["H3"]["relabeled"] is False
    assert receipt["ablations_worsen_false_promotion"] is True
    assert receipt["ablations_preserve_clean_coverage"] is True
    assert receipt["telemetry_pass"] is True
    assert receipt["receipt_digest"].startswith("sha256:")
    unsigned = {key: value for key, value in receipt.items() if key != "receipt_digest"}
    from orion.transfer.v2.canonical import content_digest

    assert content_digest(unsigned) == receipt["receipt_digest"]
    stored = json.loads(
        (
            ROOT
            / "research"
            / "p4-partial-evidence-acquisition-v2"
            / "H3_REPRODUCTION_RECEIPT_V2.json"
        ).read_text(encoding="utf-8")
    )
    assert stored["receipt_digest"] == receipt["receipt_digest"]
    assert stored["H3"]["status"] == "NOT_SUPPORTED"
    assert stored["H3"]["relabeled"] is False


def test_followup_protocol_is_frozen_before_outcomes() -> None:
    protocol = load_followup_protocol()
    assert protocol["protocol_id"] == FOLLOWUP_PROTOCOL_ID
    assert protocol["incremental_over_protocol"] == FROZEN_P4_CAMPAIGN_ID
    assert protocol["v1_protocol_mutated"] is False
    assert protocol["p4_v2_mutated"] is False
    assert protocol["outcome_accessed"] is False
    assert protocol["protocol_status"] == "DESIGN_FROZEN"
    assert protocol["authority_cap"] == "PLANNER_CAN_NEVER_AUTHORIZE"
    families = protocol["task_families"]
    required = {
        "wrong_source_ambiguity",
        "pooled_support_ambiguity",
        "citation_without_influence",
        "checker_independence_unknown",
        "evaluator_epoch_uncertain",
        "conflicting_sources",
        "evidence_unavailable",
        "clean_no_acquisition",
        "decoy_cheap_non_discharging",
        "expensive_protected_vs_cheap_unprotected",
    }
    assert required <= set(families)
    gold = protocol["gold"]
    assert set(gold["cases"]) == required
    envelope = protocol["cost_envelope"]
    assert envelope["max_actions_per_case"] == 1
    assert envelope["max_cost_units_per_case"] == 12.0
    assert envelope["matched_budget_across_baselines"] is True
    margins = protocol["statistics"]["practical_margin"]
    assert margins["false_promotion_max_increase"] == 0.0
    assert margins["clean_coverage_min_delta"] == 0.0
    assert "result" not in protocol
    assert "outcomes" not in protocol
    root = protocol_root()
    for name in (
        "PROTOCOL_V2.json",
        "CASE_STRUCTURE_V2.json",
        "ACTION_REGISTRY_V2.json",
        "GOLD_V2.json",
        "COST_ENVELOPE_V2.json",
        "LITERATURE_SATURATION_V2.md",
    ):
        assert (root / name).is_file(), name


def test_unprotected_action_cannot_discharge_protected_defeater() -> None:
    case = PartialEvidenceCase(
        case_id="hostile-unprotected",
        family="expensive_protected_vs_cheap_unprotected",
        unresolved=(
            UnresolvedDefeater(
                defeater_id="source_ownership",
                severity=0.95,
                critical=True,
                required_custody=CustodyClass.PROTECTED_EVALUATOR,
            ),
        ),
        observations={"SOURCE_OWNERSHIP": "CANNOT_CHECK"},
    )
    registry = FrozenActionRegistry.from_specs(
        (
            {
                "action_id": "cheap_unprotected_fetch",
                "addresses": ["source_ownership"],
                "success_probability": 1.0,
                "cost": 0.1,
                "custody": CustodyClass.UNPROTECTED.value,
                "source_digest": "sha256:" + "a" * 64,
            },
            {
                "action_id": "protected_source_fetch",
                "addresses": ["source_ownership"],
                "success_probability": 0.9,
                "cost": 4.0,
                "custody": CustodyClass.PROTECTED_EVALUATOR.value,
                "source_digest": "sha256:" + "b" * 64,
            },
        )
    )
    receipt = acquire_and_reevaluate(
        case,
        registry,
        executor=_scripted_executor(
            "protected_source_fetch",
            {"SOURCE_OWNERSHIP": "PASS"},
        ),
    )
    assert receipt.selected_action_id == "protected_source_fetch"
    assert receipt.planner_authority_terminal == "NONE"
    forced = acquire_and_reevaluate(
        case,
        registry,
        executor=_scripted_executor(
            "cheap_unprotected_fetch",
            {"SOURCE_OWNERSHIP": "PASS"},
        ),
        forced_action_id="cheap_unprotected_fetch",
    )
    assert forced.authority_terminal is AuthorityTerminal.CANNOT_CHECK
    assert "source_ownership" in forced.unresolved_critical_defeater_ids
    assert forced.planner_authority_terminal == "NONE"


def test_planner_output_does_not_authorize() -> None:
    case = PartialEvidenceCase(
        case_id="hostile-planner-authorize",
        family="wrong_source_ambiguity",
        unresolved=(
            UnresolvedDefeater(
                defeater_id="source_ownership",
                severity=0.9,
                critical=True,
                required_custody=CustodyClass.INDEPENDENT_HOST,
            ),
        ),
        observations={"SOURCE_OWNERSHIP": "CANNOT_CHECK"},
    )
    registry = FrozenActionRegistry.from_specs(
        (
            {
                "action_id": "host_source_fetch",
                "addresses": ["source_ownership"],
                "success_probability": 0.8,
                "cost": 2.0,
                "custody": CustodyClass.INDEPENDENT_HOST.value,
                "source_digest": "sha256:" + "c" * 64,
            },
        )
    )
    receipt = acquire_and_reevaluate(
        case,
        registry,
        executor=_scripted_executor("host_source_fetch", {"SOURCE_OWNERSHIP": "CANNOT_CHECK"}),
    )
    assert receipt.selected_action_id == "host_source_fetch"
    assert receipt.planner_status == "GATHER_EVIDENCE"
    assert receipt.planner_authority_terminal == "NONE"
    assert receipt.authority_terminal is not AuthorityTerminal.AUTHORIZE
    assert receipt.authority_terminal is AuthorityTerminal.CANNOT_CHECK


def test_no_valid_action_is_cannot_check() -> None:
    case = PartialEvidenceCase(
        case_id="unavailable-evidence",
        family="evidence_unavailable",
        unresolved=(
            UnresolvedDefeater(
                defeater_id="missing_evidence",
                severity=1.0,
                critical=True,
                required_custody=CustodyClass.PROTECTED_EVALUATOR,
            ),
        ),
        observations={"SEMANTIC_SUPPORT": "CANNOT_CHECK"},
    )
    registry = FrozenActionRegistry.from_specs(
        (
            {
                "action_id": "decoy_web_search",
                "addresses": ["unrelated"],
                "success_probability": 1.0,
                "cost": 0.2,
                "custody": CustodyClass.UNPROTECTED.value,
                "source_digest": "sha256:" + "d" * 64,
            },
        )
    )
    receipt = acquire_and_reevaluate(case, registry, executor=_rejecting_executor())
    assert receipt.selected_action_id is None
    assert receipt.authority_terminal is AuthorityTerminal.CANNOT_CHECK
    assert receipt.planner_status == "CANNOT_CHECK"


def test_candidate_cannot_modify_action_registry() -> None:
    registry = FrozenActionRegistry.from_specs(
        (
            {
                "action_id": "protected_source_fetch",
                "addresses": ["source_ownership"],
                "success_probability": 0.9,
                "cost": 4.0,
                "custody": CustodyClass.PROTECTED_EVALUATOR.value,
                "source_digest": "sha256:" + "b" * 64,
            },
        )
    )
    original = registry.digest
    with pytest.raises(FrozenRegistryError):
        registry.add(
            {
                "action_id": "candidate_self_check",
                "addresses": ["source_ownership"],
                "success_probability": 1.0,
                "cost": 0.01,
                "custody": CustodyClass.CANDIDATE.value,
                "source_digest": "sha256:" + "e" * 64,
            }
        )
    with pytest.raises(FrozenRegistryError):
        registry.replace_actions(())
    assert registry.digest == original
    case = PartialEvidenceCase(
        case_id="tamper-registry",
        family="evaluator_epoch_uncertain",
        unresolved=(
            UnresolvedDefeater(
                defeater_id="source_ownership",
                severity=0.9,
                critical=True,
                required_custody=CustodyClass.PROTECTED_EVALUATOR,
            ),
        ),
        observations={"SOURCE_OWNERSHIP": "CANNOT_CHECK"},
    )
    with pytest.raises(FrozenRegistryError):
        acquire_and_reevaluate(
            case,
            registry,
            executor=_rejecting_executor(),
            candidate_registry_patch={"action_id": "injected"},
        )


def test_clean_case_authorizes_from_existing_evidence_not_planner() -> None:
    case = PartialEvidenceCase(
        case_id="clean-no-acquisition",
        family="clean_no_acquisition",
        unresolved=(),
        observations={
            "EXACT_CONTENT_BINDING": "PASS",
            "SOURCE_OWNERSHIP": "PASS",
            "SEMANTIC_SUPPORT": "PASS",
            "CHECKER_INDEPENDENCE": "PASS",
            "CHECKER_DISCRIMINATION": "PASS",
            "BEHAVIORAL_INFLUENCE": "PASS",
            "EVALUATOR_CHRONOLOGY_INTEGRITY": "PASS",
            "SEARCH_CONTAMINATION_CLEAR": "PASS",
            "PROTECTED_ACCESS_CLEAR": "PASS",
        },
    )
    registry = FrozenActionRegistry.from_specs(())
    receipt = acquire_and_reevaluate(case, registry, executor=_rejecting_executor())
    assert receipt.selected_action_id is None
    assert receipt.planner_authority_terminal == "NONE"
    assert receipt.authority_terminal is AuthorityTerminal.AUTHORIZE


def test_campaign_is_cannot_check_without_protected_host() -> None:
    assert detect_protected_host() is False
    status = campaign_status()
    assert status["protocol_id"] == FOLLOWUP_PROTOCOL_ID
    assert status["status"] == "CANNOT_CHECK"
    assert status["reason"] == "protected_host_evaluator_unavailable"
    assert status["p4_v2_readiness"] == "PEER_REVIEW_READY"
    remaining = status["remaining_cannot_check"]
    assert "fresh_secret_seeded_protected_split" in remaining
    assert "matched_baselines_and_ablations_execution" in remaining
    assert "headline_acquisition_experiment" in remaining


def _scripted_executor(expected_action: str, updates: dict[str, str]):
    def execute(action_id: str, case: PartialEvidenceCase) -> dict[str, str]:
        if action_id != expected_action:
            raise AssertionError(f"unexpected action {action_id}")
        merged = dict(case.observations)
        merged.update(updates)
        return merged

    return execute


def _rejecting_executor():
    def execute(action_id: str, case: PartialEvidenceCase) -> dict[str, str]:
        raise AssertionError(f"executor must not run for {action_id}")

    return execute
