# P9 — Structured Epistemic Learning

Working title: **When Structure Is the Model: Causal Information/Accessibility/Computation Diagnosis Under Explicit Resource Accounting**

Target venue: **Transactions on Machine Learning Research (TMLR)**, subject to the final current-donor and package gate.

## Current scientific identity

P9 is no longer a pre-result architecture proposal. Its current top-tier object is a **causal diagnostic of failure location**: when a task fails, distinguish missing semantic information, inaccessible information/representation, insufficient computation, and missing method/coverage rather than escalating model size or compute generically.

The strongest current claim is supported by three deliberately mixed outcome classes:

1. **real same-information accessibility intervention:** breast-cancer and digits are positive; Wine is retained as a null cell;
2. **protected Qwen scaling hypothesis:** the registered monotone-scaling hypothesis is an authoritative negative, not repaired after the fact;
3. **cross-domain causal diagnostic:** registered diagnosis succeeds on 4/5 task families versus 1/5 for generic compute escalation, with zero false compute escalations versus four for the generic policy; the held-out digits accessibility cell remains `CANNOT_CHECK` because the registered threshold does not transport.

The conclusion survives the corrected full resource ledger.

## Authoritative top-tier evidence

### Causal diagnosis

`top_tier/P9_CAUSAL_DIAGNOSTIC_RESULT_RECEIPT_V1.md` binds the frozen cross-domain study.

- diagnostic accuracy: **4/5 = 0.8**;
- generic compute-escalation accuracy: **1/5 = 0.2**;
- exact executable domains: **3/3** correct diagnosis;
- real digits cells: **1/2**, with the adverse cell retained as `CANNOT_CHECK`;
- false compute escalation: **0** diagnostic vs **4** generic;
- registered-cost regret: **0**;
- independent implementation: GREEN.

### Corrected full I/A/C/M/R accounting

`top_tier/P9_UNIFIED_RESOURCE_LEDGER_RESULT_RECEIPT_V2.md` repairs audited under-counts in the earlier ledger:

- scaler fitted state is charged to `M_state`;
- exact-domain base readout touches are charged to `C_infer`;
- the B-C accessibility serialization is charged to `A_transform`;
- decisions are re-derived rather than hard-coded.

The eight-coordinate vector is

`R9 = (I_sem, A_dim, A_transform, M_state, C_fit, C_infer, C_explicit, R_registered)`.

Authoritative verdict: **`SURVIVES_FULL_ACCOUNTING`**.

The original causal result remains 4/5 vs 1/5, the protected `CANNOT_CHECK` remains, false compute escalation remains 0 vs 4, there are zero vector-dominance contradictions, the causal executor reruns identically, and a second checker is GREEN.

## Hostile representation result — required negative

The earlier D1 same-information serialization margin is **not** a robust headline.

`evidence/P9_U_T3_T4_HOSTILE_ATTACK_RECEIPT_2026-08-21.md` prospectively attacks the representation result.

- a representation-length attack does **not** explain the typed-relational result;
- a semantics-preserving global symbol reminting **does** break the same-information serialized comparator, changing its protected accuracy from `0.75` to `0.50` and changing 32/128 answers;
- therefore the historical `typed relational minus same-information serialized = +0.50` margin is format-prior sensitive and must not be used as a top-tier headline;
- the smaller typed-relational vs untyped-pair separation remains structurally invariant under that orbit;
- an order-reminting attack has an empty denominator under the frozen construction and is `CANNOT_CHECK`, not a pass.

Successor lane (2026-08-24, `NO_SCIENTIFIC_AUTHORITY_REPRESENTATION_REVIVAL_ONLY`, scope
`BOUNDED_D1_ONLY`): the defeat's one-stage attribution is `answer_determination_numerics`
(value spelling keyed the feature columns; the rank-88/150 matrix had equal-fit optima that
solver path and column order alone chose between). The registered successor representation
`TYPED_INVARIANT_PROFILE_BAG` — isomorphism-invariant profile colours over the same token
multiset — holds the raw-token orbit guard at 128/0, is stable under all solver-family and
column-order probes (0 changed answers), and recovers BASE accuracy 0.75 with an independent
second checker GREEN:
`evidence/P9_U_T4_SUCCESSOR_INVARIANT_PROFILE_RECEIPT_2026-08-24.md`.
The frozen defeat itself stands immutable; the retired-margin rule above is unchanged.

This adverse result strengthens the current P9 identity: the paper should diagnose **which resource/representation coordinate matters**, not claim that one serialization is intrinsically superior.

