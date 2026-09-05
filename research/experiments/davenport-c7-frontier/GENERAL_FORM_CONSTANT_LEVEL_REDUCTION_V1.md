# General rank-three Davenport line: constant-level reductions — V1

Status: **proved donor-dependent reductions, not a proof of the target formula**. The new deductions are an explicit level cutoff independent of the prime and a seven-level cutoff for all sufficiently large primes, extending uniformly to every power of such a prime. No value of `D_3(C_7^3)` is established.

## 1. Target and established starting point

For a prime `p>=5`, put `G_p=C_p^3` and

\[
M_p=\frac{5(p-1)}2.
\]

The generalized formula under investigation is

\[
\mathcal P(p):\qquad D_k(G_p)=kp+M_p\quad\hbox{for every }k\ge2.
\]

The lower bound `D_k(G_p)>=kp+M_p` for `k>=2` is the Freeze--Schmid donor construction. Exactness at `k=2` is proved from Zhao's short-zero theorem in `D2_PRIME_POWER_COROLLARY_V1.md`. These inputs do not establish `mathcal P(p)`.

This note strengthens the finite-level reduction in `FINITE_FIRST_FAILURE_REDUCTION_V1.md` by inserting verified Erdős--Ginzburg--Ziv bounds into the existing interface in `RESTRICTED_SUM_FIRST_FAILURE_AND_ETA_TAIL_V1.md`. It does not replace the structural work required at the remaining levels.

## 2. Tail interface and conversion from the EGZ constant

Write `s(G)` for the length forcing a zero-sum subsequence of length exactly `exp(G)`, and `eta(G)` for the length forcing a nonempty zero-sum subsequence of length at most `exp(G)`.

For a group of exponent `p`,

\[
\eta(G)\le s(G)-p+1. \tag{1}
\]

Indeed, append `p-1` zeros to any sequence of length `s(G)-p+1`. A zero-sum subsequence of length `p` must contain an original term; deleting the appended zeros gives the required nonempty subsequence of length at most `p`.

Freeze--Schmid Proposition 3.1(3), with restricted length `p`, gives

\[
D_{k+1}(G_p)\le\max\{D_k(G_p)+p,\eta(G_p)-1\}. \tag{2}
\]

Consequently, if equality on the target line holds at a level `t>=2` and

\[
(t+1)p+M_p\ge\eta(G_p)-1, \tag{3}
\]

