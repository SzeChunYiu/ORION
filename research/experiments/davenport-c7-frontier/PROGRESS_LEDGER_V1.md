# C7^3 multiwise Davenport frontier — progress ledger V12

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
- eta-tail propagation: any verified `eta(C_p^3)<=E_p` reduces the remaining levels to `m<=min(M_p+1,T_p(E_p))`;
- q-dependent rank-two plane occupancy `<=3p-q-2`, with strict rich-plane cap `3p-q-3`;
- equality for `q>=2` forcing `e1^(p-1)e2^(p-1)(e1+e2)^(p-q)` and the canonical atom `e1^q e2^q (e1+e2)^(p-q)` of length `p+q` into a maximum factorization;
- weighted projective line-deficit inequalities and full-multiplicity directions forming an arc;
- the p-group van-Emde-Boas / Geroldinger--Yang two-term avoidance for terminal maximal-atom products;
- terminality under every positive-gain conformal Graver move.

### New prime-uniform low-deficit tangent packing

For `q>=3`, put `a=floor((q-1)/2)`. If `f` projective directions have full multiplicity and `L` deficient directions have deficit in `1..a`, then

`L<=p+2-f`.

Low directions cannot lie on secants of the full arc, and two low directions cannot occupy the same remaining line through a full point. Together with total deficit `Delta`, this gives

`L>=ceil(((a+1)(r-f)-Delta)/a)`

and the useful full-direction lower bound

`f >= (a+1)r-Delta-a(p+2)`.

For `q=3` this is `f>=2r-Delta-(p+2)`. See `LOW_DEFICIT_TANGENT_PACKING_V1.md`.

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

At length 73 and 13 projective directions, total direction deficit five forces weight pattern `6^8 5^5`. The eight full directions form a conic. Two independent generators give exactly 5,166 valid five-point off-conic extensions, digest

`0eb3a99b0bb1c30595f9b6b58e74b980c094c5d5754a50f726d82aed4711d82c`.

Every saturated conic secant forces exact scalar addition. All 5,166 primary compatibility matrices have rank 13; the independent multiplicative secant-ratio verifier rejects all 5,166. Hence

`(p,q,m)=(7,2,8) => r>=14`.

### New closure: `(p,q,m,r)=(7,3,6,11)`

Here `N=60`, `Delta=6`. Low-deficit tangent packing forces at least seven full directions.

- If `f=7`, the four deficient directions have at least two deficit-one points. Such points must be secant-free relative to the full 7-arc. But a 7-arc in `PG(2,7)` has at most one secant-free extension: two would give two 8-arcs/conics sharing seven points, hence the same conic and the same unique missing point. So `f=7` is impossible.
- If `f=8`, the full directions form a conic. Every off-conic point lies on a conic secant, so the three positive deficits summing to six must all equal two. The weight pattern is `6^8 4^3`.

After canonical conic normalization, two independent generators produce exactly **4,466** admissible three-point off-conic extensions. Candidate digest:

`7f858cbd83b9922d4fc0122baa2a34680216033f28bd948aa225bde055c85cce`.

Every conic secant through a deficient point saturates the q-dependent rank-two plane bound and forces exact scalar addition. All 4,466 primary 11-variable systems have rank 11 over `F_7`. An independent 11-variable bipartite multiplicative gain-graph verifier finds every candidate connected and ratio-inconsistent.

Therefore

`(p,q,m)=(7,3,6) => r>=12`.

See `P7_Q3_M6_R11_CLOSURE_V1.md`.

## Current p=7 first-failure signature shell

The purely algebraic shell has 322 signatures. Coding reduces it to 321; the q-cap, uniform short-atom theorem and exact `(m,q)=(3,1)` atom corridors reduce the current necessary cover to **286** excess signatures, digest

`2b49f2b6f4579a27165ebe5285292a5966901f1af7793a5cf73f3e9c8d47be19`.

The new geometric closures remove projective realizations inside that signature shell; they do not alter the 286 length-signature count itself.

## Current missing theorem

The all-prime problem remains a finite **rank-three augmentation theorem**:

every surviving first-failure positive kernel vector satisfying the restricted-sum, atom-excess, q-dependent plane, tangent-packing, weighted-secant, maximal-atom-depth and hereditary-subproduct constraints must admit a positive-gain two- or three-atom conformal refactor.

The emerging geometric interface is a labelled saturated-plane gain graph: each saturated rank-two plane converts a projective trisecant into multiplicative scalar constraints. Boundary configurations fail when that gain graph is forced to be unbalanced.

## Next discriminators

1. Continue `(p,q,m)=(7,3,6)` from the improved floor `r>=12`; use tangent packing to enumerate only feasible full-direction counts before any scalar search.
2. Continue `(p,q,m)=(7,2,8)` from `r>=14`; seek a secant-supersaturation theorem forcing either a saturated gain graph or a direct Graver move.
3. Apply low-deficit tangent packing to `(q,m,r)=(3,5,10)`, where it already eliminates the `f=3` full-direction subcase.
4. Finish the eight-distinct-direction support-eight Type-A `(7,3,1)` closure.
5. Combine maximal-atom U-depth >=3 with exact short-atom/rank-two subsum structure in `(8,10,19)` and `(9,9,19)`.
6. Seek a local-`nu` three-deletion theorem for maximal atoms in `C_p^3`.
7. Continue donor saturation under generalized Noether numbers, sets of lengths, local `nu`, restricted sumsets, projective codes, gain graphs and Graver augmentation.

## Retained negative / non-promoted routes

- Eventual linearity alone does not imply stabilization at `k=2`.
- Generic Graver-basis existence is a reformulation, not the needed positive-gain theorem.
- General exact `eta(C_p^3)` is not assumed for primes `p>=7`.
- Additive-basis donor searches have not yet forced a relevant maximal-atom target to have representation depth at most two.
- q-dependent rank-two caps do not by themselves delete complete `(m,q)` levels; scalar compatibility is essential in the closed conic faces.
- The earlier eta-tail checker failure remains preserved as a failed receipt and was corrected rather than relabeled.

## Claim ceiling

No claim states that `D_3(C_7^3)` is solved, that the all-prime formula is proved or novel, or that general `eta(C_p^3)` is known. Donor theorems receive zero ORION novelty credit; finite computations authorize only their declared domains.
