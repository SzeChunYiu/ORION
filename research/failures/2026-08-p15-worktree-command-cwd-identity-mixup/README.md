# P15 worktree command CWD identity mixup

## Observed

A compound command created a new P15 worktree and then invoked `git cherry-pick`
without changing the command's working directory. The cherry-pick therefore ran
in the original checkout and created local commit `bfe8be75dce0998bbca5d6897e2da279d6447be2`
on the old local P14 branch. No remote ref was updated.

## Failure

The command treated creation of a worktree at a path as if subsequent shell
operations automatically executed inside that path. They do not: process CWD is
unchanged by `git worktree add`.

## Failure class

`EXECUTION_IDENTITY_BOUNDARY_MIXUP`

## Correct response

Leave the accidental local commit unpushed, verify the intended worktree's branch
and HEAD in a separate command whose `workdir` is the new worktree, and only then
apply the commit. The intended branch received commit
`82b69147c70c4ff44e32ecc8a73f20bbd4c7a27b` before this record was added.

## General lesson candidate

Never combine `git worktree add` with a subsequent mutating Git command unless the
shell explicitly changes directory to the new worktree. Prefer a second tool call
with its `workdir` set to the new path, and print branch plus HEAD immediately
before the mutation.
