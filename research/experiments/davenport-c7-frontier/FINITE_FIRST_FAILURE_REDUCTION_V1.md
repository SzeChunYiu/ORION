# Finite first-failure reduction for the prime-uniform rank-three Davenport line — V1

Status: **proved analytic reduction with two independently structured finite checkers**. Donor inputs retain donor ownership. The formula `D_k(C_p^3)=((2k+5)p-5)/2` is not asserted here.

## 1. Standard asymptotic coordinates

Let `p>=5` be prime, `G=C_p^3`, and

\[
M_p=\frac{5p-5}{2}.
\]

The donor-derived exact value `D_2(G)=(9p-5)/2` says

\[
D_2(G)=2p+M_p,
\]

while the Freeze--Schmid lower line gives

\[
D_k(G)\ge kp+M_p\qquad(k\ge2).
\]

Freeze--Schmid use `D_0(G)` for the **eventual intercept** and `k_D(G)` for the least stabilization index:

\[
D_k(G)=D_0(G)+k\exp(G)\qquad(k\ge k_D(G)).
\]

This must not be conflated with the branch-local defect envelope

\[
\mathfrak d_p(G)=\max_k(D_k(G)-kp),
\]

which is the maximum pre-asymptotic intercept and can in principle exceed the eventual one.

For `C_p^3`, the proposed all-`k` formula is therefore equivalent to the standard pair of assertions

\[
\boxed{D_0(C_p^3)=M_p,\qquad k_D(C_p^3)=2.}
\]

Indeed, this pair is exactly the statement `D_k=kp+M_p` for every `k>=2`. Conversely the all-`k` formula has eventual intercept `M_p` and stabilizes at 2. It cannot stabilize at 1 because

\[
D_1(G)-p=2p-2<M_p.
\]

Equivalently, the formula is the branch-local statement `\mathfrak d_p(G)=M_p`.

Donor attribution: Michael Freeze and Wolfgang A. Schmid, *Remarks on a generalization of the Davenport constant*, Discrete Mathematics 310 (2010), 3373--3389, DOI `10.1016/j.disc.2010.07.028`, arXiv `0905.4248`.

## 2. Minimal-level counterexample lemma

Assume the target formula holds for levels `2,...,m-1`, with `m>=3`, and suppose level `m` is the first failure.

Choose a zero-sum block `B` with

\[
z(B)=m,
\qquad
|B|=pm+M_p+q,
\qquad q\ge1,
\]

and factor it with maximum length

\[
B=U_1\cdots U_m.
\]

Put

\[
e_i=|U_i|-p.
\]

Because `B` is a first-level counterexample, every proper subproduct of this maximum factorization has exactly the displayed number of factors: if a subproduct of `r<m` atoms refactored into more than `r` zero-sum blocks, replacing those atoms would produce more than `m` blocks in `B`.

In particular, removing `U_i` gives a block with packing number `m-1`, so the verified lower level gives

\[
|B|-|U_i|\le D_{m-1}(G)=(m-1)p+M_p.
\]

Since `|B|=mp+M_p+q`, this is exactly

\[
\boxed{e_i\ge q\quad(1\le i\le m).}
\]

Summing the excesses,

\[
\sum_i e_i=M_p+q,
\]

therefore yields

\[
(m-1)q\le M_p.
\]

Consequently every first failure satisfies

\[
\boxed{
3\le m\le M_p+1,
\qquad
1\le q\le\left\lfloor\frac{M_p}{m-1}\right\rfloor.
}
\]

This already turns the infinite stabilization problem into `O(p)` possible first levels.

### Slack normal form

Write

\[
e_i=q+f_i,
\qquad f_i\ge0.
\]

Then

\[
\boxed{\sum_i f_i=M_p-(m-1)q.}
\]

Thus the atomic signature of a first failure is a bounded integer partition of a small explicit slack. Since every atom in a `p`-short-zero-free core has length between `p+1` and `3p-2`, one also has

\[
0\le f_i\le 2p-2-q.
\]

The old pairwise condition `e_i+e_j<=M_p` follows automatically from this first-failure normal form: every omitted complement contains at least one excess `>=q`.

At the largest algebraically possible first level `m=M_p+1`, necessarily `q=1` and every atom has excess one, hence length exactly `p+1`.

## 3. A first failure is automatically `p`-short-zero-free

Suppose `A|B` is a nonempty zero-sum subsequence with `|A|<=p`. Its zero-sum complement has length

\[
|B|-|A|
\ge (m-1)p+M_p+q
> D_{m-1}(G).
\]

Hence the complement has at least `m` disjoint zero-sum blocks. Adjoining `A` gives at least `m+1` blocks in `B`, contradicting `z(B)=m`.

Therefore every first failure belongs to the same `p`-short-free finite geometry used elsewhere in this lane.

## 4. Coding-theoretic global length cap

Let `S` be any `p`-short-zero-free sequence over `C_p^3`.

Every two-dimensional subgroup contains at most

\[
\eta(C_p^2)-1=3p-3
\]

term occurrences. If `S` spans rank at most two, this immediately gives `|S|<=3p-3`.

Otherwise use the term occurrences of `S` as the columns of a rank-three `p`-ary generator matrix. The resulting linear code has length `N=|S|`, dimension 3, and minimum distance

