# Type two: the second unsaturated main family is empty

Status: **proved prime-uniform main-family elimination, and complete face elimination for every prime p>=31**. An auxiliary cyclic atomization supplies a coordinate-sum-two group of actual occurrences. The atomic alternative is resolved by a one-step exchange and the previously proved quotient divisor restriction.

## 1. The theorem and its inverse gate

Use `p=2H+1>=7`, `m=3H+1`, `u=H+1`, `s=(u,u,1)` in a basis `(e1,e2,g)`, and

\[
U=e_1^{p-1}e_2^{p-1}g^{p-2}s^2,
\qquad V=s^c g x^r y^{p-3},
\qquad r=H+2-c,
\]

with `2<=c<=2 floor(H/2)`. Suppose `sigma(V)=0`.

**Theorem.** If `y=(A,-A,1)` with `A!=0`, then `UV` contains a nonempty zero-sum of length below `m`.

Consequently the whole rank-three face `b=3` is empty for every prime `p>=31`. Indeed the linear bounded-hole theorem applies with `b=3` since `p>=10b`; its half-power plane classification then forces precisely this main family. The actual donor has `c+2>=4` light copies. The only non-main plane exception at four or more light copies is at `p=11`, outside this consequence. If `c=H`, use the same inverse argument on the `H+1`-light subdonor; the high value still has at least `H-1` copies.

The proof below also works at smaller primes whenever the main inverse form is established. It does not classify all nonplane possibilities at `p=7,11,13,17,19,23,29`.

## 2. The smallest main layer c = 2

Here `r=H`, and the relation is

`Hx=3y-2s-g`.

Thus `x=(X1,X2,0)` and `X1+X2=4` in `F_p`. If `P=[-X1]_p<=p-4`, the sequence `x e1^P e2^{p-4-P}` is zero-sum of length `p-3<m`.

Otherwise `X1` is one of `1,2,3`, and `X2=4-X1` is the corresponding positive integer. For `x=(2,2,0)`, use `x^H e1 e2`, of length `H+2<m`. For `x=(1,3,0)`, write `p=3j+R` with `j=floor(p/3)<=H` and `R in {1,2}`. Then

`x^j e1^{p-j} e2^R`

is zero-sum of length `p+R<=p+2<m`. Axis exchange handles `(3,1,0)`. All occurrences fit, so the whole main layer `c=2` is eliminated.

## 3. The layer c = 3 has two direct groups of occurrences

Here `r=H-1`. Apply `A2_GENERALIZED_WEIGHT_TWO_MIXED_PACKET_SELECTOR_V1.md` with the following actual `x^i s^z` choices:

| Prime form | `i` | `z` | `lambda=i/r` in `F_p` | Third coordinate `C0` | `q=[-C0]_p` |
|---|---:|---:|---|---|---|
| `p=4L+1` | `L+1` | 0 | `H` | `H+1` | `H` |
| `p=4L+3` | `L` | 2 | `H+1` | `H+2` | `H-1` |

The coordinate-sum equation is `2z-4 lambda=2`, satisfied in both rows. The `x` counts are positive and at most `r`; the light counts are at most five; and `i+z<=H+1`. Also `1<=q<=p-3`, so all `y` and donor counts fit.

The selector's exceptional equation is `10 lambda=2`. In the first row its left side is `-5`, so equality would require `p=7`, impossible in that prime congruence class. In the second it is `5`, so equality would require `p=3`. Therefore the selector gives a short zero-sum in both rows.

## 4. The auxiliary cyclic sequence

Assume now `c>=4`, and set

\[
a=c-1\ge3,\qquad r+a=H+1.
\]

In an auxiliary cyclic group `C_p=<h>`, define

\[
\boxed{T=(a h)^r(-r h)^a.}
\tag{1}
\]

It is zero-sum of length `H+1`, with two distinct nonzero values: `a,r<p` and `a+r=H+1` is nonzero modulo `p`.

Any nonempty proper zero-sum count vector `(i,w)` of `T` has both coordinates positive. Its zero-sum complement also has both positive, so

\[
1\le i\le r,\quad1\le w\le a,
\quad2\le i+w\le H-1.
\tag{2}
\]

The relation `a i=r w` gives `lambda=i/r=w/a` in `F_p`. Since `r+a=H+1==1/2`, its canonical representative is

\[
\lambda=2(i+w)\in[4,p-3].
\]

Use the actual group of occurrences `x^i s^{w+1}`. In the generalized selector this means `z=w+1`; its coordinate sum is two because `2z-2a lambda=2`. Its third coordinate is `1+lambda`, so

\[
q=p-1-2(i+w)\in[2,p-5].
\]

The group length is `i+w+1<=H`, its light count is at most `a+1=c`, and every other capacity is valid. Therefore any such count vector with `5 lambda!=1` gives a short zero-sum.

## 5. Every reducible auxiliary sequence is eliminated

Suppose `T` is reducible. Every atomic divisor is proper and satisfies (2). If any atomic divisor has `5 lambda!=1`, Section 4 finishes the proof.

Otherwise every atomic divisor has the same `lambda=5^{-1}`. Its actual counts are uniquely `[r/5]_p,[a/5]_p`, so every atomic divisor has one count-vector type `Q`. Atomizing `T` gives `T=Q^k` for an ordinary integer `k>=2`. The count relation implies `k==5 (mod p)`. Since each factor has at least two terms,

`2<=k< p`,

so `k=5`. Now `2Q` is an actual proper zero-sum part; its complement `3Q` is nonempty. Its label is `2/5`, which is not exceptional, and it still satisfies (2). Applying Section 4 to `2Q` gives the contradiction.

Thus a hypothetical short-free pair forces the auxiliary sequence `T` to be an atom.

