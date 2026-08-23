# QG-7e V2 — corrected PP single-pinner closure protocol

Date: 2026-08-22
Issue: #872
V1 protected outcome: CANNOT_CHECK reference-binding gap (run 32560168955)
Exploratory V2 binding diagnostic: run 32560548231 / artifact 9472659916
Branch: `codex/orion-qg-qg7e-v2-confirm-20260822`
Status: **FROZEN BEFORE OFFICIAL V2 DUAL-HARNESS OUTCOME.**
Authority ceiling: PP single non-comm-s2 pinner normalization only; chain/global B'' completeness, novelty, R6 and physical advantage remain false.

## Correction relative to V1

QG-7c T4b `envB/envA` letters are residual-space letters. V1 failed its production reference-witness gate because the `ja=1` third-block branch-0 `envB` letter `v0b` was used as a raw target. The exact inverse is

`target3_branch0_b = v0b * Z`

because the reference third-block branch-0 frame at b is Z when `ja=1`.

V1 is preserved unchanged as CANNOT_CHECK. V2 changes only this residual->target binding and freezes fresh corrected fingerprints before official outcome.

## Complete theorem domain

- QG-7c visible PP residuals: 32,556.
- Visible delta histogram: `32116 x +1`, `440 x +2`.
- Visible parameter-cell counts in `(ja,R_b,R_a,p)` lexicographic order:
  `4057,3678,4057,3678,3678,4057,3678,4057,217,187,217,187,187,217,187,217`.
- Hidden tuple order: `(a0,b0,c0,a1,b1,c1)`.
- Hidden states per visible row: `4^6=4096`.
- Complete product: `133,349,376` environments.

## Reference binding gate

For every final hard row and deterministic controls, reconstruct the canonical PP reference frames/Tag and require production R6S:
- acceptance true;
- common ordered labels exactly `(0,1)`;
- `config_cost == C_ref`.

Expected V2 reference verification failures: zero.

No result is promotable if this gate fails.

## Stage A — parent + 576 support-one relocation

Use the unchanged parent G1-G4 bounds and exactly the V1 576-member whole-system support-one relocation library, with one global target-permutation tuple shared across b,a,home.

Corrected frozen expectation from the pre-freeze V2 diagnostic:
- residual count **5,684**;
- all residual deltas exactly `+1`.

## Stage B — exact D+

On exactly those 5,684 rows, evaluate the complete support<=1 family with the same canonical-label symmetry as V1. Expected template count: **61,056**.

Frozen exact `C_Dplus-C_ref` histogram:
- `-2: 132`
- `-1: 2,456`
- `0: 2,716`
- `+1: 380`.

Expected D+ residual count: **380**.

Production `r6p.dxx_search(..., max_weight=1)` must agree on deterministic controls including positive and nonpositive histogram classes.

## Stage C — exact unchanged B′

Evaluate committed QG-5b B′ on exactly the 380 D+ residuals, using all three target coordinates.

Frozen expectation:
- B′ rows: 380;
- `B′-C_ref = -1` on all 380;
- every selected production B′ witness verifies;
- every canonical PP reference witness verifies;
- final residual 0.

No B″, B‴ or new family is allowed in V2.

## Independent generic ORION

Generic ORION must independently rebuild phase-free Pauli/F3 semantics, PP G1-G4, corrected residual->target binding, hidden environment, globally consistent relocation, exact D+ and exact B′. It may reuse prior generic implementation code as an instrument, but may not import production QG-5b/D+ helpers.

Required exact agreement: `32556 -> 5684 -> 380 -> 0` plus all histograms above.

## Native ORION-Q

Positive only if analyzer and generic agree and all reference/production binding gates pass.

On positive:
- `PP_SINGLE_PINNER_ALL_N=true`;
- `CHAIN_ALL_N=false`;
- `GLOBAL_BDOUBLEPRIME_COMPLETENESS=false`.

## Honest terminals

- `QG7E_V2_PP_SINGLE_PINNER_CLOSED_ALL_HIDDEN_ENVIRONMENTS__CHAIN_OPEN`
- `QG7E_V2_REFERENCE_BINDING_GAP`
- `QG7E_V2_RELOCATION_FINGERPRINT_MISMATCH`
- `QG7E_V2_DPLUS_FINGERPRINT_MISMATCH`
- `QG7E_V2_BPRIME_HANDOFF_REFUTED`
- `QG7E_V2_GENERIC_NATIVE_DISAGREEMENT`
- `QG7E_V2_CANNOT_CHECK`

No protected subject access, novelty, R6 or physical quantum advantage follows.