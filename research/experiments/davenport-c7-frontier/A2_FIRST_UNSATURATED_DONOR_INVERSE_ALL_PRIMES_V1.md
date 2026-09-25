# Type two: the first unsaturated donor has an exact all-prime inverse form

Status: **proved for every prime p>=7**. One missing new-value occurrence does not change the exact donor inverse classification. Both the saturated basis donor and the actual donor missing one `g` are covered. The small endpoints follow from the bounded-hole relations and explicit certificates, not a search over companions.

## 1. Exact theorem

Let `p=2H+1>=7`, `m=3H+1`, `u=H+1=2^{-1}`, and `s=(u,u,1)` in a basis `(e1,e2,g)`. For `epsilon in {0,1}`, put

\[
B_{K,\epsilon}=e_1^{p-1}e_2^{p-1}g^{p-1-\epsilon}s^K.
\]

For `3<=K<=H+1`, the sequence `B_{K,epsilon} y^{p-2}` is short-free below `m` if and only if

1. `y=(A,-A,1)`, `A!=0`; or
2. `y=(+/-3^{-1},-/+3^{-1},2)` and either `K=3` or `(p,K)=(11,4)`.

For `K>=H+2`, no value `y` gives a short-free extension by `p-2` copies.

## 2. What the previous two-hole lemmas already prove

For `p>=11`, the hypotheses of both bounded-hole donor lemmas hold with `b=2`. Thus all coordinates of `y=(A,B,C)` are nonzero, and

\[
J=\{j:1\le[jA]_p,[jB]_p\le H\}
\]

has size at most two. Its members outside `{2,...,p-2}` lie in `{1,-1}`, with at most one such member. Its only possible member inside the core is `C^{-1}`.

The exact two-hole corollary of `MULTIPLICATIVE_HALF_INTERVAL_LINEAR_STABILITY_V1.md` gives `A+B=0` for every `p>=17`. At `p=7`, the fully saturated basis lemma still proves nonzero coordinates and the same bound on `J`. The next section checks the nonzero-coordinate endpoint for the missing-`g` donor as well.

## 3. The missing-argument endpoint at p = 7

Only a zero coordinate needs an extra argument. A zero third coordinate leaves all formal saturated completions available; the earlier complementary argument excludes it. A value on the `g` line is excluded by a singleton completion, or by `g^7` using two new copies when `y=g`.

By swapping the axes, it remains to consider `y=(0,D,C)`, with `DC!=0`. Put `T=1-D-C`. The complementary core is `{2,3,4,5}={+/-2,+/-3}`. If the unavailable completion indices `+/-C^{-1}` do not remove a whole pair from this core, at least four available indices contradict the two possible lengths `10,11`, as before. If a pair is removed, those two lengths at the remaining pair force

- `C=3,4` and `T=+/-1`; or
- `C=2,5` and `T=+/-2`.

These implications follow by reducing `L_j==jT` to `{10,11}=={3,4}` modulo seven, at the remaining indices `+/-3` or `+/-2`, respectively. The zero slope is impossible since neither length is a multiple of seven.

Substituting `D=1-C-T` gives exactly the following eight formal possibilities. All but one have a short singleton basis completion; the remaining one uses three copies. No light occurrence is needed.

| `(D,C)` | Power `j` | Required `(e2,g)` counts | Length |
|---|---:|---|---:|
| `(3,4)` | 1 | `(4,3)` | 8 |
| `(5,4)` | 1 | `(2,3)` | 6 |
| `(4,3)` | 1 | `(3,4)` | 8 |
| `(6,3)` | 1 | `(1,4)` | 6 |
| `(4,2)` | 1 | `(3,5)` | 9 |
| `(1,2)` | 3 | `(4,1)` | 8 |
| `(1,5)` | 1 | `(6,2)` | 9 |
| `(5,5)` | 1 | `(2,2)` | 5 |

Every power is at most five and every `g` count at most five. Thus all coordinates are nonzero at this endpoint. The two donor substitutions, which themselves repair the missing-`g` seams, now give the same bound on `J`.

## 4. Bounded signed products classify the nonplane endpoints p = 11,13

Suppose `A+B!=0` and set `gamma=-B/A`. Its distance from the half-interval is `d=|J|<=2`. The centered representatives of `gamma,gamma^{-1}` therefore have magnitude at most five.

At `p=11`, products congruent to one in `[-25,25]` are `-21,-10,1,12,23`. The nonidentity feasible products of two magnitudes at most five are only `-10,12`. At `p=13`, the corresponding possibilities are `-25,-12,1,14`, of which the nonidentity feasible products are `-25,-12`. The multiplier `-1` is excluded by its distance `H`.

Counting the indicated short intervals leaves precisely these distance-two multiplier families:

| p | `gamma` with `d<=2`, other than 1 | Representatives for `theta=B/A=-gamma`, up to inversion | `{i in [1,H]: [theta i]_p in [1,H]}` |
|---:|---|---|---|
| 11 | `-2,3,4,5` | `2`, `-3` | `{1,2}`, `{2,3}` |
| 13 | `3,-4` | `-3` | `{3,4}` |

For completeness, at `p=11` the other signed candidates have distance three: `2,-3,-4,-5`. At `p=13`, the candidates `-3,4` have distance four and `+/-5` have distance three. The listed counts follow by placing the few multiples in `[1,H]`; the product argument proves that no other multiplier has been omitted. Inversion of `theta` is precisely exchange of the first two coordinates.

