# Self-ORION V3 confirmatory execution result (2026-08-24)

Protocol: `papers/paper-05-self-orion/protocol/SELF_ORION_V3_REVISION_LEVEL_PROTOCOL_V1.json`
Receipt: `research/self-orion-v3/confirmatory/CONFIRMATORY_EXECUTION_RECEIPT_2026-08-24.json`
(schema `orion.p5.revision-level-v3.confirmatory-execution-receipt.v1`)

## What ran

All eight frozen confirmatory bindings (PR #1062) verified against the committed
files before a single policy executed; the committed preflight reported
`READY_TO_FREEZE_CONFIRMATORY` with `authorizes_execution=true`. Ten frozen
policies from `src/orion/study/p5/revision_level_v3_policies.py` ran on the
96-case protected confirmatory panel; the orion scorer produced the primary
decision-layer metrics and the two stdlib-only independent evaluators
(decision layer and execution layer) cross-checked and scored them. Both split
halves (PRIMARY_A 48 / REPLICATION_B 48) were scored. No rule and no policy
code was modified for this execution.

## Measured outcome

| Policy | Accuracy | False-broad | Harm | Fresh transfer |
|---|---|---|---|---|
| FULL_T7 (subject) | 0.125 | 0.000 | 0.000 | 0.125 |
| GENERIC_CAUSAL_DIAGNOSIS | 1.000 | 0.000 | 0.000 | 1.000 |
| RANDOM_DIAGNOSTIC | 0.833 | 0.000 | 0.000 | 0.833 |
| DIRECT_SELF_EDIT | 0.000 | 1.000 | 0.354 | 0.000 |
| M_OPEN_ONLY / WORLD_MODEL / REPR_REGIME | 0.125 | 0.500–0.875 | 0.198–0.302 | 0.125 |
| NO_REVISION / ALWAYS_UNRESOLVED (floors) | 0.000 / 0.125 | 0.000 | 0.000 | 0.000 / 0.125 |
| ORACLE_CEILING (analysis only) | 1.000 | 0.000 | 0.000 | 1.000 |

The independent cross-check agreed with the orion scorer for all ten policies;
both halves agreed on the direction of every FULL_T7-vs-strong-comparator
accuracy ordering. Under the frozen first-match decision rules
(`CONFIRMATORY_DECISION_RULES_V1.json`) **none of the seven terminals fired**:
the subject sat at the safety floor, so every rule requiring the R1 accuracy
bar or the R3 fresh-transfer noninferiority fails, while no binding failed, the
cross-check agreed, and the halves agreed. The receipt records
`NO_TERMINAL_UNDER_FROZEN_RULES` verbatim; no terminal was invented and no rule
was retuned after outcome access.

## One-stage attribution

The confirmatory generator registered TWO diagnostics in every hypothesis
expectation map (the weak probe and the discriminating probe), while the frozen
T7 protocol observes exactly ONE discriminator per bounded session.
`assess_responsibility`
(`src/orion/transfer/v2/epistemic_responsibility.py`) keeps the state UNRESOLVED
while any modeled discriminator of a surviving hypothesis is unobserved
(`REQUIRED_DISCRIMINATOR_OBSERVATION_MISSING`), so the responsibility gate never
identified and FULL_T7 never promoted. The committed development suite
(`research/self-orion-v3/development/PROTECTED_DEVELOPMENT_SUITE_V1.json`)
models one discriminator per hypothesis, which is why development
instrumentation reached FULL_T7 accuracy 1.0. Policy code and gate semantics
are internally consistent; the mismatch is in this panel's expectation
modeling. The frozen panel is retained unregenerated — the measured behavior
(T7 requires complete observational coverage of every modeled discriminator
before any promotion) is a genuine property of the subject mechanism under a
bounded single-probe session.

## Secondaries

- H2 feedback non-compensation: NOT confirmed (accuracy drops 0.0 under NONE
  and PERMUTED; the test is uninformative at the safety floor).
- H3 cannot-check blocking: CONFIRMED (FULL_T7 authority violations 0 on the
  six cannot-check cases; four promoting strong comparators above 0).
- H4 negative-history re-admission: CONFIRMED AS PRE-REGISTERED (the frozen
  policy set is history-blind; round-2 re-admission equals round-1 under both
  readings of the readmit set).

## Boundary

No positive authority is granted by this execution: `grants_scientific_authority`
is false everywhere; scientific authority and peer-review readiness remain with
the result-verification owner (#283). Successor (P5.H1-H4.V4): expectation sets
completable within the bounded protocol plus preservation-conflict cases
exercising the revision-gate blocking branch, with frozen rules surjective onto
the outcome space this execution exposed.
