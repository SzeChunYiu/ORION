# ORION-Q MAX-R6 exact joint TARE-3 auxiliary-frame DP protocol

Date: 2026-08-20
Parent: #679
Branch: `shadow/orion-q-max-r0`
Status: frozen before exact-joint-frame outcome generation.
Authority ceiling: candidate method development; not R6 until prospective fresh confirmation, independent replay and hostile novelty closure.

## Native admission

The corrected native Self-ORION responsibility lattice reaches method-language responsibility only after:

- current R5H search closure;
- optimistic general-m TARE donor closure;
- system-selected FOQCS interface exploration;
- an optimistic zero-PREP FOQCS envelope still failing to dominate all hard H4 coordinates;
- current mixed language providing no H4 incremental value over direct clique grouping.

This admits `REV:GROW_METHOD_LANGUAGE`. The method below is generated from the generic TARE theorem constraints, not from the earlier operator-authored R5J construction.

## Research question

For a fixed three-term corrected TARE block, can the free auxiliary anticommuting family, target assignment, control labels, Tag generators and Uanti central axis be optimized **jointly and exactly** rather than by fixing a canonical frame or optimizing one coordinate at a time?

## Donor subtraction

No novelty credit is assigned to:

- TARE itself;
- the freedom to choose `R_k`, control labels or Tag solutions, which TARE explicitly states;
- anticommuting Pauli grouping / unitary partitioning;
- generic Pauli-frame or Clifford/symplectic optimization;
- coefficient/state-preparation factorization;
- downstream Pauli-network compilation.

The candidate residual is an exact compiler for the **joint TARE-specific objective** containing frame + labels + Tag + Restore + target assignment + explicit Uanti support in one proof-carrying optimization.

## Fixed input

Three target Pauli strings `P0,P1,P2` on `n` qubits. Coefficients are not needed for the frame-support optimization except for the separately reported TARE normalization and Uanti angles.

The default logarithmic TARE ancilla width is `a=2`.

## Variables

Per system qubit the solver jointly chooses local Pauli codes for

`r0,r1,r2,s0,s1 in {I,X,Y,Z}`,

where `R0,R1,R2` are the auxiliary strings and `S0,S1` the two Tag generators.

Global target assignment `pi in S3` and Uanti central axis `c in {0,1,2}` are enumerated outside the DP.

Control labels are **not fixed before the DP**. The six final Tag-syndrome parity bits directly encode the two-bit label of each `R_k`; the final DP accepts any three distinct labels.

## Exact parity state

The global DP parity state has nine bits:

1. `<R0,R1>`;
2. `<R0,R2>`;
3. `<R1,R2>`;
4-6. `<S0,Rk>` for k=0,1,2;
7-9. `<S1,Rk>` for k=0,1,2.

The first three final bits must be `(1,1,1)`.

The last six bits form labels

`ck = (<S0,Rk>, <S1,Rk>)`,

which must be pairwise distinct.

## Odd-dependent consistency state

TARE Theorem 2 requires `c0 xor c1 xor c2 = 00` when

`R0 R1 R2` is identity up to phase, i.e. `r0+r1+r2=0` in binary symplectic representation.

The DP therefore tracks one extra monotone bit

`independent_seen = OR_q [r0_q xor r1_q xor r2_q != I]`.

At the final state:

- if `independent_seen=1`, any three distinct labels are admissible;
- if `independent_seen=0`, the three labels must XOR to `00`.

Thus the exact dynamic state has `2^10=1024` states independent of `n`.

## Additive support objective

For central axis `c`, define multiplicities

`mu_k = 2 if k=c else 4`.

For local target codes `p_pi(k)` and chosen local variables, accumulate

`raw = sum_k mu_k w(rk) + 2w(s0)+2w(s1) + sum_k w(p_pi(k) * rk)`.

After all qubits subtract the Uanti constants

`sum_k mu_k = 10`.

The resulting exact objective is

