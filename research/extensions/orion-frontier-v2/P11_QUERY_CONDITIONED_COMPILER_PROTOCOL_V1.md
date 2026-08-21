# P11 Query-Conditioned State Compiler — Confirmatory Protocol V1

Status: **FROZEN AFTER PILOT, BEFORE CONFIRMATORY OUTCOMES**
Frozen: 2026-08-20

## Pilot disclosure

A non-authorizing exploratory pilot was run before this protocol to check feasibility only. It used cells `(d,s)=(12,2),(12,3),(14,3),(16,3)`, 8 sampled queries/cell, and training sizes through 256. It suggested: raw linear near chance, one-coordinate compiled parity exact, and a finite-sample nuisance tax for a universal degree-s monomial bank. Pilot values are not confirmatory evidence and are not used as protected outcomes.

The confirmatory cells below intentionally use fresh seeds and different dimension/order combinations.

## Confirmatory question

When one current query selects one member of a large family of independent target functions, does query-conditioned state compilation avoid the representation-size and finite-sample burden of a fixed universal feature bank while preserving exact task performance?

## Frozen worlds

Cells:
- `(d=14, s=2)`, universal dimension `C(14,2)=91`;
- `(d=16, s=4)`, universal dimension `C(16,4)=1820`;
- `(d=18, s=3)`, universal dimension `C(18,3)=816`;
- `(d=20, s=3)`, universal dimension `C(20,3)=1140`.

For every cell, `X` is uniform on `{-1,+1}^d`. The query family is all size-s coordinate subsets. The label for query S is the parity product of the selected coordinates.

## Arms

1. `RAW_LINEAR`: d raw coordinates, one fixed linear logistic learner per query.
2. `UNIVERSAL_BANK`: all `binom(d,s)` degree-s parity monomials, same fixed learner per query.
3. `QUERY_COMPILED`: exactly the single parity monomial requested by the current query, same fixed learner.

The universal and query-compiled arms contain the identical decisive coordinate for the active query. The difference is that the universal arm additionally materializes every other same-order query coordinate.

## Fixed learner

`sklearn.linear_model.LogisticRegression`
- `C=1.0`
- `solver='liblinear'`
- `max_iter=1000`
- no hyperparameter selection
- deterministic data/query seeds

## Fresh seeds and sample sizes

Confirmatory master seed: `914311`.

Per cell:
- 12 queries sampled without replacement from the full query family;
- train sizes: `32,64,128,256,512,1024`;
- test size: `8192`, fixed within cell across train sizes and arms.

Each train size receives a fresh deterministic training sample; all arms/query heads at that size see the same examples and labels.

## Primary protected gates

The positive terminal is `P11_QUERY_CONDITIONED_COMPILATION_GAP_SUPPORTED` only if ALL conditions hold:

1. theorem verifier confirms the exact universal dimensions and parity orthogonality on exhaustive small-d sanity worlds;
2. `QUERY_COMPILED` mean accuracy is at least `0.995` in every cell at every train size;
3. `RAW_LINEAR` mean accuracy is at most `0.60` at n=1024 in every cell;
4. for every cell with universal dimension >= 800, at n=32 the compiled-minus-universal mean accuracy gap is at least `+0.15`;
5. define the 0.90 threshold as the smallest frozen train size at which mean accuracy >=0.90; in every cell with universal dimension >=800, the universal-bank threshold divided by compiled threshold is at least `4`, with `not reached` counted as greater than the maximum tested ratio;
6. deterministic replay is byte-identical;
7. query identity, label, and selected monomial are generated independently of the learner and no active-query coordinate is omitted from either universal or compiled arm.

If any gate fails, terminal is `P11_QUERY_CONDITIONED_COMPILATION_CONFIRMATORY_GATE_NOT_MET` and the failure remains visible.

## Secondary descriptive quantities

- accuracy curves for all arms;
- exact universal/compiled representation dimension ratio `binom(d,s)`;
- train-time and prediction-time wall clock (descriptive only; hardware-dependent);
- materialized feature count per training example;
- naive arithmetic work to build the active compiled monomial (`s-1` multiplies) versus materializing all degree-s monomials (`binom(d,s)*(s-1)` without subexpression reuse), explicitly labeled as an implementation upper-bound comparison rather than a lower bound.

## Claim boundary

A positive result may support:

> For a frozen family of parity queries and a fixed linear downstream learner, allowing the current query to participate in state construction collapses an exact combinatorial universal representation requirement to one active coordinate and avoids a large finite-sample nuisance burden from irrelevant universal coordinates.

It may NOT support:
- universal superiority of query-conditioned representations;
- arbitrary nonlinear-decoder lower bounds;
- LLM or agent performance claims;
- a universal compute-conservation law.
