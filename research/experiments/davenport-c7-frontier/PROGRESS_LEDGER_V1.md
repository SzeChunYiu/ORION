# C7^3 multiwise Davenport frontier — progress ledger V11

Status: live LLM-assisted ORION research ledger. No novelty authority.

## Verified structural spine

The current general target is

`D_k(C_p^3)=kp+(5p-5)/2=((2k+5)p-5)/2` for prime `p>=5`, `k>=2`.

The branch has reduced a first failure to a finite rank-three augmentation problem:

- with `M_p=(5p-5)/2`, a first failure has `z(B)=m`, `|B|=pm+M_p+q`, `q>=1`;
- every proper atom subproduct has its expected packing number;
- atom excesses satisfy `e_i>=q`, `sum e_i=M_p+q`, `(m-1)q<=M_p`;
- the sequence is `(p+q-1)`-short-zero-free;
- Bhowmik--Schlage-Puchta gives `q<=(p-1)/2`;
- Zhang forces a maximum factorization containing an atom with excess at most `p-2`;
- coding plus the algebraic cap gives finite first-failure levels: `K_5=10`, `K_7=15`, `K_p=(5p-3)/2` for `p>=11`;
- Freeze--Schmid's eta-tail recurrence gives the alternative bound `m<=min(M_p+1,T_p(E_p))` whenever `eta(C_p^3)<=E_p` is known;
- the p=7 excess-signature shell is reduced from 322 algebraic signatures to 286 after coding, the q-cap, the uniform short-atom theorem and the six exact `(m,q)=(3,1)` atom corridors;
- q-dependent rank-two restricted-sum theory gives every plane occupancy `<=3p-q-2`, with strict cap `3p-q-3` for four or more occupied directions;
- equality for `q>=2` forces the exact plane grammar `e1^(p-1)e2^(p-1)(e1+e2)^(p-q)` and a canonical atom `e1^q e2^q (e1+e2)^(p-q)` of length `p+q` into a maximum factorization;
- weighted projective deficits satisfy `sum_line d_i >= (t-3)(p-1)+(q-1)` on every t-secant, strengthened to `+(q)` for `t>=4`;
- full-multiplicity directions form an arc for `q>=2`;
- maximal-atom products have the Geroldinger--Yang two-term avoidance: if maximal `U` and atom `V` have `z(UV)=2`, then `Sigma_2(U)` misses `Sigma_{3..|V|-1}(V)`, so the corresponding short negative V-subsums require U-representation depth at least three;
- every surviving first failure remains terminal under every positive-gain conformal Graver move.

## Exact p=7 length-37 frontier

For zero-sum `B` over `C_7^3` with `|B|=37` and `z(B)<=3`:

- `z(B)=3`, the `(p,m,q)=(7,3,1)` slice;
- support is at least eight;
- support eight must use eight distinct projective directions;
- every maximum three-atom factorization has one of
  `(8,10,19)`, `(9,9,19)`, `(9,10,18)`, `(9,11,17)`, `(9,12,16)`, `(10,10,17)`;
- the support-seven cover is completely closed: 3,418,800 lifts, 14,860 short-free, all four-pack;
- the support-eight one-projective-collision cover is completely closed: 19,114,200 lifts, 15,844 short-free, all four-pack;
- the smallest unresolved support-eight face is the eight-distinct-direction Type-A branch over 347 projective classes and 5,841,092 class/deficit-profile pairs;
- the two length-19 corridors obey both the earlier scalar line-fiber grammar and the newer U-representation-depth >=3 constraints.

No `D_3(C_7^3)` value is claimed yet.

## New bounded closure: `(p,q,m,r)=(7,2,8,13)`

`RANK2_Q_PLANE_CAP_AND_WEIGHTED_ARC_V1.md` first raised the direction floor in the `(q,m)=(2,8)` first-failure slice to `r>=13`.

`P7_Q2_M8_R13_CONIC_CLOSURE_V1.md` now eliminates equality.

At `r=13`, total direction deficit is

`Delta=13*6-73=5`.

The arc bound forces exactly eight weight-6 directions and five weight-5 directions. The eight full directions form an 8-arc and hence, by Segre, a conic. Total deficit five is too small for a four-secant, so the direction support is a `(13,3)`-arc formed by that conic plus five off-conic points.

Two independent generators enumerate exactly **5,166** valid five-point off-conic extensions. Canonical cover digest:

`0eb3a99b0bb1c30595f9b6b58e74b980c094c5d5754a50f726d82aed4711d82c`.

Every conic secant through a weight-5 point has occupancy `6+6+5=17`, saturating the q-dependent plane cap. Rank-two inverse structure therefore forces the actual-element equation

`x_D=x_i+x_j`

on every such secant. All eight conic directions participate in saturated secants for every candidate.

Primary verifier: assemble the resulting homogeneous system in 13 scalar variables over `F_7`; **all 5,166 matrices have rank 13**.

Independent verifier: derive multiplicative conic-scalar ratios on every saturated secant and propagate them around cycles; **all 5,166 candidates have an inconsistent ratio cycle**.

Therefore the minimal direction case is impossible:

`(p,q,m)=(7,2,8) => r>=14`.

This is a bounded first-failure closure only; the `r>=14` branch remains.

## Current missing theorem

The all-prime problem is still isolated to a finite **rank-three augmentation theorem**:

every surviving first-failure positive kernel vector satisfying the short-sum, atom-excess, q-dependent plane, weighted-secants, maximal-atom depth and hereditary subproduct constraints must admit a positive-gain two- or three-atom conformal refactor.

## Next discriminators

1. Continue the `(p,q,m)=(7,2,8)` branch from the improved floor `r>=14`; test whether weighted secant supersaturation forces either another saturated plane system or a direct Graver move.
2. Apply the same saturated-conic compatibility method to the other bumped slices `(q,m)=(2,6),(2,7),(3,5),(3,6)` at their minimum projective-direction floors.
3. Finish the eight-distinct-direction support-eight Type-A `(7,3,1)` closure.
4. Combine maximal-atom U-depth >=3 with exact short-atom/rank-two subsum structure in `(8,10,19)` and `(9,9,19)`.
5. Seek a local-`nu` three-deletion theorem for maximal atoms in `C_p^3`.
6. Continue donor saturation under generalized Noether numbers, sets of lengths, local `nu`, restricted sumsets, projective codes and Graver augmentation.

## Retained negative / non-promoted routes

- Eventual linearity alone does not imply stabilization at `k=2`.
- Generic Graver-basis existence is a reformulation, not the needed positive-gain theorem.
- General exact `eta(C_p^3)` is not assumed for primes `p>=7`.
- Additive-basis donor searches have not yet forced a relevant maximal-atom target to have representation depth at most two.
- The q-dependent rank-two cap improves several geometric slices but by itself does not delete a complete `(m,q)` level; the new `q=2,m=8,r=13` deletion needs the scalar compatibility layer.

## Claim ceiling

No claim states that `D_3(C_7^3)` is solved, that the all-prime formula is proved or novel, or that general `eta(C_p^3)` is known. Donor theorems receive zero ORION novelty credit; finite computations authorize only their declared domains.
