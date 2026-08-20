# ORION-Q MAX-R6 novelty saturation pre-audit

Date: 2026-08-20
Parent: #679
Branch: `shadow/orion-q-max-r0`
Status: pre-audit frozen before any prospective MAX-R6 subject coefficient read.
Authority: research planning only; this document cannot self-authorize novelty.

## Candidate R6 object

The candidate reusable method is **composition-aware anticommuting block-encoding compilation with auxiliary-frame optimization**.

It is deliberately narrower than `new block encoding from scratch` and stronger than `combine known donors`.

The candidate method jointly chooses:

1. a partition of a Pauli Hamiltonian into blocks;
2. block cardinality;
3. block construction (`PAULI`, direct anticommuting unitary, TARE-corrected unitary);
4. for corrected TARE blocks, the pairwise-anticommuting auxiliary family `R_k` and target assignment rather than using a fixed canonical family;
5. native anchors with `R_k = P_k`, for which `T_k = I` and no correction is required for that branch;
6. controlled implementation resources;
7. outer LCU block count / PREP / selector cost;
8. a non-scalar Pareto certificate plus proof-carrying symplectic witnesses.

The R6 claim is *not* anticommuting grouping, TARE, symplectic compilation, or fast SELECT individually.

## Nearest-work subtraction

### TARE / Schillo--Sturm--Quay, arXiv:2601.05740v4

Absorbed facts:

- arbitrary target Pauli strings up to `m <= 2n+1` can be paired with a freely chosen mutually anticommuting auxiliary family;
- the TARE normalization is `sqrt(m) ||alpha||_2`;
- `Uanti` has an explicit `2m-1` Pauli-exponential implementation;
- Tag is Clifford;
- Restore maps `R_k` to `P_k` via `T_k R_k = P_k`;
- larger operators can be split and the resulting TARE encodings composed by LCU.

Explicit residuals stated by the donor paper itself:

- operators above `2n+1` terms can be split, but the splitting/partitioning problem is not further explored;
- the auxiliary family is free and the paper's numerical study fixes a canonical family;
- the conclusion explicitly identifies choosing `{R_k}` to maximize matches `alpha_k P_k = rho_k R_k` as future work; such matches make `T_k = I`, remove tagging/restoration for that term, and can reduce effective tagging states / ancilla / depth;
- systematic comparison over intermediate ancilla widths and stronger PREP constructions remains open.

These residuals are first-class donor gaps, not evidence of novelty by themselves.

### Direct anticommuting unitary partitioning

Izmaylov/Yen/Verteletskyi and related unitary-partitioning work owns the identity

`sum_{j in G} a_j P_j = ||a_G||_2 U_G`

for mutually anticommuting groups and the use of clique/graph partitions. Direct anticommuting cliques are therefore donor capability.

### FOQCS-LCU

Fast one-qubit-controlled SELECT is absorbed as an outer-control donor. Its public implementation supplies structure-specific PREP constructions (e.g. Heisenberg/spin-glass) and a fast SELECT layer; it does not supply a generic chemistry coefficient/check-state PREP that may be costed as zero. R6 must report this donor rather than dismiss it.

### Low-gate second-quantized block encoding

Liu et al., arXiv:2510.08644, owns a distinct second-quantized access/oracle route using lookup / SELECT-SWAP ideas, with improved asymptotic T complexity and subnormalization in fixed-particle sectors. It is a stronger-interface donor, not evidence that a Pauli-list compiler is globally superior.

### Symphony / global BSF compiler

Yang et al., arXiv:2608.11579, owns global binary-symplectic simplification and rescheduling for Pauli exponential sequences, with strong two-qubit-count/depth reductions. Any post-block Pauli-exponential sequence must give Symphony first right of refusal where its semantics apply.

### Non-Clifford Fusion

Li et al., arXiv:2510.13573, owns group transformations / simultaneous synthesis reducing T resources for Hamiltonian-simulation Pauli exponential sequences. It is a downstream compilation donor.

### Controlled time-evolution sign-flip grouping

Fujiwara--Yamamoto--Ishikawa, arXiv:2606.06070, owns a recursive binary-symplectic grouping method for controlled time evolution that assigns sign-flip Pauli strings to groups to remove repeated ancilla control. It is an adjacent controlled-circuit donor and must be checked before any broad `controlled Pauli compiler` claim.

## Current saturation statement

No located donor in the searched 2019--2026 block-encoding / anticommuting-grouping / controlled-Pauli / Hamiltonian-compilation neighborhood was found to jointly own all of:

`partition > block cardinality > direct-vs-corrected representation > free auxiliary anticommuting frame selection > native-anchor maximization > controlled resource accounting > outer-LCU cardinality/PREP accounting > proof-carrying Pareto selection`.

This is a bounded search statement, not a novelty certificate.

## How this search can still be falsely flat

- a compiler paper may call auxiliary-frame selection `stabilizer synthesis`, `symplectic completion`, or `Pauli frame optimization`;
- a measurement-grouping paper may contain the same combinatorial optimization but not call it block encoding;
- a multiplexor/quantum-ROM paper may subsume outer-control optimization without mentioning Hamiltonians;
- a QETU controlled-evolution paper may expose equivalent sign-flip grouping under a different primitive;
- TARE follow-up work may appear after the frozen literature date;
- generic Clifford synthesis could solve the free-`R_k` search once the constraints are encoded.

## Prospective discriminator reserved without coefficient read

Repository: `npbauman/DUCC-Hamiltonian-Library`
Commit: `be306f5830549304176365750d712093950bbdde`
Subject: N2, cc-pVTZ, 6 electrons / 6 active orbitals, stretched geometry `1.5_Eq-3.1020au`, DUCC2.
Path: `N2/cc-pVTZ/6Elec_6Orbs/1.5_Eq-3.1020au/DUCC2/N2.cc-pvtz.ducc.results.txt`
Git blob: `6ab53f2a83c1f8ab5cc3bf4309525fb1ec7421dd`

Only path/tree/blob metadata was inspected before this freeze. The coefficient file must remain unread until the R6 implementation hypothesis and gates are frozen.

## R6 promotion requirements

R6 is eligible only if all of the following hold:

1. MAX-R5H (or its corrected successor) establishes a donor-composed real-method incumbent rather than a weak baseline;
2. full general-m TARE is either implemented faithfully or bounded by a strictly stronger donor relaxation sufficient to rule out domination of the candidate;
3. the candidate uses a method-language operation absent from the frozen donor implementation, specifically optimized auxiliary-frame/native-anchor selection or a stronger residual exposed by hostile review;
4. the method is implemented before opening the prospective subject;
5. the fresh subject improves a non-compensatory resource vector against the strongest donor-composed baseline under matched access and tolerance;
6. every promoted block carries a checkable symplectic / normalization / circuit witness;
7. a structurally independent replay reproduces the result;
8. a final hostile literature pass finds no donor that already owns the complete method object.

If any item fails, R6 stays closed and the failure becomes the next research residual.
