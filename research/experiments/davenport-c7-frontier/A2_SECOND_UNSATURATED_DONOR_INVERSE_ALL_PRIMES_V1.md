# Type two: an exact inverse form with two missing new-value occurrences

Status: **proved all-prime inverse theorem for the rank-three donor**, also covering the donor missing one `g` at every prime `p>=11`. The small endpoints are derived from half-interval distances and the positions of the missing indices; no companion enumeration is used.

## 1. The exact statement

Let `p=2H+1>=7`, `m=3H+1`, `u=H+1`, `s=(u,u,1)`, and

\[
B_{K,\epsilon}=e_1^{p-1}e_2^{p-1}g^{p-1-\epsilon}s^K,
\qquad\epsilon\in\{0,1\}.
\]

Assume `epsilon=0`, or `p>=11`. For `4<=K<=H+1`, the sequence `B_{K,epsilon} y^{p-3}` is short-free below `m` if and only if

1. `y=(A,-A,1)`, `A!=0`; or
2. `(p,K)=(11,4)` and `y=(4,7,2)` or `(7,4,2)`.

For `K>=H+2`, no value has a short-free extension by `p-3` copies, for either donor and every `p>=7`.

## 2. The three-hole information

For `p>=11`, both bounded-hole donor theorems apply with `b=3`. Every coordinate of `y=(A,B,C)` is nonzero, and

\[
J=\{j:1\le[jA]_p,[jB]_p\le H\}
\]

has size at most three. At most one member of `J` lies in the core `{3,...,p-3}`, and it must be `C^{-1}`. Outside the core, at most one member lies in each pair `{1,-1}` and `{2,-2}`.

Write `theta=B/A`, `gamma=-theta`. The distance `d(gamma)` from the multiplicative half-interval equals `|J|`, and the signed centered representatives of `gamma,gamma^{-1}` have magnitude at most seven. The linear stability theorem already forces `gamma=1` for every `p>=31`.

At `p=23`, a nonidentity product of two signed integers of magnitude at most seven, congruent to one modulo 23, can only be `24=4*6`. The other possible representatives `-45,-22,47` do not have such factorizations. Thus only `gamma=+/-4,+/-6` remain. Multiplication by `4` sends exactly `1,2,6,7,8` of `{1,...,11}` back into that interval; multiplication by `6` sends exactly `1,4,5,8,9` back. Their distances are six, and those of their negatives five.

At `p=29`, the only nonidentity products are `30=5*6` and `-28=(-4)*7`. The positive multipliers `4,5,6,7` send respectively six, eight, eight, eight members of `{1,...,14}` back into the interval: their low-index sets are

`{1,2,3,8,9,10}`, `{1,2,6,7,8,12,13,14}`,

`{1,2,5,6,7,10,11,12}`, `{1,2,5,6,9,10,13,14}`.

All their signed distances are at least six. Therefore `A+B=0` already holds at 23 and 29. Only `p=7,11,13,17,19` require further work.

## 3. A missing-index pattern rule

For a fixed ratio `theta`, let

\[
E_\theta=\{v\in\{1,\ldots,H\}:[\theta v]_p\le H\}.
\]

Then `J=A^{-1} E_theta`. If `|E_theta|=3`, exactly two of its scaled members must occupy the outside pairs `+/-1,+/-2`, and the third must be the core seam `C^{-1}`. In particular two members of `E_theta` must be in the ratio `+/-2`. If `v` is the member corresponding to `+/-1`, then `A=+/-v`; the remaining member `w` gives `C=A/w`. This is an exact necessary rule, not just a cardinality estimate.

If `|E_theta|=2` and one member lies in the core, its partner lies at `+/-k` with `k in {1,2}`. The value `k y` is then one of the signed two-hole endpoint forms already derived in `A2_FIRST_UNSATURATED_DONOR_INVERSE_ALL_PRIMES_V1.md`. At 11 and 13 each such form has a singleton donor certificate of length at most 14. Replacing that singleton by `k<=2` actual copies increases the length by at most one: it remains below `m=16` or `19`. Those certificates use at most three light copies and at most `p-2` copies of `g`.

Inversion of `theta` is exchange of the first two coordinates. We use that symmetry explicitly below.

## 4. The endpoints p = 17,19

At 17, the centered-product bound leaves the feasible nonidentity products `18,-16,35`. Counting their multiplier intervals leaves only `gamma=3,5,6,7` at distance at most three. Up to inversion, the corresponding ratios and low-index sets are

`theta=-3: E={3,4,5}`,

`theta=-5: E={2,3,6}`.

The first set has no pair in ratio `+/-2`, contradicting Section 3. The second has only the pair `3,6`, so it forces, up to sign and axis exchange, `y=(3,2,10)`. Its positive and negative singleton certificates have respectively

