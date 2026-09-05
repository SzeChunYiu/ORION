# `a=3` right-half boundary `e<=f` is impossible — V1

Status: **proved prime-uniform branch elimination**. In the exceptional `a=3` light-share support-three face, every boundary row with

`e<=f`

is impossible for every prime `p>=7`. The case `c=1` is closed separately by the scalar `3`; for every `c>=2` one explicit odd multiplier closes the entire half-strip at once.

This theorem subsumes the previously separate upper-endpoint and central-boundary constructions. Those files are retained as provenance and alternative derivations.

## 1. Setup

Let

`p=2H+1`, `m=3H+1`,

and parameterize a boundary row by

`e=c-d`, `f=d+1`, `e+f=c+1`,

so

`r=H+1-e`, `t=p-f`.

The exact `a=3` overlap bound gives

`c<=floor(H/2)`, hence `H>=2c`.

Assume first `c>=2` and `e<=f`.

Put

`a=2e-1`.

Then

`2r=p-a`.

The inequality `e<=f` is equivalent to

`boxed{a<=c.}`

## 2. One universal scalar

Define

`boxed{j=floor((p-c)/(2c))}`

and

`boxed{n=p-2j.}`

Since `H>=2c`, one has `j>=1`, so `1<=n<=p-2`.

Equivalently, writing

`q=H-j`,

one has

`n=2q+1`

and

`q=ceil((c-1)p/(2c))`.

The same estimate used in the upper-endpoint proof gives

`boxed{q>=2c-1.}`

## 3. Exact multiplied coefficients

Because

`2jc<=p-c`,

the light coefficient is

> `boxed{D=[nc]_p=p-2jc.}`

The floor definition also gives

`2jc>p-3c`,

so

> `boxed{c<=D<3c.}`

For the x-coordinate,

`nr=(p-2j)r == -2jr == ja (mod p)`.

Moreover `ja<p`, and using

`j<=(p-c)/(2c)`

we obtain

`ja <= a(p-c)/(2c) <= (p-a)/2=r`,

where the final inequality is exactly `a<=c`.

Thus

> `boxed{A=[nr]_p=ja<=r.}`

For y,

`n(p-f)==2jf (mod p)`.

Again the same bound on j gives

`2jf <= f(p-c)/c <= p-f=t`,

because `f<=c`.

Hence

> `boxed{B=[nt]_p=2jf<=t.}`

So all three coefficients are realized by actual pair resources, with only the light coefficient using radial synthesis.

## 4. Exact coefficient-sum identity

Using

`a+2f=(2e-1)+2f=2c+1`,

we get

`D+A+B`

`=p-2jc+j a+2jf`

`=p+j(a+2f-2c)`

`=boxed{p+j.}`

Since `q=H-j`, this is also

`p+j=m-q`.

## 5. Radial surcharge fits automatically

By `A3_EXACT_RADIAL_EXCESS_V1.md`, and because `D<3c`,

`lambda_{3,c}(D)-D
 <=2 ceil((2c-4)/3)
 <=2c-2`.

Section 2 gives `q>=2c-1`, hence

`lambda_{3,c}(D)-D<=q-1`.

Therefore the actual lifted zero-sum has length

`D+A+B+(lambda_{3,c}(D)-D)`

`<=m-q+q-1=m-1`,

contradicting pair short-freeness.

Thus every row with `c>=2` and `e<=f` is impossible.

## 6. The remaining `c=1` row

When `c=1`, necessarily `e=f=1`. The multiplier `n=3` gives

`D=3`, `A=H-1`, `B=p-3`.

The target `3s` is literal in the pair, so the zero-sum length is exactly

`3+(H-1)+(p-3)=3H=m-1`.

Thus this final right-half row is impossible as well.

## 7. Theorem

> **Right-half boundary theorem.** For every prime `p>=7`, an exact-support-six first-corridor support-three rank-two companion of maximal type `a=3` cannot satisfy
>
> `boxed{e<=f.}`

Consequently every surviving `a=3` boundary row must lie in the strictly asymmetric half

`boxed{e>f.}`

Equivalently,

`e>(c+1)/2`.

This removes the upper endpoint `e=1`, the central line `e=f`, and every boundary on the same side in one construction.

## Verification receipt

`check_a3_right_half_boundary_elimination_v1.py` verifies the floor/ceiling identity, all coefficient capacities, exact coefficient sum, radial surcharge, and final short-zero inequality for every prime through `1009` and every allowed boundary row with `e<=f`.

The checker is regression only; theorem authority is the explicit scalar construction above.

## Boundary

- The left half `e>f` remains.
- The exceptional light types `a=1,2` remain.
- The rank-three support-four companion remains open.
- No generalized Davenport value or all-k formula is claimed.
