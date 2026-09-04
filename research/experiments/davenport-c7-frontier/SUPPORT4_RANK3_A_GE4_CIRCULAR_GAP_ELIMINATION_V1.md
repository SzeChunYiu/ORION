# Generic rank-three companions: circular-gap elimination — V1

Date: 2026-09-04. Status: **complete mathematical argument for the canonical
`a >= 4` support-four companion face**, with a finite small-prime arithmetic
table and four explicit certificates. The accompanying computation is a
regression, not the justification for the assertion over all primes.

This closes the generic rank-three gap left in
`FIRST_CORRIDOR_GENERALIZATION_CHECKPOINT_V8.md`. It does not close the
exceptional types `a=2,3`, the rank-two light types `a=1,2`, the full
first-corridor support-seven theorem, or `D_3(C_7^3)`. Novelty and priority have
not been certified. External independent mathematical review remains desirable.

## 1. Statement and hypotheses

Let `p >= 7` be prime and put

`H=(p-1)/2`, `h=ceil(H/2)`, `m=3H+1=(3p-1)/2`.

Take a basis `(e1,e2,s)` of `C_p^3`, an integer `4 <= a <= H`, and set

`u=a^(-1) mod p`, `g=s-u(e1+e2)`,

`U=e1^(p-1) e2^(p-1) s^a g^(p-a)`.

Here and below scalars inside square brackets are least residues modulo `p`.

> **Theorem.** Let `c,d,r,t` be positive integers with `c+d+r+t=m` and let
> `x,y` be distinct values outside `supp(U)`. If
>
> `V=s^c g^d x^r y^t`
>
> is zero-sum, then `UV` has a nonempty zero-sum subsequence of length less
> than `m`.

In particular, the rank-three, support-four companion in the exact-support-six
normal form cannot occur for any canonical maximal type `a >= 4`.
The theorem itself does not require a separate rank assumption on `V`.

Suppose, for contradiction, that `UV` has no zero-sum of length less than `m`.
Since `m>p`, no actual value can occur `p` times in `UV`. Thus

`c <= p-1-a`, `d <= a-1`, `1 <= r,t <= p-1`.

In particular `S=c+d` satisfies `2 <= S <= p-2`, so multiplication by `S`
is invertible in `F_p`. Every nonempty proper subsequence of `V` has nonzero
sum; otherwise it would itself contradict the short-free assumption.

Define `rho(z)` as the shortest length of a subsequence of `U` summing to `z`,
and `delta(z)=rho(z)+rho(-z)`. For every nonempty proper `W | V`, the two
mixed zero-sums obtained by representing the opposite sums of `W` and `V/W`
give

`rho(sigma(W)) >= |W|`, `rho(-sigma(W)) >= m-|W|`,

and hence

`delta(sigma(W)) >= m`.                                      (1)

This is the graded criterion from `MAXIMAL_PAIR_REPRESENTATION_DEPTH_V1.md`;
the argument above also proves the precise part used here.

## 2. Exact antipodal identity on an overlap-plane slice

Write a target in the overlap plane as `z=C s+D g`, and let

`b=[C+D]_p`, with `1 <= b <= p-1`.

The nonzero-height hypothesis is essential. We do not use the formula below
at `b=0`.

Since `e1+e2=a(s-g)`, a representation of `z` in `U` has equal saturated
counts `E` on `e1,e2`, together with counts `j` on `s` and `q` on `g`.
The integer `j+q` lies in `[0,p]`, so its residue `b != 0` forces `j+q=b`.
Consequently the admissible light counts are exactly

`K_b=[max(0,b-(p-a)), min(a,b)] cap Z`.

The saturated count is forced to be `E=[u(C-j)]_p`. Put

`R_b(C)={ [u(C-j)]_p : j in K_b }`.

Then

`rho(C s+D g)=b+2 min R_b(C)`.

Complementation in `U` sends `j` to `a-j`, `q` to `p-a-q`, and `E` to
`p-1-E`. Equivalently `K_(p-b)=a-K_b`. Thus the opposite target has minimum
cost `p-b+2(p-1-max R_b(C))`. We obtain the exact identity

> `delta(C s+D g)=p+2(p-1-diam R_b(C))`.                      (2)

This is a full overlap-plane identity, not merely a radial estimate.

For `1 <= ell <= a`, let `G_ell(u)` be the largest circular gap in

`{0,u,2u,...,ell*u} subset F_p`,

