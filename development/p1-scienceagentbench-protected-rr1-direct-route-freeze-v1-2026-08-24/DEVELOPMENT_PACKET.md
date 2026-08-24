# Paper 1 protected RR1 direct-route freeze V1 development packet

## Development question

Can ORION freeze and prepare exactly one protected ScienceAgentBench live
discriminator, `(task_id="1", arm="RR", attempt=1, seed=101)`, on one LUNARC
A40 without opening evaluator material or outcomes, and fail closed before the
dynamic RR phase-1 generation unless the exact rendered prompt is tokenized by
the already bound GGUF runtime and fits `32768 - 7168` tokens?

This lane prepares that discriminator. It does **not** authorize `sbatch`, merge,
evaluation, outcome access, production use, or a scientific claim.

## Atomic questions

1. Does the tuple freeze exactly task `1`, arm `RR`, attempt `1`, seed `101`?
2. Do the masked and recovered packet bindings equal the body-free job 3537617
   receipt while the packet bodies remain outside Git?
3. Is the owner selection byte-equal to the merged direct-route contract?
4. Does the full 102-task, three-arm, three-attempt Runner V2 plan validate even
   though only one tuple is selected for this discriminator?
5. Are model, server, CUDA backend, llama.cpp revision, loopback geometry,
   cache policy, phase caps, and the shared raw-clock deadline frozen before any
   model output?
6. After strict RR0 parsing and canonical sealing, does the bridge reproduce the
   exact RR1 prompt and call loopback `POST /tokenize` with
   `add_special=true, parse_special=true` three times before RR1 completion?
7. Does any tokenization disagreement, malformed token response, deadline
   expiry, context overflow, or completion/token-count disagreement emit or
   preserve a typed `CANNOT_CHECK` boundary?
8. Does the retained bridge receipt exclude packet bodies, prompt bodies,
   completion bodies, token IDs, credentials, evaluator material, and outcomes?
9. Can one-tuple scheduler finalization remain explicitly separate from the
   918-record Runner V2 finalizer and avoid claiming that ledger is complete?

## Incumbent mechanics and negative history

- The merged direct-route freeze fixes attempts `1/2/3` to seeds `101/202/303`,
  RR caps `1024 + 7168`, exact runtime hashes, loopback geometry, cache-off
  semantics, and the 1800-second `CLOCK_MONOTONIC_RAW` attempt deadline.
- The merged direct-route SLURM bridge stages, attests, and captures the runtime,
  renders RR1 from a strict canonical RR0 state, and checks the completion
  response's `timings.prompt_n + 7168 <= 32768`.
- That bridge does **not** call `/tokenize` on the dynamic RR1 prompt before
  issuing RR1 `/completion`. Treating it as submit-ready would therefore cross
  the required fail-close boundary.
- Job 3537617 established body-free static prompt fit for 1224/1224
  state-independent prompts, but correctly retained all 306 RR1 prompts as
  `CANNOT_CHECK_DYNAMIC_RR_PHASE0_STATE_REQUIRED`.
- The merged production finalizer requires all 918 tuples. Reusing it for one
  exploratory tuple would falsely state population finalization.

## Bounded saturation assessment

### Knowledge

The relevant merged donors are the direct-route freeze, the direct-route SLURM
preflight, the generation adapter, and the exact GGUF `/tokenize` probe. These
jointly cover prompt construction, capture semantics, scheduler identity,
runtime identity, deadline semantics, and the verified tokenize request mode.
They do not jointly implement the dynamic RR1 pre-tokenize gate.

### Search universe

The bounded search covered merged Paper 1 direct-route, SLURM, adapter,
tokenizer-probe, protected prompt-fit, and Runner V2 lanes. No evaluator,
outcome, protected body, credential, provider, or external API route was opened.

### Formulation

The smallest unresolved atom is not a new model driver. It is a protocol
successor around the merged bridge that (a) fixes one tuple, (b) binds its public
and private-input hashes, (c) inserts verified dynamic tokenization before the
second completion, and (d) retains a one-tuple finalization boundary.

## Challenge to the saturation basis

- A post-completion `timings.prompt_n` check is not equivalent to a pre-generation
  fit gate: the overflowing generation request has already been issued.
- A wrapper that monkeypatches the merged bridge but records only the merged
  launcher hash would misbind the executed code.
- A one-row Runner plan is not a conservative substitute because the merged
  direct driver requires the full Runner V2 population plan.
- Static fit of RR0 cannot establish dynamic RR1 fit because RR1 contains
  model-produced canonical state.
- Three repeated `/tokenize` calls could be viewed as unnecessary. They are kept
  because the exact tokenizer capability receipt explicitly requires a
  repeatability check, and they add no model output or external route.

## Why prior searches could have missed the gap

The merged bridge validates the dynamic rendering rule and validates the
completion's live token count, so a review focused on post-response conformance
can appear complete. The missing temporal predicate is that fit must be known
*before* RR1 generation. Hashing the merged launcher can also obscure that an
out-of-band wrapper changed behavior without being bound as executed code.

## Alternatives considered

1. **Data-only blocked freeze.** Safest and smallest, but does not prepare an
   executable pre-tokenize-capable route.
2. **Monkeypatch or shell wrapper around the merged supervisor.** Small in lines,
   but creates launcher/module identity ambiguity and is rejected.
3. **Recommended: additive protocol successor using exact-bound merged helpers.**
   Reuse the unchanged server, staging, scheduler, cleanup, and adapter helpers;
   bind the new launcher/module as the executed layer; replace only the attempt
   client and bridge receipt needed for dynamic tokenization.

## Frozen implementation hypothesis

An additive successor can prepare the one tuple without modifying merged donor
files if it:

- validates exact donor hashes before use;
- fixes task/arm/attempt/seed and packet/static-fit bindings in canonical JSON;
- imports the merged bridge only as an exact-bound helper donor;
- stages and records the successor launcher/module as the executed bridge;
- repeats exact loopback `/tokenize` three times for RR1, retains only hashes and
  counts, verifies identical token arrays, checks `token_count + 7168 <= 32768`,
  then and only then sends RR1 `/completion`;
- requires the completion `timings.prompt_n` to equal the pre-tokenized count;
- uses the same remaining raw-clock deadline for tokenization and generation;
- preserves typed adapter failure sidecars and never logs request/response bodies;
- defines a separate one-tuple scheduler-finalization contract whose authority
  is metadata conformance only and whose Runner V2 ledger status stays
  `NOT_FINALIZED_918_TUPLES`.

## Test freeze

The synthetic hostile suite must first fail while the successor is absent, then
pass only after it proves:

- exact tuple, packet, static-fit, owner, runtime, and full-plan bindings;
- request order `RR0 /completion`, three `RR1 /tokenize`, then RR1 `/completion`;
- fail-close on malformed tokens, repeat disagreement, overflow, timeout, and
  tokenize/completion count disagreement;
- no body or token-ID retention in bridge receipts;
- exact one-A40 SLURM directives and no `sbatch` invocation in repository code;
- typed one-tuple finalization boundaries; and
- exact artifact hashes plus a privacy scan.

## Reopen triggers

Reopen rather than submit if any donor hash drifts; PR 1198 evidence is not
merged or cannot be verified; packet bytes/hashes differ; the plan or owner
selection fails merged validation; the server's tokenize response shape changes;
token repeats disagree; RR1 does not fit; completion prompt count differs;
scheduler allocation/GPU identity or cleanup cannot be verified; any evaluator,
outcome, credential, protected body, external API, or body log appears; or a
review finds the executed launcher/module identity incompletely bound.
