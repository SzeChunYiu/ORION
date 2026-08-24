# P2 SYNERGY V5 content-disjoint learner/balancer transport

**Terminal:** `P2_SYNERGY_V5_CONTENT_DISJOINT_LEARNER_BALANCER_ATTRIBUTION_FAILS_ONE_OR_MORE_FROZEN_TRANSPORT_GATES_REQUIRES_SUCCESSOR`

## Scientific identity and boundary

- New identity: `P2_SYNERGY_V5_CONTENT_DISJOINT_LEARNER_BALANCER_TRANSPORT`.
- The five **review decisions** are the review-level units. The 101,044 canonical rows are screening records, not 101,044 independent replications.
- Source: DataverseNL SYNERGY V1, DOI `10.34894/HE6NAQ`, CC0-1.0.
- Claim: prospectively frozen, same-session public content-disjoint transport of the V4 learner/balancer attribution. It is not independent custody, external execution, controller promotion, or superiority.
- All prior V1/V2/V3/V4 terminal identities remain unchanged.

## Before-outcome freeze evidence

| Event | UTC | Outcome status |
|---|---|---|
| source_family_selection_frozen | 2026-08-23T16:57:22.242565+00:00 | FROZEN_BEFORE_LOCAL_SOURCE_DOWNLOAD_LABEL_ACCESS_OR_ANY_V5_MODEL_OUTCOME |
| source_download_bound | 2026-08-23T16:58:36.442560+00:00 | LABEL_HEADERS_ONLY; NO_LABEL_VALUES, CLASS COUNTS, SEEDS, ACTIVE ORDERS, OR MODEL OUTCOMES OPENED |
| population_frozen | 2026-08-23T17:01:38.328643+00:00 | NO_LABEL_VALUES, CLASS COUNTS, SEEDS, ACTIVE ORDERS, OR MODEL OUTCOMES ACCESSED |
| protocol_frozen | 2026-08-23T17:01:38.329069+00:00 | FROZEN_BEFORE_LABEL_VALUES_CLASS_COUNTS_SEEDS_OR_ANY_V5_MODEL_OUTCOME |
| implementation_frozen | 2026-08-23T17:04:15.500602+00:00 | NO LABEL VALUES, CLASS COUNTS, SEEDS, ACTIVE ORDERS, OR V5 MODEL OUTCOMES OPENED BEFORE THIS FREEZE |
| labels_and_model_execution_opened | 2026-08-23T17:04:26.078269+00:00 | OPENED_ONLY_AFTER_ALL_PRECEDING_FREEZES |
| execution_completed | 2026-08-23T17:39:08.656693+00:00 | TERMINAL_FROZEN_IN_RESULT |

The selection, source binding, population, protocol, and implementation hashes existed before V5 labels and model outcomes were opened. This is cryptographic same-session ordering, not third-party registration.

## Content-disjoint population

| Review decision | Source label IDs | Within-review duplicate excess | SWIFT-overlap excluded | Cross-successor excluded | Canonical rows | Included | Excluded |
|---|---:|---:|---:|---:|---:|---:|---:|
| Walker_2018 | 48,375 | 23 | 7,741 | 186 | 40,442 | 615 | 39,827 |
| Brouwer_2019 | 38,114 | 2 | 5 | 103 | 38,009 | 62 | 37,947 |
| Hall_2012 | 8,793 | 10 | 0 | 0 | 8,783 | 103 | 8,680 |
| Wassenaar_2017 | 7,668 | 2 | 988 | 70 | 6,621 | 107 | 6,514 |
| Leenaars_2020 | 7,216 | 5 | 7 | 19 | 7,189 | 580 | 6,609 |

- Final SWIFT overlap: **0**.
- Final pairwise successor duplicate excess: **0**.
- Shared successor content identities before exclusion: **189**.
- Four discarded within-review duplicate-content rows had label disagreement with the deterministically retained smallest-OpenAlex-id row: Walker 2, Hall 1, Leenaars 1. The outcome-blind rule was not changed.

## Frozen arms and complete tail diagnostics

- `R0_L0`: candidate representation and learner.
- `R0_L1`: candidate representation plus V4-selected u4 learner/balancer.
- `R1_L0`: u4 representation plus candidate learner.
- `R1_L1`: u4 representation and learner/balancer.

