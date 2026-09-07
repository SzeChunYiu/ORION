# First-corridor `a=2` heavy three-support branch is impossible — V1

Status: **proved prime-uniform equality-face elimination**. This is an elementary relation-multiple argument inside the support-six normal form. It uses no finite classification and claims no generalized Davenport value by itself.

## 1. Setup

Let `p>=5` be an odd prime and consider the first maximal corridor

`C_1(p)=(p+1, (3p-1)/2, 3p-2)`.

Let the support-four maximal atom be the canonical `a=2` type

`U=e1^(p-1)e2^(p-1)e3^2 g4^(p-2)`,

where

`g4=e3-2^(-1)(e1+e2)`.

Assume the maximal pair `UV` attains the support-six lower bound and lies in the three-support branch of `SUPPORT4_MAXIMAL_PAIR_SUPPORT6_NORMAL_FORM_V1.md`, sharing the **heavy** unsaturated value `g4`.

Then

`V=g4^c x^r y^t`

for two genuinely new values `x,y`, with `V` an atom of length

`m=(3p-1)/2`.

The pair is `(m-1)`-short-zero-free.

Because `U` already contains `p-2` copies of `g4` and the pair is p-short-zero-free,

`c<=1`.

The shared value actually occurs in `V`, so

`boxed{c=1.}`

Thus

`r+t=m-1=3(p-1)/2`.

Also each new actual value has multiplicity at most `p-1`, so, after interchanging `x,y`, assume

`r<=t<=p-1`.

The zero-sum relation of `V` is

`boxed{g4+r x+t y=0.}`

## 2. The multiplicity interval has only two cases

Since `t<=p-1`,

`r=3(p-1)/2-t >= (p-1)/2`.

Hence either

1. `r=(p-1)/2`, in which case necessarily `t=p-1`; or
2. `r>=(p+1)/2`, in which case also `t>=(p+1)/2`.

We show each case creates a forbidden zero-sum subsequence of `UV` of length at most `m-1`.

## 3. Interior case: double the relation

Assume

`r,t >= (p+1)/2`.

Doubling the relation gives

`2g4 + [2r]_p x + [2t]_p y = 0`,

where, because `r,t>=p/2`,

`[2r]_p=2r-p <= r`,

`[2t]_p=2t-p <= t`.

Thus the displayed zero-sum is an actual subsequence of `UV`: the `x,y` copies come from `V`, and the two `g4` copies come from `U` (which has `p-2>=2`).

Its length is

`2+(2r-p)+(2t-p)`

`=2+2(r+t)-2p`

`=2+3(p-1)-2p`

`=p-1`.

Since

`p-1 < m`,

this contradicts `(m-1)`-short-freeness of `UV`.

## 4. Boundary case: triple the relation

Now assume

`r=(p-1)/2`, `t=p-1`.

Tripling the relation gives

`3g4 + [3r]_p x + [3t]_p y = 0`.

The residues are

`[3r]_p=(p-3)/2 <= r`,

`[3t]_p=p-3 <= t`.

Also `U` contains `p-2>=3` copies of `g4` for every odd prime `p>=5`. Hence this is again an actual mixed subsequence of `UV`.

Its length is

`3+(p-3)/2+(p-3)`

`=3(p-1)/2`

`=m-1`.

This is exactly the forbidden short-zero boundary, again a contradiction.

## 5. Theorem

Combining the two cases:

> **Theorem.** For every odd prime `p>=5`, the first maximal corridor cannot have an exact-support-six maximal pair in which
>
> - the maximal atom is the support-four type `a=2`, and
> - the three-support rank-two companion shares only the heavy value `g4`.

Equivalently, this entire equality branch is empty prime-uniformly.

The proof is completely independent of the C7 finite census.

## 6. Relation to the C7 frontier

At `p=7`, the theorem removes the only heavy-share three-support radial family that survives the one-point depth filters. The full C7 pair theorem `SUPPORT6_PAIR_FACE_81019_EMPTY_V1.md` is stronger—it removes every support-six pair face—but this file identifies one piece of that finite disappearance as an all-prime mechanism.

## Verification receipt

`check_a2_heavy_support3_double_triple_v1.py` checks the two-case arithmetic for every odd prime through 1009 and every admissible ordered pair `(r,t)` with

`r+t=3(p-1)/2`, `1<=r<=t<=p-1`.

The checker is regression only; theorem authority is the symbolic proof above.

## Boundary

- The `a=2` light-share three-support branch is not eliminated here.
- The `a=2` four-support rank-three branch is not eliminated here.
- The symmetric `a=1` light-share branch remains the main first-corridor equality family.
- No `D_3(C_p^3)` value or priority/novelty claim is made.
