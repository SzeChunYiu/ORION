#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path
REPO=Path(__file__).resolve().parents[2]; A=REPO/'artifacts'
AN=REPO/'research/extensions/orion-qg/qg20_recovery_v5_n5_collision.py'
VE=REPO/'development/orion-qg-regime-geometry/qg20_recovery_v5_n5_verify.py'
SEL=A/'orion-qg-qg20-recovery-v5-n5-selection.json'; RES=A/'orion-qg-qg20-recovery-v5-n5.json'; VER=A/'orion-qg-qg20-recovery-v5-n5-verification.json'; DUAL=A/'orion-qg-qg20-recovery-v5-n5-dual.json'
SP='ORIONQG_QG20_RECOVERY_V5_N5_SELECTION='; RP='ORIONQG_QG20_RECOVERY_V5_N5='; VP='ORIONQG_QG20_RECOVERY_V5_N5_VERIFY='

def run(path, allow=False):
    p=subprocess.run([sys.executable,str(path)],cwd=REPO,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
    if p.returncode not in ({0,2} if allow else {0}): raise RuntimeError(f'{path.name} instrument failure {p.returncode}: {p.stdout!r} {p.stderr!r}')
    return p

def tok(out,prefix):
    hits=[(i,l) for i,l in enumerate(out.splitlines()) if l.startswith(prefix)]
    if len(hits)!=1: raise RuntimeError(f'expected one {prefix}, got {len(hits)}')
    i,l=hits[0]; return i,json.loads(l[len(prefix):])

def main():
    A.mkdir(parents=True,exist_ok=True)
    for p in (SEL,RES,VER,DUAL): p.unlink(missing_ok=True)
    first=run(AN); si,st=tok(first.stdout,SP); ri,_=tok(first.stdout,RP)
    if si>=ri or st.get('exact_labels_accessed') is not False: raise RuntimeError('n5 selection was not sealed before exact labels')
    sb=SEL.read_bytes(); rb=RES.read_bytes(); sha=hashlib.sha256(rb).hexdigest()
    second=run(AN); tok(second.stdout,SP); tok(second.stdout,RP)
    replay=sb==SEL.read_bytes() and rb==RES.read_bytes()
    if not replay: raise RuntimeError('n5 analyzer replay mismatch')
    vr=run(VE,allow=True); _,vt=tok(vr.stdout,VP); vp=json.loads(VER.read_text())
    if vt.get('verification_digest')!=vp.get('verification_digest'): raise RuntimeError('n5 verifier token/artifact mismatch')
    src=json.loads(RES.read_text())
    terminal=src.get('terminal') if vp.get('decision')=='ACCEPT' else 'QG20_RECOVERY_V5_DUAL_DISAGREEMENT'
    dual={'schema':'orion-qg.qg20_recovery_v5_n5_dual.v1','terminal':terminal,'source_terminal':src.get('terminal'),'selection_digest':src.get('selection_digest'),'target_count':src.get('target_count'),'exact_label_count':src.get('exact_label_count'),'inexact_label_count':src.get('inexact_label_count'),'mixed_groups':src.get('mixed_groups'),'error_floor':src.get('error_floor'),'search':src.get('search'),'analyzer_replay_identical':replay,'analyzer_sha256':sha,'selection_before_labels':True,'representation_changed_after_v4':False,'verifier_decision':vp.get('decision'),'verifier_checks':vp.get('checks'),'verifier_digest':vp.get('verification_digest'),'all_n_authority':False,'novelty_authority':False}
    dual['dual_digest']=hashlib.sha256(json.dumps(dual,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    DUAL.write_text(json.dumps(dual,indent=2,sort_keys=True)+'\n')
    print('ORIONQG_QG20_RECOVERY_V5_N5_DUAL='+json.dumps(dual,sort_keys=True,separators=(',',':')))
    return 0
if __name__=='__main__': raise SystemExit(main())
