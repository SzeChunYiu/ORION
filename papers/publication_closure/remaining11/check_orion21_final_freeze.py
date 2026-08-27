#!/usr/bin/env python3
"""Fail-closed final current-version science/content freeze for ORION-21."""
from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
P = ROOT / "papers/orion-21-state-as-computation"
AUTH = P / "P11_ACTIVE_CLAIM_AUTHORITY_V2.json"
READY = P / "PEER_REVIEW_READINESS.md"
MANUSCRIPT = P / "MANUSCRIPT.md"
OUT = ROOT / "papers/publication_closure/receipts/remaining11/ORION-21_SCIENCE_CONTENT_FREEZE_V1.json"
TERMINAL = "ORION_21_EARNED_SCIENCE_AND_PAPER_CONTENT_FROZEN"

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def req(ok: bool, msg: str) -> None:
    if not ok:
        raise AssertionError(msg)

def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()

def main() -> int:
    a = json.loads(AUTH.read_text())
    req(a["schema"] == "ORION.P11.ActiveClaimAuthority.v2", "authority schema")
    req(a["active_terminal"] == "P11_WIDTH_CONDITIONED_AUTHORITY_SUPPORTED", "active terminal")
    req(a["paper_level_outcome"] == "SUPPORTED_WITH_EXPLICIT_WIDTH_AND_RESPONSIBILITY_BOUNDARIES", "paper outcome")
    leaf = a["active_claim_leaf"]
    req(leaf["status"] == "SUPPORTED_REPLICATED", "positive leaf status")
    req(leaf["terminal"] == "P11I_HIGH_WIDTH_ADVANTAGE_REPLICATED_WIDE_PANEL", "positive terminal")
    req(leaf["scope"]["prespecified_seed_x_geometry_cells"] == 9, "positive denominator")
    neg = a["adverse_query_family_leaf"]
    req(neg["authority"] == "BINDING_NEGATIVE_BOUNDARY", "negative authority")
    req(neg["terminal"] == "P11_QUERY_FAMILY_PHASE_V1_GATE_NOT_MET", "negative terminal")
    req(neg["observed_support_counts"] == {"KNN":5,"LINEAR":3,"RBF":5,"responsibilities":10}, "negative counts")
    req(neg["retuned"] is False, "negative retuned")
    forbidden = set(a["forbidden_promotions"])
    req({"UNCONDITIONAL_COMPILED_STATE_ADVANTAGE","FAMILY_SCALE_COMPILATION_SUPPORT_ON_DIGITS","REAL_SYSTEM_SUPERIORITY"} <= forbidden, "forbidden promotions")

    bindings=[]
    for name,row in sorted(a["evidence_bindings"].items()):
        path=ROOT/row["artifact"]
        req(path.is_file(), f"missing binding {name}")
        observed=sha(path)
        req(observed == row["sha256"], f"digest drift {name}: {observed} != {row['sha256']}")
        bindings.append({"name":name,"path":row["artifact"],"sha256":observed})

    ready=READY.read_text()
    req("READY_FOR_EXTERNAL_REVIEW_AS_CONTROLLED_THEORY/SYSTEMS_SUPERIORITY_RESULT" in ready, "readiness terminal")
    req("Not authorized" in ready and "cross-domain or real-agent superiority" in ready, "real-agent boundary")
    req(all(x in ready for x in ("LINEAR 3/10","RBF 5/10","KNN 5/10")), "negative not reader-visible")
    req(MANUSCRIPT.is_file() and MANUSCRIPT.stat().st_size > 0, "manuscript missing")

    # The Git tree OID binds every tracked byte under the canonical paper directory.
    paper_dir="papers/orion-21-state-as-computation"
    tree_oid=git("rev-parse", f"HEAD:{paper_dir}")
    req(len(tree_oid)==40, "paper tree oid")
    receipt={
      "schema":"ORION.PaperScienceContentFreeze.v1",
      "paper_id":"ORION-21",
      "title":"State as Computation",
      "date":"2026-08-27",
      "subject_commit":git("rev-parse","HEAD"),
      "paper_directory":paper_dir,
      "paper_tree_oid":tree_oid,
      "manuscript":str(MANUSCRIPT.relative_to(ROOT)),
      "manuscript_sha256":sha(MANUSCRIPT),
      "peer_review_readiness":str(READY.relative_to(ROOT)),
      "peer_review_readiness_sha256":sha(READY),
      "active_authority":str(AUTH.relative_to(ROOT)),
      "active_authority_sha256":sha(AUTH),
      "positive_terminal":leaf["terminal"],
      "negative_terminal":neg["terminal"],
      "negative_support_counts":neg["observed_support_counts"],
      "evidence_bindings":bindings,
      "science_frozen":True,
      "paper_content_frozen":True,
      "successor_required_for_future_science":True,
      "top_tier_ready":False,
      "journal_authority":False,
      "submission_authority":False,
      "external_peer_review_claimed":False,
      "terminal":TERMINAL,
      "boundary":"Freeze is the current controlled width-conditioned result. The ten-responsibility family-scale result remains binding negative; real-system/cross-domain superiority is not authorized. Future science must be a successor version."
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(TERMINAL)
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"ORION_21_FINAL_FREEZE=FAIL: {exc}", file=sys.stderr)
        raise SystemExit(2)
