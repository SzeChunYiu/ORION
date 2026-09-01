#!/usr/bin/env python3
"""Create one checksum-closed Tier-B dual-route package from a verified base.

This is a publication adapter. It never changes scientific authority and it
fails closed when the declared authority or closure files are absent.
"""
from __future__ import annotations
import argparse, hashlib, json, shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
SKILL={
  "repository":"https://github.com/SzeChunYiu/academic-paper-skills",
  "revision":"488fc5310b84e578431f4a9a176d55bf9a3f0b99",
  "academic_paper_pipeline_version":"1.21.0",
  "academic_writing_version":"2.8.0",
  "nature_polishing_version":"7.5.0",
  "nature_reviewer_version":"3.5.0",
}
DATE="2026-09-01"

def sha(path:Path)->str:
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

def main()->int:
 ap=argparse.ArgumentParser()
 ap.add_argument('--paper-dir',required=True)
 ap.add_argument('--paper-id',required=True)
 ap.add_argument('--authority',required=True)
 ap.add_argument('--terminal',required=True)
 ap.add_argument('--status',default='TIER_B_PACKAGE_COMPLETE__PORTAL_ACTIONS_ONLY')
 ap.add_argument('--merged-id',action='append',default=[])
 ap.add_argument('--base',default='submission/publication-ready-20260831')
 ap.add_argument('--dest',default='submission/tier-b-final-20260901')
 ap.add_argument('--closure-file',action='append',default=[])
 a=ap.parse_args()
 paper=ROOT/'papers'/a.paper_dir
 base=paper/a.base; dest=paper/a.dest; authority=paper/a.authority
 if not base.is_dir() or not (base/'PACKAGE_MANIFEST.json').is_file(): raise SystemExit(f'missing base package: {base}')
 if not authority.is_file(): raise SystemExit(f'missing authority: {authority}')
 if dest.exists(): shutil.rmtree(dest)
 shutil.copytree(base,dest,symlinks=True)
 # Old package manifests are historical inputs, not nested authority.
 for rel in a.closure_file:
  src=paper/rel
  if not src.is_file(): raise SystemExit(f'missing closure file: {src}')
  shutil.copy2(src,dest/src.name)
 old=json.loads((base/'PACKAGE_MANIFEST.json').read_text())
 (dest/'README.md').write_text(
  f"# {a.paper_id} Tier-B final dual-route package\n\n"
  f"This is the current bounded arXiv/journal filing package, closed on {DATE} "
  "under academic-paper-pipeline v1.21.0. Scientific authority remains with "
  f"`{a.authority}`. The package changes no adverse, null, retracted or "
  "`CANNOT_CHECK` terminal. Portal identifiers and author-controlled filing "
  "choices remain outside repository authority.\n"
 )
 (dest/'SKILLS_APPLIED.md').write_text(
  "# Academic-paper skill application\n\n"
  "`skills-applied: academic-paper-pipeline@1.21.0, academic-writing@2.8.0, "
  "nature-polishing@7.5.0, nature-reviewer@3.5.0, paper-existence-scientific-mass-gate, "
  "atomic-claim-verification, manuscript-element-justification, publication-release-integrity`\n\n"
  "Skill authority: `SzeChunYiu/academic-paper-skills@488fc5310b84e578431f4a9a176d55bf9a3f0b99`. "
  "The pass is bounded to already-earned science and does not infer venue acceptance or external authority.\n"
 )
 old['schema']='ORION.tier-b-dual-submission-package.v1'
 old['date']=DATE
 old['paper']=a.paper_id
 old['merged_historical_ids']=a.merged_id
 old['academic_paper_skills']=SKILL
 old['active_authority']=str(authority.relative_to(ROOT))
 old['active_authority_sha256']=sha(authority)
 old['status']=a.status
 old['terminal']=a.terminal
 old['supersedes']=str(base.relative_to(ROOT))
 old['scientific_authority_delta']='NONE__PORTFOLIO_MERGER_AND_PUBLICATION_CLOSURE_ONLY'
 # payload is computed after all release files except manifest/checksums are final.
 old['payload']={}
 for p in sorted(dest.rglob('*')):
  if p.is_file() and p.name not in {'PACKAGE_MANIFEST.json','SHA256SUMS'}:
   rel=p.relative_to(dest).as_posix(); old['payload'][rel]={'bytes':p.stat().st_size,'sha256':sha(p)}
 (dest/'PACKAGE_MANIFEST.json').write_text(json.dumps(old,indent=2,sort_keys=True)+'\n')
 rows=[]
 for p in sorted(dest.rglob('*')):
  if p.is_file() and p.name!='SHA256SUMS': rows.append(f"{sha(p)}  {p.relative_to(dest).as_posix()}")
 (dest/'SHA256SUMS').write_text('\n'.join(rows)+'\n')
 print(dest.relative_to(ROOT))
 return 0
if __name__=='__main__': raise SystemExit(main())
