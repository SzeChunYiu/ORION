# Type a=1 rank-two balanced boundary selector — V1

Status: **proved prime-uniform elimination of an infinite family of overlap
layers**. Every right-half rank-two light-share boundary row with
`2<=c<=floor(p/7)` is impossible. A sharper remainder-dependent condition
also eliminates additional boundary rows. This does not close high relative
overlap, the opposite boundary half, or the full type-one face.

Baseline read: `86f089ab`. The scalar construction follows the boundary
coordinates of `A3_RIGHT_HALF_BOUNDARY_ELIMINATION_V1.md`; the occurrence
cost is the type-one radial construction in
`A1_LIGHT_SUPPORT3_TWO_SHARE_ELIMINATION_V1.md`.

## 1. Hypotheses and exact boundary coordinates

Let `p=2H+1>=7` be prime and `m=p+H`. In saturated coordinates, write

`U=f1^(p-1)f2^(p-1)f3^(p-1)s`, `s=f1+f2+f3`.

Suppose a hypothetical first-corridor exact-support-six light-share rank-two
companion is

`V=s^c x^r y^t`, `r<=t`, `c+r+t=m`,

and `UV` has no nonempty zero-sum of length less than `m`.

Assume it lies on the multiplicity boundary, so

`r=H+1-e`, `t=p-f`, `e,f>=1`, `e+f=c+1`.

For the main corollary `c<=p/7`, the prior low-overlap doubling theorem
already forces this boundary: its hypothesis
`c<=floor((p+3)/4)` is automatically satisfied. For the conditional result
below, the boundary remains an explicit hypothesis.

We treat the right half `e<=f`. Put `alpha=2e-1`; this condition is equivalent
to `alpha<=c`, while `alpha+2f=2c+1` and `2r=p-alpha`.

## 2. A remainder-sensitive scalar certificate

Assume `c>=2` and

`j=floor((p-c)/(2c))>=1`.

Write the exact division identity

`p=(2j+1)c+v`, `0<=v<2c`,

and select the nonzero scalar `n=p-2j`.

The multiplied companion relation has least positive residues

`D=[nc]_p=p-2jc=c+v`,

`A=[nr]_p=j alpha`, `B=[nt]_p=2jf`.

The new-value capacities hold because

`(2j+1)alpha<=(2j+1)c<=p`,

`(2j+1)f<=(2j+1)c<=p`.

These imply respectively `A<=r` and `B<=t`. Positivity and the capacity
bounds also verify that the displayed new counts are the actual least
residues, with no omitted wrap. The light residue satisfies `D<p` since
`j>=1`.

Using `alpha+2f=2c+1`, their ordinary sum is

`D+A+B=p+j`.

## 3. Explicit old-support occurrences and the exact score

Set

`q=max(v-1,0)`, `z=D-q`.

Use `q` copies of each of `f1,f2,f3` and `z` copies of `s`. Their sum is

`q(f1+f2+f3)+z s=(q+z)s=D s`.

The capacities are explicit: if `v<=1`, then `q=0` and `z=c+v<=c+1`;
otherwise `z=c+1` and `q=D-c-1<=p-1`. Thus the saturated counts fit `U`,
the light count fits the `c+1` shared occurrences in `UV`, and these old
occurrences are disjoint from `x^A y^B`.

The resulting nonempty zero-sum has length exactly

`3q+z+A+B=p+j+2 max(v-1,0)`.

It is shorter than `m` whenever

`3v<=(2j+1)c-2j+1`.                                    (1)

Indeed, if `v>=2`, condition (1) is equivalent, after substituting for `p`,
to

`2(v-1)<=H-j-1`.

If `v<=1`, the surcharge is zero; moreover
`p>=(2j+1)c>=4j+2`, so oddness gives `H>=2j+1` and the same score conclusion
holds. In that case (1) is automatic as well.

Therefore condition (1) gives a forbidden zero-sum of length at most `m-1`.
This is the conditional boundary-selector theorem.

## 4. A uniform infinite-layer corollary

If `2<=c<=floor(p/7)`, then `j>=3`. Since `v<=2c-1`,

`3v<=6c-3<=(2j+1)c-2j+1`.

The last inequality is exactly

`(2j-5)c>=2j-4`,

which holds for every `j>=3`, `c>=2`.

Consequently every right-half boundary row in this entire range is
impossible, without any fixed upper bound on `c` or any finite classification.
Together with the prior interior theorem, a surviving light-share rank-two
companion with `2<=c<=floor(p/7)` must lie on the strict opposite half
`e>f` of the boundary.

## 5. Audit and preserved limits

The proof is entirely the displayed scalar, capacity arithmetic, and explicit
occurrence vector. It requires no search over vectors or primes. The root
reviewer independently checked the complete type-one argument, including the
score equivalence, corollary inequality, and actual occurrence capacities.
The type-one surcharge is twice `max(v-1,0)` here; it was checked separately
from the type-two parity staircase. This is internal mathematical review,
not external referee certification.

The extension to smaller `j` is deliberately conditional. At `j=1,2`,
condition (1) need not hold for every remainder `v`, so no complete
right-half or high-overlap theorem is inferred from this construction.
The `x` capacity also depends on `e<=f`; it does not automatically extend
to the opposite half. If the defining floor is zero, the displayed scalar
would be zero modulo `p` and must not be used.

This result advances infinitely many previously untreated `c>=5` layers,
but does not eliminate all high relative overlaps. The full type-one and
type-two rank-two faces, the full first-corridor support-seven theorem, and
`D_3(C_7^3)` remain outside its claim scope.
