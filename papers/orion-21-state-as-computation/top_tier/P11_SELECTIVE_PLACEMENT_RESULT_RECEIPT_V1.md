# P11 selective compile-tolerance placement result receipt V1 (NR-12)

**Lane:** NR-12 of `research/paper-programme-v1/NEGATIVE_REVIVAL_BACKLOG_V1.md`
**Protocol (frozen pre-execution, commit `e8d76d93`):** `P11_SELECTIVE_PLACEMENT_PROTOCOL_V1.md`
**Primary runner:** `run_selective_placement_v1.py` (local execution, exit 0)
**Independent checker:** `check_selective_placement_independent_v1.py` (local execution, exit 0)
**Terminal (frozen rule, as produced):** `P11_SELECTIVE_PLACEMENT_V1_SUPPORTED`
**Checker terminal:** `P11_SELECTIVE_PLACEMENT_SECOND_INDEPENDENT_CHECKER_GREEN`
**Replay:** both implementations re-executed end-to-end; JSON outputs byte-identical (`cmp` green, exits 0/0)

## Exact binding

- protocol SHA-256: `4c8b4475e5de5e6e1825ee3d15d2d7e8ccaf66a36af6318a964eb25ecba036f6`
- primary receipt JSON SHA-256: `825f9268bf2051f3abb23e801960609c93da581d440bee519ec426bd6e94b69f`
- independent receipt JSON SHA-256: `68058ba78a1d127f4f0660ecbde20efe613125189e6f9d5a0ae078ab37bcd6b9`
- attribution verification JSON: `nr12_attribution_verification_v1.json` (source = frozen V1 primary, SHA `9a1f1f9b…` verified)
- environment: **local laptop execution** — numpy 2.4.4, scikit-learn 1.8.0 (the frozen V1 CI binding used numpy 2.3.2 / scikit-learn 1.7.1). Version difference is bound for the battery path: the re-executed frozen battery reproduces the committed V1 receipt numbers with **max deviation 0.0** across all 60 universal/compiled means.
- no frozen V1 file modified; the frozen battery (folds, scaler, selector `k=16`, access classes, seeds, tolerance −0.02) is re-executed unmodified; the only new degree of freedom is the pre-registered placement bit.

## Attribution verification (step 1, read-only on the frozen V1 receipt)

- QS cell matrix: **13/30** (responsibility × access-class) cells quality-supported.
- Per-responsibility tolerant-class counts: q0=3, q4=3, q6=3 (all classes); q2=2, q7=2 (stronger classes only); **q1=q3=q5=q8=q9=0** (no access class rescues them).
- Two-way partition of the V1 delta table (balanced, exact): **responsibility main effect 77.4%**, access-class main effect 2.4%, interaction 20.2%.
- Delta tracks universal difficulty: pooled Pearson +0.51 (LINEAR +0.50, RBF +0.64, KNN +0.79).

**Attribution confirmed:** compile-tolerance is a per-responsibility property (dominant axis) with a weaker access-class interaction — exactly the backlog hypothesis. A train-only selector that estimates per-responsibility tolerance is therefore the right-shaped lever.

## Frozen selector (recap)

Per outer fold and responsibility: inner `StratifiedKFold(5, shuffle, rs=2026112207)` inside the training part only; per inner fold fit `StandardScaler` + `SelectKBest(f_classif, k=16)`, train the frozen LINEAR model on universal and compiled inner states (seed `2026112500+f*10+q`), score balanced accuracy on inner-validation; **place compilation iff `mean_inner(compiled) >= mean_inner(universal) − 0.02`** (the same frozen tolerance). Placement decided per (fold, query); retained queries are served from the universal state (delta 0 by construction).

## Per-query outcome (frozen seed 20261121; LINEAR shown fully)

| query | universal | placed | placed Δ | QS | placed folds | compiled Δ (V1) |
|---|---:|---:|---:|---|---|---:|
| q0 | 0.9916 | 0.9888 | −0.0028 | Y | all 5 | −0.0028 |
| q1 | 0.9652 | 0.9652 | +0.0000 | Y | none | −0.0455 |
| q2 | 0.9968 | 0.9968 | +0.0000 | Y | none | −0.0675 |
| q3 | 0.9422 | 0.9422 | +0.0000 | Y | none | −0.0477 |
| q4 | 0.9855 | 0.9775 | −0.0080 | Y | folds 3,4 | −0.0200 |
| q5 | 0.9767 | 0.9586 | −0.0181 | Y | folds 1,2,3 | −0.0239 |
| q6 | 0.9833 | 0.9657 | −0.0176 | Y | folds 0,2 | −0.0182 |
| q7 | 0.9793 | 0.9606 | −0.0187 | Y | folds 3,4 | −0.0208 |
| q8 | 0.8576 | 0.8576 | +0.0000 | Y | none | −0.0617 |
| q9 | 0.9454 | 0.9197 | −0.0256 | **N** | folds 0,4 | −0.0296 |

