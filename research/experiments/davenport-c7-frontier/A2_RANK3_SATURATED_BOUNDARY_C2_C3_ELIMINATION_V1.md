# Complete type-two saturated-boundary elimination at c = 2 and c = 3 — V1

Status: **proved elimination of both complete overlap layers `c=2,3`, for every prime `p>=7` for which the rows occur**. General remainder selectors leave three explicit prime endpoints. A short table of symbolic mixed certificates and four additional occurrence vectors close those endpoints, including the exceptional inverse-donor family at `p=11,c=2`.

This is a proof by explicit formulas, not a finite search over hypothetical companions. The full first-corridor and generalized Davenport equalities are not asserted.

## 1. Setup and inverse-theorem alternatives

Let `p=2H+1>=7` be prime, `m=3H+1`, `u=H+1=2^(-1)` in `F_p`, and use the basis `(e1,e2,g)` with `s=(u,u,1)`.

Consider

`U=e1^(p-1)e2^(p-1)g^(p-2)s^2`,

`V=s^c g x^r y^(p-1)`, `r=H-c>0`, `c in {2,3}`.

Suppose `V` is zero-sum and, toward contradiction, `UV` has no nonempty zero-sum of length below `m`.

The actual shared donor has saturated `e1,e2,g` counts `p-1` and `c+2` copies of `s`. By `A2_CONSTANT_DONOR_INVERSE_CLASSIFICATION_V1.md`, its high-multiplicity value has the form

`y=(A,-A,1)`, `A!=0`,                                (1)

except for the explicitly retained alternative at `(p,c)=(11,2)`:

`y=(4,-4,2)` or `(-4,4,2)`.                          (2)

The companion relation is always

`r x=y-cs-g`.                                       (3)

## 2. The general prime ranges reduce to three endpoints

### c = 2

For a prime `p=4q+1`, the initial remainder selector in `A2_RANK3_SATURATED_BOUNDARY_SMALL_OVERLAP_ELIMINATION_V1.md` has `v=1`. It applies as soon as `q>1`, covering every such prime in the present range.

For a prime `p=4q+3`, that selector has `v=3` and applies when `q>3`. Below that range, `p=7` satisfies the circular-gap condition `p<(c+1)^2=9`, while `p=15` is composite. Thus only

`(p,c)=(11,2)`

remains. The exceptional inverse family (2) occurs only at this same endpoint and has not been ignored.

### c = 3

For `p=6q+1`, the initial selector has `v=1`, and applies when `q>1`. The possible lower prime `p=7` has `r=H-c=0` and is outside the stated row.

For `p=6q+5`, divide twice the prime:

`2p=6(2q+1)+4`.

The generalized remainder selector uses quotient `2q+1`, remainder `4`, and actual power

`a=2q-3`.

If `q>=4`, then `1<=a<=r=3q-1` and its score condition holds:

`(2q+1)+4=2q+5<=3q+1=H-1`.

The circular-gap theorem handles every allowed prime `p<16`. Hence the only remaining prime endpoints are

`(p,c)=(17,3),(23,3)`.

These are the exact residuals of the displayed division arguments, not the output of a prime sweep.

## 3. A reusable mixed occurrence formula for the main family

Assume (1). Let integers `n,j` satisfy

`0<=n<=c`, `1<=j<=n+1`,

and

`[nu-jA]_p+[nu+jA]_p=n`.                             (4)

The actual sequence

`Z(n,j)=x^r y^(j-1)s^(c-n)g^(1+n-j)`

`             e1^[nu-jA]_p e2^[nu+jA]_p`             (5)

is zero-sum. Indeed, (3) makes the sum before the saturated terms equal to

`j y-ns+(n-j)g=(jA-nu,-jA-nu,0)`.

Every count fits: `j-1<=n<=c`, the `g` count is nonnegative and at most `c`, the `s` count is between zero and `c`, and the two saturated counts sum to `n<=c`. Its exact length is

`|Z(n,j)|=H+n<m`.

Let `d=min([jA]_p,[-jA]_p)` be the centered magnitude. Condition (4) has two elementary forms:

- If `n` is even, it holds when `d<=n/2`, because `nu=n/2` in the field.
- If `n` is odd, it holds when `d>=H-(n-1)/2`, because `nu=(p+n)/2`, and the larger of its two shifted residues then crosses `p` exactly once.

The tables below only use these stated residue inequalities. Replacing `A` by `-A` exchanges the two saturated coordinates and preserves every resource bound, so one row for each centered magnitude `|A|` covers both signs.

## 4. Main-family table at the three endpoints

The following explicit choices satisfy (4) and hence produce (5).

