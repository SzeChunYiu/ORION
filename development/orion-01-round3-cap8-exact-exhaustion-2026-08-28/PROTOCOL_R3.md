# ORION-01 Round 3 — exact exhaustion extension for the eight R2 cap words

Date frozen: 2026-08-28

## Adaptive question and single lever

Round 2 preserved `CANNOT_CHECK_MOVE_COMPLETENESS` because exactly eight of 585 primary words hit its predeclared 20,000-state cap. Round 3 is an outcome-aware but precommitted successor. It changes one mechanism-matched lever only: those exact eight words are re-run with an exact cap of 500,000 states per word. The pinned PyZX commit (`dade7d46`), 12 registered official site-guarded moves, lossless state serialization, dense semantics including scalar, resource order, native arm, seeded generic control, witness replay, interaction census, and hostile extensions are unchanged.

The eight word indices and tokens are fixed in `SOURCE_BINDING_R3.json`. No other word is reselected or rerun in this attempt. Round-2 completed rows remain binding; a successful aggregate replaces only the eight cap rows.

## Execution and replication

One SLURM array task owns one fixed word. Each task runs from scratch twice and the two canonical JSON receipts must be byte-identical. A setup, dependency, or scheduler failure produces no scientific terminal and does not count. Aggregation refuses missing, non-identical, drifted, or unexpected task receipts.

## Terminals and precedence

1. Any semantics or guard failure aborts the task and retains `AB_R3_ATOMIC_GUARD_UNSOUND` evidence; no positive terminal is allowed.
2. Any task reaching 500,000 states without exhaustion yields `CANNOT_CHECK_MOVE_COMPLETENESS`; no approximate row is promoted.
3. A task that exhausts exactly yields `R3_CAP8_TASK_EXACT_EXHAUSTION_COMPLETE`, which is task-level only.
4. All eight task-level exact terminals, two byte-identical executions each, and a successful reconstruction of the 585-primary plus 16-probe parent domain are required before an `AB_R3_CAP8_EXTENSION_*` full-domain terminal.

## Authority and freeze boundary

Round-1 and Round-2 adverse, null, and `CANNOT_CHECK` records remain visible. This successor changes no current-paper bytes and makes no final-freeze act. Local computation is not external review, novelty authority, journal authority, submission authorization, all-PyZX optimality, compiler superiority, or hardware evidence. `scientific_authority_delta: NONE` is mandatory.
