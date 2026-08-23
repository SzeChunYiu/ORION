# ORION-RG X1-R — the `C_2^4` extremal `D_2` witness set is exactly three `GL(4,2)`-orbits

## Why this and not something else

The prior-art gate closed the rank-2 `η` line completely (six hits, X1-Q) and found the
`C_2^4` 120-element family published as punctured maximum caps of `PG(3,2)` (Davydov–Tombak
1989, via Freeze–Schmid Thm 7.2). It reported **not found**, with its scope stated, for the
full witness set — the total 3480 and the `3360 / 120` split.

That is a well-posed target precisely where computation has leverage: elementary 2-groups
are the one family where `D_k` **values** are known (`r ≤ 6`) while no structural
classification of the extremal sequences exists. This atom answers it for `r = 4`.

## Result

Under the natural `GL(4,2)` action (order 20160), the 3480 extremal `D_2` witnesses of
`C_2^4` — length-7 sequences with no two disjoint nonempty zero-sum subsequences — form
**exactly three orbits**:

| orbit size | min zero-sum | stabiliser order | `|orbit| × |Stab|` |
|---|---|---|---|
| **2520** | 3 | 8 | 20160 ✓ |
| **840** | 3 | 24 | 20160 ✓ |
| **120** | 4 | 168 | 20160 ✓ |

`2520 + 840 + 120 = 3480`, matching the complete enumeration exactly.

Two things this settles that were previously only histogram facts:

1. **The `3360` is not a single orbit.** It splits `2520 + 840`. The minimum-zero-sum
   statistic (`3` vs `4`) is therefore a *strictly coarser* invariant than the orbit
   decomposition — it separates the 120 but merges two genuinely different families.
2. **The 120 is a single orbit**, with stabiliser of order 168. That is consistent with its
   identification as a punctured maximum cap: the stabiliser of the 8-point affine hyperplane
   acting on the deleted point.

## Validation

Every row satisfies the orbit–stabiliser identity `|orbit| · |Stab| = |GL(4,2)| = 20160`
exactly, with integer stabiliser orders — the same check used to validate the `GL(3,5)`
classification in X1-F4. The orbit sizes also sum to the independently enumerated total.
`|GL(4,2)|` was computed by direct enumeration of invertible matrices, returning 20160,
which matches `(2^4-1)(2^4-2)(2^4-4)(2^4-8)`.

## Prior-art status

The 120-orbit is published as a cap-classification result (hit #13). The **three-orbit
decomposition**, and in particular the `2520 / 840` split of the min-zero-sum-3 stratum, was
reported not-found by the gate, whose stated scope was: Freeze–Schmid Section 7 read in full
(their `r = 4` content is pure *value* — Thm 7.9 gives `D_2(C_2^4) = 8` and never classifies),
Property B/C literature (degenerate on `C_2^r`, since `exp = 2` makes Property C's conclusion
vacuous), and the cap/coding literature reached via Davydov–Tombak and Grynkiewicz–Lev.
**Coverage gaps, stated:** MathSciNet and zbMATH were not searched, and Davydov–Tombak was
not read directly, only Freeze–Schmid's restatement.

No novelty is claimed beyond that scope.

## Open, and deliberately not guessed at

1. **The geometric identity of the 2520 and 840 orbits.** Both have minimum zero-sum 3, so
   each support contains a line of `PG(3,2)`; what distinguishes them is not determined here.
   Stabiliser orders 8 and 24 are the available handle. Not speculated on.
2. **`C_2^5` and `C_2^6`.** `D_2 = 10` and `11` are known, so the same question is posable at
   witness lengths 9 and 10, and the instruments already exist. The `r = 4` answer being
   three orbits gives no reason to expect any particular count there.
3. Whether the orbit decomposition has a uniform description in `r` at all.