`s_count=1, (e1,e2,g)=(5,6,6), length 19`,

`s_count=2, (e1,e2,g)=(2,1,8), length 14`.

Both are below `m=25`.

At 19, the possible products are `20,-18`; their distances leave only `gamma=3,-6`. The representative ratio `theta=-3` has `E={4,5,6}`, which has no pair in ratio `+/-2`. Section 3 rules it out. Thus both primes force the plane.

## 5. The distance-two cases at p = 11,13

The exact distance-two ratio lists from the two-hole proof remain valid:

- at 11, representatives `theta=2,-3`, with `E={1,2}` or `{2,3}`;
- at 13, representative `theta=-3`, with `E={3,4}`.

If there is a core member, the `k y` argument in Section 3 eliminates it. If both members lie outside, they must have ratio `+/-2` or its inverse. Only `p=11,theta=2,E={1,2}` permits this, and it forces `A=+/-1`, while leaving `C!=0` free.

For `y=(1,2,C)` at 11, if `C>=4`, the singleton certificate is

`y s e1^4 e2^3 g^{10-C}`,

of length `19-C<=15`. If `1<=C<=3`, use

`y^2 s e1^3 e2 g^{10-2C}`,

of length `17-2C<=15`. For `y=(10,9,C)` with `C<=9`, use `y s^2 e2 g^{9-C}`, of length `13-C<=12`. The remaining value `(10,9,10)` has `2y=(9,7,9)` and the short sequence `y^2 s^2 e1 e2^3`, of length eight. Every count fits the missing-`g` donor. Thus all distance-two nonplane possibilities are excluded.

## 6. The distance-three cases at p = 11,13

Counting the remaining multiplier intervals gives the complete representative lists

| p | `theta`, up to inversion | `E_theta` |
|---:|---|---|
| 11 | `3` | `{1,4,5}` |
| 11 | `-2` | `{3,4,5}` |
| 13 | `2` | `{1,2,3}` |
| 13 | `-2` | `{4,5,6}` |
| 13 | `5` | `{1,3,6}` |

For clarity, at 11 these correspond to `gamma=2,-3,-4,-5`; at 13 they correspond to `gamma=+/-2,+/-5,+/-6`. All other multipliers have distance zero, two as treated above, or more than three.

Applying Section 3 to the displayed pairs in ratio `+/-2` leaves, up to sign and axis exchange,

`p=11: (5,4,4),(3,5,9),(4,3,3)`,

`p=13: (1,2,9),(4,5,5),(3,2,3),(6,4,2)`.

These signed values have the following singleton certificates `y s^z e1^a e2^d g^w`:

| p | Actual y | `z` | `(a,d,w)` | Length |
|---:|---|---:|---|---:|
| 11 | `(5,4,4)` | 1 | `(0,1,6)` | 9 |
| 11 | `(6,7,7)` | 2 | `(4,3,2)` | 12 |
| 11 | `(3,5,9)` | 1 | `(2,0,1)` | 5 |
| 11 | `(8,6,2)` | 4 | `(1,3,5)` | 14 |
| 11 | `(4,3,3)` | 1 | `(1,2,7)` | 12 |
| 11 | `(7,8,8)` | 2 | `(3,2,1)` | 9 |
| 13 | `(1,2,9)` | 1 | `(5,4,3)` | 14 |
| 13 | `(12,11,4)` | 2 | `(0,1,7)` | 11 |
| 13 | `(4,5,5)` | 1 | `(2,1,7)` | 12 |
| 13 | `(9,8,8)` | 2 | `(3,4,3)` | 13 |
| 13 | `(3,2,3)` | 1 | `(3,4,9)` | 18 |
| 13 | `(10,11,10)` | 2 | `(2,1,1)` | 7 |
| 13 | `(6,4,2)` | 1 | `(0,2,10)` | 14 |
| 13 | `(7,9,11)` | 2 | `(5,3,0)` | 11 |

Each coordinate sum is zero, every length is below `m`, and every `g` count is at most `p-2`. The four-light certificate at `(11,(8,6,2))` is why this theorem retains the hypothesis `K>=4` rather than silently reducing it to three.

## 7. Nonzero coordinates at p = 7 with the saturated basis donor

Here `K>=4`, and the new value occurs four times. A value on a basis line has a short saturated singleton completion, and the zero vector is forbidden.

If exactly two coordinates are nonzero, write them as `alpha,beta`. At complementary indices `3,4`, the saturated lengths sum to 21 and must each be 10 or 11. Hence `T=1-alpha-beta` is `+/-1` modulo seven. If `alpha+beta=0`, the singleton basis completion has length eight. If `alpha+beta=2`, their positive representatives have sum two or nine; sum nine again gives a short singleton. Sum two forces `alpha=beta=1`.

