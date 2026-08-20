# P9/P10 Controlled Novelty Results Ledger V1

Status: **ACTIVE EVIDENCE LEDGER**

Date: 2026-08-20

This ledger separates exact mathematical results, prospectively frozen controlled experiments, failed experiments, and runtime-gated future claim rungs. It does not turn controlled logistic-learning results into LLM or Lean results.

## Evidence table

| ID | Result | Frozen-before-outcome status | Exact outcome | Claim authority |
|---|---|---|---|---|
| N0 | Information-equivalent linear-vs-quadratic relation theorem | mathematical statement independent of data | relational coordinates degree 1; flat affine degree 1 impossible; flat degree 2 sufficient | `PROVED_CONTROLLED_THEOREM` |
| N1 | Relational accessibility V1.1 | yes | primary effects large, but frozen one-draw shuffled-label hostile gate failed | `FAILED_TERMINAL_RETAINED` |
| N2 | Relational accessibility V2 fresh replication | yes, distinct protocol/seeds after N1 | 18/18 cells pass; mean flat `0.5046895`, mean relational `0.9999559`, median delta `0.4979248`, minimum delta `0.4575806` | `SUPPORTED_CONTROLLED_REPLICATION` |
| N3 | Representation × relational-complexity capacity frontier | yes | positive frozen terminal; flat linear never reaches 0.90; relational threshold `{64,64,128,128,512}` across k `{3,5,9,17,33}`; generic flat-quadratic threshold `{64,128,512,4096,NOT_REACHED}` | `SUPPORTED_CONTROLLED_CAPACITY_FRONTIER` |
| N4 | Invertible nonlinear obfuscation ladder | yes | positive frozen terminal; mean linear accuracy falls `1.0000 -> 0.7506 -> 0.6684 -> 0.6176 -> 0.5853 -> 0.5635 -> 0.5369` as block/inverse degree rises `1,2,4,8,16,32,65`; decode failures zero | `SUPPORTED_CONTROLLED_ACCESSIBILITY_TAX` |
| N5 | Controlled semantic-orbit stability | yes | positive frozen terminal; relational mean OIR `{0,0,0.01124}` at k `{9,17,33}` versus flat-quadratic `{0.00268,0.18289,0.31959}`; all target-preservation checks zero | `SUPPORTED_CONTROLLED_SEMANTIC_STABILITY` |
| N6 | Access-degree recovery | yes | execution pending at this ledger version | `PENDING_OUTCOME` |
| N7 | P9 LLM structure × scale × compute | yes | no reproducible multi-size model runtime currently bound | `CANNOT_CHECK_LLM_RUNTIME` |
| N8 | P10 native state incremental value | yes | exact native transition corpus/execution not yet completed | `CANNOT_CHECK_NATIVE_STATE_EXECUTION` |
| N9 | P10 action abstraction / same-information Lean feedback / cross-revision | yes | downstream runtime/corpus prerequisites unavailable | `CANNOT_CHECK_FORMAL_EXTENSIONS` |
| N10 | Cross-domain structural-accessibility law | composition protocol frozen | formal-domain same-information result absent | `BLOCKED_PENDING_SECOND_DOMAIN` |

## N1 — failed V1.1 remains visible

V1.1 is not relabeled as positive. At `n_train=4096`, relational logistic accuracy was `1.0` at all six frozen dimensions while flat accuracy remained near chance, but a single fixed shuffled-label relational control exceeded the frozen `<0.65` condition at low dimension. The frozen terminal remains `RELATIONAL_ACCESSIBILITY_PRIMARY_GATE_NOT_MET`.

The post-outcome diagnosis was that a one-draw absolute shuffle cutoff was poorly calibrated for finite-support low-dimensional relational inputs. That diagnosis motivated a separate fresh-seed V2 with a distributional shuffle null; it did not amend V1.1.

## N2 — fresh replicated information-equivalent accessibility

V2 used six dimensions `{3,5,9,17,33,65}`, three fresh worlds per dimension, `4096` training and `16384` test items per cell, plus 64 shuffled-label null fits per cell.

All 18 cells passed every frozen condition. Aggregate:

- mean flat accuracy: `0.5046895345052084`;
- mean relational accuracy: `0.9999559190538194`;
- median relational-minus-flat delta: `0.4979248046875`;
- minimum delta: `0.45758056640625`;
- maximum delta: `0.51727294921875`.

Every observed relational score exceeded all 64 frozen shuffled-label null fits in its cell, reconstruction failures were zero, broken-relation controls passed, and coordinate-permutation controls passed.

