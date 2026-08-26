# FiberGuard R15 — pre-aggregate schema repair record

Date: 2026-08-26

Frozen scientific protocol commit: `395466ed0ca7f0b98fc82763623d01aa08500063`

Frozen executor commit: `f919c37fcd2139efa9cbbe08a80814a433ff8301`

Frozen workflow commit: `7187a118bcbfaa8bfc11206609ebe101b3323167`

First execution run/job: `33015635958` / `98333009427`

Terminal:

`PRE_AGGREGATE_SCHEMA_INCOMPATIBILITY`

## What happened

The first R15 job passed exact checkout, all registered Git blob checks available before execution, Python compilation and the hostile self-test. It then stopped while loading the first frozen `algorithm_runs.arff`: the executor assumed that the single declared performance column was literally named `runtime`, but the bound table exposed a different ASlib column name.

No R15 result JSON, aggregate arm metric, scientific terminal or manuscript conclusion was emitted. The algorithm-run table was mechanically parsed before the attribute lookup failed, so this record does not pretend that the raw outcome bytes remained cognitively or mechanically unread. It does establish that no scenario, split, representation menu, support threshold, fallback, lexicographic objective, arm or success gate was changed in response to an aggregate result—none existed.

## Repair

The successor adapter accepts a run table only when its schema has:

- `instance_id`;
- `repetition`;
- `algorithm`;
- `runstatus`; and
- exactly one additional performance attribute.

The observed attribute name is bound into the result for each scenario. Zero or multiple additional attributes fail closed. Runtime aggregation, non-`ok` PAR10 treatment and timeout counting remain byte-for-byte equivalent to the frozen implementation after the column is selected.

The adapter delegates every scientific operation to the frozen R15 executor and records that the scenario registry, splits, arms, objectives and gates are unchanged.

## Authority boundary

This is an engineering compatibility repair. It adds no scientific, transfer, novelty, production or journal authority. The failed first job remains part of the custody chain and is not relabeled as a scientific terminal.
