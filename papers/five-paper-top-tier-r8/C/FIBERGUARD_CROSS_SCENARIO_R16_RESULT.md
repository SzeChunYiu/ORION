# FiberGuard R16 result — marginal certificates transfer; selective value does not

Date: 2026-08-26

Protocol execution commit: `d8f61c26142a5b4e2e7f6d36b6525f435e590bae`

Workflow run/job: `33015568382` / `98332774242`

Issue receipt: `#1386` comment `5431368114`

Full result SHA-256: `61ad624b20209082ba795f9b75ac1dff64e87bef4d1aa24599715bc9a8207731`

Observed terminal:

`FIBERGUARD_R16_NO_PORTABLE_CERTIFICATE_VALUE`

## 1. Prospectively frozen question

After exact-equality transfer failed in R14, R16 asked whether a probabilistic action-regret certificate could transfer across later SAT solver portfolios. The configuration was selected only on `SAT16-MAIN`, validated without retuning on `SAT18-EXP`, and applied unchanged to the untouched `SAT20-MAIN` method test. The solver-regret model was refit within each scenario because the solver portfolios differ.

The portable representation contained 50 common deterministic features. Proper training, calibration, and test folds were disjoint. All learned and selective arms paid the declared feature acquisition cost and used one statewise virtual-best PAR10 oracle.

The complete audit was executed twice byte-identically. Every source blob, nested fold, authority flag, result digest, issue receipt, and artifact digest was checked by the dedicated workflow.

## 2. The development gate failed before validation mattered

The prospectively frozen menu contained 192 model/certificate configurations. None met the SAT16 development feasibility constraints. The retained global objective minimum used:

- ExtraTrees with 128 trees;
- `min_samples_leaf=1`;
- `max_features=0.5`;
- `alpha=0.2`;
- `epsilon=cutoff`.

The full learned selector was useful:

- robust fallback mean excess: `9646.997321167883`;
- selected full-model mean: `4478.622343065694`;
- full-model catastrophic rate: `0.08759124087591241` versus fallback `0.19343065693430658`.

The conformal selective policy had empirically small joint false-certificate rate `0.040145985401459854`, well below the registered `alpha+0.02` check. It deployed on `67.52%` of instances. But its mean excess was `6100.819890510949`, retaining only `68.61%` of the full model's gain over fallback, and its catastrophic rate rose to `0.12043795620437957`.

The certificate was not rejected because it lacked marginal calibration. It was rejected because abstention routed difficult cases to a fallback that was less effective than the learned action on those rejected states.

## 3. Validation preserved prediction value but not selective value

On SAT18:

- fallback mean excess: `29244.235337151156`;
- selected full-model mean: `4581.444667507015`;
- selective mean: `8349.72689029404`;
- deployment coverage: `85.84%`;
- joint false-certificate rate: `0.0679886685552408`;
- full-model catastrophic rate: `0.0906515580736544`;
- selective catastrophic rate: `0.1671388101983003`.

The selective policy retained `84.72%` of the full-model gain, below the frozen 90% requirement, and increased catastrophic error. The validation gate therefore failed without retuning.

A frozen ExtraTrees reference performed better than the development-selected configuration: mean `4333.630458569199` and catastrophic rate `0.08498583569405099`. This is additional evidence that one development-selected hyperparameter tuple was not a strongest portable baseline.

## 4. The untouched test showed a different rejection regime

On SAT20:

- fallback mean excess: `9780.9137919366`;
- selected full-model mean: `7862.35229708885`;
- selective mean: `7642.60598043885`;
- deployment coverage: `68%`;
- joint false-certificate rate: `0.085`;
- full-model catastrophic rate: `0.1275`;
- selective catastrophic rate: `0.1225`.

Here abstention slightly improved both mean and catastrophic error relative to the selected full model. However the untouched gate still failed: p95 and total-cost constraints were not all met, the SAT16 development gate had already failed, and the frozen 16-NN reference was materially better at mean `6792.663230521351` and catastrophic rate `0.105`.

The SAT20 result is not permission to tune the SAT16-selected rejection rule after seeing the test. It is evidence that the value of abstention depends on whether the fallback is better or worse than the learned action on the rejected subset.

## 5. Exact rejection-set decomposition

Because the full and selective learned arms pay the same feature cost and use the same learned action on deployed states, their mean difference is entirely determined by rejected states:

`E[L_selective-L_full]`

`=P(reject) E[R(fallback,X)-R(learned,X) | reject]`.

The R16 aggregate values imply:

- SAT16: fallback exceeds learned loss on rejected states by about `4994.18` on average;
- SAT18: fallback exceeds learned loss on rejected states by about `26604.07`;
- SAT20: fallback is better on rejected states by about `686.71`.

For catastrophic events, the same identity gives rejected-set rate differences of approximately:

- `+0.1011` on SAT16;
- `+0.54` on SAT18;
- `-0.015625` on SAT20.

This is the next exact theory boundary. A certificate about the learned action does not by itself certify that the fallback is safer on rejected states. Selective value requires **fallback alignment**, not calibration alone.

## 6. What R16 refutes

The following claims are not admissible:

- marginal conformal action-regret coverage automatically improves solver-decision safety;
- abstention is beneficial merely because the learned action is uncertain;
- a robust global fallback is safer than a learned action on the certificate-rejected subset;
- one SAT16-selected model/certificate tuple transfers as a strongest SAT18/SAT20 selector;
- empirical joint false-certificate control establishes worst-case fibre safety;
- successful application of one configuration without retuning is successful value transfer.

The original result field `method_configuration_transfers_across_three_pinned_scenarios=true` means only that the method configuration was applied without retuning. The scientific result is `successful_method_value_transfer=false`.

## 7. Positive content retained

R16 supplies useful positive evidence:

1. a 50-feature representation schema was portable across three distinct SAT solver portfolios;
2. learned regret prediction had substantial decision value on all three scenarios;
3. the frozen marginal false-certificate estimand remained empirically below `alpha+0.02` on development, validation, and untouched test;
4. the protocol cleanly separated calibration validity from paid selective utility;
5. the untouched test exposed a sign reversal in fallback alignment rather than being used for retuning.

This combination is more informative than a favorable same-corpus selective result. It identifies why a calibrated certificate can fail as an operational controller.

## 8. Correct manuscript claim

The admissible application statement is:

> A marginal action-regret certificate can transfer across pinned solver portfolios without yielding portable selective decision value. On SAT16 and SAT18, rejected cases were precisely those on which the robust fallback was worse than the learned action; on untouched SAT20 that alignment reversed slightly. Calibration and fallback safety are independent obligations.

The paper should retain R11's positive complete-corpus certificate, R14's exact-equality transfer refutation, R15's coverage-tax theorem, and R16's calibrated-but-nonvaluable selective result as one coherent progression rather than selecting only favorable panels.

## 9. Remaining top-tier gate

The next theorem must characterize fallback alignment exactly. The next experiment must freeze, on a new development subject:

- a fallback or route action with its own conditional loss model;
- a decision rule comparing certified learned-action upper loss against certified fallback upper loss;
- a no-acquisition route option where appropriate;
- stronger algorithm-selection baselines such as AutoFolio/current robust portfolio methods;
- an independent implementation and at least one untouched non-SAT or production-derived portfolio.

The successor must preserve the possibility that no route action is conditionally safer. External reproduction, strongest-baseline completeness, production value, novelty, and journal authority remain open.
