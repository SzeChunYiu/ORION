# X1-B k=4 — common-prefix `I^10` intersection result

Parent: #900.
Frozen protocol: `X1B_K4_COMMON_PREFIX_I10_PROTOCOL.md`.
Committed before nonlinear ten-factor search.

## Exact intersection result

The common-prefix system has 125 group-algebra coefficient variables. Adding the exact `I^10` filtration constraints—vanishing of every z-monomial of total degree `<10`—gives a consistent affine system with:

- combined linear rank: **118**;
- affine dimension: **7**.

Thus the factor-filtration condition does not yet eliminate the final quotient obstruction, but reduces the prefix to a seven-parameter affine family.

## Canonical z-coordinate form

`I^10` has dimension 10 in `F_5[z1,z2,z3]/(z1^5,z2^5,z3^5)`:

- degree 10: 6 monomials;
- degree 11: 3 monomials;
- degree 12: 1 monomial.

A canonical particular solution of the seven-dimensional common-prefix intersection has only

```text
3 z1^2 z2^4 z3^4 + 4 z1^4 z2^2 z3^4
```

nonzero.

A canonical nullspace basis can be chosen with support among

```text
z1^3 z2^4 z3^3,
z1^4 z2^3 z3^3,
z1^4 z2^4 z3^2,
z1^3 z2^4 z3^4,
z1^4 z2^3 z3^4,
z1^4 z2^4 z3^3,
z1^4 z2^4 z3^4.
```

with the exact RREF relations preserved in the verifier.

In particular the forced degree-10 coefficients include

`[z1^2 z2^4 z3^4]P = 3`,
`[z1^3 z2^3 z3^4]P = 0`,
`[z1^4 z2^2 z3^4]P = 4`,

matching the rank-2 residual extension form on its first two coordinates.

## Next exact question

Determine whether any element of this seven-dimensional affine space factors in the group algebra as

`P=prod_{i=1}^{10}(1-X^{t_i})`

for ten nonzero `t_i in C_5^3`, with the resulting three 12-term extensions all zero-sum-free.

The factorization/extension problem must be solved exactly or return `CANNOT_CHECK_RESOURCE_BOUND`; the nonempty `I^10` intersection alone is not sequence evidence.