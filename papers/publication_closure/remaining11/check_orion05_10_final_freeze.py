#!/usr/bin/env python3
"""Fail-closed whole-tree science/content freeze for canonical ORION-05..10.

The controlling science authority is Q_QG_PUBLICATION_READINESS_V3.md, which
separates scientific-content closure from package closure and explicitly says
not to open new science merely to improve acceptance odds.
"""
from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
READINESS = ROOT / "papers/Q_QG_PUBLICATION_READINESS_V3.md"
ALIASES = ROOT / "papers/PAPER_ALIASES.md"
OUTDIR = ROOT / "papers/publication_closure/receipts/remaining11"

PAPERS = {
    "ORION-05": {
        "legacy": "Q1",
        "title": "TARE Expressivity",
        "dir": "papers/orion-05-tare-expressivity",
        "manuscript": "MANUSCRIPT_V3_REFINED.md",
        "terminal": "Q1_CONTENT_READY__NO_NEW_SCIENCE_REQUIRED",
        "boundary": "Support-two TARE theorem/counterexamples and bounded evidence only; no support-three necessity, universal two-trade theorem, production-resource superiority, journal or submission authority.",
    },
    "ORION-06": {
        "legacy": "Q2",
        "title": "Recursive Recovery",
        "dir": "papers/orion-06-recursive-recovery",
        "manuscript": "MANUSCRIPT_V3.md",
        "terminal": "Q2_CONTENT_READY__DECLARED_51_RECEIPT_DENOMINATOR_BOUND__NO_NEW_SCIENCE_REQUIRED",
        "boundary": "Feasibility/auditability over the declared 51-receipt denominator; no autonomous productivity superiority or journal/submission authority.",
    },
    "ORION-07": {
        "legacy": "Q3",
        "title": "Dual Instrument",
        "dir": "papers/orion-07-dual-instrument",
        "manuscript": "MANUSCRIPT_V3.md",
        "terminal": "Q3_PROSPECTIVE_CASE_SERIES_COMPLETE__N3_VALID__AGREEMENT_NOT_VALIDATION_COUNTEREXAMPLE_OBSERVED__NO_RELIABILITY_GENERALIZATION",
        "boundary": "Exactly three valid frontier-question units; agreement is not diagnostic correctness; no kappa/reliability/generalized accuracy or journal/submission authority.",
    },
    "ORION-08": {
        "legacy": "Q4",
        "title": "Typed State",
        "dir": "papers/orion-08-typed-state",
        "manuscript": "MANUSCRIPT_V3.md",
        "terminal": "Q4_CONTENT_READY__NO_NEW_SCIENCE_REQUIRED",
        "boundary": "Exact-synthetic matched-information mechanism evidence only; no real-agent, cross-world pooled-statistic or universal responsibility-scoped superiority claim.",
    },
    "ORION-09": {
        "legacy": "QG1",
        "title": "Compilation Regime Geometry",
        "dir": "papers/orion-09-compilation-regime-geometry",
        "manuscript": "MANUSCRIPT_V3.md",
        "terminal": "QG1_CONTENT_READY_AFTER_POSTCUT_REFRESH__NO_NEW_SCIENCE_REQUIRED",
        "boundary": "Current compiler-family synthesis and exact support/certificate results only; no universal phase claim or journal/submission authority.",
    },
    "ORION-10": {
        "legacy": "QG2",
        "title": "Certified Static Forecasting",
        "dir": "papers/orion-10-certified-static-forecasting",
        "manuscript": "MANUSCRIPT_V3.md",
        "terminal": "QG2_CONTENT_READY__NO_NEW_SCIENCE_REQUIRED",
        "boundary": "Compiler-specific static forecasting/refutation result with exact counterexample; timing remains descriptive and no journal/submission authority is granted.",
    },
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def req(ok: bool, msg: str) -> None:
    if not ok:
        raise AssertionError(msg)


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


def main() -> int:
    readiness = READINESS.read_text(encoding="utf-8")
    aliases = ALIASES.read_text(encoding="utf-8")
    req("scientific-content closure" in readiness, "closure definition missing")
    req("CONTENT_READY" in readiness and "does **not** mean" in readiness, "content/package distinction missing")
    req("do not start another scientific lane merely to improve acceptance odds" in readiness, "science stop rule missing")
    req("PACKAGE_OPEN" in readiness, "package boundary missing")
    subject_commit = git("rev-parse", "HEAD")
    readiness_sha = sha(READINESS)
    alias_sha = sha(ALIASES)
    OUTDIR.mkdir(parents=True, exist_ok=True)

    for paper_id, cfg in PAPERS.items():
        req(f"old: {cfg['legacy']}" in aliases and f"new: {paper_id}" in aliases, f"alias mapping {paper_id}")
        req(cfg["terminal"] in readiness, f"science terminal {paper_id}")
        paper_dir = ROOT / cfg["dir"]
        manuscript = paper_dir / cfg["manuscript"]
        req(paper_dir.is_dir(), f"paper dir {paper_id}")
        req(manuscript.is_file(), f"final manuscript {paper_id}")
        tree_oid = git("rev-parse", f"HEAD:{cfg['dir']}")
        req(len(tree_oid) == 40, f"paper tree {paper_id}")
        receipt = {
            "schema": "ORION.PaperScienceContentFreeze.v1",
            "paper_id": paper_id,
            "legacy_science_id": cfg["legacy"],
            "title": cfg["title"],
            "date": "2026-08-27",
            "subject_commit": subject_commit,
            "paper_directory": cfg["dir"],
            "paper_tree_oid": tree_oid,
            "final_manuscript": str(manuscript.relative_to(ROOT)),
            "final_manuscript_sha256": sha(manuscript),
            "controlling_readiness": str(READINESS.relative_to(ROOT)),
            "controlling_readiness_sha256": readiness_sha,
            "alias_registry_sha256": alias_sha,
            "scientific_content_terminal": cfg["terminal"],
            "package_terminal": "PACKAGE_OPEN",
            "science_frozen": True,
            "paper_content_frozen": True,
            "successor_required_for_future_science": True,
            "top_tier_ready": False,
            "journal_authority": False,
            "submission_authority": False,
            "external_peer_review_claimed": False,
            "terminal": f"{paper_id.replace('-', '_')}_EARNED_SCIENCE_AND_PAPER_CONTENT_FROZEN",
            "boundary": cfg["boundary"],
            "reopen_rule": "Only reopen science for direct donor subsumption, falsification/material authority change, or a genuinely missing discriminating test; otherwise future changes are package/editorial or an explicit successor version.",
        }
        out = OUTDIR / f"{paper_id}_SCIENCE_CONTENT_FREEZE_V1.json"
        out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(receipt["terminal"])
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"ORION_05_10_FINAL_FREEZE=FAIL: {exc}", file=sys.stderr)
        raise SystemExit(2)
