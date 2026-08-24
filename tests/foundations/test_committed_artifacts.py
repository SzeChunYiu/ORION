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


def test_p1_rr1_protected_paths_are_absent() -> None:
    protected = (
        "development/"
        "p1-scienceagentbench-protected-rr1-one-tuple-finalizer-freeze-v1-2026-08-24/"
    )
    paths = {
        str(path.relative_to(ROOT))
        for path in ROOT.rglob("*")
        if path.is_file() and ".pytest_cache" not in path.parts and "__pycache__" not in path.parts
    }
    assert not any(path.startswith(protected) for path in paths)
    audit = (RESEARCH / "STARTUP_AUDIT.md").read_text()
    assert "PR #1218" in audit and "5b6976ed" in audit and "NO-GO" in audit
