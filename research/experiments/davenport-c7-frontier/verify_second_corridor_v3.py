"""A SECOND corridor, for the factorization through the forced 13/14-atom.

ATOM_SPECTRUM_CONGRUENCE_V3 forces an atom B with |B| in {13,14}.  Its complement
C = T B^{-1} has length 37-|B| > D = 19, so z(C) = 2 and C = U.V with U,V atoms.  That gives
a 3-atom factorization (|B|, u, 37-|B|-u) with all parts in [8,19].

ATOM_LENGTH_CORRIDOR_V1's PROOF establishes: any 3-atom factorization CONTAINING A SHORTEST
atom has one of the six corridor profiles.  So if a candidate profile contains an atom whose
length equals the global minimum atom length s, and the profile is not a corridor triple, it
is excluded.  Since s in {8,9,10} and s is the minimum over all atoms, a profile containing
the value 8 forces s = 8 (min atom length is 8 overall), etc.
"""
CORR = {(8,10,19),(9,9,19),(9,10,18),(9,11,17),(9,12,16),(10,10,17)}
S_RANGE = (8,9,10)      # possible global shortest atom length

def profiles(b):
    out=[]
    m=37-b
    for u in range(8, m-8+1):
        v=m-u
        if u>v: continue
        if v>19 or u>19: continue
        out.append(tuple(sorted((b,u,v))))
    return sorted(set(out))

print("Candidate factorizations through a forced atom of length b:\n")
survivors={}
for b in (13,14):
    print(f"  b = {b}:")
    keep=[]
    for P in profiles(b):
        # for each possible global minimum s, is this profile admissible?
        ok_s=[]
        for s in S_RANGE:
            if min(P) < s:            # profile has an atom shorter than the claimed minimum
                continue
            if s in P and P not in CORR:
                continue              # contains a shortest atom but is not a corridor triple
            ok_s.append(s)
        status = "EXCLUDED" if not ok_s else f"survives for s in {ok_s}"
        print(f"     {str(P):>14}  {'(corridor)' if P in CORR else '':>11}  {status}")
        if ok_s: keep.append((P,ok_s))
    survivors[b]=keep
    print()
print("Surviving second-factorization profiles:")
allP=set()
for b,keep in survivors.items():
    for P,ss in keep:
        allP.add(P)
        print(f"   b={b}: {P}  (needs shortest-atom length s in {ss})")
print()
print(f"Distinct new profiles to attack: {sorted(allP)}")
print("None of these is a corridor triple, so none is covered by the existing support ladder.")
