# Exact cyclic rectangular charge rigidity — V1

Status: **proved prime-uniform iff classification**. Elementary intersection counting and parity force an entire two-value zero-sum rectangle to be a rigid power.

## 1. Abstract prime-cyclic rectangular charge rigidity

Let `p` be an odd prime. Let `x,y` be distinct nonzero elements of `C_p`, and suppose

\[
R=x^r y^t,\qquad 1\le r,t\le p-1,\qquad
r+t=p+a-1,
\qquad 2\le a\le(p-1)/2
\]

is zero-sum.

Every nonzero zero-sum count vector `(A,B)` in the occurrence rectangle `[0,r]×[0,t]` lies on the one-dimensional relation line modulo `p`. Thus it has a unique scalar `lambda` satisfying

\[
(A,B)=\lambda(r,t)\quad\text{in }\mathbb F_p^2.
\]

For each nonempty proper zero-sum count vector, define its canonical charge

\[
D=[a\lambda]_p.
\]

Assume every such vector satisfies

\[
\boxed{1\le D\le a-1,\qquad A+B\equiv D\pmod2.}
\tag{1}
\]

Then there is a mixed atom `P=x^A y^B` such that

\[
\boxed{R=P^a,}
\tag{2}
\]

and the complete set of zero-sum count vectors in `R` is precisely

\[
\boxed{(0,0),(A,B),2(A,B),\ldots,a(A,B).}
\tag{3}
\]

In particular, `P` is the only atomic divisor of `R`, and `p==1 (mod 2a)`.

### 1.1. Exact counting forces every charge to occur

Consider the subsets

\[
\mathcal A=\{Ax:0\le A\le r\},\qquad
\mathcal B=\{-By:0\le B\le t\}
\]

of `C_p`. Their elements are distinct within each set, so their cardinalities are `r+1` and `t+1`. Each point of their intersection gives exactly one zero-sum count vector. Therefore the number of such vectors is at least

\[
|\mathcal A|+|\mathcal B|-p
=r+t+2-p=a+1.
\tag{4}
\]

On the other hand, (1) allows at most one nonempty proper count vector for each charge `D=1,...,a-1`. Indeed, the charge determines `lambda=D a^{-1}` modulo `p`, and the counts lie below `p`, so their representatives are unique. Adding the empty vector and the full vector gives at most `a+1` vectors.

Thus equality holds in (4), and each charge `D=1,...,a-1` occurs exactly once. Call its actual part `Y_D`. Also set `Y_0` to be empty and `Y_a=R`.

No atomicity or bound on the length of `Y_D` has been assumed here. Some of these actual zero-sum parts may have length greater than `p`.

### 1.2. The charge-one part is an atom

Let `P=Y_1=x^A y^B`. It is mixed, because a nonempty pure zero-sum would require `p` occurrences of one value.

If `P` split into two nonempty zero-sum parts, their charges `D_1,D_2` would both lie in `[1,a-1]`. Their relation scalars add, so

\[
D_1+D_2\equiv1\pmod p.
\]

But

\[
2\le D_1+D_2\le2a-2<p,
\]

which is impossible. Hence `P` is an atom. This step uses only (1), not the earlier exact factorization budget.

### 1.3. Parity synchronizes every modular wrap

The relation-scalar formulas give, for every `0<=D<=a`,

\[
Y_D=x^{A_D}y^{B_D},\qquad
A_D=[DA]_p,\quad B_D=[DB]_p.
\tag{5}
\]

At `D=a`, this is the full vector `(r,t)`, because `a(A,B)==(r,t)` modulo `p` and both full counts are below `p`.

Write

\[
F_D=\left\lfloor\frac{DA}{p}\right\rfloor,
\qquad
G_D=\left\lfloor\frac{DB}{p}\right\rfloor.
\]

The parity assumption at charge one says that `A+B` is odd. For every `1<=D<a`, equation (1) and (5) therefore imply

\[
F_D+G_D\equiv0\pmod2.
\tag{6}
\]

The same holds at `D=a`, since

\[
|Y_a|+a=p+2a-1
\]

is even. It also holds at `D=0`.

Because `0<A,B<p`, each individual floor increment from `D-1` to `D` is zero or one. Equation (6) consequently forces the two increments to be equal at every step: any wrap occurs simultaneously in both coordinates.

Suppose a wrap occurs, and let `j<=a` be its first occurrence. All previous floors are zero and both current floors are one. Thus

\[
A_j=jA-p,
\qquad B_j=jB-p.
\]

Both values are strictly positive: `j<p`, `A,B` are nonzero modulo prime `p`, and hence neither product can equal `p`. They are also strictly smaller than `A,B`, because `(j-1)A<p` and `(j-1)B<p` before the first wrap.

The actual nonempty zero-sum sequence `Y_j` is therefore a proper divisor of the atom `P`, a contradiction.

No wrap occurs for any `D<=a`. Equation (5) becomes the ordinary equality `(A_D,B_D)=D(A,B)`, proving (2) and (3).

Finally, `a(A+B)=p+a-1` gives `(p-1)/a=A+B-1`, which is even. Thus `2a|(p-1)`.

## 2. Exact normal form and converse

Since `R=P^a` has length `p+a-1`, equality holds in the elementary bound `CYCLIC_TWO_VALUE_RIGID_POWER_BOUND_V1.md`. Consequently, after interchanging the values,

\[
\boxed{(r,t)=(a,p-1),\qquad y=a x,\qquad p\equiv1\pmod{2a}.}
\]

Conversely, suppose this normal form holds, within the stated prime and capacity range. Put `b=(p-1)/a`, which is even, and `P=x y^b`. Its sum is zero because `x+b y=(1+ab)x=px=0`. For any zero-sum count vector in `R`,

\[
A+aB\equiv0\pmod p,
\qquad B\equiv bA\pmod p.
\]

Here `0<=A<=a`, `0<=B<=p-1`, and `0<=bA<=p-1`, so `B=bA` as ordinary integers. Thus the full zero-divisor set is `P^D`, `0<=D<=a`. The relation scalar of this divisor is `D/a`, so its charge is `D`, and its length `D(b+1)` has parity `D`. Every hypothesis of the theorem follows.

This is an exact classification of the abstract charge window and parity conditions. It explains why radial scalar tests leave a saturated family: that family satisfies the abstract conditions in full, and a separate geometric donor theorem is needed to exclude it in the Davenport application.

## 3. Review and proof boundary

The coordinating researcher and quotient-structure researcher independently obtained the synchronized-wrap argument from the exact intersection count. The proof-audit researcher checked the full proof and the converse, including injectivity of the interval maps, charge-one atomicity without a factorization budget, parity at the full endpoint, and positivity of the first wrapped residues.

Only count coordinates, not arbitrary proper-part lengths, are represented by least residues. No assumption `|Y_D|<p` occurs. No prime, vector, or subsequence enumeration is used. The result classifies an abstract two-value quotient condition; it is not a full first-corridor or generalized Davenport equality.
