# Frontier F6 — Persistence–Reconstruction Tax Protocol V1

Status: **FROZEN BEFORE OUTCOMES**

Frozen: 2026-08-20

## 1. Question

How much reasoning/search cost is paid because a system repeatedly reconstructs the same sufficient state from history instead of persisting it as a first-class object?

This protocol does not claim first proof-state snapshotting or first KV/prompt caching. Its novelty target is the combination of:

- explicit task-sufficiency state analysis;
- branch/replay scaling;
- native resource accounting;
- cross-domain replication.

## 2. Controlled branch-search environment

Reuse the F2 finite transition system after the F2 certificate is frozen.

For every protected current history, generate a search tree with:

- prefix history length `L in {8,16,32,64}`;
- branching factor `b in {2,4,8,16}`;
- branch continuation depth `d=3`.

Each branch queries a distinct continuation/action sequence. All branches share the same current state at the branching point.

## 3. Arms

### R — REPLAY
For every branch independently, reconstruct the current state from the full prefix transcript, then execute the branch continuation.

### PF — PERSIST_FULL
Reconstruct the 10-bit full state once, hash it, and reuse it across every branch.

### PC — PERSIST_CERTIFIED
Construct the F2 5-bit certified state once, hash it, and use a frozen state transition/evaluator that is valid on the certified coordinates for the declared reward/query class.

### H — HEURISTIC_SUMMARY
Persist only the last four actions. Negative control; not certified.

## 4. Exact correctness conditions

Before cost comparison:

- `PF` and `PC` must produce exactly the same branch reward for every protected branch as `R`;
- `PC` must cite the exact F2 future-equivalence receipt;
- `H` must retain any observed mismatches rather than being repaired post hoc.

Any mismatch in PF/PC invalidates the corresponding replay-tax measurement.

## 5. Resource accounting

Measure separately:

- primitive transition operations;
- serialized input bytes/tokens;
- state construction operations;
- state bytes persisted;
- branch continuation operations;
- wall time;
- model calls/tokens in later LLM instantiation;
- verifier/compiler calls in later formal instantiation.

Primary controlled ReplayTax for native operation count:

`RT_ops = ops(REPLAY) / ops(PERSIST_CERTIFIED)`.

Also report `RT_wall` and `RT_tokens` where meaningful.

## 6. Scaling hypothesis

Because replay repeats prefix reconstruction per branch while persistence pays it once, `RT_ops` should increase with `b` and `L` in the controlled environment.

The primary mechanistic terminal

`PERSISTENT_SUFFICIENT_STATE_REDUCES_REPLAY_SCALING`

requires:

1. zero PF/PC correctness mismatches;
2. for every `L`, median `RT_ops` is nondecreasing over `b`;
3. for every `b>=4`, median `RT_ops` is nondecreasing over `L`;
4. at `(L=64,b=16)`, `RT_ops >= 4.0`;
5. PC persisted state is strictly smaller than PF;
6. H has no authority even if it happens to match on sampled branches.

If correctness holds but the cost gate fails, terminal is

`PERSISTENCE_CORRECT__REPLAY_TAX_TOO_SMALL`.

## 7. Lean bridge

Only after a native Lean proof-state corpus/search harness is available:

- `REPLAY_LEAN`: reconstruct elaborated proof state per search branch using the frozen baseline method;
- `SNAPSHOT_FULL`: use a full native snapshot mechanism if reproducibly available;
- `STATE_OBJECT`: reuse the exact native state/dependency object within the frozen ORION search harness.

Nearest-work boundary: `Keep the Proof State Live` already owns the systems observation that snapshotting Lean states can produce large wall-time speedups. ORION may only claim incremental novelty from its task-sufficiency/resource-frontier experiment and matched search-quality analysis.

## 8. Agent/code bridge

In a frozen coding-agent environment, compare:

- replaying the complete action/error transcript to reconstruct progress;
- persistent typed repository/task state;
- lossless-pointer context management baseline where available.

Quality must be measured by task success/test receipts, not just latency.

## 9. Cross-domain promotion

`REPLAY_TAX_GENERALIZES_ACROSS_REASONING_SYSTEMS`

requires positive direction in the controlled environment and at least two real domains with different execution semantics, with native resources reported separately.

## 10. Strongest allowed claim

If earned:

> When multiple reasoning/search branches share a task-sufficient state, reconstructing that state independently from history creates a measurable replay tax. Persisting a certified/verified state shifts the quality-resource frontier by eliminating repeated reconstruction while preserving branch outcomes.

Forbidden:

- claiming the replay tax is always the dominant inference cost;
- claiming first snapshot/cache reuse;
- using wall-time speedup alone as evidence of improved reasoning capability.
