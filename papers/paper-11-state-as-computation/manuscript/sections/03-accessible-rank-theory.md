# Accessible-rank theory

Let `X` be a domain with distribution `mu`, and let `F={f_1,...,f_N}` be query functions in `L2(mu)`. A fixed query-agnostic representation is `phi:X->R^m`. It supports exact linear query answering when, for every `q`, some `w_q` satisfies `f_q(x) = <w_q, phi(x)>` almost surely.

## Query-family accessible-rank bound

If `span(F)` has dimension `r`, every fixed representation supporting exact linear readout of all queries has `m >= r`.

**Proof.** Every `f_q` lies in the span of the `m` coordinate functions of `phi`. That span has dimension at most `m` and must contain the `r`-dimensional span of `F`; hence `m>=r`. The theorem is elementary linear algebra; its role here is as a systems resource boundary, not as a claim of mathematical novelty.

## Approximate orthonormal frontier

For orthonormal `f_1,...,f_N` and any `m`-dimensional linearly accessible subspace `U`, Bessel's inequality gives `(1/N) sum_q ||f_q - P_U f_q||_2^2 >= 1 - m/N`. This is an access-class statement, not a lower bound on unrestricted nonlinear decoding.

## Parity corollary

For `X={-1,+1}^d` under the uniform measure and all size-`s` subsets `S`, define `f_S(x)=product_{i in S} x_i`. Distinct parity characters are orthogonal. A fixed exact linear-accessible representation supporting all size-`s` queries therefore requires at least `binom(d,s)` coordinates. A query-conditioned construction need expose only the selected query structure. This establishes an exact accessible-representation gap, not a total-time lower bound.