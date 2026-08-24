import json
from pathlib import Path

from orion.foundations.cli import build_receipt
from orion.foundations.theorems import run_local_theorems


ROOT = Path(__file__).resolve().parents[2]
RESEARCH = ROOT / "research" / "orion-foundations-v2"


def test_compact_receipt_matches_executable_core() -> None:
    compact = json.loads((RESEARCH / "LOCAL_THEOREM_RECEIPT_V1.json").read_text())
    full = build_receipt(run_local_theorems())
    assert compact["canonical_core_sha256"] == full["canonical_core_sha256"]
    assert compact["summary"] == full["summary"]
    assert compact["theorem_ids"] == [row["theorem_id"] for row in full["theorems"]]
    assert compact["authority_delta"] == "NONE"
    assert compact["p1_rr1_coordination"] == "UNTOUCHED"


def test_p1_rr1_coordination_is_explicit_and_non_authorizing() -> None:
    compact = json.loads((RESEARCH / "LOCAL_THEOREM_RECEIPT_V1.json").read_text())
    audit = (RESEARCH / "STARTUP_AUDIT.md").read_text(encoding="utf-8")
    assert compact["p1_rr1_coordination"] == "UNTOUCHED"
    assert compact["authority_delta"] == "NONE"
    assert "PR #1218" in audit
    assert "5b6976ed" in audit
    assert "NO-GO" in audit
    assert "does not edit, merge, rebase, supersede, execute, or" in audit
