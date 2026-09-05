# Davenport research: unsaturated-face checkpoint — 2026-09-05

Status: **complete all-prime closure of the first two unsaturated rank-three type-two faces, exact new donor inverses, and additional rank-two closures are proved**. The full first corridor, `D_3(C_7^3)`, and a generalized Davenport numerical formula remain open.

## 1. Continuity and cross-session audit

The user named the original live branch `shadow/davenport-c7-frontier-20260903` at `86f089ab`. This continuation used its stronger published descendant

`776fb3c42e0afef9e5cecf0aaa3a62b52361fb17`,

tree `f45d32a68e16309e19740e4750788281dbc5af6f`.

All 28 Davenport remote branches were inspected through Git remote heads and complete paginated GitHub search; the final page at cursor `Mjg` was empty. The audit was repeated during the proofs and before publication. The live and prior unsaturated branches remained at `776fb3c42`; the quotient-budget branch remained at `c66be654`; all other named Davenport heads were unchanged. No stronger intervening work was overwritten or reproduced as a new result.

The work used its own checkout and branch `shadow/davenport-topface-20260905`. The already proved exceptional rank-three `a=3` negative J-selector closure, type-two submaximal rank-two closure, and other earlier theorems were retained.

## 2. New complete face closures

Use `p=2H+1>=7`, `m=p+H`, and type-two coordinates

\[
U=e_1^{p-1}e_2^{p-1}g^{p-2}s^2,\qquad
V=s^c g x^{H+b-1-c}y^{p-b},\qquad
2s=e_1+e_2+2g.
\]

The standing interior reduction gives `1<=c<=2 floor(H/2)` and `1<=b<=c+1`.

| New result | Exact proved scope | Proof |
|---|---|---|
| First unsaturated rank-three face | Every `b=2` row is impossible, at every prime and permitted overlap. | `A2_RANK3_FIRST_UNSATURATED_FACE_COMPLETE_ELIMINATION_V1.md` |
| Second unsaturated rank-three face | Every `b=3` row is impossible, at every prime and permitted overlap. | `A2_RANK3_SECOND_UNSATURATED_FACE_COMPLETE_ELIMINATION_V1.md` |
| Whole overlap layer two | `c=2` is completely closed, combining the new faces with the prior saturated face and interior reduction. | The preceding two proofs and the prior `b=1` closure |
| Rank-two top overlap | Smaller new multiplicities `r=2,3` are impossible at every prime; `r=1` was already closed. | The first and second unsaturated donor inverse theorems |
| Minimal-overlap main family | Every `b=c+1>=3` endpoint is impossible if the high value has form `(A,-A,1)`. Unconditional when `p>=10(c+1)`. | `PLANAR_HALF_POWER_INVERSE_AND_MINIMAL_OVERLAP_V1.md` |
| Whole overlap layer three above its inverse threshold | `c=3` is completely closed for `p>=41`. | The planar theorem together with complete `b=1,2,3` closure |

The `b=2` proof uses exact complement-interval rigidity. The `b=3` proof atomizes an auxiliary cyclic sequence of length `H+1`, treats its repeated exceptional factor explicitly, and resolves its atomic orientations with an actual one-step exchange and the independent quotient divisor restriction. Both isolated plane exceptions are supplied with explicit original-occurrence certificates.

## 3. General inverse and selector theorems

The main structural advances are broader than the two applications:

