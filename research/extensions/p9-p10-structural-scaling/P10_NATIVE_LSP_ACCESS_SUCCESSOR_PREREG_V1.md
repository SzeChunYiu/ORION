# P10 native LSP access successor preregistration V1

**Status:** `FROZEN_BEFORE_SUCCESSOR_IMPLEMENTATION_OR_OUTCOME_ACCESS`

This preregistration is additive. It preserves the historical native-state `CANNOT_CHECK_NATIVE_STATE_COVERAGE` result and changes only the state-access/receipt mechanism diagnosed in `P10_NATIVE_ACCESS_ROOT_CAUSE_V1.md`.

## 1. Frozen scientific identity

The successor must use exactly:

- subject corpus: the existing 457-file P10 Mathlib manifest;
- Mathlib commit: `e72c1e277f31441626621f7d0c7207862fc25569`;
- Lean toolchain: `leanprover/lean4:v4.34.0-rc1`;
- transition population: the same V2.1 collapsed source population, denominator **11,842**;
- eligibility threshold: **>=80%** of 11,842;
- B1/B2/B3/B4 definitions, held-top-module splits, nested `C in {0.01,0.1,1.0,10.0}`, primary accuracy/log-loss endpoints and hostile controls from the parent protocol.

No source file, theorem, module or transition may be removed after observing LSP accessibility or model outcomes.

## 2. Only allowed scientific change: state access

The successor access mode is:

`LEAN_LSP_PLAIN_GOAL_DIRECT_V1`

For each frozen original source file, use Lean's pinned language server on the **unmodified source text** and issue direct `$/lean/plainGoal` JSON-RPC requests at frozen tactic positions. The JSON-RPC request id plus frozen source position binds the response to transition identity. Do not inject `trace_state`, markers, imports, helper tactics, comments or other source material into scientific files.

The on-disk source SHA-256 must match the manifest before opening the document and again after all requests.

## 3. Frozen position rule

For every frozen collapsed transition action, use the existing source projector to recover its first source line.

Query position is the first character of the tactic command on that line:

- ordinary line: first non-whitespace character;
- bullet line matching `^(\s*)([·*-])\s+(.*)$`: first non-whitespace character of the command after the bullet and following whitespace.

There is no corpus-specific cursor offset search, fallback offset, nearest-state search or post-outcome position tuning.

## 4. Synthetic calibration before scientific access

Before any scientific file is queried in a shard, run the same LSP access path on a synthetic calibration file that is **not** part of the denominator:

```lean
example : α → α := by
  intro a
  exact a
```

Using the frozen tactic-token-start position rule:

- the `intro a` request must expose a pre-action goal containing an arrow/function goal equivalent in shape to `α → α`;
- the `exact a` request must expose a local context containing an `a : α`-like declaration and a goal equivalent in shape to `α`.

Calibration is structural rather than byte-text exact: it is checked by the same anonymized state feature/parser layer, not by tuning to pretty-printer whitespace.

If calibration fails, the shard terminal is `CANNOT_CHECK_LSP_CURSOR_SEMANTICS`. The implementation must **not** try alternate positions on the scientific corpus.

## 5. Frozen language-server session protocol

Per shard:

1. start one `lake env lean --server` process from the exact Mathlib checkout;
2. send `initialize` and wait for the matching response;
3. send `initialized`;
4. perform the synthetic calibration;
5. for each selected scientific file, send `textDocument/didOpen` with exact source text and version 1;
6. wait using `textDocument/waitForDiagnostics` for version 1;
7. issue all frozen `$/lean/plainGoal` requests for that file;
8. send `textDocument/didClose`;
9. continue to the next file.

Notifications may be interleaved and ignored except for protocol framing; responses are matched only by JSON-RPC id.

**Restart policy:** if the language-server process exits/crashes while processing a scientific file, that file's transitions remain ineligible. The process may be restarted once before the *next* file so one crash does not censor later files. A failed file is never retried until green.

A per-request/per-file timeout is fixed in the workflow before execution and may not be increased selectively after observing which files fail.

## 6. Eligible transition definition

A transition is eligible only if all are true:

1. source identity matches the frozen manifest;
2. the transition is in the exact 11,842-row V2.1 source population;
3. diagnostics processing for the original file completes under the pinned server;
4. the frozen `plainGoal` request returns a non-null result containing at least one goal or the explicit solved-state representation accepted by the parent state parser;
5. a state SHA-256 can be computed;
6. the transition receipt verifies against the unchanged parent receipt material:
   `transition_id, source_path, source_sha256, theorem_name, action_index, previous_family, true_action, state_sha256, mathlib_commit, lean_toolchain`.

A null response, protocol error, timeout or missing state is ineligible with an explicit reason; it is never replaced by source text, theorem names, future actions or proxy features.

## 7. Output compatibility and frozen model analysis

The successor shard may retain schema `P10.NativeTraceStateShard.v1` solely so the already-frozen `fit_p10_native_state_v1.py` can consume it unchanged. It must additionally record:

`extractor_receipt_mode = LEAN_LSP_PLAIN_GOAL_DIRECT_V1`.

The state/dependency feature extraction is the existing frozen anonymized function. Raw goal text, theorem/file/module names and source payload are not predictive model features.

If aggregate eligibility is below 80%, terminal remains:

`CANNOT_CHECK_NATIVE_STATE_COVERAGE`.

If aggregate eligibility reaches >=80%, run the **unchanged** parent B1-B4 fitting and analysis. No model or threshold adjustment is permitted after seeing the new coverage or outcome.

## 8. Access-success terminal

The access layer earns:

`P10_NATIVE_LSP_STATE_COVERAGE_SUPPORTED`

only if:

- synthetic calibration passes on every executed shard;
- aggregate eligible transitions >= 9,474 (the integer minimum satisfying >=80% of 11,842);
- all row receipts verify;
- source bytes remain unchanged;
- transition ids are unique and all belong to the frozen denominator;
- source/runtime/receipt substitution hostile checks fail closed;
- predictive-vector forbidden-identity scan is green.

This terminal establishes native-state **measurement coverage**, not predictive incremental value.

## 9. Scientific positive terminal remains unchanged

After coverage eligibility, `P10_NATIVE_STATE_INCREMENTAL_VALUE_SUPPORTED` still requires the parent conditions, including:

- B4-B1 pooled accuracy > 0;
- module-block bootstrap 95% lower bound > 0;
- >=60% evaluable modules non-negative;
- B4 log loss < B1 log loss;
- eligibility >=80%;
- label-shuffle, identity, future-step, receipt/source/runtime substitution and exact-state near-duplicate controls all pass.

A positive access result cannot rescue a negative B1-B4 result.

## 10. Prespecified interpretations for every outcome

- **coverage >=80%, B1-B4 positive:** non-mutating native proof state carries incremental action information under the frozen held-module protocol; the historical CANNOT_CHECK is attributed to measurement access, not absent signal.
- **coverage >=80%, B1-B4 negative:** native state becomes measurable, but incremental signal beyond history fails the frozen endpoint; this is a substantive predictive negative.
- **coverage <80%:** direct pinned-server access is still insufficient on the frozen corpus; report accessibility by syntax/file class and treat the boundary as an ecosystem instrumentation result. Do not lower the gate.
- **calibration failure:** `CANNOT_CHECK_LSP_CURSOR_SEMANTICS`; do not touch the scientific corpus with alternative cursor rules.

## 11. Remaining top-tier boundary

Even a full positive here is not donor-complete OCME. It closes the native-state measurement/incremental-value gate. The separate strongest-donor first-refusal experiment and native verifier-backed method-space expansion remain required for P10's broadest top-tier claim.