then equality holds at every level `k>=t`. This follows by induction from (2) and the established lower line. This is precisely the existing eta-tail interface, not a new recurrence. [Freeze--Schmid, Proposition 3.1](https://arxiv.org/html/0905.4248v2).

For any real upper bound `eta(G_p)<=E_p`, it is enough to prove the target through

\[
T_p(E_p)=\max\left\{2,\left\lceil\frac{E_p-1-M_p}{p}\right\rceil-1\right\}. \tag{4}
\]

## 3. Seven levels suffice for all sufficiently large primes

Zakharov's Theorem 1.2 and Proposition 1.3 state, for fixed dimension `d` and primes tending to infinity,

\[
s(\mathbb F_p^d)=w(\mathbb F_p^d)p+o(p),
\qquad
w(\mathbb F_p^d)\le\binom{2d-1}{d}+1.
\]

For `d=3`, these give `s(G_p)<=(11+o(1))p`. The source is the published version, *Convex geometry and the Erdős--Ginzburg--Ziv problem*, Discrete Analysis 2026:3, DOI `10.19086/da.165216`; the cited arXiv version is v6, revised 18 July 2026. [Zakharov, Theorem 1.2 and Proposition 1.3](https://arxiv.org/html/2002.09892v6).

> **Theorem.** There is an absolute threshold `P_0` such that, for every prime `p>=P_0`, the following are equivalent:
>
> 1. `mathcal P(p)` holds.
> 2. `D_k(G_p)=kp+M_p` for every `k` with `2<=k<=7`.
>
> Since `k=2` is already established, only the five levels `3,4,5,6,7` remain in this reduction.

### Proof

Choose `P_0>=11` so large that

\[
s(G_p)\le\frac{45}{4}p
\]

for every prime `p>=P_0`. Equation (1) yields

\[
\eta(G_p)-1\le\frac{41}{4}p.
\]

At `t=7`, the left side of the tail gate (3) is

\[
8p+M_p=\frac{21}{2}p-\frac52
\ge\frac{41}{4}p,
\]

because the difference is `p/4-5/2>=0` for `p>=11`. Hence exactness at level 7 propagates to every larger level. Together with the assumed levels 2 through 6, it proves `mathcal P(p)`. The reverse implication is immediate. QED.

Equivalently, for every prime `p>=P_0`, any first failure occurs at a level

\[
\boxed{3\le m\le7.} \tag{5}
\]

The threshold is **not numerically specified by this reduction**. We use the asymptotic donor non-effectively, through existence of `P_0`; no claim that its proof is inherently ineffective is made. In particular, this theorem does not assign `p=7`, or any other specified prime, to the large-prime regime.

### Prime-power extension, uniform in the exponent

> **Corollary.** After increasing `P_0` if necessary, for every prime `p>=P_0` and every integer `a>=1`, put `n=p^a`. Then
>
> \[
> D_k(C_n^3)=kn+\frac{5(n-1)}2\quad(k\ge2)
> \]
>
> holds if and only if it holds for `2<=k<=7`. The threshold on `p` is independent of `a`; the second level is already established in `D2_PRIME_POWER_COROLLARY_V1.md`.

First, increase `P_0>=83` until the donor bound gives `s(C_p^3)<=(89/8)p` for every prime `p>=P_0`. Since `p>=82`,

\[
\frac{89}{8}p\le\frac{45}{4}(p-1)+1.
\]

We use the elementary lifting inequality

\[
s(C_{uv}^3)\le u\bigl(s(C_v^3)-1\bigr)+s(C_u^3)
\qquad(u,v\ge2). \tag{PP1}
\]

To prove it, project `C_{uv}^3` onto `C_u^3`, whose kernel is isomorphic to `C_v^3`. From a sequence of the displayed length, successively extract `s(C_v^3)` disjoint subsequences of length `u` whose projected sums vanish. Before the last extraction, at least `s(C_u^3)` terms remain, so all extractions are legitimate. Their sums form a sequence in the kernel of length `s(C_v^3)`, from which exactly `v` have sum zero. The union of the corresponding disjoint subsequences has length `uv` and sum zero. This proves (PP1).

If both factors satisfy `s(C_u^3)<=C(u-1)+1` and `s(C_v^3)<=C(v-1)+1`, (PP1) yields `s(C_{uv}^3)<=C(uv-1)+1`. Induction with `C=45/4` therefore gives, simultaneously for every `a>=1`,

\[
s(C_n^3)\le\frac{45}{4}(n-1)+1,
\qquad
\eta(C_n^3)-1\le\frac{41}{4}(n-1). \tag{PP2}
\]

The second inequality follows from the zero-appending proof of (1), with `n` in place of `p`. At level 7, the tail gate is satisfied because

\[
8n+\frac{5(n-1)}2-\frac{41}{4}(n-1)
=\frac{n+31}{4}>0.
\]

The Freeze--Schmid lower construction gives `D_k(C_n^3)>=kn+5(n-1)/2` for every odd `n` and `k>=2` by its Theorem 4.1 with `s=3,t=1`. The same recurrence (2), with exponent `n`, now propagates equality at level 7 to the whole tail. This proves the corollary. The lifting concerns the short-zero bound; it does **not** assert that Davenport equality for `C_p^3` lifts to equality for `C_{p^a}^3`.

## 4. An explicit cutoff uniform over all primes

The Alon--Dubiner argument, with the rank-two starting value `c(2)=4`, gives

\[
s(G_p)\le Cp,
\qquad C=3072(\log_2 3+5)+4<20233.005
\]

for every prime `p`. Zakarczemny's Remark 3.5 records the corrected recurrence `c(r)=256r(log_2 r+5)c(r-1)+(r+1)`. The placement of the factor `r` matters; the earlier printed recurrence has a typo. [Zakarczemny, Remark 3.5](https://arxiv.org/html/1910.10984v1), [Alon--Dubiner, original paper](https://web.math.princeton.edu/~nalon/PDFS/centroid.pdf).

By (1), use `E_p=(C-1)p+1` in (4). For `p>=7`,

\[
\frac{E_p-1-M_p}{p}
=C-\frac72+\frac{5}{2p}
<20233.005-3.5+\frac5{14}
<20230.
\]

Therefore

\[
\boxed{T_p(E_p)\le20229\quad(p\ge7).} \tag{6}
\]

For `p=5`, the already cited donor value `eta(C_5^3)=33` gives `T_5=4` directly. Thus the generalized all-prime formula is equivalent to proving it for every prime `p>=5` and every level in the **fixed** range

\[
\boxed{2\le k\le20229.} \tag{7}
\]

This is a finite set of levels, not a finite set of group instances: primes still range without bound. The cutoff is a verified bound, not a claim of optimality.

Combining (6) with the existing algebraic and coding cutoffs yields the more useful per-prime range

\[
2\le k\le K_p,\qquad
K_5=4,\quad K_7=15,\quad
K_p=\min\left\{\frac{5p-3}{2},20229\right\}\quad(p\ge11).
\]

For `p>=P_0`, Section 3 further replaces `K_p` by 7. The coarser bound `eta(C_n^3)<=20369(n-1)+1` from Zakarczemny's Lemma 3.8 would instead give the uniform cutoff 20366; using the prime-specific estimate before its extension to composite exponents avoids that loss.

## 5. Failed inference: sharp second level does not force the whole line

The following shortcut is invalid without an additional theorem:

> The lower construction is sharp at `D_2`, so the eventual intercept and every later intercept equal `D_2-2p`.

A rank-three odd-prime example already refutes that general implication. Freeze--Schmid Remark 5.3(4) records

\[
D_2(C_3^3)=11,
\qquad D_0(C_3^3)=6,
\]

where `D_0` denotes the eventual intercept. The lower line in question specializes to `3k+5`, which is sharp at `k=2`; nevertheless its proposed intercept 5 differs from the actual eventual intercept 6. [Freeze--Schmid, Remark 5.3(4)](https://arxiv.org/html/0905.4248v2).

This example does not refute the target restricted to `p>=5`. It shows exactly why odd characteristic, rank three, and sharpness at level 2 are insufficient as an abstract proof. A claimed marginal monotonicity or concavity statement that would bridge this gap needs its own proof and applicable hypotheses. None is imported here.

The published Zakharov text also mentions `w(F_p^3)=9` for large primes, but explicitly omits the argument. That statement is **not a donor input in this note**. In particular, a further cutoff 5 based on that shortcut remains an unverified route; the theorem above uses only the fully stated Theorem 1.2 and Proposition 1.3.

## 6. What this advances

The earlier first-failure grammar allowed `O(p)` factorization levels. The explicit donor now gives a prime-independent constant, while the recent asymptotic donor reduces all sufficiently large primes to five unresolved levels after `D_2`. Neither reduction eliminates the exceptional local configurations or proves any remaining level.

The exact scope of the full open target remains

\[
D_0(C_p^3)=\frac{5(p-1)}2,
\qquad k_D(C_p^3)=2
\quad\hbox{for every prime }p\ge5.
\]

Those are the desired eventual intercept and stabilization index, not consequences already obtained from the new cutoffs.
