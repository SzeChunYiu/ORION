# Accidental direct write to `main` during P1-U R2 branch setup

Date: 2026-08-20

## Observed

During setup of the P1-U GPT-R2 protected naturalistic research lane, the intended `shadow/p1-u-gpt-r2-naturalistic-20260820` branch did not yet exist. A subsequent contents-API call accidentally targeted `main` and created `development/p1-u-gpt-r2-naturalistic/DEVELOPMENT_PACKET.md` containing only `x` in commit `9c8fe68bc5b5b1f39155e5e7329b9febff4c7d2a`.

## Failure

A write intended for a session-owned `shadow/*` branch mutated `main` directly.

## Failure class

`EXECUTION_IDENTITY_BOUNDARY_MIXUP` / ref-target precondition failure.

Tree identity, branch/ref identity and intended write destination were not re-verified after the first branch-not-found error.

## Correct response

- Do **not** force-reset or rewrite `main` history.
- Preserve the accidental commit as immutable process history.
- Create a dedicated `shadow/*` repair branch from the exact accidental `main` head.
- Delete only the accidental placeholder on that branch.
- Merge the repair through an ordinary PR.
- Resume P1 research only from a separately created and verified `shadow/*` branch.

## General lesson candidate

A failed contents write caused by `branch not found` must invalidate all subsequent branch-target assumptions. Before the next write:

1. fetch current `main`;
2. create the intended branch explicitly;
3. fetch/search that exact branch and verify its ref;
4. only then issue file writes with the branch argument set explicitly.

Never probe writeability by sending a placeholder contents write.
