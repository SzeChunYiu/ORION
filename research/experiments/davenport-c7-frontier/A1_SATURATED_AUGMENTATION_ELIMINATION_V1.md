# Type-one saturated donor: exact inverse classification and sharp threshold — V1

Status: **proved prime-uniform inverse classification and sharp augmentation threshold**, independent of the companion relation or atomicity. For every prime `p>=5` and every positive sum-direction capacity, the theorem identifies exactly which fourth saturated values preserve the first-corridor short-zero boundary. Increasing that capacity through one explicit threshold empties the entire class. This removes a whole high-multiplicity boundary family, but does not prove the full corridor or a generalized Davenport value.

## 1. General statement

Let `p=2H+1>=5` be prime, let `(f1,f2,f3)` be a basis of `C_p^3`, and put

`s=f1+f2+f3`, `m=p+H`, `z=floor((p+1)/4)+1`.

For an integer `K>=1` and a value `y in C_p^3`, write

`F_K(y)=f1^(p-1) f2^(p-1) f3^(p-1) s^K y^(p-1)`.

> **Exact inverse theorem.** The sequence `F_K(y)` contains no nonempty zero-sum of length less than `m` if and only if both of the following conditions hold:
>
> `1<=K<=floor((p+1)/4)`,
>
> `y` is a coordinate permutation of `(1,b,-b)` for some `b!=0` in `F_p`.

Sections 2--4 prove the necessary coordinate form using only one available `s`. Section 5 proves the upper-capacity exclusion below, and Section 5.1 proves the complete converse. Thus the capacity threshold is exact, not only a sufficient condition for exclusion.

> **Saturated-augmentation theorem.** For every `y in C_p^3`, the sequence
>
> `f1^(p-1) f2^(p-1) f3^(p-1) s^z y^(p-1)`
>
> contains a nonempty zero-sum of length less than `m`.

Additional copies of `s` or other values preserve this conclusion. The theorem does not assume that `y` is new, that the sequence is zero-sum, or that it belongs to a maximal-pair configuration.

Write `y=(A,B,C)` in the displayed basis. Throughout, `[a]_p` is the least nonnegative residue.

## 2. Zero coordinates are impossible

Suppose exactly `q` coordinates of `y` are nonzero. If `q=0`, a single copy of `y` is a zero-sum. Otherwise for every `1<=j<=p-1` the saturated basis supplies a zero-sum of length

`L_j=j+[-jA]_p+[-jB]_p+[-jC]_p`.

Its complementary index satisfies

`L_j+L_(p-j)=(q+1)p`.

Put `T=1-A-B-C` in the field. If `T!=0`, the congruences `L_j==jT` give `p-1` distinct integers. Their range is at least `p-2`. Complementarity therefore gives

`min_j L_j <= ((q+1)p-(p-2))/2 = qp/2+1`.

If `q<=2`, this is at most `p+1<m`, because `H>=2`. If `T=0`, all the positive lengths are multiples of `p`; complementarity with `q<=2` implies that some length is at most `p`. Thus every zero coordinate already proves the theorem.

Hence a hypothetical short-free sequence must have `ABC!=0`.

## 3. A single sum-direction term forces an affine equation

For `ABC!=0`, all three basis completion counts in `L_j` are positive. Replace one copy of each basis value by one `s`. The resulting occurrence-valid zero-sum has length `L_j-2`.

Under the contrary hypothesis that no nonempty zero-sum has length below `m`, this gives, for every `j`,

`L_j>=m+2`.

Now `L_j+L_(p-j)=4p`, so every `L_j` belongs to the integer interval

`[m+2, 4p-m-2]`.

Its width is `4p-2m-4=p-3`, and it contains only `p-2` integers. If `T!=0`, the `p-1` distinct lengths cannot fit in this interval. Consequently

`A+B+C=1`.

All `L_j` are now multiples of `p`. Since `p<m+2<=2p` and `2p<=4p-m-2<3p` for `p>=5`, the only possibility is

`L_j=2p` for every `1<=j<=p-1`.                     (1)

This interval argument is prime-uniform. It does not enumerate possible values of `y`.

## 4. Bernoulli pairing gives the exact candidate family

