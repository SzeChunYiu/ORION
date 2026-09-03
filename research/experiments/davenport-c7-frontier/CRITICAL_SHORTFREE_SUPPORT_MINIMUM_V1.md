# Minimum support at the prime-uniform `D_3` critical length — V1

Status: **elementary derived theorem plus donor sharpness witness**. No novelty/priority claim.

Let `p>=5` be prime, `G=C_p^3`, and put

\[
N_p=\frac{11p-3}{2}.
\]

Consider a zero-sum sequence `B` over `G` of length `N_p` with no nonempty zero-sum subsequence of length at most `p`.

Then

\[
|supp(B)|\ge7.
\]

Moreover the bound is sharp for every `p>=5`: the Fan critical family in `FAN_CRITICAL_FAMILY_FOUR_PACK_V1.md` has support exactly seven.

## Proof of the lower bound

Short-freeness implies every element multiplicity is at most `p-1`, because `p` equal terms sum to zero.

For `p=5`,

\[
N_p=26>6(p-1)=24,
\]

and for `p=7`,

\[
N_p=37>6(p-1)=36.
\]

Hence support at least seven follows immediately in these two cases.

Now let `p>=11`. Capacity gives support at least six. Suppose for contradiction that support is exactly six, with distinct actual support values `g_1,...,g_6` and multiplicities `m_i`.

Write

\[
m_i=p-1-d_i,\qquad d_i\ge0.
\]

The total deficit is

\[
\Delta=6(p-1)-N_p=\frac{p-9}{2}.
\]

Thus every `d_i<=Delta`. Define complementary counts

\[
w_i=d_i+1=p-m_i.
\]

Since `d_i<=Delta`,

\[
w_i\le\frac{p-7}{2}<m_i,
\]

so `W=\prod_i g_i^{w_i}` is a genuine nonempty subsequence of `B`.

Because `B` is zero-sum and `p g_i=0`,

\[
\sigma(W)=\sum_i(p-m_i)g_i=-\sum_i m_i g_i=0.
\]

Its length is

\[
|W|=6p-|B|=\frac{p+3}{2}\le p.
\]

This is a short zero-sum subsequence of `B`, contradiction.

Therefore support six is impossible and support at least seven holds for all primes `p>=5`.

## Complement-multiplicity principle

The proof isolates a reusable device. Suppose a zero-sum sequence has support `g_1,...,g_s`, each multiplicity strictly below `p`, and define the `p`-complement sequence

\[
B^c=\prod_i g_i^{p-m_i}.
\]

Then `B^c` is automatically zero-sum because `sigma(B^c)=-sigma(B)` in an exponent-`p` group. If `B^c|B` and `|B^c|<=p`, short-freeness fails.

At the critical `D_3` length and support six, both inequalities are forced just by the deficit budget. This is why support seven is the first genuinely nontrivial geometry for every prime `p>=5`.

## Relevance to multiwise Davenport

The donor exact value

\[
D_2(C_p^3)=\frac{9p-5}{2}
\]

implies that any zero-sum sequence of length `N_p` with packing number at most three is `p`-short-free: removing a zero-sum block of length at most `p` leaves at least `D_2+1` terms, which contain three further disjoint zero-sums.

Consequently any obstruction to

\[
D_3(C_p^3)=\frac{11p-5}{2}
\]

must have support at least seven.

The Fan family shows that support-seven short-free critical sequences genuinely exist; the problem is therefore not to eliminate support seven by short-zero arguments, but to prove a four-factor zero-sum decomposition there and then control larger supports.
