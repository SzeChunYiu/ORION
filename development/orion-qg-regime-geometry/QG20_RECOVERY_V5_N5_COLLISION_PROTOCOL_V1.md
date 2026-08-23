# QG-20 Recovery V5 — n=5 Collision-Challenge Confirmation Protocol V1

**Status:** `FROZEN_AFTER_V4_COMPLETE_N4_POSITIVE__BEFORE_ANY_N5_EXACT_LABEL`  
**Owner:** QG-20 #863  
**Recovery coordinator:** #964

## Immutable V4 method

V4 recovered a donor-owned representation with no feature selection:

`phi4 = (original QG-15b 13-vector, SIGNED_COMPLETE_WEIGHT_V1)`

where `SIGNED_COMPLETE_WEIGHT_V1` contains every signed X/Y/Z composition coefficient for the complete stabilizer group.

On all 36,720 exact n=4 StabPrep states:

- `phi0`: floor 586, 54 mixed cells;
- V1: floor 128, 20 mixed;
- V2 best old-grammar map: floor 85, 12 mixed;
- V3 simple signed weight: floor 33, 7 mixed;
- **V4 signed complete weight: floor 0, 0 mixed**, 3,997 cells.

V4 analyzer replay was byte-identical and the independent verifier accepted every registered check. V4 used 34 fixed coefficients and no selection.

## V5 question

> Does the recovered V4 representation remain non-mixing on a larger `n=5` state space when we deliberately select **same-representation collision groups before exact labels are known**?

This is not an all-n proof. It is a protected held-out-size falsification attempt.

## Frozen representation at n=5

No learned or selected coordinates may be added.

For n=5, extend the same mathematical object naturally:

`C_{a,b,c} = sum lambda(P)` over every stabilizer element with X-only/Y/Z-only composition `(a,b,c)`, for every nonzero triple with `a+b+c<=5`.

The map remains:

`phi4_n5 = (same 13 structural/donor coordinates, complete signed X/Y/Z weight enumerator)`.

## Label-blind candidate pool

Freeze:

- `n = 5`;
- RNG seed `2026082305`;
- random-walk length `14` gates;
- candidate pool cap `100,000` unique states;
- required selected collision groups `32`;
- two canonical states per group => `64` target states.

Generate a deterministic stream of random Clifford gates from the full n=5 gate alphabet:
- H/S/SDG on every qubit;
- directed CX on every ordered distinct pair.

For each generated state compute only:
- GE donor and donor cost;
- lower-bound/structural quantities already in `phi0`;
- V4 complete signed-weight vector;
- representation key `phi4_n5`.

**No exact referee or donor-exact label may be invoked during pool construction or collision selection.**

Continue generating unique states until either:
- at least 32 representation keys have >=2 states, then stop at the first stream position satisfying the condition; or
- pool cap 100,000 is reached.

If fewer than 32 collision groups exist at cap, terminal is `CANNOT_CHECK_N5_COLLISION_DENSITY`; do not change seed/length/cap in V1.

## Frozen collision-group selection

After label-blind pool closure:

1. canonicalize each state as its encoded integer tuple;
2. sort collision keys by canonical JSON encoding;
3. choose the first 32 keys;
4. within each key choose the first two lexicographically sorted states.

Persist a `selection` receipt containing:
- pool size and stream stop index;
- 32 representation-key digests;
- 64 target-state digests;
- donor costs / structural features allowed in the representation;
- `exact_labels_accessed=false`.

Only after this receipt is written and emitted may exact target costs be computed.

## Targeted exact referee

Do **not** build the complete 2,423,520-state n=5 distance table unless needed.

Run Dijkstra from the canonical stabilizer start state using the exact QG-15 gate alphabet/costs. Stop only after all 64 selected targets have been **popped from the priority queue at their final shortest distance**.

Record:
- settled-state count;
- discovered-state count;
- maximum settled target cost;
- exact cost for every target.

If resource limits prevent all 64 targets from settling, return `CANNOT_CHECK_EXACT_N5_RESOURCE`; never treat an unsettled incumbent as gold.

## Protected outcome

For each selected representation collision group, label its two target states:

`donor_exact = (C_D == C_opt)`.

Primary falsifier:
- any group containing both `True` and `False` **refutes V4 at n=5**.

Report:
- mixed collision groups;
- deterministic error floor over the selected groups;
- exact/inexact target counts;
- label diversity.

A positive confirmation additionally requires at least **4 exact and 4 inexact target states**. Otherwise terminal is `CANNOT_CHECK_LABEL_DIVERSITY` even if no mixed group appears.

## Independent verifier

A second implementation must independently:
- reproduce the RNG stream and label-blind collision selection;
- rebuild `phi4_n5` directly from encoded states and donor outputs;
- rerun targeted Dijkstra with independently written queue/state bookkeeping;
- agree on every target distance and donor-exact label;
- agree on every selected representation key and mixed-group statistic.

Verifier disagreement is serialized.

## Terminals

Strong positive:

`QG20_RECOVERY_V5_SIGNED_COMPLETE_WEIGHT_SURVIVES_N5_COLLISION_CHALLENGE`

requires:
- 32 collision groups / 64 targets selected label-blind;
- exact targeted referee settles all targets;
- >=4 exact and >=4 inexact labels;
- mixed groups = 0;
- error floor = 0;
- deterministic analyzer replay;
- independent verifier ACCEPT.

Refutation:

`QG20_RECOVERY_V5_SIGNED_COMPLETE_WEIGHT_REFUTED_BY_N5_COLLISION`

Other honest terminals:
- `CANNOT_CHECK_N5_COLLISION_DENSITY`
- `CANNOT_CHECK_EXACT_N5_RESOURCE`
- `CANNOT_CHECK_LABEL_DIVERSITY`
- `QG20_RECOVERY_V5_DUAL_DISAGREEMENT`.

## Claim boundary

A positive supports only a bounded cross-size result: V4 determines donor exactness on the complete n=4 domain and survives a prospectively selected, label-blind same-representation collision challenge at n=5. It is not an all-n theorem, not global minimal-state proof, not a new quantum compiler, not novelty for complete signed weight enumerators, and not physical quantum advantage.