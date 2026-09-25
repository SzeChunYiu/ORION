# Saturated type-two extensions lie in three affine planes — V1

Status: **proved prime-uniform rigidity of a high-multiplicity new value**, with exact seam identities. The statement uses only the original type-two maximal-atom donor, with no additional shared `s` or `g` occurrences. It converts arbitrary saturated-value coordinates into three explicit affine alternatives and determines the residue-sum profile in each alternative.

This is a necessary condition, not an existence classification or a generalized Davenport equality.

## 1. Statement

Let `p=2H+1>=7` be prime, `m=3H+1`, and use the basis `(e1,e2,g)` with

`s=(u,u,1)`, `u=H+1=2^(-1) in F_p`.

The type-two donor is

`B=e1^(p-1)e2^(p-1)g^(p-2)s^2`.

Suppose `B y^(p-1)` has no nonempty zero-sum of length below `m`, where

`y=(A,B0,C)`.

Write `T=1-A-B0-C` in `F_p`. Then

`boxed{A B0 C!=0}`

and

`boxed{T=0 or 2T=C or 2T=-C.}`                         (1)

Equivalently, every surviving value lies in one of the three affine planes

`A+B0+C=1`,

`2A+2B0+3C=2`,

`2A+2B0+C=2`.

The letter `B0` denotes a coordinate; it is distinct from the donor sequence `B`.

## 2. Zero coordinates are impossible

For `1<=j<=p-1`, define the formal saturated-basis length

`L_j=j+[-jA]_p+[-jB0]_p+[-jC]_p`.

Let `q` be the number of nonzero coordinates of `y`. If `q=0`, `y` itself is a one-term zero-sum. Suppose `1<=q<=2`.

Except possibly at `jC=1`, the displayed basis completion is an actual subsequence of `B`: the only incomplete saturated capacity is `g^(p-2)`, and its sole forbidden least-residue count is `p-1`. If `C=0`, even this exception is absent.

Choose the set `J` of indices excluding both `jC=1` and `jC=-1` when `C!=0`, and all indices when `C=0`. This set is stable under `j -> p-j` and has at least `p-3>=4` elements. For every `j in J`,

`L_j>=m`, `L_j+L_(p-j)=(q+1)p`.

Consequently

`m<=L_j<=(q+1)p-m`.

If `q=1`, this interval is empty. If `q=2`, it is the two-integer interval `[m,m+1]`.

When `T!=0`, the congruence `L_j==jT (mod p)` makes the values on `J` distinct, contradicting the available two integers. When `T=0`, all `L_j` are multiples of `p`, but `[m,m+1]` contains no such multiple for `p>=7`. This proves `A B0 C!=0`.

## 3. Two copies of s shorten every completion except one seam

All three least residues in `L_j` are now positive. Put

`a_j=[-jA]_p`, `b_j=[-jB0]_p`, `c_j=[-jC]_p`.

Whenever `c_j>=2`, the actual sequence

`y^j e1^(a_j-1)e2^(b_j-1)g^(c_j-2)s^2`

is zero-sum, since `2s=e1+e2+2g`. Its length is `L_j-2`.

Every occurrence fits: the saturated counts decrease, `c_j-2<=p-3<=p-2`, and exactly two available copies of `s` are used. This remains valid when `c_j=p-1`, even though the unmodified formal basis completion would have exceeded the `g` capacity.

Thus

`L_j>=m+2` whenever `jC!=-1`.                         (2)

At the sole remaining seam `jC=-1`, one has `c_j=1`, so the unmodified completion is available and gives

`L_j>=m`.                                             (3)

For every index, formal complementarity and congruence remain exact:

`L_j+L_(p-j)=4p`, `L_j==jT (mod p)`.                   (4)

## 4. Interval saturation forces the three-plane alternatives

Exclude the two indices `j=+C^(-1),-C^(-1)` and call the resulting set `J0`. It has `p-3` indices and is stable under negation.

By (2) and (4),

