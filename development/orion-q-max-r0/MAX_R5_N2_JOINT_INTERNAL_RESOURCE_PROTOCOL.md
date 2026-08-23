# ORION-Q MAX-R5 fresh N2 joint internal-resource confirmation protocol

Date: 2026-08-20
Parent programme: #633
MAX programme: #679
Real-method lane: #698
Branch: `shadow/orion-q-max-r0`
Status: **FROZEN BEFORE READING THE LOCKED N2 DUCC COEFFICIENT FILE**
Authority if positive: bounded R5 internal-resource confirmation only; not R6, not novelty authority, and not full outer-composition authority.

## Research question

After absorbing both TARE v4 and direct anticommuting-unitary partitioning into the incumbent, can a structure-aware split compiler reduce an exactly realized m=2 internal two-qubit resource coordinate on a fresh public N2 Hamiltonian while preserving an explicit block-encoding normalization budget and all matched access/ancilla assumptions?

This protocol deliberately separates the **internal pair-block circuit** from the **outer LCU recombination**. A positive internal result cannot be promoted to full R5 method authority until the outer controlled composition is accounted for and independently replayed.

## Pre-freeze accounting correction

The development-only H2O script `max_r5_h2o_full_pair_gate_development.py` exposed a joint-realizability defect in its convenience shortcut for target pairs that already anticommute:

- its direct shortcut charged only the `U_anti` two-qubit cost;
- but its reported normalization still used the m=2 TARE factor `sqrt(2) ||a_G||_2`;
- `U_anti` alone on an already anticommuting target pair is instead a direct unitary block with normalization `||a_G||_2`.

Those two coordinates therefore refer to different circuits. The prior H2O number remains development-only diagnostic evidence and is **not** accepted as a jointly realizable `(Lambda,G)` receipt.

MAX-R5 fixes this before the N2 coefficient file is opened.

## Locked fresh subject

Repository: `npbauman/DUCC-Hamiltonian-Library`

External commit: `be306f5830549304176365750d712093950bbdde`

Subject: N2 equilibrium, cc-pVTZ, 6 active electrons / 6 active spatial orbitals, DUCC2.

Path:

`N2/cc-pVTZ/6Elec_6Orbs/1.0_Eq-2.0680au/DUCC2/N2.cc-pvtz.ducc.results.txt`

Locked blob:

`15369e8e886efbb3d32f3b2dfe2cfbb96ddebeba`

Frozen semantic map: repository extractor semantics -> fixed Jordan-Wigner -> no tapering -> 12 spin-orbital qubits.

The coefficient content of this blob is protected until this protocol commit exists on the MAX branch.

## Atomic obligations

### O1 semantic reconstruction

The confirmation harness must verify the locked blob and reconstruct the DUCC Hamiltonian with the same extractor semantics used for R4D. It must report:

- spin-orbital qubit count;
- Pauli term count including and excluding identity;
- maximum imaginary residual after Jordan-Wigner aggregation;
- source repository, commit, path and blob;
- identity coefficient separately.

Any source/hash/semantic mismatch is a hard failure.

### O2 exact m=2 TARE internal circuit

For a non-direct pair `(P0,P1)` with coefficient vector `a=(a0,a1)`, the m=2 TARE block uses one local ancilla and an exact auxiliary representation `(R0,R1,S,T0,T1)` obeying

- `R0` anticommutes with `R1`;
- `S` commutes with `R0`;
- `S` anticommutes with `R1`;
- `Tk Rk = Pk` up to Pauli phase.

For the standard ordered `U_anti` implementation, the internal two-qubit coordinate is

`G_TARE = 4(w(R0)-1) + 2(w(R1)-1) + 2w(S) + w(T0) + w(T1)`.

The minimum must be taken over both orientations and every valid local symplectic representation using the exact 8-state min-plus dynamic program. No heuristic replacement is allowed for this local optimization.

The pair normalization is

`lambda_TARE = sqrt(2) * sqrt(|a0|^2 + |a1|^2)`.

The internal arbitrary coefficient-rotation count is exactly three per pair for the frozen `U_anti` realization.

