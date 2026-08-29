# Self-ORION V4 confirmatory execution result (2026-08-27)

Protocol: `papers/orion-15-self-orion/protocol/SELF_ORION_V4_REVISION_LEVEL_PROTOCOL_V1.json`
Receipt: `research/self-orion-v4/confirmatory/CONFIRMATORY_EXECUTION_RECEIPT_2026-08-27.json`
(schema `orion.p5.self-orion-v4.confirmatory-execution-receipt.v1`, sha256 `fcb0acf42289583efa265d2f2e396ddd50814944faca074a188957c6e2489e42`)

## What ran

This is the pre-registered revival execution of the V3 lever (frozen in the V3
receipt of 2026-08-24 BEFORE any V4 panel or subject existed): a successor
180-case protected panel whose hypothesis expectation sets are completable
within the bounded protocol (one modeled discriminator per hypothesis, the
committed development-suite contract), ambiguous UNRESOLVED cases, and 20
preservation-conflict cases whose correct terminal requires the revision-gate
blocking branch the V3 panel left unexercised. The subject `FULL_T7_V4`
(`src/orion/study/p5/revision_level_v4_policies.py`) is the V3 `FULL_T7` chain
with exactly one mechanism completion: candidate-visible `preserve:` obligations
are projected into `assess_mechanic` as obligation states plus forbidden
writes, so diagnosis-licensed repairs whose write coordinate is preserved block
with `FORBIDDEN_WRITE` and the policy refuses instead of promoting. All ten V3
baseline arms are delegated verbatim to the unmodified V3 implementation
(`FULL_T7` runs unchanged as the parent arm).

All frozen bindings verified against the committed files before any policy
executed (suite commitment `341e7163...1a864a`, subject revision sha1
`cde12fda4c1a0a8d3f09fc207e6c8b5c6c3fd536`); the committed preflight reported
`READY_TO_FREEZE_CONFIRMATORY` with `authorizes_execution=true`. Eleven frozen
policies ran on the 180-case panel; the orion scorer produced the primary
decision-layer metrics and the two stdlib-only independent evaluators
(decision layer, execution layer) cross-checked them — full agreement for all
eleven policies. Both split halves (PRIMARY_A 90 / REPLICATION_B 90) scored;
full re-execution reproduced every decision digest (H4 determinism ok). No rule
and no policy code was modified after outcome access.

## Measured outcome

| Policy | Accuracy | False-broad | Authority viol. | Correct-UNRESOLVED | Preservation refusal | Harm | Fresh transfer | Cost |
|---|---|---|---|---|---|---|---|---|
| FULL_T7_V4 (subject) | **1.000** | 0 | 0 | 1.000 | 1.000 | 0 | 0.889 | 170.0 |
| FULL_T7 (parent, V3 subject) | 0.889 | 20 | 20 | 0.500 | 0.000 | 0 | 0.889 | 170.0 |
| GENERIC_CAUSAL_DIAGNOSIS | 0.889 | 20 | 20 | 0.500 | 0.000 | 0 | 0.889 | 170.0 |
| RANDOM_DIAGNOSTIC | 0.550 | 9 | 9 | 0.775 | 0.550 | 0 | 0.489 | 128.5 |
| M_OPEN_ONLY | 0.111 | 140 | 30 | 0.000 | 0.000 | 55 | 0.111 | 0.0 |
| WORLD_MODEL_REVISION | 0.111 | 100 | 30 | 0.000 | 0.000 | 35 | 0.111 | 0.0 |
| REPRESENTATION_REGIME_ONLY | 0.111 | 160 | 30 | 0.000 | 0.000 | 65 | 0.111 | 0.0 |
| DIRECT_SELF_EDIT | 0.000 | 180 | 30 | 0.000 | 0.000 | 75 | 0.000 | 0.0 |
| NO_REVISION / ALWAYS_UNRESOLVED (floors) | 0.000 / 0.222 | 0 | 0 | 0.000 / 1.000 | 1.000 | 0 | 0.000 / 0.111 | 0.0 |
| ORACLE_CEILING (analysis only) | 1.000 | 0 | 0 | 1.000 | 1.000 | 0 | 0.889 | 0.0 |

