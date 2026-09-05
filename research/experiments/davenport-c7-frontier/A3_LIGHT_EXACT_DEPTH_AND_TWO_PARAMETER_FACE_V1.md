# `a=3` light-share exact radial depth and two-parameter equality face — V1

Status: **proved prime-uniform structural reduction**. In the first maximal corridor, the exceptional support-four maximal type `a=3` admits a closed radial-depth formula, an exact half-overlap ceiling, and a two-parameter normal form for every hypothetical exact-support-six support-three rank-two companion. This does **not** eliminate the `a=3` face by itself and makes no `D_3` or all-prime `D_k` claim.

## 1. Setup

Let

`p=2H+1>=7`, `m=(3p-1)/2=3H+1`,

and take the canonical support-four maximal atom of type `a=3`

`U=e1^(p-1)e2^(p-1)s^3 g^(p-3)`,

where

`s=e3`, `g=s-u(e1+e2)`, `u=3^(-1) mod p`.

Assume a first-corridor exact-support-six support-three companion shares only the light value:

`V=s^c x^r y^t`,

with `r<=t<=p-1` and

`c+r+t=m`.

By the first-corridor support-six normal form, `K=<s,x,y>` has rank two and meets `supp(U)` only in the actual value `s`.

## 2. Exact radial depth on the light line

For `1<=q<=p-1`, the general support-four depth formula specializes to

`rho_U(qs)=min_t (2[u t]_p+[q-t]_p+t)`,

where

`0<=t<=p-3`, `[q-t]_p<=3`.

For `1<=q<=p-2`, the only admissible values are

`t=q-r`, `0<=r<=min(3,q)`.

Hence

`rho_U(qs)=q+2 min{[u t]_p: max(0,q-3)<=t<=q}`.

Among any such block the least `u`-residue occurs at the unique multiple of `3` selected as follows:

- if `q=3j+1` or `q=3j+2`, take `t=3j`;
- if `q=3j`, take `t=3(j-1)`.

Indeed, for `p=3M+1` one has `u=2M+1`, while for `p=3M+2` one has `u=M+1`; in either case the residue of a multiple `3j` is exactly `j`, and the other two residue classes are larger throughout the admissible range.

Therefore:

> **Exact `a=3` light-line depth.** For every `1<=q<=p-2`,
>
> `boxed{rho_U(qs)=q+2 floor((q-1)/3).}`

At the endpoint `q=p-1`:

- if `p=3M+1`, the same formula remains valid;
- if `p=3M+2`, the candidate `t=3M` is excluded by `t<=p-3`, and the minimum occurs at `t=3M-1`, giving

`boxed{rho_U((p-1)s)=7M+1=(7p-11)/3.}`

Thus the radial depth of every nonzero light scalar is explicit.

## 3. The exact light overlap is at most half of `H`

In the first corridor the longer companion has excess `b=H`, so the multi-copy sharing theorem uses

`h=ceil(H/2)`.

Compatibility of `c` light copies requires

`[u k]_p<=p-h`

for every integer `k in [3,3+c]`.

We prove

> `boxed{c_light<=floor(H/2).}`

### Case `p=6k+1`

Then `H=3k`, `u=4k+1`. For `j=3q+1`,

`[u(3+j)]_p=4k+2+q`

through the relevant range. Put

`q0=2k-h`.

Then

`[u(3+(3q0+1))]_p=p+1-h>p-h`.

The corresponding offset is

`j0=3q0+1`.

If `k` is even, `j0=H/2+1`; if `k` is odd, `j0=floor(H/2)`. Thus the forbidden block is hit no later than the first offset beyond `floor(H/2)`.

### Case `p=6k+5`

Then `H=3k+2`, `u=2k+2`. For `j=3q+2`,

`[u(3+j)]_p=4k+5+q`.

Take

`q0=2k-h+1`.

Again the residue equals

`p+1-h>p-h`.

The offset

`j0=3q0+2`

is `H/2+1` when `k` is even and `floor(H/2)` when `k` is odd.

Hence in all cases

`c<=c_light<=floor(H/2)<H`.

## 4. The companion plane avoids both saturated directions

The simultaneous quotient-atom theorem says that the projections of `V` modulo `<e1>` and `<e2>` are atoms of unchanged length `m>p`.

