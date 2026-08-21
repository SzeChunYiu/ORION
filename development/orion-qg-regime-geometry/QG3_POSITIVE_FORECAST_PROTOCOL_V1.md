# QG-3 prospective positive trade-regime forecast protocol V1

Date: 2026-08-21
Parent programme: ORION #740
Child issue: ORION #745
Base revision: `13a0fc6afb1d150a114ec318d72830e3c6722b03`
Status: **FROZEN BEFORE ANY QG-3 GROUND-TRUTH DP IS OPENED**.
Authority: research protocol only; novelty and publication authority remain external.

## 1. Goal

Find one prospectively predicted **positive** compilation-regime case on previously unread public chemistry data: a matching for which the frozen R6Q structural families predict that the natural weight-one shared-Tag TARE donor is strictly suboptimal.

The result is positive only if the prediction is sealed before unrestricted R6M DP and exact ground truth confirms both the predicted cost and the predicted trade regime.

## 2. Frozen inherited machinery

Reuse without scientific modification:

- public source: `npbauman/DUCC-Hamiltonian-Library` at commit `be306f5830549304176365750d712093950bbdde`;
- R6R tree enumeration, active-space parsing, R6B six-term batch admission and 15 perfect matchings;
- R6L donor minimum `C_R6L`;
- R6O anchor-split family `C_Dplus`;
- R6Q borrow-family minimum `f_B` and simple structural features;
- R6M unrestricted exact DP and witness verifier, but **only in stage 2**.

The R6Q two-trade prediction remains

`predicted_C_DP = min(C_R6L, C_Dplus, f_B)`.

Regime is `split` when the minimum is achieved by `C_Dplus < C_R6L`, otherwise `borrow` when `f_B < min(C_R6L, C_Dplus)`; ties between positive families are recorded explicitly and remain positive if the predicted cost is strictly below `C_R6L`.

## 3. Freshness / exclusion

Exclude every molecule family frozen out by R6R: `{H2, H2O, H4, LiH, N2}`.

Additionally exclude the R6R Benzene subject and blob:

`Benzene/cc-pVDZ/FrozenCoreCCSD_6Elec_6Orbs/DUCC2/benzene.cc-pvdz_files/restricted/ducc/benzene.cc-pvdz.ducc.results.txt`

blob `5c02c72b88e12b391ea1d8f77eb6b3e04fc2a915`.

The protected stretched-N2 path remains forbidden and may never be fetched.

No subject may be admitted if its blob appears in the committed R6R subject set.

## 4. Frozen scan rule

`CANDIDATE_CAP = 12` eligible fresh entries after the exclusions above.

Eligibility and ordering are inherited exactly from R6R: DUCC2/DUCC3 `.ducc.results.txt`, explicit machine-readable even-electron active space, sorted by `(n_qubits, path)`.

For candidates in that order, at most the first 12:

1. fetch/blob-verify through the frozen R6R/R6F machinery;
2. build the frozen R6B six-term batch;
3. require six unique source indices and pairwise commuting targets;
4. enumerate the 15 canonical matchings in existing order;
5. compute **only** `C_R6L`, `C_Dplus`, `f_B`, R6Q features and the predicted two-trade cost;
6. select the first `(candidate-order, matching-order)` satisfying `predicted_C_DP < C_R6L`.

No unrestricted DP may execute anywhere in stage 1. The stage-1 program monkey-patches the R6M exact-DP entry point to raise if called.

If the frozen scan contains no predicted positive, terminal is `QG3_NO_POSITIVE_PREDICTION_IN_FROZEN_SCAN`; the cap/order may not be changed after that outcome.

## 5. Stage-1 packet

The packet binds:

- protocol SHA-256;
- source library/commit and eligible-tree digest;
- all attempted candidate paths/blobs and admission reasons;
- selected fresh subject config and six source indices, if any;
- selected matching;
- `C_R6L`, `C_Dplus`, `f_B`, predicted exact cost and predicted regime;
- R6Q structural features;
- booleans `positive_found`, `no_dp_calls`, `predicate_binding_exact`, `protected_unread`, `freshness_pass`, `admission_gates_pass`;
- `ground_truth_opened: false`.

Stage 1 is the only object visible to both admission harnesses.

## 6. Dual-harness admission

### Lane A — generic ORION research harness

The generic harness runs the stage-1 selector as a local `PYTHON` capability, preserving request/result digests. A second independently implemented generic-admission capability reads only the serialized stage-1 packet plus the frozen novelty-threat packet and emits `OPEN` only when:

- positive candidate exists;
- all stage-1 custody gates pass;
- no DP was called;
- the prediction is strictly donor-suboptimal;
- the novelty-threat packet is frozen and does not identify a close parent owning exact compilation-family regime geometry;
- requested authority remains one prospective structural forecast only.

This is an external-host admission receipt, not independent peer review.

### Lane B — ORION-Q typed campaign controller

A frozen `ORION.ResearchCampaignManifest.v1` first ingests the same stage-1 packet as evidence through a local capability, then the production responsibility/interface/mechanic stack chooses among:

- `REV:OPEN_POSITIVE_REFEREE`;
- `REV:STOP_NO_POSITIVE`;
- `REV:STOP_INVALID`.

The campaign cannot see stage-2 output. Its final terminal receipt is immutable before stage 2.

## 7. Stage 2

Stage 2 runs only when:

- Lane A decision == `OPEN`;
- Lane B terminal == `QG3_NATIVE_OPEN_RECORDED`;
- stage-1 packet digest still matches;
- `positive_found` and all custody gates remain true.

Then reconstruct the selected subject from its pinned path/blob and rerun the frozen batch admission. Assert six indices and selected matching are identical to stage 1. Only then call `r6m.exact_r6m_matching` for the one selected matching.

## 8. Positive gates

`QG3_PROSPECTIVE_POSITIVE_TRADE_FORECAST_CONFIRMED` requires:

1. predicted cost `< C_R6L` before stage 2;
2. both harnesses opened from the same stage-1 packet;
3. exact DP witness checks all pass;
4. `C_DP == predicted_C_DP` exactly;
5. exact truth regime matches predicted positive regime (ties handled by the frozen classification rule);
6. strict donor gap `C_R6L - C_DP >= 1`;
7. source/path/blob freshness and protected-subject gates pass;
8. no post-outcome scan expansion or rule change;
9. novelty authority remains false pending external review.

Honest alternatives:

- `QG3_NO_POSITIVE_PREDICTION_IN_FROZEN_SCAN`;
- `QG3_DUAL_HARNESS_DISAGREEMENT`;
- `QG3_PREDICTION_REFUTED`;
- `QG3_ACCESS_OR_PROVENANCE_CANNOT_CHECK`.

## 9. Claim boundary

A confirmation supports only: the pre-existing two-trade R6Q structural predictor prospectively located one previously unread real-chemistry matching in a donor-suboptimal regime and predicted its frozen-grammar exact support-count cost before unrestricted optimization, under this selection protocol.

It is not a physical quantum advantage, not a new quantum algorithm, not a theorem across compilation families, and not independent novelty authority.
