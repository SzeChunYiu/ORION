# X1-B k=4 — complete rank<=3 completion census

Parent: #900.
Frozen protocol: `X1B_K4_ALL_RANK3_COMPLETIONS_PROTOCOL.md`.
Committed before residual-lift classification.

## Exact census

### Quotient orbit `942777`

Across its five off-diagonal affine specializations:

```text
t=0: rank3 1
t=1: rank3 1
t=2: rank3 1
t=3: rank2 1, rank3 52
t=4: rank3 1
```

After deduplication by the full diagonal/completion matrix:

- rank 1: 0;
- rank 2: **1**;
- rank 3: **56**;
- total: **57**.

### Quotient orbit `1470123`

Nonempty specializations are:

```text
(0,3): rank3 1
(1,3): rank3 1
(2,3): rank3 1
(3,0): rank3 1
(3,1): rank3 1
(3,2): rank3 1
(3,3): rank2 1, rank3 52
(3,4): rank3 1
(4,3): rank3 1
```

All other 16 off-diagonal specializations have no rank<=3 completion.

After deduplication:

- rank 1: 0;
- rank 2: **1**;
- rank 3: **60**;
- total: **61**.

The unique rank-2 completion is the common matrix already committed for both quotient orbits.

## Next invariant classification

For a rank-3 symmetric B, any minimal factorization

`B=Y M Y^T`

has `M` nonsingular on a three-dimensional space, and two such factorizations differ by invertible change of kernel coordinates. Therefore the property

`sum_{j in Z} y_j = 0`

for a fixed quotient mask Z is invariant across all rank-3 realizations.

Thus each of the 116 rank-3 completions can now be classified exactly as:

- `RESIDUAL_ZERO_SUM_FORCED` if some quotient-zero-sum mask has zero kernel sum under one canonical principal factorization; or
- `RESIDUAL_LIFT_ZERO_SUM_FREE` otherwise.

Only the latter can correspond to a hypothetical C15 counterexample.

The unique rank-2 matrix requires separate handling because a three-dimensional degenerate realization can carry extra radical coordinates invisible to B.