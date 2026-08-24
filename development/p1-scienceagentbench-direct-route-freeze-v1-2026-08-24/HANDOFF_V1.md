# DIRECT_ROUTE_FREEZE_V1 handoff

## Bounded status

The additive direct-route packet is synthetically implemented and hostile-
validated. It is not production-admissible and does not authorize official
task access, model execution, evaluation, outcome opening, or scientific
claims. The existing Runner, adapter, analysis contract, and other lanes are
unchanged.

## Frozen decisions

- Route: already-bound `llama-server` at literal loopback
  `http://127.0.0.1:8080/completion`; no launch, pull, proxy, redirect, secret,
  tool, or external provider path.
- Runtime: exact GGUF, server, CUDA backend, llama.cpp revision, one slot,
  context 32,768, cache off, no context shift.
- Seeds: attempts 1/2/3 use 101/202/303, paired across RR/OS/NR.
- Sampling: temperature 0.2, top-k 20, top-p 0.95, min-p 0, repeat penalty 1,
  non-streaming, token return enabled.
- Output: exact production-shaped `json_schema`; strict whole-content JSON;
  one final candidate; all attempts retained without selection.
- State: sealed canonical RR state enters RR phase 1; OS is one-shot; NR reset
  phase 1 has no phase-0 input by construction.
- Equal prospective budget per arm: input 57,344; output 8,192; tools 0;
  wall 1,800 seconds; local handling 30 seconds; one final candidate.
- Phase caps: RR/NR 1,024 + 7,168; OS 8,192; every live request additionally
  requires `prompt_n + phase_cap <= 32768` without truncation.

The 30-second positive local cap is deliberate: an earlier zero-cap proposal
failed the unchanged Runner V1/V2 positive-cap invariant. It is a matched
prospective reserve. Actual local-execution usage is `0.0` because this
generation-only driver has no tool or candidate-program execution path; the
driver explicitly validates both event counts and the duration as zero. The
validator binds the corrected cap through the public adapter validator,
rejects a zero-cap mutation, and rejects unsupported nonzero actual usage.

Actual attempt wall time comes from the exact first-to-final
`CLOCK_MONOTONIC_RAW` boundaries already consumed by
`GenerationAttemptCapture`, not a server or client duration field. The driver
checks the matched cap and verifies nanosecond/second agreement in the final
adapter receipt.

CLI receipt output is new-file-only and input-safe: all input and frozen
upstream paths are checked for lexical, resolved, case-fold, symlink, hardlink,
and device/inode aliases before any caller input is read. Creation uses
`O_EXCL`, mode `0600`, `O_NOFOLLOW`, fsync, descriptor reread, exact-byte hash
and identity verification, with unchanged-created-file rollback on failure.

## What the synthetic gate establishes

- exact hashes for unchanged upstream and repaired PR #1159 dependencies;
- exact canonical schema sizes and hashes;
- equal budget and phase-cap invariants;
- paired seed and zero-tool bindings;
- literal loopback/no-secret request route;
- exact completion request fields and `json_schema`;
- strict raw JSON and fail-closed cache/context/truncation handling;
- RR state sealing, OS one-shot behavior, and NR reset isolation;
- reuse of `GenerationAttemptCapture` with allocation finalization pending;
- raw-clock-derived wall usage and explicit actual-zero local execution;
- alias-safe, no-overwrite receipt creation and failure rollback;
- exact lower claim boundary.

It uses synthetic packets only and establishes no official task fit, candidate
quality, semantic-choice sensitivity, cost result, or production admissibility.

## Required prospective staging before any official run

An authorized owner must, without changing the frozen design after observing
tasks or outcomes:

1. stage and independently hash the exact model, `llama-server`, CUDA backend,
   and tokenizer provenance on the intended allocation;
2. start the exact one-slot loopback geometry outside the driver and bind the
   runtime identity object;
3. build a Runner V2 plan whose direct-route bindings and byte-equal budgets
   match this packet exactly;
4. confirm each live `prompt_n + n_predict <= 32768`; any overflow becomes a
   typed `CANNOT_CHECK`/failed attempt, never truncation or context shift;
5. retain every RR/OS/NR attempt receipt with no semantic selection;
6. finalize all 918 task-arm-attempt allocation receipts through the unchanged
   Runner V2 scheduler-evidence path before making exclusivity or accelerator-
   cost claims;
7. obtain separate authority before any official evaluation or outcome access.

Until those gates are satisfied, keep:

```text
task_fit_status = CANNOT_CHECK_BEFORE_TASK_OPENING
allocation_status = CANNOT_CHECK_PENDING_SCHEDULER_FINALIZATION
semantic_choice_sensitivity = NOT_ESTABLISHED
production_admissibility = CANNOT_CHECK
scientific_authority_delta = NONE
```

## Verification and integrity

Run the focused validator, the existing 41-test generation-adapter validator,
Python compilation, and the SHA manifest check exactly as listed in
`DEVELOPMENT_PACKET.md`. `SHA256SUMS` covers the other seven files in this
directory and no file outside the lane.

This handoff is for review in a bounded `[skip ci]` pull request only. Do not
merge from this handoff.
