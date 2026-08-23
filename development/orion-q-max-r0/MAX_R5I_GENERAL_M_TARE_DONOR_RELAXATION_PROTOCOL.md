# ORION-Q MAX-R5I general-m TARE donor-relaxation protocol

Date: 2026-08-20
Parent: #679
Branch: `shadow/orion-q-max-r0`
Status: frozen before R5I result generation.
Authority ceiling: donor-completeness / development only; cannot authorize R6.

## Reopen cause

MAX-R5H absorbs arbitrary direct anticommuting cliques but its corrected-TARE block alphabet is exact only for `m=2`. TARE itself is a general `m <= 2n+1` construction. A donor-composed R6 baseline therefore cannot simply pretend that larger TARE blocks do not exist.

The exact optimal controlled Tag/Restore resource cost for arbitrary `m` and arbitrary free auxiliary frame `{R_k}` is itself part of the unresolved R6 research problem. R5I therefore does **not** fake an exact implementation. Instead it constructs a resource relaxation that is strictly at least as favorable as the published explicit general-m TARE implementation on the coordinates used for domination.

## Question

Can any `m>=3` general-TARE block, even under an optimistic donor relaxation, Pareto-dominate the strongest current exact mixed-cardinality frontier on already-open H4 or N2?

If no relaxed general-m donor state dominates the named incumbent/candidate, then the actual published general-m donor cannot dominate it under the same frozen projection. If the relaxation does dominate, the result is inconclusive and full general-m implementation is required before R6.

## Published donor facts absorbed

For a block of `m` target Pauli terms with coefficients `a_j`, TARE v4 provides:

- admissibility for arbitrary target strings when `m <= 2n+1`;
- block normalization `sqrt(m) * ||a||_2`;
- a mutually anticommuting auxiliary family `{R_k}`;
- an explicit `Uanti` implementation using `2m-1` Pauli exponentials;
- Tag/Restore circuitry in addition to `Uanti`;
- splitting + outer LCU for larger operators.

The donor paper leaves block partitioning and optimized auxiliary-family choice as open directions. R5I does not assign ORION credit for those gaps; it only closes the baseline-completeness question.

## Exact donor alphabet retained

The R5I relaxed donor includes every block already available to MAX-R5H mixed donor composition:

1. Pauli singleton;
2. arbitrary direct mutually anticommuting clique;
3. exact controlled-cost `m=2` TARE block.

Thus R5I cannot become weaker than the R5H mixed frontier.

## Optimistic `m>=3` TARE hyperblock

For every subset `G` of size `3 <= m <= min(12, 2n+1)` inside the same frozen coefficient-local 12-term window, add a hypothetical donor block with:

`Lambda_G = sqrt(m) * sqrt(sum_{j in G} |a_j|^2)`.

Resource coordinates are deliberately optimistic:

- block-internal controlled CNOT: `0`;
- Tag cost: `0`;
- Restore cost: `0`;
- auxiliary/tag ancilla capacity: `0`;
- block count: `1`;
- projected T: only the controlled-Rz synthesis cost of the published explicit `2m-1`-exponential `Uanti` sequence,

`T_LB = 2 * (2m-1) * 48`.

No controlled-H, conjunction, correction support, or additional Clifford+T cost is charged.

This is **not claimed achievable**. It is a donor relaxation: every omitted cost is nonnegative under the frozen resource model, so any actual implementation of the published explicit TARE circuit has no better coordinates than this relaxed block for the same `m`, coefficient subset and outer cardinality.

The relaxation intentionally starts at `m=3`: `m=2` already has an exact proof-carrying implementation in the donor alphabet and must not be replaced by a fictitious cheaper two-term block.

## Search

For open H4 and open equilibrium N2 only:

- keep the exact same sorted Pauli lists and 12-term window boundaries used by R5H;
- enumerate all exact set partitions of each window from the retained exact donor alphabet plus every optimistic general-m hyperblock;
- Pareto-prune only by the frozen non-compensatory coordinates;
- compose window frontiers exactly/sparsely as in R5H.

## Coordinates

For every state:

- `Lambda`;
- block-internal controlled CNOT;
- block-internal projected T;
- outer block count;
- maximum ancilla capacity;
- dense-PREP + unary-selector reference total T using the same R5H bookkeeping.

## Baselines / comparisons

`B_exact`: exact R5H mixed donor frontier (singleton + direct clique + exact m2 TARE).

`B_relaxed`: `B_exact` plus optimistic `m>=3` TARE hyperblocks.

For each subject bind the exact R5F/R5E pair reference and identify the exact R5H `P_BALANCED` point if one exists.

## Outcomes

### `R5I_GENERAL_M_RELAXATION_NONDOMINATING`

Allowed only if:

- a valid exact mixed `P_BALANCED` point exists;
- no state in `B_relaxed` strictly dominates that point;
- no relaxed state has identical `Lambda/CNOT/T/blocks/ancilla/reference-total-T` with a lexically different hyperblock construction that would erase method distinction;
- the relaxed frontier calculation completes without saturation bailout.

Interpretation: the actual published general-m TARE donor cannot resource-dominate the bound point under this frozen projection. This does **not** prove novelty.

### `R5I_GENERAL_M_RELAXATION_DOMINATES_OR_TIES`

If any optimistic hyperblock composition dominates/ties the exact mixed candidate, R6 remains blocked. Implement full general-m TARE or strengthen the incumbent before proceeding.

### `R5I_INCONCLUSIVE`

Use for computational saturation, missing exact R5H bound point, or inability to bind the resource coordinates.

## Hostile checks

- removing all hyperblocks must reproduce the R5H exact mixed frontier hashes/resources;
- `m=2` fantasy hyperblocks are forbidden;
- every hyperblock must satisfy `m<=2n+1`;
- normalization must be recomputed directly from coefficients;
- relaxed T must equal `96*(2m-1)` exactly;
- CNOT/ancilla zero must be labeled `OPTIMISTIC_RELAXATION`, never an achievable circuit claim;
- block-count PREP/selector changes must still be charged;
- no fresh R6 subject may be opened during R5I.