Support counts (selectively-placed vs V1 compile-all): **LINEAR 9/10 (was 3), RBF 10/10 (was 5), KNN 10/10 (was 5)**. Fold placement sizes |S_f| = 3, 2, 3, 4, 4 (union of ever-placed queries: q0, q4, q5, q6, q7, q9; q1/q2/q3/q8 declined in every fold — the four heaviest V1 losers plus q2, whose LINEAR loss −0.0675 is the largest in the family).

## Frozen-gate evaluation (preregistered rule, unchanged)

| gate component | requirement | observed | verdict |
|---|---|---|---|
| non-vacuity | \|S_f\| ≥ 1 every fold | 3,2,3,4,4 | PASS |
| LINEAR family support | ≥ 8/10 | 9/10 | PASS |
| stronger-class support (max RBF,KNN) | ≥ 8/10 | 10/10 (both) | PASS |
| all ten reported | 30 cells | 30 | PASS |
| no family below frozen baseline | LINEAR≥3, RBF≥5, KNN≥5 | 9/10, 10/10, 10/10 | PASS |
| resource identities | memory = 64+16·\|S_f\| (never wins); break-even = floor(n_train·64/48)+1 | 96–128 floats/example vs 64; 1917/1918 per placed query (= V1's U=1 row, fold-mean 1917) | PASS |
| **composite positive terminal** | all of the above | — | **`P11_SELECTIVE_PLACEMENT_V1_SUPPORTED`** |

## Selector honesty endpoints (reported, not gated)

- **Query-level false positives** (placed somewhere, test-intolerant at mean level): LINEAR q5, q7, q9 (3); RBF q5, q9 (2); KNN q5, q9 (2).
- **Fold-cell precision (LINEAR):** 16 placed (fold, query) cells; 7 individually test-tolerant, 9 individually intolerant. The family bar is met through *conservative partial placement* — the selector places borderline responsibilities in only some folds, and the retained folds contribute delta 0, diluting per-fold losses below the mean-level tolerance.
- **The single LINEAR failure (q9):** inner-CV deltas at folds 0/4 were −0.0019/−0.0014 (inside tolerance) while test compiled Δ = −0.0296; blended placed Δ = −0.0256. The selector's inner estimate and the test outcome genuinely disagree on q9 under LINEAR; under RBF/KNN q9's placed Δ is −0.0059 (the compiled loss is LINEAR-specific).
- **False negatives:** LINEAR 0 (q2 declined everywhere is a true negative for LINEAR — its LINEAR Δ −0.0675 is the family's worst); RBF/KNN 1 each (q2 would have been tolerant under stronger access — an efficiency loss, not a quality loss).

## Secondary generalization read (pre-registered, non-gating)

Outer seeds 20261122 / 20261123 / 20261124, same inner selector seed: all three
`P11_SELECTIVE_PLACEMENT_V1_SUPPORTED` — LINEAR 9/10, 9/10, 9/10; RBF 10/10, 10/10, 9/10;
KNN 10/10, 9/10, 9/10; fold sizes 2–6. The selector rule is not fold-draw-specific.

## Resource read (selective placement)

- **Memory never wins:** selective state = 64 (raw retained) + 16·|S_f| = 96–128 floats/example vs universal 64 — strictly greater whenever non-vacuous. The win axis is service touches only, exactly as pre-registered.
- **Break-even:** each placed query repays its compiler fit (n_train·64 inspections) after floor(n_train·64/48)+1 = 1917–1918 served examples (V1's U=1 identity, unchanged).
- **Future-query arrival tax:** one compiler fit iff the arriving responsibility is placed by the same train-only rule; zero otherwise — the tax now falls only on the placeable subset, never family-wide (a strict improvement over V1's compile-all policy, whose tax was unconditional).

## Scientific disposition

**Revived positive under stopping criterion (a):** the V1 negative stands unedited — compile-ALL fails the 8/10 family bar (3/5/5). Selective placement with a pre-registered train-only inner-CV tolerance selector meets the same frozen family bar (9/10 LINEAR, 10/10 stronger) without degrading any family below its frozen baseline, on the frozen battery and on three pre-registered alternative fold draws. The mechanism is the verified attribution: tolerance is a per-responsibility property (77.4% of the delta variance), predictable from train-internal held-out estimates, so placement — not compilation itself — was the failing stage of the compile-all policy.

## Non-claims

- Does NOT relabel or weaken the V1 negative: compile-all at family scale remains unsupported on digits.
- Licensed claim is digits-only and selector-scoped: "a train-only inner-CV tolerance selector places compilation on a subset such that the selectively-placed family meets the frozen 8/10 bar". No transfer beyond digits, no claim that the selector's per-cell precision is high (it is 7/16 at fold-cell level under LINEAR — the family bar survives via conservative partial placement, reported above), no open-agent-system claim, no change to the V1 resource identities.
- Retained queries contribute delta 0 by construction; the load-bearing gate content is non-vacuity plus selector precision at family level, both frozen before execution.
- Local execution only (no CI in this lane by instruction); environment difference from the frozen CI binding is bound by exact (0.0-deviation) reproduction of the frozen battery numbers.
