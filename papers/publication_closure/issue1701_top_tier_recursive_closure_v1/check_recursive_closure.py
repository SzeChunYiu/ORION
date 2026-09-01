#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ALLOWED_ROUTES = {
    "TOP_TIER_NEW_SUCCESSOR_REQUIRED__OLD_PROTOCOL_CLOSED",
    "TOP_TIER_PROMOTION_ACTIVE__EXTERNAL_DATA_REQUIRED",
    "TOP_TIER_PROMOTION_ACTIVE__THEORY_OR_EXACT_COMPUTE",
    "TOP_TIER_PROMOTION_ACTIVE__EXTERNAL_MODEL_REQUIRED",
    "TOP_TIER_PROMOTION_BLOCKED__EXTERNAL_AUTHORITY_REQUIRED",
    "TOP_TIER_PROMOTION_FAILED__SECOND_TIER_FALLBACK_JUSTIFIED",
    "TOP_TIER_CANDIDATE__INTEGRATION_AND_GOVERNANCE_REVIEW_REQUIRED",
}
REQUIRED_BOARD = {
    "formal_methods_and_theory",
    "experimental_design_and_statistics",
    "domain_and_novelty",
    "reproducibility_and_forensics",
    "top_tier_editor",
}
REQUIRED_PROTOCOL = {
    "state",
    "scientific_question",
    "design",
    "donors_and_controls",
    "authority_required",
    "positive_gate",
    "negative_or_cannot_check_terminal",
    "no_rescue_rule",
    "outcome_accessed",
}

def fail(msg: str) -> None:
    raise SystemExit(f"FAIL: {msg}")

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", type=Path, default=Path(__file__).with_name("PORTFOLIO_AUDIT.json"))
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--no-path-check", action="store_true")
    args = parser.parse_args()

    data = json.loads(args.audit.read_text(encoding="utf-8"))
    if data.get("scientific_authority_delta") != "NONE":
        fail("control packet may not create scientific authority")
    papers = data.get("papers", [])
    expected_ids = [f"ORION-{i:02d}" for i in range(1, 26)]
    ids = [p.get("paper_id") for p in papers]
    if ids != expected_ids:
        fail(f"paper IDs must be exactly ordered ORION-01..25, got {ids}")
    if len(set(ids)) != 25:
        fail("paper IDs are not unique")
    roles = {x.get("role") for x in data.get("expert_board", [])}
    if roles != REQUIRED_BOARD:
        fail(f"expert board mismatch: {roles}")

    for p in papers:
        pid = p["paper_id"]
        if p.get("top_tier_route") not in ALLOWED_ROUTES:
            fail(f"{pid}: invalid route")
        for key in (
            "current_terminal",
            "gap_type",
            "top_tier_rejection_hypothesis",
            "highest_information_move",
            "evidence_paths",
            "board_signoff",
        ):
            if not p.get(key):
                fail(f"{pid}: missing {key}")
        protocol = p.get("successor_protocol", {})
        if set(protocol) != REQUIRED_PROTOCOL:
            fail(f"{pid}: protocol keys mismatch")
        if protocol["outcome_accessed"] is not False:
            fail(f"{pid}: portfolio protocol must be outcome-free")
        for key in REQUIRED_PROTOCOL - {"outcome_accessed"}:
            if not protocol.get(key):
                fail(f"{pid}: empty protocol field {key}")
        if set(p["board_signoff"]) != REQUIRED_BOARD:
            fail(f"{pid}: incomplete board signoff")
        if "BLOCKED__EXTERNAL_AUTHORITY" in p["top_tier_route"]:
            auth = protocol["authority_required"].lower()
            if "independent" not in auth and "institution" not in auth:
                fail(f"{pid}: external-authority route lacks external authority")
        if p.get("old_identity_closed"):
            text = (protocol["no_rescue_rule"] + " " + p["highest_information_move"]).lower()
            if "rescue" not in text and "old" not in text and "same-identity" not in text:
                fail(f"{pid}: old identity closure lacks no-rescue language")
        if p["top_tier_route"].startswith("TOP_TIER_PROMOTION_ACTIVE") and protocol["state"] == "OLD_IDENTITY_CLOSED":
            fail(f"{pid}: active route cannot have closed protocol state")

    result_path = args.audit.with_name("RESULT.json")
    result = json.loads(result_path.read_text(encoding="utf-8"))
    if result.get("paper_count") != 25:
        fail("result paper count mismatch")
    if result.get("top_tier_ready_unconditional") != 0:
        fail("packet improperly grants unconditional top-tier readiness")
    if result.get("scientific_authority_delta") != "NONE":
        fail("result improperly grants authority")

    if not args.no_path_check:
        root = args.repo_root
        if root is None:
            root = args.audit.resolve().parents[3]
        for p in papers:
            for rel in p["evidence_paths"]:
                if not (root / rel).exists():
                    fail(f"{p['paper_id']}: missing evidence path {rel}")

    print("PASS: 25-paper top-tier gap map is complete, outcome-free, fail-closed, and authority-neutral")

if __name__ == "__main__":
    main()
