# `supp Q ⊆ S` proved — the twelve-point support is a theorem — V5

Status: **proved, uniformly in `p`.** Closes the claim left open by `DUAL_SUPPORT_TWELVE_POINTS_V5.md`. Observation D itself is **still not proved** — see §5 for exactly what remains.
Checker: `verify_supp_Q_proof_v5.py`. Priority CANNOT_CHECK.
Lane: `claude/orion-research-frontier-3ck9yt`.

## 1. Statement

> **Theorem.** Let `p ≥ 5` be prime, `h = (p−3)/2`, `N = 5p+h`, and let `Z ⊆ {3(p−1)/2, 2p, (5p−3)/2}` be a set of special lengths. Then every dual `Q` for the atom-spectrum system with `Z` excluded satisfies `supp Q ⊆ S`, where `S = {jp : 0 ≤ j ≤ 5} ∪ {jp+h : 0 ≤ j ≤ 5}`.

## 2. The third-difference law

Write `G_j(t) = P(jp+t)`. Since `deg P ≤ A = N−D = 2p+h+2 < 3p`, every `d ≤ A` has base-`p` high digit at most 2, so Lucas gives `G_j = F_0 + jF_1 + C(j,2)F_2` — a degree-2 binomial polynomial **in `j`**. Hence

> `G_{j+3} − 3G_{j+2} + 3G_{j+1} − G_j = 0`,

so `G_3 = 3G_2−3G_1+G_0`, `G_4 = 6G_2−8G_1+3G_0`, `G_5 = 10G_2−15G_1+6G_0`.

With `s = (−1)^N`, the involution sends `jp+t` to `(5−j)p+(h−t)` when `t ≤ h` and to `(4−j)p+(p+h−t)` when `t > h`, so

`Q(jp+t) = G_j(t) + s·G_{5−j}(h−t)`  `(t ≤ h)`,  `Q(jp+t) = G_j(t) + s·G_{4−j}(p+h−t)`  `(t > h)`.

## 3. Two identities

Purely formal in the `G`'s, hence valid for both signs of `s` (checked exactly over `ℤ`):

> **(VI)** `G_5(x) + s G_0(h−x) = 3[G_4(x) + s G_1(h−x)] − 3[G_3(x) + s G_2(h−x)] + [G_2(x) + s G_3(h−x)]`
>
> **(VII)** `G_4(u) + s G_0(w) = 3[G_3(u) + s G_1(w)] − 3[G_2(u) + s G_2(w)] + [G_1(u) + s G_3(w)]`, `w = p+h−u`.

Each bracket is `Q` at a single point.

## 4. The ranges — why every bracket is an imposed condition

By `DUAL_SUPPORT_REDUCTION_V5.md` Fact 1 it suffices that `Q` vanish on `[1,h−1] ∪ [h+1,p−1]`.

**Lower interval, `y ∈ [1,h−1]`.** Apply (VI) with `x = h−y` and multiply by `s`; the left side becomes `Q(y)`. The three brackets are `Q(4p+h−y)`, `Q(3p+h−y)`, `Q(2p+h−y)`. By the symmetry `Q(N−z) = s·Q(z)` the first two equal `s·Q(p+y)` and `s·Q(2p+y)`. Now
`p+y ∈ [p+1, p+h−1]`, `2p+y ∈ [2p+1, 2p+h−1]`, `2p+h−y ∈ [2p+1, 2p+h−1]`,
all inside the atom range `[p+1, 3p−2]`, and none equals `p+h`, `2p` or `2p+h` because `1 ≤ y ≤ h−1`. So all three are imposed conditions, whatever `Z ⊆ {a,b,c}` is.

**Upper interval, `y ∈ [h+1,p−1]`.** Apply (VII) with `u = p+h−y ∈ [h+1,p−1]`, `w = y`, and multiply by `s`; the left side becomes `Q(y)`. The brackets are `Q(3p+u)`, `Q(2p+u)`, `Q(p+u)`. Again `Q(3p+u) = s·Q(2p+h−u)` with `2p+h−u ∈ [p+h+1, 2p−1]`, and `p+u ∈ [p+h+1, 2p−1]`; both are in the atom range and differ from `p+h`, `2p`, `2p+h`. For `Q(2p+u)` we need `2p+u ≤ 3p−2`, i.e. `u ≤ p−2`; the single remaining case `u = p−1` is covered because that bracket, `G_2(p−1) + s G_2(h+1)`, is `s` times `Q(2p+h+1)`, and `2p+h+1` lies in the atom range and is not special. ∎

The argument uses no property of `p` beyond `p ≥ 5`, so it is uniform.

## 5. What this does and does not prove

**Proves.** `supp Q ⊆ S` for special `Z`, for every prime. With Lemma 1 of `DUAL_SUPPORT_TWELVE_POINTS_V5.md` (`S` meets the atom range exactly in the three special lengths), this establishes the structural core: *any* dual can break the antisymmetry of the spectrum only at the three special lengths and at `0`.

**Does not prove Observation D.** Observation D has three parts, and only the structural one is settled:

| part | status |
|---|---|
| the unrestricted system is consistent | verified `p ≤ 31` |
| **existence**: a dual exists for each special pair (so the pair is forced) | verified `p ≤ 31`, **not proved** |
| **minimality**: no dual for any other pair or single length | verified `p ≤ 19`, **not proved** |
| **structure**: any dual has `supp Q ⊆ S` | **PROVED here, all primes** |

The support theorem constrains *what a dual looks like*; it does not construct one, and it does not forbid one for a non-special `Z` — for such `Z` the bracket conditions used in §4 need not be available, so the argument simply does not apply, which is consistent with but does not imply minimality.

## 6. Verification

`verify_supp_Q_proof_v5.py` (i) checks the third-difference law and both identities exactly over `ℤ`, for `s = +1` and `s = −1`; (ii) for each prime in `{11,…,37}` and each special pair, builds the span of the imposed conditions over `F_p` in the `3p` unknowns `G_0, G_1, G_2` and verifies that **every** target form `Q(y)`, `y ∈ [1,h−1] ∪ [h+1,p−1]`, lies in it. Step (ii) is confirmation of the range bookkeeping of §4, not the proof; §4 is uniform in `p`.

## Claim ceiling

The theorem is about duals for `Z` a set of special lengths. It says nothing about other `Z`, and it does not extend Observation D's verified range (`5 ≤ p ≤ 31`), which is still bounded by the unproved existence and minimality parts.
