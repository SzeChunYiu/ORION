# C7^3 multiwise Davenport frontier — progress ledger V16

Status: live LLM-assisted ORION research ledger. No novelty authority.

## General target and first-failure formalism

For prime `p>=5`, put

`M_p=(5p-5)/2`.

The candidate line is

`D_k(C_p^3)=kp+M_p=((2k+5)p-5)/2` for `k>=2`.

Equivalently, every zero-sum block `B` should satisfy

`|B|-p z(B)<=M_p`,

where `z(B)` is its maximum zero-sum packing number. In Freeze--Schmid notation this is the joint assertion `D_0(C_p^3)=M_p` and stabilization index `k_D=2`.

A first failure may be chosen with

`z(B)=m`, `|B|=pm+M_p+q`, `q>=1`,

and a maximum atomic factorization `B=U_1...U_m`. Writing `e_i=|U_i|-p`, the branch has proved:

- every proper atom subproduct has exactly its displayed packing number;
- `e_i>=q`, `sum e_i=M_p+q`, `(m-1)q<=M_p`;
- `B` has no nonempty zero-sum through length `p+q-1`;
- `q<=(p-1)/2` by Bhowmik--Schlage-Puchta;
- Zhang forces a maximum factorization with `min e_i<=p-2`;
- coding/algebraic bounds reduce first-failure levels to `K_5=10`, `K_7=15`, `K_p=(5p-3)/2` for `p>=11`;
- any verified `eta(C_p^3)<=E_p` gives the alternative tail threshold `m<=min(M_p+1,T_p(E_p))`;
- every surviving factorization is terminal under positive-gain conformal Graver moves.

## Rank-two / projective geometry layer

The exact rank-two restricted-sum formula gives every first-failure plane occupancy

`<=3p-q-2`,

with strict cap `3p-q-3` for planes containing at least four occupied projective directions.

For `q>=2`, equality forces the exact grammar

`e1^(p-1)e2^(p-1)(e1+e2)^(p-q)`

and the canonical atom

`e1^q e2^q (e1+e2)^(p-q)`

of length `p+q` into a maximum factorization.

For projective direction deficits `d_i=(p-1)-w_i`, every `t`-secant satisfies

`sum_line d_i >= (t-3)(p-1)+(q-1)`,

and for `t>=4` the right side improves by one. Full directions form an arc for `q>=2`.

For `q>=3`, with `a=floor((q-1)/2)`, low-deficit tangent packing gives

`L<=p+2-f`

for the number `L` of directions with deficit in `1..a` relative to `f` full directions, and hence

`f >= (a+1)r-Delta-a(p+2)`.

## Large-arc scalar interpolation

### Full `(p+1)`-arc / conic

For odd prime `p>=7`, a full `(p+1)`-arc is a conic. A deficit-`q-1` off-conic direction `D=(d_0,d_1,d_2)` forces the scalar profile

`lambda(t)=mu_D(d_0d_2-d_1^2)/(d_0t^2-2d_1t+d_2)`.

Two distinct minimal-deficit centers would force proportional quadratic profiles at at least three field values, hence coincide. Therefore a full conic has at most one deficit-`q-1` off-conic direction and, with `n>=2` occupied off-conic directions,

`Delta>=qn-1`.

This yields a strict integral bump and the q=2 family

`p congruent 1 mod 4`, `p>=13`, `m=(5p-13)/4`,

with

`r>=(5p+7)/4`.

### Full p-arc

For prime `p>=11`, every p-arc extends to a unique conic. Relative to the p full arc, at most one occupied direction outside the conic completion can have deficit `q-1`; the missing completion point is an explicit exception.

At the integral p-full boundary `S=(N-p)/(p-2)`, equality `r=S` is impossible whenever

`(q-1)(S-p)>q+1`.

This gives the complementary q=2 family

`p congruent 3 mod 4`, `p>=19`, `m=(5p-15)/4`,

with

`r>=(5p+5)/4`.

