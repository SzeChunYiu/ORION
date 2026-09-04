# C7^3 multiwise Davenport frontier — progress ledger V17

Status: live LLM-assisted ORION research ledger. No novelty authority.

## General target and first-failure formalism

For prime `p>=5`, put `M_p=(5p-5)/2`. The candidate line is

`D_k(C_p^3)=kp+M_p=((2k+5)p-5)/2`, `k>=2`.

Equivalently every zero-sum block `B` should satisfy `|B|-p z(B)<=M_p`; in Freeze--Schmid notation the target is `D_0(C_p^3)=M_p` with stabilization index `k_D=2`.

A first failure can be chosen with

`z(B)=m`, `|B|=pm+M_p+q`, `q>=1`,

and maximum atomic factorization `B=U_1...U_m`. Writing `e_i=|U_i|-p`, verified constraints include:

- every proper atom subproduct has exactly its displayed packing number;
- `e_i>=q`, `sum e_i=M_p+q`, `(m-1)q<=M_p`;
- no nonempty zero-sum through length `p+q-1`;
- `q<=(p-1)/2` by Bhowmik--Schlage-Puchta;
- Zhang forces a maximum factorization with `min e_i<=p-2`;
- finite first-failure levels `K_5=10`, `K_7=15`, `K_p=(5p-3)/2` for `p>=11` from coding plus the algebraic cap;
- any verified `eta(C_p^3)<=E_p` gives the alternative tail threshold `m<=min(M_p+1,T_p(E_p))`;
- every survivor is terminal under positive-gain conformal Graver moves.

## Rank-two, projective and pair geometry

The exact rank-two restricted-sum spectrum gives every first-failure plane occupancy

`<=3p-q-2`,

with strict cap `3p-q-3` for four or more occupied projective directions. For `q>=2`, equality forces the exact rank-two grammar

`e1^(p-1)e2^(p-1)(e1+e2)^(p-q)`

and the canonical atom `e1^q e2^q (e1+e2)^(p-q)` of length `p+q` into a maximum factorization.

Direction deficits obey

`sum_line d_i >= (t-3)(p-1)+(q-1)`,

with an additional unit for `t>=4`. Full directions form an arc. For `q>=3`, low-deficit tangent packing gives, with `a=floor((q-1)/2)`,

`L<=p+2-f`

and

`f >= (a+1)r-Delta-a(p+2)`.

Large full arcs additionally satisfy scalar interpolation rigidity:

- a full `(p+1)`-arc/conic for odd `p>=7` has at most one deficit-`q-1` off-conic occupied direction; with `n>=2` off-conic directions, `Delta>=qn-1`;
- for `p>=11`, a full p-arc extends uniquely to a conic and has the analogous uniqueness outside the missing completion point;
- these yield explicit infinite q=2 direction-floor strictness families in both prime residue classes mod 4.

For any atom pair `P=U_iU_j`, put `E=e_i+e_j`. Hereditary rigidity gives `z(P)=2`, pair short-free depth

`H_ij=max(p+q-1,E-p+1)`,

and pair-plane cap

`|P_K|<=4p-3-H_ij`

for every rank-two subgroup `K`. If the whole pair had rank at most two, then

`e_i+e_j<=p-q-3`.

Hence `e_i+e_j>p-q-3` forces pair rank three. In particular every p=7 pair for q=2,3 is rank three, and every atom pair in all six length-37 corridors is rank three.

## Support-four maximal atoms: prime-uniform classification

If a maximal atom `U` of length `3p-2` has exactly four support values, then its support is a projective four-circuit and its multiplicities are, after reordering,

`boxed{(p-1,p-1,a,p-a)}`, `1<=a<=(p-1)/2`.

The proof converts atom minimality into a disjoint partition of finite rational Beatty jump sets `C_a={t:[ta]_p<a}`. For `p>=11`, moments 2,4,6,8 force

`sum x_i=sum x_i^3=sum x_i^5=sum x_i^7=2`, `x_i=a_i^{-1}`,

