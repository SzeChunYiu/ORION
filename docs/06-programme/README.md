# Phase-4 programme scaffolding — START HERE

**Status: pre-registration only.** Issue #210 is blocked on #209, which is blocked
on #76. Nothing described here is active, no gate is closed, and no authority is
granted. These documents and the `orion.programme` package exist so the Phase-4
record shapes and hostile checks are fixed *before* protected evidence exists,
rather than shaped afterwards to fit whatever arrives.

Read in this order:

| Document | What it settles |
|---|---|
| [Programme protocol](phase-4-programme-protocol.md) | The versioned protocol, the constitutional invariants, and the three knowledge-layer schemas |
| [Dependency invalidation](dependency-invalidation.md) | How the layers co-evolve, and why reopening cannot rewrite history |
| [Anti-collapse battery](anti-collapse-checks.md) | The ten hostile checks and their fail-closed contract |

## The one-paragraph version

A self-sustaining research programme has three kinds of knowledge that must move
together: what it believes about its object (`K`), what it believes is worth
searching (`W`), and how it believes things should be measured (`M`). Each is
versioned, content-bound and provenance-bound. Each carries a typed dependency on
the others, so a discovery in one can invalidate a closure in another; the
invalidation is recorded as an append-only reopen event, never as an edit. A
battery of ten hostile checks looks for the ways such a programme quietly
collapses — onto one benchmark, one evaluator, one source family, one method, or
its own output — and every one of them blocks on absent evidence rather than
passing.

## What is *not* here

- No programme loop, cycle runner, or scheduler.
- No receipts. There are no executed cycles, so there is nothing to receipt.
- No writer for protected evaluators, held-outs, authority policy or phase rules.
- No path that emits the Phase-4 terminal marker. The marker string exists in
  `orion.programme.protocol` under the name `REFUSED_TERMINAL_MARKER`, and
  `tests/unit/programme/test_constitutional_boundary.py` proves no callable in
  the package returns it.

## Code

`src/orion/programme/` — see the package docstring for the module map.
`tests/unit/programme/` — every check declares the negative fixture that shows it
rejecting something, and the battery is asserted clean on a healthy programme.
