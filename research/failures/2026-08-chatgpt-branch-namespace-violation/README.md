# 2026-08 ChatGPT branch-namespace violation

## Observed

A ChatGPT research session created and wrote to `research/p5-p11-strongest-claim-2026-08-20` before reading the repository-root `AGENTS.md` lane contract. `AGENTS.md` requires ChatGPT sessions to use `shadow/*` branches.

## Failure

The work itself was additive and did not mutate `main`, but the branch identity violated the repository's multi-agent coordination contract. Continuing on that branch would make ownership ambiguous and increase collision risk.

## Failure class

`EXECUTION_IDENTITY_BOUNDARY_MIXUP` — branch namespace/session identity mismatch.

## Correct response

1. stop all writes to the nonconforming branch;
2. preserve its commits rather than rewriting history;
3. rebuild the active work from current `main` on a compliant `shadow/*` branch;
4. close the superseded PR with an explicit explanation;
5. run exact-head checks on the compliant branch before promotion.

The P11 package was rebuilt as PR #621 on `shadow/p11-peer-review-ready-main-2026-08-20`; PR #620 was closed and retained for audit history.

## General lesson candidate

Repository governance files such as root `AGENTS.md` are execution preconditions, not optional documentation. Read them before creating the first write branch, not after scientific work has started. Branch name, tree content and scientific correctness are separate validity coordinates; a good tree on the wrong lane is still an invalid integration object.
