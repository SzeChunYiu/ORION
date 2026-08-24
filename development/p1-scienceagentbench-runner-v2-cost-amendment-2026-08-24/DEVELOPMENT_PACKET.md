# P1 ScienceAgentBench Runner V2 allocated-cost amendment — development packet

**Date:** 2026-08-24

**Base:** fresh `origin/main` at `86f85614cd84af5e16a6c69a53256ddfcfbb0d7b`,
including Analysis Freeze merge `957bc82ff2bcffa61a0bab96bc76fc6f811a9d10`

**Scope:** science-contract metadata only; additive amendment to Runner V1

**Question:** Can the open-weight LUNARC route use the prospectively frozen
`ALLOCATED_ACCELERATOR_SECONDS` primary generation-cost metric without
weakening Runner V1, losing nullable billed USD, opening an outcome, or
creating a post-outcome cost fallback?

## Pre-code authority and upstream freeze

This packet binds two already merged contracts and refuses to reinterpret them:

| Upstream byte identity | SHA-256 |
|---|---|
| Runner V1 contract | `e191540f131b3e7e33b0c040900bea94336dbd0d704b247b547a5c361b6e242f` |
| Runner V1 module | `15d6f511be9b3b1dbac408cc41812b0f72e1dd7aa700983035438efb8ed416df` |
| Analysis Freeze V1 contract, merged in `957bc82f` | `0cae220a5b2f73156eda63a01f769dfdecbf8ad1fa16bd0995e3f906cff391d4` |

Runner V1 already fixes the verified population, `RR/OS/NR`, three paired
attempts, matched prospective budgets, all-attempt retention, typed
`CANNOT_CHECK` failures, and absence of outcome fields. Analysis Freeze V1 then
fixes exactly two admissible prospective cost identities. Its handoff correctly
states that Runner V1 cannot admit a successful open-weight record whose billed
USD is unavailable, because V1 requires `billed_cost_usd` on successful
candidate records. That is the only gap addressed here.

## Competing designs considered

1. **Put zero in Runner V1 `billed_cost_usd`.** Rejected. Missing billed USD is
   not zero, and `0` would create false authority and corrupt separate
   availability reporting.
2. **Choose billed USD or accelerator seconds after outcomes.** Rejected. It is
   precisely the forbidden fallback/selection path in Analysis Freeze V1.
3. **Edit Runner V1 in place.** Rejected. That would silently alter the already
   merged `BILLED_USD` route and make prior validation receipts ambiguous.
4. **Emit a full Analysis Freeze outcome ledger before evaluation.** Rejected.
   The runner has no authority to fabricate discipline receipts, evaluator
   hashes/status, `valid_program`, `success_rate`, evaluator cost, or failure
   outcomes.
5. **Add an allocated-only V2 envelope and exact generation-side projection.**
   Selected. The V2 plan projects back through the unmodified Runner V1 plan
   validator, then adds a separately hashed metric, route, GPU-count and timing
   provenance binding. The completed 918-row ledger emits only the generation
   fields that a separately reviewed future outcome adapter may copy verbatim.

## Prospective metric identity

The only metric accepted by this amendment is the exact Analysis Freeze object:

```json
{
  "metric_id": "ALLOCATED_ACCELERATOR_SECONDS",
  "unit": "accelerator-second",
  "allocation_rule": "FOR_EACH_ATTEMPT_SUM_EXCLUSIVE_ACCELERATOR_COUNT_TIMES_MONOTONIC_GENERATION_WALL_SECONDS__NO_OVERLAP_DOUBLE_ALLOCATION__THEN_SUM_ALL_ATTEMPTS",
  "binding_phase": "BEFORE_CANDIDATE_GENERATION_AND_OUTCOME_OPENING"
}
```

Its binding is SHA-256 over canonical UTF-8 JSON (`ensure_ascii=false`, sorted
keys, comma/colon separators, no whitespace). The run plan, candidate ledger,
emitted cost projection and seal carry that object/digest. Every attempt carries
the same metric ID and digest. Any unit, allocation-rule, phase, hash, arm or
attempt drift fails before sealing. `BILLED_USD` is rejected by this module with
an explicit instruction to use unmodified Runner V1; it is not reimplemented.

## Exact LUNARC GPU/time provenance

The plan freezes:

- route `OPEN_WEIGHT_LUNARC_SLURM_EXCLUSIVE_GPU_V1`;
- `CLOCK_MONOTONIC_RAW` read through `clock_gettime_ns` in nanoseconds;
- start immediately before the first model-generation operation;
- end immediately after the final model-generation operation;
- elapsed exactly `end_ns - start_ns`;
- one task/arm/attempt per exclusive SLURM GPU allocation;
- no overlap double-allocation; and
- a strictly positive canonical GPU count that is identical for RR, OS and NR.

The entire measurement object is hash-bound. Each attempt repeats that hash,
the frozen GPU count, allocation confirmation, and canonical unsigned start,
end and elapsed nanoseconds. The primary quantity is derived with integer
arithmetic only:

```text
generation_cost_quantity = exclusive_gpu_count * monotonic_elapsed_ns / 1_000_000_000
```

The serializer produces one canonical decimal: no sign, exponent, float,
leading zero or redundant fractional trailing zero. The supplied quantity must
be byte-equal to that derived value. No ambient float or decimal precision
participates.

## Billed-USD separation and missingness

