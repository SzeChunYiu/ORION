# Prime-uniform `C_p^3` multiwise Davenport master reduction — V2

Status: **research reduction / program architecture**. The donor inputs are named below. The short-forcing hypotheses are **not** claimed proved for general `p`.

## Scope and donor baseline

Let `p>=5` be prime and `G=C_p^3`.

The donor-derived `D2_PRIME_POWER_COROLLARY_V1.md` gives

\[
D_2(G)=\frac{9p-5}{2}.
\]

The Freeze--Schmid lower bound specializes, for every `k>=2`, to

\[
D_k(G)\ge L_k:=\frac{9p-5}{2}+(k-2)p.
\]

Thus the prime-uniform target is immediate stabilization at the lower-bound slope `p`:

\[
D_k(C_p^3)=L_k \qquad(k\ge2).
\]

The right bridge is not a newly invented invariant. Fan--Gao--Wang--Zhong--Zhuang (Electron. J. Combin. 19(3) (2012), P31) define `C_0(G)` to be the exact lengths `t in [D(G)+1,eta(G)-1]` for which every zero-sum sequence of length exactly `t` contains a short zero-sum subsequence, i.e. one of length at most `exp(G)`.

For `G=C_p^3`, this means a zero-sum subsequence of length at most `p`.

## Exact-length peeling lemma

Use the standard zero-sum block characterization

\[
D_k(G)=\max\{|B|:B\text{ is zero-sum and }z(B)\le k\},
\]

where `z(B)` is the largest number of pairwise disjoint nonempty zero-sum subsequences.

Assume `D_k(G)=L_k` for some `k>=2`. Put

\[
t_k:=D_k(G)+p+1=L_k+p+1.
\]

If every zero-sum sequence of length exactly `t_k` contains a zero-sum subsequence `U` with `|U|<=p`, then

\[
D_{k+1}(G)=L_{k+1}.
\]

### Proof

Let `B` be zero-sum of length `t_k`. Remove such a short zero-sum `U`. Its complement `C=BU^{-1}` is zero-sum and has

\[
|C|\ge D_k(G)+1.
\]

Hence `z(C)>=k+1`; adjoining `U` gives `z(B)>=k+2`. Therefore no zero-sum sequence of length `D_k+p+1` has packing number at most `k+1`, and

\[
D_{k+1}(G)\le D_k(G)+p=L_{k+1}.
\]

Freeze--Schmid gives the reverse inequality.

If `t_k<eta(G)`, the short-forcing hypothesis is exactly `t_k in C_0(G)`. If `t_k>=eta(G)`, it follows automatically from the definition of `eta(G)` even without the zero-sum condition.

## What is needed for the whole tail

Starting from the exact `D_2`, the induction lengths are

\[
t_k=L_k+p+1=\frac{9p-5}{2}+(k-1)p+1,\qquad k=2,3,\ldots
\]

Thus the full lower-bound tail follows if every one of these exact lengths below `eta(G)` belongs to `C_0(G)`; once `t_k>=eta(G)`, all later peeling steps are automatic.

A stronger sufficient condition is an eventual zero-sum short threshold at or below the first induction length, but `C_0(G)` is an exact-length set and should not be treated as automatically upward closed.

This distinction matters: one exact statement such as `37 in C_0(C_7^3)` closes `D_3`, but does not by itself prove that `44 in C_0(C_7^3)`.

## Specialization to `p=7`

The first induction length is

\[
t_2=D_2(C_7^3)+7+1=37.
\]

Therefore

\[
37\in C_0(C_7^3)
\]

is exactly the short-zero statement needed to prove

\[
D_3(C_7^3)=36.
\]

The existing support-7 computation proves that any length-37 zero-sum short-free counterexample must have support at least eight.

If `D_3=36` is established, the next induction length is 44. To obtain the entire formula `D_k(C_7^3)=7k+15` by this route, one must continue checking the exact induction lengths below `eta(C_7^3)`; only after crossing `eta` does the tail become automatic.

## Negative control: `p=5`

The stronger prime-uniform threshold idea is false already at `p=5`. Fan--Gao--Wang--Zhong--Zhuang show that `C_0(C_5^3)` is confined to the top part of the short-zero interval (in particular, length 26 is not a `C_0` length), while the generalized Davenport formula for `C_5^3` nevertheless stabilizes at the lower bound from `k=2`.

So the `C_0` peeling route is a powerful sufficient mechanism, not a necessary universal explanation of the multiwise formula.

## Why this is still the right cross-scene object

The same exact-length hypothesis has several useful translations.

1. **Block monoid / factorization.** A zero-sum sequence is a block. Membership `t in C_0(G)` says every block of degree `t` has a nontrivial divisor of degree at most the exponent. Repeated low-degree divisibility gives multi-factor packing.
2. **Invariant theory.** For abelian groups the generalized Noether number satisfies `beta_k(G)=D_k(G)`. A short zero-sum divisor is a low-degree invariant monomial divisor, so the induction becomes a degree-divisibility statement.
3. **Affine semigroup / toric language.** For fixed support matrix `Q`, zero-sum multiplicity vectors are nonnegative integer solutions of congruences `Qx=0 mod p`; atoms are irreducible/Hilbert-basis elements. Peeling is conformal decomposition in this semigroup.
4. **Coding / projective geometry.** After projectivizing support, zero-sums are bounded positive kernel vectors of a diagonally scaled projective code. `C_0` asks whether every total-zero weight vector at the target degree contains a low-weight positive kernel vector.
5. **Hypergraph matching.** Term occurrences are vertices and zero-sum subsequences are hyperedges. `D_k` is a matching threshold; `C_0` supplies a bounded-size edge that can be peeled while retaining the induction surplus.

These translations are route-selection tools, not novelty claims.

## Boundary

- `37 in C_0(C_7^3)` remains the current exact short-zero target; this file does not prove it.
- No monotonicity of `C_0(G)` is assumed.
- The `p=5` negative control forbids promoting the strong eventual-threshold idea to a prime-uniform conjecture.
- This program concerns generalized/multiwise constants of `C_p^3`. Determining the classical Davenport constant for arbitrary finite abelian groups is a much broader problem and is not claimed here.
