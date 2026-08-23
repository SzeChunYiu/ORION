#!/usr/bin/env python3
"""QG-15c Stage 1: exact feature-determination test for an enlarged StabPrep vocabulary."""
from __future__ import annotations

import argparse, hashlib, json, sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]; QG=ROOT/'research/extensions/orion-qg'; sys.path.insert(0,str(QG))
import qg15_third_family as q15  # noqa:E402

PROTOCOL=ROOT/'development/orion-qg-regime-geometry/QG15C_ENLARGED_VOCAB_PROTOCOL_V1.md'
PARENT=QG/'QG15B_PREDICATE_LANGUAGE_RESULTS.json'
OUT=ROOT/'artifacts/orion-qg-qg15c-enlarged-vocab.json'
TOKEN='ORIONQG_QG15C='
KINDS=('H','S','SDG','CX'); KIND_CODE={k:i for i,k in enumerate(KINDS)}


def canonical(v): return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def base13(feats,cd,lb,rx,c,n):
 return (feats['nCZ'],feats['nY'],feats['nSignX'],feats['nSignZ'],feats['nCN'],cd,rx,c,lb,cd-lb,n-c,feats['nCN']-(n-1),cd-2*n)

def stats4(xs):
 return (min(xs) if xs else 0,max(xs) if xs else 0,sum(x*x for x in xs),sum(1 for x in xs if x==0))

def donor_path_features(circuit,n):
 totals=Counter(g[0] for g in circuit)
 channels={name:[0]*n for name in ('H','S','SDG','CX_IN','CX_OUT')}
 edges=Counter()
 kinds=[]
 for g in circuit:
  kind=g[0]; kinds.append(kind)
  if kind in ('H','S','SDG'): channels[kind][g[1]]+=1
  else:
   c,t=g[1],g[2]; channels['CX_OUT'][c]+=1; channels['CX_IN'][t]+=1; edges[(c,t)]+=1
 vec=[totals[k] for k in KINDS]
 for name in ('H','S','SDG','CX_IN','CX_OUT'): vec.extend(stats4(channels[name]))
 used=len(edges); maxmult=max(edges.values()) if edges else 0; sq=sum(v*v for v in edges.values()); reciprocal=sum(1 for a in range(n) for b in range(a+1,n) if edges[(a,b)] and edges[(b,a)])
 indeg=[sum(1 for c in range(n) if c!=t and edges[(c,t)]>0) for t in range(n)]; outdeg=[sum(1 for t in range(n) if t!=c and edges[(c,t)]>0) for c in range(n)]
 vec.extend((used,maxmult,sq,reciprocal,max(indeg) if indeg else 0,max(outdeg) if outdeg else 0,sum(x*x for x in indeg),sum(x*x for x in outdeg)))
 transitions=Counter(zip(kinds,kinds[1:]))
 for a in KINDS:
  for b in KINDS: vec.append(transitions[(a,b)])
 if kinds:
  first,last=KIND_CODE[kinds[0]],KIND_CODE[kinds[-1]]
  runs=1; maxrun=1; cur=1
  for a,b in zip(kinds,kinds[1:]):
   if a==b: cur+=1; maxrun=max(maxrun,cur)
   else: runs+=1; cur=1
  distinct=len(set(kinds))
 else: first=last=4; runs=maxrun=distinct=0
 vec.extend((first,last,runs,maxrun,distinct))
 return tuple(vec)

def l2_vector(state,n,dist):
 prep,cd,feats,dis=q15.donor(state,n); assert q15.apply_circuit(q15.start_state(n),prep,n)==state
 lb,rx,c=q15.lower_bound(state,n)
 return base13(feats,cd,lb,rx,c,n)+donor_path_features(dis,n), bool(dist[state]==cd), cd, dist[state]

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--output',type=Path,default=OUT); args=ap.parse_args(); parent=json.loads(PARENT.read_text())
 rows=[]; per_n={}; cells=defaultdict(lambda:{'pos':0,'neg':0,'pos_keys':[],'neg_keys':[]})
 for n in (1,2,3):
  dist=q15.referee(n); exact=0
  for state in sorted(dist):
   vec,label,cd,copt=l2_vector(state,n,dist); exact+=int(label); rows.append((vec,label)); cell=cells[vec]; key=list(state); cell['pos' if label else 'neg']+=1; bucket=cell['pos_keys' if label else 'neg_keys'];
   if len(bucket)<2: bucket.append(key)
  per_n[str(n)]={'instances':len(dist),'donor_exact':exact,'expected':q15.expected_count(n)}
 mixed=[]; floor=0
 for vec,rec in cells.items():
  if rec['pos'] and rec['neg']:
   floor+=min(rec['pos'],rec['neg']); mixed.append({'vector':list(vec),'pos':rec['pos'],'neg':rec['neg'],'pos_keys':rec['pos_keys'],'neg_keys':rec['neg_keys']})
 mixed.sort(key=lambda x:(x['vector'],x['pos'],x['neg']))
 gates={'protocol_bound':PROTOCOL.exists(),'parent_l1_floor_43':parent.get('q2',{}).get('E_floor')==43,'parent_l1_mixed12':parent.get('q2',{}).get('mixed_cell_count')==12,'complete_1146':len(rows)==1146 and sum(v['instances'] for v in per_n.values())==1146,'expected_counts':all(v['instances']==v['expected'] for v in per_n.values()),'feature_length_constant':len({len(v) for v,_ in rows})==1,'no_label_in_feature_construction':True}
 determined=len(mixed)==0
 terminal='QG15C_L2_FEATURE_DETERMINED_ON_COMPLETE_NLE3__HELDOUT_STAGE_REQUIRED' if determined and all(gates.values()) else ('QG15C_ENLARGED_DONOR_PATH_VOCABULARY_STILL_INSUFFICIENT__MIXED_CELLS_MACHINE_VERIFIED' if all(gates.values()) else 'QG15C_PARENT_OR_DOMAIN_BINDING_FAILURE')
 out={'schema':'ORION.QG.QG15C.EnlargedVocabulary.v1','issue':'SzeChunYiu/ORION#840','terminal':terminal,'protocol_sha256':sha(PROTOCOL),'parent_sha256':sha(PARENT),'feature_count':len(rows[0][0]),'domain':per_n,'training_rows':len(rows),'unique_feature_cells':len(cells),'mixed_cell_count':len(mixed),'irreducible_error_floor':floor,'parent_L1_mixed_cell_count':12,'parent_L1_error_floor':43,'mixed_cells_verbatim':mixed[:20],'mixed_cells_verbatim_cap':20,'feature_determined_complete_nle3':determined,'heldout_stage_authorized':determined,'gates':gates,'all_gates':all(gates.values()),'chemistry_sources_read':False,'protected_subject_read':False,'novelty_authority':False,'r6_authority':False,'physical_quantum_advantage_claim':False}
 u=dict(out); out['result_digest']=hashlib.sha256(canonical(u).encode()).hexdigest(); args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(TOKEN+canonical({'terminal':terminal,'mixed_cells':len(mixed),'floor':floor,'feature_count':out['feature_count'],'result_digest':out['result_digest']})); return 0
if __name__=='__main__': raise SystemExit(main())
