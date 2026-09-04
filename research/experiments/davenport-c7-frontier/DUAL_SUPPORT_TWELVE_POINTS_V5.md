# The dual lives on twelve points — why the special lengths are special — V5

Status: **Lemma 1 proved (uniform in `p`); Claim 2 verified for `p ∈ {11,13,17,19,23}`.** Together they explain Observation D structurally. Observation D itself is still not proved, but what is missing is now a single support statement.
Checker: `verify_dual_support_v5.py`. Priority CANNOT_CHECK.
Lane: `claude/orion-research-frontier-3ck9yt`.

## 1. The twelve-point set

Write `h = (p−3)/2`, so that `N = (11p−3)/2 = 5p + h`, i.e. `N = (5, h)_p`. Define

`S = { jp : 0 ≤ j ≤ 5 } ∪ { jp + h : 0 ≤ j ≤ 5 }` — twelve points, base-`p` digits `(j,0)` and `(j,h)`.

The involution `σ(y) = N − y` maps `S` to itself and pairs it up: `σ(jp) = (5−j)p + h`, so

`0 ↔ N`,  `p ↔ 4p+h`,  `2p ↔ 3p+h`,  `3p ↔ 2p+h`,  `4p ↔ p+h`,  `5p ↔ h`.

## 2. Lemma 1 (proved, all `p ≥ 5`)

> **Lemma 1.** Exactly three points of `S` lie in the atom range `[p+1, 3p−2]`, namely
> `p + h = 3(p−1)/2`, `2p`, and `2p + h = (5p−3)/2` — the three **special lengths**.

*Proof.* Four elementary inequalities, each valid for every prime `p ≥ 5`.
For the points `jp`: `p < p+1` rules out `j = 1`; `p+1 ≤ 2p ≤ 3p−2` keeps `j = 2`; `3p > 3p−2` rules out `j = 3` and above, and `j = 0` is `0`.
For the points `jp + h`: `h = (p−3)/2 < p+1` rules out `j = 0`; `p + h = (3p−3)/2 ≥ p+1` ⟺ `p ≥ 5` and `p+h ≤ 3p−2` keep `j = 1`; `2p + h = (5p−3)/2 ≤ 3p−2` ⟺ `p ≥ 1` keeps `j = 2`; `3p + h > 3p−2` rules out `j = 3` and above. ∎

Checked for all 76 primes `5 ≤ p ≤ 397`, and the four inequalities are asserted individually so the count is uniform in `p` rather than a computation per prime.

## 3. Claim 2 (verified, not proved)

> **Claim 2.** Every dual `Q` with `Q(0) ≠ 0` is supported inside `S`. When the excluded pair `Z` consists of two special lengths, `Q` is supported in `S` minus the involution-pair of the **third** special length.

Verified for `p ∈ {11,13,17,19,23}` and all three special pairs, for **every** basis dual with `Q(0) ≠ 0`, not merely one.

Example, `p = 11` (`h = 4`, `N = 59`), excluding `Z = {2p, (5p−3)/2} = {22, 26}`: the dual is supported on

`{0, 4, 11, 22, 26, 33, 37, 48, 55, 59} = S \ {15, 44}`,

and `{15, 44} = {a, N−a}` is the involution-pair of the third special length `a = 3(p−1)/2 = 15`.

## 4. Why this explains Observation D

Combining: the dual can be nonzero only on the twelve points of `S`; by Lemma 1 only three of those are atom lengths, and they are exactly the special lengths. The condition defining the dual is that the `(−1)^N`-antisymmetry of the spectrum is broken **only** where `Q ≠ 0`. So the antisymmetry can be broken only at the three special lengths (and at `0`, which is in `S`). Excluding two of them leaves the third to be killed, which the involution-pair omission does; excluding anything else leaves a required nonzero outside `S`, which is impossible.

This retires the description in `GENERAL_SPECTRUM_SPECIAL_LENGTHS_V4.md` that the certificates are "dense with no evident closed form". They are not dense at all — they live on twelve points. The density was an artefact of examining `P` rather than `Q = P + (−1)^N P∘σ`.

It also identifies the `4 : 2 : 3` right-hand-side ratio noted there as worth a second look: with the dual now explicit on `S`, that ratio should be computable rather than observed.

## 5. What remains for a proof of Observation D

Exactly one statement: **`supp Q ⊆ S`**. Everything else is proved — Lemma 1 above, the reduction of `OBSERVATION_D_REDUCTION_V5.md`, and the duality of `LUCAS_CRITERION_V5.md`.

The shape of the missing argument is visible. `P` vanishes on the integer interval `[N−D, D]` of length `h = (p−3)/2`, so Newton about `N−D` writes it in the shifted basis with the first `h` coefficients zero; `Q` is then a `(−1)^N`-symmetric combination that must vanish on the whole atom range bar two points. The claim to prove is that such a `Q` is forced onto the digit-pattern points `(j,0)` and `(j,h)`. That is a Lucas statement of the same kind as Theorem G, on a longer window.

## Claim ceiling

Lemma 1 is proved for all `p ≥ 5`. Claim 2 is verified for five primes and is **not** proved; Observation D therefore remains verified for `5 ≤ p ≤ 31` and unproved. Nothing here extends its verified range — the contribution is that the remaining gap is now one support statement about an explicitly described function on twelve points, rather than a rank argument about a matrix.
