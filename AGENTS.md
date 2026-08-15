# Multi-agent development protocol

Several autonomous sessions (ChatGPT, Codex, Claude, possibly others) develop ORION in parallel. This file is the shared lane protocol. It exists because a write collision between agents is an `EXECUTION_IDENTITY_BOUNDARY_MIXUP`-class failure (see `research/failures/2026-08-git-object-ref-identity-mixup/`), and prevention is cheaper than diagnosis.

## Lanes

- Each session works in its **own branch namespace**: `shadow/*` (ChatGPT session stack), `claude/*` (Claude sessions), `codex/*` (Codex sessions). A session never commits to, rebases, or force-updates a branch outside its namespace.
- Each branch has **exactly one writing session** at a time. Reviewing, verifying and commenting on another lane's branch is encouraged; writing to it is not.
- A local working tree belongs to whichever session holds it. Other sessions must not edit files in a working tree they do not own; they read via `git show`/`git archive` on fixed refs.
- Integration happens through PRs to `main` (or to an agreed stack base), never through direct pushes to `main`.

## External state mutation rule

Before any ref update or push, verify the precondition: the remote ref still points where you believe it does. On mismatch, stop and reconcile — never force. Tree identity, commit identity and ref identity are distinct objects with different admissible transitions.

## Verification rule

Verify another lane's work only in isolation: extract with `git archive <ref>` into a scratch directory, install into a private venv, run the suite there. Never run builds or tests inside a working tree you do not own.

## Signaling

- Cross-agent findings about a lane go on that lane's PR as comments, prefixed with the observing session ("Cross-agent verification note (…)").
- Process failures worth learning from become records under `research/failures/` following the existing format (Observed / Failure / Failure class / Correct response / General lesson candidate).
- High-impact code changes require a development packet per `development/README.md` before implementation, whichever agent implements them.

## Conflict minimization

- Prefer **additive files** over edits to files another lane is actively changing; check the other lanes' diffs first (`git diff main..<their-head> --stat`).
- Shared registries (`__init__` exports, decomposition tables) are edited only by the lane that owns the surrounding wave; other lanes queue their edit as a PR comment or follow-up PR after the wave lands.
