# C7^3 multiwise Davenport frontier — progress ledger V8

Status: live LLM-assisted ORION research ledger. No novelty authority.

## Closed / verified bounded results

1. **Donor D2 gate.** For prime `p>=5`, `D_2(C_p^3)=(9p-5)/2`; in particular `D_2(C_7^3)=29`. Donor-derived; priority `CANNOT_CHECK`.
2. **Atom corridor.** Any length-37 total-zero `C_7^3` sequence with packing number at most three has a maximum three-atom factorization of one of
   `(8,10,19)`, `(9,9,19)`, `(9,10,18)`, `(9,11,17)`, `(9,12,16)`, `(10,10,17)`.
3. **Support-7 exact closure.** The 54 projective seven-direction classes give 3,418,800 weighted scalar lifts; 14,860 are 7-short-zero-free and all 14,860 four-pack. Hence a length-37 packing obstruction has support at least eight. Primary and independent verifiers agree.
4. **Support-8 one-projective-collision exact closure.** Reusing the same 54 seven-direction classes gives 19,114,200 parameterized lifts; 15,844 are 7-short-zero-free and all 15,844 four-pack. Hence a support-eight obstruction, if any, uses eight distinct projective directions.
5. **Support-8 Type-A geometry.** Eight distinct projective directions reduce to 350 projective classes; three disjoint-four-secant classes are analytically impossible, leaving 347 classes and 5,841,092 class/deficit-profile pairs before scalar/kernel filtering.
6. **Prime-uniform support-complement barrier.** For a zero-sum `p`-short-free sequence of length `N` and support `s`, with `Delta=s(p-1)-N`, the conditions `Delta>=0`, `s+Delta<=p`, `2Delta<=p-2` are impossible. At the candidate critical length this forces support at least `k+4`.
7. **Length-19 projective line-fiber avoidance.** Proper-subsum avoidance localizes to scalar fibers. For a zero-sumfree fiber of length `r>p/2`, the allowed maximal-atom scalar count `d` satisfies `d(d+1)/2<=p-1-r`. At `p=7`, occupancies `3,4,5,6` leave at most `1,1,1,0` scalars. The `10+19` and `9+19` products each have support at least six.
8. **Packing-defect formalism.** With `z(B)` the maximum zero-sum packing and `delta_p(B)=|B|-p z(B)`, the proposed all-`k` formula is equivalent to `delta_p(B)<=M_p=(5p-5)/2` for every zero-sum block. In affine-semigroup language, a counterexample is an above-threshold short-free positive kernel vector terminal under every positive-gain conformal Graver move.
9. **Standard eventual-line coordinates.** Freeze--Schmid reserve `D_0(G)` for the eventual intercept and `k_D(G)` for the stabilization index. The target is exactly `D_0(C_p^3)=M_p` and `k_D(C_p^3)=2`; the branch defect envelope is not renamed `D_0`.
10. **First-failure excess grammar.** If the target first fails at level `m>=3` with overshoot `q>=1`, a maximum atomic factorization has excesses `e_i=|U_i|-p` satisfying `e_i>=q`, `sum e_i=M_p+q`, `(m-1)q<=M_p`, or `e_i=q+f_i` with `sum f_i=M_p-(m-1)q`. Every proper atom subproduct has its expected packing number.
11. **Coding/finite-geometry cap.** A `p`-short-free rank-three sequence has length at most `L_5=62` and `L_p=3p^2-3p-3` for `p>=7` from plane occupancy plus the dimension-three Griesmer bound. Together with the algebraic first-failure cap this gives `K_5=10`, `K_7=15`, and `K_p=(5p-3)/2` for `p>=11`. If a first-failure direction set has no four collinear, then `m<=2p-4`; levels `m>=2p-3` must contain a rich four-secant plane.
12. **Pre-restricted-sum p=7 signature shells.** The purely algebraic shell has 322 signatures and donor pruning leaves 301. The coding cap removes the unique `m=16` shell, giving 321 raw / 300 donor-pruned signatures. These older counts remain valid for their declared stages.
13. **Restricted-sum first-failure front end.** A first failure of overshoot `q` is `(p+q-1)`-short-zero-free. Bhowmik--Schlage-Puchta's `s_{<=(3p-1)/2}(C_p^3)<=6p-3` gives `q<=(p-1)/2`. Zhang's `s_{<=2p-2}(C_p^3)=4p-2` gives a maximum factorization with `min e_i<=p-2`. At `p=7`, the coding-refined 321 signatures reduce to 300 after the q-cap, 299 after the uniform short-atom filter, and **286** after the six exact `(m,q)=(3,1)` atom corridors. Two independent programs freeze digest `2b49f2b6f4579a27165ebe5285292a5966901f1af7793a5cf73f3e9c8d47be19`.
14. **Eta-tail propagation, corrected after CI.** Freeze--Schmid Proposition 3.1(3) implies that if `eta(C_p^3)<=E_p` and the target is exact through

   `T_p(E_p)=max(2, ceil((E_p-1-M_p)/p)-1)`,

   then it propagates to every larger level. The combined first-failure range is therefore

   `3<=m<=min(M_p+1,T_p(E_p))`.

   For the Griesmer-derived `E_p=L_p+1`, the recurrence/coding cutoff is `T_5=10`, `T_7=15`, and `T_p=3p-6` for `p>=11`. For `p>=11` the independent algebraic cap `M_p+1=(5p-3)/2` is smaller, so the final range remains `(5p-3)/2`. An earlier checker incorrectly asserted equality of the final minimum and the eta threshold for all primes; CI exposed this at `p=11`. The mathematical q-cap, short-atom rule and p=7 286-signature digest were independently unaffected.
