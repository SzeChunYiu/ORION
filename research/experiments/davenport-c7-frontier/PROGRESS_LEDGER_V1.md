# C7^3 multiwise Davenport frontier — progress ledger V7

Status: live LLM-assisted ORION research ledger. No novelty authority.

## Closed / verified bounded results

1. **Donor-derived D2 gate.** For prime `p>=5`, `a>=1`, `n=p^a`, Freeze--Schmid + the classical p-group Davenport value + Zhao Lemma 4.4 give `D_2(C_n^3)=(9n-5)/2`; in particular `D_2(C_7^3)=29`. Derivation complete; priority `CANNOT_CHECK`.
2. **Binary-cube support closure.** The natural seven-point binary-cube support has exactly 10 length-37 total-zero profiles in 4 coordinate-permutation orbits; every profile has packing number exactly 4. Two differently structured checkers agree.
3. **Six-triple atom corridor.** Any total-zero length-37 sequence with packing number at most three factors into exactly three atoms with sorted length triple one of `(8,10,19)`, `(9,9,19)`, `(9,10,18)`, `(9,11,17)`, `(9,12,16)`, `(10,10,17)`.
4. **Zhao `4p` resonance.** For `C_p^3`, `p>=5`, every admissible Zhao-Lemma-4.4 coefficient vanishes modulo `p` at total-zero length `4p`. This is a proof-instrument statement, not a physical phase theorem.
5. **Support-7 projective reduction.** A hypothetical length-37 obstruction with support seven projects to seven distinct points of `PG(2,7)` with no four collinear.
6. **Projective cover regeneration.** A deterministic frame-normalized generator enumerates 18,451 frame-containing candidates and quotients them to exactly 54 projective support classes: 53 with a collinear triple and one ordinary seven-arc. The external coding-theory count `53+1` is a control, not executable cover authority.
7. **Complete support-7 closure.** Across all 54 support classes, 7,400 normalized full-support kernel vectors and 462 positive deficit-weight profiles yield exactly 3,418,800 total-zero scalar/multiplicity lifts. Exactly 14,860 survive the necessary 7-short-zero-free filter, and all 14,860 admit four pairwise disjoint nonempty zero-sum subsequences. Therefore any hypothetical length-37 total-zero obstruction with packing number at most three has support at least eight. Primary and differently structured independent verifiers agree.
8. **Complete support-8 one-projective-collision closure.** Reusing the 54 seven-direction arc classes, 7,400 normalized full-support kernels and 2,583 doubled-direction/profile/local states give 19,114,200 parameterized lifts. Exactly 15,844 are 7-short-zero-free, and all 15,844 four-pack. Six primary and six structurally independent CI shards replay the complete class cover. Thus every support-8 obstruction, if one exists, uses eight distinct projective directions.
9. **Prime-uniform short-free complement barrier.** For a zero-sum `p`-short-zero-free sequence over any exponent-`p` group, support deficit `Delta=s(p-1)-N` is impossible whenever `Delta>=0`, `s+Delta<=p`, and `2 Delta<=p-2`. Consequently a critical sequence of length `((2k+5)p-3)/2` has support at least `k+4`.
10. **Length-19 line-fiber avoidance.** Proper-subsum avoidance localizes to each projective direction. For a zero-sumfree scalar fiber `A` of length `r>p/2`, the surviving maximal-atom scalar list satisfies `d(d+1)/2<=p-1-r`. At `p=7`, two independent exact checkers freeze all 96 zero-sumfree line multisets: occupancies `3,4,5,6` leave at most `1,1,1,0` scalars. The `(8,10,19)` length-29 pair and `(9,9,19)` length-28 pair each have actual support at least six.
11. **All-`k` packing-defect core formalism.** For exponent `n`, `delta_n(B)=|B|-n z(B)` has a finite global maximum equal to `max_k(D_k(G)-kn)`. A shortest maximizer is `n`-short-zero-free. For `C_p^3`, the proposed formula for every `k>=2` is equivalent to `delta_p(B)<=(5p-5)/2` for every zero-sum block; in Hilbert/Graver coordinates a counterexample is an above-threshold short-free box factorization terminal under every positive-gain conformal move.
12. **Minimal-level excess signatures.** If the target first fails at factorization length `m` with overshoot `q>=1`, every atom excess satisfies `e_i>=q`, `sum e_i=M_p+q`, and `(m-1)q<=M_p`. The exact `p=7` algebraic shell has 322 raw signatures. Zhang's short-atom input plus the six exact `(m,q)=(3,1)` corridors prune this to 301. Primary recursive and independent multiplicity-vector checkers agree.
13. **Coding-theoretic finite first-failure theorem.** Freeze--Schmid's standard `D_0(G)` is the eventual intercept, not the branch defect envelope; the target line is exactly `D_0(C_p^3)=M_p` with stabilization index `k_D=2`. Every first failure is `p`-short-zero-free. Combining `eta(C_p^2)=3p-2` with the dimension-three Griesmer bound gives `|B|<=62` for `p=5` and `|B|<=3p^2-3p-3` for `p>=7`. Therefore it suffices to prove the target only through `K_5=10`, `K_7=15`, and `K_p=(5p-3)/2` for primes `p>=11`. For `p=7`, the coding cap removes exactly the algebraic top shell `(m,q,e)=(16,1,(1^16))`, reducing the working signature cover from 322 raw / 301 donor-pruned to 321 raw / 300 donor-pruned. If first-failure projective directions have no four collinear, the donor `(n,3)`-arc bound gives `m<=2p-4`; levels `m>=2p-3` must contain a rich four-secant plane. Two structurally independent checkers agree on canonical digest `37f152e4074a10edeedc14ea52207fb189bcc000dcb2901c4bb182defe91d68c`.
14. **Restricted-sum front end and eta-tail propagation.** A first failure with overshoot `q` is `(p+q-1)`-short-zero-free. The Bhowmik--Schlage-Puchta bound `s_{<=(3p-1)/2}(C_p^3)<=6p-3` therefore gives the uniform overshoot cap `q<=(p-1)/2`. Zhang's exact rank-three value `s_{<=2p-2}(C_p^3)=4p-2` forces every first failure to have a maximum factorization containing an atom of excess at most `p-2`. Freeze--Schmid Proposition 3.1(3) turns any eta upper bound into a tail gate: if `eta(C_p^3)<=E_p`, it is enough to verify the target through `T_p(E_p)=max(2,ceil((E_p-1-M_p)/p)-1)`. The previous Griesmer level cap is exactly this gate with `E_p=L_p+1`. At `p=5`, `eta(C_5^3)=33` gives tail threshold 4, agreeing with the completed sibling ORION-04 `D_3,D_4` route. At `p=7`, the coding-refined signature shell drops from 321 to 300 under the q-cap, to 299 after the uniform short-atom filter, and to exactly **286** after the six atom corridors; two independent checkers freeze digest `2b49f2b6f4579a27165ebe5285292a5966901f1af7793a5cf73f3e9c8d47be19`.

