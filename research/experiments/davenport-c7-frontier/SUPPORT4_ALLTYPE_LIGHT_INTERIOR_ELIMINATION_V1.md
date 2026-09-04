# All-type light-share interior elimination from exact radial cost — V1

Status: **proved prime-uniform structural theorem**. For every canonical support-four maximal type `a>=2`, every first-corridor light-share support-three equality companion is forced onto the finite boundary strip `d<c`. The only type where doubling can leave a genuine high-overlap interior is `a=1`.

This strengthens `RADIAL_DOUBLING_INTERIOR_REDUCTION_V1.md` and uses `SUPPORT4_EXACT_RADIAL_LIFTING_COST_V1.md` as its exact radial interface. No generalized Davenport value or novelty/priority claim is made.

## 1. Setup

Let

`p=2H+1>=7`, `m=(3p-1)/2=3H+1`,

and let the support-four maximal atom be

`U=e1^(p-1)e2^(p-1)s^a g^(p-a)`,

`g=s-a^(-1)(e1+e2)`, `1<=a<=H`.

Assume an exact-support-six support-three light-share companion

`V=s^c x^r y^t`, `r<=t<=p-1`.

Then

`c+r+t=m`.

Since `t<=p-1=2H`, write

`r=H+1-c+d`, `t=2H-d`, `d>=0`.

The atom relation is

`c s+r x+t y=0`.

We call `d>=c` the **interior** and `0<=d<c` the **boundary strip**.

## 2. An interior can exist only when `c<=H-1`

The ordering `r<=t` gives

`H+1-c+d<=2H-d`,

or

`2d<=H+c-1`.

If `d>=c`, then

`2c<=H+c-1`,

hence

`boxed{c<=H-1.}`

In particular `2c<p`, so doubling the coefficient `c` causes no wrap.

## 3. Quotient-remainder radial realization

Put

`k=floor((c-1)/a)`

and choose

`q=k a`, `z=2c-k a`.

Then

`q<=c-1`,

and the definition of `k` gives

`k a<c<=(k+1)a`.

Therefore

`0<=z=2c-k a<=c+a`.

The radial resources contain `a+c` actual copies of `s`, so `z<=a+c`. Also `q<=c-1<=H-2<=p-a`, hence `q` copies of `g` are available.

Because `q=k a`,

`[a^(-1)q]_p=k`.

The exact radial lifting theorem therefore gives

`lambda_{a,c}(2c)<=z+q+2k=2c+2k`.

Equivalently, the target `2c s` has the explicit realization

`e1^k e2^k s^(2c-ka) g^(ka)`

of length `2c+2k`.

This one quotient-remainder construction simultaneously recovers the previous `a=1` and `a=2` radial certificates.

## 4. Doubling the companion relation

Assume now `d>=c`. Doubling

`c s+r x+t y=0`

gives

`2c s+A x+B y=0`,

with least residues

`A=2d-2c+1`,

`B=p-2d-2`.

The interior inequalities ensure

`1<=A<=r`, `1<=B<=t`.

Using the radial realization from Section 3, the resulting actual zero-sum subsequence of `UV` has length at most

`(2c+2k)+A+B`

`=2c+2k+p-2c-1`

`=p+2k-1`

`=2H+2k`.

Thus the interior is impossible whenever

`2k<=H`,

i.e.

`boxed{2 floor((c-1)/a)<=H.}`

## 5. Every type `a>=2` satisfies the discriminator automatically

If `a>=2`, Section 2 gives `c<=H-1`, hence

`k=floor((c-1)/a)<=floor((H-2)/a)<=floor((H-2)/2)`.

Therefore

`2k<=H-2<=H`.

So the doubled zero-sum has length at most

`2H+H=3H=m-1`,

contradicting the inherited `(m-1)`-short-freeness.

We have proved:

> **All-type interior theorem.** For every prime `p>=7` and every canonical support-four maximal type
>
> `2<=a<=(p-1)/2`,
>
> a hypothetical exact-support-six first-corridor support-three light-share companion must satisfy
>
> `boxed{0<=d<c.}`
>
> Equivalently, **every interior multiplicity row `d>=c` is impossible for every type `a>=2`.**

No multi-copy overlap ceiling is needed for this conclusion.

## 6. Exact exceptional status of `a=1`

For `a=1`, the same argument has

`k=c-1`.

The discriminator becomes

`2(c-1)<=H`,

or

`c<=floor(H/2)+1=floor((H+2)/2)`.

This exactly reproduces the previously proved low-overlap `a=1` interior range.

Hence `a=1` is not merely the first case considered historically; it is the **unique canonical support-four type for which the radial doubling argument can fail on a genuine high-overlap interior**.

This algebraically explains why the symmetric `a=1` face remains harder than the other maximal-atom types.

## 7. Strategic consequence

The rank-two support-six equality problem now separates cleanly:

- for every `a>=2`, only the boundary strip `d=0,...,c-1` remains at every overlap `c`;
- for `a=1`, the same boundary reduction holds throughout `c<=floor((H+2)/2)`, while a high-overlap interior may remain beyond that range.

Thus any future all-type support-seven proof should not search a two-dimensional multiplicity region for `a>=2`. It should prove a **boundary multiplier/stability theorem** and treat only the exceptional high-overlap `a=1` regime separately.

## Verification receipt

`check_support4_alltype_light_interior_elimination_v1.py` verifies, for every prime through `1009`, every canonical type `a`, every multiplicity row for which `d>=c`, the quotient-remainder radial resource bounds, doubled residues, coefficient capacities, and the final short-zero length inequality. It also confirms that the derived discriminator specializes exactly to the previous `a=1` range.

The checker is regression only; theorem authority is the symbolic quotient-remainder proof above.

## Boundary

- Boundary rows `0<=d<c` are not eliminated here.
- The exceptional `a=1` high-overlap interior is not eliminated here.
- Heavy-share and rank-three support-four companion faces are separate mechanisms.
- No `D_3(C_p^3)` value, all-`k` formula, or novelty/priority claim is made.
