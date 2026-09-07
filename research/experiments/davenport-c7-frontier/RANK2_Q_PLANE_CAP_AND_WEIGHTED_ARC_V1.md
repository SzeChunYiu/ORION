# Overshoot-dependent rank-two plane caps and weighted projective arcs — V1

Status: **proved first-failure reduction from exact rank-two restricted-sum theory, with independent arithmetic checks**. Donor structure remains donor-owned. No new generalized Davenport value is asserted here.

Let `p>=5` be prime, let

\[
G=C_p^3,
\qquad
M_p=\frac{5p-5}{2},
\]

and suppose the candidate line first fails at factorization level `m>=3` with overshoot `q>=1`:

\[
z(B)=m,
\qquad
|B|=N=pm+M_p+q.
\]

By `RESTRICTED_SUM_FIRST_FAILURE_AND_ETA_TAIL_V1.md`, `B` contains no nonempty zero-sum subsequence of length at most

\[
p+q-1.
\]

The new point here is to feed that stronger short-free window into every rank-two subgroup / projective plane.

## 1. Exact rank-two donor theorem

For `C_p^2`, the classical rank-two restricted-sum formula is

\[
s_{\le 2p-1-k}(C_p^2)=2p-1+k
\qquad(0\le k\le p-1).
\]

Set

\[
k=p-q.
\]

Then

\[
2p-1-k=p+q-1
\]

and therefore

\[
\boxed{s_{\le p+q-1}(C_p^2)=3p-q-1.}
\]

For prime `p`, Ebert--Grynkiewicz also determine the extremal structure for `2<=k<=p-2`: every sequence of length `2p-2+k` with no nonempty zero-sum of length at most `2p-1-k` has the form

\[
e_1^{p-1}e_2^{p-1}(e_1+e_2)^k
\]

for a basis `(e_1,e_2)`. In our first-failure range `q>=2`, one has `k=p-q in [2,p-2]`. The case `q=1` is the classical eta / Property-C endpoint.

Donor attribution: John Ebert and David J. Grynkiewicz, *Structure of a sequence with prescribed zero-sum subsequences: Rank two p-groups*, European Journal of Combinatorics 118 (2024), 103888, DOI `10.1016/j.ejc.2023.103888`, together with the earlier theorem giving the exact restricted-sum value.

## 2. q-dependent plane occupancy cap

Let `H<G` be any two-dimensional subgroup. The subsequence `B_H` formed by all term occurrences lying in `H` is also free of zero-sums of length at most `p+q-1`. Hence

\[
\boxed{|B_H|\le 3p-q-2.}
\]

This replaces the coarse eta cap `3p-3` by a cap that improves by exactly `q-1` occurrences.

For `q=1` this recovers the old plane cap. For `q>=2`, the inverse theorem also controls equality.

> **Saturated-plane grammar.** If `q>=2` and `|B_H|=3p-q-2`, then for some basis `(e_1,e_2)` of `H`,
>
> \[
> B_H=e_1^{p-1}e_2^{p-1}(e_1+e_2)^{p-q}.
> \]

Thus a saturated plane uses exactly three projective directions and exactly three actual support elements.

Consequently any plane containing at least four occupied projective directions satisfies the **strict rich-plane cap**

\[
\boxed{|B_H|\le3p-q-3.}
\]

This is the overshoot-dependent extension of the previous Property-C rich-plane improvement.

## 3. The canonical saturated-plane atom

The saturated-plane sequence contains

\[
A=e_1^q e_2^q (e_1+e_2)^{p-q}.
\]

Its length is

\[
|A|=p+q
\]

and its sum is zero. It is in fact an atom: if

`e_1^a e_2^b (e_1+e_2)^c`

is a nonempty zero-sum subsequence of `A`, then

\[
a+c\equiv b+c\equiv0\pmod p,
\]

with `0<=a,b<=q` and `0<=c<=p-q`; the only nonzero solution is

\[
a=b=q,\qquad c=p-q.
\]

Therefore equality in the plane cap produces a canonical atom of excess exactly `q`.

Inside a first failure, the complement `BA^{-1}` has length

\[
N-(p+q)=(m-1)p+M_p=D_{m-1}(G).
\]

Hence it has at least `m-1` zero-sum factors. Since `z(B)=m` and `A` is an atom, equality must hold and a maximum factorization of `B` can be chosen to contain this exact excess-`q` atom.

So a saturated plane is not merely a geometric shape: it is a forced factorization event.

## 4. Projective-direction deficits

Let the occupied projective directions of `B` be `P_1,...,P_r`. Let

\[
w_i=\text{number of term occurrences of }B\text{ on direction }P_i.
\]

Since `B` is `p`-short-free,

\[
1\le w_i\le p-1.
\]

Define the direction deficits

\[
d_i=(p-1)-w_i\ge0,
\qquad
\Delta=\sum_i d_i=r(p-1)-N.
\]

