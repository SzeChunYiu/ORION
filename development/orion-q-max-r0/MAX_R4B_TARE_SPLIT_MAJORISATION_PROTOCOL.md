# ORION-Q MAX-R4B — TARE split majorization theorem + compiler protocol

Date: 2026-08-20
Parent: #698 / #679
Branch: `shadow/orion-q-max-r0`
Status: theorem/protocol freeze before result artifact.

## Donor boundary

TARE v4 (`arXiv:2601.05740`) directly handles Pauli sums with at most `m <= 2n+1` terms and notes that larger operators may be split into groups of admissible size and recombined by an outer LCU, while leaving that split strategy unexplored. TARE, anticommuting/unitary partitioning, grouped qDRIFT, sparse-QSVT, cost-aware randomized simulation and LCU normalization optimization are donor-owned and absorbed.

This protocol does **not** claim novelty for splitting, grouping, magnitude ordering, TARE, or LCU.

## Object

Let a Pauli Hamiltonian be

`H = sum_{i=1}^L a_i P_i`, with real coefficients.

Choose an equal TARE block size `m <= 2n+1`, assume `m | L`, and partition the coefficient indices into `G=L/m` groups `G_1,...,G_G`, each of cardinality `m`.

For one TARE block `G_g`, the native subnormalization is

`lambda_g = sqrt(m) * ||a_{G_g}||_2`.

Recombining the TARE block encodings through an outer LCU yields coefficient-only subnormalization

`Lambda(P) = sum_g lambda_g = sqrt(m) * sum_g sqrt(sum_{i in G_g} |a_i|^2)`.

## Frozen theorem T-R4B.1 — equal-size coefficient-majorized TARE split

Let `x_1 >= x_2 >= ... >= x_L >= 0` be the coefficient magnitudes sorted nonincreasingly. Define the contiguous sorted partition

`G_g^* = {(g-1)m+1,...,gm}`.

Claim:

> Among **all** partitions of the L coefficients into G unlabeled groups of equal size m, the contiguous sorted partition minimizes `Lambda(P)`.

Equivalently,

`Lambda(P*) <= Lambda(P)` for every equal-size partition `P`.

### Proof obligation

Set `y_i=x_i^2` and let `S_g=sum_{i in G_g^*} y_i`. For an arbitrary partition let its group sums, sorted nonincreasingly, be `s_1>=...>=s_G`.

For every `k=1,...,G`, the k largest arbitrary groups contain exactly `km` source elements, hence

`sum_{g=1}^k s_g <= sum_{i=1}^{km} y_i = sum_{g=1}^k S_g`.

The totals agree, so `S` majorizes `s`. Because `sqrt(.)` is concave, Karamata / Schur-concavity gives

`sum_g sqrt(S_g) <= sum_g sqrt(s_g)`.

Multiplying by `sqrt(m)` proves the claim.

The theorem is coefficient-only. It does not claim circuit-depth/T-count optimality because TARE Restore/Tag structure depends on the Pauli strings and chosen stabilizer solution.

## Exact hostile verification

Before theorem promotion:

- exhaustive all unlabeled partitions for small `(L,m)` cases `(6,3)`, `(8,4)`, `(8,2)`, `(9,3)`;
- random positive coefficients over multiple dynamic ranges;
- zeros, equal coefficients, repeated coefficients, one-dominant-term cases;
- permutations/remints of coefficient identities;
- verify objective equality/ties are allowed;
- brute-force result must never beat sorted-contiguous result beyond numerical tolerance.

## Immediate corollaries

### C1 — uniform-magnitude boundary
If all `x_i` are equal, every equal-size partition has the same `Lambda`; coefficient sorting gives no benefit. This is an important no-gain control (e.g. uniform-coupling Pauli families).

### C2 — lower bound for structure-aware compiler
Any equal-size TARE partition that optimizes Pauli/Restore structure has coefficient-only subnormalization at least `Lambda(P*)`. The gap

`Delta_lambda = Lambda(P) - Lambda(P*) >= 0`

is the exact normalization price paid for circuit-structure improvements.

### C3 — compiler decomposition
The real R4B compiler is a Pareto problem over at least

`(Lambda, T_count, depth, ancillas, classical_partition_cost)`.

T-R4B.1 supplies an exact coefficient-coordinate optimum/lower bound; it does not scalarize the remaining resources.

## R4B experimental ladder

### E1 — theorem verification
Exact small exhaustive verification + large deterministic evaluation.

### E2 — physical-model controls
Evaluate coefficient-only gain on:
- uniform-coupling Heisenberg/Ising controls (expect tie/no gain);
- disordered/inhomogeneous Pauli Hamiltonians (expect nonzero gain);
- public molecular-Hamiltonian coefficients where immutable source extraction is available.

### E3 — structure tradeoff
Compare:
- `P*` coefficient-majorized split;
- structure-only TARE grouping;
- random split;
- donor grouped-qDRIFT/commuting grouping where applicable;
- a Pareto search that may sacrifice `Lambda` to reduce TARE Restore/T/depth cost.

No scalar superiority claim unless the scalar weights are frozen prospectively. Prefer Pareto dominance.

### E4 — donor-composed resource comparison
Compare large-operator routes under matched access/error assumptions:
- standard Pauli LCU/QSVT;
- split TARE + outer LCU;
- best TARE partition/compiler found here;
- sparse/randomized QSVT where assumptions map faithfully;
- grouped qDRIFT / composite randomized simulation for Hamiltonian-simulation targets;
- BLISS/other Hamiltonian transformations where faithful.

## Novelty / claim gate

A theorem/method may become `MAX_R6_NEW_QUANTUM_METHOD_CANDIDATE` only if:

1. proof + independent exhaustive checker agree;
2. current hostile literature search does not find the same TARE split theorem/compiler rule;
3. it is useful on at least one immutable nontrivial Hamiltonian family beyond uniform controls;
4. its relationship to TARE's published split extension and prior magnitude/grouping work is explicit;
5. no stronger-oracle/error/resource change is introduced;
6. external novelty/correctness authority remains separate.

Until then the maximum terminal is `MAX_R5_PROOF_CARRYING_REAL_QUANTUM_IMPROVEMENT_CANDIDATE`.

## Negative recursion

If coefficient-majorized splitting gives negligible end-to-end value, do not close R4/R6. Diagnose whether the bottleneck is Restore structure, outer SELECT/control cost, subnormalization, access model, or target Hamiltonian regime, absorb the strongest parent, and construct the next materially different representation/compiler successor.
