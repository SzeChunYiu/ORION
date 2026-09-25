# `a=3` central non-upper boundary is impossible — V1

Status: **proved prime-uniform branch elimination**. In the exceptional `a=3` light-share support-three face, every central non-upper boundary row

`e=f=(c+1)/2`

is impossible for every prime `p>=7`. Thus any remaining non-upper `a=3` row must be off-center, `e!=f`.

## 1. Setup

Let

`p=2H+1`, `m=3H+1`,

and use the boundary parameters

`e=c-d`, `f=d+1`, `e+f=c+1`.

The central case has

`e=f=(c+1)/2`,

so `c` is odd and `c>=3`. The companion multiplicities are

`r=H+1-e`, `t=p-e`.

The exact `a=3` overlap bound gives

`c<=floor(H/2)`, hence `H>=2c`.

We use an explicit even multiplier, without invoking the length-four donor theorem.

## 2. Choose the scalar

Set

`boxed{q=ceil((H+e)/c)}`

and `n=2q`.

Write

`boxed{w=qc-(H+e).}`

By the ceiling definition,

`0<=w<=c-1`.

Also `qc<p`. Indeed

`qc<=H+e+c-1=H+(3c-1)/2<2H+1=p`

because `H>=2c`.

Therefore the least residue

`R=[qc]_p`

is simply

`boxed{R=H+e+w.}`

## 3. The new-value capacities

Since `2r=p-c`,

`A=[2qr]_p=[-qc]_p=p-R`.

Thus

`A=H+1-e-w<=H+1-e=r`.

For the y-coordinate, `2t==-(c+1) (mod p)`, so we need control of

`q(c+1)=R+q`.

We claim `R+q<p`.

For `c>=5`, write `c=2e-1` and `H=2c+s`, `s>=0`. Then

`q=2+ceil((s+e)/c)<=s+3<=s+e=H-e-c+1`.

Hence

`R+q<=H+e+(c-1)+(H-e-c+1)=2H<p`.

The only smaller central value is `c=3`, `e=2`. Here

`q=ceil((H+2)/3)`.

For `H=6,7`, direct substitution gives respectively `4q=12<13` and `4q=12<15`. For `H>=8`,

`q<= (H+4)/3 <= H/2`,

so

`R+q=3q+q=4q<=2H<p`.

Thus `R+q<p` also for `c=3`.

Consequently

`B=[2qt]_p=p-q(c+1)=p-R-q`.

Since `R+q>=e`,

`B<=p-e=t`.

Both new-value coefficients therefore fit the companion.

## 4. The light coefficient and exact radial surcharge

Because `R>H`,

`D=[2qc]_p=2R-p`.

Using `R=H+e+w` and `2e-1=c`,

> `boxed{D=c+2w.}`

Moreover

`D<=3c-2<p`.

By `A3_EXACT_RADIAL_EXCESS_V1.md`,

`lambda_{3,c}(D)-D
 =2 ceil(max(2w-3,0)/3)`.

Since `w<=c-1`,

`lambda_{3,c}(D)-D<=2 ceil((2c-5)/3)<=2c-2`.

The capacity identities above give

`D+A+B=p-q`.

Hence the lifted zero-sum length is

`p-q+(lambda_{3,c}(D)-D)`.

It is at most `m-1=3H` once

`lambda_{3,c}(D)-D<=H+q-1`.

But

`2c-2<=H-2<=H+q-1`,

so the inequality holds with room to spare.

Thus the central row contains a forbidden short zero-sum.

## 5. Theorem

> **Central-boundary theorem.** For every prime `p>=7`, an exact-support-six first-corridor support-three rank-two companion of maximal type `a=3` cannot satisfy
>
> `e=f=(c+1)/2`.

Together with `A3_UPPER_ENDPOINT_ELIMINATION_V1.md`, every surviving `a=3` boundary row must satisfy

`boxed{e>=2 and e!=f.}`

## Verification receipt

`check_a3_central_boundary_elimination_v1.py` verifies the constructed q, no-wrap inequalities, coefficient identities, exact radial surcharge, and final short-zero bound for every prime through `1009` and every central c allowed by the exact overlap ceiling.

The checker is regression only; theorem authority is the explicit construction above.

## Boundary

- Off-center non-upper `a=3` rows remain.
- The exceptional light types `a=1,2` remain.
- The rank-three support-four companion remains open.
- No generalized Davenport value or all-k formula is claimed.
