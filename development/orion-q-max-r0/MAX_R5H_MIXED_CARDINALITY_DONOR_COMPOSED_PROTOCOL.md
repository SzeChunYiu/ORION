# ORION-Q MAX-R5H mixed-cardinality donor-composed protocol

Date: 2026-08-20
Parent: #679 / #698
Branch: `shadow/orion-q-max-r0`
Status: frozen before MAX-R5H development outcome generation.
Authority ceiling: donor absorption / development on already-open N2 and H4; cannot by itself authorize R6.

## Reopen cause

MAX-R5F fresh H4 and MAX-R5G independent replay establish a positive controlled-composition-aware **pair compiler**. The next donor-composed incumbent is stronger: mutually anticommuting Pauli strings can be grouped into arbitrary-size Hermitian unitaries, not only pairs.

Known unitary partitioning gives, for any pairwise anticommuting group `G`,

`A_G = sum_{j in G} a_j P_j = ||a_G||_2 U_G`,

where `U_G` is unitary. Therefore multi-term anticommuting grouping is donor capability, not ORION novelty.

TARE v4 supplies an explicit circuit construction for an `m`-term anticommuting unitary using `2m-1` Pauli exponentials. That construction is absorbed as the resource model for direct multi-term clique blocks.

## Development question

After absorbing arbitrary direct anticommuting clique blocks, does a **joint mixed-cardinality compiler** still improve the donor-composed incumbent under matched normalization, controlled Clifford+T resources, outer block count, PREP reference cost, access, ancilla, and synthesis tolerance?

## Atomic questions

1. How much of R5F's gain is already captured by donor-only anticommuting clique cover?
2. Is minimum-block clique cover the right objective once coefficient normalization and fault-tolerant implementation cost are included?
3. Can exact local set-partitioning jointly choose singleton Pauli blocks, direct anticommuting cliques, and m=2 TARE blocks better than either donor alone?
4. Does a larger direct clique's lower normalization survive its `2m-1` controlled Pauli-rotation implementation cost?
5. Does changing block cardinality cross an outer PREP address-width boundary, and if so is that gain/loss explicitly charged?
6. Is there a nontrivial Pareto successor after the strongest direct-clique donor is absorbed?

## Donors absorbed

- Pauli LCU / singleton Pauli blocks.
- Izmaylov/Yen/Lang/Verteletskyi unitary partitioning: mutually anticommuting clique grouping with group normalization `||a_G||_2`.
- TARE v4 explicit anticommuting-unitary circuit using `2m-1` Pauli exponentials.
- R5G independently replayed controlled pair compiler: exact m=2 TARE auxiliary representation + direct pairs + exact coefficient-local matching.
- FOQCS-LCU as a separate outer-SELECT donor. Its generic chemistry PREP burden is not assumed free; its SELECT-only capability is reported as a lower-bound comparator rather than silently omitted.
- Symphony/PHOENIX-style binary-symplectic sequential Pauli compilation as a later circuit donor where coherent SELECT semantics can be proved to survive.

## Frozen block alphabet

Every nonidentity Pauli term must belong to exactly one block.

### S1: Pauli singleton

For one term `(a,P)`:

- normalization: `|a|`;
- outer-controlled Pauli support two-qubit primitive reference: `wt(P)`;
- synthesized-Rz T cost: `0`;
- block cardinality: `1`.

The coefficient magnitude/sign is handled by outer PREP/phase exactly as in Pauli LCU.

### S2: m=2 pair block

For two terms, use the jointly realizable minimum between the constructions that are actually valid:

- if the targets anticommute, DIRECT_ANTI_UNITARY with normalization `hypot(|a0|,|a1|)` and exact best orientation;
- otherwise TARE_M2 with normalization `sqrt(2)*hypot(|a0|,|a1|)` and the exact R5C/R5G `8 parity states x 2 Restore-base branches x 2 target orientations` controlled-CNOT representation.

No block may use the normalization of one construction with the circuit of another.

### Sm: direct anticommuting clique, `m >= 3`

Admissible iff every distinct pair of Pauli strings anticommutes.

Normalization:

`Lambda_G = sqrt(sum_j |a_j|^2)`.

Circuit donor: the absorbed `2m-1` Pauli-exponential anticommuting-unitary implementation.

For an ordering with central/once-applied axis `P_last`, uncontrolled parity CNOT support is

`4 * sum_{j != last}(wt(P_j)-1) + 2*(wt(P_last)-1)`.

The order is otherwise free with angles recomputed for the permuted coefficient vector. Therefore the exact minimum chooses a maximum-weight Pauli string as the central `last` axis. This local ordering rule is derived from the donor circuit formula and is not claimed as standalone novelty.

Under the frozen R5B controlled-Rz projection:

- controlled-Rz count = `2m-1`;
- synthesized Rz instances = `2*(2m-1)`;
- projected T = `2*(2m-1)*48`;
- fixed controlled-Rz CNOT = `2*(2m-1)`;
- total controlled CNOT = parity support + fixed controlled-Rz CNOT;
- no TARE Tag/Restore ancilla is used for a direct clique.

