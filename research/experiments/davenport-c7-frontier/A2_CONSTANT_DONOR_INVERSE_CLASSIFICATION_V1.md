# Constant-donor inverse classification with the exact exceptional family — V1

Status: **proved structural classification and independently internally audited**. Three copies of the light donor already force two precise families. Four copies remove the second family except at one prime, where five copies remove it. The converse is proved, including the exceptional family: these are exact normal forms, not only necessary restrictions.

This strengthens `A2_SATURATED_DONOR_INVERSE_NORMAL_FORM_V1.md` by replacing its `H+1` light-donor occurrences with a variable count as small as three. It still concerns a full `p-1`-fold power of one value, and it does not assert the full first-corridor theorem or a generalized Davenport formula.

## 1. Exact prime-uniform theorem

Let `p=2H+1>=7` be prime, `m=p+H=3H+1`, `u=H+1=2^(-1)` in `F_p`, and `s=(u,u,1)` in the basis `(e1,e2,g)` of `C_p^3`. For

`3<=K<=H+1`,

set

`B_K=e1^(p-1)e2^(p-1)g^(p-1)s^K`.

For any `y in C_p^3`, the sequence `B_K y^(p-1)` has no nonempty zero-sum of length below `m` if and only if one of the following holds:

1. `y=(A,-A,1)` for some `A!=0`.
2. `y=(3^(-1),-3^(-1),2)` or its first-two-coordinate swap, and either `K=3` or `(p,K)=(11,4)`.

All inverses are in `F_p`; `3` is invertible because `p>=7`. There are no companion, atomicity, or new-support hypotheses.

Consequently four light-donor copies suffice for the single normal form `(A,-A,1)` at every prime `p>=7` except `p=11`, where five copies suffice. The exact exception with four copies at `p=11` is retained and proved to survive.

## 2. Structural reduction with three light-donor copies

Assume `B_K y^(p-1)` is short-free and write `y=(A,B_0,C)`. The zero-coordinate proof in Section 2 of `A2_SATURATED_DONOR_INVERSE_NORMAL_FORM_V1.md` uses only the saturated basis and `y^(p-1)`, so every coordinate is nonzero.

Put `T=1-A-B_0-C`.

If `T=0`, the four-entry Bernoulli pairing and the one-`s` certificate in Section 4 of that note leave precisely `y=(A,-A,1)`. This argument requires only one available `s` and is unchanged here.

Suppose `T!=0`. The pure saturated lengths

`L_j=j+[-jA]_p+[-jB_0]_p+[-jC]_p`

