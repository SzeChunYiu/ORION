# P9/P10 Controlled Novelty Results Ledger V1

Status: **ACTIVE EVIDENCE LEDGER**

Date: 2026-08-20

This ledger separates exact mathematical results, prospectively frozen controlled experiments, failed experiments, and runtime-gated future claim rungs. It does not turn controlled generated-world results into LLM or Lean results. Machine-readable identities are bound in `CONTROLLED_NOVELTY_RESULTS_RECEIPT_V1.json`.

## Evidence table

| ID | Result | Outcome | Claim authority |
|---|---|---|---|
| N0 | Information-equivalent relation theorem | relational degree 1; flat affine degree 1 impossible; flat degree 2 sufficient | `PROVED_CONTROLLED_THEOREM` |
| N1 | Relational accessibility V1.1 | large primary effect, but one frozen shuffled-label hostile gate failed | `FAILED_TERMINAL_RETAINED` |
| N2 | Relational accessibility V2 | 18/18 fresh cells pass; flat mean `0.50469`, relational mean `0.999956`, median delta `0.497925` | `SUPPORTED_CONTROLLED_REPLICATION` |
| N3 | Relational-complexity capacity frontier | at k=17, 90% threshold relational `128` vs flat quadratic `4096` (`32x`); k=33 flat quadratic never reaches 90% by 4096 | `SUPPORTED_CONTROLLED_CAPACITY_FRONTIER` |
| N4 | Invertible obfuscation ladder | linear accuracy falls monotonically `1.0000 -> 0.53695` as maximum explicit inverse-coordinate degree rises `1 -> 65`; zero decode failures | `SUPPORTED_CONTROLLED_ACCESSIBILITY_TAX` |
| N5 | Semantic-orbit stability | at k=33, flat quadratic mean OIR `0.31959` vs relational `0.01124`; exact semantics preserved | `SUPPORTED_CONTROLLED_SEMANTIC_STABILITY` |
| N6 | Access-degree recovery | b=2: degree1 `0.77395` -> degree2 `1.0`; b=4: degrees1/2/3/4 `0.67322/0.77810/0.85219/0.93347`; b=8,13 remain below 0.90 through degree4 | `SUPPORTED_CONTROLLED_CAPACITY_RECOVERY` |
| N7 | Predictive-state compression | target-sufficient/full/padded 90% sample thresholds are `64/128/512`, `128/256/1024`, `512/1024/2048` for k `17/33/65`; full = `2x` minimal in all k, padded = `8x,8x,4x` | `SUPPORTED_PREDICTIVE_SUFFICIENCY_RESULT` |
| N8 | P9 LLM structure x scale x compute | frozen analyzer exists; no reproducible multi-size model runtime bound | `CANNOT_CHECK_LLM_RUNTIME` |
| N9 | P10 native-state incremental value | frozen analyzer exists; native transition execution not completed | `CANNOT_CHECK_NATIVE_STATE_EXECUTION` |
| N10 | P10 action abstraction / same-information Lean feedback / cross-revision | frozen analyzers exist; runtime/corpus prerequisites unavailable | `CANNOT_CHECK_FORMAL_EXTENSIONS` |
| N11 | Cross-domain structural-accessibility law | formal-domain same-information result absent | `BLOCKED_PENDING_SECOND_DOMAIN` |

## N1 — failed V1.1 remains visible

V1.1 is not relabeled as positive. At `n_train=4096`, relational logistic accuracy was `1.0` at all six frozen dimensions while flat accuracy remained near chance, but a single fixed shuffled-label relational control exceeded the frozen `<0.65` condition at low dimension. Its terminal remains `RELATIONAL_ACCESSIBILITY_PRIMARY_GATE_NOT_MET`.

The CI now treats correct reproduction of that negative terminal as a green **reproducibility** check. It does not demand that the historical experiment become positive.

## N2 — fresh replicated information-equivalent accessibility

V2 used six dimensions `{3,5,9,17,33,65}`, three fresh worlds per dimension, `4096` training and `16384` test items per cell, plus 64 shuffled-label null fits per cell.

All 18 cells passed. Aggregate:

- mean flat accuracy `0.5046895345`;
- mean relational accuracy `0.9999559191`;
- median relational-minus-flat delta `0.4979248047`;
- minimum delta `0.4575805664`;
- maximum delta `0.5172729492`.

Every observed relational score exceeded all 64 frozen shuffled-label null fits in its cell. Reconstruction, broken-relation and coordinate-permutation controls all passed.

## N3 — relation coordinates change the observed capacity/sample frontier

The exact theorem establishes that the controlled target is degree 1 in relational coordinates, not affine-linearly separable in flat coordinates, and degree 2 sufficient in flat coordinates. The generic interaction-only degree-2 flat feature expansion has dimension `2k^2+k`, versus `2k` relational features.

| k | Relational linear 90% threshold | Flat quadratic 90% threshold | Flat linear |
|---:|---:|---:|---:|
| 3 | 64 | 64 | not reached |
| 5 | 64 | 128 | not reached |
| 9 | 128 | 512 | not reached |
| 17 | 128 | 4096 | not reached |
| 33 | 512 | not reached | not reached |

At k=17 the observed threshold ratio is `32x`. At k=33 the relational learner reaches 90% by 512 samples while generic flat quadratic is only `0.82495117` at 4096. The generic quadratic feature count grows `21 -> 2211` from k=3 to 33, while relational features grow `6 -> 66`.