In each retained family `|J|=2`. Therefore one member is `+/-1` and the other is `C^{-1}`. If the last column is `{v,w}`, the possibilities are exactly

`A=+/-v, C=A/w`, or `A=+/-w, C=A/v`.

Thus, up to first-coordinate exchange and simultaneous negation, the only nonplane values are

\[
\begin{array}{ll}
p=11:&(1,2,6),(2,4,2),(2,5,8),(3,2,7);\\
p=13:&(3,4,4),(4,1,10).
\end{array}
\]

Each sign is eliminated by the following singleton certificate. The displayed counts mean `y s^z e1^a e2^d g^w`; their coordinate sum is zero modulo the indicated prime.

| p | Actual y | `z` | `(a,d,w)` | Length |
|---:|---|---:|---|---:|
| 11 | `(1,2,6)` | 1 | `(4,3,4)` | 13 |
| 11 | `(10,9,5)` | 2 | `(0,1,4)` | 8 |
| 11 | `(2,4,2)` | 1 | `(3,1,8)` | 14 |
| 11 | `(9,7,9)` | 2 | `(1,3,0)` | 7 |
| 11 | `(2,5,8)` | 1 | `(3,0,2)` | 7 |
| 11 | `(9,6,3)` | 2 | `(1,4,6)` | 14 |
| 11 | `(3,2,7)` | 1 | `(2,3,3)` | 10 |
| 11 | `(8,9,4)` | 2 | `(2,1,5)` | 11 |
| 13 | `(3,4,4)` | 3 | `(2,1,6)` | 13 |
| 13 | `(10,9,9)` | 2 | `(2,3,2)` | 10 |
| 13 | `(4,1,10)` | 3 | `(1,4,0)` | 9 |
| 13 | `(9,12,3)` | 2 | `(3,0,8)` | 14 |

All use at most three light terms, at most `p-2` copies of `g`, and have length below `m=16` or `19`. Axis exchange supplies the other orderings. Hence `A+B=0` at both primes.

## 5. The nonplane endpoint p = 7

All coordinates are nonzero by Sections 2--3. The ratio `theta=B/A` cannot be one because that would give `|J|=3`; exclude `theta=-1` since it is already the desired plane. Up to inversion, the other ratios are `2,3`.

For `theta=3`, the low-half indices are `{1,3}`. Exactly as above, the two-hole seam condition leaves, up to sign, only `(1,3,5)` and `(3,2,3)`. Their four signed singleton completions are:

| Actual y | `z` | `(e1,e2,g)` counts | Length |
|---|---:|---|---:|
| `(1,3,5)` | 1 | `(2,0,1)` | 5 |
| `(6,4,2)` | 2 | `(0,2,3)` | 8 |
| `(3,2,3)` | 1 | `(0,1,3)` | 6 |
| `(4,5,4)` | 2 | `(2,1,1)` | 7 |

For `theta=2`, the low-half index is only `{1}`. Thus `J={A^{-1}}` must either lie outside the core, giving `A=+/-1`, or be its unique allowed seam, giving `C=A`.

If `C=A` and `A!=1`, choose `j=[-A^{-1}]_7` in `[1,5]`. Then `y^j e1 e2^2 g` is zero-sum and has length `j+4<=9`. For `A=C=1`, use `y s^3 e1 g^3`, of length eight.

If `A=1,C>=2`, use `y s e1^2 e2 g^{6-C}`, of length `11-C<=9`; the case `C=1` was just covered. If `A=-1` and `1<=C<=5`, use `y s^2 e2 g^{5-C}`, of length `9-C<=8`; the remaining `C=6=A` was also covered. Every displayed occurrence fits the missing-`g` donor. Axis exchange covers the inverse ratio.

This proves the plane restriction at seven without a vector sweep.

## 6. Complete classification and top capacity

The plane is now forced for every prime. Since `p-2>=H-1`, the exact half-power plane theorem, including its missing-`g` extension, proves precisely the two families in Section 1 for `3<=K<=H+1`. Its all-subsequence converse supplies sufficiency; a necessary coordinate restriction alone is not used as a converse.

If `K>=H+2` and `H` is odd, the donor-only sequence

`s^{H+2} e1^{(H-1)/2} e2^{(H-1)/2} g^{H-1}`

is zero-sum of length `m-1`. If `H` is even, take the subdonor with `K=H+1` to force `y=(A,-A,1)`; no exceptional family can occur there at an even `H>=4`. The exact top plane theorem for `g^{p-2}s^{H+2}` then permits at most `H/2` copies of any such value, whereas `p-2=2H-1>H/2`. Thus the extension is impossible for either donor.

## 7. New complete boundary consequences

- On the rank-three first unsaturated face `b=2`, every `1<=c<=H-1` has the exact inverse form above with `K=c+2`; the row `c=H` is now impossible for every prime for which it occurs.
- On the rank-two top-overlap face, the smaller new multiplicity `r=2` is now impossible for every prime: its donor has `K=H+2` and its high value has exactly `p-2` copies. Together with the older saturated `r=1` closure, every surviving top row has `r>=3`.

The first-unsaturated mixed companions with smaller shared overlap still require a separate argument; this theorem does not declare them all eliminated. It supplies the exact inverse gate for that argument, including the genuine `p=11,K=4` exception.

The proof was checked locally at the signed-product possibilities, core seam equalities, all displayed coordinate sums, and both exact converse families. No brute-force classification, separately tasked review, or external referee approval is claimed.
