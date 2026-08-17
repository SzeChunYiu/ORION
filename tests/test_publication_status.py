from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "research" / "publication" / "scoreboard.py"
STATUS_PATH = ROOT / "research" / "publication" / "publication_status.json"
SCHEMA_PATH = ROOT / "research" / "publication" / "publication_status.schema.json"


def _load_module():
    spec = importlib.util.spec_from_file_location("publication_scoreboard", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_schema_is_json_schema():
    payload = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert payload["$id"] == "orion.publication-status.v1"
    assert payload["required"] == ["schema_version", "generated_from", "programme", "papers"]


def test_committed_scoreboard_matches_derived_artifacts():
    module = _load_module()
    payload = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
    assert payload["schema_version"] == module.SCHEMA_VERSION
    errors = module.validate_scoreboard(payload, ROOT)
    assert errors == []
    assert payload["programme"]["issue"] == 97
    assert payload["programme"]["close_allowed"] is False
    assert payload["programme"]["status"] == "BLOCKED"


def test_p4_is_peer_review_ready_and_others_are_blocked():
    module = _load_module()
    derived = module.derive_scoreboard(ROOT)
    by_id = {paper["paper_id"]: paper for paper in derived["papers"]}
    assert by_id["P4"]["status"] == "PEER_REVIEW_READY"
    assert by_id["P4"]["journal_readiness_terminal"] == "PEER_REVIEW_READY"
    assert by_id["P4"]["attestation_paths"]
    assert by_id["P4"]["claim_ledgers"]
    for paper_id in ("P1", "P2", "P3", "P5"):
        assert by_id[paper_id]["status"] == "BLOCKED", paper_id
        assert by_id[paper_id]["journal_readiness_terminal"] == "CANNOT_CHECK"
        assert by_id[paper_id]["missing_artifacts"]
    assert derived["programme"]["papers_peer_review_ready"] == ["P4"]
    assert derived["programme"]["close_allowed"] is False


def test_p1_closed_issue_does_not_invent_readiness():
    """#98 is closed on GitHub; artifacts on this tree still say CANNOT_CHECK."""
    module = _load_module()
    p1 = next(paper for paper in module.derive_scoreboard(ROOT)["papers"] if paper["paper_id"] == "P1")
    assert p1["status"] != "PEER_REVIEW_READY"
    assert p1["protocol_status"] == "EXECUTION_FROZEN"
    assert p1["outcome_accessed"] is False
    joined = "\n".join(p1["missing_artifacts"])
    assert "JOURNAL_READINESS.md" in joined
    assert "not PEER_REVIEW_READY" in joined
    assert "EXTERNAL NOT EXECUTED" in joined
    assert p1["attestation_paths"] == []


def test_p5_is_blocked_despite_claim_ledger_existing():
    module = _load_module()
    p5 = next(paper for paper in module.derive_scoreboard(ROOT)["papers"] if paper["paper_id"] == "P5")
    assert p5["status"] == "BLOCKED"
    assert p5["claim_ledgers"]
    assert p5["journal_readiness_terminal"] == "CANNOT_CHECK"
    assert any("not PEER_REVIEW_READY" in item for item in p5["missing_artifacts"])
    assert p5["protocol_status"] == "DESIGN_FROZEN"
    assert p5["unbound_execution_bindings"]


def test_forged_peer_review_ready_is_rejected():
    module = _load_module()
    payload = module.derive_scoreboard(ROOT)
    p1 = next(paper for paper in payload["papers"] if paper["paper_id"] == "P1")
    p1["status"] = "PEER_REVIEW_READY"
    p1["missing_artifacts"] = []
    payload["programme"]["status"] = "BLOCKED"
    payload["programme"]["close_allowed"] = False
    errors = module.validate_scoreboard(payload, ROOT)
    assert any("P1" in error and "PEER_REVIEW_READY" in error for error in errors)


def test_close_allowed_requires_all_five_ready():
    module = _load_module()
    payload = module.derive_scoreboard(ROOT)
    payload["programme"]["close_allowed"] = True
    errors = module.validate_scoreboard(payload, ROOT)
    assert any("close_allowed" in error for error in errors)


def test_terminal_parser_distinguishes_ready_from_cannot_check():
    module = _load_module()
    ready = "**Terminal:** `ORION-P4 = PEER_REVIEW_READY`\n"
    blocked = "**Current terminal:** `CANNOT_CHECK` for external superiority / not peer-review ready.\n"
    negated = "**Current terminal:** `CANNOT_CHECK`; **not** `PEER_REVIEW_READY`.\n"
    assert module.parse_journal_readiness_terminal(ready) == "PEER_REVIEW_READY"
    assert module.parse_journal_readiness_terminal(blocked) == "CANNOT_CHECK"
    assert module.parse_journal_readiness_terminal(negated) == "CANNOT_CHECK"


def test_cli_check_accepts_committed_snapshot(capsys: pytest.CaptureFixture[str]):
    module = _load_module()
    # The committed file must already match; --check is the CI gate.
    errors = module.validate_scoreboard(
        json.loads(STATUS_PATH.read_text(encoding="utf-8")),
        ROOT,
    )
    assert errors == []
    assert capsys.readouterr().out == ""