15. **Solved p=5 control.** The donor value `eta(C_5^3)=33` gives eta-tail threshold 4. The sibling ORION-04 package records the exact early levels and hence `D_k(C_5^3)=5k+10` for all `k>=2`. This is a control, not an external novelty claim for this branch.

## Current general formalism

For `p>=5`, put

`M_p=(5p-5)/2`.

The candidate formula is

`D_k(C_p^3)=kp+M_p=((2k+5)p-5)/2`, `k>=2`.

A first counterexample may be chosen with

- `3<=m<=min(M_p+1,T_p(E_p))` for any verified eta upper bound `E_p`;
- `1<=q<=(p-1)/2`;
- excess signature `e_i=q+f_i`, `f_i>=0`, `sum f_i=M_p-(m-1)q`;
- a maximum factorization containing an atom with excess at most `p-2`;
- no nonempty zero-sum through length `p+q-1`;
- support at least `m+4` at the critical first-failure scale, plus projective direction and plane-deficit restrictions;
- coding length bounds and, at high levels, a mandatory rich projective plane;
- Graver terminality: no conformal positive-gain move may increase the factorization length.

Thus the all-`k` problem has split into two modules:

1. **restricted-sum front end** — finite bounds on `(m,q)` and forced short atoms;
2. **finite rank-three augmentation core** — prove every remaining positive kernel vector admits a positive-gain conformal refactor.

The second module is the missing theorem.

## Strongest current `C_7^3` length-37 semantics

If `B` is zero-sum over `C_7^3`, `|B|=37`, and `z(B)<=3`, then

- `z(B)=3` and this is the `(p,m,q)=(7,3,1)` first-failure slice;
- `|supp(B)|>=8`;
- support eight uses eight distinct projective directions;
- every maximum three-atom factorization lies in one of the six corridors;
- the two maximal-atom corridors obey the line-fiber avoidance grammar;
- every maximum factorization is Graver-terminal.

No `D_3(C_7^3)` value is claimed yet.

## Retained failures / non-promoted routes

- The first unstructured support-7 enumeration exceeded its host budget; the projective reformulation is the successful representation repair.
- Global cardinality of the proper-subsum set is too coarse; projective scalar fibers retain the needed rank information.
- No verified rank-three inverse theorem yet kills the two maximal-atom corridors.
- Appending `g^p` need not increase packing by exactly one, so eventual linearity alone does not imply stabilization at `k=2`.
- Generic Graver test-set existence is a reformulation, not the positive-gain augmentation theorem.
- Exact `eta(C_p^3)` is not assumed for general primes `p>=7`; the lower construction `8p-7` is not used as an upper bound.
- The failed `e3ffec52` workflow assertion conflated the eta/coding threshold with its minimum with `M_p+1`; it is preserved as a checker failure and corrected in the next commit rather than relabeled green.

## Next discriminators

1. **Rank-three augmentation theorem.** Use hereditary atom-subproduct rigidity plus the short atom `e<=p-2` to force a positive-gain two- or three-atom refactor.
2. **Support-8 Type-A exact closure.** Finish the 347 eight-distinct-direction projective classes; this is the smallest unresolved `(7,3,1)` face.
3. **Length-19 corridors.** Continue `(8,10,19)` and `(9,9,19)` with line-fiber allowed-scalar lists, primitive kernels and conformal three-splitting.
4. **Restricted-sum donor ladder.** Any sharper `s_{<=h}(C_p^3)` between `p` and `2p-2` directly improves the q-front end.
5. **Weighted projective incidence.** Combine line-richness penalties, total projective deficit and Property C to eliminate high first-failure levels before kernel enumeration.
6. **Donor saturation.** Continue searches under `D_0`, `k_D`, generalized Noether `beta_k`, sets of lengths, products of atoms, `nu(G)`, Graver augmentation and rank-three projective-code terminology.

## Claim ceiling

No claim states that `D_3(C_7^3)` is solved, that the candidate all-`k` formula is proved or novel, or that general `eta(C_p^3)` is known. Donor theorems receive zero ORION novelty credit; finite computation authorizes only its declared domain.
