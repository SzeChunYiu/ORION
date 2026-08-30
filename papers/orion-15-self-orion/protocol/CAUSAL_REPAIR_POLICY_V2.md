# ORION-15 causal-repair protocol V2

**Protocol:** `P5.causal-repair.v2`  
**Parent:** `P5.hidden-cause-staged-acceptance.v2`  
**Grandparent:** `P5.hidden-cause-fresh-transfer.v1`  
**Status:** `DESIGN_FROZEN`  
**Outcome access:** false  
**Empirical authority:** `CANNOT_CHECK`

This protocol is additive. It does not rewrite V1 or V2 after outcomes. Architecture completion, attribution accuracy, and replay gain cannot close issue #282.

## Required stages

`STATIC -> DIAGNOSE -> DISCRIMINATE -> CANDIDATE -> REPLAY -> FRESH -> PROTECTED`

- **STATIC** checks frozen structural/compile/invariant requirements.
- **DIAGNOSE** records competing causes, including the adjacent-level pair, without committing a method change.
- **DISCRIMINATE** runs the frozen intervention for that pair and updates cause state.
- **CANDIDATE** binds an isolated change whose class matches the licensed cause.
- **REPLAY** checks motivating/replay evidence already exposed to development.
- **FRESH** checks an independent fresh-transfer split that is not recycled as development feedback.
- **PROTECTED** checks the exact candidate under independently custodied evaluator/holdout authority.

## Change classes

Allowable repair scope is bound to diagnosed responsibility:

- retrieval/routing repair;
- implementation repair;
- environment/tool accommodation that does not hide external failure;
- representation repair;
- measurement/specification repair, which requires host authority;
- method-basis change only after lower-level causes are ruled out.

A lower-level cause must not silently license a broader method rewrite. A discriminator does not itself authorize a method change.

## Fresh-transfer split identities

Motivating, replay, fresh, and protected split hashes remain `UNBOUND` until an external host freeze. Fresh cases must change at least one independent axis among task, domain, model, and environment. Protected holdout identity is generated and frozen outside candidate custody.

## Acceptance doctrine

A candidate is never accepted because its motivating replay improved.

Minimum evidence for a host promotion recommendation:

1. diagnosis/discriminator chain is evidence-bound;
2. replay passes;
3. independent fresh transfer passes;
4. no frozen harmful-transfer safety violation;
5. protected evaluator/holdout integrity passes;
6. negative history includes all rejected/null/harmful candidates;
7. host-only terminal `RECOMMEND_HOST_PROMOTION` — the protocol never self-merges.

Missing fresh transfer yields `BLOCK`. Greedy replay-only acceptance yields `BLOCK`. A recurring fingerprint from negative history yields `BLOCK`. Any known harmful stage yields `REJECT` even if replay rose. PACE/SEA-style anytime-valid statistics may quantify uncertainty but cannot replace fresh transfer or protected custody.

## Terminals

- `TRANSFER_SUPPORTED` requires a prospective cycle with reproducible fresh-transfer/integrity benefit over strong baselines.
- `DIAGNOSIS_ONLY` if causal attribution improves but transfer does not.
- `HARMFUL/REFUTED` if self-improvement creates unacceptable negative transfer.
- `CANNOT_CHECK` if a protected provider/evaluator dependency is unavailable.

This file cannot issue `RECOMMEND_HOST_PROMOTION` for a live campaign. Hosts only may do that from protected evidence.
