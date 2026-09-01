from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACKET = ROOT / "papers/publication_closure/issue1701_top_tier_recursive_closure_v1"

def load(name: str):
    return json.loads((PACKET / name).read_text(encoding="utf-8"))

def test_all_25_have_atomic_top_tier_dispositions() -> None:
    audit = load("PORTFOLIO_AUDIT.json")
    papers = audit["papers"]
    assert [p["paper_id"] for p in papers] == [f"ORION-{i:02d}" for i in range(1, 26)]
    assert len({p["paper_slug"] for p in papers}) == 25
    assert all(p["top_tier_rejection_hypothesis"] for p in papers)
    assert all(p["highest_information_move"] for p in papers)

def test_protocol_readiness_never_promotes_science() -> None:
    audit = load("PORTFOLIO_AUDIT.json")
    result = load("RESULT.json")
    assert audit["scientific_authority_delta"] == "NONE"
    assert result["scientific_authority_delta"] == "NONE"
    assert result["top_tier_ready_unconditional"] == 0
    assert all(p["successor_protocol"]["outcome_accessed"] is False for p in audit["papers"])
    assert all(
        signoff == "NOT_TOP_TIER_READY_UNTIL_GATE_EARNED"
        for p in audit["papers"]
        for role, signoff in p["board_signoff"].items()
        if role == "top_tier_editor"
    )

def test_closed_identities_have_no_rescue_rule() -> None:
    audit = load("PORTFOLIO_AUDIT.json")
    closed = [p for p in audit["papers"] if p["old_identity_closed"]]
    assert {p["paper_id"] for p in closed} == {"ORION-01", "ORION-09", "ORION-11", "ORION-20", "ORION-21"}
    for p in closed:
        text = (p["highest_information_move"] + " " + p["successor_protocol"]["no_rescue_rule"]).lower()
        assert "old" in text or "rescue" in text or "same-identity" in text

def test_external_authority_is_not_self_certified() -> None:
    audit = load("PORTFOLIO_AUDIT.json")
    blocked = [
        p for p in audit["papers"]
        if p["top_tier_route"] == "TOP_TIER_PROMOTION_BLOCKED__EXTERNAL_AUTHORITY_REQUIRED"
    ]
    assert {p["paper_id"] for p in blocked} == {"ORION-18", "ORION-24"}
    for p in blocked:
        text = p["successor_protocol"]["authority_required"].lower()
        assert "independent" in text or "institution" in text
        assert p["irreducible_external_dependency"] is True

def test_adverse_ledger_preserves_each_record() -> None:
    rows = [
        json.loads(line)
        for line in (PACKET / "ADVERSE_AND_CANNOT_CHECK.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert rows
    assert all(row["preserved"] is True for row in rows)
    assert {"ORION-09", "ORION-18", "ORION-20", "ORION-21", "ORION-24"} <= {
        row["paper_id"] for row in rows
    }

def test_standalone_checker_passes_schema_without_repo_paths() -> None:
    spec = importlib.util.spec_from_file_location("closure_checker", PACKET / "check_recursive_closure.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
