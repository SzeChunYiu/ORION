#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)
def pats(lo,hi):
 z=[]
 for s in range(lo,hi+1):
  for c in range(8):
   b=31-s-3*c;a=2*s-31+2*c
   if min(a,b)>=0 and a+b+c==s and a+2*b+4*c==31:z.append({'support':s,'a1':a,'b2':b,'c4':c})
 return z
def lower_branches(p):
 a,b,c=p['a1'],p['b2'],p['c4']
 if c<=2:return [{**p,'branch':'MIXED_RANK3','engine_family':'high','seed_multiplicities':{0:[2,2,2],1:[4,2,2],2:[4,4,2]}[c],'plane_doubletons':False}]
 if c==3:return [{**p,'branch':'HIGH4_RANK3','engine_family':'rank3'},{**p,'branch':'HIGH4_RANK2_OUTSIDE','engine_family':'c4rank2'}]
 return [{**p,'branch':'HIGH4_RANK3','engine_family':'rank3'}]
def main():
 high=json.loads((ROOT/'CUBE_COVER.json').read_text())
 lp=pats(14,22);lb=[b for p in lp for b in lower_branches(p)]
 obj={'schema':'ORION.ORION04.FullSupport14To31Cover.v1','support_interval':[14,31],'pattern_count':len(lp)+high['pattern_count'],'branch_count':len(lb)+high['branch_count'],'lower_patterns':lp,'lower_branches':lb,'upper_cover_digest':high['digest'],'upper_patterns':high['patterns'],'upper_branches':high['branches'],'parent_support_le13_result_digest':'6e25fbf0a483817bb5edb4908640e0b0b83be47d2cc4b2da6192feb9fecbc004'}
 obj['digest']=hashlib.sha256(canon(obj).encode()).hexdigest();(ROOT/'FULL_CUBE_COVER.json').write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n');print(canon({'patterns':obj['pattern_count'],'branches':obj['branch_count'],'digest':obj['digest']}))
if __name__=='__main__':main()
