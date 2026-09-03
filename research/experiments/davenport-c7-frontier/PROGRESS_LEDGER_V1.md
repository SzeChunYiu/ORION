# C7^3 multiwise Davenport frontier — progress ledger V4

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
11. **All-`k` packing-defect core formalism.** For an exponent-`n` group, `delta_n(B)=|B|-n z(B)` has a finite global maximum equal to `max_k(D_k(G)-kn)`. Deleting `n` equal terms never lowers defect, and a shortest maximizer is `n`-short-zero-free, so the global problem reduces to a finite Apéry box. For `C_p^3`, the proposed formula for every `k>=2` is equivalent to the single bound `delta_p(B)<=(5p-5)/2` for every zero-sum block. In Hilbert-basis coordinates, defect is a minimum factorization cost; a counterexample is exactly a short-free box factorization above the threshold that is terminal under every positive-gain Graver move. Two independently structured arithmetic/signature checkers agree on the exact `p=7,q=1` record: 219 bounded signatures over all `m>=3`, 19 raw `m=3` signatures, and the six donor-pruned atom corridors.

## Strongest current obstruction semantics

If `B` is zero-sum over `C_7^3`, `|B|=37`, and `z(B)<=3`, then

- `z(B)=3`;
- `delta_7(B)=16`, so it is the `(p,m,q)=(7,3,1)` slice of the defect-core formalism;
- `|supp(B)|>=8`;
- if `|supp(B)|=8`, its eight actual support values lie on eight distinct projective directions;
- every three-atom factorization has one of the six corridor length triples above;
- in either length-19 corridor, the maximal-atom/short-atom pair has support at least six and obeys the exact projective line-fiber scalar grammar in `LENGTH19_PROJECTIVE_LINE_FIBER_AVOIDANCE_V1.md`;
- a maximum-length atomic factorization is Graver-terminal, and proving an applicable positive-gain conformal move would eliminate the candidate.

This is not yet a determination of `D_3(C_7^3)`.

## General formula now isolated

For `p>=5`, put

`M_p=(5p-5)/2`.

The donor lower line is

`D_k(C_p^3)>=kp+M_p` for `k>=2`.

By `PACKING_DEFECT_CORE_FORMALISM_V1.md`, equality for every `k>=2` is equivalent to

`|B|-p z(B)<=M_p`

for every zero-sum block `B`. It is also equivalent to absence of every terminal `(p,m,q)` core with `m>=3` and `q>=1`.

Every such core has:

- length `pm+M_p+q`;
- atom excesses `e_i in [1,2p-2]` summing to `M_p+q` and satisfying `e_i+e_j<=M_p`;
- actual support at least `m+4`;
- at least `ceil(m+5/2+(m+q)/(p-1))` projective directions;
- plane occupancy at most `3p-3`, with the Property-C rich-plane improvement where available;
- a positive modular kernel vector in the finite multiplicity box;
- no applicable positive-gain Graver move at an optimal factorization.

This is the current general formalism. The missing theorem is the special rank-three augmentation statement that excludes all such terminal cores.

## Retained negative / non-promoted findings

- Exact-name and one lexical multiwise donor-search route were flat. Flatness is not a novelty certificate.
- The first unstructured support-7 enumeration exceeded the host budget. It remains preserved as `CANNOT_CHECK_RESOURCE_BOUND`; the successful projective formulation is a representation repair, not a relabeling of that timeout.
- Several apparent saturation observations collapsed under hostile review to direct consequences of `D_2=29` and were not promoted.
- A donor search for a rank-three inverse theorem strong enough to eliminate the length-19 corridor patterns did not close them. See `LENGTH19_TRIPLES_RESIDUAL_V1.md`.
- Global cardinality of the proper-subsum avoidance set is not by itself a corridor separator. The retained repair is the projective line-fiber decomposition, which preserves scalar and rank information.
- The count 14,860 belongs to support seven. The independently frozen support-8 one-collision short-free count is 15,844; stale handoffs conflating them are rejected.
- Appending `g^p` need not increase the packing number by exactly one, so defect maximizers do not automatically propagate to larger `k`. Eventual linearity therefore does not prove immediate stabilization. See `FAILURE_DEFECT_BOOTSTRAP_V1.md`.
- Atomic excess signatures and a generic Graver test-set theorem are exact reductions, not the missing rank-three augmentation proof.

## Open residuals / next discriminators

1. **Defect-core augmentation theorem.** Prove that every `p`-short-zero-free box factorization over `C_p^3` with cost above `M_p` has an applicable positive-gain Graver move. Use projective support and deficit incidence before constructing any atom or move set.
2. **Length-19 inverse residual.** Continue `(8,10,19)` and `(9,9,19)` from the line-fiber grammar: projective support first, then companion fibers, allowed scalar lists, positive primitive kernels, and conformal three-splitting. No unstructured atom-pair enumeration.
3. **Support-8 Type-A closure.** Exhaust or analytically eliminate the eight-distinct-direction branch over the surviving 347 projective classes and 5,841,092 deficit-profile/class pairs before scalar/kernel filtering. This is the smallest unresolved face of the `(7,3,1)` core.
4. **Higher-core induction.** Use any verified `m`-core elimination as a donor bound on every `m`-atom subproduct of a larger terminal factorization, recursively tightening its excess signatures.
5. **Hypergraph/coding dual.** Seek a matching theorem or bounded exceptional list for the positive codewords of the projective parity-check matrix.
6. **Donor/priority saturation.** Continue alias/function/historical searches for the defect envelope, generalized Noether stabilization, Graver augmentation in block monoids, and rank-three primitive-kernel decomposition before novelty language.

## Claim ceiling

No claim states that `D_3(C_7^3)` is open or solved, that the candidate all-`k` formula is proved or novel, or that characteristic 3 has been explained. Finite closures authorize only their declared domains; donor theorems receive zero ORION novelty credit.