# Type-two saturated rank-three boundary: complete elimination for c >= 4 — V1

Status: **proved prime-uniform elimination of every shared multiplicity `c>=4` on the saturated-new-value boundary**. The exact donor inverse form, circular-gap selector, and generalized remainder selector cover the entire prime range. Three small overlap values require elementary remainder distinctions; two explicit prime endpoints use the same occurrence formula as the general proof.

The overlaps `c=1,2,3`, unsaturated new-value multiplicities, the full first-corridor theorem, and the generalized Davenport formula are outside this complete-elimination claim.

## 1. Exact theorem and donor interface

Let `p=2H+1>=7` be prime, `u=H+1=2^(-1)` in `F_p`, `m=p+H`, and `s=(u,u,1)` in the basis `(e1,e2,g)` of `C_p^3`. Put

`U=e1^(p-1)e2^(p-1)g^(p-2)s^2`.

> **Theorem.** Let `4<=c<=H-1` and `r=H-c`. If
>
> `V=s^c g x^r y^(p-1)`
>
> is zero-sum, then `UV` contains a nonempty zero-sum of length at most `m-1`.

All multiplicities are actual occurrences. The proof applies in particular to the indicated first-corridor rank-three row; it does not require a further atomicity hypothesis on `V`.

Suppose toward contradiction that `UV` has no such short zero-sum. Its shared donor contains

`e1^(p-1)e2^(p-1)g^(p-1)s^(c+2)`.

The exact theorem in `A2_CONSTANT_DONOR_INVERSE_CLASSIFICATION_V1.md` applies with `K=c+2<=H+1`. Since `c>=4`, neither its `K=3` exception nor its `(p,K)=(11,4)` exception is possible. Therefore

`y=(A,-A,1)`, `A!=0`.

The companion relation is

`r x=y-cs-g`.

Consequently, in the field,

`x1+x2=x3=-c/r=2c/(2c+1)=:beta`.                   (1)

The denominators are nonzero: `1<=r<p` and `2c+1<=p-2`.

## 2. The reusable remainder certificate

Let `ell` be a positive integer for which division gives

`ell p=2c q+v`, `1<=v<=p-1`.

Suppose

`1<=a:=q-v<=r`, `q+v<=H-1`.                         (2)

Then

`q(2c+1)=ell p+a`,

so (1) implies `-a x3==v (mod p)`. Define the actual least-residue counts

`P=[-a x1]_p`, `Q=[-a x2]_p`.

Their sum is congruent to `v`; because `0<=P,Q<=p-1` and `1<=v<=p-1`, its ordinary value is `v` or `p+v`. Thus

`boxed{x^a e1^P e2^Q g^v}`                          (3)

is a nonempty zero-sum subsequence of `UV`. Its counts fit the actual donor, and its length is at most

`a+P+Q+v<=p+a+2v=p+q+v<=m-1`.

This is the generalized remainder selector already proved in `A2_RANK3_SATURATED_BOUNDARY_SMALL_OVERLAP_ELIMINATION_V1.md`. The short proof here fixes the capacity and score conditions used in every case below. No trial over possible values of `x` or `y` is required.

## 3. Two uniform ranges dispose of every c >= 7

If

`p<(c+1)^2`,                                        (4)

the audited adaptive-parity circular-gap theorem in `A2_RANK3_SATURATED_BOUNDARY_CIRCULAR_GAP_ELIMINATION_V1.md` already gives the contradiction, for every overlap in the present theorem. It remains to consider

`p>=(c+1)^2`.                                       (5)

For `c>=7`, use `ell=4` in Section 2:

`4p=2c q+v`, `q=floor(2p/c)`.

The remainder is positive and even, hence `2<=v<=2c-2`. Indeed `v=0` would imply `2c|4`, since `p` is coprime to `2c`, contradicting `c>=7`. Condition (5) gives `q>=2c+4>v`.

The inequality

`(c-4)p>=c(4c-1)`                                   (6)

holds throughout this range. At the smallest real value permitted by (5), its difference is

`(c-4)(c+1)^2-c(4c-1)`

`=c^3-6c^2-6c-4=(c-7)(c^2+c+1)+3>0`.

Since `c-4>0`, increasing `p` preserves it. It follows that

`q+v<=2p/c+2c-2<=(p-3)/2=H-1`.

Also

`a=q-v<=2p/c-2<=H-c`,