and a four-pole rational-function collapse forces `{x_i}={1,1,u,-u}`. `p=5,7` are direct finite base cases with independent primitive-kernel scans.

Up to automorphism, the support-four maximal atom is

`e1^(p-1)e2^(p-1)e3^a(e3-a^{-1}(e1+e2))^(p-a)`.

For p=7 only `a=1,2,3` occur.

## New exact closure: support-four `(8,10,19)` branch

Let the 19-atom be one of the three p=7 canonical support-four maximal atoms `U_a`. Let `V` be the 10-atom and `W` the 8-atom.

The pair `U_aV` must be 9-short-zero-free. Two independent exhaustive enumerators give exactly

- `a=1`: 538 length-10 pair companions;
- `a=2`: 24;
- `a=3`: 0.

Extending by a zero-sum length-8 `W` while preserving whole-sequence 7-short-freeness gives:

- extendable pair candidates `229,6,0`;
- completion counts `2772,24,0`;
- total factor triples `2796`;
- distinct length-37 multiplicity vectors `1572`.

Every one of the 2796 factor triples admits a four-pack.

The primary search maintains cardinality-indexed subset-sum sets and uses a smallest-two-block four-pack criterion. The independent verifier instead uses occurrence-mask enumeration against a minimum-base-depth table and tests four-packs by complementary pairs of zero-sum block unions. Both reproduce all counts.

Therefore:

> **No `(8,10,19)` length-37 obstruction can have its 19-atom supported on exactly four elements.**

Every surviving `(8,10,19)` candidate now satisfies

`boxed{|supp(U_19)|>=5.}`

See `SUPPORT4_81019_CLOSURE_V1.md`.

### Retained failed receipt

An exploratory Python recursion earlier reported only 55 `(V,W)` completions and incorrectly removed the `a=2` type. Its recursive subset-sum state was restored incorrectly across sibling branches, producing false negatives. The rejected undercount is preserved in `FAILURE_SUPPORT4_81019_PY_STATE_RESTORE_V1.md`. The correct independently reproduced total is 2796.

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
- `(8,10,19)` now additionally has `|supp(U_19)|>=5`;
- both maximal-atom corridors obey scalar line-fiber avoidance, U-representation depth at least three, pair rank three and pair-plane caps 16/17.

No `D_3(C_7^3)` value is claimed yet.

## Exact higher first-failure closures at p=7

- `(q,m)=(2,8)`: the minimum 13-direction face is impossible, so `r>=14`.
- `(q,m)=(3,6)`: the minimum 11-direction face is impossible, so `r>=12`.

Finite conic scalar censuses remain independent controls; the analytic conic interpolation theorem now explains both closures.

## Current p=7 excess-signature shell

The necessary length-signature shell is reduced from 322 algebraic signatures to **286** after coding, the overshoot cap, Zhang's short-atom theorem and the exact `(m,q)=(3,1)` corridors. Digest:

`2b49f2b6f4579a27165ebe5285292a5966901f1af7793a5cf73f3e9c8d47be19`.

Geometric and pair-rank closures prune realizations inside this shell without changing its length-signature count.

## Current missing theorem

The all-prime problem remains a finite **rank-three augmentation theorem**:

every surviving first-failure positive kernel vector satisfying the restricted-sum, excess-signature, pair-rank, pair-plane, q-dependent plane, tangent-packing, large-arc interpolation, maximal-atom-depth, support-four classification and hereditary-subproduct constraints must admit a positive-gain two- or three-atom conformal refactor.

## Next discriminators

1. **Support-four `(9,9,19)` branch.** Repeat the canonical `a=1,2,3` attack with the necessary additional `z(UV)=2` filter, since 8-short-freeness alone allows a `(9,9,10)` three-pack in length 28.
2. **Support>=5 `(8,10,19)` branch.** Feed pair-plane cap 16, maximal-atom projective separation, line-fiber avoidance and U-depth >=3 into projective support geometry.
3. Classify the 18-term short-short pair in the maximal-atom corridors: it is 7-short-free, rank three, and every proper zero-sum has length 8--10.
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
