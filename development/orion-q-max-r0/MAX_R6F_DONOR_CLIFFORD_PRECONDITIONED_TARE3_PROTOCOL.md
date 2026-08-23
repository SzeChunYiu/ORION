# ORION-Q MAX-R6F donor-Clifford-preconditioned exact-TARE3 protocol

Date: 2026-08-21
Parent: #679
Branch: `shadow/orion-q-max-r0`
Status: **FROZEN BEFORE R6F OUTCOME GENERATION**
Authority ceiling: open-subject method development only; not R6 and not novelty.

## Reopen cause

The preserved exact-TARE3 result shows that, on the frozen top-four H4 and equilibrium-N2 development rows, exact joint TARE-3 beats the old canonical frame but ties the complete Uanti-minimal `B_FRAME_ONLY_STRONG` donor. R6B donor-owned identical-transformation reuse is negative. R6D exact six-term 3+3 repartition/co-optimization is also negative: the best candidate and the frame-only incumbent both reach structural cost 16 on H4 and equilibrium N2.

R6E separately scans the complete P10-improving population. R6F does not depend on, alter, or pre-empt the R6E sign. It tests a different representation coordinate on the same already-open development subjects.

The protected stretched-N2 prospective discriminator remains unopened.

## Donor-first capability

Global Clifford / binary-symplectic preconditioning and structure-aware SELECT compilation are donor capabilities and receive **zero ORION novelty credit**. Relevant donor neighborhood includes, at minimum:

- Symphony, arXiv:2608.11579, global binary-symplectic/Clifford simplification of Pauli programs;
- Huang, Gao, Zhou, Ying, *A Compilation Framework for Quantum Simulation of Non-unitary Dynamics*, arXiv:2605.23358, including structure-aware factorization/assignment for Pauli-sum SELECT;
- FOQCS-LCU, arXiv:2507.20887, check-matrix SELECT;
- generic Clifford/symplectic synthesis and Pauli-network compilation already registered in the MAX-R6 donor neighborhood.

R6F therefore asks only whether an absorbed, donor-owned exact Clifford representation change exposes residual value for the already-registered exact joint TARE-3 grammar beyond a donor-composed frame-only incumbent. A positive does not claim the Clifford transform itself as ORION invention.

## Frozen open subjects and source custody

Use only the existing open-subject configurations from `max_r5h_mixed_cardinality_development.py`:

- H4, cc-pVDZ, 2.0 au, DUCC3, 8 qubits, source blob `b98792b1055dbac0ebf2a7576f72412e3e4ac6c5`;
- equilibrium N2, cc-pVTZ, 1.0 Eq, DUCC2, 12 qubits, source blob `15369e8e886efbb3d32f3b2dfe2cfbb96ddebeba`.

The R6B frozen six-term batch is reused exactly: take the first two deterministic R6B window champions and the six unique term indices they define. If fewer than two champions or fewer than six unique terms exist, the subject is a fail-closed negative; no substitute batch is permitted.

All ten unordered 3+3 partitions of those six terms are retained. No outcome-dependent partition substitution is permitted.

## Frozen donor Clifford grammar

For an n-qubit subject, enumerate exactly:

1. identity; and
2. every single directed CNOT conjugation `CNOT(c -> t)` with `c != t`.

No second CNOT, local-Clifford retuning, SWAP, arbitrary tableau, or post-outcome transform is admitted in R6F.

Conjugation is exact. The implementation must track the Pauli phase/sign induced by CNOT, verify that applying the same CNOT twice returns each Pauli key and phase to the original value, and verify pairwise symplectic products are preserved.

A non-identity preconditioner represents the exact wrapper

`CNOT * block_encode(CNOT H CNOT) * CNOT`

because CNOT is self-inverse. Its wrapper structural two-qubit charge is fixed to `2`; identity has charge `0`.

This wrapper charge is added only to the existing development structural cost `C_joint`. R6F remains a structural development discriminator, not a full fault-tolerant resource claim. Any positive must later be instantiated under the full R5B/R6 non-compensatory primitive vector before prospective use.

## Candidate-blind donor shortlist

The exact-joint candidate must not choose the Clifford transform.

For every transform in the full donor grammar and every one of the ten frozen partitions:

