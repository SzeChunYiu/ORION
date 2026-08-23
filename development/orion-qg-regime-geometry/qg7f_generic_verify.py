#!/usr/bin/env python3
"""Independent generic ORION verifier for QG-7f F0 representation audit."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];IN=ROOT/"artifacts/orion-qg-qg7f-chain-representation-audit.json";OUT=ROOT/"artifacts/orion-qg-qg7f-generic-verification.json";TOKEN="ORIONQG_QG7F_GENERIC=";POS="QG7F_TWO_COORD_REDUCTION_REFUTED__TAG3_MULTI_COMM_S2_CONFIGURATION"
I,X,Y,Z=0,1,2,3
S=(X,X,X);F={"A":((X,I,I),(Y,I,I)),"B":((Y,Y,I),(Z,I,I)),"C":((I,Y,Y),(I,Z,I))}
def canon(v):return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def vd(r):
 d={k:v for k,v in r.items() if k!="result_digest"};return r.get("result_digest")==hashlib.sha256(canon(d).encode()).hexdigest()
def ls(a,b):return int(a!=0 and b!=0 and a!=b)
def w(p):return sum(x!=0 for x in p)
def sp(p):return tuple(i for i,x in enumerate(p) if x!=0)
def sy(a,b):return sum(ls(x,y) for x,y in zip(a,b))%2
def cs(r0,r1):
 if w(r0)!=2 or w(r1)!=1:return False
 a=sp(r1)[0]
 if a not in sp(r0):return False
 b=next(q for q in sp(r0) if q!=a)
 good=S[a]!=0 and S[b]!=0 and ls(S[a],r0[a])==1 and ls(S[b],r0[b])==1 and r1[a] not in (0,S[a],r0[a])
 red=any(ls(r0[q],r1[q])==0 and ls(S[q],r0[q])==0 for q in sp(r0))
 return good and not red
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--input",type=Path,default=IN);ap.add_argument("--output",type=Path,default=OUT);a=ap.parse_args();src=json.loads(a.input.read_text())
 labels={k:(sy(S,v[0]),sy(S,v[1])) for k,v in F.items()};pairs={k:sy(v[0],v[1]) for k,v in F.items()};bs=set(sp(F["B"][0]));csup=set(sp(F["C"][0]));ss=set(sp(S))
 checks={"source_digest":vd(src),"source_terminal":src.get("terminal")==POS and src.get("representation_premise_refuted") is True,
         "pairs":all(v==1 for v in pairs.values()),"labels":all(v==(0,1) for v in labels.values()),
         "anchored_A":w(F["A"][0])==w(F["A"][1])==1 and sp(F["A"][0])==sp(F["A"][1])==(0,) and S[0]==F["A"][0][0] and ls(S[0],F["A"][1][0])==1,
         "comm_s2_B":cs(F["B"][0],F["B"][1]),"comm_s2_C":cs(F["C"][0],F["C"][1]),"tag3":w(S)==3,
         "support_pairs_differ":bs!=csup,"supports_inside_tag":bs<=ss and csup<=ss,
         "source_coordinates":src.get("observed_comm_s2_support_pairs")=={"B":[0,1],"C":[1,2]},
         "scope":src.get("CHAIN_REPRESENTATION_COMPLETE") is False and src.get("CHAIN_ALL_N") is False and src.get("GLOBAL_BDOUBLEPRIME_COMPLETENESS") is False and src.get("FIFTH_REGIME_FOUND") is False,
         "authority":src.get("novelty_authority") is False and src.get("r6_authority") is False and src.get("physical_quantum_advantage_claim") is False}
 ok=all(checks.values());out={"schema":"ORIONQG.QG7F.GenericVerification.v1","decision":"ACCEPT_REPRESENTATION_PREMISE_REFUTATION" if ok else "REJECT","all_checks":bool(ok),"checks":checks,"source_result_digest":src.get("result_digest"),"representation_premise_refuted":bool(ok),"CHAIN_REPRESENTATION_COMPLETE":False,"CHAIN_ALL_N":False,"GLOBAL_BDOUBLEPRIME_COMPLETENESS":False,"FIFTH_REGIME_FOUND":False,"novelty_authority":False,"r6_authority":False,"physical_quantum_advantage_claim":False};a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(TOKEN+canon({"decision":out["decision"],"all_checks":ok,"B_support":[0,1],"C_support":[1,2]}));return 0
if __name__=="__main__":raise SystemExit(main())
