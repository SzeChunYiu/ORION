# ORION-01 Round 2 successor development packet — pinned PyZX atomic checker registry

Date: 2026-08-27
Lane: `development/orion-01-round2-atomic-registry-2026-08-27/`
Branch: `claude/science-orion01-20260827`
Authority: successor evidence only; `scientific_authority_delta: NONE`

## Purpose and revival lever

Round 1 attributed its adverse result to whole-macro batch guards whose matchers mutate during matching. Round 2 binds the same independently maintained production system, pinned PyZX commit `dade7d46`, at the official pure site-guarded primitive granularity. Round-1 custody and terminals remain unchanged.

## Custody sequence

1. Commit `05f31ac634459a102e602cbe503c35a9344fee30` introduced the protocol, source registry, runner, verifier, tests, dependency lock, and pre-outcome pilot in one commit before outcome access.
2. Two fresh full LUNARC executions covered 585 primary words plus 16 probes and produced byte-identical raw receipt bytes.
3. The full terminal is `CANNOT_CHECK_MOVE_COMPLETENESS`: eight primary words hit the frozen 20,000-state cap. No approximate result is used.
4. Four completed strict-gap words survive the declared hostile extensions; generic search misses two. This is retained as a bounded positive, not a full-domain terminal; the material full-domain negative remains ACTIVE pending Round 3.
5. After ORION-01 had independently been frozen on main, this lane was relocated additively from the historical paper subpath to `development/`; the raw receipt retains the original introduction paths and commit as historical custody facts. The frozen paper tree is unchanged.

## Verification and authority

`verify_orion01_round2_atomic.py --check` replays all 601 committed rows, including cap rows, and validates the package manifest and attempt ledger. PyZX owns the implementation and rewrite primitives. No claim is made about all PyZX/ZX moves, compiler optimality, hardware, external novelty, journal readiness, or submission. The current ORION-01 paper remains frozen by its existing receipt; this successor makes no freeze act.

## Post-outcome evidence-maintenance correction

The pre-outcome unit test had two stale probe-order assertions (`CX01` first) that contradicted both the frozen `GATE_ALPHABET` (`H0`, `H1`, ...) and the committed receipt (`H0^6`, then `H0^5 H1`). Only those test expectations were corrected after the outcome; the frozen registry, runner, protocol, source lock, raw result, and terminal were not changed. The focused suite then passed 9/9.