`C_joint = C_Uanti_parity + 2(w(S0)+w(S1)) + sum_k w(Tk)`,

with `Tk=P_pi(k) Rk` and

`C_Uanti_parity=sum_k mu_k (w(Rk)-1)`.

This is the same explicit five-exponential TARE-3 support model used for candidate generation. It is a structural circuit objective, not a complete outer-controlled Clifford+T count.

## Solver

For each of the 18 `(pi,c)` choices:

1. precompute, for each of the 64 local target triples, the minimum local cost and lexicographically first `(r0,r1,r2,s0,s1)` for each `(9-bit parity delta, independent-local bit)`;
2. propagate a 1024-state min-plus XOR/OR dynamic program across system qubits;
3. accept only final states satisfying pairwise anticommutation, distinct labels and the odd-dependent consistency rule;
4. reconstruct the lexicographically canonical minimum witness through backpointers.

Because the local alphabet and state count are constants for m=3, runtime is `O(n)` for a fixed number of target permutations/central axes, with a large but finite constant.

## Proof-carrying output

Every selected witness emits and independently recomputes:

- `R0,R1,R2`;
- rank of the three symplectic vectors;
- `S0,S1`;
- derived labels `c0,c1,c2`;
- target permutation;
- Restore strings `T0,T1,T2`;
- central axis;
- native-match set `{k:Tk=I}`;
- Uanti support;
- Tag support;
- Restore support;
- total `C_joint`;
- all three anticommutation checks;
- all six Tag-label checks;
- distinct-label check;
- dependent-family consistency check;
- all Restore identities;
- cost recomputation.

## Hostile exactness

On reminted 2-qubit cases, exhaustive enumeration over all `4^5` local tuples on every qubit and all 18 global `(pi,c)` choices must reproduce the DP optimum and canonical witness cost exactly.

On reminted 3-qubit cases, exhaustive comparison may be limited to cost equality on a fixed deterministic panel if full witness enumeration is expensive.

## Open-subject development

Use only already-open H4 and equilibrium N2.

First run the frozen candidate-blind rank-2 scan. For each subject take the deterministic top 8 triples by rank-2 improvement against strengthened canonical TARE, then apply the exact joint DP to those triples.

Comparator `B_CANONICAL_STRONG`:

- TARE v4 canonical rank-3 frame;
- all 24 ordered triples of distinct 2-bit control labels;
- all target permutations;
- all central axes;
- exact minimum-weight Tag solutions.

Comparator `B_FRAME_ONLY`:

- a target-agnostic auxiliary-frame oracle may minimize Uanti frame support first;
- after that frozen frame choice, labels/Tag/Restore are optimized exactly;
- this baseline is a mechanism comparator for generic frame/Pauli-weight optimization, not an official Treespilation reproduction.

## Development gate

`MAX_R6_EXACT_TARE3_JOINT_DP_SUPPORTED` requires on both open subjects:

1. at least one selected triple where exact joint `C_joint < B_CANONICAL_STRONG`;
2. proof-carrying witness checks all pass;
3. hostile exactness passes;
4. for at least one subject, a joint optimum is strictly better than `B_FRAME_ONLY`, demonstrating value from optimizing the TARE-specific coupled objective rather than frame weight alone;
5. no stretched-N2 coefficient content is accessed.

This remains below R6.

## Prospective R6 claim candidate

If development passes, the eligible bounded R6 object is:

> an exact linear-in-qubit-count finite-state compiler for three-term TARE auxiliary representations that jointly optimizes anticommuting frame, control labels, Tag and Restore support, target assignment and Uanti realization, with proof-carrying witnesses.

A final R6 protocol must still be frozen before reading stretched N2 and must require:

- prospective fresh improvement over the strongest frozen TARE/frame comparators;
- unchanged block cardinality, coefficient vector, TARE normalization convention, Uanti rotation count and ancilla width for the fixed-block comparison;
- structurally independent replay;
- final hostile literature search through the execution date;
- no claim of whole-Hamiltonian superiority unless separately established.
