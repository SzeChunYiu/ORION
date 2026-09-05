# Type two: complete rank-two submaximal-overlap elimination — V1

Status: **proved for every prime `p>=7` and every `1<=c<H`**, with independent hostile internal proof audit. This replaces individual overlap layers and prime-congruence reductions by one structural theorem.

## 1. Hypotheses and complete proof

Let `p=2H+1>=7`, `m=3H+1`, and

\[
U=e_1^{p-1}e_2^{p-1}g^{p-2}s^2,
\qquad e_1+e_2=2(s-g),
\]

where `(e1,e2,g)` is a basis. Suppose

\[
V=s^c x^r y^t,
\qquad c+r+t=m,
\qquad 1\le c<H,
\qquad 1\le r,t\le p-1
\]

is the rank-two zero-sum companion with distinct new values and `UV` contains no nonempty zero-sum shorter than `m`.

Put `d=H-c`, `a=d+1`, so `2<=a<=H`. Project the support plane modulo `<s>`. The two projected values are nonzero and distinct, and the quotient `R=x^r y^t` has length `p+a-1` and zero total sum.

For every nonempty proper quotient-zero occurrence part `Y=x^A y^B`, let its actual light sum be `q s`, with canonical `1<=q<=p-c-1`. The established original-donor proper-part window is

\[
2-\epsilon(q)\le D(Y):=2q-A-B
\le a-1-\epsilon(q+c).
\tag{7}
\]

In particular, `1<=D(Y)<=a-1` and `D(Y)==A+B (mod 2)`.

The full rank-two relation gives

\[
(-q,A,B)=\lambda(c,r,t)\quad\text{in }\mathbb F_p^3,
\]

so

\[
D(Y)\equiv-(2c+r+t)\lambda
\equiv(H-c+1)\lambda=a\lambda\pmod p.
\tag{8}
\]

Thus every hypothesis of `CYCLIC_RECTANGULAR_CHARGE_RIGIDITY_V1.md` is satisfied. It follows that the quotient is a rigid power `P^a`, with `P` its only atomic divisor.

Apply the established elementary rigid-power theorem from `CYCLIC_TWO_VALUE_RIGID_POWER_BOUND_V1.md`. Since `a|P|=p+a-1`, equality holds in that theorem. It forces, after swapping values,

\[
r=a,\qquad t=p-1,
\qquad c=H+1-a.
\]

This is an actual rank-two type-two saturated-new-value boundary, already completely excluded by `A2_RANK2_SATURATED_BOUNDARY_FULL_ELIMINATION_V1.md`.

Therefore

\[
\boxed{\text{No canonical rank-two type-two light-share companion exists for }1\le c<H.}
\]

This is a complete prime-uniform elimination of the entire submaximal overlap range, not a finite collection of layers or residue classes. It uses the original proper-part window, elementary cyclic intersection counting, parity, the existing elementary rigid-power theorem, and the already audited saturated donor exclusion. It needs neither the optional `d^2<p` signature regime nor any long cyclic-atom index theorem.

## 2. Independent audit and preserved boundaries

Root and quotient_structure independently obtained the simultaneous-wrap mechanism from the exact intersection count. The proof-audit teammate checked the complete application, including part-versus-atom distinctions, the endpoint parity at `D=a`, strict positivity at the first wrap, and the noncircular rigid/saturated dependency. Root and quotient_structure separately checked the abstract strengthening that dispenses with the full exact budget when establishing charge-one atomicity.

The failed route to avoid is applying the atom least-residue length formula to arbitrary proper parts. The proof uses their actual count vectors, whose coordinates remain below `p`; no proper-part length bound is needed.

The range `c=H` is separate: its quotient has length exactly `p` and need not have a proper atomic divisor. The unsaturated rank-three type-two face, other type-one cases, and the separate global first-corridor gates remain unproved here. This theorem does not assert the full first corridor, `D_3(C_7^3)`, or the generalized Davenport numerical formula.