Use the periodic Bernoulli function `B1(t)={t}-1/2` away from integers, with `B1(t)=0` at integers. Proposition 1.8 of Batyrev--Hofscheier states that a tuple of units modulo `n` whose Bernoulli sum vanishes at every integer multiplier can be partitioned into pairs summing to zero modulo `n`. The four-entry case is credited there to Morrison--Stevens. [Batyrev--Hofscheier, Proposition 1.8](https://arxiv.org/pdf/1004.3411).

Apply that theorem to the four units `(1,-A,-B,-C)` modulo `p`. Equation (1) proves the Bernoulli identity at each nonzero multiplier; the identity at multiples of `p` follows from the definition. Periodicity covers all integers.

The entry `1` must pair with a negative coordinate of `y`, and the remaining two coordinates must be opposite. Thus, after permuting the basis,

`y=(1,b,-b)`, `b!=0`.                              (2)

Basis permutations preserve the saturated donor and `s`.

## 5. An interval intersection eliminates every candidate

For the chosen `z`, one has `2z>H+1` and `z<p/2`. Consider

`J={1,...,p-z}`, `I={z,...,p-z}`

as subsets of the nonzero residues. Their sizes are `p-z` and `p-2z+1`. If

`p+2>3z`,                                           (3)

then `bJ` intersects `I` by cardinality. Choose `j in J` with `v=[jb]_p in I`.

Condition (3) holds for all primes `p>=5` except the equality case `p=7`. Indeed, if `p=4q+1`, then `z=q+1` and `p+2-3z=q>0`. If `p=4q+3`, then `z=q+2` and `p+2-3z=q-1`, which is positive for `p>=11`.

For `p=7`, `z=3`. If the intersection were empty, the two four-element sets would satisfy

`b*{1,2,3,4}={1,2,5,6}` in `F_7`.

Summing gives `3b=0`, a contradiction. Thus the required `j` exists in every case without a prime sweep or a list of coordinate witnesses.

For (2), the completion of `j` copies of `y` has basis counts

`p-j`, `p-v`, `v`.

All three are at least `z`. Replace `z` copies of each basis value by `z` copies of `s`. The resulting zero-sum is

`s^z y^j f1^(p-j-z) f2^(p-v-z) f3^(v-z)`.

Every count is nonnegative and available. Its exact length is

`2p-2z < 2p-(H+1)=p+H=m`.

This contradiction proves the saturated-augmentation theorem.

### 5.1. Converse and sharpness of the capacity threshold

Assume `1<=K<=floor((p+1)/4)` and `y=(1,b,-b)`, where `b!=0`. Coordinate permutations preserve the donor and `s`, so this treats every form in the exact inverse statement.

Consider a nonempty zero-sum subsequence of `F_K(y)`. Let its `y` count be `j`, its `s` count be `ell`, and its three basis counts be `a_1,a_2,a_3`. Thus

`0<=j,a_i<=p-1`, `0<=ell<=K<p`.

If `j>=1`, the first coordinate makes

`j+a_1+ell`

a positive multiple of `p`, hence at least `p`. Adding the second and third coordinate equations makes

`a_2+a_3+2ell`

a multiple of `p`. This multiple is positive: it is immediate if `ell>0`; if `ell=0`, then `jb!=0` and the forced counts are `a_2=[-jb]_p>0` and `a_3=[jb]_p>0`. Consequently the total length satisfies

`j+a_1+a_2+a_3+ell`

`=(j+a_1+ell)+(a_2+a_3+2ell)-2ell`

`>=2p-2ell>=2p-2K>=m`.

The last inequality is equivalent to `2K<=H+1`, which is exactly ensured by `K<=floor((p+1)/4)`.

If `j=0` and `ell=0`, independence of the basis and the counts below `p` force all counts to vanish, contradicting nonemptiness. If `j=0` and `ell>=1`, the three forced basis counts are all `p-ell`. The resulting length is

`3p-2ell>=2p-2K>=m`.

These cases exhaust all subsequences, proving that every stated value actually preserves short-freeness throughout the claimed capacity range.

Conversely, if `F_K(y)` is short-free for any `K>=1`, Sections 2--4 apply verbatim because they use only one copy of `s`. They force the displayed coordinate form. If `K>=z`, the sequence contains the donor of the saturated-augmentation theorem and is not short-free. This completes both directions of the exact inverse theorem for every integer `K>=1`.

In particular, at `K=z-1` every value of the stated family survives, while at `K=z` no value survives. These partial donor extensions are exact lower-capacity obstructions; they are not asserted to extend to full zero-sum companions.

## 6. First-corridor consequence

For canonical type `a=1`, write the maximal atom as

`U=f1^(p-1) f2^(p-1) f3^(p-1) s`.

A rank-two light-share companion with the high multiplicity `p-1` has the shape

`V=s^c x^r y^(p-1)`, `r=H+1-c`.

The actual product contains the donor from Section 1 whenever

`c>=floor((p+1)/4)`.

> **Boundary-family corollary.** Every such type-one companion with
>
> `floor((p+1)/4)<=c<=H`
>
> is impossible. Equivalently, this eliminates the `t=p-1` boundary with
>
> `1<=r<=H+1-floor((p+1)/4)`.

In particular, the top singleton row `(c,r,t)=(H,1,p-1)` is empty. The same proof applies to any configuration with the actual donor and saturated extra value; the displayed companion relation is not used.

The full type-one boundary includes values of `t` below `p-1`, and those are not eliminated by this theorem. Type-two donors satisfy a different relation and are treated separately. The all-prime first-corridor and all-`k` Davenport targets remain open.

## 7. Review and attribution

The root derived the augmentation argument, and the rank-two proof agent independently checked the singleton replacement, exact interval cardinality, pairing hypotheses, intersection criterion, and occurrence vector for `p>=11`. The proof-audit agent then checked the complete elimination proof for every `p>=5`, including the `p=5,7` endpoints in Section 5, and derived the matching converse and exact inverse statement in Section 5.1. The rank-two proof agent independently read the resulting file and verified the complete converse, both positivity cases, the exact threshold, and the endpoint extension. The Bernoulli theorem is an established donor; no novelty or priority assertion is made.

Full independent internal audit: passed for the exact inverse classification and sharp threshold throughout the stated range `p>=5`, `K>=1`. No external referee approval is asserted.
