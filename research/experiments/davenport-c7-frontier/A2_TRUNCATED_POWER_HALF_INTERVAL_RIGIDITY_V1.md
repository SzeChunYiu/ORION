# Type two: bounded-hole rigidity for an unsaturated new value

Status: **proved prime-uniform coordinate rigidity with an explicit prime threshold**. The high value needs only `p-b` occurrences. This directly addresses the missing-index obstruction in the saturated donor argument and uses no Bernoulli inverse theorem.

## 1. Actual donor and statement

Let `p=2H+1>=7` be prime, `m=3H+1`, `u=H+1=2^{-1}` in `F_p`, and `s=(u,u,1)` in a basis `(e1,e2,g)` of `C_p^3`. Let

\[
B_K=e_1^{p-1}e_2^{p-1}g^{p-1}s^K,
\qquad K\ge2,
\qquad 1\le b\le H-1.
\]

Assume `B_K y^{p-b}` contains no nonempty zero-sum of length below `m`, and write `y=(A,B,C)`.

**Theorem.** Every coordinate `A,B,C` is nonzero. Moreover, with

\[
I=\{1,\ldots,H\},\qquad
J=\{j\in\mathbb F_p^*:[jA]_p\in I,\ [jB]_p\in I\},
\]

one has

\[
\boxed{|J|\le b.}
\tag{1}
\]

Consequently,

\[
\boxed{p>(2b+1)^2+1\quad\Longrightarrow\quad A+B=0.}
\tag{2}
\]

Below that sufficient threshold, the centered representatives of `-B/A` and `-A/B` still have magnitude at most `2b+1`. Neither an exceptional-prime classification nor companion realizability is asserted there.

## 2. The complementary core excludes a zero coordinate

The indices

\[
\mathcal C=\{b,b+1,\ldots,p-b\}
\]

and their complements `p-j` all lie in the actually available power range `1,...,p-b`. Its size is `p-2b+1>=4`.

If `q` coordinates of `y` are nonzero, the saturated basis completion has length

\[
L_j=j+[-jA]_p+[-jB]_p+[-jC]_p,
\qquad L_j+L_{p-j}=(q+1)p.
\tag{3}
\]

The zero vector is already forbidden. If `q=1`, (3) contradicts `L_j,L_{p-j}>=m>p`. If `q=2`, then `3p=2m+1` forces every core length into the two integers `{m,m+1}`.

Put `T=1-A-B-C`. When `T!=0`, the congruence `L_j==jT (mod p)` makes all core lengths distinct, impossible for at least four indices and two integers. When `T=0`, every `L_j` is a multiple of `p`, but neither `m` nor `m+1` is such a multiple: `p<m<=m+1<2p`. Thus `q=2` is impossible as well. Hence `ABC!=0` and the complementary total in (3) is `4p`.

## 3. A low-half intersection gives two actual donor substitutions

Take `j in J intersection C`, and write

`a=[-jA]_p`, `d=[-jB]_p`, `w=[-jC]_p`.

The definition of `J` gives `a,d>=u`. Also `1<=w<=p-1`.

First, one copy of `s` can replace `u` copies of each axis and one copy of `g` in the saturated completion. The resulting zero-sum is available and has length

\[
L_j-(p+1).
\tag{4}
\]

Indeed, the remaining counts are `a-u,d-u,w-1`, all nonnegative; the replaced basis block has `2u+1=p+2` terms and the substitute has one term.

Second, if `w<=p-2`, the complementary index `p-j` has positive axis counts and a `g` count `p-w>=2`. Two available copies of `s`, whose sum is `e1+e2+2g`, shorten that completion by two. Thus short-freeness gives

\[
L_{p-j}-2\ge m,
\qquad L_j\le4p-m-2.
\]

Equation (4) would then have length at most

\[
4p-m-2-(p+1)=3p-m-3=m-2,
\]

a contradiction. Therefore every `j in J intersection C` must have `w=p-1`, equivalently `jC=1`. There is at most one such index.

These two certificates are tested separately. They need not be disjoint; each individually uses at most the two available copies of `s` and the saturated basis capacities.

## 4. Exactly b holes suffice

Outside the core, the possible indices form the `b-1` antipodal pairs

\[
\{1,-1\},\ldots,\{b-1,-(b-1)\}.
\]

The set `J` contains at most one element of any antipodal pair, since a nonzero residue and its negative cannot both lie in `I`. Thus at most `b-1` members of `J` lie outside the core, and Section 3 permits at most one inside it. This proves (1).

Apply `MULTIPLICATIVE_HALF_INTERVAL_STABILITY_V1.md` with `alpha=A,beta=B`. It gives the two centered bounds and then (2), with the strict threshold and the possible negative multiplier checked there.

## 5. Consequence for the live unsaturated rank-three family

For the standing companion

\[
V=s^c g x^{H+b-1-c}y^{p-b},
\qquad 2\le b\le c+1,
\]

the actual shared donor is exactly `B_{c+2}`. Therefore, whenever `b<=H-1` and `p>(2b+1)^2+1`, short-freeness forces the high value into the coordinate plane

\[
\boxed{y=(A,-A,C),\qquad AC\ne0.}
\]

In particular, this holds on the entire first unsaturated face `b=2` for every prime `p>=29`, for every permitted shared multiplicity `c`. This is a new inverse implication, not a claim that every companion in that plane survives or that the face is already empty.

The argument never applies a theorem for `y^{p-1}` to `y^{p-b}`. All complementary indices used above are in the displayed core. The missing indices are counted explicitly, including the single substitution seam. The written proof was checked locally; no independently tasked or external referee review is claimed.
