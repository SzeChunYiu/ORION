# ORION-Q MAX-R5F fresh H4 true-incumbent controlled-matching confirmation protocol

Date: 2026-08-20
Parent: #679 / #698
Branch: `shadow/orion-q-max-r0`
Status: **FROZEN BEFORE OPENING THE H4 DUCC COEFFICIENT FILE**.
Authority ceiling: fresh public-Hamiltonian confirmation of the controlled-composition-aware compiler. Passing this packet alone is not R6 novelty authority.

## Development basis available before freeze

The protocol uses only already-open H2/LiH/H2O/N2 development evidence plus non-coefficient H4 metadata.

N2 MAX-R5E, after the R5D baseline-binding erratum, established the development mechanism against a single jointly realizable incumbent:

- exact controlled-cost m=2 auxiliary representation;
- exact coefficient-local 12-term perfect matching;
- CNOT `12199 -> 11177` (`-8.3777%`);
- projected T `95318 -> 94094` (`-1.2841%`);
- direct anticommuting pairs `104 -> 140`;
- normalization increase `0.6007%`;
- 530,146 perfect matchings exhaustively evaluated;
- all frozen R5E gates passed.

The first R5D apparent positive is explicitly excluded because it compared against a weakened all-TARE adjacent baseline.

## Protected subject

Repository: `npbauman/DUCC-Hamiltonian-Library`

External commit:
`be306f5830549304176365750d712093950bbdde`

Molecule/geometry/method:
`H4 / cc-pVDZ / 2.0 au / DUCC3`

Protected DUCC coefficient path:
`H4/cc-pVDZ/2.0au/DUCC3/H4.cc-pvdz_files/restricted/ducc/H4.cc-pvdz.ducc.results.txt`

Locked blob:
`b98792b1055dbac0ebf2a7576f72412e3e4ac6c5`

The coefficient file has not been opened before this freeze.

Non-coefficient metadata file `H4-info` (blob `ee21a0de56e9a40eeeb455ec367c26699b673e12`) states:

- 4 active spatial orbitals;
- 2 occupied alpha and 2 occupied beta orbitals;
- 2 virtual alpha and 2 virtual beta orbitals.

Therefore the fixed repository-extractor -> Jordan-Wigner/no-taper convention gives **8 spin-orbital qubits**. This qubit count is frozen before coefficient access.

## Scientific question

Does the controlled-composition-aware ORION successor discovered on open N2 reproduce on an untouched public molecular Hamiltonian when every resource coordinate is bound to one jointly realizable donor-composed incumbent?

## Frozen constructions

### Mapping

Use the same faithful sparse port of the DUCC repository extractor as R4D/R5, parameterized only by:

- `N_OCC=2`
- `N_VIRT=2`
- `N_ORB=4`
- `N_QUBITS=8`

Then apply the same fixed Jordan-Wigner convention, no tapering and the same numerical thresholds. Verify source git-blob SHA before parsing.

### Edge alphabet

Every pair must choose exactly one construction whose normalization and circuit resources remain jointly bound:

1. **DIRECT_ANTI_UNITARY** if the two target Pauli strings anticommute:
   - pair normalization `hypot(|a0|,|a1|)`;
   - exact best direct orientation;
   - frozen controlled outer projection inherited from R5B/R5C.

2. **TARE_M2** otherwise:
   - pair normalization `sqrt(2)*hypot(|a0|,|a1|)`;
   - exact auxiliary representation minimizing controlled CNOT via the `8 symplectic parity states x 2 Restore-base branches x 2 target orientations` dynamic program;
   - projected T and ancilla assumptions exactly as R5B/R5C.

No construction may borrow another construction's normalization or resources.

### Donor-composed incumbent B*

Sort nonidentity Pauli terms once by descending coefficient magnitude with deterministic Pauli-key tie break.

Within each consecutive four-term quartet, enumerate all three perfect matchings and select the lexicographic minimum

`(Lambda, projected_T, controlled_CNOT, pattern_id)`.

For an even tail of 2 terms use its unique pair. If the total nonidentity term count is odd, freeze the final smallest-magnitude term as a singleton Pauli-LCU block; its absolute coefficient contributes to normalization and its controlled-Pauli resource must be accounted identically in incumbent and successor rather than silently dropped.

This B* object is the only resource reference for the primary promotion gates.

### Successor E

