"""Does the p>=11 analogue of the p=5 bridge hold?

At p=5 the congruence forced a flat profile to carry a maximal atom.  Test the
same question for D_3(C_p^3): take a special-length corridor triple with NO
maximal part, assume the atom lengths are exactly its parts, and ask whether the
spectrum system is still consistent.  If not, T needs atoms beyond the profile --
and we then ask whether D = 3p-2 is among the lengths it is forced to add.
"""
import importlib.util
spec=importlib.util.spec_from_file_location(
    "vgs","/home/user/ORION/research/experiments/davenport-c7-frontier/verify_general_spectrum_v4.py")
vgs=importlib.util.module_from_spec(spec); spec.loader.exec_module(vgs)

def law(p,m):
    r,h,base=m%p,(p-1)//2,(3*p-1)//2
    return base if (r<=h or r==p-1) else base+r-h

for p in (7,11,13,17):
    N,D,amin=(11*p-3)//2,3*p-2,p+1
    a,b,c=3*(p-1)//2,2*p,(5*p-3)//2
    LENS=set(range(amin,D+1))
    rows={}
    for L in (a,b,c):
        m=N-L; w=law(p,m)
        rows[L]=[(L,u,m-u) for u in range(max(amin,m-D),w+1) if u<=m-u<=D]
    flat=[t for L in rows for t in rows[L] if D not in t]
    print(f"p={p:>3}: D={D}; corridor triples {sum(len(v) for v in rows.values())}, "
          f"of which FLAT (no maximal part): {len(flat)}")
    # 1. is a single maximal atom forced outright?
    print(f"      excluding D alone feasible? {vgs.spec_feasible(p,{D})}")
    # 2. for each flat triple: assume atom lengths are exactly its parts
    needmore=0; forcesD=0; sample=None
    for t in flat:
        zero=LENS-set(t)
        if not vgs.spec_feasible(p,zero):
            needmore+=1
            # it needs extra lengths; is D forced among them?  test: allow every
            # length except D, on top of the profile
            if not vgs.spec_feasible(p,{D}):
                forcesD+=1
            elif sample is None:
                sample=t
    print(f"      flat triples whose own parts alone are INFEASIBLE: {needmore}/{len(flat)}"
          f" ; of those, D forced: {forcesD}")
    if sample: print(f"      e.g. {sample}: needs extra atom lengths, but NOT necessarily D")
    print()
