# X1-B k=4 — final rank-3 forbidden classes have trivial `GL(3,5)` stabilizer

Parent: #900.
Input classes: `X1B_K4_RANK3_FORBIDDEN_GL_CLASSES_2026-08-22.md`.
Committed before using this fact downstream.

## Exact audit

For each canonical forbidden set R3-10, R3-11, and R3-12, enumerate all invertible `3x3` matrices over `F_5` by their ordered basis-image columns. There are

`|GL(3,5)|=(5^3-1)(5^3-5)(5^3-5^2)=1,488,000`

such matrices.

For each matrix M, test exact set equality

`M(S)=S`.

## Result

Each of the three classes has stabilizer size exactly **1**: only the identity matrix preserves the canonical forbidden set.

Thus the induced action on the 124 nonzero group elements has 124 singleton orbits for every class.

## Consequence

There is no nontrivial linear symmetry of the frozen forbidden set that can justify a first-term or partial-sequence normalization in the authoritative ten-prefix search. The protocol's decision to assume no symmetry reduction is therefore sharp for these canonical representatives.

This does not rule out non-linear/search-state reductions, additive-combinatorial bounds, or equivalences between different forbidden classes. It only removes `GL(3,5)` stabilizer normalization for each fixed class.

## Claim boundary

This is a finite group-action audit. It carries no C15 theorem or novelty authority.