### O3 absorbed direct anticommuting-unitary block

If the target strings themselves anticommute, the donor-composed incumbent may use them directly as the anticommuting unitary representation. This is a **different block type**, not a free TARE shortcut.

For orientation `(P0,P1)`,

`G_DIRECT = 4(w(P0)-1) + 2(w(P1)-1)`,

minimized over the two orientations, and

`lambda_DIRECT = sqrt(|a0|^2 + |a1|^2)`.

It uses the same three ordered Pauli rotations. For interface matching, one local ancilla qubit may be allocated but left untouched, so the candidate never wins by secretly reducing width. Tag/Restore are absent because the target pair is already the unitary anticommuting block.

Every reported pair must bind `block_type`, `lambda_pair`, `G_pair`, orientation and representation receipt so that normalization and gate cost refer to the same realizable circuit.

### O4 donor-composed bounded incumbent

Terms are sorted by decreasing coefficient magnitude only after semantic reconstruction.

Within each consecutive four-term window, enumerate all three perfect pairings. For every edge use the stronger available block type:

- direct anticommuting unitary when admissible;
- otherwise exact m=2 TARE.

The **bounded donor-composed incumbent** chooses, independently in each quartet, the pairing with minimum jointly realizable `Lambda_joint = sum(lambda_pair)`; ties are broken by minimum `G_internal_2q`, then a frozen lexicographic pairing order.

This incumbent therefore already absorbs TARE, coefficient-aware splitting within the bounded window, exact symplectic representation optimization, and direct anticommuting-unitary partitioning. The older pure-TARE adjacent theorem optimum must still be reported as a diagnostic reference, but it is not the primary R5 baseline.

If an odd singleton exists, it is carried as a one-term unitary block with `lambda=|a|`, zero internal two-qubit cost for the pair coordinate, and a separately reported singleton flag.

### O5 structure-aware successor

The successor is allowed the same three pairings per quartet and the same exact per-edge block implementations. It may move away from the local minimum-normalization incumbent only to reduce `G_internal_2q`.

Prospective moves are ranked by a frozen deterministic efficiency rule based on exact `Delta G / Delta Lambda`, with zero-normalization-cost improvements ranked first. The global move order and tie-breaking must be deterministic and independent of protected outcomes.

Large-Hamiltonian rematching is **constructive/bounded**, not claimed globally optimal.

## Frozen primary gates

All gates are non-compensatory; failure of any one blocks the R5 confirmation state.

1. **Semantic gate**: locked source/blob and exact reconstruction pass; expected system size is 12 qubits; maximum JW imaginary residual `<= 1e-12`.
2. **Realizability gate**: every pair's reported `(lambda_pair,G_pair)` must come from the same explicit block type and satisfy the exact algebraic obligations above.
3. **Matched-count gate**: successor and incumbent have the same number of outer blocks (apart from the same deterministic singleton treatment), the same number of internal coefficient rotations (`3 * number_of_pairs`), and no larger allocated local-ancilla capacity per pair block.
4. **Normalization gate**: `Lambda_successor / Lambda_incumbent - 1 <= 0.01`.
5. **Prospective internal-G gate**: `(G_incumbent - G_successor) / G_incumbent >= 0.001` (**at least 0.10% exact reduction**).
6. **No-oracle gate**: both methods receive exactly the same reconstructed Pauli list, coefficient values, commutation tests, classical compute budget class and verifier semantics. No amplitude oracle, qRAM, tapering, hidden symmetry oracle or stronger precision assumption may appear only on the successor side.
7. **Outer-separation gate**: the receipt must explicitly mark `G_internal_2q` as **uncontrolled pair-block cost**, not total outer-LCU cost, and must emit the outer-composition report below.

The 0.10% threshold is frozen prospectively. It is intentionally slightly stronger than the invalid convenience H2O diagnostic magnitude (~0.0967%) rather than tuned below it.

## Mandatory secondary reports

These do not compensate for primary-gate failure.

