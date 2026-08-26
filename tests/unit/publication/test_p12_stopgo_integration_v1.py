from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "papers/orion-22-adaptive-state-reasoning"
CHECKER = PAPER / "check_p12_stopgo_integration_v1.py"
MENUS = PAPER / "top_tier/p12_stopgo_frozen_menus_v1.json"
AUTHORITY_V4 = PAPER / "P12_ACTIVE_CLAIM_AUTHORITY_V4.json"
AUTHORITY_V5 = PAPER / "P12_ACTIVE_CLAIM_AUTHORITY_V5.json"


def _module():
    spec = importlib.util.spec_from_file_location("p12_stopgo_integration_v1", CHECKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_menus(tmp_path: Path, menus: dict) -> Path:
    mutant = tmp_path / "menus.json"
    mutant.write_text(json.dumps(menus), encoding="utf-8")
    return mutant


def _write_authority(tmp_path: Path, authority: dict) -> Path:
    mutant = tmp_path / "authority.json"
    mutant.write_text(json.dumps(authority), encoding="utf-8")
    return mutant


def test_p12_stopgo_protocol_package_passes_fail_closed_audit():
    report = _module().audit()
    assert report["status"] == "PASS", report["errors"]


def test_p12_stopgo_freeze_confers_no_authority_and_no_external_validation():
    report = _module().audit()
    assert report["scientific_authority_delta"] == "NONE"
    assert report["external_validation"] == "CANNOT_CHECK"
    assert report["artifact_class"] == "FROZEN_PROTOCOL_NO_RESULTS"


def test_authority_v5_preserves_lifecycle_v4_and_only_extends():
    v4 = json.loads(AUTHORITY_V4.read_text(encoding="utf-8"))
    v5 = json.loads(AUTHORITY_V5.read_text(encoding="utf-8"))
    for key, value in v4.items():
        if key in ("schema", "evidence_bindings", "forbidden_promotions"):
            continue
        assert v5[key] == value, f"inherited field drifted: {key}"
    for key, binding in v4["evidence_bindings"].items():
        assert v5["evidence_bindings"].get(key) == binding, f"binding drifted: {key}"
    assert all(x in v5["forbidden_promotions"] for x in v4["forbidden_promotions"])
    assert "PUBLICDATA_CAMPAIGN_RESULT_CLAIM_BEFORE_EXECUTION" in v5["forbidden_promotions"]
    assert "P12C_ARTIFACT_INVENTED_RETROACTIVELY" in v5["forbidden_promotions"]
    assert v5["stopgo_campaign_leaf"]["results_exist"] is False
    assert v5["top_tier_submission_allowed"] is False


@pytest.mark.parametrize(
    ("mutation", "expected_error"),
    [
        (lambda d: d.update(results_exist=True), "menus claim results existence"),
        (lambda d: d.update(campaign_executed=True), "menus claim campaign execution"),
        (
            lambda d: d["arms"]["ADAPTIVE"]["action_menu"].append(
                {"action_id": "MUTANT", "state_construction_units": 9, "reasoning_units": 9}
            ),
            "action menu differs from canonical",
        ),
        (
            lambda d: d["arms"]["ONE_SIGNAL_STATE"].update(
                readable_signals=[
                    "S_PENDING_MULTIPLICITY",
                    "S_DECLARED_MATERIALIZATION_COST",
                ]
            ),
            "must read exactly one signal",
        ),
        (
            lambda d: d["arms"]["ONE_SIGNAL_REASON"].update(
                readable_signals=["S_PENDING_MULTIPLICITY"]
            ),
            "must read different signals",
        ),
        (
            lambda d: d["campaign_scope_minimums"].update(task_families=5),
            ">= 20 task families",
        ),
        (
            lambda d: d["campaign_scope_minimums"].update(satisfied_by_this_artifact=True),
            "must not claim scope satisfaction",
        ),
        (
            lambda d: d["stopgo_gate"].update(
                fail_action="keep iterating until the gate passes"
            ),
            "fail action must forbid iterating until positive",
        ),
        (
            lambda d: d["prior_adverse_evidence"][0].update(sha256="0" * 64),
            "prior evidence sha declaration drifted",
        ),
        (
            lambda d: d["prior_adverse_evidence"][1]["verdicts"].update(price_axis="OK"),
            "BROKEN verdicts must be carried verbatim",
        ),
        (lambda d: d.update(p12c_label_note=""), "P12C label-honesty note"),
        (lambda d: d["inference_unit"].update(primary="generated_row"), "inference unit"),
    ],
)
def test_menu_mutations_fail_closed(tmp_path, mutation, expected_error):
    module = _module()
    menus = json.loads(MENUS.read_text(encoding="utf-8"))
    mutation(menus)
    report = module.audit(_write_menus(tmp_path, menus))
    assert report["status"] == "FAIL"
    assert any(expected_error in error for error in report["errors"]), report["errors"]


@pytest.mark.parametrize(
    ("mutation", "expected_error"),
    [
        (lambda d: d.update(active_terminal="MUTANT"), "V4 active terminal"),
        (lambda d: d.update(active_claim_leaf={}), "active claim leaf differs"),
        (lambda d: d.update(historical_boundary_leaf={}), "historical boundary leaf"),
        (lambda d: d.update(paper_level_outcome="SUPPORTED_EVERYWHERE"), "paper-level outcome"),
        (
            lambda d: d.update(top_tier_submission_allowed=True),
            "top-tier submission gate must remain false",
        ),
        (
            lambda d: d["evidence_bindings"].pop("p12b_result_v1_1"),
            "weakened or changed inherited binding",
        ),
        (
            lambda d: d["evidence_bindings"].pop("robustness_result_receipt"),
            "missing inherited prior-evidence binding",
        ),
        (
            lambda d: d["forbidden_promotions"].remove("NATURALISTIC_AGENT_SUPERIORITY"),
            "V5 dropped a forbidden promotion",
        ),
        (
            lambda d: d["stopgo_campaign_leaf"].update(
                authority="EXECUTED_POSITIVE"
            ),
            "wrong stop/go authority class",
        ),
        (
            lambda d: d["stopgo_campaign_leaf"].update(results_exist=True),
            "stop/go leaf claims results",
        ),
        (
            lambda d: d["stopgo_campaign_leaf"].update(issue_1086_label_note=""),
            "missing the P12C no-artifact note",
        ),
        (
            lambda d: d["stopgo_campaign_leaf"]["binding_prior_terminals"].pop(),
            "stop/go leaf missing prior terminal",
        ),
        (
            lambda d: d["evidence_bindings"]["stopgo_menus_json"].update(sha256="0" * 64),
            "stop/go binding sha mismatch",
        ),
    ],
)
def test_authority_mutations_fail_closed(tmp_path, mutation, expected_error):
    module = _module()
    authority = json.loads(AUTHORITY_V5.read_text(encoding="utf-8"))
    mutation(authority)
    report = module.audit(module.MENUS, _write_authority(tmp_path, authority), check_package=False)
    assert report["status"] == "FAIL"
    assert any(expected_error in error for error in report["errors"]), report["errors"]