have exactly the two global patterns proved in Sections 2--3 of `A2_RANK3_EXTREME_FULL_ELIMINATION_V1.md`. The argument only needs saturated completion and complementary indices, with no `s` count at all. Its external ingredient is the attributed six-entry Bernoulli-pairing theorem, Proposition 1.8 of Batyrev--Hofscheier, [arXiv:1004.3411, p. 3](https://arxiv.org/pdf/1004.3411), with every hypothesis mapped in the cited note.

In the centered pattern, pairing restricts `y` to a permutation of

`(1,b,-2b)`, `(2,b,-b)`, or `(u,b,-b)`.

Every nonexceptional certificate in Sections 5--6 of the full-elimination note uses at most two `s` copies. They remain available here. The exceptional cases sent there to a plane lemma are only the following plane forms:

`y=(A,-A,2)` or `y=(A,-A,u)`, with `A!=0`.

This list includes the placements with distinguished coordinate `2` or `u` in the third coordinate, and all exceptional half-interval multipliers. No restricted-donor plane lemma is assumed at this point.

In the anomalous pattern, all substitutions in Sections 7--8 of the full-elimination note use at most three `s` copies: first `s^2`, then `s`, and finally `s^3`. They again force the normalized tuple `(j,H,v,1,H,1)`, with the two endpoint conditions at `p-3` and `p-5` contradicting every `p>=11`. The sole residual `p=7` tuple gives `y=(1,3,5)` or its swap; the one-`s` certificate `y s e1^2 g`, or its swapped version, is short. Thus the entire anomalous pattern is already impossible for `K>=3`.

We have rigorously reduced every remaining `T!=0` value, without any large light-donor assumption, to the two plane forms displayed above.

## 3. Two light copies exclude the third coordinate `u`

Let `y=(A,-A,u)`, with `A!=0`. The target third coordinate of `-y` is `H`. The sequence

`y s^2 e1^[-A-1]_p e2^[A-1]_p g^(H-2)`             (1)

is zero-sum. For every nonzero `A`,

`[-A-1]_p+[A-1]_p=p-2`.

For example, putting `a=[A]_p in {1,...,p-1}` gives the two integers `p-a-1` and `a-1`. Thus (1) has length

`1+2+(p-2)+(H-2)=m-1`.

Every count is nonnegative and available. Hence only `y=(A,-A,2)` remains in the `T!=0` slice.

## 4. Three light copies leave exactly `A=+/-1/3`

Let `y=(A,-A,2)` and put `j=H-1`. The third coordinate of `-jy` is `3`. Using `s^3` and no `g` leaves the two saturated counts

`[-jA-3u]_p`, `[jA-3u]_p`.

The standard pair-cost identity makes their sum `p-3` unless

`min([jA]_p,[-jA]_p)=H`.

Indeed, for odd count `3` the low-cost criterion is `3<=2(H-d)+1`, which holds exactly when the centered magnitude `d` is at most `H-1`. In the low case, the resulting sequence has length

`j+3+(p-3)=p+H-1=m-1`.

Therefore a survivor satisfies `jA=+/-H`, and hence

`A=+/-H/(H-1)=+/-3^(-1)`.

The last identity follows from `H=-u` and `H-1=-3u` modulo `p`. This proves the necessity of the two exceptional values when `K=3`.

## 5. Four copies eliminate the exception except at `p=11`

Assume `K>=4` and `A=+/-3^(-1)`. Put `j=H-2`, which is positive for every `p>=7`. The third coordinate of `-jy` is `5`. Use four copies of `s` and one copy of `g`. The pair-cost identity gives pair sum `p-4` unless the centered magnitude of `jA` is `1`.

In the low case, the length is

`j+4+1+(p-4)=m-1`.

Since `j=H-2=-5/2` modulo `p`, one has `jA=+/-5/6`. Centered magnitude `1` would imply `5=+/-6` modulo `p`. The congruence `5=6` is impossible; `5=-6` forces `p=11`. Thus for every `p!=11`, the displayed sequence eliminates the second family as soon as `K>=4`.

At `p=11`, one has `H=5` and `A=+/-4`. If `K>=5`, use `j=H-2=3`, five copies of `s`, and no `g`. Here `u=6`, `5u=8` modulo `11`, and the two saturated counts are `[-3A-8]_11,[3A-8]_11`, whose sum is `6`. For `A=4` they are `2,4`; the opposite sign exchanges them. This gives total length

`3+5+6=14<m=16`.

We have proved all necessity statements in Section 1, including the precise `(p,K)=(11,4)` residual possibility.

## 6. Converse for the main family

For `y=(A,-A,1)`, with `A!=0`, the complete proof in Section 6 of `A2_SATURATED_DONOR_INVERSE_NORMAL_FORM_V1.md` gives a lower bound `2p-z` for every nonempty zero-sum using `z` copies of `s`. It checks both the case with positive `y` count and donor-only zero-sums. As `z<=K<=H+1`, this is at least `m`.

This proves the main family survives throughout the stated range of `K`.

## 7. Converse for the exceptional family at three copies

Let `K=3` and `y=(A,-A,2)`, where `A=+/-3^(-1)`. Consider an arbitrary nonempty zero-sum, with counts `j` of `y`, `z` of `s`, `w` of `g`, and saturated counts `a,b` of `e1,e2`. All counts obey

`0<=j,w,a,b<=p-1`, `0<=z<=3`.

If `j=0`, the donor-only calculation gives minimum length at least `2p-z>=2p-3>=m`; a zero-sum with both `j=z=0` must be empty because all basis counts are below `p`.

Suppose `j>=1`. The first two equations force the usual pair-cost bound

`a+b>=p-z`.

Write the third-coordinate equation as

`2j+z+w=Np`,

where `N` is a positive integer. The total length satisfies

`j+z+w+a+b=Np-j+a+b>=(N+1)p-j-z`.                   (2)

If `N>=2`, then `j<=p-1`, `z<=3` give length at least `2p-2>=m`. If `N=1`, then `2j+z<=p`. To obtain length below `m`, (2) would require

`j+z>=H+2`.

For `z=0,1,2`, the constraint `2j+z<=p` instead gives `j+z<=H+1`. For `z=3`, the only possible strict-shortness candidate is `j=H-1`.

At this candidate, `jA=+/-H`; therefore the odd-count pair cost at `z=3` is the high value `2p-3`, not `p-3`. Its actual total length is

`p-j+(2p-3)=3p-H-2>m`.

Every potential zero-sum is therefore at least `m`. This proves that the exceptional family genuinely survives for every prime `p>=7` when `K=3`.

## 8. Converse for the four-copy exception at `p=11`

Now let `(p,K)=(11,4)`, `H=5`, `m=16`, and `A=+/-4`. The preceding argument remains valid with `z<=4`. Donor-only zero-sums have length at least `2p-4=18>=m`. If `j>=1` and `N>=2`, (2) gives length at least `2p-3=19>=m`.

For `N=1`, potential strict shortness still requires `j+z>=7` and `2j+z<=11`. The only possible pairs are

`(j,z)=(4,3)` or `(3,4)`.

The first is the high odd-pair-cost candidate already excluded in Section 7. In the second, `jA=+/-1` modulo `11`, so the even count `z=4` is also high: the pair-cost condition `4<=2d` fails at `d=1`. Its pair sum is `2p-4=18`, which itself exceeds `m`. Thus there is no short zero-sum.

This proves the four-copy `p=11` exceptional family actually survives. It cannot be erased by a uniform four-copy argument.

## 9. Frontier interface and preserved barrier

For an exceptional rank-three type-two companion, the actual shared old donor is

`e1^(p-1)e2^(p-1)g^(p-1)s^(c+2)`.

Whenever the high new multiplicity is exactly `p-1`, the theorem applies with `K=c+2` if `1<=c<=H-1`. It gives a structural normal form across every such overlap, including the smallest one. It does not require the other new multiplicity to be one.

The theorem alone does not eliminate the remaining main family: its sufficiency is an explicit obstruction to any pure-power donor attack. For these rows, the next proof step must use the other new value and its actual multiplicity. Likewise the second family at `c=1`, and the `p=11,c=2` exception, are real partial-donor survivors, not full companion counterexamples.

When `c=H` is available, the donor has one more `s` occurrence than the stated upper range; one may take the subdonor with `K=H+1` to obtain the main necessary family, but its actual elimination requires the extra occurrence or a mixed argument. This distinction preserves the theorem's exact converse range.

## 10. Verification and internal provenance

The classification uses only exact residue identities, the established Bernoulli theorem, half-interval invariance, and symbolic occurrence vectors. No enumeration of primes, values, or hypothetical companions supplies the proof. The special prime `11` arises from the exact congruence `5=-6`, and its residual family receives a full all-subsequence sufficiency proof.

The coordinating researcher identified the four/five-copy improvement; the inverse specialist checked that all earlier spectral and anomalous reductions need at most three light copies, proved the exact three-copy converse, and extended the converse at `(p,K)=(11,4)`. These are internal roles and provenance, not external referee or novelty claims.

Independent full internal audit: GREEN. A separately tasked auditor checked the exact three-copy dependency reduction, the two-, three-, four-, and five-copy occurrence certificates, the unique exceptional prime, and both all-subsequence converse proofs. The coordinating researcher also independently checked the full note. The generalized Davenport formula and full first-corridor theorem remain unproved here.