## Strongest current `C_7^3` obstruction semantics

If `B` is zero-sum over `C_7^3`, `|B|=37`, and `z(B)<=3`, then

- `z(B)=3` and `delta_7(B)=16`, the `(p,m,q)=(7,3,1)` core slice;
- `|supp(B)|>=8`;
- support eight, if it occurs, uses eight distinct projective directions;
- every three-atom factorization lies in the six frozen atom corridors;
- the two maximal-atom corridors obey the projective line-fiber scalar grammar;
- every maximum factorization is Graver-terminal.

This is not yet a determination of `D_3(C_7^3)`.

## General formula now isolated

For `p>=5`, put `M_p=(5p-5)/2`. The donor lower line is

`D_k(C_p^3)>=kp+M_p` for `k>=2`.

The target

`D_k(C_p^3)=kp+M_p` for every `k>=2`

now has four equivalent / complementary working coordinate systems:

1. **defect:** `|B|-p z(B)<=M_p` for every zero-sum block;
2. **standard eventual-line:** `D_0(C_p^3)=M_p` and `k_D(C_p^3)=2` in Freeze--Schmid notation;
3. **restricted-sum front end:** a first failure has `q<=(p-1)/2`, no zero-sum through length `p+q-1`, and a maximum factorization with `min e_i<=p-2`;
4. **finite augmentation core:** after any verified eta upper bound `E_p`, only `3<=m<=T_p(E_p)` remains, with excess slack `e_i=q+f_i`, `sum f_i=M_p-(m-1)q`, projective/coding deficits, and Graver terminality.

