# Exact theorem: invertible coordinates can increase algebraic access degree

Status: **PROVED CONTROLLED STATEMENT — NO EMPIRICAL OUTCOME DEPENDENCE**

## Setup

Let a block contain signs

`r_1,...,r_b in {-1,+1}`

and define the encoded coordinates

- `u_1 = r_1`,
- `u_j = r_j r_{j-1}` for `j=2,...,b`.

## Theorem 1 — exact invertibility

For every `j=1,...,b`,

`r_j = product_{i=1}^j u_i`.

Therefore the map `T_b : r -> u` is bijective on `{-1,+1}^b`.

### Proof

For `j=1`, `r_1=u_1` by definition.

Assume `r_{j-1}=product_{i=1}^{j-1}u_i`. Since `u_j=r_j r_{j-1}` and every sign is its own multiplicative inverse,

`r_j = u_j r_{j-1}`

`    = u_j product_{i=1}^{j-1}u_i`

`    = product_{i=1}^j u_i`.

Induction completes the proof. Since every `r_j` is uniquely reconstructed, `T_b` is bijective. QED.

## Corollary 1 — inverse coordinate degree

Viewed as a multilinear polynomial on the Boolean-sign cube, recovered coordinate `r_j` is the monomial

`u_1 u_2 ... u_j`

of exact degree `j`.

Thus a block of length `b` contains inverse coordinates with degrees `1,2,...,b` even though the encoding preserves all information exactly.

## Corollary 2 — majority target pullback

For odd `b`, the canonical majority score

`M(r)=sum_{j=1}^b r_j`

becomes under encoded coordinates

`M(T_b^{-1}(u)) = u_1 + u_1u_2 + u_1u_2u_3 + ... + product_{i=1}^b u_i`.

Hence a degree-1 threshold in canonical relation coordinates is transformed into the sign of a polynomial containing monomials through degree `b`.

This statement is exact. It does **not** by itself prove the minimum threshold degree, sample complexity, or neural-network complexity required to represent the resulting Boolean classifier, because cancellations or alternative representations may exist. Those stronger lower bounds require separate arguments.

## Multiple blocks

The experiment partitions a length-`k` vector into blocks of maximum length `b` and applies the same transform independently. The global map is the Cartesian product of bijections and is therefore bijective. The maximum explicit inverse-coordinate degree is the maximum block length.

## ORION interpretation

This theorem isolates the mathematical mechanism tested by `run_invertible_obfuscation_ladder_v1.py`:

- latent information is unchanged;
- canonical relation coordinates expose the decision through a degree-1 score;
- the invertible nonlinear encoding moves the same latent coordinates into progressively higher-degree monomials.

Any empirical loss in a bounded learner is therefore compatible with a **coordinate-accessibility tax** rather than missing information. The experiment still needs hostile controls and cannot promote this controlled statement to an LLM or universal computational lower bound.
