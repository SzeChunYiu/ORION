# Unbounded Proof-Language Certificate Waste over Finite Abelian Groups — R10

Date: 2026-08-26

Status: analytic strengthening of the integrated A+B abstraction-boundary paper. Classical Davenport constants and their values are donor-owned. The paper-specific point is the exact comparison of two sound shortening languages on the same production state space and objective.

## 1. Aggregation grammar

Let `G` be a nontrivial finite abelian group written additively. A state is a finite multiset/word

`W=(g_1,...,g_m)`

of nonzero group elements with nonzero total

`sum(W) != 0`.

Semantics is the total group element. Support and objective are the number of letters.

We compare two sound shortening languages.

### Weak language P0 — zero-sum deletion

Delete any nonempty proper subsequence `Z` satisfying

`sum(Z)=0`.

### Strong language P1 — aggregation-complete

P1 contains P0 and additionally permits pair aggregation for any two occurrences `a,b`:

- if `a+b != 0`, replace `a,b` by the single letter `a+b`;
- if `a+b = 0`, delete the pair.

Both cases preserve the total group sum and strictly reduce support. Because the source total is nonzero, the resulting state cannot be empty after a total-preserving reduction.

The grammar is deliberately explicit: there is no hidden auxiliary state and no third move family.

## 2. Weak terminal complexity

Let `D(G)` be the classical Davenport constant: the least integer `d` such that every length-`d` sequence over `G` has a nonempty zero-sum subsequence.

### Theorem AB-R10.1

The maximum terminal support under P0 is exactly

`beta_0(G)=D(G)-1`.

### Proof

Any state of length at least `D(G)` contains a nonempty zero-sum subsequence. The whole state cannot be zero-sum because admissible states have nonzero total. Hence the zero-sum subsequence is proper and P0 can shorten the state. Thus every P0-terminal state has length at most `D(G)-1`.

By the definition of `D(G)`, there exists a zero-sum-free sequence `W` of length `D(G)-1`. Such a sequence necessarily has nonzero total, since otherwise the whole sequence would be a nonempty zero sum. Therefore `W` is an admissible P0-terminal state of matching length. ∎

This lower witness is a realized state, not merely an abstract word outside the production state space.

## 3. Strong intrinsic support

### Theorem AB-R10.2

Under P1, every admissible state reduces to the unique singleton containing its total sum. Hence the intrinsic production support is

`kappa_1(G)=1`.

### Proof

Take any admissible state of support greater than one and choose any two occurrences `a,b`.

- If `a+b=0`, delete them.
- Otherwise replace them by `a+b`, which is a nonzero legal letter.

Either move preserves the total and strictly reduces support. Iteration therefore terminates. The terminal state cannot have support zero because its total is the original nonzero total. A support-one state with total `t` must be the singleton `(t)`, so the normal form is unique. ∎

No commutative-algebra normal-form theorem is needed beyond associativity and commutativity of the group operation.

## 4. Unbounded certificate inflation

### Corollary AB-R10.3

On the same state space, semantics, support functional, and objective,

`weak certificate complexity = D(G)-1`,

while

`intrinsic production support = 1`.

Thus the additive certificate waste is

`D(G)-2`

and the multiplicative inflation factor is

`D(G)-1`.

These quantities are unbounded over finite abelian groups. For example:

- `G=C_n` gives `D(G)=n`, so the weak budget is `n-1` and the strong budget is 1;
- `G=C_2^d` gives `D(G)=d+1`, recovering weak budget `d` and strong budget 1.

The dimension-five XOR example in the R9 production audit is the case `G=C_2^5`.

## 5. Complete interaction audit

The strong language has only two semantic move outcomes: remove a zero-sum pair or replace a nonzero-sum pair by its sum, in addition to arbitrary weak zero-sum deletion.

Every P1 move preserves the same total and decreases support. Therefore every successor has the same unique singleton normal form. In particular every local critical peak between:

- deletion/deletion;
- deletion/aggregation; and
- aggregation/aggregation

is joinable at that singleton.

This gives global confluence on the admissible state space by direct unique-normal-form reasoning together with termination; no appeal to bounded enumeration is required. The existing dimensions 2–4 exhaustive XOR audit remains an implementation corroboration of the `C_2^d` subfamily.

## 6. Why the result matters for certificate ownership

The theorem establishes a sharp negative statement about proof-language interpretation:

> A sound shortening language can overstate the support intrinsically required by the full production system by an arbitrarily large factor, even when both languages act on exactly the same finite-group semantics and every move is semantics-preserving and strictly improving.

Therefore a terminal lower certificate belongs to the named proof language until a production-realization and move-completeness audit is passed.

The gap is not caused by infeasible abstract witnesses, different objectives, or different semantic state spaces. It is caused solely by omitted legal transformations.

## 7. Direct-enumerator consequence

Suppose a declared direct enumerator over `n` positions has `q` nonidentity local labels and enumerates all support patterns through budget `B`. Its candidate volume is

`N_B(n,q)=sum_{j=0}^B binom(n,j) q^j`.

If a weak certificate uses `B=D(G)-1` while the complete aggregation language licenses `B=1`, then

`N_{D(G)-1}(n,q) / N_1(n,q)`

grows on the order of `n^{D(G)-2}` for fixed `G,q` with `D(G)>=2`.

This is an exact statement about the declared enumerator. It is not an algorithm-independent runtime lower bound, because a different solver may avoid explicit support enumeration.

## 8. Prior-art boundary

Classical zero-sum theory owns `D(G)` and its structural theory. Term-rewriting literature owns termination/confluence machinery; compiler/equality-saturation literature owns rewrite-registry engineering; associative aggregation itself is elementary.

The residual contribution is the **certificate-ownership comparison**: an exact Davenport-sized terminal lower bound in one sound proof language versus a unique support-one normal form in a strictly richer sound production language on the same states and objective, yielding arbitrarily large certificate inflation.

The publication claim must therefore be framed as an abstraction/proof-language theorem and then tested on a non-toy production rewrite system. It must not claim novelty for pairwise group aggregation or Davenport constants.

## 9. Application discriminator

The next paper-grade experiment should freeze a real equality-saturation, parity-synthesis, or exact-rewrite pipeline with nested rule registries `P_weak subset P_full` and ask:

1. which lower/terminal certificates survive the full registry;
2. how large the empirical certificate inflation is;
3. which omitted rule schemas cause collapse;
4. whether the smaller production budget changes exact search cost;
5. whether a critical-interaction audit predicts the collapses.

A null transfer result does not refute the theorem. It determines whether the theorem is a broad compiler result or a pure abstraction-boundary result.