- pure-TARE adjacent theorem-optimal split normalization;
- donor-composed incumbent `Lambda_joint` and `G_internal_2q`;
- successor `Lambda_joint` and `G_internal_2q`;
- exact normalization overhead and exact G reduction;
- count of direct-unitary blocks and TARE blocks in each method;
- distribution/hash of per-block normalizations;
- distribution/hash of per-block internal G costs;
- coefficient-rotation count;
- local-ancilla allocation;
- zero-slack successor result;
- 5% diagnostic slack result, clearly non-authorizing.

Also report the non-authorizing product diagnostic

`(Lambda_successor / Lambda_incumbent) * (G_successor / G_incumbent)`

without using it to hide either vector coordinate.

## Outer LCU composition report — mandatory but not yet authorizing

Because N2 has more terms than a single TARE block can generally hold, the pair blocks are recombined by an outer LCU-like layer. The confirmation receipt must separately report:

- number of outer blocks `B`;
- outer address width `ceil(log2 B)`;
- normalization weight vector `lambda_pair` hash;
- reference outer Prepare state-preparation model and rotation count;
- one shared local block ancilla capacity and whether it can be reused serially;
- distinction between uncontrolled pair-block `G_internal_2q` and controlled block invocation inside outer `SELECT`;
- any qROM/qROAM/q_switch/workspace assumption if used;
- total outer normalization `Lambda_joint`.

The N2 confirmation is not allowed to invent a total controlled-SELECT CNOT/T/T-depth advantage unless that circuit has actually been synthesized under matched controls. Outer controlled composition is a mandatory R5 closure task after the fresh internal result.

## Hostile checks

- swap every pair orientation and verify the reported minimum does not increase;
- brute-force the 8-state DP against exhaustive local-state enumeration on small random Pauli pairs;
- for direct anticommuting target pairs, verify `lambda_DIRECT=||a||2` and never reuse the TARE `sqrt(2)||a||2` value;
- force a direct-pair case where `G_DIRECT` is lower but its block type/normalization receipt is intentionally mismatched; strict wrapper must reject it;
- permute quartet ordering while preserving coefficient sort/tie rules and verify deterministic output;
- inject a source hash mismatch; fail closed;
- inject a 13th qubit / orbital-count mismatch; fail closed;
- inject imaginary JW residue above tolerance; fail closed;
- verify candidate cannot change pair count or rotation count to buy G reduction;
- report if the 1% normalization budget is unused rather than silently enlarging it;
- separately verify outer report is present before any `R5_*_SUPPORTED` terminal can be emitted.

## Reopen logic

If the fresh N2 primary gates fail, preserve the receipt and immediately diagnose responsibility:

1. If G cannot improve at fixed bounded representation, enlarge the rematching neighborhood (e.g. 6/8-term exact windows or sparse matching) before relaxing scientific gates.
2. If direct-unitary absorption dominates and TARE contributes no residual value, promote the hybrid matching problem itself as the new incumbent and search for the next structural layer (global/sparse matching, controlled-select-aware edge costs, or larger TARE blocks).
3. If normalization erases the internal advantage, optimize the actual outer-controlled cost jointly with normalization rather than weakening the normalization gate.
4. If controlled outer SELECT reverses the internal ordering, replace `G_internal_2q` with an exact controlled-block coordinate and rerun on a new frozen subject; do not retroactively reinterpret N2.
5. If a stronger published compiler already solves the full joint problem, absorb it and compare against that stronger incumbent.

A negative N2 result is therefore a responsibility diagnosis and next programme, not `NO_INCREMENTAL_VALUE` closure.

## Frozen authority language

If and only if all primary gates pass, the strongest immediate terminal is:

`MAX_R5_N2_JOINT_INTERNAL_RESOURCE_CONFIRMATION_SUPPORTED`

This means only that, on the locked fresh N2 public Hamiltonian, a bounded structure-aware compiler improved an exact jointly realizable **internal** m=2 block resource coordinate over the bounded donor-composed incumbent under matched semantics and a frozen normalization budget.

It does **not** establish full controlled outer-LCU resource superiority, global matching optimality, QSVT-level speedup, or novelty. Those remain required before R5 closure and are mandatory before any R6 claim.
