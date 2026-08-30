# ORION-24: replacing a degenerate comparator, and what survives

Checker: `evaluate_against_principled_nulls_v1.py`. Result: `RESULTS_V1.json`.
Input: the packet's own 67 gold-labelled external packets and its two complete decision
files. Nothing re-run, no new adjudication.

## The comparator defect

`SYSTEMA` emits **`PROMOTE` on 65 of 67** packets (the remaining 2 are `CANNOT_CHECK`) —
**2 distinct dispositions against a gold distribution spanning 8**. Beating it establishes
very little. Its 11/11 on `STRONG_PROMOTABLE` is exactly what an always-promote system
scores by construction, and its 0/56 elsewhere is the same fact from the other side.

This is a defect in the *comparison*, not in the result. Recording it and stopping would
leave the paper's claim resting on a comparator that cannot lose. The lever is to replace
it with nulls that cannot win by construction.

## Three nulls, none outcome-aware

| null | construction |
|---|---|
| `ALWAYS_PROMOTE` | the incumbent's behaviour, kept so the change is visible |
| `MARGINAL_MATCHED` | samples from the gold marginal, so it reproduces label frequencies in expectation and can only be beaten by per-item discrimination |
| `STRATIFIED_BY_DOMAIN` | per-domain majority disposition — the harder null, since it exploits domain skew |

`MARGINAL_MATCHED` is stochastic, so it is run over **10,000 seeds** and reported as a
distribution rather than a point.

## Result — the claim survives, and by more than before

| system | correct / 67 |
|---|---:|
| **SYSTEMB** | **56** |
| `STRATIFIED_BY_DOMAIN` | 16 |
| SYSTEMA | 13 |
| `ALWAYS_PROMOTE` | 11 |
| `MARGINAL_MATCHED` mean | 10.6 (p05 6, p95 16, **max 23**) |

| comparison | split | result |
|---|---|---|
| SYSTEMB vs `ALWAYS_PROMOTE` | 45–0 | log₁₀p = **−13.2** |
| SYSTEMB vs `STRATIFIED_BY_DOMAIN` | 40–0 | log₁₀p = **−11.7** |
| SYSTEMB vs `MARGINAL_MATCHED` | 56 vs 10.6 | empirical p = **0.0** |

Across 10,000 marginal draws the best null run scored **23**. SYSTEMB scored **56** — far
outside the null's entire realised range, not merely past its 95th percentile.

## And the incumbent is confirmed to be a null

| comparison | log₁₀p / p | discriminates |
|---|---|---|
| SYSTEMA vs `ALWAYS_PROMOTE` | −0.30 | no |
| SYSTEMA vs `STRATIFIED_BY_DOMAIN` | −0.19 | no |
| SYSTEMA vs `MARGINAL_MATCHED` | p = 0.25 | no |

**SYSTEMA is statistically indistinguishable from all three nulls.** It is not a weak
comparator; it is a null wearing a system's name. Every previous statement of the form
"ORION beats SYSTEMA" was measuring the gap between a working system and chance.

## Disposition

The stratum-concentration concern does not survive contact with the data either — the
advantage spans 7 of 8 families and `NEGATIVE_RETAINED` contributes 9 of the 43-point gap
(21%), recorded separately in `papers/publication_closure/DIAGNOSIS_VERIFICATION_2026-08-29.md`.

What was a claim against an always-promote baseline is now a claim against a
domain-stratified majority null and a marginal-matched null at 10,000 seeds. **No outcome
was tuned and no label was touched** — only the comparator got harder, and the result held.

What this still does **not** establish: external validity. All 67 packets are internally
adjudicated, and completing the round-1 `CLAUDE_GLM53` / `CODEX_GPT56` decision files
(currently 1 row each) remains the open path to a genuinely independent comparator.