The allocated metric is always primary on this route. Each record separately
retains both the inherited `billed_cost_usd` slot and the exact analysis field
`generation_billed_cost_usd`, plus an availability status:

- `AVAILABLE`: both values are the same canonical decimal string;
- `CANNOT_CHECK`: both values are JSON null.

A null is never written as `0`, included in a billed total, copied into the
accelerator quantity, or used as fallback. Candidate failures remain typed
`CANNOT_CHECK`, but their measured allocated time still contributes when the
exact timing receipt is available; all attempts remain in scope.

## Strongest-comparator denominator without outcomes

Analysis Freeze V1 chooses the stronger OS/NR comparator using outcomes. This
amendment cannot know that choice and does not open it. Instead it requires both
the OS total and NR total to be strictly positive across all 306 attempts in
each arm. Therefore whichever comparator is selected later has a positive
denominator. Zero for either arm is rejected before seal, rather than deferred,
divided through, or turned into `0/0`.

## Exact Analysis Freeze projection boundary

The emitter returns 102 task containers and exactly nine attempt projections per
task. The following generation-authoritative fields use the exact spelling,
type and semantics in merged Analysis Freeze V1:

- `cost_gate_metric` and `cost_gate_metric_binding_sha256`;
- `cost_accounting = ALL_ATTEMPTS_NO_SELECTION`;
- `task_id`, `arm_id`, `attempt` and `candidate_program_sha256`;
- `generation_cost_quantity`; and
- nullable `generation_billed_cost_usd`.

The projection is deliberately **not** mislabeled as the full outcome ledger.
It contains no evaluator/result fields. A future independently reviewed outcome
adapter must add the other exact Analysis Freeze fields without transforming
these bytes and must bind the emitted file as `generation_ledger_sha256`.

## I/O identity and immutable input snapshots

The four CLI roles—run plan, candidate ledger, output projection and output
receipt—first undergo pairwise lexical/resolved and existing `(st_dev, st_ino)`
preflight (therefore detecting symlinks and hardlinks). Both outputs must be new:
before input validation or any payload write, the CLI atomically reserves each
destination with `O_RDWR|O_CREAT|O_EXCL` mode `0600` and keeps both descriptors
open through final verification. This filesystem-aware step rejects a
pre-existing output and also rejects two nonexistent spellings that the host
filesystem treats as the same path, including case-fold collisions on
case-insensitive APFS/HFS. Reserved output identities must be unique and
distinct from both inputs. The programmatic seal entry point separately repeats
the input/input guard.

Canonical JSON is written only through each held descriptor. After `fsync`, the
descriptor is reread and the observed bytes and SHA-256 must exactly equal the
intended canonical bytes; the pathname must still identify the reserved inode
before and after writing and after both emissions. Any reservation, validation,
write, hash or identity failure rolls back only a pathname that still identifies
its owned reservation. A substituted path or input is never deleted as
collateral.

Each input is then read exactly once as bytes. SHA-256 and strict UTF-8 JSON
parsing—including duplicate-member rejection—operate on that same immutable
buffer. The path is never hashed and reopened for parsing. A deterministic
hostile regression replaces both valid input paths immediately after their one
read; the seal continues to bind and project only the original captured bytes,
with one read per input, so swapped bodies cannot be certified under earlier
hashes.

## Hostile review matrix

Focused standard-library verification constructs a full synthetic 102 x 3 x 3
ledger and attacks:

- upstream contract/module hash drift and duplicate JSON members;
- BILLED_USD shadowing, alternate metric, unit/allocation/phase/hash drift and
  extra fallback fields;
- route, clock, timing-boundary, allocation and provenance drift;
- unequal/zero/noncanonical GPU counts and per-attempt mismatches;
- signed, exponent, float, Boolean, negative, leading-zero and trailing-zero
  cost/timing forms;
- end-before-start, elapsed mismatch and exact derived-cost mismatch;
- billed availability/value mismatches and missing-as-zero imputation;
- missing, duplicate, extra, wrong-arm/attempt/seed and selected-only records;
- zero OS or NR all-attempt totals;
- Runner V1 unequal budgets, cap exceedance, candidate failures and hashes; and
- output/output and output/input lexical, symlink and hardlink aliases;
- pre-existing outputs and case-folded nonexistent output collisions on a
  case-insensitive filesystem;
- post-write destination substitution, byte/hash corruption and safe owned-file
  rollback;
- deterministic run-plan and candidate-ledger swaps between hypothetical hash
  and parse stages; and
- analysis-projection field drift or evaluator/outcome leakage.

`38/38` synthetic hostile tests pass on a case-insensitive host. The explicit
case-fold regression is conditionally skipped on a case-sensitive host, where
the two spellings are not aliases. The suite opens zero official tasks/outcomes
and exercises no provider, model, archive, credential, container, evaluator,
CI, pytest, manuscript or PDF.

## Review and activation rule

The contract and hostile validator provide deterministic review evidence, not
independent scientific review. The amendment must remain inactive until its PR
is reviewed and merged, its exact plan/metric/route/timing bytes are externally
frozen before any candidate generation, and the future generation adapter is
shown to place `CLOCK_MONOTONIC_RAW` reads at the frozen boundaries. This packet
does not authorize an official run.

## Authority delta and retention

No production plan, task, archive, candidate, evaluator record, outcome,
credential, timing receipt, manuscript or PDF is committed. No scientific
effect, success rate, cost ratio, superiority claim or transition decision is
computed. Scientific authority delta: `NONE`.
