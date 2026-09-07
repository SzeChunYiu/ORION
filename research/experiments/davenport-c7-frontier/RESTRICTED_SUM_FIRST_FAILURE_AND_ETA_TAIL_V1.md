# Restricted-sum first-failure front end and eta-tail propagation — V2

Status: **proved analytic reduction with donor restricted-sum inputs and two independent arithmetic/signature checkers**. No new value of `D_k(C_p^3)` is asserted here.

Let `p>=5` be prime, `G=C_p^3`, and

\[
M_p=\frac{5p-5}{2}.
\]

The target line under investigation is

\[
D_k(G)=kp+M_p\qquad(k\ge2).
\]

As in `FINITE_FIRST_FAILURE_REDUCTION_V1.md`, suppose this line first fails at level `m>=3`, and choose a zero-sum block `B` with

\[
z(B)=m,\qquad |B|=pm+M_p+q,\qquad q\ge1.
\]

The integer `q` is the overshoot above the proposed line.

## 1. Overshoot-sensitive short-free lemma

> **Lemma.** `B` contains no nonempty zero-sum subsequence of length at most
>
> \[
> p+q-1.
> \]

### Proof

If `A|B` is zero-sum with `|A|<=p+q-1`, then its zero-sum complement has length

\[
|B|-|A|
\ge pm+M_p+q-(p+q-1)
=(m-1)p+M_p+1
=D_{m-1}(G)+1.
\]

Since level `m-1` is assumed exact, the complement has zero-sum packing number at least `m`. Adjoining `A` gives at least `m+1` disjoint nonempty zero-sums in `B`, contradicting `z(B)=m`.

Thus a first failure is not merely `p`-short-zero-free: the forbidden length grows exactly with its overshoot.

## 2. General restricted-sum interface

Write `s_{<=h}(G)` for the least length forcing a nonempty zero-sum subsequence of length at most `h`.

The lemma gives the following plug-in rule.

> **Restricted-sum killer.** If a donor theorem supplies
>
> \[
> s_{\le h}(G)\le S,
> \]
>
> and a proposed first-failure pair `(m,q)` satisfies
>
> \[
> h\le p+q-1,
> \qquad
> pm+M_p+q\ge S,
> \]
>
> then that pair is impossible.

This is the front-end interface between the multiwise Davenport problem and the restricted-sum invariant. Better values of `s_{<=h}(C_p^3)` can be inserted without changing the rest of the argument.

## 3. Prime-uniform overshoot cap

Zhao's 2025 paper recalls the Bhowmik--Schlage-Puchta bound

\[
s_{\le(3p-1)/2}(C_p^3)\le6p-3.
\]

If `q>=(p+1)/2`, then

\[
p+q-1\ge\frac{3p-1}{2}.
\]

Moreover, since `m>=3`,

\[
|B|
\ge3p+M_p+\frac{p+1}{2}
=6p-2
>6p-3.
\]

The restricted-sum killer gives a contradiction. Therefore every first failure satisfies the **prime-uniform overshoot bound**

\[
\boxed{1\le q\le\frac{p-1}{2}.}
\]

This strictly improves the purely algebraic bound `q<=floor(M_p/(m-1))` whenever the latter is larger.

Donor attribution: Kevin Zhao, *On zero-sum subsequences in a finite abelian group of length not exceeding a given number*, arXiv:2506.21383 (2025), Lemma 1.6 citing G. Bhowmik and J.-C. Schlage-Puchta.

## 4. Prime-uniform short-atom insertion

Zhang's rank-three theorem, restated as Zhao Lemma 1.7(v), gives for odd prime `p`

\[
\boxed{s_{\le2p-2}(C_p^3)=4p-2.}
\]

Every first failure has

\[
|B|\ge3p+M_p+1=\frac{11p-3}{2}>4p-2,
\]

so `B` contains a nonempty zero-sum subsequence of length at most `2p-2`. Because `B` is `p`-short-free, this subsequence contains an atom `U` satisfying

\[
p+1\le|U|\le2p-2.
\]

We may insert `U` into a maximum factorization of `B`. For `m>=4`, the complement after deleting `U` has length strictly larger than `D_{m-2}`; for `m=3` it is strictly larger than `D_1=3p-2`. Hence the complement has enough zero-sum factors that a maximum factorization can be chosen to contain such a short atom.

Writing its excess as `e=|U|-p`, every first failure therefore has a maximum factorization with

\[
\boxed{1\le\min_i e_i\le p-2.}
\]

This is the prime-uniform version of the existing `p=7` short-atom pruning `min e_i<=5`.

Donor attribution: Shiwen Zhang, *On some zero-sum invariants for abelian groups of rank three*, Publicationes Mathematicae Debrecen 106 (2025), 225--240, DOI `10.5486/PMD.2025.9991`; Zhao 2025, Lemma 1.7(v).

## 5. Freeze--Schmid recurrence as an eta-tail gate

Freeze--Schmid Proposition 3.1(3) states that for every positive integer `ell`,

\[
D_{k+1}(G)\le
\max\{D_k(G)+\ell,\ s_{\le\ell}(G)-1\}.
\]

Taking `ell=p` gives the useful special case

