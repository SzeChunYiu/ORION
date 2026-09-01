# A1 priority audit — public-index search for a prior exact `D_k(C_5^3)`

**Date:** 2026-09-01
**Outcome:** `NEGATIVE__NOT_MATHSCINET_CERTIFIED`
**Scientific authority delta:** `NONE`. A negative priority search does not establish
novelty; it removes one of the two named blockers on the novelty *claim*.

Issue #49 A1 requires searching MathSciNet, zbMATH, arXiv, Google Scholar and citation
neighbourhoods for `D_4(C_5^3)`, `D_k(C_5^3)`, equivalent `C_5^3` notation, fourth /
multiwise / generalized Davenport constants and equivalent short-zero obstruction
formulations, and to record every closest theorem and whether it already implies the exact
value — with **no "first" language unless this closes**.

## Result

**No source found stating an exact `D_k(C_5^3)` for `k >= 2`, including `D_4(C_5^3)`.**

Five searches were run: the notation variants; "generalized Davenport constant" with
"elementary abelian"; "fourth Davenport constant" and "multiwise Davenport"; `C_5^3` with
zero-sum and Davenport/obstruction, also testing `C_5 (+) C_5 (+) C_5`, `Z_5^3` and
elementary-5-group / rank-3 phrasings; and MSC `(11B75 OR 11P70) AND 20K01` for 2015–2026.

## The one value that *is* known, and it is not ours

```
D_1(C_5^3) = D(C_5^3) = 1 + 3(5 - 1) = 13
```

standard for a finite abelian `p`-group via `D(G) = 1 + d^*(G)`. The claim under test
concerns `k >= 2` and is untouched by it.

## Closest prior work, with why each falls short

| authors | year | why it does not settle `D_4(C_5^3)` |
|---|---|---|
| Freeze & Schmid | 2010 | General `D_k` theory and eventual arithmetic progression; exact cases are elementary **2**-groups |
| Cziszter & Domokos | 2013 | Generalized `D_k` / Noether number theory, no exact `C_5^3` computation |
| Marchan, Ordaz, Santos & Schmid | 2015 | Elementary `p`-group multiwise constants, but **weighted**; no ordinary exact `D_k(C_5^3)` |
| Girard & Schmid | 2019 | Determines multiwise Davenport constants exactly — but only for `C_2 (+) C_{n_2} (+) C_{n_3}` with `2 | n_2 | n_3` |
| Zakarczemny | 2021 | Defines `D_m(G)`; result is an **upper bound** for ordinary rank-3 `D(G)` |
| Gao, Hui, Li, Li, Qu & Zhong | 2024 | Different invariants (`D^N`, `eta^N`, `s^N`) |
| Zhong | 2025 | Exact `k`-th Davenport inverse problem for **rank 2** only |

A rank-2 false positive is worth naming so it is not mistaken later: Zhong's material
yields values such as `D_4(C_5^2) = 16`. That is `C_5^2`, not `C_5^3`.

## The obvious shortcut does not apply, and this is the useful check

A known theorem gives `D_k(G) = D(G) + (k-1) exp(G)` for certain `p`-groups satisfying
`D(G) <= 2 exp(G) - 1`. For `C_5^3` that hypothesis demands `13 <= 9`, which is false. So
the natural route from the known `D_1` to a higher `D_k` **is unavailable here**, and the
absence of a published `D_4(C_5^3)` is consistent with the problem being genuinely open
rather than merely unrecorded.

## A numerical coincidence to guard against

`eta(C_5^2) = 13` appears in ORION-04's own branch lemmas, and `D(C_5^3) = 13` appears
here. **These are different constants over different groups that happen to share a value.**
Anyone reading the two together should not treat one as evidence about the other. Noted
because the collision is exactly the kind that produces a silent error.

## Why this is not certified, and must not be written as if it were

The searches were run against public indexes. **MathSciNet-specific record counts remain
unverified**, because an institution-bound MathSciNet session cannot be transferred into
this environment.

So the honest terminal is *negative but not MathSciNet-certified*. The distinction matters
in both directions: it is strong enough that lack of a citation should **not** be read as
evidence someone has already computed `D_4(C_5^3)`, and it is weak enough that the paper
may **not** yet use "first" language, which A1 conditions on this search closing.

## Effect on A1

A1 listed two externally gated tasks. This closes the first to the strength stated above.
The second — an independent mathematical proof audit, in which a reviewer reconstructs the
chain from the corridor and saturation lemmas to the 60-pattern / 78-branch cover without
treating the current scripts as authority — remains open and cannot be self-supplied.

The branch half of the independent implementation also remains `NOT_REGENERATED`; see
`COVER_REGENERATION_V1.json`.
