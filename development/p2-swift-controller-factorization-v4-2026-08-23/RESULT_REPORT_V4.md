# P2 SWIFT V4 controller-component factorization

**Terminal:** `P2_SWIFT_V4_POST_OUTCOME_FACTORIZATION_IDENTIFIES_STABLE_COMPONENT_REQUIRES_CONTENT_DISJOINT_OUTCOME_UNOPENED_FAMILY`

## Scope and integrity

- Frozen identity: `P2_SWIFT_CONTROLLER_COMPONENT_FACTORIZATION_V4`.
- Scope: post-outcome public-development mechanism diagnosis only; not confirmation, controller promotion, or a superiority retest.
- All 30 files in the V3 checksum manifest passed; the V3 source binding, exact population, and both corner reproductions also passed.
- Five review decisions, **96,241 canonical rows per arm**, four arms, **384,964 row-arm evaluations**.
- The 90,520,080-byte private PubMed snapshot and all source bodies remain in the V3 source handoff and were not copied here. No title or abstract is emitted.
- Every V1/V2/V3 adverse terminal is preserved.

## Frozen arms

- `R0_L0`: candidate representation + candidate SGD log-loss/class-weight-balanced learner.
- `R0_L1`: candidate representation + u4 LinearSVC/balanced-ratio-9.8 learner.
- `R1_L0`: u4 representation + candidate learner.
- `R1_L1`: u4 representation + u4 learner/balancer.

## Review/configuration tail diagnostics

| Review | Rows | Arm | Features | Fits | R@5 | R@10 | R@20 | Frac@R95 | WSS@95 |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| BPA | 7,697 | `R0_L0` | 50,000 | 481 | 0.774774774775 | 0.864864864865 | 0.954954954955 | 0.198518903469 | 0.751481096531 |
| BPA | 7,697 | `R0_L1` | 50,000 | 481 | 0.846846846847 | 0.891891891892 | 0.981981981982 | 0.148239573860 | 0.801760426140 |
| BPA | 7,697 | `R1_L0` | 467,539 | 481 | 0.819819819820 | 0.873873873874 | 0.981981981982 | 0.160452124204 | 0.789547875796 |
| BPA | 7,697 | `R1_L1` | 467,539 | 481 | 0.846846846847 | 0.891891891892 | 0.972972972973 | 0.113810575549 | 0.836189424451 |
| Fluoride | 4,477 | `R0_L0` | 50,000 | 448 | 0.882352941176 | 0.941176470588 | 0.980392156863 | 0.143846325665 | 0.806153674335 |
| Fluoride | 4,477 | `R0_L1` | 50,000 | 448 | 0.941176470588 | 0.960784313725 | 0.980392156863 | 0.077730623185 | 0.872269376815 |
| Fluoride | 4,477 | `R1_L0` | 352,541 | 448 | 0.941176470588 | 0.941176470588 | 0.980392156863 | 0.143846325665 | 0.806153674335 |
| Fluoride | 4,477 | `R1_L1` | 352,541 | 448 | 0.960784313725 | 0.980392156863 | 0.980392156863 | 0.050033504579 | 0.899966495421 |
| Neuropain | 29,157 | `R0_L0` | 50,000 | 495 | 0.244861305129 | 0.471762123329 | 0.807024545999 | 0.311794766265 | 0.638205233735 |
| Neuropain | 29,157 | `R0_L1` | 50,000 | 495 | 0.240870085811 | 0.475354220714 | 0.823588106166 | 0.294028878142 | 0.655971121858 |
| Neuropain | 29,157 | `R1_L0` | 1,410,708 | 495 | 0.245459988026 | 0.479545000998 | 0.817601277190 | 0.302671742635 | 0.647328257365 |
| Neuropain | 29,157 | `R1_L1` | 1,410,708 | 495 | 0.241668329675 | 0.477349830373 | 0.820794252644 | 0.298007339575 | 0.651992660425 |
| PFOS-PFOA | 6,309 | `R0_L0` | 50,000 | 486 | 0.778947368421 | 0.915789473684 | 0.978947368421 | 0.111428118561 | 0.838571881439 |
| PFOS-PFOA | 6,309 | `R0_L1` | 50,000 | 486 | 0.831578947368 | 0.957894736842 | 0.989473684211 | 0.086226026312 | 0.863773973688 |
| PFOS-PFOA | 6,309 | `R1_L0` | 466,132 | 486 | 0.768421052632 | 0.884210526316 | 0.978947368421 | 0.142494848629 | 0.807505151371 |
| PFOS-PFOA | 6,309 | `R1_L1` | 466,132 | 486 | 0.821052631579 | 0.936842105263 | 0.989473684211 | 0.103502932319 | 0.846497067681 |
| Transgenerational | 48,601 | `R0_L0` | 50,000 | 496 | 0.643979057592 | 0.816753926702 | 0.908376963351 | 0.247752103866 | 0.702247896134 |
| Transgenerational | 48,601 | `R0_L1` | 50,000 | 496 | 0.678010471204 | 0.829842931937 | 0.958115183246 | 0.191765601531 | 0.758234398469 |
| Transgenerational | 48,601 | `R1_L0` | 2,423,501 | 496 | 0.659685863874 | 0.819371727749 | 0.934554973822 | 0.213802185140 | 0.736197814860 |
| Transgenerational | 48,601 | `R1_L1` | 2,423,501 | 496 | 0.662303664921 | 0.832460732984 | 0.958115183246 | 0.196004197444 | 0.753995802556 |

