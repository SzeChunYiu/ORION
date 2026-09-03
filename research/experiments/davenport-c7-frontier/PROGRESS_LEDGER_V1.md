# C7^3 multiwise Davenport frontier — progress ledger V10

Status: live LLM-assisted ORION research ledger. No novelty authority.

## Verified structural spine

1. **Exact donor base.** For prime `p>=5`, `D_2(C_p^3)=(9p-5)/2`; in particular `D_2(C_7^3)=29`.
2. **Length-37 atom corridor.** A `C_7^3` zero-sum length-37 packing obstruction has a maximum three-atom factorization of one of `(8,10,19)`, `(9,9,19)`, `(9,10,18)`, `(9,11,17)`, `(9,12,16)`, `(10,10,17)`.
3. **Support-7 exact closure.** All 3,418,800 projective/scalar/multiplicity lifts were replayed; 14,860 are 7-short-free and every one four-packs. Hence support is at least eight.
4. **Support-8 one-projective-collision closure.** All 19,114,200 parameterized lifts were replayed; 15,844 are 7-short-free and all four-pack. Hence any support-eight obstruction uses eight distinct projective directions.
5. **Support-8 Type-A residual.** Eight distinct directions reduce to 350 projective classes; after the existing four-secant/Property-C exclusions, 347 classes and 5,841,092 class/deficit-profile pairs remain before scalar/kernel filtering.
6. **Packing-defect equivalence.** With `z(B)` the maximum zero-sum packing, `delta_p(B)=|B|-p z(B)`. The candidate all-`k` formula is equivalent to `delta_p(B)<=M_p=(5p-5)/2` for every zero-sum block. A counterexample is an above-threshold finite-box kernel vector terminal under every positive-gain conformal Graver move.
7. **Standard asymptotic coordinates.** Freeze--Schmid's `D_0(G)` is the eventual intercept and `k_D(G)` the stabilization index. The target is exactly `D_0(C_p^3)=M_p` and `k_D(C_p^3)=2`.
8. **First-failure grammar.** If the target first fails at level `m>=3` with overshoot `q>=1`, a maximum atomic factorization has excesses `e_i=|U_i|-p` with `e_i>=q`, `sum e_i=M_p+q`, `(m-1)q<=M_p`, and every proper atom subproduct has its expected packing number.
9. **Restricted-sum front end.** A first failure is `(p+q-1)`-short-zero-free. Bhowmik--Schlage-Puchta gives `q<=(p-1)/2`; Zhang gives a maximum factorization with `min e_i<=p-2`.
10. **Finite level cap.** The Griesmer/plane argument plus the algebraic first-failure cap gives `K_5=10`, `K_7=15`, and `K_p=(5p-3)/2` for primes `p>=11`. Freeze--Schmid's recurrence also gives the eta-tail gate `3<=m<=min(M_p+1,T_p(E_p))` for any verified upper bound `eta(C_p^3)<=E_p`.
11. **p=7 signature shell.** Algebraic: 322. After coding: 321. After `q<=3`: 300. After the uniform short-atom filter: 299. After the six exact `(m,q)=(3,1)` corridors: **286**. Independent digest: `2b49f2b6f4579a27165ebe5285292a5966901f1af7793a5cf73f3e9c8d47be19`.
12. **Maximal-atom line fibers.** In the `(8,10,19)` and `(9,9,19)` corridors, the 19-atom is projectively separated and the companion scalar fibers obey the exact line-fiber avoidance grammar.
13. **Two-term maximal-atom avoidance.** Geroldinger--Yang's p-group `nu` theorem implies: if maximal atom `U` and atom `V` satisfy `z(UV)=2`, then `Sigma_2(U)` is disjoint from `Sigma_{3..|V|-1}(V)`. Equivalently, short negative V-subsums have U-representation depth at least three. For the 10-atom corridor the negative range is sizes `1..7`; for the 9-atom corridor it is `1..6`. The independent affine-coset replay checks 900,748 ordered pairs.
14. **q-dependent rank-two plane cap.** Exact rank-two restricted-sum theory gives

   `s_{<=p+q-1}(C_p^2)=3p-q-1`,

   hence every first-failure plane has occupancy at most

   `3p-q-2`.

   For `q>=2`, equality forces the exact three-direction pattern

   `e1^(p-1) e2^(p-1) (e1+e2)^(p-q)`.

   A four-direction plane therefore has the strict cap `3p-q-3`. Saturation also forces the canonical atom `e1^q e2^q (e1+e2)^(p-q)` of length `p+q` and excess exactly `q` into a maximum factorization.
