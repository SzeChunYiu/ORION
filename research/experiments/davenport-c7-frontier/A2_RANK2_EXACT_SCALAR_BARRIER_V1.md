# An exact two-parameter obstruction to rank-two scalar-only proofs — V1

Status: **proved prime-uniform route obstruction and an equal-sum exchange interface**. For every prime `p=4Rk+1` with positive integers `R,k`, an explicit rank-two multiplicity row defeats every relation multiplier, even with the exact optimal type-two radial donor. The same row also defeats the type-one radial donor. This includes rows with `r=(p-1)/4`; the obstruction is not confined to a singleton new value.

These results do not construct a compatible full companion and do not disprove the first-corridor target. They identify why a generalized proof must use mixed geometry beyond radial relation multiples.

## 1. The family and its actual multiplicities

Let `R,k>=1`, suppose `p=4Rk+1>=7` is prime, and put

`H=2Rk`, `m=3H+1`,

`r=R`, `t=p-1`, `c=H+1-R`.

Thus `1<=c<=H`, `c+r+t=m`, and the row is on the strict opposite boundary half whenever `c>=2`:

`e=c`, `f=1`.

The type-two overlap bound is respected: `p==1 (mod 4)` and its exact light ceiling is `H`. The type-one ceiling is larger and is also respected.

Assume the rank-two companion relation

`c s+R x+(p-1)y=0`.

The actual enlarged type-two radial donor is

`B=e1^(p-1)e2^(p-1)g^(p-2)s^(c+2)`,

where `e1+e2=2(s-g)`.

## 2. Exhaustive symbolic parametrization of admissible multipliers

For `1<=n<=p-1`, put

`D=[nc]_p`, `A=[nR]_p`, `Bnew=[n(p-1)]_p`.

Since `t=p-1`, the `y` capacity is automatic. The `x` capacity is `1<=A<=R`.

Write `nR=bp+A`. Then `0<=b<=R-1`. Reduction modulo `R`, using `p==1 (mod R)`, gives `A+b==0 (mod R)`. The bounds `1<=A+b<=2R-1` force

`A=R-b`, `n=4kb+1`, `0<=b<=R-1`.

Conversely each of these values of `b` gives an admissible nonzero multiplier. Thus this list is exact; it is not a sampled family of scalars.

All these multipliers are odd. Using `c==2^(-1)-R (mod p)` gives their remaining residues:

`D_b=c+b(2k+1)`,

`A_b=R-b`,

`B_b=4k(R-b)`.

The displayed light residue lies between `c` and `p-1-2k`, so no modular wrap is hidden. The ordinary sum is

`D_b+A_b+B_b=m-2kb`.                                  (1)

## 3. Exact type-two score: never below m

By `A2_EXACT_OVERLAP_AND_RADIAL_STAIRCASE_V1.md`, the optimal radial surcharge is

`q_b=2ceil(max(D_b-c-2,0)/2)`.

For `b=0`, this is zero and the lifted score is exactly `m`.

For `b>=1`, one has `b(2k+1)-2>=1`, so

`q_b=2ceil((b(2k+1)-2)/2)`

`=2kb+2ceil((b-2)/2)`.

Combining this with (1), the **optimal** scalar-lifted length is

`boxed{m+2ceil((b-2)/2),  b>=1.}`                      (2)

For `b=1,2`, the ceiling term is zero. For every larger `b`, it is positive. Consequently no admissible relation scalar produces a zero-sum of length less than `m`, even after exact radial optimization.

When `R=1`, only `b=0` occurs; this recovers the earlier singleton obstruction. When `k=1`, every prime `p==1 (mod 4)` gives the barrier row

`boxed{r=(p-1)/4, c=(p+3)/4, t=p-1.}`

Thus failure of scalar-only proofs persists with both `r` and `c` linear in `p`.

## 4. Type-one extension of the obstruction

For type one, use

`U=f1^(p-1)f2^(p-1)f3^(p-1)s`, `s=f1+f2+f3`.

The enlarged donor contains `c+1` copies of `s`. Its exact radial cost at `D` is

`lambda_(1,c)(D)=D+2max(D-c-1,0)`.

To see exactness directly, a representation of `D s` using `z` shared-direction terms forces equal saturated counts `q` in all three basis coordinates, with `z+q==D (mod p)`. The least feasible nonwrapped count is `q=max(D-c-1,0)`; a wrapped representation adds `p` to `z+q` and cannot improve the resulting length. The stated counts are within the actual capacities.

At `b=0`, the score is again `m`. For `b>=1`, substituting `D_b-c=b(2k+1)` into this exact cost and (1) gives

`boxed{m+2b(k+1)-2>=m.}`

Therefore the same two-parameter family defeats every type-one radial relation multiplier as well.

## 5. The companion relation itself is atom-compatible

This failure cannot be bypassed by claiming that the coefficient row is non-atomic.

Choose any linearly independent `s,y` and define

`x=R^(-1)(y-cs)`.

Then `s,x,y` span a plane and are distinct. Every nonzero relation among them is a scalar multiple of the displayed companion relation. An actual zero-sum subsequence of `s^c x^R y^(p-1)` would therefore have one of the count vectors in Section 2, additionally satisfying `D_b<=c`.

For every `b>=1`, however, `D_b>c`. The sole remaining vector, `b=0`, is the full companion itself. Hence

`s^c x^R y^(p-1)`

is an atom for every such choice of independent `s,y`.

This only establishes atomicity of the companion in its plane. It does not establish the geometric avoidance conditions relative to the maximal atom, or the mixed short-freeness of their product.

## 6. A concrete equal-sum exchange beyond the radial obstruction

The same arithmetic gives

`boxed{x+4k y=(2k+1)s.}`                               (3)

Indeed, multiply `y=cs+R x` by `4k`, use `4kR== -1 (mod p)`, and calculate `4kc==2k+1 (mod p)`.

In the type-two maximal atom, the actual subsequence

`T=e1^k e2^k g^(2k)s`

also sums to `(2k+1)s`, because `k(e1+e2)+2k g+s=(2k+1)s`. Its length equals the length of

`W=x y^(4k)`:

`|T|=|W|=4k+1`.

Every occurrence fits: `k<=p-1`, `2k<=p-2`, and `4k<=p-1`. Consequently, for any hypothetical short-free maximal pair on this row, the exchange

`U'=U T^(-1)W`, `V'=V W^(-1)T`

preserves the product and both factor lengths. Both factors are zero-sum. They are atoms: the product has no nonempty zero-sum shorter than `m`, while

`|U'|=3p-2<2m=3p-1`, `|V'|=m`.

Thus neither factor can split into two nonempty zero-sums. In particular `U'` is a maximal atom. Under the original distinct-support hypotheses, it uses all six support values: the residual old counts are positive, and `x,y` enter through `W`.

This is a structural interface for a stronger inverse theorem about exchanged maximal atoms. It is not a contradiction by itself: the existing support-four classification does not apply to this six-support `U'`.

## 7. Review and scope

A separately tasked proof auditor verified the exhaustive multiplier parametrization, all residue formulas, the parity ceiling in (2), and the distinction between a route obstruction and companion existence. The root independently checked the full written proof, including the exact type-one radial cost, companion atomicity, and occurrence-valid equal-sum exchange. Internal mathematical review is GREEN; this is not external referee approval.

The claim is exact and prime-uniform. No search over primes, support vectors, or subsequences establishes it. Its practical implication is that repeated scalar enumeration cannot finish the generalized exceptional rank-two problem on these rows; a proof must exploit mixed donor geometry or another structural invariant.