| Review | Arm | Features | Fits | R@5 | R@10 | R@20 | Frac@R95 | WSS@95 |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Walker_2018 | `R0_L0` | 50,000 | 500 | 0.611382113821 | 0.783739837398 | 0.891056910569 | 0.338039661738 | 0.611960338262 |
| Walker_2018 | `R0_L1` | 50,000 | 500 | 0.691056910569 | 0.796747967480 | 0.944715447154 | 0.218139557885 | 0.731860442115 |
| Walker_2018 | `R1_L0` | 2,268,041 | 500 | 0.645528455285 | 0.798373983740 | 0.915447154472 | 0.254957717225 | 0.695042282775 |
| Walker_2018 | `R1_L1` | 2,268,041 | 500 | 0.687804878049 | 0.793495934959 | 0.944715447154 | 0.216136689580 | 0.733863310420 |
| Brouwer_2019 | `R0_L0` | 50,000 | 494 | 1.000000000000 | 1.000000000000 | 1.000000000000 | 0.030887421400 | 0.919112578600 |
| Brouwer_2019 | `R0_L1` | 50,000 | 494 | 1.000000000000 | 1.000000000000 | 1.000000000000 | 0.022784077455 | 0.927215922545 |
| Brouwer_2019 | `R1_L0` | 1,704,327 | 494 | 1.000000000000 | 1.000000000000 | 1.000000000000 | 0.029019442764 | 0.920980557236 |
| Brouwer_2019 | `R1_L1` | 1,704,327 | 494 | 1.000000000000 | 1.000000000000 | 1.000000000000 | 0.021337051751 | 0.928662948249 |
| Hall_2012 | `R0_L0` | 50,000 | 488 | 0.970873786408 | 0.990291262136 | 0.990291262136 | 0.037572583400 | 0.912427416600 |
| Hall_2012 | `R0_L1` | 50,000 | 488 | 0.990291262136 | 0.990291262136 | 0.990291262136 | 0.026528521006 | 0.923471478994 |
| Hall_2012 | `R1_L0` | 398,148 | 488 | 0.990291262136 | 0.990291262136 | 0.990291262136 | 0.037914152340 | 0.912085847660 |
| Hall_2012 | `R1_L1` | 398,148 | 488 | 0.990291262136 | 0.990291262136 | 0.990291262136 | 0.026870089946 | 0.923129910054 |
| Wassenaar_2017 | `R0_L0` | 50,000 | 473 | 0.757009345794 | 0.850467289720 | 0.962616822430 | 0.165231838091 | 0.784768161909 |
| Wassenaar_2017 | `R0_L1` | 50,000 | 473 | 0.831775700935 | 0.887850467290 | 0.990654205607 | 0.127624225948 | 0.822375774052 |
| Wassenaar_2017 | `R1_L0` | 448,983 | 473 | 0.775700934579 | 0.869158878505 | 0.962616822430 | 0.148013895182 | 0.801986104818 |
| Wassenaar_2017 | `R1_L1` | 448,983 | 473 | 0.831775700935 | 0.887850467290 | 0.990654205607 | 0.127171122187 | 0.822828877813 |
| Leenaars_2020 | `R0_L0` | 50,000 | 480 | 0.350000000000 | 0.632758620690 | 0.846551724138 | 0.306162192238 | 0.643837807762 |
| Leenaars_2020 | `R0_L1` | 50,000 | 480 | 0.387931034483 | 0.643103448276 | 0.887931034483 | 0.273473362081 | 0.676526637919 |
| Leenaars_2020 | `R1_L0` | 404,958 | 480 | 0.374137931034 | 0.631034482759 | 0.877586206897 | 0.294755877034 | 0.655244122966 |
| Leenaars_2020 | `R1_L1` | 404,958 | 480 | 0.382758620690 | 0.644827586207 | 0.889655172414 | 0.278759215468 | 0.671240784532 |

### Unweighted review-level arm means

