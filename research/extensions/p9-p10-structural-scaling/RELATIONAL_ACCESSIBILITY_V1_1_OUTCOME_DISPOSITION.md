# Relational Accessibility V1.1 outcome disposition

Status: **COMPLETED; PRIMARY EFFECT STRONG, FROZEN HOSTILE GATE NOT MET**

Execution head: `7db79fab550e62c4a7ca4e527ee14b0859a1d135`

Workflow run: `32313546948`

Artifact id: `9387291134`

Artifact digest: `sha256:4e4de02fe5610d27331d847b2007e7283ba182537578e43b17341a5dcb6d5af8`

The workflow executed the frozen benchmark twice and required byte-identical JSON before evaluating the terminal. Both executions completed and the replay check passed. The artifact is therefore retained even though the positive terminal did not clear.

## Frozen primary effects

At `n_train=4096`, the information-equivalent relational representation reached `1.0` held-out accuracy at every frozen odd dimension, while the flat representation remained approximately chance:

| d | Flat | Relational | Delta |
|---:|---:|---:|---:|
| 3 | 0.507446 | 1.000000 | +0.492554 |
| 5 | 0.510010 | 1.000000 | +0.489990 |
| 9 | 0.500610 | 1.000000 | +0.499390 |
| 17 | 0.493652 | 1.000000 | +0.506348 |
| 33 | 0.500366 | 1.000000 | +0.499634 |
| 65 | 0.498779 | 1.000000 | +0.501221 |

Every preregistered primary representation-effect condition passed:

- relational accuracy `>0.90` at all dimensions;
- flat accuracy `<0.65` at all dimensions;
- relational-minus-flat delta `>0.30` at all dimensions;
- exact reconstruction failures `0`.

The smallest frozen sample size reaching 0.90 relational accuracy was:

- d=3: 64;
- d=5: 64;
- d=9: 128;
- d=17: 256;
- d=33: 256;
- d=65: 1024.

The flat logistic learner did not reach 0.90 at any dimension or frozen sample size through 4096.

## Hostile controls

The broken-relation control passed at every dimension, with held-out accuracies between approximately `0.485` and `0.525`. The shared surface-coordinate permutation changed canonical accuracy by exactly `0.0` for both representations in every dimension. Flat shuffled-label controls remained below `0.65` in every dimension.

The sole failed frozen condition was:

`label_shuffle_lt_0_65_all_dimensions = false`.

Specifically, one fixed shuffled-label draw for the relational representation produced:

- d=3: `0.649658`;
- d=5: `0.718628`;
- d=9: `0.614014`;
- d=17: `0.592163`;
- d=33: `0.505371`;
- d=65: `0.504028`.

Because d=5 exceeded the frozen `<0.65` bound, the terminal is retained exactly as

`RELATIONAL_ACCESSIBILITY_PRIMARY_GATE_NOT_MET`.

## Interpretation of the failure

The failed single-seed shuffle threshold does not erase the large primary effect, but under the frozen V1.1 rules it blocks the controlled positive terminal. At low dimensions the relational representation has a small finite pattern space with many repeated rows; a single random label permutation can by chance assign imbalanced labels to those patterns and induce a high held-out score. A one-seed absolute cutoff is therefore a poorly calibrated randomization control for this finite-support setting.

This diagnosis was made only after V1.1 completed. V1.1 is not amended or rerun under a different threshold. A distinct V2 protocol must use fresh outcome seeds and a distributional label-randomization null frozen before V2 outcomes.

## Claim authority

V1.1 may be cited for its exact measured primary curves and as a falsification of the one-seed hostile-control design. It may **not** be called a positive-terminal experiment.
