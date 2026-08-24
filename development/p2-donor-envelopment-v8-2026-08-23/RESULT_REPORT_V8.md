# P2 V8 donor-envelopment nested-LORO development study

## Exact adjudicated terminal

`P2_V8_DONOR_ENVELOPMENT_CROSSFIT_FAILS_CRE20_WSS95_AND_HARM__NO_RESIDUAL_ADMITTED__EXACT_U4_FALLBACK`

The execution-level terminal records that a residual activated in at least one outer fold. Post-execution scientific adjudication is adverse: the cross-fitted controller failed CRE20, relative WSS95, and worst-review R@10. This classification is not represented as a retroactive protocol freeze.

## Design

The exact V7 `R1_L1` u4 arm was reconstructed with identical metrics and order hashes in all 14 reviews. Three representation-only residual families, each at alpha 0.10 and 0.25, were evaluated. For each held-out review, only the other 13 reviews could support a configuration; otherwise the emitted order was exact u4.

## Cross-fitted result

| Quantity | Result |
|---|---:|
| Mean delta CRE20 | -0.002009123382 |
| Mean delta R@10 | -0.028273809524 |
| Mean delta WSS95 | -0.000991113755 |
| Worst-review delta R@10 | -0.333333333333 |
| Exact-u4 fallbacks | 12/14 (85.7%) |

No held-out review had a strictly positive CRE20 or R@10 delta after nested selection. The two nonfallback activations were precisely exclusion-fragile: removing a harmed review made the residual pass on the remaining 13, then the residual harmed that held-out review.

| Held-out review | Selected residual | Delta CRE20 | Delta R@10 | Delta WSS95 |
|---|---|---:|---:|---:|
| Shoulderdystocia_positioning | `F1_WORD_PRUNED_A100` | -0.009208103131 | -0.333333333333 | -0.005524861878 |
| Total_knee_replacement | `F2_TITLE_EMPHASIS_A250` | -0.018919624217 | -0.062500000000 | -0.008350730689 |

## Residual diagnosis

| Configuration | Mean delta CRE20 | Mean delta R@10 | Mean delta WSS95 | Worst delta R@10 | Full support |
|---|---:|---:|---:|---:|---|
| `F1_WORD_PRUNED_A100` | -0.000119920062 | -0.023809523810 | +0.001278952546 | -0.333333333333 | false |
| `F1_WORD_PRUNED_A250` | +0.002971151997 | -0.000324675325 | -0.001091932271 | -0.050000000000 | false |
| `F2_TITLE_EMPHASIS_A100` | +0.009018501243 | -0.001217532468 | +0.003228424769 | -0.062500000000 | false |
| `F2_TITLE_EMPHASIS_A250` | +0.010693125060 | -0.001217532468 | +0.002042792819 | -0.062500000000 | false |
| `F3_CHAR_MORPHOLOGY_A100` | -0.003032297898 | +0.006493506494 | -0.020770200388 | +0.000000000000 | false |
| `F3_CHAR_MORPHOLOGY_A250` | +0.001333707306 | -0.026244588745 | -0.025055156866 | -0.333333333333 | false |

Title emphasis is the only family with positive full-grid mean CRE20 and WSS95 at both strengths, but its worst-review R@10 delta is -0.0625, below the unchanged -0.05 floor. Character morphology at alpha 0.10 has nonnegative worst-review R@10 but loses CRE20 and WSS95. No configuration jointly closes the frontier.

## Boundary and next discriminator

KIFMS is open same-workspace development data, not confirmation or independent custody. No residual is admitted and no V7 threshold is relaxed. `NEXT_DISCRIMINATOR_V9.json` carries exactly one bounded diagnostic, title emphasis at alpha 0.25, to a lawful source-disjoint family with unchanged coprimary, work-saving, harm, and absolute-efficiency gates. A positive new-family result cannot overwrite KIFMS harm; a failure retires this residual.
