# P10 native-state access root-cause census V1

**Status:** historical-result diagnosis; no successor outcome authority.

**Historical scientific population is unchanged:** Mathlib commit `e72c1e277f31441626621f7d0c7207862fc25569`, Lean `leanprover/lean4:v4.34.0-rc1`, 457 frozen files, 11,842 V2.1 transitions, and the original >=80% native-state eligibility gate.

## 1. Historical result retained

The native-state study executed in GitHub Actions run `32346652258` and terminated `CANNOT_CHECK_NATIVE_STATE_COVERAGE`. Across all eight source-revision shards:

- frozen files: **457**;
- transition denominator: **11,842**;
- eligible native-state transitions: **0**;
- eligibility coverage: **0.0**.

The zero-coverage result is retained. This memo does not convert it into a positive B1-B4 scientific result.

## 2. Complete eight-shard failure census

The eight historical source-shard artifacts are:

| shard | artifact id | archived ZIP SHA-256 |
|---:|---:|---|
| 0 | `9405860060` | `81fd696a1e8e76d4a6d6122301f5691da97010bf26d8031b2c4eb8c297f00015` |
| 1 | `9405853656` | bound by GitHub Actions artifact metadata |
| 2 | `9405778806` | bound by GitHub Actions artifact metadata |
| 3 | `9406291714` | bound by GitHub Actions artifact metadata |
| 4 | `9406301977` | bound by GitHub Actions artifact metadata |
| 5 | `9406280259` | bound by GitHub Actions artifact metadata |
| 6 | `9406224166` | bound by GitHub Actions artifact metadata |
| 7 | `9406189444` | bound by GitHub Actions artifact metadata |

A complete census of the shard JSONs gives:

- `PARTIAL_TRACE`: **180 files**, carrying **2,964/11,842 transitions (25.030%)**;
- `INSTRUMENTATION_UNSUPPORTED`: **153 files**, carrying **8,878/11,842 transitions (74.970%)**;
- `TRACE_GREEN`: **124 files**, carrying **0 transitions**.

Every nonzero-transition file whose instrumented Lean invocation returned success still reported `native_trace_count = 0`. The files labelled `TRACE_GREEN` were zero-transition files.

Therefore the historical `0/11,842` result decomposes into two distinct measurement failures:

1. **source-mutation compatibility failure:** transient source injection made files containing 8,878/11,842 frozen transitions fail instrumentation;
2. **receipt/alignment failure:** files containing the remaining 2,964/11,842 transitions compiled under instrumentation, but the diagnostic-line-number parser recovered zero native states.

This decomposition is a result in its own right: the old `CANNOT_CHECK` cannot be interpreted as evidence that native Lean proof states do not exist or carry no predictive signal.

## 3. Protocol/implementation mismatch

The prospectively frozen amendment `P10_NATIVE_TRACE_STATE_EXTRACTOR_AMENDMENT_V1.md` specified a unique transition marker followed by Lean `trace_state`, so state output could be atomically associated with transition identity.

The executed extractor `extract_p10_native_trace_state_v1.py` instead records:

`extractor_receipt_mode = LEAN_DIAGNOSTIC_LINE_NUMBER`

and inserts only `trace_state`; `states_from_messages` tries to recover transition identity from diagnostic source line numbers. The promised atomic `ORION_P10_STATE::<transition-id>` marker was not present in the executed source instrumentation.

This is an access/receipt defect. It does **not** justify changing the 11,842-transition denominator, excluding difficult files, lowering the >=80% threshold, or changing the B1-B4 endpoint.

## 4. Native non-mutating access exists in the pinned runtime

Lean `v4.34.0-rc1` exposes the language-server request `$/lean/plainGoal` in `src/Lean/Data/Lsp/Extra.lean`. `PlainGoalParams` extends `TextDocumentPositionParams`; the response contains the current pretty-printed tactic goals. Lean's server tests at the same tag (`tests/server_interactive/plainGoal.lean`) exercise the request at tactic-proof source positions.

The same pinned Lean release stores elaborator `InfoTree` information and native tactic contexts internally. A language-server request therefore offers a non-mutating access path on the original source bytes and directly binds each response to a JSON-RPC request id and source position.

This motivates a new **access-mechanism successor**, not a changed scientific target.

## 5. Consequence for the next study

The next study must preserve:

- all 457 files;
- all 11,842 transitions;
- the exact Mathlib and Lean identities;
- the >=80% eligibility gate;
- B1-B4 models, nested regularization, held-module split and success criteria;
- every historical `CANNOT_CHECK`, failed file and unavailable comparator.

It may change only how native pre-tactic state is observed: from source mutation + diagnostic-line inference to direct language-server requests on the exact original source.

If the non-mutating successor still fails to reach >=80%, that failure becomes an ecosystem/state-access boundary. If it reaches >=80%, only then may the unchanged B1-B4 scientific endpoint be evaluated.
