# Theorem: Query-Conditioned Compilation Gap V1

Status: EXACT CONTROLLED THEOREM / NOT A UNIVERSAL LOWER BOUND
Frozen: 2026-08-20 before confirmatory execution.

## Setup

Let `X = {-1,+1}^d` with the uniform measure. Fix `1 <= s <= d` and define the query family

`Q_s = { S subseteq [d] : |S| = s }`.

For each query `S`, define the parity character

`f_S(x) = product_{i in S} x_i`.

There are `N = binom(d,s)` such queries.

A **query-agnostic representation** is any fixed map `phi : X -> R^m` that does not depend on S. It supports exact linear query answering if, for every `S in Q_s`, there exists a vector `w_S in R^m` such that

`f_S(x) = <w_S, phi(x)>`

for every `x in X`.

## Theorem 1 — exact dimension lower bound

Every query-agnostic representation supporting exact linear readout of all size-s parity queries satisfies

`m >= binom(d,s)`.

### Proof

Under the uniform measure on the Boolean hypercube, distinct parity characters are orthogonal:

`E[f_S(X) f_T(X)] = 0` for `S != T`, and `1` for `S = T`.

Hence the `N = binom(d,s)` functions `{f_S : S in Q_s}` are linearly independent in the vector space of real-valued functions on X.

If every `f_S` is a linear readout of `phi`, then every `f_S` lies in the span of the m coordinate functions of `phi`. That span has dimension at most m. Because it contains N linearly independent functions, `m >= N`.

QED.

## Theorem 2 — one-coordinate query-conditioned compiler

If the query may participate in state construction, define

`C(x,S) = product_{i in S} x_i`.

Then `C(x,S) in R` is one-dimensional and the identity readout returns `f_S(x)` exactly. A straightforward implementation requires `s-1` binary multiplications after the requested coordinates are read.

Therefore the exact **representation dimension gap** between fixed universal state and query-conditioned compiled state is at least

`binom(d,s) : 1`

for this controlled linear-readout problem.

## Corollary — multiple query orders

If one fixed representation must support all parity queries with sizes in a set `K subseteq {0,...,d}`, exact linear readout requires

`m >= sum_{s in K} binom(d,s)`.

The proof is identical because all Boolean parity characters are mutually orthogonal.

## What this theorem does and does not say

It DOES establish:
- an exact gap between query-agnostic state materialization and query-conditioned state compilation;
- a family in which goal/query conditioning can collapse required linear-readout representation dimension from combinatorial to one;
- a formal basis for studying representation construction as a computational action.

It DOES NOT establish:
- a lower bound for arbitrary nonlinear downstream decoders;
- a lower bound on total algorithmic time for parity;
- that every task admits an advantageous query-conditioned compiler;
- that LLMs automatically discover or exploit such compilers;
- novelty of parity orthogonality or linear-method lower bounds themselves.

The scientific novelty target is the ORION resource/programme interpretation and cross-domain execution, not ownership of classical parity mathematics.

## Nearest-work boundary

Classical dimension and kernel lower bounds already use orthogonal parity families to show limitations of fixed linear/kernel approaches. Predictive V-information already formalizes computationally usable information. The present theorem is therefore used as a transparent controlled foundation for a different systems question: **what happens when state construction is explicitly allowed to depend on the current query, and its cost is accounted jointly with downstream inference/search cost?**
