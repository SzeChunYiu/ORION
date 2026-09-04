# Exact multi-copy sharing criterion from support-line depth — V1

Status: **proved prime-uniform necessary condition for every maximal corridor**. This strengthens the one-copy modular-inverse selector to the exact number of copies of either unsaturated maximal-atom value that a compatible companion may reuse. It is a depth consequence only; passing the criterion does not prove that a companion exists.

## 1. Setup

Let

`U=e1^(p-1)e2^(p-1)e3^a g4^(p-a)`

be a support-four maximal atom over `C_p^3`, where

`g4=e3-a^{-1}(e1+e2)`, `1<=a<=(p-1)/2`.

Put

`u=[a^{-1}]_p`.

In the maximal corridor `C_j(p)`, let the longer companion have

`|V|=m=p+b`,

with

`b=(p+1)/2-j`, `1<=j<=floor((p+1)/4)`.

The pair `UV` is `(m-1)`-short-zero-free. Hence, if `V` contains `c` copies of a value `s`, then for every `1<=r<=c` the shared-only subsequence `s^r` must satisfy

`r+rho_U(-r s)>=m`.

Set

`h=ceil(b/2)`.

We now evaluate all these inequalities exactly for `s=e3` and `s=g4`.

## 2. Light value `e3`: exact radial depth

Assume `1<=r<=p-1-a`, the pair-capacity range for `e3`.

For the target

`-r e3=(0,0,p-r)`,

the one-parameter depth formula has admissible parameters

`p-r-a <= t <= min(p-r,p-a)`.

Write `z=p-t`. Then

`max(a,r)<=z<=a+r`,

and the depth becomes

`rho_U(-r e3)=p-r+2 min_z [u t]_p`

`=p-r+2(p-max_{max(a,r)<=z<=a+r}[u z]_p)`.

Therefore

`r+rho_U(-r e3)>=p+b`

is equivalent to

`max_{max(a,r)<=z<=a+r}[u z]_p <= p-h`.

As `r` runs from `1` through `c`, the intervals

`[max(a,r),a+r]`

have union exactly

`[a,a+c]`.

Thus:

> **Light multi-copy criterion.** If `v_e3(V)>=c`, then
>
> `boxed{[u k]_p<=p-h for every integer k in [a,a+c].}`

Equivalently, the maximum possible reusable light multiplicity is

`c_light=max{c<=p-1-a : [u k]_p<=p-h for all k=a,...,a+c}`.

Since `[u a]_p=1`, `c_light` is the forward distance from `a` to the first integer whose `u`-multiple lands in the top forbidden residue block

`{p-h+1,...,p-1}`.

## 3. Heavy value `g4`: exact radial depth

Assume `1<=r<=a-1`, the pair-capacity range for `g4`.

For

`-r g4=(r u,r u,p-r)`,

the same admissible `t` interval applies. With `z=p-t`, the first two coordinates depend on

`u(r-z)=-u(z-r)`.

Since `r<a` in the heavy capacity range, the new variable

`k=z-r`

runs through

`a-r<=k<=a`.

Hence

`rho_U(-r g4)=p-r+2(p-max_{a-r<=k<=a}[u k]_p)`.

The short-free condition is therefore equivalent to

`max_{a-r<=k<=a}[u k]_p<=p-h`.

Taking all `1<=r<=c` gives the union interval `[a-c,a]`. Thus:

> **Heavy multi-copy criterion.** If `v_g4(V)>=c`, then
>
> `boxed{[u k]_p<=p-h for every integer k in [a-c,a].}`

Equivalently,

`c_heavy=max{c<=a-1 : [u k]_p<=p-h for all k=a-c,...,a}`.

This is the backward distance from `a` to the first top-block hit under multiplication by `u`.

## 4. The one-copy selector is the endpoint case

The previous modular-inverse selector is recovered immediately.

For one light copy, the new residue is

`[u(a+1)]_p=[1+u]_p`.

In the support-four range `u!=p-1`, so light sharing is possible only if

`boxed{u<=p-h-1.}`

For one heavy copy, when `a>1`,

`[u(a-1)]_p=[1-u]_p=p+1-u`,

so heavy sharing is possible only if

`boxed{u>=h+1.}`

These are the integer forms of the earlier fractional thresholds.

## 5. Exact p=7 first-corridor table

For `p=7`, `j=1`, one has `b=3` and `h=2`. The three canonical support-four types give:

| `a` | `u=a^{-1}` | `c_light` | `c_heavy` |
|---:|---:|---:|---:|
| 1 | 1 | 4 | 0 |
| 2 | 4 | 2 | 1 |
| 3 | 5 | 0 | 2 |

Thus any hypothetical exact-support-six `(8,10,19)` maximal pair already has its overlap multiplicity bounded to these tiny intervals before the new support values are considered.

The old singleton selector only saw `light / both / heavy`; the present theorem determines the full admissible multiplicity of that overlap.

## 6. Arithmetic interpretation

Multiplication by `u` permutes the nonzero residues. The companion may keep reusing an unsaturated maximal-atom value only while a consecutive integer interval adjacent to `a` avoids the top `h-1` residues under this permutation.

This is a finite rotation/Beatty-type interval avoidance problem. It is exact and prime-uniform, and it turns the shared multiplicity into arithmetic data of the inverse residue `u` rather than a free search variable.

For a support-six equality search, the next sequence of reductions is therefore:

1. choose the support-four type `a`;
2. compute `c_light,c_heavy` from the modular interval criterion;
3. apply the inverse selector to remove one side when possible;
4. use the rank-two/three support-six normal form on the remaining companion support;
5. only then enumerate or classify the two genuinely new values.

## Verification receipt

`check_support4_multicopy_sharing_v1.py` compares the interval criteria against the original exact one-parameter depth formula for every prime through 401, every maximal corridor, every support-four type, and every multiplicity within pair capacity. It also freezes the p=7 first-corridor table `(4,0),(2,1),(0,2)`.

The checker is regression only; theorem authority is the depth calculation above.

## Boundary

- This is a necessary compatibility criterion, not a realizability theorem.
- It does not eliminate the remaining support-three or support-four equality branches by itself.
- The theorem assumes a support-four maximal atom.
- No `D_3(C_p^3)` value or novelty/priority claim is made.