\[
D_k(G)\ge\eta(G)-1-p
\quad\Longrightarrow\quad
D_{k+1}(G)\le D_k(G)+p.
\]

Suppose the target line is verified at some level `t>=2` and

\[
tp+M_p\ge\eta(C_p^3)-1-p.
\]

The Freeze--Schmid upper bound and the known lower line then give

\[
D_{t+1}(C_p^3)=(t+1)p+M_p.
\]

The inequality remains true at the next level, so induction propagates equality for every `k>=t`.

Thus **one exact level at or beyond the eta threshold determines the entire tail**.

If only an upper bound

\[
\eta(C_p^3)\le E_p
\]

is known, define the recurrence threshold

\[
\boxed{
T_p(E_p)=
\max\left(2,
\left\lceil\frac{E_p-1-M_p}{p}\right\rceil-1
\right).
}
\]

If the target is verified through level `T_p(E_p)`, the recurrence propagates it to every larger level. Independently, the first-failure excess grammar gives `m<=M_p+1`. Hence the combined finite verification range is

\[
\boxed{2\le k\le\min\{M_p+1,T_p(E_p)\}.}
\]

For the Griesmer short-free cap `L_p` from `FINITE_FIRST_FAILURE_REDUCTION_V1.md`, taking `E_p=L_p+1` makes the **coding cutoff** exactly `T_p(E_p)`. Numerically,

\[
T_5=10,\qquad T_7=15,\qquad T_p=3p-6\quad(p\ge11).
\]

For `p>=11`, the independent algebraic bound `M_p+1=(5p-3)/2` is smaller than `3p-6`, so the final first-failure cap remains `(5p-3)/2`. This distinction was exposed by CI and is the reason for this V2 correction.

## 6. The solved p=5 control

For `C_5^3`, the donor value

\[
\eta(C_5^3)=33
\]

gives

\[
T_5(33)=4.
\]

Therefore exactness of the lower line at levels 2, 3 and 4 is enough to force the whole tail. The sibling ORION-04 proof package records `D_3(C_5^3)=25` and `D_4(C_5^3)=30`; together with `D_2=20`, the recurrence therefore yields

\[
D_k(C_5^3)=5k+10\qquad(k\ge2).
\]

This is used here only as a control showing that the front-end/tail architecture closes a full prime when the short-sum threshold and the first few levels are available.

## 7. What the eta conjecture would do -- not used as a theorem

For general odd primes, the precise value of `eta(C_p^3)` is not known. The classical lower construction gives

\[
\eta(C_p^3)\ge8p-7,
\]

and `eta(C_p^3)=8p-7` is the expected rank-three value in the relevant conjectural picture. This conjecture is **not used** anywhere in the verified reductions.

If an upper bound `eta(C_p^3)<=8p-7` were eventually proved, then `T_p(8p-7)` would reduce the all-`k` problem to only the first few levels, rather than `O(p)` levels. This quantifies exactly why the rank-three short-zero problem is structurally coupled to immediate multiwise stabilization.

## 8. Exact p=7 signature refinement

The coding-refined first-failure universe at `p=7` contains 321 raw excess signatures.

The new uniform overshoot cap `q<=3` removes 21, leaving

\[
\boxed{300}
\]

raw signatures. The prime-uniform short-atom rule `min e_i<=5` removes one further signature not already removed by the q-cap, leaving 299. Finally the established six `(m,q)=(3,1)` atom corridors remove 13 more.

The current donor-pruned `p=7` first-failure cover therefore has exactly

\[
\boxed{286}
\]

excess signatures.

Two differently structured checkers freeze the same canonical list with SHA-256

`2b49f2b6f4579a27165ebe5285292a5966901f1af7793a5cf73f3e9c8d47be19`.

The reduction is purely at the atom-length/excess level; it does not assert that any of the 286 signatures has a vector realization.

## 9. General formalism after this reduction

For a fixed prime `p>=5`, a first counterexample to

\[
D_k(C_p^3)=kp+M_p
\]

must now satisfy simultaneously:

1. a finite factorization level `3<=m<=min(M_p+1,T_p(E_p))` for any verified eta upper bound `E_p`;
2. overshoot `1<=q<=(p-1)/2`;
3. excess normal form `e_i=q+f_i` with `sum f_i=M_p-(m-1)q`;
4. a maximum factorization containing an atom with excess at most `p-2`;
5. no zero-sum subsequence of length at most `p+q-1`;
6. support, projective-direction, plane-deficit and coding constraints from the existing geometry reductions;
7. terminality under every positive-gain conformal Graver move.

The all-`k` question has therefore split cleanly into two modules:

- a **restricted-sum front end** that bounds `(m,q)` and forces short atoms;
- a **finite rank-three augmentation core** that must eliminate the remaining positive-kernel signatures.

This is the current general mechanism. The missing theorem is the second module, not eventual linearity itself.

## Boundary

- No new exact value for `D_3(C_7^3)` is claimed.
- No general exact value of `eta(C_p^3)` is assumed for `p>=7`.
- The Bhowmik--Schlage-Puchta, Zhang, Zhao and Freeze--Schmid inputs are donor-owned.
- The 286-count is an exact length-signature cover only; geometry and scalar/kernel realizability remain to be imposed.
