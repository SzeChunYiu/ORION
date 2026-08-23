# Worktree command-context mix-up during P11-P15 aggregation

## Observed

While creating the isolated `codex/p11-p15-confirmatory-execution` lane, the
worktree-add command was followed by status and cherry-pick commands whose
working directory still pointed at the pre-existing P1 checkout.  That checkout
was clean at exact head
`ffa745aeaac592c0e198ee8555006936e7cc2fbb` before the accidental writes.

## Failure

Eight already-published P11-P15 commits were cherry-picked onto the checked-out
`codex/p1-diagnostic-ontology-active-base` ref instead of the newly created
worktree branch.  The commit objects were legitimate inputs, but the execution
context selected the wrong branch/ref identity.

## Failure class

`EXECUTION_IDENTITY_BOUNDARY_MIXUP`

The intended worktree path and the process working directory were treated as if
they changed together.  They are distinct state, and Git correctly applied the
commands to the checkout named by the unchanged process working directory.

## Correct response

1. Stop before any push or further edit.
2. Verify that the affected P1 checkout has no uncommitted content.
3. Restore it with `git reset --keep` to its exact original head
   `ffa745aeaac592c0e198ee8555006936e7cc2fbb`.
4. Verify that both `HEAD` and `git status --short --branch` match the original
   clean state; they did.
5. Run all subsequent commands with the isolated path
   `/workspace/orion-p11-p15-execution` supplied explicitly as the working
   directory.

No force operation or remote ref mutation occurred, and no user content was
present or lost.

## General lesson candidate

A successful `git worktree add` does not transition the calling process into the
new checkout.  Every write-capable Git command must bind and report the intended
absolute worktree path, checked-out branch and pre-write head immediately before
execution.  Orchestration should reject a write whenever any of those three
identities differs from the frozen command context.
