# C7^3 multiwise Davenport frontier — progress ledger V14

Status: live LLM-assisted ORION research ledger. No novelty authority.

## Verified general structural spine

The current target is

`D_k(C_p^3)=kp+(5p-5)/2=((2k+5)p-5)/2` for prime `p>=5`, `k>=2`.

With `M_p=(5p-5)/2`, a first failure may be chosen with

- `z(B)=m`, `|B|=pm+M_p+q`, `q>=1`;
- every proper atom subproduct having its displayed packing number;
- atom excesses `e_i>=q`, `sum e_i=M_p+q`, `(m-1)q<=M_p`;
- no nonempty zero-sum through length `p+q-1`;
- `q<=(p-1)/2` by the Bhowmik--Schlage-Puchta restricted-sum bound;
- a maximum factorization containing an atom of excess at most `p-2` by Zhang's rank-three theorem;
- finite first-failure levels from coding/algebraic bounds: `K_5=10`, `K_7=15`, `K_p=(5p-3)/2` for `p>=11`;
- eta-tail propagation from any verified upper bound on `eta(C_p^3)`;
- q-dependent rank-two plane occupancy `<=3p-q-2`, with strict rich-plane cap `3p-q-3`;
- equality for `q>=2` forcing the exact rank-two grammar and a canonical atom of length `p+q` into a maximum factorization;
- weighted projective line-deficit inequalities and full-multiplicity directions forming an arc;
- low-deficit tangent packing for `q>=3`;
- saturated full-arc scalar interpolation for full arcs of sizes `p+1` and, when `p>=11`, `p`;
- the p-group Geroldinger--Yang two-term avoidance for terminal maximal-atom products;
- terminality under every positive-gain conformal Graver move.

## Low-deficit tangent packing

For `q>=3`, put `a=floor((q-1)/2)`. If `f` projective directions have full multiplicity and `L` deficient directions have deficit in `1..a`, then

`L<=p+2-f`.

Together with total direction deficit `Delta`,

`L>=ceil(((a+1)(r-f)-Delta)/a)`

and hence

`f >= (a+1)r-Delta-a(p+2)`.

For `q=3`, `f>=2r-Delta-(p+2)`. See `LOW_DEFICIT_TANGENT_PACKING_V1.md`.

## Saturated full-conic scalar uniqueness

For odd prime `p>=7`, a full `(p+1)`-arc is a conic. If `D=(d_0,d_1,d_2)` is an occupied off-conic direction of deficit exactly `q-1`, saturated conic secants force the actual full-direction scalar profile

`lambda(t)=mu_D (d_0d_2-d_1^2)/(d_0t^2-2d_1t+d_2)`.

Two distinct minimal-deficit off-conic directions would make two quadratic denominators proportional at at least `p-4>=3` field values, hence projectively equal. Therefore a full conic supports at most one deficit-`q-1` off-conic direction.

If it has `n>=2` occupied off-conic directions, total projective deficit satisfies

`Delta>=qn-1`.

This yields the first integral direction-floor bump. With

`R=(N-p-1)/(p-2)`

integral, equality `r=R` is impossible for `q>=3,R>=p+2`, and for `q=2,p>=7,R>=p+3`. One explicit q=2 family is

`p congruent 1 mod 4`, `p>=13`, `m=(5p-13)/4`,

with the improved floor

`r>=(5p+7)/4`.

The p=5 hostile control has 30 compatible distinct saturated-center pairs, so the p>=7 threshold is retained exactly.

See `SATURATED_CONIC_SCALAR_UNIQUENESS_V1.md`.

## New p-full arc interpolation layer

For prime `p>=11`, every p-arc in `PG(2,p)` extends to a unique `(p+1)`-arc/conic. If the p full directions are the conic with one completion point `R` deleted, then any occupied direction outside the completed conic with deficit exactly `q-1` again imposes the reciprocal-quadratic scalar profile on all but at most three full arc points.

Two distinct off-conic minimal-deficit centers would therefore have profiles agreeing at at least `p-7>=4` finite parameters, forcing the centers to coincide. Hence:

> relative to a p-point full arc, at most one occupied direction **outside its conic completion** has deficit `q-1` for `p>=11`.

The missing completion point is a genuine exceptional direction: it lies on no secant through two full arc points and may have deficit below `q-1`.

If exactly p directions are full and `n=r-p>=2` are deficient, the total deficit satisfies

`Delta>=qn-q`.

At the integral p-full boundary

`S=(N-p)/(p-2) in Z`, `n=S-p`,

equality `r=S` forces at least p full directions. Accounting for both possible cases—exactly p full or all p+1 full—gives the corrected strictness criterion

`(q-1)n>q+1  =>  r>=S+1`.

Thus equality is impossible for:

- q=2 with `n>=4`;
- q=3 with `n>=3`;
- q>=4 with `n>=2`.

The earlier scratch example `p=11,q=2,m=10` has `n=3` and is **not** promoted: a full conic plus deficit pattern `(1,2)` remains compatible with the present theorem.

An explicit complementary q=2 family is obtained for

`p congruent 3 mod 4`, `p>=19`, `m=(5p-15)/4`.

Here

`S=(5p+1)/4`, `n=(p+1)/4>=5`,

so

`r>=(5p+5)/4`.

Together with the `p congruent 1 mod 4` conic family, every prime `p>=13` now has an explicit high-level q=2 slice where the raw full-direction arc floor is provably strict.

Independent deleted-conic gain-graph replays show the threshold is real:

