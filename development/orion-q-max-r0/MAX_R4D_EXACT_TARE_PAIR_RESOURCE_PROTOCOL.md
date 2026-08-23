# ORION-Q MAX-R4D — exact symplectic TARE-pair resource compiler

Date: 2026-08-20
Parent: #698 / #679
Status: protocol freeze before fresh H2O subject extraction.

## Goal

Replace the failed normalization-only H2 gate with an implementation-grounded **resource vector**, while remaining inside TARE's published circuit semantics.

This stage studies pair blocks (`m=2`) because the TARE auxiliary-representation optimization is then exactly enumerable/checkable for benchmark-size Pauli strings. It is a compiler/mechanism result, not a claim that pair blocking is globally optimal among all block sizes.

## Donor circuit facts absorbed

TARE Theorem 1 permits the anti-commuting family `R_k`, control states and tagging strings to be chosen by the user. For `m=2`, use one tagging ancilla (`a=1`) and control labels `c0=0,c1=1`.

Required relations:
- `T_k R_k = P_k` up to Pauli phase;
- `R0,R1` anti-commute;
- tagging Pauli `S` satisfies `<S,R0>_symp=0`, `<S,R1>_symp=1`.

TARE's explicit Uanti circuit for m=2 uses three Pauli exponentials:

`exp(i theta0/2 R0) exp(i theta1 R1) exp(i theta0/2 R0)`

up to global phase. Tag is Clifford; Restore applies branch-controlled `T0,T1`.

## Exact resource vector per pair

For Pauli weight `w(P)` and the standard all-to-all parity-ladder implementation of `exp(i theta P)`, define

`E_exp(P)=2 max(w(P)-1,0)` two-qubit parity entanglers.

For an ordered auxiliary pair `(R0,R1)`, define

`E_U = 2 E_exp(R0) + E_exp(R1)`

(the repeated role may be swapped by relabeling and is optimized exactly).

Do **not** convert Clifford controlled-Pauli factors into T gates. Track separately:

`C_TR = 2 w(S) + w(T0) + w(T1)`,

where the factor 2 is Tag + Tag† and the remaining terms are Restore branches. This is a logical controlled-Pauli-factor metric, not a hardware CNOT/T count.

Additional exact coordinates:
- arbitrary Pauli rotations in Uanti: `N_rot=3` for every m=2 TARE block;
- inner TARE ancillas: `A_inner=1` for a corrected pair;
- subnormalization `lambda_ij=sqrt(2)*sqrt(a_i^2+a_j^2)`.

### Direct anti-commuting target pair

If `P0,P1` already anti-commute, choose `R_k=P_k`; then TARE's own matching observation makes Tag/Restore unnecessary for both terms. Record a direct block with
- `C_TR=0`;
- `A_inner=0`;
- `E_U=min(2E_exp(P0)+E_exp(P1), 2E_exp(P1)+E_exp(P0))`;
- `N_rot=3`.

The compiler is still allowed to find an alternative corrected TARE representation with a different resource vector; preserve all nondominated representations.

## Exact auxiliary-representation search

For one n-qubit target pair `(P0,P1)`:

1. enumerate every non-identity n-qubit Pauli `R0`;
2. enumerate every non-identity `R1` anti-commuting with R0;
3. set phase-free `T0=P0*R0`, `T1=P1*R1` in the symplectic representation;
4. enumerate tagging Paulis S satisfying the two symplectic constraints and retain the minimum possible `w(S)` for that `(R0,R1)`;
5. compute `(E_U,C_TR,A_inner,N_rot)`;
6. retain the exact Pareto set in `(E_U,C_TR,A_inner)`; coefficient-dependent `lambda_ij` is fixed for the target pair.

For n=4 this is finite and exhaustively checkable. For larger n this enumeration is a diagnostic ceiling and must later be replaced by symplectic MILP/SAT/optimization rather than called scalable.

## Global pair partition

For an even L-term Hamiltonian, choose a perfect matching of terms. Each selected edge chooses one of its nondominated exact TARE representations.

Report the global Pareto frontier over

`(Lambda, E_U_total, C_TR_total, A_inner_max_or_sum, N_rot_total)`

where

`Lambda=sum_edges lambda_ij`, `N_rot_total=3L/2`.

No scalar objective is primary. A point dominates another only if it is no worse in every frozen coordinate and strictly better in at least one.

The coefficient-majorization theorem gives the global lower bound `Lambda >= Lambda*` for equal-size pair partitions.

## Exact TARE heterogeneity identity

For any m-term positive coefficient-magnitude block with mean mu and population standard deviation sigma,

`sqrt(m)||a||2 / ||a||1 = sqrt(1 + (sigma/mu)^2)`.

Thus coefficient variation is exactly the block's TARE-vs-Pauli-LCU subnormalization ratio. This identity is reported as a theorem corollary and used to interpret, not tune, the partitioner.

## Development-only evidence

H2 and LiH are development subjects and cannot confirm this protocol. H2 development showed exact auxiliary-representation/partition search can reduce the logical resource vector even when a preregistered direct-unitary coverage gate fails.

## Fresh confirmation subject rule

After this file is committed, lock one immutable public molecular Hamiltonian not previously inspected for coefficients/Pauli strings. The intended first subject is an H2O equilibrium Hamiltonian from a public independent repository, but the exact file + commit must be recorded **before reading its coefficient contents**.

No terms may be removed or reordered for favorable results except deterministic canonical identity removal and canonical coefficient/Pauli parsing declared before extraction. If the retained Pauli term count is odd, the pair-only test returns `CANNOT_CHECK_ODD_L` unless the source contains a physically declared identity term that is excluded under the same rule used for prior H2/LiH subjects.

## Fresh primary hypothesis

On the locked fresh subject, the exact pair compiler must produce at least one point that strictly Pareto-dominates the **coefficient-majorized pair split with its own exact best auxiliary TARE representation choices** in at least one implementation coordinate while matching its Lambda to numerical tolerance; OR, if exact Lambda equality is impossible, produce a nontrivial certified Pareto frontier with at least one point reducing both `E_U_total` and `C_TR_total` for <=1% Lambda overhead.

This is intentionally stronger than merely reducing correction count.

## Strong baselines

- standard Pauli LCU/QSVT resource objects;
- TARE v4 direct implementation;
- coefficient-majorized split-TARE lower bound;
- direct anti-commuting/unitary partitioning;
- grouped-Hamiltonian simulation methods;
- generic perfect matching/MILP;
- exhaustive symplectic auxiliary search (ceiling at n=4).

## Hard boundaries

- outer-LCU PREPARE/SELECT cost is not yet quantified by this inner-block resource vector; do not claim full QSVT T/depth superiority until outer composition is costed;
- `C_TR` is not T-count;
- the standard Pauli exponential ladder is one explicit implementation, not a hardware-independent lower bound;
- no novelty authority from this benchmark;
- any apparent advantage must survive strongest-current donor recheck.

## Result ladder

- `R4D_EXACT_INNER_TARE_COMPILER_PARETO_SUPPORTED`;
- `R4D_COEFFICIENT_OPTIMUM_ALREADY_RESOURCE_OPTIMAL`;
- `R4D_FRESH_SUBJECT_CANNOT_CHECK`;
- `R4D_INVALID_RESOURCE_MODEL`.

A positive R4D is absorbed into R5. R5 must add outer composition / end-to-end block-encoding resource accounting and immutable multi-family validation before `MAX_R5_PROOF_CARRYING_REAL_QUANTUM_IMPROVEMENT_CANDIDATE`.
