# Support-7 binary-cube obstruction eliminated — V1

Status: **proved bounded structural result**, donor/priority novelty **not assessed**.
Research frame: `FRAME_V1.md`.
Branch: `shadow/davenport-c7-frontier-20260903`.

## Statement

Let `G = C_7^3 = F_7^3`, let `e1,e2,e3` be a basis, and write

- `e12 = e1+e2`,
- `e13 = e1+e3`,
- `e23 = e2+e3`,
- `e123 = e1+e2+e3`.

Let

`Q = {e1,e2,e3,e12,e13,e23,e123}`.

If `S` is a zero-sum sequence over `G` of length `37`, supported on `Q`, and every multiplicity is at most `6`, then `S` is a product of four pairwise disjoint nonempty zero-sum subsequences. Consequently, no length-37 zero-sum sequence with zero-sum packing number at most three can have support GL(3,7)-equivalent to `Q`.

The last consequence uses the independently established `D_2(C_7^3)=29` gate only to note that a length-37 packing-number-at-most-three obstruction cannot contain seven equal terms: seven copies form one zero-sum and the remaining total-zero sequence has length 30, which is longer than the maximum total-zero length with packing number at most two.

## Proof

Order the points as

`(e1,e2,e3,e12,e13,e23,e123)`

and write their multiplicities as `m_i`. Since `|S|=37` and all `m_i<=6`, all seven points occur. Put `d_i=6-m_i`. Then

`sum_i d_i = 42-37 = 5`.

The sequence containing six copies of each point of `Q` has coordinate sum

`4*6 = 24 = 3 (mod 7)`

in each of the three coordinates. Since `S` is zero-sum, the deleted deficit sequence has coordinate sum `(3,3,3)`. Each coordinate deficit is an integer between 0 and the total deficit 5, so the three congruences modulo 7 are ordinary integer equalities:

```
d1  + d12 + d13 + d123 = 3
d2  + d12 + d23 + d123 = 3
d3  + d13 + d23 + d123 = 3.
```

Set `g=d123` and `h=d12+d13+d23`. Adding the three displayed equations and using total deficit 5 gives

`h + 2g = 4`.

Hence exactly three cases are possible.

### Case A: `g=2`, `h=0`

Then `d12=d13=d23=0` and `d1=d2=d3=1`. This is one pattern.

### Case B: `g=1`, `h=2`

Writing `(d12,d13,d23)=(a,b,c)` with `a+b+c=2`, the coordinate equations give

`(d1,d2,d3)=(c,b,a)`.

There are six labelled solutions. Up to coordinate permutations they split into the compositions `2+0+0` and `1+1+0`.

### Case C: `g=0`, `h=4`

Again write `(d12,d13,d23)=(a,b,c)`, now with `a+b+c=4`. The coordinate equations give

`(d1,d2,d3)=(c-1,b-1,a-1)`.

Nonnegativity forces `a,b,c>=1`, hence `(a,b,c)` is a permutation of `(2,1,1)`. There are three labelled solutions.

Thus there are exactly `1+6+3=10` labelled multiplicity patterns, forming four orbits under coordinate permutations.

It remains to exhibit a four-zero-sum partition for one representative of each orbit. In the following table a seven-tuple records multiplicities in the fixed order `(e1,e2,e3,e12,e13,e23,e123)`.

### Orbit 1

Sequence multiplicities:

`(5,6,6,5,5,4,6)`.

Partition:

```
(0,0,1,1,0,0,6)
(2,0,2,0,5,0,0)
(0,3,3,0,0,4,0)
(3,3,0,4,0,0,0)
```

Their coordinate sums are respectively `(7,7,7)`, `(7,0,7)`, `(0,7,7)`, `(7,7,0)`.

### Orbit 2

Sequence multiplicities:

`(4,6,6,6,6,4,5)`.

Partition:

```
(0,0,0,1,1,1,5)
(2,0,2,0,5,0,0)
(2,2,0,5,0,0,0)
(0,4,4,0,0,3,0)
```

Their coordinate sums are `(7,7,7)`, `(7,0,7)`, `(7,7,0)`, `(0,7,7)`.

### Orbit 3

Sequence multiplicities:

`(5,5,6,6,5,5,5)`.

Partition:

```
(0,0,0,1,1,1,5)
(2,2,0,5,0,0,0)
(0,3,3,0,0,4,0)
(3,0,3,0,4,0,0)
```

Again each coordinate sum is divisible by 7.

### Orbit 4

Sequence multiplicities:

`(5,5,5,6,6,6,4)`.

Partition:

```
(0,1,1,0,0,6,0)
(1,0,1,0,6,0,0)
(1,1,0,6,0,0,0)
(3,3,3,0,0,0,4)
```

The first three blocks have coordinate sums `(0,7,7)`, `(7,0,7)`, `(7,7,0)` and the fourth has `(7,7,7)`.

In every orbit the four rows are nonempty, sum componentwise to the sequence multiplicity vector, and each row is zero-sum in `F_7^3`. Coordinate permutations preserve zero-sum structure and disjointness, so all ten labelled patterns have a four-block partition. This proves the statement.

## Boundary

This result eliminates one complete support geometry (the nonzero binary cube) and its whole length-37 multiplicity space. It does **not** eliminate all seven-point supports in `F_7^3`, and it does not by itself determine `D_3(C_7^3)`.