- p=5: 125 compatible distinct off-conic center pairs;
- p=7: 84 compatible;
- p=11: 0 compatible;
- p=13: 0 compatible.

See `SATURATED_P_ARC_SCALAR_UNIQUENESS_V1.md`.

## Exact p=7 length-37 frontier

For zero-sum `B` over `C_7^3` with `|B|=37` and `z(B)<=3`:

- `z(B)=3`, the `(p,m,q)=(7,3,1)` slice;
- support is at least eight;
- support eight must use eight distinct projective directions;
- every maximum three-atom factorization has one of `(8,10,19)`, `(9,9,19)`, `(9,10,18)`, `(9,11,17)`, `(9,12,16)`, `(10,10,17)`;
- support seven is completely closed: 3,418,800 lifts, 14,860 short-free, all four-pack;
- support-eight one-projective-collision is completely closed: 19,114,200 lifts, 15,844 short-free, all four-pack;
- the smallest unresolved support-eight face is the eight-distinct-direction Type-A branch over 347 projective classes and 5,841,092 class/deficit-profile pairs;
- the two length-19 corridors obey both scalar line-fiber avoidance and U-representation depth at least three.

No `D_3(C_7^3)` value is claimed yet.

## Exact first-failure closures beyond the length-37 slice

### `(p,q,m,r)=(7,2,8,13)`

At length 73 and `r=13`, total direction deficit five forces `6^8 5^5`, hence a full conic plus five deficit-one directions. Saturated-conic scalar uniqueness gives an analytic contradiction, so

`(p,q,m)=(7,2,8) => r>=14`.

The finite controls remain: 5,166 conic-plus-five extensions, all rank-13 systems full rank and all ratio graphs inconsistent; digest

`0eb3a99b0bb1c30595f9b6b58e74b980c094c5d5754a50f726d82aed4711d82c`.

### `(p,q,m,r)=(7,3,6,11)`

Here `N=60`, `Delta=6`. Tangent packing forces at least seven full directions. Seven full directions would require at least two secant-free deficit-one points, but a 7-arc has at most one secant-free extension. Eight full directions force a conic plus three deficit-two directions, contradicted by saturated-conic scalar uniqueness. Therefore

`(p,q,m)=(7,3,6) => r>=12`.

The finite controls remain: 4,466 conic-plus-three extensions, all rank-11 systems full rank and all gain graphs inconsistent; digest

`7f858cbd83b9922d4fc0122baa2a34680216033f28bd948aa225bde055c85cce`.

## Current p=7 first-failure signature shell

The purely algebraic shell has 322 signatures. Coding reduces it to 321; the q-cap, uniform short-atom theorem and exact `(m,q)=(3,1)` atom corridors reduce the current necessary cover to **286** excess signatures, digest

`2b49f2b6f4579a27165ebe5285292a5966901f1af7793a5cf73f3e9c8d47be19`.

The geometric closures remove projective realizations inside that signature shell; they do not alter the 286 length-signature count itself.

## Current missing theorem

The all-prime problem remains a finite **rank-three augmentation theorem**:

every surviving first-failure positive kernel vector satisfying the restricted-sum, atom-excess, q-dependent plane, tangent-packing, large-arc interpolation, weighted-secant, maximal-atom-depth and hereditary-subproduct constraints must admit a positive-gain two- or three-atom conformal refactor.

The geometric interface is now systematic: saturated rank-two planes impose rational scalar profiles, while large-arc completion turns compatibility into low-degree polynomial interpolation.

## Next discriminators

1. Search for controlled interpolation rigidity for `(p-1)` full arcs. Uniform completion is unavailable in the small odd-prime cases, so this requires either a large-arc theorem with explicit exceptions or a different projective-code invariant.
2. Continue `(p,q,m)=(7,2,8)` from `r>=14`; the full-conic subcase is constrained by `Delta>=qn-1` and has sharply restricted deficit patterns.
3. Continue `(p,q,m)=(7,3,6)` from `r>=12` using tangent packing before scalar search.
4. Apply the conic/tangent framework to `(q,m,r)=(3,5,10)`, where `f=3` is already excluded.
5. Finish the eight-distinct-direction support-eight Type-A `(7,3,1)` closure.
6. Combine maximal-atom U-depth >=3 with exact short-atom/rank-two subsum structure in `(8,10,19)` and `(9,9,19)`.
7. Seek a local-`nu` three-deletion theorem and continue donor saturation under generalized Noether numbers, sets of lengths, restricted sumsets, projective codes and Graver augmentation.

## Retained negative / non-promoted routes

- Eventual linearity alone does not imply stabilization at `k=2`.
- Generic Graver-basis existence is a reformulation, not the needed positive-gain theorem.
- General exact `eta(C_p^3)` is not assumed for primes `p>=7`.
- Additive-basis donor searches have not yet forced a relevant maximal-atom target to have representation depth at most two.
- The full-conic interpolation theorem fails at p=5; the p-full interpolation theorem still has compatible pairs at p=5 and p=7.
- No uniform claim is made for `(p-1)` full arcs because complete `(p-1)`-arcs exist for several small odd orders.
- The corrected p-full case split explicitly preserves the q=2,n=3 boundary rather than overclaiming a strict bump.

## Claim ceiling

No claim states that `D_3(C_7^3)` is solved, that the all-prime formula is proved or novel, or that general `eta(C_p^3)` is known. Donor theorems receive zero ORION novelty credit; finite computations authorize only their declared domains.