Small-prime hostile boundaries are retained: compatible distinct centers exist for full p-arcs at `p=5,7`.

## Pair-product rank forcing

For every distinct pair of atoms `U_i,U_j`, put

`E=e_i+e_j`, `P=U_iU_j`.

Hereditary rigidity gives `z(P)=2`. Besides the ambient short-free window, the pair-complement argument makes `P` short-zero-free through

`H_ij=max(p+q-1,E-p+1)`.

Hence every rank-two subgroup `K` satisfies

`|(U_iU_j)_K|<=4p-3-H_ij`.

If the whole pair had rank at most two, total-zero structure improves the ambient extremal length by one:

`|U_iU_j|<=3p-q-3`,

or equivalently

`rank <U_iU_j> <=2 => e_i+e_j<=p-q-3`.

Thus

`e_i+e_j>p-q-3 => <supp(U_iU_j)>=C_p^3`.

Since every `e_i>=q`, every atom pair is rank three whenever `3q>p-3`.

At `p=7`, this applies uniformly for `q=2,3`. In the length-37 `q=1` frontier, every pair in all six exact corridors is also rank three because every pair excess sum is at least four while the rank-two threshold is three.

The maximal-short pair-plane caps sharpen to:

- `(19,10)`: plane occupancy at most `16`;
- `(19,9)`: plane occupancy at most `17`.

See `FIRST_FAILURE_PAIR_RANK_FORCING_V1.md`.

## New support-four maximal-atom classification

Let `U` be a maximal atom of length `3p-2` over `C_p^3` with exactly four support values. Then the support is a projective four-circuit and, after reordering, its multiplicities are exactly

`boxed{(p-1,p-1,a,p-a)}`

for some `1<=a<=(p-1)/2`.

The proof is arithmetic. Put `a_i=p-v_i(U)`, so `sum a_i=p+2`. Atom minimality is equivalent to the exact jump-set partition

`C_{a_1} sqcup ... sqcup C_{a_4}={2,...,p-1}`,

where

`C_a={t:[ta]_p<a}`

and `|C_a|=a-1`.

For `p>=11`, power moments `2,4,6,8` force, with `x_i=a_i^{-1}`,

`sum x_i=sum x_i^3=sum x_i^5=sum x_i^7=2`.

The rational function

`sum_i x_i/(1-x_i^2z)`

then agrees with `2/(1-z)` to order four at zero and to one extra order at infinity because `sum x_i^{-1}=sum a_i=2`. Its numerator must vanish identically. Partial fractions force

`{x_i}={1,1,u,-u}`,

hence

`{a_i}={1,1,c,p-c}`

and the displayed multiplicity pattern. The small primes `p=5,7` are checked directly by two independent primitive-kernel enumerators.

Up to automorphism and reordering, every such atom has canonical form

`e_1^(p-1) e_2^(p-1) e_3^a (e_3-a^{-1}(e_1+e_2))^(p-a)`.

For `p=7`, only `a=1,2,3` remain. This sharply reduces the support-four branch of the two length-19 corridors.

See `SUPPORT4_MAXIMAL_ATOM_WEIGHTS_V1.md`.

## Exact p=7 length-37 frontier

For zero-sum `B` over `C_7^3` with `|B|=37` and `z(B)<=3`:

- `z(B)=3`, the `(p,m,q)=(7,3,1)` first-failure slice;
- support is at least eight;
- support eight must use eight distinct projective directions;
- every maximum factorization has one of `(8,10,19)`, `(9,9,19)`, `(9,10,18)`, `(9,11,17)`, `(9,12,16)`, `(10,10,17)`;
- every pair of these atoms spans rank three;
- support seven is exactly closed: 3,418,800 lifts, 14,860 short-free, all four-pack;
- support-eight one-projective-collision is exactly closed: 19,114,200 lifts, 15,844 short-free, all four-pack;
- the smallest unresolved support-eight face is Type A: eight distinct projective directions over 347 surviving classes and 5,841,092 class/deficit-profile pairs;
- the `(8,10,19)` and `(9,9,19)` corridors obey scalar line-fiber avoidance, maximal-atom U-representation depth at least three, pair rank three, pair-plane caps 16/17, and now a three-type canonical classification whenever the 19-atom has support four.

