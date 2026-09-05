# An occurrence-preserving exchange for long two-value cyclic atoms — V1

Status: **proved structural exchange and two-length-spectrum obstruction**. The strict long-atom threshold is part of the hypotheses.

## 1. Reusable long-atom exchange lemma

Let `p` be prime, let `u,v` be distinct nonzero elements of `C_p`, and let `S=u^r v^t` be zero-sum with `r,t<p` and `|S|>p`. Suppose an atomic divisor `P|S` has length `N>p/2+1`.

The long cyclic-atom index theorem of [Savchev–Chen, Section 5 and Proposition 10](https://arxiv.org/pdf/math/0602568) gives a generator `h` for which the positive representatives in `P` sum to `p`. Since `2N>p`, one of its two coefficients must be one. Write

\[
P=h^A(jh)^B,\qquad j\ge2,\quad A,B\ge1,
\]

and put `w=j-1`, `s=p-N`. Then

\[
A+B=N,\qquad A+jB=p,\qquad wB=s.
\]

In particular, `1<=B<=s`. The elementary inequality

\[
B+s/B\le s+1
\]

follows from `(B-1)(B-s)<=0`. Hence

\[
A-j=N-B-1-s/B\ge2N-p-2>0.
\]

The complement `S/P` is nonempty, because `|S|>p>=|P|`. It is zero-sum, and it contains both values: a nonempty pure zero-sum would require at least `p` copies of one value, whereas the entire `S` has fewer. Therefore the actual sequence

\[
P'=h^{A-j}(jh)^{B+1}
\]

divides `S`. Its positive representatives sum to `p`, so it is an atom. Its length is `N-w`.

Consequences:

1. The greatest common divisor of all atomic-divisor lengths of `S` is one. Indeed, any common divisor divides `N` and `w=N-|P'|`, hence divides `p=N+wB`; it cannot equal `p` because `N<p`.
2. If all atomic-divisor lengths belong to a two-point spectrum `{M,N}`, where `M<N`, then

\[
w=N-M,\qquad (N-M)\mid(p-N).
\]

The atom `P'` is strictly shorter than `P`, so its length must be `M`.

The only external input is the existing long-atom index theorem, used with its strict threshold `N>p/2+1`. All exchange capacities are proved above.

## 2. Review and scope

The quotient-structure researcher supplied this proof; a separately tasked proof auditor and the coordinating researcher checked the index threshold, the mixed complement, every exchanged occurrence, and the integer inequality. The general length-gcd conclusion is superseded in strength by the elementary `TWO_VALUE_LATTICE_ATOMS_AND_LENGTH_GCD_DICHOTOMY_V1.md`, which needs no long atom. The exact exchanged length and two-length divisibility obstruction here remain additional information.

A formal candidate length is not an existing atomic divisor. Short atoms need a different argument. No prime enumeration or unproved Davenport value is used.
