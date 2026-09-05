# Davenport Paper-2 structural frontier handoff — 2026-09-05

Starting live branch: `shadow/davenport-c7-frontier-20260903`.
Starting commit: `86f089ab63ba90f7df292cd44d5a46c7527014ce`.
Private continuation checkout: `shadow/davenport-boundary-20260905`.

## Main outcome

The exceptional canonical **rank-three `a=3` face is completely eliminated
for every prime `p>=7`**, by structural shared-donor certificates. See
`A3_RANK3_COMPLETE_ELIMINATION_V1.md` for the exact theorem and its dependency
map. The original fixed negative-even `J` family needed a larger donor
interval and complementary odd/wrapped scalars; existence of a universal
original `J` was neither assumed nor proved.

The first-corridor support-seven theorem and `D_3(C_7^3)` remain open.
No all-prime `D_k` formula, novelty certification, or submission readiness
is asserted.

## Genuine advances and commits

Use `H=(p-1)/2`, `m=p+H` throughout.

| Advance | Exact scope | Commit / proof note |
|---|---|---|
| Rank-three `a=3,c=1` | Entire layer; scalar three plus two explicit small-prime vectors | `1f3540ac0`; `A3_RANK3_ONE_LIGHT_SHARE_ELIMINATION_V1.md` |
| Rank-three `a=3,c>=3` | Entire layer; flexible donors and complementary interval selectors | `3c04ec2d2`; `A3_RANK3_BOUNDARY_C_GE3_ELIMINATION_V1.md` |
| Rank-three `a=3,c=2` and full `a=3` conclusion | Entire layer and all-prime assembly, including a direct `p=7` certificate | `33213d200`; `A3_RANK3_TWO_LIGHT_SHARE_ELIMINATION_V1.md`, `A3_RANK3_COMPLETE_ELIMINATION_V1.md` |
| Rank-three `a=2` mixed rigidity | Extreme row `c=H-1,d=1,r=1,t=p-1`: plane, zero-coordinate, and affine sum-one slices eliminated | `4650d280c`; `A2_RANK3_EXTREME_BOUNDARY_MIXED_PLANE_ELIMINATION_V1.md` |
| Rank-two `a=2` balanced selector | `2<=c<=floor(p/3)`, balanced boundary; additional conditional high-overlap certificate | `3dc3bd08f`; `A2_RANK2_BALANCED_BOUNDARY_SELECTOR_V1.md` |
| Rank-two `a=1` balanced selector | `2<=c<=floor(p/7)`, balanced boundary; sharper remainder-sensitive condition | `30c9c90e2`; `A1_RANK2_BALANCED_BOUNDARY_SELECTOR_V1.md` |
| Rank-three `a=2` global interior and balanced band | Every interior eliminated; balanced band `c>=7`, `c+1<=p/3`, `2k<=c` eliminated | `0d0cae590`; `A2_RANK3_SHARED_DONOR_BOUNDARY_REDUCTION_V1.md` |

The rank-two boundary convention is
`r=H+1-e`, `t=p-f`, `e+f=c+1`; balanced means `e<=f`.
The `a=1` and `a=2` statements remove infinitely many absolute overlap
layers `c>=5`, but do not close all large relative overlaps.

The extreme rank-three `a=2` result uses unequal saturated donor counts.
Its exceptional certificate `xy s^(H-2)e_i` is genuinely mixed. In the
basis `(e1,e2,g)`, a surviving high-multiplicity value `y=(A,B,C)` on that
row must satisfy

`ABC!=0`, `A+B!=0`, `A+B+C!=1`.