## 6. The two atomic alternatives are exact

A two-value cyclic atom of length `H+1` has index one. The needed borderline input is the Xia--Yuan splitting lemma, stated as Lemma 2.5 in [Peng--Sun](https://arxiv.org/html/1409.1970v1): a two-value atom can be split into an atom one term longer. Its length `H+2` is strictly above `p/2+1`, so [Savchev--Chen, Section 5, Proposition 10](https://arxiv.org/pdf/math/0602568) gives positive normalized representatives summing to `p`. Recombining the split pair preserves that sum; their sum is below `p` because other positive terms remain. The `p>155` assumption in Peng--Sun's later main section is not a hypothesis of its preliminary splitting lemma. Both sources were reopened for this proof.

As `2(H+1)>p`, one normalized support coefficient is one. Therefore exactly one of the following orientations applies, for an integer `j>=2`:

\[
\boxed{r+ja=p\quad\text{or}\quad a+jr=p.}
\tag{3}
\]

No index theorem is applied to a reducible sequence: Section 5 established atomicity first.

## 7. The orientation a divides H has an actual one-step exchange

In the first orientation, put `d=j-1=H/a`. Since `r>=2`, one has `d>=2`, and

`r=a(d-1)+1`.

Choose the auxiliary count vector

\[
i=r-j=ad-a-d,\qquad w=a+1.
\tag{4}
\]

It obeys `a i-r w=-p`, so gives the same modular relation as in Section 4. It is not a divisor of `T`, because its second coordinate has increased by one; instead it uses the actual additional shared light capacity.

For `a>=3,d>=2`, its first coordinate is positive and at most `r`. Its length is

`i+w=H+1-d<=H-1`,

and its required light count is `z=w+1=a+2=c+1<=c+2`. Thus all packet conditions in Section 4 remain valid. Its label is

\[
\lambda=2(H+1-d)\equiv1-2d\pmod p.
\]

The exceptional equation `5 lambda=1` would imply `p|5d-2`. But

`0<5d-2<2ad+1=p`,

since `a>=3`. It is impossible. The generalized selector therefore rules out this entire orientation.

## 8. The other orientation collapses to r = 3

In the second orientation of (3), put `d=j-1=H/r`, so

\[
H=dr,\qquad c=(d-1)r+2.
\]

Here `d>=2`, because `d=1` would give `c=2`, already treated.

The already proved `b=3` quotient-atom theorem in `A2_RANK3_UNSATURATED_QUOTIENT_BUDGET_V1.md`, Section 8, gives the independent necessary restriction

\[
c\mid(H-1)\quad\text{or}\quad r\mid(H-1).
\tag{5}
\]

Its hypotheses hold here: the actual saturated `g` donor is present, and `s,g,y` are independent because `A!=0`; relation (2) in the generalized selector then has full support and `r,c,3` nonzero. The original quotient is atomic by that theorem, independently of the auxiliary atom `T`.

The second alternative in (5) is impossible because `r>=2` divides `H`. Thus `c|(H-1)`. But

`H-1=dr-1<2((d-1)r+2)=2c`.

The positive quotient must be one, giving `H-1=c`, hence `r=3`. Consequently the only remaining parameters in this orientation are

\[
\boxed{H=3d,\quad p=6d+1,\quad c=3d-1,\quad r=3,
\qquad d\ge2.}
\tag{6}
\]

## 9. A mixed circular-gap certificate closes the final parameters

For any main-family `b=3` relation, take `3<=j<=n+1`, `0<=n<=c`, and a centered integer `v==2jA (mod p)` with `|v|<=n` and `v==n (mod 2)`. Then

\[
\boxed{x^r y^{j-3}s^{c-n}g^{1+n-j}
e_1^{(n-v)/2}e_2^{(n+v)/2}}
\tag{7}
\]

is an available zero-sum of length `H+n<m`. Indeed the companion relation makes the new-value sum `j y-cs-g`; after the displayed light and heavy terms its coordinates are `(jA-nu,-jA-nu,0)`. The two nonnegative axis counts cancel these coordinates. Every count fits, including the lower bound `j>=3` required by the missing new-value occurrences.

In (6), first let `d>=3`. The `d` distinct points

`0,6A,...,6(d-1)A`

on the circle of circumference `p=6d+1` have a gap at most `floor(p/d)=6`. Their endpoint difference gives `j=3ell` for some `1<=ell<=d-1`, with a centered representative `v` of `2jA` satisfying `|v|<=6`. Since `c=3d-1>=8` and `j<=c-2`, the smallest integer at least `max(j-1,|v|)` with parity `v` is at most `c`. This supplies (7).

At `d=2`, one has `p=13,c=5`. If `||6A||_13<=5`, take `j=3` and the same parity choice `n<=5`. Otherwise `6A=+/-6`, hence `A=+/-1`. Take `j=4,n=5`, since `2jA=+/-8` has centered representative of magnitude five and odd parity. Formula (7) again applies.

This eliminates the last atomic orientation and proves the main-family theorem.

## 10. Exact completed scope

The main inverse family on the whole face `b=3` is now empty, for all allowed primes and overlaps. The linear inverse threshold makes this a complete, unconditional face elimination for every `p>=31`. The unsaturated inverse gate at the seven smaller primes listed in Section 1 remains separate; it has not been replaced by the saturated theorem.

The proof uses atomization to separate a reducible auxiliary sequence from its atomic alternative, checks the one possible repeated-factor exception, and uses the actual extra light occurrence in (4). The one-step exchange is not incorrectly required to lie inside the auxiliary sequence. Local scrutiny checked these distinctions, the two imported index thresholds, the independent quotient restriction, all circle endpoints, and the actual occurrence counts. No separate external referee approval or full first-corridor claim is made.