Partition the paired sorted terms into contiguous **12-term windows aligned at term 0**, so each full window contains three complete incumbent quartets. Use an even final tail as one smaller window.

Enumerate **all perfect matchings** inside every window (10,395 for each full 12-term window). For every matching compute the exact jointly bound vector:

`(Lambda, controlled_CNOT, projected_T, direct_count)`.

Retain the exact local Pareto frontier. Compose windows with an exact sparse global DP keyed by `(direct_count_delta, controlled_CNOT_delta)`, storing minimum normalization delta.

Final admissibility:

- normalization increase <=1% versus B*;
- projected T <= B*;
- direct count >= B*;
- minimize controlled CNOT.

No scalar reward may compensate a T/direct regression with CNOT gain.

## Proof-carrying requirement

A numerical minimum is not enough. For **every selected TARE block** in B* and E, reconstruct an explicit witness `(orientation,R0,R1,S,T0,T1)` and verify:

- `R0` anticommutes with `R1`;
- `S` commutes with `R0`;
- `S` anticommutes with `R1`;
- `T0 R0 = P0` and `T1 R1 = P1` in Pauli-bit representation;
- the controlled-CNOT cost recomputed from the emitted witness equals the DP minimum;
- the chosen Restore-base branch realizes the reported controlled Restore support;
- direct blocks truly anticommute and use the reported orientation.

Emit canonical hashes for sorted terms, pair lists and proof witnesses.

## Frozen primary endpoints

Non-compensatory vector:

- exact semantic reconstruction / Hermiticity residual;
- source blob match;
- qubits and Pauli-term count;
- B* and E total normalization;
- B* and E controlled CNOT;
- B* and E projected T;
- B* and E direct/TARE counts;
- fixed coefficient-rotation count / pair count where applicable;
- local ancilla capacity and outer-address register;
- perfect-matchings-enumerated count;
- proof-witness verification status.

Report dense outer PREP and selector-routing layers separately. Equal common layers may be identified as common but must not be hidden from the receipt.

## Fresh confirmation gates

All must pass:

1. locked source blob matches;
2. DUCC -> JW reconstruction is Hermitian within the existing tolerance;
3. 8-qubit mapping is respected with no tapering;
4. B* is reconstructed as frozen, with one jointly realizable pair/resource list;
5. every full 12-term window exhaustively enumerates 10,395 matchings;
6. all selected B* and E TARE/direct witnesses verify;
7. E normalization overhead <=1.0% versus B*;
8. E projected T <= B* projected T;
9. E direct count >= B* direct count;
10. E controlled CNOT reduction >= **1.0%** versus B*;
11. no stronger oracle/access/ancilla/synthesis tolerance/PREP omission than B*;
12. outer common-layer accounting is present rather than omitted.

The **1.0%** fresh CNOT threshold is frozen before opening H4 coefficients. It is deliberately much smaller than N2's 8.38% development effect while still an order of magnitude above the tiny R5C quartet-only movement.

## Secondary comparisons required after a positive

A positive H4 result is immediately absorbed, then compared against:

- Pauli-LCU;
- coefficient-optimal pure split-TARE;
- direct anticommuting unitary partitioning / clique grouping;
- R5B/R5C pair compiler;
- FOQCS-LCU's check-matrix SELECT, with its actual generic/structured PREP burden and ancilla width stated rather than granting free state preparation;
- relevant global binary-symplectic compilation donors such as PHOENIX/Symphony only where their sequential-Pauli-network transformations preserve coherent block-encoding/SELECT semantics.

## Negative response

If H4 fails any primary gate, preserve the negative and immediately recurse by responsibility:

- direct-count scarcity -> mixed block cardinality / direct multi-term anticommuting cliques;
- controlled-SELECT dominance -> explicit FOQCS-style outer-selector/PREP co-design;
- representation-locality failure -> overlapping/global matching subject to exact or certified bounds;
- fault-tolerant projection sensitivity -> vector Pareto compiler across primitive-level circuits, never a post-hoc scalar proxy.

A negative is not programme closure.

## Authority if positive

At most:

`MAX_R5F_FRESH_H4_CONTROLLED_COMPOSITION_AWARE_COMPILER_SUPPORTED`

This is fresh real-public Hamiltonian evidence for a reusable compiler construction. Full R5/R6 still requires independent replay, donor-composed outer comparison, applicability/failure boundary and hostile novelty authority.