Workflow run `32314020312`; artifact `9387438843`; artifact ZIP SHA-256 `6769c944ba59fd81b9db921ec6eae0b35ed82fcea3c4119a33adca27cea6bb79`.

## N3 — relation coordinates change the observed capacity/sample frontier

The exact theorem establishes that the controlled target is degree 1 in relational coordinates, not affine-linearly separable in flat coordinates, and degree 2 sufficient in flat coordinates. The generic interaction-only quadratic feature expansion has dimension `2k^2+k`, versus `2k` relational features.

Fresh experiment thresholds for 90% held-out accuracy:

| k | Relational linear | Flat quadratic | Flat linear |
|---:|---:|---:|---:|
| 3 | 64 | 64 | not reached |
| 5 | 64 | 128 | not reached |
| 9 | 128 | 512 | not reached |
| 17 | 128 | 4096 | not reached |
| 33 | 512 | not reached | not reached |

At k=17 the observed quadratic-to-relational threshold ratio is `32x`. At k=33, relational reaches the target by 512 samples while generic flat quadratic is only `0.82495117` at 4096. Across cells where both reach 0.90, threshold ratios are `{1,2,4,32}`, median `3.0`.

The quadratic feature count grows from 21 at k=3 to 2211 at k=33 (`105.2857x`), while relational features grow from 6 to 66 (`11x`).

Workflow run `32333835844`; frontier artifact `9393449190`; artifact ZIP SHA-256 `6c04ac6b146b7087eaebd0b76dd45ccab6d61dee25be41553a83223cb6367263`.

## N4 — invertible representation difficulty ladder

The block-chain transform is exactly invertible and preserves all latent bits. Its explicit inverse-coordinate degree rises with block length. On fresh k=65 worlds, mean linear accuracy over three replications is:

| Maximum inverse degree / block | Accuracy |
|---:|---:|
| 1 | 1.000000 |
| 2 | 0.750590 |
| 4 | 0.668447 |
| 8 | 0.617554 |
| 16 | 0.585337 |
| 32 | 0.563507 |
| 65 | 0.536947 |

All six adjacent transitions are non-increasing. The canonical-to-full-chain gap is `0.4630534`; descriptive slope versus `log2(block)` is `-0.0672733`. First mean accuracy below 0.80 occurs at degree 2, below 0.70 at degree 4, and below 0.60 at degree 16. Decode failures are zero.

Workflow run `32333835844`; artifact `9393428588`; artifact ZIP SHA-256 `013c8e1971b04675fdc9c6822ee399661357867cec5ce2d199eaa66e3acaa6d1`.

## N5 — semantic-orbit stability

Models were trained once on canonical data and evaluated under 32 semantics-preserving signed coordinate permutations without retraining. Every transformation exactly preserved the target.

| k | Flat quadratic canonical acc | Relational canonical acc | Flat mean OIR | Relational mean OIR | Flat items with any prediction change | Relational items with any prediction change |
|---:|---:|---:|---:|---:|---:|---:|
| 9 | 0.996826 | 1.000000 | 0.002678 | 0.000000 | 0.076904 | 0.000000 |
| 17 | 0.815918 | 1.000000 | 0.182892 | 0.000000 | 0.820557 | 0.000000 |
| 33 | 0.672363 | 0.988525 | 0.319588 | 0.011238 | 0.993408 | 0.205322 |

Mean relational OIR advantage `(flat - relational)` across k is `0.16463979`. At k=33, the 95th-percentile OIR is `0.5` for flat quadratic versus `0.0625` for relational linear.

Workflow run `32333934412`; artifact `9393963905`; artifact ZIP SHA-256 `539ed0a44d55fabcc9a829c090fbe6458a8c8a5da70c977cf4a9da11018f1a4b`.

## Strongest currently earned controlled statement

The combined controlled evidence supports this bounded statement:

> For a family of information-equivalent encodings, explicit relation coordinates can reduce the interaction order required by a restricted hypothesis class, materially shift its observed sample/capacity frontier, remain more stable across exact semantic symmetries, and avoid a large accessibility loss induced by progressively higher-degree invertible coordinate obfuscation.

This statement is about the frozen controlled hypothesis classes and generated worlds. It is **not** yet a claim about transformer parameter scaling, natural-language chain-of-thought, native Lean proof-state utility, or a universal computational law.

## Blocked revolutionary rungs

The phrase `representation changes the LLM scaling frontier` remains blocked until the frozen P9 multi-size LLM experiment produces an on-grid model-scale or inference-budget substitution under same-information controls.

Cross-domain language remains blocked until a formal-domain same-information result clears P10's native-state/representation gates. Existing P10 tactic-history transfer is important but does not satisfy that condition.