No `D_3(C_7^3)` value is claimed yet.

## Exact higher first-failure closures at p=7

- `(q,m)=(2,8)`: the minimum 13-direction face is impossible, so `r>=14`. The 5,166-candidate conic census remains an independent control; full-conic interpolation gives the analytic contradiction.
- `(q,m)=(3,6)`: the minimum 11-direction face is impossible, so `r>=12`. Tangent packing plus 7-arc extension kills seven full directions; full-conic interpolation kills eight full directions. The 4,466-candidate scalar census remains an independent control.

## Current p=7 excess-signature shell

The necessary shell is reduced from 322 algebraic signatures to **286** after coding, the overshoot cap, Zhang's short-atom theorem and the exact `(m,q)=(3,1)` corridors.

Digest:

`2b49f2b6f4579a27165ebe5285292a5966901f1af7793a5cf73f3e9c8d47be19`.

Geometric and pair-rank constraints prune realizations inside this shell without changing its length-signature count.

## Current missing theorem

The all-prime problem remains a finite **rank-three augmentation theorem**:

every surviving first-failure positive kernel vector satisfying the restricted-sum, excess-signature, pair-rank, pair-plane, q-dependent plane, tangent-packing, large-arc interpolation, maximal-atom-depth, support-four maximal-atom classification and hereditary-subproduct constraints must admit a positive-gain two- or three-atom conformal refactor.

The strongest current interfaces are:

- atom excess -> pair short-free depth -> pair rank / plane geometry;
- plane saturation -> canonical atom and scalar gain constraints;
- large full arcs -> rational scalar interpolation;
- maximal atoms -> one/two-term representation-depth exclusions;
- support-four maximal atoms -> a one-parameter primitive circuit family.

## Next discriminators

1. **Support-four length-19 corridor closure.** For `p=7`, test the three canonical maximal atoms `a=1,2,3` against the 9- and 10-atom companion using pair-plane caps, U-depth >=3 and line-fiber avoidance. This should be done before any generic maximal-atom search.
2. Feed pair-plane caps 16/17 into the remaining support>=5 maximal-atom corridor geometry.
3. Classify the short-short 18-term zero-sum pair in the two maximal-atom corridors: it is 7-short-free, rank three, and every proper zero-sum has length 8--10.
4. Finish the support-eight Type-A `(7,3,1)` closure.
5. Continue q=2,m=8 from r>=14 and q=3,m=6 from r>=12 using pair-rank forcing before kernel enumeration.
6. Seek a local-`nu` three-deletion theorem for maximal atoms.
7. Continue donor saturation under generalized Noether numbers, rational Beatty covers, cyclic index theory, rank-two inverse theory, projective codes, gain graphs and Graver augmentation.

## Retained negative / non-promoted routes

- Eventual linearity alone does not imply stabilization at `k=2`.
- Generalized Noether number language is useful but current subgroup/quotient degree inequalities are too coarse for the rank-three line.
- Generic Graver-basis existence is a reformulation, not the needed positive-gain theorem.
- General exact `eta(C_p^3)` is not assumed for primes `p>=7`.
- Additive-basis donor searches have not forced a relevant maximal-atom target to have U-representation depth at most two.
- No uniform `(p-1)`-full-arc interpolation theorem is claimed.
- The p-full q=2 boundary with `n=3` is explicitly preserved.
- Rational Beatty DCS results and the 2026 length-four cyclic index theorem are nearby structures but do not directly imply the support-four maximal-atom classification; donor overlap remains `CANNOT_CHECK`.

## Claim ceiling

No claim states that `D_3(C_7^3)` is solved, that the all-prime formula is proved or novel, or that general `eta(C_p^3)` is known. Donor theorems receive zero ORION novelty credit; finite computations authorize only their declared domains.
