# ORION-QG QG-28 — exact local-Clifford orbit compression protocol V1

Date: 2026-08-22
Issue: #888
Parent programme: #740
Execution branch: `codex/orion-qg-qg28-clifford-orbits-20260822`
Direct parent: QG-26 protected 4096-column guarded histogram geometry.
Related parent: QG-27 protected four-form bulk geometry.
Status: **FROZEN BEFORE QG-28 MACHINE OUTCOME.**
Authority: exact abstract compiler-symmetry quotient only; no novelty, R6, physical-equivalence, unsafe per-column target-position relabeling, template-basis, forecaster, chain, or B''-completeness authority.

## Frozen theorem candidate

The phase-free one-qubit Pauli algebra is `F_2^2`; its automorphism group `GL(2,2) ~= S3` fixes I and permutes X,Y,Z. A different automorphism may be chosen independently at each physical qubit, applied simultaneously to all six target letters and all local frame/Tag letters at that coordinate.

The analyzer must prove complete local equivariance under all six automorphisms:
- multiplication equivariance on all 16 pairs;
- symplectic invariance on all 16 pairs;
- nonidentity-weight invariance on all 4 letters;
- F3 invariance on all 64 triples.

Because the global TARE grammar is built only from coordinatewise multiplication/weight/F3 and XOR sums of symplectic bits, independent per-qubit automorphisms preserve exact feasibility and cost.

## Orbit census

Let S3 act diagonally on each target column `t in {I,X,Y,Z}^6`.

Burnside targets:
- identity fixes 4096 types;
- each of 3 transpositions fixes 64;
- each of 2 three-cycles fixes 1.

Expected orbit count: `(4096+3*64+2)/6 = 715`.

Complete enumeration must recover orbit-size distribution:
- size 1: 1 orbit;
- size 3: 63 orbits;
- size 6: 651 orbits.

Canonical representative is the lexicographically smallest type in each orbit.

## 715-count sufficient statistic

For an n-qubit target instance, independently map each physical column to its canonical orbit representative and transform its local auxiliary letters by the same automorphism. Thus exact cost depends only on the 715 orbit counts `M_o`, not the original 4096 type counts.

The QG-26 guarded min-affine theorem therefore descends to 715 orbit counts: spectator coefficients are constant on each orbit; active-template target occurrences can be canonicalized coordinatewise with their auxiliary letters; multiplicity guards become orbit-count guards.

## Baseline controls

Reconstruct all eight QG-26 spectator vectors and require:
- each is constant on every S3 orbit;
- they still form four distinct quotient vectors;
- each 715-entry quotient vector has orbit-count histogram `{0:1,1:8,2:44,3:128,4:222,5:216,6:96}`;
- lifting the quotient coefficient on each orbit back to all 4096 members reproduces the full vector and its protected QG-26 SHA256.

## Active canonicalization control

For every 4096 target type, choose the lexicographically first automorphism mapping it to its canonical representative. For all exact 48 feasible one-coordinate shared-label frame/Tag rows and all 8 target-permutation tuples, canonical central tuple `(0,0,0)`:
- transform all six frame letters and the Tag letter by that automorphism;
- require production n=1 `config_cost` before/after to be identical;
- require production `config_labels` before/after to be identical;
- require baseline-plus-active-correction decomposition before/after identical.

This is `4096*48*8 = 1,572,864` deterministic rows. Generic ORION independently rebuilds the algebra and reproduces aggregate digests.

## Mandatory unsafe-symmetry barrier

Permuting the three blocks or swapping target identities inside blocks is a **global whole-string relabeling**, not a coordinatewise freedom. QG-28 must not aggregate histogram bins as if those position permutations could be chosen independently at each qubit.

Mandatory false: `INDEPENDENT_POSITION_RELABEL_PER_COLUMN`, any 54-bin or other combined local position quotient, physical equivalence beyond the frozen abstract objective.

## Native authority

May authorize only:
- `LOCAL_CLIFFORD_EQUIVARIANCE_PER_QUBIT`;
- `LOCAL_CLIFFORD_ORBIT_COUNT_715`;
- `ORBIT_HISTOGRAM_SUFFICIENT_STATISTIC_ALL_N`;
- `GUARDED_TROPICAL_GEOMETRY_DESCENDS_TO_715_COUNTS`.

Mandatory false: independent position relabel per column, explicit template basis, practical forecaster, chain/B'' completeness, physical-advantage and novelty/R6 authority.

## Intended terminal

`QG28_TARE_EXACT_COST_DESCENDS_TO_715_LOCAL_CLIFFORD_COLUMN_ORBIT_COUNTS_ALL_N`

Honest alternatives: local equivariance refuted; baseline not constant; active canonicalization counterexample; QG-26 binding gap; generic/native disagreement; CANNOT_CHECK.

## Donor subtraction

Finite group actions, Burnside/Pólya counting, local Clifford automorphisms and invariant theory are established donor mathematics/quantum information. Candidate contribution is only the exact TARE-specific 4096→715 sufficient-statistic theorem and descent of its all-n regime geometry.