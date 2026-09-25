# Type-two rank-three one-share saturated boundary: all-prime elimination — V1

Status: **proved for every prime `p>=7`, with independent internal proof audit**. The exact constant-donor inverse theorem leaves two families. One fixed actual power of the other new value eliminates both for every `p>=11`; four explicitly checked sign orbits complete `p=7`.

This closes the whole `c=1` row with one new multiplicity equal to `p-1`. It does not, by itself, close unsaturated rank-three rows, the complete first-corridor theorem, or the generalized Davenport formula.

## 1. Statement and exact normal forms

Let `p=2H+1>=7` be prime, `u=H+1=2^(-1)` in `F_p`, and `m=p+H=3H+1`. In the basis `(e1,e2,g)`, put `s=(u,u,1)` and

`U=e1^(p-1)e2^(p-1)g^(p-2)s^2`.

Consider a zero-sum companion

`V=s g x^r y^(p-1)`, `r=H-1`.

The combined old-support donor is

`B_3=e1^(p-1)e2^(p-1)g^(p-1)s^3`.

> **Theorem.** The product `UV` contains a nonempty zero-sum of length at most `m-1`.

Assume otherwise. The exact theorem in `A2_CONSTANT_DONOR_INVERSE_CLASSIFICATION_V1.md` applies with `K=3` and forces one of exactly two forms:

`y=(A,-A,1)`, `A!=0`,                                (1)

or

`y=(3^(-1),-3^(-1),2)` and its `e1,e2` swap.          (2)

Both inverse forms genuinely survive the pure-power donor test; neither may be dropped without using the other value. The companion relation is

`r x=y-s-g`.                                         (3)

As `r=H-1=-3/2` modulo `p`, it is a nonzero field element. The use of (3) to compute coordinates below does not replace actual occurrence counts by field residues.

## 2. Every prime at least eleven: the main family

Assume `p>=11` and (1). The sum of the first two coordinates and the third coordinate of the right side of (3) are both `-1`. Consequently

`x1+x2=x3=2/3` in `F_p`.

Choose the actual positive occurrence count

`a=H-4=r-3`.

Since `H>=5`, one has `1<=a<=r`. Also `a=-9/2` modulo `p`, so

`a*(2/3)=-3`.

Thus `x^a s^3` has third coordinate zero and first two coordinates summing to zero. Write its first coordinate as `P=a x1+3u`; its second is then `-P`. The sequence

`x^a s^3 e1^[-P]_p e2^[P]_p`                         (4)

is zero-sum.

If `P=0`, the saturated completion has length zero; otherwise it has length exactly `p`. Every saturated count is at most `p-1`, and all three actual `s` occurrences are present in `B_3`. Therefore (4) is a nonempty available subsequence of length at most

`a+3+p=p+H-1=m-1`.

This contradicts short-freeness throughout the main family.

## 3. Every prime at least eleven: the exceptional family

Assume now (2). Equation (3) gives

`x3=0`, `x1+x2=2/3`.

Use the same positive count `a=H-4=r-3`. Put

`P=[-a x1]_p`, `Q=[-a x2]_p`.

Their sum is congruent to `3` modulo `p`. Since `0<=P,Q<=p-1`, their ordinary sum is either `3` or `p+3`. Therefore

`x^a e1^P e2^Q`                                      (5)

is an available nonempty zero-sum of length at most

`a+p+3=m-1`.

Its third coordinate is already zero; no `g` or `s` occurrences are needed. This eliminates the whole second inverse family for every `p>=11`.

## 4. The endpoint `p=7` has four sign orbits

Here `H=3`, `m=10`, `r=2`, and `s=(4,4,1)`. The main family has the three centered magnitudes `|A|=1,2,3`; changing the sign of `A` exchanges `e1,e2`. The second inverse family has `A=+/-3^(-1)=+/-5`, which is the orbit represented by `A=2`.

Equation (3), now with `r=2`, gives each displayed `x` exactly. The following table supplies one occurrence-valid zero-sum for every orbit:

| Inverse family | Representative `y` | Forced `x` | Zero-sum subsequence | Length |
|---|---|---|---|---:|
| Main, `A=1` | `(1,6,1)` | `(2,1,3)` | `x s e1 e2^2 g^3` | 8 |
| Main, `A=2` | `(2,5,1)` | `(6,4,3)` | `x e1 e2^3 g^4` | 9 |
| Main, `A=3` | `(3,4,1)` | `(3,0,3)` | `x e1^4 g^4` | 9 |
| Exceptional, `A=2` | `(2,5,2)` | `(6,4,0)` | `x e1 e2^3` | 5 |

Every row has zero group sum by direct coordinate addition modulo `7`. All lengths are below `m=10`.

The capacities are `x:2`, `y:6`, `s:3`, and `e1,e2,g:6` each. Every certificate uses exactly one `x`, no `y`, at most one `s`, at most four copies of either first basis value, and at most four `g`. Thus none relies on a surplus occurrence. Swapping `e1,e2` in each row covers the opposite sign. These are all possibilities because the inverse theorem already supplied the exhaustive two-family classification.

The table verifies explicitly stated certificates for the four normal-form orbits. It does not enumerate hypothetical companions to supply the all-prime proof.

## 5. Conclusion, mechanism, and review

The same actual power `x^(H-4)` resolves both inverse families uniformly for every `p>=11`. In the main family, three light-donor occurrences turn its coordinate sum into an opposite pair; in the exceptional family, its third coordinate is already zero and the first two target coordinates have a small sum. The occurrence count is always checked as an integer before its modular identity is used. The `p=7` endpoint has been treated separately and completely.

Hence the entire one-share saturated boundary is eliminated for every prime `p>=7`.

The coordinating researcher supplied the two-family fixed-power argument. The inverse specialist independently checked the coordinate identities, capacities, and scores, and supplied the four endpoint certificates. A separately tasked proof auditor independently checked both uniform branches and all four endpoint representatives. All three internal roles returned GREEN. This is internal mathematical review, not external referee approval or a novelty certification.

The exact constant-donor inverse theorem remains the external interface for arbitrary `y`; no affine plane condition has been imposed without proof. The full first-corridor theorem and the generalized Davenport equality are not claimed here.
