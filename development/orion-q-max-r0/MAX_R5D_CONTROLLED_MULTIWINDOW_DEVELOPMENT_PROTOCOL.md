# ORION-Q MAX-R5D controlled multiwindow development protocol

Date: 2026-08-20
Parent: #679 / #698
Branch: `shadow/orion-q-max-r0`
Status: frozen development-only protocol before MAX-R5D outcome generation.
Authority ceiling: development mechanism only; N2 is already open. This protocol cannot authorize R5 or R6.

## Responsibility diagnosis from R5B/R5C

R5B independently replayed the N2 internal advantage but showed that the original uncontrolled objective can worsen a fixed Clifford+T outer-control projection. R5C repairs the local representation objective by minimizing controlled CNOT cost exactly while making projected T non-compensatory. On the fixed adjacent/quartet matching, however, quartet-local moves have almost no remaining freedom.

The residual hypothesis is therefore not `controlled cost is impossible to improve`; it is:

> the useful controlled-cost moves are distributed across a larger coefficient-local matching neighborhood than a four-term quartet.

This packet widens only the matching representation. It does not change the Hamiltonian, access model, synthesis precision, normalization formulas, direct/TARE semantics, or frozen R5B fault-tolerant projection.

## Donors absorbed before development

- TARE v4: Tag-and-Restore block construction and normalization semantics.
- anticommuting unitary partitioning/direct anticommuting blocks.
- R4B adjacent equal-size split majorization theorem as the pure-TARE coefficient baseline.
- R5B controlled outer-LCU projection and proof-carrying witness discipline.
- R5C exact `8 parity states x 2 Restore-base branches x 2 orientations` controlled-CNOT auxiliary-representation DP.
- FOQCS-LCU (arXiv:2507.20887): check-matrix SELECT can move cost from multi-control routing to singly controlled Pauli layers when a suitable PREP is available. This is absorbed as an outer-SELECT donor and must be included in later donor-composed closure; it does not by itself supply a generic low-cost PREP for the N2 coefficient/check-string distribution.
- Symphony (arXiv:2608.11579): global binary-symplectic simplification is absorbed as a compiler donor for sequential Pauli-exponential networks; its applicability to coherent multiplexed SELECT must be established rather than assumed.

## Atomic development questions

1. After exact controlled-cost auxiliary optimization, does a larger local perfect-matching neighborhood expose materially more CNOT savings than quartet rematching?
2. Can every accepted matching preserve or improve projected T count (equivalently, not reduce direct anticommuting-block count under the frozen per-block projection)?
3. Can the search remain within a <=1% total normalization increase over the absorbed controlled-cost adjacent incumbent?
4. Can the larger search be exact inside each frozen window rather than heuristic over candidate pairings?
5. Does a positive result survive comparison to the original R5B incumbent, not merely to a weakened or redefined baseline?
6. Where does the advantage come from: auxiliary representation, rematching, direct-block retention, or normalization expenditure?

## Frozen development method

### Local edge authority

For every pair of Pauli terms, use R5C semantics:

- direct anticommuting pair: exact direct orientation, normalization `hypot(|a|,|b|)`, projected T = 288;
- TARE pair: normalization `sqrt(2)*hypot(|a|,|b|)`, exact controlled-CNOT auxiliary representation from the 8-state x 2 Restore-base x 2 orientation DP, projected T = 322.

No edge may use the normalization of one construction with the circuit cost of another.

### Window search

Sort terms once by descending coefficient magnitude with the existing deterministic Pauli-key tie break.

Partition into contiguous windows of 10 terms, with any even tail handled as its own smaller window. Within each window enumerate **all perfect matchings** (945 for a full 10-term window). Compute the exact vector

`(Lambda, controlled_CNOT, projected_T, direct_count)`

for every matching and retain the nondominated local frontier.

The window size 10 is frozen before running MAX-R5D. It is large enough to strictly contain quartet search while keeping exact enumeration auditable.

### Global composition

Compose one local frontier choice per disjoint window. Retain global nondominated states under:

- total normalization increase <= 1% of the absorbed controlled-cost adjacent incumbent;
- projected T <= incumbent projected T;
- minimize controlled CNOT.

Because normalization is continuous, global search may use a deterministic sparse Pareto frontier rather than discretizing Lambda. A state dominates another only when it is no worse in normalization increase, projected T, and CNOT and is strictly better in at least one coordinate.

If exact frontier growth becomes computationally excessive, fail closed and record the saturation point; do not silently switch to a weighted scalar reward.

## Required baselines

B0 original R5B donor-composed adjacent incumbent under the frozen outer projection.
B1 R5C controlled-cost auxiliary optimization on the same adjacent pair list.
B2 quartet-only controlled rematching from R5C.
B3 MAX-R5D exact 10-term-window composed frontier.

Report all four. A claimed development positive must improve B1 and B2 and must also be compared to B0.

## Development success gates

A MAX-R5D development positive requires all of:

- exact per-edge controlled-cost DP semantics unchanged;
- all windows exhaustively enumerated;
- projected T no worse than B1;
- normalization overhead <=1% versus B1;
- controlled CNOT strictly lower than B2;
- controlled CNOT at least 0.5% lower than B0, to justify freezing a fresh subject rather than promoting noise-level movement;
- no stronger oracle, coefficient access, ancilla assumption, synthesis tolerance, or PREP/SELECT omission than R5B.

The 0.5% threshold is frozen before MAX-R5D outcome generation. It deliberately exceeds the ~0.29% combined local-representation + quartet improvement currently visible on open N2.

## Failure response

If the 10-term exact windows fail the 0.5% gate:

1. preserve the negative;
2. diagnose whether the remaining obstruction is the fixed pair cardinality, direct-vs-TARE block alphabet, disjoint-window boundary, or outer-SELECT architecture;
3. absorb FOQCS-LCU more deeply by comparing a check-matrix SELECT representation and its PREP burden;
4. open the next materially different representation: mixed block cardinalities / direct multi-term anticommuting blocks / outer-selector co-design, rather than merely increasing window size indefinitely.

## Fresh-subject rule

H4/cc-pVDZ/2.0au/DUCC3 remains protected. Its DUCC path and blob metadata may be known, but its coefficients must not be opened until a separate fresh protocol is frozen after the N2 development outcome.
