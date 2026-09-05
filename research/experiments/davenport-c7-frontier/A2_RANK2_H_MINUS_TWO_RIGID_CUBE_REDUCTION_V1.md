# Type two: the c=H-2 layer forces one rigid cubic endpoint — V1

Status: **proved prime-uniform elimination of all unsaturated new-multiplicity rows in the complete layer `c=H-2`**, together with an exact prime-congruence reduction of its saturated endpoint. The remaining endpoint is identified, not claimed to be eliminated.

## 1. Setup and theorem

Let `p=2H+1>=7` be prime, `m=3H+1`, and

\[
U=e_1^{p-1}e_2^{p-1}g^{p-2}s^2,
\qquad e_1+e_2=2(s-g),
\]

where `(e_1,e_2,g)` is a basis. Suppose

\[
V=s^{H-2}x^r y^t,\qquad r+t=p+2,
\qquad 1\le r,t\le p-1
\]

has rank two and distinct new values, and `UV` has no nonempty zero-sum shorter than `m`.

> **Rigid cubic endpoint theorem.** Necessarily, after swapping the new values,
>
> \[
> \boxed{p=12L+1,\qquad
> V=s^{6L-2}x^3y^{p-1}.}
> \tag{1}
>
> The known four-share elimination excludes `L=1`; hence any remaining row has prime `p>=37`.

In particular, every row in this layer with both `r,t<=p-2` is impossible, for every prime `p>=7`.

## 2. The defect alphabet has only two elements

Project the support plane modulo `<s>` and put `R=x^r y^t`. In `A2_RANK2_EXACT_QUOTIENT_DEFECT_BUDGET_V1.md`, this is `d=2`. Every quotient atom has defect `D` in `{1,2}`, and every factorization satisfies

\[
\sum_i D_i=3.
\tag{2}
\]

Thus its defect pattern is either `1+2` or `1+1+1`. In particular, there is always an atom with defect one. The atom of defect `D` has the unique possible length

\[
\ell_D=[2D\cdot3^{-1}]_p.
\tag{3}
\]

These statements use all proper projected-zero parts, not a choice of a preferred factorization.

## 3. Primes p congruent to two modulo three are impossible

Write `p=3u+2`. Equation (3) gives

\[
\ell_1=2u+2.
\]

But defect one means `2q=ell_1+1`, whose right side is odd. This is impossible. There can be no factorization of the required kind, contradicting (2).

This argument eliminates the entire prime class without a cyclic inverse theorem or a search.

## 4. The other prime class forces a rigid cube

Write `p=3u+1`; since `p>=7`, `u>=2`. Then

\[
\ell_1=u+1,\qquad \ell_2=2u+2=2\ell_1<p.
\tag{4}
\]

Choose an existing defect-one atom `P=bar(x)^A bar(y)^B`. The count formulas in the exact-budget theorem say that a defect-two atom would have counts

\[
[2A]_p,\qquad [2B]_p.
\]

As `A+B=ell_1` and `2ell_1<p`, both counts are simply `2A,2B`. Such a sequence is `P^2`, so it is not an atom. Thus no defect-two atom can divide `pi(R)`.

All defect-one atoms have the same occurrence multiplicities, again by the count formulas. Atomizing `pi(R)` now yields

\[
\boxed{\pi(R)=P^3,\qquad
P\text{ is its only atomic divisor}.}
\tag{5}
\]

This proves rigidity; it is not inferred merely from the existence of a cubic factorization.

## 5. The cube and parity determine the endpoint

Apply `CYCLIC_TWO_VALUE_RIGID_POWER_BOUND_V1.md` with `k=3`. The power has length `p+2=p+k-1`, so its equality classification gives, up to order,

\[
A=1,\qquad B=(p-1)/3,
\qquad r=3,\quad t=p-1.
\]

For the defect-one atom, (4) gives

\[
q=(u+2)/2.
\]

The lower shifted-depth bound is `1>=2-epsilon(q)`, so `q` must be odd. Therefore `u` is divisible by four. Writing `u=4L` gives exactly (1), including `c=H-2=6L-2`.

At `L=1`, the prime is `13` and the overlap is `c=4`. The already proved `A2_LIGHT_SUPPORT3_FOUR_SHARE_ELIMINATION_V1.md` excludes that whole overlap layer. For `L=2`, `12L+1=25` is not prime. Thus the first prime not excluded by this theorem and the recorded four-share dependency is `37`.

## 6. Why the surviving row requires another idea

The row (1) is precisely the `R=3` subfamily of `A2_RANK2_EXACT_SCALAR_BARRIER_V1.md`. In that row every admissible relation multiplier, even with the exact optimized radial donor, has score at least `m`. The companion relation is itself atom-compatible. These facts do not construct a short-free full pair, but they rule out completing this proof by claiming a missing radial scalar must exist.

The quotient cube has

\[
P=\bar x\bar y^{4L},\qquad
\sigma(xy^{4L})=(2L+1)s.
\]

Its one-copy and two-copy projected-zero parts have defects one and two and satisfy the complete shifted-depth window. A mixed donor argument or an inverse theorem about exchanged atoms is still required.

The following tempting exchange shortcut was also checked and rejected. The whole new-value sequence has length `p+2` and light sum `(H+3)s`. At `p=12L+1`, its minimum original-donor representation has length `p+4`, not `p+2`. Exchanging that whole representation therefore does not preserve maximal-atom length and does not license the maximal saturated-quotient theorem. Exchanging one or two tight quotient atoms preserves length but does not produce `p-1` copies of the new value. Neither operation is a contradiction on its own.

## 7. Audit and scope

The proof review checked both residue classes modulo three, parity before applying any cyclic structural theorem, the strict inequality `2ell_1<p`, exact count doubling without modular wrap, the distinction between an atomization and rigidity, and the previously proved `c=4` dependency. All new mathematical steps are elementary and uniform in the prime. No brute-force enumeration is used.

This advances the whole `c=H-2` layer to the single family (1), and eliminates every unsaturated row there. It does **not** eliminate (1), the other high-overlap layers, the remaining rank-three type-two mixed cases, or the full first corridor. Neither `D_3(C_7^3)` nor the generalized Davenport formula is claimed. Review is by the producing researcher; independent review and novelty certification are not asserted.
