# Type two: a generalized coordinate-sum-two mixed selector

Status: **proved prime-uniform selector theorem**. The complement-interval mechanism extends from one new occurrence on `b=2` to any available group of new and light occurrences whose coordinate sum is two. This gives an explicit general interface for deeper unsaturated faces.

## 1. Standing main inverse family

Use `p=2H+1>=7`, `m=3H+1`, `u=H+1`, `s=(u,u,1)`, and

\[
U=e_1^{p-1}e_2^{p-1}g^{p-2}s^2,
\qquad V=s^c g x^r y^{p-b},
\qquad r=H+b-1-c>0.
\]

Assume `sigma(V)=0` and that the high value has the main inverse form

\[
y=(A,-A,1),\qquad A\ne0.
\tag{1}
\]

This is an explicit hypothesis here. It has already been proved for all `b=2` nonexceptional rows; for `b>=3`, the bounded-hole and half-power theorems supply it under `p>=10b`, `2<=c<=H-1`, with the inverse exceptions checked separately. It is not assumed below the available inverse threshold.

The relation is

\[
rx=by-cs-g.
\tag{2}
\]

## 2. Exact selector conditions

Choose ordinary integers `i,z` and let `lambda=i/r` in `F_p`. Suppose

\[
1\le i\le r,\qquad0\le z\le c+2,
\qquad i+z\le H+1,
\tag{3}
\]

\[
2z+(b-2c-1)\lambda=2\quad\text{in }\mathbb F_p,
\tag{4}
\]

and, with

\[
C_0=z+(b-c-1)\lambda,
\qquad q=[-C_0]_p,
\]

one has

\[
1\le q\le\min(p-3,p-b),
\qquad(3b+1)\lambda\ne2\quad\text{in }\mathbb F_p.
\tag{5}
\]

**Theorem.** Every row admitting such integers has a nonempty zero-sum subsequence of `UV` shorter than `m`.

## 3. Proof by an actual occurrence group

Let `X` denote the group sum of the available occurrence sequence `x^i s^z`; it is used as one vector only for the argument, then expanded back into those actual occurrences. Multiplying (2) by `lambda` gives

\[
X=b\lambda y+(z-c\lambda)s-\lambda g.
\tag{6}
\]

Its third coordinate is `C0`, and (4) says exactly that the sum of its three coordinates is two. By (5), put `M=p-2-q>=1`. The complement-interval theorem therefore gives an occurrence-valid zero-sum

\[
\boxed{x^i s^z y^j g^{q-j}e_1^P e_2^{M-P},
\qquad0\le j\le q,\quad0\le P\le M,}
\tag{7}
\]

unless `A=1,X1=1` or `A=-1,X2=1`.

All capacities in (7) are actual. Conditions (3) provide its `x,s` occurrences; `j<=q<=p-b` fits the new value; `q-j<=p-3` fits the saturated shared `g` donor; and the two axis counts are at most `M<p`. Its total length is

\[
i+z+q+M=i+z+p-2\le p+H-1=m-1.
\tag{8}
\]

It is nonempty because `i>=1`.

To exclude the two possible failures, solve (4) for `z-c lambda`:

\[
z-c\lambda=1+(1-b)\lambda/2.
\]

At `A=1`, the first coordinate of (6) is

\[
X_1=\frac12+\frac{3b+1}{4}\lambda.
\]

It equals one only when `(3b+1)lambda=2`, forbidden by (5). At `A=-1`, the identical formula applies to the second coordinate. Thus neither failure is possible, proving the theorem.

## 4. Ordinary length and third-coordinate identities

The selector equation has two useful consequences in the field:

\[
\boxed{i+z=1+(b-2)\lambda/2,\qquad
C_0=1+(b-1)\lambda/2.}
\tag{9}
\]

They follow from `2r==2b-3-2c` and (4). The first is only a congruence until the ordinary length bound (3) is verified. It must not be used to divide or manufacture occurrences.

At `b=2`, choosing `i=1,z=0` satisfies the coordinate-sum equation automatically; this is the all-prime first-face argument. At `b=3`, if the actual packet length is `n+1` with `1<=n<=H-1`, then (9) makes `lambda=2n` as its least positive even representative. One can search for a proof of existence through the ordinary division identities

\[
i=hp-(2c-3)n,\qquad
z=(2c-2)n-hp+1,
\tag{10}
\]

for an integer `h`. These imply `i+z=n+1`; the capacity inequalities in (3) and the nonexceptional condition in (5) still have to be proved. Formula (10) is a symbolic selector interface, not an assertion that a suitable division always exists.

## 5. Exact limitation

This theorem generalizes the proved mixed mechanism to every unsaturated deficit `b`, but it is a sufficient criterion. The inverse form (1), an actual solution of (3)--(5), and the absence of the exceptional equality must each be established before using it. Consequently it does not itself close all `b>=3`, the first corridor, or the generalized Davenport formula.

The proof was checked locally for the expanded occurrence capacities, both coordinate identities, the ordinary length bound, and both exceptional progression steps. No enumeration or separate external referee claim is involved.
