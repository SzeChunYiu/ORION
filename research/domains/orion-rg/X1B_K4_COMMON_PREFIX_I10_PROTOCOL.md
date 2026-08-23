# X1-B k=4 — prospective common-prefix `I^10` intersection discriminator

Parent: #900.
Input affine space: `X1B_K4_COMMON_PREFIX_GROUP_ALGEBRA_LINEAR_RESULT_2026-08-22.md`.

## Evidence status

**PROSPECTIVE FROZEN DISCRIMINATOR.** The intersection outcome below has not been computed or inspected before this packet is committed.

## Necessary factor-filtration condition

In `F_5[C_5^3]`, write `z_r=1-X^{e_r}`. Then

`F_5[C_5^3] ~= F_5[z1,z2,z3]/(z1^5,z2^5,z3^5)`.

For any ten kernel block sums `t_1,...,t_10`,

`P_T=prod_i(1-X^{t_i})`

belongs to the tenth power of the augmentation ideal `I=(z1,z2,z3)`, hence `P_T in I^10`.

In the monomial basis, `I^10` is exactly the span of `z1^a z2^b z3^c` with `0<=a,b,c<=4` and `a+b+c>=10`.

## Frozen exact algorithm

1. Reconstruct the three common-prefix multiplication equations in the canonical `X^g` basis and their 15-dimensional affine solution space.
2. Build the exact change-of-basis matrix using

   `X^(a,b,c)=(1-z1)^a(1-z2)^b(1-z3)^c`

   over `F_5`.
3. For every monomial of total degree `<10`, add the linear equation that its z-basis coefficient is zero.
4. Row-reduce the combined affine system over `F_5`.
5. If consistent, serialize a canonical particular solution and nullspace basis in both X and z coordinates and replay all common-prefix identities plus all filtration zeros.

## Terminals

- `COMMON_PREFIX_I10_INCONSISTENT`: no ten-factor prefix can realize the final rank-2 obstruction; both final k=4 quotient orbits are eliminated.
- `COMMON_PREFIX_I10_NONEMPTY`: record its exact affine dimension and restore the next condition, factorability into ten individual `(1-X^t)` factors and zero-sum-free compatibility.

No heuristic factor search may replace this exact intersection test.