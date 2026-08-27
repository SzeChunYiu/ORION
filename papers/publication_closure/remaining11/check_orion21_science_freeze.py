#!/usr/bin/env python3
"""Fail-closed bounded science-freeze gate for ORION-21.

This gate freezes only the evidence-backed width-conditioned controlled result.
It deliberately preserves the ten-responsibility family-scale negative and does
not grant top-tier, real-system, journal, peer-review, or submission authority.
"""
from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
P = ROOT / "papers/orion-21-state-as-computation"
AUTH = P / "P11_ACTIVE_CLAIM_AUTHORITY_V2.json"
READY = P / "PEER_REVIEW_READINESS.md"
MANUSCRIPT = P / "MANUSCRIPT.md"
RECEIPT = ROOT / "papers/publication_closure/receipts/remaining11/ORION-21_SCIENCE_FREEZE_V1.json"
TERMINAL = "ORION_21_BOUNDED_SCIENCE_FROZEN__TOP_TIER_PROMOTION_PENDING"


def sha256(path: Path) -> str:
    h = hashlib.sha256(); h.update(path.read_bytes()); return h.hexdigest()


def require(ok: bool, msg: str) -> None:
    if not ok: raise AssertionError(msg)


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


def main() -> int:
    authority = json.loads(AUTH.read_text())
    require(authority["schema"] == "ORION.P11.ActiveClaimAuthority.v2", "wrong active authority schema")
    require(authority["active_terminal"] == "P11_WIDTH_CONDITIONED_AUTHORITY_SUPPORTED", "wrong active terminal")
    require(authority["paper_level_outcome"] == "SUPPORTED_WITH_EXPLICIT_WIDTH_AND_RESPONSIBILITY_BOUNDARIES", "wrong paper outcome")
    require(authority["promotion_allowed"] is True, "bounded promotion not allowed")

    leaf = authority["active_claim_leaf"]
    require(leaf["status"] == "SUPPORTED_REPLICATED", "active claim is not replicated")
    require(leaf["terminal"] == "P11I_HIGH_WIDTH_ADVANTAGE_REPLICATED_WIDE_PANEL", "wrong positive leaf")
    require(leaf["scope"]["prespecified_seed_x_geometry_cells"] == 9, "wrong replicated cell denominator")

    neg = authority["adverse_query_family_leaf"]
    require(neg["authority"] == "BINDING_NEGATIVE_BOUNDARY", "family negative is not binding")
    require(neg["terminal"] == "P11_QUERY_FAMILY_PHASE_V1_GATE_NOT_MET", "negative terminal drift")
    require(neg["observed_support_counts"] == {"KNN": 5, "LINEAR": 3, "RBF": 5, "responsibilities": 10}, "negative counts drift")
    require(neg["retuned"] is False, "negative was retuned")

    forbidden = set(authority["forbidden_promotions"])
    require({"UNCONDITIONAL_COMPILED_STATE_ADVANTAGE", "FAMILY_SCALE_COMPILATION_SUPPORT_ON_DIGITS", "REAL_SYSTEM_SUPERIORITY"} <= forbidden, "forbidden promotion boundary incomplete")

    checked = []
    for name, row in authority["evidence_bindings"].items():
        path = ROOT / row["artifact"]
        require(path.is_file(), f"missing evidence binding: {name}: {path}")
        observed = sha256(path)
        require(observed == row["sha256"], f"evidence digest drift: {name}: {observed} != {row['sha256']}")
        checked.append({"name": name, "path": str(path.relative_to(ROOT)), "sha256": observed})

    ready = READY.read_text()
    require("READY_FOR_EXTERNAL_REVIEW_AS_CONTROLLED_THEORY/SYSTEMS_SUPERIORITY_RESULT" in ready, "bounded readiness terminal missing")
    require("Not authorized: cross-domain or real-agent superiority" in ready, "real-agent nonclaim missing")
    require("LINEAR 3/10" in ready and "RBF 5/10" in ready and "KNN 5/10" in ready, "negative result not reader-visible")

    manuscript = MANUSCRIPT.read_text()
    for token in ("width", "responsibility", "negative", "CANNOT_CHECK"):
        require(token.lower() in manuscript.lower(), f"manuscript missing bounded-science token: {token}")

    receipt = {
        "schema": "ORION.Remaining11.ScienceFreeze.v1",
        "paper_id": "ORION-21",
        "title": "State as Computation",
        "date": "2026-08-27",
        "subject_commit": git("rev-parse", "HEAD"),
        "active_authority": str(AUTH.relative_to(ROOT)),
        "active_authority_sha256": sha256(AUTH),
        "positive_terminal": leaf["terminal"],
        "negative_terminal": neg["terminal"],
        "negative_support_counts": neg["observed_support_counts"],
        "evidence_bindings": checked,
        "terminal": TERMINAL,
        "science_frozen": True,
        "top_tier_ready": False,
        "journal_authority": False,
        "submission_authority": False,
        "external_peer_review_claimed": False,
        "remaining_top_tier_work": [
            "learned non-oracle compiler",
            "full end-to-end compiler accounting in a real system",
            "matched-cost smaller-real-reasoner versus larger-universal-reasoner replication"
        ],
        "boundary": "Freeze applies only to the controlled width-conditioned theory/systems result; the ten-responsibility family-scale claim remains a binding negative and real-system superiority is not authorized."
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(TERMINAL)
    return 0


if __name__ == "__main__":
    try: raise SystemExit(main())
    except AssertionError as exc:
        print(f"ORION_21_SCIENCE_FREEZE=FAIL: {exc}", file=sys.stderr)
        raise SystemExit(2)
