#!/usr/bin/env python3
"""Independent exact replay of Paper C's two load-bearing fiber families."""
from __future__ import annotations
import json
from functools import lru_cache
from itertools import combinations
from math import ceil, log2


def b(s:int)->int:
    return 0 if s==1 else ceil(log2(s))

@lru_cache(None)
def d(s:int)->int:
    if s==1: return 0
    return d((s+1)//2)+d(s//2)+s-2


def partitions(n:int):
    blocks=[]
    def rec(i):
        if i==n:
            yield tuple(tuple(block) for block in blocks)
            return
        for j in range(len(blocks)):
            blocks[j].append(i)
            yield from rec(i+1)
            blocks[j].pop()
        blocks.append([i])
        yield from rec(i+1)
        blocks.pop()
    yield from rec(0)


def weight(p:str)->int:
    return sum(c!='I' for c in p)


def common_factor(strings, block):
    count=0
    for col in range(len(strings[0])):
        letters={strings[i][col] for i in block}
        if len(letters)==1 and 'I' not in letters:
            count+=1
    return count


def partition_cost(strings, pi):
    m=len(strings)
    W=sum(map(weight,strings))
    if len(pi)==1:
        F=common_factor(strings,pi[0])
        return (b(m)+1)*W+m-1+d(m)+b(m)-(m*(b(m)+1)-1)*F
    total=2*m+len(pi)-3+sum(d(len(S)) for S in pi)+max(b(len(S)) for S in pi)
    for S in pi:
        f=common_factor(strings,S)
        ws=sum(weight(strings[i]) for i in S)
        total += 2*f+(b(len(S))+2)*(ws-len(S)*f)
    return total


def pair_features(strings):
    out=[]
    for i,j in combinations(range(len(strings)),2):
        f=common_factor(strings,(i,j))
        g=4*f-(weight(strings[i])+weight(strings[j]))
        out.append((i,j,f,g))
    return tuple(out)


def solve(strings):
    m=len(strings)
    unary=2*sum(map(weight,strings))+3*m-3
    best=10**18; opts=[]; count=0
    for pi in partitions(m):
        count+=1
        cost=partition_cost(strings,pi)
        if cost<best:
            best=cost; opts=[pi]
        elif cost==best:
            opts.append(pi)
    return {"m":m,"partitions":count,"unary":unary,"best":best,"improvement":unary-best,"optima":opts}


def has_triple(pi): return any(len(S)>=3 for S in pi)
def mixed_block(pi, gadget_size=5): return any(len({i//gadget_size for i in S})>1 for S in pi)


def check_pair_family():
    A1=("XXXXII","XXXIXI","XXXIIX","XXIIII","XXIIII")
    B1=("XXXXII","XXXIXI","XXIXXI","XXIIII","XXIIII")
    assert tuple(map(weight,A1))==tuple(map(weight,B1))==(4,4,4,2,2)
    assert pair_features(A1)==pair_features(B1)
    results={}
    for name,base in (("A",A1),("B",B1)):
        one=solve(base)
        assert one["improvement"]==(10 if name=="A" else 9)
        if name=="A": assert all(has_triple(pi) for pi in one["optima"])
        else: assert all(not has_triple(pi) for pi in one["optima"])
        two=solve(tuple(p+"IIIIII" for p in base)+tuple("IIIIII"+p for p in base))
        assert two["improvement"]==(22 if name=="A" else 19)
        assert all(not mixed_block(pi) for pi in two["optima"])
        if name=="A": assert all(has_triple(pi) for pi in two["optima"])
        else: assert all(not has_triple(pi) for pi in two["optima"])
        results[name]={
            "t1":{"improvement":one["improvement"],"optima":len(one["optima"]),"partitions":one["partitions"]},
            "t2":{"improvement":two["improvement"],"optima":len(two["optima"]),"partitions":two["partitions"]},
        }
    return {"features_identical":True,"results":results}


def parity_instance(m:int,L:int,parity:int):
    q=m-1
    columns=[]
    for mask in range(1<<q):
        if (mask.bit_count()&1)==parity:
            support={0}|{j+1 for j in range(q) if mask>>j&1}
            columns.extend([support]*L)
    N=(1<<(m-2))*L
    K=N*m*(b(m)+1)+m-1+d(m)+b(m)+1
    columns.extend([set(range(m))]*K)
    strings=[]
    for i in range(m):
        strings.append(''.join('X' if i in support else 'I' for support in columns))
    return tuple(strings),N,K


def all_labeled_common_counts(strings,max_order):
    out={}
    m=len(strings)
    for r in range(1,max_order+1):
        for S in combinations(range(m),r): out[S]=common_factor(strings,S)
    return out


def check_parity_family():
    rows=[]
    for m in (5,6):
        L=1
        even,N,K=parity_instance(m,L,0)
        odd,_,_=parity_instance(m,L,1)
        assert tuple(map(weight,even))==tuple(map(weight,odd))
        assert all_labeled_common_counts(even,m-2)==all_labeled_common_counts(odd,m-2)
        se=solve(even); so=solve(odd)
        gap=abs(se["improvement"]-so["improvement"])
        expected=(m*(b(m)+1)-1)*L
        assert gap==expected
        assert all(len(pi)==1 for pi in se["optima"])
        assert all(len(pi)==1 for pi in so["optima"])
        rows.append({"m":m,"N":N,"K":K,"gap":gap,"expected":expected,
                     "even_improvement":se["improvement"],"odd_improvement":so["improvement"],
                     "partitions":se["partitions"]})
    return rows


def main():
    report={"pair_family":check_pair_family(),"parity_family":check_parity_family(),"status":"PASS"}
    print(json.dumps(report,indent=2,sort_keys=True,default=list))
if __name__=='__main__': main()
