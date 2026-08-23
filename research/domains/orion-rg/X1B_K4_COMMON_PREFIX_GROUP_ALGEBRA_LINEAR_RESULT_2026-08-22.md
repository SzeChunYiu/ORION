# X1-B k=4 — common-prefix group-algebra linear result

Parent: #900.
Frozen protocol: `X1B_K4_COMMON_PREFIX_GROUP_ALGEBRA_PROTOCOL.md`.
Committed before imposing augmentation-ideal/factorability constraints.

## Result

Representing an unknown common prefix `P in F_5[C_5^3]` by its 125 coefficients and imposing, for each of the three residual pair types,

`P (1-X^x)(1-X^y) = Omega`

produces 375 coefficient equations over `F_5`.

Exact row reduction gives:

- linear equation rank: **110**;
- system consistency: **YES**;
- affine solution dimension: **15**.

Thus the full group-algebra identity is much stronger than the top-coefficient bilinear relaxation, but does not by itself eliminate the final quotient obstruction.

## Structural observation

All three pair elements have zero third coordinate. Consequently the multiplication equations preserve the five `z3`/third-coordinate layers; the 15-dimensional freedom is compatible with a small per-layer residual freedom rather than a generic 125-dimensional prefix.

## Next mandatory condition

Any true ten-block prefix has form

`P_T=product_{i=1}^{10}(1-X^{t_i})`.

Every factor belongs to the augmentation ideal `I`, hence

`P_T in I^10`.

For `F_5[C_5^3] ≅ F_5[z1,z2,z3]/(z1^5,z2^5,z3^5)`, `I^10` is the linear span of monomials `z1^a z2^b z3^c` with `a+b+c>=10` and each exponent at most 4.

Therefore the next exact discriminator is the **linear intersection**

`{P : all three common-prefix equations} intersect I^10`.

Only if this intersection is nonempty should nonlinear factorability into ten sequence factors be attempted.

No C15 counterexample or theorem follows from the 15-dimensional relaxed solution space.