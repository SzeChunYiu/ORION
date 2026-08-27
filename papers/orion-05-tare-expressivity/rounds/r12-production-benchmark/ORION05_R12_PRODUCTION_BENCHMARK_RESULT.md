# ORION-05 Round 2 result: exact, but no measured production value

Date: 2026-08-27
Science terminal: `ORION05_R12_EXACT_BUT_NO_PRODUCTION_VALUE`
Status: **NULL/ADVERSE ROUND CONSUMED; SCIENCE REMAINS OPEN**

The prospectively frozen H4/N2 comparison completed on LUNARC job `3549607`.
All source bindings and subject reconstructions passed. The two exact solvers
agreed on every shared completed correctness cell, and every completed witness
verified. The unrestricted 512-state referee completed all six full-subject
cells. The support-two direct solver timed out on all six full-subject cells
under the frozen 120-second limit, so it had no qualifying 25% improvement and
the predeclared production-value rule failed.

## Preserved execution facts

- 120 attempts: 108 completed, 12 timed out, zero non-timeout errors;
- six of the timeouts are the support-two full-subject cells;
- unrestricted full-subject median wall time: `263730846 ns`;
- no support-two full-subject resource median exists because those cells did
  not complete;
- exact aggregate SHA-256:
  `3514b160acdb506e94c18e043190f118511fb628ad6a3629b811bb5b4c7c5c2a`;
- exact raw JSONL SHA-256:
  `69294c9633c51d4ee32bdf869b1a7eed39f52f72ff51eb47126365fb50ead251`.

Attempt 1, job `3549585`, is retained as
`ORION05_R12_ATTEMPT1_FAILED_POST_MEASUREMENT_ENVIRONMENT_RECEIPT__NO_ROUND_TERMINAL`.
It finished all 120 measurement children but failed before aggregation because
the archive deployment had no `.git` directory. The defect-only successor
validates `SOURCE_COMMIT.txt` instead. After attempt 2 emitted a valid terminal,
the two raw files were compared: attempt IDs, completion/timeout status, exact
costs, witnesses, planned states, and all other non-machine-specific fields are
identical. Timing, RSS, verification timing, and process IDs differ. This does
not retroactively promote attempt 1 into a round terminal.

## Consequence

Round 2 is consumed adversely. The Round-1 exact `O(n^9)` theorem for the
frozen grammar remains valid, but it did not yield measured production value
on this frozen panel and implementation. The only permitted Round-3 successor
is a prospectively frozen, scientifically distinct safe-ordering or bounded-
parallelism mechanism. R12 thresholds or the exposed H4/N2 panel may not be
retuned.

No generic TARE, physical-resource, compiler, novelty, external-independence,
journal, or submission claim follows. Protected Task-3/P9 is untouched.