### Unweighted review-level arm means

| Arm | R@5 | R@10 | R@20 | Frac@R95 | WSS@95 |
|---|---:|---:|---:|---:|---:|
| `R0_L0` | 0.664983089419 | 0.802069371834 | 0.925939197918 | 0.202668043565 | 0.747331956435 |
| `R0_L1` | 0.707696564364 | 0.823153619022 | 0.946710222494 | 0.159598140606 | 0.790401859394 |
| `R1_L0` | 0.686912638988 | 0.799635519905 | 0.938695551656 | 0.192653445255 | 0.757346554745 |
| `R1_L1` | 0.706531157349 | 0.823787343475 | 0.944349649987 | 0.152271709893 | 0.797728290107 |

## Factorial effects

Effects follow the frozen review-level formulas. Positive recall or WSS effects favor R1 over R0 for representation and L1 over L0 for learner/balancer. No pooled-row estimand is substituted.

### Representation main effect

| Review | R@5 | R@10 | R@20 | Frac@R95 | WSS@95 |
|---|---:|---:|---:|---:|---:|
| BPA | +0.022522522523 | +0.004504504505 | +0.009009009009 | -0.036247888788 | +0.036247888788 |
| Fluoride | +0.039215686275 | +0.009803921569 | +0.000000000000 | -0.013848559303 | +0.013848559303 |
| Neuropain | +0.000698463381 | +0.004889243664 | +0.003891438835 | -0.002572281099 | +0.002572281099 |
| PFOS-PFOA | -0.010526315789 | -0.026315789474 | +0.000000000000 | +0.024171818038 | -0.024171818038 |
| Transgenerational | +0.000000000000 | +0.002617801047 | +0.013089005236 | -0.014855661406 | +0.014855661406 |
| **Unweighted mean** | **+0.010382071278** | **-0.000900063738** | **+0.005197890616** | **-0.008670514512** | **+0.008670514512** |

### Learner/balancer main effect

| Review | R@5 | R@10 | R@20 | Frac@R95 | WSS@95 |
|---|---:|---:|---:|---:|---:|
| BPA | +0.049549549550 | +0.022522522523 | +0.009009009009 | -0.048460439132 | +0.048460439132 |
| Fluoride | +0.039215686275 | +0.029411764706 | +0.000000000000 | -0.079964261782 | +0.079964261782 |
| Neuropain | -0.003891438835 | +0.000698463381 | +0.009878267811 | -0.011215145591 | +0.011215145591 |
| PFOS-PFOA | +0.052631578947 | +0.047368421053 | +0.010526315789 | -0.032097004280 | +0.032097004280 |
| Transgenerational | +0.018324607330 | +0.013089005236 | +0.036649214660 | -0.036892245016 | +0.036892245016 |
| **Unweighted mean** | **+0.031165996653** | **+0.022618035379** | **+0.013212561454** | **-0.041725819160** | **+0.041725819160** |