If a projective line contains `t>=3` occupied directions, its term occupancy is

\[
t(p-1)-\sum_{P_i\text{ on the line}}d_i.
\]

The q-dependent plane cap gives

\[
\boxed{
\sum_{P_i\text{ on the line}}d_i
\ge (t-3)(p-1)+(q-1).
}
\]

If `t>=4`, equality in the plane occupancy cap is forbidden by the saturated-plane grammar, so the strict version is

\[
\boxed{
\sum_{P_i\text{ on the line}}d_i
\ge (t-3)(p-1)+q.
}
\]

These are weighted secant inequalities for every first-failure support.

## 5. Full-multiplicity directions form an arc when q>=2

Suppose `q>=2`. A direction with `d_i=0` carries the full `p-1` occurrences.

Three full directions cannot be collinear: otherwise their plane would already contain

\[
3(p-1)=3p-3>3p-q-2
\]

term occurrences.

Thus the full-multiplicity directions form an arc in `PG(2,p)`. For odd prime `p`, an arc in `PG(2,p)` has at most `p+1` points. Since at most `Delta` directions can have positive deficit,

\[
r-\Delta\le p+1.
\]

Using `Delta=r(p-1)-N` gives the explicit direction lower bound

\[
\boxed{
r\ge
\left\lceil\frac{N-p-1}{p-2}\right\rceil
\qquad(q\ge2).
}
\]

It should be combined with the raw direction-capacity bound

\[
r\ge\left\lceil\frac{N}{p-1}\right\rceil.
\]

Hence

\[
\boxed{
r\ge
\max\left(
\left\lceil\frac{N}{p-1}\right\rceil,
\left\lceil\frac{N-p-1}{p-2}\right\rceil
\right)
\qquad(q\ge2).
}
\]

Donor input here is the classical Segre bound that an arc in `PG(2,p)`, `p` odd, has size at most `p+1`.

### Small-total-deficit strengthening

If

\[
\Delta<q-1,
\]

then **no three occupied directions at all** can be collinear, since every trisecant would require line-deficit at least `q-1`. Thus the entire direction support is an arc and

\[
\boxed{
\Delta<q-1\quad\Longrightarrow\quad r\le p+1.
}
\]

This gives a discrete extra bump beyond the closed-form full-direction bound in boundary cases.

## 6. Exact p=7 high-overshoot direction floor

At `p=7`, `M_7=15` and the restricted-sum front end already gives `q in {1,2,3}`.

For `q=2,3`, applying raw capacity, the full-direction arc bound, and the small-total-deficit strengthening gives the following necessary minimum number of projective directions:

| `q` | `m` | `N=7m+15+q` | old capacity floor | new direction floor |
|---:|---:|---:|---:|---:|
| 2 | 3 | 38 | 7 | 7 |
| 2 | 4 | 45 | 8 | 8 |
| 2 | 5 | 52 | 9 | 9 |
| 2 | 6 | 59 | 10 | **11** |
| 2 | 7 | 66 | 11 | **12** |
| 2 | 8 | 73 | 13 | 13 |
| 3 | 3 | 39 | 7 | 7 |
| 3 | 4 | 46 | 8 | 8 |
| 3 | 5 | 53 | 9 | **10** |
| 3 | 6 | 60 | 10 | **11** |

Thus four previously allowed high-overshoot slices require one additional projective direction before any scalar or kernel enumeration.

No whole `(m,q)` level is eliminated by this argument alone.

## 7. q-dependent coding side effect

The same plane cap gives a q-dependent minimum distance for the occurrence code:

\[
d\ge N-(3p-q-2).
\]

Combining this with the three-dimensional Griesmer bound yields a q-dependent global length cap. For `p>=11` the arithmetic equality case is

\[
N\le3p^2-pq-2p-q-2.
\]

At `p=7` the corresponding caps are

\[
q=1:123,\qquad q=2:115,\qquad q=3:114.
\]

These do **not** shrink the current first-failure `(m,q)` shell beyond the stronger excess inequality `(m-1)q<=M_p`; they are retained as coding controls rather than promoted as an additional signature reduction.

## 8. Strategic use

The first-failure geometry now has two exact plane modes.

1. **Saturated plane:** exactly three directions with multiplicities `(p-1,p-1,p-q)`, plus a canonical atom of length `p+q` and excess `q` that enters a maximum factorization.
2. **Non-saturated/rich plane:** at least one extra unit of plane deficit; four-direction planes obey the strict cap `3p-q-3`.

This turns a future plane-based augmentation proof into a dichotomy between a forced exact atom and a quantitatively stronger deficit.

## Boundary

- No new `D_3(C_7^3)` value is claimed.
- The exact rank-two restricted-sum value and inverse structure are donor-owned.
- The Segre arc bound is donor-owned.
- The p=7 direction floors are necessary conditions only; they do not prove realizability or non-realizability of the surviving slices.