because this last inequality needs only `(c-4)p>=c(2c-3)`, which is weaker than (6). Thus (2) holds and the actual certificate (3) completes the `c>=7` case. This reproduces the previously established large-overlap assembly with its exact inequalities.

## 4. Shared estimates for c = 4, 5, 6

Continue to assume (5). Write

`p=cq+t`, `q=floor(p/c)`, `1<=t<=c-1`.

The remainder is nonzero because `p>c` is prime. Using `ell=2` in Section 2 gives

`2p=2c q+v`, `v=2t`, `2<=v<=2c-2`.

Whenever `q>v`, the positive count `a=q-v` automatically fits the available `x` multiplicity. Namely,

`a<=p/c-2<=H-c`.

For the second inequality it suffices that `(c-2)p>=c(2c-3)`. Under (5) its difference is at least

`(c-2)(c+1)^2-c(2c-3)=c^2(c-2)-2>0`

for every `c>=4`. Thus only positivity `q>v` and the score `q+v<=H-1` require the following small-overlap distinctions.

### c = 4

Here `q>=6` and primality gives `t=1` or `3`, so `v=2` or `6`. Failure of `q>v` could only occur at `q=6,t=3`, giving `p=27`, which is composite. Positivity therefore holds.

The exact score difference is

`H-1-q-v=q-(3t+3)/2`.

It equals `q-3` for `t=1`, or `q-6` for `t=3`; both are nonnegative. Section 2 eliminates every prime in (5) at `c=4`.

### c = 5

Here `q>=7` and `v` belongs to `{2,4,6,8}`. Failure of `q>v` could only give `(q,v)=(7,8)` or `(8,8)`, corresponding to the composite numbers `p=39` and `p=44`.

For the score,

`q+v<=p/5+8<=(p-3)/2`,

because the last inequality is equivalent to `3p>=95`, and (5) gives `p>=36`. This proves (2) for every remaining prime at `c=5`.

### c = 6 outside two explicit endpoints

Here `q>=8`. Since `p>3` is prime, its residue modulo 6 is 1 or 5; hence `v=2` or `10`. Failure of `q>v` can only give `v=10` and `q=8,9,10`, corresponding to `p=53,59,65`. The last number is composite.

For every other prime in (5), positivity holds and the score satisfies

`q+v<=p/6+10<=(p-3)/2`,

since the last inequality is equivalent to `4p>=138`, while (5) gives `p>=49`. Only `p=53,59` remain at `c=6`.

## 5. The two endpoints use the same certificate

At these two primes, take `ell=3` in Section 2. The following table records the exact division and the resulting occurrence and length bounds.

| p | c | ell | q | v | a = q-v | r = H-c | m | Upper length p+q+v |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 53 | 6 | 3 | 13 | 3 | 10 | 20 | 79 | 69 |
| 59 | 6 | 3 | 14 | 9 | 5 | 23 | 88 | 82 |

The division identities are `3*53=12*13+3` and `3*59=12*14+9`. Both rows satisfy all conditions (2): the displayed `a` is between 1 and `r`, and the final length bound is strictly below `m`. The actual zero-sum is exactly (3), with `P=[-a x1]_p`, `Q=[-a x2]_p`.

These are direct arithmetic and occurrence certificates at two isolated endpoints of the symbolic remainder argument. No finite prime search or coordinate enumeration supplies their authority.

## 6. Complete scope and provenance

The circle argument handles (4) for all `c>=4`. Under its complement (5), Section 3 handles `c>=7`, Section 4 handles `c=4,5,6` apart from the two endpoints, and Section 5 handles those endpoints. The stated theorem is therefore proved throughout

`boxed{p>=7 prime, 4<=c<=H-1.}`

This is a complete shared-multiplicity range on the saturated-new-value rank-three boundary. The proof does not assert elimination of `c=1,2,3`, and the exact inverse exceptions at `c=1` and `(p,c)=(11,2)` have not been used outside their scope. The earlier smaller-capacity donor obstructions and failed scalar routes remain valid records.

The proof-audit agent derived the complete `c>=4` assembly and the remainder distinctions for `c=4,5,6`, building on the team's generalized remainder and circular-gap selectors. The coordinating researcher independently checked the complete packet, including the bounds and both endpoint divisions. The rank-two proof agent independently read the final note and checked the common occurrence certificate, capacity polynomial, all three remainder distinctions, both endpoint tables, and the complete range assembly. These are internal proof roles, not external referee or novelty claims.

Independent final written-note audit: passed throughout the stated prime and overlap range. No full first-corridor or generalized Davenport formula is asserted.
