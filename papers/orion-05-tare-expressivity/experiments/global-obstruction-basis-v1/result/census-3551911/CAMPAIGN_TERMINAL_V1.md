# ORION05.GLOBAL_OBSTRUCTION_BASIS.v1 — campaign terminal

**Terminal:** `CANNOT_CHECK__CHECKER_DISAGREEMENT`
**scientific_authority_delta:** `NONE`
**Graded by:** the frozen independent checker, not by this session.

## What ran

| Item | Job | Outcome |
|---|---|---|
| CONTROL_GATE (3 R6O planted positives + corrupted-basis firing) | `3551909` | `FAILED`, exit `4:0`, 23m37s on `cx04` |
| Census array, 5,005 instances | `3551911` | 753 array tasks `COMPLETED` |

The census itself is **complete**: `out/instances/` holds all 5,005 per-instance
JSON rows. This is not an incomplete-census terminal.

Runner exit `4` is not an infrastructure failure. In
`run_global_obstruction_basis_v1.py` the `--controls` path returns
`0 if payload["control_gate_passed"] else 4`, so exit `4` is the runner
reporting `control_gate_passed: false` after a clean 23-minute run
(MaxRSS 14 MB — not an OOM, not a timeout).

## Why the terminal is DISAGREEMENT and not CONTROL_FAILURE

The independent checker was self-tested first (`--self-test` → `self_test_passed: true`,
including its malformed-input scenario) and then run against the census
(`--out-dir`, `--protocol`). It exited `2` with:

```
{"verdict": "DISAGREEMENT", "campaign_terminal_for_this_state": "CANNOT_CHECK__CHECKER_DISAGREEMENT"}
```

13 disagreements, 0 `CANNOT_CHECK` rows. **Every disagreement is on one of the three
planted controls; none of the 5,005 census rows disagree.** On its own reckoning the
checker recomputed `CANNOT_CHECK_CONTROL_FAILURE`, but because the two implementations
do not agree on the control records themselves, the admissible terminal is the
disagreement one.

The direction matters. On all three controls the checker recovers what the runner misses:

| Control | Field | Checker | Runner |
|---|---|---|---|
| `C_POS_R6O_16` | `gap_positive` | `true` | `0` |
| `C_POS_R6O_16` | `membership` | `IN_BASIS` | `NO_GAP` |
| `C_POS_R6O_16` | `corrupted_basis_fired` | `true` | `false` |
| `C_POS_R6O_17` | `c_d1` | `6` | `5` |
| `C_POS_R6O_17` | `gap_positive` | `true` | `0` |
| `C_POS_R6O_17` | `membership` | `IN_BASIS` | `NO_GAP` |
| `C_POS_R6O_17` | `corrupted_basis_fired` | `true` | `false` |
| `C_POS_R6O_19` | `c_d2` | `5` | `6` |
| `C_POS_R6O_19` | `gap_positive` | `true` | `0` |
| `C_POS_R6O_19` | `membership` | `IN_BASIS` | `NO_GAP` |
| `C_POS_R6O_19` | `corrupted_basis_fired` | `true` | `false` |

So this is not "the planted positives turned out not to be there." The second,
independent implementation finds them `IN_BASIS` exactly as planted, and also fires the
corrupted-basis control that the runner leaves silent. The runner's census path is the
component under suspicion, and it fails in **both** directions at once: it misses known
positives and it does not alarm on a corrupted basis.

## Consequence

The 5,005-instance census **cannot be graded** T1/T2/T3/T4. A census whose instrument
does not recover planted positives, and does not fire on deliberate corruption, carries
no evidential weight regardless of how complete it is — the rows agreeing between the two
implementations does not rescue it, because agreement on unlabelled rows is not evidence
when the labelled controls fail.

No obstruction-basis claim may be drawn from this run in either direction. In particular
this run supports neither `T1_BASIS_COMPLETE` nor `T4_NO_GAPS_IN_CENSUS`.

## What must not happen next

- The gate must not be relaxed, and the controls must not be re-specified, to let this
  census grade. The clarification window closed at first outcome access
  (2026-08-28 ~20:25Z, recorded in `OUTCOME_ACCESS_LOG.md`); no predicate, threshold,
  terminal or decision-order change is admissible for this campaign.
- The raw rows, the `CONTROL_GATE.json` and this checker report are preserved verbatim
  and must never be rewritten.

## What should happen next

The defect is localized to a disagreement between two implementations on three known
inputs, which is the most tractable possible form of this failure. The next step is a
diagnosis lane that determines which implementation is wrong on `gap_positive`,
`membership`, `corrupted_basis_fired` and the `c_d1`/`c_d2` counts for these three
instances — a comparison over three inputs, needing no cluster time. Only after that is
resolved, under a newly frozen identity, can a census be graded.

## Custody

- `CONTROL_GATE.json` — copied from `/projects/hep/fs9/scratch/scyiu-o05-census/out/`.
- `INDEPENDENT_CHECKER_REPORT.jsonl` — the checker's full 16-line output, verbatim.
- The 5,005 per-instance rows remain on LUNARC at
  `/projects/hep/fs9/scratch/scyiu-o05-census/out/instances/`; they are not copied here
  because the terminal forbids grading them, and they are large.
