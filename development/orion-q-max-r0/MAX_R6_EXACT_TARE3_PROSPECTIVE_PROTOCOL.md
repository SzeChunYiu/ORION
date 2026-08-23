# ORION-Q MAX-R6 exact TARE-3 prospective protocol

Date: 2026-08-20
Parent programme: #679
Branch: `shadow/orion-q-max-r0`
Status: frozen before any stretched-N2 coefficient read.
Authority ceiling before the final replay receipt: below R6.

## Candidate object

The bounded candidate is the exact finite-state compiler for three-term TARE auxiliary representations frozen in `MAX_R6_EXACT_TARE3_JOINT_FRAME_DP_PROTOCOL.md` plus Errata 1--3. It jointly optimizes the auxiliary anticommuting frame, distinct two-bit control labels, Tag generators, Restore strings, target assignment and Uanti central axis for the frozen structural objective `C_joint`.

No novelty credit is assigned to TARE, the freedom to choose auxiliary `R_k`, anticommuting grouping, Clifford/symplectic synthesis, Pauli-frame optimization, downstream Pauli-network compilation, state preparation, SELECT, or any other donor capability.

## Gate order

The protected discriminator remains closed unless the already-open exact-TARE3 end-to-end verifier reports all of the following on the same checkout:

1. `software_integrity_pass = true`;
2. `pre_prospective_ready = true`;
3. all three frozen exact-DP errata are bound;
4. `top_four_panel_complete = true` on both open H4 and equilibrium N2;
5. the core solver and independent end-to-end verifier agree on the declared gate conjunction;
6. every protected-reference field still reports no stretched-N2 access.

Failure of any prerequisite is a terminal negative for this prospective attempt and must not open the protected file.

## Frozen fresh subject

Repository: `npbauman/DUCC-Hamiltonian-Library`
Commit: `be306f5830549304176365750d712093950bbdde`
Subject: N2, cc-pVTZ, 6 electrons / 6 active orbitals, stretched geometry `1.5_Eq-3.1020au`, DUCC2.
Path: `N2/cc-pVTZ/6Elec_6Orbs/1.5_Eq-3.1020au/DUCC2/N2.cc-pvtz.ducc.results.txt`
Git blob: `6ab53f2a83c1f8ab5cc3bf4309525fb1ec7421dd`
Extractor dimensions: `n_occ=3`, `n_virt=3`, `n_orb=6`, `n_qubits=12`.

Only this path/tree/blob metadata and dimensions implied by the frozen active space are admitted before release. Coefficient content is not part of this protocol freeze.

## Frozen selection

After the prerequisite gate passes, the fresh subject is parsed with the same DUCC extractor semantics, Jordan--Wigner map, Pauli threshold, ordering and 12-term windows as the open development lane.

The already-frozen candidate-blind P10 scan is applied unchanged. Its improving triples are sorted exactly by

`(-rank2_fraction, -rank2_delta, term_indices)`.

The prospective panel is exactly the first four improving P10 triples. Fewer than four improving triples is a negative prospective outcome. No fifth triple, substitute triple, changed window, or post-outcome reselection is allowed.

All four selected triples are serialized in the receipt regardless of the final sign.

## Matched comparator contract

For every selected triple, the candidate and both comparators receive the identical three Pauli targets and coefficient vector.

The comparators are frozen as:

- `B_CANONICAL_STRONG`: canonical rank-3 TARE frame with all distinct two-bit label assignments, all target permutations, all central axes and exact minimum-weight Tag solutions;
- `B_FRAME_ONLY_STRONG`: the complete global Uanti-minimum auxiliary-frame set characterized by Erratum 3, followed by exact optimization of labels, Tag, Restore and target assignment.

The fixed-block comparison holds constant:

- block cardinality `m=3`;
- coefficient vector;
- TARE normalization `sqrt(3) * ||alpha||_2`;
- five Pauli-exponential Uanti realization (`2m-1`);
- logarithmic TARE ancilla width `a=2`;
- target Pauli strings and parsing/mapping semantics.

Therefore the non-compensatory prospective resource vector is

`(Lambda_TARE3, Uanti_rotation_count, ancilla_width, C_joint)`

with the first three coordinates required equal and only `C_joint` permitted to improve.

## Prospective support gate

A primary fresh-subject receipt is prospective-positive only if all of the following hold:

1. prerequisite open-development verification passed before fresh access;
2. the protected source blob equals the frozen blob;
3. the prospective panel contains exactly four preselected improving P10 triples;
4. every exact-joint proof-carrying witness passes all symplectic, label, dependence, Restore and cost checks;
5. at least one of the four triples satisfies
   `C_joint < min(C_joint(B_CANONICAL_STRONG), C_joint(B_FRAME_ONLY_STRONG))`;
6. no matched resource coordinate was changed to obtain the strict win;
7. all four outcomes, including zero/negative deltas, remain in the receipt.

This primary receipt is not yet R6.

## Independent replay gate

R6 additionally requires a separate verifier implementation that does not call the primary exact-joint optimizer for its optimality decision. For each of the four proof-carrying triples it must:

- reconstruct the targets from the serialized witness;
- recheck the Pauli/symplectic witness relations;
- recompute the exact joint optimum with an independently coded unified-state dynamic program;
- independently recompute the canonical and frame-only comparator optima;
- reproduce the primary `C_joint` and comparator costs exactly;
- recompute the prospective support predicate.

Any disagreement is a negative/integrity failure and R6 stays closed.

## Donor and novelty gate

The final hostile donor/novelty freeze must be committed before the workflow capable of fresh access exists. It must include TARE v4 and the adjacent 2019--2026 anticommuting-unitary, symplectic/Clifford, block-encoding, controlled-Pauli and downstream-compilation donors. A donor that already owns the complete exact joint TARE-specific compiler object closes novelty; donor components never create novelty credit.

## R6 authority

Only the final independent replay receipt may set `r6_earned = true`, and only when the prospective support gate, replay gate, frozen donor/novelty gate and protected-source identity all pass together.

The claim, if earned, is bounded to:

> an exact linear-in-system-qubit finite-state compiler for three-term TARE auxiliary representations that jointly optimizes anticommuting frame, control labels, Tag/Restore support, target assignment and Uanti realization, with proof-carrying witnesses and prospective fresh-subject reproduction.

It is not a claim of whole-Hamiltonian superiority, global block-encoding superiority, asymptotic quantum advantage, or novelty of any donor component.

If any gate fails, preserve the receipt as an R6 negative and return the residual to ORION/ORION-Q responsibility diagnosis.