including the gap from the largest residue back to zero through `p`.
If `ell <= b <= p-ell`, the interval `K_b` contains at least `ell+1`
consecutive integers: indeed its size is
`1+min(a,b,p-b)` because `a <= (p-1)/2`.
The set `R_b(C)` therefore contains a translate of an `ell+1` term rotation
block. The ordinary diameter of any translate of such a block is at least
`p-G_ell(u)`. Equation (2) implies

> `delta(C s+D g) <= p+2(G_ell(u)-1)`
> whenever `ell <= [C+D]_p <= p-ell`.                       (3)

If `G_ell(u) <= h`, the right side is strictly less than `m`:
`p+2(h-1) <= m-1` (and is at most `m-2` when `H` is even).
By (1), the entire band of plane heights `[ell,p-ell]` is then forbidden
for proper companion subsequences, regardless of `x,y` or the individual
coefficients `C,D`.

## 3. Counting attainable heights instead of searching multipliers

Define the set of capacity-admissible relation multiples

`Q={n in F_p : [nr]_p <= r and [nt]_p <= t}`.

Multiplication by each of `r,t` is a permutation, so intersection counting
gives

`|Q| >= (r+1)+(t+1)-p = r+t+2-p`.

For every `n in Q`, the actual subsequence

`W_n=x^[nr]_p y^[nt]_p`

has sum `-n(cs+dg)`. Append any `i` copies of `s` and `j` copies of `g`
with `0<=i<=c`, `0<=j<=d`. All integers `i+j` from `0` through `S=c+d`
are attainable. Therefore the heights attained by these subsequences include

`B+[0,S]`, where `B=-S Q` and `|B|=|Q|`.

For every nonempty `B subset F_p`, elementary interval growth gives

`|B+[0,S]| >= min(p, |B|+S)`.

For completeness, adding `{0,1}` to a nonempty proper subset of `F_p`
increases its cardinality by at least one: equality without growth would
make the subset invariant under translation by `1`, hence all of `F_p`.
Iterate this observation `S` times. No inverse theorem is being assumed.

It follows that the number of attained heights is at least

`min(p,r+t+2-p+S)=m+2-p=H+2`.                              (4)

The empty subsequence and the full `V` both have height zero. Hence every
attained height in `[ell,p-ell]` comes from a nonempty proper subsequence;
these two exceptions do not weaken the counting argument.

The complement of that forbidden band has only `2ell-1` residues. Combining
(3) and (4) yields:

> **Gap/count criterion.** The short-free pair is impossible if
>
> `G_ell(u) <= h` and `2ell-1 < H+2`.                        (5)

Take

`L=floor((H+2)/2)=ceil(p/4)`, `ell=min(a,L)`.

The second inequality in (5) always holds. The only remaining task is a
short rotation-cover bound, independent of every companion multiplicity.

## 4. Sharing both directions forces a middle inverse

Two explicit circuit multiples already fit `UV` because `c,d>=1`.
For scalar `n=u+1`, the old-support occurrence vector is

`(p-n,p-n,a+1,p-a-1)`.

For scalar `n=p+1-u`, it is

`(p-n,p-n,a-1,p-a+1)`.

Each is zero-sum and has length `3p-2n`. Both scalars lie in `[1,p-1]`:
`a>=4` and `a<=H` exclude `u=1,p-1`. Requiring both lengths to be at least
`m` gives exactly

> `h+1 <= u <= p-h-1`.                                    (6)

Thus, after reflecting the rotation if necessary,

`v=min(u,p-u)` lies in `[h+1,H]`.

Reflection does not change circular gaps.

## 5. A complete rotation block has an exact gap formula

For any coprime integers `p,a` with `2 <= a <= (p-1)/2`,

> `G_a(a^(-1) mod p)=ceil((p-1)/a)`.                       (7)

Here primality is unnecessary. To prove (7), write `p=q a+b`, `1<=b<a`,
and `a u=1+lambda p`. Since `lambda p == -1 (mod a)`, `lambda` is a unit
modulo `a`. For `0<=j<a`, put `r_j=[lambda j]_a`. Then

`[ju]_p=(r_j p+j)/a`.

These residues are ordered by `r_j`. The index with `r_j=r` is
`j=[-b r]_a`, so successive circular gaps are `q` or `q+1`, with exactly
`b` gaps of size `q+1`. The first gap after zero is `q+1`. Adding the last
point `[a u]_p=1` splits this gap into `1` and `q`. The resulting gap
multiset consists of one `1`, `a-b+1` copies of `q`, and `b-1` copies of
`q+1`, proving (7).

When `a<=L`, choose `ell=a`. Since `a>=4`,

`G_a(u)=ceil(2H/a) <= ceil(H/2)=h`,

and (5) closes the case. Only `a>L` remains.

