# ORION-Q MAX-R5J anchored dependent TARE-3 development protocol

Date: 2026-08-20
Parent: #679
Branch: `shadow/orion-q-max-r0`
Status: frozen before R5J outcome generation.
Authority ceiling: open-subject method development only; cannot by itself authorize R6 novelty.

## Reopen cause

MAX-R5H on H4 shows that arbitrary direct anticommuting clique partitioning absorbs the named mixed m=2 TARE point. A materially different corrected-unitary primitive is required.

TARE v4 explicitly leaves the choice of the freely selectable anticommuting family `{R_k}` as an optimization direction and notes that a native match `R_k=P_k` makes the corresponding correction `T_k=I`. R5J turns one nontrivial instance of that residual into a closed proof-carrying construction for `m=3`.

## Candidate primitive: anchored dependent TARE-3 (ADT3)

Given three target Pauli strings `(P_a,P_b,P_c)` with real coefficients, choose one target as a native anchor

`R0 = P_a`.

Choose a Pauli string `R1` satisfying

`<R0,R1>_symp = 1`,

and define

`R2 = R0 R1`

(up to irrelevant Pauli phase; binary vector `r2=r0+r1`).

Then

`<R0,R1>=<R0,R2>=<R1,R2>=1`,

so `{R0,R1,R2}` is pairwise anticommuting. Moreover

`r0+r1+r2=0`.

Use two tag ancillas and control labels

`c0=01, c1=10, c2=11`.

Their XOR is zero, exactly satisfying the TARE Theorem-2 consistency condition for the dependent odd anticommuting family.

An explicit valid tag dual is

- one tagging Pauli equal to `R0`, whose syndromes against `(R0,R1,R2)` are `(0,1,1)`;
- the other equal to `R1`, whose syndromes are `(1,0,1)`.

Thus the construction is proof-carrying without solving a separate tag linear system.

Restore strings are

`T0 = I`,
`T1 = P_b R1`,
`T2 = P_c R2`.

The anchor therefore realizes the donor-paper future-work condition `T0=I` exactly.

## Exact frame optimization

For each triple:

1. try each of the 3 targets as anchor;
2. try both assignments of the remaining two targets to `(R1,R2)`;
3. try each of the 3 Uanti axes as the once-applied central axis;
4. for each case solve the exact minimum over all Pauli `R1` subject to `<R0,R1>=1`.

For a fixed case, the frame-dependent support objective is

`C_frame = C_Uanti + 2(w(R0)+w(R1)) + w(P_b R1) + w(P_c R0 R1)`

with

`C_Uanti = 4*sum_{j != central}(w(R_j)-1) + 2*(w(R_central)-1)`.

Every term is a sum of single-qubit contributions once `central` is fixed. The only global constraint is one symplectic parity bit `<R0,R1>=1`. Therefore the optimum is obtained by an exact two-state dynamic program over qubits:

`DP[q, parity] = minimum accumulated local support through qubit q`.

This is `O(n * 4)` per fixed anchor/assignment/central case and `O(n)` for the whole fixed-size block up to a constant factor.

The DP must carry lexicographic backpointers and emit `R0,R1,R2,T0,T1,T2,S0,S1`.

## Strong donor comparator

The TARE-v4 canonical-family donor is reconstructed for the same three target terms:

- use the paper's fixed anticommuting family from Eq. (31), restricted to three generators;
- allow all 6 target-to-generator permutations;
- allow all 3 choices of Uanti central axis;
- solve the TARE Theorem-2 tag equations for `c=(01,10,11)` and independently minimize each tag Pauli by exact syndrome DP, matching/strengthening the numerical protocol in the paper;
- use exact Restore strings `T_k=P_kR_k`.

This gives the canonical donor first right of refusal. ADT3 gets no credit unless it beats this strengthened canonical comparator at identical block normalization, identical `2m-1=5` Uanti rotation count, identical tag-ancilla count, and identical outer block cardinality.

## Primary development metric

Because normalization, Uanti non-Clifford rotation count, ancilla count, and block count are identical between the two TARE-3 realizations, compare the exact frame-dependent Pauli support cost `C_frame` above.

This support is the portion that determines parity-ladder / controlled-Pauli two-qubit work under the frozen R5 projection; all representation-independent fixed outer-control constants are reported separately and cancel in a same-block comparison.

For each triple report:

- canonical minimum `C_frame`;
- ADT3 minimum `C_frame`;
- strict reduction;
- anchor identity;
- target assignment;
- central axis;
- full proof witness;
- canonical and ADT3 hashes.

## Open-subject evaluation

Use only already-open H4 and equilibrium N2.

For every contiguous 12-term coefficient-local window, evaluate every 3-subset that is **not already a direct mutually anticommuting clique**. Direct cliques remain donor-owned and should not be replaced by a worse corrected block.

Report:

- number of eligible triples;
- fraction strictly improved over canonical TARE3;
- median/mean/max frame-support reduction;
- number of cases with an actual native anchor `T0=I` (must equal all ADT3 cases by construction);
- top transfer-stable witness families shared by H4 and N2 structural signatures.

## Development success

`R5J_ADT3_DEVELOPMENT_SUPPORTED` requires on **both** open subjects:

1. all algebraic/symplectic/tag/restore checks pass;
2. exact DP matches brute force on every reminted 2- and 3-qubit hostile instance;
3. at least 100 eligible chemistry triples are evaluated in total;
4. at least 20% of eligible non-direct triples strictly beat the strengthened canonical TARE3 comparator;
5. median strict improvement among improved triples is at least one support unit;
6. at least one triple on each subject improves canonical support by >=20%;
7. no normalization/T/block/ancilla coordinate changes are hidden.

This is method development, not novelty authority.

## Reopen / failure response

If ADT3 rarely beats canonical TARE3, the anchor restriction is too rigid; reopen to multi-anchor / general symplectic-frame search.

If local blocks improve but cannot create a donor-composed Hamiltonian frontier point, absorb ADT3 as a primitive and attack global partition/PREP/selector co-design.

If a literature donor already gives this anchored dependent-triple construction or an equivalent exact auxiliary-frame optimizer, absorb it and move upward.
