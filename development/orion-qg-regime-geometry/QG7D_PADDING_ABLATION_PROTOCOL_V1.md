# QG-7d spectator-padding ablation — frozen counterexample-first packet

Status: FROZEN BEFORE OUTCOME. Parent issue #836. Base `c5ba39fef4f25c46de5fb69bf07f50530f4693ca`.

## Purpose
QG-7c's T4b local census is exact, but its finite Arm-C target realization gave all six branches the same spectator Z. This packet tests whether that common factor masked a real configuration outside D+ / B′ / B″.

## Frozen rows
Use the exact `failing_verbatim_capped` rows committed in `QG7C_CLASSIFICATION_RESULTS.json`, in stored order, n=3 only. No outcome-based row selection.

## Frozen spectator policies, in order
1. `COMMON_Z`: original QG-7c control `[Z,Z,Z,Z,Z,Z]`.
2. `NO_COMMON_FACTOR`: `[X,Y,Z,X,Y,Z]`.
3. `PAIRWISE_MISMATCH`: `[X,Y,X,Z,Y,Z]`.
4. `MINIMAL_NONZERO`: strip the common Z; add branch-specific `[X,Y,Z,X,Y,Z]` only when the resulting branch would otherwise be identity.

The first three policies replace the q2 spectator letter exactly. `MINIMAL_NONZERO` is deterministic from the stripped target branch and does not inspect costs.

## Exact discriminator
For every row/policy compute exact `C_D++`, `C_D+`, `f_Bprime`, `f_Bsecond`. Only when `C_D++ < min(C_D+,f_Bprime,f_Bsecond)` may unrestricted DP be opened. A replay-confirmed strict gap is terminal evidence of a B‴ residual. Absence is a bounded negative only and routes to J5.

Positive: `QG7D_BTRIPLEPRIME_REGIME_FOUND__PADDING_ABLATION_EXACT_WITNESS`.
Negative: `QG7D_PADDING_ABLATION_NO_BTRIPLEPRIME_IN_FROZEN_ROWS__J5_REQUIRED`.

No theorem may be inferred from the negative. No novelty/R6/physical advantage authority.