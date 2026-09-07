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

# Property C(C_7^2): an 18-term 7-short-free plane sequence has at most 3 actual support values.
# Therefore a plane with four actual support values has occupancy <=17, so its four deficits sum to >=7.
one_four=[d for d in profiles if sum(d[i] for i in (0,1,2,3))>=7]
assert len(one_four)==8264

# Two 4-secants meeting in support point 0: {0,1,2,3} and {0,4,5,6}.
two_intersecting=[d for d in profiles
    if sum(d[i] for i in (0,1,2,3))>=7
    and sum(d[i] for i in (0,4,5,6))>=7]
assert len(two_intersecting)==1061
assert all(d[0]>=3 for d in two_intersecting)
assert all(d[0]-d[7]>=3 for d in two_intersecting)

# Two support-disjoint 4-secants would each consume at least 7 deficit, impossible with global budget 11.
two_disjoint=[d for d in profiles
    if sum(d[i] for i in (0,1,2,3))>=7
    and sum(d[i] for i in (4,5,6,7))>=7]
assert len(two_disjoint)==0

effective_type_a_pairs=181*len(profiles)+146*len(one_four)+20*len(two_intersecting)
assert effective_type_a_pairs==5841092

print(json.dumps({
 'ordered_deficit_profiles':len(profiles),
 'allowed_oriented_duplicated_line_states':len(allowed),
 'max_duplicated_direction_occupancy_under_7_short_free':max(r+s for _,r,s in allowed),
 'duplicated_ratio_orbits_present':ratios,
 'global_deficit_budget':11,
 'four_point_plane_minimum_deficit_property_c':7,
 'profiles_one_four_secant':len(one_four),
 'profiles_two_intersecting_four_secants':len(two_intersecting),
 'profiles_two_disjoint_four_secants':len(two_disjoint),
 'intersecting_four_secant_shared_point_max_multiplicity':3,
 'effective_type_a_projective_profile_pairs':effective_type_a_pairs,
},sort_keys=True))
