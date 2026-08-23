# QG-10C interval-geometry closure calibration — frozen protocol

Issue #842. Base `c5ba39fef4f25c46de5fb69bf07f50530f4693ca`.

## Purpose
Calibrate sound regime certification before claiming scalable interval geometry. Exact ground truth is opened only for scoring; the certificates are defined from already-earned parent theorems/families.

## SixLCU arm — all admitted n=1/n=2 instances
Use the QG-12 P0 all-instance theorem as a certificate, not the full 203-partition optimizer:
- if P0 is true: cost interval is `[C_U,C_U]`, regime=`DONOR_EXACT`;
- if P0 is false: theorem converse gives `C_F <= C_U-1` for integer costs; interval `[0,C_U-1]`, regime=`FAMILY_BETTER`.
After sealing the prediction, reveal `C_F` from `qg4.eval_instance` only for scoring. Domain: all 729 n=1 + 38,760 n=2 instances.

Required: zero false regime certifications and 39,489/39,489 resolved. This success is credited entirely to QG-12/P0, not to generic interval methodology.

## TARE arm — committed QG-7c C1 exact rows
Use exactly the 50 committed `QG7C_CLASSIFICATION_RESULTS.json -> arm_c.c1_realizations.rows`.
Two layers:
1. **Coarse interval only:** `L=0`, `U=min(C_Dplus,f_Bprime,f_Bsecond)` over available values. It may certify an exact cost only if `L==U`; otherwise `CANNOT_CHECK`.
2. **Theorem-assisted:** R6S proves `C_DP=C_Dxx`, so `[C_Dxx,C_Dxx]` is a point interval. This is a theorem-reduced exact family and receives no incremental interval-method credit.
Reveal/score against committed `C_Dxx` after both intervals are formed.

## Scientific interpretation
- Any false certification refutes soundness.
- If SixLCU resolves through P0 but TARE coarse intervals mostly/entirely abstain and only the theorem-assisted point interval resolves them, terminal is:
`QG10_SOUND_CERTIFICATION_CALIBRATED__INCREMENTAL_INTERVAL_VALUE_DONOR_DEPENDENT_OR_WEAK`.
- If coarse TARE unexpectedly resolves useful cases soundly, report the resolved fraction without upgrading to a universal scaling claim.
- `CANNOT_CHECK` is first-class.

No new theorem, novelty, R6, or physical-advantage authority.