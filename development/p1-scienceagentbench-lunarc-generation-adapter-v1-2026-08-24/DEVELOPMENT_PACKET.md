# P1 ScienceAgentBench LUNARC generation adapter V1 — development packet

## Development question

Can one additive, outcome-blind adapter close the generation-instrumentation gap
left by Runner V2 by (1) reading `CLOCK_MONOTONIC_RAW` at the exact first and
final model-operation boundaries, (2) refusing incomplete or reordered arm
phases, (3) requiring scheduler-backed one-allocation-per-attempt evidence for
all 918 tuples, and (4) projecting only records accepted by unchanged Runner V2?

## Fixed incumbent and negative history

- Runner V1 and Runner V2 remain byte-for-byte unchanged. They validate metadata;
  neither is a model or scheduler adapter.
- The prior Ollama/A40 smoke was adverse: RR phase 1 hit its 512-token cap and a
  same-seed replay diverged. It is not promoted.
- The direct llama-server cache-off witness passed only its distinct bounded
  synthetic fixture. `PRODUCTION_ADMISSIBILITY=NOT_ESTABLISHED` and witness
  composition remains forbidden.
- `time.monotonic()`, `time.monotonic_ns()`, server-reported duration, sampled
  telemetry, `CUDA_VISIBLE_DEVICES`, and mere `SLURM_JOB_ID` presence are not
  substitutes for the Runner V2 timing/allocation contract.

## Atomized fibers

1. Validate and hash one immutable production-shaped Runner V2 plan snapshot.
2. Enforce arm phase order: RR and NR have two operations; OS has one.
3. Read raw monotonic nanoseconds immediately before the first operation and in
   the immediate return/exception path of the final attempted operation.
4. Emit timing-captured but allocation-pending sidecars; never self-attest
   exclusivity in the generation process.
5. Validate a scheduler evidence ledger containing exactly the same 918 tuples,
   one unique job/allocation identity per tuple, exact GPU counts, bounded
   scheduler intervals, and scheduler-confirmed consumable exclusive GRES.
6. Reject overlap of the same node/GPU allocation key while allowing concurrent
   attempts on different GPU keys.
7. Emit exact Runner V2 records only after fiber 5 passes; preserve missing
   billed USD as null and use integer-only accelerator-second serialization.
8. Hash-bind captures, scheduler evidence, allocation index, final ledger,
   adapter/contract and unchanged Runner V2 identities without opening outcomes.

## Saturation and challenge

The search universe covered Runner V1/V2, their hostile validators, the existing
Ollama and direct llama-server clients, SLURM scripts/receipts, GPU telemetry and
generic process receipts. The apparently reusable timing paths were false-flat:
they use a different clock, float seconds, or a wider/narrower interval. The
apparently reusable allocation evidence was also false-flat: it reports a job,
GPU or telemetry interval but does not prove the exact 918 tuple-to-allocation
mapping or no-overlap relation.

The strongest conservative donor product is therefore unchanged Runner V2 plus
a separate capture and scheduler-evidence layer. Editing Runner V2 would break
its frozen upstream hashes; copying sampled/runtime evidence would weaken its
semantics. The additive projection is the smallest conservative embedding.

## Frozen implementation hypothesis

A stateful `GenerationAttemptCapture` with an injected generation callable and
injected raw-clock reader can make call order testable without model access.
Successful capture remains `ALLOCATION_FINALIZATION_PENDING`. A separate pure
finalizer accepts only exact scheduler records and is the sole code path allowed
to write `EXCLUSIVE_NO_OVERLAP_CONFIRMED` into a V2 ledger.

## Hostile validation surface

- exact raw clock API and call order, including operation exceptions;
- wrong/missing/extra phases and reuse after failure/finalization;
- mutually exclusive one-shot success versus `CANNOT_CHECK` terminal receipts;
- Boolean, negative, decreasing and float clock values;
- base-record identity/seed/field drift;
- missing/duplicate/extra tuples and reused job identities;
- GPU count/key drift, unbound/environment-only allocation status, invalid
  scheduler intervals, nonterminal job states and same-GPU overlap;
- scheduler config/export snapshots whose raw-file hashes do not match the
  scheduler-evidence bindings;
- exact integer-derived quantity and nullable billed USD;
- full 102 x 3 x 3 unchanged-Runner-V2 validation;
- strict JSON, exclusive output creation, rollback after a later output race,
  fresh per-attempt wrapper directories and evidence/seal hash drift;
- evaluator/outcome/candidate-body capability leakage.

## Test-first tightening provenance

The initial validator failed because the adapter module did not exist. The first
implemented surface reached 28 passing tests. Subsequent hostile tests first
demonstrated that a nonterminal `RUNNING` scheduler record was admitted, then
that raw scheduler snapshot bytes were not independently bound. Release audit
also first exposed a stale Runner V1 hash inside the contract, partial output
survival after a later-path race, untyped scheduler members, reusable wrapper
directories, retryable failed captures, dual success/`CANNOT_CHECK` emission and
non-strict base-record serialization. Each finding was reproduced as a failing
test before its tightening. The release contract therefore records post-test-
first tightening rather than claiming that its final bytes predated every fix.

## Reopen triggers

Reopen rather than weaken the contract if LUNARC cannot expose scheduler-backed
GPU allocation identity, if clock reads cannot be placed at the frozen call
boundaries, if a concrete driver needs an uninstrumented model call, if a tuple
cannot be mapped to one allocation, or if any evidence is missing after a job.

## Authority boundary

All development fixtures are synthetic nonbenchmark metadata. No archive, task,
candidate body, credential, evaluator, official outcome, manuscript or PDF is
opened. Passing establishes adapter conformance only. It does not authorize an
official run or establish allocation facts, cost ratios, task success,
superiority, causal repair, transition authority or publication claims.
