#!/usr/bin/env python3
"""Fail-closed current-version science/content freeze for ORION-01."""
from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
P = ROOT / "papers/orion-01-certificate-realization"
STATUS = ROOT / "research/orion-01-05-convergence-v1/SCIENCE_STATUS_V1.json"
A = P / "theory-A-CLAIM_LEDGER_R2.md"
B = P / "theory-B-CLAIM_LEDGER_R2.md"
MA = P / "theory-A-MANUSCRIPT_V2.md"
MB = P / "theory-B-MANUSCRIPT_V2.md"
OUT = ROOT / "papers/publication_closure/receipts/remaining11/ORION-01_SCIENCE_CONTENT_FREEZE_V1.json"
TERMINAL = "ORION_01_EARNED_CERTIFICATE_REGISTRY_SCIENCE_AND_CONTENT_FROZEN"

def req(x: bool, m: str) -> None:
    if not x: raise AssertionError(m)
def sha(p: Path) -> str: return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*a: str) -> str: return subprocess.check_output(["git","-C",str(ROOT),*a],text=True).strip()

def main() -> int:
    s=json.loads(STATUS.read_text())
    req(s["schema"]=="ORION.ORION0105.ScienceStatus.v1","convergence schema")
    p=s["papers"]["ORION-01"]
    req(p["title"]=="Certificate Realization","identity")
    req(p["evidence_status"]["pending_candidates"]==[],"unexpected pending candidate")
    expected_a=["A2-C1","A2-C2","A2-C3","A2-C4","A2-C5"]
    expected_b=["B2-C1","B2-C2","B2-C3","B2-C4","B2-C5","B2-C6"]
    req(p["claim_ledgers"][0]["claim_dispositions"]["established_at_stated_ceiling"]==expected_a,"A established claims")
    req(p["claim_ledgers"][1]["claim_dispositions"]["established_at_stated_ceiling"]==expected_b,"B established claims")
    req(p["claim_ledgers"][0]["sha256"]==sha(A),"A ledger digest")
    req(p["claim_ledgers"][1]["sha256"]==sha(B),"B ledger digest")
    req(p["authority"]=={
      "production_authority_established":False,
      "external_independence_established":False,
      "novelty_authority_established":False,
      "journal_authority_established":False,
      "submission_authorized":False,
    },"authority boundary")
    records={r["value"]:r for r in p["evidence_status"]["preserved_records"]}
    req("AB_REGISTRY_NONIDENTIFIABILITY_R12_PASS" in records,"registry theorem terminal")
    req("FINITE_PRODUCTION_REALIZATION_CERTIFICATE_REJECTED" in records,"production rejection terminal")
    req("AB_PR1469_PRODUCTION_TRANSFER_NOT_ESTABLISHED" in records,"production audit terminal")
    req(p["evidence_status"]["convergence_summary"]["label"]=="ORION-01_PRODUCTION_TRANSFER_NOT_ESTABLISHED__SCIENCE_OPEN","convergence summary")
    # Current paper identity retains both A/B cuts under one canonical ORION-01 directory.
    req(MA.is_file() and MB.is_file(),"retained manuscript cuts")
    for text in (MA.read_text(),MB.read_text()):
        low=text.lower(); req("physical" in low and ("not" in low or "no " in low),"hardware nonclaim not reader-visible")
    paper_dir="papers/orion-01-certificate-realization"
    tree=git("rev-parse",f"HEAD:{paper_dir}")
    receipt={
      "schema":"ORION.PaperScienceContentFreeze.v1","paper_id":"ORION-01","title":"Certificate Realization","date":"2026-08-27",
      "subject_commit":git("rev-parse","HEAD"),"paper_directory":paper_dir,"paper_tree_oid":tree,
      "science_frozen":True,"paper_content_frozen":True,"successor_required_for_future_science":True,
      "terminal":TERMINAL,"top_tier_ready":False,"journal_authority":False,"submission_authority":False,"external_peer_review_claimed":False,
      "established_claim_ids":expected_a+expected_b,
      "claim_ledgers":[{"path":str(A.relative_to(ROOT)),"sha256":sha(A)},{"path":str(B.relative_to(ROOT)),"sha256":sha(B)}],
      "manuscript_cuts":[{"path":str(MA.relative_to(ROOT)),"sha256":sha(MA)},{"path":str(MB.relative_to(ROOT)),"sha256":sha(MB)}],
      "positive_terminal":"AB_REGISTRY_NONIDENTIFIABILITY_R12_PASS",
      "adverse_terminal":"FINITE_PRODUCTION_REALIZATION_CERTIFICATE_REJECTED",
      "production_transfer_disposition":"AB_PR1469_PRODUCTION_TRANSFER_NOT_ESTABLISHED",
      "successor_only_work":p["open_science_gates"],
      "boundary":"The current paper freezes the abstract certificate, terminal-complexity and registry-nonidentifiability results at their stated finite-language ceilings. Production-registry completeness, production transfer, physical-resource value, external novelty and journal authority are not established; any such science requires a successor version."
    }
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(TERMINAL); return 0
if __name__=="__main__":
    try: raise SystemExit(main())
    except AssertionError as e:
        print(f"ORION_01_FINAL_FREEZE=FAIL: {e}",file=sys.stderr); raise SystemExit(2)
