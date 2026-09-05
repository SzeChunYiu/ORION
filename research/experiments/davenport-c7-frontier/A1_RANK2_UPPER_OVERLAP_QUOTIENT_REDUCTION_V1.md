# Type one: an upper-overlap quotient budget and top-layer inverse restriction — V1

Status: **proved prime-uniform structural reduction**. This extends the proper-part budget beyond `c<H` and forces an atomic cyclic quotient at the maximal allowed light overlap. It does not eliminate that top layer.

## 1. Setup

Let `p=2H+1>=7`, `m=3H+1`, and

\[
U=f_1^{p-1}f_2^{p-1}f_3^{p-1}s,\qquad s=f_1+f_2+f_3,
\]

where the `f_i` form a basis. Suppose `V=s^c x^r y^t` is a zero-sum rank-two companion with distinct new values, `c+r+t=m`, `1<=r,t<=p-1`, and `UV` has no nonempty zero-sum shorter than `m`. Assume

\[
H\le c\le\lfloor3H/2\rfloor.
\]

The upper endpoint is the type-one light-share ceiling in `SUPPORT4_MULTICOPY_SHARING_DEPTH_V1.md`. Put `R=x^r y^t` and project the support plane modulo `<s>`.

## 2. The proper-part window still holds

For a nonempty proper projected-zero part `Y|R`, let `sigma(Y)=q s`, `ell=|Y|`. Atomicity of `V` gives `1<=q<=p-c-1`. The radial donor formula `rho_U(qs)=3q-2` and the two shifted-depth inequalities yield exactly as before

\[
\boxed{2\le D(Y):=3q-\ell\le B:=3H-2c.}
\]

The derivation in `A1_RANK2_QUOTIENT_BUDGET_AND_QUARTER_LAYER_ELIMINATION_V1.md` uses properness, not the condition `c<H`, at this step. Thus the window applies in the present range as well.

If the projected `R` is reducible, every atom in a factorization is proper. Its positive defects lie in `[2,B]`. In any atomization the total positive canonical light sum is `p-c+hp` for an integer `h>=0`, so its ordinary defect sum is

\[
3(p-c+hp)-|R|=B+2+3hp>B.
\]

A first prefix crossing `B` has sum at most `2B<3p`. If proper, reduction of its light coefficient subtracts a nonnegative multiple of `3p`; it could not yield a value in `[2,B]`. Therefore that prefix is the whole factorization and `h=0`. Every reducible quotient satisfies

\[
\boxed{\sum q_i=p-c,\qquad\sum D_i=B+2.}
\]

If `B<2`, the proper-part window is empty, so no proper projected-zero part exists in the first place: the quotient is an atom. No factorization assertion is made for an atomic quotient by pretending its whole factor is proper.

## 3. The seam c=H

Here `r+t=p`. The projected values are nonzero by rank two. Their zero-sum relation gives `r(bar x-bar y)=0`, so they coincide. Hence the quotient is exactly `h^p` for a nonzero cyclic value `h`, and is automatically an atom.

## 4. The maximal overlap has a divisor normal form

Take `c=floor(3H/2)` and put `e=c-H=floor(H/2)>=1`. Then `B` is zero or one. Section 2 forces the quotient of `R` to be an atom, of length

\[
N=p-e>p/2+1.
\]

The strict inequality follows from `e<=H/2` and `H>=3`. The projected values are distinct: if equal, their nonzero common value repeated `p-e` times would not sum to zero.

By [Savchev–Chen, Section 5 and Proposition 10](https://arxiv.org/pdf/math/0602568), the cyclic atom has index one. In a suitable generator its two positive coefficients have weighted sum `p`. They cannot both be at least two because `2N>p`; exactly one is one, and the other is an integer `j>=2`. Thus

\[
\boxed{(j-1)r=e\quad\text{or}\quad(j-1)t=e.}
\]

In particular one of the actual new multiplicities divides `floor(H/2)`. This is an inverse restriction on a hypothetical companion, not a realization or an elimination.

## 5. Independent scrutiny and exact scope

The coordinating researcher derived the extension, and the proof-audit researcher independently checked the shifted window, properness in the reducible branch, carry sign, empty-window endpoint, coincident projection at `c=H`, strict index threshold, and divisor equation.

The new proof uses no prime or vector enumeration. Its top inverse form has the explicitly cited long cyclic-atom input. Additional mixed donor geometry remains necessary to eliminate the resulting rows; the first corridor and generalized Davenport formula are not asserted.
