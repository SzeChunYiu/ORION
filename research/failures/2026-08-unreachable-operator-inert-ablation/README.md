# An ablation arm that could not run the path it was ablating

**Observed:** 2026-08-21, tracing why P1-U-T1 (#649) is blocked on attribution.

## Failure

The P1-U R6 native trial added an `ORION_NATIVE_BASE` arm for one stated reason
(#723): to show that any gain comes from the ARD addition **rather than merely
from runtime wrapping**. That arm returned `UNRESOLVED` on **48/48 episodes**.

It was not weak. The path it was supposed to exercise was unreachable.

Reproduced against the campaign branch in an isolated scratch tree (12 episodes,
`DIAGNOSE` reached in 0). Every episode produced the same operator sequence:

```text
RECURSE FRAME SEARCH ABSORB RECONSTRUCT DETECT RECURSE SATURATE_BOUNDED
        SEARCH ABSORB RECONSTRUCT DETECT RECURSE SATURATE_BOUNDED
```

The chain, each step verified by instrumenting the operator:

1. `SolverLoop` reaches `DIAGNOSE` **once per material residual**:
   `for residual in material:` where `material` filters `detect.output`.
2. `DetectOperator` emits a residual under exactly three conditions — an unsearched
   candidate domain, no `VERIFIED` claim, or a contradiction between claims.
3. Instrumented, every episode entered `DETECT` in this state:
   `candidate=1 searched=1 unsearched=0 claims=1 verified=1` → **`residuals=0`**.
4. No residual → no material residual → the loop body never runs → no `DIAGNOSE`
   event, so no `diagnose` task ever reaches the provider.
5. `host.diagnosis_tokens` stays empty → `diagnosis_token=None` →
   `_base_responsibility(observed={})` → `UNRESOLVED`, on every episode.

The episode encoding handed the runtime a world with one already-searched domain
and one already-verified claim: a world in which, by construction, nothing is
residual and therefore nothing can be diagnosed.

## Failure class

`UNREACHABLE_OPERATOR_INERT_ABLATION`

An experimental arm was compared against a control that could not execute the
mechanism under test. The comparison is not weak evidence; it is **no evidence**,
because the independent variable was never varied.

Two properties made it survive review:

1. **Static coverage answered a different question.** The harness's
   `execution_coverage` asks whether every canonical mechanic has a resolvable
   execution owner. `DIAGNOSE.v1` resolves to `DiagnoseOperator`, so it reported
   ready — truthfully. Nothing asked whether any *run* reached it.
2. **The campaign's own trace assertion looked, and missed.** It required
   `{FRAME, SEARCH, ABSORB, RECONSTRUCT} ⊆ operator_sequence`. Four operators,
   none of them the one that was absent. A check that enumerates what must be
   present cannot notice what should have been.

The result was fully receipted, digest-bound, leakage-free and reproducible. Every
integrity property held. It still could not support the claim it was built for.

## Correct response

1. Do not score an arm before establishing it executed the mechanism under test.
2. Make that establishable: `orion_research_harness.operator_coverage` reports
   which cycle operators a run actually reached, and
   `require_operators_exercised(outcome, {"DIAGNOSE"}, label="ORION_NATIVE_BASE")`
   **raises**, naming what never ran. One line, on episode one.
3. `run_problem` now returns `operator_coverage` on every outcome, so the
   distinction between *could run* and *did run* is visible without extra work.
4. `compare_operator_coverage` reports when two arms executed identical operator
   sets — an ablation whose arms differ only in parameters is not an ablation of
   the mechanism.
5. Repair the episode encoding so the world presents what the dossier actually
   contains. This is the campaign lane's call and is **not** done here; the
   diagnosis and the instrument are.

## General lesson candidate

**Coverage of the code is not coverage of the run.** A static guarantee that a
mechanism *can* execute is compatible with every execution skipping it, and the
gap between those two is invisible in receipts, digests and integrity checks —
all of which passed here.

The sharper form, and the one that generalizes past this repository: **an
experiment must verify that its independent variable actually varied.** A control
arm is only a control if it ran the thing being controlled for. Everything
downstream — margins, bootstraps, stratified intervals — is arithmetic over a
comparison that was never made.

This is a sibling of
`research/failures/2026-08-digest-representation-boundary-mixup/`. There, a type
error at a boundary was counted as a scientific negative. Here, an unreachable
code path was counted as a scientific comparison. Both are cases of a
**non-scientific fact wearing a scientific result's clothes**, and in both the
receipts were immaculate.
