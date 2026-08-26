#!/usr/bin/env python3
"""Exhaustive controls for the AB R10 graph interaction-tax theorem."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

SCHEMA="ORION.AB.InteractionTax.R10.v1"

def edge_list(n): return [(i,j) for i in range(n) for j in range(i+1,n)]
def independent(mask,edges): return all(not (((mask>>u)&1) and ((mask>>v)&1)) for u,v in edges)
def vertex_cover(mask,n,edges): return all(((mask>>u)&1) or ((mask>>v)&1) for u,v in edges)

def run():
    graphs=states=mismatches=0; hist={}
    for n in range(1,6):
        slots=edge_list(n)
        for gmask in range(1<<len(slots)):
            edges=[e for i,e in enumerate(slots) if (gmask>>i)&1]; graphs+=1
            terminals=[]
            for smask in range(1<<n):
                states+=1
                if independent(smask,edges): terminals.append(smask)
            beta=max(s.bit_count() for s in terminals)
            alpha=max(s.bit_count() for s in range(1<<n) if independent(s,edges))
            tau=min(s.bit_count() for s in range(1<<n) if vertex_cover(s,n,edges))
            if beta!=alpha or beta+tau!=n:
                mismatches+=1; raise AssertionError((n,gmask,beta,alpha,tau))
            hist[str(n-beta)]=hist.get(str(n-beta),0)+1
    assert graphs==1099 and mismatches==0
    result={"schema":SCHEMA,"status":"PASS","graphs_exhausted":graphs,"terminal_state_checks":states,"mismatches":mismatches,"interaction_tax_histogram":hist,"authority":{"graph_identities_donor_owned":True,"finite_mapping_controls_exact":True,"production_transfer":False}}
    result["content_sha256"]=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return result

if __name__=="__main__":
    r=run(); text=json.dumps(r,indent=2,sort_keys=True)+"\n"; print(text,end=""); Path(__file__).with_name("INTERACTION_TAX_R10_RESULTS.json").write_text(text)
