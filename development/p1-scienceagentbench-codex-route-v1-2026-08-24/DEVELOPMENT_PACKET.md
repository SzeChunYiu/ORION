# P1 ScienceAgentBench Codex CLI route V1 - development packet

**Development question:** Can the merged verified ScienceAgentBench runner be
given a shortest executable RR/OS/NR generation route through the locally
authenticated Codex CLI 0.147.0 without inventing an immutable model snapshot,
tokenizer, seed, billed cost, or runtime guarantee that the client does not
expose?

**Base subject:** `e4026dc81a8ccc44841cd2d44115bb05873a03da`.

**Merged dependency:**
`development/p1-scienceagentbench-runner-v1-2026-08-24/` from PR #1101.

**Authority:** outcome-blind generation-route preflight and synthetic
nonbenchmark adapter evidence only. No official task, task text, Parquet,
benchmark archive entry, candidate, evaluator, gold program, rubric, outcome,
manuscript, PDF, or publication package is opened or executed. Scientific
authority delta remains `NONE`.

## Atomic development questions

1. What exact local Codex package, launcher, native binary, provider identifier,
   model slug, reasoning effort, service tier, sandbox, approval policy, and
   authentication route can be byte- or value-bound without reading secrets?
2. Does refreshed model metadata establish that `gpt-5.6-sol` is an immutable
   dated snapshot, or only a mutable alias/catalog slug?
3. Does Codex 0.147.0 expose an exact tokenizer revision and a supported seed
   control that can satisfy the merged runner's non-placeholder bindings?
4. Which JSONL events and per-turn usage fields are actually emitted, and do
   they include tool count, wall time, resolved provider/model, or billed USD?
5. Can exact outcome-blind RR, OS, and NR prompt-template bytes and canonical
   rendering rules be frozen without using any ScienceAgentBench task content?
6. Can one synthetic attempt per arm exercise RR persistence, OS one-shot, and
   NR reset while retaining raw-output hashes, observed token/tool/wall-time
   values, and honest null billed cost?
7. Can a three-attempt schedule and equal prospective acceptance caps be
   specified without mislabelling attempt ordinals/nonces as model seeds or
   post-run rejection as provider-side enforcement?
8. If any mandatory merged-runner field remains unbound, what exact external
   discriminator would close it without weakening the contract?

## Incumbent mechanics and negative history recovered

- The merged runner fixes `verified`, the Parquet and mask hashes, task IDs
  `1..102`, RR/OS/NR, three attempts, exact matched caps, all-attempt cost, and
  a `provider_seed_capability` value of `CONFIRMED` before a production plan can
  seal.
- Codex CLI 0.147.0 accepts explicit model/provider/config overrides and emits
  JSONL, but its public `exec` help contains no seed, tokenizer, hard token cap,
  hard tool-call cap, billed-cost, or resolved-snapshot option.
- A clean, owner-controlled temporary `CODEX_HOME` can reference the existing
  ChatGPT authentication file by symlink without opening or hashing credential
  bytes. `--ignore-user-config`, `--ignore-rules`, read-only sandbox, and never
  approval remove local configuration/rule variation; Codex's own model-visible
  base instructions remain part of the client/server route.
- An initial synthetic schema probe showed JSONL thread/turn/item events and a
  terminal usage object. JSONL did not echo the selected model/provider/config,
  tool policy, elapsed time, tokenizer, seed, or billed cost.
- A strict clean-config `seed=101` override failed before generation with the
  exact error `unknown configuration field 'seed'`.
- Bundled and refreshed 0.147.0 catalogs describe the same `gpt-5.6-sol` slug
  but already disagree on `max_context_window` (272000 versus 872000). A slug
  and catalog record are therefore not evidence of an immutable model snapshot.

## Bounded saturation assessment

### Knowledge saturation

