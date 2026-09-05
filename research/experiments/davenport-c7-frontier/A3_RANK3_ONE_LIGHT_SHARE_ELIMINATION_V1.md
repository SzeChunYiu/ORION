# Type-three rank-three companions with one light shared copy are impossible

Date: 2026-09-05. Baseline: `86f089ab63ba90f7df292cd44d5a46c7527014ce`.
Status: **prime-uniform proof of the complete `a=3,c=1` layer**.

Let `p=2H+1>=11` be prime, `m=p+H`, and

`U=e1^(p-1)e2^(p-1)s^3 g^(p-3)`, with `e1+e2=3(s-g)`.

Suppose `V=s g^d x^r y^t` is a zero-sum of length `m`, the values `x,y`
are genuinely new, and `UV` has no nonempty zero-sum of length less than
`m`. Then the multiplicity obstruction gives `1<=d<=2`, and the
shared-donor doubling theorem in
`A3_RANK3_SHARED_DONOR_NEGATIVE_EVEN_V1.md` permits us to order `r<=t`
and write

`r=H-k`, `t=p-(1+d)+k`, `0<=k<=d`.

We prove that every such row is impossible. No rank condition beyond those
needed for the stated canonical setup is used in the certificates.

## The uniform certificate

For `p>=17`, take three times the relation defining `V`. Its new-value
least residues are

`R=H-3k-1`, `T=p-3(1+d-k)`.

They are positive: `H>=8`, `k<=2`, and `1<=1+d-k<=3`.
Moreover `R<=H-k=r` and `T<=p-(1+d-k)=t`. Use the actual old-support
occurrences `s^3 g^(3d)`. They fit because `UV` has four copies of `s`
and `p-3+d` copies of `g`, and `3d<=p-3+d`.

The resulting zero-sum has length

`R+T+3+3d=p+H-1=m-1`.

Thus all primes `p>=17` are settled by one scalar and one occurrence formula.

## The two small primes

For `p=11,13`, the same scalar-three certificate works for every row except
`d=2,k=2`. Positivity and capacities follow from the displayed formulas
with `k<=1`; they also hold for `d=1,k<=1`.

The two remaining rows have these explicit certificates. The occurrence
vector is in the order `(e1,e2,s,g,x,y)`.

| p | d | k | r | t | relation scalar n | occurrence vector | length | m |
|---|---|---|---|---|---|---|---|---|
| 11 | 2 | 2 | 3 | 10 | 8 | (2,2,2,0,2,3) | 11 | 16 |
| 13 | 2 | 2 | 4 | 12 | 7 | (1,1,4,4,2,6) | 18 | 19 |

To verify without choosing coordinates for `x,y`, write the first two equal
counts as `E`, and the next two as `z,w`. In both rows

`3E+z == n (mod p)`, `w-3E == nd (mod p)`,
`R == nr (mod p)`, `T == nt (mod p)`.

The entire sum is therefore `n(s+dg+rx+ty)=0`. Every count fits within
`(p-1,p-1,4,p-3+d,r,t)`, and the last two columns prove strict shortness.
This table is a hand-derived finite remainder, not a search over possible
companion values.

## Failed selector route and review boundary

The original negative-even selector cannot close this layer on its own.
For example, at `p=13,c=d=1,k=0`, its donor-capacity condition permits only
`J=2,4,6`. Their lengths are respectively `20,19,20`, while `m=19`;
none is strictly short. Every even `J>=8` violates its condition (C).
The positive scalar-three certificate above bypasses this exact obstruction.

The full occurrence argument and both exceptional vectors were independently
checked by the session's zero-sum inverse-theory agent. This is internal
multi-agent review, not external referee certification. Direct arithmetic
replay also checks both exceptional vectors and their capacities; the
all-prime authority is the proof above.

This theorem closes only the `a=3,c=1` rank-three layer. It does not assert
the full first-corridor support-seven theorem, any value of `D_3(C_7^3)`,
an all-prime `D_k` formula, or priority.