All direct-clique pairwise anticommutation relations and the chosen central axis must be proof-checked.

## Frozen local search

Use the already-open H4 and N2 sorted Pauli lists as development subjects.

Partition each contiguous 12-term coefficient-local window exactly by **subset dynamic programming**. Candidate blocks are:

- every singleton;
- every 2-subset, using the exact S2 construction;
- every pairwise-anticommuting subset of size `3..12`, using Sm.

The DP must enumerate all admissible blocks in the window and all exact set partitions reachable from them. It may Pareto-prune only by jointly valid dominance coordinates.

## Resource vector

For every complete local/global partition report:

- `Lambda`;
- controlled block-internal `CNOT`;
- projected block-internal `T`;
- outer block count `B`;
- direct-clique cardinality histogram;
- TARE block count;
- singleton count;
- maximum local ancilla capacity.

### Outer reference cost when `B` changes

Let `q = ceil(log2 B)` and `P = 2^q` for `B>1`.

Report separately and also in a reference total:

- dense real-amplitude PREP rotations per PREP: `P-1`;
- two-sided PREP rotations: `2(P-1)`;
- reference PREP T: `2(P-1)*48` at the frozen synthesis precision;
- unary selector-routing T reference: `4(B-1)`;
- reference total T: `block_internal_T + PREP_T + selector_routing_T`.

This reference model is intentionally conservative/simple and matches the previous R5B bookkeeping style. No claim of optimal PREP is allowed from it.

CNOT for generic PREP is reported as `UNRESOLVED_GENERIC_PREP_CNOT` unless an explicit matched synthesis is implemented; block-internal CNOT therefore remains a separate non-compensatory coordinate.

## Baselines

For each open subject report:

B0 Pauli LCU singleton decomposition.

B1 R5G pairwise controlled compiler (the independently replayed pair-only system).

B2 donor-only direct-antipartition baseline: exact same 12-term windows, block alphabet restricted to singletons + arbitrary direct anticommuting cliques; choose the exact Pareto set rather than minimum clique count alone.

B3 donor-composed mixed alphabet: singletons + direct cliques + m=2 TARE.

ORION receives no credit merely for recovering B2. B2 is absorbed into the incumbent.

## Global composition

Compose exact local window Pareto sets with a sparse global Pareto DP. Do not scalarize into one reward.

A state dominates another only if it is no worse in all of:

- normalization;
- block-internal CNOT;
- block-internal projected T;
- reference total T;
- block count;
- maximum ancilla capacity;

and strictly better in at least one.

The development harness may return the full compact Pareto set plus named points chosen by deterministic constraints.

## Frozen named endpoints

### P-LAMBDA
Minimum normalization state, reported with all resources.

### P-FT
Minimum reference-total-T state subject to normalization <= the R5G pair compiler normalization and block-internal CNOT <= the R5G pair compiler CNOT.

### P-CNOT
Minimum block-internal CNOT state subject to:

- normalization <= R5G normalization;
- reference total T <= R5G reference total T;
- maximum ancilla capacity <= R5G;

### P-BALANCED
A non-scalar Pareto witness that simultaneously satisfies:

- normalization <= R5G normalization;
- block-internal CNOT <= R5G CNOT;
- block-internal T <= R5G block-internal T;
- reference total T <= R5G reference total T;
- and at least one strict improvement of >=1%.

If no such point exists, preserve the negative and move to selector/PREP co-design.

## Development success criterion

MAX-R5H is a donor-composed development positive only if B3 contains P-BALANCED and B3 is **not identical to B2** at that point. The selected point must use at least one TARE block or otherwise demonstrate a mixed-alphabet feature unavailable to donor-only direct clique partitioning.

This gate intentionally prevents claiming ORION value for merely rediscovering unitary partitioning.

## FOQCS hostile comparator

For each subject report:

- original Pauli-term count `L` and system qubits `n`;
- FOQCS check-matrix SELECT two-qubit layer reference where supported by its published construction;
- its required selection/check ancillas from the donor implementation/paper if resolved;
- generic coefficient/check-state PREP status.

If a fair generic PREP cannot be instantiated from the donor, report `GENERIC_PREP_NOT_SUPPLIED_BY_DONOR_IMPLEMENTATION`; do not either grant zero PREP cost or dismiss the donor.

## Failure response

If B2 absorbs all of B3's value, direct-clique partitioning becomes the incumbent and ORION must climb to outer-selector/PREP co-design.

If B3 improves normalization but loses FT resources, open a selector-aware mixed-block circuit compiler rather than relaxing the non-compensatory gates.

If block-count/PREP dominates, attack PREP representation (check-matrix, QROM/QROAM, alias sampling, structured coefficient loading) under matched access assumptions.

If exact 12-term windows hide cross-window cliques, open a certified global graph/set-partition bound rather than merely increasing window size until a preferred answer appears.

## Fresh-subject rule

R5H uses only already-open N2/H4. Any later immutable-domain promotion requires a new frozen subject/protocol after this donor-composed development result is known.