1. **Multiplicative half-interval stability.** If a multiplier moves only `d` members of the lower half out of that half, its centered representative and inverse both have magnitude at most `2d+1`. Every nonidentity multiplier has `d>p/10`. The exact two/three-hole endpoints are handled by bounded signed products and missing-index positions.
2. **Unsaturated donor rigidity.** A high value with `p-b` occurrences gives a half-interval intersection of size at most `b`, with a single possible core seam. Thus `p>=10b` forces opposite first two coordinates, with the one-missing-`g` donor treated using its actual capacities.
3. **Half-power plane inverse.** Once in that plane, only `H-1` copies force the same exact families as the full-power theorem. This has a complete all-subsequence converse.
4. **All-prime first and second truncated inverses.** The exact donor forms are proved for powers `p-2` and `p-3`, with all small-prime and light-capacity hypotheses explicit. The second missing-`g` theorem retains `p>=11`; its top-capacity corollary separately covers seven.
5. **Complement-interval and mixed packet rigidity.** A coordinate-sum-two group of actual occurrences gives a short mixed zero unless a precise interval-progression exception holds. Its general type-two interface applies to every deficit, subject to stated capacity and residue conditions.
6. **Planar half-power inverse.** The short-free sequence `e1^(p-1)e2^(p-1)x^H` has exactly one possible plane value, `x=e1+e2`. The proof and converse are elementary.
7. **Type-one first unsaturated inverse.** For every `K>=2`, deleting one high-power occurrence preserves the sharp saturated inverse theorem: short-freeness is equivalent to `K<=floor((p+1)/4)` and a permutation of `y=(1,b,-b)`, `b!=0`.
8. **Type-one mixed circle selector.** For the main inverse family with deficit `d`, the explicit condition `(c+1)(floor(c/d)+1)>p` supplies a mixed short zero. At `d=2`, the new inverse makes this unconditional and leaves only a square-root-size overlap range.

The first three half-interval proof files and the subsequent all-prime inverses retain the progression from sufficient thresholds to exact endpoint statements. Those earlier thresholds are superseded where a later theorem explicitly supplies the missing prime cases; they are not silently promoted elsewhere.

## 4. Exact residual frontier

| Face | Necessary conditions after this checkpoint |
|---|---|
| Exceptional rank-three `a=3` | Already completely closed before this continuation. |
| Type-two rank-three | Any survivor has `c>=3`, `b>=4`, `b<=c+1`, and all prior quotient-budget restrictions. Its minimal endpoint is excluded in the main inverse family; in particular `c=3` can survive only below 41. |
| Type-two rank-two | Every `c<H` is closed. A top survivor has even `H`, `c=H`, and `4<=r<=H` with `r>p/10`, in addition to the prior maximal-atom exchange constraint. |
| Type-one first unsaturated boundary `t=p-2` | Any survivor satisfies `5<=c<floor((p+1)/4)` and `(c+1)(floor(c/2)+1)<=p`; hence `(c+1)^2<=2p`. The high-overlap range through `c=H+1` is closed. |
| Other type-one rank-two faces | The prior low-overlap, rigid-quotient, quarter-layer, balanced-band and upper-overlap restrictions remain. Nonrigid geometry and other truncated inverses are still open. |
| Global theorem | Larger-support and separate corridor gates remain; no numerical generalized Davenport formula follows from the local closures alone. |

The type-one statements and exact certificate are in `A1_FIRST_UNSATURATED_DONOR_INVERSE_AND_AUGMENTATION_V1.md` and `A1_GENERALIZED_MIXED_CIRCLE_SELECTOR_V1.md`.

## 5. Corrected authority and failed routes

The six-pattern corridor argument establishes the **existence of a selected shortest-first factorization**, not a restriction on every alternative factorization. Both affected older statements were corrected. This is a genuine quantifier correction, not a counterexample claim.

`DAVENPORT_TOPFACE_ROUTES_PRESERVED_20260905_V1.md` records the unusable `m+1` exchange, the general auxiliary rectangle's unproved occurrence gate, the one-missing-`g` endpoint limitation, and the exact inverse assumptions that must remain attached to the generalized selectors.

## 6. Verification and publication

Each theorem advance has a separate local commit, beginning with the quantifier audit `78d2478ff` and ending with the type-one circle selector `40bbf2c7a` before this checkpoint. The proofs were checked locally for actual occurrence capacities, strict-short lengths, missing complementary endpoints, signed-product coverage, and complete converses where an iff is claimed. The small endpoint tables are consequences of analytic restrictions with displayed certificates; no brute-force sweep supplies theorem authority.

The primary Bernoulli-pairing, two-value splitting, and strict long-atom index statements were reopened and their precise hypotheses checked where used. This continuation did not receive a separately tasked independent-agent audit or external referee approval. Earlier results retain their own recorded review status.

Publication preserves each reviewed tree and commit order, checks the expected remote references immediately before nonforced updates, and records local-to-published identities in the companion publication receipt. Other sessions' branches and `main` are not publication targets.