`m+2<=L_j<=4p-m-2` for `j in J0`.

This is the interval

`[3H+3,5H+1]=[2p-(H-1),2p+(H-1)]`,

containing exactly `p-2` integers. Its only multiple of `p` is `2p`.

If `T!=0`, the `p-3` values `L_j` are distinct and none equals `2p`. They therefore occupy all the remaining `p-3` integers of that interval. Their residues are exactly

`{-H+1,...,-1,1,...,H-1}`.

Multiplication by the nonzero `T` permutes `F_p^*`. The two excluded indices must consequently have the missing residues `{H,-H}`:

`{T/C,-T/C}={H,-H}`.

Since `2H==-1 (mod p)`, this is equivalent to `2T=C` or `2T=-C`. Together with the separate possibility `T=0`, this proves (1).

## 5. Exact profiles and seam restrictions

For a residue `v`, write `cent(v)` for its representative in `[-H,H]`.

### Affine sum-one case

If `T=0`, equations (2)--(4) imply

`boxed{L_j=2p for every 1<=j<=p-1.}`

For the non-seam indices this follows from Section 4. At `j=C^(-1)`, the lower bound is `m+2`, while (3) at its opposite bounds the value above by `4p-m`; the only multiple of `p` in this interval is again `2p`. Its complementary value is also `2p`.

Thus this branch meets the exact Bernoulli-pairing hypothesis already verified in `A2_RANK3_EXTREME_BOUNDARY_MIXED_PLANE_ELIMINATION_V1.md`, Section 10. That established donor theorem forces one of the familiar forms

`y=(1,b,-b)`, `y=(a,1,-a)`, `y=(a,-a,1)`.

The pairing theorem remains donor-owned; the elementary argument here establishes its hypothesis without assuming a plane condition for `y`.

### Two nonzero-T cases

For every non-seam index in `J0`, interval saturation determines the exact integer

`boxed{L_j=2p+cent(jT).}`

The two exceptional values are also determined. Put `jplus=[C^(-1)]_p` and `jminus=p-jplus`.

| Alternative | `L_jplus` | `L_jminus` |
|---|---:|---:|
| `2T=C` | `2p+H+1` | `m` |
| `2T=-C` | `2p+H` | `m+1` |

For example, `2T=C` gives `jplus*T==H+1`, and the bounds `m+2<=L_jplus<=4p-m` leave only `2p+H+1` with that residue. The other row and both complementary entries follow in the same way from (4).

There is an additional half-interval constraint at the low seam. Put

`a=[A/C]_p`, `b=[B0/C]_p`.

Both are positive. At `jminus`, replacing its one `g` together with the appropriate saturated counts by one `s` gives a valid zero-sum of length

`L_jminus-(p+1)+pN`,

where `N` is the number of `a,b` that are smaller than `u=H+1`. This follows by using saturated counts `[a-u]_p,[b-u]_p`, no `g`, and one `s`.

If `2T=C`, the original low-seam length is `m`; both `N=0` and `N=1` would make it short. Therefore

`boxed{1<=[A/C]_p,[B0/C]_p<=H.}`

If `2T=-C`, the low-seam length is `m+1`, and `N=0` would make it short. Thus at least one of `[A/C]_p,[B0/C]_p` belongs to `[1,H]`.

## 6. Applicability and limitations

Every first-corridor canonical type-two pair with a new value of multiplicity `p-1` contains the donor used here. The theorem therefore applies to rank-two endpoint rows and rank-three extreme rows, regardless of how many extra shared `s` or `g` terms the pair contributes.

The conclusion is only a necessary condition. In particular, membership in one of the three affine planes does not prove short-freeness, and the two nonzero-`T` planes are not identified with the previously treated plane `A+B0=0`.

The main interval-saturation argument received an independent check from the inverse-theory agent. A separately tasked auditor and the root checked the full written argument, including the one-seam improvement, zero-coordinate exception, exact profiles, and half-interval restrictions. Internal mathematical review is GREEN. No vector or prime enumeration is used.
