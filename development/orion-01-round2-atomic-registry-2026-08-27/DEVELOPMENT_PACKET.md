# ORION-01 Round 2 development packet — pinned PyZX atomic checker registry

Date: 2026-08-27
Lane: `papers/orion-01-certificate-realization/experiments/round2-pyzx-atomic-checker-registry/`
Branch: `claude/science-orion01-20260827`
Round accounting: consumes ORION-01 Round 2 of at most 3.

## Purpose

Execute the #1507 immediate order 5 gate: try to establish the AB
production-registry completeness gate by binding ONE real independently
maintained production system (pinned PyZX `dade7d46`) at the granularity its
own source exposes for manual targeting — official site-guarded rewrite
primitives — then test whether certificate realization (exhaustive bounded
minimum over the registry) predicts and controls production transformations
better than the native heuristic (`full_reduce`) and a seeded generic search.

## Root-cause revival (not a relabeling of Round 1)

Round 1's adverse terminal was attributed to ONE stage: whole-macro batch
guards whose matchers mutate during matching. The Round-2 lever binds the
same production system at site granularity, where the official pure
`check_*` predicates exist. Round-1 custody (`r11-pyzx-full-reduce/`) is
untouched.

## Custody sequence

1. Freeze commit: protocol, source registry, runner, verifier, lane test,
   CI workflow, `requirements-lock.txt`, and the pre-outcome infrastructure
   pilot log — all introduced in ONE commit before any outcome access.
2. Execution run 1 on LUNARC (`wtO01-venv`, python 3.11.5 / numpy 2.4.6):
   `orion01_round2_atomic_registry.py execute`.
3. Fresh full re-execution: `orion01_round2_atomic_registry.py check` —
   byte-identical receipts required against the committed files.
4. Outcome commit: full + subset receipts, run logs, claim addendum.
5. CI (python 3.12 / numpy 2.5.2) replays the committed subset receipt
   row-by-row and enforces lane scope + authority boundaries.

## Fail-closed rules

- Any primary-domain per-word state cap hit (20,000 states) →
  `CANNOT_CHECK_MOVE_COMPLETENESS`, no approximate result.
- Any legal atomic move that changes the dense map including scalar →
  `AB_R2_ATOMIC_GUARD_UNSOUND` with full witness.
- All realization gates (audits, exhaustion, native representation,
  semantics, witness replay, 12x12 interaction matrix, freeze binding,
  byte-identical rerun) must pass before any positive/null terminal.

## Authority boundary

PyZX owns the implementation and rewrite primitives. No claim is made about
all of PyZX, the ZX calculus, compiler optimality, hardware, external
novelty, journal readiness, or submission. Round-1 results are preserved,
never relabeled.
