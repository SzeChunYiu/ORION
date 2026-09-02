# A6's ideal-donor tie gate could not fail

**Date:** 2026-09-02 · **Scientific authority delta:** `NONE`. No theorem, bound or count
changes; this replaces a vacuous control with a measuring one and reports what it measured.

## The defect

ORION-paper#49 gate: *"ideal typed donor ties exactly (otherwise the comparison is not
isolating the claimed relation)"*.

The shipped audit reports `candidate_ideal_exact_tie: true` over all 81 typed states. It
cannot report anything else:

```python
def merged_candidate(record):                     return typed_full_relation(record)
def information_equivalent_typed_donor(record):   return typed_full_relation(record)
```

Both sides delegate to the same function, so `assert cand == ideal` inside
`exhaustive_tie_audit()` is a tautology. The gate exists to certify that the comparison
isolates the claimed relation, and as written it certifies nothing. The module docstring is
candid that the two are "intentionally extensionally identical" — the problem is not the
intent, it is that the *check* of that intent has no way to detect a later divergence.

## The repair

`check_ideal_donor_tie_v1.py` re-derives the ideal donor **independently**, as an explicit
fold over the coordinate alphabet — deny on any refuting coordinate, admit only when every
coordinate is discharged, otherwise could-not-check — sharing no code with the candidate. The
tie is now a measurement.

## What it measures

| result | value |
|---|---|
| typed states enumerated | 81 (exhaustive) |
| candidate vs independently derived ideal | **0 disagreements** — the tie is real |
| candidate vs strongest incomplete donor | **9 of 81 states differ** |

The 9 discriminating states are all in the conservative direction — `ADMIT→DENY`,
`ADMIT→CANNOT_CHECK`, and `CANNOT_CHECK→DENY` (7) — so reading the `scientific_discharge`
coordinate never admits something the incomplete donor denied. **The coordinate is not inert,
which is the positive result the gate was supposed to establish and previously could not.**

## The checker was validated against its own failure modes

| mutation | result |
|---|---|
| break the independent donor (`UNKNOWN → ADMIT`) | **exit 2**, 15/81 disagreements reported |
| make the candidate equal the incomplete donor | **exit 2**, "scientific-discharge coordinate is inert" |
| unmutated | exit 0 |

Exit codes follow the repo convention established in #2084: `0` clean, `2` a finding, `3`
could not check.

## Also found

`TIER_A_BASELINE_EXECUTION_FREEZE_V1.json` records the A6 baseline as
`MERGED_CANDIDATE_TYPED_RELATION`; the shipped `BASELINES` key is `MERGED_CANDIDATE`. A
name-only drift between the frozen record and the implementation, recorded here rather than
silently reconciled — the frozen record should not be edited to match code without a decision.