## 6. Two or three directed chains cover the large-prime case

We use an elementary circle observation. If a set of base points has largest
circular gap `G0`, and we add `N` steps of a common displacement `+e` or
`-e` from each base, the resulting largest gap is at most

`max(e,G0-N e)`.                                         (8)

Indeed, inside a gap between consecutive bases, the chain starting at the
appropriate endpoint fills in points spaced by `e`; any remaining end gap
is at most the original gap minus `N e`. Other chains can only decrease gaps.

Assume now `p>=53`, `a>L`, and (6).

### 6.1 Two-chain regime: `2v >= p-h`

Put `e=p-2v` and `N=floor((L-1)/2)`. We have `1<=e<=h`, and `e` is odd.
The case `e=1` would give `a=2` or `a=p-2`, excluded here. Thus `e>=3`.

The first `L+1` rotation points contain the two chains based at `0,v` with
`N` steps of `2v == -e (mod p)`. The largest base gap is
`G0=p-v=(p+e)/2`. Since `N>=1`, (8) gives

`G_L(v) <= max(e,(p+e)/2-N e)`

`        <= max(h,(p+3)/2-3N)`.

As `N >= (L-2)/2 >= p/8-1`, the second expression is at most
`p/8+9/2`, which is at most `(p-1)/4 <= h` for `p>=38`.
In particular `G_L(v)<=h` for the present range.

### 6.2 Three-chain regime: `2v < p-h`

Put `e=|3v-p|` and `N=floor((L-2)/3)`.
The inequalities `h+1<=v` and `2v<p-h`, together with `4h>=p-1`, give
`e<=h`. The value `e=0` is impossible for a prime `p>=53`. The value `e=1`
would give `a=3` or `a=p-3`, again excluded. Thus `2<=e<=h`.

The rotation block contains the three chains based at `0,v,2v`, each with
`N` steps of `3v-p`, a signed displacement of magnitude `e`.
Their base gap is

`G0=max(v,p-2v) <= (p+2e)/3`.

Since `N>=1`, (8) yields

`G_L(v) <= max(e,(p+2e)/3-N e)`

`        <= max(h,(p+4)/3-2N)`.

Here `N >= (L-4)/3 >= p/12-4/3`, so the second expression is at most
`p/6+4 <= (p-1)/4 <= h` for `p>=51`.
Thus `G_L(v)<=h` also in this regime.

These two arguments prove (5) for every prime `p>=53`, without scanning
primes or companion parameters.

## 7. Finite small-prime arithmetic

For primes below `53`, the following table lists **all** canonical types
`a>L` that satisfy (6). An entry `a:G` means
`G=G_L(a^(-1) mod p)`, computed by sorting the at most `L+1` displayed-form
residues `0,u,...,Lu` and taking consecutive differences, including wrap.
Types `a<=L` were already handled by (7); types violating (6) were already
handled by the explicit short zero-sums of Section 4.

| p | h | L | All remaining a:G |
|---|---|---|---|
| 7 | 2 | 2 | none |
| 11 | 3 | 3 | none |
| 13 | 3 | 4 | 5:3 |
| 17 | 4 | 5 | **7:5** |
| 19 | 5 | 5 | 7:5, 8:5 |
| 23 | 6 | 6 | 7:4, 10:5 |
| 29 | 7 | 8 | 9:4, 11:5, 12:5, 13:7 |
| 31 | 8 | 8 | 11:5, 12:5, 13:5, 14:7 |
| 37 | 9 | 10 | 11:4, 13:5, 17:7 |
| 41 | 10 | 11 | 12:4, 13:7, 15:5, 16:5, 17:5, 18:7, 19:9 |
| 43 | 11 | 11 | 12:4, 15:8, 18:5, 20:9 |
| 47 | 12 | 12 | 13:4, 15:7, 18:5, 22:9 |

Every entry satisfies `G<=h` except `(p,a)=(17,7)`.
For that exception, the sorted points are `0,3,5,8,10,15`; the gap `5`
from `10` to `15` is real. It must not be rounded down or absorbed into the
uniform gap assertion.

## 8. Four certificates close the sole rotation exception

Let `p=17`, `a=7`, `u=5`, `m=25`.
If `c>=3`, then `e1 e2 s^10 g^7` is an actual zero-sum of length `19`.
If `d>=4`, then `e1^2 e2^2 s^3 g^14` is one of length `21`.
These follow from `e1+e2=7(s-g)`. Therefore `1<=c<=2`, `1<=d<=3`, and
`2<=S=c+d<=5`.

Order the two new values so `r<=t<=16`, with `r+t=25-S`.
If `r>=9`, doubling the companion relation gives the available subsequence

