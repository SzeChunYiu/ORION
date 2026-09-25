# Complete exceptional type-three rank-three face elimination — V1

Date: 2026-09-05. Starting live commit: `86f089ab`.
Status: **proved for every prime `p>=7` in the canonical first-corridor face**.

## Theorem

Let `p>=7` be prime, `H=(p-1)/2`, `m=(3p-1)/2`, and let `(e1,e2,s)`
be a basis of `C_p^3`. Put

`g=s-3^(-1)(e1+e2)`,
`U=e1^(p-1)e2^(p-1)s^3 g^(p-3)`.

Let `c,d,r,t` be positive integers, with `c+d+r+t=m`, and let `x,y`
be distinct values outside `supp(U)`. If

`V=s^c g^d x^r y^t`

is zero-sum, then `UV` has a nonempty zero-sum subsequence of length
strictly less than `m`.

Thus the exceptional `a=3` rank-three support-four companion in the
first-corridor exact-support-six normal form is impossible. The actual
certificate argument does not need a separate rank hypothesis on `V`.

## Proof and dependency map

For `p=7`, the old-support subsequence

`e1 e2 s^4 g^3`

is available because `c>=1`. Its sum is zero, by
`e1+e2=3(s-g)`, and its length is `9<m=10`.

Now suppose `p>=11` and, for contradiction, that `UV` is short-free
below `m`. The existing light multi-copy obstruction gives
`c<=floor(H/2)`, and the elementary `g^p` obstruction gives `d<=2`.
Also `r,t<=p-1`. The shared-donor doubling theorem at the starting
commit removes `r,t>H`; ordering `r<=t` leaves exactly

`r=H-k`, `t=p-(c+d)+k`, `0<=k<c+d`.

These are precisely the hypotheses of the following disjoint layers:

| Light overlap | Proof |
|---|---|
| `c=1` | `A3_RANK3_ONE_LIGHT_SHARE_ELIMINATION_V1.md` |
| `c=2` | `A3_RANK3_TWO_LIGHT_SHARE_ELIMINATION_V1.md` |
| `c>=3` | `A3_RANK3_BOUNDARY_C_GE3_ELIMINATION_V1.md` |

Each layer constructs an occurrence-valid zero-sum of length below `m`.
The cases exhaust all positive `c`, proving the theorem.

The inherited light ceiling and interior argument are in
`A3_LIGHT_EXACT_DEPTH_AND_TWO_PARAMETER_FACE_V1.md` and
`A3_RANK3_SHARED_DONOR_NEGATIVE_EVEN_V1.md`. The new proofs use flexible
shared donors with complementary even, odd, and wrapped negative scalars.
They do not assert that the original fixed `J` interface covers every row.

## Review, finite remainder, and claim ceiling

The proof-audit agent independently reviewed all three complete layer proofs
and the `p=7` vector. The selector agent additionally reviewed the complete
two-light-share proof. All 50 displayed small-prime certificates across the
three layer notes were directly checked for group congruences, each actual
occurrence capacity, and strict length. No search over primes, support
vectors, or potential companions establishes the all-prime result.

These are internal reviews; no external referee approval or novelty
certification is asserted. Failed universal-selector extensions remain
recorded in the layer notes.

Together with the prior `a>=4` circular-gap result and the saturation
exclusion of `a=1`, this reduces the rank-three equality face to `a=2`.
Rank-two light types `a=1,2` also remain. This is **not** the full
first-corridor support-seven theorem, an exact value of `D_3(C_7^3)`,
or an all-prime formula for `D_k`.