Under the frozen surjective first-match decision rules
(`CONFIRMATORY_DECISION_RULES_V2.json`), rule order 4 fired:
**`REVISION_LEVEL_DISCRIMINATION_SUPPORTED`** — the subject is the only arm
satisfying the full frozen performance content (accuracy 1.000 ≥ 0.75 with
every repair class ≥ 0.5; false-broad 0 ≤ every non-floor; harm 0 ≤ every
non-floor; authority violations 0 ≤ every non-floor; fresh transfer 0.889
noninferior to the best strong comparator 0.889 within the 0.02 margin; and
split-half direction agreement against every strong comparator, subject 1.0/1.0
vs parent 1.0/0.778 and generic 1.0/0.778). Rules 1–3 did not fire: no binding
failed, the oracle ceiling is 1.000, the cross-check agreed, the subject is not
above the safety floors, and no other arm satisfies the content (every strong
arm except the subject takes exactly 20 authority violations on the
preservation-conflict stratum).

The revival is a mechanism effect, not a panel gift: the parent arm — the
unchanged frozen V3 subject — runs the same panel at 0.889 with 20 authority
violations, all 20 concentrated in the preservation stratum where diagnosis
licenses a preserved write; the preservation-wired subject refuses all 20 and
loses nothing measurable (same diagnostic cost 170.0, same fresh-transfer rate
as the oracle ceiling). The V3 negative stays in the record verbatim
(`NO_TERMINAL_UNDER_FROZEN_RULES`, one-stage attribution: two-modeled-
discriminators expectation maps vs the bounded one-probe session); the V4
panel closes that contract gap and adds the preservation stratum.

## Issue #1541 three-arm execution (this panel)

| Arm | Policy | Accuracy | Fresh transfer | Authority viol. |
|---|---|---|---|---|
| (a) no-edit | NO_REVISION | 0.000 | 0.000 | 0 |
| (b) direct-self-edit | DIRECT_SELF_EDIT | 0.000 (180 false-broad, 75 harms) | 0.000 | 30 |
| (c) strongest runnable self-improvement baseline | GENERIC_CAUSAL_DIAGNOSIS (max on panel; ties FULL_T7) | 0.889 | 0.889 | 20 |
| revived subject | FULL_T7_V4 | 1.000 | 0.889 | 0 |

Arms (a) and (b) are nulls on this panel as the frozen protocol predicts:
no-edit never repairs, direct self-edit never finds the licensed class and is
harmful. Arm (c) is the honest measured baseline; the subject beats it on
accuracy and authority violations at identical fresh transfer and cost.

## Secondaries

- H2 diagnostic cost: subject 170.0 == parent == generic — the preservation
  wiring costs zero additional diagnostics (it reuses the same single probe and
  blocks at the gate, not by spending more).
- H3 preservation refusal: subject 1.000 vs generic 0.000 vs parent 0.000.
- H4 determinism: full re-execution reproduced all 11×180 decision digests.
- Feedback non-compensation (subject): accuracy 1.000 NORMAL vs 0.222 under
  NONE/PERMUTED/CONTRADICTORY and 0.678 RANDOM — the subject is
  feedback-dependent, not cached; under no/contradictory feedback it fails
  shut to refusal (0.222 = the ALWAYS_UNRESOLVED-compatible floor), never to
  promotion.

## Boundary

No positive authority is granted by this execution:
`grants_scientific_authority` is false everywhere; scientific authority and
peer-review readiness remain with the result-verification owner (#283). The
terminal is a frozen-rule selection over a benchmark-local protected panel; it
does not certify the live-provider lane (#8), which remains BLOCKED, and does
not modify the V3 record. No manuscript prose, README, or REPRODUCE file is
touched by this change.