### Interaction

| Review | R@5 | R@10 | R@20 | Frac@R95 | WSS@95 |
|---|---:|---:|---:|---:|---:|
| BPA | -0.045045045045 | -0.009009009009 | -0.036036036036 | +0.003637780954 | -0.003637780954 |
| Fluoride | -0.039215686275 | +0.019607843137 | +0.000000000000 | -0.027697118606 | +0.027697118606 |
| Neuropain | +0.000199560966 | -0.005787268010 | -0.013370584714 | +0.013101485064 | -0.013101485064 |
| PFOS-PFOA | +0.000000000000 | +0.010526315789 | +0.000000000000 | -0.013789824061 | +0.013789824061 |
| Transgenerational | -0.031413612565 | +0.000000000000 | -0.026178010471 | +0.038188514640 | -0.038188514640 |
| **Unweighted mean** | **-0.023094956584** | **+0.003067576381** | **-0.015116926244** | **+0.002688167598** | **-0.002688167598** |

## Frozen classification

- **Learner/balancer: stable within this post-outcome panel.** Mean R@10 effect **+0.022618035379**, same sign in **5/5**, above the effective threshold **0.010858985821**. Mean WSS@95 effect is **+0.041725819160**.
- **Representation: not stable.** Mean R@10 effect -0.000900063738; mean sign in 1/5; below threshold.
- **Interaction: not dominant.** Mean R@10 interaction +0.003067576381; mean sign in 3/5; absolute mean below 0.01.
- `R0_L0` reproduced the V3 candidate and `R1_L1` reproduced the V3 u4 corner exactly in all five reviews, including feature counts, fits, metrics and order hashes.

## Scientific interpretation

The V3 full-arm R@10 gap is mechanistically associated with the learner/balancer contrast in this locked post-outcome factorization, not with a stable representation main effect or a dominant interaction. This narrows the mechanism of the adverse V3 result without rewriting it. Because V4 was designed after V3 outcomes and reuses the same partly overlapping SWIFT decisions, the result cannot promote `R0_L1`, `R1_L1`, or any other arm, cannot establish ORION superiority, and cannot serve as protected confirmation.

The next discriminator is a pre-outcome freeze on a lawful content-disjoint review family with an independently audited population adapter, unchanged active u4 comparator and safety gates, review-level aggregation, complete tail reporting, and no review deletion or post-result tuning.

## Preserved adverse identities

- `P2_ZENODO_V2_ACTIVE_COMPARATOR_TIES_OR_WINS_REQUIRES_CONTROLLER_SUCCESSOR`
- `P2_SWIFT_CROSS_REVIEW_CONTROLLER_TRANSPORT_CANNOT_CHECK_BINDING_OR_POPULATION`
- `P2_SWIFT_V2_CROSS_REVIEW_CONTROLLER_TRANSPORT_CANNOT_CHECK_BINDING_OR_POPULATION`
- `P2_SWIFT_V3_CROSS_REVIEW_CONTROLLER_FAILS_ONE_OR_MORE_PUBLIC_DEVELOPMENT_GATES_REQUIRES_SUCCESSOR`

## Artifact map

- `RESULT_V4.json`: complete arms, metrics, effects, binding and terminal.
- `EXECUTION_RECEIPT_V4.json`: compact counts/configurations/corner receipt.
- `SOURCE_BINDING_RECEIPT_V4.json`: all source-hash and omission boundaries.
- `FAILURE_ATLAS_V4.json`: cause, residual and next discriminator for every retained failure and V4 blocker.
- `NEXT_DISCRIMINATOR_REQUIREMENTS_V5.json`: requirements only; no new family is yet bound or frozen.
- `IMPLEMENTATION_FREEZE_V4.json`, `NEXT_CONTROLLER_SUCCESSOR_PROTOCOL_V4.json`, and runner: exact execution.
- `SHA256SUMS`: handoff integrity.

No pytest, repository CI, Git mutation, manuscript edit, or main-checkout write was performed.
