# Git object/ref identity mix-up during Shadow development

**Observed:** 2026-08-15 while landing the candidate mechanic-action module.

## Failure

The development process created a Git tree and commit, then attempted to update `shadow/self-orion-v0` using the wrong object identity at the ref boundary. GitHub refused the update. No forced ref update was used.

## Failure class

`EXECUTION_IDENTITY_BOUNDARY_MIXUP`

A tree identity, commit identity and branch/ref identity were treated too loosely during orchestration even though they are distinct objects with different admissible transitions.

## Correct response

1. Stop instead of forcing the ref.
2. Inspect/recover the current branch identity and preserve any concurrent work.
3. Move remaining new modular work to `shadow/mechanics-completion-v1` using contents-API commits rather than rewriting the tested base branch.
4. Retain the episode as engineering/execution knowledge.

## General lesson candidate

At any external state mutation boundary, ORION should bind the exact object type plus identity expected by the operation, verify that the current ref/state still matches the precondition, and treat mismatch as a reconciliation/diagnosis event rather than coercing the write. This lesson aligns with the new state, transition, dependency and engineering contracts but still requires transfer evidence beyond Git/GitHub before promotion as a general guard.