- transform the six target Paulis;
- compute `B_FRAME_ONLY_STRONG` independently on each 3-term block;
- define `C_donor = C_frame_A + C_frame_B + wrapper_charge`;
- retain the exact two-block TARE normalization `Lambda_batch = Lambda_A + Lambda_B` from the untouched coefficients.

The full donor envelope includes **all** identity/single-CNOT transforms and all ten partitions.

Before any exact-joint result is computed, rank transforms by the donor-only key

`(min_partition_C_donor, sum_partition_C_donor, transform_id)`.

Freeze the candidate evaluation transform set to:

- identity, plus
- the first seven non-identity transforms under that donor-only key.

Thus at most eight transforms per subject enter the exact-joint candidate evaluation. The shortlist is derived solely from donor/frame-only evidence and cannot inspect exact-joint outcomes.

## Candidate grammar

For every shortlisted transform and every retained partition, run the unchanged proof-producing `exact_joint` solver independently on both transformed 3-term blocks.

Define

`C_candidate = C_joint_A + C_joint_B + wrapper_charge`.

No DP objective, accepting state, target permutation grammar, central-axis grammar, Tag label grammar, tie rule, or witness check may change in R6F.

The candidate receives no credit merely for using a donor-selected Clifford transform. Its only possible value is a strict residual between unchanged exact-joint TARE-3 and the full donor-composed frame-only envelope.

## Budget-matched donor envelope

For each candidate point with normalization `Lambda_candidate`, define

`C_donor_envelope(Lambda_candidate)`

as the minimum `C_donor` among **all** donor transform/partition points satisfying

`Lambda_donor <= Lambda_candidate + 1e-12`.

A strict point requires

`C_candidate < C_donor_envelope(Lambda_candidate)`.

The comparator is therefore allowed to use a different transform and a different 3+3 partition whenever it has no worse normalization.

Block count, TARE cardinality, coefficient-rotation count, local TARE ancilla class, source access, scientific operator and coefficient vector are matched by construction. CNOT-wrapper charges are included in the structural cost rather than hidden.

## Development outcomes

### `MAX_R6F_CLIFFORD_PRECONDITIONED_TARE3_SUPPORTED__NOT_R6`

Allowed only if all integrity gates pass and both H4 and equilibrium N2 contain at least one strict budget-matched candidate point.

This is a positive open-subject method-language result only. It authorizes a separately frozen circuit-level/non-compensatory resource instantiation and donor/novelty audit. It does not authorize protected-subject access.

### `MAX_R6F_PARTIAL_CLIFFORD_REOPEN__NOT_R6`

If exactly one open subject has a strict point, preserve the matched counterfactual split and route responsibility accordingly. Do not call this general support.

### `MAX_R6F_CLIFFORD_PRECONDITIONING_NEGATIVE__NOT_R6`

If neither open subject has a strict point, preserve the negative and close the entire identity/single-CNOT preconditioning grammar. Do not enlarge the grammar after seeing this outcome without a new frozen protocol.

## Integrity and hostile gates

The implementation must fail closed unless all hold:

- the two open source blobs are the frozen blobs above;
- the R6B batch selector returns exactly six unique source terms per subject;
- exactly ten unordered 3+3 partitions are present;
- the transform grammar contains exactly `1 + n(n-1)` transforms;
- CNOT conjugation is involutive including phase on an exhaustive two-qubit Pauli panel;
- CNOT conjugation preserves the symplectic product on the exhaustive two-qubit Pauli panel;
- donor shortlist length is exactly eight when at least seven non-identity transforms exist;
- shortlist computation completes before candidate exact-joint evaluation and is serialized independently;
- every exact-joint witness passes all original checks;
- full donor envelope is computed from every frozen donor transform/partition point, not only the shortlist;
- `reserved_stretched_n2_accessed = false`;
- `novelty_credit = false` and `r6_authority = false`.

## Next-stage rule

If R6F is positive, do **not** open stretched N2. First freeze and execute a circuit-level successor that expands the structural scalar into the full controlled outer-LCU primitive/resource vector, gives Symphony/structure-aware SELECT/FOQCS and any stronger current donor first right of refusal, and requires an independent replay. Only after that successor is positive may a new protected R6 prospective protocol be frozen.