| p | c | Centered magnitude of A | n | j | Centered magnitude d of jA |
|---:|---:|---:|---:|---:|---:|
| 11 | 2 | 1 | 2 | 1 | 1 |
| 11 | 2 | 3 | 1 | 2 | 5 |
| 11 | 2 | 4 | 2 | 3 | 1 |
| 11 | 2 | 5 | 2 | 2 | 1 |
| 17 | 3 | 1 | 2 | 1 | 1 |
| 17 | 3 | 2 | 3 | 4 | 8 |
| 17 | 3 | 3 | 3 | 3 | 8 |
| 17 | 3 | 4 | 3 | 2 | 8 |
| 17 | 3 | 5 | 3 | 2 | 7 |
| 17 | 3 | 6 | 2 | 3 | 1 |
| 17 | 3 | 7 | 3 | 1 | 7 |
| 17 | 3 | 8 | 2 | 2 | 1 |
| 23 | 3 | 1 | 2 | 1 | 1 |
| 23 | 3 | 3 | 3 | 4 | 11 |
| 23 | 3 | 4 | 3 | 3 | 11 |
| 23 | 3 | 5 | 3 | 2 | 10 |
| 23 | 3 | 6 | 3 | 2 | 11 |
| 23 | 3 | 8 | 2 | 3 | 1 |
| 23 | 3 | 9 | 3 | 4 | 10 |
| 23 | 3 | 10 | 3 | 1 | 10 |
| 23 | 3 | 11 | 3 | 1 | 11 |

At `p=11`, the table leaves only `A=+/-2` in the main family. At `p=17`, it covers every nonzero `A`. At `p=23`, it leaves only `A=+/-2,+/-7`. The next section gives direct mixed vectors for these exact residual values.

## 5. Four explicit residual certificates

All coordinates below are in the fixed basis `(e1,e2,g)`.

### p = 11, c = 2, main family A = 2

Here `H=5`, `r=3`, `s=(6,6,1)`, `y=(2,9,1)`. Equation (3) gives

`x=(4,10,3)`.

The actual sequence

`x y s^2 e1^4 e2^2 g^5`

has length `15<m=16`. Its coordinate sum, using the displayed representatives, is `(22,33,11)`, hence zero in `C_11^3`. Every count is available: in particular the shared donor has four copies of `s` and ten copies of `g`. Swapping the first two coordinates handles `A=-2`.

### p = 11, c = 2, exceptional family A = 4, C = 2

For (2), take `y=(4,7,2)`. Equation (3) gives

`x=(1,2,7)`.

The sequence

`x s e1^4 e2^3 g^3`

has coordinate sum `(11,11,11)` and length `12<m=16`. All counts fit. The coordinate swap handles the other exceptional value. This closes the actual exceptional inverse-theorem family, rather than assuming it has the main third coordinate.

### p = 23, c = 3, main family A = 2

Here `H=11`, `r=8`, `s=(12,12,1)`, `y=(2,21,1)`. Equation (3) gives

`x=(13,1,14)`.

The sequence

`x^2 s^5 e1^6 e2^7 g^13`

has coordinate sum `(92,69,46)` and length `33<m=34`. It uses exactly the five available `s` occurrences; its other counts are at most their displayed capacities. The coordinate swap handles `A=-2`.

### p = 23, c = 3, main family A = 7

Take `y=(7,16,1)`. Equation (3) gives

`x=(5,9,14)`.

The sequence

`x^3 s e1^19 e2^7 g^3`

has coordinate sum `(46,46,46)` and length `33<m=34`. Its counts fit the same resources. The coordinate swap handles `A=-7`.

## 6. Complete theorem and provenance

Section 2 eliminates all primes except the three identified endpoints. Sections 3--5 eliminate every main-family value at those endpoints and both additional values in the only exceptional inverse family. Therefore:

> **Theorem.** For every prime `p>=7` and `c in {2,3}` with `r=H-c>0`, a zero-sum companion
>
> `V=s^c g x^r y^(p-1)`
>
> cannot form an `(m-1)`-short-zero-free product with the canonical type-two maximal atom `U`.

Together with `A2_RANK3_SATURATED_BOUNDARY_C_GE4_ELIMINATION_V1.md`, this closes every saturated-new-value rank-three row with `c>=2`. The layer `c=1` is separate and is not proved in this note. Unsaturated new multiplicities and global packing implications remain outside the conclusion.

The coordinating researcher derived the remainder reductions and explicit residual certificates. The rank-two proof agent independently checked every coordinate sum, the sign symmetry, occurrence capacities, and the table's centered-residue conditions, then wrote the complete packet. A separately tasked proof auditor independently read the final note and checked the general prime reductions, all 21 table entries, all four residual certificates, actual capacities, sign-orbit coverage, and the exceptional inverse family. A clerical raw-coordinate sum at the first `p=11` certificate was corrected before the final audit; its modular zero-sum and length were unchanged.

Independent final written-note audit: passed for both complete layers `c=2,3` throughout their stated prime range. The coordinating researcher and inverse specialist also independently reviewed the endpoint certificates. These are internal mathematical reviews, not external referee or novelty claims.

The finite table consists of written group identities at endpoints isolated by symbolic arguments. No companion enumeration, machine search, or numerical extrapolation supplies theorem authority.