The three possible placements are excluded by

`y=(1,1,0): y^2 s^3 g^4`,

`y=(1,0,1): y^2 s^3 e2^2 g^2`,

and the axis exchange of the second sequence. All have length nine. Therefore all three coordinates are nonzero. The two substitution argument now gives the same core-seam rule, even though its total bound `|J|<=3` is no longer a strict bound on the half-interval size.

## 8. Every nonplane ratio at p = 7

Up to inversion the nonplane ratios are `theta=1,2,3`.

For `theta=1`, `E={1,2,3}`. The rule in Section 3 leaves, up to sign, `(1,1,5),(2,2,2),(3,3,5)`. Their signed singleton certificates are

| Actual y | Light count | `(e1,e2,g)` counts | Length |
|---|---:|---|---:|
| `(1,1,5)` | 1 | `(2,2,1)` | 7 |
| `(6,6,2)` | 2 | `(0,0,3)` | 6 |
| `(2,2,2)` | 3 | `(0,0,2)` | 6 |
| `(5,5,5)` | 2 | `(1,1,0)` | 5 |
| `(3,3,5)` | 1 | `(0,0,1)` | 3 |
| `(4,4,2)` | 4 | `(1,1,1)` | 8 |

For `theta=3`, `E={1,3}`. If a core point occurs, either `y` or `2y` is one of the signed two-hole forms `(1,3,5),(3,2,3)` from the first-unsaturated inverse proof. Their singleton certificate lengths are at most eight, so replacing that singleton by at most two copies remains short. If both points lie outside, `A=+/-3`.

For `y=(3,2,C)`, the sequence `y s e2 g^{6-C}` has length `9-C<=8`. For `y=(4,5,C)` with `2<=C<=5`, use `y s^2 e1^2 e2 g^{5-C}`, of length `11-C<=9`. At `C=1`, use `y^2 s e1^2 g^4`, of length nine; at `C=6`, use `y^2 s e1^2 g`, of length six.

For `theta=2`, `E={1}`. Its only scaled point must be outside or at the seam, so either `A=+/-1,+/-1/2` or `C=A`.

If `C=A` and `A` is neither one nor four, choose `j=[-A^{-1}]_7<=4`. Then `y^j e1 e2^2 g` has length `j+4<=8`. At `A=C=1`, use `y s^3 e1 g^3`, of length eight; at `A=C=4`, use `y^2 s^3 e1 g^3`, of length nine.

For `A=1`, the first-unsaturated proof already supplied a singleton certificate for every `C`: `y s e1^2 e2 g^{6-C}` when `C>=2`, and the just displayed three-light certificate at `C=1`. For `A=-1`, its singleton formula `y s^2 e2 g^{5-C}` covers `C<=5`, and `C=6=A` was just handled.

For `A=1/2=4`, the value `2y` has its first two coordinates `(1,2)`. The preceding singleton certificates, expanded to two actual copies, remain short except when `C=1`; at that point `y=(4,1,1)` has the explicit certificate `y^3 s^4 e2^2`, of length nine. For `A=-1/2=3`, the value `2y` has first coordinates `(6,5)`. Its preceding singleton certificates all remain short after expansion; when its third coordinate is six, use `y^2 e1 e2^2 g`, of length six.

These formulas exhaust all nonplane ratios and nonzero coordinate choices at seven. Every power is at most four, every light count at most four, and all donor counts are available. Thus the plane is forced here as well.

## 9. Converse, top capacity, and consequences

The plane has now been proved in every stated donor range. Since `p-3>=H-1`, the half-power plane theorem and its missing-`g` version give precisely the two families in Section 1. Their previously proved full-power converses imply survival with the smaller power as well.

At `K>=H+2`, odd `H` has the old donor-only zero-sum of length `m-1`. For even `H`, the `H+1`-light subdonor forces the main plane family; the exact top-plane theorem then forbids its `p-3=2H-2>H/2` copies. This applies to either donor. In particular no claim about the unproved missing-`g`, `p=7,K=4` inverse classification is needed for the top-capacity conclusion.

This exact inverse gate applies to every rank-three second-unsaturated row `b=3`, with `K=c+2>=4`, including the genuine exception at `p=11,c=2`. It also eliminates the complete rank-two top-overlap case with smaller new multiplicity `r=3`: the high value has `p-3` copies and the actual donor has `K=H+2`.

The finite tables above are endpoints forced by signed products and index-hole patterns. They are written coordinate certificates, not outputs of a vector search. The proof was checked locally for the complete ratio lists, the one/two-copy expansion margins, the separate saturated-basis endpoint at seven, and every resource count. No separate external referee approval or full first-corridor theorem is claimed.