15. **Weighted arc consequence for q>=2.** If `r` projective directions have weights `w_i` and deficits `d_i=p-1-w_i`, `Delta=sum d_i`, then every projective line with `t>=3` occupied directions satisfies

   `sum_line d_i >= (t-3)(p-1)+(q-1)`,

   with `+q` instead of `+(q-1)` for `t>=4`. Full-multiplicity directions form an arc, so

   `r >= max(ceil(N/(p-1)), ceil((N-p-1)/(p-2)))`.

   If `Delta<q-1`, the entire direction set is an arc and has size at most `p+1`.
16. **p=7 high-overshoot direction refinement.** The new weighted-arc condition raises the projective-direction floor by one in exactly four slices: `(q,m)=(2,6),(2,7),(3,5),(3,6)`. The new floors are respectively `11,12,10,11`. No whole `(m,q)` level is eliminated by this step alone.
17. **Solved p=5 control.** The sibling ORION-04 package plus `eta(C_5^3)=33` gives `D_k(C_5^3)=5k+10` for every `k>=2`; retained only as a control for the general mechanism.

## Current target

For `p>=5`, the conjectured line is

`D_k(C_p^3)=kp+(5p-5)/2=((2k+5)p-5)/2`, `k>=2`.

A first counterexample can now be required to satisfy simultaneously:

- finite `(m,q)` range with `q<=(p-1)/2`;
- excess slack `e_i=q+f_i`, `sum f_i=M_p-(m-1)q`;
- a short atom with `e_i<=p-2`;
- q-dependent plane occupancy `<=3p-q-2`;
- exact saturated-plane grammar or an extra unit of plane deficit;
- weighted projective secant inequalities and strengthened direction floors;
- maximal-atom representation-depth constraints when a `D(G)`-atom occurs;
- hereditary rigidity of every proper atom subproduct;
- terminality under positive-gain Graver augmentation.

The missing theorem is still the **finite rank-three augmentation theorem**: every surviving first-failure kernel must admit a positive-gain two- or three-atom refactor.

## Retained negative / non-promoted routes

- Unstructured support enumeration remains inferior to the projective reduction.
- Eventual linearity does not imply stabilization at `k=2`: appending a pure `g^p` block need not raise packing by exactly one.
- Generic Graver-basis existence is a reformulation, not the needed rank-three positive-gain theorem.
- General exact `eta(C_p^3)` is not assumed for primes `p>=7`.
- The additive-basis donor sweep after the two-term `nu` lemma did not produce a theorem forcing every relevant target to have U-depth at most two; no corridor elimination is claimed from that route.
- The q-dependent rank-two cap improves geometry but does not by itself delete a complete first-failure `(m,q)` level.

## Next discriminators

1. **Saturated-plane factorization attack.** If a plane is saturated, exploit the forced excess-`q` atom of length `p+q`; otherwise charge the extra plane deficit globally until a Graver move is forced.
2. **Representation-depth corridor attack.** Combine U-depth `>=3` with exact short-atom/rank-two subsum structure; kill a maximal-atom corridor if any required negative V-subsum is forced to have U-depth `<=2`.
3. **Support-8 Type-A exact closure.** Finish the 347 eight-distinct-direction classes, retaining complete primitive-core certificates for any survivor.
4. **Weighted projective supersaturation.** Use the q-dependent secant deficit inequalities together with lower bounds on trisecants/four-secants to raise support or force a saturated plane.
5. **Local-`nu` extension.** Seek a three-deletion analogue for maximal atoms in `C_p^3`.
6. **Donor saturation.** Continue searches under `D_0`, `k_D`, generalized Noether numbers, sets of lengths, products of atoms, local `nu`, restricted sumsets, projective codes, and Graver augmentation.

## Claim ceiling

No claim states that `D_3(C_7^3)` is solved, that the all-prime formula is proved or novel, or that general `eta(C_p^3)` is known. Donor theorems receive zero ORION novelty credit; finite computations authorize only their declared domains.