| Arm | R@5 | R@10 | R@20 | Frac@R95 | WSS@95 |
|---|---:|---:|---:|---:|---:|
| `R0_L0` | 0.737853049205 | 0.851451401989 | 0.938103343855 | 0.175578739373 | 0.774421260627 |
| `R0_L1` | 0.780210981624 | 0.863598629036 | 0.962718389876 | 0.133709948875 | 0.816290051125 |
| `R1_L0` | 0.757131716607 | 0.857771721428 | 0.949188289187 | 0.152932216909 | 0.797067783091 |
| `R1_L1` | 0.778526092362 | 0.863293050118 | 0.963063217462 | 0.134054833787 | 0.815945166213 |

## Every review-level factorial contrast

### Representation main effect

| Review | R@5 | R@10 | R@20 | Frac@R95 | WSS@95 |
|---|---:|---:|---:|---:|---:|
| Walker_2018 | +0.015447154472 | +0.005691056911 | +0.012195121951 | -0.042542406409 | +0.042542406409 |
| Brouwer_2019 | +0.000000000000 | +0.000000000000 | +0.000000000000 | -0.001657502171 | +0.001657502171 |
| Hall_2012 | +0.009708737864 | +0.000000000000 | +0.000000000000 | +0.000341568940 | -0.000341568940 |
| Wassenaar_2017 | +0.009345794393 | +0.009345794393 | +0.000000000000 | -0.008835523335 | +0.008835523335 |
| Leenaars_2020 | +0.009482758621 | +0.000000000000 | +0.016379310345 | -0.003060230908 | +0.003060230908 |
| **Unweighted mean** | **+0.008796889070** | **+0.003007370261** | **+0.005714886459** | **-0.011150818777** | **+0.011150818777** |

### Learner/balancer main effect

| Review | R@5 | R@10 | R@20 | Frac@R95 | WSS@95 |
|---|---:|---:|---:|---:|---:|
| Walker_2018 | +0.060975609756 | +0.004065040650 | +0.041463414634 | -0.079360565748 | +0.079360565748 |
| Brouwer_2019 | +0.000000000000 | +0.000000000000 | +0.000000000000 | -0.007892867479 | +0.007892867479 |
| Hall_2012 | +0.009708737864 | +0.000000000000 | +0.000000000000 | -0.011044062393 | +0.011044062393 |
| Wassenaar_2017 | +0.065420560748 | +0.028037383178 | +0.028037383178 | -0.029225192569 | +0.029225192569 |
| Leenaars_2020 | +0.023275862069 | +0.012068965517 | +0.026724137931 | -0.024342745862 | +0.024342745862 |
| **Unweighted mean** | **+0.031876154087** | **+0.008834277869** | **+0.019244987149** | **-0.030373086810** | **+0.030373086810** |

### Interaction

| Review | R@5 | R@10 | R@20 | Frac@R95 | WSS@95 |
|---|---:|---:|---:|---:|---:|
| Walker_2018 | -0.037398373984 | -0.017886178862 | -0.024390243902 | +0.081079076208 | -0.081079076208 |
| Brouwer_2019 | +0.000000000000 | +0.000000000000 | +0.000000000000 | +0.000420952932 | -0.000420952932 |
| Hall_2012 | -0.019417475728 | +0.000000000000 | +0.000000000000 | +0.000000000000 | +0.000000000000 |
| Wassenaar_2017 | -0.018691588785 | -0.018691588785 | +0.000000000000 | +0.016764839148 | -0.016764839148 |
| Leenaars_2020 | -0.029310344828 | +0.003448275862 | -0.029310344828 | +0.016692168591 | -0.016692168591 |
| **Unweighted mean** | **-0.020963556665** | **-0.006625898357** | **-0.010740117746** | **+0.022991407376** | **-0.022991407376** |

### Preserved full-arm candidate-minus-u4 contrast

| Review | R@5 | R@10 | R@20 | Frac@R95 | WSS@95 |
|---|---:|---:|---:|---:|---:|
| Walker_2018 | -0.076422764228 | -0.009756097561 | -0.053658536585 | +0.121902972158 | -0.121902972158 |
| Brouwer_2019 | +0.000000000000 | +0.000000000000 | +0.000000000000 | +0.009550369649 | -0.009550369649 |
| Hall_2012 | -0.019417475728 | +0.000000000000 | +0.000000000000 | +0.010702493453 | -0.010702493453 |
| Wassenaar_2017 | -0.074766355140 | -0.037383177570 | -0.028037383178 | +0.038060715904 | -0.038060715904 |
| Leenaars_2020 | -0.032758620690 | -0.012068965517 | -0.043103448276 | +0.027402976770 | -0.027402976770 |
| **Unweighted mean** | **-0.040673043157** | **-0.011841648130** | **-0.024959873608** | **+0.041523905587** | **-0.041523905587** |

