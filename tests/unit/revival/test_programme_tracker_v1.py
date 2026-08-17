from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
REVIVAL = ROOT / "research" / "revival"
MODULE_PATH = REVIVAL / "tracker.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("revival_tracker", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _tracker():
    return json.loads((REVIVAL / "PROGRAMME_TRACKER_V1.json").read_text(encoding="utf-8"))


def _child(issue: int) -> dict:
    tracker = _tracker()
    return copy.deepcopy(next(item for item in tracker["children"] if item["issue"] == issue))


def test_committed_tree_is_scaffolding_only_and_valid() -> None:
    module = _load_module()
    report = module.validate_tree(REVIVAL)
    assert report["errors"] == []
    assert report["valid"] is True
    assert report["programme_status"] == "SCAFFOLDING_ONLY"
    assert report["scientific_children_complete"] == 0

    tracker = _tracker()
    assert tracker["claims_children_done"] is False
    assert tracker["scientific_children_complete"] == 0
    for child in tracker["children"]:
        assert child["current_state"] == "OPEN"
        assert child["scientific_terminal_reached"] is False
        assert child["verification_record_id"] is None
        assert child["cannot_check"], f"#{child['issue']} must list current CANNOT_CHECK items"
        assert child["next_discriminator"]


def test_committed_doctrine_and_novelty_are_constraints_not_claims() -> None:
    module = _load_module()
    doctrine = json.loads((REVIVAL / "CONSTITUTIONAL_DOCTRINE_V1.json").read_text(encoding="utf-8"))
    novelty = json.loads((REVIVAL / "NOVELTY_HYPOTHESES_V1.json").read_text(encoding="utf-8"))
    corrections = json.loads((REVIVAL / "CORRECTIONS_V1.json").read_text(encoding="utf-8"))
    assert module.validate_doctrine(doctrine) == []
    assert module.validate_novelty(novelty) == []
    assert module.validate_corrections(corrections) == []
    assert all(item["claimed_novelty"] is False for item in novelty["hypotheses"])
    assert corrections["facts"]["p4_v2"]["terminal"] == "PEER_REVIEW_READY"
    p1_power = corrections["facts"]["p1_power"]
    assert p1_power["h1_required_n"] == 385
    assert p1_power["h2_required_n"] == 2401
    assert p1_power["h1_and_h2_power_identical"] is False
    assert corrections["facts"]["p5_attribution"]["correct"] == "21/24"
    assert corrections["facts"]["post_outcome_margin_relaxation"] is False


def test_mechanism_supported_without_verification_record_is_illegal() -> None:
    module = _load_module()
    child = _child(278)
    child["current_state"] = "MECHANISM_SUPPORTED"
    child["scientific_terminal_reached"] = True
    child["verification_record_id"] = None
    errors = module.validate_child(child)
    assert any("verification_record_id" in item for item in errors)

    child = _child(278)
    child["current_state"] = "INDEPENDENT_VERIFICATION_IN_PROGRESS"
    child["next_discriminator"] = "verification receipt for P1 V2"
    with pytest.raises(module.TrackerError, match="verification_record_id"):
        module.apply_transition(child, "MECHANISM_SUPPORTED")


def test_open_to_mechanism_supported_is_illegal() -> None:
    module = _load_module()
    child = _child(278)
    with pytest.raises(module.TrackerError, match="illegal from OPEN"):
        module.apply_transition(
            child,
            "MECHANISM_SUPPORTED",
            verification_record_id="vr-fake",
        )


def test_protocol_frozen_before_discriminator_is_illegal() -> None:
    module = _load_module()
    child = _child(278)
    with pytest.raises(module.TrackerError, match="discriminator"):
        module.apply_transition(child, "PROTOCOL_FROZEN")


def test_positive_terminal_with_verification_record_is_legal_after_verification() -> None:
    module = _load_module()
    child = _child(278)
    child["current_state"] = "INDEPENDENT_VERIFICATION_IN_PROGRESS"
    child["next_discriminator"] = "independent rescoring of P1 V2 holdout"
    updated = module.apply_transition(
        child,
        "MECHANISM_SUPPORTED",
        verification_record_id="issue-283/records/p1-v2-placeholder",
    )
    assert updated["scientific_terminal_reached"] is True
    assert updated["verification_record_id"] == "issue-283/records/p1-v2-placeholder"
    assert module.validate_child(updated) == []


def test_tracker_rejects_claiming_children_done_while_open() -> None:
    module = _load_module()
    payload = _tracker()
    payload["claims_children_done"] = True
    payload["scientific_children_complete"] = 10
    payload["programme_status"] = "CLOSED"
    errors = module.validate_tracker(payload)
    assert any("must not claim children are done" in item for item in errors)
    assert any("scientific_children_complete must equal" in item for item in errors)
    assert any("cannot CLOSE" in item for item in errors)


def test_doctrine_rejects_margin_relaxation_flag() -> None:
    module = _load_module()
    doctrine = json.loads((REVIVAL / "CONSTITUTIONAL_DOCTRINE_V1.json").read_text(encoding="utf-8"))
    doctrine["checks"]["margin_relaxation_after_outcome_access"] = True
    errors = module.validate_doctrine(doctrine)
    assert any("margin_relaxation_after_outcome_access" in item for item in errors)


def test_novelty_rejects_claimed_novelty() -> None:
    module = _load_module()
    novelty = json.loads((REVIVAL / "NOVELTY_HYPOTHESES_V1.json").read_text(encoding="utf-8"))
    novelty["hypotheses"][0]["claimed_novelty"] = True
    novelty["hypotheses"][0]["status"] = "CLAIMED"
    errors = module.validate_novelty(novelty)
    assert any("claimed_novelty" in item for item in errors)


def test_cannot_check_requires_reasons() -> None:
    module = _load_module()
    child = _child(287)
    child["cannot_check"] = []
    with pytest.raises(module.TrackerError, match="CANNOT_CHECK requires"):
        module.apply_transition(child, "CANNOT_CHECK")
