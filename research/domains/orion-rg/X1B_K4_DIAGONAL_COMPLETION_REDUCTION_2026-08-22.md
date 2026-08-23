# X1-B k=4 — final two bilinear orbits reduce to exact diagonal completion

Parent: #900.
Protocol parent: `X1B_K4_GLOBAL_BILINEAR_MINRANK_PROTOCOL.md`.
Committed before the decisive minimum-rank execution.

## Observed affine-space structure

Reconstructing the canonical RREF parameterization from the prospectively frozen linear-stage verifier gives:

- orbit `942777`: affine dimension 14;
- orbit `1470123`: affine dimension 15.

For `942777`, exactly 13 nullspace basis directions are the elementary diagonal matrices `E_ii`; the only remaining free direction is one symmetric off-diagonal matrix of rank 7.

For `1470123`, exactly 13 nullspace basis directions are the elementary diagonal matrices `E_ii`; the two remaining free directions are symmetric off-diagonal matrices, each of rank 7.

Thus every candidate matrix has form

`B = A(t) + diag(d_0,...,d_12)`

where `t in F_5` for `942777` and `t in F_5^2` for `1470123`.

This is an exact consequence of the committed affine linear system, not a heuristic basis change.

## Exact rank<=3 decision by principal-basis completion

For a fixed off-diagonal specialization `A(t)`, only the diagonal is free.

If a symmetric matrix B over a field of odd characteristic has rank `r<=3`, then it has a nonsingular principal `r x r` submatrix `B[S,S]` for some `S` with `|S|=r` (symmetric elimination / principal-rank characterization).

For each `r in {0,1,2,3}` and each candidate principal set `S`:

1. enumerate the diagonal entries on S (`5^r` possibilities);
2. require `B[S,S]` nonsingular when r>0;
3. for every `i,j notin S`, enforce the Schur-complement identities

   `B[i,j] = B[i,S] B[S,S]^{-1} B[S,j]`;

   all off-diagonal quantities here are already fixed by A(t);
4. if the off-diagonal identities hold, set each remaining diagonal by the same formula and replay the full affine edge system plus exact rank.

This is complete for rank<=3: every such symmetric completion must appear in one of these principal-basis cases.

## Frozen finite search size

- orbit `942777`: 5 off-diagonal specializations;
- orbit `1470123`: 25 off-diagonal specializations;
- per specialization, at most `sum_{r=0}^3 C(13,r) 5^r` principal/diagonal cases.

This is far below the frozen resource cap and requires no heuristic optimizer or Gröbner fallback.

## Required terminal

For each orbit, return either:

- a complete rank<=3 witness with primitive edge replay; or
- exhaustive principal-basis infeasibility, which proves minimum rank >3 and eliminates the orbit from any C15 counterexample.

No C15 theorem authority follows until both k=4 survivors and the separately governed k=3 residual are closed and the entire reduction chain is independently reconstructed.