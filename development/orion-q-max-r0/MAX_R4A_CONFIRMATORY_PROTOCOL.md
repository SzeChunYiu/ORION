# ORION-Q MAX-R4A confirmatory diagnostic protocol

Date: 2026-08-20
Parent protocol: `MAX_R4_GROUPED_SPARSE_QSVT_PROTOCOL.md`
Parent programme: #679
Status: **FROZEN AFTER DEVELOPMENT SWEEP, BEFORE CONFIRMATORY SUBJECT GENERATION/OUTCOMES**

The earlier development sweep is non-authorizing and used only to choose this frozen panel. No development subject seed appears below.

## Subject generator

All subjects have `n=5` qubits and `L=30` distinct nonidentity Pauli terms. Coefficients are normalized to `sum_j |c_j| = 1`.

Fresh confirmatory seeds:

- F1: `51000..51049`;
- F2: `52000..52049`;
- F3: `53000..53049`.

No other seeds enter the primary confirmatory endpoint.

### F1 — structured heavy-tail

- plant four disjoint size-7 mutually anticommuting Pauli groups using Clifford-equivalent transforms of a `2n+1` gamma family;
- fill remaining terms with distinct random Pauli strings;
- coefficient magnitudes `exp(N(0,1.6^2))`, random signs, then L1 normalize.

### F2 — unstructured low-dispersion control

- all 30 terms distinct random nonidentity Pauli strings;
- coefficient magnitudes `exp(N(0,0.25^2))`, random signs, then L1 normalize.

### F3 — mixed structure

- plant two disjoint size-7 mutually anticommuting groups;
- fill remaining terms randomly;
- coefficient magnitudes `exp(N(0,1.6^2))`, random signs, then L1 normalize.

## Anticommuting partition search

For each subject build candidate partitions by greedy pairwise-anticommutation packing under exactly 13 orderings:

1. descending `|c_j|`;
2. ascending `|c_j|`;
3. original generated order;
4. ten pseudorandom orderings using seed `subject_seed + 999`.

B5 uses ordering 1 only. B6 may choose the best candidate partition under the frozen proxy.

## Exact semantic checks

For every selected partition on every subject:

`a_g = sqrt(sum_{j in G_g} c_j^2)`

`A_g = (1/a_g) sum_{j in G_g} c_j P_j`.

Require:

- pairwise anticommutation inside each nonsingleton group;
- `||A_g^2-I||_2 <= 1e-10`;
- `||A_g-A_g^dagger||_2 <= 1e-10`;
- `||H-sum_g a_g A_g||_2 <= 1e-10`;
- `Lambda_G = sum_g a_g <= 1 + 1e-12`.

Any semantic failure invalidates that subject and fails the hard gate if count > 0.

## Frozen proxy models

Let polynomial degree `d`.

### B0 — term-level deterministic

`C_B0 = d * lambda * L`, with `lambda=1` by normalization.

### B1 — optimized term-level sparse

Sort terms by descending `|c_j|`. For every prefix size `k`:

`lambda_D = sum_{j<=k}|c_j|`

`lambda_S = 1-lambda_D`

`C_B1(k) = d*lambda_D*k + d^2*lambda_S^2`.

Take minimum over `k=0..L`.

### Group implementation penalty

For group size `s_g`:

`K_g = k0 + k1*(s_g-1)`.

Nonzero grouping/preprocessing charge:

`C_pre = 0.001 * L^2`.

### B2/B3 — deterministic grouped / structure-aware deterministic proxy

`C_B2 = d * Lambda_G * sum_g K_g + C_pre`.

For this first proxy B3 is conservatively represented by the same structure-aware deterministic grouped cost; no separate stabilizer-compiler finite cost is fabricated.

### B4 — donor-composed supplied-method ceiling

`C_B4 = min(C_B0, C_B1, C_B2)`.

### B5/B6 — grouped sparse

For a group partition, let group weights `a_g`. Consider exactly three deterministic-prefix orderings:

1. descending `a_g`;
2. descending `a_g/K_g`;
3. descending `a_g*K_g`.

For each prefix D with residual S:

`Lambda_D=sum_{g in D} a_g`

`Lambda_S=sum_{g in S} a_g`

`Kbar_S = sum_{g in S} a_g K_g / Lambda_S` when `Lambda_S>0`.

`C_group_sparse = d*Lambda_D*sum_{g in D}K_g + d^2*Lambda_S^2*Kbar_S + C_pre`.

B5 minimizes prefixes/orderings for the fixed descending-coefficient Pauli partition. B6 additionally minimizes over the 13 candidate Pauli partitions.

## Frozen sensitivity grid

Degrees:

`d in {4, 8, 16, 32}`.

Group costs:

`k0 in {1, 2, 4}`;

`k1 in {0.25, 0.5, 1, 2, 4}`.

All 60 cost/degree cells are reported. No cell may be removed after outcomes.

## Primary preregistered R4A criterion

Define the **low-overhead coherent-group regime** exactly as:

- `k0 = 1`;
- `k1 = 0.25`;
- all four degrees `d in {4,8,16,32}`.

`R4A_REPRESENTATION_COMPOSITION_HAS_ROBUST_PROXY_REGIME` passes only if:

1. semantic failure count = 0;
2. for **each** family F1, F2 and F3 and **each** of the four degrees, B6 strictly beats B4 on at least 80% of the 50 fresh subjects;
3. for each family the geometric-mean `B6/B4` across the four degree cells is < 0.90;
4. the high-overhead control `k0=4,k1=4` contains at least one degree/family cell where B6 does not beat B4 on a majority of subjects, demonstrating a real failure boundary rather than an always-win proxy construction.

## Secondary/exploratory reports

- full 60-cell heatmap/table;
- median and geometric-mean B6/B4;
- `Lambda_G/lambda` distribution;
- group counts/sizes;
- B5 vs B6 partition-search gain;
- which donor baseline wins B4;
- crossover with group synthesis overhead.

## Authority

Even a pass is **only a robust exact-semantic diagnostic proxy regime**. It authorizes implementation/resource-model follow-up. It does not authorize compiled Pareto gain, real-Hamiltonian gain, new quantum algorithm, or novelty.
