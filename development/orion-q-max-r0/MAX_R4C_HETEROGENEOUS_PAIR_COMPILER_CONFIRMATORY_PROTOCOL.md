# ORION-Q MAX-R4C — heterogeneous unitary/TARE pair compiler fresh confirmation

Date: 2026-08-20
Parent: #698 / #679
Status: **FROZEN BEFORE H2 NOTEBOOK OUTCOME EXTRACTION**.

## Development evidence only

LiH from `SNIPRS/hamiltonian` was used to discover the following pair-level compiler object and is development-only:
- pair terms into blocks of size 2;
- a pair that already anti-commutes is a direct weighted unitary block and requires no TARE Tag/Restore correction;
- a commuting pair remains TARE-encodable but requires correction;
- pair subnormalization is `sqrt(2)*sqrt(a_i^2+a_j^2)`;
- LiH showed a nontrivial normalization/correction Pareto frontier.

No LiH outcome may authorize this confirmation.

## Fresh immutable subject

Repository: `SNIPRS/hamiltonian`
Commit/source snapshot discovered before outcome extraction: `c628c05430e9409f3c637f2f65f05c40438d1c29`.
File: `simulation-H2.ipynb`.

The entire non-identity H2 Pauli list printed by the notebook is the subject. Do not cherry-pick or drop terms after viewing outcomes. Global coefficient signs/phases do not alter commutation classification; magnitudes enter subnormalization.

If the extracted non-identity term count `L` is odd, the pair-only confirmatory endpoint is `CANNOT_CHECK_PAIR_PROTOCOL_ODD_L`; do not delete a term to make the test work.

## Exact compiler

For `L` even, form the complete graph on terms.

For pair `(i,j)`:
- `lambda_ij = sqrt(2)*sqrt(|a_i|^2+|a_j|^2)`;
- `u_ij = 1` iff Pauli strings anti-commute, else `0`.

For each integer `K=0,...,L/2`, solve the exact binary minimum-weight perfect matching

`min sum_(i,j) lambda_ij x_ij`

subject to:
- every term occurs in exactly one pair;
- `sum u_ij x_ij >= K`;
- `x_ij in {0,1}`.

The solver must report optimality / zero MIP gap. Independently verify every returned matching's degree constraints, anti-commutation count and objective from the raw subject.

This yields `Lambda_K`, the globally minimum pair-split subnormalization subject to at least `K` direct-unitary blocks.

## Fresh primary hypothesis H-R4C

Let `B=L/2`, `Lambda_0` be the coefficient-only optimum, and define the 1% normalization-slack set

`S_1% = {K : Lambda_K <= 1.01*Lambda_0}`.

Primary endpoint:

`direct_unitary_fraction_at_1pct = max(S_1%)/B`.

Fresh success gate:

> `direct_unitary_fraction_at_1pct >= 0.50`.

This was frozen before H2 output was inspected. It means at least half of pair blocks can eliminate TARE correction while paying no more than 1% coefficient-subnormalization overhead relative to the exact majorization optimum.

Secondary endpoints, all reported regardless of outcome:
- full `(K,Lambda_K)` frontier;
- `Lambda_0 / ||a||_1`;
- `Lambda_B` if full direct-unitary pairing is feasible;
- smallest overhead for 25%, 50%, 75% direct-unitary fractions;
- infeasible K values;
- Pauli/term identities in each selected matching.

## Donor-composed baselines / interpretation

Absorb:
- anti-commuting/unitary partitioning;
- TARE;
- standard Pauli LCU;
- grouped Hamiltonian simulation;
- magnitude grouping;
- generic perfect matching/MILP.

Therefore a positive does **not** claim any of those primitives as novel.

The candidate contribution is the heterogeneous representation rule:

> within TARE's explicitly unexplored large-operator split extension, jointly choose direct anti-commuting unitary blocks and TARE correction blocks on an exact normalization/correction Pareto frontier.

The pair case is a polynomial/exact special case; the general `m>2` problem becomes a weighted hypergraph partition/compiler problem and is a later MAX-R5/R6 extension.

## Hard boundaries

- `direct-unitary block` means target Pauli pair itself anti-commutes; do not infer low compiled gate cost beyond removal of TARE correction.
- no compiled T-count/depth claim from correction-block count alone;
- no stronger oracle/access change;
- no QSVT polynomial/error claim yet;
- novelty remains `CANNOT_CHECK` until hostile current-literature saturation and independent authority.

## Result terminals

- `R4C_FRESH_H2_HETEROGENEOUS_PAIR_FRONTIER_SUPPORTED` if primary gate passes;
- `R4C_REGIME_LIMITED_H2_NEGATIVE` if valid but gate fails;
- `CANNOT_CHECK_PAIR_PROTOCOL_ODD_L`;
- `R4C_INVALID_EXTRACTION_OR_SOLVER`.

Any negative recursively opens the next representation/compiler successor; it does not close MAX-R6.