The bounded evidence universe is the installed 0.147.0 package/binary, its
redacted doctor output, bundled/refreshed model catalog metadata, CLI help,
strict configuration parsing, and synthetic JSONL calls. No external benchmark
or model claim is needed to decide whether the merged runner's required fields
are observable.

### Search-universe saturation

Admissible routes are limited to locally authenticated `codex exec` with a
clean temporary home, built-in `openai` provider, explicit model/config values,
read-only sandbox, no project rules, frozen prompt/schema bytes, external
wall-time enforcement, JSONL parsing, and post-run matched-cap rejection.
Provider APIs, browser inspection, credential files, unofficial tokenizers,
price tables, proxy internals, and official benchmark material are excluded.

### Formulation saturation

The task is not to run ScienceAgentBench. It is to determine whether the local
transport can populate every mandatory field of the already-merged runner. A
transport-successful synthetic response is not a production-ready run plan.

## Challenge to the saturation basis

The route could look bound while remaining non-replayable if a friendly model
slug is treated as a snapshot, catalog metadata is treated as server identity,
attempt numbers are called seeds, JSONL token counts are attributed to an
unpublished tokenizer, subscription access is converted to zero-dollar billed
cost, prompt-template hashes omit rendered task bytes, or after-run cap checks
are described as hard provider limits. The packet must make each distinction
machine-readable.

## Missed-knowledge hypotheses

1. The service may possess a resolved snapshot identifier that Codex JSONL does
   not return.
2. Token counts may be computed by a server tokenizer whose revision is absent
   from both client help and model catalog.
3. A seed may exist in a lower-level API even though Codex strict config rejects
   it; this cannot be assumed for the authenticated CLI route.
4. ChatGPT subscription accounting may have owner-visible usage elsewhere, but
   the per-call JSONL stream has no billed USD field.
5. Codex base instructions/catalog records may change independently of the
   installed wrapper and native-binary hashes.
6. RR resume may preserve more hidden session state than its visible phase-0
   output; NR must use a fresh thread to prove reset at the client boundary.
7. A post-run tool/token rejection cap may spend unequal resources before
   rejection even when the acceptance envelope is identical.

## Frozen implementation hypothesis

> A small outcome-blind adapter can freeze prompt rendering, emit exact clean
> Codex argv, parse JSONL, count tools, measure wall time, preserve output hashes
> and null billed cost, and demonstrate RR/OS/NR transport on synthetic data;
> however it must produce a blocked run-plan candidate unless an immutable
> resolved model, tokenizer revision, supported seed, and per-attempt billed
> cost become independently observable.

This is a local engineering/preflight hypothesis only.

## Frozen hostile checks

- prompt-template and schema byte/hash drift fails;
- noncanonical packet JSON or undeclared placeholder fields fail;
- RR phase 1 without the phase-0 state hash/thread binding fails;
- NR phase 1 reusing the phase-0 thread fails;
- OS phase 0 containing model output fails;
- missing/duplicate JSONL terminal usage, failed turns, tool over-cap, token
  over-cap, wall-time over-cap, absent output hash, and numeric billed-cost
  invention fail;
- attempt ordinals are never accepted as seeds;
- the three-attempt schedule is exact but explicitly `UNSEEDED`;
- all three arms have byte-identical acceptance caps;
- no run-plan candidate is promoted while snapshot, tokenizer, seed, or billed
  cost is `CANNOT_CHECK`;
- no credential path, contents, hash, token, cookie, header, or account identity
  enters a committed artifact.

## Reopen triggers and exact next discriminators

Reopen only if the provider returns a signed/durable resolved model snapshot;
Codex or the provider documents and receipts an exact tokenizer revision; a
strict supported seed option is added and repeat-call behavior is characterized;
and an owner-authoritative per-attempt billed-USD receipt can be joined to the
same attempt ID. After those four closures, freeze provider-side or externally
enforced token/tool/time limits, render and hash every official task prompt
outside ORION, and rerun the merged runner's full synthetic contract before any
official generation.
