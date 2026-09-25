# Type two: the exact top-overlap maximal-atom exchange — V1

Status: **proved prime-uniform equal-sum, equal-length exchange**. The coordinating researcher and proof-audit researcher independently derived and checked it. This is a structural reduction of the remaining top layer, not its elimination.

## 1. Hypotheses and the cyclic quotient

Let `p=2H+1>=7` be prime and `m=3H+1`. In `C_p^3`, use a basis `(e1,e2,g)` and put

\[
2s=e_1+e_2+2g,
\qquad
U=e_1^{p-1}e_2^{p-1}g^{p-2}s^2.
\]

Assume that

\[
V=s^H x^r y^t,
\qquad r+t=p,
\qquad 1\le r,t\le p-1,
\qquad \sigma(V)=0,
\]

has rank two, with distinct new values `x,y` outside `supp(U)`, and that `UV` has no nonempty zero-sum subsequence of length below `m`. Let `R=x^r y^t`.

Projection of the rank-two support plane modulo `<s>` sends `x,y` to nonzero values: a zero image for one would force a zero image for the other by the companion relation, contradicting rank two. As `r+t=p`, that relation gives

\[
r\bar x+t\bar y=r(\bar x-\bar y)=0,
\]

so `bar x=bar y=h!=0`. Hence

\[
\pi(R)=h^p
\]

is a single cyclic atom. It has no proper projected-zero part. This is precisely why the submaximal-overlap rectangle proof, which assumes `|R|>p`, does not apply here.

## 2. The odd-H top layer already has a short donor certificate

If `H` is odd, let `b=(H-1)/2`. The actual donor-only subsequence

\[
s^{H+2}e_1^b e_2^b g^{H-1}
\]

is zero-sum and has length `3H=m-1`. To check its sum, in the basis `(e1,e2,g)` write `s=(u,u,1)` with `u=H+1=2^{-1}` modulo `p`. The first two coordinates are

\[
(H+2)u+b\equiv (H+2+H-1)/2=p/2=0\pmod p,
\]

and the third is `(H+2)+(H-1)=p`. Its light count is exactly the `H+2` copies available in `UV`; the two axis counts are nonnegative and at most `p-1`; and `H-1<=p-2`. Thus a hypothetical surviving top-overlap pair has `H` even, equivalently `p≡1 (mod 4)`. This also follows from the previously proved exact light-overlap ceiling.

## 3. An actual tight p-term replacement

Assume now `H` is even and put `b=H/2`. The subsequence

\[
\boxed{W=s e_1^b e_2^b g^H}
\]

belongs to `U`: it uses one of the two copies of `s`, `b<=p-1` of each axis value, and `H<=p-2` copies of `g`. Its length is

\[
|W|=1+2b+H=2H+1=p=|R|.
\]

Using `e1+e2=2(s-g)`, its sum is

\[
\sigma(W)=s+b(e_1+e_2)+Hg
=s+Hs-Hg+Hg=(H+1)s.
\]

The zero-sum relation of `V` gives

\[
\sigma(R)=-Hs=(H+1)s.
\]

Thus `W` and `R` are actual equal-length, equal-sum occurrence sequences. No formal extra donor occurrence is used.

## 4. The two exchanged sequences are atoms

Define

\[
U'=U W^{-1}R,
\qquad V'=s^H W.
\]

These are occurrence sequences satisfying

\[
U'V'=UV,
\qquad \sigma(U')=\sigma(V')=0,
\qquad |U'|=3p-2,
\qquad |V'|=m.
\]

Both are atoms under the standing short-freeness hypothesis.

For `V'`, every nonempty proper zero-sum divisor would have length below `m`, which is forbidden. For `U'`, a nonempty proper zero-sum divisor and its nonempty zero-sum complement would both have length at least `m`, forcing `|U'|>=2m`. But

\[
|U'|=3p-2=2m-1<2m.
\]

This contradiction proves atomicity of `U'`. Its length is the same classical maximal atom length as `U`; equivalently, the standard value `D(C_p^3)=3p-2` makes `U'` another maximal atom.

## 5. Exact occurrence and support data

The exchanged sequences have the explicit forms

\[
\boxed{
U'=e_1^{3H/2}e_2^{3H/2}g^{H-1}s\,x^r y^t,
\qquad
V'=e_1^{H/2}e_2^{H/2}g^H s^{H+1}.
}
\]

All displayed exponents are positive in the stated range. Because `x,y` are distinct new values, `U'` has exactly six support values and rank three. The companion `V'` has exactly the four old support values `e1,e2,g,s` and rank three. Their support intersection has size four, and their union still has size six.

The product capacities are unchanged. In particular the combined `g` count remains `(H-1)+H=p-2`, and the combined `s` count remains `1+(H+1)=H+2`. The exchange does not manufacture a saturated `g^(p-1)` donor.

## 6. Exact limitation

This exchange is available at every hypothetical surviving top-overlap pair and preserves both atom lengths. Unlike the lower-overlap whole-`R` exchange that had a length mismatch, this is a genuine maximal-atom exchange.

It changes the maximal atom from the canonical support-four form to an explicit support-six form. No classification or elimination of that support-six maximal atom is supplied here. Consequently the exchange does not by itself contradict short-freeness and does not close `c=H`, the remaining rank-three mixed cases, the full first corridor, or any unproved generalized Davenport value.

Any subsequent use must prove or cite a structural result that applies to the newly displayed support-six atom and its actual support-four companion. A theorem stated only for canonical support-four maximal atoms cannot be transferred to `U'` without an additional argument.
