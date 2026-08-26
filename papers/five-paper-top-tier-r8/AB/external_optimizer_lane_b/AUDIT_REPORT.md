# JOB-AB-R8-2 — external exact-optimizer realization audit

## Disposition

**Terminal: `CANNOT_CHECK`.**

The strongest open, source-auditable candidate identified for this lane is the
MQT QMAP SAT/MaxSAT Clifford synthesizer at commit
`6a0d8a2ff411a0e2c9604c71aff80ba633c0d660`. Its complete synthesis gate
inventory and its three target metrics can be frozen from code. The candidate
does **not**, however, realize the AB weak-delete/strong-fuse separation under
one representation and one cost contract. The prerequisite faithfulness map is
refuted before execution, so no weak terminal, production irreducibility,
state-volume consequence, or runtime consequence can be transferred to QMAP.

This is an adverse result. The AB XOR grammar remains a calibration rather than
an externally realized production case.

## Frozen external authority

The primary source is Schneider, Burgholzer, and Wille, *A SAT Encoding for
Optimal Clifford Circuit Synthesis*, DOI
[`10.1145/3566097.3567929`](https://doi.org/10.1145/3566097.3567929), corrected
arXiv version `2208.11713v2`. The bound PDF hash is
`bea4eea2fc32f6d35b0df4fc68501c93b032083d42a66f90fcab219b0c03c082`.
The correction binds its reproduction claim to QMAP `@6a0d8a2` and narrows the
reported experimental scale from 27 to 6 qubits. This audit preserves that
correction; it does not reuse the withdrawn scalability claim.

The code binding is exact:

- repository: `munich-quantum-toolkit/qmap`;
- commit: `6a0d8a2ff411a0e2c9604c71aff80ba633c0d660`;
- tree: `9a5ad960beb63a0cc23f78b289e629da58b99941`;
- license: MIT;
- single-qubit inventory: `None, X, Y, Z, H, S, Sdg`;
- ordered two-qubit inventory: `CX(control,target)`;
- target metrics: gates, two-qubit gates, and depth.

Full file hashes, immutable permalinks, and line ranges are frozen in
`SOURCE_BINDINGS.json`.

## Contracts compared

### AB weak and production languages

Let the AB state be a multiset of nonzero vectors

\[
W=(w_1,\ldots,w_m),\qquad w_i\in\mathbb F_2^d\setminus\{0\},
\qquad \bigoplus_i w_i\ne 0.
\]

The weak language deletes a nonempty proper submultiset (S\) with

\[
\bigoplus_{i\in S}w_i=0.
\]

The strong production language additionally fuses unequal nonzero fragments:

\[
u,v\longmapsto u\oplus v.
\]

Its declared objective is live-fragment count (C_{AB}(W)=m\). A fuse changes
that cost by (-1\); a weak deletion changes it by (-|S|\).

### QMAP exact-synthesis language

For (n\) qubits, QMAP stores a stabilizer tableau with (r\in\{n,2n\}\) rows.
After dropping the phase coordinate, each row is a label in
(mathbb F_2^{2n}\). Every supported gate acts through an invertible binary
linear transformation:

\[
P\longmapsto P M_g,\qquad M_g\in GL(2n,2).
\]

Therefore a legal QMAP move preserves row count, object cardinality, and the
GF(2) rank of the projected row family. It also has a legal inverse: `H`, `X`,
`Y`, `Z`, and `CX` are self-inverse in the frozen inventory; `S` and `Sdg` are
mutual inverses. A nonidentity move adds a gate/time-step rather than removing a
live object. Under the depth target, QMAP can place compatible primitive gates
in one time step; such a layer is a composition of invertible generators and
therefore preserves the same cardinality and rank invariants.

## Smallest witnessed mismatches

### Strong fuse

Take (W=(001,010)\). AB permits

\[
(001,010)\longmapsto(011).
\]

Cardinality changes (2\to1\), rank changes (2\to1\), and live-fragment cost
changes by (-1\). No QMAP gate has any of those structural deltas.

The move is also many-to-one:

\[
(001,010)\mapsto(011),\qquad (100,111)\mapsto(011).
\]

A bijective Clifford move cannot implement this map on the same state space.

### Weak delete

Take (W=(001,010,011,100)\). Since
(001\oplus010\oplus011=0\), AB permits deletion of the first three fragments:

\[
(001,010,011,100)\longmapsto(100).
\]

Cardinality changes (4\to1\), while projected rank changes (3\to1\). Again,
no QMAP move can match this under the fixed tableau representation.

## Obligation table

| Obligation | Disposition | Reason |
|---|---|---|
| AB weak delete to QMAP | `REFUTED` | Delete can lower cardinality and rank; QMAP preserves both. |
| AB strong fuse to QMAP | `REFUTED` | Fuse is many-to-one and removes one object; QMAP gates are bijective on fixed-size tableaus. |
| QMAP moves to AB bidirectionally | `REFUTED` | QMAP moves have legal inverses; AB delete/fuse do not. |
| One representation | `REFUTED` | AB uses variable-cardinality fragment multisets; QMAP uses fixed-row tableaus. |
| One cost contract | `REFUTED` | AB counts live fragments; QMAP minimizes gate count, two-qubit gate count, or depth. |
| Realized weak terminal | `CANNOT_CHECK` | The representation/move/cost map fails first. |
| Production reducibility/irreducibility | `CANNOT_CHECK` | It would refer to a non-faithful mapped object. |
| State-volume or runtime consequence | `CANNOT_CHECK` | No common enumeration architecture survives the contract audit. |

## Why quotienting does not repair the map

One could force a resemblance by quotienting away tableau rows as garbage, or
by adding row deletion, allocation, or deallocation. Those operations are not
in QMAP's frozen complete synthesis inventory. Adding them would change the
external state and move contract after seeing the adverse result. It is
therefore disallowed rather than treated as a repair.

The mismatch is also not evidence that prior work absorbs the AB theorem or
that AB has no incremental value. Those conclusions require a faithful nearest-
work comparison under the same representation and legal moves. That comparison
does not exist here, so the correct issue terminal is `CANNOT_CHECK`, not
`AB_EXTERNAL_CASE_ABSORBED_BY_PRIOR_WORK` or
`AB_EXTERNAL_CASE_NO_INCREMENTAL_VALUE`.

## Executable checks

`qmap_ab_faithfulness.py` implements the phase-free QMAP actions, exhaustive
bijection checks for 2–5 qubits, GF(2) rank checks, the two AB counterexamples,
inverse closure, and the machine-readable disposition. The result is frozen in
`QMAP_AB_MAPPING_RESULT.json`. `verify_lane_b_evidence.py` checks internal hashes,
the generated result, source-binding fields, and—when an external cache is
provided—the exact upstream source and paper bytes.

These checks are conformance and invariant evidence. QMAP itself was not built
or executed because the necessary faithfulness obligations were already
refuted. Running it could not convert a representation mismatch into an AB
realization.

## Claim ceiling and next discriminator

This audit grants none of the following: external production realization,
runtime/state-volume improvement, hardware advantage, novelty, journal
acceptance, or a Q1 extension.

The next smallest discriminator is frozen as:

`EXTERNAL_MOVE_DECREASES_LIVE_FRAGMENT_CARDINALITY_WITHOUT_GARBAGE_QUOTIENT`

Only an open optimizer whose native legal move inventory satisfies that
discriminator should be considered for the next Lane B candidate.