The affine sum-one elimination explicitly uses the established Bernoulli
pairing result, Proposition 1.8 of Batyrev–Hofscheier,
[A generalization of a theorem of G. K. White](https://arxiv.org/pdf/1004.3411).
The proof note verifies every hypothesis and attributes the four-entry
donor to Morrison–Stevens as the primary source does. It makes no claim
of ownership of that theorem.

## Research team and verification

Three separately tasked agents supplied an additive-combinatorics selector
specialist, a zero-sum inverse-theory specialist, and an independent proof
auditor. The root integrated the results, independently proved the `c=1,2`
layers, and reviewed the other proof packets. Findings and corrections were
exchanged across the team, including donor floors, high-boundary wraps,
small-prime completeness, and the external pairing theorem's hypotheses.

All three complete `a=3` layer proofs received separate full mathematical
review. The 50 explicit finite-remainder vectors were directly replayed for
group congruences, all six occurrence capacities, and strict shortness;
the `p=7` old-support certificate was checked separately. These checks
verify written certificates and do not enumerate hypothetical companions.
The infinite-prime authority is the symbolic proof, not finite replay.

The rank-two selectors and all parts of the extreme `a=2` proof received
independent review. The root and auditor opened the external primary
Bernoulli-pairing source. Internal review is not external referee approval
or a novelty audit. No manuscript or historical claim ledger was silently
promoted by this research checkpoint.

## Preserved failed routes

1. The original negative-even selector requires `3k+1<=H` for every
   `J>=2`, so it cannot cover the whole multiplicity strip. Even at
   `p=13,c=d=1,k=0`, its only donor-feasible even scalars have lengths
   `20,19,20`, none below `m=19`. The completed proof changes the donor
   and scalar parity where needed.
2. At the extreme rank-three `a=2` row, the admissible relation multipliers
   are exactly `{0,1}`. More strongly, new-value subsequences enter the
   overlap plane only when empty or equal to the full new-value part.
   The donor-only minimum is at least `m`, and the full new-value part
   has best completion exactly `m`. Equal saturated donor counts therefore
   cannot settle that row; the new mixed mechanism deliberately leaves
   that restriction.
3. Lower-overlap `a=2` pure-power partial extensions already have an infinite
   short-free barrier in `A2_SHARED_DONOR_PLANE_RIGIDITY_V1.md`. They are
   not full companions and are not counterexamples to the corridor target.
4. Neither the plane condition nor affine coordinate sum one is forced for
   arbitrary high-multiplicity values. The Bernoulli-pairing theorem cannot
   be applied after silently imposing either condition.
5. The balanced rank-two floors can be zero at high relative overlap, and
   their new-value capacities do not automatically extend to the opposite
   half. Each conditional score and capacity hypothesis remains explicit.

## Exact next frontier

The prior generic `a>=4` rank-three theorem and the present `a=3` closure
leave **only `a=2` in the rank-three equality face**. The first remaining
task is mixed-subsequence rigidity on the now-proved strip

`d=1`, `r=H-k`, `t=p-c-1+k`, `0<=k<=min(c,H-1)`,

with `c<=2 floor(H/2)`. Subtract the newly eliminated band
`c>=7`, `c+1<=p/3`, `2k<=c`. The remaining high-`k`, smaller-`c`, and
higher-relative-overlap cases still need proof. Start with arbitrary
high-multiplicity values in the explicit extreme-row complement above;
restricting again to relation multipliers on that row cannot work.

Rank-two light types `a=1,2` still have open overlap layers `c>=5`, after
subtracting the balanced slices proved here and all earlier `c<=4` results.
Target the opposite boundary half and the remaining high relative overlaps
with actual mixed occurrence certificates or a proved inverse theorem.

No completion of these local faces should be converted into a generalized
Davenport value without separately checking every global corridor and
packing implication required by the exact-value problem.

## Branch reconciliation

`DAVENPORT_BRANCH_AUDIT_20260905_V1.md` records all 23 discovered remote
Davenport branch heads and their comparison with the starting live commit.
Remote branch discovery used the connected GitHub source and a fresh Git
ref listing. The same 23 heads were rechecked after the theorem commits;
none had advanced. Other sessions' working trees were never edited.
All changes here are additive proof notes on a private continuation branch.
