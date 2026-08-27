#!/usr/bin/env python3
"""Upgrade ORION-16's existing bounded science freeze to a whole-tree content freeze."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PAPER_DIR = "papers/orion-16-formal-epistemic-structures-and-mechanics"
P = ROOT / PAPER_DIR
SCIENCE = ROOT / "papers/publication_closure/receipts/remaining11/ORION-16_SCIENCE_FREEZE_V1.json"
CONTENT = P / "CONTENT_MANIFEST_V2.json"
CONTENT_SUMS = P / "content_binding_v2/SHA256SUMS"
CONTRACT = P / "evidence/local/P6_LOCAL_REPLAY_CONTRACT_V4.json"
OUT = ROOT / "papers/publication_closure/receipts/remaining11/ORION-16_SCIENCE_CONTENT_FREEZE_V1.json"
TERMINAL = "ORION_16_BOUNDED_SCIENCE_AND_PAPER_CONTENT_FROZEN"


def require(ok: bool, msg: str) -> None:
    if not ok:
        raise AssertionError(msg)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


def main() -> int:
    science = json.loads(SCIENCE.read_text(encoding="utf-8"))
    require(science["paper_id"] == "ORION-16", "wrong science receipt")
    require(science["science_frozen"] is True, "science not frozen")
    require(science["terminal"] == "ORION_16_BOUNDED_SCIENCE_FROZEN__REAL_SYSTEM_PROMOTION_PENDING", "science terminal drift")
    require(science["top_tier_ready"] is False and science["submission_authority"] is False, "authority promoted")
    result_path = ROOT / science["result_receipt"]
    require(result_path.is_file(), "science result receipt missing")
    require(git("rev-parse", f"HEAD:{science['result_receipt']}") == science["result_receipt_git_blob"], "science result blob drift")

    manifest = json.loads(CONTENT.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    contract_rows = {row["path"]: row["sha256"] for row in contract["execution_inputs"] + contract["historical_predecessors"]}
    require(len(contract_rows) == len(contract["execution_inputs"]) + len(contract["historical_predecessors"]), "duplicate contract path")
    for path, expected in contract_rows.items():
        bound = ROOT / path
        require(bound.is_file(), f"missing contract input: {path}")
        require(sha256(bound) == expected, f"contract digest drift: {path}")

    manifest_rows = {row["path"]: row["sha256"] for row in manifest["bound_files"]}
    contract_rel = str(CONTRACT.relative_to(ROOT))
    require(manifest_rows.get(contract_rel) == sha256(CONTRACT), "content manifest does not bind repaired V4 contract")
    for path, expected in manifest_rows.items():
        bound = ROOT / path
        require(bound.is_file(), f"missing content-bound file: {path}")
        require(sha256(bound) == expected, f"content manifest digest drift: {path}")

    sum_lines = [line.strip() for line in CONTENT_SUMS.read_text(encoding="utf-8").splitlines() if line.strip()]
    require(sum_lines == [f"{sha256(CONTENT)}  {CONTENT.relative_to(ROOT)}"], "content-binding SHA256SUMS drift")

    tree_oid = git("rev-parse", f"HEAD:{PAPER_DIR}")
    receipt = {
        "schema": "ORION.PaperScienceContentFreeze.v1",
        "paper_id": "ORION-16",
        "title": science["title"],
        "date": "2026-08-27",
        "subject_commit": git("rev-parse", "HEAD"),
        "paper_directory": PAPER_DIR,
        "paper_tree_oid": tree_oid,
        "science_receipt": str(SCIENCE.relative_to(ROOT)),
        "science_receipt_sha256": sha256(SCIENCE),
        "science_terminal": science["terminal"],
        "result_receipt": science["result_receipt"],
        "result_receipt_git_blob": science["result_receipt_git_blob"],
        "content_manifest": str(CONTENT.relative_to(ROOT)),
        "content_manifest_sha256": sha256(CONTENT),
        "local_replay_contract": contract_rel,
        "local_replay_contract_sha256": sha256(CONTRACT),
        "claude_r0_binding_repair_integrated": True,
        "science_frozen": True,
        "paper_content_frozen": True,
        "successor_required_for_future_science": True,
        "top_tier_ready": False,
        "journal_authority": False,
        "submission_authority": False,
        "external_peer_review_claimed": False,
        "terminal": TERMINAL,
        "boundary": science["boundary"],
        "successor_only_work": science["remaining_top_tier_work"],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(TERMINAL)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"ORION_16_FINAL_CONTENT_FREEZE=FAIL: {exc}", file=sys.stderr)
        raise SystemExit(2)
