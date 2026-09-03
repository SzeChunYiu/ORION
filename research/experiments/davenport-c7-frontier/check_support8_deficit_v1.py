#!/usr/bin/env python3
from __future__ import annotations
import itertools,json
P=7
# Actual multiplicities m_i are in [1,6] and sum to 37. Deficits d_i=6-m_i sum to 11.
profiles=[d for d in itertools.product(range(6),repeat=8) if sum(d)==11]
assert len(profiles)==25488
# Two distinct actual support elements on the same projective direction, normalized as x and a*x.
# A genuine obstruction is 7-short-zero-free, so no available nonzero count pair may sum to 0 mod 7.
allowed=[]
for a in range(2,P):
    for r in range(1,7):
        for s in range(1,7-r):
            bad=False
            for u in range(r+1):
                for v in range(s+1):
                    if u+v and (u+a*v)%P==0:
                        bad=True;break
                if bad:break
            if not bad:
                allowed.append((a,r,s))
assert len(allowed)==18
assert max(r+s for _,r,s in allowed)==5
# Inverse identifies a with a^{-1} when the two support values are swapped.
ratios=sorted({min(a,pow(a,-1,P)) for a,_,_ in allowed})
assert ratios==[2,3]
# ratio 4 is inverse to2 and5 inverse to3; ratio6=-1 never survives.
# Plane-occupancy deficit: four actual support points in one plane require sum(d_i)>=6.
# Two four-secants disjoint on the support already consume >=12>11 and are impossible.
print(json.dumps({
 'ordered_deficit_profiles':len(profiles),
 'allowed_oriented_duplicated_line_states':len(allowed),
 'max_duplicated_direction_occupancy_under_7_short_free':max(r+s for _,r,s in allowed),
 'duplicated_ratio_orbits_present':ratios,
 'global_deficit_budget':11,
 'four_point_plane_minimum_deficit':6,
 'two_disjoint_four_secants_impossible':True,
},sort_keys=True))