If `K` contained `<e1>`, then its image in `C_p^3/<e1>` would be one-dimensional. The projected companion would then be an atom of length `m>p` in a cyclic group of order `p`, impossible. Thus

`K cap <e1>={0}`.

The same argument gives

`K cap <e2>={0}`.

Because the first-corridor normal form also says `g notin K`, the image of `K` modulo `<s>` is a projective line in `<e1,e2>` different from the three special directions `<e1>`, `<e2>`, and `<e1+e2>`.

Therefore there is a unique slope

`boxed{zeta in F_p\{0,1}}`

such that

`K=span(s, e1+zeta e2)`.

## 5. Two-parameter normal form

Let

`v=e1+zeta e2`.

Since `x` is genuinely new, its image in `K/<s>` is nonzero. Rescale `v` inside this one-dimensional quotient so that

`x=v+alpha s`

for a unique

`alpha in F_p`.

Write

`y=tau v+beta s`.

Projecting the companion relation

`c s+r x+t y=0`

modulo `<s>` gives

`r+t tau=0`,

so

`boxed{tau=-r t^(-1) mod p.}`

The `s` coordinate then gives

`c+r alpha+t beta=0`,

hence

`boxed{beta=-(c+r alpha)t^(-1) mod p.}`

Because `c<H`, one has

`r+t=m-c=p+(H-c)`

with `0<H-c<p`, so `r+t` is not divisible by `p`. Therefore

`tau!=1`.

Consequently `x` and `y` are automatically distinct.

We have proved:

> **Two-parameter face theorem.** For every admissible multiplicity row `(c,r,t)`, every hypothetical `a=3` exact-support-six light-share rank-two companion is uniquely represented by
>
> `zeta in F_p\{0,1}`, `alpha in F_p`,
>
> through
>
> `x=e1+zeta e2+alpha s`,
>
> `y=tau(e1+zeta e2)+beta s`,
>
> where `tau=-r t^(-1)` and `beta=-(c+r alpha)t^(-1)`.

Thus each multiplicity row has at most

`boxed{p(p-2)}`

geometric parameters before the graded depth inequalities are applied.

## 6. Exact graded predicate in the two parameters

For a count-vector subsequence

`W=s^i x^j y^k`,

put

`L=i+j+k`,

`q=j+tau k`,

`z=i+j alpha+k beta`.

Then

`sigma(W)=q e1+q zeta e2+z s`.

The pair short-free condition is therefore exactly

`boxed{L+rho_U(-q,-q zeta,-z)>=m}`

for every nonempty proper count triple

`0<=i<=c`, `0<=j<=r`, `0<=k<=t`.

The complementary inequality is included automatically by applying the same condition to `V/W`.

In particular the new-value power constraints become one-dimensional tests along the two explicit vectors above:

`rho_U(jx)>=j`, `j+rho_U(-jx)>=m`, `1<=j<=r`,

and

`rho_U(ky)>=k`, `k+rho_U(-ky)>=m`, `1<=k<=t`.

These are the next analytic interface.

## 7. Discovery control

The companion checker `check_a3_light_two_parameter_face_v1.py` verifies:

- the exact radial formula against the general support-four depth oracle for every prime through `199`;
- `c_light<=floor(H/2)` for every prime through `1009`;
- the coordinate normal form and exact graded predicate on bounded synthetic rows;
- for the first-corridor primes `11,13,17,19,23,29,31,37,41,43`, every boundary row allowed by the exact multi-copy ceiling has **zero** two-parameter candidates surviving even the two separate new-value power tests.

The last item is discovery evidence only. It motivates a prime-uniform power-depth incompatibility theorem; it is not used as theorem authority here.

## 8. Strategic consequence

The `a=3` face is no longer an unrestricted rank-two search in `C_p^3`. The remaining proof problem is:

> show that no pair `(zeta,alpha)` can simultaneously satisfy the two new-value power-depth windows (or derive a forbidden mixed count triple once those windows hold).

This is a two-variable modular-depth problem with explicit `rho_U`, `tau`, and `beta`, and is the natural next target for Paper 2.

## Boundary

- The `a=3` support-three face is not closed here.
- The exceptional light types `a=1,2` remain separate.
- The rank-three support-four companion remains open.
- No `D_3(C_p^3)` value, all-`k` formula, or novelty/priority statement is made.