## Frozen gates

### Learner/balancer transport

| Gate | Result |
|---|---|
| `M1_BINDING` | **PASS** |
| `M2_CONTENT_DISJOINT_POPULATION` | **PASS** |
| `M3_LEARNER_RECALL10_MAGNITUDE` | **FAIL** |
| `M4_LEARNER_RECALL10_SIGN` | **FAIL** |
| `M5_LEARNER_WORK_SAVING` | **PASS** |
| `M6_LEARNER_HARM` | **PASS** |

### Preserved V3 safety/superiority gates

| Gate | Result |
|---|---|
| `G1_BINDING` | **PASS** |
| `G2_POPULATION` | **PASS** |
| `G3_PRIMARY_MARGIN` | **FAIL** |
| `G4_WORK_SAVING` | **FAIL** |
| `G5_HARM` | **PASS** |
| `G6_ABSOLUTE_WORK_SAVING` | **PASS** |

## Result and recursive diagnosis

The frozen V5 primary transport result is adverse. The learner/balancer R@10 main effect was **+0.008834277869**, below the locked **+0.010858985821** magnitude threshold. It was strictly positive in **3/5** review decisions and exactly zero in Brouwer and Hall; the frozen sign gate required at least 4/5 strictly positive. No review had a negative learner R@10 effect, but the protocol did not permit replacing strictly positive with nonnegative after outcomes.

The same learner/balancer contrast was positive at R@5 (**+0.031876154087**), R@20 (**+0.019244987149**), and WSS@95 (**+0.030373086810**). These tail diagnostics motivate—but do not themselves preregister or confirm—a smoother recall-effort-curve discriminator on a new outcome-unopened family.

The preserved full-arm candidate-minus-u4 contrast remained adverse: mean R@10 **-0.011841648130** and WSS@95 **-0.041523905587**. The harm and absolute-work-saving gates passed, but they do not compensate for failed relative gates.

The strongest upward next problem is therefore not post-hoc relaxation of R@10. It is a before-outcome, rank-continuous learner/balancer mechanism test on a lawful family disjoint from both SWIFT and V5, ideally from another source and under independent custody. R@10 remains a locked adverse coprimary endpoint.

## Rights, custody, and transport limits

- All 12 staged source files (287,754,769 bytes) matched Dataverse SHA-1 and local SHA-256; none is copied into this handoff.
- Same-session local execution; no independent custody, external execution, or protected freshness.
- Five decisions are content-identity-disjoint after exclusion, but they share one source release and adapter. Content disjointness alone is not proof of stochastic independence.
- SYNERGY labels are final full-text inclusions. Stage transport to other title/abstract screening decisions is not claimed.
- No source title or abstract appears in any result artifact.
- No arm is promoted and no ORION or controller superiority claim is supported.

## Artifacts

- `SOURCE_FAMILY_SELECTION_FREEZE_V5.json`
- `SOURCE_DOWNLOAD_BINDING_V5.json`
- `SOURCE_RIGHTS_CUSTODY_RECEIPT_V5.json`
- `POPULATION_PREFLIGHT_V5.json` and `POPULATION_AND_CONTENT_FREEZE_V5.json`
- `PROTOCOL_FREEZE_V5.json` and `IMPLEMENTATION_FREEZE_V5.json`
- `PREREGISTRATION_BEFORE_OUTCOME_RECEIPT_V5.json`
- `RESULT_V5.json` and `EXECUTION_RECEIPT_V5.json`
- `FAILURE_ATLAS_V5.json`
- `NEXT_DISCRIMINATOR_REQUIREMENTS_V6.json`
- `SCIENTIFIC_VERIFICATION_V5.json`
- `SHA256SUMS`

No pytest, repository CI, Git mutation, manuscript edit, or shared-checkout write was performed.
