#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)
def pats(lo,hi):
 z=[]
 for s in range(lo,hi+1):
  for c in range(8):
   b=31-s-3*c;a=2*s-31+2*c
   if min(a,b)>=0 and a+b+c==s and a+2*b+4*c==31:z.append({'support':s,'a1':a,'b2':b,'c4':c})
 return z
def lb(p):
 c=p['c4']
 if c<=2:return [{**p,'branch':'MIXED_RANK3','engine_family':'high','seed_multiplicities':{0:[2,2,2],1:[4,2,2],2:[4,4,2]}[c],'plane_doubletons':False}]
 if c==3:return [{**p,'branch':'HIGH4_RANK3','engine_family':'rank3'},{**p,'branch':'HIGH4_RANK2_OUTSIDE','engine_family':'c4rank2'}]
 return [{**p,'branch':'HIGH4_RANK3','engine_family':'rank3'}]
def main():
 got=json.loads((ROOT/'FULL_CUBE_COVER.json').read_text());up=json.loads((ROOT/'CUBE_COVER.json').read_text());p=pats(14,22);b=[q for x in p for q in lb(x)]
 exp={'schema':'ORION.ORION04.FullSupport14To31Cover.v1','support_interval':[14,31],'pattern_count':len(p)+up['pattern_count'],'branch_count':len(b)+up['branch_count'],'lower_patterns':p,'lower_branches':b,'upper_cover_digest':up['digest'],'upper_patterns':up['patterns'],'upper_branches':up['branches'],'parent_support_le13_result_digest':'6e25fbf0a483817bb5edb4908640e0b0b83be47d2cc4b2da6192feb9fecbc004'};exp['digest']=hashlib.sha256(canon(exp).encode()).hexdigest()
 checks={'exact':got==exp,'patterns_60':got['pattern_count']==60,'branches_78':got['branch_count']==78,'lower_51':len(got['lower_branches'])==51,'upper_27':len(got['upper_branches'])==27}
 mut=json.loads(json.dumps(got));mut['lower_branches'].pop();checks['missing_branch_rejected']=mut!=exp
 r={'schema':'ORION.ORION04.FullCoverIndependentCheck.v1','checks':checks,'decision':'FULL_COVER_ACCEPT' if all(checks.values()) else 'FULL_COVER_REJECT'};r['digest']=hashlib.sha256(canon(r).encode()).hexdigest();(ROOT/'FULL_COVER_CHECK_RESULT.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(canon({'decision':r['decision'],'digest':r['digest']}));return 0 if all(checks.values()) else 1
if __name__=='__main__':raise SystemExit(main())
