# X1-B k=4 — every rank-3 bilinear completion has a zero-sum-free 13-term residual lift

Parent: #900.
Input completion census: `X1B_K4_ALL_RANK3_COMPLETIONS_RESULT_2026-08-22.md`.
Committed before forbidden-set orbit classification.

## Exact result

For each of the 116 rank-3 symmetric completion matrices B across the two final quotient orbits:

1. choose a canonical nonsingular principal 3x3 block `C=B[S,S]`;
2. set `Y=B[:,S]` and `M=C^{-1}`, so `B=Y M Y^T` exactly over `F_5`;
3. for every nonempty quotient-zero-sum mask Z in the corresponding 13-position `C_3^3` residual, compute `z_Z=sum_{j in Z}Y_j`.

Result:

- orbit `942777`: **56/56** rank-3 completions have `z_Z != 0` for every quotient-zero-sum mask;
- orbit `1470123`: **60/60** rank-3 completions have `z_Z != 0` for every quotient-zero-sum mask.

Hence all 116 rank-3 completions give genuine zero-sum-free lifts of the 13-term residual itself to `C_3^3 direct-sum C_5^3`.

## Invariance

Because rank(B)=3, the bilinear form is nonsingular on the realized three-dimensional kernel space. Any two minimal factorizations are related by an invertible change of kernel coordinates. Therefore whether `z_Z=0` is invariant across all rank-3 realizations of the same B.

Thus none of these 116 matrices can be eliminated by choosing a different minimal factorization.

## Induced prefix-obstruction sizes

For each completion, form the forbidden prefix set consisting of 0 together with the negatives of `z_Z`, `z_W`, and `z_Z+z_W` over every disjoint quotient-zero-sum pair `(Z,W)`.

The rank-3 completions induce forbidden sets of sizes only:

- 10;
- 11;
- 12.

Raw canonical-factorization counts are:

```text
942777: size10=8, size11=16, size12=32
1470123: size10=4, size11=24, size12=32
```

Before running any ten-prefix search, these sets must be quotiented by exact `GL(3,5)` equivalence because prefix existence is invariant under invertible kernel coordinate changes.

## Consequence

Residual zero-sum-freeness is not the missing condition. The live classification problem is now the finite family of `GL(3,5)`-orbits of 10–12 point forbidden sets induced by all rank-3 completions, plus the separately treated rank-2 radical-realization family.