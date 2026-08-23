# ORION-QG QG-37b — independent physical-probe PB-SAT replication

Date: 2026-08-22
Parent issue: SzeChunYiu/ORION#937

## Status

**FROZEN BEFORE THE TWO RESIDUAL 48-ORBIT ROBUST MINIMA ARE READ FROM ANY COMPLETED EXECUTION. NO ROBUST CARDINALITY IS PREDICTED HERE.**

QG-37b is an independent exact replication of the class-conditioned one-corruption problem frozen in QG-37. It does not alter the scientific target, response universe, distance target, physical-probe multiplicity, decoder semantics, or authority ceiling.

## Frozen universe and target

Independently reconstruct from the generic F2^2/F3 primitives:
- 715 local-Clifford orbit representatives;
- 384 **physical** indexed probe coordinates;
- exact integer response matrix `K[o,p]`;
- the same 92 joint bulk+spectrum summary classes;
- distance target three inside each known class.

For each class `S`, define `D3(S)` as the minimum number of distinct physical probes such that every pair of orbit identities in `S` differs on at least three selected coordinates.

QG-35 may be used only for the already-earned exact noiseless value `D1(S)=F(S)` and the puncturing lower bound `D3(S) >= F(S)+2` on non-singleton classes. This is not robust authority by itself.

## Independent exact formulation

QG-37b must not import the production MILP basis, LP bound, branch tree, grouped-variable incumbent, or claimed optimality.

Use one Boolean variable `x_p` for every physical probe identity `p in {0,...,383}` that distinguishes at least one pair in the class. For every unordered orbit pair `(a,b)` in the class impose the pseudo-Boolean constraint

`sum_{p: K[a,p] != K[b,p]} x_p >= 3`.

For a cardinality decision `k`, also impose

`sum_p x_p <= k`.

The solver is an exact SAT/pseudo-Boolean decision engine over physical Boolean coordinates. Coverage-equivalent probes remain separate Boolean variables; multiplicity is never collapsed.

For each class:
1. start from the puncturing floor `F(S)+2` (or zero for a singleton);
2. obtain a deterministic verified upper bound either from an independently generated greedy distance-three code or from a production witness only after independently recomputing its distance;
3. test cardinalities monotonically from the floor upward;
4. the first SAT cardinality is the exact `D3(S)` because every smaller cardinality has returned UNSAT;
5. `unknown`, timeout, malformed model, or a disagreement with direct distance recomputation is `CANNOT_CHECK` for that class.

Fix solver/version and deterministic seeds in the workflow. A SAT model is not authority until the full response code is independently recomputed and has minimum Hamming distance at least three.

## Independent decoder check

For the chosen exact witness in every non-singleton class:
- recompute all pairwise selected-word distances;
- require minimum distance >=3;
- explicitly enumerate every radius-0/1 corrupted word using every response symbol appearing at the mutated coordinate plus one deterministic foreign-symbol control;
- require no corrupted word to lie within radius one of two distinct clean orbit words.

## Comparison to QG-37 production

After QG-37 production exists, QG-37b may compare:
- exact minima vector;
- robust worst case;
- selected-witness cardinalities;
- exceptional classes strictly above the puncturing floor.

Any disagreement is fail-closed and blocks robust authority. QG-37b may independently discover a smaller witness than production; in that case production is not exact and must not be promoted.

## Honest terminals

- `QG37B_INDEPENDENT_EXACT_ROBUST_MINIMA_MACHINE_CHECKED`
- `QG37B_INDEPENDENT_ROBUST_WITNESS_DISAGREEMENT`
- `QG37B_CANNOT_CHECK`

## Hard false authority

Always false:
- hardware measurement-noise model;
- stochastic physical error rate;
- FT threshold;
- full finite-n optimum probe claim;
- generic coding/SAT novelty;
- runtime or compiler-resource advantage;
- physical quantum advantage;
- external novelty authority.

## Donor subtraction

Pseudo-Boolean SAT, minimum-distance coding criteria, multicover, separating systems, and puncturing bounds are donor mathematics. Candidate value is only the exact compiler-specific response-code geometry and its scoped evidence-reliability consequence.
