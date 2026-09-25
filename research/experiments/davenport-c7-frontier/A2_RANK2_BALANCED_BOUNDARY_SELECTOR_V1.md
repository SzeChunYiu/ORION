# Type a=2 rank-two balanced boundary selector — V1

Status: **proved prime-uniform boundary-slice elimination**. For every prime
`p>=7`, the entire right half of the light-share rank-two boundary is empty
whenever `2<=c<=floor(p/3)`. The proof uses one explicit scalar and the exact
shared-donor radial staircase; it does not classify vectors or enumerate
primes. The higher-overlap region and the other half of the boundary remain
outside this statement.

Baseline read: `86f089ab`. Source interfaces:
`RADIAL_DOUBLING_INTERIOR_REDUCTION_V1.md`,
`A2_EXACT_OVERLAP_AND_RADIAL_STAIRCASE_V1.md`, and the analogous scalar
construction in `A3_RIGHT_HALF_BOUNDARY_ELIMINATION_V1.md`.

## 1. Statement and boundary coordinates

Let `p=2H+1>=7` be prime, `m=3H+1`, and

`U=e1^(p-1)e2^(p-1)s^2 g^(p-2)`,

with `e1+e2=2(s-g)`. Suppose a hypothetical exact-support-six first-corridor
light-share rank-two companion has

`V=s^c x^r y^t`, `c+r+t=m`, `r<=t`,

and `UV` contains no nonempty zero-sum of length less than `m`.

The previously proved interior elimination permits boundary coordinates

`r=H+1-e`, `t=p-f`, `e,f>=1`, `e+f=c+1`.

We prove that this is impossible under

`2<=c<=floor(p/3)` and `e<=f`.

The latter condition is the balanced/right half of the boundary. Equivalently,
putting `alpha=2e-1`, it is exactly `alpha<=c`.

## 2. Select one negative even scalar

Set

`j=floor((p-c)/(2c))`, `n=p-2j`.

The overlap hypothesis gives `j>=1`. Euclidean division yields the exact
integer decomposition

`p=(2j+1)c+v`, `0<=v<2c`.

Because `c>=2`, the scalar satisfies `1<=n<=p-2`. Multiplying the companion
relation by `n` gives the least positive residues

`D=[nc]_p=p-2jc=c+v`,

`A=[nr]_p=j alpha`,

`B=[nt]_p=2jf`.

Here `D<p` because `j>=1`. For the other two residues, use
`2r=p-alpha`, `t=p-f`, and the capacities below to establish that no wrap
has been omitted.

## 3. Both new-value capacities hold

Since `alpha<=c`,

`(2j+1)alpha<=(2j+1)c<=p`,

and therefore

`j alpha<=(p-alpha)/2=r`.

Also `f<=c`, since `e>=1` and `e+f=c+1`. Thus

`(2j+1)f<=(2j+1)c<=p`,

which gives `2jf<=p-f=t`.

All displayed residues are positive and at most the corresponding available
multiplicities. In particular `x^A y^B` uses actual occurrences of `V`.

The identity `alpha+2f=2c+1` gives

`D+A+B=p+j`.

## 4. The exact staircase fits the remaining length budget

The available radial donor is

`e1^(p-1)e2^(p-1)s^(c+2)g^(p-2)`.

The exact type-two staircase theorem gives

`lambda_(2,c)(D)-D=2 ceil(max(D-c-2,0)/2)`

`=2 ceil(max(v-2,0)/2)`.

Write this surcharge as `L`. If `v<=1`, then `L=0`. Since
`p>=(2j+1)c>=4j+2` and `p` is odd, one has `H>=2j+1`, so in this case
`L<=H-j-1`.

For `v>=2`, elementary parity gives `L<=v-1`. Moreover,

`v<=2c-1<=(2j+1)c-2j-1`,

where the second inequality is equivalent to `(2j-1)c>=2j` and follows
from `c>=2`, `j>=1`. Substituting the decomposition of `p` gives

`2(v-1)<=p-2j-3=2(H-j-1)`.

Consequently `L<=H-j-1` in every case. The actual lifted zero-sum has length

`lambda_(2,c)(D)+A+B=p+j+L<=p+H-1=m-1`,

contradicting the inherited short-free threshold.

This proves the announced all-prime boundary-slice theorem.

## 5. Explicit occurrence reconstruction

The proof does not require treating the radial minimum as an abstract oracle.
Let

`q=2 ceil(max(v-2,0)/2)` and `z=D-q`.

Use `q/2` copies of each of `e1,e2`, `q` copies of `g`, and `z` copies of
`s`, followed by `A` copies of `x` and `B` copies of `y`.

Because `q` is even,

`(q/2)(e1+e2)+q g+z s=(q+z)s=D s`.

The staircase construction guarantees `0<=z<=c+2`, `0<=q<=p-2`, and
`q/2<=p-1`. Directly, when `v<=2` one has `q=0` and `z=c+v`; otherwise
`q` is either `v-2` or `v-1`, so `z` is `c+2` or `c+1`. In particular,
the old and new occurrence sets are disjoint and every capacity is checked.
The total length is `p+j+q`, exactly the score bounded above.

## 6. Scope, proof audit, and failed extension

An internal independent-agent arithmetic review checked the selected residues,
both new-value capacities, the parity bound, the explicit old-support
reconstruction, and the strict score. It confirmed the proof and the following
two boundaries:

- The selector requires `j>=1`. For `c>p/3`, its defining floor can be zero,
  and `n=p` would be the zero scalar; that is not a usable certificate.
- The `x` capacity uses `alpha<=c`. The same formula does not automatically
  handle `e>f`.

There is a useful additional conditional certificate beyond the stated
range. If `p/3<c<=H`, choose `n=p-2`. Its light residue `D=p-2c` is literal
because `0<D<c`. The new residues are `A=alpha`, `B=2f`; hence the
certificate applies whenever `3alpha<=p` and `3f<=p`, with length exactly
`p+1<m`. This condition can cover rows in either boundary half, but its
capacity inequalities must be retained. It is not a full high-overlap
closure.

The proof authority is the symbolic construction above. No finite search,
new execution receipt, external novelty audit, or donor-theorem ownership
claim is asserted by this note.

The full type-two rank-two face, full first-corridor support-seven theorem,
and `D_3(C_7^3)` remain unproved by this result.
