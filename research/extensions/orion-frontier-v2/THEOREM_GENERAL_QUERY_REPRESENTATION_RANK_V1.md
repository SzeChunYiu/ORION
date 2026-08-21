# Theorem: General Query-Family Representation Rank V1

Status: EXACT CONTROLLED FOUNDATION / CLASSICAL LINEAR-ALGEBRA ARGUMENT
Frozen: 2026-08-20

## Setup

Let `X` be a domain with probability measure `mu`, and let `F = {f_1,...,f_N}` be real-valued query functions in `L2(mu)`. A query-agnostic representation is a fixed map `phi : X -> R^m`. Exact linear query support means that for every q there exists `w_q in R^m` such that

`f_q(x) = <w_q, phi(x)>` almost surely.

## Theorem 1 — rank lower bound

If the linear span of `F` has dimension `r`, every fixed representation supporting exact linear readout of every query satisfies

`m >= r`.

Proof: every `f_q` lies in the span of the m coordinate functions of `phi`; that span has dimension at most m and must contain `span(F)`.

This is elementary linear algebra. ORION does not claim the rank argument itself as new mathematics.

## Theorem 2 — approximate orthonormal frontier

Assume `f_1,...,f_N` are orthonormal in `L2(mu)`. Let U be any m-dimensional subspace of `L2(mu)`, representing all functions linearly accessible from a fixed m-dimensional representation. Let `P_U` be orthogonal projection onto U. Then

`(1/N) sum_q ||f_q - P_U f_q||_2^2 >= 1 - m/N`.

### Proof

For every q, `||f_q - P_U f_q||_2^2 = 1 - ||P_U f_q||_2^2`.

Choose an orthonormal basis `u_1,...,u_m` for U. Then

`sum_q ||P_U f_q||_2^2 = sum_j sum_q |<u_j,f_q>|^2 <= sum_j ||u_j||_2^2 = m`

by Bessel's inequality. Divide by N.

QED.

## Query-conditioned comparison

If a compiler receives both x and the current query q and is allowed to compute a task-relevant state `c(x,q)`, it need not materialize a fixed basis supporting all N queries simultaneously. For the trivial exact compiler `c(x,q)=f_q(x)`, one scalar suffices, but this can be criticized as answer laundering.

Therefore ORION separates two experimental regimes:

1. **direct specialization** — compiler may compute the queried function itself; useful for exact resource-transfer accounting and classical partial-evaluation analogy;
2. **no-answer-laundering specialization** — a query names multiple latent basis functions and the compiler may expose only those component features; the downstream learner still must compute the final decision.

Only regime 2 is used to argue that query-conditioned state construction can reduce nuisance dimensionality without simply returning the answer.

## Corollary — parity family

For uniform Boolean inputs, distinct parity characters are orthonormal. Thus all size-s parities have fixed exact linear representation rank `binom(d,s)`, and the average squared approximation error of any m-dimensional fixed linear-accessible subspace is at least

`1 - m/binom(d,s)`.

## Claim boundary

These are lower bounds for fixed linear-accessible function spaces. They are not lower bounds for arbitrary nonlinear decoders, unrestricted circuits, or total algorithmic complexity. Their role is to make the resource accounting in the ORION frontier programme explicit and auditable.
