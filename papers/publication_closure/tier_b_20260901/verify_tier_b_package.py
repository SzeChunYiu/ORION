#!/usr/bin/env python3
"""Fail-closed exact-byte, source-build and claim-boundary audit for one Tier-B package."""
from __future__ import annotations
import argparse, collections, hashlib, json, os, re, shutil, subprocess, tempfile, zipfile
from pathlib import Path
import jsonschema
ROOT=Path(__file__).resolve().parents[3]
SKILL_ROOT=Path(__file__).resolve().parents[4]/'codex-tier-b-skill' # overridden below if absent
DEFAULT_SKILL=Path('/Users/billy/Documents/Codex/2026-08-31/prompt-1-orion-01-02-03/work/codex-tier-b-skill/skills/nature-shared')
EXPECTED_SKILL='488fc5310b84e578431f4a9a176d55bf9a3f0b99'
AUTHOR=('Sze Chun Yiu','Stockholm University','sze-chun.yiu@fysik.su.se')
PLACEHOLDERS=('TITLE TBD','PLACEHOLDER AUTHOR','Working framework draft','Replacement abstract for')

def sha(p:Path)->str:
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def run(*args,cwd=None)->str:
 env=os.environ.copy(); env['PATH']='/usr/local/texlive/2026basic/bin/universal-darwin:'+env.get('PATH','')
 p=subprocess.run(args,cwd=cwd,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 if p.returncode: raise RuntimeError(f"command failed ({p.returncode}): {' '.join(args)}\n{p.stdout[-5000:]}")
 return p.stdout
def text_pdf(p:Path)->str:
 return run('pdftotext','-layout',str(p),'-')
def pages(p:Path)->int:
 out=run('pdfinfo',str(p)); m=re.search(r'^Pages:\s+(\d+)',out,re.M)
 if not m: raise RuntimeError(f'cannot read page count: {p}')
 return int(m.group(1))
def normalized(s:str)->list[str]:
 return re.findall(r'[a-z0-9]+',s.lower())
def similarity(a:str,b:str)->float:
 ca,cb=collections.Counter(normalized(a)),collections.Counter(normalized(b)); den=sum(ca.values())+sum(cb.values())
 return 1.0 if den==0 else 2*sum((ca&cb).values())/den
def safe_zip(p:Path)->list[str]:
 out=[]
 with zipfile.ZipFile(p) as z:
  for i in z.infolist():
   q=Path(i.filename)
   if q.is_absolute() or '..' in q.parts: raise RuntimeError(f'unsafe zip member {p}: {i.filename}')
   out.append(i.filename)
 return out
def clean_build(source_zip:Path,release_pdf:Path)->dict:
 with tempfile.TemporaryDirectory(prefix='orion-tier-b-build-') as td:
  w=Path(td)
  with zipfile.ZipFile(source_zip) as z:z.extractall(w)
  if not (w/'main.tex').is_file(): raise RuntimeError(f'no top-level main.tex in {source_zip}')
  if 'quantumarticle' in (w/'main.tex').read_text(errors='replace'):
   out=run('tectonic','--keep-logs','main.tex',cwd=w)
  else:
   out=run('latexmk','-pdf','-interaction=nonstopmode','-halt-on-error','main.tex',cwd=w)
  built=w/'main.pdf'
  bt,rt=text_pdf(built),text_pdf(release_pdf)
  sim=similarity(bt,rt)
  if pages(built)!=pages(release_pdf) or sim<0.995: raise RuntimeError(f'clean build drift for {source_zip}: pages {pages(built)}/{pages(release_pdf)} similarity={sim:.6f}')
  logs='\n'.join(p.read_text(errors='replace') for p in w.rglob('*.log'))
  if re.search(r'(undefined references|Citation .* undefined|Reference .* undefined)',logs,re.I): raise RuntimeError(f'undefined reference/citation in {source_zip}')
  return {'release_pdf_sha256':sha(release_pdf),'source_zip_sha256':sha(source_zip),'pages':pages(release_pdf),'normalized_text_similarity':sim,'overfull_boxes':len(re.findall(r'Overfull \\[hv]box',logs)),'build_tail':out[-500:]}

def main()->int:
 ap=argparse.ArgumentParser(); ap.add_argument('package',type=Path); ap.add_argument('--report',type=Path); a=ap.parse_args()
 package=a.package.resolve(); manifest=json.loads((package/'PACKAGE_MANIFEST.json').read_text())
 checks=[]; actual={p.relative_to(package).as_posix() for p in package.rglob('*') if p.is_file()}
 payload=actual-{'PACKAGE_MANIFEST.json','SHA256SUMS'}
 if set(manifest['payload'])!=payload: raise RuntimeError('manifest payload file-set mismatch')
 for rel,rec in manifest['payload'].items():
  p=package/rel
  if sha(p)!=rec['sha256'] or p.stat().st_size!=rec['bytes']: raise RuntimeError(f'manifest mismatch {rel}')
 checks.append('manifest_payload_exact')
 sums={}
 for row in (package/'SHA256SUMS').read_text().splitlines():
  d,rel=row.split('  ',1); sums[rel]=d
 if set(sums)!=actual-{'SHA256SUMS'}: raise RuntimeError('SHA256SUMS file-set mismatch')
 for rel,d in sums.items():
  if sha(package/rel)!=d: raise RuntimeError(f'checksum mismatch {rel}')
 checks.append('sha256_closure')
 skill=manifest['academic_paper_skills']
 if skill['revision']!=EXPECTED_SKILL or skill['academic_paper_pipeline_version']!='1.21.0': raise RuntimeError('stale academic-paper skill authority')
 checks.append('academic_paper_pipeline_1_21')
 authority=ROOT/manifest['active_authority']
 if not authority.is_file() or sha(authority)!=manifest['active_authority_sha256']: raise RuntimeError('active authority binding mismatch')
 checks.append('active_authority_binding')
 ledger=package/'PAPER_EXISTENCE_SCIENTIFIC_MASS.json'
 shared=DEFAULT_SKILL
 schema=json.loads((shared/'analysis-contracts/paper-existence-scientific-mass.schema.json').read_text())
 data=json.loads(ledger.read_text()); jsonschema.validate(data,schema)
 gate=json.loads(run('python3',str(shared/'scripts/verify_paper_existence_scientific_mass.py'),str(ledger),'--json'))
 if gate['verdict']!='PASS': raise RuntimeError(f'paper-existence gate {gate}')
 checks.extend(['paper_existence_schema','paper_existence_gate_PASS'])
 for route in ('arxiv','journal'):
  safe_zip(package/route/'source.zip')
 safe_zip(package/'journal/review-materials.zip')
 artifact=package/'journal/artifact.zip'
 if artifact.is_file():
  safe_zip(artifact)
  checks.append('paper_specific_artifact_archive')
 checks.append('archive_path_safety')
 arx=text_pdf(package/'arxiv/manuscript.pdf'); jour=text_pdf(package/'journal/manuscript.pdf')
 if any(x.lower() in arx.lower() or x.lower() in jour.lower() for x in PLACEHOLDERS): raise RuntimeError('visible manuscript placeholder')
 review=manifest['journal']['review_model']
 if not all(x.lower() in arx.lower() for x in AUTHOR): raise RuntimeError('arXiv identity incomplete')
 if review=='double_blind':
  if any(x.lower() in jour.lower() for x in AUTHOR): raise RuntimeError('journal identity leak')
 else:
  if not all(x.lower() in jour.lower() for x in AUTHOR): raise RuntimeError('journal identity incomplete')
 route_sim=similarity(arx,jour)
 if route_sim<0.90: raise RuntimeError(f'route scientific text drift {route_sim:.6f}')
 checks.extend(['identity_partition','visible_placeholder_scan','route_science_similarity'])
 inv=json.loads((package/'ATOMIC_CLAIM_INVENTORY.json').read_text())
 retention=(package/'RESULT_RETENTION.md').read_text()
 for x in inv['retained_negative_null_open_cannot_check']:
  if x not in retention: raise RuntimeError(f'dropped adverse result: {x}')
 checks.append('adverse_null_cannot_check_retention')
 builds={route:clean_build(package/route/'source.zip',package/route/'manuscript.pdf') for route in ('arxiv','journal')}
 checks.extend(['fresh_clean_arxiv_build','fresh_clean_journal_build','source_pdf_text_binding','resolved_references'])
 report={'schema':'ORION.tier-b-package-verification.v1','paper':manifest['paper'],'terminal':manifest['terminal'],'status':'PASS','package':str(package.relative_to(ROOT)),'package_manifest_sha256':sha(package/'PACKAGE_MANIFEST.json'),'checks':checks,'route_science_similarity':route_sim,'builds':builds,'paper_existence_gate':gate,'visual_audit':'PENDING_SEPARATE_RENDER_INSPECTION'}
 if a.report:
  a.report.parent.mkdir(parents=True,exist_ok=True); a.report.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
 print(json.dumps(report,indent=2,sort_keys=True))
 return 0
if __name__=='__main__': raise SystemExit(main())
