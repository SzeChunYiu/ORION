# `a=3` upper boundary endpoint reduces to an odd-multiplier radial inequality — V1

Status: **proved prime-uniform arithmetic reduction**. The unique `a=3` boundary row excluded from the length-four index-one donor theorem has a complementary scalar structure: every even multiplier fails the `x`-capacity automatically, while every odd multiplier has an explicit capacity and short-zero test in one residue. This does not yet prove that a usable odd multiplier always exists.

## 1. Upper endpoint

Use the `a=3` first-corridor notation

`p=2H+1`, `m=3H+1`.

The upper boundary is `e=1`, equivalently `d=c-1`, so

`boxed{V=s^c x^H y^(p-c).}`

The companion relation is

`c s+H x+(p-c)y=0`.

The exact overlap theorem gives `c<=floor(H/2)`.

## 2. Every even multiplier fails the x-capacity

Let `n=2q`, `1<=q<=H`.

Since `2H=p-1`,

`[nH]_p=[q(p-1)]_p=p-q`.

Thus the multiplied coefficient of `x` is

`A=p-q>=H+1>H=v_x(V)`.

Therefore:

> `boxed{no even multiplier can produce a subsequence relation supported inside V on the upper endpoint.}`

This explains why the even index-one mechanism from the non-upper rows cannot extend to `e=1`.

## 3. Odd multiplier normal form

Let

`n=2q+1`, `0<=q<=H-1`.

Put

`D=[nc]_p`.

Then

`A=[nH]_p=H-q`,

which always satisfies `1<=A<=H`.

Because the y coefficient is `p-c`,

`B=[n(p-c)]_p=p-D`.

Hence the y-capacity condition is exactly

> `boxed{B<=p-c iff D>=c.}`

For every `q>=1` with `D>=c`, the multiplied relation therefore fits both new-value multiplicities.

## 4. Exact short-zero inequality

Let `lambda_{3,c}(D)` be the exact light radial cost in the pair resources.

The actual lifted zero-sum has length

`lambda_{3,c}(D)+(H-q)+(p-D)`.

Since `p+H=3H+1=m`, this is at most `m-1` precisely when

> `boxed{lambda_{3,c}(D)-D<=q-1.}`

Thus the upper endpoint is eliminated by any integer

`1<=q<=H-1`

such that

`D=[(2q+1)c]_p>=c`

and

`lambda_{3,c}(D)-D<=q-1`.

This is an exact one-dimensional criterion.

## 5. Literal-radial subcase

If in addition

`c<=D<=c+3`,

then the pair contains `D` literal copies of `s`, so

`lambda_{3,c}(D)=D`.

Any such residue with `q>=1` automatically kills the row.

This supplies many endpoint certificates, but not all of them; a uniform proof must also use nonliteral radial realizations.

## 6. Discovery control

`check_a3_upper_endpoint_odd_multiplier_v1.py` verifies the algebraic identities through prime `1009` and scans every admissible upper endpoint through prime `401`. Every row tested has at least one odd multiplier satisfying the exact criterion above. The scan also records that restricting to the literal-radial subcase leaves genuine residual rows, so the full radial oracle is load-bearing.

The zero-residual finite scan is discovery evidence only. The missing theorem is a prime-uniform modular approximation statement for the odd orbit `[(2q+1)c]_p` weighted by the exact radial excess `lambda_{3,c}(D)-D`.

## Boundary

- Existence of a usable odd multiplier is not proved here.
- Non-upper rows are governed separately by the index-one donor reduction.
- The rank-three support-four companion remains open.
- No `D_3(C_p^3)` value or all-`k` formula is claimed.
