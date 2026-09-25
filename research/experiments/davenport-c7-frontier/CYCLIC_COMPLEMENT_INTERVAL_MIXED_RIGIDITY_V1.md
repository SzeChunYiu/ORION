# An exact complement-interval test for mixed donor completions

Status: **proved prime-uniform structural equivalence for an explicit completion family**. One available occurrence of one value and a long progression of occurrences of a second value force an arithmetic progression to be an interval. This is the mixed-subsequence step used to close the first unsaturated type-two face.

## 1. A proper interval cannot have a different progression step

Let `p>=5` be prime and `2<=N<=p-2`. If

\[
\{a,a+d,\ldots,a+(N-1)d\}
\]

is a consecutive interval of `N` residues, with `d!=0`, then `d=+/-1`.

The progression and its translate by `d` have symmetric difference two, since all `N+1<=p-1` displayed consecutive progression points are distinct. For a consecutive interval `T` of length `N`, however,

\[
|T\mathbin\triangle(T+d)|
=2\min(\|d\|_p,N,p-N).
\tag{1}
\]

To check (1), replace `T` by its consecutive complement if necessary, so its length is at most `(p-1)/2`, and translate its start to zero. A centered displacement of magnitude at most `(p-1)/2` gives intersection length `max(N-||d||_p,0)`; the negative displacement has the same intersection size. This yields (1) in both original length ranges.

Since `N,p-N>=2`, the boundary can be two only when `||d||_p=1`, as claimed.

## 2. The mixed completion family

In a basis `(e1,e2,g)` of `C_p^3`, let

\[
y=(A,-A,1),\quad A\ne0,\qquad
x=(X_1,X_2,C),\qquad X_1+X_2+C=2.
\]

Put

\[
q=[-C]_p,\qquad1\le q\le p-3,\qquad M=p-2-q.
\tag{2}
\]

Assume the occurrence sequence contains one `x`, at least `q` copies of `y` and `g`, and at least `M` copies of each axis. These modest bounds suffice; the intended application supplies saturated axes and even more copies of `g,y`.

For `0<=j<=q`, a nonempty zero-sum of the form

\[
\boxed{Z_j=x\,y^j g^{q-j}e_1^{P_j}e_2^{M-P_j},
\qquad P_j=[-X_1-jA]_p}
\tag{3}
\]

is available exactly when `P_j<=M`. Indeed its third coordinate is `C+q=0`, its first coordinate is zero by definition, and its first two coordinates sum to

`X1+X2+M=2-C+p-2-q=0`.

All displayed exponents are then nonnegative and within the stated capacities. Every such certificate has the same strict-short length

\[
\boxed{|Z_j|=1+q+M=p-1.}
\tag{4}
\]

The use of one `x` guarantees nonemptiness, including at `j=0`.

## 3. Exact classification of failure of this family

**Theorem.** No certificate (3) exists if and only if one of the following holds:

\[
\boxed{A=1,\ X_1=1,
\qquad\text{or}\qquad A=-1,\ X_2=1.}
\tag{5}
\]

If no certificate exists, the progression

\[
T=\{-X_1-jA:0\le j\le q\}
\]

is disjoint from `{0,...,M}`. Its `q+1` distinct points and that interval's `M+1` points have total size exactly `p`. Therefore

\[
\boxed{T=\{M+1,\ldots,p-1\}.}
\tag{6}
\]

Here `2<=q+1<=p-2`, so Section 1 forces `A=+/-1`.

For `A=1`, a decreasing progression of this proper length can equal (6) only when its start is `p-1`: an internal start would either miss that endpoint or include a residue outside the interval. Thus `-X1=p-1`, giving `X1=1`.

For `A=-1`, the progression is increasing, so its start must be `M+1`. Thus `X1=-(M+1)=q+1=1-C` in the field, and the coordinate-sum hypothesis gives `X2=1`.

Conversely, each case in (5) gives exactly the progression (6), by these endpoint formulas. Thus all `P_j` exceed `M`, proving the equivalence for this family.

## 4. Exact scope

The condition `X1+X2+C=2` is an equality in `F_p`, not a claim that the three chosen least residues have ordinary sum two. The integers `q,M` and all occurrence counts are defined separately in (2)--(3).

The converse classifies failure of the displayed family only. It does not assert that the exceptional coordinate forms give a globally short-free sequence. In applications their compatibility with the independent companion relation must still be checked.

The proof neither enumerates the possible step `A` nor tests all subsequences. The exact cardinality equality (6), followed by a two-point translation boundary, provides the rigidity. Every resulting forbidden zero-sum has the occurrence form (3). The written proof was checked locally for the interval and capacity endpoints and both directions of (5).
