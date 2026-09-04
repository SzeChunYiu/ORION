# `a=3` light-share upper boundary endpoint is impossible — V1

Status: **proved prime-uniform branch elimination**. Every upper boundary row `e=1` in the exceptional `a=3` first-corridor light-share support-three face is impossible for every prime `p>=7`. Together with `A3_BOUNDARY_INDEX_ONE_DONOR_REDUCTION_V1.md`, this leaves only the non-upper boundary rows `e>=2` in type `a=3`.

No generalized Davenport value or novelty/priority claim is made.

## 1. Setup

Let

`p=2H+1>=7`, `m=3H+1`.

At the upper boundary the companion has

`V=s^c x^H y^(p-c)`

and relation

`c s+H x+(p-c)y=0`.

The exact overlap bound from `A3_LIGHT_EXACT_DEPTH_AND_TWO_PARAMETER_FACE_V1.md` gives

`boxed{c<=floor(H/2).}`

The odd-multiplier reduction `A3_UPPER_ENDPOINT_ODD_MULTIPLIER_REDUCTION_V1.md` says that an odd scalar `n=2q+1`, `1<=q<=H-1`, kills the row whenever

`D=[(2q+1)c]_p>=c`

and

`lambda_{3,c}(D)-D<=q-1`.

We now construct such a q explicitly.

## 2. The case `c=1`

Take

`q=1`, `n=3`.

Then

`D=3`,

which lies in the literal radial range `D<=c+3=4`. Hence

`lambda_{3,1}(3)-3=0=q-1`.

The new-value coefficients are

`A=H-1`, `B=p-3`,

so they fit `x^H y^(p-1)`. The resulting zero-sum has length exactly `m-1`.

Thus the upper endpoint is impossible for `c=1`.

## 3. Construct the odd multiplier for `c>=2`

Assume `c>=2` and define

`boxed{q=ceil((c-1)p/(2c)).}`

Because `c<=H/2`, one has `H>=2c`.

First, q lies in the allowed odd-multiplier range. Indeed

`H-(c-1)p/(2c)=(2H-c+1)/(2c)>1`,

so

`q<=H-1`.

Also

`(c-1)p/(2c) >= (c-1)(4c+1)/(2c) > 2c-2`,

hence

`boxed{q>=2c-1.}`

Now put

`E=2cq-(c-1)p`.

The defining ceiling and the fact that `(c-1)p/(2c)` is not an integer give

`boxed{1<=E<=2c-1.}`

(The fraction cannot be integral because `2c<p` and p is prime.)

Then

`(2q+1)c=(c-1)p+(c+E)`.

Moreover

`c+E<=3c-1<p`

because `H>=2c`. Therefore the least residue is exactly

> `boxed{D=c+E.}`

In particular `D>=c`, so the y-capacity condition holds.

## 4. Exact radial surcharge fits the odd-multiplier budget

By `A3_EXACT_RADIAL_EXCESS_V1.md`,

`lambda_{3,c}(D)-D = 2 ceil(max(D-c-3,0)/3)`

`=2 ceil(max(E-3,0)/3)`.

Since `E<=2c-1`,

`lambda_{3,c}(D)-D <= 2 ceil((2c-4)/3)`.

For every `c>=2`,

`ceil((2c-4)/3)<=c-1`,

so

`lambda_{3,c}(D)-D<=2c-2`.

But Section 3 gave `q>=2c-1`. Hence

> `boxed{lambda_{3,c}(D)-D<=q-1.}`

The odd-multiplier criterion is satisfied, producing a forbidden zero-sum subsequence of length at most `m-1`.

## 5. Theorem

Combining `c=1` and `c>=2`:

> **Upper-endpoint theorem.** For every prime `p>=7`, no exact-support-six first-corridor support-three rank-two companion of maximal type `a=3` can lie on the upper light boundary
+>
+> `r=H`, `t=p-c`.

Equivalently, in the boundary parameters `e=c-d`, `f=d+1`, every surviving `a=3` row must satisfy

`boxed{e>=2.}`

These are exactly the rows to which the length-four index-one donor reduction applies.

## 6. Verification receipt

`check_a3_upper_endpoint_elimination_v1.py` verifies the constructed q, the residue identity `D=c+E`, the exact radial-excess formula, both coefficient capacities, and the final short-zero inequality for every prime through `1009` and every c allowed by the exact first-corridor light overlap ceiling.

The checker is regression only; theorem authority is the explicit ceiling construction above.

## Boundary

- Non-upper `a=3` rows `e>=2` remain, now reduced to the capacity-aware index-one problem.
- The exceptional light types `a=1,2` remain.
- The rank-three support-four companion remains open.
- No `D_3(C_p^3)` value or all-k formula is claimed.
