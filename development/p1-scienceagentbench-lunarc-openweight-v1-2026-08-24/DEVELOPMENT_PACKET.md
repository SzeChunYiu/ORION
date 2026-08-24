# P1 ScienceAgentBench LUNARC open-weight synthetic smoke — development packet

Date: 2026-08-24  
Scope: synthetic nonbenchmark GPU generation only  
Authority: infrastructure witness only; no Paper 1 outcome or scientific-authority delta

## Atomic questions

1. Can the exact bytes of a public, pinned Qwen3-Coder GGUF be verified before
   import into a pinned LUNARC Ollama runtime?
2. Can Ollama serve the imported model only on loopback with proxy variables
   cleared, while accurately recording that Ollama cloud capability remained
   enabled and that no pull event was observed in the retained logs?
3. Can one frozen, nonbenchmark fixture exercise the RR persistent-state, OS
   one-shot, and NR reset generation topologies with seeds 101, 202, and 303?
4. Does a repeated same-request/same-seed probe replay byte-identically, and
   do different seeds produce at least two distinct outputs under stochastic
   decoding?
5. Can a bounded long-context probe retain frozen markers from the beginning,
   middle, and end while reporting a prompt-token count below the requested
   context window?
6. Can model/runtime/tokenizer/blob/request/response hashes, token counts,
   throughput, wall time, GPU memory, GPU seconds, sampled energy, and SLURM
   accounting be retained without inventing a billed-USD conversion?

## Bounded saturation and nearest donors

- The merged ScienceAgentBench protocol, runner, Codex-route synthetic fixture,
  LUNARC protected-artifact staging, and LUNARC container-runtime smoke were
  inspected as the nearest in-repository donors.
- The candidate route is deliberately narrower: a local GGUF imported into the
  site-provided Ollama module, with no benchmark archive, task, outcome,
  evaluator, or credential access.
- The public model and tokenizer repository revisions, expected artifact size,
  expected GGUF SHA-256, the Ollama version and executable SHA-256, prompt
  fixture, and decoding options are byte-bound.
- Saturation is only claimed for this one synthetic route on one assigned GPU;
  it does not cover other runtimes, quantizations, hosts, drivers, context
  sizes, or official benchmark execution.

## Challenge to the saturation basis

- A loopback listener and cleared proxy variables do not prove a kernel-level
  absence of every outbound packet. Both retained jobs reported
  `OLLAMA_NO_CLOUD:false`, `OLLAMA_REMOTES:[ollama.com]`, and
  `Ollama cloud disabled: false`. The route therefore makes only this boundary
  claim:
  `BOUNDARY_ONLY__CLOUD_CAPABILITY_ENABLED__NO_PULL_EVENT_OBSERVED__NO_KERNEL_EGRESS_AUDIT`.
- GPU inference can be nondeterministic even with a fixed sampling seed. A
  replay mismatch is retained as an adverse result rather than repaired away.
- Recalling distributed long-context markers plus a nontruncated reported token
  count is a strong witness for this prompt, not a universal proof of absence
  of truncation.
- Scheduler accounting exposes resource use but may not expose an
  owner-authoritative monetary conversion. GPU seconds and sampled energy stay
  separate from billed cost.

## Why prior checks could be falsely flat

- A trivial exact-output prompt can hide whether stochastic seeds are honored.
- A short prompt cannot detect context-window clipping.
- A model tag alone can hide mutable upstream bytes or a tokenizer mismatch.
- Process wall time alone hides model-load time, GPU memory, and scheduler
  allocation use.

## Frozen implementation hypothesis

> If the pinned GGUF bytes and source-tokenizer files match their recorded
> SHA-256 values, Ollama 0.32.14 imports the GGUF into a content-addressed local
> store, all inference requests are sent to a loopback-only endpoint with
> explicit options, and the frozen synthetic probes pass, then this job is a
> usable infrastructure witness for an immutable open-weight generation route.
> It is not benchmark evidence and cannot close billed-cost, evaluator, or
> manuscript gates.

## Hostile checks and reopen triggers

- Any model/tokenizer/runtime/manifest/blob hash mismatch fails closed.
- Any non-loopback Ollama listening socket, inherited proxy setting, actual
  pull event in the retained server log, or missing cloud-capability state
  fails closed. The literal `registry.ollama.ai` is not by itself a pull event;
  Ollama also uses it as a local manifest namespace.
- Missing seeds, token counters, request/response bytes, raw hashes, or GPU
  telemetry fail closed.
- Same-seed byte mismatch or no different-seed sensitivity is reported as a
  failed probe, never normalized into a pass.
- A long-context marker miss, `done_reason != stop`, or reported prompt count at
  or above `num_ctx` reopens the context configuration.
- Absence of an owner-authoritative allocation-to-currency conversion produces
  `CANNOT_CHECK`, never a zero or estimated billed USD.

## Forbidden inputs

The job must not read or mount any protected ScienceAgentBench archive, task,
outcome, gold program, evaluator, rubric, credential, or secret. It must not run
an official task or evaluator. All payloads are frozen synthetic text authored
in this packet.
