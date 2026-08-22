# ORION-QG QG-35 — summary-conditioned fixed probe complexity

Date: 2026-08-22
Issue: SzeChunYiu/ORION#932
Parent programme: #740
Direct earned parent: QG-32 #911.
Context-only earned parent: QG-32c #928 proves universal fixed minimum 5, but QG-35 does not use that lower bound because its fixed probe set may depend on the known joint summary class.
Comparison successor: QG-36 #933, frozen before any QG-35 result.

## Status

**PROSPECTIVE FAIR-BASELINE LANE. FROZEN BEFORE ANY QG-35 OUTCOME.**

The initial joint bulk+spectrum summary class is known before any indexed probe is selected. For each of the 92 exact initial classes `S`, define `F(S)` as the minimum cardinality of a probe set selected after `S` is known but fixed before any probe responses are observed, such that the joint response signature separates every orbit in `S`.

`F_* = max_S F(S)`.

No value of `F(S)` or `F_*` is predicted.

## Frozen universe and binding

Reconstruct only from the earned QG-32 generic primitives:
- 715 local-response orbit representatives;
- 384 indexed response coordinates;
- 92 exact joint bulk+spectrum classes;
- class-size histogram `{1:7,2:22,3:6,4:6,6:25,8:2,12:14,24:8,48:2}`;
- exact integer response matrix `K[o,p]`.

Bind QG-32's already-certified universal five-probe separator `[18,68,101,181,139]` only as a constructive per-class upper bound `F(S)<=5`. It provides no QG-35 lower-bound authority.

## Exact per-class cover formulation

For one initial class `S`, define its pair universe

`U(S) = {{a,b}: a,b in S, a<b}`.

Probe `p` covers pair `{a,b}` iff `K[a,p] != K[b,p]`.

A fixed probe set separates `S` iff the union of its pair-cover sets equals `U(S)`.

Singleton classes have `F(S)=0`.

## Production exact method

For every non-singleton class:
1. construct all 384 physical probe pair-cover bitsets from the exact response matrix;
2. collapse identical nonzero cover sets, retaining the minimum physical probe index as representative;
3. remove coverage-dominated classes: if `cover(A) subseteq cover(B)`, A cannot be required by a minimum-cardinality solution when B is available;
4. solve exact cardinality in increasing order `d=1,2,3,4` using memoized bounded branch search;
5. allowed sound pruning only:
   - no-slots terminal;
   - maximum-cover cardinality lower bound;
   - choose one uncovered pair with the fewest still-available candidate probes;
   - sorted-probe start index to avoid duplicate combinations;
   - memoization keyed by `(remaining_pairs, slots, start)`;
6. if no `d<=4` exists, verify the earned QG-32 universal five-probe basis separates this class and set `F(S)=5`.

Required serialization:
- all 92 exact `F(S)` values in canonical class order;
- minimum histogram by class count and by orbit mass;
- `F_*`;
- worst class indices/sizes;
- canonical exact witness probe set for every worst class;
- witness separation check;
- per-class reduced cover count and branch-search statistics.

## Independent generic method

Generic ORION must reconstruct the response matrix independently from the phase-free F2^2/F3 primitives and must not call the production QG-35 solver.

For each class:
1. independently build/collapse/dominance-reduce pair-cover sets;
2. enumerate every unique union attainable by 0, 1, or 2 retained probe classes, keeping a minimum-cardinality deterministic witness for each union;
3. determine the exact minimum <=4 by meet-in-the-middle:
   - 0: singleton only;
   - 1: a one-probe half covers the universe;
   - 2: one two-probe half covers the universe;
   - 3: one half of size <=1 plus one half of size <=2 covers the universe;
   - 4: two halves of size <=2 cover the universe;
4. complement candidates may be accelerated by postings on uncovered pair bits, but every survivor must be checked by exact bitset union;
5. if no <=4 cover exists, independently verify the QG-32 five-probe basis separates the class and set minimum 5.

The generic verifier must compare the entire 92-value array, maxima, histograms, worst-class set, and every serialized worst-class witness.

## Native ORION-Q authority

May authorize only:
- exact summary-conditioned nonadaptive fixed observation complexity `F(S)` on the frozen 92 classes;
- exact worst-case `F_*`;
- exact worst-class fixed witnesses.

Must keep false:
- adaptive minimax authority (QG-34 is separate);
- strict adaptivity advantage (QG-36 composition is separate);
- universal fixed minimum authority beyond the already-earned QG-32c receipt;
- full finite-n optimum probes;
- hardware measurement minimum;
- global state minimality;
- novelty authority;
- physical quantum advantage.

## Workflow

Require:
- production/generic/native GREEN;
- deterministic byte-identical production replay;
- self-consistent class-minimum/witness tamper rejected by generic verifier;
- hard authority-boundary assertion.

## Honest terminals

- `QG35_EXACT_SUMMARY_CONDITIONED_FIXED_PROBE_COMPLEXITY_MACHINE_CHECKED`
- `QG35_CLASS_CONDITIONED_FIXED_UPPER_BOUND_ONLY`
- `QG35_CANNOT_CHECK`

## Donor subtraction

Set cover, branch-and-bound and meet-in-the-middle are donor methods. Candidate value is only the exact compiler-specific class-conditioned observation complexity and the fair fixed baseline it supplies to QG-36.