# Type two: the entire rank-two c=H-3 layer is empty — V1

Status: **proved prime-uniform complete-layer elimination**. Every rank-two light-share row with `c=H-3>=1` is impossible. The proof uses the exact defect budget, rigid-power structure, and a one-step exchange inside a long cyclic atom.

## 1. Hypotheses and defect alphabet

Let `p=2H+1>=11` be prime, `m=3H+1`, and use the canonical type-two maximal atom

\[
U=e_1^{p-1}e_2^{p-1}g^{p-2}s^2,
\qquad e_1+e_2=2(s-g).
\]

Suppose `V=s^(H-3)x^r y^t` is a rank-two zero-sum companion with distinct new values, `r+t=p+3`, `1<=r,t<=p-1`, and `UV` has no nonempty zero-sum shorter than `m`.

In `A2_RANK2_EXACT_QUOTIENT_DEFECT_BUDGET_V1.md`, this is `d=3`. Every quotient atom has defect `D` in `{1,2,3}`, with unique possible length

\[
\ell_D=[3D\cdot4^{-1}]_p,
\]

and every atomic factorization satisfies

\[
\sum_i D_i=4.
\tag{1}
\]

Also `ell_D+D` must be even. The projected values are distinct and nonzero, and every atom dividing the quotient is mixed.

## 2. Primes p congruent to one modulo four

Write `p=4u+1`. Here `u>=3`, since the smallest such prime in the stated range is `13`. The three possible lengths are

\[
\ell_D=D(u+1),\qquad 1\le D\le3,
\qquad 3(u+1)<p.
\tag{2}
\]

If a defect-one atom `P=bar(x)^A bar(y)^B` exists, the exact count formula says that a defect-`D` atom has counts `[DA]_p,[DB]_p`. By (2), `DA+DB=D|P|<p`, so these are the ordinary counts `DA,DB`. For `D=2,3` this is `P^D`, which is not an atom. Therefore the only atom dividing the quotient is `P`, and (1) gives `pi(R)=P^4`. The rigid-power exclusion in Section 6 of `A2_RANK2_SATURATED_BOUNDARY_FULL_ELIMINATION_V1.md` rules this out.

If no defect-one atom exists, then no defect-three atom exists either: its complement would factor with total defect one by (1). Hence all atoms have defect two. Their count vectors are identical, so the quotient is a rigid square `Q^2`. But its length is `p+3`, exceeding the bound `p+1` for a rigid square from `CYCLIC_TWO_VALUE_RIGID_POWER_BOUND_V1.md`.

Both possibilities are impossible. This excludes the entire prime class.

## 3. Primes p congruent to three modulo four

Write `p=4u+3`; then `u>=2`. Direct least-residue arithmetic gives

\[
\ell_D=p-uD,\qquad 1\le D\le3.
\tag{3}
\]

If a quotient factorization has `k` atoms, its total length and (1) imply

\[
p+3=\sum_i\ell_{D_i}=kp-4u.
\]

Since `p+3+4u=2p`, necessarily `k=2`. Its defect pattern is `1+3` or `2+2`. But `ell_2=2u+3` is odd, and cannot have the same parity as defect two. Thus every factorization is of the form

\[
\pi(R)=P Q,\qquad
D(P)=1,\quad D(Q)=3,
\]

with

\[
|P|=3u+3,\qquad |Q|=u+3.
\tag{4}
\]

The parity of `|P|+1` additionally forces `u` even. If `u` is odd there is already a contradiction; below we handle the only remaining possibility.

## 4. A mixed cyclic exchange creates a forbidden third length

The atom `P` has length `3u+3>(p/2)+1`. The long-atom index theorem therefore gives a generator `h` for which its positive representatives sum to `p`. This is the standard consequence of [Savchev–Chen, Section 5 and Proposition 10](https://arxiv.org/pdf/math/0602568), independently obtained by Yuan. The cited paper uses unnormalized index `p`; normalized index is one. Its proof is combinatorial, with no bounded enumeration input.

Since `2|P|>p` and its support has exactly two values, one of those positive coefficients is one. Write

\[
P=h^A(jh)^B,\qquad j\ge2,\quad A,B\ge1.
\]

The length and weight equations give

\[
A+B=3u+3,\qquad A+jB=p,
\qquad (j-1)B=u.
\tag{5}
\]

Thus `B<=u`, `j<=u+1`, and `A>=2u+3`.

The count formula for defect three says that `Q` contains `[3B]_p=3B` copies of `jh`; no wrap occurs because `3B<=3u<p`. Therefore the whole quotient has `4B` copies of that value.

Now take

\[
P'=h^{A-j}(jh)^{B+1}.
\]

This is an actual subsequence of `PQ`: its first count is positive because `A-j>=u+2`, and its second count satisfies `B+1<=4B`. Its positive representatives sum to

\[
(A-j)+j(B+1)=A+jB=p,
\]

so `P'` is an atom. Its length is

\[
|P'|=3u+3-(j-1)=3u+3-u/B.
\]

As `1<=u/B<=u`,

\[
u+3<|P'|<3u+3.
\]

But (4) lists the only two possible atom lengths after the parity exclusion of defect two. This is a contradiction. Hence the second prime class is empty as well.

## 5. Conclusion and audit

For every prime `p>=11`, no rank-two type-two first-corridor companion can have `c=H-3`. At `p=7`, this expression is zero and is not a positive-overlap layer.

Together with the previous results, the three consecutive positive layers

\[
\boxed{c=H-1,\qquad c=H-2,\qquad c=H-3}
\]

are all eliminated whenever the displayed overlap is positive. The `c=H` unsaturated layer is separate.

The internal review checked both residue tables, exact factor counts, the distinction between an existing defect-one atom and its absence, all no-wrap inequalities, the long-atom theorem's strict threshold, and every occurrence of the exchanged atom. The one-step exchange is a structural operation, not an enumeration of cyclic atoms.

This note does not eliminate all remaining high-overlap layers or the unsaturated rank-three type-two face. It makes no full first-corridor, `D_3(C_7^3)`, or generalized Davenport equality claim. No independent referee audit or novelty certification is asserted.
