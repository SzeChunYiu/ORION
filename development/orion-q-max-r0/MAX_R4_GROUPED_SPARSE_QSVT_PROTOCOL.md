# ORION-Q MAX-R4 real-method candidate — structure-grouped sparse QSVT

Date: 2026-08-20
Parent: #679
Prerequisite: MAX-R3E synthetic self-evolving-system milestone absorbed into incumbent.
Status: **FROZEN BEFORE RESULT-BEARING BENCHMARK EXECUTION**

## Maximal research question

> For Pauli-decomposed Hamiltonians, can a proof-carrying representation compiler first convert structurally compatible Pauli subsets into normalized unitary groups, then perform deterministic/stochastic sparse-QSVT at the **group** level, yielding an end-to-end Pareto improvement over term-level sparse-QSVT, ordinary LCU/QSVT, and structure-aware deterministic block encoding under matched Hamiltonian, error and access semantics?

This is a real quantum-algorithm/resource question. Component novelty is explicitly not claimed: anticommuting unitary partitioning, stabilizer block encoding and sparse-QSVT are absorbed donors.

## Absorbed donor mechanisms

1. **Unitary partitioning / anticommuting grouping**
   - mutually anticommuting Pauli strings can be normalized into a Hermitian unitary group;
   - grouping is a clique-partition problem and implementation cost is not free.
2. **2026 stabilizer block encoding**
   - Pauli structure can be transformed to exploit pairwise anticommutation with correction circuitry.
3. **2026 sparse-QSVT**
   - dominant components deterministic, weak components stochastic;
   - coefficient dispersion controls the favorable regime;
   - current random ensembles omit realistic commutation structure.
4. **Randomized/block-encoding-free QSVT**
   - stochastic simulation/transformation cost can avoid linear dependence on raw Hamiltonian term count but pays degree/error penalties.

## Mathematical representation

Let

`H = sum_j c_j P_j`

with real coefficients and Pauli strings `P_j`.

Partition a subset/all terms into disjoint mutually anticommuting groups `G_g`. Define

`a_g = sqrt(sum_{j in G_g} c_j^2)`

and, for `a_g > 0`,

`A_g = (1/a_g) sum_{j in G_g} c_j P_j`.

Because distinct terms in `G_g` anticommute and `P_j^2=I`, evaluator must verify

`A_g^2 = I`.

Then

`H = sum_g a_g A_g`

for a full partition (plus singleton groups as needed).

The group normalization

`Lambda_G = sum_g a_g`

obeys

`Lambda_G <= lambda = sum_j |c_j|`,

with strict reduction whenever a group contains at least two nonzero coefficients.

This normalization fact is donor mathematics / elementary consequence, not ORION novelty.

## Candidate method

1. Build an anticommutation graph over Pauli terms.
2. Generate one or more admissible group partitions.
3. Construct/estimate implementation cost for each group unitary `A_g`.
4. Represent `H` at group level using weights `a_g`.
5. Choose group-level deterministic set `D` and stochastic set `S` under a sparse-QSVT-style error/resource model.
6. Optimize a **resource vector**, not one hidden scalar:
   - group construction gates;
   - SELECT/PREPARE or equivalent block-encoding cost;
   - sampled group execution cost;
   - ancillas;
   - target polynomial degree;
   - stochastic/error amplification;
   - classical grouping/preprocessing;
   - total logical depth/T proxy where derivable.
7. Verify exact Hamiltonian reconstruction and group unitarity on benchmark-scale matrices.

## Baselines

B0 ordinary term-level LCU/QSVT.
B1 term-level sparse-QSVT using coefficient-only deterministic/stochastic partition.
B2 anticommuting/unitary partitioning followed by deterministic QSVT only.
B3 2026 stabilizer-structure block-encoding proxy where assumptions map faithfully.
B4 best of B0-B3 selected per instance (donor-composed oracle ceiling for supplied methods).
B5 grouped sparse-QSVT candidate.
B6 optimized grouped sparse-QSVT over multiple partitions/thresholds.

A valid ORION R4 candidate must beat **B4**, not just B0/B1.

## Benchmark families

### F1 structured anticommuting blocks
Synthetic exact Hamiltonians with planted mutually anticommuting groups and heavy-tailed coefficients.

### F2 unstructured/random Pauli
Negative control where little grouping benefit should exist.

### F3 mixed commuting/anticommuting structure
Tests whether group construction cost or poor grouping erases normalization gain.

### F4 chemistry-like coefficient hierarchy
Generated or public molecular-Pauli Hamiltonians if immutable data/code is available; otherwise clearly label generated proxy and do not promote to real-chemistry claim.

### F5 adversarial implementation-cost cases
Large anticommuting groups that reduce `Lambda_G` but require enough coherent construction cost to lose overall.

## Frozen first diagnostic cost model

Before compiled circuit integration, use an explicitly labeled **diagnostic proxy**:

- term-level normalization `lambda = sum |c_j|`;
- group normalization `Lambda_G = sum_g ||c_G||_2`;
- group synthesis penalty `K_g = k0 + k1*(|G_g|-1)` with sensitivity sweep over frozen `(k0,k1)` grid;
- deterministic route proxy proportional to `degree * normalization * implementation_cost`;
- stochastic residual proxy proportional to `degree^2 * residual_normalization^2 * mean_sample_implementation_cost`;
- total candidate proxy = deterministic grouped cost + stochastic grouped residual cost + grouping conversion cost.

No finite-resource quantum claim may be promoted from this proxy alone. Its role is to identify whether the composition has a nonempty robust regime worth exact/compiled follow-up.

## Exact semantic gates

For all small-n subjects:
- matrix reconstruction `||H - sum_g a_g A_g|| <= 1e-10`;
- each `A_g` Hermitian/unitary to tolerance;
- no changed target polynomial/error norm;
- same Pauli access information supplied to all baselines;
- grouping classical cost reported;
- group implementation penalty never set to zero in the primary sensitivity grid;
- candidate Pareto claim requires superiority over B4 in at least one resource dimension without worsening hard semantic/error gates.

## Primary diagnostic endpoint

Across frozen generated families and sensitivity grid:

- fraction of subjects where B5/B6 strictly improves the donor-composed B4 proxy;
- robustness region in coefficient dispersion × anticommutation density × group synthesis penalty × degree;
- normalization ratio `Lambda_G/lambda`;
- total proxy ratio vs B4;
- cases where normalization gain is erased by implementation cost;
- exact semantic failure count.

## Positive ladder

- `R4A_REPRESENTATION_COMPOSITION_HAS_ROBUST_PROXY_REGIME` — exact semantics + robust diagnostic resource regime; authorizes compiled/exact cost follow-up only.
- `R4B_COMPILED_PARETO_GAIN` — real compiled/logical resource model shows gain over B4.
- `R4C_HELD_OUT_REAL_HAMILTONIAN_GAIN` — gain survives immutable real Hamiltonian families.
- `MAX_R5_PROOF_CARRYING_REAL_QUANTUM_IMPROVEMENT` — independent correctness/resource replay and current donor comparison.
- `MAX_R6_NEW_QUANTUM_METHOD_OR_RESULT` — external novelty/correctness authority supports a genuinely new reusable result.

Always aim upward; lower rungs are milestones.

## Negative recursion

If grouped sparse-QSVT loses:
- diagnose normalization vs group-implementation vs stochastic-error cause;
- absorb stronger grouping/block-encoding method;
- test optimized partition objective rather than coefficient-only grouping;
- test interaction-picture or commuting-structure representation;
- do not conclude cross-layer method invention is useless.
