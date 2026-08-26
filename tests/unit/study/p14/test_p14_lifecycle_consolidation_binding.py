"""P14 manuscript integration of P14D and the D7 consolidation scope."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PAPER = ROOT / "papers/orion-24-orion-rse"
P13_PAPER = ROOT / "papers/orion-23-responsibility-carrying-state"
SCOPE_BINDING = P13_PAPER / "P13_P14_CONSOLIDATION_SCOPE_BINDING_V1.json"
GOLD_RULE = P13_PAPER / "P13_P14_LIFECYCLE_GOLD_DERIVATION_RULE_V1.md"


def test_manuscript_integrates_the_blocked_p14d_status() -> None:
    manuscript = (PAPER / "MANUSCRIPT.md").read_text(encoding="utf-8")
    assert "### P14D — frozen acquisition contract; preflight blocked" in manuscript
    assert "P14D_EXTERNAL_ACQUISITION_BLOCKED" in manuscript
    assert "execution_authorized=false" in manuscript
    assert "P14C_SPECIFICATION_SEPARATED_GOVERNANCE_CONFORMANCE_SUPPORTED" in manuscript


def test_manuscript_carries_the_d7_cannot_check_scope_bound() -> None:
    manuscript = (PAPER / "MANUSCRIPT.md").read_text(encoding="utf-8")
    assert "### Scope binding — consolidated lifecycle-contract safety" in manuscript
    assert "two independent experts plus" in manuscript
    assert "CANNOT_CHECK" in manuscript
    assert "not** a separate paper at the 75+" in manuscript
    assert "P13_P14_CONSOLIDATION_SCOPE_BINDING_V1.json" in manuscript
    assert "P13_P14_LIFECYCLE_GOLD_DERIVATION_RULE_V1.md" in manuscript


def test_ledger_binds_the_integration_and_the_open_campaign() -> None:
    ledger = (PAPER / "CLAIM_EVIDENCE_LEDGER.md").read_text(encoding="utf-8")
    assert "P14D_EXTERNAL_ACQUISITION_BLOCKED" in ledger
    assert "SUPPORTED / BINDING" in ledger
    assert "CANNOT_CHECK / CONSOLIDATED D7" in ledger
    assert "30–50 pinned repositories from >=5 unrelated organizations remains OPEN" in ledger


def test_scope_binding_binds_d7_and_the_gold_rule_by_hash() -> None:
    binding = json.loads(SCOPE_BINDING.read_text(encoding="utf-8"))
    assert binding["decision_id"] == "D7"
    assert binding["papers"] == ["P13", "P14"]
    assert binding["p14_separate_75_paper"] is False
    assert binding["broader_claims_status"] == "CANNOT_CHECK"
    assert binding["broader_claims_require"] == ["two independent experts", "tie-break/custodian"]
    disposition = ROOT / binding["source_disposition_artifact"]
    assert binding["source_disposition_sha256"] == sha256(disposition.read_bytes()).hexdigest()
    assert binding["gold_derivation_rule_sha256"] == sha256(GOLD_RULE.read_bytes()).hexdigest()


def test_gold_rule_only_admits_objective_facts_and_never_orion_as_subject() -> None:
    rule = GOLD_RULE.read_text(encoding="utf-8")
    assert "PROSPECTIVE_PROTOCOL_RULE" in rule
    for fact in (
        "object/hash existence",
        "ancestry",
        "tag/signature",
        "test exit",
        "timestamp order",
    ):
        assert fact in rule
    assert "**never** be used as an external subject" in rule
    assert "30–50 pinned repositories" in rule
    assert "OPEN" in rule