Thus the all-`k` problem has split into a **restricted-sum front end plus a finite rank-three positive-kernel augmentation theorem**. The latter is the missing theorem.

## Retained negative / non-promoted findings

- Exact-name and one lexical multiwise donor-search route were flat. Flatness is not a novelty certificate.
- The first unstructured support-7 enumeration exceeded the host budget and remains `CANNOT_CHECK_RESOURCE_BOUND`.
- Several apparent saturation observations reduced to direct consequences of `D_2=29` and were not promoted.
- No verified rank-three donor inverse theorem yet eliminates the two length-19 corridors.
- Global cardinality of the proper-subsum avoidance set is insufficient; projective line fibers retain the needed rank/scalar data.
- The count 14,860 belongs to support seven; the support-8 one-collision short-free count is 15,844.
- Appending `g^p` need not raise packing by exactly one. Eventual linearity alone does not prove immediate stabilization; see `FAILURE_DEFECT_BOOTSTRAP_V1.md`.
- The old 322/301 and 321/300 counts remain correct for their declared pre-restricted-sum shells. The new 286 count is a strict donor refinement, not a correction of those checkers.
- Generic Graver test-set existence is an exact reformulation, not the missing positive-gain rank-three theorem.
- The exact value `eta(C_p^3)` remains unknown for general primes `p>=7`; the lower construction `8p-7` is not used as an upper bound.

## Open residuals / next discriminators

1. **Finite first-failure augmentation theorem.** Work only with `q<=(p-1)/2` and `3<=m<=T_p(E_p)`. Apply slack signatures before vector enumeration. High levels `m>=2p-3` must enter a four-secant/rich-plane branch.
2. **Support-8 Type-A closure.** Eliminate the eight-distinct-direction `(7,3,1)` face over the surviving 347 projective classes and 5,841,092 deficit-profile/class pairs before scalar/kernel filtering.
3. **Length-19 inverse residual.** Continue `(8,10,19)` and `(9,9,19)` via line fibers, primitive positive kernels and conformal three-splitting.
4. **Restricted-sum donor ladder.** Insert any stronger values or upper bounds for `s_{<=h}(C_p^3)` into the overshoot-sensitive killer. Intermediate `h` between `p` and `2p-2` are especially valuable because they can lower the q-cap below `(p-1)/2`.
5. **Coding/finite-geometry upgrade.** Improve the eta upper bound and weighted-projective restrictions using repeated-column restrictions, rich-plane counts and Property C.
6. **Higher-core induction.** Push every verified lower level into all proper atom subproducts of a first failure before constructing moves.
7. **Hypergraph dual.** Seek a matching/fractional-matching theorem whose deficiency equals the factor-excess slack.
8. **Donor/priority saturation.** Continue searches for stabilization-index bounds, generalized Noether stabilization, rank-three primitive-kernel decomposition and weighted projective-code bounds.

## Claim ceiling

No claim states that `D_3(C_7^3)` is open or solved, that the candidate all-`k` formula is proved or novel, or that characteristic 3 has been explained. Finite closures authorize only their declared domains; donor theorems receive zero ORION novelty credit.
