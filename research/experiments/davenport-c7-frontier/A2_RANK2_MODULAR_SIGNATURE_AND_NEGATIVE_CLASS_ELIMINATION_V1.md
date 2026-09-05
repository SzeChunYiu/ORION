# Type two: modular atom signatures and an infinite family of empty layers — V1

Status: **proved prime-uniform two-budget normal form and whole-layer congruence elimination**. The negative congruence class is excluded for arbitrary overlap defect, without a square-root restriction. A second integer budget describes all atomizations in the additional range `d^2<p`.

## 1. Common setup

Use the rank-two canonical type-two hypotheses of `A2_RANK2_EXACT_QUOTIENT_DEFECT_BUDGET_V1.md`, and put

\[
p=2H+1,\quad 1\le c<H,\quad
d=H-c,\quad a=d+1,\quad R=x^r y^t.
\]

Then `|R|=p+a-1`, every quotient atom has an integer defect `D` in `[1,a-1]`, and

\[
\ell_D=[(a-1)Da^{-1}]_p,\qquad
\ell_D+D\equiv0\pmod2,
\qquad \sum_iD_i=a.
\tag{1}
\]

The projected values are distinct and nonzero. Every quotient atom is proper, since `|R|>p`.

## 2. A second positive integer budget

Assume additionally `(a-1)^2=d^2<p`. For a quotient atom of length `ell` and defect `D`, define

\[
h=\frac{a\ell-(a-1)D}{p}.
\tag{2}
\]

This is an integer by (1). Its numerator exceeds `-(a-1)^2>-p`, so `h>=0`. Equality would give `a ell=(a-1)D`, forcing `a|D`, impossible for `1<=D<=a-1`. Also `ell<=p-1`, so the numerator is strictly below `ap`. Hence

\[
1\le h\le a-1.
\]

The parity condition in (1) is equivalent to

\[
hp-D=a(\ell-D)\equiv0\pmod{2a}.
\]

Finally, summing (2) over any atomization and using its total length and exact defect budget gives

\[
\boxed{
\begin{gathered}
1\le D_i,h_i\le a-1,\qquad
h_i p\equiv D_i\pmod{2a},\\
\sum_iD_i=\sum_i h_i=a,\\
\ell_i=\frac{h_i p+(a-1)D_i}{a}.
\end{gathered}}
\tag{3}
\]

Thus every atomization is a pair of positive partitions of the same integer `a`, linked by the single multiplier `p` modulo `2a`. For fixed overlap defect, the allowed signature pairs depend only on this residue class of the prime. Actual atom counts and capacities remain governed by the exact count formula; not every formal signature is asserted to occur.

The condition `d^2<p` was used only to establish positivity of this second weight. It is not a condition of the original defect budget.

## 3. The negative congruence class is empty without that restriction

Suppose now, without assuming `d^2<p`, that

\[
\boxed{p\equiv-1\pmod{2a}.}
\tag{4}
\]

Write `p=2aL-1`. Then `a^{-1}=2L` modulo `p`, and for every candidate defect `1<=D<=a-1`,

\[
\ell_D=[(a-1)D\cdot2L]_p
=[-(2L-1)D]_p.
\]

The ordinary integer `(2L-1)D` lies strictly between zero and `p`: its largest possible value is `(2L-1)(a-1)<2aL-1`. Therefore

\[
\ell_D=p-(2L-1)D,
\qquad \ell_D+D=p-2(L-1)D.
\]

The last integer is odd, contradicting (1). No quotient atom can exist, although the nonempty zero-sum quotient must have an atomization. This proves:

> **Negative-class whole-layer theorem.** For every prime `p>=7` and every positive overlap `c<H`, the rank-two type-two layer is empty whenever
>
> \[
> \boxed{2(H-c+1)\mid(p+1).}
> \tag{5}

Equivalently, for arbitrary integers `a>=2,L>=2` with prime `p=2aL-1`, the complete overlap layer

\[
c=a(L-1),\qquad H=aL-1,
\]

is empty, independently of both new multiplicities. The bound `L>=2` is equivalent here to positive overlap.

This is an infinite structural family, not a list of verified primes. It includes the excluded residue classes used in the `H-1`, `H-2`, and `H-3` layer arguments, and applies to arbitrarily large defects as well.

## 4. Audit and preserved limitations

The review checked integrality and positivity separately in (2), the factor `2a` in the parity condition, both summed budgets, and the direct least-residue computation in Section 3. The direct proof of (5) deliberately does not infer positivity of `h` outside its proved range.

The two-budget signature is a necessary structural normal form, not a sufficient realization criterion or a universal elimination. For general residue classes, the partition constraints still allow several atom types, and their mixed occurrence geometry remains to be controlled. No full first-corridor, `D_3(C_7^3)`, or generalized Davenport equality is asserted. Internal review is by the producing researcher, without an independent referee or novelty claim.
