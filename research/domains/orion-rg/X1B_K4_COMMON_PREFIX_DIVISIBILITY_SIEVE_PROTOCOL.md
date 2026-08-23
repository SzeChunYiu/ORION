# X1-B k=4 — prospective first-factor divisibility sieve

Parent: #900.
Input affine space: seven-dimensional common-prefix `I^10` intersection.

## Evidence status

**PROSPECTIVE FROZEN DISCRIMINATOR.** No surviving factor directions have been computed before this packet is committed.

## Necessary factor condition

A genuine ten-block prefix has

`P_T=prod_{i=1}^{10}(1-X^{t_i})`.

Therefore for at least one nonzero `t in C_5^3`, P belongs to the principal ideal

`J_t = image(mu_t)`,

where

`mu_t(Q)=Q(1-X^t)`.

For fixed t, `J_t` is a linear subspace of the 125-dimensional group algebra, so intersection with the committed seven-dimensional affine P-space is exact finite-field linear algebra.

## Frozen algorithm

For every nonzero `t in F_5^3`:

1. build the 125x125 multiplication matrix for `1-X^t` in the canonical `X^g` basis;
2. test whether the seven-dimensional affine common-prefix `I^10` space intersects its image;
3. record intersection consistency and affine dimension;
4. quotient equivalent scalar multiples/projective directions only after raw element-level replay is complete.

If no t survives, factorability is impossible and both final k=4 orbits close.

If a small set survives, recursively restore further factors using preimage affine spaces, while additionally enforcing `I^(10-r)` after r factors are removed. Every recursive pruning step must remain exact linear algebra; any combinatorial branching cap exhaustion returns `CANNOT_CHECK_RESOURCE_BOUND`.

A surviving first factor is not a ten-factor witness.