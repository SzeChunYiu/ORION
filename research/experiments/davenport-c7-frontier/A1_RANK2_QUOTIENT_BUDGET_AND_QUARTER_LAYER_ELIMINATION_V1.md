# Type one: a quotient budget and a complete quarter-overlap elimination — V1

Status: **proved prime-uniform structural budget and complete-layer elimination**. For every prime `p>=7` with `p==3 (mod 4)`, the entire rank-two light-share layer `c=(p+1)/4` is empty, including unsaturated new multiplicities. This follows from a vanishing relation coefficient, not a scalar sweep.

## 1. Setup and exact proper-part window

Let `p=2H+1>=7` be prime, `m=3H+1`, and let

\[
U=f_1^{p-1}f_2^{p-1}f_3^{p-1}s,
\qquad s=f_1+f_2+f_3,
\]

where `(f1,f2,f3)` is a basis. Suppose `V=s^c x^r y^t` is a rank-two zero-sum companion with distinct new values, `c+r+t=m`, `1<=r,t<=p-1`, and `UV` has no nonempty zero-sum shorter than `m`. For the budget theorem assume `1<=c<H`, and put `R=x^r y^t`, so `|R|=p+H-c>p`.

The original donor has the exact radial depth

\[
\rho_U(qs)=3q-2,\qquad 1\le q\le p-1.
\tag{1}
\]

Indeed, using the single `s` occurrence leaves `q-1` of each basis value and gives length `3q-2`; using no `s` costs `3q`, and the coordinate equations allow no shorter representation.

Project the support plane modulo `<s>`. For a nonempty proper projected-zero part `Y|R`, write `sigma(Y)=qs`, `ell=|Y|`. Atomicity of `V` forces `1<=q<=p-c-1`. Applying the graded depth inequalities to `Y` and `Ys^c`, and using (1), gives

\[
\ell\le3q-2,
\qquad m-\ell-c\le3(p-q-c)-2.
\]

Consequently, with `D(Y)=3q-ell`,

\[
\boxed{2\le D(Y)\le B:=3H-2c.}
\tag{2}
\]

This holds for every proper projected-zero part. The projected values are nonzero; otherwise the rank-two companion relation would force rank one.

## 2. Exact factorization-independent budget

Every quotient atom is proper, because cyclic atoms have length at most `p` while `|R|>p`. For any atomization, write its canonical light coefficients and defects as `q_i,D_i`. Then

\[
\boxed{\sum_i q_i=p-c,\qquad
\sum_iD_i=3H-2c+2=B+2.}
\tag{3}
\]

**Proof.** The total light sum is `-cs`, so the positive ordinary sum of the `q_i` is `p-c+ap` for some `a>=0`. Therefore

\[
\sum_iD_i=3(p-c+ap)-|R|=B+2+3ap>B.
\]

In any ordering of the atoms, the first prefix crossing `B` has ordinary defect sum `S` in `[B+1,2B]`. Here

\[
2B\le6H-4<3p.
\]

If that prefix is proper, reducing its light sum modulo `p` changes `S` by a nonnegative multiple of `3p`. The result is either greater than `B` or negative, contradicting (2). The crossing is therefore the whole factorization. Since its sum is below `3p`, the formula above forces `a=0`, proving (3). QED.

In particular, every quotient factorization has at most `floor((3H-2c+2)/2)` atoms. This is the slope-three version of the positive-defect first-crossing mechanism used for type two.

## 3. A vanishing coefficient excludes the full quarter layer

For any proper quotient atom with counts `A_x,A_y`, the rank-two relation space gives

\[
(-q,A_x,A_y)=\lambda(c,r,t)\quad\text{in }\mathbb F_p^3.
\]

Thus its defect satisfies

\[
D=3q-(A_x+A_y)
\equiv-(3c+r+t)\lambda
\equiv(3H-2c+2)\lambda\pmod p.
\tag{4}
\]

Now assume `p==3 (mod 4)` and take

\[
c=(H+1)/2=(p+1)/4.
\]

This is an integer in `[1,H-1]`. The coefficient in (4) becomes

\[
3H-2c+2=2H+1=p,
\]

so every quotient atom would have `D==0 (mod p)`. But (2) requires

\[
2\le D\le3H-2c=2H-1=p-2.
\]

There is no such integer. A quotient atom must exist since `R` is nonempty and projects to zero, and it is proper since `|R|>p`. This contradiction proves:

> **Quarter-layer theorem.** For every prime `p>=7`, `p==3 (mod 4)`, no rank-two type-one first-corridor companion can satisfy
>
> \[
> \boxed{c=(p+1)/4,\qquad r+t=m-c.}
> \]

The conclusion holds for all positive allowed new multiplicities. Unlike the earlier saturated-augmentation consequence, it does not require a new value with multiplicity `p-1`.

## 4. Review and boundary

The review checked the original one-`s` depth formula, both shifted-depth inequalities, the factor `3p` in carry reduction, properness of every cyclic atom, and the exact vanishing coefficient at the stated overlap. The contradiction in Section 3 needs only the proper-part window and one quotient atom; it does not assume a special factorization.

No prime enumeration or external classification theorem supplies this proof. The budget in Section 2 requires `c<H`; the quarter-layer specialization meets that requirement for every stated prime. Other type-one high-overlap layers, the remaining type-two mixed cases, the full first corridor, and the generalized Davenport formula remain unproved here. Internal review is by the producing researcher, with no independent referee or novelty claim.