`s^(2c) g^(2d) x^(2r-17) y^(2t-17)`

of length exactly `16`.

Otherwise write `r=8-k`, `t=17-S+k`; the bound `t<=16` gives
`0<=k<=S-1`. For `k<=2`, tripling gives the available subsequence

`s^(3c) g^(3d) x^(7-3k) y^(17-3(S-k))`

of length exactly `24`. Its counts are nonnegative and within the capacities
of `UV` because `c<=2`, `d<=3`, and `1<=S-k<=5`.

Only the following four rows remain. The occurrence vectors are ordered
`(e1,e2,s,g,x,y)`; `n` records the scalar multiple of the companion relation.

| c | d | k | r | t | n | Actual occurrence vector | Length |
|---|---|---|---|---|---|---|---|
| 1 | 3 | 3 | 5 | 16 | 7 | (0,0,7,4,1,10) | 22 |
| 2 | 2 | 3 | 5 | 16 | 7 | (1,1,7,4,1,10) | 24 |
| 2 | 3 | 3 | 5 | 15 | 7 | (2,2,0,1,1,3) | 9 |
| 2 | 3 | 4 | 4 | 16 | 9 | (0,0,1,10,2,8) | 21 |

To check each row, write its first two equal counts as `E`. The old-support
part has coefficients `7E+s_count` and `g_count-7E` in the basis `(s,g)`.
They equal `nc,nd` modulo `17`; the new counts equal `[nr]_17,[nt]_17`.
The total is therefore zero. Each count is at most the corresponding actual
capacity `(16,16,7+c,10+d,r,t)`, and each displayed length is less than `25`.
This closes the exception and proves the theorem.

## 9. A reusable transfer inequality, including other ranks

The same argument is not limited to the first-corridor length.
Let the ambient rank be `R>=2`, take a basis `(e1,...,e_(R-1),s)`, and set

`g=s-a^(-1)(e1+...+e_(R-1))`,

`U=(product e_i^(p-1)) s^a g^(p-a)`, `1<=a<=(p-1)/2`.

Let `V=s^c g^d x^r y^t` be zero-sum of length `M`, where `c,d>=0`,
`1<=c+d<=p-1`, `1<=r,t<=p-1`, and `x,y` are distinct outside `supp(U)`.
If `UV` contains no nonempty zero-sum of length less than `M`, then, for
every integer `1<=ell<=a`,

> `M <= max(p+(R-1)(G_ell(a^(-1))-1), p+2ell-3)`.           (9)

Indeed (2) and (3) hold with `2` replaced by `R-1`: membership in the plane
forces all `R-1` saturated occurrence counts to be equal. Section 3 gives
at least `min(p,M+2-p)` attainable heights. If `M` exceeded both entries
on the right of (9), the central band would be forbidden, while the attained
set would have more than its complement's `2ell-1` residues, a contradiction.
Taking the minimum of the right side over `ell` is an immediate corollary.
No generalized Davenport value follows without the other global reductions.

## 10. Verification, review boundaries, and provenance

Parent integration snapshot: `6be5e754005317f9389d677065572a0ce26743e9`.
Its ancestry includes V8 `9229d28be5a643ff7bf30ea6213aba717c48e309` and the
parallel `a=2` fiber-envelope and standard-family work. This proof does not
assume that the standard-family classification problem has been solved.

The argument above was checked from three complementary perspectives:
capacity algebra for (2), elementary additive counting for (4), and endpoint/
counterexample checks for (6)--(8). These are checks in the present work,
not a claim that an external reviewer or another agent certified the proof.

`check_rank3_circular_gap_v1.py` imports no repository module or existing depth
table. It compares raw capacity enumeration with (2), compares a separate
occurrence-level subset DP with the raw depth computation, regenerates the
small table, tests the chain and interval lemmas, and replays all 36 small
exception multiplicity rows. It also accepts an actual compatible `p=5,a=2`
control outside this theorem's hypotheses and detects six targeted mutations.
The deterministic result is in `RANK3_CIRCULAR_GAP_RECEIPT_V1.json`.

The finite checks cannot establish an all-prime conclusion by themselves.
Sections 2--6 give the uniform argument, and Sections 7--8 give the complete
finite remainder. Python checks use explicit exceptions and remain active
under `python -O`.

No theorem here relies on the V8 overlap-sum bound, doubling-boundary
reduction, scalar-three central-strip theorem, or an unproved index-one /
bi-minimal classification. The new obstruction bypasses those generic edge
cases rather than extending their brute-force coverage. It does not replace
the independent review or novelty audit needed before submission.
