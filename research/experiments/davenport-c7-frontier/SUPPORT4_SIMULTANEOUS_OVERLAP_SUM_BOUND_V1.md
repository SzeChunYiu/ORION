# Simultaneous light-heavy overlap sum bound for support-four maximal types — V1

Status: **proved prime-uniform structural theorem**. In the first maximal corridor, if a support-four maximal atom of canonical type `a>=4` admits sharing of both unsaturated values, then the exact reusable light and heavy multiplicities satisfy

`boxed{c_light+c_heavy<=a-2.}`

This is the first uniform joint bound on the two overlap directions. It is especially useful for the rank-three support-four equality face, where both overlaps are present.

No generalized Davenport value, support-seven theorem, or novelty/priority claim is made here.

## 1. Setup

Let

`p=2H+1>=7`,

and write the canonical support-four maximal atom as

`U=e1^(p-1)e2^(p-1)s^a g^(p-a)`,

`g=s-u(e1+e2)`, `u=a^(-1) mod p`,

with

`4<=a<=H`.

For the first corridor put

`h=ceil(H/2)`.

The exact multi-copy theorem says that the maximum light and heavy reuse counts are characterized by

`[u k]_p<=p-h`

throughout the intervals

`[a,a+c_light]`

and

`[a-c_heavy,a]`,

respectively.

Assume both overlap directions are actually available, so

`c_light>=1`, `c_heavy>=1`.

We prove that their sum cannot reach `a-1`.

## 2. A residue formula for multiplication by `u`

Write

`a u=1+ell p`,

where

`1<=ell<=a-1`.

Because `u` is invertible modulo p and `a<p`, one has

`gcd(ell,a)=1`.

For an integer `k` with `1<=k<=p-1`, let

`r_k=[ell k]_a in {0,...,a-1}`.

Then

`boxed{[u k]_p=(r_k p+k)/a.}`

Indeed `ell k=aM+r_k`, so

`u k=M p+(r_k p+k)/a`,

and `r_k p+k` is divisible by a because

`ell p==-1 (mod a)`.

Moreover

`0<r_k p+k<a p`,

so the displayed quotient is already the least residue modulo p.

Since `gcd(ell,a)=1`, on every block of `a` consecutive integers the values `r_k` run through every residue class modulo a exactly once.

## 3. Contradiction if the combined interval has length at least `a`

Suppose for contradiction that

`c_light+c_heavy>=a-1`.

Then the combined interval

`I=[a-c_heavy,a+c_light]`

contains at least `a` consecutive integers, and the exact sharing criteria force

`[u k]_p<=p-h`

for every `k in I`.

Choose any `a` consecutive integers inside I. By Section 2, one of them, call it `k_*`, satisfies

`r_{k_*}=a-1`.

For this integer

`[u k_*]_p=((a-1)p+k_*)/a`

`=p-(p-k_*)/a`.

The required upper bound `[u k_*]_p<=p-h` would imply

`boxed{k_*<=p-a h.}`

We now show this is impossible.

## 4. Every type `a>=5`

For `a>=5`, one has `H>=a>=5` and

`a h>=a H/2>=5H/2>2H+1=p`.

Hence

`p-a h<0`.

But `k_*>=1`, contradicting the inequality from Section 3.

Therefore

`c_light+c_heavy<=a-2`

for every `a>=5`.

## 5. The endpoint type `a=4`

It remains to treat `a=4`.

### 5.1 `H` odd

If `H` is odd, then

`h=(H+1)/2`

and

`4h=2H+2=p+1>p`.

The same argument as Section 4 gives an immediate contradiction.

### 5.2 `H` even

If `H` is even, then

`p==1 (mod 4)`, `h=H/2`,

so

`4h=2H=p-1`.

The inequality from Section 3 becomes only

`k_*<=1`,

so we need to use the fact that both overlap directions are present.

From

`4u=1+ell p`

and `p==1 (mod 4)`, divisibility by four forces

`ell=3`.

Since `c_heavy>=1` and `c_light>=1`, the combined interval I contains

`3,4,5`.

If `c_light+c_heavy>=3=a-1`, then I has length at least four. In particular it contains `k=5`: the right endpoint is already at least five.

For `k=5`,

`r_5=[3*5]_4=3=a-1`.

But `5>1`, contradicting the necessary inequality `k_*<=1`.

Thus the bound also holds for `a=4`.

## 6. Theorem

Combining Sections 4 and 5:

> **Simultaneous-overlap theorem.** Let `p>=7` be prime and let a first-corridor support-four maximal atom have canonical type
>
> `4<=a<=(p-1)/2`.
>
> If both unsaturated maximal-atom values are reusable by a compatible companion, then
>
> `boxed{c_light+c_heavy<=a-2.}`

Consequently any rank-three support-four equality companion

`V=s^c g^d x^r y^t`

with `c,d>=1` satisfies

`boxed{c+d<=a-2.}`

Since its total length is `m=3H+1`, the two genuinely new values carry

`r+t=m-c-d>=3H-a+3>=2H+3=p+2`.

Thus the projection of the `x,y` subsequence to the quotient by the overlap plane has length strictly greater than p.

## 7. Verification receipt

`check_support4_simultaneous_overlap_sum_bound_v1.py` directly recomputes the exact light and heavy interval ceilings for every prime through `2003` and every canonical type `a>=4`. Whenever both ceilings are positive it verifies

`c_light+c_heavy<=a-2`.

The checker also verifies the residue formula `[u k]_p=(r_k p+k)/a` on a bounded all-k control and freezes the `a=4` borderline cases separately.

The checker is regression only; theorem authority is the residue-block argument above.

## Boundary

- Types `a=2,3` are exceptional and are not covered by this sum bound.
- The theorem is a compatibility bound, not a rank-three elimination by itself.
- No `D_3(C_p^3)` value or all-k formula is claimed.