## N4 — invertible representation difficulty ladder

The exact block-chain theorem gives `r_j=product_{i=1}^j u_i`; therefore the encoding is bijective while explicit inverse-coordinate degree grows with block length.

On fresh k=65 worlds, mean linear accuracy over three replications is:

| Maximum inverse degree | Accuracy |
|---:|---:|
| 1 | 1.000000 |
| 2 | 0.750590 |
| 4 | 0.668447 |
| 8 | 0.617554 |
| 16 | 0.585337 |
| 32 | 0.563507 |
| 65 | 0.536947 |

All six adjacent transitions are non-increasing. The canonical-to-full-chain gap is `0.4630534`, and decode failures are zero.

## N5 — semantic-orbit stability

Models were trained once on canonical data and evaluated under 32 target-preserving signed coordinate permutations without retraining.

| k | Flat quadratic canonical acc | Relational canonical acc | Flat mean OIR | Relational mean OIR | Flat items with any change | Relational items with any change |
|---:|---:|---:|---:|---:|---:|---:|
| 9 | 0.996826 | 1.000000 | 0.002678 | 0.000000 | 0.076904 | 0.000000 |
| 17 | 0.815918 | 1.000000 | 0.182892 | 0.000000 | 0.820557 | 0.000000 |
| 33 | 0.672363 | 0.988525 | 0.319588 | 0.011238 | 0.993408 | 0.205322 |

Mean OIR advantage `(flat-relational)` is `0.16463979`; every semantic-preservation check passed exactly.

## N6 — increasing model interaction degree buys back accessibility

The access-degree experiment tests whether increasing polynomial interaction order can recover performance lost under the bijective nonlinear encoding.

| Encoding block / inverse degree | Degree 1 | Degree 2 | Degree 3 | Degree 4 | Minimum tested degree reaching 90% |
|---:|---:|---:|---:|---:|---:|
| 1 | 1.00000 | 0.81832 | 0.98171 | 0.93085 | 1 |
| 2 | 0.77395 | 1.00000 | 0.95520 | 0.99972 | 2 |
| 4 | 0.67322 | 0.77810 | 0.85219 | 0.93347 | 4 |
| 8 | 0.61381 | 0.67499 | 0.72880 | 0.77452 | not reached |
| 13 | 0.59814 | 0.62203 | 0.64069 | 0.65273 | not reached |

The result supports a controlled representation-complexity/model-interaction frontier: capacity of the appropriate order can recover accessibility, while tested degree-4 capacity remains insufficient once the explicit inverse-coordinate degree is much higher. The non-monotonic higher-degree results at block 1 are retained; generic polynomial expansion is not claimed to be universally beneficial.

## N7 — exact predictive-state compression reduces nuisance burden

This experiment is intentionally **not same-information**. The minimal arm `r=x*c` discards world-state information but is exactly sufficient for the target `Y`; full `(x,r)` retains recoverable world state, and padded adds `4k` independently generated nuisance signs.

| k | Minimal 90% threshold | Full | Padded | Full/minimal | Padded/minimal |
|---:|---:|---:|---:|---:|---:|
| 17 | 64 | 128 | 512 | 2x | 8x |
| 33 | 128 | 256 | 1024 | 2x | 8x |
| 65 | 512 | 1024 | 2048 | 2x | 4x |

Median full/minimal threshold ratio is `2x`; median padded/minimal is `8x`. The maximum absolute nuisance-label correlation in the preserved workflow artifact is `0.0286118235`, below the preregistered `0.04` independence sentinel.

At k=65 and 4096 samples, minimal/full/padded mean accuracies are `1.0 / 0.9997559 / 0.9709066`, with mean log losses `0.0326718 / 0.0363818 / 0.0726977`.

This supports a target-specific predictive-sufficiency result: unnecessary state can impose measurable sample burden on a bounded learner. It does not imply that shorter prompts or lossy compression are universally beneficial.

## Runtime-gated experiments are already analysis-complete

`RUNTIME_GATED_ANALYSIS_CONTRACT_V1.md` and `analyze_runtime_gated_novelty_v1.py` freeze the analysis and promotion rules for:

- P9 multi-size LLM structure x scale x compute;
- P10 native-state incremental value;
- P10 proof-action abstraction phase diagram;
- same-information Lean feedback repair;
- P10 cross-revision structural transfer.

Missing runtime artifacts produce explicit `CANNOT_CHECK_*`; malformed artifacts produce `INVALID_*`. Neither may be treated as evidence.

## Strongest currently earned controlled statement

> For the frozen generated-world families, representation changes computational accessibility for restricted hypothesis classes even when latent information is held fixed: explicit relation coordinates reduce required interaction order, shift observed sample/capacity thresholds, stabilize predictions across exact semantic symmetries, and avoid large losses induced by higher-degree invertible coordinate maps. Increasing model interaction degree can recover accessibility when it matches the representation's algebraic access degree. Separately, exact predictive-state compression shows that retaining target-irrelevant state can materially increase sample burden.

This is **not** yet a transformer scaling law, a natural-language chain-of-thought result, a native Lean proof-state utility result, or a universal computational lower bound.

## Blocked revolutionary rungs

`representation changes the LLM scaling frontier` remains blocked until the frozen P9 multi-size LLM experiment produces an on-grid model-scale or inference-budget substitution under same-information controls.

Cross-domain law language remains blocked until a formal-domain same-information result clears P10's native-state/representation gates. Existing P10 tactic-history transfer does not satisfy that condition.