\[
d\ge N-(3p-3),
\]

because a nonzero codeword vanishes exactly on the columns contained in one projective line / two-dimensional subgroup.

The Griesmer bound for a `p`-ary `[N,3,d]` linear code gives

\[
N\ge d+\left\lceil\frac d p\right\rceil
      +\left\lceil\frac d{p^2}\right\rceil.
\]

Substituting the smallest possible `d=N-(3p-3)` yields the exact cap obtainable from these two donor inputs:

\[
\boxed{
|S|\le L_p:=
\begin{cases}
62,&p=5,\\
3p^2-3p-3,&p\ge7.
\end{cases}}
\]

For `p>=7`, the forbidden next length `N=3p^2-3p-2` would have

\[
d\ge3p^2-6p+1,
\]

so the last two Griesmer terms are at least `3p-5` and `3`, whose sum exceeds the available `3p-3`. At `N=3p^2-3p-3` they are `3p-6` and `3`, so this argument is sharp at the arithmetic level. For `p=5`, `N=62` is the corresponding equality case.

Donor inputs here are the classical identity `eta(C_p^2)=3p-2` and the Griesmer bound. No novelty credit is assigned to either.

## 5. Finite level theorem

Combine Sections 2--4. A first failure must satisfy both

\[
m\le M_p+1
\]

and

\[
pm+M_p+1\le L_p.
\]

Therefore define

\[
K_p=
\min\left(M_p+1,
\left\lfloor\frac{L_p-M_p-1}{p}\right\rfloor\right).
\]

The expression simplifies to

\[
\boxed{
K_p=
\begin{cases}
10,&p=5,\\
15,&p=7,\\
(5p-3)/2,&p\ge11.
\end{cases}}
\]

> **Finite first-failure theorem.** To prove
>
> \[
> D_k(C_p^3)=\frac{(2k+5)p-5}{2}
> \qquad\text{for every }k\ge2,
> \]
>
> it is enough to prove it for the finite range
>
> \[
> 2\le k\le K_p.
> \]

If all these levels are correct and some larger level failed, choose the least failing `m`; Sections 2--4 would force `m<=K_p`, contradiction.

This does not solve those finitely many levels, but it removes the infinite-`k` dimension of the problem for every fixed prime.

## 6. Finite-geometry split at high factorization level

Let `r` be the number of occupied projective directions of a first-failure core. Direction capacity gives

\[
r\ge
\left\lceil
m+\frac52+\frac{m+q}{p-1}
\right\rceil.
\]

If no four occupied directions are collinear, they form an `(r,3)`-arc in `PG(2,p)`. The donor bound

\[
m_3(2,p)\le2p+1\qquad(p\ge5)
\]

then forces, already at `q>=1`,

\[
\boxed{m\le2p-4.}
\]

Hence every first failure with

\[
m\ge2p-3
\]

must contain a projective line carrying at least four occupied directions. In the `p=7` program this means any first failure at levels `11,...,15` is automatically in a four-secant / rich-plane branch, where the existing Property-C deficit upgrade applies.

The `m_3(2,p)<=2p+1` estimate is finite-geometry donor structure, commonly attributed to J. A. Thas (1975); later finite-geometry surveys and `(n,3)`-arc classifications record the same bound. Priority remains `CANNOT_CHECK`.

## 7. Exact finite signature receipts

`check_first_failure_reduction_v1.py` independently checks the symbolic inequalities for all primes through 401 and explicitly enumerates first-failure excess signatures for `p=5,7`.

`verify_first_failure_reduction_independent_v1.py` regenerates the same signatures by multiplicity-vector enumeration rather than ordered-partition recursion, and separately reconstructs the projective point-line incidences for `p=5,7,11`.

Both freeze the canonical digest

`37f152e4074a10edeedc14ea52207fb189bcc000dcb2901c4bb182defe91d68c`.

Before any geometry or short-sum filtering, the first-failure signature universes have exactly

- `71` signatures for `p=5`;
- `321` signatures for `p=7`.

For `p=7`, there are 29 admissible `(m,q)` pairs with `3<=m<=15`; the present length-37 frontier is only the `(m,q)=(3,1)` face.

## 8. What this changes strategically

The general program no longer needs to reason about arbitrary large `k` or arbitrary excess.

For a fixed prime, a counterexample can be chosen at its first failing level and then has simultaneously:

1. `3<=m<=K_p`;
2. `1<=q<=floor(M_p/(m-1))`;
3. first-failure excess normal form `e_i=q+f_i` with total slack `M_p-(m-1)q`;
4. `p`-short-zero-freeness;
5. total length at most `L_p` by coding theory;
6. support/projective deficit constraints from the existing complement lemma;
7. a mandatory rich plane whenever `m>=2p-3`;
8. Graver terminality at a maximum factorization.

The remaining theorem is now a **finite-level rank-three augmentation theorem** rather than an infinite stabilization problem.

## Boundary

- No `D_3(C_7^3)` value is claimed here.
- No all-prime formula is claimed here.
- The Griesmer, `eta(C_p^2)`, Freeze--Schmid eventual-line, and `(n,3)`-arc inputs are donor-owned.
- The branch-local defect envelope should not be renamed `D_0(G)`; the latter already has a standard eventual-intercept meaning in the donor literature.
