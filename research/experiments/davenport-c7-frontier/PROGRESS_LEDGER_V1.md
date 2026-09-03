# C7^3 multiwise Davenport frontier — progress ledger V3

Status: live LLM-assisted ORION research ledger. No novelty authority.

## Closed / verified bounded results

1. **Donor-derived D2 gate.** For prime `p>=5`, `a>=1`, `n=p^a`, Freeze--Schmid + the classical p-group Davenport value + Zhao Lemma 4.4 give `D_2(C_n^3)=(9n-5)/2`; in particular `D_2(C_7^3)=29`. Derivation complete; priority `CANNOT_CHECK`.
2. **Binary-cube support closure.** The natural seven-point binary-cube support has exactly 10 length-37 total-zero profiles in 4 coordinate-permutation orbits; every profile has packing number exactly 4. Two differently structured checkers agree.
3. **Six-triple atom corridor.** Any total-zero length-37 sequence with packing number at most three factors into exactly three atoms with sorted length triple one of `(8,10,19)`, `(9,9,19)`, `(9,10,18)`, `(9,11,17)`, `(9,12,16)`, `(10,10,17)`.
4. **Zhao `4p` resonance.** For `C_p^3`, `p>=5`, every admissible Zhao-Lemma-4.4 coefficient vanishes modulo `p` at total-zero length `4p`. This is a proof-instrument statement, not a physical phase theorem.
5. **Support-7 projective reduction.** A hypothetical length-37 obstruction with support seven projects to seven distinct points of `PG(2,7)` with no four collinear.
6. **Projective cover regeneration.** A deterministic frame-normalized generator enumerates 18,451 frame-containing candidates and quotients them to exactly 54 projective support classes: 53 with a collinear triple and one ordinary seven-arc. The external coding-theory count `53+1` is a control, not executable cover authority.
7. **Complete support-7 closure.** Across all 54 support classes, 7,400 normalized full-support kernel vectors and 462 positive deficit-weight profiles yield exactly 3,418,800 total-zero scalar/multiplicity lifts. Exactly 14,860 survive the necessary 7-short-zero-free filter, and all 14,860 admit four pairwise disjoint nonempty zero-sum subsequences. Therefore any hypothetical length-37 total-zero obstruction with packing number at most three has support at least eight. Primary and differently structured independent verifiers agree.
8. **Complete support-8 one-projective-collision closure.** Reusing the 54 seven-direction arc classes, 7,400 normalized full-support kernels and 2,583 doubled-direction/profile/local states give 19,114,200 parameterized lifts. Exactly 15,844 are 7-short-zero-free, and all 15,844 four-pack. Six primary and six structurally independent CI shards replay the complete class cover. Thus every support-8 obstruction, if one exists, uses eight distinct projective directions. See `SUPPORT8_ONE_COLLISION_THEOREM_V1.md` and `SUPPORT8_ONE_COLLISION_HOSTILE_AUDIT_V1.md`.
9. **Prime-uniform short-free complement barrier.** For a zero-sum `p`-short-zero-free sequence over any exponent-`p` group, support deficit `Delta=s(p-1)-N` is impossible whenever `Delta>=0`, `s+Delta<=p`, and `2 Delta<=p-2`. Consequently a critical sequence of length `((2k+5)p-3)/2` has support at least `k+4`. Conditional on the `(k-1)`-st stabilized lower line, every first obstruction to `D_k(C_p^3)<=((2k+5)p-5)/2` satisfies this support bound.
10. **Length-19 line-fiber avoidance.** Proper-subsum avoidance localizes to each projective direction. For a zero-sumfree scalar fiber `A` of length `r>p/2`, the surviving maximal-atom scalar list satisfies `d(d+1)/2<=p-1-r`, where `d=|R(A)|`. At `p=7`, two independent exact checkers freeze all 96 zero-sumfree line multisets: occupancies `3,4,5,6` leave at most `1,1,1,0` scalars, and every survivor for occupancy at least three is already a companion-atom scalar. The `(8,10,19)` length-29 pair and `(9,9,19)` length-28 pair each have actual support at least six.

## Strongest current obstruction semantics

If `B` is zero-sum over `C_7^3`, `|B|=37`, and `z(B)<=3`, then

- `z(B)=3`;
- `|supp(B)|>=8`;
- if `|supp(B)|=8`, its eight actual support values lie on eight distinct projective directions;
- every three-atom factorization has one of the six corridor length triples above;
- in either length-19 corridor, the maximal-atom/short-atom pair has support at least six and obeys the exact projective line-fiber scalar grammar in `LENGTH19_PROJECTIVE_LINE_FIBER_AVOIDANCE_V1.md`.

This is not yet a determination of `D_3(C_7^3)`.

## Retained negative / non-promoted findings

- Exact-name and one lexical multiwise donor-search route were flat. Flatness is not a novelty certificate.
- The first unstructured support-7 enumeration exceeded the host budget. It remains preserved as `CANNOT_CHECK_RESOURCE_BOUND`; the successful projective formulation is a representation repair, not a relabeling of that timeout.
- Several apparent saturation observations collapsed under hostile review to direct consequences of `D_2=29` and were not promoted.
- A donor search for a rank-three inverse theorem strong enough to eliminate the length-19 corridor patterns did not close them. See `LENGTH19_TRIPLES_RESIDUAL_V1.md`.
- Global cardinality of the proper-subsum avoidance set is not by itself a corridor separator. The retained repair is the projective line-fiber decomposition, which preserves scalar and rank information.
- The count 14,860 belongs to support seven. The independently frozen support-8 one-collision short-free count is 15,844; stale handoffs conflating them are rejected.

## Open residuals / next discriminators

1. **Length-19 inverse residual.** Continue `(8,10,19)` and `(9,9,19)` from the line-fiber grammar: projective support first, then companion fibers, allowed scalar lists, positive primitive kernels, and conformal three-splitting. No unstructured atom-pair enumeration.
2. **Support-8 Type-A closure.** Exhaust or analytically eliminate the eight-distinct-direction branch over the surviving 347 projective classes and 5,841,092 deficit-profile/class pairs before scalar/kernel filtering.
3. **Prime-family decomposition theorem.** Turn the support-complement and deficit-incidence formulas into a uniform theorem that every critical positive kernel vector conformally splits into at least `k+1` zero-sum blocks. This is the Graver/Hilbert-basis bottleneck behind the candidate formula `D_k(C_p^3)=((2k+5)p-5)/2` for `k>=2`.
4. **Hypergraph/coding dual.** Use zero-sum count vectors as hyperedges and projective supports as parity-check columns to seek either a matching theorem or a bounded list of primitive exceptional kernels.
5. **Donor/priority saturation.** Continue alias/function/historical searches before novelty language, especially for cyclic line-fiber bounds, generalized Noether-number stabilization, and rank-three primitive-kernel decomposition.

## Claim ceiling

No claim states that `D_3(C_7^3)` is open or solved, that the candidate all-`k` formula is proved or novel, or that characteristic 3 has been explained. Finite closures authorize only their declared domains; donor theorems receive zero ORION novelty credit.