## Strongest paper-level claim

> On the registered cross-domain tasks, failure location is not reducible to generic compute shortage. A frozen causal diagnostic that distinguishes semantic information, accessibility/representation and computation identifies the registered intervention class on 4/5 task families versus 1/5 for generic compute escalation, produces zero false compute escalations versus four, and retains one threshold-transport failure as `CANNOT_CHECK`. These dispositions survive a corrected eight-coordinate resource ledger with no scalarization across resource types. Historical representation margins that fail a semantics-preserving format-prior attack are explicitly retired rather than used as evidence for the causal claim.

## Historical bounded structural-learning paper

The earlier D0/M0/A*/D1 package remains a valid bounded benchmark/methodology record and retains its historical `JOURNAL_READINESS.md`. It is not deleted or rewritten after the later hostile audit.

The current top-tier paper should use that package as the **mechanism-development history**, not as authority for the fragile same-information serialized margin.

## Current manuscript integration

The canonical TMLR source is `manuscript/main.tex`; `build_tmlr_pdf.sh` runs the fail-closed reproduction/audit chain before rendering.

Manuscript-facing integration requirements are in:

`top_tier/P9_TOP_TIER_MANUSCRIPT_INTEGRATION_2026-08-23.md`.

The final manuscript must jointly report:

- real accessibility positive cells;
- Wine null;
- protected Qwen scaling negative;
- causal diagnostic 4/5 vs 1/5;
- protected `CANNOT_CHECK` threshold-transport cell;
- corrected full-accounting survival;
- hostile format-prior negative that retires the old serialized-margin headline.

## Explicit nonclaims

No universal causal diagnosis, no universal neural-model failure, no claim that larger models/compute are generally useless, no scalar exchange rate across the resource vector, no robust `+0.50` same-information serialized superiority claim, no natural-science/LLM/agent generality unless separately executed, and no `TOP_TIER_SUBMISSION_READY` self-promotion from repository prose alone.

Direct open-weight LLM T3/T4 structure×compute claims remain separate: where the required outcome grid was never acquired, the correct state is `CANNOT_CHECK`, not an inferred positive or negative.

## Remaining top-tier work

- rewrite the TMLR abstract/results around causal diagnosis + full accounting;
- remove or explicitly retire format-fragile serialized-margin language from manuscript tables/prose;
- refresh nearest 2026 work on test-time compute, representation/accessibility diagnosis and resource-rational inference immediately before submission;
- add procedural/open-weight breadth only if the headline explicitly claims it;
- regenerate the full evidence summary/tables/PDF from the current receipts;
- rerun clean-environment reproduction, anonymity and clipping/content-binding gates;
- bind exact final manuscript, evidence, environment and PDF bytes.

## Replay determinism (2026-08-24)

The reopened 0.50-vs-0.75 serialized-arm divergence is mechanistically closed
by a one-factor toggle: with bit-identical inputs, identical scipy/scikit-learn
versions, and the identical frozen selection rule, the executing **binary
build** of the numerical stack decides which attractor lbfgs terminates on
(480 iterations → the archived 0.50 with zero per-case flips; 439 iterations →
0.75 with the same 32 UNRESOLVED knife-edge cases flipped). Both sides converge
cleanly; both are deterministic within build; the version manifest
underdetermines the replay. Determinism is enforced by a pinned entry point
whose numeric canary (converged serialized-arm coefficient hash) predicts the
attractor before any accuracy is read, with two clean replays recorded and a
binding checker over the committed tree:

| File | Role |
|---|---|
| `top_tier/replay_d1v1_2_pinned.py` | single documented pinned replay entry point (canary, margins, attractor classification, canonical digest) |
| `top_tier/demonstrate_d1v1_2_build_toggle.py` | two-phase A/B toggle: dump bit-identical designs, refit under any build |
| `evidence/P9_D1V1_2_BINARY_BUILD_TOGGLE_2026-08-24.json` | toggle receipt: both numbers reproduced by the one factor |
| `evidence/P9_D1V1_2_PINNED_REPLAY_R1_2026-08-24.json` / `..._R2_...` | two clean replays, identical cores and digests, archive per-case equality |
| `top_tier/check_d1v1_2_pinned_replay_v1.py` | binding checker over the committed tree (append-only history byte-anchored) |

Nothing is relabelled: the archived 0.5 remains the modal-class prior of a
degenerate comparator, `P9_D1V1_2_LOCKED_ENV_REPRODUCTION_FAILED` stays
append-only, and no claim row changes.
